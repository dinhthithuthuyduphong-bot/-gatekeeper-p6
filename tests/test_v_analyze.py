"""Study V analysis on synthetic records: flips, F0 misses, F1 retirement and epoch-1 decisions."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import v_analyze as V  # noqa: E402


def row(cell, harmful, g, draws=200, b8=None):
    return {"cell": cell, "harmful": harmful, "G": g, "g_draws": draws, "n_gate": 200, "B8": (not harmful) if b8 is None else b8}


class VAnalyze(unittest.TestCase):
    def test_flip_retired_and_rejected(self):
        td, vd = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        t = [row("p/A", False, True), row("p/B", True, False, 3), row("q/C", False, True)]
        (td / "STUDY_T_RESULT.json").write_text(json.dumps({"rows": t}))
        (td / "STUDY_T_EPOCH0.json").write_text(json.dumps({"rows": t}))
        v = [row("p/A", True, False, 2), row("p/B", False, True), row("q/C", False, True)]
        (vd / "STUDY_V_RESULT.json").write_text(json.dumps({"rows": v, "package_errors": []}))
        for proj in ("p", "q"):
            (vd / ("TRIALS_%s.json" % proj)).write_text(json.dumps({"project": proj, "env": {"fingerprint": {"python": "3.13.1", "freeze": []}}}))
        r = V.analyse(td, vd)
        self.assertEqual((r["flips_safe_to_harmful"], r["flips_harmful_to_safe"]), (["p/A"], ["p/B"]))
        self.assertEqual((r["t_admitted_epoch0"], r["f0_harmful_kept"], r["f1_retired"]), (2, 1, 2))
        self.assertEqual(r["f1_epoch1"]["harmful_admitted"], 0)
        self.assertEqual(r["f1_epoch1"]["safe_admitted"], 2)
        self.assertTrue(r["V_W1"] and r["V_W2"])
        self.assertEqual(r["packages_fingerprint_changed"], 2)

    def test_unchanged_fingerprint_is_not_retired(self):
        td, vd = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
        t = [row("p/A", False, True)]
        (td / "STUDY_T_RESULT.json").write_text(json.dumps({"rows": t}))
        (td / "STUDY_T_EPOCH0.json").write_text(json.dumps({"rows": t}))
        (vd / "STUDY_V_RESULT.json").write_text(json.dumps({"rows": [row("p/A", True, True)]}))
        (vd / "TRIALS_p.json").write_text(json.dumps({"project": "p", "env": {"fingerprint": {"python": "3.12.9", "freeze": []}}}))
        r = V.analyse(td, vd)
        self.assertEqual((r["f0_harmful_kept"], r["f1_retired"]), (1, 0))
        self.assertFalse(r["V_W1"] or r["V_W2"])


if __name__ == "__main__":
    unittest.main()
