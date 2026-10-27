"""Summarise stage S2 (vetting) of the Study M A* track and apply gate M1 exactly as registered.

python tools/s2_summary.py ARTIFACT_DIR CANDIDATES.json OUT_DIR [LIMIT=250] [THRESHOLD=40] [MIN_CANDIDATES=80]
(Study M gate M1: 250 40 80.  Study N gate N1: 400 60 200.)

ARTIFACT_DIR holds the extracted M_VET_* artifacts (any nesting).  Gate M1 (study_m_astar/GATES.md): at least 40
ELIGIBLE among the first min(250, n) candidates; fewer than 80 candidates fails the gate.  The non-eligible cases are
classified from the vetting logs so that the attrition table says WHY, but the classification never changes the gate.
"""
import collections
import json
import re
import sys
from pathlib import Path


def category(r):
    v = r.get("verdict", "")
    if v == "ELIGIBLE":
        return "eligible (fail-before, pass-after test)"
    if v.startswith("VETTING_ERROR"):
        return "vetting tool error"
    s = r.get("summary") or {}
    if sum(s.values()) > 0:
        return "tests ran, no fail-to-pass test"
    t = " ".join(((r.get("arms") or {}).get(k) or {}).get("tail") or "" for k in ("pre", "gold"))
    if re.search(r"No module named '", t):
        return "tests not runnable: missing python module"
    if re.search(r"conftest|fixture", t):
        return "tests not runnable: conftest or fixture error"
    return "tests not runnable: other"


def main(art, cands_path, out, limit=250, threshold=40, min_candidates=80):
    vet = {}
    for f in Path(art).rglob("VETTING_*.json"):
        r = json.loads(f.read_text())
        vet[r["name"]] = r
    cands = json.loads(Path(cands_path).read_text())[: int(limit)]
    rows, missing_mods = [], collections.Counter()
    for i, c in enumerate(cands):
        r = vet.get(c["name"])
        cat = category(r) if r else "no vetting result"
        rows.append({"position": i, "name": c["name"], "repo": c["repo"], "pr": c["pr"], "category": cat,
                     "f2p": (r or {}).get("summary", {}).get("F->P", 0) if r else 0})
        if r and cat == "tests not runnable: missing python module":
            t = " ".join(((r.get("arms") or {}).get(k) or {}).get("tail") or "" for k in ("pre", "gold"))
            missing_mods.update({m.split(".")[0] for m in re.findall(r"No module named '([\w\.]+)'", t)})
    cnt = collections.Counter(r["category"] for r in rows)
    eligible = cnt["eligible (fail-before, pass-after test)"]
    runnable = eligible + cnt["tests ran, no fail-to-pass test"]
    gate = "PASS" if (len(cands) >= int(min_candidates) and eligible >= int(threshold)) else "FAIL"
    summary = {"candidates_considered": len(cands), "vetting_results": sum(1 for r in rows if r["category"] != "no vetting result"),
               "categories": dict(cnt), "eligible": eligible, "runnable": runnable,
               "eligible_share_of_runnable": round(eligible / runnable, 3) if runnable else None,
               "gate": gate, "gate_M1": gate, "threshold": ">= %s eligible among the first %d (at least %s candidates)" % (threshold, len(cands), min_candidates),
               "eligible_repositories": len({r["repo"] for r in rows if r["category"].startswith("eligible")}),
               "most_missing_modules": missing_mods.most_common(15)}
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    (o / "S2_ROWS.json").write_text(json.dumps(rows, indent=1))
    (o / "S2_SUMMARY.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:7]))
