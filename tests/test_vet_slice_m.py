import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vet_slice as V  # noqa: E402


def cands(n_repos=30, per=3):
    return [{"name": "r%d_pr%d" % (r, i), "repo": "https://github.com/o/r%d.git" % r, "pr": i, "python": "3.12"}
            for r in range(n_repos) for i in range(per)]


class VetSlice(unittest.TestCase):
    def test_shards_partition_the_first_limit_candidates(self):
        c = cands(30)
        parts = [V.slice_for(c, s, 4, 50) for s in range(4)]
        flat = [x["name"] for p in parts for x in p]
        self.assertEqual(sorted(flat), sorted(x["name"] for x in c[:50]))
        self.assertEqual(len(flat), len(set(flat)))

    def test_timeouts_and_crashes_are_recorded_not_skipped(self):
        calls = []

        def runner(spec, out, timeout):
            name = Path(spec).stem
            calls.append(name)
            if name.endswith("pr1"):
                raise subprocess.TimeoutExpired("x", 1)
            if name.endswith("pr2"):
                raise RuntimeError("boom")
            return subprocess.CompletedProcess([], 0, "ok", "")
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "c.json"
            f.write_text(json.dumps(cands(2)))
            V.run(str(f), str(Path(tmp) / "o"), 0, 1, 10, 5, runner)
            rows = json.loads((Path(tmp) / "o" / "SHARD_0_SUMMARY.json").read_text())["candidates"]
        self.assertEqual([r["status"] for r in rows], ["FINISHED", "TIMEOUT", "CRASH", "FINISHED", "TIMEOUT", "CRASH"])
        self.assertEqual(len(calls), 6)


if __name__ == "__main__":
    unittest.main()
