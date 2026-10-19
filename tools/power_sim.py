"""Power simulation for Gatekeeper admission on measured paired outcomes.

python tools/power_sim.py out_real/RESULT.json [--sims 2000] [--exclude lazy] [--out POWER.md]

For every paired record it rebuilds the task pool the e-process would see (reach-
filtered when available; otherwise discriminating tasks plus the right number of
tied tasks), then replays many frozen random orders under several designs and reports
P(ADMIT), P(REJECT_HARM) and mean tasks used.  Uses only already-measured outcomes.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite.eprocess import BettingEProcess, DiscordantSignEProcess  # noqa: E402

DESIGNS = [
    ("mean θ=0.1", "mean", 24, False), ("mean θ=0.1", "mean", 120, False),
    ("dấu q0=0.6", "sign", 24, False), ("dấu q0=0.6", "sign", 120, False),
    ("dấu q0=0.6 + ưu tiên oracle biên", "sign", 24, True),
    ("dấu q0=0.6 + ưu tiên oracle biên", "sign", 120, True),
]


def pool(record: dict, exclude: list) -> list:
    per = record["paired"]["per_task"]
    tf = record.get("task_filter") or {}
    ids = tf.get("reached_ids")
    if ids is None:
        disc = [c for c, v in per.items() if v["Z"] != 0]
        n_reach = tf.get("reaching_tasks") or len(per)
        zeros = [f"_tie_{i}" for i in range(max(n_reach - len(disc), 0))]
        items = [(c, per[c]["Z"]) for c in disc] + [(c, 0.0) for c in zeros]
    else:
        items = [(c, per[c]["Z"]) for c in ids]
    return [(c, z) for c, z in items if not any(e in c for e in exclude)]


def simulate(items, kind, budget, prioritise, threshold, sims, rng):
    admit = harm = used = 0
    for _ in range(sims):
        pri = [x for x in items if prioritise and "gk_boundary" in x[0]]
        rest = [x for x in items if x not in pri]
        rng.shuffle(pri)
        rng.shuffle(rest)
        order = (pri + rest)[:budget]
        ep = DiscordantSignEProcess() if kind == "sign" else BettingEProcess(0.1)
        n = 0
        for n, (_, z) in enumerate(order, 1):
            ep.update(z)
            if getattr(ep, "harm_value", 0) >= threshold:
                harm += 1
                break
            if ep.value >= threshold:
                admit += 1
                break
        used += n
    return admit / sims, harm / sims, used / sims


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("result")
    ap.add_argument("--sims", type=int, default=2000)
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--alpha-cell", type=float, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    run = json.loads(Path(args.result).read_text(encoding="utf-8"))
    cells = run["config"]["cells"]
    alpha_cell = args.alpha_cell or min(cells.values())
    threshold = 1.0 / (alpha_cell * 6 / math.pi ** 2)
    rng = random.Random(20261019)
    lines = [f"# Mô phỏng lực kiểm định ({args.sims} thứ tự ngẫu nhiên mỗi ô)", "",
             f"Nguồn: `{args.result}` · α/ô = {alpha_cell} · ngưỡng 1/α (epoch 0) = {threshold:.0f}"
             + (f" · loại bỏ: {args.exclude}" if args.exclude else ""), "",
             "| Target | Skill | Pool (bất đồng: lợi/hại) | Thiết kế | Ngân sách | P(ADMIT) | P(REJECT_HARM) | Task dùng TB |",
             "|---|---|---|---|---|---|---|---|"]
    for r in run["records"]:
        if "paired" not in r:
            continue
        items = pool(r, args.exclude)
        helped = sum(1 for _, z in items if z < 0)
        hurt = sum(1 for _, z in items if z > 0)
        for name, kind, budget, pri in DESIGNS:
            a, h, u = simulate(items, kind, budget, pri, threshold, args.sims, rng)
            lines.append(f"| {r['target']} | {r['skills'][0]} | {len(items)} ({helped}/{hurt}) | {name} | "
                         f"{budget} | {a:.2f} | {h:.2f} | {u:.1f} |")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
