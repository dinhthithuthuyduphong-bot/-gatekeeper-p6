"""Small, read-only evidence helpers. Never call a model or alter a source checkout."""
import hashlib
import json
import subprocess
import time
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def new_output(path):
    path = Path(path).resolve()
    if path.exists() and any(path.iterdir()):
        raise ValueError("Choose a new output directory; preserve earlier attempts")
    path.mkdir(parents=True, exist_ok=True)
    return path


def execute(command, cwd, log, env=None, timeout=600):
    start = time.perf_counter()
    try:
        p = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                           text=True, errors="replace", timeout=timeout)
        code, output = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as exc:
        def decode(x):
            return x.decode(errors="replace") if isinstance(x, bytes) else x or ""
        code, output = 124, decode(exc.stdout) + decode(exc.stderr) + "\nCOMMAND_TIMEOUT\n"
    Path(log).write_text(output)
    receipt = {"command":command, "returncode":code, "seconds":time.perf_counter()-start,
               "log":Path(log).name, "log_sha256":digest(log)}
    print(json.dumps({"step":Path(log).stem, "returncode":code, "seconds":round(receipt["seconds"],3)}), flush=True)
    return receipt


def checkout(repository, revision, directory, logs):
    directory, logs = Path(directory).resolve(), Path(logs).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    logs.mkdir(parents=True, exist_ok=True)
    rows=[]
    for i, cmd in enumerate((["git", "init", "-q"], ["git", "fetch", "--depth=1",
               "https://github.com/"+repository+".git", revision],
               ["git", "checkout", "--detach", "FETCH_HEAD"])):
        row=execute(cmd,directory,logs/("fetch_%s.log"%i),timeout=300);rows.append(row)
        write_json(logs/"FETCH.json",rows)
        if row["returncode"]:raise RuntimeError("Source checkout failed; see fetch logs")
    actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=directory,text=True).strip()
    if actual!=revision:raise ValueError("Source revision mismatch")
    return directory


def verify_source(source, revision, hashes):
    source=Path(source).resolve()
    if subprocess.check_output(["git","rev-parse","HEAD"],cwd=source,text=True).strip()!=revision:
        raise ValueError("Wrong upstream commit")
    if subprocess.check_output(["git","diff","HEAD"],cwd=source,text=True).strip():
        raise ValueError("Tracked source files changed")
    for rel,expected in hashes.items():
        if digest(source/rel)!=expected:raise ValueError("Source/test hash mismatch: "+rel)


def xml_cases(path):
    result={}
    for node in ET.parse(path).getroot().iter("testcase"):
        key=node.attrib.get("classname","")+"::"+node.attrib["name"]
        if key in result:raise ValueError("Duplicate test identity")
        status=next((s for s in ("error","failure","skipped") if node.find(s) is not None),"passed")
        result[key]=status
    if not result:raise ValueError("No test cases recorded")
    return result


def baseline_status(runs):
    if len(runs)!=3:return "INCOMPLETE"
    if any(r["returncode"] not in (0,1) for r in runs):return "ENV_OR_COLLECTION_BLOCKED"
    if any(r.get("phase_errors") for r in runs):return "SETUP_OR_TEARDOWN_BLOCKED"
    if any(r.get("call_failures") for r in runs):return "BASELINE_FUNCTIONAL_FAILURES"
    if any(r["returncode"] != 0 for r in runs):return "INCONSISTENT_EXIT_AND_PHASES"
    if any(r["inventory"]!=runs[0]["inventory"] or r["phase_signature"]!=runs[0]["phase_signature"] for r in runs[1:]):
        return "BASELINE_UNSTABLE"
    if min(r.get("passed_calls",0) for r in runs)<5:return "INSUFFICIENT_PASSING_TESTS"
    return "BASELINE_STABLE_ORACLE_REVIEW_PENDING"
