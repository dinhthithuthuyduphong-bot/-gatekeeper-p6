"""Study Q robustness to the repository mix (post hoc, labelled as such): leave-one-repository-out estimates of Q4 (contract
regression share) and HQ1 (share of HQ1 units without a contract regression), with Wilson intervals.  Django contributes 215 of
469 instances, so a reviewer will ask whether one repository drives the result.
python tools/q_robustness.py OUT_DIR"""
import gzip
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import q_review_items as RI  # noqa: E402


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [(c - h) / d, (c + h) / d]


def main(argv):
    recs = [json.loads(l) for l in gzip.open(ROOT / "research_closure/results/study_q/Q_RECORDS.jsonl.gz", "rt")]
    by = defaultdict(lambda: {"patches": 0, "contract": 0, "units": 0, "without": 0})
    for r in recs:
        b = by[r["repo"]]
        for p in r.get("patches") or []:
            if p.get("status") == "SCORED":
                b["patches"] += 1
                b["contract"] += p["classified"]["contract_harm"] > 0
        u = RI.hq1_unit(r)
        if u:
            b["units"] += 1
            b["without"] += u["classified"]["contract_harm"] == 0
    tot = {k: sum(v[k] for v in by.values()) for k in ("patches", "contract", "units", "without")}
    loro = {}
    for repo, b in by.items():
        P, C = tot["patches"] - b["patches"], tot["contract"] - b["contract"]
        U, W = tot["units"] - b["units"], tot["without"] - b["without"]
        loro[repo] = {"Q4": C / P, "HQ1_units": U, "HQ1_without": W, "HQ1_share": W / U, "HQ1_wilson95": wilson(W, U)}
    res = {"per_repo": dict(by), "total": tot, "leave_one_repo_out": loro,
           "Q4_range": [min(v["Q4"] for v in loro.values()), max(v["Q4"] for v in loro.values())],
           "HQ1_share_range": [min(v["HQ1_share"] for v in loro.values()), max(v["HQ1_share"] for v in loro.values())],
           "HQ1_max_upper_bound": max(v["HQ1_wilson95"][1] for v in loro.values())}
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    (out / "Q_ROBUSTNESS.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("Q4_range", "HQ1_share_range", "HQ1_max_upper_bound")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
