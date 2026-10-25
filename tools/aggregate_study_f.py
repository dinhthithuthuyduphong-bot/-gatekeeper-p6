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
from gatekeeper_ext.study_f_validation import VERDICTS, digest, require, validate_heldout  # noqa: E402


def main(config, heldout_dir, out):
    cfg = json.loads(Path(config).read_text())
    k, alpha = cfg["k_patches"], cfg["alpha"]
    models = list(cfg["b9_configs"])
    files = sorted(Path(heldout_dir).glob("HELDOUT_*.json"))
    if {f.stem.replace("HELDOUT_", "") for f in files} != set(cfg["cells"]):
        raise SystemExit("held-out results missing for some targets")
    documents = [json.loads(f.read_text()) for f in files]
    for f, doc in zip(files, documents):
        require(f.stem == "HELDOUT_" + str(doc.get("target")), "filename/target mismatch")
    raw_rows, candidate_rows = validate_heldout(cfg, documents, digest(config))
    raw = {key: row["verdict"] for key, row in raw_rows.items()}
    family = {key: row["e_patch"] for key, row in candidate_rows.items()}
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
    L += ["", "| Model | SUCCESS được giữ / SUCCESS thô | HARMFUL bị chặn / HARMFUL thô | Δ SUCCESS (điểm %) | Δ HARMFUL (điểm %) |",
          "|---|---|---|---|---|"]
    metrics = {}
    for m in models:
        keys = [key for key in raw if key[0] == m]
        success = sum(raw[x] == "SUCCESS" for x in keys)
        harm = sum(raw[x] == "HARMFUL" for x in keys)
        kept = sum(gated[x] == "SUCCESS" for x in keys)
        harm_after = sum(gated[x] == "HARMFUL" for x in keys)
        ds, dh = 100 * (kept - success) / len(keys), 100 * (harm_after - harm) / len(keys)
        metrics[m] = {"n": len(keys), "raw_success": success, "kept_success": kept,
                      "raw_harmful": harm, "blocked_harmful": harm - harm_after,
                      "delta_success_pp": ds, "delta_harmful_pp": dh,
                      "generation_cost_usd": sum(raw_rows[x]["cost_usd"] for x in keys)}
        L.append(f"| {m} | {kept}/{success}" + (" (không xác định tỷ lệ)" if not success else "")
                 + f" | {harm-harm_after}/{harm}" + (" (không có harm để đánh giá)" if not harm else "")
                 + f" | {ds:+.2f} | {dh:+.2f} |")
    L += ["", "## Theo target (đơn vị cụm)", "",
          "| Model | Target | n | SUCCESS thô → GK | HARMFUL thô → GK |", "|---|---|---|---|---|"]
    for m in models:
        for target in cfg["cells"]:
            keys = [x for x in raw if x[0] == m and x[2] == target]
            ns = lambda src, verdict: sum(src[x] == verdict for x in keys)
            L.append(f"| {m} | {target} | {len(keys)} | {ns(raw, 'SUCCESS')} → {ns(gated, 'SUCCESS')}"
                     f" | {ns(raw, 'HARMFUL')} → {ns(gated, 'HARMFUL')} |")
    L += ["", "Đơn vị cụm là target; các lần lặp trong một target không phải target độc lập.",
          "Gatekeeper ở đây là bộ lọc trên cùng patch: không thể tăng số SUCCESS thô; phải báo cáo cả harm bị chặn và SUCCESS bị loại.",
          "Không có HARMFUL thô không chứng minh khả năng chặn hại. Không suy ra model independence từ kết quả không khác biệt.",
          "Chi phí sinh patch dùng chung giữa hai điều kiện; phải cộng riêng chi phí admission để so hiệu quả kinh tế."]
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    Path(out).with_suffix(".json").write_text(json.dumps({"schema_version": 2,
        "evidence": "RECORDED_PROVIDER_REPLAY", "config_sha256": digest(config),
        "k_patches": k, "selected": sorted(selected), "models": metrics,
        "input_sha256": {f.name: digest(f) for f in files}}, indent=2, allow_nan=False))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
