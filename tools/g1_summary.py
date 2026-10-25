"""Summarise G1_*.json files into the gate decision.  python tools/g1_summary.py DIR OUT.md
Gate G1 passes if at least 5 of the 6 instances pass criteria (a)-(d) (GATES.md; immutable)."""
import json
import sys
from pathlib import Path

ORDER = ["D1_py_ecc", "D2_cerberus", "D3_speckit", "D4_openfeature", "D5_pycubrid", "A1_speckit_catalog"]


def main(d, out):
    res = {}
    for f in Path(d).rglob("G1_*.json"):
        r = json.loads(f.read_text())
        res[r["target"]] = r
    L = ["# Gate G1 result", "", "| Instance | Eligible | (a) bug detected | (b) no regression | (c) deterministic | (d) mutant caught | bug-trigger rate | Pass |",
         "|---|---|---|---|---|---|---|---|"]
    passed = 0
    for t in ORDER:
        r = res.get(t)
        if r is None:
            L.append(f"| {t} | MISSING | | | | | | no |")
            continue
        g = r.get("g1")
        if not r.get("eligible") or not g:
            L.append(f"| {t} | no: {r.get('reason')} | | | | | | no |")
            continue
        passed += bool(g["pass"])
        L.append(f"| {t} | yes | {g['a_detects_bug_with_known_good_patch']} | {g['b_no_regression_for_known_good_patch']} | "
                 f"{g['c_deterministic_in_three_fresh_runs']} | {g['d_catches_a_mutant']} | {r['bug_trigger_rate']:.1%} | {'**yes**' if g['pass'] else 'no'} |")
    L += ["", f"**{passed} of 6 instances pass.  Gate G1: {'PASS' if passed >= 5 else 'FAIL'}** (threshold: at least 5 of 6).", ""]
    for t in ORDER:
        r = res.get(t)
        if r and r.get("note"):
            L.append(f"- {t}: {r['note']}")
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
