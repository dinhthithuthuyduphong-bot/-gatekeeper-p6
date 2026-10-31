import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import rq5_agreement as A  # noqa: E402
import rq5_rate_llm as L  # noqa: E402
from gatekeeper_lite import b9  # noqa: E402


class Rater(unittest.TestCase):
    def test_blind_prompt_and_parsing(self):
        it = {"id": "x#1", "function": "f", "file": "a.py", "diff": "+x", "reference_output": ["ok", "int", "1"], "patch_output": ["ok", "int", "2"]}
        p = L.prompt(it)
        self.assertNotIn("C1", p)
        self.assertNotIn("hypothes", p.lower())
        self.assertEqual(L.parse('{"code": "R", "reason": "differs"}'), ("R", "differs"))
        self.assertEqual(L.parse("no json")[0], "U")
        r, spent = L.rate([it], b9.ScriptedFakeModel(['{"code": "B", "reason": "order"}']), "fake", {"input": 1.0, "output": 1.0}, 1.0)
        self.assertEqual(r[0]["code"], "B")

    def test_kappa(self):
        self.assertIsNone(A.kappa_nominal(["R"] * 5, ["R"] * 5))                # no variation: kappa undefined
        self.assertAlmostEqual(A.kappa_nominal(["R", "R", "B", "B"], ["R", "B", "B", "B"]), 0.5)


if __name__ == "__main__":
    unittest.main()
