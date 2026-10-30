import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import rq3_summary as S  # noqa: E402
import rq3_target as R  # noqa: E402
from gatekeeper_lite import b9  # noqa: E402

GEN = "```python\ndef make_inputs(rng, n):\n    return [(None, [rng.choice([True, False, 80, 8080, -1, 70000])], {}) for _ in range(n)]\n```"


class EndToEnd(unittest.TestCase):
    def test_the_local_smoke_target_hand_g0_and_g2(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = R.run("study_d_smoke", "S1_demo_port", tmp, n=60, client=b9.ScriptedFakeModel([GEN] * 6))
            on_disk = json.loads((Path(tmp) / "RQ3_S1_demo_port.json").read_text())
        self.assertEqual(r["status"], "FINISHED", r)
        self.assertTrue(r["hand"]["detects"])                                  # the skill changes behaviour on bools
        self.assertGreater(r["hand"]["scopes"]["bool"]["divergent"], 0)
        self.assertEqual(r["hand"]["scopes"]["int"]["divergent"], 0)           # and nothing on ints
        self.assertIn("detects", r["G0"])
        self.assertTrue(r["G2"]["detects"], r["G2"])
        self.assertEqual(on_disk["target"], "S1_demo_port")


class Summary(unittest.TestCase):
    def test_agreement_interval_and_kappa(self):
        lo, hi = S.cp_interval(12, 14)
        self.assertTrue(0.55 < lo < 0.6 and 0.97 < hi < 0.99, (lo, hi))       # textbook values: 0.572, 0.982
        self.assertAlmostEqual(S.kappa([(True, True), (False, False), (True, False), (False, False)]), 0.5)
        with tempfile.TemporaryDirectory() as tmp:
            for i, (h, g) in enumerate([(True, True), (True, False), (False, False)]):
                (Path(tmp) / ("RQ3_t%d.json" % i)).write_text(json.dumps({"target": "t%d" % i, "status": "FINISHED", "hand": {"ran": True, "detects": h},
                                                                          "G0": {"detects": g}}))
            S.main(tmp, tmp + "/o")
            s = json.loads((Path(tmp) / "o" / "RQ3_SUMMARY.json").read_text())
        self.assertEqual((s["G0"]["agree"], s["G0"]["hand_detects_auto_misses"]), (2, 1))


if __name__ == "__main__":
    unittest.main()
