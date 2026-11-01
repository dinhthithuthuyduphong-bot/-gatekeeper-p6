"""Study T-A6: B9, a model applies each sampled cell's rule directly to the touched functions; its output is tried with the same
harness and reference stream as the ground truth.  Also re-times Gatekeeper's gate-stream trials of the same cells.

python tools/market_b9.py WORK_DIR OUT_DIR MODELS.json --shard I --shards K [--cap 0.75]
"""
import ast
import hashlib
import json
import os
import random
import re
import shutil
import sys
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import composition_study as CS  # noqa: E402
import market_census as MC  # noqa: E402
import market_trials as MT  # noqa: E402
from gatekeeper_lite import b9 as B  # noqa: E402

PROMPT = ("Apply the lint rule below to this Python function. Keep its behaviour identical for every caller. Return only the "
          "complete rewritten function (no decorators, no explanation) in one ```python block; if the rule does not apply, return "
          "the function unchanged.")
N_SAFE, SEED = 139, "study-t-b9"


def sample(result):
    """All harmful Ruff cells plus N_SAFE other usable Ruff cells, uniformly with a fixed seed (T-A6)."""
    rows = [r for r in result["rows"] if not r["r2"]]
    harmful = sorted(r["cell"] for r in rows if r["harmful"])
    rest = sorted(r["cell"] for r in rows if not r["harmful"])
    rng = random.Random(int(hashlib.sha256(SEED.encode()).hexdigest(), 16))
    return harmful + rng.sample(rest, N_SAFE)


def rule_docs():
    import subprocess
    r = subprocess.run(["ruff", "rule", "--all", "--output-format", "json"], capture_output=True, text=True, check=True)
    return {d["code"]: {"name": d.get("name"), "explanation": d.get("explanation", "")} for d in json.loads(r.stdout)}


def find_def(tree, qualname):
    parts = qualname.split(".")

    def walk(node, i):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and ch.name == parts[i]:
                if i == len(parts) - 1:
                    return ch if not isinstance(ch, ast.ClassDef) else None
                return walk(ch, i + 1)
        return None
    return walk(tree, 0)


def function_source(src, qualname):
    node = find_def(ast.parse(src), qualname)
    if node is None:
        return None
    lines = src.splitlines(keepends=True)
    return node, "".join(lines[node.lineno - 1:node.end_lineno])


def code_block(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text or "", re.S)
    return m.group(1) if m else None


def replace_function(src, qualname, new_code):
    """Replace the def (not its decorators) of qualname by new_code, re-indented; None if the result does not parse."""
    node = find_def(ast.parse(src), qualname)
    if node is None or new_code is None:
        return None
    lines = src.splitlines(keepends=True)
    indent = " " * node.col_offset
    body = textwrap.indent(textwrap.dedent(new_code).strip("\n") + "\n", indent)
    out = "".join(lines[:node.lineno - 1]) + body + "".join(lines[node.end_lineno:])
    try:
        ast.parse(out)
    except SyntaxError:
        return None
    return out


def flags(py, root, snap, pp, f, q, seed, n, work, tag):
    calls = work / (tag + ".calls.json")
    gen = CS.inner(py, root, pp, f, q, "generate", calls, work / (tag + ".gen.json"), n, seed)
    if gen.get("status") != "GENERATED":
        return None
    runs = [CS.inner(py, d, pp, f, q, "run", calls, work / ("%s.%s%d.json" % (tag, nm, i)), n, seed)
            for nm, d in (("o", root), ("v", snap)) for i in (1, 2)]
    if any(r.get("status") != "RAN" for r in runs):
        return None
    a, b, c, d = (r["outcomes"] for r in runs)
    m = min(map(len, (a, b, c, d)))
    return [int(a[i] != c[i]) for i in range(m) if a[i] == b[i] and c[i] == d[i] and a[i] != ["timeout"] and c[i] != ["timeout"]]


def run(argv):
    work, out, models = Path(argv[0]), Path(argv[1]), argv[2]
    opt = lambda key, d: type(d)(argv[argv.index(key) + 1]) if key in argv else d   # noqa: E731
    shard, shards, cap, n = opt("--shard", 0), opt("--shards", 1), opt("--cap", 0.75), 200
    model, effort, tag = opt("--model", "vertex-gemini-flash"), opt("--effort", ""), opt("--tag", "")   # T-A7
    MT.configure_harness()
    res_t = json.loads((MT.RES / "STUDY_T_RESULT.json").read_text())
    cells = sample(res_t)
    census = {p["project"]: p for p in json.loads((MT.RES / "MARKET_CENSUS.json").read_text())["packages"]}
    targets = {t["project"]: t for t in json.loads((MT.RES / "TARGETS.json").read_text())["selected"]}
    rules = rule_docs()
    from cohort_inner import RefreshingClient
    cfg = next(m for m in json.loads(Path(models).read_text())["models"] if m["name"] == model)
    extra = dict(cfg.get("extra", {}), **({"reasoning_effort": effort} if effort else {}))
    client = RefreshingClient(cfg["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", "")), cfg["key_env"], extra)
    guard = B.SpendGuard(cap)
    by_pkg = {}
    for c in cells:
        by_pkg.setdefault(c.split("/", 1)[0], []).append(c.split("/", 1)[1])
    pkgs = sorted(by_pkg)[shard::shards]
    results = {}
    for proj in pkgs:
        t = targets[proj]
        w = work / proj
        meta = json.loads(MC.fetch("https://pypi.org/pypi/%s/%s/json" % (proj, t["version"])))
        sd = next(f for f in meta["urls"] if f["filename"] == t["sdist"])
        root = MT.extract_all(MC.fetch(sd["url"], 300), sd["filename"], w / "src")
        py, _log = MT.env_for(w, root, proj, t["version"])
        for rule in by_pkg[proj]:
            cell = census[proj]["cells"][rule]
            fs = MT.funcs_of(cell, 5)
            rec = {"cell": "%s/%s" % (proj, rule), "functions": [], "usd": 0.0, "llm_seconds": 0.0, "g_seconds": 0.0}
            # Gatekeeper's cost: the gate-stream trials of Ruff's fix on this cell, re-timed here
            gsnap = w / "gsnap"
            shutil.rmtree(gsnap, ignore_errors=True)
            shutil.copytree(root, gsnap, symlinks=True)
            MT.apply_skill(rule, gsnap, sorted({f for f, _ in fs}), {})
            # B9: the model rewrites each touched function
            bsnap = w / "bsnap"
            shutil.rmtree(bsnap, ignore_errors=True)
            shutil.copytree(root, bsnap, symlinks=True)
            for f, q in fs:
                src = (bsnap / f).read_text(encoding="utf-8")
                fsrc = function_source(src, q)
                fr = {"file": f, "qualname": q}
                if fsrc is None:
                    fr["b9"] = "function not found"
                    rec["functions"].append(fr)
                    continue
                info = rules.get(rule, {})
                user = "Rule %s (%s):\n%s\n\nFunction:\n```python\n%s```" % (rule, info.get("name"), (info.get("explanation") or "")[:800], fsrc[1])
                msgs = [{"role": "system", "content": PROMPT}, {"role": "user", "content": user}]
                try:
                    guard.check(msgs, 4000, cfg["prices_usd_per_mtok"])
                except B.BudgetExceeded:
                    fr["b9"] = "budget cap reached"
                    rec["functions"].append(fr)
                    continue
                t0 = time.time()
                r = client.complete(cfg["model_id"], msgs, 4000, 0.0, 1)
                rec["llm_seconds"] += time.time() - t0
                rec["usd"] += guard.add(r["usage"], cfg["prices_usd_per_mtok"])
                new = replace_function(src, q, code_block(r["text"]))
                fr["b9"] = "applied" if new is not None else "unparsable reply (left unchanged)"
                fr["b9_changed_source"] = new is not None and new != src
                if new is not None:
                    (bsnap / f).write_text(new, encoding="utf-8")
                rec["functions"].append(fr)
            for fr in rec["functions"]:
                f, q = fr["file"], fr["qualname"]
                pp = [MT.import_root(root, f)] if MT.import_root(root, f) else []
                ftag = hashlib.sha1((rec["cell"] + q).encode()).hexdigest()[:10]   # not `tag`: that is the tier (T-A7 bug)
                t0 = time.time()
                gflags = flags(py, root, gsnap, pp, f, q, MT.SEEDS["gate"], n, w, ftag + "g")
                rec["g_seconds"] += time.time() - t0
                fr["gatekeeper_gate_flags_ok"] = gflags is not None
                fr["b9_ref_flags"] = None
                if fr.get("b9_changed_source"):
                    bf = flags(py, root, bsnap, pp, f, q, MT.SEEDS["ref"], n, w, ftag + "b")
                    fr["b9_ref_flags"] = "".join(map(str, bf)) if bf is not None else None
                elif fr.get("b9", "").startswith("applied"):
                    fr["b9_ref_flags"] = ""          # unchanged source: no behaviour change
            shutil.rmtree(gsnap, ignore_errors=True)
            shutil.rmtree(bsnap, ignore_errors=True)
            results[rec["cell"]] = rec
        shutil.rmtree(w, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    name = ("B9_%s_%02d.json" % (tag, shard)) if tag else ("B9_%02d.json" % shard)
    (out / name).write_text(json.dumps({"model": cfg["model_id"], "effort": extra.get("reasoning_effort"), "spent_usd": guard.spent_usd,
                                        "cells": results}))
    print(json.dumps({"shard": shard, "cells": len(results), "usd": round(guard.spent_usd, 4)}))
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
