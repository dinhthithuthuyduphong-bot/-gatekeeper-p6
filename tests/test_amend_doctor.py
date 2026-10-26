import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import amend_doctor as A  # noqa: E402

EDITS = "'config_s.json:extra_tracked=[\"tools/a.py\",\"s/GATES.md\"]'\n"


def tree(tmp, status="FROZEN", amendments="## S-A1 text", edits=EDITS, files=("tools/a.py", "s/GATES.md"), applied=()):
    root = Path(tmp)
    (root / "s").mkdir()
    (root / "s" / "config_s.json").write_text(json.dumps({"status": status, "extra_tracked": [], "amendments_applied": list(applied)}))
    (root / "s" / "AMENDMENTS.md").write_text(amendments)
    (root / "s" / "FREEZE.json").write_text(json.dumps({"files": {}}))
    (root / "s" / "S_A1_EDITS.txt").write_text(edits)
    for f in files:
        p = root / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x")
    return root


def blockers(items):
    return [m for lvl, m in items if lvl == "BLOCKER"]


class Doctor(unittest.TestCase):
    def run_check(self, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            root = tree(tmp, **{k: v for k, v in kw.items() if k in ("status", "amendments", "edits", "files", "applied")})
            return A.check("s", "S-A1", "S_A1_EDITS.txt", root=root, tags=kw.get("tags", []))

    def test_clean_case_has_no_blockers(self):
        self.assertEqual(blockers(self.run_check()), [])

    def test_each_failure_mode_is_reported(self):
        self.assertTrue(any("FROZEN" in m for m in blockers(self.run_check(status="DRAFT"))))
        self.assertTrue(any("NOT documented" in m for m in blockers(self.run_check(amendments="nothing"))))
        self.assertTrue(any("already applied" in m for m in blockers(self.run_check(applied=["S-A1"]))))
        self.assertTrue(any("missing" in m for m in blockers(self.run_check(files=("tools/a.py",)))))
        self.assertTrue(any("tag s-s-a1 already exists" in m for m in blockers(self.run_check(tags=["s-s-a1"]))))
        self.assertTrue(any("not valid JSON" in m for m in blockers(self.run_check(edits="'config_s.json:extra_tracked=[oops'\n"))))
        self.assertTrue(any("cannot be parsed" in m for m in blockers(self.run_check(edits="'unterminated\n"))))

    def test_a_draft_config_next_to_a_freeze_record_points_to_the_restore_tool(self):
        items = self.run_check(status="DRAFT")
        self.assertTrue(any(lvl == "INFO" and "overwritten" in m and "restore" in m for lvl, m in items))

    def test_folder_extracted_into_a_subfolder_is_recognised(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "wrapper" / "s").mkdir(parents=True)
            items = A.check("s", "S-A1", "x", root=tmp, tags=[])
            self.assertIn("does not exist at the repository root", items[0][1])

    def test_failing_tests_are_listed_from_a_unittest_log(self):
        log = "FAIL: test_x (tests.test_a.Case)\nERROR: test_y (tests.test_b.Other)\n----\nRan 3 tests\n"
        self.assertEqual(A.failing_tests(log), ["test_x (tests.test_a.Case)", "test_y (tests.test_b.Other)"])
        self.assertIn("BLOCKERS: 2", A.render([], A.failing_tests(log)))


if __name__ == "__main__":
    unittest.main()
