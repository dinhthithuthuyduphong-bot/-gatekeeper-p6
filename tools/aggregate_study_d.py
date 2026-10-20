"""Combine per-target Study D results: e-Holm (primary) and e-BH (secondary) over all
pre-registered cells, plus B2 / B6-R / B8 decisions and measured cost."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gatekeeper_lite.eprocess import e_bh, e_holm  # noqa: E402


def main(config: str, results_dir: str, out: str) -> int:
    cfg = json.loads(Path(config).read_text())
    rows, evals = [], {}
    for cell in cfg["cells"]:
        tgt, scope = cell.split("/")
        f = Path(results_dir) / f"RESULT_{tgt}.json"
        r = json.loads(f.read_text()) if f.exists() else None
        sc = (r or {}).get("scopes", {}).get(scope)
        binds = bool(r and r.get("bind", {}).get("treated_modules"))
        e = sc["e_min"] if sc and sc["decision"] in ("ADMIT", "UNDECIDED") else 0.0
        evals[cell] = e
        rows.append({"cell": cell, "binds": binds, "gk_stop": sc["decision"] if sc else "OUT_OF_SCOPE",
                     "draws": sc["draws"] if sc else 0, "counts": sc["counts"] if sc else None,
                     "b8": (sc or {}).get("b8"), "census_new": len((r or {}).get("census", {}).get("new_failures", [])),
                     "B2": "ADMIT" if binds else "OUT_OF_SCOPE",
                     "B6R": "ADMIT" if binds and (r or {}).get("B6R_replay", {}).get("passed") else "REJECT"})
    holm, bh = set(e_holm(evals, cfg["alpha"])), set(e_bh(evals, cfg["alpha"]))
    for row in rows:
        row["Gatekeeper"] = "ADMIT" if row["cell"] in holm and row["gk_stop"] != "REJECT_HARM" else (
            "REJECT_HARM" if row["gk_stop"] == "REJECT_HARM" else row["gk_stop"] if row["gk_stop"] == "OUT_OF_SCOPE" else "QUARANTINE")
        row["Gatekeeper_eBH"] = "ADMIT" if row["cell"] in bh and row["gk_stop"] != "REJECT_HARM" else "-"
    Path(out).write_text(json.dumps({"cells": rows, "e_values": evals}, indent=2))
    for row in rows:
        print(row["cell"], row["B2"], row["B6R"], (row["b8"] or {}).get("decision"), row["Gatekeeper"], row["draws"])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
