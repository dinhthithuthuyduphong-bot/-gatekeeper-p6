import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_ext.usage import output_tokens, reasoning_tokens  # noqa: E402

PRO = {"completion_tokens_details": {"reasoning_tokens": 12}, "prompt_tokens": 7, "total_tokens": 19}      # as logged on 26/10/2026
FLASH = {"completion_tokens": 1, "prompt_tokens": 7, "total_tokens": 8}


class Usage(unittest.TestCase):
    def test_the_two_records_seen_in_the_smoke_test(self):
        self.assertEqual(output_tokens(PRO), 12)
        self.assertEqual(reasoning_tokens(PRO), 12)
        self.assertEqual(output_tokens(FLASH), 1)
        self.assertEqual(reasoning_tokens(FLASH), 0)

    def test_fallbacks_and_unknowns(self):
        self.assertEqual(output_tokens({"completion_tokens": 5}), 5)
        self.assertEqual(output_tokens({"completion_tokens_details": {"reasoning_tokens": 9}}), 9)
        self.assertIsNone(output_tokens({"prompt_tokens": 3}))
        self.assertIsNone(output_tokens(None))
        self.assertIsNone(output_tokens({}))


if __name__ == "__main__":
    unittest.main()
