import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import rare_harm_study as U  # noqa: E402


class RareHarmTest(unittest.TestCase):
    def test_split_is_seeded_and_keeps_counts(self):
        p = {"sha": "abc", "n": 400, "k": 30}
        g1, r1 = U.split(p)
        g2, r2 = U.split(p)
        self.assertEqual((g1, r1), (g2, r2))
        self.assertEqual(sum(g1) + sum(r1), 30)
        self.assertEqual(len(g1), 200)


if __name__ == "__main__":
    unittest.main()
