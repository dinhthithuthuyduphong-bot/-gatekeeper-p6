"""Paired trials: run the same oracle tasks WITHOUT and WITH the skill.

Both arms are copied from the same frozen target snapshot into fresh temporary
directories and differ only in the treated module file (pair integrity).  Each arm
runs in its own subprocess with the same seed and PYTHONHASHSEED.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ArmResult:
    arm: str
    results: Dict[str, dict]
    seconds: float
    file_hashes: Dict[str, str]

    def failed(self) -> set:
        return {c for c, r in self.results.items() if not r["passed"]}


@dataclass
class PairedRun:
    baseline: ArmResult
    treatment: ArmResult
    integrity_ok: bool
    integrity_notes: List[str] = field(default_factory=list)

    @property
    def case_ids(self) -> List[str]:
        return sorted(self.baseline.results)

    def z(self, case_id: str) -> float:
        b = 0.0 if self.baseline.results[case_id]["passed"] else 1.0
        t = 0.0 if self.treatment.results[case_id]["passed"] else 1.0
        return t - b

    @property
    def new_failures(self) -> List[str]:
        return sorted(self.treatment.failed() - self.baseline.failed())

    @property
    def resolved_failures(self) -> List[str]:
        return sorted(self.baseline.failed() - self.treatment.failed())

    def suite_loss(self, arm: str) -> float:
        """Paper-style loss: (1 - pass rate) + 0.5 per regression, clipped to [0, 1]."""
        res = self.baseline if arm == "baseline" else self.treatment
        n = len(res.results)
        fail_rate = len(res.failed()) / n if n else 1.0
        regressions = len(self.new_failures) if arm == "treatment" else 0
        return min(1.0, fail_rate + 0.5 * regressions)


def _hash_tree(root: Path) -> Dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def parse_junit(xml_text: str) -> Dict[str, dict]:
    """Per-test outcome from a pytest JUnit XML report (skips count as missing, not pass)."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_text)
    results = {}
    for case in root.iter("testcase"):
        case_id = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("skipped") is not None:
            continue
        bad = case.find("failure") if case.find("failure") is not None else case.find("error")
        results[case_id] = {"passed": bad is None}
        if bad is not None:
            results[case_id]["error"] = (bad.get("message") or "")[:200]
    return results


def _run_pytest(snapshot: Path, tests: List[str], env: dict, timeout: float,
                extra_args: Optional[List[str]] = None) -> Dict[str, dict]:
    junit = snapshot / "_gk_junit.xml"
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
           f"--junitxml={junit}", *(extra_args or []), *tests]
    proc = subprocess.run(cmd, cwd=str(snapshot), env=env, capture_output=True,
                          text=True, timeout=timeout)
    if not junit.exists():
        raise RuntimeError(f"pytest produced no report (exit {proc.returncode}): "
                           f"{(proc.stderr or proc.stdout)[-500:]}")
    return parse_junit(junit.read_text(encoding="utf-8"))


def run_arm(arm: str, target_root: Path, module: str, treated_source: Optional[str],
            seed: int, timeout: float = 60.0, oracle: Optional[dict] = None,
            pythonpath: Optional[List[str]] = None, extra_env: Optional[dict] = None) -> ArmResult:
    work = Path(tempfile.mkdtemp(prefix=f"gk_{arm}_"))
    try:
        snapshot = work / "snapshot"
        shutil.copytree(target_root, snapshot,
                        ignore=shutil.ignore_patterns("__pycache__", ".git", "*.egg-info"))
        if treated_source is not None:
            (snapshot / module).write_text(treated_source, encoding="utf-8")
        hashes = _hash_tree(snapshot)
        paths = [str(snapshot / p) for p in (pythonpath or [])] + [str(PACKAGE_ROOT)]
        env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=os.pathsep.join(paths), **(extra_env or {}))
        oracle = oracle or {"kind": "cases"}
        start = time.perf_counter()
        if oracle["kind"] == "pytest":
            results = _run_pytest(snapshot, oracle["tests"], env, timeout,
                                  oracle.get("pytest_args"))
            if not results:
                raise RuntimeError(f"pytest collected no usable tests in {arm}")
        else:
            proc = subprocess.run([sys.executable, "-m", "gatekeeper_lite.harness",
                                   str(snapshot), str(seed)],
                                  cwd=str(snapshot), env=env, capture_output=True,
                                  text=True, timeout=timeout)
            if proc.returncode != 0:
                raise RuntimeError(f"harness failed in {arm}: {proc.stderr[-500:]}")
            results = json.loads(proc.stdout.strip().splitlines()[-1])["results"]
        seconds = time.perf_counter() - start
        return ArmResult(arm, results, seconds, hashes)
    finally:
        shutil.rmtree(work, ignore_errors=True)       # cleanup is part of the protocol


def reach_pass(target, functions: List[str], seed: int, timeout: float = 600.0) -> Optional[dict]:
    """Extra baseline-only pytest pass recording which tests call the edited functions.

    Runs on the untreated snapshot, so the filter cannot depend on treatment outcomes.
    Returns None (no filter) if the pass fails for any reason.
    """
    oracle = target.manifest.get("oracle", {})
    if oracle.get("kind") != "pytest" or not functions:
        return None
    work = Path(tempfile.mkdtemp(prefix="gk_reach_"))
    try:
        snapshot = work / "snapshot"
        shutil.copytree(target.root, snapshot,
                        ignore=shutil.ignore_patterns("__pycache__", ".git", "*.egg-info"))
        out = work / "reach.json"
        paths = [str(snapshot / p) for p in target.manifest.get("pythonpath", [])]
        env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=os.pathsep.join(paths + [str(PACKAGE_ROOT)]),
                   GK_REACH_FUNCS=",".join(functions), GK_REACH_FILE=target.module,
                   GK_REACH_OUT=str(out), **target.manifest.get("env", {}))
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "-p", "gatekeeper_lite.pytest_reach", *(oracle.get("pytest_args") or []),
               *oracle["tests"]]
        subprocess.run(cmd, cwd=str(snapshot), env=env, capture_output=True, text=True,
                       timeout=timeout)
        return json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
    except Exception:
        return None
    finally:
        shutil.rmtree(work, ignore_errors=True)


def paired_run(target, treated_source: str, seed: int, timeout: float = 60.0) -> PairedRun:
    oracle = target.manifest.get("oracle", {"kind": "cases"})
    paths = target.manifest.get("pythonpath", [])
    extra = target.manifest.get("env", {})
    base = run_arm("baseline", target.root, target.module, None, seed, timeout, oracle, paths,
                   extra)
    treat = run_arm("treatment", target.root, target.module, treated_source, seed, timeout,
                    oracle, paths, extra)
    notes = []
    differing = {k for k in set(base.file_hashes) | set(treat.file_hashes)
                 if base.file_hashes.get(k) != treat.file_hashes.get(k)
                 and not k.startswith("_gk_")}
    if differing - {target.module}:
        notes.append(f"unexpected file differences: {sorted(differing - {target.module})}")
    if target.module not in differing:
        notes.append("treated module is identical to baseline")
    if set(base.results) != set(treat.results):
        notes.append("arms ran different task sets")
    return PairedRun(base, treat, not notes, notes)
