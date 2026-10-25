"""Development summary of the test-level differential.  python tools/tm_summary.py DIR OUT.md"""
import json
import sys
from pathlib import Path

ORDER = ["D1_py_ecc", "D2_cerberus", "D3_speckit", "D4_openfeature", "D5_pycubrid", "A1_speckit_catalog"]


def main(d, out):
    res = {}
    for f in Path(d).rglob("TM_*.json"):
        r = json.loads(f.read_text())
        res[r["target"]] = r
    L = ["# Test-level differential: development feasibility (NOT evidence; exposed instances)", "",
         "| Instance | Eligible | Eligible tests | Draws run | Bug-trigger rate | Known-good patch (help/hurt) | Gold mutants caught | Deterministic | Seconds |",
         "|---|---|---|---|---|---|---|---|---|"]
    for t in ORDER:
        r = res.get(t)
        if r is None:
            L.append(f"| {t} | MISSING | | | | | | | |")
            continue
        if not r.get("eligible"):
            L.append(f"| {t} | no: {r.get('reason')} | {r.get('eligible_test_functions', '')} | | | | | | |")
            continue
        p = next(iter(r["patches"].values()))
        caught = sum(1 for m in r["mutants"] if m["hurt"] > 0)
        L.append(f"| {t} | yes | {r['eligible_test_functions']} | {r['draws_run']} | {r['bug_trigger_rate']:.1%} | "
                 f"{p['help']}/{p['hurt']} | {caught}/{len(r['mutants'])} | {r['deterministic']} | {r.get('seconds')} |")
    ok = sum(1 for r in res.values() if r.get("eligible") and r["checks"]["all_four"])
    L += ["", f"Instances for which all four feasibility checks (a)-(d) hold: **{ok} of {len(ORDER)}**.",
          "Development stage: the thresholds of Study L2 are set only after this table is seen, and these instances are never used as evidence."]
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
