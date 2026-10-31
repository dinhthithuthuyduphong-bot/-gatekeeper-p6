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


class Entries(unittest.TestCase):
    def test_asset_urls(self):
        u, _ = Q.asset_urls({"assets": {"repo": "https://github.com/acme/swe-run", "logs": "s3://swe-bench-submissions/verified/20250101_x"}})
        self.assertIn("https://raw.githubusercontent.com/acme/swe-run/HEAD/all_preds.jsonl", u)
        self.assertIn("https://swe-bench-submissions.s3.amazonaws.com/verified/20250101_x/all_preds.jsonl", u)
        u, _ = Q.asset_urls({"assets": {"repo": "https://github.com/acme/r/tree/main/sub/dir"}})
        self.assertEqual(u[0], "https://raw.githubusercontent.com/acme/r/main/sub/dir/all_preds.jsonl")

    def test_old_s3_entries_use_the_submission_folder_then_per_instance_patches(self):
        meta = {"assets": {"logs": "s3://swe-bench-submissions/verified/2024_x/logs", "trajs": "s3://swe-bench-submissions/verified/2024_x/trajs"}}
        u, _ = Q.asset_urls(meta)
        self.assertEqual(u[0], "https://swe-bench-submissions.s3.amazonaws.com/verified/2024_x/all_preds.jsonl")
        self.assertEqual(Q.logs_bases(meta), ["https://swe-bench-submissions.s3.amazonaws.com/verified/2024_x/logs/"])
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "evaluation" / "verified" / "2024_x"
            (d / "results").mkdir(parents=True)
            (d / "metadata.yaml").write_text("assets:\n  logs: s3://swe-bench-submissions/verified/2024_x/logs\n")
            (d / "results" / "results.json").write_text(json.dumps({"resolved": ["i1", "i2"]}))
            get = lambda url: "diff for " + url.split("/")[-2] if url.endswith("/i1/patch.diff") else None
            per, pool = Q.entries(tmp, get=get)
        self.assertTrue(per["2024_x"]["usable"])
        self.assertEqual([p["instance_id"] for p in pool], ["i1"])            # i2 has no patch file: not in the pool

    def test_unreadable_results_are_described(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "evaluation" / "verified" / "y"
            (d / "results").mkdir(parents=True)
            (d / "metadata.yaml").write_text("assets: {}\n")
            (d / "results" / "by_repo.json").write_text(json.dumps({"django": 3}))
            per, _ = Q.entries(tmp, get=lambda u: None)
        self.assertEqual(per["y"]["results_files"], [["by_repo.json", ["django"]]])

    def test_parse_both_formats(self):
        self.assertEqual(Q.parse_preds('{"instance_id": "a", "model_patch": "p"}\n{"instance_id": "b", "model_patch": "q"}'), [("a", "p"), ("b", "q")])
        self.assertEqual(Q.parse_preds(json.dumps({"a": {"instance_id": "a", "model_patch": "p"}})), [("a", "p")])

    def test_entries_end_to_end(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "evaluation" / "verified" / "20250101_x"
            (d / "results").mkdir(parents=True)
            (d / "metadata.yaml").write_text("assets:\n  repo: https://github.com/acme/run\n")
            (d / "results" / "results.json").write_text(json.dumps({"resolved": ["i1"]}))
            preds = json.dumps({"instance_id": "i1", "model_patch": "diff"}) + "\n" + json.dumps({"instance_id": "i2", "model_patch": "diff2"})
            get = lambda u: preds if u.endswith("acme/run/HEAD/all_preds.jsonl") else None
            per, pool = Q.entries(tmp, get=get)
        self.assertTrue(per["20250101_x"]["usable"])
        self.assertEqual([p["instance_id"] for p in pool], ["i1"])
        self.assertEqual(per["20250101_x"]["tried"][0][1], True)


if __name__ == "__main__":
    unittest.main()
