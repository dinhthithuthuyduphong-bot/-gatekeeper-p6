"""Failure-mode tests prepared for GitHub; synthetic fixtures are not study data."""
import copy
from pathlib import Path
import unittest

from next_evidence.common import baseline_status
from next_evidence.source import is_test, production


class NextEvidenceContracts(unittest.TestCase):
    def rows(self):
        row={"returncode":0,"phase_errors":[],"call_failures":[],"inventory":["test_x"],
             "phase_signature":[["test_x","call","passed",None]],"passed_calls":10}
        return [copy.deepcopy(row) for _ in range(3)]

    def test_exit_failure_without_phase_failure_is_not_success(self):
        rows=self.rows();rows[1]["returncode"]=1
        self.assertEqual(baseline_status(rows),"INCONSISTENT_EXIT_AND_PHASES")

    def test_setup_failure_is_not_a_functional_regression(self):
        rows=self.rows();rows[0].update(returncode=1,phase_errors=["test_x"])
        self.assertEqual(baseline_status(rows),"SETUP_OR_TEARDOWN_BLOCKED")

    def test_missing_attempt_or_collection_error_cannot_pass(self):
        rows=self.rows()
        self.assertEqual(baseline_status(rows[:2]),"INCOMPLETE")
        rows[2]["returncode"]=2
        self.assertEqual(baseline_status(rows),"ENV_OR_COLLECTION_BLOCKED")

    def test_changed_test_inventory_is_not_stable(self):
        rows=self.rows();rows[2]["inventory"].append("test_extra")
        self.assertEqual(baseline_status(rows),"BASELINE_UNSTABLE")

    def test_green_baseline_does_not_claim_a_validated_oracle(self):
        self.assertEqual(baseline_status(self.rows()),"BASELINE_STABLE_ORACLE_REVIEW_PENDING")

    def test_root_examples_and_test_suffixes_are_not_production(self):
        for path in ("example.py","examples/demo.py","pkg/unit_test.py","tests/check.py"):
            self.assertFalse(production(Path(path)),path)
        self.assertTrue(is_test(Path("pkg/unit_test.py")))
        self.assertTrue(production(Path("pkg/provider.py")))


if __name__=="__main__":unittest.main()
