import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vet_dev  # noqa: E402


class GroupTimeout(unittest.TestCase):
    def test_grandchildren_are_killed_on_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "alive"
            script = Path(tmp) / "parent.py"
            script.write_text("import subprocess,sys,time\n"
                              "subprocess.Popen([sys.executable,'-c',\"import time; time.sleep(3); open(%r,'w').write('x')\"])\n"
                              "time.sleep(30)\n" % str(marker))
            t = time.time()
            with self.assertRaises(subprocess.TimeoutExpired):
                vet_dev.run_group([sys.executable, str(script)], timeout=1)
            self.assertLess(time.time() - t, 5)
            time.sleep(4)
            self.assertFalse(marker.exists())                      # the grandchild did not survive

    def test_output_is_returned_like_subprocess_run(self):
        r = vet_dev.run_group([sys.executable, "-c", "print('hello')"], timeout=20)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "hello"))


if __name__ == "__main__":
    unittest.main()
