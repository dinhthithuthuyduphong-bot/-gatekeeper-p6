"""Runnability check for a study's targets: baseline only, the skill is NEVER applied, so
no outcome is observed.  Reports whether each target installs and how many of its census
tests pass in three baseline runs (the census rule: >= 5 stable passes).

python tools/baseline_check.py study_e/config_study_e.json E1_pyyaml out_dir
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from fetch_real_targets import _clone_ref  # noqa: E402
from run_study_d import _pytest_once  # noqa: E402
from gatekeeper_lite.skill import Target  # noqa: E402
from gatekeeper_lite.drawharness import _Worker, _load  # noqa: E402


def main(config, target_id, out_dir):
    base = Path(config).resolve().parent
    m = json.loads((base / "eval_targets" / target_id / "gk_target.json").read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"target": target_id, "python": sys.version.split()[0]}
    work = Path(tempfile.mkdtemp())
    try:
        root = work / target_id
        rec["commit"] = _clone_ref(m["checkout"]["repo"], m["checkout"]["ref"], root)
        shutil.rmtree(root / ".git", ignore_errors=True)
        (root / "gk_target.json").write_text(json.dumps(m))
        kind, _, pkg = m.get("install", "").partition(":")
        env = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", str(root)], env=env,
                           capture_output=True, text=True)
        rec["install_ok"] = r.returncode == 0
        rec["install_tail"] = (r.stdout + r.stderr)[-600:]
        if kind == "self-then-uninstall":
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", pkg])
        if m.get("census_requirements"):
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", *m["census_requirements"]])
        target = Target.load(root)
        runs = [_pytest_once(target, None, m["census_tests"], f"b{i}") for i in range(3)]
        ids = set().union(*(x["results"] for x in runs))
        stable = [t for t in ids if not t.startswith("::") and all(t in x["results"] and x["results"][t]["passed"] for x in runs)]
        rec.update(collected=len(ids), stable_pass=len(stable), census_would_be="VALID" if len(stable) >= 5 else "INVALID",
                   exits=[x["exit"] for x in runs], tail=runs[0]["tail"][-600:])
        # diagnostics: the first failing census test's output (the tail shows only the end)
        rec["census_first_failure"] = next((k + ": " + (v.get("error") or "")[:400] for k, v in runs[0]["results"].items()
                                            if not v.get("passed")), None)
        # oracle sanity on the UNTREATED code only (10 draws per scope; skill never applied)
        import random
        oracle_path = (base / m["draw_oracle"]).resolve()
        oracle = _load(oracle_path)
        w = _Worker(root, m.get("pythonpath", []), oracle_path, 1)
        sanity = {}
        try:
            for scope, gen in oracle.scopes().items():
                rng = random.Random(f"baseline-sanity:{scope}")
                ok = err = not_ok = 0
                examples = []
                for _ in range(10):
                    d = gen(rng)
                    o = w.run(d)
                    if "harness_error" in o:
                        err += 1
                        examples.append(o["harness_error"][:150])
                    else:
                        ok += int(oracle.judge(scope, d, o, o)[0])
                        if o.get("ok") is False:          # differential judges pass trivially; check execution too
                            not_ok += 1
                            examples.append(json.dumps(o)[:200])
                sanity[scope] = {"baseline_judged_pass": ok, "harness_errors": err, "execution_not_ok": not_ok,
                                 "examples": examples[:3]}
        finally:
            w.close()
        rec["oracle_sanity_baseline_only"] = sanity
    except Exception as exc:
        rec["error"] = f"{type(exc).__name__}: {exc}"[:500]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / f"BASELINE_{target_id}.json").write_text(json.dumps(rec, indent=2))
    print(json.dumps({k: rec.get(k) for k in ("target", "install_ok", "collected", "stable_pass", "census_would_be", "error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
