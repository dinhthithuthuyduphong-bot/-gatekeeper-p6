import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from gatekeeper_ext import testmut  # noqa: E402
import test_golddiff as G  # noqa: E402  (same bool/int fixture)

JUNIT = '''<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest" errors="0" failures="1" skipped="1" tests="3">
<testcase classname="tests.test_m.TestA" name="test_a[1]" time="0.002"/>
<testcase classname="tests.test_m" name="test_b__gkm3" time="0.001"><failure message="assert 1 == 2&#10;  +  where 1 = f()">trace</failure></testcase>
<testcase classname="tests.test_m" name="test_c" time="0.000"><skipped type="pytest.skip" message="no dep">x</skipped></testcase>
</testsuite></testsuites>'''


class TestMutUnits(unittest.TestCase):
    def test_junit_parser_and_signatures(self):
        r = testmut.parse_junit(JUNIT)
        self.assertEqual([x["status"] for x in r], ["passed", "failed", "skipped"])
        self.assertEqual(r[0]["classname"], "tests.test_m.TestA")
        sig = testmut.signatures(r, ["/x/root"])
        self.assertEqual(list(sig), [3])
        self.assertIn("failed", sig[3])

    def test_norm_removes_machine_specific_text(self):
        s = testmut.norm("at /tmp/abc123/orig/m.py:44 obj 0x7f1234 took 1.52s in /snap/root", ["/snap/root"])
        self.assertNotIn("abc123", s)
        self.assertNotIn("0x7f", s)
        self.assertIn("<ROOT>", s)

    def test_mutated_sources_compile_and_keep_originals(self):
        with tempfile.TemporaryDirectory() as tmp:
            o = G.make(tmp, "o", G.ORIG)
            base, _ = testmut.run_tests(o, "unittest", ["test_m.py"], [], None, Path(tmp) / "w", "base")
            funcs = testmut.eligible_functions(o, ["test_m.py"], base)
            self.assertEqual({f["name"] for f in funcs}, {"test_ints", "test_strings"})
            mut = testmut.make_mutants(funcs, 12, 5)
            texts, ok = testmut.build_mutated_sources(o, mut)
            self.assertEqual(len(ok), len(mut))
            compile(texts["test_m.py"], "t", "exec")
            self.assertIn("def test_ints(self)", texts["test_m.py"])        # the original is still there
            self.assertIn("def test_ints__gkm", texts["test_m.py"])
            # the same seed gives the same mutants
            self.assertEqual([m["rep"] for m in mut], [m["rep"] for m in testmut.make_mutants(funcs, 12, 5)])


class TestMutEndToEnd(unittest.TestCase):
    def test_bool_int_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g, p = G.make(tmp, "o", G.ORIG), G.make(tmp, "g", G.GOLD), G.make(tmp, "p", G.GOOD)
            res = testmut.analyze(o, g, ["m.py"], [], "unittest", ["test_m.py"], {"good": p}, Path(tmp) / "w",
                                  seed=3, n_draws=40, n_mutants=3)
            self.assertTrue(res["eligible"], res)
            self.assertGreater(res["bug_trigger_rate"], 0)                      # mutated literals reach the bug
            self.assertGreater(res["patches"]["good"]["help"], 0)
            self.assertEqual(res["patches"]["good"]["hurt"], 0)
            self.assertTrue(any(m["hurt"] > 0 for m in res["mutants"]))          # a wrong patch is caught
            self.assertTrue(res["checks"]["all_four"], res["checks"])

    def test_wrong_patch_is_flagged(self):
        bad = "def is_int(x):\n    return False\n\n\ndef double(x):\n    raise TypeError('no')\n"
        with tempfile.TemporaryDirectory() as tmp:
            o, g, p = G.make(tmp, "o", G.ORIG), G.make(tmp, "g", G.GOLD), G.make(tmp, "p", bad)
            res = testmut.analyze(o, g, ["m.py"], [], "unittest", ["test_m.py"], {"bad": p}, Path(tmp) / "w",
                                  seed=3, n_draws=40, n_mutants=2)
            self.assertGreater(res["patches"]["bad"]["hurt"], 0)
            self.assertFalse(res["checks"]["b_no_regression_for_known_good_patch"])


if __name__ == "__main__":
    unittest.main()
