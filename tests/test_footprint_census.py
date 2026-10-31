import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import footprint_census as F  # noqa: E402


class FootprintCensusTest(unittest.TestCase):
    def test_test_files_are_excluded(self):
        self.assertTrue(F.is_test("pkg/tests/x.py"))
        self.assertTrue(F.is_test("test_a.py"))
        self.assertTrue(F.is_test("pkg/a_test.py"))
        self.assertFalse(F.is_test("pkg/testing_utils.py"))

    def test_both_families_bind_on_a_shared_function(self):
        src = "def f(x):\n    if isinstance(x, int) and x == None:\n        return 1\n"
        b = {s.function for s in F.Skill.load(F.SKILLS["bool"]).transform().apply(src, single_site=False).sites}
        n = {s.function for s in F.Skill.load(F.SKILLS["none"]).transform().apply(src, single_site=False).sites}
        self.assertEqual(b & n, {"f"})


if __name__ == "__main__":
    unittest.main()
