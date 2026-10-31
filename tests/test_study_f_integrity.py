"""Synthetic contract tests only: never evidence of model effectiveness or spend."""
import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gatekeeper_ext.study_f_validation import (ProviderReplayClient, digest, validate_heldout,
                                               compare_replay)
from gatekeeper_lite.b9 import Budget, RepairResult, SpendGuard, repair
from tools import aggregate_study_f, score_heldout


def fixture():
    cfg = {"status": "FROZEN", "alpha": .1, "n_max": 300, "theta": .2, "eta": .05, "repetitions": 3,
           "cells": ["T" + str(i) for i in range(6)],
           "b9_configs": {"test-model-" + str(i): "unused" for i in range(4)}, "k_patches": 72}
    cfg["scopes_by_target"] = {t:["bool"] for t in cfg["cells"]}
    documents = []
    for target in cfg["cells"]:
        rows = [{"approach": "skill+" + name, "verdict": "NO_PATCH", "state": {"status": "NO_PATCH"}}
                for name in ("Gatekeeper", "B6R", "B8")]
        for model in cfg["b9_configs"]:
            for rep in range(3):
                state = {"status": "SUBMITTED", "census": {"status": "VALID", "new_failures": []},
                         "hidden_oracle": {"bool": {"help": 1, "hurt": int(rep == 2), "tie": 299-int(rep == 2), "harness_error": 0}}}
                state["hidden_traces"] = {"bool": [[-1,False]] + ([[1,True]] if rep == 2 else []) + [[0,False]]*(299-int(rep == 2))}
                verdict = "HARMFUL" if rep == 2 else "SUCCESS"
                from gatekeeper_ext.patch_rule import patch_evalue
                admission = {"bool": ([[1,True]] if rep == 2 else [[-1,False]])*300}
                counts = {"bool": {"help": 0 if rep == 2 else 300, "hurt": 300 if rep == 2 else 0, "tie": 0, "harness_error": 0}}
                e = patch_evalue(admission, .2, .05, 300)
                rows.append({"approach": "B9 raw", "model": model, "repetition": rep,
                             "verdict": verdict, "cost_usd": 0.0, "state": state})
                rows.append({"approach": "B9+Gatekeeper (candidate)", "model": model, "repetition": rep,
                             "raw_verdict": verdict, "cost_usd": 0.0, "e_patch": e,
                             "gate": {"submitted": True, "e_patch": e, "census_ok": True, "scope_counts": counts, "scope_traces": admission}})
        documents.append({"schema_version": 2, "evidence": "RECORDED_PROVIDER_REPLAY",
                          "config_sha256": "a"*64, "target": target, "commit": "a"*40,
                          "heldout_seed": {"seed": 2}, "admission_seed": 1,
                          "source_artifacts": {m: {"result_sha256": "b"*64, "cassette_sha256": "c"*64}
                                               for m in cfg["b9_configs"]}, "rows": rows})
    return cfg, documents


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.cfg, self.docs = fixture()

    def validate(self):
        return validate_heldout(self.cfg, self.docs, "a"*64)

    def test_complete_family(self):
        raw, candidates = self.validate()
        self.assertEqual((len(raw), len(candidates)), (72, 72))

    def test_empty_rows(self):
        for d in self.docs:
            d["rows"] = []
        with self.assertRaises(ValueError): self.validate()

    def test_each_required_row_is_required(self):
        for i in range(len(self.docs[0]["rows"])):
            cfg, docs = fixture()
            docs[0]["rows"].pop(i)
            with self.subTest(row=i), self.assertRaises(ValueError):
                validate_heldout(cfg, docs, "a"*64)

    def test_duplicate_rows(self):
        self.docs[0]["rows"].append(copy.deepcopy(self.docs[0]["rows"][3]))
        with self.assertRaises(ValueError): self.validate()

    def test_out_of_family(self):
        self.docs[0]["rows"][3]["model"] = "unknown"
        with self.assertRaises(ValueError): self.validate()

    def test_nonfinite_negative_evidence(self):
        for e in (float("nan"), float("inf"), -1, True):
            self.docs[0]["rows"][4]["e_patch"] = e
            with self.subTest(e=e), self.assertRaises(ValueError): self.validate()

    def test_wrong_verdict(self):
        self.docs[0]["rows"][3]["verdict"] = "NO_EFFECT"
        with self.assertRaises(ValueError): self.validate()

    def test_harness_error_is_not_harm_or_benefit(self):
        self.docs[0]["rows"][3]["state"]["hidden_oracle"]["bool"]["harness_error"] = 1
        with self.assertRaises(ValueError): self.validate()

    def test_missing_scope_cannot_be_omitted(self):
        self.cfg["scopes_by_target"]["T0"].append("int")
        with self.assertRaisesRegex(ValueError, "scope"): self.validate()

    def test_tampered_admission_evalue(self):
        row = self.docs[0]["rows"][4]
        row["e_patch"] *= 2
        row["gate"]["e_patch"] = row["e_patch"]
        with self.assertRaisesRegex(ValueError, "raw admission trace"): self.validate()

    def test_counts_must_match_raw_observations(self):
        counts = self.docs[0]["rows"][3]["state"]["hidden_oracle"]["bool"]
        counts["help"], counts["tie"] = counts["help"]+1, counts["tie"]-1
        with self.assertRaisesRegex(ValueError, "counts/paired trace"): self.validate()

    def test_seeds_and_config_consistency(self):
        for field, value in (("heldout_seed", {"seed": 1}), ("admission_seed", 3), ("config_sha256", "d"*64)):
            cfg, docs = fixture(); docs[0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): validate_heldout(cfg, docs, "a"*64)

    def test_missing_artifact_provenance(self):
        self.docs[0]["source_artifacts"] = {}
        with self.assertRaises(ValueError): self.validate()

    def test_mock_label_is_rejected(self):
        self.docs[0]["evidence"] = "MOCK"
        with self.assertRaises(ValueError): self.validate()

    def test_candidate_print_does_not_claim_final_verdict(self):
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture): score_heldout.print_rows("T0", self.docs[0]["rows"])
        self.assertIn("PENDING_FAMILY; raw=SUCCESS", capture.getvalue())

    def test_missing_model_inventory_prevents_execution(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"config.json"; p.write_text(json.dumps(self.cfg))
            with patch.object(score_heldout, "_clone_ref", side_effect=AssertionError("must not clone")):
                with self.assertRaisesRegex(ValueError, "missing model"): score_heldout.main(str(p), "T0", d)

    def test_aggregation_complete_and_no_positive_success_delta(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); cfg = root/"config.json"; cfg.write_text(json.dumps(self.cfg))
            for doc in self.docs:
                doc["config_sha256"] = digest(cfg)
                (root/("HELDOUT_"+doc["target"]+".json")).write_text(json.dumps(doc))
            with contextlib.redirect_stdout(io.StringIO()):
                aggregate_study_f.main(str(cfg), str(root), str(root/"SYNTHETIC_TEST_OUTPUT.md"))
            result = json.loads((root/"SYNTHETIC_TEST_OUTPUT.json").read_text())
            for m in result["models"].values():
                self.assertEqual(m["n"],18)
                self.assertEqual((m["raw_success"],m["kept_success"],m["blocked_harmful"]),(12,12,6))
                self.assertLessEqual(m["delta_success_pp"],0)

    def test_missing_provider_usage_cannot_become_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"cassette.json"
            key=ProviderReplayClient.key("test", [], 1, 0, 1)
            path.write_text(json.dumps({key:{"text":"", "usage":{"input":0,"output":0}}}))
            with self.assertRaisesRegex(ValueError,"raw provider usage"):
                ProviderReplayClient(path).complete("test",[],1,0,1)

    def test_replay_miss_never_calls_provider(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"cassette.json";path.write_text("{}")
            with patch("urllib.request.urlopen",side_effect=AssertionError("network forbidden")):
                with self.assertRaises(KeyError):ProviderReplayClient(path).complete("test",[],1,0,1)

    def test_budget_cap_replay_needs_no_cassette_entry(self):
        class Target:
            modules=[]
        class NeverCall:
            def complete(self,*a):raise AssertionError("budget must stop before API/replay")
        result=repair(Target(),{"issue":"x","visible_desc":"x"},NeverCall(),"test",Budget(5,4000,5),
                      {"input":1,"output":1},seed=1,guard=SpendGuard(0))
        self.assertEqual(result.calls,0)
        self.assertEqual(result.attempts[0]["verdict"],"BUDGET_CAP")

    def test_replay_cannot_silently_change_patch_selection(self):
        result=RepairResult("SUBMITTED",treated={"x.py":"pass"})
        recorded={"status":"NO_PATCH","attempts":[],"calls":0,"visible_runs":0,"tokens":{"input":0,"output":0},
                  "patched_modules":[],"cost_usd":0}
        with self.assertRaisesRegex(ValueError,"status"):compare_replay(result,recorded)


if __name__ == "__main__":
    unittest.main(verbosity=2)
