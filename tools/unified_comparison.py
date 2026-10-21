"""Common-standard comparison across approaches (no new runs).

Every approach is judged by the END STATE of the target code it leaves behind, scored by
the SAME frozen draw oracle (full 300-draw budget) and census, through the SAME verdict
function (gatekeeper_lite.b9.b9_verdict).  No outcome is simulated: when a skill is
deployed, ALL of its measured scope outcomes count.
  * B2, B6-R, B8 : target-level decisions.  The skill is deployed iff the comparator admits
                   EVERY scope cell of the target (B8 rejects the whole skill on any harm).
  * Gatekeeper   : deployed iff at least one scope is admitted.  Deployment is the full
                   skill (no runtime scope guard exists); this is exact here only if the
                   non-admitted scopes showed NO behaviour change, which is checked and
                   reported per target ("scope restriction needed" otherwise).
  * B9           : the submitted patch (from RESULT_B9_*.json, when available).
python tools/unified_comparison.py study_d/results study_e/results [--b9 DIR] [--out OUT.md]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.b9 import b9_verdict  # noqa: E402

TIE = {"help": 0, "tie": 300, "hurt": 0}


def end_state(result: dict, aggregate_rows: dict, target: str, approach: str) -> tuple:
    scopes = result.get("scopes", {})
    if not scopes:
        return {"status": "NO_PATCH"}, ""
    decisions = {s: aggregate_rows.get(f"{target}/{s}", {}).get(approach) for s in scopes}
    if approach == "Gatekeeper":
        deploy = any(d == "ADMIT" for d in decisions.values())
    else:
        deploy = all(d == "ADMIT" for d in decisions.values())
    if not deploy:
        return {"status": "NO_PATCH"}, ""
    note = ""
    if approach == "Gatekeeper":
        changed = [s for s, d in decisions.items() if d != "ADMIT"
                   and (scopes[s]["b8"]["counts"]["help"] or scopes[s]["b8"]["counts"]["hurt"])]
        note = " (cần giới hạn scope: " + ", ".join(changed) + ")" if changed else ""
    hidden = {s: sc["b8"]["counts"] for s, sc in scopes.items()}
    return {"status": "SUBMITTED", "census": result.get("census", {}), "hidden_oracle": hidden}, note


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--b9")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    lines = ["# So sánh theo chuẩn chung: trạng thái cuối của mã, cùng oracle, cùng hàm kết luận", "",
             "| Target | Skill + Gatekeeper | Skill + B6-R | Skill + B8 | B9 (DeepSeek / Gemini) |", "|---|---|---|---|---|"]
    b9 = {}
    if a.b9:
        for f in Path(a.b9).glob("*RESULT_B9_*.json"):
            r = json.loads(f.read_text())
            if r.get("evidence") not in ("PAID_B9", "REPLAY_OF_RECORDED_B9"):
                raise SystemExit(f"{f.name}: evidence={r.get('evidence')!r} is not B9 evidence "
                                 "(dry runs and unmarked files are refused)")
            b9.setdefault(r["target"], []).extend(f"{r['model']}:{v}" for v in r.get("verdicts", []))
    for d in a.dirs:
        d = Path(d)
        agg = {row["cell"]: row for row in json.loads((d / "AGGREGATE.json").read_text())["cells"]}
        for f in sorted(d.glob("RESULT_*.json")):
            if f.stem.startswith("RESULT_B9"):
                continue
            r = json.loads(f.read_text())
            t = r["target"]
            cols = []
            for ap_ in ("Gatekeeper", "B6R", "B8"):
                st, note = end_state(r, agg, t, ap_)
                cols.append(b9_verdict(st) + note)
            lines.append(f"| {t} | " + " | ".join(cols) + f" | {', '.join(b9.get(t, [])) or 'chưa chạy / không áp dụng'} |")
    lines += ["", "SUCCESS = có lợi ở scope lỗi, không hại ở đâu; HARMFUL = có hại ở bất kỳ scope nào hoặc census; "
              "NO_EFFECT = có thay đổi nhưng không đo được lợi ích; NO_PATCH = không triển khai gì (mã giữ nguyên). "
              "B2/B6-R/B8 quyết định ở mức target; Gatekeeper triển khai toàn bộ skill khi có ít nhất một scope được admit, "
              "và mọi kết quả scope đã đo đều được tính (không mô phỏng)."]
    text = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
