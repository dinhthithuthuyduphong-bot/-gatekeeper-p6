"""Re-render REPORT.md from a RESULT.json with the correct evidence class.

python tools/render_report.py RESULT.json OUT.md --evidence-class PROSPECTIVE_FROZEN_REAL_TARGETS
Only the presentation changes; RESULT.json is read, never modified.  (The frozen
pipeline labelled every report as demo fixtures; this tool fixes the label without
touching frozen files.)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite import report  # noqa: E402

LABELS = {
    "PROSPECTIVE_FROZEN_REAL_TARGETS":
        "> **Loại bằng chứng: PROSPECTIVE_FROZEN_REAL_TARGETS.** Target thật, chưa từng chạy trước "
        "khi đóng băng protocol; oracle gồm bộ test gốc của target và oracle metamorphic khai báo trước.",
    "POSTHOC_SUPPLEMENTARY":
        "> **Loại bằng chứng: POSTHOC_SUPPLEMENTARY.** Chạy hậu kiểm trên target đã thấy; báo riêng, "
        "không thay kết quả chính.",
    "REAL_CODE_DEVELOPMENT_ORACLE":
        "> **Loại bằng chứng: REAL_CODE_DEVELOPMENT_ORACLE.** Mã thật, nhưng target đã dùng khi phát "
        "triển và oracle biên viết sau khi nghiên cứu dữ liệu.",
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result")
    ap.add_argument("out")
    ap.add_argument("--evidence-class", required=True, choices=sorted(LABELS))
    args = ap.parse_args(argv)
    run = json.loads(Path(args.result).read_text(encoding="utf-8"))
    run["evidence_class"] = args.evidence_class
    run["limits"] = [x for x in run["limits"] if "constructed demo" not in x.lower()]
    text = report.render(run)
    old = next(l for l in text.splitlines() if l.startswith("> **Loại bằng chứng"))
    text = text.replace(old, LABELS[args.evidence_class]).replace(
        "# Gatekeeper-Lite — kết quả demo", f"# Gatekeeper-Lite — {run['config']['experiment_id']}")
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"written {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
