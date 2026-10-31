import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import conformance as C  # noqa: E402
from gatekeeper_ext.ledger import LibraryLedger  # noqa: E402


class ConformanceTest(unittest.TestCase):
    def test_cited_studies_have_the_full_guarantee(self):
        for p in ("study_d/config_study_d.json", "study_e/config_study_e.json", "study_g/config_study_g.json",
                  "study_h/config_study_h.json"):
            r = C.check_config(json.loads((ROOT / p).read_text()))
            self.assertEqual(r["guarantee"], C.FULL, (p, r))

    def test_options_are_labelled(self):
        self.assertEqual(C.check_config({"task_priority": ["x"]})["guarantee"], C.NONE)
        self.assertEqual(C.check_config({"task_filter": "reach_baseline"})["guarantee"], C.SIGN_ONLY)
        self.assertEqual(C.check_config({"evidence": "discordant_sign"})["guarantee"], C.SIGN_ONLY)
        self.assertEqual(C.check_config({"multiplicity": {"method": "e-BH"}})["guarantee"], C.FDR)
        self.assertEqual(C.check_config({"alpha_total": 0.1, "cells": {"a": 0.08, "b": 0.08}})["guarantee"], C.NONE)

    def test_every_config_in_the_repository_is_labelled(self):
        for p in sorted(ROOT.glob("*/config*.json")):
            r = C.check_config(json.loads(p.read_text()))
            self.assertIn(r["guarantee"], (C.FULL, C.SIGN_ONLY, C.FDR, C.NONE))


class LibraryLedgerTest(unittest.TestCase):
    def test_shares_are_fixed_by_identity_and_growth_does_not_change_them(self):
        led = LibraryLedger(0.1, capacity=10, skills=["a", "b"])
        before = (led.share({"a"}), led.share({"a", "b"}), led.share({"a", "b"}, 2))
        led.register("c")
        self.assertEqual(before, (led.share({"a"}), led.share({"a", "b"}), led.share({"a", "b"}, 2)))
        self.assertAlmostEqual(led.share({"a"}), 0.1 * 0.5 / 10 * 6 / math.pi ** 2)   # epoch 0 factor 6/pi^2

    def test_no_recycling_unknown_skills_and_capacity(self):
        led = LibraryLedger(0.1, capacity=2, skills=["a", "b"])
        led.draw({"a", "b"}, 0)
        with self.assertRaises(ValueError):
            led.draw({"b", "a"}, 0)
        with self.assertRaises(KeyError):
            led.share({"z"})
        with self.assertRaises(ValueError):
            led.register("c")

    def test_total_at_most_alpha(self):
        for n in (1, 2, 5, 12, 50):
            self.assertLessEqual(LibraryLedger(0.1, n).total_bound(), 0.1 + 1e-12)


if __name__ == "__main__":
    unittest.main()
