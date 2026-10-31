"""Study S (study_s/PROTOCOL.md): behaviour of real compositions on the functions Study R2 found touched by two families.
No model calls.

python tools/composition_study.py WORK_DIR OUT_DIR [--targets T1,T2] [--n 200]

Per unit (target, file, qualified function, family pair): snapshots O, A, B, AB, BA; G0 inputs generated on O; outcomes of
every snapshot on the same inputs; losses = outcome differs from O on a stable input; interaction measures; harm certificate
per cell and e-Holm over all cells.
"""
import ast
import itertools
import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import fn_probe as FP  # noqa: E402
from footprint_census import clone  # noqa: E402
from library_census import apply_all, load_skills  # noqa: E402
from gatekeeper_lite.eprocess import HarmAlarmEProcess, HarmCertEProcess, e_holm  # noqa: E402

CENSUS = ROOT / "research_closure/results/study_r2/LIBRARY_CENSUS.json"
ETA, ALPHA, ALPHA_ALARM, MIN_STABLE = 0.05, 0.1, 0.05, 50
VARIANTS = ("A", "B", "AB", "BA")
UNITS_ONLY = False   # --units-only: list the units (no function is run, no outcome is seen)
S_A1 = False         # --s-a1: amendment S-A1 (post hoc): receivers built from the constructor signature, mangled names,
#                      manifest Python version, install log recorded (study_s/AMENDMENTS.md)
S_A2 = False         # --s-a2: amendment S-A2 (S-A1 plus subtype substitution and a Python 3.11 install fallback)
S_A3 = False         # --s-a3: S-A2 plus every variant run twice; only inputs stable in O and every variant count
S_A3_FIXED_HASH = "--fixed-hash" in sys.argv   # for runs after S-A3; the reported S-A3 run did not fix it
INSTALL_LOG = {}


def inner(py, root, pp, rel, qualname, mode, calls, out, n, seed=0):
    """FP.inner (frozen) as registered; under S-A1 the same call through tools/composition_inner.py."""
    if not S_A1:
        return FP.inner(py, root, pp, rel, qualname, mode, calls, out, n, seed)
    args = {"root": str(root), "pythonpath": pp, "file": rel, "qualname": qualname, "mode": mode, "n": n, "seed": seed,
            "calls": str(calls), "out": str(out), "timeout": 2, "subtype": S_A2}
    ap = Path(str(out) + ".args.json")
    try:
        with FP.at_common_path(root) as common:
            args["root"] = str(common)
            ap.write_text(json.dumps(args))
            # fixed hash seed: S-A3 traced a non-replicated difference to per-process hash randomisation (study_s/AMENDMENTS.md)
            p = subprocess.run([str(py), str(ROOT / "tools" / "composition_inner.py"), str(ap)], capture_output=True, text=True,
                               timeout=120 + n * 2, env=dict(os.environ, PYTHONHASHSEED="0") if S_A3_FIXED_HASH else None)
    except subprocess.TimeoutExpired:
        return {"status": "PROCESS_TIMEOUT"}
    if not Path(out).exists():
        return {"status": "CRASHED", "tail": (p.stdout + p.stderr)[-400:]}
    return json.loads(Path(out).read_text())


# ------------------------------------------------------------------ units
def qualified_defs(src):
    """[(qualname, lineno, end_lineno)] of functions not nested in other functions."""
    out = []

    def walk(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, ast.ClassDef):
                walk(ch, prefix + ch.name + ".")
            elif isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append((prefix + ch.name, ch.lineno, ch.end_lineno))
    walk(ast.parse(src), "")
    return out


def site_lines(skill, src):
    try:
        r = skill.transform().apply(src, single_site=False)
    except Exception:  # noqa: BLE001 - abstain or parse problem: no sites
        return []
    return [s.lineno for s in r.sites]


def units_for_target(t, pairs, skills, root):
    """Units of the protocol: shared regions (1) and enabling pairs (2)."""
    out, seen = [], set()
    fp = t.get("footprints") or {}
    regions = {}
    for fam, regs in fp.items():
        for r in regs:
            regions.setdefault(r, set()).add(fam)
    cand = []
    for r, fams in sorted(regions.items()):
        if len(fams) < 2:
            continue
        rel, func = r.split("::", 1)
        for a, b in itertools.combinations(sorted(fams), 2):
            cand.append(("shared", rel, func, a, b))
    for p in pairs:
        if not p["commute"] or p["a_changes_b_sites"] or p["b_changes_a_sites"]:
            cand.append(("enabling", p["file"], None, p["a"], p["b"]))
    for kind, rel, func, a, b in cand:
        src = (root / rel).read_text(encoding="utf-8")
        la, lb = site_lines(skills[a], src), site_lines(skills[b], src)
        if kind == "enabling":   # functions where one family's sites change after the other is applied
            after_a, after_b = apply_all(skills[a], src)[0], apply_all(skills[b], src)[0]
            lb2, la2 = site_lines(skills[b], after_a), site_lines(skills[a], after_b)
            defs_new = qualified_defs(after_a) + qualified_defs(after_b)
            names = {q for q, s, e in defs_new
                     if sum(s <= x <= e for x in lb2) != sum(s <= x <= e for x in lb) or
                     sum(s <= x <= e for x in la2) != sum(s <= x <= e for x in la)}
            quals = sorted(names)
        else:
            quals = [q for q, s, e in qualified_defs(src) if q.split(".")[-1] == func
                     and any(s <= x <= e for x in la) and any(s <= x <= e for x in lb)]
            if func == "<module>":
                out.append({"kind": kind, "file": rel, "qualname": "<module>", "a": a, "b": b,
                            "usable": False, "why": "module-level region: no function to call"})
                continue
        for q in quals:
            key = (rel, q, a, b)
            if key not in seen:
                seen.add(key)
                out.append({"kind": kind, "file": rel, "qualname": q, "a": a, "b": b})
    return out


# ------------------------------------------------------------------ snapshots and environment
def variant_source(skills, a, b, src, v):
    if v == "A":
        return apply_all(skills[a], src)[0]
    if v == "B":
        return apply_all(skills[b], src)[0]
    if v == "AB":
        return apply_all(skills[b], apply_all(skills[a], src)[0])[0]
    return apply_all(skills[a], apply_all(skills[b], src)[0])[0]


def make_env(work, root, manifest):
    env_dir = work / "venv"
    base = shutil.which("python%s" % manifest.get("python", "")) if S_A1 else None
    if not env_dir.exists():
        if base:
            subprocess.run([base, "-m", "venv", str(env_dir)], check=True)
        else:
            venv.create(env_dir, with_pip=True)
    py = env_dir / "bin" / "python"
    kind, _, pkg = (manifest.get("install") or "").partition(":")
    log = {"python": base or sys.executable}
    if kind == "self-then-uninstall":
        e = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        r = subprocess.run([str(py), "-m", "pip", "install", "-q", str(root)], env=e, capture_output=True, text=True, timeout=1800)
        log.update(install_rc=r.returncode, install_tail=(r.stderr or r.stdout)[-600:])
        subprocess.run([str(py), "-m", "pip", "uninstall", "-y", "-q", pkg], capture_output=True, timeout=600)
    if S_A2 and log.get("install_rc") and shutil.which("python3.11") and manifest.get("python") != "3.11":
        env2 = work / "venv311"
        subprocess.run([shutil.which("python3.11"), "-m", "venv", str(env2)], check=True)
        py2 = env2 / "bin" / "python"
        r = subprocess.run([str(py2), "-m", "pip", "install", "-q", str(root)], env=e, capture_output=True, text=True, timeout=1800)
        log["fallback_311"] = {"install_rc": r.returncode, "install_tail": (r.stderr or r.stdout)[-600:]}
        if r.returncode == 0:
            subprocess.run([str(py2), "-m", "pip", "uninstall", "-y", "-q", pkg], capture_output=True, timeout=600)
            py = py2
    INSTALL_LOG[str(root)] = log
    return py


# ------------------------------------------------------------------ measures
def losses(o1, o2, runs):
    """Stable input indices and, per variant, the 0/1 loss (differs from O) on each stable input."""
    a, b = o1["outcomes"], o2["outcomes"]
    n = min([len(a), len(b)] + [len(r["outcomes"]) for r in runs.values()])
    stable = [i for i in range(n) if a[i] == b[i] and a[i] != ["timeout"]]
    return stable, {v: [int(r["outcomes"][i] != a[i]) for i in stable] for v, r in runs.items()}


def interaction(L, runs, stable):
    la, lb, lab, lba = L["A"], L["B"], L["AB"], L["BA"]
    n = len(stable)
    emergent = sum(1 for i in range(n) if (lab[i] or lba[i]) and not la[i] and not lb[i])
    masking = sum(1 for i in range(n) if (la[i] or lb[i]) and not (lab[i] and lba[i]))
    order = sum(1 for k, i in enumerate(stable) if runs["AB"]["outcomes"][i] != runs["BA"]["outcomes"][i])
    nonadd = sum(1 for i in range(n) if lab[i] != min(1, la[i] + lb[i]) or lba[i] != min(1, la[i] + lb[i]))
    return {"emergent": emergent, "masking": masking, "order_dependent": order, "non_additive": nonadd}


def harm_e(loss_seq):
    cert, alarm, fired = HarmCertEProcess(ETA), HarmAlarmEProcess(ETA), False
    for x in loss_seq:
        cert.update(bool(x))
        alarm.update(bool(x))
        fired = fired or alarm.value >= 1 / ALPHA_ALARM
    return (0.0 if fired else cert.value), fired


# ------------------------------------------------------------------ driver
def run_target(t, pairs, skills, work, n):
    manifest = json.loads((ROOT / ("study_%s" % t["study"].lower()) / "eval_targets" / t["target"] / "gk_target.json").read_text())
    root = work / "repo"
    err = clone(manifest, root)
    if err:
        return {"target": t["target"], "error": "clone: %s" % err, "units": []}
    units = units_for_target(t, pairs, skills, root)
    if UNITS_ONLY or not any("usable" not in u for u in units):
        return {"target": t["target"], "units": units}
    py = make_env(work, root, manifest)
    pp = manifest.get("pythonpath", [])
    for k, u in enumerate(units):
        if "usable" in u:
            continue
        src = (root / u["file"]).read_text(encoding="utf-8")
        tag = "u%02d" % k
        calls = work / (tag + ".calls.json")
        gen = inner(py, root, pp, u["file"], u["qualname"], "generate", calls, work / (tag + ".gen.json"), n, 0)
        if gen.get("status") != "GENERATED":
            u.update(usable=False, why="did not run: %s %s" % (gen.get("status"), str(gen.get("reason") or gen.get("tail") or "")[:200]))
            continue
        o1 = inner(py, root, pp, u["file"], u["qualname"], "run", calls, work / (tag + ".o1.json"), n)
        o2 = inner(py, root, pp, u["file"], u["qualname"], "run", calls, work / (tag + ".o2.json"), n)
        runs, rep2 = {}, {}
        for v in VARIANTS:
            snap = work / ("snap_" + v)
            if snap.exists():
                shutil.rmtree(snap)
            shutil.copytree(root, snap, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            (snap / u["file"]).write_text(variant_source(skills, u["a"], u["b"], src, v), encoding="utf-8")
            runs[v] = inner(py, snap, pp, u["file"], u["qualname"], "run", calls, work / ("%s.%s.json" % (tag, v)), n)
            if S_A3:
                rep2[v] = inner(py, snap, pp, u["file"], u["qualname"], "run", calls, work / ("%s.%s.r2.json" % (tag, v)), n)
            shutil.rmtree(snap)
        bad = [x for x in [o1, o2] + list(runs.values()) + list(rep2.values()) if x.get("status") != "RAN"]
        if bad:
            u.update(usable=False, why="did not run: %s" % bad[0].get("status"))
            continue
        stable, L = losses(o1, o2, runs)
        if S_A3:   # keep only inputs on which every variant repeats its own outcome
            keep = [k for k, i in enumerate(stable) if all(runs[v]["outcomes"][i] == rep2[v]["outcomes"][i] for v in VARIANTS)]
            u["variant_unstable_inputs"] = len(stable) - len(keep)
            stable = [stable[k] for k in keep]
            L = {v: [L[v][k] for k in keep] for v in VARIANTS}
        if len(stable) < MIN_STABLE:
            u.update(usable=False, why="only %d stable inputs" % len(stable))
            continue
        u.update(usable=True, stable=len(stable), d={v: sum(L[v]) / len(stable) for v in VARIANTS},
                 counts={v: sum(L[v]) for v in VARIANTS}, **interaction(L, runs, stable),
                 examples=[{"input": i, "O": o1["outcomes"][i], **{v: runs[v]["outcomes"][i] for v in VARIANTS}}
                           for i in stable if runs["AB"]["outcomes"][i] != o1["outcomes"][i]
                           or runs["BA"]["outcomes"][i] != o1["outcomes"][i]][:3])
        u["losses"] = L
    return {"target": t["target"], "units": units, "install": INSTALL_LOG.get(str(root))}


def summarise(targets):
    units = [dict(u, target=t["target"]) for t in targets for u in t["units"]]
    ok = [u for u in units if u.get("usable")]
    evals = {}
    for k, u in enumerate(ok):
        u["cells"] = {}
        for v in VARIANTS:
            e, fired = harm_e(u["losses"][v])
            evals["%d:%s" % (k, v)] = e
            u["cells"][v] = {"e": e, "alarm": fired}
    adm = set(e_holm(evals, ALPHA))
    for k, u in enumerate(ok):
        for v in VARIANTS:
            u["cells"][v]["admitted"] = "%d:%s" % (k, v) in adm
        singles = u["cells"]["A"]["admitted"] and u["cells"]["B"]["admitted"]
        comps = u["cells"]["AB"]["admitted"] and u["cells"]["BA"]["admitted"]
        u["singles_admitted_composite_not"] = singles and not comps
        u["composite_admitted_single_not"] = comps and not singles
        del u["losses"]
    tot = {"units": len(units), "usable": len(ok),
           "unusable_reasons": sorted({u.get("why", "") for u in units if not u.get("usable")}),
           "units_any_behaviour_change": sum(1 for u in ok if any(u["counts"][v] for v in VARIANTS)),
           "units_emergent": sum(1 for u in ok if u["emergent"]), "units_masking": sum(1 for u in ok if u["masking"]),
           "units_order_dependent": sum(1 for u in ok if u["order_dependent"]),
           "units_non_additive": sum(1 for u in ok if u["non_additive"]),
           "cells": len(evals), "cells_admitted": len(adm),
           "variant_unstable_inputs": sum(u.get("variant_unstable_inputs", 0) for u in ok),
           "units_singles_admitted_composite_not": sum(1 for u in ok if u["singles_admitted_composite_not"]),
           "units_composite_admitted_single_not": sum(1 for u in ok if u["composite_admitted_single_not"])}
    return {"total": tot, "units": units}


def main(argv):
    work, out = Path(argv[0]), Path(argv[1])
    opt = lambda k, d: type(d)(argv[argv.index(k) + 1]) if k in argv else d   # noqa: E731
    n = opt("--n", 200)
    global UNITS_ONLY, S_A1, S_A2, S_A3
    UNITS_ONLY = "--units-only" in argv
    S_A3 = "--s-a3" in argv
    S_A2 = "--s-a2" in argv or S_A3
    S_A1 = "--s-a1" in argv or S_A2
    census = json.loads(CENSUS.read_text())
    only = set(opt("--targets", "").split(",")) - {""}
    edge_targets = {k for k, v in census["with_enabling_edges"]["targets"].items() if v["edges"]}
    skills = load_skills()
    res = []
    for t in census["targets"]:
        if t.get("clone_error") or (only and t["target"] not in only):
            continue
        shared = any(sum(1 for v in t["footprints"].values() if r in v) > 1 for regs in t["footprints"].values() for r in regs)
        if not shared and t["target"] not in edge_targets:
            continue
        pairs = [p for p in census["pairs"] if p["target"] == t["target"]]
        w = work / t["target"]
        w.mkdir(parents=True, exist_ok=True)
        print("target", t["target"], flush=True)
        res.append(run_target(t, pairs, skills, w, n))
    if UNITS_ONLY:
        for r in res:
            for u in r["units"]:
                print(r["target"], u["kind"], u["file"], u["qualname"], u["a"], u["b"], u.get("why", ""))
        return 0
    summary = summarise(res)
    summary["install"] = {r["target"]: r.get("install") for r in res}
    out.mkdir(parents=True, exist_ok=True)
    name = "COMPOSITION_STUDY_SA3.json" if S_A3 else "COMPOSITION_STUDY_SA2.json" if S_A2 else "COMPOSITION_STUDY_SA1.json" if S_A1 else "COMPOSITION_STUDY.json"
    (out / name).write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps(summary["total"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
