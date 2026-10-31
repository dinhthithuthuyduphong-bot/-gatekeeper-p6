"""Library ledger: the allocation Theorem "Admission over a declared scope family" asks for, as code (theory/code audit TC2).

The theorem needs a share alpha_{c,k} for EVERY cell c that could ever be formed (single skills and compositions) and every
epoch k, fixed in advance as a function of the cell's identity, with total at most alpha.  The frozen
`gatekeeper_lite.eprocess.AlphaLedger` covers a list of cells fixed at construction (enough for Studies D-H, which have no
compositions); it has no rule for composites or for skills added later.

Rule (declared capacity N of the scope's library, single share s):
    single skill            alpha * s / N
    composite of m >= 2     alpha * (1 - s) * 6 / (pi^2 (m-1)^2) / C(N, m)
    epoch k                 times 6 / (pi^2 (k+1)^2)
The share depends only on the cell's size, N and s, so it is fixed before any data and does not change when skills are
registered later (up to N).  Sum over all cells and epochs:
    alpha * [ s + (1 - s) * sum_{m=2..N} 6/(pi^2 (m-1)^2) ] * sum_k 6/(pi^2 (k+1)^2)  <=  alpha.
"""
from __future__ import annotations

import math
from typing import Dict, FrozenSet, Iterable, List, Tuple

Cell = FrozenSet[str]


def _basel(i: int) -> float:
    return 6.0 / (math.pi ** 2 * i * i)


class LibraryLedger:
    def __init__(self, alpha: float, capacity: int, single_share: float = 0.5, skills: Iterable[str] = ()):
        if not (0 < alpha < 1 and capacity >= 1 and 0 < single_share <= 1):
            raise ValueError("need 0 < alpha < 1, capacity >= 1, 0 < single_share <= 1")
        self.alpha, self.capacity, self.single_share = alpha, capacity, single_share
        self.skills: List[str] = []
        self.spent: Dict[Tuple[Cell, int], float] = {}
        for s in skills:
            self.register(s)

    def register(self, skill: str) -> None:
        """Add a skill to the library.  Shares of existing cells do not change."""
        if skill in self.skills:
            raise ValueError("skill %r already registered" % skill)
        if len(self.skills) >= self.capacity:
            raise ValueError("library capacity %d reached: a larger library needs a new, larger declaration before any data"
                             % self.capacity)
        self.skills.append(skill)

    def share(self, cell: Iterable[str], epoch: int = 0) -> float:
        c = frozenset(cell)
        unknown = sorted(c - set(self.skills))
        if not c or unknown:
            raise KeyError("cell has unregistered skills: %s" % unknown)
        if epoch < 0:
            raise ValueError("epoch must be >= 0")
        m, n = len(c), self.capacity
        base = (self.single_share / n if m == 1 else
                (1 - self.single_share) * _basel(m - 1) / math.comb(n, m))
        return self.alpha * base * _basel(epoch + 1)

    def draw(self, cell: Iterable[str], epoch: int = 0) -> float:
        """Spend the share of (cell, epoch) once; a second draw of the same pair is refused (alpha is never recycled)."""
        key = (frozenset(cell), epoch)
        if key in self.spent:
            raise ValueError("alpha for %s epoch %d already spent" % (sorted(key[0]), epoch))
        a = self.share(key[0], epoch)
        self.spent[key] = a
        return a

    def total_bound(self) -> float:
        """Exact sum of the shares of all cells over all subsets of a full library and all epochs (<= alpha)."""
        n = self.capacity
        per_epoch = self.single_share + (1 - self.single_share) * sum(_basel(m - 1) for m in range(2, n + 1))
        return self.alpha * per_epoch   # times sum_k 6/(pi^2 (k+1)^2) = 1
