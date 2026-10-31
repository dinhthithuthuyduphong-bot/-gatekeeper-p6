import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import q_f2 as Q  # noqa: E402


class Pool(unittest.TestCase):
    def test_census(self):
        preds_a = "\n".join(json.dumps({"instance_id": i, "model_patch": "diff --git a\nindex 1\n+x  "}) for i in ("i1", "i2", "i3"))
        preds_b = "\n".join(json.dumps({"instance_id": i, "model_patch": "diff --git a\nindex 2\n+x"}) for i in ("i1", "i2"))
        files = {("20250101_a", "all_preds.jsonl"): preds_a, ("20250101_a", "results/results.json"): json.dumps({"resolved": ["i1", "i2"]}),
                 ("20250202_b", "all_preds.jsonl"): preds_b, ("20250202_b", "results/results.json"): json.dumps({"resolved": ["i1"]}),
                 ("broken", "all_preds.jsonl"): None}
        get = lambda url: next((v for (s, f), v in files.items() if url.endswith("/%s/%s" % (s, f))), None)
        per_sub, per_inst, pool = Q.census(["20250101_a", "20250202_b", "broken"], get=get)
        self.assertEqual(len(pool), 3)                                    # only resolved predictions
        self.assertEqual(per_inst["i1"], {"patches": 2, "distinct": 1})   # same content after normalisation
        self.assertFalse(per_sub["broken"]["usable"])
        self.assertEqual(per_sub["20250101_a"]["date"], "20250101")

    def test_resolved_layouts(self):
        self.assertEqual(Q.resolved_ids(json.dumps({"resolved": ["a"]})), {"a"})
        self.assertEqual(Q.resolved_ids(json.dumps({"resolved": {"x": ["a", "b"]}})), {"a", "b"})
        self.assertIsNone(Q.resolved_ids("not json"))


if __name__ == "__main__":
    unittest.main()
