"""Study T-A6 analysis: B9 (model applies the rule) against Gatekeeper on the same sampled cells; harm and cost.
python tools/b9_analyze.py RESULTS_DIR      (reads B9_*.json and STUDY_T_RESULT.json; writes B9_RESULT.json)"""
import json
import sys
from pathlib import Path

ETA, RUNNER_USD_PER_MIN, MIN_STABLE = 0.05, 0.008, 50


def cell_harm(rec):
    """Pooled change rate of B9's output over functions with enough stable reference inputs (None if none)."""
    rates = []
    for f in rec["functions"]:
        fl = f.get("b9_ref_flags")
        if fl == "":                          # model returned the function unchanged
            rates.append(0.0)
        elif fl and len(fl) >= MIN_STABLE:
            rates.append(fl.count("1") / len(fl))
    return sum(rates) / len(rates) if rates else None


def analyse(d, tag=""):
    d = Path(d)
    t = {r["cell"]: r for r in json.loads((d / "STUDY_T_RESULT.json").read_text())["rows"]}
    recs, spent = {}, 0.0
    files = sorted(d.glob("B9_%s_??.json" % tag)) if tag else sorted(p for p in d.glob("B9_??.json"))
    if not files:
        raise SystemExit("no B9 files for tier %r: refusing to write an empty result" % (tag or "cheap"))
    model = None
    for p in files:
        j = json.loads(p.read_text())
        spent += j["spent_usd"]
        m = "%s (%s)" % (j["model"], j.get("effort") or "low")
        if model and m != model:
            raise SystemExit("B9 files of tier %r mix models: %s and %s" % (tag, model, m))
        model = m
        recs.update(j["cells"])
    rows = []
    for cell, rec in recs.items():
        h = cell_harm(rec)
        g = t.get(cell, {})
        rows.append({"cell": cell, "truth_harmful": g.get("harmful"), "G": g.get("G"), "b9_rate": h,
                     "b9_harmful": None if h is None else h >= ETA,
                     "b9_failed": sum(1 for f in rec["functions"] if str(f.get("b9", "")).startswith("unparsable")),
                     "usd": rec["usd"], "llm_s": rec["llm_seconds"], "g_s": rec["g_seconds"]})
    ev = [r for r in rows if r["b9_harmful"] is not None]
    n = len(rows)
    res = {"tag": tag or "cheap", "model": model, "cells": n, "evaluable_b9": len(ev), "spent_usd": spent,
           "b9_harmful_applied": sum(1 for r in ev if r["b9_harmful"]),
           "b9_harmful_among_truth_harmful": sum(1 for r in ev if r["b9_harmful"] and r["truth_harmful"]),
           "b9_harmful_among_truth_safe": sum(1 for r in ev if r["b9_harmful"] and not r["truth_harmful"]),
           "g_harmful_admitted": sum(1 for r in rows if r["G"] and r["truth_harmful"]),
           "g_admitted": sum(1 for r in rows if r["G"]),
           "b9_unparsable_functions": sum(r["b9_failed"] for r in rows),
           "cost_per_cell": {"b9_usd": spent / max(1, n), "b9_seconds": sum(r["llm_s"] for r in rows) / max(1, n),
                             "g_seconds": sum(r["g_s"] for r in rows) / max(1, n),
                             "g_usd_runner": sum(r["g_s"] for r in rows) / max(1, n) / 60 * RUNNER_USD_PER_MIN},
           "rows": rows}
    res["B9_W"] = (res["g_harmful_admitted"] < res["b9_harmful_applied"]
                   and res["cost_per_cell"]["g_usd_runner"] <= res["cost_per_cell"]["b9_usd"])
    (d / ("B9_RESULT_%s.json" % tag if tag else "B9_RESULT.json")).write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    r = analyse(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
    print(json.dumps({k: v for k, v in r.items() if k != "rows"}, indent=1))
