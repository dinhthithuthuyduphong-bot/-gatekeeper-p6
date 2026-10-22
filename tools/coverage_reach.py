"""Reach vs effect (post hoc, 0 cost): for each recorded draw of a frozen study, did the
UNTREATED code execute a line the skill rewrites?  Draws are regenerated exactly as the
harness generated them (random.Random(f"{seed}:{target}:{scope}")), so draw i here is draw i
of the recorded trace.  The skill is never applied; no outcome is changed.

python tools/coverage_reach.py study_d/config_study_d.json D5_pycubrid out_dir
"""
import hashlib
import importlib.util
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

WORKER = r'''
import importlib.util, json, sys
oracle_path, target_file, lines, draws = sys.argv[1], sys.argv[2], set(json.loads(sys.argv[3])), json.loads(sys.stdin.read())
spec = importlib.util.spec_from_file_location("gk_cov_oracle", oracle_path)
o = importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
hit = [False]
def tracer(frame, event, arg):
    if frame.f_code.co_filename != target_file:
        return None
    def local(f, ev, a):
        if ev == "line" and f.f_lineno in lines:
            hit[0] = True
        return local
    return local
out = []
for d in draws:
    hit[0] = False
    sys.settrace(tracer)
    try:
        o.execute(d)
    except Exception:
        pass
    finally:
        sys.settrace(None)
    out.append(hit[0])
print(json.dumps(out))
'''


def main(config, target_id, out_dir):
    from run_study_d import drand_seed
    from fetch_real_targets import _clone_ref
    base = Path(config).resolve().parent
    cfg = json.loads(Path(config).read_text())
    seed = drand_seed(cfg.get("seed_freeze_sha256") or hashlib.sha256((base / "FREEZE.json").read_bytes()).hexdigest(),
                      cfg["seed_time_utc"])["seed"]
    m = json.loads((base / "eval_targets" / target_id / "gk_target.json").read_text())
    result = json.loads((base / "results" / f"RESULT_{target_id}.json").read_text())
    sites = result["bind"]["sites"]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"target": target_id, "seed": seed, "sites": sites, "scopes": {}}
    if not sites:
        rec["note"] = "skill did not bind; nothing to reach"
        (out / f"REACH_{target_id}.json").write_text(json.dumps(rec, indent=2))
        return 0
    work = Path(tempfile.mkdtemp())
    try:
        root = work / target_id
        _clone_ref(m["checkout"]["repo"], m["checkout"]["ref"], root)
        kind, _, pkg = m.get("install", "").partition(":")
        env = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        if kind == "self-then-uninstall":
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", str(root)], check=True, env=env)
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", pkg], check=True)
        spec = importlib.util.spec_from_file_location("gk_cov_gen", base / m["draw_oracle"])
        oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(oracle)
        paths = [str(root / p) for p in m.get("pythonpath", [])] + [str(root)]
        wenv = dict(os.environ, PYTHONPATH=os.pathsep.join(paths), PYTHONDONTWRITEBYTECODE="1")
        by_file = {}
        for s in sites:
            by_file.setdefault(str((root / s["module"]).resolve()), []).append(s["line"])
        for scope, gen in oracle.scopes().items():
            rng = random.Random(f"{seed}:{target_id}:{scope}")
            draws = [gen(rng) for _ in range(300)]
            reach = [False] * len(draws)
            for fpath, lines in by_file.items():
                p = subprocess.run([sys.executable, "-c", WORKER, str((base / m["draw_oracle"]).resolve()), fpath,
                                    json.dumps(lines)], input=json.dumps(draws), capture_output=True, text=True,
                                   cwd=root, env=wenv, timeout=3600)
                got = json.loads(p.stdout.strip().splitlines()[-1]) if p.stdout.strip() else [False] * len(draws)
                reach = [a or b for a, b in zip(reach, got)]
            trace = result["scopes"].get(scope, {}).get("trace", [])
            cross = {"reach_help": 0, "reach_tie": 0, "reach_hurt": 0, "noreach_help": 0, "noreach_tie": 0, "noreach_hurt": 0}
            for r, (z, reg) in zip(reach, trace):
                k = ("reach_" if r else "noreach_") + ("hurt" if reg else "help" if z < 0 else "tie")
                cross[k] += 1
            rec["scopes"][scope] = {"reach_rate": sum(reach) / len(reach), "cross": cross}
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / f"REACH_{target_id}.json").write_text(json.dumps(rec, indent=2))
    print(json.dumps({s: v["reach_rate"] for s, v in rec["scopes"].items()}), json.dumps({s: v["cross"] for s, v in rec["scopes"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
