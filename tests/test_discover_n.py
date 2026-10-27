import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import discover_m_candidates as D  # noqa: E402
import discover_n_continue as N  # noqa: E402
from test_discover_m import FakeGitHub  # noqa: E402


def client(fake):
    t = [0.0]
    return D.Client("tok", opener=fake, sleep=lambda s: None, clock=lambda: t[0])


def full_order(n=60):
    with tempfile.TemporaryDirectory() as tmp:
        D.run(tmp, client(FakeGitHub(n)), "seedX", set(), target=10 ** 6, windows=[(2025, 1)], queries=["q {lo} {hi}"])
        return json.loads((Path(tmp) / "M_CANDIDATES.json").read_text())


class Continuation(unittest.TestCase):
    def test_key_of_a_stored_candidate_equals_the_search_key(self):
        it = {"repository_url": "https://api.github.com/repos/o/r3", "number": 3}
        self.assertEqual(N.key_of_candidate("s", {"repo": "https://github.com/o/r3.git", "pr": 3}), D.order_key("s", it))

    def test_continuation_is_exactly_the_next_part_of_the_same_ordering(self):
        full = full_order(60)                         # 20 candidates pass in total
        first = full[:6]
        with tempfile.TemporaryDirectory() as tmp:
            N.run(tmp, client(FakeGitHub(60)), "seedX", set(), first, target=5, windows=[(2025, 1)], queries=["q {lo} {hi}"])
            cont = json.loads((Path(tmp) / "N_CANDIDATES.json").read_text())
            log = json.loads((Path(tmp) / "N_DISCOVERY_LOG.json").read_text())
        self.assertEqual([c["name"] for c in cont], [c["name"] for c in full[6:11]])
        self.assertFalse({c["name"] for c in cont} & {c["name"] for c in first})
        self.assertEqual(log["stopped_because"], "target reached")

    def test_independent_of_list_position_when_results_change(self):
        full = full_order(60)
        first = full[:6]
        with tempfile.TemporaryDirectory() as tmp:          # the search now returns 10 more PRs
            N.run(tmp, client(FakeGitHub(70)), "seedX", set(), first, target=10 ** 6, windows=[(2025, 1)], queries=["q {lo} {hi}"])
            cont = json.loads((Path(tmp) / "N_CANDIDATES.json").read_text())
        keys = [N.key_of_candidate("seedX", c) for c in cont]
        self.assertTrue(all(k > max(N.key_of_candidate("seedX", c) for c in first) for k in keys))
        self.assertEqual(keys, sorted(keys))


if __name__ == "__main__":
    unittest.main()
