import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import p_stream_resume as R  # noqa: E402


class Stages:
    def __init__(self, boom=()):
        self.boom, self.seen = set(boom), []

    def vet(self, c, out):
        self.seen.append(c["name"])
        if c["name"] in self.boom:
            raise ValueError("broken")
        return {"verdict": "NOT_ELIGIBLE"}


class Resume(unittest.TestCase):
    def test_same_shard_assignment_and_only_unprocessed_candidates(self):
        cands = [{"name": "c%d" % i, "repo": "r"} for i in range(20)]
        self.assertEqual([c["name"] for c in R.todo(cands, 3, 5, {"c8"})], ["c3", "c13", "c18"])

    def test_one_failing_candidate_does_not_end_the_shard(self):
        cands = [{"name": "c%d" % i, "repo": "r"} for i in range(10)]
        st = Stages(boom={"c2"})
        with tempfile.TemporaryDirectory() as tmp:
            done = R.run(cands, tmp, 0, 2, set(), st)
            err = (Path(tmp) / "STREAM_c2.json").read_text()
        self.assertEqual(done, ["c0", "c2", "c4", "c6", "c8"])
        self.assertIn("STAGE_ERROR", err)


if __name__ == "__main__":
    unittest.main()
