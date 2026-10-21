"""Non-mutating statistical contract checks for the FROZEN implementation.

These checks are mathematical smoke tests, NOT empirical validation of Study D/E
and NOT a substitute for independent theorem review or confidence sequences.
"""
import unittest

from gatekeeper_lite.eprocess import (
    BettingEProcess, HarmCertEProcess, HarmAlarmEProcess, e_holm
)


class StatisticalContractTests(unittest.TestCase):
    def test_benefit_bet_is_predictable_and_one_step_null_mean_one(self):
        p = BettingEProcess(theta=0.2)
        lam = p._bet()  # public implementation's bet before observing any sample
        self.assertGreaterEqual(lam, 0)
        self.assertLess(lam, 1 / 1.2)
        # Boundary null E[Y]=theta, Y in {-1,+1}: P(Y=1)=0.6
        factor_good = 1 + lam * (1 - 0.2)
        factor_bad = 1 + lam * (-1 - 0.2)
        self.assertGreaterEqual(factor_bad, 0)
        self.assertAlmostEqual(0.6 * factor_good + 0.4 * factor_bad, 1.0)

    def test_harm_certificate_boundary_null_mean_one(self):
        p = HarmCertEProcess(eta=0.05)
        lam = p.lam
        self.assertGreaterEqual(1 - lam * (1 - 0.05), 0)
        expected = 0.95 * (1 + lam * 0.05) + 0.05 * (1 + lam * (0.05 - 1))
        self.assertAlmostEqual(expected, 1.0)

    def test_harm_alarm_boundary_null_mean_one(self):
        p = HarmAlarmEProcess(eta_alarm=0.05)
        mu = p.mu
        expected = 0.95 * (1 - mu * 0.05) + 0.05 * (1 + mu * 0.95)
        self.assertAlmostEqual(expected, 1.0)

    def test_e_holm_inactive_cells_can_reduce_power(self):
        # Illustrative synthetic e-values, NOT real study results.
        self.assertEqual(e_holm({"active": 30}, 0.1), ["active"])
        self.assertNotIn("active", e_holm({"active": 30, "inactive1": 0,
                                           "inactive2": 0, "inactive3": 0}, 0.1))

    def test_e_holm_requires_all_intersections(self):
        # With 2 hypotheses, E=30 passes singleton (>=10)
        # and intersection mean (30+0)/2=15 passes.
        self.assertIn("a", e_holm({"a": 30, "b": 0}, 0.1))
        self.assertNotIn("b", e_holm({"a": 30, "b": 0}, 0.1))


if __name__ == "__main__":
    unittest.main()
