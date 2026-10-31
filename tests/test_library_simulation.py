import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import library_simulation as L  # noqa: E402


class LibrarySimulationTest(unittest.TestCase):
    def test_execution_rule_controls_harmful_components(self):
        r = L.run(reps=120, k=12, regions=8, q=0.3, n=300, seed=3)
        self.assertLessEqual(r["P2"]["harmful_component_rate"], 0.1)
        self.assertGreater(r["P1"]["harmful_component_rate"], r["P2"]["harmful_component_rate"])

    def test_group_risk_model(self):
        risk = {"a": -0.3, "b": -0.3, "c": 0.0}
        self.assertEqual(L.group_str({"a", "b"}, risk, {frozenset(("a", "b"))}), L.HARM)
        self.assertAlmostEqual(L.group_str({"a", "b"}, risk, set()), -0.6)


if __name__ == "__main__":
    unittest.main()
