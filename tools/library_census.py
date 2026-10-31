"""Study R2 (study_r2/PROTOCOL.md): census of a twelve-family skill library on the 16 real targets.  No model calls; no target
code runs.

python tools/library_census.py WORK_DIR OUT_DIR [--targets d,e,g]

Per target: the families that bind (single-skill cells), functions touched per family, overlapping family pairs, footprint
components and the composite cells the execution rule requires.  Per file and ordered family pair applying to it: whether the
two rewrites commute (A then B == B then A) and whether A changes B's sites.
"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from footprint_census import clone, is_test  # noqa: E402
from gatekeeper_ext import execution as X  # noqa: E402
from gatekeeper_ext.skill_library import register_all  # noqa: E402
from gatekeeper_lite import transforms  # noqa: E402
from gatekeeper_lite.skill import Skill  # noqa: E402

register_all()
SKILL_FILES = {"negative_type_guard": ROOT / "study_d/skills/bool-excluded-from-int.json",
               "none_identity": ROOT / "study_g/skills/none-identity.json"}
SKILL_FILES.update({p.stem.replace("-", "_"): p for p in sorted((ROOT / "study_r2/skills").glob("*.json"))})


def load_skills():
    return {k: Skill.load(v) for k, v in SKILL_FILES.items()}


def apply_all(skill, src):
    """(new_source, sites as a sorted tuple of (function, snippet)) or (src, ()) when the skill abstains everywhere."""
    try:
        r = skill.transform().apply(src, single_site=False)
    except transforms.Abstain:
        return src, ()
    return r.source, tuple(sorted((s.function, s.snippet) for s in r.sites))


def _count(sites):
    return sorted(Counter(f for f, _ in sites).items())


def file_pairs(skills, src):
    """Per family: sites on src.  Per ordered pair of families both applying: commute? does A change B's sites?"""
    base = {k: apply_all(sk, src) for k, sk in skills.items()}
    live = [k for k, (_, s) in base.items() if s]
    pairs = []
    for a, b in itertools.combinations(live, 2):
        ab = apply_all(skills[b], base[a][0])
        ba = apply_all(skills[a], base[b][0])
        pairs.append({"a": a, "b": b,
                      "shared_function": bool({f for f, _ in base[a][1]} & {f for f, _ in base[b][1]} - {"<module>"}),
                      "commute": ab[0] == ba[0],
                      # enables/disables: the number of sites per function changes; nested: same sites, but one edit lies
                      # inside the other's span (the site text changes)
                      "a_changes_b_sites": _count(ab[1]) != _count(base[b][1]), "b_changes_a_sites": _count(ba[1]) != _count(base[a][1]),
                      "nested": (ab[1] != base[b][1] or ba[1] != base[a][1])
                      and _count(ab[1]) == _count(base[b][1]) and _count(ba[1]) == _count(base[a][1])})
    return {k: base[k][1] for k in live}, pairs


def scan(root, skills):
    funcs = {k: set() for k in skills}
    pairs, scanned, skipped = [], 0, 0
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        if ".git/" in rel or is_test(rel):
            continue
        try:
            src = p.read_text(encoding="utf-8")
            sites, fp = file_pairs(skills, src)
        except (UnicodeDecodeError, OSError, SyntaxError, ValueError, RecursionError):
            skipped += 1
            continue
        scanned += 1
        for k, ss in sites.items():
            funcs[k] |= {(rel, f) for f, _ in ss}
        pairs += [dict(x, file=rel) for x in fp]
    return funcs, pairs, scanned, skipped


def summarise_target(funcs):
    """Cells, overlapping pairs and footprint components of one target's library (footprint = set of (file, function))."""
    lib = {k: sorted("%s::%s" % t for t in v if t[1] != "<module>") for k, v in funcs.items() if v}
    overl = [[a, b] for a, b in itertools.combinations(sorted(lib), 2) if set(lib[a]) & set(lib[b])]
    comps = [sorted(c) for c in X.components({k: v for k, v in lib.items()})]
    return {"cells": len(lib), "families": sorted(lib), "functions": {k: len(funcs[k]) for k in funcs if funcs[k]},
            "overlapping_pairs": overl, "components": comps,
            "composite_cells_required": sum(1 for c in comps if len(c) > 1),
            "largest_component": max((len(c) for c in comps), default=0), "footprints": lib}


def enabling_edges(pairs):
    """Family pairs that do not commute or where one changes the other's sites, on any file of the target."""
    return sorted({tuple(sorted((p["a"], p["b"]))) for p in pairs
                   if not p["commute"] or p["a_changes_b_sites"] or p["b_changes_a_sites"]})


def dynamic(res):
    """Execution rule with enabling edges (gatekeeper_ext.execution, edges=): components and composite cells per target,
    derived from the census' own measures 2 and 3 (no re-scan)."""
    out, tot = {}, {"composite_cells_required": 0, "targets_changed": 0, "largest_component": 0, "missed_by_static": []}
    for t in res["targets"]:
        if t.get("clone_error"):
            continue
        edges = enabling_edges([p for p in res["pairs"] if p["target"] == t["target"]])
        comps = [sorted(c) for c in X.components(t["footprints"], edges)]
        missed = [list(e) for e in edges if not any(set(e) <= set(c) for c in t["components"])]
        row = {"edges": [list(e) for e in edges], "components": comps, "composite_cells_required": sum(1 for c in comps if len(c) > 1),
               "largest_component": max((len(c) for c in comps), default=0), "edges_missed_by_static_rule": missed}
        out[t["target"]] = row
        tot["composite_cells_required"] += row["composite_cells_required"]
        tot["targets_changed"] += comps != t["components"]
        tot["largest_component"] = max(tot["largest_component"], row["largest_component"])
        tot["missed_by_static"] += [[t["target"]] + e for e in missed]
    return {"total": tot, "targets": out}


def census(work, targets):
    skills = load_skills()
    rows, all_pairs = [], []
    for study in targets:
        for tdir in sorted((ROOT / ("study_%s" % study) / "eval_targets").iterdir()):
            mf = tdir / "gk_target.json"
            if not mf.is_file():
                continue
            manifest = json.loads(mf.read_text())
            dest = Path(work) / ("%s_%s" % (study, tdir.name))
            err = clone(manifest, dest)
            row = {"study": study.upper(), "target": tdir.name, "repository": manifest.get("repository"), "clone_error": err}
            if not err:
                funcs, pairs, scanned, skipped = scan(dest, skills)
                row.update(files_scanned=scanned, files_skipped=skipped, **summarise_target(funcs))
                all_pairs += [dict(p, target=tdir.name) for p in pairs]
            rows.append(row)
    ok = [r for r in rows if not r["clone_error"]]
    fam_targets = Counter(f for r in ok for f in r["families"])
    poss = sum(r["cells"] * (r["cells"] - 1) // 2 for r in ok)

    def inter(sel):
        return {"file_pairs": len(sel), "non_commuting": sum(not p["commute"] for p in sel),
                "site_changing": sum(p["a_changes_b_sites"] or p["b_changes_a_sites"] for p in sel),
                "nested_only": sum(p["nested"] for p in sel)}
    total = {"targets": len(rows), "cloned": len(ok), "families": len(skills), "files_scanned": sum(r["files_scanned"] for r in ok),
             "cells": sum(r["cells"] for r in ok), "mean_cells_per_target": round(sum(r["cells"] for r in ok) / max(1, len(ok)), 2),
             "family_pairs_possible": poss, "family_pairs_overlapping": sum(len(r["overlapping_pairs"]) for r in ok),
             "composite_cells_required": sum(r["composite_cells_required"] for r in ok),
             "largest_component": max((r["largest_component"] for r in ok), default=0),
             "functions_touched": sum(len(set().union(*[set(v) for v in r["footprints"].values()])) if r["footprints"] else 0 for r in ok),
             "functions_touched_by_two_or_more": sum(sum(1 for c in Counter(f for v in r["footprints"].values() for f in v).values() if c > 1) for r in ok),
             "families_binding_on_targets": dict(sorted(fam_targets.items())),
             "families_binding_nowhere": sorted(set(skills) - set(fam_targets)),
             "interaction_shared_function": inter([p for p in all_pairs if p["shared_function"]]),
             "interaction_disjoint_functions": inter([p for p in all_pairs if not p["shared_function"]]),
             "non_commuting_family_pairs": sorted({"%s+%s" % (p["a"], p["b"]) for p in all_pairs if not p["commute"]}),
             "site_changing_family_pairs": sorted({"%s+%s" % (p["a"], p["b"]) for p in all_pairs
                                                   if p["a_changes_b_sites"] or p["b_changes_a_sites"]})}
    res = {"total": total, "targets": rows, "pairs": all_pairs}
    res["with_enabling_edges"] = dynamic(res)
    return res


def main(argv):
    if argv and argv[0] == "--dynamic":   # recompute the enabling-edge analysis on a committed census (no re-scan)
        res = json.loads(Path(argv[1]).read_text())
        res["with_enabling_edges"] = dynamic(res)
        Path(argv[1]).write_text(json.dumps(res, indent=1, default=list))
        print(json.dumps(res["with_enabling_edges"]["total"], indent=1))
        return 0
    work, out = Path(argv[0]), Path(argv[1])
    targets = (argv[argv.index("--targets") + 1] if "--targets" in argv else "d,e,g").split(",")
    work.mkdir(parents=True, exist_ok=True)
    res = census(work, targets)
    out.mkdir(parents=True, exist_ok=True)
    (out / "LIBRARY_CENSUS.json").write_text(json.dumps(res, indent=1, default=list))
    print(json.dumps(res["total"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
