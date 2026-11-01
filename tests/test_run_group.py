"""T2-A2: processes started by the target code are killed with the inner process's group."""
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import composition_study as CS  # noqa: E402


class RunGroup(unittest.TestCase):
    def test_orphan_is_killed(self):
        pidfile = Path(tempfile.mkdtemp()) / "pid"
        code = ("import subprocess,sys;p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']);"
                "open(%r,'w').write(str(p.pid))" % str(pidfile))
        import subprocess
        # the leftover child holds the pipes: the call times out exactly as subprocess.run did (outcomes unchanged) ...
        with self.assertRaises(subprocess.TimeoutExpired):
            CS._run_group([sys.executable, "-c", code], 3, None)
        pid = int(pidfile.read_text())   # ... and the leftover child is killed with the group
        time.sleep(0.3)
        try:
            os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            pass
        alive = Path("/proc/%d" % pid).exists() and "zombie" not in Path("/proc/%d/status" % pid).read_text().lower()
        self.assertFalse(alive)

    def test_normal_call(self):
        r = CS._run_group([sys.executable, "-c", "print('x')"], 30, None)
        self.assertEqual((r.returncode, r.stdout), (0, "x\n"))

    def test_timeout_raises(self):
        import subprocess
        with self.assertRaises(subprocess.TimeoutExpired):
            CS._run_group([sys.executable, "-c", "import time;time.sleep(10)"], 0.5, None)


if __name__ == "__main__":
    unittest.main()
