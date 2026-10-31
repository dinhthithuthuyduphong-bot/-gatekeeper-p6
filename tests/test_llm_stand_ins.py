import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import llm_review as LR  # noqa: E402
import qa1_three_raters as Q3  # noqa: E402


class Fake:
    def __init__(self, text):
        self.text, self.calls = text, 0

    def complete(self, model, msgs, max_out, temp, n):
        self.calls += 1
        return {"text": self.text, "usage": {"input": 1000, "output": 200}}


CFG = {"model_id": "m", "prices_usd_per_mtok": {"input": 2.0, "output": 10.0}}


class LlmStandInTest(unittest.TestCase):
    def test_paper_text_has_theory_and_abstract(self):
        t = LR.paper_text()
        self.assertIn("ABSTRACT", t)
        self.assertIn("thm:admission", t)
        self.assertNotIn("ABSTRACT", LR.paper_text(["theory"]))

    def test_proofs_and_mock_modes(self):
        f = Fake('{"items": [{"label": "Lemma 1", "verdict": "correct", "issue": "", "fix": ""}], "overall": "ok"}')
        r = LR.run("proofs", f, CFG, 5.0)
        self.assertEqual(r["review"]["items"][0]["verdict"], "correct")
        self.assertIn("| Lemma 1 | correct |", LR.to_markdown(r))
        f2 = Fake('{"overall": "weak accept", "weaknesses": [{"id": "W1", "severity": "major", "text": "t", "what_would_fix_it": "x"}]}')
        r2 = LR.run("mock", f2, CFG, 5.0)
        self.assertEqual(f2.calls, 3)
        self.assertIn("W1 (major)", LR.to_markdown(r2))
        self.assertIn("parse_error", LR.parse_json("not json"))

    def test_calibration_items_and_score(self):
        import rater_calibration as RC
        its = RC.items()
        self.assertEqual((sum(i["known"] == "B" for i in its), sum(i["known"] == "R" for i in its)), (10, 10))
        all_r = [{"id": i["id"], "code": "R"} for i in its]
        s = RC.score(its, all_r)
        self.assertEqual(s["accuracy"], 0.5)
        self.assertFalse(s["discriminates"])

    def test_inputs_are_inlined_in_review_text(self):
        t = LR.paper_text()
        self.assertNotIn("\\input{", t)
        self.assertLess(t.index("Risk control"), t.index("section{Conclusion}"))

    def test_majority_and_fleiss(self):
        self.assertEqual(Q3.majority(["R", "R", "B"]), "R")
        self.assertEqual(Q3.majority(["R", "B", "U"]), "U")
        self.assertAlmostEqual(Q3.fleiss([["R", "R", "R"], ["B", "B", "B"]]), 1.0)
        self.assertLess(Q3.fleiss([["R", "B", "U"], ["B", "U", "R"]]), 0)


if __name__ == "__main__":
    unittest.main()
