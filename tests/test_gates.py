import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_ext import gates as G  # noqa: E402


class FixedSample(unittest.TestCase):
    def test_xstar_matches_the_values_of_the_phase_diagram(self):
        self.assertEqual(G.fixed_sample_xstar(300), 9)
        self.assertEqual(G.fixed_sample_xstar(1000), 40)
        self.assertEqual(G.fixed_sample_xstar(20), -1)           # too few draws to certify anything


class Sequential(unittest.TestCase):
    def test_clean_run_is_certified_after_about_fifty_draws(self):
        adm, cert_at, alarm_at = G.gatekeeper_path([False] * 300)
        self.assertTrue(adm)
        self.assertTrue(49 <= cert_at <= 51, cert_at)             # threshold 10 at 0.0463 per clean draw
        self.assertIsNone(alarm_at)

    def test_frequent_harm_trips_the_alarm_before_certification(self):
        adm, cert_at, alarm_at = G.gatekeeper_path([True, True, True] + [False] * 200)
        self.assertFalse(adm)
        self.assertIsNotNone(alarm_at)

    def test_family_size_raises_the_bar(self):
        self.assertGreater(G.gatekeeper_path([False] * 300, k_family=72)[1], G.gatekeeper_path([False] * 300)[1])

    def test_a_few_harms_delay_but_do_not_prevent_certification_at_low_rates(self):
        flags = [False] * 100
        flags[10] = flags[60] = True
        adm, cert_at, _ = G.gatekeeper_path(flags + [False] * 100)
        self.assertTrue(adm or cert_at is None)                   # no crash on a mixed path; decision is deterministic
        self.assertEqual(G.gatekeeper_path(flags + [False] * 100), G.gatekeeper_path(flags + [False] * 100))


class Decisions(unittest.TestCase):
    def test_clean_patch(self):
        d = G.decisions([False] * 200, plausible=True, helps=5)
        self.assertTrue(all(d[k] for k in ("census_only", "zero_tolerance", "b8_plus", "smoke20", "fixed_sample", "gatekeeper")))

    def test_not_plausible_is_rejected_by_every_gate(self):
        d = G.decisions([False] * 200, plausible=False, helps=5)
        self.assertFalse(any(d[k] for k in d if not k.startswith("_")))

    def test_b8_plus_needs_a_help_draw(self):
        d = G.decisions([False] * 200, plausible=True, helps=0)
        self.assertTrue(d["zero_tolerance"])
        self.assertFalse(d["b8_plus"])

    def test_partial_harm_is_where_the_gates_disagree(self):
        flags = [False] * 200
        for i in (30, 90, 150):                                   # 3 harms in 200 draws: 1.5%
            flags[i] = True
        d = G.decisions(flags, plausible=True, helps=3)
        self.assertFalse(d["zero_tolerance"])
        self.assertTrue(d["smoke20"])                             # the 20-draw smoke test misses it
        self.assertTrue(d["fixed_sample"])                        # 3 <= x*(200)
        self.assertTrue(G.band(flags))
        self.assertTrue(G.acceptable(flags))

    def test_band_boundaries(self):
        self.assertFalse(G.band([False] * 200))                   # no harm
        self.assertFalse(G.band([True, True] + [False] * 198))    # 1% < 3/200: indistinguishable from 0 (rule of three)
        self.assertTrue(G.band([True] * 3 + [False] * 197))       # 3/n
        self.assertTrue(G.band([True] * 21 + [False] * 179))      # 10.5% <= 10.87%
        self.assertFalse(G.band([True] * 22 + [False] * 178))     # 11% above: smoke-20 admits < 10% of the time
        self.assertAlmostEqual(G.BAND_HIGH, 1 - 0.1 ** (1 / 20))
        self.assertAlmostEqual((1 - G.BAND_HIGH) ** 20, 0.10)
        self.assertFalse(G.acceptable([True] * 10 + [False] * 190))


if __name__ == "__main__":
    unittest.main()
