"""Study H analysis (pre-registered): admission rates per harm rate rho, for every comparator,
from the recorded traces of all replications.
python tools/analyze_study_h.py study_h/config_study_h.json RESULT_H1_rare.json OUT.md"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext.mixture_cert import MixtureHarmCert  # noqa: E402
from gatekeeper_lite.eprocess import BettingEProcess, HarmAlarmEProcess, e_holm  # noqa: E402


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def mixture_rule(trace, cfg, k):
    ben, cert, al = BettingEProcess(cfg["theta"]), MixtureHarmCert(cfg["eta"]), HarmAlarmEProcess(cfg["eta"])
    for n, (z, reg) in enumerate(trace[:cfg["n_max"]], 1):
        ben.update(z); cert.update(bool(reg)); al.update(bool(reg))
        if al.value >= 1 / cfg["alpha_alarm"]:
            return 0.0, n
        if min(ben.value, cert.value) >= k / cfg["alpha"]:
            return min(ben.value, cert.value), n
    return min(ben.value, cert.value), min(len(trace), cfg["n_max"])


def main(config, result, out):
    cfg = json.loads(Path(config).read_text())
    r = json.loads(Path(result).read_text())
    rho = cfg["rho_by_cell"]
    cells = cfg["cells"]
    k = len(cells)
    census_ok = r["census"].get("status") == "VALID" and not r["census"].get("new_failures")
    adm = {c: {m: 0 for m in ("GK", "GK-mix", "B6S-5", "B6S-20", "B6S-50", "B8", "B6R")} for c in cells}
    draws = {c: {"GK": 0, "GK-mix": 0} for c in cells}
    R = len(r["replications"])
    for rep in r["replications"]:
        for c in cells:
            if len(rep["scopes"][c]["trace"]) < cfg["n_max"]:
                raise SystemExit(f"rep {rep['rep']} {c}: trace has {len(rep['scopes'][c]['trace'])} draws < n_max "
                                 "(run without b8_full); comparators after the stopping time would be wrong")
    for rep in r["replications"]:
        mix_e, mix_n = {}, {}
        for c in cells:
            sc = rep["scopes"][c]
            tr = sc["trace"]
            adm[c]["GK"] += sc["decision"] == "ADMIT"
            draws[c]["GK"] += sc["draws"]
            e, n = mixture_rule(tr, cfg, k)
            mix_e[c] = e if census_ok else 0.0
            mix_n[c] = n
            for kk in (5, 20, 50):
                adm[c][f"B6S-{kk}"] += census_ok and not any(reg for _, reg in tr[:kk])
            adm[c]["B8"] += census_ok and not any(reg for _, reg in tr[:cfg["n_max"]])
            adm[c]["B6R"] += bool(r["B6R_replay"].get("passed"))
        sel = set(e_holm(mix_e, cfg["alpha"]))
        for c in cells:
            adm[c]["GK-mix"] += c in sel
            draws[c]["GK-mix"] += mix_n[c]
    L = [f"# Study H — tác hại hiếm: tỉ lệ admit theo ρ ({R} lần lặp mỗi ô; η = {cfg['eta']}, θ = {cfg['theta']}, α = {cfg['alpha']})", "",
         "Ô được phép admit khi ρ < η (lợi ích luôn vượt biên: E[−Z] = 0,5 − ρ). Khoảng tin cậy Wilson 95%.", "",
         "| ρ | Được phép? | Gatekeeper (c = 0,9) | Gatekeeper (mixture, phụ) | B6-S(5) | B6-S(20) | B6-S(50) | B8 (300) | B6-R |",
         "|---|---|---|---|---|---|---|---|---|"]
    for c in cells:
        cell = []
        for m in ("GK", "GK-mix", "B6S-5", "B6S-20", "B6S-50", "B8", "B6R"):
            lo, hi = wilson(adm[c][m], R)
            cell.append(f"{adm[c][m]}/{R} [{lo:.2f}; {hi:.2f}]")
        L.append(f"| {rho[c]:.2%} | {'có' if rho[c] < cfg['eta'] else '**không**'} | " + " | ".join(cell) + " |")
    L += ["", "| ρ | Lần rút trung bình, Gatekeeper (c = 0,9) | Lần rút trung bình, mixture |", "|---|---|---|"]
    for c in cells:
        L.append(f"| {rho[c]:.2%} | {draws[c]['GK'] / R:.0f} | {draws[c]['GK-mix'] / R:.0f} |")
    L += ["", f"Census: {r['census'].get('status')}, {len(r['census'].get('new_failures', []))} regression mới "
              f"(bộ test của target không kiểm tra NullSentinel). B6-R: replay {'pass' if r['B6R_replay'].get('passed') else 'fail'}."]
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
