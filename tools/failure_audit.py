"""Audit every failed GitHub Actions run of this repository: which job and step failed, the error lines, and a root-cause
category.  Runs inside GitHub Actions (needs GH_TOKEN with actions:read); writes FAILURE_AUDIT.json and FAILURE_AUDIT.md.

python tools/failure_audit.py OWNER/REPO OUT_DIR [--max-runs 400] [--runs id,id,...]

Root-cause categories are assigned by the first matching rule (ordered from specific to generic); the matched rule and the
evidence lines are kept so that every category can be checked by hand.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RULES = [
    ("TOKEN_EXPIRED", r"ACCESS_TOKEN_EXPIRED|invalid authentication credentials|HTTP 401", "Vertex OAuth token outlived (about 1 h) or not refreshed"),
    ("RATE_LIMIT_429", r"HTTP 429|RESOURCE_EXHAUSTED|rate limit", "provider quota; retried with back-off where the client supports it"),
    ("INPUT_VALIDATION", r"ids not in the frame|not Q-A1 targets|AssertionError|at most 256 jobs", "workflow input rejected (e.g. an instance id that is not in the frame)"),
    ("NOT_FROZEN_OR_FREEZE_DRIFT", r"is not FROZEN|freeze .*changed|FREEZE.*mismatch|changed since freeze|amendment .* not applied", "study not frozen, or a frozen file changed"),
    ("UNIT_TESTS_FAILED", r"FAILED \((failures|errors)=", "unit tests failed before the guarded step"),
    ("CANCELLED_OR_TIMEOUT", r"exceeded the maximum execution time|The operation was canceled|exit code 143|SIGTERM|timed out", "job cancelled, killed (143) or over its time limit"),
    ("GIT_PUSH_REJECTED", r"\[rejected\]|non-fast-forward|failed to push|Updates were rejected", "push raced with another commit"),
    ("MISSING_FILE", r"FileNotFoundError|No such file or directory|can't open file", "a path the step expected was missing"),
    ("NETWORK", r"URLError|Connection reset|Temporary failure in name resolution|RemoteDisconnected|Read timed out", "network error to an external service"),
    ("PYTHON_EXCEPTION", r"Traceback \(most recent call last\)|Error: ", "uncaught Python exception (see evidence)"),
]
EVIDENCE = re.compile(r"##\[error\]|Traceback|Error|Exception|HTTP \d{3}|AssertionError|SystemExit|FAILED|exit code|rejected|ACCESS_TOKEN|RESOURCE_EXHAUSTED|No such file")
TS = re.compile(r"^\d{4}-\d\d-\d\dT[\d:.]+Z ")


def gh(*args, text=True):
    p = subprocess.run(["gh", "api", *args], capture_output=True, text=text)
    if p.returncode:
        raise RuntimeError(p.stderr[:300])
    return p.stdout


def failed_runs(repo, max_runs):
    runs, page = [], 1
    while len(runs) < max_runs:
        d = json.loads(gh("repos/%s/actions/runs?per_page=100&page=%d" % (repo, page)))
        batch = d.get("workflow_runs") or []
        if not batch:
            break
        runs += batch
        page += 1
    return [r for r in runs[:max_runs] if r.get("conclusion") in ("failure", "timed_out", "startup_failure")]


def classify(text):
    for name, pat, why in RULES:
        if re.search(pat, text):
            return name, why, pat
    return "OTHER", "no rule matched; read the evidence", None


def audit_run(repo, run):
    jobs = json.loads(gh("repos/%s/actions/runs/%d/jobs?per_page=100" % (repo, run["id"]))).get("jobs") or []
    rec = {"run_id": run["id"], "workflow": run.get("name"), "created": run.get("created_at"), "sha": (run.get("head_sha") or "")[:7],
           "conclusion": run.get("conclusion"), "url": run.get("html_url"), "jobs_total": len(jobs), "failed_jobs": []}
    if not jobs:
        rec["category"], rec["why"] = "WORKFLOW_DID_NOT_START", "no job was created (invalid workflow file or startup failure)"
        return rec
    texts = []
    p = subprocess.run(["gh", "run", "view", str(run["id"]), "-R", repo, "--log-failed"], capture_output=True, text=True)
    failed_log = p.stdout if p.returncode == 0 else ""
    rec["log_chars"], rec["log_error"] = len(failed_log), (p.stderr[:200] if p.returncode else None)
    by_job = {}
    for line in failed_log.splitlines():                       # "<job>\t<step>\t<timestamp> <text>"
        parts = line.split("\t", 2)
        if len(parts) == 3:
            by_job.setdefault(parts[0], []).append(TS.sub("", parts[2]))
    for j in jobs:
        if j.get("conclusion") not in ("failure", "timed_out", "cancelled"):
            continue
        steps = [s["name"] for s in j.get("steps") or [] if s.get("conclusion") in ("failure", "timed_out", "cancelled")]
        lines = by_job.get(j.get("name"), [])
        if not lines:                                          # fall back to the job-log endpoint
            try:
                lines = [TS.sub("", l) for l in gh("repos/%s/actions/jobs/%d/logs" % (repo, j["id"])).splitlines()]
            except RuntimeError:
                lines = []
        ev = [l.strip()[:300] for l in lines if EVIDENCE.search(l)][-12:]
        texts.append("\n".join(lines[-400:]))
        rec["failed_jobs"].append({"job": j.get("name"), "failed_steps": steps, "evidence": ev})
        if len(rec["failed_jobs"]) >= 5:                      # matrix runs: five failed jobs are enough to see the pattern
            break
    rec["failed_job_count"] = sum(1 for j in jobs if j.get("conclusion") in ("failure", "timed_out", "cancelled"))
    cat, why, pat = classify("\n".join(texts))
    rec.update(category=cat, why=why, rule=pat)
    return rec


def main(argv):
    repo, out = argv[0], Path(argv[1])
    max_runs = int(argv[argv.index("--max-runs") + 1]) if "--max-runs" in argv else 400
    if "--runs" in argv:
        ids = [int(x) for x in argv[argv.index("--runs") + 1].split(",") if x]
        runs = [json.loads(gh("repos/%s/actions/runs/%d" % (repo, i))) for i in ids]
    else:
        runs = failed_runs(repo, max_runs)
    recs = []
    for r in runs:
        try:
            recs.append(audit_run(repo, r))
        except RuntimeError as exc:
            recs.append({"run_id": r["id"], "workflow": r.get("name"), "category": "AUDIT_ERROR", "why": str(exc)})
    out.mkdir(parents=True, exist_ok=True)
    (out / "FAILURE_AUDIT.json").write_text(json.dumps(recs, indent=1))
    by = {}
    for r in recs:
        by[r["category"]] = by.get(r["category"], 0) + 1
    md = ["# Failure audit (%d failed runs)" % len(recs), "", "| Category | Runs |", "|---|---|"]
    md += ["| %s | %d |" % (k, v) for k, v in sorted(by.items(), key=lambda kv: -kv[1])]
    md += ["", "| Run | Workflow | Created | Category | Failed step | Last evidence line |", "|---|---|---|---|---|---|"]
    for r in recs:
        fj = (r.get("failed_jobs") or [{}])[0]
        step = ", ".join(fj.get("failed_steps") or [])[:60]
        ev = ((fj.get("evidence") or [""])[-1]).replace("|", "\\|")[:160]
        md.append("| [%s](%s) | %s | %s | %s | %s | %s |" % (r["run_id"], r.get("url", ""), r.get("workflow"), (r.get("created") or "")[:16],
                                                       r["category"], step.replace("|", "\\|"), ev))
    (out / "FAILURE_AUDIT.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[:4 + len(by)]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
