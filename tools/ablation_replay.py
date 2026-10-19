"""Post-hoc ablations replayed on frozen per-task outcomes (no new executions).

python tools/ablation_replay.py RESULT.json [--out ABLATION.md]
Each variant re-applies a modified Gatekeeper rule to the SAME measured paired outcomes
of a scoped study (e.g. Study C), so differences come only from the rule.  Ground truth
per cell is taken from the full scoped pool, as in the study.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite.eprocess import e_bh  # noqa: E402
from gatekeeper_lite.gatekeeper import BindOutcome, gatekeeper  # noqa: E402
from gatekeeper_lite.scoped import _view, scope_members  # noqa: E402
from gatekeeper_lite.skill import Target  # noqa: E402


class _Ledger:
    def __init__(self, alpha):
        self.alpha = alpha

    def draw(self, cell, epoch):
        return self.alpha


VARIANTS = [
    ("Đầy đủ (như đã chạy)", {}),
    ("Bỏ chia scope (gộp mọi task)", {"_no_scopes": True}),
    ("E-process trung bình θ=0,1 thay kiểm định dấu", {"evidence": "mean_betting"}),
    ("Bỏ lọc theo khả năng chạm", {"_no_reach": True}),
    ("Bỏ ưu tiên oracle (thứ tự ngẫu nhiên)", {"task_priority": None}),
    ("Bonferroni thay e-BH (ngưỡng 1/(α/K))", {"_bonferroni": True}),
]


def replay(run: dict, variant: dict) -> dict:
    cfg = copy.deepcopy(run["config"])
    cfg.update({k: v for k, v in variant.items() if not k.startswith("_")})
    bases = {}
    for r in run["records"]:
        bases.setdefault((r["target"], r["skills"][0]), r)
    k_cells = len(cfg["cells"])
    if variant.get("_bonferroni"):
        cfg.pop("multiplicity", None)
        ledger = _Ledger(cfg.get("alpha_total", 0.1) / k_cells * 3.14159 ** 2 / 6)
    else:
        ledger = _Ledger(None)
    cells, pool = [], {}
    for (tgt, skill), r in bases.items():
        per = {}
        for x in run["records"]:
            if x["target"] == tgt and x["skills"][0] == skill and "paired" in x:
                per.update(x["paired"]["per_task"])
        if not per:
            continue
        reach_all = r.get("task_filter", {}).get("reached_ids")
        scopes = {"all": []} if variant.get("_no_scopes") else cfg["scopes"]
        groups = {"all": sorted(per)} if variant.get("_no_scopes") else scope_members(sorted(per), scopes)
        for scope, ids in groups.items():
            view = _view(per, ids)
            reached = None if variant.get("_no_reach") or reach_all is None else set(reach_all) & set(ids)
            target = Target(tgt, Path("."), {"python": "3.12", "packages": {}})
            gk = gatekeeper(f"{tgt}/{skill}/{scope}", [], target, view, BindOutcome(True, "x"),
                            ledger, cfg, 0, reached)
            truth_view = view
            truth = "HARMFUL" if truth_view.new_failures else ("BENEFICIAL" if truth_view.resolved_failures else "NO_DELTA")
            cells.append({"cell": f"{tgt}/{skill}/{scope}", "truth": truth, "decision": gk.decision,
                          "e": gk.e_value or 0.0, "trials": 2 * gk.tasks_used})
            pool[cells[-1]["cell"]] = (gk.e_value or 0.0) if gk.decision in ("ADMIT", "PENDING_EBH") else 0.0
    if cfg.get("multiplicity", {}).get("method") == "e-BH":
        admitted = set(e_bh(pool, cfg["multiplicity"]["fdr"]))
        for c in cells:
            if c["decision"] in ("ADMIT", "PENDING_EBH"):
                c["decision"] = "ADMIT" if c["cell"] in admitted else "QUARANTINE"
    return {"cells": len(cells),
            "harmful": sum(c["truth"] == "HARMFUL" for c in cells),
            "beneficial": sum(c["truth"] == "BENEFICIAL" for c in cells),
            "harmful_admitted": sum(c["truth"] == "HARMFUL" and c["decision"] == "ADMIT" for c in cells),
            "beneficial_admitted": sum(c["truth"] == "BENEFICIAL" and c["decision"] == "ADMIT" for c in cells),
            "harm_rejections": sum(c["decision"] == "REJECT_HARM" for c in cells),
            "trials": sum(c["trials"] for c in cells)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    run = json.loads(Path(args.result).read_text(encoding="utf-8"))
    lines = [f"# Ablation hậu kiểm trên dữ liệu `{run['config']['experiment_id']}` (không chạy thêm)", "",
             "| Biến thể | Ô (có hại / có lợi) | Có hại bị admit | Có lợi được admit | Từ chối vì tác hại | Lượt chạy thử |",
             "|---|---|---|---|---|---|"]
    for name, variant in VARIANTS:
        s = replay(run, variant)
        lines.append(f"| {name} | {s['cells']} ({s['harmful']}/{s['beneficial']}) | {s['harmful_admitted']} | "
                     f"{s['beneficial_admitted']} | {s['harm_rejections']} | {s['trials']} |")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
