"""Run a command locally with a traceable log, and push the log to the branch.

python tools/local_run.py NAME [--no-push] -- CMD [ARGS...]

Writes logs/local_runs/<UTC time>_<NAME>.log: the command, working directory, git HEAD, uncommitted files at start, start and end
time, exit code and the full stdout and stderr; appends one row to logs/local_runs/INDEX.md; commits both (and nothing else) and
pushes to the current branch and to main, unless --no-push.  The command's exit code is returned.
"""
import datetime
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs/local_runs"
INDEX = LOG_DIR / "INDEX.md"
HEADER = ("# Local runs\n\nEvery local run made through `tools/local_run.py`; each row links its full log.\n\n"
          "| UTC start | Name | Command | Exit | Seconds | HEAD | Log |\n|---|---|---|---|---|---|---|\n")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main(argv):
    if "--" not in argv or argv.index("--") == 0:
        print(__doc__)
        return 2
    name = re.sub(r"[^A-Za-z0-9_.-]", "_", argv[0])
    push = "--no-push" not in argv[:argv.index("--")]
    cmd = argv[argv.index("--") + 1:]
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    start = datetime.datetime.now(datetime.timezone.utc)
    head, dirty = git("rev-parse", "--short", "HEAD"), git("status", "--short")
    t0 = time.time()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    secs = time.time() - t0
    stamp = start.strftime("%Y%m%dT%H%M%SZ")
    log = LOG_DIR / ("%s_%s.log" % (stamp, name))
    log.write_text("command: %s\ncwd: %s\nhead: %s\nuncommitted at start:\n%s\nstart: %s\nseconds: %.1f\nexit: %d\n\n"
                   "===== stdout =====\n%s\n===== stderr =====\n%s\n" % (" ".join(cmd), ROOT, head, dirty or "(none)", start.isoformat(),
                                                                       secs, p.returncode, p.stdout, p.stderr))
    if not INDEX.exists():
        INDEX.write_text(HEADER)
    shown = " ".join(cmd).replace("|", "\\|")
    with INDEX.open("a") as f:
        f.write("| %s | %s | `%s` | %d | %.1f | %s | [log](%s) |\n" % (start.strftime("%Y-%m-%d %H:%M"), name, shown[:120], p.returncode,
                                                                      secs, head, log.name))
    sys.stdout.write(p.stdout[-4000:])
    sys.stderr.write(p.stderr[-2000:])
    if push:
        git("add", str(log.relative_to(ROOT)), str(INDEX.relative_to(ROOT)))
        subprocess.run(["git", "commit", "-q", "-m", "Local run log: %s (exit %d)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
                        "Claude-Session: https://claude.ai/code/session_01HnEHQyrYok4Zv2BE2RWPrc" % (name, p.returncode),
                        "--", str(log.relative_to(ROOT)), str(INDEX.relative_to(ROOT))], cwd=ROOT)
        branch = git("rev-parse", "--abbrev-ref", "HEAD")
        subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=ROOT)
        subprocess.run(["git", "rebase", "-q", "--autostash", "origin/main"], cwd=ROOT)
        for target in (branch, "main"):
            subprocess.run(["git", "push", "-q", "origin", "HEAD:%s" % target], cwd=ROOT)
    return p.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
