import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import q_analyze as A  # noqa: E402


def rec(i, naive, contract):
    c = {"divergent": 1 if naive else 0, "naive_harm": naive, "contract_harm": contract, "c1_only_harm": contract,
         "by_source": {"G2": {"C1": contract, "C2-O": naive - contract}}, "categories": {}, "scored": 400}
    return {"instance_id": "i%d" % i, "repo": "r%d" % (i % 7), "status": "FINISHED", "distinct_patches": 5,
            "patches": [{"order": 0, "status": "SCORED", "submissions": ["20240101_x"], "classified": c}]}


class Analysis(unittest.TestCase):
    def test_hq1_and_gate(self):
        recs = [rec(i, 3, 1 if i < 4 else 0) for i in range(24)] + [rec(100 + i, 0, 0) for i in range(100)]
        with tempfile.TemporaryDirectory() as tmp:
            for r in recs:
                (Path(tmp) / ("Q_%s.json" % r["instance_id"])).write_text(json.dumps(r))
            A.main([tmp, "469", tmp + "/o", "--boot", "200"])
            res = json.loads((Path(tmp) / "o" / "Q_ANALYSIS.json").read_text())
        h = res["HQ1"]
        self.assertEqual((h["units"], h["without_contract_regression"], h["gate_Q_G1_met"]), (24, 20, True))
        self.assertTrue(h["HQ1_supported_at_0.05"])                               # 20/24 vs 0.5
        self.assertAlmostEqual(res["Q5_inflation_naive_over_contract"], 24 / 4)

    def test_gate_not_met(self):
        h = A.hq1([rec(i, 3, 0) for i in range(10)], "contract_harm")
        self.assertFalse(h["gate_Q_G1_met"])
        self.assertNotIn("HQ1_supported_at_0.05", h)


if __name__ == "__main__":
    unittest.main()
