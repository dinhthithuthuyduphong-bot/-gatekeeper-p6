import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import p_analyze as A  # noqa: E402


def cohort(name, repo, theta, plausible=True, model="vertex-gemini-flash", fs=True, gk=True, n=400):
    harm = round(theta * n)
    return {"name": name, "repo": repo, "inner": {"attempts": [{"model": model, "status": "SUBMITTED", "labels": {"plausible": plausible},
            "draws": {"complete": n, "h_hat": harm / n, "by_source": {"G0": {"complete": n // 2, "harm": harm // 2}, "G2": {"complete": n // 2, "harm": harm - harm // 2}}},
            "gates": {"census_only": plausible, "zero_tolerance": plausible and harm == 0, "b8_plus": False, "smoke20": plausible, "fixed_sample": fs, "gatekeeper": gk}}]}}


class Analysis(unittest.TestCase):
    def write(self, tmp, recs):
        d = Path(tmp) / "art"
        d.mkdir()
        for r in recs:
            (d / ("COHORT_%s.json" % r["name"])).write_text(json.dumps(r))
            (d / ("STREAM_%s.json" % r["name"])).write_text(json.dumps({"name": r["name"], "vet_verdict": "ELIGIBLE", "stage_reached": "P-GEN"}))
        (Path(tmp) / "frame.json").write_text(json.dumps([{"name": r["name"]} for r in recs]))
        return d

    def test_primary_share_interval_precision_and_h1(self):
        recs = [cohort("a%d" % i, "r%d" % (i % 30), 0.02 if i < 30 else 0.0) for i in range(250)]   # 30 of 250 in band = 12%
        with tempfile.TemporaryDirectory() as tmp:
            d = self.write(tmp, recs)
            A.main([str(d), tmp + "/o", "--frame", tmp + "/frame.json", "--boot", "500"])
            r = json.loads((Path(tmp) / "o" / "P_ANALYSIS.json").read_text())
        p = r["PRIMARY"]
        self.assertEqual((p["plausible"], p["in_band"]), (250, 30))
        self.assertAlmostEqual(p["share"], 0.12)
        self.assertTrue(p["P3_precision_met"])                                  # half-width about 0.04
        self.assertFalse(p["H1_reject_at_0.05"])                                # 12% vs 10% is not significant at n = 250
        self.assertLess(p["repo_cluster_boot95"][0], p["share"])

    def test_band_uses_the_derived_edges(self):
        self.assertFalse(A.in_band_rate(0.005, 400))                            # below 3/400 = 0.75%
        self.assertTrue(A.in_band_rate(0.0075, 400))
        self.assertFalse(A.in_band_rate(0.11, 400))                             # above 10.87%
        self.assertFalse(A.in_band_rate(0.0, 0))                                # amendment P-A4: no scored input
        self.assertFalse(A.in_band_rate(None, 0))

    def test_h3_counts_discordance_only_among_acceptable_patches(self):
        recs = [cohort("a%d" % i, "r", 0.02, fs=True, gk=(i % 5 == 0)) for i in range(20)] + [cohort("b", "r", 0.08, fs=False, gk=True)]
        with tempfile.TemporaryDirectory() as tmp:
            d = self.write(tmp, recs)
            A.main([str(d), tmp + "/o", "--frame", tmp + "/frame.json", "--boot", "100"])
            h = json.loads((Path(tmp) / "o" / "P_ANALYSIS.json").read_text())["H3"]
        self.assertEqual((h["acceptable"], h["fixed_sample_only"], h["gatekeeper_only"], h["P4_met"]), (20, 16, 0, True))

    def test_stratified_weights(self):
        recs = [cohort("a%d" % i, "r%d" % i, 0.03) for i in range(10)]
        rows = A.patches(self._dir(recs), "vertex-gemini-flash")
        for w in (0, 0.5, 1):
            self.assertEqual(A.by_weight(rows, w)["patches"], 10)

    def _dir(self, recs):
        tmp = tempfile.mkdtemp()
        return self.write(tmp, recs)


if __name__ == "__main__":
    unittest.main()
