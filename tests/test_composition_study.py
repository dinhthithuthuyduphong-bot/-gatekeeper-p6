import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import composition_study as S  # noqa: E402


class CompositionStudyTest(unittest.TestCase):
    def test_qualified_defs(self):
        src = "class A:\n    def f(self):\n        def g():\n            pass\n\ndef f(x):\n    pass\n"
        self.assertEqual([q for q, _, _ in S.qualified_defs(src)], ["A.f", "f"])

    def test_losses_and_interaction(self):
        o = {"outcomes": [["ok", "1"], ["ok", "2"], ["ok", "3"], ["exc", "E"]]}
        o2 = {"outcomes": [["ok", "1"], ["ok", "2"], ["ok", "X"], ["exc", "E"]]}     # input 2 unstable
        runs = {"A": {"outcomes": [["ok", "9"], ["ok", "2"], ["ok", "3"], ["exc", "E"]]},
                "B": {"outcomes": [["ok", "1"], ["ok", "2"], ["ok", "3"], ["exc", "E"]]},
                "AB": {"outcomes": [["ok", "1"], ["ok", "8"], ["ok", "3"], ["exc", "E"]]},
                "BA": {"outcomes": [["ok", "9"], ["ok", "2"], ["ok", "3"], ["exc", "E"]]}}
        stable, L = S.losses(o, o2, runs)
        self.assertEqual(stable, [0, 1, 3])
        self.assertEqual(L["A"], [1, 0, 0])
        r = S.interaction(L, runs, stable)
        self.assertEqual(r["emergent"], 1)        # AB differs on input 1, neither single does
        self.assertEqual(r["masking"], 1)         # A differs on input 0, AB does not
        self.assertEqual(r["order_dependent"], 2)  # AB != BA on inputs 0 and 1

    def test_variant_sources(self):
        sk = S.load_skills()
        src = "def f(x):\n    if type(x) is not int:\n        return 1\n    return 0\n"
        ab = S.variant_source(sk, "negative_type_guard", "type_eq_isinstance", src, "AB")
        ba = S.variant_source(sk, "negative_type_guard", "type_eq_isinstance", src, "BA")
        self.assertIn("not isinstance(x, int)", ab)
        self.assertIn("isinstance(x, bool)", ba)          # B first creates the site the bool guard then rewrites
        self.assertNotEqual(ab, ba)

    def test_mangled_private_method(self):
        import composition_inner as CI
        self.assertEqual(CI.mangled("Mongo", "__select"), "_Mongo__select")
        self.assertEqual(CI.mangled("_Priv", "__x"), "_Priv__x")
        self.assertEqual(CI.mangled("A", "__init__"), "__init__")

    def test_subtype_substitution(self):
        import random
        import composition_inner as CI
        rng = random.Random(1)
        vals = [CI.subst(5, rng) for _ in range(400)]
        n_bool = sum(type(v) is bool for v in vals)
        self.assertTrue(60 < n_bool < 140)                        # about 1/4
        self.assertIs(CI.subst(True, rng), True)                   # bools stay
        self.assertEqual(CI.subst("x", rng), "x")
        self.assertTrue(all(type(v) in (int, bool) for v in CI.subst([1, (2, 3), {"k": 4}], rng)[:1]))

    def test_harm_e(self):
        e, fired = S.harm_e([0] * 150)
        self.assertGreater(e, 100)
        self.assertFalse(fired)
        self.assertEqual(S.harm_e([1] * 10), (0.0, True))


if __name__ == "__main__":
    unittest.main()
