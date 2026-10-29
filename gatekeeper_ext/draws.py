"""Per-draw measurements of one instance, reusing the helpers of the frozen harness (gatekeeper_ext/testmut.py,
tm-dev-v4-reach) WITHOUT modifying it.  Runs inside the instance's own virtual environment.

prepare_base: everything that does not depend on the patch (baseline, reach filter, the draws, the outcomes of the
              original and of the upstream fix, two repetitions each); done once per instance.
score_patch : the outcomes of one candidate patch on the same draws (two repetitions), and the per-draw flags that
              the gates of gatekeeper_ext/gates.py need.
"""
import json
from pathlib import Path

from gatekeeper_ext import testmut as T


def prepare_base(orig_root, gold_root, modules, pythonpath, runner, census, work, seed, n_draws=200):
    """Returns (base, None) or (None, {"reason": ...})."""
    orig_root, gold_root, work = Path(orig_root), Path(gold_root), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    files = T.expand_files(orig_root, census)
    if not files:
        return None, {"reason": "configured test entries resolved to zero files"}
    baseline, err = T.run_tests(orig_root, runner, files, pythonpath, None, work, "baseline")
    if baseline is None:
        return None, {"reason": "baseline test run produced no result", "tail": err}
    edited = T.edited_with_lines(orig_root, gold_root, modules)
    if not edited:
        return None, {"reason": "no edited function present in both versions"}
    reached, rerr = T.run_reach(orig_root, runner, files, pythonpath, edited, work, "reach")
    if reached is None:
        return None, {"reason": "reach pass failed", "tail": rerr}
    funcs = T.eligible_functions(orig_root, files, baseline, reached)
    if not funcs:
        return None, {"reason": "no passing fast test reaches the edited code"}
    mut = T.make_mutants(funcs, n_draws, seed)
    texts, ok = T.build_mutated_sources(orig_root, mut)
    ids = sorted(ok)
    if not ids:
        return None, {"reason": "no mutated test compiled"}
    sigs = {}
    for name, root in (("orig", orig_root), ("gold", gold_root)):
        s, e = T.run_arm(root, name, texts, {}, runner, pythonpath, work, 2)
        if s is None:
            return None, {"reason": "arm run failed: " + name, "tail": e}
        sigs[name] = s
    first_o, first_g = sigs["orig"][0], sigs["gold"][0]
    complete = [k for k in ids if k in first_o and k in first_g]
    differs = sum(1 for k in complete if first_o[k] != first_g[k])
    base = {"ids": ids, "texts": texts, "sig_orig": first_o, "sig_gold": first_g,
            "deterministic": sigs["orig"][0] == sigs["orig"][1] and sigs["gold"][0] == sigs["gold"][1],
            "info": {"test_files": len(files), "baseline_cases": len(baseline), "baseline_passed": sum(1 for r in baseline if r["status"] == "passed"),
                     "edited_functions": [e["qualname"] for e in edited], "eligible_test_functions_unfiltered": len(T.eligible_functions(orig_root, files, baseline)),
                     "eligible_test_functions": len(funcs), "draws_compiled": len(ids), "draws_complete_orig_gold": len(complete),
                     "bug_trigger_draws": differs, "bug_trigger_rate": differs / float(len(complete)) if complete else 0.0,
                     "common_failure_fraction": T.common_failure_fraction({"orig": first_o, "gold": first_g}, ids)}}
    (work / "base_info.json").write_text(json.dumps(base["info"], indent=1))
    return base, None


def score_patch(base, orig_root, treated, pythonpath, runner, work, tag):
    """treated: {relative path: new source}.  Returns (score, None) or (None, error text)."""
    sigs, err = T.run_arm(Path(orig_root), "patch_" + tag, base["texts"], treated, runner, pythonpath, Path(work), 2)
    if sigs is None:
        return None, err
    s = sigs[0]
    rows, missing = [], 0
    for k in base["ids"]:
        a, g, p = base["sig_orig"].get(k), base["sig_gold"].get(k), s.get(k)
        if a is None or g is None or p is None:
            missing += 1
            continue
        rows.append({"id": k, "l0": a != g, "l1": p != g})
    return {"deterministic": sigs[0] == sigs[1], "complete": len(rows), "missing": missing,
            "harm": [(not r["l0"]) and r["l1"] for r in rows], "help": sum(1 for r in rows if r["l0"] and not r["l1"]),
            "still_wrong": sum(1 for r in rows if r["l0"] and r["l1"])}, None
