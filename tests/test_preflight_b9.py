"""Zero-cost preflight regression tests. No cloud credentials required."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from tools import preflight_b9


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        for folder in ("study_d", "study_f", "pre_b9"):
            (root / folder).mkdir()
        self.root = root
        self.write("study_d/b9_config.json", {
            "status": "FROZEN", "not_before_utc": "2026-10-31T00:00:00Z",
            "models": [{"name": "deepseek-flash",
                        "prices_usd_per_mtok": {"input": 0.3, "output": 1.2}}],
            "instances": ["D1_py_ecc"]})
        self.write("study_f/b9_config_f.json", {
            "status": "FROZEN", "not_before_utc": "2026-10-31T00:00:00Z",
            "models": [{"name": "vertex-gemini-flash",
                        "prices_usd_per_mtok": {"input": 0.75, "output": 3.75}}],
            "instances": ["D1_py_ecc"]})
        self.write("study_f/config_study_f.json", {
            "status": "FROZEN", "frozen_on": "2026-10-21T16:06:53Z",
            "cells": ["D1_py_ecc"],
            "b9_configs": {"deepseek-flash": "study_d/b9_config.json",
                           "vertex-gemini-flash": "study_f/b9_config_f.json"}})
        self.write("pre_b9/RELEASE_GATE.json", {"status": "HOLD", "approved_for": None})
        self.patch_root = patch.object(preflight_b9, "ROOT", root)
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)
        self.now = datetime(2026, 11, 1, tzinfo=timezone.utc)

    def write(self, path, obj):
        (self.root / path).write_text(json.dumps(obj), encoding="utf-8")

    def validate(self, mode="record", config="study_d/b9_config.json",
                 model="deepseek-flash", now=None):
        return preflight_b9.validate(config, "D1_py_ecc", model, mode,
                                     now=now or self.now, verify_freezes=False)

    def test_paid_is_on_hold_even_after_date(self):
        with self.assertRaisesRegex(ValueError, "PRE_B9_REVIEW_HOLD"):
            self.validate()

    def test_replay_allowed_without_paid_signoff(self):
        self.assertIn("REPLAY_PREFLIGHT_OK", self.validate("replay"))

    def test_record_refused_before_oct31_even_if_go(self):
        self.write("pre_b9/RELEASE_GATE.json",
                   {"status": "GO", "approved_for": "study-f-v1"})
        with self.assertRaisesRegex(ValueError, "forbidden before"):
            self.validate(now=datetime(2026, 10, 22, tzinfo=timezone.utc))

    def test_reject_unknown_config_path(self):
        with self.assertRaisesRegex(ValueError, "approved repository paths"):
            self.validate(config="../outside.json")

    def test_reject_wrong_model_config_mapping(self):
        with self.assertRaisesRegex(ValueError, "does not map"):
            self.validate(config="study_f/b9_config_f.json")

    def test_reject_unfrozen(self):
        cfg = json.loads((self.root / "study_d/b9_config.json").read_text())
        cfg["status"] = "DRAFT"
        self.write("study_d/b9_config.json", cfg)
        with self.assertRaisesRegex(ValueError, "FROZEN"):
            self.validate()

    def test_record_go_only_with_explicit_signoff(self):
        self.write("pre_b9/RELEASE_GATE.json",
                   {"status": "GO", "approved_for": "study-f-v1"})
        self.assertIn("RECORD_PREFLIGHT_OK", self.validate())

    def test_no_implicit_model_substitution(self):
        with self.assertRaisesRegex(ValueError, "does not map"):
            self.validate(model="vertex-gemini-flash")


if __name__ == "__main__":
    unittest.main()
