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

    def test_enabling_edge_joins_disjoint_footprints(self):
        # Study R2, pydal: type_eq_isinstance creates a site for the bool guard in a function the guard did not touch
        fp = {"guard": ["func:a"], "typeeq": ["func:b"]}
        self.assertEqual(len(X.components(fp)), 2)
        self.assertEqual(X.components(fp, edges=[("typeeq", "guard")]), [F({"guard", "typeeq"})])
        singles = [F({"guard"}), F({"typeeq"})]
        self.assertTrue(X.check_execution(fp, singles).allowed)
        self.assertFalse(X.check_execution(fp, singles, edges=[("guard", "typeeq")]).allowed)
        self.assertEqual(X.composites_to_test(fp, singles, edges=[("guard", "typeeq")]), [F({"guard", "typeeq"})])
        self.assertEqual(len(X.executable_subset(fp, singles, edges=[("guard", "typeeq")])), 1)

    def test_module_level_edits_of_one_file_overlap(self):
        # TC5: the frozen tag func:<module> is dropped; qualified site footprints keep module-level regions per file
        a = X.site_footprint([{"module": "m.py", "function": "<module>"}])
        b = X.site_footprint([{"module": "m.py", "function": "<module>"}, {"module": "m.py", "function": "f"}])
        c = X.site_footprint([{"module": "n.py", "function": "<module>"}])
        self.assertEqual(X.components({"a": a, "b": b, "c": c}), [F({"a", "b"}), F({"c"})])
        self.assertEqual(len(X.components({"a": ["func:<module>"], "b": ["func:<module>"]})), 2)   # the frozen behaviour

    def test_canonical_order_is_registration_order(self):
        self.assertEqual(X.canonical_order({"b", "a", "c"}, ["c", "a", "b"]), ["c", "a", "b"])
        with self.assertRaises(KeyError):
            X.canonical_order({"z"}, ["a"])


if __name__ == "__main__":
    unittest.main()
