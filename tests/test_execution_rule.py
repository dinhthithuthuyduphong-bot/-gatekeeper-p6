import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_ext import execution as X  # noqa: E402

F = frozenset


class ExecutionRuleTest(unittest.TestCase):
    def setUp(self):
        # A-B overlap on f, B-C overlap on g, A-C disjoint: one component {A, B, C}; D is alone
        self.fp = {"A": ["func:f"], "B": ["func:f", "func:g"], "C": ["func:g"], "D": ["func:h"]}

    def test_components_are_transitive(self):
        self.assertEqual(X.components(self.fp), [F({"A", "B", "C"}), F({"D"})])

    def test_generic_module_tag_is_not_an_overlap(self):
        self.assertEqual(len(X.components({"A": ["func:<module>"], "B": ["func:<module>"]})), 2)

    def test_individual_admissions_are_not_enough(self):
        d = X.check_execution(self.fp, [F({"A"}), F({"B"}), F({"C"}), F({"D"})])
        self.assertFalse(d.allowed)
        self.assertEqual(d.missing, [F({"A", "B", "C"})])
        self.assertEqual(X.composites_to_test(self.fp, [F({"A"}), F({"B"}), F({"C"})]), [F({"A", "B", "C"})])

    def test_a_pairwise_composite_does_not_cover_the_triple(self):
        self.assertFalse(X.check_execution(self.fp, [F({"A", "B"}), F({"B", "C"}), F({"D"})]).allowed)

    def test_admitted_component_runs(self):
        d = X.check_execution(self.fp, [F({"A", "B", "C"}), F({"D"})])
        self.assertTrue(d.allowed, d.explain())

    def test_disjoint_skills_need_only_their_own_admission(self):
        self.assertTrue(X.check_execution({"A": ["func:f"], "D": ["func:h"]}, [F({"A"}), F({"D"})]).allowed)

    def test_greedy_subset_respects_the_rule(self):
        # B is admitted alone, but adding A next to B needs {A, B}: greedy in order B, A, C, D keeps B and D
        self.assertEqual(X.executable_subset(self.fp, [F({"A"}), F({"B"}), F({"C"}), F({"D"})], ["B", "A", "C", "D"]), ["B", "D"])

    def test_property_random_libraries(self):
        rng = random.Random(4)
        for _ in range(300):
            ids = ["s%d" % i for i in range(rng.randint(1, 7))]
            fp = {i: ["r%d" % rng.randint(0, 5) for _ in range(rng.randint(1, 2))] for i in ids}
            admitted = [F({i}) for i in ids if rng.random() < 0.7] + \
                       [F(rng.sample(ids, k)) for k in range(2, len(ids) + 1) if rng.random() < 0.3]
            chosen = X.executable_subset(fp, admitted)
            d = X.check_execution({k: fp[k] for k in chosen}, admitted)
            self.assertTrue(d.allowed)                                   # the greedy result always satisfies the rule
            for comp in d.components:                                    # and every component is literally admitted
                self.assertIn(comp, {F(c) for c in admitted})


if __name__ == "__main__":
    unittest.main()
