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


class RealLayoutTests(unittest.TestCase):
    """Exercise the real-target path offline: src/ layout, function anchor, function replay."""

    def test_src_layout_anchor_and_function_replay(self):
        import json
        import tempfile
        from gatekeeper_lite.eprocess import AlphaLedger
        from gatekeeper_lite.gatekeeper import replay, run_pair
        from gatekeeper_lite.skill import Skill, Target

        core = ('class Option:\n'
                '    def get_help_record(self, default_value):\n'
                '        if default_value == "":\n'
                '            return \'""\'\n'
                '        return str(default_value)\n\n'
                'def unrelated(x):\n'
                '    return x == ""\n')
        fixed = core.replace('if default_value == "":',
                             'if isinstance(default_value, str) and default_value == "":')
        fixed = fixed.replace('return x == ""', 'return x == ""  # touched elsewhere')
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "t" / "src" / "pkg").mkdir(parents=True)
            (tmp / "t" / "src" / "pkg" / "__init__.py").write_text("")
            (tmp / "t" / "src" / "pkg" / "core.py").write_text(core)
            (tmp / "t" / "oracle_cases.py").write_text(
                "from pkg.core import Option\n"
                "class S:\n    def __eq__(self, o):\n        raise ValueError\n"
                "    __hash__ = object.__hash__\n    def __str__(self):\n        return 's'\n"
                "def cases():\n"
                "    return [('plain', lambda: Option().get_help_record('a')),\n"
                "            ('strict', lambda: Option().get_help_record(S()))]\n")
            (tmp / "t" / "gk_target.json").write_text(json.dumps({
                "target_id": "t", "module": "src/pkg/core.py", "pythonpath": ["src"],
                "python": "3.12", "packages": {}, "scope": "s"}))
            (tmp / "before.py").write_text(core)
            (tmp / "after.py").write_text(fixed)
            (tmp / "skill.json").write_text(json.dumps({
                "skill_id": "k", "version": "1", "scope": "s",
                "pi": {"transform": "empty_string_guard",
                       "params": {"functions": ["get_help_record"]}},
                "D": {"python": ">=3.8"}, "I": ["single_site"], "K": {},
                "P": [{"before": "before.py", "after": "after.py",
                       "compare_function": "get_help_record"}]}))
            skill = Skill.load(tmp / "skill.json")
            self.assertTrue(replay(skill)["passed"])
            rec = run_pair("k@s", [skill], Target.load(tmp / "t"),
                           AlphaLedger(0.1, {"k@s": 0.05}),
                           {"theta": 0.1, "seed": 1, "budget_tasks": 2})
            self.assertTrue(rec["bind"]["ok"], rec["bind"]["reason"])
            self.assertEqual(rec["ground_truth"], "BENEFICIAL")
            self.assertTrue(rec["paired"]["integrity_ok"])
            self.assertEqual(rec["comparators"]["B6R"]["decision"], "ADMIT")


class EmbeddedPayloadTests(unittest.TestCase):
    def test_extract_xz_zip_payload_from_workflow(self):
        import base64, importlib.util, io, lzma, tempfile, zipfile
        spec = importlib.util.spec_from_file_location(
            "extract_tool", ROOT / "tools" / "extract_embedded_payload.py")
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("binder/anchored_binder.py", "print('v3')\n")
        b64 = base64.b64encode(lzma.compress(buf.getvalue())).decode()
        wrapped = "\n          ".join(b64[i:i + 76] for i in range(0, len(b64), 76))
        yaml = ("jobs:\n  x:\n    steps:\n      - run: |\n          python3 - <<'PY'\n"
                f"          transport = base64.b64decode('''{wrapped}''')\n          PY\n")
        with tempfile.TemporaryDirectory() as tmp:
            wf = Path(tmp) / "wf.yml"
            wf.write_text(yaml)
            manifest = tool.extract(wf, Path(tmp) / "out")
            self.assertEqual(manifest["payloads"][0]["kind"], "zip")
            self.assertEqual(read(Path(tmp) / "out" / "binder" / "anchored_binder.py"), "print('v3')\n")


class P73WrapperTests(unittest.TestCase):
    def test_v3_wrapper_abstains_outside_scope_and_checks_freeze(self):
        ext = T.ExternalCommand(command="{python} " + str(ROOT / "p7" / "p73_binder_cli.py")
                                + " --in {input} --out {output} --receipt {receipt}")
        with self.assertRaises(T.Abstain) as ctx:
            ext.apply("def f(x):\n    return x == ''\n")
        self.assertEqual(ctx.exception.reason, "ABSTAIN_SCOPE_MISMATCH")


class ReachPluginTests(unittest.TestCase):
    def test_junit_id_and_tracer(self):
        import importlib, os, sys
        os.environ["GK_REACH_FUNCS"] = "target_fn"
        os.environ["GK_REACH_FILE"] = "test_core.py"
        import gatekeeper_lite.pytest_reach as reach
        reach = importlib.reload(reach)
        self.assertEqual(reach.junit_id("tests/test_options.py::test_a[x-1]"),
                         "tests.test_options::test_a[x-1]")
        self.assertEqual(reach.junit_id("tests/test_x.py::Cls::test_b"), "tests.test_x.Cls::test_b")

        def target_fn():
            return 1

        class Item:
            nodeid = "tests/test_options.py::test_reach"
        reach.pytest_runtest_setup(Item())
        target_fn()
        reach.pytest_runtest_teardown(Item(), None)
        self.assertIn("tests.test_options::test_reach", reach._state["reached"])

    def test_filter_without_reaching_tasks_quarantines(self):
        from gatekeeper_lite.gatekeeper import BindOutcome, gatekeeper
        from gatekeeper_lite.runner import ArmResult, PairedRun
        from gatekeeper_lite.skill import Target
        base = ArmResult("baseline", {"a": {"passed": False}}, 0, {})
        treat = ArmResult("treatment", {"a": {"passed": True}}, 0, {})
        run = PairedRun(base, treat, True)
        tgt = Target.load(TGT / "T1_help_strict")
        res = gatekeeper("c", [], tgt, run, BindOutcome(True, "x"), AlphaLedger(0.1, {"c": 0.05}),
                         {"theta": 0.1, "seed": 1, "budget_tasks": 5}, reached=set())
        self.assertEqual(res.decision, "QUARANTINE")


class DiscordantSignTests(unittest.TestCase):
    def test_admission_type_one_error(self):
        from gatekeeper_lite.eprocess import DiscordantSignEProcess
        rng, alpha, sims, crossed = random.Random(11), 0.05, 3000, 0
        for _ in range(sims):
            ep = DiscordantSignEProcess(q0=0.6)
            for _ in range(200):
                u = rng.random()
                z = 0.0 if u < 0.7 else (-1.0 if rng.random() < 0.6 else 1.0)   # q = q0
                if ep.update(z) >= 1 / alpha:
                    crossed += 1
                    break
        self.assertLessEqual(crossed / sims, alpha + 0.012)

    def test_harm_type_one_error(self):
        from gatekeeper_lite.eprocess import DiscordantSignEProcess
        rng, alpha, sims, flagged = random.Random(5), 0.05, 3000, 0
        for _ in range(sims):
            ep = DiscordantSignEProcess(eps=0.05)
            for _ in range(200):
                z = -1.0 if rng.random() < 0.95 else 1.0                      # h = eps
                ep.update(z)
                if ep.harm_value >= 1 / alpha:
                    flagged += 1
                    break
        self.assertLessEqual(flagged / sims, alpha + 0.012)

    def test_ties_cost_nothing_and_clear_benefit_admits(self):
        from gatekeeper_lite.eprocess import DiscordantSignEProcess
        ep = DiscordantSignEProcess(q0=0.6)
        for _ in range(100):
            ep.update(0.0)
        self.assertEqual(ep.value, 1.0)
        n = 0
        while ep.value < 1 / 0.009:
            ep.update(-1.0)
            n += 1
        self.assertLessEqual(n, 12)

    def test_priority_order_is_outcome_independent(self):
        from gatekeeper_lite.gatekeeper import _ordered_tasks
        ids = ["t::a", "t::gk_boundary[x]", "t::b", "t::gk_boundary[y]"]
        order = _ordered_tasks(ids, 3, ["gk_boundary"])
        self.assertEqual(set(order[:2]), {"t::gk_boundary[x]", "t::gk_boundary[y]"})
        self.assertEqual(order, _ordered_tasks(ids, 3, ["gk_boundary"]))


class FreezeLockTests(unittest.TestCase):
    def test_draft_study_b_refuses_to_run(self):
        with self.assertRaises(SystemExit):
            run_experiment(ROOT / "study_b" / "config_study_b.json")

    def test_family_anchor_matches_help_default_functions_only(self):
        src = ("def _get_parameter_default(param, default_value):\n"
               "    if default_value == '':\n        return '\"\"'\n"
               "def _metavar(m):\n    return m == ''\n"
               "def confirm(value):\n    return value == ''\n")
        t = T.EmptyStringGuard(functions=["get_help_extra"], function_patterns=["default"],
                               subjects=["default_value"])
        res = t.apply(src)
        self.assertEqual([s.function for s in res.sites], ["_get_parameter_default"])
