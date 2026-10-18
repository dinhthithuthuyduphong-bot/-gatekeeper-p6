"""Scope screening: D compatibility and I input assumptions.

Screen(S, x) = I(x) AND Compatible(D, x).  A pass is necessary, never sufficient, for
admission.  Missing information is reported as UNRESOLVED and treated as out of scope
(fail closed); it is never silently promoted to a match.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

MATCH, DRIFT, UNRESOLVED = "MATCH", "DRIFT", "UNRESOLVED"


def _version(text: str) -> Tuple[int, ...]:
    parts = re.findall(r"\d+", str(text))
    if not parts:
        raise ValueError(f"not a version: {text!r}")
    return tuple(int(p) for p in parts)


def _cmp(a: Tuple[int, ...], b: Tuple[int, ...]) -> int:
    n = max(len(a), len(b))
    a, b = a + (0,) * (n - len(a)), b + (0,) * (n - len(b))
    return (a > b) - (a < b)


def satisfies(version: str, spec: str) -> bool:
    """spec like '>=3.9,<3.13' or '==8.1.7'."""
    v = _version(version)
    for clause in [c.strip() for c in spec.split(",") if c.strip()]:
        m = re.match(r"(>=|<=|==|!=|>|<)\s*(.+)", clause)
        if not m:
            raise ValueError(f"bad clause {clause!r}")
        op, ref = m.group(1), _version(m.group(2))
        c = _cmp(v, ref)
        ok = {">=": c >= 0, "<=": c <= 0, "==": c == 0, "!=": c != 0, ">": c > 0, "<": c < 0}[op]
        if not ok:
            return False
    return True


@dataclass
class ScreenResult:
    relation: str                   # MATCH / DRIFT / UNRESOLVED
    in_scope: bool
    reasons: List[str] = field(default_factory=list)


def environment_relation(contract: dict, env: dict) -> Tuple[str, List[str]]:
    reasons: List[str] = []
    checks = []
    if contract.get("python"):
        checks.append(("python", contract["python"], env.get("python")))
    for pkg, spec in (contract.get("packages") or {}).items():
        checks.append((pkg, spec, (env.get("packages") or {}).get(pkg)))
    if not checks:
        return UNRESOLVED, ["empty source environment contract"]
    relation = MATCH
    for name, spec, observed in checks:
        if observed in (None, ""):
            reasons.append(f"{name}: not declared by target")
            relation = UNRESOLVED if relation == MATCH else relation
            continue
        try:
            ok = satisfies(observed, spec)
        except ValueError as exc:
            reasons.append(f"{name}: {exc}")
            relation = UNRESOLVED if relation == MATCH else relation
            continue
        if not ok:
            reasons.append(f"{name} {observed} violates {spec}")
            relation = DRIFT
    return relation, reasons


def screen(skill, target) -> ScreenResult:
    relation, reasons = environment_relation(skill.D, target.environment())
    caps = set(target.manifest.get("capabilities", []))
    for predicate in skill.I:
        if predicate.startswith("target_declares:"):
            needed = predicate.split(":", 1)[1]
            if needed not in caps:
                reasons.append(f"I failed: target does not declare {needed}")
                return ScreenResult(relation, False, reasons)
    return ScreenResult(relation, relation == MATCH, reasons)
