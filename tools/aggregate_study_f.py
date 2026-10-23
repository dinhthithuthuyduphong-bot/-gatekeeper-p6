"""Study F aggregation: e-Holm over the WHOLE pre-registered family, then within-model effects.

python tools/aggregate_study_f.py study_f/config_study_f.json DIR_WITH_HELDOUT_JSON OUT.md

Family (F-A2): every (model, repetition, target) PATCH, K = config k_patches (72 = 4 x 3 x 6).
Each patch has one e-value e_patch (gatekeeper_ext/patch_rule.py): benefit with low harm in some
scope AND low harm certified in every scope; 0 without a patch, with a harm alarm or a census
regression.  A patch is deployed under "B9 + Gatekeeper" iff e-Holm selects it.
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
    k, alpha = cfg["k_patches"], cfg["alpha"]
    models = list(cfg["b9_configs"])
    reps = cfg["repetitions"]
    family = {(m, r, t): 0.0 for m in models for r in range(reps) for t in cfg["cells"]}
    if len(family) != k:
        raise SystemExit(f"family size {len(family)} != registered k_patches {k}")
    raw = {}
    files = sorted(Path(heldout_dir).glob("HELDOUT_*.json"))
    if {f.stem.replace("HELDOUT_", "") for f in files} != set(cfg["cells"]):
        raise SystemExit("held-out results missing for some targets")
    for f in files:
        h = json.loads(f.read_text())
        for row in h["rows"]:
            key = (row.get("model"), row.get("repetition"), h["target"])
            if row["approach"] == "B9 raw":
                raw[key] = row["verdict"]
            elif row["approach"].startswith("B9+Gatekeeper"):
                family[key] = float(row["e_patch"])
    selected = set(e_holm({"|".join(map(str, c)): e for c, e in family.items()}, alpha))
    gated = {key: (v if "|".join(map(str, key)) in selected else "NO_PATCH") for key, v in raw.items()}
    L = [f"# Study F — kết quả theo model (e-Holm trên K = {k} patch, α = {alpha}; chấm trên seed held-out)", "",
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
