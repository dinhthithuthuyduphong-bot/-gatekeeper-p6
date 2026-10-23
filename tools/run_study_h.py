"""Study H runner: R independent replications of the frozen per-cell rule on the synthetic
rare-harm target (real two-worker harness, real none-identity skill, real census).
python tools/run_study_h.py study_h/config_study_h.json out_dir"""
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from gatekeeper_ext.none_identity import register  # noqa: E402
register()
from run_study_d import census, drand_seed  # noqa: E402
from gatekeeper_lite.drawharness import run_draw_study  # noqa: E402
from gatekeeper_lite.eprocess import e_holm  # noqa: E402
from gatekeeper_lite.gatekeeper import bind_modules, replay  # noqa: E402
from gatekeeper_lite.skill import Skill, Target  # noqa: E402


def main(config, out_dir):
    cfg_path = Path(config).resolve()
    base = cfg_path.parent
    cfg = json.loads(cfg_path.read_text())
    if cfg.get("status") == "SMOKE":
        seed_info = {"seed": cfg.get("smoke_seed", 1), "round": None, "note": "SMOKE (development only)"}
    elif cfg.get("status") != "FROZEN":
        raise SystemExit("Study H is not FROZEN")
    else:
        seed_info = drand_seed(cfg.get("seed_freeze_sha256") or
                               hashlib.sha256((base / "FREEZE.json").read_bytes()).hexdigest(), cfg["seed_time_utc"])
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp())
    try:
        root = work / "H1_rare"
        shutil.copytree(base / "fixtures" / "H1_rare", root)
        target = Target.load(root)
        skill = Skill.load(ROOT / cfg["skill"])
        bound = bind_modules([skill], target)
        cen = census(target, bound["treated"], target.manifest["census_tests"])
        oracle = (base / target.manifest["draw_oracle"]).resolve()
        # fail fast and loudly if the oracle file is not the reviewed one (Study H amendment H-A1)
        import importlib.util
        spec = importlib.util.spec_from_file_location("gk_h_oracle_check", oracle)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        digest = hashlib.sha256(oracle.read_bytes()).hexdigest()
        print(f"oracle {oracle} sha256 {digest} size {oracle.stat().st_size}")
        missing = [f for f in ("scopes", "execute", "judge") if not hasattr(mod, f)]
        if missing:
            raise SystemExit(f"oracle {oracle} lacks {missing}; the file in the repository is not the reviewed oracle")
        k = len(cfg["cells"])
        reps = []
        for rep in range(cfg["replications"]):
            seed = int(hashlib.sha256(f"{seed_info['seed']}:{rep}".encode()).hexdigest(), 16) % (2 ** 62)
            res = run_draw_study(target, bound["treated"], oracle,
                                 {"seed": seed, "alpha": cfg["alpha"], "n_max": cfg["n_max"], "theta": cfg["theta"],
                                  "eta": cfg["eta"], "alpha_alarm": cfg["alpha_alarm"],
                                  "b8_full": True}, k)   # full trace: B8, B6-S and the mixture need every draw
            cen_bad = bool(cen.get("new_failures")) or cen.get("status") != "VALID"
            evals = {s: (0.0 if (v["decision"] == "REJECT_HARM" or cen_bad) else v["e_min"]) for s, v in res["scopes"].items()}
            adm = set(e_holm(evals, cfg["alpha"]))
            reps.append({"rep": rep, "seed": seed, "scopes": {
                s: {"decision": ("ADMIT" if s in adm else "REJECT_HARM" if v["decision"] == "REJECT_HARM" else "QUARANTINE"),
                    "draws": v["draws"], "e_min": v["e_min"], "trace": v["trace"]} for s, v in res["scopes"].items()}})
            print(f"rep {rep}: " + ", ".join(f"{s}={r['decision'][:3]}({r['draws']})" for s, r in reps[-1]["scopes"].items()))
        rec = {"seed": seed_info, "oracle_sha256": digest, "bind": {"sites": [vars(x) if hasattr(x, "__dict__") else x for x in bound.get("sites", [])]},
               "B6R_replay": replay(skill), "census": cen, "replications": reps}
        (out / "RESULT_H1_rare.json").write_text(json.dumps(rec, default=str))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
