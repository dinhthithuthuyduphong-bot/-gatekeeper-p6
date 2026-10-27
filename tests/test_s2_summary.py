import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import s2_summary as S  # noqa: E402


def rec(name, verdict="NOT_ELIGIBLE (no fail-before/pass-after test)", summary=None, tail=""):
    return {"name": name, "verdict": verdict, "summary": summary or {}, "arms": {"pre": {"tail": tail}, "gold": {"tail": tail}}}


class S2(unittest.TestCase):
    def test_categories(self):
        self.assertTrue(S.category(rec("a", "ELIGIBLE", {"F->P": 2})).startswith("eligible"))
        self.assertEqual(S.category(rec("b", summary={"P->P": 3})), "tests ran, no fail-to-pass test")
        self.assertEqual(S.category(rec("c", tail="E   ModuleNotFoundError: No module named 'yaml'")), "tests not runnable: missing python module")
        self.assertEqual(S.category(rec("d", tail="ImportError while loading conftest")), "tests not runnable: conftest or fixture error")
        self.assertEqual(S.category(rec("e", "VETTING_ERROR: x")), "vetting tool error")

    def test_gate_is_applied_exactly_as_registered(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            cands = [{"name": "n%d" % i, "repo": "r%d" % i, "pr": i} for i in range(100)]
            (t / "c.json").write_text(json.dumps(cands))
            (t / "art").mkdir()
            for i in range(100):
                r = rec("n%d" % i, "ELIGIBLE", {"F->P": 1}) if i < 39 else rec("n%d" % i, tail="No module named 'x'")
                (t / "art" / ("VETTING_n%d.json" % i)).write_text(json.dumps(r))
            S.main(str(t / "art"), str(t / "c.json"), str(t / "o"), 100)
            s = json.loads((t / "o" / "S2_SUMMARY.json").read_text())
            self.assertEqual((s["eligible"], s["gate_M1"]), (39, "FAIL"))          # 39 < 40
            (t / "art" / "VETTING_n39.json").write_text(json.dumps(rec("n39", "ELIGIBLE", {"F->P": 1})))
            S.main(str(t / "art"), str(t / "c.json"), str(t / "o"), 100)
            self.assertEqual(json.loads((t / "o" / "S2_SUMMARY.json").read_text())["gate_M1"], "PASS")
            S.main(str(t / "art"), str(t / "c.json"), str(t / "o"), 100, 60, 200)       # Study N thresholds
            self.assertEqual(json.loads((t / "o" / "S2_SUMMARY.json").read_text())["gate"], "FAIL")


if __name__ == "__main__":
    unittest.main()
