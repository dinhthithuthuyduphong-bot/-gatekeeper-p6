"""RQ5 step 2 (plan: research_closure/results/rq5/RQ5_PLAN.md): reproduction check and rule-based classification of every
harmful input of the re-generated patches.  python tools/rq5_classify.py ARTIFACT_DIR RQ5_TARGETS.json OUT_DIR"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from gatekeeper_ext import gates as G  # noqa: E402
from p_analyze import wilson  # noqa: E402

KEYS = ("complete", "harm", "help", "divergent", "by_source")
PLAUSIBLE_TOTAL = 205                    # light-model plausible patches of the cohort (study_p results)
ORIGINAL_IN_BAND = 16


def category(gold, patch):
    if gold == ["timeout"] or patch == ["timeout"] or not isinstance(gold, list) or not isinstance(patch, list):
        return "C3"
    if gold[0] == "ok":
        return "C1a" if patch[0] == "exc" else "C1b"
    if patch[0] == "ok":
        return "C2a"
    return "C2b" if patch[1] != gold[1] else "C2c"


def classify(att):
    d = att.get("draws") or {}
    cats, examples = {}, []
    for x in d.get("outcomes") or []:
        if not x["patch_stable"] or x["orig"] != x["gold"] or x["patch"] == x["gold"]:
            continue
        c = category(x["gold"], x["patch"])
        cats[c] = cats.get(c, 0) + 1
        if c.startswith("C1") and len(examples) < 5:
            examples.append({"source": x["source"], "i": x["i"], "reference": x["gold"], "patch": x["patch"]})
    return cats, examples


def main(art, targets_path, out):
    targets = {t["name"]: t for t in json.loads(Path(targets_path).read_text())}
    rows = []
    for f in sorted(Path(art).rglob("COHORT_*.json")):
        r = json.loads(f.read_text())
        t = targets.get(r["name"])
        att = next((a for a in (r.get("inner") or {}).get("attempts", []) if a.get("model") == "vertex-gemini-flash"), None)
        if not t or att is None:
            continue
        d = att.get("draws") or {}
        reproduced = bool((att.get("labels") or {}).get("plausible")) and all(d.get(k) == t["original"].get(k) for k in KEYS)
        cats, ex = classify(att)
        n = d.get("complete") or 0
        c1 = cats.get("C1a", 0) + cats.get("C1b", 0)
        lo, hi = G.band_edges(n) if n else (None, None)
        rows.append({"name": r["name"], "repo": r["repo"], "reproduced": reproduced, "original": t["original"],
                     "categories": cats, "theta_c1": c1 / n if n else None,
                     "in_band_c1": bool(n and lo <= c1 / n <= hi), "c1_examples": ex, "diff": att.get("diff")})
    missing = sorted(set(targets) - {x["name"] for x in rows})
    rep = [x for x in rows if x["reproduced"]]
    nonrep = [x for x in rows if not x["reproduced"]] + [{"name": m, "original": targets[m]["original"]} for m in missing]
    k_rep = sum(x["in_band_c1"] for x in rep)
    k_upper = k_rep + sum(1 for x in nonrep if x["original"].get("in_band"))
    res = {"targets": len(targets), "rescored": len(rows), "reproduced": len(rep), "not_reproduced_or_missing": [x["name"] for x in nonrep],
           "category_totals": {c: sum(x["categories"].get(c, 0) for x in rep) for c in ("C1a", "C1b", "C2a", "C2b", "C2c", "C3")},
           "revised_primary": {"lower": {"in_band": k_rep, "share": k_rep / PLAUSIBLE_TOTAL, "wilson95": wilson(k_rep, PLAUSIBLE_TOTAL)},
                               "upper": {"in_band": k_upper, "share": k_upper / PLAUSIBLE_TOTAL, "wilson95": wilson(k_upper, PLAUSIBLE_TOTAL)},
                               "registered": {"in_band": ORIGINAL_IN_BAND, "share": ORIGINAL_IN_BAND / PLAUSIBLE_TOTAL}},
           "patches": rows}
    Path(out).mkdir(parents=True, exist_ok=True)
    (Path(out) / "RQ5_CLASSIFIED.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "patches"}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
