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


if __name__ == "__main__" and not (len(sys.argv) > 1 and sys.argv[1] == "--family"):
    sys.exit(main())


# --------------------------------------------------------------------------- family mode
FAMILIES = {   # name -> list of (count, p_help, p_tie, p_hurt); nulls are cells that must NOT be admitted
    "toàn null ở biên (8 biên lợi ích + 8 biên tác hại)": [(8, 0.20, 0.80, 0.00), (8, 0.80, 0.15, 0.05)],
    "hỗn hợp giống Study D (4 tốt, 2 có hại, 4 biên lợi ích, 4 không đổi, 2 biên tác hại)":
        [(4, 1.00, 0.00, 0.00), (2, 0.00, 0.00, 1.00), (4, 0.20, 0.80, 0.00), (4, 0.00, 1.00, 0.00),
         (2, 0.80, 0.15, 0.05)],
}


def _cell_final(p_help, p_tie, p_hurt, theta, eta, k_cells, alpha, alpha_alarm, n_max, rng):
    ben, cert, alarm = BettingEProcess(theta), HarmCertEProcess(eta), HarmAlarmEProcess(eta)
    for _ in range(n_max):
        u = rng.random()
        z = -1.0 if u < p_help else (1.0 if u < p_help + p_hurt else 0.0)
        ben.update(z)
        cert.update(z > 0)
        alarm.update(z > 0)
        if alarm.value >= 1 / alpha_alarm:
            return 0.0                                  # REJECT_HARM: never admitted
        if min(ben.value, cert.value) >= k_cells / alpha:
            break                                       # early stop; e-Holm will accept it
    return min(ben.value, cert.value)


def family(argv=None) -> int:
    from gatekeeper_lite.eprocess import e_holm
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", type=float, default=0.2)
    ap.add_argument("--eta", type=float, default=0.05)
    ap.add_argument("--alpha", type=float, default=0.1)
    ap.add_argument("--alpha-alarm", type=float, default=0.05)
    ap.add_argument("--n-max", type=int, default=300)
    ap.add_argument("--sims", type=int, default=1000)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    rng = random.Random(20261021)
    lines = [f"# Mô phỏng cả họ ô với e-Holm (θ={a.theta}, η={a.eta}, α={a.alpha}, n_max={a.n_max}, {a.sims} lần)", "",
             "| Họ ô | K | FWER quan sát (khoảng tin cậy 95%) | Số ô null bị admit trung bình | Power trên ô tốt |",
             "|---|---|---|---|---|"]
    for name, spec in FAMILIES.items():
        cells = [(f"c{i}_{j}", ph, pt, pr) for i, (cnt, ph, pt, pr) in enumerate(spec) for j in range(cnt)]
        k = len(cells)
        is_null = {c: not (pr - ph < -a.theta and pr < a.eta) for c, ph, pt, pr in cells}
        any_false, false_total, good_hits, good_total = 0, 0, 0, 0
        for _ in range(a.sims):
            evals = {c: _cell_final(ph, pt, pr, a.theta, a.eta, k, a.alpha, a.alpha_alarm, a.n_max, rng)
                     for c, ph, pt, pr in cells}
            admitted = set(e_holm(evals, a.alpha))
            fa = sum(1 for c in admitted if is_null[c])
            any_false += fa > 0
            false_total += fa
            good = [c for c in evals if not is_null[c]]
            good_hits += sum(1 for c in good if c in admitted)
            good_total += len(good)
        p = any_false / a.sims
        half = 1.96 * (p * (1 - p) / a.sims) ** 0.5
        lines.append(f"| {name} | {k} | {p:.3f} ({max(0, p - half):.3f}–{p + half:.3f}) | "
                     f"{false_total / a.sims:.3f} | {(good_hits / good_total) if good_total else float('nan'):.3f} |")
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--family":
    sys.exit(family(sys.argv[2:]))
