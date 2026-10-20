"""Pre-registered Study D ablations, replayed on the recorded per-draw traces (no new runs).

python tools/ablation_study_d.py study_d/config_study_d.json RESULTS_DIR [--out ABLATION.md]
Variants (fixed in the protocol before the run):
  full          : benefit + harm certificate + harm alarm, e-Holm (FWER)
  no_harm_cert  : admit on the benefit e-process alone (what is lost without certifying low harm)
  no_census     : ignore the census gate
  bonferroni    : e-Bonferroni (K/alpha) instead of e-Holm
  sign_test     : discordant sign test (q0=0.6) instead of the mean e-process
  eta_0.10      : harm tolerance eta = 0.10 instead of 0.05
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite.eprocess import (BettingEProcess, DiscordantSignEProcess, HarmAlarmEProcess,  # noqa: E402
                                      HarmCertEProcess, e_holm)

VARIANTS = ["full", "no_harm_cert", "no_census", "bonferroni", "sign_test", "eta_0.10"]


def replay(trace, cfg, k, variant):
    eta = 0.10 if variant == "eta_0.10" else cfg["eta"]
    ben = DiscordantSignEProcess() if variant == "sign_test" else BettingEProcess(cfg["theta"])
    cert, alarm = HarmCertEProcess(eta), HarmAlarmEProcess(eta)
    stop_admit, stop_alarm = k / cfg["alpha"], 1 / cfg["alpha_alarm"]
    for n, (z, reg) in enumerate(trace[:cfg["n_max"]], 1):
        ben.update(z)
        cert.update(reg)
        alarm.update(reg)
        if alarm.value >= stop_alarm:
            return "REJECT_HARM", n, 0.0
        e = ben.value if variant == "no_harm_cert" else min(ben.value, cert.value)
        if e >= stop_admit:
            return "ADMIT", n, e
    e = ben.value if variant == "no_harm_cert" else min(ben.value, cert.value)
    return "UNDECIDED", min(len(trace), cfg["n_max"]), e


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("results")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text())
    k = len(cfg["cells"])
    data = {}
    for cell in cfg["cells"]:
        tgt, scope = cell.split("/")
        f = Path(a.results) / f"RESULT_{tgt}.json"
        r = json.loads(f.read_text()) if f.exists() else {}
        sc = r.get("scopes", {}).get(scope)
        census_bad = bool(r.get("census", {}).get("new_failures"))
        data[cell] = (sc["trace"] if sc else None, census_bad)
    lines = ["| Biến thể | " + " | ".join(cfg["cells"]) + " |", "|---|" + "---|" * k]
    for v in VARIANTS:
        decisions, evals = {}, {}
        for cell, (trace, census_bad) in data.items():
            if trace is None:
                decisions[cell], evals[cell] = "OUT_OF_SCOPE", 0.0
                continue
            d, n, e = replay(trace, cfg, k, v)
            if census_bad and v != "no_census":
                d, e = "REJECT_HARM(census)", 0.0
            decisions[cell], evals[cell] = f"{d}@{n}", e
        accepted = set(c for c in evals if evals[c] >= k / cfg["alpha"]) if v == "bonferroni" \
            else set(e_holm(evals, cfg["alpha"]))
        row = [("ADMIT" if c in accepted else decisions[c].split("@")[0].replace("UNDECIDED", "QUARANTINE"))
               + "@" + decisions[c].split("@")[-1] if "@" in decisions[c] else decisions[c] for c in cfg["cells"]]
        lines.append(f"| {v} | " + " | ".join(row) + " |")
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
