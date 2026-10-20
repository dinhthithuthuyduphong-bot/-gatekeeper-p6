"""Simulate the FULL Study-D admission rule on i.i.d. draws from a scope generator.

Per cell: benefit e-process (H0: mu >= -theta), harm certificate (H0: h >= eta) and a
harm alarm (H0: h <= eta, fail fast).  Stop with REJECT_HARM when the alarm reaches
1/alpha_alarm; stop with ADMIT when min(benefit, certificate) >= K/alpha (the
e-Bonferroni level, which e-Holm always accepts); otherwise stop at n_max and report the
final min e-value (which e-Holm may still accept jointly with other cells).
Reports P(admit), P(reject_harm), P(undecided) and draw-count quantiles.
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite.eprocess import BettingEProcess, HarmAlarmEProcess, HarmCertEProcess  # noqa: E402

SCENARIOS = [  # name, P(help: Z=-1), P(tie), P(hurt: Z=+1 and regression)
    ("tốt, không hại", 1.00, 0.00, 0.00),
    ("tốt, nhiều ca hòa", 0.40, 0.60, 0.00),
    ("tốt, hại hiếm 2%", 0.80, 0.18, 0.02),
    ("biên tác hại h = η = 5%", 0.80, 0.15, 0.05),
    ("biên lợi ích μ = −θ", 0.20, 0.80, 0.00),
    ("không đổi", 0.00, 1.00, 0.00),
    ("hỗn hợp có hại 30%", 0.70, 0.00, 0.30),
    ("toàn hại (như lớp lazy)", 0.00, 0.00, 1.00),
]


def run_cell(p_help, p_tie, p_hurt, theta, eta, k_cells, alpha, alpha_alarm, n_max, rng):
    ben, cert, alarm = BettingEProcess(theta), HarmCertEProcess(eta), HarmAlarmEProcess(eta)
    for n in range(1, n_max + 1):
        u = rng.random()
        z = -1.0 if u < p_help else (1.0 if u < p_help + p_hurt else 0.0)
        regressed = z > 0
        ben.update(z)
        cert.update(regressed)
        alarm.update(regressed)
        if alarm.value >= 1 / alpha_alarm:
            return "REJECT_HARM", n
        if min(ben.value, cert.value) >= k_cells / alpha:
            return "ADMIT", n
    return "UNDECIDED", n_max


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", type=float, default=0.2)
    ap.add_argument("--eta", type=float, default=0.05)
    ap.add_argument("--cells", type=int, default=8)
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--alpha-alarm", type=float, default=0.05)
    ap.add_argument("--n-max", type=int, default=300)
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    rng = random.Random(20261020)
    lines = [f"# Mô phỏng quy tắc quyết định đầy đủ (θ={a.theta}, η={a.eta}, K={a.cells}, α={a.alpha}, "
             f"α_alarm={a.alpha_alarm}, n_max={a.n_max}, {a.sims} lần/kịch bản)", "",
             "| Kịch bản (giúp/hòa/hại) | μ | h | Nên admit? | P(ADMIT) | P(REJECT_HARM) | P(chưa quyết) | Số lần rút: trung vị / P90 |",
             "|---|---|---|---|---|---|---|---|"]
    for name, ph, pt, pr in SCENARIOS:
        res = [run_cell(ph, pt, pr, a.theta, a.eta, a.cells, a.alpha, a.alpha_alarm, a.n_max, rng)
               for _ in range(a.sims)]
        ns = sorted(n for _, n in res)
        mu, h = pr - ph, pr
        should = "có" if (mu < -a.theta and h < a.eta) else "không"
        lines.append(f"| {name} ({ph:.2f}/{pt:.2f}/{pr:.2f}) | {mu:+.2f} | {h:.2f} | {should} | "
                     f"{sum(d == 'ADMIT' for d, _ in res) / a.sims:.3f} | "
                     f"{sum(d == 'REJECT_HARM' for d, _ in res) / a.sims:.3f} | "
                     f"{sum(d == 'UNDECIDED' for d, _ in res) / a.sims:.3f} | "
                     f"{statistics.median(ns):.0f} / {ns[int(0.9 * len(ns)) - 1]} |")
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
