import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import fn_draws as D  # noqa: E402
from gatekeeper_ext import gates  # noqa: E402

ENV = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONHASHSEED="0")
ORIG = "def clip(x: int, hi: int = 10):\n    return x if x < hi else hi\n"
GOLD = "def clip(x: int, hi: int = 10):\n    if x < 0:\n        return 0\n    return x if x < hi else hi\n"
GEN = "def make_inputs(rng, n):\n    return [(None, [rng.randint(-20, 20)], {}) for _ in range(n)]\n"


def make(tmp, name, text):
    d = Path(tmp) / name
    d.mkdir()
    (d / "k.py").write_text(text)
    return d


class FnDraws(unittest.TestCase):
    def base(self, tmp):
        o, g = make(tmp, "orig", ORIG), make(tmp, "gold", GOLD)
        fn = {"file": "k.py", "qualname": "clip", "generator_code": GEN}
        b, why = D.prepare_fn_base(sys.executable, o, g, [], fn, Path(tmp) / "w", n=150, seed=3, env=ENV)
        self.assertIsNone(why)
        return o, b

    def test_two_sources_one_order_and_the_bug_is_triggered(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, b = self.base(tmp)
        self.assertEqual(set(b["info"]["inputs_by_source"]), {"G0", "G2"})
        self.assertEqual(b["info"]["stable_inputs"], len(b["order"]))
        self.assertGreater(b["info"]["bug_trigger_inputs"], 0)
        self.assertEqual({s for s, _ in b["order"]}, {"G0", "G2"})              # interleaved

    def test_the_fix_itself_has_no_harm_and_full_help(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, b = self.base(tmp)
            sc, _ = D.score_fn_patch(sys.executable, b, o, {"k.py": GOLD}, [], Path(tmp) / "w", "gold_itself", env=ENV)
        self.assertEqual((sum(sc["harm"]), sc["divergent"]), (0, 0))
        self.assertEqual(sc["help"], b["info"]["bug_trigger_inputs"])

    def test_a_patch_with_a_partial_regression_is_measured_as_a_rate(self):
        # fixes negatives, but breaks the upper clip for x == hi (a narrow region of the inputs)
        partial = "def clip(x: int, hi: int = 10):\n    if x < 0:\n        return 0\n    return x if x <= hi else hi + 0 if x != hi else -1\n"
        partial = "def clip(x: int, hi: int = 10):\n    if x < 0:\n        return 0\n    if x == hi:\n        return -1\n    return x if x < hi else hi\n"
        with tempfile.TemporaryDirectory() as tmp:
            o, b = self.base(tmp)
            sc, _ = D.score_fn_patch(sys.executable, b, o, {"k.py": partial}, [], Path(tmp) / "w", "partial", env=ENV)
        rate = gates.h_hat(sc["harm"])
        self.assertGreater(sum(sc["harm"]), 0)
        self.assertLess(rate, 0.2)                                                # a rate, not an all-or-nothing verdict
        d = gates.decisions(sc["harm"], True, sc["help"])
        self.assertFalse(d["zero_tolerance"])


if __name__ == "__main__":
    unittest.main()
