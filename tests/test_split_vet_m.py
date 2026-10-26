import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import split_candidates as S  # noqa: E402
import vet_slice as V  # noqa: E402


def cands(n_repos=200, per=3):
    return [{"name": "r%d_pr%d" % (r, i), "repo": "https://github.com/o/r%d.git" % r, "pr": i, "python": "3.12"}
            for r in range(n_repos) for i in range(per)]


class Split(unittest.TestCase):
    def test_tracks_are_disjoint_by_repository_and_cover_everything(self):
        c = cands()
        p = S.split(c, "seedA")
        self.assertEqual(len(p["RR"]) + len(p["ASTAR"]), len(c))
        self.assertFalse({x["repo"] for x in p["RR"]} & {x["repo"] for x in p["ASTAR"]})

    def test_deterministic_roughly_balanced_and_seed_dependent(self):
        c = cands()
        a, b = S.split(c, "seedA"), S.split(c, "seedA")
        self.assertEqual(a, b)
        share = len({x["repo"] for x in a["RR"]}) / 200.0
        self.assertTrue(0.4 < share < 0.6, share)
        self.assertNotEqual([x["name"] for x in a["RR"]], [x["name"] for x in S.split(c, "seedB")["RR"]])

    def test_order_inside_a_track_is_preserved(self):
        c = cands(50)
        names = [x["name"] for x in c]
        for part in S.split(c, "s").values():
            idx = [names.index(x["name"]) for x in part]
            self.assertEqual(idx, sorted(idx))

    def test_cli_writes_files_and_a_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "o.json"
            f.write_text(json.dumps(cands(40)))
            S.main(str(f), "x", str(Path(tmp) / "out"))
            s = json.loads((Path(tmp) / "out" / "SPLIT_SUMMARY.json").read_text())
            self.assertEqual(s["shared_repositories"], 0)
            self.assertEqual(s["pull_requests"]["RR"] + s["pull_requests"]["ASTAR"], 120)


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
