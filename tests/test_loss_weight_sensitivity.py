import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import loss_weight_sensitivity as L  # noqa: E402


class LossWeightTest(unittest.TestCase):
    def test_one_test_loss_ignores_the_penalty(self):
        for lam in (0, 0.2, 0.5, 1, 2, 5, 100):
            for pw in (True, False):
                for pt in (True, False):
                    z = L.loss_one_test(pt, pw and not pt, lam) - L.loss_one_test(pw, False, lam)
                    self.assertEqual(z, (0.0 if pt else 1.0) - (0.0 if pw else 1.0))

    def test_recorded_draws_unchanged(self):
        a = L.part_a([0, 0.5, 5])
        self.assertGreater(a["draws"], 1000)
        self.assertTrue(all(v == 0 for v in a["draws_with_changed_z_per_lambda"].values()))


if __name__ == "__main__":
    unittest.main()
