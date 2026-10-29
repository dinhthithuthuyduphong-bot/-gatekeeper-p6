import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import cohort_inner as CI  # noqa: E402
import test_golddiff as G  # noqa: E402

DIFF_GOOD = ("--- a/m.py\n+++ b/m.py\n@@ -1,5 +1,5 @@\n def is_int(x):\n-    return isinstance(x, int)\n"
             "+    return isinstance(x, int) and not isinstance(x, bool)\n \n \n def double(x):\n")
DIFF_BAD = ("--- a/m.py\n+++ b/m.py\n@@ -1,5 +1,5 @@\n def is_int(x):\n-    return isinstance(x, int)\n+    return False\n \n \n def double(x):\n")
VET = {"name": "fix1_pr1", "repo": "https://github.com/o/fix1.git", "pre": "a" * 40, "gold": "b" * 40, "verdict": "ELIGIBLE",
       "changed_files": ["m.py", "test_m.py"], "gold_test_files": ["test_m.py"], "gold_source_diff": "",
       "eligible_oracle": ["test_m.T::test_ints"], "eligible_sources": {"test_m.T::test_ints": "def test_ints(): ..."},
       "classification": {"test_m.T::test_ints": "F->P", "test_m.T::test_strings": "P->P"}}
CFG = {"name": "fake", "model_id": "fake", "prices_usd_per_mtok": {"input": 1.0, "output": 2.0}, "max_output_tokens": 500}


def run(tmp, replies, vet=VET, cap=5.0, reps=1, orig_src=G.ORIG, gold_src=G.GOLD):
    o, g = G.make(tmp, "o", orig_src), G.make(tmp, "g", gold_src)
    args = {"orig": str(o), "gold": str(g), "work": str(Path(tmp) / "w"), "out": str(Path(tmp) / "r.json"), "vet": vet, "issue": None,
            "pr_title": "is_int accepts bool", "models": [CFG], "reps": reps, "seed": 3, "cap_usd": cap, "runner": "unittest", "n_draws": 40,
            "scripted": {"fake": replies},
            "visible_override": {"kind": "python", "code": "import m,sys; sys.exit(0 if m.is_int(True) is False else 1)"}}
    return CI.run(args)


class Inner(unittest.TestCase):
    def test_a_good_patch_is_plausible_and_passes_every_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [DIFF_GOOD])
        self.assertEqual(r["status"], "FINISHED", r)
        a = r["attempts"][0]
        self.assertEqual((a["status"], a["verdicts"]), ("SUBMITTED", ["PASSES_VISIBLE"]))
        self.assertTrue(a["labels"]["plausible"], a["labels"])
        self.assertEqual(a["draws"]["harm"], 0)
        self.assertGreater(a["draws"]["help"], 0)
        g = a["gates"]
        self.assertTrue(all(g[k] for k in ("census_only", "zero_tolerance", "b8_plus", "smoke20")), g)
        # with only 40 draws the statistical gates cannot certify anything (the exact test needs more draws, the certificate
        # about 50 clean ones): this is why gate N2 requires at least 100 complete draws
        self.assertEqual((g["fixed_sample"], g["gatekeeper"], g["_detail"]["xstar"]), (False, False, -1))

    def test_a_patch_that_fails_the_visible_check_is_not_submitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, ["no diff here"] * 5)
        a = r["attempts"][0]
        self.assertEqual(a["status"], "NO_PATCH")
        self.assertNotIn("gates", a)

    def test_a_patch_that_passes_visible_but_breaks_the_rest_is_not_plausible(self):
        # visible check only asks is_int(True) is False, so a constant-False patch passes it but fails test_strings/ints
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [DIFF_BAD])
        a = r["attempts"][0]
        self.assertEqual(a["status"], "SUBMITTED")
        self.assertFalse(a["labels"]["plausible"])
        self.assertFalse(any(a["gates"][k] for k in a["gates"] if not k.startswith("_")))      # every gate rejects a non-plausible patch
        self.assertGreater(a["draws"]["harm"], 0)

    def test_ineligible_harness_stops_before_any_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [DIFF_GOOD], orig_src=G.ORIG, gold_src=G.ORIG)
        self.assertEqual(r["status"], "HARNESS_NOT_ELIGIBLE")
        self.assertEqual(r["attempts"], [])

    def test_the_spend_guard_stops_a_call_that_could_exceed_the_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [DIFF_GOOD], cap=0.0000001)
        a = r["attempts"][0]
        self.assertEqual(a["status"], "NO_PATCH")
        self.assertEqual(a["verdicts"], ["BUDGET_CAP"])
        self.assertEqual(a["calls"], 0)


if __name__ == "__main__":
    unittest.main()
