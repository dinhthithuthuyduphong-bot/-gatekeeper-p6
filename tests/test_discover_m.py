import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import discover_m_candidates as D  # noqa: E402
import order_candidates as O  # noqa: E402


def pr(title="Fix crash when value is None", repo="a/b", merged=True):
    return {"title": title, "number": 7, "html_url": "u", "draft": False, "merged_at": "2025-01-01" if merged else None,
            "merge_commit_sha": "abc" if merged else None, "base": {"repo": {"full_name": repo}}}


def f(name, add=3, dele=1, status="modified"):
    return {"filename": name, "additions": add, "deletions": dele, "status": status}


class Filters(unittest.TestCase):
    def test_accepts_a_small_bugfix_with_a_test(self):
        ok, why = D.passes_filters(pr(), [f("pkg/core.py"), f("tests/test_core.py")], set())
        self.assertTrue(ok, why)

    def test_rejections(self):
        base = [f("pkg/core.py"), f("tests/test_core.py")]
        self.assertEqual(D.passes_filters(pr(repo="X/Y"), base, {"x/y"})[1], "repository already used or exposed")
        self.assertEqual(D.passes_filters(pr(merged=False), base, set())[1], "not merged")
        self.assertIn("maintenance", D.passes_filters(pr(title="Fix typo in docs"), base, set())[1])
        self.assertIn("no test file", D.passes_filters(pr(), [f("pkg/core.py")], set())[1])
        self.assertIn("no non-test", D.passes_filters(pr(), [f("tests/test_core.py")], set())[1])
        self.assertIn("larger than", D.passes_filters(pr(), [f("pkg/core.py", 70, 0), f("tests/test_core.py")], set())[1])
        self.assertIn("changed files", D.passes_filters(pr(), [f("pkg/m%d.py" % i) for i in range(9)] + [f("tests/test_a.py")], set())[1])
        self.assertIn("removed or renamed", D.passes_filters(pr(), [f("pkg/core.py", status="renamed"), f("tests/test_core.py")], set())[1])

    def test_excluded_repository_list_covers_the_development_instances(self):
        import json
        repos = set(json.loads((ROOT / "study_m" / "EXCLUDED_REPOS.json").read_text())["repos"])
        for r in ("github/spec-kit", "openfeature/python-sdk", "ethereum/py_ecc"):
            self.assertIn(r, repos)


class Ordering(unittest.TestCase):
    def test_order_depends_on_the_seed_and_is_stable(self):
        c = [{"repo": "r%d" % i, "pr": i} for i in range(30)]
        self.assertEqual(O.order(c, "s1"), O.order(c, "s1"))
        self.assertNotEqual(O.order(c, "s1"), O.order(c, "s2"))
        self.assertEqual(sorted(x["pr"] for x in O.order(c, "s1")), list(range(30)))


if __name__ == "__main__":
    unittest.main()
