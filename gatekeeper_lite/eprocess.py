"""Anytime-valid admission evidence (betting e-process) and the alpha ledger.

Paired difference Z = loss(with skill) - loss(without skill), Z in [-1, 1].
Admission wants STR = E[Z] <= -theta.  With Y = -Z this is E[Y] >= theta.

Null H0: E[Y] < theta (benefit margin not reached).  The wealth process
    K_n = prod_i (1 + lambda_i * (Y_i - theta)),  lambda_i in [0, 1/(1+theta))
uses a predictable bet lambda_i (computed only from Y_1..Y_{i-1}).  Each factor is
non-negative and has conditional mean <= 1 under H0, so K_n is a non-negative
supermartingale and Ville's inequality gives P(sup_n K_n >= 1/alpha) <= alpha,
valid at data-dependent stopping times.  (Construction in the spirit of
Waudby-Smith & Ramdas 2024; this is the project's implementation, not the
paper's code.)  The guarantee assumes i.i.d. paired tasks from the scope.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class BettingEProcess:
    def __init__(self, theta: float, max_bet_fraction: float = 0.5, prior_mean: float = 0.5,
                 prior_weight: float = 1.0):
        if not 0 < theta < 1:
            raise ValueError("theta must be in (0, 1)")
        self.theta = theta
        self.lam_cap = max_bet_fraction / (1.0 + theta)
        self.prior_mean, self.prior_weight = prior_mean, prior_weight
        self.ys: List[float] = []
        self.log_wealth = 0.0
        self.history: List[float] = [1.0]

    def _bet(self) -> float:
        n = len(self.ys)
        mean = (self.prior_mean * self.prior_weight + sum(self.ys)) / (self.prior_weight + n)
        if n >= 2:
            mu = sum(self.ys) / n
            var = sum((y - mu) ** 2 for y in self.ys) / (n - 1)
        else:
            var = 0.25
        edge = mean - self.theta
        lam = edge / (var + edge * edge + 1e-9) if edge > 0 else 0.0
        return max(0.0, min(lam, self.lam_cap))

    def update(self, z: float) -> float:
        if not -1.0 <= z <= 1.0:
            raise ValueError("paired difference must lie in [-1, 1]")
        y = -z
        lam = self._bet()                     # predictable: uses past only
        factor = 1.0 + lam * (y - self.theta)
        self.log_wealth += math.log(max(factor, 1e-300))
        self.ys.append(y)
        self.history.append(self.value)
        return self.value

    @property
    def value(self) -> float:
        return math.exp(self.log_wealth)


@dataclass
class AlphaLedger:
    """Pre-allocated error budget per (skill, scope) cell; never recycled.

    Epoch k of a cell (k = 0 first admission, k >= 1 re-admission after retirement)
    spends alpha_cell * 6 / (pi^2 (k+1)^2); the sum over all epochs is <= alpha_cell.
    """
    total: float
    cells: Dict[str, float]
    spent: List[Tuple[str, int, float]] = field(default_factory=list)

    def __post_init__(self):
        if sum(self.cells.values()) > self.total + 1e-12:
            raise ValueError("cell allocations exceed the total alpha budget")

    def draw(self, cell: str, epoch: int) -> float:
        if cell not in self.cells:
            raise KeyError(f"cell {cell!r} has no pre-allocated alpha")
        if any(c == cell and e == epoch for c, e, _ in self.spent):
            raise ValueError(f"alpha for {cell} epoch {epoch} already spent")
        share = self.cells[cell] * 6.0 / (math.pi ** 2 * (epoch + 1) ** 2)
        self.spent.append((cell, epoch, share))
        return share
