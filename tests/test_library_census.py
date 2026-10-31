import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import library_census as C  # noqa: E402


class LibraryCensusTest(unittest.TestCase):
    def test_twelve_families(self):
        self.assertEqual(len(C.SKILL_FILES), 12)

    def test_pairs_on_a_shared_function_commute_and_nest(self):
        src = "import yaml\ndef f(x):\n    if x == None:\n        return yaml.load(open(x))\n"
        sites, pairs = C.file_pairs(C.load_skills(), src)
        self.assertEqual(set(sites), {"none_identity", "open_encoding", "yaml_safe_load"})
        p = [q for q in pairs if {q["a"], q["b"]} == {"open_encoding", "yaml_safe_load"}][0]
        self.assertTrue(p["shared_function"] and p["commute"] and p["nested"])
        self.assertFalse(p["a_changes_b_sites"] or p["b_changes_a_sites"])

    def test_components_and_composites(self):
        t = C.summarise_target({"a": {("m.py", "f")}, "b": {("m.py", "f"), ("m.py", "g")}, "c": {("n.py", "h")},
                                "d": {("m.py", "<module>")}, "e": set()})
        self.assertEqual(t["cells"], 4)          # e binds nowhere
        self.assertEqual(t["overlapping_pairs"], [["a", "b"]])
        t2 = C.summarise_target({"a": {("m.py", "<module>")}, "b": {("m.py", "<module>")}, "c": {("n.py", "<module>")}})
        self.assertEqual(t2["overlapping_pairs"], [["a", "b"]])   # module-level edits of one file overlap (TC5)
        self.assertEqual(t["composite_cells_required"], 1)
        self.assertEqual(t["largest_component"], 2)


if __name__ == "__main__":
    unittest.main()
