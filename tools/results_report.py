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


def main(argv):
    out_p = Path(argv[0]) if argv else ROOT / "docs/paper/RESULTS_REPORT.md"
    L = ["# Báo cáo kết quả: số liệu thống kê trước, đánh giá sau", "",
         "*Sinh tự động bởi `tools/results_report.py` từ tệp kết quả trong `research_closure/results/`. Không có con số nào gõ tay. "
         "Khoảng tin cậy là Wilson 95%. Cột cuối là đánh giá của Gatekeeper (G) so với từng luật.*", ""]
    t = json.loads((R / "study_t/STUDY_T_RESULT.json").read_text())
    rc = t["ruff_cells"]
    names = {"U": "Áp dụng tất cả (U)", "RS": "Nhãn safe của Ruff (RS)", "B6R": "Replay ví dụ tài liệu (B6-R)",
             "B6S": "Replay trên mọi gói nguồn (B6-strong)", "B6M": "B6-majority", "LJ": "LLM judge (LJ)", "S20": "Smoke 20 draw",
             "FS": "Fixed-sample (%d draw)" % t["fs_draws"], "B8": "Always-retest B8", "G": "**Gatekeeper (G)**"}
    draws = {"S20": "20", "FS": str(t["fs_draws"]), "B8": "%.1f" % t["mean_draws"]["B8"], "G": "%.1f" % t["mean_draws"]["G"]}
    order = [k for k in ["U", "RS", "B6R", "B6S", "B6M", "LJ", "S20", "FS", "B8", "G"] if k in rc]
    L += table("Study T: kỹ năng thị trường (rule Ruff) trên 60 gói PyPI — %d ô dùng được" % rc["G"]["cells"],
               rc["G"]["harmful_total"], rc["G"]["safe_total"], {k: rc[k] for k in order}, names, draws,
               {k: verdict_vs(rc["G"], rc[k]) for k in order},
               "Tiêu chí đăng ký trước: W1 %s, W2 %s, W3 %s, W4 %s." % tuple("THẮNG" if t[w]["won"] else "THUA" for w in ("W1", "W2", "W3", "W4")))
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
    bp = R / "study_t/B9_RESULT.json"
    if bp.exists():
        b = json.loads(bp.read_text())
        c = b["cost_per_cell"]
        L += ["### Study T-A6: B9 (model tự áp dụng thay đổi) so với Gatekeeper, %d ô lấy mẫu" % b["cells"], "",
              "| Đại lượng | B9 (gemini-flash) | Gatekeeper | **Đánh giá** |", "|---|---|---|---|",
              "| Ô có hại được áp dụng / admit | %d / %d ô đánh giá được | %d | %s |" % (
                  b["b9_harmful_applied"], b["evaluable_b9"], b["g_harmful_admitted"],
                  "G **thắng**" if b["g_harmful_admitted"] < b["b9_harmful_applied"] else "G không thắng"),
              "| …trong đó trên ô vốn an toàn (B9 tự gây hại) | %d | — | |" % b["b9_harmful_among_truth_safe"],
              "| Hàm model trả lời không parse được | %d | 0 | |" % b["b9_unparsable_functions"],
              "| Chi phí mỗi ô (USD) | %.5f | %.5f (runner) | %s |" % (c["b9_usd"], c["g_usd_runner"],
                                                                       "G rẻ hơn" if c["g_usd_runner"] <= c["b9_usd"] else "G đắt hơn"),
              "| Thời gian mỗi ô (giây) | %.1f | %.1f | |" % (c["b9_seconds"], c["g_seconds"]),
              "", "Tiêu chí B9-W: **%s**. Tổng chi phí model: %.3f USD." % ("THẮNG" if b["B9_W"] else "THUA", b["spent_usd"]), ""]
    out_p.write_text("\n".join(L) + "\n")
    print(out_p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
