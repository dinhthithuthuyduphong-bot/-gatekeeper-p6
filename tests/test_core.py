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
    def test_draft_study_refuses_to_run(self):
        import json, tempfile
        cfg = json.loads((ROOT / "study_b" / "config_study_b.json").read_text())
        cfg["status"] = "DRAFT"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps(cfg))
            with self.assertRaises(SystemExit):
                run_experiment(path)

    def test_family_anchor_matches_help_default_functions_only(self):
        src = ("def _get_parameter_default(param, default_value):\n"
               "    if default_value == '':\n        return '\"\"'\n"
               "def _metavar(m):\n    return m == ''\n"
               "def confirm(value):\n    return value == ''\n")
        t = T.EmptyStringGuard(functions=["get_help_extra"], function_patterns=["default"],
                               subjects=["default_value"])
        res = t.apply(src)
        self.assertEqual([s.function for s in res.sites], ["_get_parameter_default"])


class EBHTests(unittest.TestCase):
    def test_e_bh(self):
        from gatekeeper_lite.eprocess import e_bh
        # K=4, fdr=0.1: thresholds 40 (R=1), 20 (R=2), 13.3 (R=3), 10 (R=4)
        self.assertEqual(e_bh({"a": 45, "b": 1, "c": 0, "d": 0}, 0.1), ["a"])
        self.assertEqual(sorted(e_bh({"a": 25, "b": 21, "c": 0, "d": 0}, 0.1)), ["a", "b"])
        self.assertEqual(e_bh({"a": 39, "b": 1, "c": 0, "d": 0}, 0.1), [])
        self.assertEqual(sorted(e_bh({"a": 11, "b": 12, "c": 10.5, "d": 10}, 0.1)), ["a", "b", "c", "d"])


class OracleGroupTests(unittest.TestCase):
    def test_broken_group_is_recorded_not_fatal(self):
        from gatekeeper_lite.runner import run_oracle_groups

        def fake(snapshot, tests, env, timeout, args=None, junit_name=""):
            if tests == ["tests"]:
                raise RuntimeError("ImportError while loading conftest")
            return {"gk_oracle::t[a]": {"passed": True}}
        oracle = {"kind": "pytest", "groups": [{"tests": ["gk_oracle/x.py"]}, {"tests": ["tests"]}]}
        res, errors = run_oracle_groups(Path("."), oracle, {}, 5, runner=fake)
        self.assertEqual(list(res), ["gk_oracle::t[a]"])
        self.assertIn("conftest", errors[0])

    def test_all_groups_broken_raises(self):
        from gatekeeper_lite.runner import run_oracle_groups

        def fake(*a, **k):
            raise RuntimeError("boom")
        with self.assertRaises(RuntimeError):
            run_oracle_groups(Path("."), {"kind": "pytest", "tests": ["t"]}, {}, 5, runner=fake)


class ScopedAdmissionTests(unittest.TestCase):
    def test_same_skill_admitted_in_safe_scope_blocked_in_risky_scope(self):
        import json, tempfile
        cfg = json.loads((ROOT / "demo" / "config.json").read_text())
        cfg.update({"evidence": "discordant_sign", "budget_tasks": 40,
                    "multiplicity": {"method": "e-BH", "fdr": 0.1, "harm_alpha": 0.05},
                    "scopes": {"objects": ["strict_eq", "array_like"], "lazy": ["lazy_"]},
                    "pairs": [{"skills": ["empty-string-guard"], "target": "T1_help_strict"},
                              {"skills": ["empty-string-guard"], "target": "T2_help_lazy"}],
                    "compositions": [], "retirement": []})
        cfg["cells"] = {f"empty-string-guard@{s}/{k}": 0.01
                        for s in ("help/object-defaults", "help/lazy-text-defaults")
                        for k in ("objects", "lazy")}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            cfg["skills_dir"] = str(ROOT / "demo" / "skills")
            cfg["targets_dir"] = str(ROOT / "demo" / "targets")
            path.write_text(json.dumps(cfg))
            res = run_experiment(path)
        by = {(r["target"], r["scope_class"]): r for r in res["records"]}
        self.assertEqual(by[("T1_help_strict", "objects")]["gatekeeper"]["decision"], "ADMIT")
        self.assertEqual(by[("T2_help_lazy", "lazy")]["ground_truth"], "HARMFUL")
        self.assertEqual(by[("T2_help_lazy", "lazy")]["gatekeeper"]["decision"], "REJECT_HARM")
        self.assertEqual({r["comparators"]["B6R"]["decision"] for r in res["records"]
                          if r["target"] == "T2_help_lazy"}, {"ADMIT"})


class StudyDStatsTests(unittest.TestCase):
    def test_harm_certificate_valid_at_boundary(self):
        from gatekeeper_lite.eprocess import HarmCertEProcess
        rng, alpha, sims, false = random.Random(17), 0.05, 3000, 0
        for _ in range(sims):
            ep = HarmCertEProcess(eta=0.05)
            for _ in range(400):
                if ep.update(rng.random() < 0.05) >= 1 / alpha:   # h exactly eta (H0 true)
                    false += 1
                    break
        self.assertLessEqual(false / sims, alpha + 0.012)

    def test_harm_certificate_needs_many_clean_draws(self):
        from gatekeeper_lite.eprocess import HarmCertEProcess
        ep, n = HarmCertEProcess(eta=0.05), 0
        while ep.value < 80:
            ep.update(False)
            n += 1
        self.assertGreater(n, 70)      # ~ln(80)/-ln(1-0.9*0.05/0.95)

    def test_e_holm(self):
        from gatekeeper_lite.eprocess import e_holm
        # K=4, alpha=0.1: a single cell needs e >= K/alpha = 40 (e-Bonferroni level)
        self.assertEqual(e_holm({"a": 50, "b": 0, "c": 0, "d": 0}, 0.1), ["a"])
        self.assertEqual(e_holm({"a": 30, "b": 0, "c": 0, "d": 0}, 0.1), [])
        # Holm gain: two strong cells help each other (30 < 40 alone)
        self.assertEqual(sorted(e_holm({"a": 30, "b": 30, "c": 0, "d": 0}, 0.1)), ["a", "b"])
        self.assertEqual(sorted(e_holm({"a": 50, "b": 50, "c": 0, "d": 0}, 0.1)), ["a", "b"])


class BoolGuardFamilyTests(unittest.TestCase):
    def test_negated_and_multi_site_and_idempotent(self):
        src = ("def validate_number(v):\n"
               "    if not isinstance(v, (int, float)):\n"
               "        raise TypeError('number')\n"
               "    return v\n\n"
               "def coerce(n):\n"
               "    return isinstance(n, int)\n")
        out = T.NegativeTypeGuard("int", "bool").apply(src, single_site=False).source
        ns = {}
        exec(compile(out, "<t>", "exec"), ns)
        with self.assertRaises(TypeError):
            ns["validate_number"](True)
        self.assertEqual(ns["validate_number"](3), 3)
        self.assertFalse(ns["coerce"](True))
        self.assertTrue(ns["coerce"](5))
        with self.assertRaises(T.Abstain) as ctx:
            T.NegativeTypeGuard("int", "bool").apply(out, single_site=False)
        self.assertIn(ctx.exception.reason, ("ALREADY_GUARDED", "NO_APPLICABLE_SITE"))
        upstream_style = "def f(v):\n    if not isinstance(v, int) or isinstance(v, bool):\n        raise TypeError\n"
        with self.assertRaises(T.Abstain):
            T.NegativeTypeGuard("int", "bool").apply(upstream_style, single_site=False)


class DrawHarnessAcceptanceTests(unittest.TestCase):
    """Harness acceptance on development fixtures (never on Study D evaluation targets)."""

    def _run(self, target_dir, oracle):
        from gatekeeper_lite.drawharness import run_draw_study
        from gatekeeper_lite.gatekeeper import bind_modules
        from gatekeeper_lite.skill import Skill, Target
        skill = Skill.load(ROOT / "demo" / "skills" / "negative-bool-guard.json")
        target = Target.load(TGT / target_dir)
        bound = bind_modules([skill], target)
        self.assertTrue(bound["treated"])
        cfg = {"seed": 7, "alpha": 0.1, "n_max": 150, "theta": 0.2, "eta": 0.05}
        return run_draw_study(target, bound["treated"], ROOT / "demo" / "draw_oracles" / oracle,
                              cfg, k_cells=4)

    def test_beneficial_scope_admitted_and_stops_for_real(self):
        res = self._run("T5_port_bool", "port_bool.py")
        bool_scope, int_scope = res["scopes"]["bool"], res["scopes"]["int"]
        self.assertEqual(bool_scope["decision"], "ADMIT")
        self.assertLess(bool_scope["draws"], 150)            # stopped before the budget
        self.assertEqual(int_scope["counts"]["hurt"], 0)     # no regression on ints
        self.assertEqual(int_scope["decision"], "UNDECIDED") # no benefit on ints: not admitted

    def test_harmful_scope_rejected_fast(self):
        res = self._run("T6_count_bool", "count_bool.py")
        self.assertEqual(res["scopes"]["bool"]["decision"], "REJECT_HARM")
        self.assertLessEqual(res["scopes"]["bool"]["draws"], 5)


class B9AcceptanceTests(unittest.TestCase):
    """B9 harness acceptance with a scripted fake model (development fixture T5)."""

    VISIBLE = {"kind": "python", "code": (
        "from config import parse_port\n"
        "try:\n    parse_port(True)\nexcept TypeError:\n    pass\nelse:\n    raise SystemExit(1)\n")}

    def _diff(self, new_line):
        import difflib
        src = read(TGT / "T5_port_bool" / "config.py")
        new = src.replace("    if isinstance(value, int):", new_line, 1)
        lines = difflib.unified_diff(src.splitlines(True), new.splitlines(True),
                                     fromfile="a/config.py", tofile="b/config.py")
        return "diff --git a/config.py b/config.py\n" + "".join(lines)

    def _repair(self, replies, budget=None):
        from gatekeeper_lite.b9 import Budget, ScriptedFakeModel, repair
        from gatekeeper_lite.skill import Target
        target = Target.load(TGT / "T5_port_bool")
        inst = {"issue": "Booleans must not be accepted as ports.", "visible": self.VISIBLE,
                "visible_desc": "parse_port(True) must raise TypeError"}
        return target, repair(target, inst, ScriptedFakeModel(replies), "fake", budget or Budget(),
                              {"input": 0.15, "output": 0.60}, seed=1)

    def _hidden(self, target, treated):
        from gatekeeper_lite.drawharness import run_draw_study
        cfg = {"seed": 3, "alpha": 0.1, "n_max": 60, "theta": 0.2, "eta": 0.05, "b8_full": True}
        res = run_draw_study(target, treated, ROOT / "demo" / "draw_oracles" / "port_bool.py", cfg, 4)
        return {s: v["b8"]["counts"] for s, v in res["scopes"].items()}

    def test_gold_patch_submitted_and_scored_on_hidden_oracle(self):
        target, r = self._repair([self._diff("    if isinstance(value, int) and not isinstance(value, bool):")])
        self.assertEqual(r.status, "SUBMITTED")
        counts = self._hidden(target, r.treated)
        self.assertEqual(counts["bool"]["help"], 60)
        self.assertEqual(counts["int"]["hurt"], 0)
        self.assertGreater(r.cost_usd, 0)

    def test_visible_pass_but_hidden_harm_is_caught(self):
        target, r = self._repair([self._diff("    if isinstance(value, int) and value > 100:")])
        self.assertEqual(r.status, "SUBMITTED")                 # the visible check cannot see it
        self.assertGreater(self._hidden(target, r.treated)["int"]["hurt"], 0)

    def test_bad_replies_and_budget(self):
        outside = "diff --git a/other.py b/other.py\n--- a/other.py\n+++ b/other.py\n@@ -1 +1 @@\n-x\n+y\n"
        broken = "diff --git a/config.py b/config.py\n--- a/config.py\n+++ b/config.py\n@@ -1,1 +1,1 @@\n-nonexistent\n+line\n"
        target, r = self._repair(["I cannot fix this.", outside, broken], budget=__import__(
            "gatekeeper_lite.b9", fromlist=["Budget"]).Budget(max_calls=3))
        self.assertEqual(r.status, "NO_PATCH")
        verdicts = [a["verdict"] for a in r.attempts]
        self.assertEqual(verdicts[0], "NO_DIFF")
        self.assertTrue(verdicts[1].startswith("OUTSIDE_EDIT_RIGHTS"))
        self.assertEqual(verdicts[2], "DOES_NOT_APPLY")
        self.assertEqual(r.calls, 3)

    def test_cassette_replay_never_calls_out(self):
        import tempfile
        from gatekeeper_lite.b9 import CassetteClient, ScriptedFakeModel
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.json"
            rec = CassetteClient(path, "record", ScriptedFakeModel(["hello"]))
            msgs = [{"role": "user", "content": "x"}]
            self.assertEqual(rec.complete("m", msgs, 10, 0.0, 1)["text"], "hello")
            rep = CassetteClient(path, "replay")
            self.assertEqual(rep.complete("m", msgs, 10, 0.0, 1)["text"], "hello")
            with self.assertRaises(KeyError):
                rep.complete("m", msgs, 10, 0.0, 2)


class LargeSeedTests(unittest.TestCase):
    def test_drand_sized_seed_starts_workers(self):
        """drand-derived seeds are ~60-bit; PYTHONHASHSEED must be reduced into [0, 2^32)."""
        from gatekeeper_lite.drawharness import run_draw_study
        from gatekeeper_lite.gatekeeper import bind_modules
        from gatekeeper_lite.skill import Skill, Target
        skill = Skill.load(ROOT / "demo" / "skills" / "negative-bool-guard.json")
        target = Target.load(TGT / "T5_port_bool")
        bound = bind_modules([skill], target)
        cfg = {"seed": int("f" * 15, 16), "alpha": 0.1, "n_max": 5, "theta": 0.2, "eta": 0.05}
        res = run_draw_study(target, bound["treated"], ROOT / "demo" / "draw_oracles" / "port_bool.py", cfg, 4)
        self.assertEqual(res["scopes"]["bool"]["counts"]["harness_error"], 0)


class CensusProtocolTests(unittest.TestCase):
    def _run(self, runs):
        import importlib, sys
        sys.path.insert(0, str(ROOT / "tools"))
        rs = importlib.import_module("run_study_d")
        seq = iter(runs)
        orig = rs._pytest_once
        rs._pytest_once = lambda target, treated, tests, tag: {"results": next(seq), "seconds": 0.1, "exit": 0, "tail": ""}
        try:
            return rs.census(None, {}, ["tests"])
        finally:
            rs._pytest_once = orig

    def test_three_baselines_flaky_excluded_and_retest(self):
        P, F = {"passed": True}, {"passed": False}
        ok = {f"t{i}": P for i in range(6)}
        b1, b2, b3 = dict(ok, flaky=P, bad=F), dict(ok, flaky=F, bad=F), dict(ok, flaky=P, bad=F)
        treat = dict(ok, t0=F, t1=F)                 # two failures with the skill
        retest = dict(ok, t0=F)                      # t1 was transient
        out = self._run([b1, b2, b3, treat, retest])
        self.assertEqual(out["status"], "VALID")
        self.assertEqual(out["excluded_flaky"], ["flaky"])
        self.assertEqual(out["excluded_baseline_failures"], ["bad"])
        self.assertEqual(out["new_failures"], ["t0"])
        self.assertEqual(out["transient_treatment_failures"], ["t1"])

    def test_invalid_when_too_few_stable(self):
        P = {"passed": True}
        out = self._run([{"a": P}, {"a": P}, {"a": P}])
        self.assertEqual(out["status"], "INVALID")


class B9GuardAndVisibleTests(unittest.TestCase):
    def test_spend_guard_blocks_before_overspending(self):
        from gatekeeper_lite.b9 import Budget, ScriptedFakeModel, SpendGuard, repair
        from gatekeeper_lite.skill import Target
        target = Target.load(TGT / "T5_port_bool")
        inst = {"issue": "x" * 3000, "visible": {"kind": "python", "code": "raise SystemExit(1)"},
                "visible_desc": "never passes"}
        guard = SpendGuard(cap_usd=0.0001)
        r = repair(target, inst, ScriptedFakeModel(["no diff"]), "fake", Budget(max_calls=5, max_output_tokens=4000),
                   {"input": 0.30, "output": 1.20}, seed=1, guard=guard)
        self.assertEqual(r.calls, 0)
        self.assertEqual(r.attempts[-1]["verdict"], "BUDGET_CAP")
        self.assertLessEqual(guard.spent_usd, 0.0001)

    def test_oracle_draw_visible_check(self):
        from gatekeeper_lite.b9 import run_visible
        spec = {"kind": "oracle_draw", "oracle": str(ROOT / "demo" / "draw_oracles" / "port_bool.py"),
                "scope": "bool", "draw": {"via": "direct", "arg": True}}
        self.assertFalse(run_visible(TGT / "T5_port_bool", spec, []))   # unpatched: True accepted as port

    def test_b9_allocations_respect_cap(self):
        import json
        c = json.loads((ROOT / "study_d" / "b9_config.json").read_text())
        self.assertLessEqual(sum(c["allocation_vnd"].values()), c["spend_cap_vnd"])
        self.assertEqual(sorted(c["instances"]), sorted(c["allocation_vnd"]))


class StudyDDecisionConsistencyTests(unittest.TestCase):
    """aggregate, report and ablation must agree (single decision module)."""

    def _fixture(self, tmp):
        import json
        good = {"decision": "ADMIT", "e_min": 500.0, "draws": 110,
                "counts": {"help": 110, "tie": 0, "hurt": 0, "harness_error": 0},
                "b8": {"draws": 300, "counts": {"help": 300, "tie": 0, "hurt": 0, "harness_error": 0}},
                "trace": [[-1.0, False]] * 300, "gatekeeper_seconds": 0.1, "seconds": 0.3}
        base = {"bind": {"treated_modules": ["m.py"], "abstained": {}}, "B6R_replay": {"passed": True},
                "commit": "x", "startup_seconds": {}}
        res = {
            "A": dict(base, census={"status": "VALID", "new_failures": [], "seconds": {}},
                      B6R_fingerprint={"relation": "MATCH"}, scopes={"bool": good}),
            "B": dict(base, census={"status": "INVALID", "new_failures": [], "seconds": {}, "reason": "x"},
                      B6R_fingerprint={"relation": "MATCH"}, scopes={"bool": dict(good, decision="CENSUS_INVALID")}),
            "C": dict(base, census={"status": "VALID", "new_failures": [], "seconds": {}},
                      B6R_fingerprint={"relation": "DRIFT"}, scopes={"bool": good}),
        }
        cfg = {"experiment_id": "t", "cells": ["A/bool", "B/bool", "C/bool"], "alpha": 0.1, "theta": 0.2,
               "eta": 0.05, "alpha_alarm": 0.05, "n_max": 300}
        for t in res:
            (tmp / "eval_targets" / t).mkdir(parents=True)
            (tmp / "eval_targets" / t / "gk_target.json").write_text(json.dumps({"role": "test"}))
            (tmp / f"RESULT_{t}.json").write_text(json.dumps(res[t]))
        (tmp / "config_study_d.json").write_text(json.dumps(cfg))
        return cfg

    def test_three_paths_agree(self):
        import json, sys, tempfile, importlib
        sys.path.insert(0, str(ROOT / "tools"))
        agg, rep, abl = (importlib.import_module(m) for m in ("aggregate_study_d", "report_study_d", "ablation_study_d"))
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            self._fixture(tmp)
            agg.main(str(tmp / "config_study_d.json"), str(tmp), str(tmp / "agg.json"))
            rows = {r["cell"]: r for r in json.loads((tmp / "agg.json").read_text())["cells"]}
            self.assertEqual(rows["A/bool"]["Gatekeeper"], "ADMIT")
            self.assertEqual(rows["B/bool"]["Gatekeeper"], "CENSUS_INVALID")
            self.assertEqual(rows["B/bool"]["B8"], "CENSUS_INVALID")
            self.assertEqual(rows["C/bool"]["B6R"], "REJECT")          # fingerprint DRIFT
            self.assertEqual(rows["A/bool"]["B6R"], "ADMIT")
            rep.main([str(tmp / "config_study_d.json"), str(tmp), str(tmp / "R.md")])
            md = (tmp / "R.md").read_text()
            self.assertIn("| B/bool |", md)
            line_b = next(l for l in md.splitlines() if l.startswith("| B/bool |"))
            self.assertIn("CENSUS_INVALID", line_b)
            out = tmp / "abl.md"
            abl.main([str(tmp / "config_study_d.json"), str(tmp), "--out", str(out)])
            for line in out.read_text().splitlines()[2:]:
                self.assertIn("CENSUS_INVALID", line.split("|")[3])  # column B/bool in every variant


class B9VerdictTests(unittest.TestCase):
    def test_verdicts(self):
        from gatekeeper_lite.b9 import b9_verdict
        ok_c = {"status": "VALID", "new_failures": []}
        self.assertEqual(b9_verdict({"status": "NO_PATCH"}), "NO_PATCH")
        self.assertEqual(b9_verdict({"status": "SUBMITTED", "census": {"status": "INVALID"}}), "CENSUS_INVALID")
        self.assertEqual(b9_verdict({"status": "SUBMITTED", "census": {"status": "VALID", "new_failures": ["t"]},
                                     "hidden_oracle": {"bool": {"help": 5, "hurt": 0}}}), "HARMFUL")
        self.assertEqual(b9_verdict({"status": "SUBMITTED", "census": ok_c,
                                     "hidden_oracle": {"bool": {"help": 5, "hurt": 0}, "int": {"help": 0, "hurt": 1}}}), "HARMFUL")
        self.assertEqual(b9_verdict({"status": "SUBMITTED", "census": ok_c,
                                     "hidden_oracle": {"bool": {"help": 5, "hurt": 0}, "int": {"help": 0, "hurt": 0}}}), "SUCCESS")
        self.assertEqual(b9_verdict({"status": "SUBMITTED", "census": ok_c,
                                     "hidden_oracle": {"bool": {"help": 0, "hurt": 0}}}), "NO_EFFECT")
