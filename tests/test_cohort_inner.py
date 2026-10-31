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


GEN_CODE = "```python\ndef make_inputs(rng, n):\n    return [(None, [rng.choice([True, False, 0, 1, -3, 2])], {}) for _ in range(n)]\n```"


class FunctionOracle(unittest.TestCase):
    def run_fn(self, tmp, replies):
        o, g = G.make(tmp, "o", G.ORIG), G.make(tmp, "g", G.GOLD)
        args = {"orig": str(o), "gold": str(g), "work": str(Path(tmp) / "w"), "out": str(Path(tmp) / "r.json"), "vet": VET, "issue": None,
                "pr_title": "is_int accepts bool", "models": [CFG], "reps": 1, "seed": 3, "cap_usd": 5.0, "runner": "unittest", "n_draws": 120,
                "scripted": {"fake": replies, "generator": [GEN_CODE]}, "oracle": "function",
                "fn_target": {"file": "m.py", "qualname": "is_int"}, "generator_model": dict(CFG, name="generator"),
                "visible_override": {"kind": "python", "code": "import m,sys; sys.exit(0 if m.is_int(True) is False else 1)"}}
        return CI.run(args)

    def test_the_function_oracle_scores_a_good_and_a_bad_patch(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = self.run_fn(tmp, [DIFF_GOOD])
        a = good["attempts"][0]
        self.assertEqual(good["harness"]["oracle"], "function", good)
        self.assertTrue(good["generator"]["usable"], good["generator"])
        self.assertEqual((a["draws"]["harm"], a["draws"]["divergent"]), (0, 0))
        self.assertGreater(a["draws"]["help"], 0)
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.run_fn(tmp, [DIFF_BAD])
        b = bad["attempts"][0]
        self.assertGreater(b["draws"]["harm"], 0)                                 # is_int(1) == False is a regression
        self.assertNotIn("diff", b)                                               # capture is off by default

    def test_capture_keeps_the_patch_and_the_outcomes(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g = G.make(tmp, "o", G.ORIG), G.make(tmp, "g", G.GOLD)
            args = {"orig": str(o), "gold": str(g), "work": str(Path(tmp) / "w"), "out": str(Path(tmp) / "r.json"), "vet": VET, "issue": None,
                    "pr_title": "t", "models": [CFG], "reps": 1, "seed": 3, "cap_usd": 5.0, "runner": "unittest", "n_draws": 120,
                    "scripted": {"fake": [DIFF_BAD], "generator": [GEN_CODE]}, "oracle": "function", "capture": True,
                    "fn_target": {"file": "m.py", "qualname": "is_int"}, "generator_model": dict(CFG, name="generator"),
                    "visible_override": {"kind": "python", "code": "import m,sys; sys.exit(0 if m.is_int(True) is False else 1)"}}
            r = CI.run(args)
        a = r["attempts"][0]
        self.assertIn("+++ b/m.py", a["diff"])
        self.assertEqual(len(a["draws"]["outcomes"]), r["harness"]["stable_inputs"])


class Fixes(unittest.TestCase):
    def test_api_seed_always_fits_a_signed_32_bit_integer_with_room_for_retries(self):
        for s in (0, 2197221932, 4217795844, 2 ** 32 - 1):          # the two seeds that got HTTP 400 in P0, and the maximum
            self.assertLessEqual(CI.api_seed(s) + 100 + 5, 2 ** 31 - 1)

    def test_test_ids_reported_relative_to_a_sub_directory_are_mapped(self):
        vet = dict(VET, changed_files=["src/pk/m.py", "src/pk/tests/unit/test_a.py"], gold_test_files=["src/pk/tests/unit/test_a.py", "tests/test_b.py"],
                   eligible_oracle=["tests.unit.test_a.T::test_x"], eligible_sources={"tests.unit.test_a.T::test_x": "def test_x(): ..."},
                   classification={"tests.unit.test_a.T::test_x": "F->P", "tests.unit.test_a.T::test_y": "P->P"})
        manifest, inst, remap = CI.build_instance_robust(vet, None, "t")
        self.assertEqual(inst["visible"]["tests"], ["src/pk/tests/unit/test_a.py::T::test_x"])
        self.assertEqual(inst["hidden_p2p"], ["src/pk/tests/unit/test_a.py::T::test_y"])
        self.assertEqual(remap["tests.unit.test_a.T::test_x"], "src.pk.tests.unit.test_a.T::test_x")

    def test_http_429_is_retried_with_backoff_then_succeeds(self):
        import io
        import json as J
        import os
        import urllib.error
        import urllib.request
        os.environ["TOK_Z"] = "k"
        calls = {"n": 0}

        class R:
            def read(self):
                return J.dumps({"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                                "usage": {"prompt_tokens": 5, "total_tokens": 7}}).encode()

        def flaky(req, timeout=0):
            calls["n"] += 1
            if calls["n"] <= 2:
                raise urllib.error.HTTPError(req.full_url, 429, "Too Many", {}, io.BytesIO(b'{"error":{"status":"RESOURCE_EXHAUSTED"}}'))
            return R()
        waits = []
        old, old_sleep = urllib.request.urlopen, CI.RefreshingClient._sleep
        urllib.request.urlopen, CI.RefreshingClient._sleep = flaky, staticmethod(lambda s: waits.append(s))
        try:
            r = CI.RefreshingClient("https://h", "TOK_Z").complete("m", [{"role": "user", "content": "x"}], 16, 0, 1)
        finally:
            urllib.request.urlopen, CI.RefreshingClient._sleep = old, old_sleep
        self.assertEqual(r["text"], "ok")
        self.assertEqual(waits, [10, 30])

    def test_http_429_gives_up_after_four_retries(self):
        import io
        import os
        import urllib.error
        import urllib.request
        os.environ["TOK_Z"] = "k"

        def always(req, timeout=0):
            raise urllib.error.HTTPError(req.full_url, 429, "Too Many", {}, io.BytesIO(b"{}"))
        waits = []
        old, old_sleep = urllib.request.urlopen, CI.RefreshingClient._sleep
        urllib.request.urlopen, CI.RefreshingClient._sleep = always, staticmethod(lambda s: waits.append(s))
        try:
            with self.assertRaises(RuntimeError) as cm:
                CI.RefreshingClient("https://h", "TOK_Z").complete("m", [{"role": "user", "content": "x"}], 16, 0, 1)
        finally:
            urllib.request.urlopen, CI.RefreshingClient._sleep = old, old_sleep
        self.assertEqual(waits, [10, 30, 90, 180])
        self.assertIn("HTTP 429", str(cm.exception))

    def test_http_errors_keep_the_provider_message(self):
        import io
        import os
        import urllib.error
        import urllib.request
        os.environ["TOK_Y"] = "k"
        old = urllib.request.urlopen

        def boom(req, timeout=0):
            raise urllib.error.HTTPError(req.full_url, 400, "Bad Request", {}, io.BytesIO(b'{"error":{"message":"Invalid value at seed (TYPE_INT32)"}}'))
        urllib.request.urlopen = boom
        try:
            with self.assertRaises(RuntimeError) as cm:
                CI.RefreshingClient("https://h", "TOK_Y").complete("m", [{"role": "user", "content": "x"}], 16, 0, 1)
        finally:
            urllib.request.urlopen = old
        self.assertIn("TYPE_INT32", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
