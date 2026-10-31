"""Study P: function-level draws for one instance and the scoring of candidate patches on the SAME inputs.
Runs inside the instance's environment (sys.executable); every snapshot runs at one common path (tools/fn_probe.py).

Inputs come from two sources in equal parts (protocol section 2): G0, the signature-driven generator
(gatekeeper_ext/fn_inputs.py), and G2, a model-written make_inputs program that was fixed BEFORE any patch existed.
They are interleaved in one seeded order, which is the order the sequential gates read them in.
"""
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def _runs(py, root, pythonpath, fn, work, tag, calls, gen, n, env):
    import fn_probe as FP
    import fn_probe_llm as FL
    out = {}
    if calls is not None:
        out["G0"] = FP.inner(py, root, pythonpath, fn["file"], fn["qualname"], "run", calls, Path(work) / (tag + ".g0.json"), n, env=env)
    if gen is not None:
        out["G2"] = FL.run_gen(py, root, pythonpath, fn["file"], fn["qualname"], gen, Path(work) / (tag + ".g2.json"), n, env)
    return out


def _stable(a, b):
    if a.get("status") != "RAN" or b.get("status") != "RAN":
        return set()
    return {i for i in range(min(len(a["outcomes"]), len(b["outcomes"]))) if a["outcomes"][i] == b["outcomes"][i] and a["outcomes"][i] != ["timeout"]}


def prepare_fn_base(py, orig, gold, pythonpath, fn, work, n=200, seed=0, env=None):
    """fn: {"file", "qualname", "generator_code"}.  Returns (base, None) or (None, {"reason": ...})."""
    import fn_probe as FP
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    calls = work / "g0.calls.json"
    gen = FP.inner(py, orig, pythonpath, fn["file"], fn["qualname"], "generate", calls, work / "g0.gen.json", n, seed, env=env)
    calls = calls if gen.get("status") == "GENERATED" else None
    code = None
    if fn.get("generator_code"):
        code = work / "g2.make_inputs.py"
        code.write_text(fn["generator_code"])
    if calls is None and code is None:
        return None, {"reason": "no input source: %s" % gen.get("reason")}
    o1 = _runs(py, orig, pythonpath, fn, work, "orig1", calls, code, n, env)
    o2 = _runs(py, orig, pythonpath, fn, work, "orig2", calls, code, n, env)
    g = _runs(py, gold, pythonpath, fn, work, "gold", calls, code, n, env)
    stable = {src: sorted(_stable(o1[src], o2[src]) & set(range(len(g[src].get("outcomes", []))))) for src in o1}
    order = [(src, i) for src in sorted(stable) for i in stable[src]]
    random.Random("order:%s:%s" % (seed, fn["qualname"])).shuffle(order)
    trigger = sum(1 for src, i in order if o1[src]["outcomes"][i] != g[src]["outcomes"][i])
    base = {"fn": fn, "calls": str(calls) if calls else None, "gen": str(code) if code else None, "n": n, "order": order,
            "orig": {s: o1[s].get("outcomes", []) for s in o1}, "gold": {s: g[s].get("outcomes", []) for s in g},
            "info": {"inputs_by_source": {s: len(stable[s]) for s in stable}, "stable_inputs": len(order), "bug_trigger_inputs": trigger,
                     "bug_trigger_rate": trigger / len(order) if order else 0.0}}
    (work / "fn_base_info.json").write_text(json.dumps(base["info"], indent=1))
    if not order:
        return None, {"reason": "no stable input"}
    return base, None


def score_fn_patch(py, base, orig, treated, pythonpath, work, tag, env=None, capture=False):
    """Run the patched snapshot twice on the same inputs; per input in the frozen order: harm = original agrees with the
    fix and the patch does not; help = original differs and the patch agrees; divergence = patch differs from the fix."""
    work = Path(work)
    patched = work / ("patched_" + tag)
    shutil.rmtree(patched, ignore_errors=True)
    shutil.copytree(orig, patched, ignore=shutil.ignore_patterns(".git"))
    for rel, src in treated.items():
        (patched / rel).write_text(src, encoding="utf-8")
    calls = Path(base["calls"]) if base["calls"] else None
    gen = Path(base["gen"]) if base["gen"] else None
    p1 = _runs(py, patched, base["fn"].get("pythonpath", []), base["fn"], work, tag + "_p1", calls, gen, base["n"], env)
    p2 = _runs(py, patched, base["fn"].get("pythonpath", []), base["fn"], work, tag + "_p2", calls, gen, base["n"], env)
    shutil.rmtree(patched, ignore_errors=True)
    stable = {s: _stable(p1[s], p2[s]) for s in p1}
    harm, helps, div, missing = [], 0, 0, 0
    by_source = {s: {"complete": 0, "harm": 0} for s in p1}           # stratified reporting (protocol section 4.5)
    for s, i in base["order"]:
        if i not in stable.get(s, set()):
            missing += 1
            continue
        o, g, p = base["orig"][s][i], base["gold"][s][i], p1[s]["outcomes"][i]
        harm.append(o == g and p != g)
        by_source[s]["complete"] += 1
        by_source[s]["harm"] += o == g and p != g
        helps += o != g and p == g
        div += p != g
    out = {"complete": len(harm), "missing": missing, "harm": harm, "help": helps, "divergent": div, "by_source": by_source,
            "deterministic": all(p1[s].get("status") == "RAN" for s in p1)}
    if capture:                                                   # amendment P-A5 (RQ5): keep every outcome; off by default
        out["outcomes"] = [{"source": s, "i": i, "orig": base["orig"][s][i], "gold": base["gold"][s][i],
                            "patch": p1[s]["outcomes"][i] if i < len(p1[s].get("outcomes", [])) else None,
                            "patch_stable": i in stable.get(s, set())} for s, i in base["order"]]
    return out, None
