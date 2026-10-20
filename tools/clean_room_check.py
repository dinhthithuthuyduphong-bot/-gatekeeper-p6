"""Clean-room reproducibility check (fresh checkout, nothing pre-built).

python tools/clean_room_check.py
1. unit tests; 2. demo run compared with demo/EXPECTED_DECISIONS.json;
3. decision simulation reproduces the frozen numbers in study_d/DECISION_SIM_default.md;
4. freeze verification of study_d when it is FROZEN.  Exit 1 on any mismatch.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def step(name, ok, detail=""):
    print(f"[{'OK' if ok else 'FAIL'}] {name}{' — ' + detail if detail else ''}")
    return ok


def main() -> int:
    ok = step("unit tests", subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                                           cwd=ROOT, capture_output=True).returncode == 0)
    from gatekeeper_lite.experiment import run_experiment
    run = run_experiment(ROOT / "demo" / "config.json")
    exp = json.loads((ROOT / "demo" / "EXPECTED_DECISIONS.json").read_text())["records"]
    got = [{"target": x["target"], "skills": x["skills"], "ground_truth": x["ground_truth"],
            "decisions": {k: x["comparators"][k]["decision"] for k in ("B2", "B6R", "B8", "Gatekeeper")},
            "tasks_used": x["gatekeeper"]["tasks_used"]} for x in run["records"]]
    ok &= step("demo decisions match EXPECTED_DECISIONS.json", got == exp)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "sim.md"
        subprocess.run([sys.executable, str(ROOT / "tools" / "decision_sim.py"), "--sims", "1500",
                        "--out", str(out)], cwd=ROOT, capture_output=True, check=True)
        ok &= step("decision simulation reproduces study_d/DECISION_SIM_default.md",
                   out.read_text() == (ROOT / "study_d" / "DECISION_SIM_default.md").read_text())
    cfg = json.loads((ROOT / "study_d" / "config_study_d.json").read_text())
    if cfg.get("status") == "FROZEN":
        r = subprocess.run([sys.executable, str(ROOT / "tools" / "freeze_study.py"), "verify", "study_d"],
                           cwd=ROOT, capture_output=True, text=True)
        ok &= step("study_d freeze hashes", r.returncode == 0, r.stdout.strip()[:200])
    else:
        step("study_d freeze hashes", True, "not frozen yet (skipped)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
