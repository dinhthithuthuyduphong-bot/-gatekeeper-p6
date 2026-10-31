import gzip
import io
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import make_anonymous_artifact as A  # noqa: E402


class AnonymousArtifactTest(unittest.TestCase):
    def test_scan_finds_identifiers_in_text_and_archives(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "a.txt"
            p.write_text("run by SomeOwner today")
            self.assertEqual(A.scan_file(p, {"someowner"}), ["someowner"])
            g = Path(t) / "b.jsonl.gz"
            g.write_bytes(gzip.compress(b'{"x": "someowner"}'))
            self.assertEqual(A.scan_file(g, {"someowner"}), ["someowner"])
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode="w:gz") as tf:
                data = b"hello someowner"
                info = tarfile.TarInfo("inner.txt")
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))
            tg = Path(t) / "c.tar.gz"
            tg.write_bytes(buf.getvalue())
            self.assertEqual(A.scan_file(tg, {"someowner"}), ["someowner"])
            clean = Path(t) / "d.txt"
            clean.write_text("nothing here")
            self.assertEqual(A.scan_file(clean, {"someowner"}), [])

    def test_internal_notes_and_draft_pdfs_are_excluded(self):
        for rel in ("docs/PROCESS_LOG.md", "docs/paper/source/01-FSE-2027-13-paper.pdf", "archive/root_packages/x.py", ".git/config"):
            self.assertTrue(A.excluded(rel), rel)
        self.assertFalse(A.excluded("gatekeeper_lite/eprocess.py"))


if __name__ == "__main__":
    unittest.main()
