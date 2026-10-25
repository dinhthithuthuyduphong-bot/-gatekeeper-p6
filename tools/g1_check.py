"""Gate G1 for one B9 instance: gold-differential harness with the automatic generator.

python tools/g1_check.py TARGET_ID OUT_DIR            (real instance; needs network and the study_d inputs)
Known-good patch: the frozen skill's rewrite of the original when it binds, otherwise the gold fix itself
(recorded in the output).  Seed is derived from the target id, so it cannot depend on any outcome.
"""
import hashlib
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
from gatekeeper_ext import golddiff  # noqa: E402
from gatekeeper_lite.gatekeeper import bind_modules  # noqa: E402
from gatekeeper_lite.skill import Skill, Target  # noqa: E402

VETTING = {"D1_py_ecc": "py_ecc_161", "D2_cerberus": "cerberus_144", "D3_speckit": "speckit_3268",
           "D4_openfeature": "openfeature_621", "D5_pycubrid": "pycubrid_479", "A1_speckit_catalog": "speckit_2589"}


def seed_for(target_id):
    return int(hashlib.sha256(("study-l-G1:" + target_id).encode()).hexdigest()[:8], 16)


def run(manifest, gold_ref, skill_path, out_dir, runner="pytest", n_draws=300):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp())
    tid = manifest["target_id"]
    try:
        orig, gold = work / "orig", work / "gold"
        orig_sha = _clone_ref(manifest["checkout"]["repo"], manifest["checkout"]["ref"], orig)
        gold_sha = _clone_ref(manifest["checkout"]["repo"], gold_ref, gold)
        for d in (orig, gold):
            shutil.rmtree(d / ".git", ignore_errors=True)
        (orig / "gk_target.json").write_text(json.dumps(manifest))
        env = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        kind, _, pkg = manifest.get("install", "").partition(":")
        for pre in manifest.get("pre_install", []):
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", pre], env=env)
        if kind == "self-then-uninstall":
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", str(orig)], check=True, env=env)
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", pkg], check=True)
        if manifest.get("census_requirements"):     # same step as the Study D runner
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", *manifest["census_requirements"]], check=True)
        patches, note = {}, None
        skill = Skill.load(Path(skill_path))
        treated = bind_modules([skill], Target.load(orig))["treated"]
        if treated:
            snap = work / "skill"
            shutil.copytree(orig, snap)
            for rel, src in treated.items():
                (snap / rel).write_text(src, encoding="utf-8")
            patches["skill"] = snap
        else:
            patches["gold_itself"] = gold
            note = "skill does not bind on this instance; the gold fix is used as the known-good patch (criterion (b) is then vacuous)"
        args = ["-q", "-p", "no:cacheprovider"] + list(manifest["census_tests"]) if runner == "pytest" else list(manifest["census_tests"])
        res = golddiff.analyze(orig, gold, manifest["modules"], manifest.get("pythonpath", []), runner, args,
                               work / "run", seed_for(tid), patches, n_draws=n_draws)
        res.update(target=tid, orig_sha=orig_sha, gold_sha=gold_sha, known_good_patch=sorted(patches), note=note,
                   python=sys.version.split()[0])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / ("G1_%s.json" % tid)).write_text(json.dumps(res, indent=2))
    g1 = res.get("g1", {})
    print(tid, "eligible" if res.get("eligible") else "INELIGIBLE: " + str(res.get("reason")), "G1 pass:", g1.get("pass"))
    return 0


def main(target_id, out_dir):
    base = ROOT / "study_d"
    manifest = json.loads((base / "eval_targets" / target_id / "gk_target.json").read_text())
    spec = json.loads((base / "targets" / ("%s.json" % VETTING[target_id])).read_text())
    return run(manifest, spec["gold"], base / "skills" / "bool-excluded-from-int.json", out_dir)


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
