import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import b9_analyze as BA  # noqa: E402
import market_b9 as M  # noqa: E402


class B9Test(unittest.TestCase):
    def test_replace_method_keeps_indent_and_decorator(self):
        src = "class A:\n    @staticmethod\n    def f(x):\n        return x == None\n\nY = 1\n"
        new = M.replace_function(src, "A.f", "def f(x):\n    return x is None\n")
        self.assertEqual(new, "class A:\n    @staticmethod\n    def f(x):\n        return x is None\n\nY = 1\n")
        self.assertIsNone(M.replace_function(src, "A.f", "def f(x:\n"))
        self.assertIsNone(M.replace_function(src, "A.g", "def g(): pass"))

    def test_code_block_and_source(self):
        self.assertEqual(M.code_block("x\n```python\ndef f(): pass\n```\n"), "def f(): pass\n")
        node, text = M.function_source("def f():\n    return 1\n", "f")
        self.assertEqual(text, "def f():\n    return 1\n")

    def test_cell_harm(self):
        rec = {"functions": [{"b9_ref_flags": "0" * 90 + "1" * 10}, {"b9_ref_flags": ""}, {"b9_ref_flags": None}]}
        self.assertAlmostEqual(BA.cell_harm(rec), 0.05)


if __name__ == "__main__":
    unittest.main()
