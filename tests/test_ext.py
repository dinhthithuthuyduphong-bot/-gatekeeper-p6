import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite import transforms as T  # noqa: E402


class NoneIdentitySkillTests(unittest.TestCase):
    def test_rewrite_and_semantics(self):
        from gatekeeper_ext.none_identity import NoneIdentity, register
        src = ("def f(x, y):\n    if x == None:\n        return 1\n    if None != y:\n        return 2\n"
               "    if x == None == y:\n        return 3\n    return 0\n")
        res = NoneIdentity().apply(src, single_site=False)
        self.assertIn("if x is None:", res.source)
        self.assertIn("if y is not None:", res.source)
        self.assertIn("x == None == y", res.source)          # chained comparison left alone
        self.assertEqual(len(res.sites), 2)
        register()
        self.assertEqual(T.make("none_identity").name, "none_identity")

    def test_behaviour_changes_only_for_overridden_eq(self):
        class Expr:                                           # stands for an ORM column expression
            def __eq__(self, other):
                return "IS NULL" if other is None else False
        e = Expr()
        self.assertEqual(e == None, "IS NULL")               # noqa: E711  intended semantics
        self.assertIs(e is None, False)                      # what the rewrite would produce
        self.assertEqual((5 == None), (5 is None))           # noqa: E711  ordinary objects: unchanged


class NoneIdentityPrecedenceTests(unittest.TestCase):
    """The rewrite must preserve meaning for ordinary objects whatever the operand's syntax."""

    CASES = ["(x if flag else y) == None", "None == (x if flag else y)", "(a or b) == None",
             "(not a) == None", "(lambda: 1) == None", "(n := x) == None", "a + b == None",
             "-a != None", "f(x)[0] == None", "(a and b) != None", "x.y == None", "(yield_ := x) != None"]

    def test_semantics_preserved_for_ordinary_values(self):
        from gatekeeper_ext.none_identity import NoneIdentity
        env_values = [None, 0, 5, "", [], [1]]
        for case in self.CASES:
            src = f"def g(x, y, a, b, flag, f):\n    return {case}\n"
            new = NoneIdentity().apply(src, single_site=False).source
            ns_old, ns_new = {}, {}
            exec(src, ns_old)
            exec(new, ns_new)
            for x in env_values:
                for flag in (True, False):
                    args = (x, None, x, 1, flag, lambda v: [v])
                    if "a + b" in case or "-a" in case:
                        args = (x, None, 2, 3, flag, lambda v: [v])
                    try:
                        old = ns_old["g"](*args)
                    except Exception as exc:
                        old = type(exc)
                    try:
                        got = ns_new["g"](*args)
                    except Exception as exc:
                        got = type(exc)
                    self.assertEqual(old, got, f"{case}: {old!r} vs {got!r} (x={x!r}, flag={flag})\\n{new}")


class StudyFAggregationTests(unittest.TestCase):
    def _run(self, rows_by_target, k=4):
        import json, tempfile, importlib
        sys.path.insert(0, str(ROOT / "tools"))
        agg = importlib.import_module("aggregate_study_f")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            cfg = {"k_patches": k, "alpha": 0.1, "n_max": 300, "theta": .2, "eta": .05, "repetitions": 1, "cells": list(rows_by_target),
                   "b9_configs": {"m1": "x", "m2": "y"}}
            cfg["scopes_by_target"] = {t:["bool"] for t in cfg["cells"]}
            (tmp / "c.json").write_text(json.dumps(cfg))
            from gatekeeper_ext.study_f_validation import digest
            for t, rows in rows_by_target.items():
                rows = [{"approach": "skill+" + name, "verdict": "NO_PATCH", "state": {"status": "NO_PATCH"}}
                        for name in ("Gatekeeper", "B6R", "B8")] + rows
                (tmp / f"HELDOUT_{t}.json").write_text(json.dumps({
                    "schema_version": 2, "evidence": "RECORDED_PROVIDER_REPLAY", "config_sha256": digest(tmp / "c.json"),
                    "target": t, "commit": "a"*40, "heldout_seed": {"seed": 2}, "admission_seed": 1,
                    "source_artifacts": {m: {"result_sha256": "b"*64, "cassette_sha256": "c"*64} for m in cfg["b9_configs"]},
                    "rows": rows}))
            agg.main(str(tmp / "c.json"), str(tmp), str(tmp / "o.md"))
            return (tmp / "o.md").read_text()

    def test_patch_level_family(self):
        def rows(m, e, v):
            submitted = v != "NO_PATCH"
            state = {"status": "NO_PATCH"}
            if submitted:
                help_, hurt = int(v == "SUCCESS"), int(v == "HARMFUL")
                state = {"status": "SUBMITTED", "census": {"status": "VALID", "new_failures": []},
                         "hidden_oracle": {"bool": {"help": help_, "hurt": hurt, "tie": 300-help_-hurt, "harness_error": 0}}}
            from gatekeeper_ext.patch_rule import patch_evalue
            gate = {"submitted": submitted, "e_patch": 0.0, "census_ok": submitted}
            if submitted:
                state["hidden_traces"] = {"bool": [[-1,False]]*help_ + [[1,True]]*hurt + [[0,False]]*(300-help_-hurt)}
                tr = {"bool": ([[-1,False]] if v == "SUCCESS" else [[1,True]] if v == "HARMFUL" else [[0,False]])*300}
                e = patch_evalue(tr,.2,.05,300)
                gate.update(e_patch=e,scope_traces=tr,scope_counts={"bool": {"help":300*help_,"hurt":300*hurt,"tie":300*(1-help_-hurt),"harness_error":0}})
            return [{"approach": "B9 raw", "model": m, "repetition": 0, "verdict": v, "state": state, "cost_usd": 0},
                    {"approach": "B9+Gatekeeper (candidate)", "model": m, "repetition": 0, "e_patch": e,
                     "raw_verdict": v, "cost_usd": 0, "gate": gate}]
        out = self._run({"T1": rows("m1", 0.0, "HARMFUL") + rows("m2", 1e9, "SUCCESS"),
                         "T2": rows("m1", 0.5, "NO_EFFECT") + rows("m2", 0.0, "NO_PATCH")})
        self.assertIn("| m1 | B9 + Gatekeeper | 0 | 0 | 0 | 2 |", out)     # harmful patch never deployed
        self.assertIn("| m2 | B9 + Gatekeeper | 1 | 0 | 0 | 1 |", out)

    def test_family_size_must_match_registration(self):
        with self.assertRaisesRegex(ValueError, "family size"):
            self._run({"T1": []}, k=99)


class PatchRuleTests(unittest.TestCase):
    def test_quarantined_scope_without_certificate_blocks_patch(self):
        from gatekeeper_ext.patch_rule import patch_evalue
        good = [[-1.0, False]] * 300
        few = [[0.0, False]] * 20                      # scope barely sampled: no low-harm certificate
        self.assertGreater(patch_evalue({"a": good, "b": [[0.0, False]] * 300}, 0.2, 0.05, 300), 60)
        self.assertLess(patch_evalue({"a": good, "b": few}, 0.2, 0.05, 300), 10)
        self.assertEqual(patch_evalue({"a": good, "b": [[1.0, True]] * 3 + [[0.0, False]] * 297}, 0.2, 0.05, 300), 0.0)


class FreezeExtraTrackedTests(unittest.TestCase):
    def test_extra_tracked_only_affects_its_own_study(self):
        import importlib, json, tempfile, shutil
        sys.path.insert(0, str(ROOT / "tools"))
        fz = importlib.import_module("freeze_study")
        d_files = {p.name for p in fz.tracked((ROOT / "study_d").resolve())}
        self.assertNotIn("score_heldout.py", d_files)
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            st = Path(tmp)
            (st / "config_x.json").write_text(json.dumps({"extra_tracked": ["tools/score_heldout.py"]}))
            self.assertIn("score_heldout.py", {p.name for p in fz.tracked(st.resolve())})


class MixtureCertTests(unittest.TestCase):
    def test_type_one_error_at_boundary(self):
        import random
        from gatekeeper_ext.mixture_cert import MixtureHarmCert
        rng, eta, crossed, sims = random.Random(3), 0.05, 0, 2000
        for _ in range(sims):
            m = MixtureHarmCert(eta)
            for _ in range(400):
                m.update(rng.random() < eta)          # h = eta exactly (null boundary)
                if m.value >= 20:
                    crossed += 1
                    break
        self.assertLessEqual(crossed / sims, 0.05 + 0.015)

    def test_no_regression_grows(self):
        from gatekeeper_ext.mixture_cert import MixtureHarmCert
        m = MixtureHarmCert(0.05)
        for _ in range(100):
            m.update(False)
        self.assertGreater(m.value, 60)
