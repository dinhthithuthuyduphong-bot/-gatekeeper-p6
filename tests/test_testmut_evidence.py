"""Regression checks for evidence integrity, not tests of scientific effectiveness."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from gatekeeper_ext.testmut_evidence import feasibility_checks, preserve_run, execute_logged, write_json
from gatekeeper_ext import testmut


class EvidenceContractTests(unittest.TestCase):
    def test_missing_outcomes_veto_otherwise_passing_diagnostics(self):
        p = {"skill": {"help": 1, "hurt": 0, "missing": 1}}
        m = [{"hurt": 1, "missing": 0}]
        self.assertFalse(feasibility_checks(p, m, True)["all_four"])
        p["skill"]["missing"] = 0
        self.assertTrue(feasibility_checks(p, m, True)["all_four"])

    def test_preserve_raw_files_but_not_disposable_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); src = root / "run"; src.mkdir()
            (src / "arm_orig").mkdir(); (src / "arm_orig" / "source.py").write_text("x=1")
            (src / "arm_signatures.json").write_text("{}")
            (src / "baseline.xml").write_text("<testsuites/>")
            preserve_run(src, root / "evidence")
            self.assertTrue((root / "evidence/arm_signatures.json").exists())
            self.assertTrue((root / "evidence/baseline.xml").exists())
            self.assertFalse((root / "evidence/arm_orig/source.py").exists())

    def test_timeout_keeps_receipt(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp) / "trial"
            with patch("gatekeeper_ext.testmut_evidence.subprocess.run", side_effect=subprocess.TimeoutExpired("stub", 1)):
                r = execute_logged(["stub"], tmp, None, prefix, 1)
            self.assertEqual(r["status"], "TIMEOUT")
            self.assertTrue(Path(str(prefix) + ".command.json").exists())

    def test_nonfunctional_runner_exit_is_rejected_even_with_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "trial.xml").write_text('<testsuites><testsuite><testcase name="x"/></testsuite></testsuites>')
            with patch("gatekeeper_ext.testmut.execute_logged", return_value={"status": "COMPLETED", "returncode": 2}):
                records, error = testmut.run_tests(root, "pytest", ["test_x.py"], [], None, root, "trial")
            self.assertIsNone(records)
            self.assertIsNotNone(error)

    def test_zero_configured_files_stops_before_any_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("gatekeeper_ext.testmut.run_tests") as run:
                r = testmut.analyze(root, root, [], [], "pytest", ["absent"], {}, root / "work", 1)
            self.assertFalse(r["eligible"])
            run.assert_not_called()

    def test_legacy_tests_py_is_in_file_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "tests").mkdir()
            (root / "tests/tests.py").write_text("def test_x(): pass")
            self.assertEqual(testmut.expand_files(root, ["tests"]), ["tests/tests.py"])

    def test_mutation_catalog_accepts_bytes_literals(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            write_json(path, {"literal": b"abc"})
            self.assertIn('616263', path.read_text())


if __name__ == "__main__":
    unittest.main()
