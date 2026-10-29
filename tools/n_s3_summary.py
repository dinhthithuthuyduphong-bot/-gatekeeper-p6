"""Gate N2 of Study N (study_n/GATES.md): at least 40 instances eligible for the harness.

python tools/n_s3_summary.py DIR OUT_DIR [THRESHOLD=40] [MIN_DRAWS=100]
An instance passes when: the harness ran (eligible, which includes a passing baseline and at least one test reaching
the edited code), at least MIN_DRAWS draws are complete for the original, the fix and the reference patch, the outcomes
are deterministic, and the original differs from the fix on at least one draw.
"""
import collections
import json
import sys
from pathlib import Path


def n2_pass(r, min_draws=100):
    h = r.get("harness") or {}
    if not h.get("eligible"):
        return False, "harness not eligible: %s" % h.get("reason")
    complete = (h.get("complete_draws_by_patch") or {}).get("gold_itself")
    if complete is None:
        complete = h.get("draws_compiled", 0) - (h.get("patches", {}).get("gold_itself", {}) or {}).get("missing", 0)
    if complete < min_draws:
        return False, "only %d complete draws" % complete
    if not h.get("deterministic"):
        return False, "not deterministic"
    if not (h.get("bug_trigger_rate") or 0) > 0:
        return False, "the original never differs from the fix"
    return True, "pass"


def main(d, out, threshold=40, min_draws=100):
    rows = []
    for f in sorted(Path(d).rglob("S3_*.json")):
        r = json.loads(f.read_text())
        ok, why = n2_pass(r, int(min_draws))
        h = r.get("harness") or {}
        rows.append({"name": r.get("name"), "repo": r.get("repo"), "pass": ok, "why": why, "status": r.get("status"),
                     "draws": h.get("draws_compiled"), "trigger": h.get("bug_trigger_rate"),
                     "common_failure": h.get("common_failure_fraction"), "mutants_caught": sum(1 for m in h.get("mutants", []) if m.get("hurt", 0) > 0)})
    n = sum(r["pass"] for r in rows)
    summary = {"instances": len(rows), "pass": n, "gate_N2": "PASS" if n >= int(threshold) else "FAIL", "threshold": int(threshold),
               "reasons": dict(collections.Counter(r["why"] if not r["pass"] else "pass" for r in rows)),
               "passing_repositories": len({r["repo"] for r in rows if r["pass"]})}
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    (o / "S3_ROWS.json").write_text(json.dumps(rows, indent=1))
    (o / "S3_SUMMARY.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
