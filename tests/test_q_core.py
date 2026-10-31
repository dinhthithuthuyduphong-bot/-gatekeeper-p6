import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import q_instance as QI  # noqa: E402
from gatekeeper_ext import q_classify as QC  # noqa: E402

EXP = ["exc", "ValueError", "m", "explicit"]
INC = ["exc", "IndexError", "m", "incidental"]
OK = lambda v: ["ok", "int", v]


class Classify(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(QC.category(OK("1"), OK("2")), "C1")
        self.assertEqual(QC.category(OK("1"), EXP), "C1")
        self.assertEqual(QC.category(EXP, OK("2")), "C2-D")                    # explicit rejection skipped
        self.assertEqual(QC.category(INC, OK("2")), "C2-O")                    # incidental crash, the patch copes
        self.assertEqual(QC.category(EXP, ["exc", "TypeError", "x", "explicit"]), "C2-O")
        self.assertEqual(QC.category(["timeout"], OK("1")), "C3")

    def test_summary(self):
        o = [{"source": "G2", "i": 0, "orig": OK("1"), "gold": OK("1"), "patch": OK("2"), "patch_stable": True},
             {"source": "G2", "i": 1, "orig": EXP, "gold": EXP, "patch": OK("2"), "patch_stable": True},
             {"source": "G0", "i": 0, "orig": INC, "gold": INC, "patch": OK("2"), "patch_stable": True},
             {"source": "G0", "i": 1, "orig": OK("1"), "gold": OK("3"), "patch": OK("3"), "patch_stable": True},
             {"source": "G0", "i": 2, "orig": OK("1"), "gold": OK("1"), "patch": OK("9"), "patch_stable": False}]
        s = QC.summarise(o)
        self.assertEqual((s["scored"], s["naive_harm"], s["contract_harm"], s["c1_only_harm"]), (4, 3, 2, 1))


class Selection(unittest.TestCase):
    def test_distinct_seeded_order(self):
        pool = [{"instance_id": "a", "sha": "s%d" % (i % 5), "patch": "p%d" % (i % 5), "submission": "sub%d" % i} for i in range(10)]
        pool += [{"instance_id": "b", "sha": "x", "patch": "q", "submission": "z"}]
        c1, n = QI.select_patches(pool, "a", "seed1")
        c2, _ = QI.select_patches(list(reversed(pool)), "a", "seed1")
        self.assertEqual(n, 5)
        self.assertEqual([c["sha"] for c in c1], [c["sha"] for c in c2])       # independent of the pool's order
        self.assertEqual(len(c1), 3)
        self.assertEqual(sorted(c1[0]["submissions"]), sorted("sub%d" % i for i in range(10) if "s%d" % (i % 5) == c1[0]["sha"]))
        self.assertNotEqual([c["sha"] for c in c1], [c["sha"] for c in QI.select_patches(pool, "a", "seed2")[0]][:3] or None)


class Wrapper(unittest.TestCase):
    def test_wrapper_swaps_the_inner_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Path(tmp) / "py"
            w.write_text(QI.wrapper_text("CID").replace('exec docker exec -i -w "$PWD" CID %s' % QI.QF.TESTBED_PY, 'echo'))
            w.chmod(0o755)
            out = subprocess.run([str(w), "/x/tools/fn_probe_inner.py", "args.json"], capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "/x/tools/q_probe_inner.py args.json")


class Apply(unittest.TestCase):
    def test_patch_application(self):
        with tempfile.TemporaryDirectory() as tmp:
            o = Path(tmp) / "orig"
            o.mkdir()
            (o / "m.py").write_text("a = 1\n")
            patch = "diff --git a/m.py b/m.py\n--- a/m.py\n+++ b/m.py\n@@ -1 +1 @@\n-a = 1\n+a = 2\n"
            self.assertEqual(QI.treated_files(o, patch, tmp, "t"), {"m.py": "a = 2\n"})
            self.assertIsNone(QI.treated_files(o, patch.replace("-a = 1", "-a = 7"), tmp, "u"))


if __name__ == "__main__":
    unittest.main()
