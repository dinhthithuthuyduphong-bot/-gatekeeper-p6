import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import rq5_classify as C  # noqa: E402

OK = lambda v: ["ok", "int", v]
EXC = lambda t, m="m": ["exc", t, m]


class Rules(unittest.TestCase):
    def test_categories_follow_the_reference_outcome(self):
        self.assertEqual(C.category(OK("1"), EXC("ValueError")), "C1a")
        self.assertEqual(C.category(OK("1"), OK("2")), "C1b")
        self.assertEqual(C.category(EXC("TypeError"), OK("2")), "C2a")
        self.assertEqual(C.category(EXC("TypeError"), EXC("ValueError")), "C2b")
        self.assertEqual(C.category(EXC("TypeError", "a"), EXC("TypeError", "b")), "C2c")
        self.assertEqual(C.category(["timeout"], OK("1")), "C3")

    def test_reproduction_and_revised_share(self):
        def outcomes(c1, c2, n=400):
            xs = [{"source": "G0", "i": i, "orig": OK("1"), "gold": OK("1"), "patch": OK("2"), "patch_stable": True} for i in range(c1)]
            xs += [{"source": "G0", "i": c1 + i, "orig": EXC("TypeError"), "gold": EXC("TypeError"), "patch": EXC("ValueError"), "patch_stable": True} for i in range(c2)]
            xs += [{"source": "G2", "i": i, "orig": OK("1"), "gold": OK("1"), "patch": OK("1"), "patch_stable": True} for i in range(n - c1 - c2)]
            return xs
        orig_a = {"complete": 400, "harm": 20, "help": 0, "divergent": 20, "by_source": {"G0": {"complete": 200, "harm": 20}}, "h_hat": 0.05, "in_band": True}
        orig_b = dict(orig_a, harm=8, divergent=8, by_source={"G0": {"complete": 200, "harm": 8}}, h_hat=0.02)
        targets = [{"name": "a", "original": orig_a}, {"name": "b", "original": orig_b}, {"name": "c", "original": dict(orig_a)}]
        recs = {"a": (orig_a, outcomes(2, 18)), "b": (orig_b, outcomes(8, 0))}
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "t.json").write_text(json.dumps(targets))
            for n, (o, xs) in recs.items():
                d = {k: o[k] for k in C.KEYS}
                d["outcomes"] = xs
                (Path(tmp) / ("COHORT_%s.json" % n)).write_text(json.dumps({"name": n, "repo": "r", "inner": {"attempts": [
                    {"model": "vertex-gemini-flash", "labels": {"plausible": True}, "draws": d}]}}))
            C.main(tmp, str(Path(tmp) / "t.json"), tmp + "/o")
            r = json.loads((Path(tmp) / "o" / "RQ5_CLASSIFIED.json").read_text())
        by = {p["name"]: p for p in r["patches"]}
        self.assertEqual(by["a"]["categories"], {"C1b": 2, "C2b": 18})
        self.assertFalse(by["a"]["in_band_c1"])            # 2/400 = 0.5% < 3/400: most of its harm was outside the contract
        self.assertTrue(by["b"]["in_band_c1"])             # 8/400 = 2%, all on accepted inputs
        self.assertEqual(r["not_reproduced_or_missing"], ["c"])
        self.assertEqual((r["revised_primary"]["lower"]["in_band"], r["revised_primary"]["upper"]["in_band"]), (1, 2))


if __name__ == "__main__":
    unittest.main()
