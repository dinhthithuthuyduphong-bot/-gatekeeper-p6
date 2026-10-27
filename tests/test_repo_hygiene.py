import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import repo_hygiene as H  # noqa: E402


class Hygiene(unittest.TestCase):
    def test_root_duplicates_and_lone_root_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)
            for rel in ("tools/vet_dev.py", "tests/test_vet_target2.py", ".github/workflows/x.yml", "README.md"):
                (r / rel).parent.mkdir(parents=True, exist_ok=True)
                (r / rel).write_text("x")
            for name in ("vet_dev.py", "test_vet_target2.py", "x.yml", "test_orphan.py"):
                (r / name).write_text("old")
            dup, lone = H.strays(r)
            self.assertEqual([n for n, _ in dup], ["test_vet_target2.py", "vet_dev.py", "x.yml"])
            self.assertEqual(lone, ["test_orphan.py"])
            self.assertNotIn("README.md", [n for n, _ in dup])          # a normal root file is left alone

    def test_this_repository_is_clean(self):
        dup, lone = H.strays(ROOT)
        self.assertEqual((dup, lone), ([], []))


if __name__ == "__main__":
    unittest.main()
