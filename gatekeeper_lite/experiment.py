"""Runs a frozen experiment configuration and returns a JSON-serialisable record."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Dict, List

from .eprocess import AlphaLedger, e_bh
from .gatekeeper import (ADMIT, Certificate, footprint_overlap, retirement_check, run_pair)
from .skill import Skill, Target

COMPARATORS = ["B2", "B6R", "B8", "Gatekeeper"]
NOT_ADMITTED_BY_HARM = "REJECT_HARM"


def _cell(skills: List[Skill], target: Target) -> str:
    """(skill, scope) cell; the scope class is declared by the target manifest in advance."""
    return "+".join(s.skill_id for s in skills) + "@" + target.manifest["scope"]


def _file_sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def summarize(records: List[dict]) -> Dict[str, dict]:
    summary = {}
    for comp in COMPARATORS:
        row = {"harmful_admitted": 0, "beneficial_admitted": 0, "no_delta_admitted": 0,
               "beneficial_not_admitted": 0, "cost_tasks": 0}
        for r in records:
            dec = r["comparators"][comp]["decision"]
            truth = r["ground_truth"]
            row["cost_tasks"] += r["comparators"][comp].get("cost_tasks", 0)
            if dec == ADMIT:
                key = {"HARMFUL": "harmful_admitted", "BENEFICIAL": "beneficial_admitted",
                       "NO_DELTA": "no_delta_admitted"}.get(truth)
                if key:
                    row[key] += 1
            elif truth == "BENEFICIAL":
                row["beneficial_not_admitted"] += 1
        summary[comp] = row
    summary["_denominators"] = {
        "pairs": len(records),
        "harmful": sum(r["ground_truth"] == "HARMFUL" for r in records),
        "beneficial": sum(r["ground_truth"] == "BENEFICIAL" for r in records),
        "no_delta": sum(r["ground_truth"] == "NO_DELTA" for r in records),
        "not_applicable": sum(r["ground_truth"] == "NOT_APPLICABLE" for r in records),
    }
    return summary


def run_experiment(config_path: Path) -> dict:
    config_path = Path(config_path).resolve()
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    if cfg.get("requires_freeze") and cfg.get("status") != "FROZEN":
        raise SystemExit(f"{config_path.name}: status is {cfg.get('status')!r}; this experiment "
                         "only runs after the protocol is frozen (status FROZEN).")
    base = config_path.parent
    skills = {}
    for p in sorted((base / cfg["skills_dir"]).glob("*.json")):
        s = Skill.load(p)
        skills[s.skill_id] = s
    targets = {p.name: Target.load(p) for p in sorted((base / cfg["targets_dir"]).iterdir())
               if (p / "gk_target.json").exists()}
    ledger = AlphaLedger(cfg["alpha_total"], cfg["cells"])

    records, certificates = [], {}
    for pair in cfg["pairs"]:
        sk = [skills[i] for i in pair["skills"]]
        rec = run_pair(_cell(sk, targets[pair["target"]]), sk, targets[pair["target"]], ledger, cfg)
        records.append(rec)
        if rec["gatekeeper"]["decision"] == ADMIT:
            certificates[(rec["cell"], rec["target"])] = Certificate(
                rec["cell"], rec["target"], rec["fingerprint"], rec["gatekeeper"]["epoch"])

    multi = cfg.get("multiplicity", {})
    if multi.get("method") == "e-BH":
        # Every cell that reached a stopping point with an e-value takes part; harmful
        # rejections and out-of-scope cells enter with e = 0 (they can never be admitted).
        pool = {r["cell"]: (r["gatekeeper"]["e_value"] or 0.0)
                if r["gatekeeper"]["decision"] in ("ADMIT", "PENDING_EBH") else 0.0
                for r in records}
        admitted = set(e_bh(pool, multi["fdr"]))
        for r in records:
            if r["gatekeeper"]["decision"] in ("ADMIT", "PENDING_EBH"):
                final = ADMIT if r["cell"] in admitted else "QUARANTINE"
                r["gatekeeper"]["reason"] += f"; e-BH(fdr={multi['fdr']}, K={len(pool)}) -> {final}"
                r["gatekeeper"]["decision"] = final
                r["comparators"]["Gatekeeper"]["decision"] = final
        for r in records:
            if r["gatekeeper"]["decision"] == ADMIT:
                certificates[(r["cell"], r["target"])] = Certificate(
                    r["cell"], r["target"], r["fingerprint"], r["gatekeeper"]["epoch"])

    compositions = []
    for comp in cfg.get("compositions", []):
        sk = [skills[i] for i in comp["skills"]]
        target = targets[comp["target"]]
        singles = [r for r in records if r["target"] == target.target_id
                   and len(r["skills"]) == 1 and r["skills"][0] in comp["skills"]]
        composite = run_pair(_cell(sk, target), sk, target, ledger, cfg)
        overlap = footprint_overlap(*[r["bind"]["footprint"] for r in singles]) \
            if len(singles) == 2 else []
        compositions.append({
            "skills": comp["skills"], "target": target.target_id,
            "footprint_overlap": overlap,
            "single_Z": {r["skills"][0]: r.get("paired", {}).get("Z_suite") for r in singles},
            "single_truth": {r["skills"][0]: r["ground_truth"] for r in singles},
            "composite_Z": composite.get("paired", {}).get("Z_suite"),
            "composite_truth": composite["ground_truth"],
            "per_skill_B6R_admits_both": all(r["comparators"]["B6R"]["decision"] == ADMIT
                                             for r in singles),
            "gatekeeper_composite_decision": composite["gatekeeper"]["decision"],
            "record": composite,
        })

    retirements = []
    for ret in cfg.get("retirement", []):
        sk = [skills[i] for i in ret["skills"]]
        target = targets[ret["target"]]
        cell = _cell(sk, target)
        cert = certificates.get((cell, target.target_id))
        if cert is None:
            retirements.append({"cell": cell, "target": target.target_id,
                                "status": "NO_CERTIFICATE (skill was not admitted)"})
            continue
        changed = target.with_environment(**ret["change"])
        check = retirement_check(cert, changed)
        check["change"] = ret["change"]
        if check["status"].startswith("REVOKED"):
            rec = run_pair(cell, sk, changed, ledger, cfg, epoch=cert.epoch + 1)
            check["revalidation"] = {"decision": rec["gatekeeper"]["decision"],
                                     "reason": rec["gatekeeper"]["reason"],
                                     "alpha": rec["gatekeeper"]["alpha"],
                                     "tasks_used": rec["gatekeeper"]["tasks_used"]}
        retirements.append(check)

    return {
        "schema": "gatekeeper_lite_run_v1",
        "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "config": cfg,
        "config_sha256": _file_sha(config_path),
        "skill_sha256": {k: v.digest() for k, v in skills.items()},
        "alpha_spent": [list(x) for x in ledger.spent],
        "records": records,
        "summary": summarize(records),
        "compositions": compositions,
        "retirements": retirements,
        "evidence_class": "CONSTRUCTED_DEMO_FIXTURES",
        "limits": [
            "Targets are constructed demo fixtures, not independent repositories.",
            "A task is one oracle case inside one target; tasks are not i.i.d. contexts.",
            "B6-R is a reconstruction of the paper's B6, not the original system.",
            "Counts are descriptive; no population rate or superiority claim.",
        ],
    }
