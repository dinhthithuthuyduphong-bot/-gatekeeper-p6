import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from gatekeeper_lite.eprocess import BettingEProcess  # noqa: E402
import theory_checks as TC  # noqa: E402


class TheoryChecksTest(unittest.TestCase):
    def test_fast_betting_equals_repo_eprocess(self):
        rng = random.Random(1)
        for theta in (0.05, 0.1, 0.3):
            a, b = BettingEProcess(theta=theta), TC.FastBetting(theta)
            for _ in range(200):
                z = rng.uniform(-1, 1)
                self.assertAlmostEqual(a.update(z), b.update(z), delta=1e-9 * max(1.0, a.value))

    def test_corrected_statements_hold(self):
        self.assertTrue(TC.check_tv()["held"])
        self.assertTrue(TC.check_composition()["held"])
        self.assertTrue(TC.check_ledger()["held"])
        self.assertTrue(TC.check_pairing(3, n=50000)["held"])
        self.assertFalse(TC.check_corollary8()["held"])         # the draft's numbers are inconsistent

    def test_shared_budget_inflates_familywise_error(self):
        c1, c2 = TC.check_alpha(reps=150, cells=10, n=300, seed=7)
        self.assertLessEqual(c1["rate"], 0.1)
        self.assertGreater(c2["familywise_shared"], 0.1)
        self.assertLessEqual(c2["familywise_split"], 0.1)

    def test_harm_certificate(self):
        r = TC.check_harm_certificate(reps=300, n=300, seed=7)
        self.assertTrue(r["held"])
        self.assertAlmostEqual(r["growth_threshold_over_eta"], 0.394, places=2)

    def test_readmission_needs_the_ledger(self):
        r = TC.check_readmission(reps=150, epochs=10, n=300, seed=7)
        self.assertGreater(r["error_full_alpha_each_epoch"], 0.1)
        self.assertLessEqual(r["error_ledger"], 0.1)


if __name__ == "__main__":
    unittest.main()
