"""Study H secondary analyses (post hoc, on the recorded traces):
  1. family-wise errors counted in the correct unit (one family = one replication of 6 cells)
  2. fixed-sample baseline with the SAME theta, eta and alpha (exact one-sided bounds, Bonferroni
     over the 6 cells): B-FS(n), n in {100, 200, 300}
  3. hybrid policy: smoke test on the first k draws, Gatekeeper rule only on the remaining draws
python tools/study_h_extra.py study_h/config_study_h.json RESULT_H1_rare.json OUT.md"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.eprocess import BettingEProcess, HarmAlarmEProcess, HarmCertEProcess, e_holm  # noqa: E402


def binom_upper(x, n, a):
    """Exact one-sided (1-a) Clopper-Pearson upper bound for a binomial proportion."""
    if x >= n:
        return 1.0
    lo, hi = x / n, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        tail = sum(math.comb(n, i) * m ** i * (1 - m) ** (n - i) for i in range(x + 1))
        lo, hi = (m, hi) if tail > a else (lo, m)
    return hi


def fixed_sample_admit(tr, n, cfg, k):
    """Admit iff (a) the exact upper bound on h is below eta and (b) the Hoeffding lower bound on
    E[-Z] (range 2) exceeds theta; each at alpha/(2k) (Bonferroni over the 2 nulls x k cells)."""
    a = cfg["alpha"] / (2 * k)
    seg = tr[:n]
    harms = sum(1 for _, r in seg if r)
    mean = sum(-z for z, _ in seg) / n
    lower = mean - 2 * math.sqrt(math.log(1 / a) / (2 * n))
    return binom_upper(harms, n, a) < cfg["eta"] and lower > cfg["theta"]


def gk_rule(tr, cfg, k, start=0):
    ben, cert, al = BettingEProcess(cfg["theta"]), HarmCertEProcess(cfg["eta"]), HarmAlarmEProcess(cfg["eta"])
    for n, (z, reg) in enumerate(tr[start:cfg["n_max"]], 1):
        ben.update(z); cert.update(bool(reg)); al.update(bool(reg))
        if al.value >= 1 / cfg["alpha_alarm"]:
            return 0.0, n
        e = min(ben.value, cert.value)
        if e >= k / cfg["alpha"]:
            return e, n
    return min(ben.value, cert.value), cfg["n_max"] - start


def main(config, result, out):
    cfg = json.loads(Path(config).read_text())
    r = json.loads(Path(result).read_text())
    cells, rho, k = cfg["cells"], cfg["rho_by_cell"], len(cfg["cells"])
    null = [c for c in cells if rho[c] >= cfg["eta"]]
    R = len(r["replications"])
    fam_err = {"Gatekeeper": 0, "B6-S(5)": 0, "B6-S(20)": 0, "B6-S(50)": 0, "B-FS(100)": 0, "B-FS(200)": 0,
               "B-FS(300)": 0, "Lai: smoke 5 + GK": 0}
    adm = {m: {c: 0 for c in cells} for m in fam_err}
    cost = {m: 0 for m in fam_err}
    for rep in r["replications"]:
        sc = {c: rep["scopes"][c]["trace"] for c in cells}
        dec = {}
        dec["Gatekeeper"] = {c: rep["scopes"][c]["decision"] == "ADMIT" for c in cells}
        cost["Gatekeeper"] += sum(rep["scopes"][c]["draws"] for c in cells)
        for kk in (5, 20, 50):
            dec[f"B6-S({kk})"] = {c: not any(x for _, x in sc[c][:kk]) for c in cells}
            cost[f"B6-S({kk})"] += kk * k
        for n in (100, 200, 300):
            dec[f"B-FS({n})"] = {c: fixed_sample_admit(sc[c], n, cfg, k) for c in cells}
            cost[f"B-FS({n})"] += n * k
        ev, hyb_cost = {}, 0
        for c in cells:
            if any(x for _, x in sc[c][:5]):
                ev[c] = 0.0
                hyb_cost += next(i for i, (_, x) in enumerate(sc[c][:5], 1) if x)
            else:
                e, n_used = gk_rule(sc[c], cfg, k, start=5)
                ev[c] = e
                hyb_cost += 5 + n_used
        sel = set(e_holm(ev, cfg["alpha"]))
        dec["Lai: smoke 5 + GK"] = {c: c in sel for c in cells}
        cost["Lai: smoke 5 + GK"] += hyb_cost
        for m in fam_err:
            fam_err[m] += any(dec[m][c] for c in null)
            for c in cells:
                adm[m][c] += dec[m][c]
    L = [f"# Study H — phân tích thứ cấp (post hoc, trên trace đã ghi; {R} họ kiểm định)", "",
         f"**Đơn vị FWER:** một họ = một lần lặp gồm {k} ô. Ô null (không được phép admit): {', '.join(null)}.", "",
         "| Cách tiếp cận | Họ có admit sai (trên " + str(R) + ") | " + " | ".join(f"ρ = {rho[c]:.0%}" for c in cells) + " | Lần rút trung bình mỗi họ |",
         "|---|---|" + "---|" * len(cells) + "---|"]
    for m in fam_err:
        L.append(f"| {m} | {fam_err[m]} | " + " | ".join(f"{adm[m][c]}" for c in cells) + f" | {cost[m] / R:.0f} |")
    L += ["", "B-FS(n): cỡ mẫu cố định n, cùng θ, η và α (cận chính xác Clopper–Pearson cho h, cận Hoeffding cho lợi ích, "
              "Bonferroni trên 2 giả thuyết × 6 ô). Lai: smoke test 5 lần rút; nếu sạch thì chạy quy tắc Gatekeeper trên các lần rút "
              "**tiếp theo** (không dùng lại 5 lần rút smoke), e-Holm trên các ô."]
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main(*sys.argv[1:4])
