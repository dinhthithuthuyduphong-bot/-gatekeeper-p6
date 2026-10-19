"""Scan candidate repositories for the skill's pattern (read-only; Study B sampling frame).

python tools/scan_candidates.py study_b/candidates.json study_b/out
For each candidate: shallow-fetch the ref, record the resolved commit, find every
`X == ""` comparison with the skill's own AST matcher, flag sites in help/default code,
and record test-suite and license indicators.  Nothing from the candidates is executed.
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from fetch_real_targets import _clone_ref  # noqa: E402
from gatekeeper_lite import transforms as T  # noqa: E402

HELP_HINTS = ("help", "default")


def scan_tree(repo: Path) -> dict:
    sites, files = [], 0
    for path in sorted(repo.rglob("*.py")):
        rel = path.relative_to(repo).as_posix()
        if any(part in ("tests", "test", "docs", "examples") for part in rel.split("/")[:-1]):
            continue
        files += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        T._parents(tree)
        for node in T.EmptyStringGuard().find(tree):
            func = T._enclosing_function(node)
            parent = T._parent(node)
            guarded = isinstance(parent, ast.BoolOp) and any(
                T._is_isinstance(v, node.left, "str") for v in parent.values)
            sites.append({"file": rel, "line": node.lineno, "function": func,
                          "subject": ast.unparse(node.left), "already_guarded": guarded,
                          "help_or_default": any(h in func.lower() for h in HELP_HINTS)})
    license_text = next((p.read_text(errors="replace").splitlines()[0].strip()
                         for p in repo.glob("LICENSE*") if p.is_file()), None)
    pyproject = (repo / "pyproject.toml").read_text(errors="replace") if (repo / "pyproject.toml").exists() else ""
    return {"python_files_scanned": files, "sites": sites,
            "relevant_unguarded": [s for s in sites if (s["help_or_default"] or "default" in s["subject"])
                                   and not s["already_guarded"]],
            "has_tests_dir": (repo / "tests").is_dir(),
            "pytest_configured": "pytest" in pyproject or (repo / "pytest.ini").exists()
                                 or (repo / "setup.cfg").exists(),
            "license_first_line": license_text}


def _version_key(tag: str):
    import re
    return tuple(int(x) for x in re.findall(r"\d+", tag)) or (0,)


def latest_tags(repo: str, n: int) -> list:
    """The n highest version-like tags of a remote (read-only ls-remote)."""
    import subprocess
    out = subprocess.run(["git", "ls-remote", "--tags", "--refs", repo], check=True,
                         capture_output=True, text=True).stdout
    tags = [line.split("refs/tags/", 1)[1] for line in out.splitlines() if "refs/tags/" in line]
    tags = [t for t in tags if any(ch.isdigit() for ch in t)]
    return sorted(tags, key=_version_key)[-n:]


def expand(candidates: list) -> list:
    out = []
    for cand in candidates:
        if cand.get("tags_latest"):
            for tag in latest_tags(cand["repo"], int(cand["tags_latest"])):
                out.append(dict(cand, name=f"{cand['name']}@{tag}", ref=f"refs/tags/{tag}"))
        else:
            out.append(cand)
    return out


def main(candidates: str, out_dir: str) -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for cand in expand(json.loads(Path(candidates).read_text(encoding="utf-8"))["candidates"]):
        entry = {"name": cand["name"], "repo": cand["repo"], "ref": cand["ref"]}
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
                entry["commit"] = _clone_ref(cand["repo"], cand["ref"], Path(tmp) / "r")
                entry.update(scan_tree(Path(tmp) / "r"))
        except Exception as exc:  # recorded, never hidden
            entry["error"] = f"{type(exc).__name__}: {exc}"[:300]
        results.append(entry)
        print(f"{cand['name']}: {len(entry.get('relevant_unguarded', []))} relevant unguarded site(s)")
    (out / "CANDIDATE_SCAN.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    lines = ["# Quét ứng viên Study B (chỉ đọc)", "",
             "| Ứng viên | Commit | Site `== \"\"` | Liên quan help/default, chưa guard | Có tests/ | Giấy phép |",
             "|---|---|---|---|---|---|"]
    for e in results:
        if "error" in e:
            lines.append(f"| {e['name']} | lỗi | {e['error'][:80]} | | | |")
            continue
        rel = "; ".join(f"{s['file']}:{s['line']} `{s['function']}`" for s in e["relevant_unguarded"]) or "không"
        lines.append(f"| {e['name']} | `{e['commit'][:10]}` | {len(e['sites'])} | {rel} | "
                     f"{'có' if e['has_tests_dir'] else 'không'} | {e['license_first_line'] or '?'} |")
    (out / "CANDIDATE_SCAN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
