"""Results report: statistics first, verdict last.  Generated from the result files; no number is typed by hand.
python tools/results_report.py [OUT.md]     (default docs/paper/RESULTS_REPORT.md)"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "research_closure/results"


def wilson(k, n, z=1.96):
    if not n:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))


def pct(x):
    return "%.1f%%" % (100 * x)


def ci(k, n):
    lo, hi = wilson(k, n)
    return "%s [%s, %s]" % (pct(k / n) if n else "–", pct(lo), pct(hi))


def table(title, harmful_total, safe_total, rows, names, draws, verdict, note=""):
    out = ["### " + title, "",
           "| Luật | Có hại admit | Tỉ lệ có hại admit [Wilson 95%] | An toàn giữ | Tỉ lệ giữ [Wilson 95%] | Draw/ô | **Đánh giá** |",
           "|---|---|---|---|---|---|---|"]
    for k in rows:
        s = names[k]
        h, a = rows[k]["harmful_admitted"], rows[k]["safe_admitted"]
        out.append("| %s | %d/%d | %s | %d/%d | %s | %s | %s |" % (s, h, harmful_total, ci(h, harmful_total), a, safe_total,
                                                               ci(a, safe_total), draws.get(k, "0"), verdict.get(k, "")))
    if note:
        out += ["", note]
    return out + [""]


def verdict_vs(g, x, gname="G"):
    """Win/lose of Gatekeeper against rule x on (harmful admitted, safe kept)."""
    if x is g:
        return "—"
    hg, sg, hx, sx = g["harmful_admitted"], g["safe_admitted"], x["harmful_admitted"], x["safe_admitted"]
    if hg < hx and sg >= sx:
        return "G **thắng** cả hai chiều"
    if hg <= hx and sg > sx:
        return "G **thắng** (giữ nhiều hơn, hại không hơn)" if hg == hx else "G **thắng** cả hai chiều"
    if hg < hx and sg < sx:
        return "G an toàn hơn, giữ ít hơn (**đánh đổi**)"
    if hg == hx and sg == sx:
        return "hoà"
    if hg >= hx and sg <= sx:
        return "G **thua**"
    return "đánh đổi"

NAMES = {"U": "Áp dụng tất cả (U)", "RS": "Nhãn safe của Ruff (RS)", "B6R": "Replay ví dụ tài liệu (B6-R)",
         "B6S": "Replay trên mọi gói nguồn (B6-strong)", "B6M": "B6-majority", "LJ": "LLM judge (LJ)", "S20": "Smoke 20 draw",
         "FS": "Fixed-sample", "B8": "Always-retest B8", "TS": "Test suite của gói (TS, CI xanh)", "G": "**Gatekeeper (G), e-Holm**",
         "G_FDR": "Gatekeeper, e-BH (G-FDR)"}


def market(d, title, all_cells=False):
    p = d / "STUDY_T_RESULT.json"
    if not p.exists():
        return []
    t = json.loads(p.read_text())
    names = dict(NAMES, FS="Fixed-sample (%d draw)" % t["fs_draws"])
    draws = {"S20": "20", "FS": str(t["fs_draws"]), "B8": "%.1f" % t["mean_draws"]["B8"], "G": "%.1f" % t["mean_draws"]["G"],
             "G_FDR": "%.1f" % t["mean_draws"]["G"]}
    out = []
    errs = t.get("package_errors", [])
    note = "Tiêu chí đăng ký trước: " + ", ".join("%s %s" % (w, "THẮNG" if t[w]["won"] else "THUA") for w in ("W1", "W2", "W3", "W4") if w in t) + "."
    note += " LLM judge chấm %d ô." % t.get("lj_judged_cells", 0)
    if errs:
        note += " **Gói chưa có kết quả (%d):** %s." % (len(errs), ", ".join(e["project"] for e in errs))
    for key, sub in (("ruff_cells", "ô rule Ruff"),) + ((("all_cells", "mọi ô, gồm R2"),) if all_cells else ()):
        rc = t[key]
        order = [k for k in ["U", "RS", "B6R", "B6S", "B6M", "LJ", "S20", "FS", "B8", "G", "G_FDR"] if k in rc and rc[k]["cells"]]
        out += table("%s — %s, %d ô dùng được" % (title, sub, rc["G"]["cells"]), rc["G"]["harmful_total"], rc["G"]["safe_total"],
                     {k: rc[k] for k in order}, names, draws, {k: verdict_vs(rc["G"], rc[k]) for k in order}, note)
    return out


def test_suite(d, label):
    p = d / "TS_RESULT.json"
    if not p.exists():
        return []
    r = json.loads(p.read_text())
    sc = r["scores"]
    order = [k for k in ["U", "RS", "B6S", "LJ", "S20", "B8", "TS", "G", "G_FDR"] if k in sc and sc[k]["harmful_total"] + sc[k]["safe_total"]]
    rows = {k: sc[k] for k in order}
    out = ["### %s-A4: test suite của chính gói (TS) — %d ô chạy được trên %d/%d gói có test ổn định" % (
        label, r["cells_run"], r["packages"]["applicable"], r["packages"]["packages"]), "",
        "| Luật | Có hại admit | Tỉ lệ có hại admit [Wilson 95%] | An toàn giữ | Tỉ lệ giữ [Wilson 95%] | **Đánh giá** |",
        "|---|---|---|---|---|---|"]
    for k in order:
        x = rows[k]
        out.append("| %s | %d/%d | %s | %d/%d | %s | %s |" % (NAMES.get(k, k), x["harmful_admitted"], x["harmful_total"],
                   ci(x["harmful_admitted"], x["harmful_total"]), x["safe_admitted"], x["safe_total"],
                   ci(x["safe_admitted"], x["safe_total"]), verdict_vs(sc["G"], x)))
    n, k = r["g_admitted"], r["g_admitted_ts_confirmed_reject"]
    out += ["", "| Đại lượng | Giá trị |", "|---|---|",
            "| Ô có hại (oracle của ta) mà test suite bắt được | %d/%d (%s) |" % (r["harmful_rejected_by_ts"], r["harmful"], ci(r["harmful_rejected_by_ts"], r["harmful"])),
            "| Ô G admit mà test suite báo lỗi, xác nhận lại | %d/%d (%s) |" % (k, n, ci(k, n)),
            "| …báo lỗi nhưng không lặp lại (flaky) | %d |" % r["g_admitted_ts_unconfirmed_reject"],
            "| Giây mỗi ô, TS | %s |" % r["ts_seconds_per_cell"],
            "| Ô chưa chạy (hết ngân sách) | %d |" % r["not_run_budget"],
            "", "Tiêu chí: TS-W1 **%s**, TS-W2 (oracle độc lập, cận trên ≤ 5%%) **%s**." % (
                "THẮNG" if r["TS_W1"] else "THUA", "THẮNG" if r["TS_W2"] else "THUA"), ""]
    return out


def b9_tiers():
    out = []
    tiers = [(t, R / ("study_t/B9_RESULT%s.json" % ("_" + t if t else ""))) for t in ("", "medium", "strong")]
    tiers = [(t, json.loads(p.read_text())) for t, p in tiers if p.exists()]
    if not tiers:
        return out
    label = {"": "rẻ", "medium": "vừa", "strong": "mạnh"}
    out += ["### Study T-A6/T-A7: B9 (model tự áp dụng thay đổi) theo 3 mức model, so với Gatekeeper", "",
            "| Mức | Model | Ô đánh giá được | Có hại được áp dụng [Wilson 95%] | …trên ô vốn an toàn | Không parse được | USD/ô | Giây/ô | G có hại | G USD/ô | B9 đắt hơn G | **Đánh giá** |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t, b in tiers:
        c = b["cost_per_cell"]
        ratio = c["b9_usd"] / c["g_usd_runner"] if c["g_usd_runner"] else float("nan")
        out.append("| %s | %s | %d | %d (%s) | %d | %d | %.4f | %.1f | %d | %.5f | ×%.0f | %s |" % (
            label[t], b.get("model", "?"), b["evaluable_b9"], b["b9_harmful_applied"], ci(b["b9_harmful_applied"], b["evaluable_b9"]),
            b["b9_harmful_among_truth_safe"], b["b9_unparsable_functions"], c["b9_usd"], c["b9_seconds"], b["g_harmful_admitted"],
            c["g_usd_runner"], ratio, "G **thắng**" if b["B9_W"] else "G thua"))
    return out + [""]


def retirement():
    p = R / "study_v/V_RESULT.json"
    if not p.exists():
        return []
    v = json.loads(p.read_text())
    f1, b8 = v["f1_epoch1"], v["b8_v"]
    return ["### Study V: retirement khi môi trường thật đổi (Python %s → %s)" % ("3.12", ", ".join(v["python_v"])), "",
            "| Đại lượng | Giá trị |", "|---|---|",
            "| Ô dùng được ở cả hai môi trường | %d (T %d, V %d) |" % (v["usable_both"], v["usable_t"], v["usable_v"]),
            "| Gói có fingerprint đổi | %d/%d |" % (v["packages_fingerprint_changed"], v["packages_with_fingerprint"]),
            "| Ô đổi từ an toàn sang có hại | %d |" % len(v["flips_safe_to_harmful"]),
            "| Ô đổi từ có hại sang an toàn | %d |" % len(v["flips_harmful_to_safe"]),
            "| Ô G admit ở T (phần epoch 0) | %d (cả α: %d) |" % (v["t_admitted_epoch0"], v["t_admitted_full_alpha"]),
            "| F0 (không retire): ô có hại ở 3.13 vẫn giữ | %d |" % v["f0_harmful_kept"],
            "| F1 (retire theo fingerprint): ô bị retire | %d |" % v["f1_retired"],
            "| F1 epoch 1: có hại admit | %d/%d (%s) |" % (f1["harmful_admitted"], f1["harmful_total"], ci(f1["harmful_admitted"], f1["harmful_total"])),
            "| F1 epoch 1: an toàn giữ | %d/%d (%s) |" % (f1["safe_admitted"], f1["safe_total"], ci(f1["safe_admitted"], f1["safe_total"])),
            "| Draw/ô chứng nhận lại: G / B8 | %s / %s |" % (f1["mean_draws"], b8["mean_draws"]),
            "| B8 ở 3.13: có hại admit / an toàn giữ | %d / %d |" % (b8["harmful_admitted"], b8["safe_admitted"]),
            "", "Tiêu chí: V-W1 **%s**, V-W2 **%s**." % ("THẮNG" if v["V_W1"] else "THUA", "THẮNG" if v["V_W2"] else "THUA"), ""]


def main(argv):
    out_p = Path(argv[0]) if argv else ROOT / "docs/paper/RESULTS_REPORT.md"
    L = ["# Báo cáo kết quả: số liệu thống kê trước, đánh giá sau", "",
         "*Sinh tự động bởi `tools/results_report.py` từ tệp kết quả trong `research_closure/results/`. Không có con số nào gõ tay. "
         "Khoảng tin cậy là Wilson 95%. Cột cuối là đánh giá của Gatekeeper (G) so với từng luật.*", ""]
    L += market(R / "study_t", "Study T: kỹ năng thị trường (rule Ruff) trên 60 gói PyPI")
    L += market(R / "study_t2", "Study T2: nhân rộng trên 140 gói PyPI hạng 61–200 (G-FDR đăng ký trước)", all_cells=True)
    for d, label in ((R / "study_t", "Study T"), (R / "study_t2", "Study T2")):
        L += test_suite(d, label)
    L += b9_tiers()
    L += retirement()
    up = R / "study_u/STUDY_U_RESULT.json"
    if up.exists():
        u = json.loads(up.read_text())
        for hk, label in (("contract", "contract regression (chính)"), ("naive", "khác biệt naive (phụ)")):
            v = u[hk]
            un = {"U": "Test pass (U)", "S20": "Smoke 20 draw", "FS": "Fixed-sample (%d draw)" % v["fs_draws"], "B8": "Always-retest B8",
                  "G": "**Gatekeeper (G), e-Holm**", "G_FDR": "Gatekeeper, e-BH (post hoc, U-A1)"}
            ud = {"S20": "20", "FS": str(v["fs_draws"]), "B8": "%.1f" % v["mean_draws"]["B8"], "G": "%.1f" % v["mean_draws"]["G"],
                  "G_FDR": "%.1f" % v["mean_draws"]["G"]}
            ks = [k for k in un if k in v["scores"]]
            L += table("Study U: tác hại hiếm, %d patch agent đã resolved trên SWE-bench — tác hại = %s" % (v["patches"], label),
                       v["harmful"], v["safe"], {k: v["scores"][k] for k in ks}, un, ud,
                       {k: verdict_vs(v["scores"]["G"], v["scores"][k]) for k in ks},
                       "Dải tác hại 5–20%%: %d patch; admit: %s. Tiêu chí: U1 %s, U2 %s, U3 %s." % (
                           v["band_5_20"]["patches"], ", ".join("%s %d" % (k, n) for k, n in v["band_5_20"]["admitted"].items()),
                           *("THẮNG" if v[c] else "THUA" for c in ("U1", "U2", "U3"))))
    out_p.write_text("\n".join(L) + "\n")
    print(out_p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
