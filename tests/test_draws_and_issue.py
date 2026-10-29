import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from gatekeeper_ext import draws, gates, issue_fetch  # noqa: E402
import test_golddiff as G  # noqa: E402


class Resp:
    def __init__(self, body):
        self._b = json.dumps(body).encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class IssueFetch(unittest.TestCase):
    def opener(self, table):
        def f(req, timeout=0):
            u = req.full_url.split("api.github.com")[1]
            if u not in table:
                raise urllib.error.HTTPError(req.full_url, 404, "x", {}, io.BytesIO(b"{}"))
            return Resp(table[u])
        return f

    def test_linked_issue_is_used_and_the_pr_body_never_is(self):
        t = {"/repos/o/r/pulls/5": {"title": "Fix crash", "body": "The fix is `x is None`. Fixes #9"},
             "/repos/o/r/issues/9": {"title": "Crash on None", "body": "it crashes"}}
        title, issue, prov = issue_fetch.fetch("https://github.com/o/r.git", 5, "", self.opener(t))
        self.assertEqual((title, issue), ("Fix crash", {"title": "Crash on None", "body": "it crashes"}))
        self.assertEqual(prov["issue_used"], 9)
        self.assertNotIn("x is None", json.dumps(issue))

    def test_title_only_when_nothing_is_linked_or_the_link_is_a_pull_request(self):
        t = {"/repos/o/r/pulls/5": {"title": "Fix crash", "body": "closes #7"}, "/repos/o/r/issues/7": {"title": "t", "body": "b", "pull_request": {}}}
        title, issue, prov = issue_fetch.fetch("https://github.com/o/r.git", 5, "", self.opener(t))
        self.assertEqual((title, issue), ("Fix crash", None))

    def test_errors_do_not_raise(self):
        self.assertIn("error", issue_fetch.fetch("https://github.com/o/r.git", 5, "", self.opener({}))[2])
        self.assertIn("error", issue_fetch.fetch("not a url", 5)[2])


class Draws(unittest.TestCase):
    def test_base_and_patch_scoring_on_the_bool_int_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g = G.make(tmp, "o", G.ORIG), G.make(tmp, "g", G.GOLD)
            base, err = draws.prepare_base(o, g, ["m.py"], [], "unittest", ["test_m.py"], Path(tmp) / "w", seed=3, n_draws=40)
            self.assertIsNone(err)
            self.assertGreater(base["info"]["bug_trigger_draws"], 0)
            self.assertTrue(base["deterministic"])
            good = draws.score_patch(base, o, {"m.py": G.GOOD}, [], "unittest", Path(tmp) / "w", "good")[0]
            self.assertEqual(sum(good["harm"]), 0)
            self.assertGreater(good["help"], 0)
            bad_src = "def is_int(x):\n    return False\n\n\ndef double(x):\n    raise TypeError('no')\n"
            bad = draws.score_patch(base, o, {"m.py": bad_src}, [], "unittest", Path(tmp) / "w", "bad")[0]
            self.assertGreater(sum(bad["harm"]), 0)                # the regression is seen on draws where the original agrees with the fix
            self.assertFalse(gates.decisions(bad["harm"], True, bad["help"])["zero_tolerance"])
            self.assertTrue(gates.decisions(good["harm"], True, good["help"])["zero_tolerance"])

    def test_not_eligible_reasons_are_returned_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g = G.make(tmp, "o", G.ORIG), G.make(tmp, "g", G.ORIG)          # identical: nothing edited
            base, err = draws.prepare_base(o, g, ["m.py"], [], "unittest", ["test_m.py"], Path(tmp) / "w", seed=3)
            self.assertIsNone(base)
            self.assertIn("no edited function", err["reason"])


if __name__ == "__main__":
    unittest.main()
