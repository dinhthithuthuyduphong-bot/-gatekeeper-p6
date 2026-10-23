"""Harness statelessness check (post hoc, 0 cost): re-execute recorded draws of a frozen study in a
SHUFFLED order, with FRESH worker processes every `chunk` draws, and compare every paired outcome
(Z, regression) with the outcome recorded in the original sequential run.  Any mismatch means that
an outcome depended on execution order or on state carried between draws.
python tools/statelessness_check.py STUDY_DIR/config_*.json TARGET out_dir [n_per_scope] [chunk]"""
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from gatekeeper_ext.none_identity import register  # noqa: E402
register()
from fetch_real_targets import _clone_ref  # noqa: E402
from run_study_d import drand_seed  # noqa: E402
from gatekeeper_lite.drawharness import _Worker, _load  # noqa: E402
from gatekeeper_lite.gatekeeper import bind_modules  # noqa: E402
from gatekeeper_lite.skill import Skill, Target  # noqa: E402


def main(config, target_id, out_dir, n_per_scope="100", chunk="25"):
    n_per_scope, chunk = int(n_per_scope), int(chunk)
    cfg_path = Path(config).resolve()
    base = cfg_path.parent
    cfg = json.loads(cfg_path.read_text())
    seed = drand_seed(cfg.get("seed_freeze_sha256") or hashlib.sha256((base / "FREEZE.json").read_bytes()).hexdigest(),
                      cfg["seed_time_utc"])["seed"]
    m = json.loads((base / "eval_targets" / target_id / "gk_target.json").read_text())
    result = json.loads((base / "results" / f"RESULT_{target_id}.json").read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp())
    rec = {"target": target_id, "seed": seed, "n_per_scope": n_per_scope, "chunk": chunk, "scopes": {}}
    try:
        root = work / "t"
        _clone_ref(m["checkout"]["repo"], m["checkout"]["ref"], root)
        shutil.rmtree(root / ".git", ignore_errors=True)
        (root / "gk_target.json").write_text(json.dumps(m))
        kind, _, pkg = m.get("install", "").partition(":")
        env = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        for pre in m.get("pre_install", []):
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", pre], env=env)
        if kind == "self-then-uninstall":
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", str(root)], check=True, env=env)
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", pkg], check=True)
        target = Target.load(root)
        treated = bind_modules([Skill.load(base / cfg["skill"])], target)["treated"]
        snap_t = work / "treated"
        shutil.copytree(root, snap_t)
        for rel, src in treated.items():
            (snap_t / rel).write_text(src, encoding="utf-8")
        oracle_path = (base / m["draw_oracle"]).resolve()
        oracle = _load(oracle_path)
        for scope, gen in oracle.scopes().items():
            rng = random.Random(f"{seed}:{target_id}:{scope}")
            draws = [gen(rng) for _ in range(n_per_scope)]
            recorded = result["scopes"][scope]["trace"][:n_per_scope]
            order = list(range(n_per_scope))
            random.Random(f"shuffle:{seed}:{scope}").shuffle(order)
            got = {}
            for start in range(0, n_per_scope, chunk):
                w0 = _Worker(root, m.get("pythonpath", []), oracle_path, seed)   # same hash seed as the study run
                w1 = _Worker(snap_t, m.get("pythonpath", []), oracle_path, seed)
                try:
                    for i in order[start:start + chunk]:
                        o0, o1 = w0.run(draws[i]), w1.run(draws[i])
                        if "harness_error" in o0 or "harness_error" in o1:
                            got[i] = "harness_error"
                            continue
                        p0, p1 = oracle.judge(scope, draws[i], o0, o1)
                        got[i] = [float(int(not p1) - int(not p0)), bool(p0 and not p1)]
                finally:
                    w0.close(); w1.close()
            mism = [i for i in range(n_per_scope) if got[i] != [float(recorded[i][0]), bool(recorded[i][1])]]
            rec["scopes"][scope] = {"compared": n_per_scope, "mismatches": len(mism), "examples": mism[:10],
                                    "harness_errors": sum(1 for v in got.values() if v == "harness_error")}
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rec["status"] = "STATELESS" if all(v["mismatches"] == 0 for v in rec["scopes"].values()) else "ORDER_OR_STATE_DEPENDENT"
    (out / f"STATELESS_{target_id}.json").write_text(json.dumps(rec, indent=2))
    print(rec["status"], {s: (v["mismatches"], v["harness_errors"]) for s, v in rec["scopes"].items()})
    return 0 if rec["status"] == "STATELESS" else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:6]))
