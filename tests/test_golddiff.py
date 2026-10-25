import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import golddiff, golddiff_oracle, mutants  # noqa: E402

ORIG = '''def is_int(x):
    return isinstance(x, int)


def double(x):
    if is_int(x):
        return x * 2
    raise TypeError("not an int")
'''
GOLD = ORIG.replace("return isinstance(x, int)\n", "return isinstance(x, int) and not isinstance(x, bool)\n")
GOOD = ORIG.replace("return isinstance(x, int)\n", "return type(x) is int\n")
TEST = '''import unittest
import m


class T(unittest.TestCase):
    def test_ints(self):
        self.assertTrue(m.is_int(4))
        self.assertTrue(m.is_int(-1))
        self.assertEqual(m.double(3), 6)

    def test_strings(self):
        self.assertFalse(m.is_int("a"))
        self.assertFalse(m.is_int(2.5))
        self.assertFalse(m.is_int(None))
        with self.assertRaises(TypeError):
            m.double("a")
'''


def make(tmp, name, source):
    d = Path(tmp) / name
    d.mkdir()
    (d / "m.py").write_text(source)
    (d / "test_m.py").write_text(TEST)
    return d


class GoldDiffUnits(unittest.TestCase):
    def test_edited_functions_and_module_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g = make(tmp, "o", ORIG), make(tmp, "g", GOLD)
            ed = golddiff.edited_functions(o, g, ["m.py"])
            self.assertEqual([e["qualname"] for e in ed], ["is_int"])      # double() is untouched
        self.assertEqual(golddiff.module_name("src/pkg/mod.py", ["src"]), "pkg.mod")
        self.assertEqual(golddiff.module_name("pkg/__init__.py", []), "pkg")

    def test_mutants_are_deterministic_and_compile(self):
        a = mutants.mutants(GOLD, ["is_int"], 5)
        b = mutants.mutants(GOLD, ["is_int"], 5)
        self.assertEqual(a, b)
        self.assertTrue(a)
        for desc, src in a:
            compile(src, "<m>", "exec")
        self.assertIn("or not isinstance", a[0][1])
        src2 = "def f(x, y):\n    if x == y:\n        return True\n    return x < y\n"
        ops = [d.split(" at ")[0] for d, _ in mutants.mutants(src2, ["f"], 9)]
        self.assertEqual(ops, ["cmp_flip", "if_negate", "bool_const", "cmp_flip"])

    def test_canon_distinguishes_bool_from_int(self):
        c = golddiff_oracle.canon
        self.assertNotEqual(c(True), c(1))
        self.assertEqual(c({"b": 1, "a": 2}), c({"a": 2, "b": 1}))
        self.assertEqual(c(object()).split(":")[0], "object")


class GoldDiffEndToEnd(unittest.TestCase):
    def test_gate_g1_on_a_bool_int_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g, p = make(tmp, "o", ORIG), make(tmp, "g", GOLD), make(tmp, "p", GOOD)
            res = golddiff.analyze(o, g, ["m.py"], [], "unittest", ["discover", "-s", ".", "-p", "test_m.py"],
                                   Path(tmp) / "work", seed=7, patches={"good": p}, n_draws=120, n_mutants=3)
        self.assertTrue(res["eligible"], res)
        self.assertTrue(res["g1"]["pass"], json.dumps(res, indent=1)[:1500])
        self.assertGreater(res["patches"]["good"]["help"], 0)         # bool draws reach the original bug
        self.assertEqual(res["patches"]["good"]["hurt"], 0)
        self.assertTrue(any(m["hurt"] > 0 for m in res["mutants"]))   # positive control: a wrong patch is caught

    def test_identical_original_and_gold_is_ineligible(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g = make(tmp, "o", ORIG), make(tmp, "g", ORIG)
            res = golddiff.analyze(o, g, ["m.py"], [], "unittest", ["discover", "-s", ".", "-p", "test_m.py"],
                                   Path(tmp) / "work", seed=1, patches={})
        self.assertFalse(res["eligible"])


if __name__ == "__main__":
    unittest.main()
