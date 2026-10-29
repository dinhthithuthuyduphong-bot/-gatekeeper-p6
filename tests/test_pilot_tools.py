import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import cohort_instance as CIN  # noqa: E402
import pilot_select as PS  # noqa: E402
import pilot_summary as S  # noqa: E402


def att(model="m", status="SUBMITTED", plausible=True, in_band=False, verdicts=("PASSES_VISIBLE",), **kw):
    a = {"model": model, "status": status, "verdicts": list(verdicts), "calls": 1, "tokens": {"input": 1000, "output": 300}, "cost_usd": 0.01,
         "finish_reasons": ["stop"]}
    if status == "SUBMITTED":
        a.update(labels={"plausible": plausible}, draws={"h_hat": 0.02, "in_band": in_band, "acceptable": True},
                 gates={"census_only": True, "zero_tolerance": not in_band, "b8_plus": not in_band, "smoke20": True, "fixed_sample": True, "gatekeeper": True, "_detail": {}})
    a.update(kw)
    return a


def rec(name, attempts, inner_status="FINISHED"):
    return {"name": name, "status": "FINISHED", "inner": {"status": inner_status, "attempts": attempts}}


class Select(unittest.TestCase):
    def test_first_n_by_position_one_per_repository(self):
        recs = [{"name": "a1", "repo": "R1", "position": 0}, {"name": "a2", "repo": "r1", "position": 1}, {"name": "b", "repo": "R2", "position": 2},
                {"name": "c", "repo": "R3", "position": 3}]
        self.assertEqual(PS.select(recs, 3), ["a1", "b", "c"])
        self.assertEqual(PS.select(recs[::-1], 2), ["a1", "b"])                      # order of the file does not matter

    def test_the_real_development_list_gives_ten_distinct_repositories(self):
        recs = json.loads((ROOT / "research_closure" / "pilot" / "DEV_VET.json").read_text())
        names = PS.select(recs, 10)
        repos = {r["repo"] for r in recs if r["name"] in names}
        self.assertEqual((len(names), len(repos)), (10, 10))


class Summary(unittest.TestCase):
    def test_pass_and_fail_of_the_registered_rule(self):
        ok = [rec("i%d" % i, [att(), att()]) for i in range(8)]
        s = S.summarise(ok, "P0", 8)
        self.assertTrue(s["pilot_pass"])
        self.assertEqual(s["models"]["m"]["attempts"], 16)
        self.assertEqual(S.summarise(ok[:7], "P0", 8)["pilot_pass"], False)                # criterion (a)
        none = [rec("i%d" % i, [att(plausible=False)]) for i in range(8)]
        s2 = S.summarise(none, "P0", 8)
        self.assertEqual((s2["criterion_a_full_chain"], s2["criterion_b_some_plausible_patch"], s2["pilot_pass"]), (True, False, False))

    def test_a_generation_error_or_a_scoring_error_breaks_the_chain(self):
        self.assertFalse(S.chain_ok(rec("x", [att(status="GENERATION_ERROR")])))
        self.assertFalse(S.chain_ok(rec("x", [att(scoring_error="boom")])))
        self.assertFalse(S.chain_ok({"name": "x", "status": "FINISHED", "inner": {"status": "HARNESS_NOT_ELIGIBLE", "attempts": []}}))
        self.assertTrue(S.chain_ok(rec("x", [att(status="NO_PATCH", verdicts=("FAILS_VISIBLE",))])))   # the model failing is not a chain failure

    def test_truncation_and_first_call_are_reported_per_model(self):
        a = att(model="strong", finish_reasons=["length", "stop"], calls=2, verdicts=("FAILS_VISIBLE", "PASSES_VISIBLE"))
        s = S.summarise([rec("i", [a])], "P1", 1)["models"]["strong"]
        self.assertEqual((s["truncated_calls_share"], s["first_call_visible_pass"], s["mean_calls_per_attempt"]), (0.5, 0, 2))

    def test_spend_guard_stops_are_counted(self):
        stopped = att(status="NO_PATCH", verdicts=("BUDGET_CAP",), calls=0)
        s = S.summarise([rec("i", [stopped, att()])], "P0", 1)["models"]["m"]
        self.assertEqual((s["stopped_by_spend_guard"], s["attempts"]), (1, 2))

    def test_files_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "in"
            d.mkdir()
            (d / "COHORT_a.json").write_text(json.dumps(rec("a", [att()])))
            S.main([str(d), str(Path(tmp) / "out"), "--stage", "P0", "--min-instances", "1"])
            self.assertTrue(json.loads((Path(tmp) / "out" / "P0_RESULT.json").read_text())["p0_pass"])


class Models(unittest.TestCase):
    def test_model_selection_refuses_unknown_names(self):
        cfg = json.loads((ROOT / "research_closure" / "pilot" / "models.json").read_text())
        self.assertEqual([m["name"] for m in CIN.select_models(cfg, ["vertex-gemini-flash"])], ["vertex-gemini-flash"])
        with self.assertRaises(SystemExit):
            CIN.select_models(cfg, ["gemini-3.1-pro-preview"])                 # not available in the pilot configuration
        self.assertNotEqual(CIN.seed_for("study-n-pilot:", "a"), CIN.seed_for("study-n-pilot:", "b"))

    def test_the_flash_price_in_the_config_is_the_one_that_doubles_in_2027(self):
        cfg = {m["name"]: m for m in json.loads((ROOT / "research_closure" / "pilot" / "models.json").read_text())["models"]}
        f = cfg["vertex-gemini-flash"]
        self.assertEqual(f["prices_from_2027_01_01"]["input"], 2 * f["prices_usd_per_mtok"]["input"])
        self.assertEqual(cfg["vertex-gemini-argon"]["max_output_tokens"], 32768)       # the protocol's cap for the strong model


if __name__ == "__main__":
    unittest.main()
