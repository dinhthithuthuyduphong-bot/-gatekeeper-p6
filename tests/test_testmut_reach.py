import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from gatekeeper_ext import reach, testmut  # noqa: E402
import test_golddiff as G  # noqa: E402

ORIG2 = G.ORIG + "\n\ndef unrelated():\n    return 7\n"
GOLD2 = G.GOLD + "\n\ndef unrelated():\n    return 7\n"
GOOD2 = G.GOOD + "\n\ndef unrelated():\n    return 7\n"
TEST2 = G.TEST + '''
    def test_unrelated(self):
        self.assertEqual(m.unrelated(), 7)
        self.assertEqual(m.unrelated() + 1, 8)
'''


def make(tmp, name, src):
    d = Path(tmp) / name
    d.mkdir()
    (d / "m.py").write_text(src)
    (d / "test_m.py").write_text(TEST2)
    return d


class ReachUnits(unittest.TestCase):
    def test_nodeid_to_junit_key(self):
        self.assertEqual(reach.key_from_nodeid("tests/core/test_x.py::TestA::test_b[1-2]"), ("tests.core.test_x.TestA", "test_b"))
        self.assertEqual(reach.key_from_nodeid("cerberus/tests/tests.py::test_c"), ("cerberus.tests.tests", "test_c"))

    def test_tracker_marks_only_tests_that_enter_the_target(self):
        def target():
            return 1

        def other():
            return 2
        tr = reach.ReachTracker({(str(Path(__file__).resolve()), target.__code__.co_firstlineno)})
        tr.start(("m", "t_hit"))
        target()
        tr.stop()
        tr.start(("m", "t_miss"))
        other()
        tr.stop()
        self.assertEqual(tr.reached, {("m", "t_hit")})


class ReachEndToEnd(unittest.TestCase):
    def test_unrelated_test_is_outside_the_sampling_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g, p = make(tmp, "o", ORIG2), make(tmp, "g", GOLD2), make(tmp, "p", GOOD2)
            res = testmut.analyze(o, g, ["m.py"], [], "unittest", ["test_m.py"], {"good": p}, Path(tmp) / "w",
                                  seed=3, n_draws=40, n_mutants=3)
            self.assertTrue(res["eligible"], res)
            self.assertEqual(res["harness_version"], "tm-dev-v4-reach")
            self.assertEqual(res["eligible_test_functions_unfiltered"], 3)
            self.assertEqual(res["eligible_test_functions"], 2)             # test_unrelated never enters is_int
            self.assertTrue(res["checks"]["all_four"], res["checks"])
            cat = (Path(tmp) / "w" / "mutation_catalog.json").read_text()
            self.assertNotIn("test_unrelated", cat)


if __name__ == "__main__":
    unittest.main()
