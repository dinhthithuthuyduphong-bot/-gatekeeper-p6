import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import p_stream as S  # noqa: E402


class Fake:
    """Stage stubs that record what each stage received."""

    def __init__(self, verdict="ELIGIBLE", funcs=None, gen=None):
        self.verdict, self.funcs, self.genr, self.calls = verdict, funcs, gen, []

    def vet(self, cand, out):
        self.calls.append("vet")
        return {"verdict": self.verdict, "name": cand["name"]}

    def fn(self, v, cand, out):
        self.calls.append("fn")
        return {"verdict": "usable" if any(f.get("usable") for f in self.funcs or []) else "never differs", "functions": self.funcs or []}

    def gen(self, v, cand, target, out):
        self.calls.append(("gen", target["qualname"], target["generator_sha256"]))
        return self.genr or {"inner": {"status": "FINISHED", "attempts": [{"model": "flash", "status": "SUBMITTED", "labels": {"plausible": True},
                                                                           "draws": {"h_hat": 0.02, "in_band": True}}]}}


C = {"name": "x_pr1", "repo": "https://github.com/o/x.git", "pr": 1}
CODE = "def make_inputs(rng, n):\n    return []\n"


class Stream(unittest.TestCase):
    def test_a_candidate_that_is_not_eligible_stops_after_vetting(self):
        f = Fake(verdict="NOT_ELIGIBLE")
        s = S.process(C, "o", f)
        self.assertEqual((f.calls, s["stage_reached"]), (["vet"], "P-S2"))

    def test_no_usable_function_stops_before_any_model_call_for_patches(self):
        f = Fake(funcs=[{"file": "a.py", "qualname": "f", "usable": False}])
        s = S.process(C, "o", f)
        self.assertEqual((f.calls, s["stage_reached"]), (["vet", "fn"], "P-S3"))

    def test_the_first_usable_function_and_its_stored_generator_go_to_generation(self):
        funcs = [{"file": "b.py", "qualname": "g", "usable": True, "generator_code": CODE},
                 {"file": "a.py", "qualname": "z", "usable": True, "generator_code": CODE + "#"},
                 {"file": "a.py", "qualname": "f", "usable": False}]
        f = Fake(funcs=funcs)
        s = S.process(C, "o", f)
        self.assertEqual(f.calls[2][1], "z")                                   # sorted by (file, qualname): a.py::z
        self.assertEqual(f.calls[2][2], hashlib.sha256((CODE + "#").encode()).hexdigest())
        self.assertEqual(s["stage_reached"], "P-GEN")
        self.assertTrue(s["attempts"][0]["in_band"])

    def test_a_usable_function_without_stored_code_is_not_used(self):
        f = Fake(funcs=[{"file": "a.py", "qualname": "f", "usable": True}])     # protocol: the generator must exist before patches
        s = S.process(C, "o", f)
        self.assertEqual(s["stage_reached"], "P-S3")

    def test_shards_partition_the_frame_in_order(self):
        cands = [{"name": "c%d" % i, "repo": "r", "pr": i} for i in range(10)]
        shards = [cands[i::3] for i in range(3)]
        self.assertEqual(sorted(c["name"] for sh in shards for c in sh), sorted(c["name"] for c in cands))
        self.assertEqual([c["name"] for c in shards[1]], ["c1", "c4", "c7"])


if __name__ == "__main__":
    unittest.main()
