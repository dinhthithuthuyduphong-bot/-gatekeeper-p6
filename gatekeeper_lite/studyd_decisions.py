"""Single source of truth for Study D cell decisions (used by aggregate, report, ablation).

Rules (protocol sections 3, 5, 7):
  * OUT_OF_SCOPE     skill bound to no module of the target.
  * CENSUS_INVALID   census baseline unusable -> technical, never an outcome, e = 0, not
                     admitted by any comparator that needs the census (B8, Gatekeeper).
  * REJECT_HARM      harm alarm fired, or the census found a persistent new failure.
  * Gatekeeper ADMIT only through e-Holm over min(e_benefit, e_cert) of eligible cells.
  * B2  ADMIT whenever the skill binds.
  * B6R ADMIT iff binds AND source replay passes AND fingerprint relation is MATCH.
  * B8  REJECT if any regression in the full-budget draws or a persistent census failure;
        CENSUS_INVALID if the census is unusable; otherwise ADMIT.
"""
from __future__ import annotations

from typing import Dict, List

from .eprocess import e_bh, e_holm


def cell_inputs(cfg: dict, results: Dict[str, dict]) -> List[dict]:
    out = []
    for cell in cfg["cells"]:
        tgt, scope = cell.split("/")
        r = results.get(tgt, {})
        sc = r.get("scopes", {}).get(scope)
        census = r.get("census", {})
        out.append({"cell": cell, "target": tgt, "scope": scope, "result": r, "scope_result": sc,
                    "binds": bool(r.get("bind", {}).get("treated_modules")),
                    "census_invalid": census.get("status") == "INVALID",
                    "census_bad": bool(census.get("new_failures")),
                    "replay_ok": bool(r.get("B6R_replay", {}).get("passed")),
                    "fingerprint": r.get("B6R_fingerprint", {}).get("relation")})
    return out


def eligible_e(c: dict, stop: str, e_min: float) -> float:
    if c["census_invalid"] or c["census_bad"] or stop not in ("ADMIT", "UNDECIDED"):
        return 0.0
    return e_min


def decide(cfg: dict, results: Dict[str, dict]) -> List[dict]:
    cells = cell_inputs(cfg, results)
    evals = {}
    for c in cells:
        sc = c["scope_result"]
        c["stop"] = sc["decision"] if sc else "OUT_OF_SCOPE"
        evals[c["cell"]] = eligible_e(c, c["stop"], sc["e_min"]) if sc else 0.0
    holm, bh = set(e_holm(evals, cfg["alpha"])), set(e_bh(evals, cfg["alpha"]))
    for c in cells:
        sc = c["scope_result"]
        c["e"] = evals[c["cell"]]
        c["B2"] = "ADMIT" if c["binds"] else "OUT_OF_SCOPE"
        c["B6R"] = ("OUT_OF_SCOPE" if not c["binds"] else
                    "ADMIT" if c["replay_ok"] and c["fingerprint"] == "MATCH" else "REJECT")
        if not sc:
            c["B8"] = c["Gatekeeper"] = "OUT_OF_SCOPE"
            c["eBH"] = "—"
            continue
        if c["census_invalid"]:
            c["B8"] = c["Gatekeeper"] = "CENSUS_INVALID"
            c["eBH"] = "—"
            continue
        c["B8"] = "REJECT" if (sc["b8"]["counts"]["hurt"] or c["census_bad"]) else "ADMIT"
        c["Gatekeeper"] = ("REJECT_HARM" if (c["stop"] == "REJECT_HARM" or c["census_bad"]) else
                           "ADMIT" if c["cell"] in holm else "QUARANTINE")
        c["eBH"] = "ADMIT" if c["cell"] in bh and c["Gatekeeper"] != "REJECT_HARM" else "—"
    return cells
