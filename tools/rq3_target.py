"""RQ3 for one evaluation target of Studies D, E, G: do AUTOMATIC input generators detect the same behaviour change of a
learned skill as the target's HAND-WRITTEN oracle?  Plan: research_closure/results/RQ3_PLAN.md (committed before the run).

python tools/rq3_target.py STUDY TARGET_ID OUT_DIR [--target-python PY] [--models MODELS.json --cap USD] [--n 200]

The two snapshots are exactly the pair measured by the original study: the target at its recorded commit, and the same
target with the skill applied (gatekeeper_lite.gatekeeper.bind_modules).  Three generators measure, on each pair:
  hand  the oracle's scopes() through its execute() (original twice for stability, treated once)
  G0    signature-driven inputs on the functions the skill edits (tools/fn_probe.py)
  G2    a model-written make_inputs on the same functions (tools/fn_probe_llm.py), only with --models
All snapshots run at one common path.  Writes RQ3_<target>.json.
"""
import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def hand_runs(py, root, pythonpath, oracle, work, tag, n, seed, env):
    import fn_probe as FP
    out = Path(work) / ("hand_%s.json" % tag)
    args = {"pythonpath": pythonpath, "oracle": str(oracle), "n": n, "seed": seed, "out": str(out), "timeout": 5}
    ap = Path(work) / ("hand_%s.args.json" % tag)
    try:
        with FP.at_common_path(root) as common:
            args["root"] = str(common)
            ap.write_text(json.dumps(args))
            p = subprocess.run([str(py), str(ROOT / "tools" / "rq3_oracle_inner.py"), str(ap)], env=env, capture_output=True, text=True, timeout=120 + 10 * n)
    except subprocess.TimeoutExpired:
        return {"status": "PROCESS_TIMEOUT"}
    return json.loads(out.read_text()) if out.exists() else {"status": "CRASHED", "tail": (p.stdout + p.stderr)[-400:]}


def compare_hand(o1, o2, t):
    if any(r.get("status") != "RAN" for r in (o1, o2, t)):
        return {"ran": False, "why": [r.get("status") for r in (o1, o2, t)]}
    scopes = {}
    for s in o1["scopes"]:
        a, b, c = o1["scopes"][s], o2["scopes"].get(s, []), t["scopes"].get(s, [])
        stable = [i for i in range(min(len(a), len(b), len(c))) if a[i] == b[i] and a[i] != "timeout"]
        div = [i for i in stable if a[i] != c[i]]
        scopes[s] = {"stable": len(stable), "divergent": len(div), "rate": len(div) / len(stable) if stable else None}
    return {"ran": True, "scopes": scopes, "detects": any(v["divergent"] > 0 for v in scopes.values())}


def install(py, root, manifest):
    kind, _, pkg = manifest.get("install", "").partition(":")
    if kind == "self-then-uninstall":
        env = dict(os.environ, SETUPTOOLS_SCM_PRETEND_VERSION="0.0.0")
        subprocess.run([str(py), "-m", "pip", "install", "-q", str(root)], check=False, env=env)
        subprocess.run([str(py), "-m", "pip", "uninstall", "-y", "-q", pkg], check=False)
    if manifest.get("census_requirements"):
        subprocess.run([str(py), "-m", "pip", "install", "-q", *manifest["census_requirements"]], check=False)


def skill_text(skill_json):
    d = json.loads(Path(skill_json).read_text())
    return "A learned code transformation '%s' (scope: %s; transform: %s) was applied to this function." % (d.get("skill_id"), d.get("scope"), d.get("pi"))


def register_extensions():
    """Studies G and H use the extension transform 'none_identity', registered at run time exactly as
    tools/run_study_g.py does; without it their skill cannot be loaded."""
    from gatekeeper_ext.none_identity import register
    register()


def run(study, tid, out_dir, py=sys.executable, models=None, cap=0.5, n=200, client=None, seed=7):
    register_extensions()
    from gatekeeper_lite.gatekeeper import bind_modules
    from gatekeeper_lite.skill import Skill, Target
    import fn_probe as FP
    base = ROOT / study
    manifest = json.loads((base / "eval_targets" / tid / "gk_target.json").read_text())
    cfg = json.loads(next(base.glob("config_*.json")).read_text())
    skill_path = base / manifest.get("skill", cfg.get("skill"))
    work = Path(tempfile.mkdtemp(prefix="rq3_"))
    rec = {"study": study, "target": tid, "python": manifest.get("python"), "skill": json.loads(skill_path.read_text()).get("skill_id"), "status": "started"}
    try:
        root = work / "src"
        if "local" in manifest["checkout"]:
            shutil.copytree(ROOT / manifest["checkout"]["local"], root)
        else:
            from fetch_real_targets import _clone_ref
            rec["commit"] = _clone_ref(manifest["checkout"]["repo"], manifest["checkout"]["ref"], root)
            shutil.rmtree(root / ".git", ignore_errors=True)
        (root / "gk_target.json").write_text(json.dumps(manifest))
        bound = bind_modules([Skill.load(skill_path)], Target.load(root))
        rec["sites"] = bound["sites"]
        if not bound["treated"]:
            rec.update(status="OUT_OF_SCOPE")
            return rec
        install(py, root, manifest)
        orig, treated = work / "orig", work / "treated"
        shutil.copytree(root, orig)
        shutil.copytree(root, treated)
        for rel, src in bound["treated"].items():
            (treated / rel).write_text(src, encoding="utf-8")
        pp = manifest.get("pythonpath", [])
        env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
        oracle = base / manifest["draw_oracle"]
        (work / "w").mkdir()
        h = [hand_runs(py, d, pp, oracle, work / "w", tag, n, seed, env) for d, tag in ((orig, "o1"), (orig, "o2"), (treated, "t"))]
        rec["hand"] = compare_hand(*h)
        modules = sorted(bound["treated"])
        g0 = FP.probe_roots(py, orig, treated, modules, pp, work / "w", n, 3, env)
        rec["G0"] = {"verdict": g0["verdict"], "functions": [{k: f.get(k) for k in ("file", "qualname", "stable", "divergent", "why")} for f in g0["functions"]]}
        rec["G0"]["detects"] = any((f.get("divergent") or 0) > 0 for f in g0["functions"])
        if models or client is not None:
            import fn_probe_llm as FL
            if client is None:
                sys.path.insert(0, str(ROOT / "tools"))
                from cohort_inner import RefreshingClient
                cfgm = next(m for m in json.loads(Path(models).read_text())["models"] if m["name"] == "vertex-gemini-flash")
                client = RefreshingClient(cfgm["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", "")), cfgm["key_env"], cfgm.get("extra", {}))
                model_id, prices = cfgm["model_id"], cfgm["prices_usd_per_mtok"]
            else:
                model_id, prices = "fake", {"input": 1.0, "output": 1.0}

            def diff_for(rel):
                a = (orig / rel).read_text(encoding="utf-8", errors="replace").splitlines(True)
                b = bound["treated"][rel].splitlines(True)
                return "".join(difflib.unified_diff(a, b, "a/" + rel, "b/" + rel))[:4000]
            g2 = FL.probe_llm(client, model_id, prices, cap, py, orig, treated, modules, pp, skill_text(skill_path), work / "w", n, 3, env, seed, diff_for)
            rec["G2"] = {"verdict": g2["verdict"], "spent_usd": g2["spent_usd"],
                         "functions": [{k: f.get(k) for k in ("file", "qualname", "stable", "divergent", "why")} for f in g2["functions"]]}
            rec["G2"]["detects"] = any((f.get("divergent") or 0) > 0 for f in g2["functions"])
        rec["status"] = "FINISHED"
    except Exception as exc:
        rec.update(status="ERROR", error=("%s: %s" % (type(exc).__name__, exc))[:400])
    finally:
        shutil.rmtree(work, ignore_errors=True)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        (Path(out_dir) / ("RQ3_%s.json" % tid)).write_text(json.dumps(rec, indent=1, default=str))
    return rec


def main(argv):
    study, tid, out = argv[:3]
    opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
    r = run(study, tid, out, opt("--target-python", sys.executable), opt("--models", None), float(opt("--cap", 0.5)), int(opt("--n", 200)))
    print(json.dumps({k: r.get(k) for k in ("target", "status", "error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
