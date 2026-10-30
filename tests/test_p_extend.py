import json
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import discover_m_candidates as D  # noqa: E402
import discover_p_extend as X  # noqa: E402
import p_assemble_ext as PA  # noqa: E402
from split_candidates import track  # noqa: E402
from test_discover_m import FakeResp, item, GOOD  # noqa: E402


class PagedGitHub:
    """Serves different PRs on different (window, page) pairs; records which pages were asked for."""

    def __init__(self, per_page=5):
        self.asked, self.per_page = [], per_page

    def __call__(self, req, timeout=0):
        url = req.full_url
        if "/search/issues" in url:
            page = int(url.split("page=")[-1])
            q = urllib.parse.unquote(url.split("q=")[1].split("&")[0])
            year = int(q.split("created:")[1][:4])
            self.asked.append((year, page))
            base = year * 1000 + page * 100
            return FakeResp({"items": [item(base + i, repo="o/r%d" % ((base + i) % 37)) for i in range(self.per_page)]})
        return FakeResp(GOOD, {"X-RateLimit-Remaining": "900"})


def client(fake):
    return D.Client("t", opener=fake, sleep=lambda s: None, clock=lambda: 0.0)


class Extension(unittest.TestCase):
    def test_only_the_new_part_of_the_space_is_searched(self):
        space = [((2025, 1), (3, 4, 5)), ((2021, 1), (1, 2, 3, 4, 5))]
        fake = PagedGitHub(per_page=100)                                         # full pages, so paging continues
        with tempfile.TemporaryDirectory() as tmp:
            X.run(tmp, client(fake), "S", set(), [], target=3, space=space, queries=["q created:{lo}..{hi}"], clock=lambda: 0.0)
        self.assertEqual(sorted(set(fake.asked)), [(2021, p) for p in range(1, 6)] + [(2025, p) for p in (3, 4, 5)])

    def test_excluded_candidates_never_reappear_and_order_is_the_key_order(self):
        space = [((2021, 1), (1, 2))]
        with tempfile.TemporaryDirectory() as tmp:
            X.run(tmp, client(PagedGitHub()), "S", set(), [], target=10 ** 6, space=space, queries=["q created:{lo}..{hi}"], clock=lambda: 0.0)
            full = json.loads((Path(tmp) / "P_EXT_CANDIDATES.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            X.run(tmp, client(PagedGitHub()), "S", set(), full[:3], target=10 ** 6, space=space, queries=["q created:{lo}..{hi}"], clock=lambda: 0.0)
            rest = json.loads((Path(tmp) / "P_EXT_CANDIDATES.json").read_text())
        self.assertEqual([c["name"] for c in rest], [c["name"] for c in full[3:]])

    def test_after_continues_an_interrupted_part_b(self):
        space = [((2021, 1), (1, 2))]
        with tempfile.TemporaryDirectory() as tmp:
            X.run(tmp, client(PagedGitHub()), "S", set(), [], target=4, space=space, queries=["q created:{lo}..{hi}"], clock=lambda: 0.0)
            first = json.loads((Path(tmp) / "P_EXT_CANDIDATES.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            X.run(tmp, client(PagedGitHub()), "S", set(), [], after_cands=first, target=10 ** 6, space=space, queries=["q created:{lo}..{hi}"], clock=lambda: 0.0)
            second = json.loads((Path(tmp) / "P_EXT_CANDIDATES.json").read_text())
        self.assertTrue({c["name"] for c in first}.isdisjoint({c["name"] for c in second}))

    def test_forks_with_the_same_name_are_kept_and_renamed(self):
        b = [{"name": "pytest_proj_pr1", "repo": "https://github.com/u%d/pytest_proj.git" % i, "pr": 1} for i in range(5)]
        na, nr, s = PA.extend([], [], b, "S")
        names = [c["name"] for c in na + nr]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(names), 5)
        self.assertEqual(len(s["renamed"]["pytest_proj_pr1"]), 4)                 # the first keeps its name

    def test_part_b_is_appended_by_track(self):
        a = [{"name": "a1", "repo": "https://github.com/x/a.git", "pr": 1}]
        r = [{"name": "r1", "repo": "https://github.com/x/r.git", "pr": 1}]
        b = [{"name": "b%d" % i, "repo": "https://github.com/y/b%d.git" % i, "pr": 1} for i in range(20)]
        na, nr, s = PA.extend(a, r, b, "S")
        self.assertEqual((na[0]["name"], nr[0]["name"]), ("a1", "r1"))               # part A stays first
        self.assertTrue(all(track("S", c["repo"]) == "ASTAR" for c in na[1:]))
        self.assertEqual(s["part_b"]["ASTAR"] + s["part_b"]["RR"], 20)
        with self.assertRaises(SystemExit):
            PA.extend(a, r, a, "S")


if __name__ == "__main__":
    unittest.main()


class Robustness(unittest.TestCase):
    def test_a_dropped_connection_is_retried_then_recorded_not_raised(self):
        import http.client

        class Flaky:
            def __init__(self, fails):
                self.fails, self.calls = fails, 0

            def get(self, url, search=False):
                self.calls += 1
                if self.calls <= self.fails:
                    raise http.client.RemoteDisconnected("Remote end closed connection without response")
                return {"ok": True}
        waits = []
        self.assertEqual(X.safe_get(Flaky(2), "u", sleep=waits.append), {"ok": True})
        self.assertEqual(waits, [5, 15])
        waits = []
        self.assertIn("RemoteDisconnected", X.safe_get(Flaky(99), "u", sleep=waits.append)["error"])
        self.assertEqual(waits, [5, 15, 45, 120])
