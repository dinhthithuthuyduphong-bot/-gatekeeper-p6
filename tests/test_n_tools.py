import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import freeze_doctor as F  # noqa: E402
import n_assemble as A  # noqa: E402
from split_candidates import track  # noqa: E402


def cands(prefix, n_repos, per=2, start=0):
    return [{"name": "%s%d_%d" % (prefix, r, i), "repo": "https://github.com/o/%s%d.git" % (prefix, r), "pr": i}
            for r in range(start, start + n_repos) for i in range(per)]


class Assemble(unittest.TestCase):
    def test_frames(self):
        first, cont = cands("a", 30), cands("b", 40)
        astar, rr, s = A.assemble(first, cont, "S")
        self.assertTrue(all(track("S", c["repo"]) == "ASTAR" for c in astar))
        self.assertTrue(all(track("S", c["repo"]) == "RR" for c in rr))
        self.assertTrue({c["name"] for c in astar} <= {c["name"] for c in cont})        # no exposed candidate
        self.assertEqual(s["frame_rr"], s["first_500"]["RR"] + s["continuation"]["RR"])
        self.assertEqual([c["name"] for c in rr][: s["first_500"]["RR"]], [c["name"] for c in first if track("S", c["repo"]) == "RR"])

    def test_duplicates_are_refused(self):
        first = cands("a", 5)
        with self.assertRaises(SystemExit):
            A.assemble(first, first[:2] + cands("b", 3), "S")


class FreezeDoctor(unittest.TestCase):
    def test_an_unlisted_protocol_file_is_a_blocker(self):
        name = "_tmp_freeze_doctor_test"
        d = ROOT / name
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir()
        try:
            (d / "AMENDMENTS.md").write_text("x")
            (d / "GATES.md").write_text("x")
            (d / "config_s.json").write_text(json.dumps({"status": "DRAFT", "extra_tracked": [name + "/GATES.md"]}))
            items = F.check(name)
            self.assertFalse([m for lvl, m in items if lvl == "BLOCKER"], items)
            (d / "DECISION_RULE.md").write_text("x")                       # forgotten in extra_tracked
            items = F.check(name)
            self.assertTrue(any(lvl == "BLOCKER" and "DECISION_RULE.md" in m for lvl, m in items))
            (d / "config_s.json").write_text(json.dumps({"status": "FROZEN", "extra_tracked": [name + "/GATES.md", name + "/DECISION_RULE.md"]}))
            items = F.check(name)
            self.assertTrue(any(lvl == "BLOCKER" and "DRAFT" in m for lvl, m in items))   # already frozen
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
