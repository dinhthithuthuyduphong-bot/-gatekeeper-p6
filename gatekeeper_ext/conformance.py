"""Theory/code conformance of a study configuration (docs/paper/THEORY_CODE_AUDIT.md, TC7).

The paper's guarantee (Lemma "Betting e-process", Theorem "Admission over a declared scope family") is for the mean-betting
e-process on i.i.d. trials, thresholded at 1/alpha_{c,k} from a ledger, or e-Holm over e-values read at stopping times.  The
frozen `gatekeeper_lite.gatekeeper.gatekeeper` also offers options under which that statement does NOT hold as written.  They
are kept (frozen studies used them) but every config is labelled here with the guarantee it actually has.

    task_priority        tasks matching patterns are consumed first: the sequence is not exchangeable, so the e-process
                         certifies the mean of the priority groups in the order consumed, not the scope mean -> NO guarantee
                         for STR over the scope (unless every group satisfies the null on its own).
    task_filter=reach_*  only tasks that reach an edited site are used.  With Z = 0 on the others, STR_P = p_reach STR_reach,
                         so the certificate gives STR_P <= -p_reach theta (+2 xi): sign kept, margin scaled by p_reach.
    evidence=discordant_sign  certifies q = P(help | discordant) > q0, i.e. STR <= -(2 q0 - 1) P(Z != 0): sign kept, margin
                         depends on the discordance rate, not theta.
    multiplicity=e-BH    false discovery rate, not the family-wise guarantee of the Theorem.
"""
from __future__ import annotations

from typing import Dict, List

FULL = "FULL"            # the paper's Theorem as stated
SIGN_ONLY = "SIGN_ONLY"  # no admitted harmful cell (STR > 0) w.p. >= 1 - alpha, but not the margin -theta
FDR = "FDR"              # false discovery rate only
NONE = "NONE"            # no guarantee for the scope mean


def check_config(cfg: Dict) -> Dict:
    findings: List[Dict] = []
    if cfg.get("task_priority"):
        findings.append({"option": "task_priority", "guarantee": NONE,
                         "why": "priority order is not exchangeable; the null on the conditional mean fails for the scope"})
    tf = cfg.get("task_filter")
    if tf and tf != "none":
        findings.append({"option": "task_filter=%s" % tf, "guarantee": SIGN_ONLY,
                         "why": "STR_P = p_reach * STR_reach: certificate gives STR_P <= -p_reach*theta + 2 xi"})
    if cfg.get("evidence") == "discordant_sign":
        findings.append({"option": "evidence=discordant_sign", "guarantee": SIGN_ONLY,
                         "why": "certifies STR <= -(2 q0 - 1) P(Z != 0), not -theta"})
    multi = cfg.get("multiplicity") or {}
    method = multi.get("method") if isinstance(multi, dict) else multi
    if method == "e-BH":
        findings.append({"option": "multiplicity=e-BH", "guarantee": FDR, "why": "FDR control, not family-wise"})
    cells = cfg.get("cells")
    if isinstance(cells, dict) and "alpha_total" in cfg and sum(cells.values()) > cfg["alpha_total"] + 1e-12:
        findings.append({"option": "cells", "guarantee": NONE, "why": "ledger allocations exceed alpha_total"})
    order = [FULL, SIGN_ONLY, FDR, NONE]
    level = max([f["guarantee"] for f in findings] or [FULL], key=order.index)
    return {"guarantee": level, "findings": findings}
