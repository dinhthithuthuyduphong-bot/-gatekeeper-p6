"""Study V (study_v/PROTOCOL.md): retirement under a real environment change (CPython 3.12 -> 3.13).

python tools/v_analyze.py T_DIR V_DIR
Reads T_DIR/STUDY_T_RESULT.json (Study T, whole alpha), T_DIR/STUDY_T_EPOCH0.json (Study T at the epoch-0 share),
V_DIR/STUDY_V_RESULT.json (Study V at the epoch-1 share) and V_DIR/TRIALS_*.json (fingerprints).  Writes V_DIR/V_RESULT.json.
"""
import json
import sys
from pathlib import Path

T_PYTHON = "3.12"     # Study T's trial environment (setup-python 3.12 in study-t-trials.yml)


def analyse(td, vd):
    t_full = {r["cell"]: r for r in json.loads((td / "STUDY_T_RESULT.json").read_text())["rows"]}
    t0 = {r["cell"]: r for r in json.loads((td / "STUDY_T_EPOCH0.json").read_text())["rows"]}
    vres = json.loads((vd / "STUDY_V_RESULT.json").read_text())
    v = {r["cell"]: r for r in vres["rows"]}
    fps = {}
    for p in vd.glob("TRIALS_*.json"):
        rec = json.loads(p.read_text())
        fp = (rec.get("env") or {}).get("fingerprint")
        if fp:
            fps[rec["project"]] = fp
    both = sorted(set(t0) & set(v))
    to_harm = [c for c in both if not t0[c]["harmful"] and v[c]["harmful"]]
    to_safe = [c for c in both if t0[c]["harmful"] and not v[c]["harmful"]]
    t_adm = [c for c in both if t0[c]["G"]]
    f0_miss = [c for c in t_adm if v[c]["harmful"]]
    changed_fp = sorted(p for p, fp in fps.items() if not fp["python"].startswith(T_PYTHON))
    retired = [c for c in t_adm if c.split("/", 1)[0] in changed_fp]
    harm_v = [c for c in both if v[c]["harmful"]]
    safe_v = [c for c in both if not v[c]["harmful"]]
    f1 = {"harmful_admitted": sum(1 for c in harm_v if v[c]["G"]), "harmful_total": len(harm_v),
          "safe_admitted": sum(1 for c in safe_v if v[c]["G"]), "safe_total": len(safe_v),
          "mean_draws": round(sum(v[c]["g_draws"] for c in both) / len(both), 1) if both else None}
    b8 = {"harmful_admitted": sum(1 for c in harm_v if v[c]["B8"]), "safe_admitted": sum(1 for c in safe_v if v[c]["B8"]),
          "mean_draws": round(sum(v[c]["n_gate"] for c in both) / len(both), 1) if both else None}
    res = {"usable_t": len(t0), "usable_v": len(v), "usable_both": len(both),
           "packages_with_fingerprint": len(fps), "packages_fingerprint_changed": len(changed_fp),
           "python_v": sorted({fp["python"] for fp in fps.values()}),
           "flips_safe_to_harmful": to_harm, "flips_harmful_to_safe": to_safe,
           "t_admitted_epoch0": len(t_adm), "t_admitted_full_alpha": sum(1 for c in both if t_full.get(c, {}).get("G")),
           "f0_harmful_kept": len(f0_miss), "f0_harmful_kept_cells": f0_miss,
           "f1_retired": len(retired), "f1_epoch1": f1, "b8_v": b8,
           "package_errors_v": vres.get("package_errors", [])}
    res["V_W1"] = f1["harmful_admitted"] == 0
    res["V_W2"] = set(f0_miss) <= set(retired)
    (vd / "V_RESULT.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    r = analyse(Path(sys.argv[1]), Path(sys.argv[2]))
    print(json.dumps({k: v for k, v in r.items() if not k.endswith("_cells")}, indent=1))
