import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import discover_m_candidates as D  # noqa: E402
import order_candidates as O  # noqa: E402


def item(n, repo="a/b", title="Fix crash when value is None", merged=True):
    return {"number": n, "title": title, "html_url": "https://github.com/%s/pull/%d" % (repo, n), "draft": False,
            "repository_url": "https://api.github.com/repos/%s" % repo,
            "pull_request": {"url": "https://api.github.com/repos/%s/pulls/%d" % (repo, n), "merged_at": "2025-01-01" if merged else None}}


def f(name, add=3, dele=1, status="modified"):
    return {"filename": name, "additions": add, "deletions": dele, "status": status}


GOOD = [f("pkg/core.py"), f("tests/test_core.py")]


class Filters(unittest.TestCase):
    def test_accepts_a_small_bugfix_with_a_test(self):
        self.assertTrue(D.passes_filters(item(1), GOOD, set())[0])

    def test_rejections(self):
        self.assertEqual(D.passes_filters(item(1, repo="X/Y"), GOOD, {"x/y"})[1], "repository already used or exposed")
        self.assertEqual(D.passes_filters(item(1, merged=False), GOOD, set())[1], "not merged")
        self.assertIn("maintenance", D.passes_filters(item(1, title="Fix typo in docs"), GOOD, set())[1])
        self.assertIn("no test file", D.passes_filters(item(1), [f("pkg/core.py")], set())[1])
        self.assertIn("no non-test", D.passes_filters(item(1), [f("tests/test_core.py")], set())[1])
        self.assertIn("larger than", D.passes_filters(item(1), [f("pkg/core.py", 70, 0), f("tests/test_core.py")], set())[1])
        self.assertIn("changed files", D.passes_filters(item(1), [f("pkg/m%d.py" % i) for i in range(9)] + [f("tests/test_a.py")], set())[1])
        self.assertIn("removed or renamed", D.passes_filters(item(1), [f("pkg/core.py", status="renamed"), f("tests/test_core.py")], set())[1])

    def test_excluded_repository_list_covers_the_development_instances(self):
        repos = set(json.loads((ROOT / "study_m" / "EXCLUDED_REPOS.json").read_text())["repos"])
        for r in ("github/spec-kit", "openfeature/python-sdk", "ethereum/py_ecc", "sqlalchemy/sqlalchemy"):
            self.assertIn(r, repos)


class Ordering(unittest.TestCase):
    def test_order_depends_on_the_seed_and_is_stable(self):
        c = [{"repo": "r%d" % i, "pr": i} for i in range(30)]
        self.assertEqual(O.order(c, "s1"), O.order(c, "s1"))
        self.assertNotEqual(O.order(c, "s1"), O.order(c, "s2"))


class FakeResp:
    def __init__(self, body, headers=None):
        self._b, self.headers = json.dumps(body).encode(), headers or {}

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class FakeGitHub:
    """Serves search pages and per-PR file lists; counts calls; can raise a 403 once."""

    def __init__(self, n=60, bad=()):
        self.items = [item(i, repo="o/r%d" % (i % 20)) for i in range(n)]
        self.files = {i: (GOOD if i % 3 == 0 else [f("pkg/x.py")]) for i in range(n)}   # one in three passes
        self.search_calls = self.file_calls = 0
        self.fail_once = False
        self.bad = set(bad)

    def __call__(self, req, timeout=0):
        url = req.full_url
        if "/search/issues" in url:
            self.search_calls += 1
            page = int(url.split("page=")[-1])
            return FakeResp({"items": self.items if page == 1 else []})
        self.file_calls += 1
        if self.fail_once:
            self.fail_once = False
            raise urllib.error.HTTPError(url, 403, "limit", {"X-RateLimit-Reset": "1000"}, io.BytesIO(b"{}"))
        n = int(url.split("/pulls/")[1].split("/")[0])
        return FakeResp(self.files[n], {"X-RateLimit-Remaining": "900"})


def run(fake, **kw):
    sleeps = []
    t = [0.0]
    client = D.Client("tok", opener=fake, sleep=lambda s: sleeps.append(s), clock=lambda: t[0])
    with tempfile.TemporaryDirectory() as tmp:
        D.run(tmp, client, "seedX", set(), windows=[(2025, 1)], queries=["q {lo} {hi}"], clock=lambda: t[0], **kw)
        log = json.loads((Path(tmp) / "M_DISCOVERY_LOG.json").read_text())
        cands = json.loads((Path(tmp) / "M_CANDIDATES.json").read_text())
    return log, cands, sleeps


class LazyDiscovery(unittest.TestCase):
    def test_stops_at_target_after_examining_only_a_prefix(self):
        fake = FakeGitHub(60)
        log, cands, _ = run(fake, target=5)
        self.assertEqual(len(cands), 5)
        self.assertEqual(log["stopped_because"], "target reached")
        self.assertLess(fake.file_calls, 60)                  # not every hit was fetched
        self.assertEqual(fake.file_calls, log["examined"])    # exactly one API call per examined PR

    def test_result_is_the_prefix_of_the_fully_evaluated_ordered_list(self):
        full_log, full, _ = run(FakeGitHub(60), target=10 ** 6)
        _, part, _ = run(FakeGitHub(60), target=6)
        self.assertEqual([c["name"] for c in part], [c["name"] for c in full[:6]])
        self.assertEqual(full_log["stopped_because"], "list exhausted")

    def test_waits_for_the_rate_limit_instead_of_failing(self):
        fake = FakeGitHub(30)
        fake.fail_once = True
        log, cands, sleeps = run(fake, target=3)
        self.assertEqual(len(cands), 3)
        self.assertTrue(any(s > 3000 for s in sleeps) or any(s > 1 for s in sleeps))   # waited for the reset

    def test_start_continues_where_a_previous_run_stopped(self):
        _, first, _ = run(FakeGitHub(60), target=4)
        log1, _, _ = run(FakeGitHub(60), target=4)
        _, second, _ = run(FakeGitHub(60), target=4, start=log1["next_position"])
        self.assertTrue({c["name"] for c in first}.isdisjoint({c["name"] for c in second}))

    def test_outputs_exist_even_when_the_budget_is_exhausted(self):
        log, cands, _ = run(FakeGitHub(60), target=100, max_examined=7)
        self.assertEqual(log["stopped_because"], "max_examined reached")
        self.assertEqual(log["examined"], 7)


if __name__ == "__main__":
    unittest.main()
