"""Read-only B6-R audit tests with synthetic fixtures."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.b6r_contract_audit import inventory


class ContractInventoryTests(unittest.TestCase):
    def test_missing_source_package_contract_is_not_misreported_as_match(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base = root / "study_d"
            (base / "skills").mkdir(parents=True)
            (base / "eval_targets" / "T1").mkdir(parents=True)
            (base / "config_study_d.json").write_text(
                json.dumps({"skill": "skills/skill.json"}), encoding="utf-8")
            (base / "skills/skill.json").write_text(
                json.dumps({"skill_id": "synthetic", "D": {"python": ">=3.10"}}),
                encoding="utf-8")
            (base / "eval_targets/T1/gk_target.json").write_text(
                json.dumps({"python": "3.12", "packages": {"pytest": "8.3"}}),
                encoding="utf-8")
            result = inventory(root)
            row = result["targets"][0]
            self.assertEqual(row["evidence_completeness"], "INCOMPLETE")
            self.assertIn("source_package_constraints", row["missing"])
            self.assertEqual(row["admission_decision"], "NOT_EVALUATED")
            self.assertFalse(row["source_provenance_verified"])


if __name__ == "__main__":
    unittest.main()
