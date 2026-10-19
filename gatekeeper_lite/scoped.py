"""Scope-conditional admission ("scope before reuse").

One paired run per (skill, target); the tasks are then partitioned into declared
behaviour-class scopes (task-name patterns fixed in the protocol).  Each scope is its
own admission cell: Gatekeeper decides per scope, while B2/B6-R, which do not look at
behaviour classes, necessarily give the same decision for every scope.  Tasks that
match no declared class (e.g. the target's own regression suite) belong to every scope,
so a regression anywhere blocks admission in every scope.
"""
from __future__ import annotations

import copy
from typing import Dict, List, Sequence

from .gatekeeper import ADMIT, BindOutcome, gatekeeper, ground_truth, run_pair
from .runner import ArmResult, PairedRun


def _view(per_task: Dict[str, dict], ids: List[str]) -> PairedRun:
    base = ArmResult("baseline", {c: {"passed": per_task[c]["without"]} for c in ids}, 0, {})
    treat = ArmResult("treatment", {c: {"passed": per_task[c]["with"]} for c in ids}, 0, {})
    return PairedRun(base, treat, True)


def scope_members(case_ids: Sequence[str], scopes: Dict[str, List[str]]) -> Dict[str, List[str]]:
    every = [p for pats in scopes.values() for p in pats]
    shared = [c for c in case_ids if not any(p in c for p in every)]
    return {name: [c for c in case_ids if any(p in c for p in pats)] + shared
            for name, pats in scopes.items()}


def run_pair_scoped(cell: str, skills, target, ledger, cfg: dict) -> List[dict]:
    if cfg.get("multiplicity", {}).get("method") != "e-BH":
        raise ValueError("scoped admission requires multiplicity e-BH")
    base = run_pair(cell, skills, target, ledger, cfg)
    if "paired" not in base:
        out = []
        for name in cfg["scopes"]:
            rec = copy.deepcopy(base)
            rec["cell"], rec["scope_class"] = f"{cell}/{name}", name
            out.append(rec)
        return out
    per_task = base["paired"]["per_task"]
    reached_all = base.get("task_filter", {}).get("reached_ids")
    out = []
    for name, ids in scope_members(sorted(per_task), cfg["scopes"]).items():
        view = _view(per_task, ids)
        reached = set(reached_all) & set(ids) if reached_all is not None else None
        gk = gatekeeper(f"{cell}/{name}", skills, target, view, BindOutcome(True, "scoped"),
                        ledger, cfg, 0, reached)
        rec = copy.deepcopy(base)
        rec["cell"], rec["scope_class"] = f"{cell}/{name}", name
        rec["ground_truth"] = ground_truth(view)
        rec["paired"] = {k: v for k, v in base["paired"].items() if k != "per_task"}
        rec["paired"].update(tasks=len(ids), new_failures=view.new_failures,
                             resolved_failures=view.resolved_failures,
                             per_task={c: per_task[c] for c in ids})
        rec["gatekeeper"] = {"decision": gk.decision, "reason": gk.reason, "alpha": gk.alpha,
                             "threshold": gk.threshold, "tasks_used": gk.tasks_used,
                             "e_value": gk.e_value, "trajectory": gk.trajectory, "epoch": 0}
        rec["comparators"]["B8"] = {"decision": ADMIT if not view.new_failures else "REJECT",
                                    "cost_tasks": 2 * len(ids)}
        rec["comparators"]["Gatekeeper"] = {"decision": gk.decision,
                                            "cost_tasks": 2 * gk.tasks_used}
        out.append(rec)
    return out
