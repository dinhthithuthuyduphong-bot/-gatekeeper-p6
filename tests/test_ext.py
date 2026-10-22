import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite import transforms as T  # noqa: E402


class NoneIdentitySkillTests(unittest.TestCase):
    def test_rewrite_and_semantics(self):
        from gatekeeper_ext.none_identity import NoneIdentity, register
        src = ("def f(x, y):\n    if x == None:\n        return 1\n    if None != y:\n        return 2\n"
               "    if x == None == y:\n        return 3\n    return 0\n")
        res = NoneIdentity().apply(src, single_site=False)
        self.assertIn("if x is None:", res.source)
        self.assertIn("if y is not None:", res.source)
        self.assertIn("x == None == y", res.source)          # chained comparison left alone
        self.assertEqual(len(res.sites), 2)
        register()
        self.assertEqual(T.make("none_identity").name, "none_identity")

    def test_behaviour_changes_only_for_overridden_eq(self):
        class Expr:                                           # stands for an ORM column expression
            def __eq__(self, other):
                return "IS NULL" if other is None else False
        e = Expr()
        self.assertEqual(e == None, "IS NULL")               # noqa: E711  intended semantics
        self.assertIs(e is None, False)                      # what the rewrite would produce
        self.assertEqual((5 == None), (5 is None))           # noqa: E711  ordinary objects: unchanged
