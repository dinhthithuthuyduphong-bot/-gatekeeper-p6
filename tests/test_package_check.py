import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import package_check as P  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


class Check(unittest.TestCase):
    def test_ok_missing_different_and_misplaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)
            (r / "tools").mkdir()
            (r / "study_n").mkdir()
            (r / "tools" / "a.py").write_bytes(b"aaa")
            (r / "tools" / "b.py").write_bytes(b"changed")
            (r / "N_T1_EDITS.txt").write_bytes(b"edits")                 # delivered to the wrong place
            m = {"files": {"tools/a.py": sha(b"aaa"), "tools/b.py": sha(b"bbb"), "study_n/N_T1_EDITS.txt": sha(b"edits"), "tools/c.py": sha(b"c")}}
            rows = {rel: (st, d) for rel, st, d in P.check(m, r)}
            self.assertEqual(rows["tools/a.py"][0], "OK")
            self.assertEqual(rows["tools/b.py"][0], "DIFFERENT")
            self.assertEqual(rows["study_n/N_T1_EDITS.txt"][0], "MISSING")
            self.assertIn("N_T1_EDITS.txt", rows["study_n/N_T1_EDITS.txt"][1])        # says where it actually is
            self.assertIn("not found anywhere", rows["tools/c.py"][1])
            self.assertIn("PROBLEMS: 3 of 4", P.render("x", P.check(m, r)))


if __name__ == "__main__":
    unittest.main()
