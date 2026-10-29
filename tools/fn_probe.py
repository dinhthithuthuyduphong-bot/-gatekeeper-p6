"""Study P feasibility (development, 0 cost): can the edited function of a real bug-fix PR be called directly with
generated inputs, and does the original differ from the upstream fix on some of them?

python tools/fn_probe.py ELIGIBLE.json NAME OUT_DIR [N_INPUTS=200] [MAX_FUNCS=3]

Per instance: rebuild the two snapshots from the recorded SHAs, provision one virtual environment (version-2.1 rules),
list the functions edited by the fix that exist in both versions, and for at most MAX_FUNCS of them: generate inputs once
from the ORIGINAL, run the original twice (stability) and the fix once, each in a fresh process.  Writes FNPROBE_<name>.json.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
MIN_STABLE = 100


def inner(py, root, pythonpath, rel, qualname, mode, calls, out, n=200, seed=0, per_call=2, env=None):
    args = {"root": str(root), "pythonpath": pythonpath, "file": rel, "qualname": qualname, "mode": mode, "n": n, "seed": seed,
            "calls": str(calls), "out": str(out), "timeout": per_call}
    ap = Path(str(out) + ".args.json")
    ap.write_text(json.dumps(args))
    try:
        p = subprocess.run([str(py), str(ROOT / "tools" / "fn_probe_inner.py"), str(ap)], env=env, capture_output=True, text=True,
                           timeout=60 + n * per_call)
    except subprocess.TimeoutExpired:
        return {"status": "PROCESS_TIMEOUT"}
    if not Path(out).exists():
        return {"status": "CRASHED", "tail": (p.stdout + p.stderr)[-400:]}
    return json.loads(Path(out).read_text())


def compare(o1, o2, g):
    """Per-function verdict from three runs: original twice, fix once."""
    if o1.get("status") != "RAN" or o2.get("status") != "RAN" or g.get("status") != "RAN":
        bad = next(r for r in (o1, o2, g) if r.get("status") != "RAN")
        return {"usable": False, "why": "did not run: %s %s" % (bad.get("status"), bad.get("reason") or bad.get("tail") or "")}
    a, b, c = o1["outcomes"], o2["outcomes"], g["outcomes"]
    stable = [i for i in range(min(len(a), len(b), len(c))) if a[i] == b[i] and a[i] != ["timeout"]]
    diverge = [i for i in stable if a[i] != c[i]]
    exc_both = sum(1 for i in stable if a[i][0] == "exc" and c[i][0] == "exc")
    out = {"inputs": len(a), "stable": len(stable), "divergent": len(diverge), "trigger_rate": len(diverge) / len(stable) if stable else 0.0,
           "both_raise": exc_both, "examples": [{"orig": a[i], "fix": c[i]} for i in diverge[:3]]}
    if len(stable) < MIN_STABLE:
        out.update(usable=False, why="only %d stable inputs" % len(stable))
    elif not diverge:
        out.update(usable=False, why="the original never differs from the fix on generated inputs")
    else:
        out.update(usable=True, why="usable")
    return out


def instance_verdict(funcs, prep_error=None, n_edited=None):
    if prep_error:
        return "snapshots or environment failed"
    if not n_edited:
        return "no edited function present in both versions"
    if any(f.get("usable") for f in funcs):
        return "usable"
    whys = [f.get("why", "") for f in funcs]
    if all(w.startswith("did not run") for w in whys):
        return "no edited function could be imported or called"
    if any("stable inputs" in w for w in whys) and not any("never differs" in w for w in whys):
        return "unstable outcomes"
    return "the original never differs from the fix on generated inputs"


def probe_roots(py, orig, gold, modules, pythonpath, work, n=200, max_funcs=3, env=None):
    from gatekeeper_ext import testmut as T
    edited = T.edited_with_lines(orig, gold, modules)
    funcs = []
    for e in sorted(edited, key=lambda e: (e["file"], e["qualname"]))[:max_funcs]:
        tag = "%s__%s" % (e["file"].replace("/", "_"), e["qualname"])
        calls = Path(work) / (tag + ".calls.json")
        gen = inner(py, orig, pythonpath, e["file"], e["qualname"], "generate", calls, Path(work) / (tag + ".gen.json"), n, 0, env=env)
        rec = {"file": e["file"], "qualname": e["qualname"]}
        if gen.get("status") != "GENERATED":
            rec.update(usable=False, why="did not run: %s %s" % (gen.get("status"), gen.get("reason") or gen.get("tail") or ""))
        else:
            o1 = inner(py, orig, pythonpath, e["file"], e["qualname"], "run", calls, Path(work) / (tag + ".o1.json"), n, env=env)
            o2 = inner(py, orig, pythonpath, e["file"], e["qualname"], "run", calls, Path(work) / (tag + ".o2.json"), n, env=env)
            g = inner(py, gold, pythonpath, e["file"], e["qualname"], "run", calls, Path(work) / (tag + ".g.json"), n, env=env)
            rec.update(compare(o1, o2, g))
        funcs.append(rec)
    return {"edited_functions": len(edited), "functions": funcs, "verdict": instance_verdict(funcs, None, len(edited))}


def prepare(rec, work):
    """Rebuild the two snapshots from the recorded SHAs and provision one environment (version-2.1 rules)."""
    import n_s3_check as N                                       # frozen helpers: plan rules
    import vet_target as V
    import vet_target2 as T2
    modules, census, pythonpath, tests = N.instance_plan(rec)
    repo = work / "repo"
    repo.mkdir()
    V.sh([*V.GIT, "init", "-q"], cwd=repo)
    V.sh([*V.GIT, "remote", "add", "origin", rec["repo"]], cwd=repo)
    V.sh([*V.GIT, "fetch", "-q", "--filter=blob:none", "origin", rec["pre"], rec["gold"]], cwd=repo, timeout=900)
    orig, gold = work / "orig", work / "gold"
    V.checkout_to(repo, rec["pre"], orig)
    V.checkout_to(repo, rec["gold"], gold)
    venv.EnvBuilder(with_pip=True).create(work / "venv")
    py = work / "venv" / "bin" / "python"
    log, repairs = [], []
    T2.provision(py, orig, ["test", "dev"], log)
    T2.repair({"pre": (py, orig), "gold": (py, gold)}, tests, repairs)
    env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
    return {"py": py, "orig": orig, "gold": gold, "repo": repo, "modules": modules, "pythonpath": pythonpath, "env": env}


def main(eligible_path, name, out_dir, n=200, max_funcs=3):
    rec = next(r for r in json.loads(Path(eligible_path).read_text()) if r["name"] == name)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="fnp_"))
    report = {"name": name, "repo": rec["repo"], "status": "started"}
    try:
        p = prepare(rec, work)
        (work / "probe").mkdir()
        report.update(probe_roots(p["py"], p["orig"], p["gold"], p["modules"], p["pythonpath"], work / "probe", int(n), int(max_funcs), p["env"]), status="FINISHED")
    except Exception as exc:
        report.update(status="ERROR", error=("%s: %s" % (type(exc).__name__, exc))[:400], verdict="snapshots or environment failed")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / ("FNPROBE_%s.json" % name)).write_text(json.dumps(report, indent=1, default=str))
    print(json.dumps({k: report.get(k) for k in ("name", "status", "verdict")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:6]))
