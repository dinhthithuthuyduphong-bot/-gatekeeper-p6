"""CLI:  python -m gatekeeper_lite run --config demo/config.json --out out_demo"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import report
from .experiment import run_experiment


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gatekeeper_lite")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run a frozen experiment configuration")
    r.add_argument("--config", default="demo/config.json")
    r.add_argument("--out", default="out_demo")
    sh = sub.add_parser("show", help="explain one pair from a RESULT.json (for live demo)")
    sh.add_argument("result")
    sh.add_argument("target")
    sh.add_argument("--skill", default=None)
    args = ap.parse_args(argv)

    if args.cmd == "show":
        return show(Path(args.result), args.target, args.skill)

    result = run_experiment(Path(args.config))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                     encoding="utf-8")
    (out / "REPORT.md").write_text(report.render(result), encoding="utf-8")
    s, d = result["summary"], result["summary"]["_denominators"]
    print(f"pairs={d['pairs']} harmful={d['harmful']} beneficial={d['beneficial']}")
    for comp in ("B2", "B6R", "B8", "Gatekeeper"):
        row = s[comp]
        print(f"  {comp:<10} harmful_admitted={row['harmful_admitted']} "
              f"beneficial_admitted={row['beneficial_admitted']} cost_tasks={row['cost_tasks']}")
    print(f"report: {out / 'REPORT.md'}")
    return 0


def show(result_path: Path, target: str, skill=None) -> int:
    run = json.loads(result_path.read_text(encoding="utf-8"))
    recs = [r for r in run["records"] + [c["record"] for c in run["compositions"]]
            if r["target"] == target and (skill is None or "+".join(r["skills"]) == skill)]
    if not recs:
        print("no matching record")
        return 1
    for r in recs:
        print("=" * 72)
        print(f"{'+'.join(r['skills'])}  ->  {r['target']}   cell={r['cell']}")
        print(f"bind: {'APPLIED' if r['bind']['ok'] else r['bind']['reason']}")
        if r["bind"]["diff"]:
            print(r["bind"]["diff"])
        print(f"footprint K: {r['bind']['footprint']}")
        p = r.get("paired")
        if p:
            print(f"paired tasks={p['tasks']} new_failures={len(p['new_failures'])} "
                  f"resolved={len(p['resolved_failures'])} loss {p['loss_without']} -> "
                  f"{p['loss_with']} (Z_suite={p['Z_suite']})  truth={r['ground_truth']}")
        g = r["gatekeeper"]
        print(f"Gatekeeper: {g['decision']} — {g['reason']}")
        if g["trajectory"]:
            traj = ", ".join(f"{v:.2f}" for v in g["trajectory"])
            print(f"  e-process E_n: {traj}")
        for comp in ("B2", "B6R", "B8"):
            c = r["comparators"][comp]
            print(f"  {comp}: {c['decision']}" + (f" ({c.get('reason')})" if c.get("reason") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
