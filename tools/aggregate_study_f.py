"""Study F aggregation: e-Holm over the WHOLE pre-registered family, then within-model effects.

python tools/aggregate_study_f.py study_f/config_study_f.json DIR_WITH_HELDOUT_JSON OUT.md

Family: every (model, repetition, target, scope) cell, K = config k_cells (144 = 4 x 3 x 6 x 2).
A cell without a submitted patch, with REJECT_HARM in any scope of its patch, or with a census
regression enters with e = 0.  A patch is deployed under "B9 + Gatekeeper" iff at least one of
its cells is selected by e-Holm (and, by construction, none of its scopes rejected harm).
Its end state is then the held-out verdict of the raw patch; otherwise NO_PATCH.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.eprocess import e_holm  # noqa: E402

VERDICTS = ("SUCCESS", "HARMFUL", "NO_EFFECT", "NO_PATCH", "BUDGET_CAP", "CENSUS_INVALID")


def main(config, heldout_dir, out):
    cfg = json.loads(Path(config).read_text())
    k, alpha = cfg["k_cells"], cfg["alpha"]
    models = list(cfg["b9_configs"])
    reps = cfg["repetitions"]
    scopes = {t: ["bool", "number" if t == "D2_cerberus" else "int"] for t in cfg["cells"]}
    family = {(m, r, t, s): 0.0 for m in models for r in range(reps) for t in cfg["cells"] for s in scopes[t]}
    if len(family) != k:
        raise SystemExit(f"family size {len(family)} != registered k_cells {k}")
    raw, cand = {}, {}
    files = sorted(Path(heldout_dir).glob("HELDOUT_*.json"))
    if {f.stem.replace("HELDOUT_", "") for f in files} != set(cfg["cells"]):
        raise SystemExit("held-out results missing for some targets")
    for f in files:
        h = json.loads(f.read_text())
        for row in h["rows"]:
            if row["approach"] == "B9 raw":
                raw[(row["model"], row["repetition"], h["target"])] = row["verdict"]
            elif row["approach"].startswith("B9+Gatekeeper"):
                key = (row["model"], row["repetition"], h["target"])
                cand[key] = row
                for s, e in row["gate"].get("e_min", {}).items():
                    family[(row["model"], row["repetition"], h["target"], s)] = e if row["candidate"] else 0.0
    selected = set(e_holm({"|".join(map(str, c)): e for c, e in family.items()}, alpha))
    gated = {}
    for key, verdict in raw.items():
        m, r, t = key
        deployed = any("|".join(map(str, (m, r, t, s))) in selected for s in scopes[t])
        gated[key] = verdict if deployed else "NO_PATCH"
    L = [f"# Study F — kết quả theo model (e-Holm trên K = {k} ô, α = {alpha}; chấm trên seed held-out)", "",
         "| Model | Điều kiện | " + " | ".join(VERDICTS) + " |", "|---|---|" + "---|" * len(VERDICTS)]
    for m in models:
        for lab, src in (("B9 thô", raw), ("B9 + Gatekeeper", gated)):
            cnt = defaultdict(int)
            for (mm, _, _), v in src.items():
                if mm == m:
                    cnt[v] += 1
            L.append(f"| {m} | {lab} | " + " | ".join(str(cnt[v]) for v in VERDICTS) + " |")
    L += ["", "| Model | Δ SUCCESS (GK − thô) | Δ HARMFUL (GK − thô) | n |", "|---|---|---|---|"]
    for m in models:
        keys = [key for key in raw if key[0] == m]
        ds = sum((gated[x] == "SUCCESS") - (raw[x] == "SUCCESS") for x in keys)
        dh = sum((gated[x] == "HARMFUL") - (raw[x] == "HARMFUL") for x in keys)
        L.append(f"| {m} | {ds:+d} | {dh:+d} | {len(keys)} |")
    L += ["", "Đơn vị là lần sửa (target × lần lặp); 6 target × 3 lần lặp không phải 18 target độc lập."]
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
