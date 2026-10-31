"""Numerical checks of the corrected theory of the FSE-2027-13 draft (docs/paper/THEORY.md).  No model calls.

python tools/theory_checks.py OUT_DIR [--reps 2000] [--cells 10] [--n 300] [--seed 7]

Each check is a falsifiable statement; the script records the numbers and whether the statement held.
  C1  per-cell e-process (gatekeeper_lite.eprocess.BettingEProcess) at the null boundary: false admission <= alpha
  C2  the draft's Theorem 4 budget (one alpha_s per SCOPE shared by L skills) can exceed alpha family-wise;
      the corrected per-CELL budget alpha/L keeps the family-wise rate <= alpha
  C3  bounded shift: |STR_Q - STR_P| <= 2 TV, and 2 TV is attained (the draft's bound TV is violated)
  C4  composition: STR(S1 o S2) <= 1 + min(STR(S1), STR(S2)) on random instances, and the bound is attained
  C5  pairing: variance ratio unpaired/paired = 1 + 2 sT^2/sS^2 (draft: 1 + sT^2/sS^2)
  C6  alpha ledger: sum_k 6/(pi^2 (k+1)^2) <= 1
  C8  re-admission after retirement: full alpha at every epoch vs the 6/(pi^2 (k+1)^2) ledger
  C7  Corollary 8 consistency: mean overlapping partners implied by 11.4% overlapping pairs of 94 skills
"""
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.eprocess import BettingEProcess  # noqa: E402


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


class FastBetting:
    """Same bets and wealth as gatekeeper_lite.eprocess.BettingEProcess (default arguments), with running sums instead of a
    full recomputation per step; tests/test_theory_checks.py checks the two agree on random sequences."""

    def __init__(self, theta, max_bet_fraction=0.5, prior_mean=0.5, prior_weight=1.0):
        self.theta, self.lam_cap = theta, max_bet_fraction / (1.0 + theta)
        self.pm, self.pw = prior_mean, prior_weight
        self.n, self.s, self.ss, self.log_wealth = 0, 0.0, 0.0, 0.0

    def _bet(self):
        n = self.n
        mean = (self.pm * self.pw + self.s) / (self.pw + n)
        if n >= 2:
            mu = self.s / n
            var = max(0.0, (self.ss - n * mu * mu) / (n - 1))
        else:
            var = 0.25
        edge = mean - self.theta
        lam = edge / (var + edge * edge + 1e-9) if edge > 0 else 0.0
        return max(0.0, min(lam, self.lam_cap))

    def update(self, z):
        y = -z
        lam = self._bet()
        self.log_wealth += math.log(max(1.0 + lam * (y - self.theta), 1e-300))
        self.n += 1
        self.s += y
        self.ss += y * y
        return math.exp(self.log_wealth)


def crosses(theta, threshold, n, rng):
    """One cell at the null boundary E[Y] = theta, Y in {-1, +1}; True if the e-process ever reaches threshold."""
    ep = FastBetting(theta)
    p_up = (1 + theta) / 2
    for _ in range(n):
        y = 1.0 if rng.random() < p_up else -1.0
        if ep.update(-y) >= threshold:                     # update takes Z = -Y
            return True
    return False


def check_alpha(reps, cells, n, seed, theta=0.1, alpha=0.1):
    rng = random.Random(seed)
    single = sum(crosses(theta, 1 / alpha, n, rng) for _ in range(reps))
    shared = split = 0
    for _ in range(reps):
        hits_shared = hits_split = False
        for _c in range(cells):
            ep_draws = [rng.random() for _i in range(n)]
            for thr_name, thr in (("shared", 1 / alpha), ("split", cells / alpha)):
                ep = FastBetting(theta)
                p_up = (1 + theta) / 2
                hit = False
                for u in ep_draws:
                    if ep.update(-(1.0 if u < p_up else -1.0)) >= thr:
                        hit = True
                        break
                if thr_name == "shared":
                    hits_shared |= hit
                else:
                    hits_split |= hit
        shared += hits_shared
        split += hits_split
    c1 = {"statement": "per-cell false admission <= alpha", "alpha": alpha, "theta": theta, "n": n, "reps": reps,
          "false_admissions": single, "rate": single / reps, "wilson95": wilson(single, reps)}
    c1["held"] = c1["rate"] <= alpha
    c2 = {"statement": "shared per-scope threshold can exceed alpha family-wise; per-cell alpha/L does not",
          "cells_in_scope": cells, "familywise_shared": shared / reps, "familywise_shared_wilson95": wilson(shared, reps),
          "familywise_split": split / reps, "familywise_split_wilson95": wilson(split, reps),
          "union_bound_shared": min(1.0, cells * c1["rate"])}
    c2["held"] = c2["familywise_split"] <= alpha
    c2["draft_budget_exceeded_alpha"] = c2["familywise_shared"] > alpha
    return c1, c2


def check_readmission(reps, epochs, n, seed, theta=0.1, alpha=0.1):
    """One cell at the null boundary, retired and re-tested `epochs` times on fresh tasks: full alpha at every epoch vs the
    ledger alpha * 6 / (pi^2 (k+1)^2)."""
    rng = random.Random(seed + 1)
    full = ledger = 0
    for _ in range(reps):
        hit_full = hit_ledger = False
        for k in range(epochs):
            draws = [rng.random() for _i in range(n)]
            for name, thr in (("full", 1 / alpha), ("ledger", 1 / (alpha * 6 / (math.pi ** 2 * (k + 1) ** 2)))):
                ep, p_up, hit = FastBetting(theta), (1 + theta) / 2, False
                for u in draws:
                    if ep.update(-(1.0 if u < p_up else -1.0)) >= thr:
                        hit = True
                        break
                if name == "full":
                    hit_full |= hit
                else:
                    hit_ledger |= hit
        full += hit_full
        ledger += hit_ledger
    res = {"statement": "re-admission: full alpha per epoch can exceed alpha; the ledger does not", "epochs": epochs, "reps": reps,
           "error_full_alpha_each_epoch": full / reps, "error_ledger": ledger / reps}
    res["held"] = res["error_ledger"] <= alpha
    res["no_ledger_exceeded_alpha"] = res["error_full_alpha_each_epoch"] > alpha
    return res


def check_tv():
    # two task types: a (loss with skill 1, without 0: Z=+1) and b (Z=-1)
    p = {"a": 0.1, "b": 0.9}
    q = {"a": 0.2, "b": 0.8}
    z = {"a": 1.0, "b": -1.0}
    tv = 0.5 * sum(abs(p[k] - q[k]) for k in p)
    gap = abs(sum(q[k] * z[k] for k in q) - sum(p[k] * z[k] for k in p))
    rng = random.Random(3)
    worst = 0.0
    for _ in range(20000):                                 # random distributions on 4 task types, random losses in [0,1]
        k = 4
        pa = [rng.random() for _ in range(k)]
        qa = [rng.random() for _ in range(k)]
        sp, sq = sum(pa), sum(qa)
        pa, qa = [x / sp for x in pa], [x / sq for x in qa]
        lp = [(rng.random(), rng.random()) for _ in range(k)]
        zz = [a - b for a, b in lp]
        t = 0.5 * sum(abs(a - b) for a, b in zip(pa, qa))
        g = abs(sum(a * b for a, b in zip(qa, zz)) - sum(a * b for a, b in zip(pa, zz)))
        if t > 0:
            worst = max(worst, g / t)
    return {"statement": "|STR_Q - STR_P| <= 2 TV, attained; draft bound (TV) violated",
            "example_tv": tv, "example_gap": gap, "ratio_gap_over_tv": gap / tv, "max_ratio_random": worst,
            "held": abs(gap - 2 * tv) < 1e-12 and worst <= 2 + 1e-9}


def check_composition():
    rng = random.Random(5)
    viol = 0
    for _ in range(20000):
        k = 3
        w = [rng.random() for _ in range(k)]
        s = sum(w)
        w = [x / s for x in w]
        base = [rng.random() for _ in range(k)]
        l1 = [rng.random() for _ in range(k)]
        l2 = [rng.random() for _ in range(k)]
        lc = [rng.random() for _ in range(k)]
        e = lambda v: sum(a * b for a, b in zip(w, v))   # noqa: E731
        a, b, c = e(l1) - e(base), e(l2) - e(base), e(lc) - e(base)
        if c > 1 + min(a, b) + 1e-12:
            viol += 1
    theta = 0.1
    construct = {"baseline": theta, "skill1": 0.0, "skill2": 0.0, "composition": 1.0}
    str1 = construct["skill1"] - construct["baseline"]
    strc = construct["composition"] - construct["baseline"]
    return {"statement": "STR(S1 o S2) <= 1 + min(STR1, STR2); attained by the construction",
            "random_instances": 20000, "violations": viol, "construction_theta": theta,
            "construction_str_single": str1, "construction_str_composite": strc, "bound": 1 + str1,
            "draft_claim_1_minus_eps_possible_for_eps_below_theta": False,
            "held": viol == 0 and abs(strc - (1 + str1)) < 1e-12}


def check_pairing(seed, ratio_t_s=2.1, n=200000):
    rng = random.Random(seed)
    s_s = 1.0
    s_t = math.sqrt(ratio_t_s) * s_s
    paired, wo, wi = [], [], []
    for _ in range(n):
        t = rng.gauss(0, s_t)
        sk = rng.gauss(0, s_s)
        paired.append((t + sk) - t)                        # same task, with and without the skill
        wo.append(rng.gauss(0, s_t))                       # unpaired: independent tasks for each arm
        wi.append(rng.gauss(0, s_t) + rng.gauss(0, s_s))
    def var(v):
        m = sum(v) / len(v)
        return sum((x - m) ** 2 for x in v) / (len(v) - 1)
    vp = var(paired)
    vu = var(wi) + var(wo)
    measured = vu / vp
    return {"statement": "unpaired/paired variance ratio = 1 + 2 sT^2/sS^2", "sT2_over_sS2": ratio_t_s,
            "measured_ratio": measured, "corrected_formula": 1 + 2 * ratio_t_s, "draft_formula": 1 + ratio_t_s,
            "held": abs(measured - (1 + 2 * ratio_t_s)) < 0.15}


def check_ledger():
    s = sum(6 / (math.pi ** 2 * (k + 1) ** 2) for k in range(1_000_000))
    return {"statement": "sum over epochs of 6/(pi^2 (k+1)^2) <= 1", "partial_sum_1e6": s, "held": s <= 1.0}


def check_corollary8(skills=94, overlap_share=0.114, draft_dbar=0.34):
    dbar = overlap_share * (skills - 1)
    return {"statement": "Corollary 8: d_bar implied by the overlap share", "skills": skills, "overlap_share": overlap_share,
            "implied_mean_partners": dbar, "overlapping_pairs": overlap_share * skills * (skills - 1) / 2,
            "draft_dbar": draft_dbar, "held": abs(dbar - draft_dbar) < 0.05,
            "note": "held=False means the draft's numbers are inconsistent (expected)"}


def main(argv):
    out = Path(argv[0])
    opt = lambda k, d: type(d)(argv[argv.index(k) + 1]) if k in argv else d   # noqa: E731
    reps, cells, n, seed = opt("--reps", 2000), opt("--cells", 10), opt("--n", 300), opt("--seed", 7)
    c1, c2 = check_alpha(reps, cells, n, seed)
    res = {"C1_per_cell_validity": c1, "C2_budget_per_cell_vs_per_scope": c2, "C3_bounded_shift": check_tv(),
           "C4_composition": check_composition(), "C5_pairing": check_pairing(seed), "C6_alpha_ledger": check_ledger(),
           "C7_corollary8_consistency": check_corollary8(),
           "C8_readmission_ledger": check_readmission(max(100, reps // 4), 10, n, seed)}
    out.mkdir(parents=True, exist_ok=True)
    (out / "THEORY_CHECKS.json").write_text(json.dumps(res, indent=1))
    lines = ["| Check | Statement | Held | Key numbers |", "|---|---|---|---|"]
    keys = {"C1_per_cell_validity": ("rate", "wilson95"), "C2_budget_per_cell_vs_per_scope": ("familywise_shared", "familywise_split"),
            "C3_bounded_shift": ("ratio_gap_over_tv", "max_ratio_random"), "C4_composition": ("violations", "construction_str_composite"),
            "C5_pairing": ("measured_ratio", "corrected_formula"), "C6_alpha_ledger": ("partial_sum_1e6",),
            "C7_corollary8_consistency": ("implied_mean_partners", "draft_dbar"),
            "C8_readmission_ledger": ("error_full_alpha_each_epoch", "error_ledger")}
    for k, v in res.items():
        nums = ", ".join("%s=%s" % (x, json.dumps(v[x]) if not isinstance(v[x], float) else round(v[x], 4)) for x in keys[k])
        lines.append("| %s | %s | %s | %s |" % (k, v["statement"], v["held"], nums))
    (out / "THEORY_CHECKS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
