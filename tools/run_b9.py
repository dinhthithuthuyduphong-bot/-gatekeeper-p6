"""Run B9 on one Study D target with one model (after 31/10 only; needs network and a key).

python tools/run_b9.py study_d/b9_config.json study_d/config_study_d.json D1_py_ecc deepseek-flash out_b9 [record|replay]
The cassette (out_b9/cassette_<target>_<model>.json) stores every model reply, so a
re-run in replay mode reproduces the exact patches without paying again.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from fetch_real_targets import _clone_ref  # noqa: E402
from run_study_d import census, drand_seed  # noqa: E402
from gatekeeper_lite.b9 import Budget, CassetteClient, OpenAICompatibleClient, SpendGuard, b9_verdict, repair  # noqa: E402
from gatekeeper_lite.drawharness import run_draw_study  # noqa: E402
from gatekeeper_lite.skill import Target  # noqa: E402


def main(b9_cfg, d_cfg, target_id, model_name, out_dir, mode="replay") -> int:
    b9 = json.loads(Path(b9_cfg).read_text())
    dcfg_path = Path(d_cfg).resolve()
    dcfg = json.loads(dcfg_path.read_text())
    if mode == "record":
        if b9.get("status") != "FROZEN":
            raise SystemExit("B9 config is not FROZEN; paid calls are not allowed")
        if datetime.now(timezone.utc) < datetime.fromisoformat(b9["not_before_utc"].replace("Z", "+00:00")):
            raise SystemExit("paid B9 runs are not allowed before " + b9["not_before_utc"])
    base = dcfg_path.parent
    model = next(m for m in b9["models"] if m["name"] == model_name)
    if target_id not in b9["instances"]:
        raise SystemExit(f"{target_id}: B9 not applicable ({b9.get('not_applicable', {}).get(target_id, 'not declared')})")
    inst = json.loads((base / "b9_instances" / f"{target_id}.json").read_text())
    if inst["visible"].get("kind") == "oracle_draw":
        inst["visible"]["oracle"] = str((base / inst["visible"]["oracle"]).resolve())
    # hard cap for this job: the target's pre-declared allocation, split evenly across models
    cap_usd = b9["allocation_vnd"][target_id] / b9["vnd_per_usd"] / len(b9["models"])
    guard = SpendGuard(cap_usd)
    manifest = json.loads((base / "eval_targets" / target_id / "gk_target.json").read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cassette = CassetteClient(out / f"cassette_{target_id}_{model_name}.json", mode,
                              OpenAICompatibleClient(model["base_url"], model["key_env"]))
    work = Path(tempfile.mkdtemp(prefix="b9run_"))
    runs = []
    try:
        root = work / target_id
        commit = _clone_ref(manifest["checkout"]["repo"], manifest["checkout"]["ref"], root)
        shutil.rmtree(root / ".git", ignore_errors=True)
        (root / "gk_target.json").write_text(json.dumps(manifest))
        kind, _, pkg = manifest.get("install", "").partition(":")
        if kind == "self-then-uninstall":
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", str(root)], check=True)
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", pkg], check=True)
        if manifest.get("census_requirements"):          # same environment as the Study D runner
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", *manifest["census_requirements"]], check=True)
        target = Target.load(root)
        seed = drand_seed(__import__("hashlib").sha256((base / "FREEZE.json").read_bytes()).hexdigest(),
                          dcfg["seed_time_utc"])
        for rep in range(b9["repetitions"]):
            r = repair(target, inst, cassette, model_name, Budget(**b9["budget"]),
                       model["prices_usd_per_mtok"], seed=b9["seed"] + 100 * rep,
                       guard=guard if mode == "record" else None)
            entry = {"repetition": rep, "status": r.status, "attempts": r.attempts, "calls": r.calls,
                     "visible_runs": r.visible_runs, "tokens": r.tokens, "cost_usd": r.cost_usd,
                     "seconds": r.seconds, "patched_modules": sorted(r.treated)}
            if r.status == "SUBMITTED":
                entry["census"] = census(target, r.treated, manifest["census_tests"])
                scored = run_draw_study(target, r.treated, base / manifest["draw_oracle"],
                                        {"seed": seed["seed"], "alpha": dcfg["alpha"], "n_max": dcfg["n_max"],
                                         "theta": dcfg["theta"], "eta": dcfg["eta"], "b8_full": True},
                                        k_cells=len(dcfg["cells"]))
                entry["hidden_oracle"] = {s: v["b8"]["counts"] for s, v in scored["scopes"].items()}
            entry["verdict"] = b9_verdict(entry)
            runs.append(entry)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    total = sum(r["cost_usd"] for r in runs)
    (out / f"RESULT_B9_{target_id}_{model_name}.json").write_text(json.dumps(
        {"target": target_id, "commit": commit, "model": model_name, "mode": mode,
         "runs": runs, "total_cost_usd": round(total, 4),
         "cap_usd": round(cap_usd, 4), "guard_spent_usd": round(guard.spent_usd, 4),
         "guard_overshoot": guard.overshoot,
         "verdicts": [r["verdict"] for r in runs]}, indent=2))
    print(json.dumps({"target": target_id, "model": model_name, "statuses": [r["status"] for r in runs],
                      "total_cost_usd": round(total, 4)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:7]))
