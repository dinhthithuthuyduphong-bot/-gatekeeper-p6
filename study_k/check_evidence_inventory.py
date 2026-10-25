"""Read-only completeness/hash check before tests; never synthesize missing evidence."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent


def check(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "study_k/EVIDENCE_MANIFEST.json").read_text())
    files = manifest["files"]
    if manifest["kind"] != "IMMUTABLE_STUDY_K_EVIDENCE" or len(files) != manifest["expected_files"]:
        raise ValueError("Invalid evidence inventory")
    names = [entry["path"] for entry in files]
    if len(set(names)) != len(names) or not names:
        raise ValueError("Empty or duplicate evidence inventory")
    rows = []
    for entry in files:
        relative = PurePosixPath(entry["path"])
        if relative.is_absolute() or ".." in relative.parts or "\\" in entry["path"]:
            raise ValueError("Invalid evidence path")
        if not entry["path"].startswith(("study_k/results/local-20261025-clean/", "study_k/results/pilot_attempts/")):
            raise ValueError("Evidence path outside the declared study snapshots")
        path = root
        symlink = False
        for part in relative.parts:
            path = path / part
            symlink = symlink or path.is_symlink()
        row = {"path": entry["path"], "expected_sha256": entry["sha256"]}
        if symlink:
            row["status"] = "SYMLINK_NOT_ALLOWED"
        elif not path.is_file():
            row["status"] = "MISSING"
        else:
            try:
                raw = path.read_bytes()
                row["actual_sha256"] = hashlib.sha256(raw).hexdigest()
                row["status"] = "MATCH" if row["actual_sha256"] == entry["sha256"] and len(raw) == entry["bytes"] else "MISMATCH"
            except OSError as error:
                row.update(status="UNREADABLE", error=type(error).__name__)
        rows.append(row)
    problems = [row for row in rows if row["status"] != "MATCH"]
    return {"status": "EVIDENCE_INVENTORY_OK" if not problems else "EVIDENCE_INVENTORY_BLOCKED",
            "expected_files": len(rows), "matching_files": len(rows) - len(problems), "problems": problems,
            "source_archive": manifest["source_archive"], "source_archive_sha256": manifest["source_archive_sha256"],
            "model_calls": 0, "note": "Inventory success is not experimental success. Restore original bytes; do not generate a replacement result or skip the evidence tests."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("Choose a new output path; preserve earlier receipts")
    try:
        result = check(args.root)
    except (ValueError, KeyError, OSError, TypeError) as error:
        result = {"status": "INVALID_EVIDENCE_INVENTORY", "error": str(error), "model_calls": 0}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)
    if result["status"] != "EVIDENCE_INVENTORY_OK":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
