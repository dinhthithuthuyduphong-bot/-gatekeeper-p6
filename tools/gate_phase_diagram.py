"""Gate phase diagram (0 cost): P(admit) of each acceptance gate as a function of the true harm rate h.

One patch, alpha = 0.1, eta = 0.05, benefit assumed satisfied (help rate 0.5), census clean.
Exact for smoke / zero-tolerance / fixed-sample gates; Monte Carlo for the sequential rules.
The sequential rules use the certificate and the Kelly alarm of gatekeeper_lite (alarm stake nu for h = 0.5).
Approximation: the benefit e-process is assumed to have crossed its threshold when the certificate does
(it needs about 50 draws at help rate 0.5 and does not decrease afterwards).

python tools/gate_phase_diagram.py [--out study_l/PHASE_DIAGRAM.md] [--sims 2000]
"""
import argparse
import math
from pathlib import Path

import numpy as np

ETA, ALPHA, ALARM = 0.05, 0.1, 20.0
THR = 1 / ALPHA
NU = min((0.5 - ETA) / (ETA * (1 - ETA)), 0.95 / ETA)
FIXED = [(1.0, 0.9)]
MIX = [(0.5, 0.99)] + [(0.5 / 8, c) for c in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)]
HS = [0.0, 0.001, 0.0025, 0.003, 0.01, 0.02, 0.03, 0.05, 0.10, 0.20]


def binom_cdf(x, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))


def fixed_sample_xstar(n):
    """Largest harm count a fixed-sample exact test (same eta, alpha) still accepts."""
    x = -1
    while x + 1 <= n and binom_cdf(x + 1, n, ETA) < ALPHA:
        x += 1
    return x


def sequential(h, n, stakes, sims, rng):
    R = rng.random((sims, n)) < h
    la = np.cumsum(np.where(R, math.log(1 + NU * (1 - ETA)), math.log(1 - NU * ETA)), axis=1)
    fired = la >= math.log(ALARM)
    alarm_t = np.where(fired.any(1), fired.argmax(1), n + 1)
    W = np.zeros((sims, n))
    for w, c in stakes:
        lam = c / (1 - ETA)
        W += w * np.exp(np.cumsum(np.where(R, math.log(1 - c), math.log(1 + lam * ETA)), axis=1))
    ok = W >= THR
    adm_t = np.where(ok.any(1), ok.argmax(1) + 1, n + 1)
    admit = (adm_t <= n) & (adm_t <= alarm_t)
    return float(admit.mean()), float(np.where(admit, adm_t, np.where(alarm_t <= n, alarm_t, n)).mean())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    ap.add_argument("--sims", type=int, default=2000)
    a = ap.parse_args(argv)
    rng = np.random.default_rng(20261026)
    x300, x1000 = fixed_sample_xstar(300), fixed_sample_xstar(1000)
    cols = ["smoke 20", "smoke 50", "zero-tol 300", "fixed 300", "fixed 1000", "GK c=0.9 @300", "mixture @300", "mixture @1000", "mixture @2000"]
    L = [f"# Gate phase diagram (alpha={ALPHA}, eta={ETA}, {a.sims} simulations per sequential cell)", "",
         "P(admit) for a patch that always helps (help rate 0.5). From h >= eta admitting is an error.", "",
         "| h | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    draws_note = {}
    for h in HS:
        row = [(1 - h) ** 20, (1 - h) ** 50, (1 - h) ** 300, binom_cdf(x300, 300, h), binom_cdf(x1000, 1000, h)]
        g3, d3 = sequential(h, 300, FIXED, a.sims, rng)
        m3, _ = sequential(h, 300, MIX, a.sims, rng)
        m10, _ = sequential(h, 1000, MIX, max(a.sims * 3 // 4, 500), rng)
        m20, _ = sequential(h, 2000, MIX, max(a.sims // 3, 300), rng)
        draws_note[h] = d3
        mark = " (error if admitted)" if h >= ETA else ""
        L.append(f"| {h:.2%}{mark} | " + " | ".join(f"{v:.2f}" for v in row + [g3, m3, m10, m20]) + " |")
    lo = 1 - 0.5 ** (1 / 300)       # zero-tolerance 300-draw gate keeps a patch less than half of the time
    hi = 1 - 0.1 ** (1 / 20)        # smoke-20 admits a harmful patch (h above eta) at most 10% of the time only above this h
    L += ["", f"Fixed-sample test accepts at most {x300} harms in 300 draws and {x1000} in 1000 (exact one-sided bound below eta).", "",
          f"**Band where simple gates are wrong:** a zero-tolerance 300-draw gate keeps less than half of acceptable patches once h > {lo:.2%}; "
          f"a 20-draw smoke test still admits more than 10% of inadmissible patches until h reaches {hi:.1%}. "
          f"Band used by gate G3: [0.25%, 10%].", "",
          f"Mean draws used by the fixed-stake sequential rule at 300 draws (one patch, threshold 1/alpha = 10; with a family of K = 16 cells the threshold is 160 and the h = 0 value becomes 110): " +
          ", ".join(f"h={h:.2%}: {d:.0f}" for h, d in draws_note.items() if h in (0.0, 0.01, 0.05, 0.10)) + "."]
    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
