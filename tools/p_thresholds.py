"""Derive the Study P gates from the statistics of the registered hypotheses, not from judgment.

python tools/p_thresholds.py [--pi PLAUSIBLE_RATE_PER_ATTEMPT] [--models M] [--reps R] [--rho ICC]

Chain:  power of H1, H2, H3  ->  P3 (plausible patches) and P4 (patches in the band, discordant pairs)
        P3 / (models x reps x pi_low)  ->  P2 (usable instances)  ->  P1 (eligible)  ->  candidates to vet
Every rate entering the chain is the LOWER end of a 95% Wilson interval of what was measured.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_ext import gates as G  # noqa: E402

ALPHA_H, POWER = 0.05, 0.80


def sf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def exact_n(p0, p1, alpha=ALPHA_H, power=POWER, nmax=3000):
    """Smallest n whose one-sided exact binomial test of H0: p <= p0 has power >= power at p1 (and stays there)."""
    run = 0
    for n in range(5, nmax):
        k = next(k for k in range(n + 2) if sf(k, n, p0) <= alpha)
        ok = sf(k, n, p1) >= power
        run = run + 1 if ok else 0
        if run == 10:                                         # exact tests saw-tooth: require 10 consecutive n
            return n - 9
    return None


def wilson_low(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h


def discordance(n_draws=400, thetas=(0.01, 0.02, 0.03, 0.04), sims=4000, seed=1):
    """Among admissible-but-harmful patches (theta in the low band), how often do the fixed-sample test and the sequential
    certificate disagree, and which side admits?  Returns (P[disagree], q = P[FS admits | disagree])."""
    rng = random.Random(seed)
    fs_only = gk_only = 0
    for t in thetas:
        for _ in range(sims):
            flags = [rng.random() < t for _ in range(n_draws)]
            d = G.decisions(flags, True, 1)
            fs_only += d["fixed_sample"] and not d["gatekeeper"]
            gk_only += d["gatekeeper"] and not d["fixed_sample"]
    tot = sims * len(thetas)
    return (fs_only + gk_only) / tot, fs_only / max(fs_only + gk_only, 1)


RHO_FLOOR = 0.3          # the clustering used is never below this, even if the pilot estimates less


def from_pilot(path, model="vertex-gemini-flash"):
    """pi = Wilson LOWER bound of the plausible rate; rho = max(estimated ICC, RHO_FLOOR).  Both conservative."""
    import json
    m = json.loads(Path(path).read_text())["models"][model]
    icc = m.get("icc_of_plausibility")
    return m["plausible_rate_wilson_low"], max(icc if icc is not None else RHO_FLOOR, RHO_FLOOR)


def main(argv):
    opt = lambda k, d: float(argv[argv.index(k) + 1]) if k in argv else d
    pi, models, reps, rho = opt("--pi", None), int(opt("--models", 1)), int(opt("--reps", 3)), opt("--rho", RHO_FLOOR)
    if "--from-pilot" in argv:
        pi, rho = from_pilot(argv[argv.index("--from-pilot") + 1])
        print("from the pilot: pi (Wilson lower bound) = %.3f, rho = %.3f" % (pi, rho))
    m = models * reps                                           # patches per instance
    deff = 1 + (m - 1) * rho                                    # Kish design effect for clustered patches
    out = []
    # H1: share of plausible patches with theta-hat in the band; null 0.10, smallest effect of interest 0.20 (twice the null)
    n_h1 = exact_n(0.10, 0.20)
    p3 = math.ceil(n_h1 * deff)
    out.append(("H1", "exact one-sided binomial, H0 p <= 0.10, power 0.80 at p = 0.20, alpha 0.05", n_h1, "x design effect %.2f (m=%d patches per instance, ICC %.2f)" % (deff, m, rho), p3))
    # H2: smoke-20 admission among inadmissible patches; admission (1-theta)^20: 0.36 at 5%, 0.29 at 6%, 0.12 at 10%
    n_h2 = exact_n(0.15, 0.30)
    out.append(("H2", "exact one-sided binomial, H0 p <= 0.15, power 0.80 at p = 0.30 = (1-0.06)^20", n_h2, "x design effect", math.ceil(n_h2 * deff)))
    # H3: McNemar exact on discordant pairs; q = P(fixed-sample is the side that admits | disagreement), from simulation
    pdis, q = discordance()
    n_h3 = exact_n(0.5, max(min(q, 0.99), 0.51))
    out.append(("H3", "McNemar exact one-sided, H0 q <= 0.5, power 0.80 at q = %.2f (simulated at n=400, theta 1-4%%)" % q, n_h3, "discordant pairs", n_h3))
    print("%-3s | %-92s | %5s | %s" % ("", "test", "n", "-> gate"))
    for h, t, n, note, g in out:
        print("%-3s | %-92s | %5d | %s -> %d" % (h, t, n, note, g))
    print("simulated: a low-band patch makes the two statistical gates disagree with probability %.2f" % pdis)
    p4_band, p4_inad, p4_disc = math.ceil(n_h1 * deff * 0.10), math.ceil(n_h2 * deff), n_h3
    print("\nP3 (plausible patches) = %d   [H1 needs the largest sample]" % p3)
    print("P4 = at least %d patches with theta-hat > 5%% (H2), and at least %d discordant pairs (H3)" % (p4_inad, p4_disc))
    # funnel back to instances, with the LOWER Wilson bounds of what was measured
    e_low = wilson_low(107, 400)                               # Study N: 107 of 400 eligible
    u_low = wilson_low(58, 107)                                # feasibility step 2: 58 of 107 usable (conservative count)
    print("\nmeasured rates (lower 95%% Wilson): eligible %.3f (107/400), usable %.3f (58/107)" % (e_low, u_low))
    pis = [pi] if pi else [0.2, 0.3, 0.4, 0.5]
    print("%-8s | %-14s | %-12s | %-12s" % ("pi_low", "P2 usable", "P1 eligible", "candidates"))
    for p in pis:
        U = math.ceil(p3 / (m * p))
        E = math.ceil(U / u_low)
        C = math.ceil(E / e_low)
        print("%-8.2f | %-14d | %-12d | %-12d" % (p, U, E, C))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
