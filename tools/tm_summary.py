"""Summarize development records without promoting missing/duplicate data into a pass."""
import json
import sys
from pathlib import Path

ORDER = ["D1_py_ecc", "D2_cerberus", "D3_speckit", "D4_openfeature", "D5_pycubrid", "A1_speckit_catalog"]


def main(d, out):
    results, duplicates = {}, set()
    for f in sorted(Path(d).rglob("TM_*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        target = r.get("target")
        if target not in ORDER:
            continue
        if target in results:
            duplicates.add(target)
        results[target] = r
    lines = ["# Test-mutation development summary", "",
             "Exposed instances; not a confirmatory cohort. Missing jobs remain pending, not scientific failures.", "",
             "| Target | Status | Compiled IDs | Complete IDs per patch | Deterministic | All checks + completeness |",
             "|---|---|---:|---|---|---|"]
    passed = 0
    for target in ORDER:
        r = results.get(target)
        if r is None:
            lines.append("| %s | MISSING / not selected | | | | |" % target)
            continue
        checks = r.get("checks", {})
        clean = checks.get("no_missing_outcomes") is True
        ok = bool(r.get("eligible") and checks.get("all_four") and clean and target not in duplicates)
        passed += ok
        counts = r.get("complete_draws_by_patch")
        if counts is None and "draws_run" in r:
            counts = {k: r["draws_run"] - v["missing"] for k, v in r.get("patches", {}).items() if "missing" in v}
        status = "DUPLICATE: manual reconciliation required" if target in duplicates else r.get("status", "legacy record")
        if not r.get("eligible"):
            status += "; ineligible: " + str(r.get("reason", "unknown"))
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            target, status.replace("|", "/").replace("\n", " "), r.get("draws_compiled", r.get("draws_run", "N/A")),
            counts or "N/A", r.get("deterministic", "N/A"), ok))
    lines += ["", "Completed records: **%d/6**; complete feasibility passes: **%d**." % (len(results), passed),
              "This count is descriptive, not a new G1/G2 decision. Review per-target RESULT files and evidence inventories.",
              "Do not pool legacy and corrected-harness runs. Study L G1 remains 2/6 (failed); B9 remains HOLD."]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Development summary written; records=%d, duplicates=%d" % (len(results), len(duplicates)))
    return 2 if duplicates else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
