"""Phase-2 zero-cost regression tests; all fixtures synthetic and labeled."""
from __future__ import annotations

import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

from tools.phase2_cs_audit import bounded_cs, cell_row
from tools.phase2_b6r_v2 import evaluate, satisfies
from tools.phase2_integrity_audit import inspect


class Phase2CS(unittest.TestCase):
    def test_n1_interval_contains_full_parameter_space(self):
        a,b=bounded_cs(-1.0,1,-1,1,.001)
        self.assertEqual((a,b),(-1,1))

    def test_width_shrinks_with_n_for_fixed_mean(self):
        a,b=bounded_cs(0,100,-1,1,.001)
        c,d=bounded_cs(0,300,-1,1,.001)
        self.assertLess(d-c,b-a)

    def test_actual_stopping_prefix_only(self):
        row=cell_row("X/bool",{"scopes":{"bool":{
            "draws":2,"decision":"ADMIT","trace":[[-1,False],[0,False],[1,True]],
            "counts":{"help":1,"tie":1,"hurt":0}
        }}},.05,2)
        self.assertEqual(row["n"],2)
        self.assertEqual(row["trace_total"],3)
        self.assertAlmostEqual(row["mu"],-.5)
        self.assertEqual(row["h"],0.0)

    def test_inconsistent_regression_flag_fails(self):
        with self.assertRaisesRegex(ValueError,"inconsistent regression"):
            cell_row("X/bool",{"scopes":{"bool":{
                "draws":1,"decision":"UNDECIDED","trace":[[1,False]],
                "counts":{"help":0,"tie":0,"hurt":1}
            }}},.05,2)

    def test_missing_scope_not_fabricated(self):
        row=cell_row("X/int",{"scopes":{}},.05,2)
        self.assertFalse(row["estimable"])


class Phase2B6R(unittest.TestCase):
    def test_strict_numeric_comparator(self):
        self.assertTrue(satisfies("3.12",">=3.8,<3.13"))
        self.assertFalse(satisfies("3.13",">=3.8,<3.13"))
        with self.assertRaises(ValueError):
            satisfies("3.12rc1",">=3.8")

    def test_missing_receipts_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            row=evaluate(Path(folder),{},{"target_id":"T","python":"3.12"})
            self.assertEqual(row["decision"],"UNRESOLVED")

    def test_independent_synthetic_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            fixtures={
                "origin.json":{"origin":{"repo":"https://example.org/project.git","commit":"a"*40},
                               "required_environment":{"python":">=3.8,<3.13","packages":{"pytest":">=8.0,<9"}}},
                "replay.json":{"status":"PASS","heldout_examples":3},
                "smoke.json":{"status":"PASS","oracle_kind":"VISIBLE_PREDECLARED","uses_hidden_oracle":False}
            }
            rec={"status":"PREDECLARED_CANDIDATE"}
            for name, data in fixtures.items():
                f=root/name
                f.write_text(json.dumps(data),encoding="utf-8")
                rec[{"origin.json":"origin","replay.json":"replay","smoke.json":"smoke"}[name]]={
                    "path":name,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()}
            target={"target_id":"fixture","python":"3.12","packages":{"pytest":"8.3.5"}}
            self.assertEqual(evaluate(root,rec,target)["decision"],"ADMIT")
            target["packages"]={}
            self.assertEqual(evaluate(root,rec,target)["decision"],"UNRESOLVED")
            target["packages"]={"pytest":"9.1"}
            self.assertEqual(evaluate(root,rec,target)["decision"],"REJECT")
            target["packages"]={"pytest":"8.3"}
            fixtures["smoke.json"]["uses_hidden_oracle"]=True
            (root/"smoke.json").write_text(json.dumps(fixtures["smoke.json"]),encoding="utf-8")
            rec["smoke"]["sha256"]=hashlib.sha256((root/"smoke.json").read_bytes()).hexdigest()
            self.assertEqual(evaluate(root,rec,target)["decision"],"UNRESOLVED")


class Phase2Integrity(unittest.TestCase):
    def test_missing_score_hash_is_reported_not_silently_fixed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in ("study_f","pre_b9","tools",".github/workflows"):
                (root/name).mkdir(parents=True)
            (root/"study_f/FREEZE.json").write_text(json.dumps({"files":{"a":"hash"}}))
            (root/"study_f/config_study_f.json").write_text(json.dumps({
                "status":"FROZEN","k_cells":48,"b9_configs":{"A":"x","B":"x","C":"x","D":"x"},
                "cells":["t1","t2","t3","t4","t5","t6"]}))
            (root/"pre_b9/RELEASE_GATE.json").write_text(json.dumps({"status":"HOLD"}))
            (root/"tools/score_heldout.py").write_text('def gate():\n    return "ADMIT"\n')
            (root/".github/workflows/study-f-score.yml").write_text("python tools/score_heldout.py")
            (root/"study_f/STUDY_F_PROTOCOL.md").write_text("BẢN NHÁP, chưa đóng băng")
            audit=inspect(root)
            codes={f["code"] for f in audit["findings"]}
            self.assertIn("F-SCORER-UNPINNED",codes)
            self.assertIn("F-AGGREGATOR-PATH",codes)
            self.assertEqual(audit["release_status"],"HOLD")
            self.assertEqual(audit["status"],"REVIEW_REQUIRED")


if __name__=="__main__":
    unittest.main()
