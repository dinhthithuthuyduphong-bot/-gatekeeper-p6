"""Execution rule for a skill library (paper, Section "Problem Formulation", paragraph "Execution rule"; Corollary
"What actually runs"; docs/paper/PHASE1_REVIEW.md, gap G1; docs/TECH_DEBT.md, TD7).

Per-cell certificates say nothing about skills that run TOGETHER.  The rule: split the set E of skills to be executed into
the connected components of its footprint-overlap graph (two skills are adjacent when their footprints intersect); E may run
only if every component is an admitted cell (a single admitted skill, or an admitted composite of exactly that component).
Under the non-interaction assumption for disjoint footprints, this bounds the risk of E by the sum over its components.

Enabling edges (Study R2): a footprint computed on the ORIGINAL code misses a skill that creates or removes another skill's
sites (on pydal, `type(x) is not int` -> `not isinstance(x, int)` creates a site for the bool-exclusion guard in a function the
guard did not touch before).  `edges` adds such pairs, measured by applying the two skills in both orders
(tools/library_census.py: non-commuting or site-changing pairs), to the overlap graph.

Lives in gatekeeper_ext (not gatekeeper_lite) on purpose: every frozen study hashes every module of gatekeeper_lite, so a
new module there would break their freeze verification.  It reuses gatekeeper_lite.gatekeeper.footprint_overlap unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Collection, Dict, FrozenSet, Iterable, List, Mapping, Optional, Sequence, Set

from gatekeeper_lite.gatekeeper import footprint_overlap

Cell = FrozenSet[str]          # the skill ids applied together in one scope; a singleton is a single-skill cell


def site_footprint(sites: Iterable[Mapping[str, str]]) -> List[str]:
    """Module-qualified footprint from binding sites ({"module", "function"}), module-level code INCLUDED.

    The frozen `footprint_overlap` drops the generic tag `func:<module>`, because a transform's own footprint does not say which
    file it came from; two skills editing module-level code of the same file would then look disjoint, which Corollary
    "What actually runs" does not allow (theory/code audit TC5).  Qualified ids `site:<module>::<function>` keep module-level
    regions apart per file and are never dropped."""
    return sorted({"site:%s::%s" % (s["module"], s["function"]) for s in sites})


Edges = Collection[Collection[str]]   # extra adjacencies (enabling pairs), each a pair of skill ids


def components(footprints: Mapping[str, Sequence[str]], edges: Edges = ()) -> List[Cell]:
    """Connected components of the footprint-overlap graph plus `edges`, each a frozenset of skill ids (sorted)."""
    ids = sorted(footprints)
    parent = {i: i for i in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a_i, a in enumerate(ids):
        for b in ids[a_i + 1:]:
            if footprint_overlap(footprints[a], footprints[b]):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[rb] = ra
    for e in edges:
        a, b = sorted(e)
        if a in parent and b in parent:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra
    groups: Dict[str, Set[str]] = {}
    for i in ids:
        groups.setdefault(find(i), set()).add(i)
    return sorted((frozenset(g) for g in groups.values()), key=lambda g: sorted(g))


@dataclass
class ExecutionDecision:
    allowed: bool
    components: List[Cell]
    missing: List[Cell] = field(default_factory=list)   # components that are not admitted cells

    def explain(self) -> str:
        if self.allowed:
            return "allowed: every component is an admitted cell (%d components)" % len(self.components)
        return "refused: not admitted as a cell: %s" % ", ".join("{%s}" % ", ".join(sorted(c)) for c in self.missing)


def check_execution(footprints: Mapping[str, Sequence[str]], admitted: Iterable[Cell], edges: Edges = ()) -> ExecutionDecision:
    """Decide whether the skills in `footprints` (skill id -> footprint) may run together in one scope, given the admitted
    cells of that scope.  A component of size 1 needs the single skill admitted; a larger one needs exactly its composite."""
    adm = {frozenset(c) for c in admitted}
    comps = components(footprints, edges)
    missing = [c for c in comps if c not in adm]
    return ExecutionDecision(allowed=not missing, components=comps, missing=missing)


def executable_subset(footprints: Mapping[str, Sequence[str]], admitted: Iterable[Cell],
                      priority: Optional[Sequence[str]] = None, edges: Edges = ()) -> List[str]:
    """Greedy selection in priority order (default: sorted ids): add a skill only if the enlarged set still satisfies the
    execution rule.  The result always satisfies the rule; it is maximal for the order, not necessarily maximum."""
    adm = {frozenset(c) for c in admitted}
    chosen: List[str] = []
    for sid in (priority or sorted(footprints)):
        trial = chosen + [sid]
        if check_execution({k: footprints[k] for k in trial}, adm, edges).allowed:
            chosen = trial
    return chosen


def composites_to_test(footprints: Mapping[str, Sequence[str]], admitted: Iterable[Cell], edges: Edges = ()) -> List[Cell]:
    """The composite cells that must be admitted before the whole set may run: its non-admitted components of size >= 2."""
    return [c for c in check_execution(footprints, admitted, edges).missing if len(c) >= 2]


def canonical_order(cell: Iterable[str], registration: Sequence[str]) -> List[str]:
    """The one order in which a composite cell is applied and certified (paper, Section "Problem formulation"): registration
    order, fixed before any data.  A set of skills defines one composite cell; the certificate covers this order only, which
    matters when one rewrite enables another (Study R2).  Skills not in the registration list are refused."""
    pos = {sid: i for i, sid in enumerate(registration)}
    missing = sorted(set(cell) - set(pos))
    if missing:
        raise KeyError("unregistered skills: %s" % missing)
    return sorted(cell, key=pos.__getitem__)

