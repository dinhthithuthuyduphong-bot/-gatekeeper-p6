"""Held-out end-state scoring and the "model + Gatekeeper" condition (Study F; Actions only).

python tools/score_heldout.py study_f/config_study_f.json TARGET out_dir --b9 DIR [DIR ...]

For one target it builds every end state an approach would leave behind and scores each on
a HELD-OUT draw seed (drand round after the held-out freeze), never on the draws used for
any admission decision:
  * skill + Gatekeeper / B6-R / B8 : deployment decisions taken from Study D's AGGREGATE.json
  * B9 raw (per model, per repetition): the submitted patch, re-derived by replaying the
    recorded cassette (no paid call)
  * B9 + Gatekeeper: the same patch, subject to the F-A2 PATCH-level rule on the
    ADMISSION seed. Final deployment is decided only after the complete family is scored.
Every end state goes through the same verdict function (gatekeeper_lite.b9.b9_verdict).
Results without provider usage or with evidence other than PAID_B9 / REPLAY_OF_RECORDED_B9
are refused.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from fetch_real_targets import _clone_ref  # noqa: E402
from run_study_d import census, drand_seed  # noqa: E402
from gatekeeper_lite.b9 import Budget, SpendGuard, b9_verdict, repair  # noqa: E402
from gatekeeper_lite.drawharness import run_draw_study  # noqa: E402
from gatekeeper_lite.gatekeeper import bind_modules  # noqa: E402
from gatekeeper_lite.skill import Skill, Target  # noqa: E402
from gatekeeper_ext.study_f_validation import (ProviderReplayClient, compare_replay, digest,
                                              expected_keys, require, validate_record)  # noqa: E402


def score(target, treated, oracle, cfg, seed, k_cells):
    if not treated:
        return {"status": "NO_PATCH"}
    res = run_draw_study(target, treated, oracle, {"seed": seed, "alpha": cfg["alpha"], "n_max": cfg["n_max"],
                                                    "theta": cfg["theta"], "eta": cfg["eta"], "b8_full": True}, k_cells)
    require(all(v["b8"]["counts"]["harness_error"] == 0 for v in res["scopes"].values()),
            "held-out harness error; no functional verdict may be reported")
    return {"status": "SUBMITTED", "census": census(target, treated, target.manifest["census_tests"]),
            "hidden_oracle": {s: v["b8"]["counts"] for s, v in res["scopes"].items()},
            "hidden_traces": {s: v["trace"] for s, v in res["scopes"].items()}}


def gate(target, treated, oracle, cfg, seed, k_patches):
    """Patch-level Gatekeeper rule (F-A2) on the ADMISSION seed: full n_max draws in every declared
    scope, e_patch = min(mean_s min(e_ben_s, e_cert_s), min_s e_cert_s) (gatekeeper_ext/patch_rule.py),
    0 if any harm alarm fires or the census regresses.  Deployment is decided by e-Holm over the
    family of patches in tools/aggregate_study_f.py."""
    from gatekeeper_ext.patch_rule import patch_evalue
    if not treated:
        return {"submitted": False, "e_patch": 0.0}
    res = run_draw_study(target, treated, oracle, {"seed": seed, "alpha": cfg["alpha"], "n_max": cfg["n_max"],
                                                    "theta": cfg["theta"], "eta": cfg["eta"], "b8_full": True}, k_patches)
    require(all(v["b8"]["counts"]["harness_error"] == 0 for v in res["scopes"].values()),
            "admission harness error; rerun only under the declared environment-failure policy")
    cen = census(target, treated, target.manifest["census_tests"])
    census_bad = cen.get("status") != "VALID" or bool(cen.get("new_failures"))
    e = patch_evalue({s: v["trace"] for s, v in res["scopes"].items()}, cfg["theta"], cfg["eta"], cfg["n_max"], census_bad)
    return {"submitted": True, "e_patch": e, "census_ok": not census_bad,
            "scope_counts": {s: v["b8"]["counts"] for s, v in res["scopes"].items()},
            "scope_traces": {s: v["trace"] for s, v in res["scopes"].items()},
            "census_new_failures": len(cen.get("new_failures", []))}


def fixed_skill_admissions(cfg, d_base):
    """F-A3: the six fixed skill patches obey the same all-scope safety rule.

    This is a separately declared six-patch comparator family, not a change to
    the historical per-cell decisions published for Study D.
    """
    from gatekeeper_ext.patch_rule import patch_evalue
    from gatekeeper_lite.eprocess import e_holm
    values = {}
    for target_id in cfg["cells"]:
        path = d_base / "results" / ("RESULT_" + target_id + ".json")
        require(path.is_file(), "missing fixed-skill source result: " + str(path))
        record = json.loads(path.read_text())
        require(record["target"] == target_id, "fixed-skill result target mismatch")
        scopes = record.get("scopes", {})
        invalid = (record.get("census", {}).get("status") != "VALID"
                   or bool(record.get("census", {}).get("new_failures")))
        traces = {name: s.get("trace", []) for name, s in scopes.items()}
        require(not traces or all(len(t) >= cfg["n_max"] for t in traces.values()),
                "incomplete fixed-skill admission traces")
        values[target_id] = patch_evalue(traces, cfg["theta"], cfg["eta"], cfg["n_max"], invalid)
    return set(e_holm(values, cfg["alpha"]))


def print_rows(target_id, rows):
    for row in rows:
        verdict = row.get("verdict")
        if row["approach"] == "B9+Gatekeeper (candidate)":
            verdict = "PENDING_FAMILY; raw=" + row["raw_verdict"]
        print(target_id, row["approach"], row.get("model", ""), row.get("repetition", ""), verdict)


def main(config, target_id, out_dir, *b9_dirs) -> int:
    cfg_path = Path(config).resolve()
    cfg = json.loads(cfg_path.read_text())
    if cfg.get("status") != "FROZEN":
        raise SystemExit("Study F is not FROZEN")
    expected_keys(cfg)
    require(target_id in cfg["cells"], "unknown target")
    # Validate file inventory BEFORE cloning, installing dependencies or running tests.
    sources = {}
    for b9_dir in b9_dirs:
        for f in sorted(Path(b9_dir).glob(f"RESULT_B9_{target_id}_*.json")):
            record = json.loads(f.read_text())
            model = record.get("model")
            require(model in cfg["b9_configs"] and model not in sources, "unknown/duplicate model result")
            sources[model] = (f, record)
    require(set(sources) == set(cfg["b9_configs"]), "missing model results for target; do not score a partial family")
    d_base = ROOT / "study_d"
    dcfg = json.loads((d_base / "config_study_d.json").read_text())
    manifest = json.loads((d_base / "eval_targets" / target_id / "gk_target.json").read_text())
    inst = json.loads((d_base / "b9_instances" / f"{target_id}.json").read_text())
    agg = {r["cell"]: r for r in json.loads((d_base / "results" / "AGGREGATE.json").read_text())["cells"]}
    admission_seed = drand_seed(dcfg.get("seed_freeze_sha256") or
                                hashlib.sha256((d_base / "FREEZE.json").read_bytes()).hexdigest(),
                                dcfg["seed_time_utc"])["seed"]
    # the held-out seed is pinned to the ORIGINAL Study F freeze hash (amendments cannot move it)
    heldout = drand_seed(cfg.get("seed_freeze_sha256") or
                         hashlib.sha256((cfg_path.parent / "FREEZE.json").read_bytes()).hexdigest(),
                         cfg["seed_time_utc"])
    require(heldout["seed"] != admission_seed, "held-out seed must differ from admission seed")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    require(not (out / f"HELDOUT_{target_id}.json").exists(), "held-out output already exists; preserve the old evidence")
    oracle = (d_base / manifest["draw_oracle"]).resolve()
    if inst["visible"].get("kind") == "oracle_draw":
        inst["visible"]["oracle"] = str((d_base / inst["visible"]["oracle"]).resolve())
    k = cfg["k_cells"]
    rows, provenance = [], {}
    fixed_admitted = fixed_skill_admissions(cfg, d_base)
    work = Path(tempfile.mkdtemp())
    try:
        root = work / target_id
        commit = _clone_ref(manifest["checkout"]["repo"], manifest["checkout"]["ref"], root)
        shutil.rmtree(root / ".git", ignore_errors=True)
        (root / "gk_target.json").write_text(json.dumps(manifest))
        kind, _, pkg = manifest.get("install", "").partition(":")
        import os
        env = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        if kind == "self-then-uninstall":
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", str(root)], check=True, env=env)
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", pkg], check=True)
        if manifest.get("census_requirements"):
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", *manifest["census_requirements"]], check=True)
        target = Target.load(root)
        skill_treated = bind_modules([Skill.load(d_base / dcfg["skill"])], target)["treated"]
        scopes = ["bool", "number" if target_id == "D2_cerberus" else "int"]
        for approach in ("Gatekeeper", "B6R", "B8"):
            dec = [agg.get(f"{target_id}/{s}", {}).get(approach) for s in scopes]
            deploy = target_id in fixed_admitted if approach == "Gatekeeper" else all(x == "ADMIT" for x in dec)
            st = score(target, skill_treated if deploy else {}, oracle, cfg, heldout["seed"], k)
            rows.append({"approach": f"skill+{approach}", "verdict": b9_verdict(st), "state": st})
        for model, (f, b) in sorted(sources.items()):
            recorded = validate_record(b, target_id, model, cfg["repetitions"], commit)
            b9cfg = json.loads((ROOT / cfg["b9_configs"][model]).read_text())
            require(b9cfg["repetitions"] == cfg["repetitions"], "B9/F repetitions disagree")
            cas_path = f.parent / f"cassette_{target_id}_{model}.json"
            cas = ProviderReplayClient(cas_path)
            provenance[model] = {"result_sha256": digest(f), "cassette_sha256": digest(cas_path)}
            mcfg = next(m for m in b9cfg["models"] if m["name"] == model)
            guard = SpendGuard(b9cfg["allocation_vnd"][target_id] / b9cfg["vnd_per_usd"] / len(b9cfg["models"]))
            for rep in range(b9cfg["repetitions"]):
                r = repair(target, inst, cas, mcfg.get("model_id", model), Budget(**b9cfg["budget"]), mcfg["prices_usd_per_mtok"],
                           seed=b9cfg["seed"] + 100 * rep, guard=guard)
                compare_replay(r, recorded[rep])
                raw = score(target, r.treated, oracle, cfg, heldout["seed"], k)
                if not r.treated:
                    raw["attempts"] = r.attempts  # retain BUDGET_CAP, rather than silently calling it NO_PATCH
                gate_info = gate(target, r.treated, oracle, cfg, admission_seed, cfg["k_patches"])
                rows.append({"approach": "B9 raw", "model": model, "repetition": rep, "verdict": b9_verdict(raw),
                             "cost_usd": r.cost_usd, "state": raw})
                rows.append({"approach": "B9+Gatekeeper (candidate)", "model": model, "repetition": rep,
                             "e_patch": gate_info["e_patch"], "raw_verdict": b9_verdict(raw), "gate": gate_info,
                             "cost_usd": r.cost_usd})
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / f"HELDOUT_{target_id}.json").write_text(json.dumps(
        {"schema_version": 2, "evidence": "RECORDED_PROVIDER_REPLAY", "config_sha256": digest(cfg_path),
         "target": target_id, "commit": commit, "heldout_seed": heldout, "admission_seed": admission_seed,
         "source_artifacts": provenance,
         "rows": rows}, indent=2))
    print_rows(target_id, rows)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--b9" in a:
        i = a.index("--b9")
        sys.exit(main(*a[:i], *a[i + 1:]))
    sys.exit(main(*a))
