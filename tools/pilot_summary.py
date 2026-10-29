"""Summarise a pilot (P0 or P1) of Study N and apply the registered rule (study_n/STUDY_N_PROTOCOL.md, section 6).

python tools/pilot_summary.py DIR OUT_DIR [--stage P0] [--min-instances 8] [--planned N]

P0 passes when (a) at least MIN instances ran the whole chain (harness measured, every generation finished, every submitted
patch labelled and scored) and (b) at least one patch is plausible.  P1 compares a strong model with the light one on the same
instances and reports the share of attempts whose FIRST call already passed the visible check, because the spend guard may
stop a strong model after fewer calls than the light one (worst-case accounting).  Nothing here changes any gate.
"""
import collections
import json
import statistics
import sys
from pathlib import Path


def chain_ok(r):
    inner = r.get("inner") or {}
    if r.get("status") != "FINISHED" or inner.get("status") != "FINISHED":
        return False
    for a in inner.get("attempts", []):
        if a.get("status") == "GENERATION_ERROR":
            return False
        if a.get("status") == "SUBMITTED" and (a.get("scoring_error") or (a.get("labels") or {}).get("error") or "draws" not in a):
            return False
    return bool(inner.get("attempts"))


def summarise(records, stage="P0", min_instances=8, planned=None):
    per_model = collections.defaultdict(lambda: collections.Counter())
    finish, tokens, cost, calls = collections.defaultdict(collections.Counter), collections.defaultdict(list), collections.Counter(), collections.defaultdict(list)
    plaus, band_rows, status = [], [], collections.Counter()
    for r in records:
        inner = r.get("inner") or {}
        status[inner.get("status") or r.get("status")] += 1
        for a in inner.get("attempts", []):
            m = a["model"]
            c = per_model[m]
            c["attempts"] += 1
            c["submitted"] += a.get("status") == "SUBMITTED"
            c["first_call_visible_pass"] += (a.get("verdicts") or [None])[0] == "PASSES_VISIBLE"
            c["stopped_by_spend_guard"] += "BUDGET_CAP" in (a.get("verdicts") or [])
            cost[m] += a.get("cost_usd") or 0
            calls[m].append(a.get("calls") or 0)
            tokens[m].append((a.get("tokens") or {}).get("output", 0) / max(a.get("calls") or 1, 1))
            for f in a.get("finish_reasons") or []:
                finish[m][f] += 1
            lab = a.get("labels") or {}
            if lab.get("plausible"):
                c["plausible"] += 1
                d, g = a.get("draws") or {}, a.get("gates") or {}
                plaus.append({"name": r["name"], "model": m, "h_hat": d.get("h_hat"), "in_band": d.get("in_band"), "acceptable": d.get("acceptable"),
                              "gates": {k: v for k, v in g.items() if not k.startswith("_")}})
    chain = [r for r in records if chain_ok(r)]
    a_ok, b_ok = len(chain) >= int(min_instances), any(c["plausible"] for c in per_model.values())
    discord = sum(1 for p in plaus if len({p["gates"].get("fixed_sample"), p["gates"].get("gatekeeper")} ^ {p["gates"].get("b8_plus"), p["gates"].get("smoke20")}) > 0
                  and (p["gates"].get("fixed_sample") != p["gates"].get("b8_plus") or p["gates"].get("gatekeeper") != p["gates"].get("b8_plus")
                       or p["gates"].get("fixed_sample") != p["gates"].get("smoke20")))
    out = {"stage": stage, "instances_run": len(records), "planned": planned, "instances_status": dict(status), "instances_with_full_chain": len(chain),
           "criterion_a_full_chain": a_ok, "criterion_b_some_plausible_patch": b_ok, "min_instances": int(min_instances),
           "pilot_pass": bool(a_ok and b_ok), "spent_usd": round(sum(cost.values()), 4),
           "models": {m: {**dict(c), "cost_usd": round(cost[m], 4), "finish_reasons": dict(finish[m]),
                          "median_output_tokens_per_call": statistics.median(tokens[m]) if tokens[m] else None,
                          "mean_calls_per_attempt": round(statistics.mean(calls[m]), 2) if calls[m] else None,
                          "plausible_rate": round(c["plausible"] / c["attempts"], 3) if c["attempts"] else None,
                          "truncated_calls_share": round(finish[m].get("length", 0) / max(sum(finish[m].values()), 1), 3)}
                      for m, c in per_model.items()},
           "plausible_patches": plaus, "plausible_in_band": sum(1 for p in plaus if p["in_band"]), "plausible_with_discordant_gates": discord,
           "note": "Development instances (exposed). Not evidence for any gate of Study N."}
    return out


def render(s):
    L = ["# Pilot %s: summary" % s["stage"], "", "**%s**: criterion (a) full chain on at least %d instances: %s (%d of %s); criterion (b) at least one plausible patch: %s. Spent %.4f USD."
         % ("PASS" if s["pilot_pass"] else "NOT PASSED", s["min_instances"], s["criterion_a_full_chain"], s["instances_with_full_chain"], s["planned"] or s["instances_run"],
            s["criterion_b_some_plausible_patch"], s["spent_usd"]), "",
         "| Model | Attempts | Submitted | Plausible | First call passes visible | Stopped by the spend guard | Truncated calls | Median output tokens per call | Mean calls | Cost USD |", "|---|---|---|---|---|---|---|---|---|---|"]
    for m, v in s["models"].items():
        L.append("| %s | %d | %d | %d | %d | %d | %s | %s | %s | %s |" % (m, v.get("attempts", 0), v.get("submitted", 0), v.get("plausible", 0), v.get("first_call_visible_pass", 0),
                                                                      v.get("stopped_by_spend_guard", 0), v["truncated_calls_share"], v["median_output_tokens_per_call"], v["mean_calls_per_attempt"], v["cost_usd"]))
    L += ["", "Instances by status: %s." % s["instances_status"], "Plausible patches in the harm band: %d; with gates that disagree: %d." % (s["plausible_in_band"], s["plausible_with_discordant_gates"]), "", s["note"]]
    return "\n".join(L) + "\n"


def main(argv):
    d, out = argv[0], argv[1]
    opt = lambda k, default: argv[argv.index(k) + 1] if k in argv else default
    recs = [json.loads(f.read_text()) for f in sorted(Path(d).rglob("COHORT_*.json"))]
    s = summarise(recs, opt("--stage", "P0"), opt("--min-instances", 8), int(opt("--planned", 0)) or None)
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    (o / "PILOT_SUMMARY.json").write_text(json.dumps(s, indent=1))
    (o / "PILOT_SUMMARY.md").write_text(render(s), encoding="utf-8")
    (o / ("%s_RESULT.json" % s["stage"])).write_text(json.dumps({"stage": s["stage"], "p0_pass" if s["stage"] == "P0" else "pilot_pass": s["pilot_pass"],
                                                                   "pilot_pass": s["pilot_pass"], "instances_with_full_chain": s["instances_with_full_chain"],
                                                                   "spent_usd": s["spent_usd"]}, indent=1))
    print(render(s))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
