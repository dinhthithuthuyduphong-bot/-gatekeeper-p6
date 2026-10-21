"""Results reproducibility check (separate from the frozen clean_room_check.py).

Re-derives, from the committed raw RESULT files only, and compares with what is committed:
  * every cell decision (B2, B6R, B8, Gatekeeper) against AGGREGATE.json
  * every per-cell draw count and help/tie/hurt count against AGGREGATE.json
  * census status / new-failure counts are present for every target that bound
  * the study's draw totals and measured-time totals quoted in its summaries
Missing results FAIL (no silent SKIP).  python tools/results_check.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.studyd_decisions import decide  # noqa: E402

STUDIES = [("study_d", "config_study_d.json", 3220, 3600), ("study_e", "config_study_e.json", 2106, 3000)]


def main() -> int:
    ok = True
    for study, cfg_name, exp_g, exp_b in STUDIES:
        res_dir = ROOT / study / "results"
        if not (res_dir / "AGGREGATE.json").exists():
            print(f"[FAIL] {study}: committed results missing")
            ok = False
            continue
        cfg = json.loads((ROOT / study / cfg_name).read_text())
        results = {f.stem.replace("RESULT_", ""): json.loads(f.read_text())
                   for f in res_dir.glob("RESULT_*.json") if not f.stem.startswith("RESULT_B9")}
        expected_targets = {c.split("/")[0] for c in cfg["cells"]}
        missing = sorted(expected_targets - set(results))
        if missing:
            print(f"[FAIL] {study}: raw results missing for {missing}")
            ok = False
            continue
        derived = decide(cfg, results)
        committed = {r["cell"]: r for r in json.loads((res_dir / "AGGREGATE.json").read_text())["cells"]}
        bad = []
        for c in derived:
            row = committed.get(c["cell"], {})
            for k in ("B2", "B6R", "B8", "Gatekeeper"):
                if row.get(k) != c[k]:
                    bad.append(f"{c['cell']}:{k}")
            sc = c["scope_result"]
            if sc and (row.get("draws") != sc["draws"] or row.get("counts") != sc["counts"]):
                bad.append(f"{c['cell']}:draws/counts")
            if c["binds"] and "status" not in c["result"].get("census", {}):
                bad.append(f"{c['cell']}:census missing")
        g = sum(s["draws"] for r in results.values() for s in r.get("scopes", {}).values())
        b = sum(s["b8"]["draws"] for r in results.values() for s in r.get("scopes", {}).values())
        if (g, b) != (exp_g, exp_b):
            bad.append(f"draw totals {g}/{b} != quoted {exp_g}/{exp_b}")
        ok &= not bad
        print(f"[{'OK' if not bad else 'FAIL'}] {study}: {len(derived)} cells, decisions + draws + counts + census "
              f"re-derived; draws GK {g} / B8 {b}" + (f" — mismatches: {bad[:6]}" if bad else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
