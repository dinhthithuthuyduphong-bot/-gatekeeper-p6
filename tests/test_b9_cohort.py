import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import b9_cohort as C  # noqa: E402
from gatekeeper_lite import b9  # noqa: E402
from gatekeeper_lite.skill import Target  # noqa: E402

VET = {"name": "quantammsim_379bc0d", "repo": "https://github.com/o/r.git", "pre": "a" * 40, "gold": "b" * 40, "verdict": "ELIGIBLE",
       "changed_files": ["pkg/core/forward.py", "pkg/util.py", "tests/unit/test_lint_bugs.py"], "gold_test_files": ["tests/unit/test_lint_bugs.py"],
       "gold_source_diff": "@@ -1 +1 @@\n-    return value == None  # the buggy comparison\n+    return value is None  # the fixed comparison\n",
       "eligible_oracle": ["tests.unit.test_lint_bugs.TestB006::test_b[forward.fn]", "tests.unit.test_lint_bugs.TestB006::test_a"],
       "eligible_sources": {"tests.unit.test_lint_bugs.TestB006::test_a": "def test_a():\n    assert is_none(None)\n"},
       "classification": {"tests.unit.test_lint_bugs.TestB006::test_a": "F->P", "tests.unit.test_lint_bugs.TestB006::test_p": "P->P",
                          "tests.unit.test_lint_bugs.TestB006::test_b[forward.fn]": "F->P"}}


class IssuePolicy(unittest.TestCase):
    def test_linked_issue_numbers(self):
        self.assertEqual(C.linked_issue_numbers("This fixes #12 and Closes: #7, resolved #12"), [7, 12])
        self.assertEqual(C.linked_issue_numbers("no link, see #99"), [])

    def test_title_only_without_a_linked_issue(self):
        text, prov = C.issue_text("Fix crash on None", None, "")
        self.assertEqual((text, prov["source"]), ("Fix crash on None", "pull request title only"))

    def test_code_blocks_that_leak_the_fix_are_removed_others_kept(self):
        issue = {"title": "None handling", "body": "Calling it fails.\n```\nreturn value is None  # the fixed comparison\n```\nand also\n```\nx = 1\n```"}
        text, prov = C.issue_text("t", issue, VET["gold_source_diff"])
        self.assertNotIn("the fixed comparison", text)
        self.assertIn("x = 1", text)
        self.assertEqual(prov["removed_code_blocks"], 1)
        self.assertTrue(text.startswith("None handling"))

    def test_truncation(self):
        self.assertEqual(len(C.issue_text("t", {"title": "a", "body": "x" * 9000}, "")[0]), 4000)


class Mapping(unittest.TestCase):
    def test_node_ids(self):
        f = ["tests/unit/test_lint_bugs.py", "tests/test_other.py"]
        self.assertEqual(C.to_nodeid("tests.unit.test_lint_bugs.TestB006::test_b[a.b-c]", f), "tests/unit/test_lint_bugs.py::TestB006::test_b[a.b-c]")
        self.assertEqual(C.to_nodeid("tests.test_other::test_f", f), "tests/test_other.py::test_f")
        with self.assertRaises(ValueError):
            C.to_nodeid("other.mod::t", f)


class Builder(unittest.TestCase):
    def test_instance_from_a_vetting_result(self):
        manifest, inst = C.build_instance(VET, None, "Fix None comparison")
        self.assertEqual(manifest["modules"], ["pkg/core/forward.py", "pkg/util.py"])        # tests are not editable
        self.assertEqual(manifest["census_tests"], ["tests/unit"])
        self.assertEqual(inst["visible"]["tests"], ["tests/unit/test_lint_bugs.py::TestB006::test_a"])   # first by id
        self.assertEqual(inst["hidden_f2p"], ["tests/unit/test_lint_bugs.py::TestB006::test_b[forward.fn]"])
        self.assertEqual(inst["hidden_p2p"], ["tests/unit/test_lint_bugs.py::TestB006::test_p"])
        self.assertIn("def test_a", inst["visible_desc"])
        self.assertNotIn("test_b", inst["visible_desc"])                                     # hidden labels are never shown

    def test_unusable_vetting_results_are_refused(self):
        for change in ({"verdict": "NOT_ELIGIBLE"}, {"changed_files": ["tests/unit/test_lint_bugs.py"]}, {"eligible_oracle": []}):
            with self.assertRaises(ValueError):
                C.build_instance(dict(VET, **change), None, "t")


class FakeResp:
    def __init__(self, body):
        self._b = json.dumps(body).encode()

    def read(self):
        return self._b


class ClientAccounting(unittest.TestCase):
    def test_thinking_tokens_are_counted_and_finish_reason_kept(self):
        import os
        import urllib.request
        os.environ["TOK_X"] = "k"
        pro = {"model": "m", "choices": [{"message": {"content": ""}, "finish_reason": "length"}],
               "usage": {"completion_tokens_details": {"reasoning_tokens": 12}, "prompt_tokens": 7, "total_tokens": 19}}
        old = urllib.request.urlopen
        urllib.request.urlopen = lambda req, timeout=0: FakeResp(pro)
        try:
            r = C.CohortClient("https://h", "TOK_X").complete("m", [{"role": "user", "content": "x"}], 16, 0, 1)
        finally:
            urllib.request.urlopen = old
        self.assertEqual((r["usage"]["input"], r["usage"]["output"], r["usage"]["usage_missing"]), (7, 12, False))
        self.assertEqual(r["raw"]["finish_reason"], "length")


class EndToEnd(unittest.TestCase):
    def test_repair_loop_on_a_cohort_style_instance(self):
        orig = "def is_int(x):\n    return isinstance(x, int)\n"
        diff = ("--- a/m.py\n+++ b/m.py\n@@ -1,2 +1,2 @@\n def is_int(x):\n-    return isinstance(x, int)\n"
                "+    return isinstance(x, int) and not isinstance(x, bool)\n")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "m.py").write_text(orig)
            (root / "gk_target.json").write_text(json.dumps({"target_id": "T", "modules": ["m.py"], "pythonpath": []}))
            inst = {"issue": "is_int(True) must be False", "visible_desc": "check",
                    "visible": {"kind": "python", "code": "import m,sys; sys.exit(0 if m.is_int(True) is False else 1)"}}
            client = b9.ScriptedFakeModel(["I think the answer is no diff", diff])
            res, reasons = C.generate(Target.load(root), inst, client, "fake", b9.Budget(3, 500, 3), {"input": 1.0, "output": 2.0}, seed=1)
        self.assertEqual(res.status, "SUBMITTED")
        self.assertEqual([a["verdict"] for a in res.attempts], ["NO_DIFF", "PASSES_VISIBLE"])
        self.assertIn("not isinstance(x, bool)", res.treated["m.py"])
        self.assertEqual(len(reasons), 2)


if __name__ == "__main__":
    unittest.main()
