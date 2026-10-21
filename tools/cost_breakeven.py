"""When would fewer trials become real time savings?  (analysis of measured data only)

For each target: fixed cost F (census + worker start-up), measured seconds per paired draw
c, Gatekeeper draws g, B8 draws b.  Time = F + draws * c.  The per-draw cost c* at which
Gatekeeper saves a fraction r of B8's total time solves  (b - g) c* = r (F + b c*).
python tools/cost_breakeven.py study_d/results study_e/results [--out OUT.md]
"""
import argparse
import json
import sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    lines = ["# Chi phí: thời gian đo thật và ước tính theo mô hình (từ dữ liệu đã ghi, không chạy thêm)", "",
             "Thời gian đo thật = census (3 baseline + treatment + chạy lại nếu có) + khởi động worker + thời gian rút mẫu "
             "đã ghi (`gatekeeper_seconds` cho Gatekeeper; `seconds` cho B8, tức đủ 300 lần rút mỗi scope). Không gồm tải repo "
             "và cài dependency. Hai cột cuối là **ước tính theo mô hình** T = F + n·c.", "",
             "| Target | F đo được (s) | Lần rút GK / B8 | GK đo được (s) | B8 đo được (s) | Tiết kiệm đo được | "
             "c cần để tiết kiệm 10% (mô hình) | Tiết kiệm tối đa (mô hình, c rất lớn) |", "|---|---|---|---|---|---|---|---|"]
    tot = {"F": 0.0, "g": 0, "b": 0, "gk_s": 0.0, "b8_s": 0.0}
    for d in a.dirs:
        for f in sorted(Path(d).glob("RESULT_*.json")):
            if f.stem.startswith("RESULT_B9"):
                continue
            r = json.loads(f.read_text())
            scs = r.get("scopes", {})
            if not scs:
                continue
            F = sum(r.get("census", {}).get("seconds", {}).values()) + sum(r.get("startup_seconds", {}).values())
            g = sum(s["draws"] for s in scs.values())
            b = sum(s["b8"]["draws"] for s in scs.values())
            secs = sum(s["seconds"] for s in scs.values())
            gk_draw_s = sum(s.get("gatekeeper_seconds", 0.0) for s in scs.values())
            gk_s, b8_s = F + gk_draw_s, F + secs
            measured = (b8_s - gk_s) / b8_s if b8_s else 0.0

            def need(rr):
                den = (b - g) - rr * b
                return rr * F / den if den > 0 else float("inf")
            need10 = need(0.10)
            lines.append(f"| {r['target']} | {F:.2f} | {g} / {b} | {gk_s:.2f} | {b8_s:.2f} | {measured:.2%} | "
                         f"{(f'{need10:.2f} s' if need10 != float('inf') else 'không đạt được')} | {(b - g) / b:.1%} |")
            tot["F"] += F; tot["g"] += g; tot["b"] += b; tot["gk_s"] += gk_s; tot["b8_s"] += b8_s
    lines += ["", f"**Tổng (đo thật):** lần rút Gatekeeper {tot['g']} so với B8 {tot['b']} (ít hơn {1 - tot['g'] / tot['b']:.1%}); "
              f"thời gian Gatekeeper {tot['gk_s']:.2f} s so với B8 {tot['b8_s']:.2f} s (ít hơn {1 - tot['gk_s'] / tot['b8_s']:.2%}). "
              "Chi phí cố định chiếm gần toàn bộ thời gian; tiết kiệm thời gian chỉ đáng kể ở target có lần rút đắt (spec-kit). "
              "Tiết kiệm không bao giờ vượt tỉ lệ lần rút giảm được, và bằng 0 ở các ô không có quyết định sớm."]
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
