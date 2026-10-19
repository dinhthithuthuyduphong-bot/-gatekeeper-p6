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


class DiscordantSignEProcess:
    """Sequential sign test on discordant pairs (anytime-valid McNemar).

    Ties (Z == 0) leave wealth unchanged, so tasks that cannot discriminate cost no
    evidence.  For a discordant pair let X = 1 if the skill helped (Z < 0), else 0.
      admission:  H0: q = P(X=1 | Z!=0) <= q0, wealth prod(1 + lam (X - q0)),
                  lam = GROW/Kelly bet for alternative q1:  (q1-q0) / (q0 (1-q0)),
                  capped below 1/q0 so every factor stays positive;
      harm:       H0: h = P(X=0 | Z!=0) <= eps, wealth prod(1 + mu ((1-X) - eps)),
                  mu = Kelly bet for alternative h1, capped below 1/eps.
    Both are non-negative supermartingales under their nulls (fixed predictable bets),
    so Ville's inequality bounds each false alarm by alpha.  Assumes discordant pairs
    are exchangeable draws from the scope (conditional on discordance).
    """

    def __init__(self, q0: float = 0.6, q1: float = 0.9, eps: float = 0.05, h1: float = 0.5):
        if not (0 < q0 < q1 < 1 and 0 < eps < h1 < 1):
            raise ValueError("need 0 < q0 < q1 < 1 and 0 < eps < h1 < 1")
        self.q0, self.eps = q0, eps
        self.lam = min((q1 - q0) / (q0 * (1 - q0)), 0.95 / q0)
        self.mu = min((h1 - eps) / (eps * (1 - eps)), 0.95 / eps)
        self.log_admit = 0.0
        self.log_harm = 0.0
        self.n = self.helped = self.hurt = 0
        self.history: List[float] = [1.0]

    def update(self, z: float) -> float:
        if not -1.0 <= z <= 1.0:
            raise ValueError("paired difference must lie in [-1, 1]")
        self.n += 1
        if z != 0:
            x = 1.0 if z < 0 else 0.0
            self.helped += int(x)
            self.hurt += int(1 - x)
            self.log_admit += math.log(1.0 + self.lam * (x - self.q0))
            self.log_harm += math.log(1.0 + self.mu * ((1.0 - x) - self.eps))
        self.history.append(self.value)
        return self.value

    @property
    def value(self) -> float:
        return math.exp(self.log_admit)

    @property
    def harm_value(self) -> float:
        return math.exp(self.log_harm)


def make_eprocess(cfg: dict):
    mode = cfg.get("evidence", "mean_betting")
    if mode == "discordant_sign":
        p = cfg.get("discordant", {})
        return DiscordantSignEProcess(p.get("q0", 0.6), p.get("q1", 0.9),
                                      p.get("harm_eps", 0.05), p.get("harm_alt", 0.5))
    return BettingEProcess(theta=cfg["theta"])


def e_bh(e_values: Dict[str, float], fdr: float) -> List[str]:
    """e-BH (Wang & Ramdas 2022): reject the R cells with the largest e-values, where
    R = max{k : e_(k) >= K / (fdr * k)}.  Controls FDR at `fdr` under any dependence.
    Each e-value must be the e-process value at a stopping time fixed by the protocol."""
    k_total = len(e_values)
    ranked = sorted(e_values.items(), key=lambda kv: kv[1], reverse=True)
    r = 0
    for k, (_, e) in enumerate(ranked, start=1):
        if e >= k_total / (fdr * k):
            r = k
    return [cell for cell, _ in ranked[:r]]
