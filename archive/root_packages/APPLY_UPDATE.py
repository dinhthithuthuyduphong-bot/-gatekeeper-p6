"""Copy reviewed changes to a clean main checkout; never tests, commits or pushes."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def atomic_write(path, raw, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(raw)
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    repo = args.repo.resolve()
    manifest = json.loads((package / "UPDATE_MANIFEST.json").read_text())

    def git(*argv):
        return subprocess.check_output(["git", "-C", str(repo), *argv], text=True).strip()

    if git("branch", "--show-current") != "main":
        raise SystemExit("STOP: choose the existing main checkout first.")
    if git("rev-parse", "HEAD") != manifest["base_commit"]:
        raise SystemExit("STOP: main differs from the reviewed base. Preserve newer work; do not reset or force-push. Send the current commit for reconciliation.")
    if git("status", "--porcelain"):
        raise SystemExit("STOP: working tree is not clean. Preserve your own changes; extract this package outside the repo.")
    payload_root = package / "main_update"
    pending, seen = [], set()
    for item in manifest["files"]:
        name = item["path"]
        relative = PurePosixPath(name)
        if name in seen or relative.is_absolute() or ".." in relative.parts or "\\" in name or ".git" in relative.parts:
            raise SystemExit("Invalid manifest path")
        seen.add(name)
        source = payload_root.joinpath(*relative.parts)
        dest = repo.joinpath(*relative.parts)
        for root in (payload_root, repo):
            current = root
            for part in relative.parts:
                current = current / part
                if current.is_symlink(): raise SystemExit("Symlink not allowed: " + name)
        raw = source.read_bytes()
        if len(raw) != item["bytes"] or digest(raw) != item["sha256"]:
            raise SystemExit("Damaged package: " + name)
        if item["previous_sha256"] is None:
            if dest.exists(): raise SystemExit("Unexpected existing file: " + name)
            old, mode = None, 0o644
        else:
            if not dest.is_file(): raise SystemExit("Missing base file: " + name)
            old, mode = dest.read_bytes(), dest.stat().st_mode & 0o777
            if digest(old) != item["previous_sha256"]:
                raise SystemExit("Changed base file: " + name)
        pending.append((dest, raw, old, mode))
    actual = {p.relative_to(payload_root).as_posix() for p in payload_root.rglob("*") if p.is_file()}
    if actual != seen: raise SystemExit("Payload and manifest differ")
    print("Verified", len(pending), "new/changed files. B9 remains HOLD.")
    if args.check_only: return
    written = []
    try:
        for dest, raw, old, mode in pending:
            written.append((dest, old, mode))
            atomic_write(dest, raw, mode)
    except Exception:
        for dest, old, mode in reversed(written):
            if old is None:
                if dest.exists(): dest.unlink()
            else:
                atomic_write(dest, old, mode)
        raise
    print("Copied update only. Review, commit, push to main and dispatch GitHub Actions yourself. No tests or remote actions were run.")


if __name__ == "__main__":
    main()
