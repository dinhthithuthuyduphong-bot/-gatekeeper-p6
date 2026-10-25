"""Gold-differential admission harness (Study L, amendment L-A1).  Compatible with Python 3.8.

Ground truth is the upstream developers' fix, not a researcher-written oracle:
    l0 = [original code differs from the gold fix on the draw],  l1 = [patch differs from the gold fix],
    Z = l1 - l0 in {-1, 0, 1},  R = [l0 = 0 and l1 = 1]   (the definition used in the paper).
Draws come from a fixed algorithm (recorded calls of the edited functions, optional type-confusion
mutation of one argument); nothing about the target is hand-written.
"""
import ast
import json
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import golddiff_oracle as O  # noqa: E402
from gatekeeper_ext.mutants import functions, mutants  # noqa: E402
from gatekeeper_lite.drawharness import _Worker  # noqa: E402

P_MUTATE = 0.5          # probability that a draw mutates one argument (algorithm constant, pre-declared)


def edited_functions(orig_root, gold_root, modules):
    """Functions present in both versions whose AST differs (module-level functions and methods)."""
    out = []
    for rel in modules:
        a, b = Path(orig_root) / rel, Path(gold_root) / rel
        if not (a.exists() and b.exists()):
            continue
        fa, fb = functions(ast.parse(a.read_text(encoding="utf-8"))), functions(ast.parse(b.read_text(encoding="utf-8")))
        for q, (na, first) in fa.items():
            if q in fb and ast.dump(na) != ast.dump(fb[q][0]):
                out.append({"file": rel, "qualname": q, "first_line": first})
    return out


def module_name(rel, pythonpath):
    rel = rel.replace("\\", "/")
    for p in sorted(pythonpath, key=len, reverse=True):
        p = p.strip("/")
        if p and rel.startswith(p + "/"):
            rel = rel[len(p) + 1:]
            break
    if rel.endswith("/__init__.py"):
        rel = rel[:-len("/__init__.py")]
    elif rel.endswith(".py"):
        rel = rel[:-3]
    return rel.replace("/", ".")


def make_draws(pool, n, seed):
    rng = random.Random("%s:golddiff:v1" % seed)
    usable = [i for i, f in enumerate(pool["functions"]) if f["calls"]]
    draws = []
    for _ in range(n):
        fi = rng.choice(usable)
        f = pool["functions"][fi]
        ci = rng.randrange(len(f["calls"]))
        m = None
        if rng.random() < P_MUTATE:
            nargs, kws = f["shape"][ci]
            cands = [["p", i] for i in range(1 if f["skip_first"] else 0, nargs)] + [["k", k] for k in kws]
            if cands:
                kind, key = rng.choice(cands)
                m = [kind, key, rng.randrange(O.N_CONFUSION)]
        draws.append({"f": fi, "c": ci, "m": m})
    return draws


def run_arm(snapshot, pythonpath, oracle_path, draws, seed):
    w = _Worker(Path(snapshot), pythonpath, Path(oracle_path), seed)
    try:
        return [w.run(d) for d in draws]
    finally:
        w.close()


def _out(o):
    return None if "harness_error" in o else o.get("out")


def paired(orig, gold, patch):
    s = {"help": 0, "hurt": 0, "tie": 0, "bug_trigger": 0, "harness_errors": 0}
    for a, g, p in zip(map(_out, orig), map(_out, gold), map(_out, patch)):
        if a is None or g is None or p is None:
            s["harness_errors"] += 1
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


def analyze(orig_root, gold_root, modules, pythonpath, runner, test_args, work_dir, seed, patches,
            n_draws=300, n_mutants=5, record_timeout=3600):
    """Run gate G1 for one instance.  patches: {name: snapshot_root} of known-good patches."""
    orig_root, gold_root, work = Path(orig_root), Path(gold_root), Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    res = {"seed": seed, "n_draws": n_draws, "modules": modules}
    edited = edited_functions(orig_root, gold_root, modules)
    res["edited_functions"] = [e["qualname"] for e in edited]
    if not edited:
        return dict(res, eligible=False, reason="no edited function present in both versions")
    targets = [{"module": module_name(e["file"], pythonpath), "qualname": e["qualname"], "file": e["file"]} for e in edited]
    (work / "targets.json").write_text(json.dumps(targets))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=os.pathsep.join([str(orig_root / p) for p in pythonpath] + [str(orig_root), str(ROOT)]))
    try:
        proc = subprocess.run([sys.executable, "-m", "gatekeeper_ext.record_run", str(work / "targets.json"),
                               str(work / "recorded.json"), runner] + list(test_args),
                              cwd=str(orig_root), env=env, capture_output=True, text=True, timeout=record_timeout)
    except subprocess.TimeoutExpired:
        return dict(res, eligible=False, reason="recording timed out")
    res["record_tail"] = (proc.stdout + proc.stderr)[-600:]
    if not (work / "recorded.json").exists():
        return dict(res, eligible=False, reason="recording produced no output")
    rec = json.loads((work / "recorded.json").read_text())
    pool = {"functions": rec["functions"]}
    res["recorded"] = [{"qualname": f["qualname"], "calls": len(f["calls"]), "note": f["note"],
                        "unpicklable": f["unpicklable"]} for f in rec["functions"]]
    if not any(f["calls"] for f in pool["functions"]):
        return dict(res, eligible=False, reason="no call of an edited function was recorded")
    odir = work / "oracle"
    odir.mkdir(exist_ok=True)
    shutil.copy(ROOT / "gatekeeper_ext" / "golddiff_oracle.py", odir / "oracle.py")
    (odir / "pool.json").write_text(json.dumps(pool))
    draws = make_draws(pool, n_draws, seed)
    res["mutated_draw_fraction"] = sum(1 for d in draws if d["m"] is not None) / float(n_draws)
    arms = {"orig": orig_root, "gold": gold_root}
    arms.update({"patch:" + k: v for k, v in patches.items()})
    mut_dirs = {}
    for fpath in sorted({e["file"] for e in edited}):
        src = (gold_root / fpath).read_text(encoding="utf-8")
        names = [e["qualname"] for e in edited if e["file"] == fpath]
        for desc, new in mutants(src, names, n_mutants):
            if len(mut_dirs) >= n_mutants:
                break
            d = work / ("mutant%d" % len(mut_dirs))
            shutil.copytree(gold_root, d, ignore=shutil.ignore_patterns(".git"))
            (d / fpath).write_text(new, encoding="utf-8")
            mut_dirs[desc] = d
            arms["mutant:" + desc] = d
    runs = []
    for _ in range(3):                                   # three fresh-worker repetitions
        runs.append({name: run_arm(root, pythonpath, odir / "oracle.py", draws, seed) for name, root in arms.items()})
    first = runs[0]
    res["deterministic"] = all(runs[i][name] == first[name] for i in (1, 2) for name in arms)
    res["patches"] = {k: paired(first["orig"], first["gold"], first["patch:" + k]) for k in patches}
    res["mutants"] = [{"desc": d, **paired(first["orig"], first["gold"], first["mutant:" + d])} for d in mut_dirs]
    res["bug_trigger_rate"] = paired(first["orig"], first["gold"], first["gold"])["bug_trigger"] / float(n_draws)
    res["eligible"] = True
    a = bool(res["patches"]) and all(v["help"] > 0 for v in res["patches"].values())
    b = bool(res["patches"]) and all(v["hurt"] == 0 for v in res["patches"].values())
    d = any(m["hurt"] > 0 for m in res["mutants"])
    clean = all(v["harness_errors"] == 0 for v in list(res["patches"].values()) + res["mutants"])
    res["g1"] = {"a_detects_bug_with_known_good_patch": a, "b_no_regression_for_known_good_patch": b,
                 "c_deterministic_in_three_fresh_runs": res["deterministic"], "d_catches_a_mutant": d,
                 "no_harness_errors": clean, "pass": bool(a and b and res["deterministic"] and d and clean)}
    return res
