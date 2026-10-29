import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import n_s3_check as C  # noqa: E402
import n_s3_shard as SH  # noqa: E402
import n_s3_summary as S  # noqa: E402
import test_golddiff as G  # noqa: E402


def harness(**kw):
    h = {"eligible": True, "complete_draws_by_patch": {"gold_itself": 150}, "deterministic": True, "bug_trigger_rate": 0.02, "draws_compiled": 150}
    h.update(kw)
    return {"name": "x", "repo": "r", "status": "FINISHED", "harness": h}


class Gate(unittest.TestCase):
    def test_each_condition(self):
        self.assertEqual(S.n2_pass(harness())[0], True)
        self.assertIn("not eligible", S.n2_pass(harness(eligible=False, reason="baseline"))[1])
        self.assertIn("complete draws", S.n2_pass(harness(complete_draws_by_patch={"gold_itself": 99}))[1])
        self.assertIn("deterministic", S.n2_pass(harness(deterministic=False))[1])
        self.assertIn("never differs", S.n2_pass(harness(bug_trigger_rate=0.0))[1])

    def test_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(41):
                r = harness() if i < 40 else harness(deterministic=False)
                r["name"] = "n%d" % i
                (Path(tmp) / ("S3_n%d.json" % i)).write_text(json.dumps(r))
            S.main(tmp, tmp + "/o")
            s = json.loads((Path(tmp) / "o" / "S3_SUMMARY.json").read_text())
            self.assertEqual((s["pass"], s["gate_N2"]), (40, "PASS"))


class Plan(unittest.TestCase):
    def test_modules_census_pythonpath(self):
        rec = {"changed_files": ["src/pkg/a.py", "tests/unit/test_a.py", "docs/x.md"], "gold_test_files": ["tests/unit/test_a.py", "tests/unit/test_b.py"]}
        modules, census, pp, tests = C.instance_plan(rec)
        self.assertEqual((modules, census, pp), (["src/pkg/a.py"], ["tests/unit"], ["src"]))
        rec2 = {"changed_files": ["a.py", "test_a.py"], "gold_test_files": ["test_a.py"]}
        self.assertEqual(C.instance_plan(rec2)[1], ["test_a.py"])                 # common dir is the root: use the files
        self.assertNotEqual(C.seed_for("a"), C.seed_for("b"))


class Analyze(unittest.TestCase):
    def test_inner_step_end_to_end_on_a_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            o, g = G.make(tmp, "o", G.ORIG), G.make(tmp, "g", G.GOLD)
            args = {"orig": str(o), "gold": str(g), "modules": ["m.py"], "pythonpath": [], "census": ["test_m.py"],
                    "work": str(Path(tmp) / "w"), "seed": 3, "out": str(Path(tmp) / "h.json"), "runner": "unittest", "n_draws": 40, "n_mutants": 2}
            (Path(tmp) / "a.json").write_text(json.dumps(args))
            p = subprocess.run([sys.executable, str(ROOT / "tools" / "n_s3_analyze.py"), str(Path(tmp) / "a.json")], capture_output=True, text=True, timeout=200)
            self.assertEqual(p.returncode, 0, p.stderr[-800:])
            h = json.loads((Path(tmp) / "h.json").read_text())
        self.assertTrue(h["eligible"], h)
        self.assertGreater(h["bug_trigger_rate"], 0)
        ok, why = S.n2_pass({"harness": h}, min_draws=10)
        self.assertTrue(ok, why)


class Shard(unittest.TestCase):
    def test_timeout_is_recorded_as_a_failed_instance(self):
        with tempfile.TemporaryDirectory() as tmp:
            elig = Path(tmp) / "e.json"
            elig.write_text(json.dumps([{"name": "a", "repo": "r1"}, {"name": "b", "repo": "r2"}]))

            def fake(cmd, timeout, cwd=None):
                if cmd[-2] == "a":
                    raise subprocess.TimeoutExpired(cmd, timeout)
                return subprocess.CompletedProcess(cmd, 0, "ok", "")
            old, SH.run_group = SH.run_group, fake
            try:
                SH.main(str(elig), tmp + "/o", 0, 1, 5)
            finally:
                SH.run_group = old
            a = json.loads((Path(tmp) / "o" / "S3_a.json").read_text())
            self.assertEqual(a["status"], "TIMEOUT")
            self.assertFalse(S.n2_pass(a)[0])
            rows = json.loads((Path(tmp) / "o" / "SHARD_0_SUMMARY.json").read_text())["instances"]
            self.assertEqual([r["status"] for r in rows], ["TIMEOUT", "FINISHED"])


if __name__ == "__main__":
    unittest.main()
