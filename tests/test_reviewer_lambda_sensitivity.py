"""Analytic sensitivity tests, no simulated/observed target outcomes."""
import math
import unittest
from tools.reviewer_lambda_sensitivity import row


class LambdaSensitivityTests(unittest.TestCase):
    def test_boundary_null_expected_wealth_multiplier_one(self):
        eta, frac = 0.05, 0.9
        lam = row(eta, frac, eta, 0.1)["lambda"]
        multiplier = (1 - eta) * (1 + lam * eta) + eta * (1 - lam * (1 - eta))
        self.assertAlmostEqual(multiplier, 1.0)

    def test_no_harm_crossing_finite(self):
        a = row(0.05, 0.9, 0.0, 0.1)
        self.assertGreater(a["no_harm_draws_to_1_over_alpha"], 0)
        self.assertTrue(math.isfinite(a["expected_log_growth"]))

    def test_invalid_parameters_fail_closed(self):
        with self.assertRaises(ValueError):
            row(0.05, 1.0, 0.0, 0.1)


if __name__ == "__main__":
    unittest.main()
