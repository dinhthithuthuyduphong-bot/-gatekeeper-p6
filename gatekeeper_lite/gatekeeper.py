"""Gatekeeper-Lite admission pipeline and comparators.

Gatekeeper (Algorithm 1, Lite):  scope screen -> bind (abstain = out of scope)
  -> paired trials consumed sequentially -> betting e-process
  -> ADMIT if E_n >= 1/alpha_cell within budget, else QUARANTINE.
Comparators:
  B1 no skill; B2 unrestricted reuse (admit whenever the procedure binds);
  B6-R replay + environment fingerprint (reconstruction, not the paper's B6);
  B8 always-retest (run every task with and without the skill, admit if no new failure).
"""
from __future__ import annotations

import difflib
import random
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Sequence

from . import transforms
from .eprocess import AlphaLedger, BettingEProcess, make_eprocess
from .runner import PairedRun, paired_run, reach_pass
from .screen import MATCH, screen
from .skill import Skill, Target

ADMIT, QUARANTINE, OUT_OF_SCOPE, REJECT, ENV_UNRESOLVED, REJECT_HARM = (
    "ADMIT", "QUARANTINE", "OUT_OF_SCOPE", "REJECT", "ENV_UNRESOLVED", "REJECT_HARM")


def _ordered_tasks(case_ids, seed: int, priority=None) -> list:
    """Frozen sampling order: tasks matching declared priority patterns first.

    The order depends only on task identifiers and the seed, never on outcomes.
    """
    rng = random.Random(seed)
    groups = [[] for _ in range((len(priority) if priority else 0) + 1)]
    for c in case_ids:
        idx = next((i for i, pat in enumerate(priority or []) if pat in c), len(groups) - 1)
        groups[idx].append(c)
    order = []
    for g in groups:
        rng.shuffle(g)
        order.extend(g)
    return order


@dataclass
class BindOutcome:
    ok: bool
    source: Optional[str] = None
    reason: str = ""
    sites: List[dict] = field(default_factory=list)
    footprint: List[str] = field(default_factory=list)


def bind(skills: Sequence[Skill], target: Target) -> BindOutcome:
    """Apply one skill, or a composition S1 o S2 (applied in the given order)."""
    source, sites, footprint = target.source(), [], set()
    for skill in skills:
        try:
            res = skill.transform().apply(source, single_site=skill.single_site)
        except transforms.Abstain as exc:
            return BindOutcome(False, reason=f"{skill.skill_id}: ABSTAIN {exc.reason}"
                               + (f" ({exc.detail})" if exc.detail else ""))
        source = res.source
        sites += [dict(skill=skill.skill_id, line=s.lineno, function=s.function,
                       snippet=s.snippet) for s in res.sites]
        footprint.update(res.footprint)
    return BindOutcome(True, source, "", sites, sorted(footprint))


def footprint_overlap(a: Sequence[str], b: Sequence[str]) -> List[str]:
    """K1 ∩ K2, ignoring generic behaviour tags that every skill of a family shares."""
    return sorted((set(a) & set(b)) - {"func:<module>"})


def _functions_dump(source: str, name: str) -> list:
    import ast
    return [ast.dump(n) for n in ast.walk(ast.parse(source))
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]


def replay(skill: Skill) -> dict:
    """Source replay (B5/B6 ingredient): reproduce each recorded fix on its source.

    With "compare_function", only that function is compared (the official commit may
    also touch unrelated code in the same file).
    """
    checks = []
    for ex in skill.P:
        before = (skill.root / ex["before"]).read_text(encoding="utf-8")
        after = (skill.root / ex["after"]).read_text(encoding="utf-8")
        try:
            out = skill.transform().apply(before, single_site=skill.single_site).source
            if ex.get("compare_function"):
                got, want = (_functions_dump(x, ex["compare_function"]) for x in (out, after))
                ok = bool(want) and got == want
            else:
                ok = transforms.ast_equal(out, after)
            checks.append({"example": ex["before"], "passed": ok,
                           "heldout": bool(ex.get("heldout", False))})
        except transforms.Abstain as exc:
            checks.append({"example": ex["before"], "passed": False, "error": exc.reason})
    return {"passed": bool(checks) and all(c["passed"] for c in checks), "checks": checks}


def ground_truth(run: PairedRun) -> str:
    """Independent label from ALL tasks (primary endpoint: any new failure = harm)."""
    if run.new_failures:
        return "HARMFUL"
    if run.resolved_failures:
        return "BENEFICIAL"
    return "NO_DELTA"


@dataclass
class GatekeeperResult:
    decision: str
    reason: str = ""
    alpha: Optional[float] = None
    threshold: Optional[float] = None
    tasks_used: int = 0
    e_value: Optional[float] = None
    trajectory: List[float] = field(default_factory=list)
    epoch: int = 0


def gatekeeper(cell: str, skills: Sequence[Skill], target: Target, run: Optional[PairedRun],
               bound: BindOutcome, ledger: AlphaLedger, cfg: dict, epoch: int = 0,
               reached: Optional[set] = None) -> GatekeeperResult:
    for skill in skills:
        scr = screen(skill, target)
        if not scr.in_scope:
            return GatekeeperResult(OUT_OF_SCOPE, f"{skill.skill_id}: screen {scr.relation} "
                                    + "; ".join(scr.reasons), epoch=epoch)
    if not bound.ok:
        return GatekeeperResult(OUT_OF_SCOPE, bound.reason, epoch=epoch)
    if run is None or not run.integrity_ok:
        return GatekeeperResult(QUARANTINE, "pair integrity failed", epoch=epoch)
    order = _ordered_tasks(run.case_ids, cfg["seed"] * 1000 + epoch, cfg.get("task_priority"))
    if reached is not None:
        order = [c for c in order if c in reached]
        if not order:
            return GatekeeperResult(QUARANTINE, "no task reaches the edited site", epoch=epoch)
    alpha = ledger.draw(cell, epoch)
    threshold = 1.0 / alpha
    ep = make_eprocess(cfg)
    budget = min(cfg["budget_tasks"], len(order))
    for n, case_id in enumerate(order[:budget], start=1):
        value = ep.update(run.z(case_id))
        if getattr(ep, "harm_value", 0.0) >= threshold:
            return GatekeeperResult(REJECT_HARM,
                                    f"harm e-value {ep.harm_value:.1f} >= {threshold:.0f} "
                                    f"(helped {ep.helped}, hurt {ep.hurt})",
                                    alpha, threshold, n, value, ep.history, epoch)
        if value >= threshold:
            return GatekeeperResult(ADMIT, f"E={value:.1f} >= 1/alpha={threshold:.0f}",
                                    alpha, threshold, n, value, ep.history, epoch)
    return GatekeeperResult(QUARANTINE, f"budget exhausted: E={ep.value:.2f} < {threshold:.0f}",
                            alpha, threshold, budget, ep.value, ep.history, epoch)


def comparators(skills: Sequence[Skill], target: Target, run: Optional[PairedRun],
                bound: BindOutcome) -> Dict[str, dict]:
    out = {"B1": {"decision": "NO_SKILL", "cost_tasks": 0}}
    out["B2"] = {"decision": ADMIT if bound.ok else OUT_OF_SCOPE, "cost_tasks": 0}
    # B6-R: structural bind + source replay + environment fingerprint relation
    if not bound.ok:
        out["B6R"] = {"decision": REJECT, "reason": bound.reason, "cost_tasks": 0}
    else:
        replays = [replay(s) for s in skills]
        relations = [screen(s, target).relation for s in skills]
        if not all(r["passed"] for r in replays):
            dec, why = REJECT, "source replay failed"
        elif any(r != MATCH for r in relations):
            dec = ENV_UNRESOLVED if "UNRESOLVED" in relations else REJECT
            why = f"fingerprint {relations}"
        else:
            dec, why = ADMIT, "replay passed, fingerprint MATCH"
        out["B6R"] = {"decision": dec, "reason": why, "fingerprint": relations,
                      "replay": replays, "cost_tasks": 0}
    # B8: always retest every task
    if not bound.ok or run is None:
        out["B8"] = {"decision": OUT_OF_SCOPE, "cost_tasks": 0}
    else:
        n = len(run.case_ids)
        out["B8"] = {"decision": ADMIT if not run.new_failures else REJECT,
                     "cost_tasks": 2 * n}
    return out


def sensitivity(run: PairedRun, patterns: Sequence[Sequence[str]]) -> dict:
    """Ground truth recomputed after removing declared task classes (pre-declared)."""
    out = {}
    for pats in patterns:
        keep = [c for c in run.case_ids if not any(p in c for p in pats)]
        new = [c for c in keep if run.baseline.results[c]["passed"]
               and not run.treatment.results[c]["passed"]]
        res = [c for c in keep if not run.baseline.results[c]["passed"]
               and run.treatment.results[c]["passed"]]
        out["without:" + "+".join(pats)] = {
            "truth": "HARMFUL" if new else ("BENEFICIAL" if res else "NO_DELTA"),
            "new_failures": len(new), "resolved": len(res), "tasks": len(keep)}
    return out


def run_pair(cell: str, skills: Sequence[Skill], target: Target, ledger: AlphaLedger,
             cfg: dict, epoch: int = 0) -> dict:
    bound = bind(skills, target)
    run = paired_run(target, bound.source, cfg["seed"],
                     timeout=cfg.get("timeout_seconds", 120)) if bound.ok else None
    reach = None
    if run is not None and cfg.get("task_filter") == "reach_baseline":
        functions = sorted({s["function"] for s in bound.sites if s.get("function")})
        reach = reach_pass(target, functions, cfg["seed"], cfg.get("timeout_seconds", 600))
    reached = set(reach["reached"]) & set(run.case_ids) if reach else None
    gk = gatekeeper(cell, skills, target, run, bound, ledger, cfg, epoch, reached)
    record = {
        "cell": cell,
        "skills": [s.skill_id for s in skills],
        "target": target.target_id,
        "regime": target.regime,
        "fingerprint": target.fingerprint(),
        "bind": {"ok": bound.ok, "reason": bound.reason, "sites": bound.sites,
                 "footprint": bound.footprint,
                 "diff": "".join(difflib.unified_diff(
                     target.source().splitlines(keepends=True),
                     bound.source.splitlines(keepends=True),
                     fromfile=f"a/{target.module}", tofile=f"b/{target.module}"))
                 if bound.ok else ""},
        "ground_truth": ground_truth(run) if run else "NOT_APPLICABLE",
        "comparators": comparators(skills, target, run, bound),
        "gatekeeper": asdict(gk),
    }
    screening = len(run.case_ids) if (run is not None and reach) else 0
    record["comparators"]["Gatekeeper"] = {"decision": gk.decision,
                                           "cost_tasks": 2 * gk.tasks_used + screening}
    record["task_filter"] = {"mode": cfg.get("task_filter", "none"),
                             "available": reach is not None,
                             "reaching_tasks": len(reached) if reached is not None else None,
                             "reached_ids": sorted(reached) if reached is not None else None,
                             "discriminating_tasks": (sum(1 for c in run.case_ids if run.z(c) != 0)
                                                      if run is not None else None),
                             "screening_cost_tasks": screening}
    if run:
        record["paired"] = {
            "integrity_ok": run.integrity_ok, "integrity_notes": run.integrity_notes,
            "tasks": len(run.case_ids),
            "new_failures": run.new_failures, "resolved_failures": run.resolved_failures,
            "loss_without": round(run.suite_loss("baseline"), 4),
            "loss_with": round(run.suite_loss("treatment"), 4),
            "seconds": round(run.baseline.seconds + run.treatment.seconds, 3),
            "per_task": {c: {"without": run.baseline.results[c]["passed"],
                             "with": run.treatment.results[c]["passed"], "Z": run.z(c)}
                         for c in run.case_ids},
        }
        if cfg.get("sensitivity_exclude"):
            record["sensitivity"] = sensitivity(run, cfg["sensitivity_exclude"])
        record["paired"]["Z_suite"] = round(record["paired"]["loss_with"]
                                            - record["paired"]["loss_without"], 4)
    return record


@dataclass
class Certificate:
    cell: str
    target: str
    fingerprint: str
    epoch: int


def retirement_check(cert: Certificate, current: Target) -> dict:
    """Revoke admission whenever the environment fingerprint changes (no test needed)."""
    now = current.fingerprint()
    revoked = now != cert.fingerprint
    return {"cell": cert.cell, "target": cert.target, "admitted_under": cert.fingerprint,
            "current": now, "status": "REVOKED_REVALIDATE" if revoked else "STILL_VALID"}
