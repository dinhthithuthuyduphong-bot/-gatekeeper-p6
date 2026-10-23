"""Robustness of the per-cell admission rule to violations of independence (simulation only).

The rule assumes i.i.d. draws.  Two realistic violations are simulated at the null boundaries
(harm h = eta, benefit mu = -theta), where a false admission is most likely:
  * duplication: every distinct draw is repeated r times in a row (a generator that repeats inputs)
  * persistence: with probability p the outcome of the previous draw is repeated (a harness that
    carries state from one draw to the next), otherwise a fresh i.i.d. outcome is drawn
Reported: P(false admission within n_max) for the K=16 bar used in Study D.
python tools/dependence_sim.py [--sims 4000] [--out OUT.md]"""
import argparse
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.eprocess import BettingEProcess, HarmAlarmEProcess, HarmCertEProcess  # noqa: E402

THETA, ETA, ALPHA, NMAX = 0.2, 0.05, 0.1, 300


def outcome(rng, p_help, p_hurt):
    u = rng.random()
    return (-1.0, False) if u < p_help else ((1.0, True) if u < p_help + p_hurt else (0.0, False))


def stream(rng, p_help, p_hurt, dup, persist):
    prev = None
    while True:
        if prev is not None and persist and rng.random() < persist:
            o = prev
        else:
            o = outcome(rng, p_help, p_hurt)
        for _ in range(dup):
            yield o
        prev = o


def admits(rng, p_help, p_hurt, dup, persist, k):
    ben, cert, al = BettingEProcess(THETA), HarmCertEProcess(ETA), HarmAlarmEProcess(ETA)
    for n, (z, reg) in zip(range(NMAX), stream(rng, p_help, p_hurt, dup, persist)):
        ben.update(z); cert.update(reg); al.update(reg)
        if al.value >= 20:
            return False
        if min(ben.value, cert.value) >= k / ALPHA:
            return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sims", type=int, default=4000)
    ap.add_argument("--k", type=int, default=16)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    scen = {"harm boundary h = eta (0.80/0.15/0.05)": (0.80, 0.05),
            "benefit boundary mu = -theta (0.20/0.80/0)": (0.20, 0.0)}
    L = [f"# Độ bền khi vi phạm i.i.d. (mô phỏng; ngưỡng K/α với K = {a.k}; {a.sims} lần mỗi ô)", "",
         "| Kịch bản (biên null) | Vi phạm | P(admit sai) | KTC 95% |", "|---|---|---|---|"]
    rng = random.Random(20261023)
    for name, (ph, pr) in scen.items():
        for label, dup, pers in (("i.i.d. (tham chiếu)", 1, 0.0), ("lặp mỗi lần rút 2 lần", 2, 0.0),
                                 ("lặp mỗi lần rút 5 lần", 5, 0.0), ("giữ kết quả trước, p = 0,3", 1, 0.3),
                                 ("giữ kết quả trước, p = 0,6", 1, 0.6)):
            x = sum(admits(rng, ph, pr, dup, pers, a.k) for _ in range(a.sims))
            p = x / a.sims
            hw = 1.96 * math.sqrt(max(p * (1 - p), 1e-9) / a.sims)
            L.append(f"| {name} | {label} | {p:.4f} | [{max(0, p - hw):.4f}; {p + hw:.4f}] |")
    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
