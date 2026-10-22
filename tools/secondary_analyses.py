"""Secondary / exploratory analyses on the FROZEN per-draw traces of Studies D and E.

Nothing here changes a primary result: every analysis replays the recorded draws (the full
300-draw B8 trace of each cell) under an alternative rule and is labelled post hoc.
python tools/secondary_analyses.py study_d/results study_e/results --out OUT.md
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.eprocess import BettingEProcess, HarmAlarmEProcess, HarmCertEProcess, e_holm  # noqa: E402

THETA, ETA, ALPHA, ALARM, NMAX = 0.2, 0.05, 0.1, 20.0, 300


def load(dirs):
    cells = {}
    for d in dirs:
        for f in sorted(Path(d).glob("RESULT_*.json")):
            if f.stem.startswith("RESULT_B9"):
                continue
            r = json.loads(f.read_text())
            for s, sc in r.get("scopes", {}).items():
                cells[f"{r['target']}/{s}"] = {"trace": sc["trace"], "study": "D" if "study_d" in str(d) else "E",
                                               "census_bad": bool(r.get("census", {}).get("new_failures"))}
    return cells


def replay(trace, k_cells, cert_frac=0.9, theta=THETA, eta=ETA, futility=False):
    """Primary per-cell rule, with optional cert fraction, margins and futility stop."""
    ben, cert, al = BettingEProcess(theta), HarmCertEProcess(eta, frac=cert_frac), HarmAlarmEProcess(eta)
    cs = HedgedCS() if futility else None
    for n, (z, reg) in enumerate(trace[:NMAX], 1):
        ben.update(z); cert.update(bool(reg)); al.update(bool(reg))
        if al.value >= ALARM:
            return "REJECT_HARM", n, 0.0
        e = min(ben.value, cert.value)
        if e >= k_cells / ALPHA:
            return "ADMIT", n, e
        if cs is not None:
            cs.update((-z + 1) / 2)                 # benefit Y=-Z mapped to [0,1]
            lo, hi = cs.interval()
            if 2 * hi - 1 < theta:                  # upper bound on E[-Z] below the margin: benefit impossible
                return "FUTILE", n, e
    return "UNDECIDED", min(len(trace), NMAX), min(ben.value, cert.value)


class HedgedCS:
    """Hedged-capital confidence sequence for the mean of [0,1] observations
    (Waudby-Smith & Ramdas 2024, predictable plug-in bets), evaluated on a grid."""

    def __init__(self, alpha=0.05, grid=201):
        self.alpha, self.ms = alpha, [i / (grid - 1) for i in range(grid)]
        self.logp = [0.0] * grid
        self.logm = [0.0] * grid
        self.n, self.s, self.s2 = 0, 0.0, 0.0

    def update(self, x):
        n = self.n
        mu_hat = (0.5 + self.s) / (n + 1)
        var_hat = (0.25 + self.s2 - 2 * mu_hat * self.s + n * mu_hat ** 2) / (n + 1)
        lam = math.sqrt(2 * math.log(2 / self.alpha) / (max(var_hat, 1e-6) * (n + 1) * math.log(n + 2)))
        for i, m in enumerate(self.ms):
            lp = min(lam, 0.5 / max(m, 1e-9))
            lm = min(lam, 0.5 / max(1 - m, 1e-9))
            self.logp[i] += math.log(max(1 + lp * (x - m), 1e-300))
            self.logm[i] += math.log(max(1 - lm * (x - m), 1e-300))
        self.n += 1; self.s += x; self.s2 += x * x

    def interval(self):
        thr = math.log(1 / self.alpha)
        keep = [m for i, m in enumerate(self.ms)
                if math.log(0.5 * math.exp(self.logp[i]) + 0.5 * math.exp(self.logm[i])) < thr]
        return (min(keep), max(keep)) if keep else (float("nan"), float("nan"))


def cs_at(seq, n):
    c = HedgedCS()
    for x in seq[:n]:
        c.update(x)
    return c.interval()


def family_decisions(cells, k, **kw):
    out, evals = {}, {}
    for name, c in cells.items():
        d, n, e = replay(c["trace"], k, **kw)
        out[name] = (d, n)
        evals[name] = 0.0 if (d == "REJECT_HARM" or c["census_bad"]) else e
    adm = set(e_holm(evals, ALPHA))
    return {n: ("ADMIT" if n in adm else ("REJECT_HARM" if out[n][0] == "REJECT_HARM" else "Q"), out[n][1]) for n in out}


def sim_cert(frac, h, sims=2000, k=16, seed=7):
    rng = random.Random(seed)
    adm = 0
    for _ in range(sims):
        tr = []
        for _ in range(NMAX):
            u = rng.random()
            reg = u < h
            tr.append([-1.0 if not reg else 1.0, reg])
        adm += replay(tr, k, cert_frac=frac)[0] == "ADMIT"
    return adm / sims


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    cells = load(a.dirs)
    D = {k: v for k, v in cells.items() if v["study"] == "D"}
    E = {k: v for k, v in cells.items() if v["study"] == "E"}
    L = ["# Phân tích thứ cấp trên trace đã đóng băng (post hoc; không thay kết quả chính)", ""]

    L += ["## 1. Chiến lược betting và λ (lấy từ mã nguồn)", "",
          "- **Lợi ích** (`BettingEProcess`): Y = −Z, H0: E[Y] ≤ θ; vốn ∏(1 + λᵢ(Yᵢ − θ)); λᵢ = (m̂ − θ)/(σ̂² + (m̂ − θ)²), "
          "cắt về [0; 0,5/(1+θ)]; m̂ là trung bình co về prior 0,5 với trọng số 1; σ̂² là phương sai mẫu (0,25 khi n < 2). "
          "λᵢ chỉ dùng dữ liệu trước lần rút i (predictable). Đây là chiến lược kiểu aGRAPA của Waudby-Smith & Ramdas, "
          "không phải hỗn hợp (mixture). Lần rút hoà có Y = 0 < θ nên làm vốn giảm khi λ > 0; sau vài lần hoà, m̂ < θ và λ = 0.",
          "- **Chứng nhận ít tác hại** (`HarmCertEProcess`): λ **cố định** = 0,9/(1 − η); mỗi lần rút sạch nhân vốn với "
          "1 + 0,9η/(1 − η) = 1,0474; một regression nhân vốn với 0,1.",
          "- **Báo động** (`HarmAlarmEProcess`): cược Kelly cho h = 0,5: μ = min((0,5 − η)/(η(1 − η)), 0,95/η) = 9,47; "
          "mỗi regression nhân vốn khoảng 10, nên hai regression vượt 1/0,05 = 20.", ""]

    L += ["## 2. Độ nhạy theo λ của chứng nhận (K = 16, mô phỏng 2.000 lần)", "",
          "| Tỉ lệ λ/λmax | Lần rút để admit khi h = 0 | P(admit trong 300 lần rút), h = 0,02 | P(admit), h = η = 0,05 (phải thấp) |",
          "|---|---|---|---|"]
    for frac in (0.5, 0.7, 0.9, 0.99):
        n0 = math.ceil(math.log(160) / math.log(1 + frac * ETA / (1 - ETA)))
        L.append(f"| {frac} | {n0} | {sim_cert(frac, 0.02):.3f} | {sim_cert(frac, 0.05):.3f} |")
    L += ["", "λ lớn hơn admit nhanh hơn khi không có hại, nhưng mỗi regression làm vốn mất nhiều hơn, nên skill có hại hiếm "
          "khó được admit hơn. Giá trị 0,9 đã được đóng băng trước Study D/E.", ""]

    L += ["## 3. Họ e-Holm khi loại các ô ngoài scope", "",
          "Binding xảy ra trước mọi lần rút, nên loại ô ngoài scope khỏi họ không dùng tới kết quả. Study D: K = 16 → 12 (bỏ D4, A1); "
          "Study E không có ô ngoài scope.", "",
          "| Ô | Quyết định (K = 16) | Quyết định (K = 12) |", "|---|---|---|"]
    k16 = family_decisions(D, 16)
    k12 = family_decisions(D, 12)
    for n in sorted(D):
        if k16[n] != k12[n] or k16[n][0] == "ADMIT":
            L.append(f"| {n} | {k16[n][0]} ({k16[n][1]}) | {k12[n][0]} ({k12[n][1]}) |")
    L += ["", "Chỉ số lần rút để admit thay đổi; tập ô được admit không đổi.", ""]

    L += ["## 4. Baseline mạnh hơn: replay + fingerprint + k lần smoke test với đầu vào của scope", "",
          "B6-S(k): admit cả skill cho target khi replay pass, fingerprint khớp, census không có regression, **và** k lần rút đầu "
          "tiên ở mọi scope không có regression. Đây là kiểm thử khói không có thống kê, dùng đúng bộ sinh của scope.", "",
          "| k | Ô có hại bị admit (trên 3) | Ô có lợi được admit (trên 3) | Ô vô ích được admit (trên 16) | Tổng lần rút |",
          "|---|---|---|---|---|"]
    by_target = {}
    for n, c in cells.items():
        by_target.setdefault(n.split("/")[0], []).append((n, c))
    for k in (1, 3, 5, 10, 20):
        harm = ben = neu = draws = 0
        for t, lst in by_target.items():
            ok = all(not any(r for _, r in c["trace"][:k]) for _, c in lst) and not lst[0][1]["census_bad"]
            draws += k * len(lst)
            for n, c in lst:
                full = c["trace"][:NMAX]
                hurt = sum(1 for z, r in full if r)
                help_ = sum(1 for z, r in full if z < 0)
                if ok:
                    harm += hurt > 0
                    ben += help_ > 0 and hurt == 0
                    neu += help_ == 0 and hurt == 0
        L.append(f"| {k} | {harm} | {ben} | {neu} | {draws} |")
    L += ["", "Với k ≥ 1, B6-S chặn được cả ba ô có hại vì tác hại xảy ra ở 87–100% đầu vào bool. Một baseline mạnh hơn như vậy "
          "**an toàn ngang Gatekeeper trên dữ liệu này**; khác biệt còn lại là B6-S admit mọi thay đổi vô ích và không có bảo "
          "đảm sai số khi tác hại hiếm (ví dụ h = 2% cần khoảng 35 lần rút để có 50% xác suất thấy một regression).", ""]

    L += ["## 5. Confidence sequence 95% tại thời điểm dừng (μ = E[Z]; h = P(regression))", "",
          "| Ô | Lần rút | μ (CS 95%) | h (CS 95%) |", "|---|---|---|---|"]
    for n in sorted(cells):
        c = cells[n]
        d, stop, _ = replay(c["trace"], 16 if c["study"] == "D" else 10)
        if not any(z != 0 for z, _ in c["trace"]) and d != "ADMIT":
            continue
        ys = [(-z + 1) / 2 for z, _ in c["trace"]]
        hs = [1.0 if r else 0.0 for _, r in c["trace"]]
        lo, hi = cs_at(ys, stop)
        hl, hh = cs_at(hs, stop)
        L.append(f"| {n} | {stop} | [{-(2 * hi - 1):.2f}; {-(2 * lo - 1):.2f}] | [{hl:.3f}; {hh:.3f}] |")
    L += ["", "Ô có hại dừng sau 2 lần rút nên khoảng còn rất rộng; quyết định dựa trên e-process báo động, không trên khoảng này.", ""]

    L += ["## 6. Dừng sớm khi vô vọng (futility, khám phá)", "",
          "Quy tắc: dừng với QUARANTINE khi cận trên của CS 95% cho E[−Z] nhỏ hơn θ (lợi ích vượt biên là không còn khả dĩ). "
          "Quy tắc chỉ dẫn tới không-admit, nên không làm tăng sai số admit.", "",
          "| Họ | Lần rút (quy tắc chính) | Lần rút (có futility) | Quyết định thay đổi |", "|---|---|---|---|"]
    for lab, grp, k in (("Study D", D, 16), ("Study E", E, 10)):
        base = {n: replay(c["trace"], k) for n, c in grp.items()}
        fut = {n: replay(c["trace"], k, futility=True) for n, c in grp.items()}
        changed = [n for n in grp if (base[n][0] == "ADMIT") != (fut[n][0] == "ADMIT")]
        L.append(f"| {lab} | {sum(b[1] for b in base.values())} | {sum(f[1] for f in fut.values())} | {', '.join(changed) or 'không'} |")
    L += [""]

    L += ["## 7. Độ nhạy theo θ và η (trên trace thật)", "", "| θ | η | Ô được admit (Study D, K = 16) | Ô REJECT_HARM (Study E) |", "|---|---|---|---|"]
    for th in (0.05, 0.1, 0.2, 0.3):
        for et in (0.02, 0.05, 0.1):
            dd = family_decisions(D, 16, theta=th, eta=et)
            ee = family_decisions(E, 10, theta=th, eta=et)
            L.append(f"| {th} | {et} | {', '.join(sorted(n for n, v in dd.items() if v[0] == 'ADMIT')) or '—'} | "
                     f"{', '.join(sorted(n for n, v in ee.items() if v[0] == 'REJECT_HARM'))} |")
    L += [""]
    text = "\n".join(L) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
