import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import split_candidates as S  # noqa: E402
import check_track as C  # noqa: E402


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


class CheckTrack(unittest.TestCase):
    def test_a_file_from_the_other_track_is_rejected(self):
        c = cands(60)
        parts = S.split(c, "seedZ")
        self.assertEqual(C.wrong_track(parts["ASTAR"], "ASTAR", "seedZ"), [])
        self.assertEqual(C.wrong_track(parts["RR"], "RR", "seedZ"), [])
        self.assertEqual(len(C.wrong_track(parts["RR"], "ASTAR", "seedZ")), len(parts["RR"]))
        mixed = parts["ASTAR"][:3] + parts["RR"][:1]
        self.assertEqual(len(C.wrong_track(mixed, "ASTAR", "seedZ")), 1)

    def test_unknown_track_name_is_refused(self):
        with self.assertRaises(SystemExit):
            C.main("x.json", "BOTH")


if __name__ == "__main__":
    unittest.main()
