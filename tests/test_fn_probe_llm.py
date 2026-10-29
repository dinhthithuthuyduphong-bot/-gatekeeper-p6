import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import fn_probe_llm as L  # noqa: E402
from gatekeeper_ext import fn_llm_gen as LG  # noqa: E402
from gatekeeper_lite import b9  # noqa: E402

ENV = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONHASHSEED="0")
PRICES = {"input": 0.75, "output": 3.75}
# a class that needs a constructor argument: the signature-driven generator of step 1 could not call it
ORIG = "class Box:\n    def __init__(self, size):\n        self.size = size\n\n    def fits(self, x: int):\n        return x < self.size\n"
GOLD = ORIG.replace("return x < self.size", "return x <= self.size")
GEN_OK = "```python\ndef make_inputs(rng, n):\n    out = []\n    for _ in range(n):\n        b = target_class(rng.randint(0, 5))\n        out.append((b, [rng.randint(0, 6)], {}))\n    return out\n```"
GEN_BAD = "```python\ndef make_inputs(rng, n):\n    return [(target_class(), [1], {}) for _ in range(n)]\n```"


def make(tmp, name, text):
    d = Path(tmp) / name
    d.mkdir()
    (d / "k.py").write_text(text)
    return d


def run(tmp, replies, cap=1.0, orig=ORIG, gold=GOLD):
    o, g = make(tmp, "o", orig), make(tmp, "g", gold)
    client = b9.ScriptedFakeModel(list(replies))
    return L.probe_llm(client, "fake", PRICES, cap, sys.executable, o, g, ["k.py"], [], "fits() excludes the boundary", Path(tmp),
                       n=120, env=ENV, diff_for=lambda rel: "-        return x < self.size\n+        return x <= self.size\n")


class Prompt(unittest.TestCase):
    def test_prompt_contains_what_the_plan_says_and_nothing_of_the_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            o = make(tmp, "o", ORIG)
            ctx = LG.function_context(o, "k.py", "Box.fits")
        m = LG.build_messages("k.py", "Box.fits", ctx, "issue text here", "+ return x <= self.size")
        u = m[1]["content"]
        for part in ("def fits", "def __init__", "issue text here", "x <= self.size", "make_inputs(rng, n)", "about half"):
            self.assertIn(part, u)

    def test_code_extraction(self):
        self.assertIn("def make_inputs", LG.extract_code("text\n```python\ndef make_inputs(rng, n):\n    return []\n```\nmore"))
        self.assertIsNone(LG.extract_code("no code here"))


class StepTwo(unittest.TestCase):
    def test_a_model_written_generator_reaches_the_boundary_bug_in_a_class_needing_arguments(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [GEN_OK])
        f = r["functions"][0]
        self.assertEqual(r["verdict"], "usable", r)
        self.assertGreater(f["divergent"], 0)
        self.assertEqual(f["generator_attempt"], 0)
        self.assertEqual(r["model_calls"], 1)

    def test_a_failing_generator_gets_one_retry_with_the_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [GEN_BAD, GEN_OK])
        f = r["functions"][0]
        self.assertEqual([c["verdict"] for c in f["calls"]], ["GENERATOR_FAILED", "REPLY"])
        self.assertIn("TypeError", f["calls"][0]["error"])
        self.assertEqual(f["generator_attempt"], 1)
        self.assertTrue(f["usable"])

    def test_two_failures_end_the_function_without_a_third_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [GEN_BAD, GEN_BAD, GEN_OK])
        self.assertEqual(r["model_calls"], 2)
        self.assertIn("no working generator", r["functions"][0]["why"])

    def test_the_spend_guard_prevents_the_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [GEN_OK], cap=1e-9)
        self.assertEqual(r["model_calls"], 0)
        self.assertEqual(r["functions"][0]["calls"][0]["verdict"], "BUDGET_CAP")

    def test_no_divergence_when_the_fix_changes_nothing_reachable(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run(tmp, [GEN_OK], gold=ORIG.replace("return x < self.size", "return self.size > x"))
        self.assertEqual(r["verdict"], "the original never differs from the fix on generated inputs")


if __name__ == "__main__":
    unittest.main()
