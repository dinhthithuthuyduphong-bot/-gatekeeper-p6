"""Execute the replacement workflow's NetworkX Bash steps locally.

This tests installation and the full study in an isolated directory. It does
not emulate the GitHub service or execute the setup/upload JavaScript actions.
"""
from pathlib import Path
import json
import os
import subprocess
import time
import yaml

ROOT = Path(__file__).resolve().parent.parent
JOB = ROOT / "local_job"
wf = yaml.safe_load((ROOT / "study-i-zero-cost.yml").read_text())
env = dict(os.environ, GITHUB_SHA="local-bootstrap-validation", GITHUB_RUN_ID="LOCAL",
           GITHUB_RUN_ATTEMPT="1", RUNNER_TEMP=str(JOB / "runner_temp"),
           GITHUB_PATH=str(JOB / "github_path.txt"), EXPECTED_PYTHON="3.8.20")
selected = {"Initialize evidence before runtime setup", "Install Python 3.8.20 for NetworkX",
            "Install pinned local-test dependencies", "Reproduce upstream tests and generator diagnostics",
            "Record final job state even if setup failed"}
rows = []
failed = False
for step in wf["jobs"]["reproduce"]["steps"]:
    if step.get("name") not in selected:
        continue
    if failed and step.get("if") != "always()":
        continue
    script = step["run"].replace("${{ matrix.target }}", "networkx").replace("${{ matrix.python }}", "3.8.20")
    script = script.replace("${{ job.status }}", "failure" if failed else "success")
    print("WORKFLOW_STEP", step["name"], flush=True)
    started = time.perf_counter()
    p = subprocess.run(["bash", "-c", script], cwd=JOB, env=env)
    rows.append({"step":step["name"], "returncode":p.returncode, "seconds":time.perf_counter()-started})
    failed |= p.returncode != 0
    additions = (JOB / "github_path.txt").read_text().splitlines()
    if additions:
        env["PATH"] = os.pathsep.join(additions) + os.pathsep + os.environ["PATH"]
(ROOT / "evidence/bootstrap_result.json").write_text(json.dumps({"local_only":True,
    "github_actions_executed":False, "status":"FAIL" if failed else "PASS", "steps":rows},indent=2)+"\n")
raise SystemExit(int(failed))
