"""Regression checks prepared for CI; these fixtures are not research outcomes."""
from pathlib import Path
import tempfile
import unittest

from next_evidence.site_coverage import site_rows
from next_evidence.review_bundle import build


class FakeTraceData:
    def __init__(self, path, lines, contexts):
        self.path, self.raw_lines, self.contexts = str(path), lines, contexts

    def measured_files(self): return [self.path]
    def lines(self, path): return self.raw_lines
    def contexts_by_lineno(self, path): return self.contexts


class PhysicalSiteCoverage(unittest.TestCase):
    def rows(self, lines, contexts):
        source = Path("/pinned/source")
        data = FakeTraceData(source / "utils.py", lines, contexts)
        return site_rows(data, source, [{"file": "utils.py", "line": 449}])

    def test_continuation_line_uses_raw_trace(self):
        rows = self.rows([447, 449], {447: ["t|call"], 449: ["t|call"]})
        self.assertTrue(rows[0]["executed"])
        self.assertEqual(rows[0]["test_call_contexts"], ["t"])

    def test_neighboring_statement_does_not_prove_site_reach(self):
        row = self.rows([447], {447: ["t|call"]})[0]
        self.assertFalse(row["executed"])
        self.assertEqual(row["test_call_contexts"], [])

    def test_inconsistent_raw_trace_is_rejected(self):
        with self.assertRaises(ValueError):
            self.rows([447], {449: ["t|call"]})

    def test_setup_reach_is_not_call_reach(self):
        row = self.rows([449], {449: ["t|setup"]})[0]
        self.assertTrue(row["executed"])
        self.assertFalse(row["executed_in_test_call"])

    def test_compact_bundle_preserves_evidence_and_discloses_omissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / "raw"
            raw.mkdir()
            (raw / "coverage.data").write_bytes(b"synthetic raw file")
            (raw / "SESSION.json").write_text('{"fixture": true}')
            report = build(raw, root / "review")
            self.assertEqual((report["included_files"], report["omitted_files"]), (1, 1))
            self.assertTrue((raw / "coverage.data").is_file())
            self.assertFalse((root / "review/coverage.data").exists())
            self.assertEqual((root / "review/SESSION.json").read_bytes(), (raw / "SESSION.json").read_bytes())
            self.assertEqual(len(report["files"][0]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
