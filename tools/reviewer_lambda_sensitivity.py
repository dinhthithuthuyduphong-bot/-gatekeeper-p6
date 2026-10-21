"""Exploratory harm-certificate lambda sensitivity, using the frozen formula.

Analytic Bernoulli scenarios only. This is NOT an empirical Study D/E result.
Does not change frozen implementation, alpha, eta or admission decisions.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path


def row(eta: float, frac: float, harm: float, alpha: float) -> dict:
    if not 0 < eta < 1 or not 0 < frac < 1 or not 0 < alpha < 1:
        raise ValueError("eta, frac and alpha must be in (0, 1)")
    if not 0 <= harm <= 1:
        raise ValueError("harm probability must be in [0, 1]")
    lam = frac / (1 - eta)
    good = 1 + lam * eta
    bad = 1 - lam * (1 - eta)
    expected_log_growth = (1 - harm) * math.log(good) + harm * math.log(bad)
    no_harm_draws = math.ceil(math.log(1 / alpha) / math.log(good))
    return {"eta": eta, "frac": frac, "lambda": lam, "harm": harm,
            "expected_log_growth": expected_log_growth,
            "no_harm_draws_to_1_over_alpha": no_harm_draws}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eta", type=float, default=0.05)
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--out", type=Path, default=Path("pre_b9/LAMBDA_SENSITIVITY_EXPLORATORY.md"))
    args = ap.parse_args()
    lines = [
        "# Exploratory analytic sensitivity: harm-certificate λ",
        "",
        "**NOT prospective evidence.** Analytic Bernoulli scenarios, not observed target outcomes.",
        "The frozen implementation uses `lambda = frac/(1-eta)` with `frac=0.9`.",
        "Rows with alternative fractions are hypothetical; do not overwrite frozen settings.",
        "",
        "| frac | λ | true h | E[log wealth per draw] | draws to 1/α with 0 regressions |",
        "|---:|---:|---:|---:|---:|",
    ]
    for frac in (0.3, 0.5, 0.7, 0.9):
        for h in (0, 0.02, args.eta, 0.10):
            r = row(args.eta, frac, h, args.alpha)
            lines.append(
                f"| {frac:.1f} | {r['lambda']:.4f} | {h:.2f} | "
                f"{r['expected_log_growth']:+.5f} | "
                f"{r['no_harm_draws_to_1_over_alpha']} |"
            )
    lines.extend([
        "",
        "At the null boundary `h=eta`, expected *wealth multiplier* equals 1;",
        "expected log growth can be negative by Jensen's inequality.",
        "The no-regression crossing count is a conditional best-case path,",
        "NOT expected admission time or statistical power.",
        "Power and stopping-time distributions require separately labeled Monte Carlo",
        "simulations or actual prospective draws.",
        "",
    ])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
