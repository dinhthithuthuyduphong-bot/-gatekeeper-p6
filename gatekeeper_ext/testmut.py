"""Test-level differential (Study L2, development stage).  Compatible with Python 3.8.

Draws are mutants of the repository's OWN tests: one literal inside a passing, fast upstream test is replaced
(type-confusion value or a small perturbation) and the mutated test is run unchanged against three snapshots:
the original code, the upstream fix (gold) and a candidate patch.  A draw's outcome is the pass/fail status and
the normalised failure text of the mutated test (all parameter cases together).
    l0 = [outcome(original) != outcome(gold)],  l1 = [outcome(patch) != outcome(gold)],  Z = l1 - l0,
    R = [l0 = 0 and l1 = 1]
Nothing is pickled and no function is intercepted, so receivers that cannot be serialised, callbacks registered
by decorators and deeply nested inputs are all reachable (the three failure modes observed in gate G1 of Study L).
"""
import ast
import json
import os
import random
import re
import shutil
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import golddiff_oracle as O  # noqa: E402
from gatekeeper_ext.testmut_evidence import execute_logged, feasibility_checks, write_json
from gatekeeper_ext.golddiff import edited_functions  # noqa: E402
from gatekeeper_ext.mutants import _offsets, mutants as ast_mutants  # noqa: E402

MAXT = 1.0                       # a test is eligible if every case passed at the original in at most this many seconds
MARK = re.compile(r"__gkm(\d+)")


def expand_files(root, entries):
    files = []
    for e in entries:
        p = Path(root) / e
        if p.is_dir():
            files += [str(q.relative_to(root)).replace("\\", "/") for q in sorted(p.rglob("*.py"))
                      if (q.name.startswith("test_") or q.name.endswith("_test.py") or q.name == "tests.py")]
        elif p.exists():
            files.append(e)
    return sorted(set(files))


def parse_junit(text):
    out = []
    for tc in ET.fromstring(text).iter("testcase"):
        status, msg = "passed", ""
        for child in tc:
            if child.tag in ("failure", "error"):
                status = "failed" if child.tag == "failure" else "error"
                msg = child.get("message") or (child.text or "")[:300]
                break
            if child.tag == "skipped":
                status, msg = "skipped", child.get("message") or ""
        out.append({"classname": tc.get("classname", ""), "name": tc.get("name", ""), "status": status,
                    "time": float(tc.get("time") or 0), "msg": msg})
    return out


def norm(msg, roots):
    s = msg or ""
    for r in sorted((str(x) for x in roots), key=len, reverse=True):
        s = s.replace(r, "<ROOT>")
    s = re.sub(r"0x[0-9a-fA-F]+", "0x", s)
    s = re.sub(r"/tmp/[^\s'\"]+", "<TMP>", s)
    s = re.sub(r"\.py:\d+", ".py:N", s)
    s = re.sub(r"\bline \d+\b", "line N", s)
    s = re.sub(r"\d+\.\d+s\b", "Ns", s)
    return s[:300]


def run_tests(root, runner, files, pythonpath, select, work, tag, timeout=1800):
    root, work = Path(root), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0",
               PYTHONPATH=os.pathsep.join([str(root / p) for p in pythonpath] + [str(root), str(ROOT)]))
    if runner == "pytest":
        xml = work / (tag + ".xml")
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:randomly",
               "--junitxml", str(xml), "-o", "junit_family=xunit2"]
        if select:
            cmd += ["-k", select]
        receipt = execute_logged(cmd + list(files), root, env, work / tag, timeout)
        if receipt["status"] != "COMPLETED" or receipt["returncode"] not in (0, 1):
            return None, "runner did not finish normally; see " + tag + ".command.json"
        if not xml.exists():
            return None, "runner produced no XML; see " + tag + ".stdout.txt"
        try:
            records = parse_junit(xml.read_text(encoding="utf-8"))
        except (ET.ParseError, ValueError, OSError) as exc:
            return None, "invalid XML: " + type(exc).__name__
        if not records:
            return None, "runner produced no test records"
        return records, None
    out = work / (tag + ".json")
    receipt = execute_logged([sys.executable, "-m", "gatekeeper_ext.testmut_unittest", str(out), select or ""] + list(files),
                             root, env, work / tag, timeout)
    if receipt["status"] != "COMPLETED" or receipt["returncode"] != 0:
        return None, "unittest runner did not finish normally; see " + tag + ".command.json"
    if not out.exists():
        return None, "unittest runner produced no result"
    try:
        records = json.loads(out.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return None, "invalid unittest result: " + type(exc).__name__
    if not records:
        return None, "unittest runner produced no test records"
    return records, None


def _sites(src, node, at):
    skip = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.JoinedStr):
            skip.update(id(d) for d in ast.walk(sub))
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    found = {}
    for stmt in body:
        for sub in ast.walk(stmt):
            if isinstance(sub, ast.Constant) and id(sub) not in skip:
                v = sub.value
                if v is None or isinstance(v, (bool, int, float, str, bytes)):
                    if isinstance(v, (str, bytes)) and len(v) > 120:
                        continue
                    found[(at(sub.lineno, sub.col_offset), at(sub.end_lineno, sub.end_col_offset))] = v
    return sorted((s, e, v) for (s, e), v in found.items())


def eligible_functions(root, files, baseline):
    funcs = []
    for rel in files:
        src = (Path(root) / rel).read_text(encoding="utf-8")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        at = _offsets(src)
        modname = rel[:-3].replace("/", ".")

        def visit(body, classes):
            for n in body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test"):
                    cls = ".".join([modname] + classes)
                    cases = [r for r in baseline if r["classname"] == cls and (r["name"] == n.name or r["name"].startswith(n.name + "["))]
                    if cases and all(c["status"] == "passed" and c["time"] <= MAXT for c in cases):
                        sites = _sites(src, n, at)
                        if sites:
                            first = min([n.lineno] + [d.lineno for d in n.decorator_list])
                            funcs.append({"file": rel, "name": n.name, "first": first, "end": n.end_lineno, "sites": sites})
                elif isinstance(n, ast.ClassDef):
                    visit(n.body, classes + [n.name])
        visit(tree.body, [])
    return sorted(funcs, key=lambda f: (f["file"], f["first"]))


def replacement(rng, v):
    if rng.random() < 0.5:
        for _ in range(8):
            val = O.CONFUSION[rng.randrange(O.N_CONFUSION)]()
            if type(val) is not type(v) or val != v:
                return repr(val)
        return None
    if v is None:
        return "0"
    if isinstance(v, bool):
        return repr(not v)
    if isinstance(v, int):
        return repr(v + 1)
    if isinstance(v, float):
        return repr(v + 1.0)
    if isinstance(v, str):
        return repr(v + "x")
    return repr(v + b"x")


def make_mutants(funcs, n, seed):
    rng = random.Random("%s:testmut:v1" % seed)
    out, seen, attempts = [], set(), 0
    while funcs and len(out) < n and attempts < n * 30:
        attempts += 1
        f = rng.choice(funcs)
        s, e, v = rng.choice(f["sites"])
        rep = replacement(rng, v)
        if rep is None or (f["file"], f["first"], s, rep) in seen:
            continue
        seen.add((f["file"], f["first"], s, rep))
        out.append({"id": len(out), "func": f, "site": (s, e), "rep": rep})
    return out


def build_mutated_sources(root, mutants):
    """File -> new text with one renamed, mutated copy of each mutated test inserted after the original."""
    by_file, texts, ok = {}, {}, set()
    for m in mutants:
        by_file.setdefault(m["func"]["file"], []).append(m)
    for rel, ms in by_file.items():
        src = (Path(root) / rel).read_text(encoding="utf-8")
        starts, pos = [], 0
        for ln in src.splitlines(True):
            starts.append(pos)
            pos += len(ln)
        inserts = []
        for m in ms:
            f = m["func"]
            a = starts[f["first"] - 1]
            b = starts[f["end"]] if f["end"] < len(starts) else len(src)
            s, e = m["site"]
            if not (a <= s and e <= b):
                continue
            seg = src[a:s] + m["rep"] + src[e:b]
            seg = re.sub(r"(\bdef\s+)%s(\s*\()" % re.escape(f["name"]), r"\g<1>%s__gkm%d\g<2>" % (f["name"], m["id"]), seg, count=1)
            seg = seg if seg.endswith("\n") else seg + "\n"
            try:
                compile(textwrap.dedent(seg), "<mutant>", "exec")
            except SyntaxError:
                continue
            inserts.append((b, ("\n" if b == len(src) and not src.endswith("\n") else "") + seg, m["id"]))
        text = src
        for b, seg, mid in sorted(inserts, key=lambda x: x[0], reverse=True):
            text = text[:b] + seg + text[b:]
            ok.add(mid)
        try:
            compile(text, rel, "exec")
        except SyntaxError:
            ok -= {mid for _, _, mid in inserts}
            continue
        texts[rel] = text
    return texts, ok


def signatures(results, roots):
    sig = {}
    for r in results:
        m = MARK.search(r["name"])
        if m:
            sig.setdefault(int(m.group(1)), []).append("%s|%s|%s|%s" % (r["classname"], MARK.sub("", r["name"]), r["status"], norm(r["msg"], roots)))
    return {k: "\n".join(sorted(v)) for k, v in sig.items()}


def run_arm(base_root, name, test_texts, source_overrides, runner, pythonpath, work, repeats):
    d = Path(work) / ("arm_" + re.sub(r"\W", "_", name))
    shutil.copytree(base_root, d, ignore=shutil.ignore_patterns(".git"))
    if source_overrides:
        write_json(Path(work) / ("source_override_" + re.sub(r"\W", "_", name) + ".json"), source_overrides)
    for rel, text in list(source_overrides.items()) + list(test_texts.items()):
        (d / rel).write_text(text, encoding="utf-8")
    sigs = []
    for i in range(repeats):
        res, err = run_tests(d, runner, sorted(test_texts), pythonpath, "__gkm", work, "%s_%d" % (re.sub(r"\W", "_", name), i))
        if res is None:
            return None, err
        sig = signatures(res, [d, base_root])
        write_json(Path(work) / ("%s_%d.records.json" % (re.sub(r"\W", "_", name), i)), res)
        write_json(Path(work) / ("%s_%d.signatures.json" % (re.sub(r"\W", "_", name), i)), sig)
        sigs.append(sig)
    return sigs, None


def paired(orig, gold, patch, ids):
    s = {"help": 0, "hurt": 0, "tie": 0, "bug_trigger": 0, "missing": 0}
    for k in ids:
        a, g, p = orig.get(k), gold.get(k), patch.get(k)
        if a is None or g is None or p is None:
            s["missing"] += 1
            continue
        l0, l1 = a != g, p != g
        s["bug_trigger"] += l0
        if l1 and not l0:
            s["hurt"] += 1
        elif l0 and not l1:
            s["help"] += 1
        else:
            s["tie"] += 1
    return s


def analyze(orig_root, gold_root, modules, pythonpath, runner, test_entries, patches, work, seed, n_draws=200, n_mutants=5):
    import time
    t0 = time.time()
    orig_root, gold_root, work = Path(orig_root), Path(gold_root), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    res = {"seed": seed, "n_draws_requested": n_draws}
    files = expand_files(orig_root, test_entries)
    res["test_files"] = len(files)
    write_json(work / "test_inventory.json", {"requested": list(test_entries), "expanded": files})
    if not files:
        return dict(res, eligible=False, reason="configured test entries resolved to zero files")
    baseline, err = run_tests(orig_root, runner, files, pythonpath, None, work, "baseline")
    if baseline is None:
        return dict(res, eligible=False, reason="baseline test run produced no result", tail=err)
    res["baseline_cases"] = len(baseline)
    res["baseline_passed"] = sum(1 for r in baseline if r["status"] == "passed")
    funcs = eligible_functions(orig_root, files, baseline)
    res["eligible_test_functions"] = len(funcs)
    if not funcs:
        return dict(res, eligible=False, reason="no passing fast test function with a literal to mutate")
    mut = make_mutants(funcs, n_draws, seed)
    texts, ok = build_mutated_sources(orig_root, mut)
    ids = sorted(ok)
    write_json(work / "mutation_catalog.json", {"seed": seed, "mutants": mut, "compiled_ids": ids})
    for rel, text in texts.items():
        saved = work / "mutated_tests" / rel
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_text(text, encoding="utf-8")
    res["mutants_generated"], res["mutants_compiled"] = len(mut), len(ids)
    if not ids:
        return dict(res, eligible=False, reason="no mutated test compiled")
    arms = {"orig": (orig_root, {}), "gold": (gold_root, {})}
    for k, v in patches.items():
        arms["patch:" + k] = (v, {})
    n_ast = 0
    for rel in sorted({e["file"] for e in edited_functions(orig_root, gold_root, modules)}):
        names = [e["qualname"] for e in edited_functions(orig_root, gold_root, modules) if e["file"] == rel]
        for desc, new in ast_mutants((gold_root / rel).read_text(encoding="utf-8"), names, n_mutants):
            if n_ast >= n_mutants:
                break
            arms["mutant:" + desc] = (gold_root, {rel: new})
            n_ast += 1
    sigs, errors = {}, {}
    for name, (root, over) in arms.items():
        repeats = 2 if (name in ("orig", "gold") or name.startswith("patch:")) else 1
        s, e = run_arm(root, name, texts, over, runner, pythonpath, work, repeats)
        if s is None:
            errors[name] = e
            break  # retain partial evidence; do not spend further trials after an invalid arm
        else:
            sigs[name] = s
    write_json(work / "arm_signatures.json", sigs)
    write_json(work / "arm_errors.json", errors)
    if errors:
        return dict(res, eligible=False, reason="arm run failed: " + ", ".join(sorted(errors)), arm_errors=errors)
    res["deterministic"] = all(len(s) < 2 or s[0] == s[1] for s in sigs.values())
    first = {n: s[0] for n, s in sigs.items()}
    res["patches"] = {k: paired(first["orig"], first["gold"], first["patch:" + k], ids) for k in patches}
    res["mutants"] = [{"desc": n[7:], **paired(first["orig"], first["gold"], first[n], ids)} for n in first if n.startswith("mutant:")]
    res["bug_trigger_rate"] = paired(first["orig"], first["gold"], first["gold"], ids)["bug_trigger"] / float(len(ids))
    res["draws_run"] = len(ids)
    res["eligible"] = True
    res["checks"] = feasibility_checks(res["patches"], res["mutants"], res["deterministic"])
    res["draws_compiled"] = len(ids)
    res["complete_draws_by_patch"] = {k: len(ids) - v["missing"] for k, v in res["patches"].items()}
    res["draws_run_definition"] = "legacy count of compiled mutant IDs, not guaranteed complete paired outcomes"
    res["method_limits"] = [
        "Unique test mutants are sampled without replacement; this is not the primary iid generator.",
        "Test literals may be in assertions as well as inputs; outcomes measure test signatures, not functional truth.",
        "Normalized failure text can retain nondeterministic differences; inspect raw records before interpreting effects.",
        "No prospective admission or population generalization claim is made."]
    res["seconds"] = round(time.time() - t0, 1)
    return res

