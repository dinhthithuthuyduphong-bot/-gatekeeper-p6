"""Markdown report (Vietnamese) for the advisor demo."""
from __future__ import annotations

from typing import List

NAMES = {"B2": "B2 · dùng bừa", "B6R": "B6-R · replay + fingerprint",
         "B8": "B8 · luôn retest", "Gatekeeper": "Gatekeeper-Lite"}


def _row(cells: List[str]) -> str:
    return "| " + " | ".join(str(c) for c in cells) + " |"


def render(run: dict) -> str:
    out = ["# Gatekeeper-Lite — kết quả demo", "",
           f"Thời điểm chạy (UTC): {run['created_utc']} · Python {run['python']} · "
           f"config `{run['config_sha256'][:12]}`", "",
           "> **Loại bằng chứng: CONSTRUCTED_DEMO_FIXTURES.** Đây là demo cơ chế trên target "
           "dựng sẵn, không phải kết quả nghiên cứu trên repository độc lập.", ""]

    cfg = run["config"]
    out += ["## Tham số đã đóng băng", "",
            f"- θ (benefit margin): {cfg['theta']} · α tổng: {cfg['alpha_total']} · "
            f"ngân sách: {cfg['budget_tasks']} task/cặp · seed: {cfg['seed']}",
            f"- Bằng chứng: {cfg.get('evidence', 'mean_betting')}"
            + (f" {cfg.get('discordant')}" if cfg.get('evidence') == 'discordant_sign' else "")
            + (f" · ưu tiên task: {cfg.get('task_priority')}" if cfg.get('task_priority') else "")
            + (f" · lọc task: {cfg.get('task_filter')}" if cfg.get('task_filter') else ""), ""]

    out += ["## Từng cặp skill–target", "",
            _row(["Target", "Regime", "Skill", "Bind", "Nhãn thật", "B2", "B6-R", "B8",
                  "Gatekeeper", "Task GK dùng"]),
            _row(["---"] * 10)]
    for r in run["records"]:
        c = r["comparators"]
        bind = "áp dụng" if r["bind"]["ok"] else r["bind"]["reason"].split(": ", 1)[-1]
        scope = f" [{r['scope_class']}]" if r.get("scope_class") else ""
        out.append(_row([r["target"] + scope, r["regime"], "+".join(r["skills"]), bind,
                         r["ground_truth"], c["B2"]["decision"], c["B6R"]["decision"],
                         c["B8"]["decision"], c["Gatekeeper"]["decision"],
                         r["gatekeeper"]["tasks_used"]]))
    out.append("")

    s = run["summary"]
    d = s["_denominators"]
    out += ["## Tổng hợp (số đếm thô)", "",
            f"Mẫu số: {d['pairs']} cặp · có hại {d['harmful']} · có lợi {d['beneficial']} · "
            f"không đổi {d['no_delta']} · không áp dụng được {d['not_applicable']}", "",
            _row(["Comparator", "Cặp có hại bị admit", "Cặp có lợi được admit",
                  "Cặp có lợi bị bỏ lỡ", "Chi phí (lượt chạy task)"]),
            _row(["---"] * 5)]
    for comp in ("B2", "B6R", "B8", "Gatekeeper"):
        row = s[comp]
        out.append(_row([NAMES[comp], f"{row['harmful_admitted']}/{d['harmful']}",
                         f"{row['beneficial_admitted']}/{d['beneficial']}",
                         row["beneficial_not_admitted"], row["cost_tasks"]]))
    out.append("")

    sens = [r for r in run["records"] if r.get("sensitivity")]
    if sens:
        keys = list(sens[0]["sensitivity"])
        out += ["## Phân tích độ nhạy (lớp task khai báo trước)", "",
                _row(["Target", "Skill", "Nhãn gốc"] + [k.replace("without:", "Bỏ ") for k in keys]),
                _row(["---"] * (3 + len(keys)))]
        for r in sens:
            out.append(_row([r["target"], "+".join(r["skills"]), r["ground_truth"]]
                            + [f"{r['sensitivity'][k]['truth']} (sửa {r['sensitivity'][k]['resolved']}, "
                               f"hỏng {r['sensitivity'][k]['new_failures']})" for k in keys]))
        out.append("")

    if run["compositions"]:
        out += ["## Composition (Theorem 7)", ""]
        for comp in run["compositions"]:
            out += [f"- Skill: {' ∘ '.join(reversed(comp['skills']))} trên `{comp['target']}`",
                    f"  - Z riêng lẻ: {comp['single_Z']} → {comp['single_truth']}",
                    f"  - Z khi ghép: {comp['composite_Z']} → {comp['composite_truth']}",
                    f"  - Footprint giao nhau: {comp['footprint_overlap'] or 'không'}",
                    f"  - B6-R admit từng skill riêng: {comp['per_skill_B6R_admits_both']}",
                    f"  - Gatekeeper với bài toán ghép: "
                    f"{comp['gatekeeper_composite_decision']}"]
        out.append("")

    if run["retirements"]:
        out += ["## Retirement khi môi trường đổi", ""]
        for ret in run["retirements"]:
            line = f"- `{ret['target']}` · {ret.get('change')} → {ret['status']}"
            if "revalidation" in ret:
                rv = ret["revalidation"]
                alpha = "—" if rv["alpha"] is None else f"{rv['alpha']:.4g}"
                line += (f"; kiểm lại: {rv['decision']} (α={alpha}, "
                         f"{rv['tasks_used']} task) — {rv['reason']}")
            out.append(line)
        out.append("")

    out += ["## Giới hạn", ""] + [f"- {x}" for x in run["limits"]]
    return "\n".join(out) + "\n"
