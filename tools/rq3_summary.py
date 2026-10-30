"""RQ3 summary (plan: research_closure/results/RQ3_PLAN.md): agreement between hand-written and automatic generators on
DETECTING the behaviour change of a learned skill, over the evaluation targets.
python tools/rq3_summary.py DIR OUT_DIR"""
import json
import sys
from pathlib import Path


def cp_interval(k, n, alpha=0.05):
    """Clopper & Pearson (1934) exact interval by bisection on the binomial tail (standard library only)."""
    from math import comb

    def tail_ge(p):
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

    def tail_le(p):
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))

    def solve(f, target):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(tail_ge, alpha / 2)
    upper = 1.0 if k == n else 1 - solve(lambda p: tail_le(1 - p), alpha / 2)
    return lower, upper


def kappa(pairs):
    """Cohen (1960) kappa for two binary raters."""
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    pa, pb = sum(a for a, _ in pairs) / n, sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def main(d, out):
    recs = [json.loads(f.read_text()) for f in sorted(Path(d).rglob("RQ3_*.json"))]
    usable = [r for r in recs if r.get("status") == "FINISHED" and (r.get("hand") or {}).get("ran")]
    rows, res = [], {"targets": len(recs), "measured": len(usable)}
    for gen in ("G0", "G2", "G0_or_G2"):
        pairs = []
        for r in usable:
            if gen == "G0_or_G2":
                if "G0" not in r and "G2" not in r:
                    continue
                auto = bool((r.get("G0") or {}).get("detects") or (r.get("G2") or {}).get("detects"))
            elif gen in r:
                auto = bool(r[gen].get("detects"))
            else:
                continue
            pairs.append((bool(r["hand"]["detects"]), auto))
        agree = sum(a == b for a, b in pairs)
        lo, hi = cp_interval(agree, len(pairs)) if pairs else (None, None)
        res[gen] = {"targets": len(pairs), "agree": agree, "agreement": round(agree / len(pairs), 3) if pairs else None,
                    "agreement_cp95": [round(lo, 3), round(hi, 3)] if pairs else None, "kappa": kappa(pairs),
                    "hand_detects_auto_misses": sum(1 for a, b in pairs if a and not b), "auto_detects_hand_misses": sum(1 for a, b in pairs if b and not a)}
    for r in recs:
        rows.append({"target": r.get("target"), "status": r.get("status"), "hand": (r.get("hand") or {}).get("detects"),
                     "G0": (r.get("G0") or {}).get("detects"), "G2": (r.get("G2") or {}).get("detects"),
                     "hand_scopes": {s: v.get("rate") for s, v in ((r.get("hand") or {}).get("scopes") or {}).items()}})
    res["rows"] = rows
    Path(out).mkdir(parents=True, exist_ok=True)
    (Path(out) / "RQ3_SUMMARY.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
