"""Run Study D on one frozen evaluation target (Actions only; needs network).

python tools/run_study_d.py study_d/config_study_d.json D1_py_ecc out_d
Steps: freeze check -> seed (drand) -> fetch pinned commit -> install deps (the package
itself is uninstalled so each arm imports its own snapshot) -> bind frozen skill to the
declared modules -> census gate (own tests, both arms) -> sequential draw study per scope
with real stopping (and full-budget continuation recorded separately for B8).
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
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from fetch_real_targets import _clone_ref  # noqa: E402
from gatekeeper_lite.drawharness import run_draw_study  # noqa: E402
from gatekeeper_lite.gatekeeper import bind_modules, replay  # noqa: E402
from gatekeeper_lite.runner import parse_junit  # noqa: E402
from gatekeeper_lite.skill import Skill, Target  # noqa: E402

DRAND_QUICKNET = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971"
QUICKNET_GENESIS, QUICKNET_PERIOD = 1692803367, 3


def drand_seed(freeze_sha: str, when_utc: str) -> dict:
    t = int(datetime.fromisoformat(when_utc.replace("Z", "+00:00")).timestamp())
    rnd = max(1, -(-(t - QUICKNET_GENESIS) // QUICKNET_PERIOD) + 1)
    if QUICKNET_GENESIS + (rnd - 1) * QUICKNET_PERIOD > time.time():
        raise SystemExit("seed round is in the future; run after seed_time_utc")
    url = f"https://api.drand.sh/{DRAND_QUICKNET}/public/{rnd}"
    beacon = json.loads(urllib.request.urlopen(url, timeout=30).read())
    seed = hashlib.sha256((freeze_sha + beacon["randomness"]).encode()).hexdigest()
    return {"round": rnd, "randomness": beacon["randomness"], "seed": int(seed[:15], 16), "url": url}


def census(target: Target, treated: dict, tests: list) -> dict:
    out = {}
    for arm in ("baseline", "treatment"):
        work = Path(tempfile.mkdtemp(prefix=f"census_{arm}_"))
        try:
            snap = work / "s"
            shutil.copytree(target.root, snap, symlinks=True, ignore=shutil.ignore_patterns(".git"))
            if arm == "treatment":
                for rel, src in treated.items():
                    (snap / rel).write_text(src, encoding="utf-8")
            junit = work / "j.xml"
            env = dict(os.environ, PYTHONPATH=str(snap), PYTHONDONTWRITEBYTECODE="1")
            t0 = time.perf_counter()
            proc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                                   "-o", "addopts=", "--continue-on-collection-errors",
                                   f"--junitxml={junit}", *tests], cwd=snap, env=env,
                                  capture_output=True, text=True, timeout=3600)
            res = parse_junit(junit.read_text()) if junit.exists() else {}
            out[arm] = {"results": res, "seconds": round(time.perf_counter() - t0, 2),
                        "exit": proc.returncode, "tail": (proc.stdout + proc.stderr)[-600:]}
        finally:
            shutil.rmtree(work, ignore_errors=True)
    base, treat = out["baseline"]["results"], out["treatment"]["results"]
    excluded = sorted(t for t, r in base.items() if not r["passed"])
    new_fail = sorted(t for t, r in base.items() if r["passed"] and not treat.get(t, {"passed": False})["passed"])
    return {"tests": len(base), "excluded_baseline_failures": excluded, "new_failures": new_fail,
            "seconds": {a: out[a]["seconds"] for a in out}, "exit": {a: out[a]["exit"] for a in out},
            "tail": {a: out[a]["tail"] for a in out}}


def main(config: str, target_id: str, out_dir: str) -> int:
    cfg_path = Path(config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    if cfg.get("requires_freeze") and cfg.get("status") != "FROZEN":
        raise SystemExit(f"Study D status is {cfg.get('status')!r}; freeze before running.")
    base = cfg_path.parent
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    freeze_sha = hashlib.sha256((base / "FREEZE.json").read_bytes()).hexdigest()
    seed = drand_seed(freeze_sha, cfg["seed_time_utc"])
    manifest = json.loads((base / "eval_targets" / target_id / "gk_target.json").read_text())
    work = Path(tempfile.mkdtemp(prefix="study_d_"))
    record = {"experiment_id": cfg["experiment_id"], "target": target_id, "seed": seed,
              "python": sys.version.split()[0], "freeze_sha256": freeze_sha}
    try:
        root = work / target_id
        commit = _clone_ref(manifest["checkout"]["repo"], manifest["checkout"]["ref"], root)
        shutil.rmtree(root / ".git", ignore_errors=True)
        (root / "gk_target.json").write_text(json.dumps(manifest), encoding="utf-8")
        record["commit"] = commit
        kind, _, pkg = manifest.get("install", "").partition(":")
        if kind == "self-then-uninstall":
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", str(root)], check=True)
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", pkg], check=True)
        target = Target.load(root)
        skill = Skill.load(base / cfg["skill"])
        bound = bind_modules([skill], target)
        record["bind"] = {"sites": bound["sites"], "abstained": bound["abstained"],
                          "treated_modules": sorted(bound["treated"])}
        record["B6R_replay"] = replay(skill)
        if not bound["treated"]:
            record["decision_basis"] = "OUT_OF_SCOPE (skill abstained on every module)"
            record["scopes"] = {}
        else:
            record["census"] = census(target, bound["treated"], manifest["census_tests"])
            draw_cfg = {"seed": seed["seed"], "alpha": cfg["alpha"], "n_max": cfg["n_max"],
                        "theta": cfg["theta"], "eta": cfg["eta"], "alpha_alarm": cfg["alpha_alarm"],
                        "b8_full": True}
            res = run_draw_study(target, bound["treated"], base / manifest["draw_oracle"], draw_cfg,
                                 k_cells=len(cfg["cells"]))
            if record["census"]["new_failures"]:
                for sc in res["scopes"].values():
                    sc["decision"] = "REJECT_HARM"
                    sc["decision_basis"] = "census gate: new failure in the target's own tests"
            record.update(res)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / f"RESULT_{target_id}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({k: record.get(k) for k in ("target", "commit", "bind")}, indent=2)[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
