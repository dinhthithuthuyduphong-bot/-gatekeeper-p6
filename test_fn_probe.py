import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
from gatekeeper_ext import fn_inputs as FI  # noqa: E402
import fn_probe as P  # noqa: E402
import test_golddiff as G  # noqa: E402

ENV = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONHASHSEED="0")


def make(tmp, name, files):
    d = Path(tmp) / name
    d.mkdir()
    for rel, text in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text)
    return d


class Inputs(unittest.TestCase):
    def test_same_seed_same_inputs_and_exact_round_trip(self):
        def f(a: int, b: str = "x", *, c: float = 1.0, d: list = None):
            return a
        c1, _ = FI.generate(f, 50, 7)
        c2, _ = FI.generate(f, 50, 7)
        self.assertEqual(FI.dumps_calls(c1), FI.dumps_calls(c2))
        back = FI.loads_calls(FI.dumps_calls(c1))
        self.assertEqual(FI.dumps_calls(back), FI.dumps_calls(c1))
        self.assertTrue(all(isinstance(a[0], int) for a, kw in c1))                # the annotation is honoured
        self.assertNotEqual(FI.dumps_calls(FI.generate(f, 50, 8)[0]), FI.dumps_calls(c1))

    def test_special_values_survive_encoding(self):
        x = [float("nan"), float("-inf"), b"\x00", (1, "a"), {"k": 2}]
        y = FI.decode(json.loads(json.dumps(FI.encode(x))))
        self.assertTrue(y[0] != y[0] and y[1] == float("-inf") and y[2] == b"\x00" and y[3] == (1, "a") and y[4] == {"k": 2})


class Probe(unittest.TestCase):
    def test_the_bool_int_fix_is_seen_by_direct_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g = G.make(tmp, "o", G.ORIG), G.make(tmp, "g", G.GOLD)
            r = P.probe_roots(sys.executable, o, g, ["m.py"], [], Path(tmp), n=150, env=ENV)
        self.assertEqual(r["verdict"], "usable", r)
        f = next(x for x in r["functions"] if x["qualname"] == "is_int")
        self.assertGreater(f["divergent"], 0)
        self.assertEqual(f["stable"], 150)

    def test_a_class_method_and_an_unbuildable_class(self):
        orig = "class A:\n    def f(self, x: int):\n        return x\n\n\nclass B:\n    def __init__(self, need):\n        pass\n\n    def g(self, x: int):\n        return x\n"
        gold = orig.replace("return x\n\n\nclass B", "return abs(x)\n\n\nclass B").replace("    def g(self, x: int):\n        return x", "    def g(self, x: int):\n        return -x")
        with tempfile.TemporaryDirectory() as tmp:
            o, g = make(tmp, "o", {"k.py": orig}), make(tmp, "g", {"k.py": gold})
            r = P.probe_roots(sys.executable, o, g, ["k.py"], [], Path(tmp), n=120, env=ENV)
        by = {f["qualname"]: f for f in r["functions"]}
        self.assertTrue(by["A.f"]["usable"], by["A.f"])                              # abs differs on negative ints
        self.assertIn("cannot be built without arguments", by["B.g"]["why"])
        self.assertEqual(r["verdict"], "usable")

    def test_unstable_outcomes_are_excluded_and_reported(self):
        orig = "import random\n\n\ndef f(x: int):\n    return random.random()\n"
        gold = orig.replace("random.random()", "random.random() + 1")
        with tempfile.TemporaryDirectory() as tmp:
            o, g = make(tmp, "o", {"k.py": orig}), make(tmp, "g", {"k.py": gold})
            r = P.probe_roots(sys.executable, o, g, ["k.py"], [], Path(tmp), n=120, env=ENV)
        self.assertEqual(r["verdict"], "unstable outcomes", r)

    def test_identical_behaviour_on_generated_inputs(self):
        orig = "def f(x: int):\n    return x + 0\n"
        gold = "def f(x: int):\n    return x\n"
        with tempfile.TemporaryDirectory() as tmp:
            o, g = make(tmp, "o", {"k.py": orig}), make(tmp, "g", {"k.py": gold})
            r = P.probe_roots(sys.executable, o, g, ["k.py"], [], Path(tmp), n=120, env=ENV)
        self.assertEqual(r["verdict"], "the original never differs from the fix on generated inputs")

    def test_a_module_that_cannot_be_imported(self):
        orig = "import not_a_real_module_xyz\n\n\ndef f(x: int):\n    return x\n"
        gold = orig.replace("return x", "return -x")
        with tempfile.TemporaryDirectory() as tmp:
            o, g = make(tmp, "o", {"k.py": orig}), make(tmp, "g", {"k.py": gold})
            r = P.probe_roots(sys.executable, o, g, ["k.py"], [], Path(tmp), n=120, env=ENV)
        self.assertEqual(r["verdict"], "no edited function could be imported or called")

    def test_a_call_that_never_returns_is_a_timeout_not_a_hang(self):
        orig = "def f(x: int):\n    while x == 0:\n        pass\n    return x\n"
        gold = orig.replace("return x", "return -x")
        with tempfile.TemporaryDirectory() as tmp:
            o, g = make(tmp, "o", {"k.py": orig}), make(tmp, "g", {"k.py": gold})
            r = P.probe_roots(sys.executable, o, g, ["k.py"], [], Path(tmp), n=110, env=ENV)
        f = r["functions"][0]
        self.assertLess(f["stable"], 110)                                            # the x == 0 inputs timed out and were excluded
        self.assertTrue(f["divergent"] > 0)


if __name__ == "__main__":
    unittest.main()
