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
    lines = ["# Điểm hòa vốn chi phí (từ dữ liệu đã đo, không chạy thêm)", "",
             "| Target | Chi phí cố định F (s) | Giây / lần rút đo được | Lần rút GK / B8 | Tiết kiệm thời gian hiện tại | "
             "Giây/lần rút cần để tiết kiệm 10% | Tiết kiệm tối đa có thể (lần thử rất đắt) |", "|---|---|---|---|---|---|---|"]
    tot = {"F": 0.0, "g": 0, "b": 0, "secs": 0.0, "draws": 0}
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
            c = secs / b if b else 0.0
            now = (b - g) * c / (F + b * c) if F + b * c else 0.0

            def need(rr):
                den = (b - g) - rr * b
                return rr * F / den if den > 0 else float("inf")
            need10 = need(0.10)
            lines.append(f"| {r['target']} | {F:.1f} | {c * 1000:.2f} ms | {g} / {b} | {now:.2%} | "
                         f"{(f'{need10:.2f} s' if need10 != float('inf') else 'không đạt được')} | {(b - g) / b:.1%} |")
            tot["F"] += F; tot["g"] += g; tot["b"] += b; tot["secs"] += secs
    lines += ["", f"Tổng: F = {tot['F']:.0f} s; lần rút Gatekeeper {tot['g']} so với B8 {tot['b']} "
              f"(ít hơn {1 - tot['g'] / tot['b']:.1%}). Với chi phí mỗi lần rút đo được (vài ms), tiết kiệm thời gian "
              "gần bằng 0 ở hầu hết target; spec-kit (55 ms/lần rút) đã tiết kiệm khoảng 22%. Tiết kiệm không bao giờ vượt "
              "tỉ lệ lần rút giảm được (cột cuối), và bằng 0 ở các ô không có quyết định sớm (không có lợi ích, không có hại)."]
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
