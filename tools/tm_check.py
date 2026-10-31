"""Study L2 development check for one B9 instance: test-level differential (gatekeeper_ext/testmut.py).
python tools/tm_check.py TARGET_ID OUT_DIR
DEVELOPMENT ONLY: these six instances are exposed (their outcomes were seen in Studies D and L gate G1) and are
never used as confirmatory evidence.  Known-good patch: the frozen skill's rewrite when it binds, else the gold fix."""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import traceback
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from fetch_real_targets import _clone_ref  # noqa: E402
from gatekeeper_ext.testmut_evidence import execute_logged, preserve_run, write_json, write_result_md, write_inventory
from gatekeeper_ext import testmut  # noqa: E402
from gatekeeper_lite.gatekeeper import bind_modules  # noqa: E402
from gatekeeper_lite.skill import Skill, Target  # noqa: E402

VETTING = {"D1_py_ecc": "py_ecc_161", "D2_cerberus": "cerberus_144", "D3_speckit": "speckit_3268",
           "D4_openfeature": "openfeature_621", "D5_pycubrid": "pycubrid_479", "A1_speckit_catalog": "speckit_2589"}


def run(manifest, gold_ref, skill_path, out_dir, runner="pytest", n_draws=200):
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    tid = manifest["target_id"]
    evidence = out / "evidence" / tid
    if evidence.exists() or (out / ("TM_%s.json" % tid)).exists():
        raise FileExistsError("Use a new output directory; existing evidence will not be overwritten")
    evidence.mkdir(parents=True)
    work = Path(tempfile.mkdtemp())
    started = time.time()
    res = {"target": tid, "stage": "DEVELOPMENT_NOT_EVIDENCE", "schema_version": 2,
           "eligible": False, "status": "STARTED", "python": sys.version.split()[0]}
    exit_code = 0
    write_json(evidence / "input_manifest.json", manifest)
    write_json(evidence / "execution_context.json", {"github_sha": os.getenv("GITHUB_SHA"),
               "github_run_id": os.getenv("GITHUB_RUN_ID"), "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
               "gold_ref": gold_ref, "requested_draws": n_draws})
    def install_step(label, command, env=None):
        receipt = execute_logged(command, ROOT, env, evidence / label, 1800)
        if receipt["status"] != "COMPLETED" or receipt["returncode"] != 0:
            raise RuntimeError("dependency step failed: " + label)
    try:
        orig, gold = work / "orig", work / "gold"
        orig_sha = _clone_ref(manifest["checkout"]["repo"], manifest["checkout"]["ref"], orig)
        gold_sha = _clone_ref(manifest["checkout"]["repo"], gold_ref, gold)
        for d in (orig, gold):
            shutil.rmtree(d / ".git", ignore_errors=True)
        (orig / "gk_target.json").write_text(json.dumps(manifest))
        env = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        kind, _, pkg = manifest.get("install", "").partition(":")
        for idx, pre in enumerate(manifest.get("pre_install", [])):
            install_step("pre_install_%d" % idx, [sys.executable, "-m", "pip", "install", "-q", pre], env)
        if kind == "self-then-uninstall":
            install_step("install_target", [sys.executable, "-m", "pip", "install", "-q", str(orig)], env)
            install_step("uninstall_target", [sys.executable, "-m", "pip", "uninstall", "-y", "-q", pkg])
        if manifest.get("census_requirements"):
            install_step("census_dependencies", [sys.executable, "-m", "pip", "install", "-q", *manifest["census_requirements"]])
        install_step("environment_inventory", [sys.executable, "-m", "pip", "freeze"])
        patches, note = {}, None
        treated = bind_modules([Skill.load(Path(skill_path))], Target.load(orig))["treated"]
        if treated:
            snap = work / "skill"
            shutil.copytree(orig, snap)
            for rel, src in treated.items():
                (snap / rel).write_text(src, encoding="utf-8")
            patches["skill"] = snap
            write_json(evidence / "skill_source_overrides.json", treated)
        else:
            patches["gold_itself"] = gold
            note = "skill does not bind; the gold fix is the known-good patch (criterion (b) is then vacuous)"
        seed = int(hashlib.sha256(("study-l2-dev:" + tid).encode()).hexdigest()[:8], 16)
        res.update(orig_sha=orig_sha, gold_sha=gold_sha, known_good_patch=sorted(patches), note=note)
        write_json(evidence / "pre_execution.json", res)
        measured = testmut.analyze(orig, gold, manifest["modules"], manifest.get("pythonpath", []), runner,
                              manifest["census_tests"], patches, work / "run", seed, n_draws=n_draws)
        res.update(measured)
        res.update(status="COMPLETED", b_is_self_comparison=("gold_itself" in patches))
        if measured.get("arm_errors") or measured.get("reason", "").startswith("baseline test run"):
            res["status"] = "HARNESS_INVALID"
            exit_code = 2
    except Exception as exc:
        exit_code = 2
        res.update(status="HARNESS_EXCEPTION", eligible=False, reason=type(exc).__name__ + ": " + str(exc))
        (evidence / "exception.txt").write_text(traceback.format_exc(), encoding="utf-8")
    finally:
        try:
            preserve_run(work / "run", evidence / "run")
            res["total_seconds"] = round(time.time() - started, 3)
            write_json(out / ("TM_%s.json" % tid), res)
            write_result_md(res, out / ("RESULT_%s.md" % tid))
            write_inventory(evidence)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    print(tid, "eligible" if res.get("eligible") else "INELIGIBLE: " + str(res.get("reason")),
          "| trigger", res.get("bug_trigger_rate"), "| checks", res.get("checks", {}).get("all_four"))
    return exit_code


def main(target_id, out_dir):
    base = ROOT / "study_d"
    manifest = json.loads((base / "eval_targets" / target_id / "gk_target.json").read_text())
    spec = json.loads((base / "targets" / ("%s.json" % VETTING[target_id])).read_text())
    return run(manifest, spec["gold"], base / "skills" / "bool-excluded-from-int.json", out_dir)


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))

