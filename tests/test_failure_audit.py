import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import failure_audit as FA  # noqa: E402


class ClassifyTest(unittest.TestCase):
    def test_real_log_excerpts(self):
        # excerpts of real logs: run 41193552100 (second rater), run 41182723003 (stream plan with only=3)
        self.assertEqual(FA.classify('"reason": "ACCESS_TOKEN_EXPIRED",\n##[error]Process completed with exit code 1.')[0], "TOKEN_EXPIRED")
        self.assertEqual(FA.classify('File "<stdin>", line 11, in <module>\nAssertionError\n##[error]Process completed')[0], "INPUT_VALIDATION")
        self.assertEqual(FA.classify("FileNotFoundError: [Errno 2] No such file or directory: '/tmp/x'")[0], "MISSING_FILE")
        self.assertEqual(FA.classify("Ran 300 tests\nFAILED (failures=2)")[0], "UNIT_TESTS_FAILED")
        self.assertEqual(FA.classify("! [rejected] HEAD -> main (fetch first)")[0], "GIT_PUSH_REJECTED")
        self.assertEqual(FA.classify("nothing recognisable")[0], "OTHER")


if __name__ == "__main__":
    unittest.main()
