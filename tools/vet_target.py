"""Vet a candidate target pair (pre-fix commit, gold fix) for use as an oracle.

python tools/vet_target.py study_d/targets/<name>.json out_dir
For each arm (pre, gold) a fresh venv is created and the package installed from that
checkout.  The gold commit's changed test files are copied onto the pre checkout, so
both arms run the SAME tests.  Each test id is classified:
  F->P  fails before, passes with the gold fix   -> eligible oracle test
  P->P  passes in both                           -> regression guard
  F->F / P->F                                     -> not usable / suspicious
  ERR(pre)  collection/import error on pre only    -> must be re-expressed via public API
Nothing is executed on the host interpreter except pip/pytest inside the venvs.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite.runner import parse_junit  # noqa: E402

GIT = ["git", "-c", "gc.auto=0", "-c", "maintenance.auto=false"]
EXTRA_TEST_REQS: list = []


def sh(cmd, cwd=None, check=True, capture=True, env=None, timeout=1800):
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, capture_output=capture,
                          env=env, timeout=timeout)


def pr_info(spec: dict) -> dict:
    """Merged state and merge commit of a PR via the GitHub CLI (needs GH_TOKEN)."""
    if not spec.get("pr"):
        return {}
    slug = spec["repo"].split("github.com/")[1].removesuffix(".git") if hasattr(str, "removesuffix") \
        else spec["repo"].split("github.com/")[1][:-4]
    r = sh(["gh", "pr", "view", str(spec["pr"]), "--repo", slug, "--json",
            "state,mergedAt,mergeCommit,title"], check=False)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"error": (r.stderr or r.stdout)[-300:]}


def resolve(spec: dict, repo: Path) -> tuple:
    sh([*GIT, "init", "-q"], cwd=repo)
    sh([*GIT, "remote", "add", "origin", spec["repo"]], cwd=repo)
    sh([*GIT, "fetch", "-q", "--filter=blob:none", "origin", spec["default_branch"]], cwd=repo)
    sh([*GIT, "branch", "-f", "upstream_default", "FETCH_HEAD"], cwd=repo)
    sh([*GIT, "fetch", "-q", "--filter=blob:none", "origin", spec["gold"]], cwd=repo)
    gold = sh([*GIT, "rev-parse", "FETCH_HEAD"], cwd=repo).stdout.strip()
    if spec.get("pre") == "merge-base":
        pre = sh([*GIT, "merge-base", gold, "upstream_default"], cwd=repo).stdout.strip()
    else:
        pre = sh([*GIT, "rev-parse", f"{gold}^"], cwd=repo).stdout.strip()
    return pre, gold


def checkout_to(repo: Path, rev: str, dest: Path) -> None:
    dest.mkdir(parents=True)
    tar = subprocess.run([*GIT, "archive", rev], cwd=repo, check=True, capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(dest)], input=tar, check=True)


def make_env(root: Path, src: Path, extras: list, log: list) -> Path:
    venv.EnvBuilder(with_pip=True).create(root)
    py = root / "bin" / "python"
    sh([str(py), "-m", "pip", "install", "-q", "--upgrade", "pip"], check=False)
    for extra in extras + [None]:
        target = f"{src}[{extra}]" if extra else str(src)
        r = sh([str(py), "-m", "pip", "install", "-q", target], check=False)
        log.append(f"pip install {target}: exit {r.returncode}")
        if r.returncode == 0:
            break
    sh([str(py), "-m", "pip", "install", "-q", "pytest", *EXTRA_TEST_REQS], check=False)
    return py


def run_tests(py: Path, src: Path, tests: list, junit: Path) -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    # A test file that fails to import (e.g. it imports a helper added by the fix) must not
    # abort the whole session: other files still run and the error is recorded per file.
    r = sh([str(py), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts=",
            "--continue-on-collection-errors", f"--junitxml={junit}", *tests],
           cwd=src, check=False, env=env)
    res = parse_junit(junit.read_text()) if junit.exists() else {}
    return {"exit": r.returncode, "results": res, "tail": (r.stdout + r.stderr)[-1500:]}


def _test_sources(root: Path, ids: list) -> dict:
    """Source of each eligible test function (so scope generators can mirror the public API)."""
    import ast
    out = {}
    for tid in ids:
        mod, _, name = tid.partition("::")
        func = name.split("[")[0].split("::")[-1]
        parts = mod.split(".")
        path = None
        for cut in range(len(parts), 0, -1):          # strip trailing class names
            cand = root / ("/".join(parts[:cut]) + ".py")
            if cand.exists():
                path = cand
                break
        if path is None:
            continue
        src = path.read_text(encoding="utf-8", errors="replace")
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func:
                deco = "".join(ast.get_source_segment(src, d) + "\n" for d in node.decorator_list)
                out[tid] = (deco + ast.get_source_segment(src, node))[:3000]
    return out


def main(spec_path: str, out_dir: str) -> int:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    EXTRA_TEST_REQS[:] = spec.get("test_requirements", [])
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="vet_"))
    report = {"name": spec["name"], "repo": spec["repo"], "python": sys.version.split()[0]}
    try:
        repo = work / "repo"
        repo.mkdir()
        info = pr_info(spec)
        report["pr_info"] = info
        if info.get("mergeCommit", {}) and info.get("mergeCommit", {}).get("oid"):
            spec = dict(spec, gold=info["mergeCommit"]["oid"], pre="parent")   # what upstream accepted
        pre, gold = resolve(spec, repo)
        report.update(pre=pre, gold=gold)
        changed = sh([*GIT, "diff", "--name-only", pre, gold], cwd=repo).stdout.split()
        test_files = [f for f in changed if "test" in f.split("/")[-1] and f.endswith(".py")]
        report.update(changed_files=changed, gold_test_files=test_files)
        src_files = [f for f in changed if f.endswith(".py") and f not in test_files]
        report["gold_source_diff"] = sh([*GIT, "diff", pre, gold, "--", *src_files], cwd=repo).stdout[-12000:] if src_files else ""
        arms = {}
        for arm, rev in (("pre", pre), ("gold", gold)):
            src = work / arm
            checkout_to(repo, rev, src)
            if arm == "pre":
                for f in test_files:   # same tests on both arms
                    (src / f).parent.mkdir(parents=True, exist_ok=True)
                    (src / f).write_bytes(subprocess.run([*GIT, "show", f"{gold}:{f}"], cwd=repo,
                                                         check=True, capture_output=True).stdout)
            log = []
            py = make_env(work / f"venv_{arm}", src, spec.get("extras", ["test", "dev"]), log)
            arms[arm] = run_tests(py, src, spec.get("tests") or test_files, work / f"junit_{arm}.xml")
            arms[arm]["install_log"] = log
        pre_r, gold_r = arms["pre"]["results"], arms["gold"]["results"]
        coll = {t for t in set(pre_r) | set(gold_r) if t.startswith("::")}   # file-level collection errors
        report["collection_errors"] = {t: {"pre": t in pre_r, "gold": t in gold_r} for t in sorted(coll)}
        ids = sorted((set(pre_r) | set(gold_r)) - coll)
        cls = {}
        for t in ids:
            a, b = pre_r.get(t), gold_r.get(t)
            if a is None and b is not None:
                cls[t] = "ERR(pre)"
            elif b is None:
                cls[t] = "ERR(gold)"
            else:
                cls[t] = f"{'P' if a['passed'] else 'F'}->{'P' if b['passed'] else 'F'}"
        summary = {k: sum(v == k for v in cls.values()) for k in sorted(set(cls.values()))}
        report.update(classification=cls, summary=summary,
                      eligible_oracle=[t for t, c in cls.items() if c == "F->P"],
                      arms={k: {"exit": v["exit"], "tail": v["tail"], "install_log": v["install_log"]}
                            for k, v in arms.items()})
        report["eligible_sources"] = _test_sources(work / "gold", report["eligible_oracle"])
        dump = {}
        for f in test_files:   # whole changed test files + every conftest.py on their path (fixtures)
            p = work / "gold" / f
            for cand in [p] + [q / "conftest.py" for q in p.parents if work / "gold" in q.parents or q == work / "gold"]:
                if cand.exists():
                    dump[str(cand.relative_to(work / "gold"))] = cand.read_text(encoding="utf-8", errors="replace")[:60000]
        report["test_file_sources"] = dump
        report["verdict"] = ("ELIGIBLE" if report["eligible_oracle"]
                             else "NOT_ELIGIBLE (no fail-before/pass-after test)")
    except Exception as exc:  # recorded, never hidden
        report["verdict"] = f"VETTING_ERROR: {type(exc).__name__}: {exc}"[:500]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / f"VETTING_{spec['name']}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report.get(k) for k in ("name", "pre", "gold", "summary", "verdict")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
