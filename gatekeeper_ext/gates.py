"""Acceptance gates on the HARM side, applied to per-draw regression flags (Study N protocol sections 2 and 6).

A draw is a mutant of an upstream test (see gatekeeper_ext/testmut.py).  For a patch, per draw:
    l0 = [original differs from the upstream fix],  l1 = [patch differs from the upstream fix],
    harm R = (not l0) and l1,   help = l0 and (not l1).
Benefit is NOT tested here: a patch is "plausible" when it passes the instance's fail-to-pass and pass-to-pass tests
(the census), and every gate below is applied to plausible patches only.  Standard library only.

Gates (same theta-free harm threshold eta and level alpha for all):
    census_only     admit every plausible patch
    zero_tolerance  plausible and no harm draw (B8)
    b8_plus         zero_tolerance and at least one help draw (B8+)
    smoke20         plausible and no harm in the first 20 draws
    fixed_sample    plausible and an exact one-sided test rejects harm rate >= eta at level alpha
    gatekeeper      plausible and the fixed-stake harm certificate (c = 0.9) reaches K/alpha before the Kelly alarm
Gatekeeper-mixture needs about 1,000 draws and is not applicable at the draw counts of this harness.
"""
import math

ETA, ALPHA, C_STAKE, ALARM = 0.05, 0.1, 0.9, 20.0
BAND_LOW_FLOOR, BAND_HIGH = 0.01, 0.10


def binom_cdf(x, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))


def fixed_sample_xstar(n, eta=ETA, alpha=ALPHA):
    """Largest harm count the exact test still accepts (-1 if even zero harms cannot be certified at this n)."""
    x = -1
    while x + 1 <= n and binom_cdf(x + 1, n, eta) < alpha:
        x += 1
    return x


def gatekeeper_path(flags, k_family=1, eta=ETA, alpha=ALPHA, c=C_STAKE):
    """Sequential harm certificate with a Kelly alarm.  Returns (admit, certified_at, alarm_at); positions are 1-based."""
    lam = c / (1 - eta)
    log_clean, log_harm = math.log(1 + lam * eta), math.log(1 - c)
    nu = min((0.5 - eta) / (eta * (1 - eta)), 0.95 / eta)
    a_clean, a_harm = math.log(1 - nu * eta), math.log(1 + nu * (1 - eta))
    thr, alarm_thr = math.log(k_family / alpha), math.log(ALARM)
    w = wa = 0.0
    cert_at = alarm_at = None
    for i, r in enumerate(flags, 1):
        w += log_harm if r else log_clean
        wa += a_harm if r else a_clean
        if alarm_at is None and wa >= alarm_thr:
            alarm_at = i
        if cert_at is None and w >= thr:
            cert_at = i
        if cert_at is not None or alarm_at is not None:
            break
    return (cert_at is not None and (alarm_at is None or cert_at <= alarm_at)), cert_at, alarm_at


def decisions(flags, plausible, helps, k_family=1):
    """flags: harm booleans in draw order; helps: number of help draws."""
    n, hurt = len(flags), sum(flags)
    adm, cert_at, alarm_at = gatekeeper_path(flags, k_family)
    return {"census_only": bool(plausible),
            "zero_tolerance": bool(plausible and hurt == 0),
            "b8_plus": bool(plausible and hurt == 0 and helps >= 1),
            "smoke20": bool(plausible and not any(flags[:20])),
            "fixed_sample": bool(plausible and n > 0 and hurt <= fixed_sample_xstar(n)),
            "gatekeeper": bool(plausible and adm),
            "_detail": {"n": n, "hurt": hurt, "helps": helps, "xstar": fixed_sample_xstar(n), "certified_at": cert_at, "alarm_at": alarm_at}}


def h_hat(flags):
    return (sum(flags) / float(len(flags))) if flags else None


def band(flags):
    """In the region where simple gates misjudge: harm rate between max(1%, 2/n) and 10%."""
    n = len(flags)
    h = h_hat(flags)
    return bool(n and h is not None and max(BAND_LOW_FLOOR, 2.0 / n) <= h <= BAND_HIGH)


def acceptable(flags):
    """Harm rate below eta (the registered acceptability boundary)."""
    h = h_hat(flags)
    return bool(h is not None and h < ETA)
