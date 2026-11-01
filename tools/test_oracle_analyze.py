"""Study T-A4 analysis: TS (admit iff the package's own stable-passing tests still pass) against every rule, and the
independent-oracle check of Gatekeeper's admissions.  Reads STUDY_T_RESULT.json and TS_*.json; writes TS_RESULT.json.

python tools/test_oracle_analyze.py RESULTS_DIR
"""
import json
import math
import sys
from pathlib import Path

ETA = 0.05
RULES = ["U", "RS", "B6S", "LJ", "S20", "B8", "G", "G_FDR"]


def wilson_hi(k, n, z=1.96):
    if not n:
        return 1.0
    p = k / n
    d = 1 + z * z / n
    return min(1.0, (p + z * z / (2 * n) + z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d)


def analyse(d):
    rows = {r["cell"]: r for r in json.loads((d / "STUDY_T_RESULT.json").read_text())["rows"]}
    ts, pk = {}, {"packages": 0, "applicable": 0, "errors": [], "not_applicable": []}
    seconds = []
    for p in sorted(d.glob("TS_*.json")):
        t = json.loads(p.read_text())
        pk["packages"] += 1
        if t.get("error"):
            pk["errors"].append({"project": t["project"], "error": t["error"]})
            continue
        if not t.get("applicable"):
            pk["not_applicable"].append(t["project"])
            continue
        pk["applicable"] += 1
        for rule, c in t["cells"].items():
            if c.get("status") == "run":
                ts["%s/%s" % (t["project"], rule)] = c
                seconds.append(c["seconds"])
    cells = [rows[c] | {"TS": ts[c]["admit"]} for c in ts if c in rows]
    harm = [r for r in cells if r["harmful"]]
    safe = [r for r in cells if not r["harmful"]]
    score = {}
    for k in RULES + ["TS"]:
        if k in ("RS", "B6S"):
            sub_h, sub_s = [r for r in harm if not r["r2"]], [r for r in safe if not r["r2"]]
        elif k == "LJ":
            sub_h, sub_s = [r for r in harm if r.get("LJ") is not None], [r for r in safe if r.get("LJ") is not None]
        else:
            sub_h, sub_s = harm, safe
        if k != "TS" and not any(k in r for r in cells):
            continue
        score[k] = {"harmful_admitted": sum(1 for r in sub_h if r.get(k) is True or (k == "U")),
                    "harmful_total": len(sub_h),
                    "safe_admitted": sum(1 for r in sub_s if r.get(k) is True or (k == "U")), "safe_total": len(sub_s)}
    g_adm = [c for c in ts if c in rows and rows[c].get("G")]
    confirmed = [c for c in g_adm if not ts[c]["admit"] and ts[c].get("confirmed")]
    unconfirmed = [c for c in g_adm if not ts[c]["admit"] and not ts[c].get("confirmed")]
    g, t = score["G"], score["TS"]
    res = {"packages": pk, "cells_run": len(cells), "harmful": len(harm), "safe": len(safe), "scores": score,
           "not_run_budget": sum(1 for p in d.glob("TS_*.json") for c in json.loads(p.read_text()).get("cells", {}).values()
                                 if c.get("status") == "not run (budget)"),
           "ts_seconds_per_cell": round(sum(seconds) / len(seconds), 1) if seconds else None,
           "harmful_rejected_by_ts": sum(1 for r in harm if not r["TS"]),
           "g_admitted": len(g_adm), "g_admitted_ts_confirmed_reject": len(confirmed),
           "g_admitted_ts_unconfirmed_reject": len(unconfirmed), "confirmed_cells": confirmed[:50],
           "confirmed_rate_wilson_hi": round(wilson_hi(len(confirmed), len(g_adm)), 4)}
    res["TS_W1"] = (g["harmful_admitted"] < t["harmful_admitted"]) or (
        g["harmful_admitted"] == t["harmful_admitted"] == 0 and g["safe_admitted"] >= t["safe_admitted"])
    res["TS_W2"] = bool(g_adm) and res["confirmed_rate_wilson_hi"] <= ETA
    (d / "TS_RESULT.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    r = analyse(Path(sys.argv[1]))
    print(json.dumps({k: v for k, v in r.items() if k != "confirmed_cells"}, indent=1))
