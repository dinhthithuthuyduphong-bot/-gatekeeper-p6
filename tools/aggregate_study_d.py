"""Combine per-target Study D results through gatekeeper_lite.studyd_decisions (the single
source of truth also used by the report and the ablation replay)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite.studyd_decisions import decide  # noqa: E402


def load_results(results_dir: str) -> dict:
    return {f.stem.replace("RESULT_", ""): json.loads(f.read_text())
            for f in Path(results_dir).glob("RESULT_*.json") if not f.stem.startswith("RESULT_B9")}


def main(config: str, results_dir: str, out: str) -> int:
    cfg = json.loads(Path(config).read_text())
    cells = decide(cfg, load_results(results_dir))
    keep = ("cell", "binds", "stop", "e", "B2", "B6R", "B8", "Gatekeeper", "eBH", "census_invalid", "census_bad",
            "fingerprint", "replay_ok")
    rows = [{k: c[k] for k in keep} | {"draws": (c["scope_result"] or {}).get("draws", 0),
                                         "counts": (c["scope_result"] or {}).get("counts")} for c in cells]
    Path(out).write_text(json.dumps({"cells": rows}, indent=2))
    for r in rows:
        print(r["cell"], r["B2"], r["B6R"], r["B8"], r["Gatekeeper"], r["draws"])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
