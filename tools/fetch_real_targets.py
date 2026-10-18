"""Fetch the frozen real targets and source files declared under real/ (needs git + network).

Run on GitHub Actions:  python tools/fetch_real_targets.py real
Each target's gk_target.json declares {"checkout": {"repo", "ref", "tests_from"?, "test_files"?}}.
The resolved commit of every checkout is written to real/FETCH_RECEIPT.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# No background gc/maintenance: a detached git process writing into .git/objects
# while the temporary directory is removed caused "Directory not empty" on Actions.
_GIT = ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false",
        "-c", "fetch.writeCommitGraph=false", "-c", "core.fsmonitor=false"]


def _git(*args, cwd, capture=False):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    res = subprocess.run([*_GIT, *args], cwd=cwd, check=True, text=True,
                         capture_output=capture, env=env)
    return res.stdout.strip() if capture else None


def _clone_ref(repo: str, ref: str, dest: Path) -> str:
    dest.mkdir(parents=True, exist_ok=True)
    _git("init", "-q", cwd=dest)
    _git("remote", "add", "origin", repo, cwd=dest)
    _git("fetch", "-q", "--depth", "1", "origin", ref, cwd=dest)
    _git("checkout", "-q", "FETCH_HEAD", cwd=dest)
    return _git("rev-parse", "HEAD", cwd=dest, capture=True)


def _show(repo_dir: Path, repo: str, ref: str, path: str) -> tuple:
    _git("fetch", "-q", "--depth", "1", "origin", ref, cwd=repo_dir)
    sha = _git("rev-parse", "FETCH_HEAD", cwd=repo_dir, capture=True)
    return _git("show", f"FETCH_HEAD:{path}", cwd=repo_dir, capture=True) + "\n", sha


def main(root: str) -> int:
    root = Path(root).resolve()
    receipt = {"targets": {}, "sources": {}}
    for manifest_path in sorted((root / "targets").glob("*/gk_target.json")):
        target_dir = manifest_path.parent
        spec = json.loads(manifest_path.read_text(encoding="utf-8"))["checkout"]
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo_dir = Path(tmp) / "repo"
            sha = _clone_ref(spec["repo"], spec["ref"], repo_dir)
            shutil.copytree(repo_dir, target_dir, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(".git"))
            entry = {"ref": spec["ref"], "commit": sha}
            if spec.get("tests_from"):
                for test_file in spec.get("test_files", []):
                    text, test_sha = _show(repo_dir, spec["repo"], spec["tests_from"], test_file)
                    (target_dir / test_file).write_text(text, encoding="utf-8")
                    entry.setdefault("tests_from", {})[test_file] = test_sha
        for rel in json.loads(manifest_path.read_text()).get("inject_tests", []):
            src = root / rel
            shutil.copy2(src, target_dir / "tests" / src.name)
            entry.setdefault("injected", {})[src.name] = hashlib.sha256(src.read_bytes()).hexdigest()
        module = target_dir / json.loads(manifest_path.read_text())["module"]
        entry["module_sha256"] = hashlib.sha256(module.read_bytes()).hexdigest()
        receipt["targets"][target_dir.name] = entry
        print(f"{target_dir.name}: {spec['ref']} -> {sha}")
    sources = root / "sources" / "sources.json"
    if sources.exists():
        for item in json.loads(sources.read_text(encoding="utf-8"))["files"]:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
                sha = _clone_ref(item["repo"], item["ref"], Path(tmp) / "repo")
                data = (Path(tmp) / "repo" / item["path"]).read_text(encoding="utf-8")
            (root / "sources" / item["out"]).write_text(data, encoding="utf-8")
            receipt["sources"][item["out"]] = {"ref": item["ref"], "commit": sha,
                                               "path": item["path"]}
            print(f"source {item['out']}: {sha}")
    (root / "FETCH_RECEIPT.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "real"))
