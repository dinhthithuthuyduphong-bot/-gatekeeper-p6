"""Restore exact missing evidence from FINAL and copy the small CI fix; no tests or remote writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile
import zipfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def contained(root, relative):
    parts = PurePosixPath(relative)
    if "\\" in relative or parts.is_absolute() or not parts.parts or any(p in ("..", ".git") for p in parts.parts):
        raise ValueError("Invalid package path")
    path = root
    for part in parts.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Refusing a symlink path: " + relative)
    path.resolve().relative_to(root.resolve())
    return path


def git(root, *args):
    process = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if process.returncode:
        raise ValueError("Git check failed: " + " ".join(args))
    return process.stdout.strip()


def atomic_write(path, raw, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".gk-restore-", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--final-zip", type=Path)
    source.add_argument("--final-dir", type=Path, help="Extracted FINAL folder containing main_update/")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    manifest = json.loads((package / "CI_FIX_MANIFEST.json").read_text())
    root = args.repo.resolve()
    if manifest["kind"] != "RESTORE_ORIGINAL_EVIDENCE_AND_CI_PREFLIGHT":
        raise ValueError("Wrong package kind")
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root or git(root, "branch", "--show-current") != "main":
        raise ValueError("Select the repository root on branch main")
    if git(root, "status", "--porcelain"):
        raise ValueError("Working tree must be clean; keep the extracted fix and FINAL outside the repo")
    rows = manifest["update_files"] + manifest["restore_files"]
    if len({r["path"] for r in rows}) != len(rows):
        raise ValueError("Duplicate update path")
    restored_source = {}
    if args.final_zip:
        archive = args.final_zip.resolve()
        if sha(archive.read_bytes()) != manifest["final_archive_sha256"]:
            raise ValueError("Use the original FINAL ZIP; its archive hash differs")
        with zipfile.ZipFile(archive) as bundle:
            for row in manifest["restore_files"]:
                restored_source[row["path"]] = bundle.read("main_update/" + row["path"])
    else:
        source_root = args.final_dir.resolve() / "main_update"
        for row in manifest["restore_files"]:
            restored_source[row["path"]] = contained(source_root, row["path"]).read_bytes()
    pending = []
    for row in rows:
        rel = row["path"]
        raw = restored_source[rel] if rel in restored_source else contained(package / "main_update", rel).read_bytes()
        if sha(raw) != row["sha256"] or len(raw) != row["bytes"]:
            raise ValueError("Source checksum differs: " + rel)
        target = contained(root, rel)
        if target.exists() and not target.is_file():
            raise ValueError("Destination is not a regular file: " + rel)
        previous = target.read_bytes() if target.exists() else None
        previous_hash = sha(previous) if previous is not None else None
        if previous_hash == row["sha256"]:
            continue
        if previous_hash != row["previous_sha256"]:
            raise ValueError("Local content differs; no overwrite: " + rel)
        mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
        pending.append((target, raw, previous, mode))
    if args.check_only:
        print(json.dumps({"status": "SOURCE_AND_DESTINATION_CHECKS_OK", "files_to_copy": len(pending), "tests_run": 0}))
        return
    written = []
    try:
        for target, raw, previous, mode in pending:
            current = target.read_bytes() if target.exists() else None
            if current != previous:
                raise ValueError("A destination changed during application")
            written.append((target, raw, previous, mode))
            atomic_write(target, raw, mode)
    except Exception:
        for target, raw, previous, mode in reversed(written):
            current = target.read_bytes() if target.exists() else None
            if current == previous:
                continue
            if current != raw:
                raise ValueError("Concurrent edit detected; review files before retrying") from None
            if previous is None:
                target.unlink()
            else:
                atomic_write(target, previous, mode)
        raise
    receipt = {"status": "FILES_COPIED_REVIEW_AND_COMMIT", "files_copied": len(pending),
               "source_final_sha256": manifest["final_archive_sha256"], "base_commit_before_copy": git(root, "rev-parse", "HEAD"),
               "restored_files_sha256": {row["path"]: row["sha256"] for row in manifest["restore_files"]},
               "project_tests": "NOT_RUN", "model_calls": 0, "remote_push": False, "B9": "HOLD"}
    (package / "RESTORATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({key: receipt[key] for key in ("status", "files_copied", "project_tests", "B9")}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit("STOP: " + str(error)) from None
