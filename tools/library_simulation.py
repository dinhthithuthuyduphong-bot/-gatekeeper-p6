"""Library-level simulation (paper, Section 7, "Library-level control"): what actually runs when skills are admitted one by
one, versus with composite cells, the per-cell ledger and the execution rule.  Synthetic and labelled as such; no model calls.

python tools/library_simulation.py OUT_DIR [--reps 400] [--skills 12] [--regions 8] [--q 0.3] [--n 300] [--seed 11]

Model (one scope, theta = 0.1, alpha = 0.1):
  - each skill is beneficial (STR = -0.3) with probability 0.7, otherwise not admissible (STR = 0);
  - each skill touches one of `regions` code regions (its footprint); skills on the same region overlap;
  - a footprint-connected group of skills applied together is HARMFUL (STR = +0.5) if it contains a "bad pair" (each overlapping
    pair is bad with probability q, the construction of Theorem 5.5); otherwise risks add (Assumption 4 holds by construction);
  - disjoint groups add, so STR(E) of an executed set is the sum over its footprint-connected components;
  - paired trials give Y = -Z in {-1, +1} with mean -STR; the e-process is the implementation's betting e-process.
Policies:
  P1 per-skill admission (the draft): admit each skill with alpha/K, then run every admitted skill together;
  P2 this paper: same single-skill admissions from half of alpha; every footprint component of admitted skills with two or more
     skills is a composite cell tested with its ledger entry (fixed enumeration of subsets, alpha/2 * 6/(pi^2 j^2)); the executed
     set is gatekeeper_ext.execution.executable_subset over the admitted cells.
Reported per policy: probability that some executed footprint component is harmful (a defect in some code region, the primary
measure), probability that the executed set as a whole is harmful (STR > 0; harm can be masked by benefits elsewhere), mean number of beneficial skills executed, mean
trials.  Theorem 5.2 with Corollary 5.6 predicts at most alpha for P2; nothing bounds P1.
"""
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from gatekeeper_ext import execution as X  # noqa: E402
from theory_checks import FastBetting, wilson  # noqa: E402

THETA, ALPHA, BENEFIT, HARM = 0.1, 0.1, -0.3, 0.5


def test_cell(str_true, alpha_c, n, rng):
    """Run the betting e-process on n paired trials; True if it reaches 1/alpha_c. Returns (admitted, trials used)."""
    ep, p_up = FastBetting(THETA), (1 - str_true) / 2          # P(Y = +1) with E[Y] = -STR
    thr = 1 / alpha_c
    for i in range(1, n + 1):
        if ep.update(-(1.0 if rng.random() < p_up else -1.0)) >= thr:
            return True, i
    return False, n


def library(rng, k, regions, q):
    skills = ["s%02d" % i for i in range(k)]
    risk = {s: (BENEFIT if rng.random() < 0.7 else 0.0) for s in skills}
    fp = {s: ["region:%d" % rng.randrange(regions)] for s in skills}
    bad = set()
    for i, a in enumerate(skills):
        for b in skills[i + 1:]:
            if fp[a] == fp[b] and rng.random() < q:
                bad.add(frozenset((a, b)))
    return skills, risk, fp, bad


def graph_library(rng, lib, q):
    """Graph mode (Study R2): skills and footprints are one real target's measured library; benefit/harm stay synthetic.
    An overlapping pair (shared function) is bad with probability q."""
    skills = sorted(lib)
    risk = {s: (BENEFIT if rng.random() < 0.7 else 0.0) for s in skills}
    fp = {s: list(lib[s]) for s in skills}
    bad = set()
    for i, a in enumerate(skills):
        for b in skills[i + 1:]:
            if set(fp[a]) & set(fp[b]) and rng.random() < q:
                bad.add(frozenset((a, b)))
    return skills, risk, fp, bad


def group_str(group, risk, bad):
    g = sorted(group)
    if any(frozenset((a, b)) in bad for i, a in enumerate(g) for b in g[i + 1:]):
        return HARM
    return sum(risk[s] for s in g)


def executed_str(executed, risk, fp, bad):
    if not executed:
        return 0.0
    return sum(group_str(c, risk, bad) for c in X.components({s: fp[s] for s in executed}))


def subset_index(group, skills):
    """Fixed enumeration of all subsets (by bitmask) -> 1-based index; defined before any data."""
    return sum(1 << skills.index(s) for s in group)


def run(reps, k, regions, q, n, seed, graph=None):
    rng = random.Random(seed)
    stats = {p: {"harmful": 0, "harmful_component": 0, "beneficial_run": 0, "trials": 0} for p in ("P1", "P2")}
    libs_with_bad_pair = 0
    for rep_i in range(reps):
        if graph:
            skills, risk, fp, bad = graph_library(rng, graph[rep_i % len(graph)], q)
            k = len(skills)
        else:
            skills, risk, fp, bad = library(rng, k, regions, q)
        libs_with_bad_pair += bool(bad)
        # P1: per-skill admission with alpha / K, everything admitted runs together
        adm1, t1 = [], 0
        for s in skills:
            ok, used = test_cell(risk[s], ALPHA / k, n, rng)
            t1 += used
            if ok:
                adm1.append(s)
        e1 = adm1
        # P2: singles with (alpha/2)/K, composites from the ledger, execution rule
        adm2, t2 = [], 0
        for s in skills:
            ok, used = test_cell(risk[s], (ALPHA / 2) / k, n, rng)
            t2 += used
            if ok:
                adm2.append(s)
        admitted_cells = [frozenset([s]) for s in adm2]
        for comp in X.components({s: fp[s] for s in adm2}):
            if len(comp) < 2:
                continue
            j = subset_index(comp, skills)
            ok, used = test_cell(group_str(comp, risk, bad), (ALPHA / 2) * 6 / (math.pi ** 2 * j ** 2), n, rng)
            t2 += used
            if ok:
                admitted_cells.append(frozenset(comp))
        e2 = X.executable_subset({s: fp[s] for s in adm2}, admitted_cells)
        for name, ex, t in (("P1", e1, t1), ("P2", e2, t2)):
            st = stats[name]
            st["harmful"] += executed_str(ex, risk, fp, bad) > 0
            st["harmful_component"] += any(group_str(c, risk, bad) > 0 for c in X.components({s_: fp[s_] for s_ in ex})) if ex else False
            st["beneficial_run"] += sum(1 for s in ex if risk[s] < 0)
            st["trials"] += t
    out = {"model": {"skills": "per target (graph mode)" if graph else k, "regions": "measured footprints" if graph else regions, "bad_pair_prob": q, "trials_per_cell": n, "theta": THETA, "alpha": ALPHA,
                     "reps": reps, "seed": seed, "libraries_with_a_bad_pair": libs_with_bad_pair}}
    for name, st in stats.items():
        out[name] = {"harmful_component_rate": st["harmful_component"] / reps, "harmful_component_wilson95": wilson(st["harmful_component"], reps),
                     "harmful_execution_rate": st["harmful"] / reps, "wilson95": wilson(st["harmful"], reps),
                     "mean_beneficial_skills_executed": st["beneficial_run"] / reps, "mean_trials": st["trials"] / reps}
    out["P2_within_alpha"] = out["P2"]["harmful_component_rate"] <= ALPHA and out["P2"]["harmful_execution_rate"] <= ALPHA
    return out


def main(argv):
    opt = lambda key, d: type(d)(argv[argv.index(key) + 1]) if key in argv else d   # noqa: E731
    reps, k, regions, n, seed = opt("--reps", 400), opt("--skills", 12), opt("--regions", 8), opt("--n", 300), opt("--seed", 11)
    if "--graph" in argv:
        return main_graph(argv, reps, n, seed, opt("--q", 0.3))
    res = {"main": run(reps, k, regions, opt("--q", 0.3), n, seed),
           "sweep_bad_pair_prob": {str(q): run(reps, k, regions, q, n, seed) for q in (0.1, 0.5)}}
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    (out / "LIBRARY_SIMULATION.json").write_text(json.dumps(res, indent=1))
    for label, r in [("q=0.3", res["main"])] + [("q=" + q, r) for q, r in res["sweep_bad_pair_prob"].items()]:
        print(label, {p: (round(r[p]["harmful_component_rate"], 3), round(r[p]["mean_beneficial_skills_executed"], 2)) for p in ("P1", "P2")})
    return 0 if all(r["P2_within_alpha"] for r in [res["main"]] + list(res["sweep_bad_pair_prob"].values())) else 1


def main_graph(argv, reps, n, seed, q):
    """--graph CENSUS.json: one library per target with at least two cells, cycled over the repetitions."""
    census = json.loads(Path(argv[argv.index("--graph") + 1]).read_text())
    graph = [t["footprints"] for t in census["targets"] if not t.get("clone_error") and t.get("cells", 0) >= 2]
    if not graph:
        print("no target has two or more cells")
        return 1
    res = {"source": argv[argv.index("--graph") + 1], "libraries": len(graph),
           "library_sizes": sorted(len(g) for g in graph),
           "overlapping_pairs_per_library": sorted(sum(1 for i, a in enumerate(sorted(g)) for b in sorted(g)[i + 1:]
                                                       if set(g[a]) & set(g[b])) for g in graph),
           "main": run(reps, None, None, q, n, seed, graph),
           "sweep_bad_pair_prob": {str(x): run(reps, None, None, x, n, seed, graph) for x in (0.1, 0.5, 1.0)}}
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    (out / "LIBRARY_SIMULATION_GRAPH.json").write_text(json.dumps(res, indent=1))
    for label, r in [("q=%s" % q, res["main"])] + [("q=" + x, r) for x, r in res["sweep_bad_pair_prob"].items()]:
        print(label, {p: (round(r[p]["harmful_component_rate"], 3), round(r[p]["mean_beneficial_skills_executed"], 2)) for p in ("P1", "P2")})
    return 0 if all(r["P2_within_alpha"] for r in [res["main"]] + list(res["sweep_bad_pair_prob"].values())) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
