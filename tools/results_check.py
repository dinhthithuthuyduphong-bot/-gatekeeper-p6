"""Results reproducibility check (separate from the frozen clean_room_check.py):
re-derive every committed decision table from the committed raw RESULT files.
python tools/results_check.py   -> exit 1 on any mismatch"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.studyd_decisions import decide  # noqa: E402

STUDIES = [("study_d", "config_study_d.json"), ("study_e", "config_study_e.json")]
KEYS = ("cell", "B2", "B6R", "B8", "Gatekeeper")


def main() -> int:
    ok = True
    for study, cfg_name in STUDIES:
        res_dir = ROOT / study / "results"
        if not (res_dir / "AGGREGATE.json").exists():
            print(f"[SKIP] {study}: no committed results")
            continue
        cfg = json.loads((ROOT / study / cfg_name).read_text())
        results = {f.stem.replace("RESULT_", ""): json.loads(f.read_text())
                   for f in res_dir.glob("RESULT_*.json") if not f.stem.startswith("RESULT_B9")}
        derived = [{k: c[k] for k in KEYS} for c in decide(cfg, results)]
        committed = [{k: r[k] for k in KEYS} for r in json.loads((res_dir / "AGGREGATE.json").read_text())["cells"]]
        same = derived == committed
        ok &= same
        print(f"[{'OK' if same else 'FAIL'}] {study}: {len(derived)} cell decisions re-derived from raw results")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
