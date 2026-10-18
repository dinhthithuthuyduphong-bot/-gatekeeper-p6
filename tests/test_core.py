import random
import unittest
from pathlib import Path

from gatekeeper_lite import transforms as T
from gatekeeper_lite.eprocess import AlphaLedger, BettingEProcess
from gatekeeper_lite.experiment import run_experiment
from gatekeeper_lite.runner import parse_junit
from gatekeeper_lite.screen import DRIFT, MATCH, UNRESOLVED, environment_relation, satisfies

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "demo" / "sources"
TGT = ROOT / "demo" / "targets"


def read(p):
    return Path(p).read_text(encoding="utf-8")


class TransformTests(unittest.TestCase):
    def test_empty_string_guard_replays_source_fix(self):
        out = T.EmptyStringGuard().apply(read(SRC / "help_before.py")).source
        self.assertTrue(T.ast_equal(out, read(SRC / "help_after.py")))

    def test_second_application_abstains(self):
        once = T.EmptyStringGuard().apply(read(SRC / "help_before.py")).source
        with self.assertRaises(T.Abstain) as ctx:
            T.EmptyStringGuard().apply(once)
        self.assertEqual(ctx.exception.reason, "ALREADY_GUARDED")

    def test_abstain_reasons(self):
        cases = {
            "ALREADY_GUARDED": read(TGT / "T3_help_guarded" / "helpfmt.py"),
            "BUILTIN_SHADOWED": read(TGT / "T4_help_shadow" / "helpfmt.py"),
            "MULTIPLE_MATCHES": "def f(a, b):\n    return a == '' or b == ''\n",
            "NO_MATCH": "def f(a):\n    return a\n",
        }
        for reason, source in cases.items():
            with self.subTest(reason=reason), self.assertRaises(T.Abstain) as ctx:
                T.EmptyStringGuard().apply(source)
            self.assertEqual(ctx.exception.reason, reason)

    def test_rewrite_keeps_rest_of_file(self):
        src = "# keep me\nx = 1  # and me\n\ndef f(v):\n    return v == ''\n"
        out = T.EmptyStringGuard().apply(src).source
        self.assertIn("# keep me", out)
        self.assertIn("# and me", out)

    def test_negative_type_guard(self):
        out = T.NegativeTypeGuard("int", "bool").apply(read(SRC / "status_before.py")).source
        self.assertTrue(T.ast_equal(out, read(SRC / "status_after.py")))
        tup = "def f(v):\n    if isinstance(v, (int, float)):\n        return v\n"
        self.assertIn("not isinstance(v, bool)", T.NegativeTypeGuard().apply(tup).source)
        with self.assertRaises(T.Abstain):
            T.NegativeTypeGuard().apply(
                "def f(v):\n    if isinstance(v, int) and not isinstance(v, bool):\n        return v\n")

    def test_retry_requires_exception_symbol(self):
        with self.assertRaises(T.Abstain) as ctx:
            T.RetryWrap().apply("def push(c, x):\n    c.write(x)\n")
        self.assertEqual(ctx.exception.reason, "MISSING_SYMBOL")
        out = T.RetryWrap().apply(read(SRC / "retry_before.py")).source
        self.assertTrue(T.ast_equal(out, read(SRC / "retry_after.py")))

    def test_composition_order(self):
        src = read(TGT / "T7_db_save" / "store.py")
        both = T.RetryWrap().apply(T.AsyncWrite().apply(src).source).source
        self.assertIn("_gk_retry(lambda: db.write_async(record), TransientError, 3)", both)

    def test_footprint_overlap(self):
        src = read(TGT / "T7_db_save" / "store.py")
        k1 = set(T.RetryWrap().apply(src).footprint)
        k2 = set(T.AsyncWrite().apply(src).footprint)
        self.assertIn("func:save", k1 & k2)


class ScreenTests(unittest.TestCase):
    def test_version_specs(self):
        self.assertTrue(satisfies("3.12", ">=3.9,<3.13"))
        self.assertFalse(satisfies("3.13", ">=3.9,<3.13"))
        self.assertTrue(satisfies("8.1.7", ">=8,<9"))

    def test_relations(self):
        contract = {"python": ">=3.9", "packages": {"lib": ">=1,<2"}}
        self.assertEqual(environment_relation(contract, {"python": "3.12", "packages": {"lib": "1.4"}})[0], MATCH)
        self.assertEqual(environment_relation(contract, {"python": "3.12", "packages": {"lib": "2.0"}})[0], DRIFT)
        self.assertEqual(environment_relation(contract, {"python": "3.12", "packages": {}})[0], UNRESOLVED)
        self.assertEqual(environment_relation({}, {"python": "3.12"})[0], UNRESOLVED)


class EProcessTests(unittest.TestCase):
    def test_type_one_error_under_null(self):
        """Under H0 (E[-Z] < theta) the crossing rate must stay <= alpha (Ville)."""
        rng, alpha, theta, sims, crossed = random.Random(7), 0.05, 0.1, 2000, 0
        for _ in range(sims):
            ep = BettingEProcess(theta)
            for _ in range(150):
                # mean of Y = -Z is 0.08 < theta
                y = 1.0 if rng.random() < 0.54 else -1.0
                if ep.update(-y) >= 1 / alpha:
                    crossed += 1
                    break
        self.assertLessEqual(crossed / sims, alpha + 0.015)

    def test_power_under_clear_benefit(self):
        rng, hits = random.Random(3), 0
        for _ in range(200):
            ep = BettingEProcess(0.1)
            for _ in range(60):
                z = -1.0 if rng.random() < 0.6 else 0.0
                if ep.update(z) >= 20:
                    hits += 1
                    break
        self.assertGreater(hits, 180)

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            BettingEProcess(0.1).update(1.5)


class LedgerTests(unittest.TestCase):
    def test_no_overallocation_or_recycling(self):
        with self.assertRaises(ValueError):
            AlphaLedger(0.05, {"a": 0.04, "b": 0.02})
        led = AlphaLedger(0.1, {"a": 0.1})
        shares = [led.draw("a", e) for e in range(50)]
        self.assertLessEqual(sum(shares), 0.1)
        with self.assertRaises(ValueError):
            led.draw("a", 0)


class JunitTests(unittest.TestCase):
    def test_parse(self):
        xml = ('<testsuites><testsuite><testcase classname="tests.t" name="a"/>'
               '<testcase classname="tests.t" name="b"><failure message="boom"/></testcase>'
               '<testcase classname="tests.t" name="c"><skipped/></testcase>'
               '</testsuite></testsuites>')
        res = parse_junit(xml)
        self.assertTrue(res["tests.t::a"]["passed"])
        self.assertFalse(res["tests.t::b"]["passed"])
        self.assertNotIn("tests.t::c", res)


class EndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = run_experiment(ROOT / "demo" / "config.json")
        cls.by = {(r["target"], "+".join(r["skills"])): r for r in cls.res["records"]}

    def dec(self, target, skill, comp):
        return self.by[(target, skill)]["comparators"][comp]["decision"]

    def test_beneficial_admitted_harmful_quarantined(self):
        self.assertEqual(self.dec("T1_help_strict", "empty-string-guard", "Gatekeeper"), "ADMIT")
        self.assertEqual(self.by[("T2_help_lazy", "empty-string-guard")]["ground_truth"], "HARMFUL")
        self.assertEqual(self.dec("T2_help_lazy", "empty-string-guard", "B6R"), "ADMIT")
        self.assertNotEqual(self.dec("T2_help_lazy", "empty-string-guard", "Gatekeeper"), "ADMIT")
        self.assertNotEqual(self.dec("T6_count_bool", "negative-bool-guard", "Gatekeeper"), "ADMIT")

    def test_abstentions(self):
        for t in ("T3_help_guarded", "T4_help_shadow"):
            self.assertEqual(self.dec(t, "empty-string-guard", "Gatekeeper"), "OUT_OF_SCOPE")

    def test_pair_integrity(self):
        for r in self.res["records"]:
            if "paired" in r:
                self.assertTrue(r["paired"]["integrity_ok"], r["target"])

    def test_composition(self):
        comp = self.res["compositions"][0]
        self.assertEqual(set(comp["single_truth"].values()), {"BENEFICIAL"})
        self.assertEqual(comp["composite_truth"], "HARMFUL")
        self.assertTrue(comp["footprint_overlap"])
        self.assertNotEqual(comp["gatekeeper_composite_decision"], "ADMIT")

    def test_retirement(self):
        statuses = [r["status"] for r in self.res["retirements"]]
        self.assertTrue(all(s.startswith("REVOKED") for s in statuses), statuses)


if __name__ == "__main__":
    unittest.main()
