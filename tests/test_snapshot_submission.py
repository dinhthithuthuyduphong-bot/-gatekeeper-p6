import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import snapshot_submission as S  # noqa: E402


class SnapshotTest(unittest.TestCase):
    def test_records_hashes_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            pdf = Path(t) / "p.pdf"
            pdf.write_bytes(b"%PDF-1.5 test")
            man = Path(t) / "m.json"
            man.write_text(json.dumps({"a": "1", "b": "2"}))
            out = Path(t) / "snap"
            S.main([str(out), "--venue", "FSE2027", "--paper-id", "123", "--pdf", str(pdf), "--artifact-manifest", str(man),
                    "--date", "2027-01-01", "--commit", "abc"])
            rec = json.loads((out / "SUBMISSION.json").read_text())
            self.assertEqual(rec["paper_pdf_sha256"], S.sha(pdf))
            self.assertEqual((rec["artifact_files"], rec["commit"], rec["date"]), (2, "abc", "2027-01-01"))
            self.assertTrue((out / "paper.pdf").is_file())
            with self.assertRaises(SystemExit):
                S.main([str(out), "--venue", "FSE2027", "--paper-id", "123", "--pdf", str(pdf)])


if __name__ == "__main__":
    unittest.main()
