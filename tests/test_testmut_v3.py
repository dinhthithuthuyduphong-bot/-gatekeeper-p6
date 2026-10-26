import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import testmut  # noqa: E402

D5_TAIL = "FAILED x - AssertionError\n!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 25 failures !!!!!!!!!!!!!!!!!!!!!!!!!!\n25 failed, 49 deselected in 0.29s"
D2_TAIL = "!!!!!!!! stopping after 2 failures !!!!!!!!\n2 failed, 1 passed, 146 deselected, 14 warnings in 0.32s"


class V3MeasurementFixes(unittest.TestCase):
    def test_truncation_seen_in_d5_and_d2_logs_is_detected(self):
        self.assertTrue(testmut.was_truncated(D5_TAIL))
        self.assertTrue(testmut.was_truncated(D2_TAIL))
        self.assertFalse(testmut.was_truncated("2 failed, 198 passed in 1.2s"))
        self.assertFalse(testmut.was_truncated(""))

    def test_pytest_command_overrides_repository_maxfail(self):
        cmd = testmut.pytest_command("/x/o.xml", "__gkm", ["tests/test_types.py"])
        self.assertIn("--maxfail=0", cmd)
        self.assertLess(cmd.index("--maxfail=0"), cmd.index("--junitxml"))     # after addopts, before the targets
        self.assertEqual(cmd[-1], "tests/test_types.py")
        self.assertEqual(cmd[cmd.index("-k") + 1], "__gkm")

    def test_normaliser_masks_mock_object_ids_but_keeps_real_differences(self):
        a = "where X = get_provider_status(<Mock id='140485139372160'>)"
        b = "where X = get_provider_status(<Mock id='140593613512368'>)"
        self.assertEqual(testmut.norm(a, []), testmut.norm(b, []))
        self.assertNotEqual(testmut.norm("assert 'NUMBER' == 'NUMBERx'", []), testmut.norm("assert 'NUMBER' == 'NUMBER'", []))
        self.assertNotEqual(testmut.norm("id=7", []), testmut.norm("id=8", []))    # short ids are meaningful values

    def test_common_failure_fraction(self):
        fail = "m|t|failed|assert 1 == 2"
        ok = "m|t|passed|"
        sigs = {"orig": {0: fail, 1: ok, 2: fail}, "gold": {0: fail, 1: ok, 2: ok}, "patch:p": {0: fail, 1: ok, 2: fail}}
        self.assertAlmostEqual(testmut.common_failure_fraction(sigs, [0, 1, 2]), 1 / 3.0)
        self.assertIsNone(testmut.common_failure_fraction({"orig": {}}, [0]))

    def test_harness_version_is_declared(self):
        self.assertEqual(testmut.HARNESS_VERSION, "tm-dev-v3")


if __name__ == "__main__":
    unittest.main()
