"""Read-only reanalysis of saved coverage.py schema-7 arc data, not a test run."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def review(baseline_path, data_path):
    baseline_path, data_path = Path(baseline_path), Path(data_path).resolve()
    result = json.loads(baseline_path.read_text())
    old = result["runs"][0]
    before = digest(data_path)
    if before != old["probe_sha256"]["coverage.data"]:
        raise ValueError("Saved coverage bytes do not match the first run receipt")
    rows = []
    con = sqlite3.connect(data_path.as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        if con.execute("SELECT version FROM coverage_schema").fetchall() != [(7,)]:
            raise ValueError("Only documented coverage.py schema 7 is supported")
        meta = dict(con.execute("SELECT key, value FROM meta"))
        if meta.get("has_arcs") != "1":
            raise ValueError("This reanalysis requires branch/arc data")
        files = con.execute("SELECT id, path FROM file").fetchall()
        for site in old["site_reach"]:
            matches = [(i, p) for i, p in files if p.endswith("/" + site["file"])]
            if len(matches) != 1:
                raise ValueError("Missing/ambiguous measured file: " + site["file"])
            contexts = [r[0] for r in con.execute(
                "SELECT DISTINCT context.context FROM arc JOIN context ON arc.context_id=context.id "
                "WHERE arc.file_id=? AND (arc.fromno=? OR arc.tono=?) ORDER BY context.context",
                (matches[0][0], site["line"], site["line"]))]
            calls = sorted({c.rsplit("|", 1)[0] for c in contexts if c.endswith("|call")})
            if calls != site["test_call_contexts"] or contexts != sorted(set(site["all_contexts"])):
                raise ValueError("Raw trace contexts differ from the recorded baseline report")
            rows.append({"file": site["file"], "line": site["line"],
                         "legacy_executed": site["executed"], "raw_trace_executed": bool(contexts),
                         "call_context_count": len(calls), "test_call_contexts": calls,
                         "all_contexts": contexts})
    finally:
        con.close()
    if digest(data_path) != before:
        raise ValueError("Raw database changed during review")
    return {
        "status": "SAVED_FIRST_RUN_TRACE_REVIEWED",
        "coverage_version": meta.get("version"), "schema": 7,
        "baseline_result_sha256": digest(baseline_path), "coverage_data_sha256": before,
        "same_hash_recorded_by_all_runs": all(r["probe_sha256"]["coverage.data"] == before for r in result["runs"]),
        "raw_databases_independently_read": 1, "sites": rows,
        "method": "Read-only immutable SQLite; join arc endpoints to test-phase contexts; verify original hashes before and after.",
        "scope": "Only probe_1 raw database was independently read. Repetitions 2/3 have matching hashes in BASELINE_RESULT, not separately downloaded databases. This is a separate correction; original artifacts remain unchanged.",
        "new_test_runs": 0, "treatment_runs": 0, "model_calls": 0,
        "oracle_validated": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("Preserve previous output; choose a new path")
    report = review(args.baseline, args.coverage)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "raw_databases_independently_read": 1,
                      "sites": [{k: r[k] for k in ("file", "line", "legacy_executed", "raw_trace_executed", "call_context_count")} for r in report["sites"]],
                      "new_test_runs": 0}), flush=True)
