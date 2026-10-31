"""Apply only the NEXT delta after FINAL. Copies files; never tests, commits or pushes."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def contained(root, relative):
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("Invalid relative package path")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or not parts.parts or any(p in ("..", ".git") for p in parts.parts):
        raise ValueError("Unsafe package path: " + relative)
    path = root
    for part in parts.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Refusing a symlink destination/source: " + relative)
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        raise ValueError("Path leaves the selected directory") from None
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
        with tempfile.NamedTemporaryFile(prefix=".gk-next-", dir=path.parent, delete=False) as stream:
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
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    root = args.repo.resolve()
    package = Path(__file__).resolve().parent
    manifest = json.loads((package / "DELTA_MANIFEST.json").read_text())
    if manifest["kind"] != "DELTA_AFTER_FINAL":
        raise ValueError("Wrong package kind")
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("--repo must point to the repository root")
    if git(root, "branch", "--show-current") != "main":
        raise ValueError("Select main before applying this update")
    if git(root, "status", "--porcelain"):
        raise ValueError("Working tree must be clean. Commit FINAL first; keep the extracted ZIP outside the repo")
    entries = {entry["path"]: entry for entry in manifest["files"]}
    if len(entries) != len(manifest["files"]):
        raise ValueError("Duplicate update path")
    for rel, expected in manifest["final_base_file_sha256"].items():
        path = contained(root, rel)
        allowed = {expected}
        if rel in entries:
            if entries[rel]["previous_sha256"] != expected:
                raise ValueError("Inconsistent base metadata: " + rel)
            allowed.add(entries[rel]["sha256"])
        if not path.is_file() or digest(path.read_bytes()) not in allowed:
            raise ValueError("FINAL prerequisite missing or changed: " + rel)
    pending = []
    for rel, entry in entries.items():
        source = contained(package / "main_update", rel)
        raw = source.read_bytes()
        if digest(raw) != entry["sha256"]:
            raise ValueError("Package checksum mismatch: " + rel)
        path = contained(root, rel)
        if path.exists() and not path.is_file():
            raise ValueError("A directory blocks the target file: " + rel)
        before = path.read_bytes() if path.exists() else None
        actual = digest(before) if before is not None else None
        if actual == entry["sha256"]:
            continue
        if actual != entry["previous_sha256"]:
            raise ValueError("Local content differs from both FINAL and NEXT: " + rel)
        mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
        pending.append((path, raw, before, mode))
    if args.check_only:
        print(json.dumps({"status": "PRECHECK_OK", "files_to_copy": len(pending), "B9": "HOLD"}))
        return
    written = []
    try:
        for path, raw, before, mode in pending:
            current = path.read_bytes() if path.exists() else None
            if current != before:
                raise ValueError("A destination changed during application: " + str(path))
            written.append((path, raw, before, mode))
            atomic_write(path, raw, mode)
    except Exception:
        for path, raw, before, mode in reversed(written):
            current = path.read_bytes() if path.exists() else None
            if current == before:
                continue
            if current != raw:
                raise ValueError("Concurrent content change; review destination before retrying: " + str(path)) from None
            if before is None:
                path.unlink()
            else:
                atomic_write(path, before, mode)
        raise
    print(json.dumps({"status": "COPIED_REVIEW_BEFORE_COMMIT", "files_copied": len(pending),
                      "tests_run": 0, "remote_push": False, "B9": "HOLD"}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit("STOP: " + str(error)) from None
