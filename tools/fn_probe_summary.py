"""Feasibility funnel of the function-level oracle, next to the test-level result of Study N stage N-S3 for the same
instances.  python tools/fn_probe_summary.py DIR S3_ROWS.json OUT_DIR"""
import collections
import json
import statistics
import sys
from pathlib import Path

ORDER = ["snapshots or environment failed", "no edited function present in both versions", "no edited function could be imported or called",
         "unstable outcomes", "the original never differs from the fix on generated inputs", "usable"]


def main(d, s3_rows, out):
    recs = {r["name"]: r for r in (json.loads(f.read_text()) for f in sorted(Path(d).rglob("FNPROBE_*.json")))}
    s3 = {r["name"]: r for r in json.loads(Path(s3_rows).read_text())}
    funnel = collections.Counter(r.get("verdict") for r in recs.values())
    usable = [r for r in recs.values() if r.get("verdict") == "usable"]
    rates = [f["trigger_rate"] for r in usable for f in r["functions"] if f.get("usable")]
    both = collections.Counter((bool(s3.get(n, {}).get("pass")), r.get("verdict") == "usable") for n, r in recs.items())
    why = collections.Counter(f.get("why", "")[:70] for r in recs.values() for f in r.get("functions", []) if not f.get("usable"))
    summary = {"instances": len(recs), "funnel": {k: funnel.get(k, 0) for k in ORDER}, "usable": len(usable),
               "usable_share": round(len(usable) / len(recs), 3) if recs else None,
               "trigger_rate_of_usable_functions": {"median": statistics.median(rates), "min": min(rates), "max": max(rates)} if rates else None,
               "test_level_vs_function_level": {"both usable": both[(True, True)], "only test-level": both[(True, False)],
                                                "only function-level": both[(False, True)], "neither": both[(False, False)]},
               "function_failure_reasons": dict(why.most_common(12)),
               "note": "Development measurement on the Study N A* instances (exposed at N-S2 and N-S3, not to the function-level oracle)."}
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    (o / "FNPROBE_SUMMARY.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
