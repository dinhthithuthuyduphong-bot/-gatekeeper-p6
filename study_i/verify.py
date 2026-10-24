"""Fail-closed audit of raw XML/JSONL and the four-cell exploratory family.

No target packages, models, network calls or execution of target code are needed.
This rechecks recorded outcomes; it does not turn retrospective data into a
pre-registered experiment or prove generalization beyond the declared scopes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import importlib.util
import json
import math
from pathlib import Path
import sys

from run import digest, xml_cases, write_json

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_float(a, b):
    return math.isfinite(a) and math.isfinite(b) and math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12)


def counts(zs):
    return {"help": sum(z < 0 for z in zs), "tie": sum(z == 0 for z in zs),
            "hurt": sum(z > 0 for z in zs), "harness_error": 0}


def audit_target(directory, name, cfg, settings, config_sha):
    from gatekeeper_lite.eprocess import BettingEProcess, HarmCertEProcess, HarmAlarmEProcess
    result = json.loads((directory / "RESULT.json").read_text())
    require(result["status"] == "VERIFIED_EXPLORATORY", "Incomplete target: " + name)
    require(result["target_config"] == cfg and result["config_sha256"] == config_sha, "Config mismatch")
    require(result["upstream_revision"] == cfg["revision"], "Revision mismatch")
    require(result["llm_calls"] == 0 and result["model_cost_usd"] == 0, "Unexpected model use")
    for rel, sha in result["study_code_sha256"].items():
        require(digest(HERE / rel) == sha, "Measured code changed: " + rel)
    arms = ["baseline", "treated"] + (["gold"] if cfg.get("gold") else [])
    groups = ["census"] + (["witness"] if cfg.get("witness") else [])
    grouped = defaultdict(list)
    identities = set()
    for run in result["runs"]:
        key = (run["arm"], run["group"], run["repetition"])
        require(key not in identities, "Duplicate run")
        identities.add(key)
        require(run["arm"] in arms and run["group"] in groups, "Unexpected arm/group")
        require(run["returncode"] in (0, 1), "Invalid process return code")
        require(math.isfinite(run["seconds"]) and run["seconds"] > 0, "Invalid timing")
        require((directory / run["log"]).stat().st_size > 0, "Missing/empty console log")
        cases = xml_cases(directory / run["xml"])
        labels = {k: v["status"] for k, v in cases.items()}
        require(labels == run["case_status"], "XML disagrees with recorded outcomes")
        c = {s: sum(v == s for v in labels.values()) for s in ("passed", "failure", "error", "skipped")}
        require(c == run["counts"], "XML count mismatch")
        require(run["returncode"] == int(c["failure"] + c["error"] > 0), "Exit/outcome mismatch")
        if c["error"]:
            require(name == "networkx" and run["arm"] == "baseline" and run["group"] == "witness"
                    and len(cases) == 1 and all(
                        "ValueError" in v["message"] + v["detail"]
                        and "truth value of an array" in v["message"] + v["detail"]
                        and "_fruchterman_reingold" in v["detail"] for v in cases.values()),
                    "Unclassified error cannot be counted as functional evidence")
        grouped[(run["arm"], run["group"])].append((run["repetition"], labels))
    require(set(grouped) == {(a, g) for a in arms for g in groups}, "Missing arm/group")
    states = {}
    repeats = set()
    for key, reps in grouped.items():
        reps.sort()
        repeats.add(len(reps))
        require(len(reps) >= 3 and [x[0] for x in reps] == list(range(1, len(reps)+1)), "Missing repetition")
        require(all(x[1] == reps[0][1] for x in reps), "Unstable test identities/outcomes")
        states[key] = reps[0][1]
    require(len(repeats) == 1, "Unbalanced repetitions")
    b, t = states[("baseline", "census")], states[("treated", "census")]
    require(set(b) == set(t) and sum(v == "passed" for v in b.values()) >= 5, "Invalid census inventory")
    require(all(v in ("passed", "skipped") for v in b.values()), "Baseline census was not clean")
    regressions = sorted(k for k in b if b[k] == "passed" and t[k] in ("failure", "error"))
    require(regressions == result["census_regressions"], "Regression mismatch")
    resolved = []
    if "witness" in groups:
        wb, wt = states[("baseline", "witness")], states[("treated", "witness")]
        require(set(wb) == set(wt), "Witness inventory mismatch")
        resolved = sorted(k for k in wb if wb[k] in ("failure", "error") and wt[k] == "passed")
        require(all(states[("gold", g)] == states[("treated", g)] for g in groups), "Gold differs from skill")
    require(resolved == result["resolved_upstream_witnesses"], "Resolved witness mismatch")
    require(bool(regressions) if cfg["direction"] == "harmful" else bool(resolved) and not regressions,
            "Expected candidate direction did not reproduce")

    spec = importlib.util.spec_from_file_location("verify_oracle_"+name, HERE / cfg["draw_oracle"])
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    observed = defaultdict(list)
    for line in (directory / "draws.jsonl").read_text().splitlines():
        require(bool(line.strip()), "Blank JSONL observation")
        r = json.loads(line)
        require("harness_error" not in r["without"] and "harness_error" not in r["with"], "Harness error")
        require("/baseline/" in r["without"].get("module", "") and
                "/treatment/" in r["with"].get("module", ""), "Wrong source import")
        pw, pt = map(bool, oracle.judge(r["scope"], r["draw"], r["without"], r["with"]))
        require(pw == r["passed_without"] and pt == r["passed_with"], "Oracle label mismatch")
        require(r["z"] == int(not pt) - int(not pw), "Z mismatch")
        observed[r["scope"]].append(r)
    require(set(observed) == set(oracle.scopes()) == set(result["diagnostic_draws"]["scopes"]), "Scope missing/extra")
    stability = json.loads((directory / "STATELESSNESS.json").read_text())
    require(stability["status"] == "STABLE_ON_CHECKED_DRAWS", "State/order check did not pass")
    stable_rows = [json.loads(x) for x in (directory / "statelessness.jsonl").read_text().splitlines()]
    wanted = {(s, n) for s in observed for n in range(1, 101)}
    require(Counter((r["scope"], r["original_n"]) for r in stable_rows) == Counter(wanted),
            "Incomplete or duplicate state/order observations")
    clean = lambda x: {k:v for k,v in x.items() if k != "module"}
    for row in stable_rows:
        original = observed[row["scope"]][row["original_n"]-1]
        require(not row["mismatch"] and not row["harness_error"], "State/order mismatch")
        require(clean(row["without"]) == clean(original["without"]) and
                clean(row["with"]) == clean(original["with"]), "State/order semantic output mismatch")
        require(row["passed_without"] == original["passed_without"] and
                row["passed_with"] == original["passed_with"], "State/order label mismatch")
    require(set(stability["scopes"]) == set(observed) and all(
        s == {"compared":100, "mismatches":0, "harness_errors":0} for s in stability["scopes"].values()),
        "State/order summary mismatch")
    cells = []
    for scope, observations in observed.items():
        require(len(observations) == settings["n_max"], "Missing/extra raw draw")
        require([r["n"] for r in observations] == list(range(1, settings["n_max"]+1)), "Draw order/ID mismatch")
        raw = result["diagnostic_draws"]["scopes"][scope]
        zs = [r["z"] for r in observations]
        trace = [[r["z"], r["passed_without"] and not r["passed_with"]] for r in observations]
        require(trace == raw["trace"], "Trace differs from raw observations")
        require(counts(zs) == raw["b8"]["counts"] and raw["b8"]["draws"] == len(zs), "Full-budget count mismatch")
        ben, cert = BettingEProcess(settings["theta"]), HarmCertEProcess(settings["eta"])
        alarm = HarmAlarmEProcess(settings["eta"])
        decision, stop = "UNDECIDED", len(zs)
        for i, (z, harm) in enumerate(trace, 1):
            ben.update(z); cert.update(harm); alarm.update(harm)
            if alarm.value >= 1 / settings["alpha_alarm"]:
                decision, stop = "REJECT_HARM", i
                break
            if min(ben.value, cert.value) >= len(settings["cells"]) / settings["alpha"]:
                decision, stop = "ADMIT", i
                break
        require(decision == raw["decision"] and stop == raw["draws"], "Stopping rule mismatch")
        require(counts(zs[:stop]) == raw["counts"], "Stopped counts mismatch")
        for key, value in (("e_benefit", ben.value), ("e_cert", cert.value),
                           ("e_alarm", alarm.value), ("e_min", min(ben.value, cert.value))):
            require(same_float(value, raw[key]), "Stopped e-value mismatch: " + key)
        e = 0.0 if regressions or decision == "REJECT_HARM" else min(ben.value, cert.value)
        cells.append({"cell": cfg["target_id"]+"/"+scope, "raw_decision": decision,
                      "draws_to_stop": stop, "full_counts": counts(zs), "e_for_family": e,
                      "census_veto": bool(regressions), "gatekeeper_seconds": raw["gatekeeper_seconds"],
                      "full_draw_seconds": raw["seconds"]})
    print("VERIFIED_RAW", name, "runs", len(result["runs"]), "draws", sum(map(len, observed.values())),
          "regressions", len(regressions), "resolved", len(resolved), flush=True)
    return cells


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True, help="Directory containing sqlalchemy/ and networkx/")
    parser.add_argument("--gatekeeper", type=Path, default=HERE.parent)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads((HERE / "targets.json").read_text())
    for rel, sha in cfg["gatekeeper_sha256"].items():
        require(digest(args.gatekeeper / rel) == sha, "Frozen core/skill changed: " + rel)
    sys.path.insert(0, str(args.gatekeeper.resolve()))
    from gatekeeper_lite.eprocess import e_holm
    cells = []
    for name, target in cfg["targets"].items():
        cells += audit_target(args.results / name, name, target, cfg["diagnostic_draws"], digest(HERE / "targets.json"))
    require(Counter(c["cell"] for c in cells) == Counter(cfg["diagnostic_draws"]["cells"]), "Family missing/duplicate cell")
    admitted = e_holm({c["cell"]: c["e_for_family"] for c in cells}, cfg["diagnostic_draws"]["alpha"])
    for c in cells:
        c["final_decision"] = ("REJECT_CENSUS" if c["census_veto"] else "REJECT_HARM"
                               if c["raw_decision"] == "REJECT_HARM" else "ADMIT_DIAGNOSTIC"
                               if c["cell"] in admitted else "QUARANTINE")
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "FAMILY_RESULT.json", {"status": "VERIFIED_EXPLORATORY",
               "not_preregistered": True, "model_calls": 0, "B9": "HOLD", "cells": cells,
               "admitted_diagnostic_cells": admitted})
    lines = ["# Study I: verified exploratory family", "",
             "Retrospective target vetting and generator diagnostics; no prospective/generalization claim.", "",
             "| Cell | Final decision | Draws to stop | Full help / tie / hurt |", "|---|---|---:|---|"]
    for c in cells:
        n = c["full_counts"]
        lines.append("| %s | %s | %s | %s / %s / %s |" %
                     (c["cell"], c["final_decision"], c["draws_to_stop"], n["help"], n["tie"], n["hurt"]))
    lines += ["", "Four cells are retained in the e-Holm family, including census-vetoed cells with e=0.",
              "The full 300-draw traces were executed for diagnostics after each stopped decision. Do not call this a production cost saving.",
              "The custom draw oracles are distinct from the unchanged upstream tests used to establish target behavior.",
              "Model calls: 0. B9 remains HOLD."]
    (args.output / "FAMILY_RESULT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status": "VERIFIED_EXPLORATORY", "admitted_diagnostic_cells": admitted}, indent=2))


if __name__ == "__main__":
    main()
