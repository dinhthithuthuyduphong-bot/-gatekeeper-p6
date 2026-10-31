"""Study Q amendment Q-A1, steps 1-2: reproduction check and blind review items.

python tools/q_review_items.py CAPTURE_DIR Q_RECORDS.jsonl.gz VERIFIED.json SEED OUT_DIR [--per-unit 5]

CAPTURE_DIR holds the outputs of tools/q_review_capture.py, one sub-directory per instance (R_<id>/ with Q_<id>.json,
inputs/, patches/).  For each HQ1 unit of the cohort (first patch, in seeded order, with a naive difference):
  reproduced  = the re-run scored the same patch (same sha) on the same target function and its classification summary
                (scored, categories, divergent, naive_harm, contract_harm) equals the cohort record exactly;
  review items = up to --per-unit contract-regression inputs (C1 or C2-D) of a reproduced unit, chosen in a seeded order,
                 written BLIND (no category, no instance outcome) in the format of tools/rq5_rate_llm.py.
Writes REPRO.json, ITEMS.json (blind), KEY.json (item -> instance, patch, source, index, category).
"""
import gzip
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import q_classify as QC  # noqa: E402

SUMMARY_KEYS = ("scored", "categories", "divergent", "naive_harm", "contract_harm")


def hq1_unit(rec):
    """The patch HQ1 uses for an instance (tools/q_analyze.py: hq1), or None."""
    scored = [p for p in sorted(rec.get("patches") or [], key=lambda p: p["order"]) if p.get("status") == "SCORED"]
    naive = [p for p in scored if p["classified"]["naive_harm"] > 0]
    return naive[0] if naive else None


def summary(classified):
    return {k: classified.get(k) for k in SUMMARY_KEYS}


def contract_inputs(outcomes):
    out = []
    for x in outcomes:
        if x.get("patch_stable") and x["orig"] == x["gold"] and x["patch"] != x["gold"]:
            c = QC.category(x["gold"], x["patch"])
            if c in QC.CONTRACT:
                out.append(dict(x, category=c))
    return out


def find_capture(cap_dir, iid):
    hits = sorted(Path(cap_dir).rglob("Q_%s.json" % iid))
    return hits[-1] if hits else None


def build(cap_dir, records_path, verified_path, seed, out_dir, per_unit=5):
    cohort = [json.loads(l) for l in gzip.open(records_path, "rt")]
    gold_patch = {r["instance_id"]: r["patch"] for r in json.loads(Path(verified_path).read_text())}
    repro, items, key = [], [], []
    for rec in sorted(cohort, key=lambda r: r["instance_id"]):
        unit = hq1_unit(rec)
        if unit is None:
            continue
        iid = rec["instance_id"]
        row = {"instance_id": iid, "sha": unit["sha"], "cohort_summary": summary(unit["classified"]),
               "cohort_contract_regression": unit["classified"]["contract_harm"] > 0}
        path = find_capture(cap_dir, iid)
        new = json.loads(path.read_text()) if path else None
        twin = next((p for p in (new or {}).get("patches") or [] if p.get("sha") == unit["sha"] and p.get("status") == "SCORED"), None)
        same_target = bool(new) and (new.get("target") or {}).get("qualname") == (rec.get("target") or {}).get("qualname") \
            and (new.get("target") or {}).get("file") == (rec.get("target") or {}).get("file")
        row.update(captured=bool(new), rerun_status=(new or {}).get("status"), same_target=same_target,
                   rerun_summary=summary(twin["classified"]) if twin else None,
                   same_generator=bool(new) and (new.get("target") or {}).get("generator_sha256") == (rec.get("target") or {}).get("generator_sha256"))
        row["reproduced"] = bool(twin) and same_target and row["rerun_summary"] == row["cohort_summary"]
        repro.append(row)
        if not row["reproduced"]:
            continue
        cand = contract_inputs(twin["classified"].get("outcomes") or [])
        random.Random("q-a1:%s:%s" % (seed, iid)).shuffle(cand)
        capdir = path.parent
        calls = None
        if (capdir / "inputs" / "g0.calls.json").is_file():
            calls = json.loads((capdir / "inputs" / "g0.calls.json").read_text())
        diff_path = capdir / "patches" / (unit["sha"] + ".diff")
        diff = diff_path.read_text() if diff_path.is_file() else ""
        for x in cand[:per_unit]:
            item_id = hashlib.sha256(("%s:%s:%s:%s" % (seed, iid, x["source"], x["i"])).encode()).hexdigest()[:12]
            if x["source"] == "G0" and calls is not None and x["i"] < len(calls):
                shown_input = calls[x["i"]]
            else:
                shown_input = "item #%d of the model-written input generator (inputs/g2.make_inputs.py)" % x["i"]
            items.append({"id": item_id, "function": new["target"]["qualname"], "file": new["target"]["file"], "diff": diff,
                          "reference_output": x["gold"], "patch_output": x["patch"], "input": shown_input,
                          "reference_diff": gold_patch.get(iid, "")[:3000]})
            key.append({"id": item_id, "instance_id": iid, "sha": unit["sha"], "source": x["source"], "i": x["i"], "category": x["category"]})
    items.sort(key=lambda it: it["id"])                            # blind order: not grouped by instance
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stats = {"hq1_units": len(repro), "captured": sum(r["captured"] for r in repro), "reproduced": sum(r["reproduced"] for r in repro),
             "items": len(items), "units_with_items": len({k["instance_id"] for k in key})}
    (out / "REPRO.json").write_text(json.dumps({"stats": stats, "units": repro}, indent=1))
    (out / "ITEMS.json").write_text(json.dumps(items, indent=1))
    (out / "KEY.json").write_text(json.dumps(key, indent=1))
    print(json.dumps(stats))
    return stats


def main(argv):
    per = int(argv[argv.index("--per-unit") + 1]) if "--per-unit" in argv else 5
    build(argv[0], argv[1], argv[2], argv[3], argv[4], per)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
