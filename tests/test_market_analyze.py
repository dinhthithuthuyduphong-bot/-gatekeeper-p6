import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import market_analyze as A  # noqa: E402


def fn(gate, ref):
    return {"gate": {"usable": True, "flags": gate}, "ref": {"usable": True, "flags": ref}}


class MarketJudgeTest(unittest.TestCase):
    def test_parse_verdict(self):
        import market_judge as J
        self.assertEqual(J.parse('{"verdict": "safe", "reason": "r"}')[:2], ("safe", "r"))
        self.assertEqual(J.parse("garbage")[0], "unsafe")            # unparsable counts as unsafe (T-A2)
        self.assertFalse(J.parse("garbage")[2])


class MarketAnalyzeTest(unittest.TestCase):
    def test_doc_example_parsing_and_ast(self):
        ex = "## Example\n```python\nx = dict()\n```\n\nUse instead:\n```python\nx = {}\n```\n"
        self.assertEqual(A.doc_examples(ex), ("x = dict()\n", "x = {}\n"))
        self.assertIsNone(A.doc_examples("no example"))
        self.assertTrue(A.same_ast("x = (1)", "x = 1"))

    def test_ground_truth_and_sequence(self):
        funcs = [fn("0" * 200, "0" * 180 + "1" * 20), fn("0" * 200, "0" * 200)]
        pooled, harmful = A.ground_truth(funcs)
        self.assertAlmostEqual(pooled, 0.05)
        self.assertTrue(harmful)
        self.assertEqual(len(A.gate_sequence(funcs)), 200)

    def test_gatekeeper_stops(self):
        e, used = A.gatekeeper([1] * 10, 2578)
        self.assertEqual(e, 0.0)
        self.assertLess(used, 5)                         # alarm after about two harmful draws
        e, used = A.gatekeeper([0] * 200, 16)
        self.assertGreaterEqual(e, 160)                  # certified before the budget for K = 16
        self.assertEqual(A.fs_n(2578), 199)

    def test_end_to_end_small(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "MARKET_CENSUS.json").write_text(json.dumps({"total": {"cells": 3}, "packages": []}))
            (d / "REPLAY.json").write_text(json.dumps({"UP008": {"replay": True}, "SIM108": {"replay": True}}))
            cells = {"UP008": {"applicability": "safe", "functions": [fn("0" * 200, "0" * 200)]},
                     "SIM108": {"applicability": "unsafe", "functions": [fn("10000" * 40, "1" * 40 + "0" * 160)]},
                     "R2:bare_except": {"applicability": "r2", "functions": [fn("0" * 200, "0" * 200)]}}
            (d / "TRIALS_p.json").write_text(json.dumps({"project": "p", "cells": cells}))
            r = A.analyse(d)
            self.assertEqual(r["harmful_cells"], 1)
            g = r["ruff_cells"]["G"]
            self.assertEqual(g["harmful_admitted"], 0)
            self.assertEqual(r["ruff_cells"]["U"]["harmful_admitted"], 1)
            self.assertEqual(r["ruff_cells"]["B6R"]["harmful_admitted"], 1)
            self.assertTrue(r["W2"]["won"])
            self.assertIn("B6S", r["ruff_cells"])

    def test_cell_shards_of_one_package_merge(self):
        """T2-A4: a package's cells split over two records give the same rows as one record."""
        cells = {"UP008": {"applicability": "safe", "functions": [fn("0" * 200, "0" * 200)]},
                 "SIM108": {"applicability": "unsafe", "functions": [fn("10000" * 40, "1" * 40 + "0" * 160)]}}
        out = []
        for split in (False, True):
            with tempfile.TemporaryDirectory() as d:
                d = Path(d)
                (d / "MARKET_CENSUS.json").write_text(json.dumps({"total": {"cells": 2}, "packages": []}))
                (d / "TARGETS.json").write_text(json.dumps({"selected": [{"project": "p"}]}))
                if split:
                    for i, rule in enumerate(sorted(cells)):
                        (d / ("TRIALS_p__%dof2.json" % i)).write_text(json.dumps({"project": "p", "cells": {rule: cells[rule]}}))
                else:
                    (d / "TRIALS_p.json").write_text(json.dumps({"project": "p", "cells": cells}))
                r = A.analyse(d)
                out.append((sorted(x["cell"] for x in r["rows"]), r["package_errors"], r["harmful_cells"]))
        self.assertEqual(out[0], out[1])
        self.assertEqual(out[0][1], [])

    def test_b6_strong_uses_other_packages_only(self):
        rows = [{"cell": "p1/X", "rule": "X", "r2": False, "changed_any": True, "B6R": True},
                {"cell": "p2/X", "rule": "X", "r2": False, "changed_any": False, "B6R": True},
                {"cell": "p3/X", "rule": "X", "r2": False, "changed_any": False, "B6R": True},
                {"cell": "p1/Y", "rule": "Y", "r2": False, "changed_any": True, "B6R": False}]
        A.b6_strong(rows)
        self.assertEqual([r["B6S"] for r in rows], [True, False, False, False])   # p1 sees clean sources; p2, p3 see p1's change
        self.assertEqual([r["B6M"] for r in rows], [True, False, False, False])   # 1 of 2 changed is not fewer than half
        self.assertEqual(rows[3]["b6_sources"], 0)


if __name__ == "__main__":
    unittest.main()
