import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from gatekeeper_ext import fn_draws  # noqa: E402
from gatekeeper_ext import q_classify as QC  # noqa: E402
import q_review_capture as RC  # noqa: E402
import q_review_items as RI  # noqa: E402

OK1, OK2, EXC = ["ok", "int", "1"], ["ok", "int", "2"], ["exc", "ValueError", "bad"]


def outcomes():
    # i0: C1 (fix returns 1, patch 2); i1: no naive difference; i2: C2-O (fix raises incidentally); i3: unstable
    return [{"source": "G0", "i": 0, "orig": OK1, "gold": OK1, "patch": OK2, "patch_stable": True},
            {"source": "G0", "i": 1, "orig": OK1, "gold": OK1, "patch": OK1, "patch_stable": True},
            {"source": "G2", "i": 2, "orig": EXC, "gold": EXC, "patch": OK1, "patch_stable": True},
            {"source": "G2", "i": 3, "orig": OK1, "gold": OK1, "patch": OK2, "patch_stable": False}]


class CaptureTest(unittest.TestCase):
    def test_install_keeps_outcomes_and_inputs(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "src"
            src.mkdir()
            (src / "calls.json").write_text("[[[1], {}]]")
            (src / "gen.py").write_text("def make_inputs(): pass\n")
            old_s, old_p = QC.summarise, fn_draws.prepare_fn_base
            fn_draws.prepare_fn_base = lambda *a, **k: ({"calls": str(src / "calls.json"), "gen": str(src / "gen.py")}, None)
            try:
                RC.install(Path(t) / "out")
                s = QC.summarise(outcomes())
                self.assertEqual(s["outcomes"], outcomes())
                self.assertEqual(s["categories"], old_s(outcomes())["categories"])
                fn_draws.prepare_fn_base()
                self.assertTrue((Path(t) / "out" / "inputs" / "g0.calls.json").is_file())
                self.assertTrue((Path(t) / "out" / "inputs" / "g2.make_inputs.py").is_file())
            finally:
                QC.summarise, fn_draws.prepare_fn_base = old_s, old_p


class ItemsTest(unittest.TestCase):
    def _write(self, t, rerun_outcomes):
        cls = QC.summarise(outcomes())
        target = {"file": "a.py", "qualname": "f", "generator_sha256": "g"}
        rec = {"instance_id": "x__y-1", "repo": "x/y", "status": "FINISHED", "target": target,
               "patches": [{"order": 0, "sha": "s1", "status": "SCORED", "submissions": [], "classified": cls}]}
        recs = Path(t) / "Q_RECORDS.jsonl.gz"
        with gzip.open(recs, "wt") as f:
            f.write(json.dumps(rec) + "\n")
            f.write(json.dumps({"instance_id": "x__y-2", "repo": "x/y", "status": "NOT_USABLE"}) + "\n")
        cap = Path(t) / "cap" / "R_x__y-1"
        (cap / "inputs").mkdir(parents=True)
        (cap / "patches").mkdir()
        (cap / "inputs" / "g0.calls.json").write_text(json.dumps([[[5], {}]]))
        (cap / "patches" / "s1.diff").write_text("--- a\n+++ b\n")
        new_cls = dict(QC.summarise(rerun_outcomes), outcomes=rerun_outcomes)
        new = dict(rec, patches=[dict(rec["patches"][0], classified=new_cls)])
        (cap / "Q_x__y-1.json").write_text(json.dumps(new))
        ver = Path(t) / "VERIFIED.json"
        ver.write_text(json.dumps([{"instance_id": "x__y-1", "patch": "gold"}]))
        return recs, ver

    def test_reproduced_unit_gives_blind_items(self):
        with tempfile.TemporaryDirectory() as t:
            recs, ver = self._write(t, outcomes())
            st = RI.build(Path(t) / "cap", recs, ver, "7", Path(t) / "out")
            self.assertEqual((st["hq1_units"], st["reproduced"], st["items"]), (1, 1, 1))
            item = json.loads((Path(t) / "out" / "ITEMS.json").read_text())[0]
            self.assertNotIn("category", item)
            self.assertEqual(item["input"], [[5], {}])
            self.assertEqual(json.loads((Path(t) / "out" / "KEY.json").read_text())[0]["category"], "C1")

    def test_not_reproduced_unit_gives_no_items(self):
        with tempfile.TemporaryDirectory() as t:
            changed = outcomes()
            changed[1]["patch"] = OK2                              # one more naive difference: summary differs
            recs, ver = self._write(t, changed)
            st = RI.build(Path(t) / "cap", recs, ver, "7", Path(t) / "out")
            self.assertEqual((st["reproduced"], st["items"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
