"""Study P analysis, exactly as registered (study_p/STUDY_P_PROTOCOL.md sections 4 and 9).

python tools/p_analyze.py ARTIFACT_DIR OUT_DIR [--frame study_p/candidates_astar.json] [--dev-repos FILE ...] [--boot 10000]

RQ1  funnel: candidates -> eligible -> usable function -> patches
PRIMARY  share of PLAUSIBLE light-model patches (one per instance) whose theta-hat is in the band [3/n, 1 - 0.1**(1/20)],
         with a Wilson 95% interval and a 95% cluster bootstrap interval resampling repositories; P3 = Wilson half-width <= 0.05
H1 (secondary)  exact one-sided binomial test of H0: share <= 0.10
H3 / P4  among acceptable plausible patches (theta-hat < 5%): McNemar exact one-sided on the fixed-sample vs Gatekeeper
         discordant pairs; tested only with >= 11 discordant pairs
RQ4  per gate: admission rate, admission of inadmissible patches (theta-hat > 5%), rejection of patches with theta-hat = 0
Sensitivity  (a) repositories of the development sets excluded, (b) G2 weight 0, 50, 100% (stratified estimates)
Exploratory  the strong model on the same instances (paired)
"""
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext import gates as G  # noqa: E402

LIGHT, STRONG = "vertex-gemini-flash", "vertex-gemini-argon"
GATES = ("census_only", "zero_tolerance", "b8_plus", "smoke20", "fixed_sample", "gatekeeper")


def wilson(k, n, z=1.96):
    if not n:
        return None, None
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def binom_sf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def in_band_rate(theta, n):
    lo, hi = G.band_edges(n)
    return theta is not None and n > 0 and lo <= theta <= hi


def cluster_boot(rows, key, B=10000, seed=11):
    """95% percentile interval of the share, resampling repositories with replacement [Field & Welsh 2007]."""
    by = {}
    for r in rows:
        by.setdefault(r["repo"], []).append(1 if r[key] else 0)
    groups = list(by.values())
    if not groups:
        return None, None
    rng = random.Random(seed)
    est = []
    for _ in range(B):
        s = [rng.choice(groups) for _ in groups]
        n = sum(len(g) for g in s)
        est.append(sum(map(sum, s)) / n if n else 0.0)
    est.sort()
    return est[int(0.025 * B)], est[int(0.975 * B) - 1]


def patches(art, model):
    rows = []
    for f in sorted(Path(art).rglob("COHORT_*.json")):
        r = json.loads(f.read_text())
        for a in (r.get("inner") or {}).get("attempts", []):
            if a.get("model") != model:
                continue
            d = a.get("draws") or {}
            rows.append({"name": r["name"], "repo": r["repo"].lower(), "status": a.get("status"),
                         "plausible": bool((a.get("labels") or {}).get("plausible")), "n": d.get("complete") or 0,
                         "theta": d.get("h_hat"), "by_source": d.get("by_source") or {}, "gates": {k: v for k, v in (a.get("gates") or {}).items() if k in GATES}})
    for r in rows:
        r["in_band"] = in_band_rate(r["theta"], r["n"])
    return rows


def primary(plaus, boot):
    k, n = sum(r["in_band"] for r in plaus), len(plaus)
    lo, hi = wilson(k, n)
    blo, bhi = cluster_boot(plaus, "in_band", boot)
    crit = next((c for c in range(n + 1) if binom_sf(c, n, 0.10) <= 0.05), None) if n else None
    return {"plausible": n, "in_band": k, "share": k / n if n else None, "wilson95": [lo, hi], "repo_cluster_boot95": [blo, bhi],
            "half_width": (hi - lo) / 2 if n else None, "P3_precision_met": bool(n and (hi - lo) / 2 <= 0.05),
            "H1_p_value": binom_sf(k, n, 0.10) if n else None, "H1_reject_at_0.05": bool(n and binom_sf(k, n, 0.10) <= 0.05), "H1_critical_count": crit}


def h3(plaus):
    acc = [r for r in plaus if r["theta"] is not None and r["theta"] < G.ETA]
    b = sum(1 for r in acc if r["gates"].get("fixed_sample") and not r["gates"].get("gatekeeper"))
    c = sum(1 for r in acc if r["gates"].get("gatekeeper") and not r["gates"].get("fixed_sample"))
    out = {"acceptable": len(acc), "fixed_sample_only": b, "gatekeeper_only": c, "discordant": b + c, "P4_met": b + c >= 11}
    if b + c:
        out["mcnemar_one_sided_p"] = binom_sf(b, b + c, 0.5)
    return out


def rq4(plaus):
    inad = [r for r in plaus if r["theta"] is not None and r["theta"] > G.ETA]
    zero = [r for r in plaus if r["theta"] == 0]
    out = {}
    for g in GATES:
        out[g] = {"admit_rate": sum(r["gates"].get(g, False) for r in plaus) / len(plaus) if plaus else None,
                  "admits_inadmissible": "%d/%d" % (sum(r["gates"].get(g, False) for r in inad), len(inad)),
                  "rejects_theta_zero": "%d/%d" % (sum(not r["gates"].get(g, False) for r in zero), len(zero))}
    return out


def by_weight(plaus, w):
    rows = []
    for r in plaus:
        s = r["by_source"]
        g0, g2 = s.get("G0", {}), s.get("G2", {})
        if not g0.get("complete") and not g2.get("complete"):
            continue
        t0 = g0["harm"] / g0["complete"] if g0.get("complete") else None
        t2 = g2["harm"] / g2["complete"] if g2.get("complete") else None
        if w == 0 and t0 is None or w == 1 and t2 is None:
            continue
        theta = t0 if w == 0 else t2 if w == 1 else (w * (t2 if t2 is not None else t0) + (1 - w) * (t0 if t0 is not None else t2))
        n = g0.get("complete", 0) if w == 0 else g2.get("complete", 0) if w == 1 else g0.get("complete", 0) + g2.get("complete", 0)
        rows.append(dict(r, in_band=in_band_rate(theta, n)))
    k = sum(x["in_band"] for x in rows)
    lo, hi = wilson(k, len(rows))
    return {"weight_G2": w, "patches": len(rows), "share": k / len(rows) if rows else None, "wilson95": [lo, hi]}


def main(argv):
    art, out = argv[0], Path(argv[1])
    opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
    boot = int(opt("--boot", 10000))
    dev = set()
    for i, a in enumerate(argv):
        if a == "--dev-repos":
            dev |= {c["repo"].lower() for c in json.loads(Path(argv[i + 1]).read_text())}
    streams = [json.loads(f.read_text()) for f in sorted(Path(art).rglob("STREAM_*.json"))]
    frame = json.loads(Path(opt("--frame", str(ROOT / "study_p/candidates_astar.json"))).read_text())
    funnel = {"frame": len(frame), "streamed": len(streams),
              "eligible": sum(1 for s in streams if s.get("vet_verdict") == "ELIGIBLE"),
              "usable": sum(1 for s in streams if s.get("stage_reached") == "P-GEN"),
              "generator_failures": sum(1 for s in streams if s.get("stage_reached") == "P-S3" and "generator" in str(s.get("fn_verdict", ""))),
              "stage_errors": sum(1 for s in streams if s.get("stage_reached") == "STAGE_ERROR"),
              "job_lost": len(frame) - len(streams)}            # amendment P-A3: candidates whose job left no record
    light = patches(art, LIGHT)
    plaus = [r for r in light if r["plausible"]]
    res = {"RQ1_funnel": funnel, "light_patches": len(light), "PRIMARY": primary(plaus, boot), "H3": h3(plaus), "RQ4": rq4(plaus),
           "sensitivity": {"without_development_repositories": primary([r for r in plaus if r["repo"] not in dev], boot) if dev else None,
                           "G2_weight": [by_weight(plaus, w) for w in (0, 0.5, 1)]}}
    strong = {r["name"]: r for r in patches(art, STRONG)}
    pairs = [(r["plausible"], strong[r["name"]]["plausible"]) for r in light if r["name"] in strong]
    res["exploratory_strong_model"] = {"paired_instances": len(pairs), "light_only": sum(1 for a, b in pairs if a and not b),
                                       "strong_only": sum(1 for a, b in pairs if b and not a),
                                       "primary_on_strong": primary([r for r in strong.values() if r["plausible"]], boot)}
    out.mkdir(parents=True, exist_ok=True)
    (out / "P_ANALYSIS.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res["PRIMARY"], indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
