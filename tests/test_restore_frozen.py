import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import restore_frozen_file as R  # noqa: E402

FROZEN = json.dumps({"status": "FROZEN", "frozen_on": "2026-10-26T01:02:03Z", "seed_time_utc": "2026-10-26T02:02:03Z"}, indent=2)
DRAFT = json.dumps({"status": "DRAFT", "seed_time_utc": "SET_AT_FREEZE"}, indent=2)


def git(root, *a):
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=n", *a], cwd=root, check=True, capture_output=True)


def make(tmp, freeze_hash=None):
    root = Path(tmp)
    d = root / "s"
    d.mkdir()
    (d / "config_s.json").write_text(FROZEN)
    h = freeze_hash or hashlib.sha256(FROZEN.encode()).hexdigest()
    (d / "FREEZE.json").write_text(json.dumps({"files": {"s/config_s.json": h}}, indent=2))
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "freeze")
    git(root, "tag", "s-freeze")
    return root


class Restore(unittest.TestCase):
    def test_overwritten_config_is_restored_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make(tmp)
            (root / "s" / "config_s.json").write_text(DRAFT)                  # the package overwrote it
            msg = R.restore("s", "s-freeze", root=root)
            self.assertIn("restored", msg)
            self.assertEqual((root / "s" / "config_s.json").read_text(), FROZEN)
            self.assertIn("already identical", R.restore("s", "s-freeze", root=root))

    def test_refused_when_the_tag_version_does_not_match_the_recorded_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make(tmp, freeze_hash="0" * 64)
            (root / "s" / "config_s.json").write_text(DRAFT)
            with self.assertRaises(SystemExit) as cm:
                R.restore("s", "s-freeze", root=root)
            self.assertIn("REFUSED", str(cm.exception))
            self.assertEqual((root / "s" / "config_s.json").read_text(), DRAFT)   # nothing was written

    def test_refused_when_the_freeze_record_itself_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make(tmp)
            (root / "s" / "FREEZE.json").write_text(json.dumps({"files": {}}))
            with self.assertRaises(SystemExit) as cm:
                R.restore("s", "s-freeze", root=root)
            self.assertIn("FREEZE.json differs", str(cm.exception))

    def test_refused_for_a_file_that_was_never_hashed_and_for_a_bad_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make(tmp)
            with self.assertRaises(SystemExit):
                R.restore("s", "s-freeze", "s/GATES.md", root=root)
            with self.assertRaises(SystemExit):
                R.restore("s", "no-such-tag", root=root)


if __name__ == "__main__":
    unittest.main()
