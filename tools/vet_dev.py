"""Run the version-2 vetting on one shard (reuses the frozen shard logic of tools/vet_slice.py).

python tools/vet_dev.py CANDIDATES.json OUT_DIR SHARD K [LIMIT] [TIMEOUT_SECONDS]

The vetting tool starts pip and pytest as grandchildren.  subprocess.run(timeout=...) kills only the direct child, and
the grandchildren keep running (verified 26/10/2026), competing for CPU and memory with the next candidates of the shard.
This runner starts the tool in its own process group, sends its output to a file instead of a pipe, and kills the
WHOLE group on timeout; vet_slice records the candidate as TIMEOUT.
"""
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vet_slice  # noqa: E402


def run_group(cmd, timeout, cwd=None):
    with tempfile.TemporaryFile("w+") as log:
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, cwd=cwd, start_new_session=True, text=True)
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            p.wait()
            raise
        log.seek(0)
        return subprocess.CompletedProcess(cmd, p.returncode, log.read(), "")


def runner(spec_path, out_dir, timeout):
    return run_group([sys.executable, str(ROOT / "tools" / "vet_target2.py"), str(spec_path), str(out_dir)], timeout, cwd=str(ROOT))


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(vet_slice.run(a[0], a[1], a[2], a[3], *(a[4:6] or []), runner=runner) if len(a) <= 6 else 2)
