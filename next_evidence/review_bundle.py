"""Copy a compact review bundle; preserve hashes and locations of bulky raw files."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

OMITTED_NAMES = {"coverage.data", "coverage.json"}


def sha256(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def build(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_dir():
        raise ValueError("Raw artifact directory is missing")
    if source == destination or source.is_relative_to(destination) or destination.is_relative_to(source):
        raise ValueError("Input and output must be separate directories")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Choose an empty review output directory")
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlinks are not supported in evidence bundles")
        if not path.is_file():
            continue
        name = path.relative_to(source).as_posix()
        if name == "REVIEW_SCOPE.json":
            raise ValueError("Input already contains a review manifest")
        omit = path.name in OMITTED_NAMES
        row = {"path": name, "bytes": path.stat().st_size, "sha256": sha256(path),
               "included": not omit}
        if omit:
            row["reason"] = "Large raw coverage file; retrieve from the corresponding next-raw-* job artifact."
        else:
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        rows.append(row)
    result = {
        "format": "COMPACT_REVIEW_BUNDLE_V1", "files": rows,
        "included_files": sum(r["included"] for r in rows),
        "omitted_files": sum(not r["included"] for r in rows),
        "note": "This is a selected review bundle, not a complete raw archive. This command does not delete or change the input. Check each job artifact and JOB_STATUS.json for upload and experiment status. A green collect job is not a scientific result.",
        "B9": "HOLD",
    }
    (destination / "REVIEW_SCOPE.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.input, args.out)
    print(json.dumps({k: report[k] for k in ("format", "included_files", "omitted_files", "B9")}), flush=True)
