"""Study Q analysis, as registered (study_q/STUDY_Q_PROTOCOL.md section 6).
python tools/q_analyze.py ARTIFACT_DIR FRAME_SIZE OUT_DIR [--boot 10000]"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p_analyze import binom_sf, wilson  # noqa: E402

MIN_UNITS = 18                                                    # gate Q-G1 (protocol section 5)


def boot(rows, key, cluster, B, seed=13):
    by = {}
    for r in rows:
        by.setdefault(r[cluster], []).append(1 if r[key] else 0)
    groups = list(by.values())
    if not groups:
        return None, None
    rng, est = random.Random(seed), []
    for _ in range(B):
        s = [rng.choice(groups) for _ in groups]
        n = sum(len(g) for g in s)
        est.append(sum(map(sum, s)) / n if n else 0.0)
    est.sort()
    return est[int(0.025 * B)], est[int(0.975 * B) - 1]


def share(rows, key, B):
    k, n = sum(1 for r in rows if r[key]), len(rows)
    return {"k": k, "n": n, "share": k / n if n else None, "wilson95": wilson(k, n) if n else None,
            "boot_instance95": boot(rows, key, "instance", B), "boot_repo95": boot(rows, key, "repo", B)}


def hq1(recs, key):
    units = []
    for r in recs:
        naive = [p for p in sorted(r.get("patches") or [], key=lambda p: p["order"]) if p.get("status") == "SCORED" and p["classified"]["naive_harm"] > 0]
        if naive:
            units.append(naive[0]["classified"][key] == 0)    # True = the naive harm is NOT a contract regression
    k, n = sum(units), len(units)
    res = {"units": n, "without_contract_regression": k, "share": k / n if n else None, "wilson95": wilson(k, n) if n else None,
           "gate_Q_G1_met": n >= MIN_UNITS}
    if n >= MIN_UNITS:
        res["p_value_one_sided_vs_0.5"] = binom_sf(k, n, 0.5)
        res["HQ1_supported_at_0.05"] = res["p_value_one_sided_vs_0.5"] <= 0.05
    return res


def main(argv):
    art, frame, out = argv[0], int(argv[1]), Path(argv[2])
    B = int(argv[argv.index("--boot") + 1]) if "--boot" in argv else 10000
    recs = [json.loads(f.read_text()) for f in sorted(Path(art).rglob("Q_*.json"))]
    funnel = {"frame": frame, "records": len(recs)}
    for r in recs:
        funnel[r["status"]] = funnel.get(r["status"], 0) + 1
    rows = []
    for r in recs:
        for p in r.get("patches") or []:
            if p.get("status") != "SCORED":
                continue
            c = p["classified"]
            rows.append({"instance": r["instance_id"], "repo": r["repo"], "divergent": c["divergent"] > 0, "naive": c["naive_harm"] > 0,
                         "contract": c["contract_harm"] > 0, "c1": c["c1_only_harm"] > 0,
                         "early": any(s[:4] < "2025" for s in p["submissions"]), "distinct3": (r.get("distinct_patches") or 0) >= 3,
                         "g0_contract": sum(v for k, v in c["by_source"].get("G0", {}).items() if k in ("C1", "C2-D")) > 0,
                         "g2_contract": sum(v for k, v in c["by_source"].get("G2", {}).items() if k in ("C1", "C2-D")) > 0})
    res = {"Q1_funnel": funnel, "patches_scored": len(rows),
           "Q2_divergent": share(rows, "divergent", B), "naive_harm": share(rows, "naive", B), "Q4_contract_regression": share(rows, "contract", B),
           "HQ1": hq1(recs, "contract_harm")}
    q2, q4 = res["naive_harm"]["share"], res["Q4_contract_regression"]["share"]
    res["Q5_inflation_naive_over_contract"] = (q2 / q4) if q2 and q4 else None
    res["sensitivity"] = {"C1_only": {"Q4": share(rows, "c1", B), "HQ1": hq1(recs, "c1_only_harm")},
                          "G0_only_contract": share(rows, "g0_contract", B), "G2_only_contract": share(rows, "g2_contract", B),
                          "submissions_before_2025": share([x for x in rows if x["early"]], "contract", B),
                          "instances_with_3_distinct": share([x for x in rows if x["distinct3"]], "contract", B)}
    out.mkdir(parents=True, exist_ok=True)
    (out / "Q_ANALYSIS.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("Q1_funnel", "patches_scored", "HQ1")}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
