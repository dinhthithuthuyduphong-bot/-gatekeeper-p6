"""Read-only applicability scan of the FROZEN Study D skill over candidate repositories.

python tools/applicability_scan.py study_e/candidates.json out_dir
For each candidate: shallow-fetch, run the frozen skill's own matcher on every non-test
module (nothing is executed), and look for upstream test functions that reference the
matched function AND contain a True/False literal (candidate tier-1 oracle evidence).
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
from scan_candidates import expand  # noqa: E402
from gatekeeper_lite import transforms as T  # noqa: E402
from gatekeeper_lite.skill import Skill  # noqa: E402

TEST_DIRS = ("tests", "test", "testing")


def _is_test(rel: str) -> bool:
    parts = rel.split("/")
    return any(p in TEST_DIRS for p in parts[:-1]) or parts[-1].startswith("test_")


def bool_tests(repo: Path) -> list:
    """(file, test name, referenced names) for test functions containing True/False."""
    out = []
    for path in repo.rglob("*.py"):
        rel = path.relative_to(repo).as_posix()
        if not _is_test(rel):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name.startswith("test"):
                has_bool = any(isinstance(n, ast.Constant) and isinstance(n.value, bool) for n in ast.walk(fn))
                if has_bool:
                    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)} | \
                            {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
                    out.append((rel, fn.name, names))
    return out


def scan(repo: Path, transform) -> dict:
    sites = []
    for path in sorted(repo.rglob("*.py")):
        rel = path.relative_to(repo).as_posix()
        if _is_test(rel) or "/docs/" in f"/{rel}" or "/examples/" in f"/{rel}":
            continue
        src = path.read_text(encoding="utf-8", errors="replace")
        try:
            res = transform.apply(src, single_site=False)
        except T.Abstain:
            continue
        except Exception as exc:
            sites.append({"file": rel, "error": f"{type(exc).__name__}: {exc}"[:200]})
            continue
        for s in res.sites:
            sites.append({"file": rel, "line": s.lineno, "function": s.function, "snippet": s.snippet[:160]})
    tests = bool_tests(repo)
    for s in sites:
        fn = s.get("function")
        s["bool_tests_referencing_function"] = [f"{f}::{t}" for f, t, names in tests if fn and fn in names][:10]
    return {"sites": sites, "n_sites": len([s for s in sites if "line" in s]),
            "n_sites_with_bool_test": len([s for s in sites if s.get("bool_tests_referencing_function")])}


def main(candidates: str, out_dir: str) -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    skill = Skill.load(ROOT / "study_d" / "skills" / "bool-excluded-from-int.json")
    transform = skill.transform()
    results = []
    for cand in expand(json.loads(Path(candidates).read_text(encoding="utf-8"))["candidates"]):
        entry = {k: cand[k] for k in ("name", "repo", "ref")} | {"hypothesis": cand.get("hypothesis", "")}
        try:
            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
                entry["commit"] = _clone_ref(cand["repo"], cand["ref"], Path(tmp) / "r")
                entry.update(scan(Path(tmp) / "r", transform))
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"[:300]
        results.append(entry)
        print(f"{entry['name']}: {entry.get('n_sites', 'ERR')} site(s), "
              f"{entry.get('n_sites_with_bool_test', 0)} with a bool-literal test")
    (out / "APPLICABILITY_SCAN.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    lines = ["# Quét áp dụng skill đã đóng băng (chỉ đọc)", "",
             "| Ứng viên | Commit | Site khớp | Site có test dùng True/False tham chiếu hàm | Giả thuyết |", "|---|---|---|---|---|"]
    for e in results:
        lines.append(f"| {e['name']} | `{e.get('commit', 'lỗi')[:10]}` | {e.get('n_sites', e.get('error', '')[:60])} | "
                     f"{e.get('n_sites_with_bool_test', '—')} | {e['hypothesis']} |")
    lines += ["", "## Chi tiết site", ""]
    for e in results:
        for s in e.get("sites", []):
            if "line" in s:
                lines.append(f"- **{e['name']}** `{s['file']}:{s['line']}` `{s['function']}` — `{s['snippet']}`"
                             + (f" — test: {', '.join(s['bool_tests_referencing_function'][:3])}"
                                if s['bool_tests_referencing_function'] else ""))
    (out / "APPLICABILITY_SCAN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
