"""Study N / pilot: one instance, end to end.  Outer part (system python): fetch the issue text, rebuild the two
snapshots from the recorded SHAs, provision ONE virtual environment with the version-2.1 rules (missing modules of either
arm installed for both), then run tools/cohort_inner.py INSIDE that environment.

python tools/cohort_instance.py RECORDS.json NAME OUT_DIR MODELS.json MODEL_NAMES REPS CAP_USD SEED_PREFIX [N_DRAWS]

RECORDS.json: list of vetting records (trimmed) with "pr".  MODEL_NAMES: comma-separated names in MODELS.json.
"""
import hashlib
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
import vet_target as V  # noqa: E402  (frozen helpers)
import vet_target2 as T  # noqa: E402  (frozen provisioning v2.1)
from gatekeeper_ext import issue_fetch  # noqa: E402


def seed_for(prefix, name):
    return int(hashlib.sha256((prefix + name).encode()).hexdigest()[:8], 16)


def select_models(cfg, names):
    by = {m["name"]: m for m in cfg["models"]}
    missing = [n for n in names if n not in by]
    if missing:
        raise SystemExit("unknown model name(s) %s; available: %s" % (missing, sorted(by)))
    return [by[n] for n in names]


def main(records_path, name, out_dir, models_path, model_names, reps, cap_usd, seed_prefix, n_draws=200, oracle="test"):
    rec = next(r for r in json.loads(Path(records_path).read_text()) if r["name"] == name)
    cfg_all = json.loads(Path(models_path).read_text())
    models = select_models(cfg_all, [m for m in model_names.split(",") if m])
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="coh_"))
    report = {"name": name, "repo": rec["repo"], "status": "started", "models": [m["name"] for m in models]}
    try:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
        pr_title, issue, prov = issue_fetch.fetch(rec["repo"], int(rec["pr"]), token)
        report["issue_fetch"] = prov
        repo = work / "repo"
        repo.mkdir()
        V.sh([*V.GIT, "init", "-q"], cwd=repo)
        V.sh([*V.GIT, "remote", "add", "origin", rec["repo"]], cwd=repo)
        V.sh([*V.GIT, "fetch", "-q", "--filter=blob:none", "origin", rec["pre"], rec["gold"]], cwd=repo, timeout=900)
        orig, gold = work / "orig", work / "gold"
        V.checkout_to(repo, rec["pre"], orig)
        V.checkout_to(repo, rec["gold"], gold)
        tests = list(rec.get("gold_test_files") or [])
        for f in tests:                                              # the fix's tests exist in the original snapshot
            blob = subprocess.run([*V.GIT, "show", "%s:%s" % (rec["gold"], f)], cwd=repo, capture_output=True)
            if blob.returncode == 0:
                (orig / f).parent.mkdir(parents=True, exist_ok=True)
                (orig / f).write_bytes(blob.stdout)
        venv.EnvBuilder(with_pip=True).create(work / "venv")
        py = work / "venv" / "bin" / "python"
        log, repairs = [], []
        T.provision(py, orig, ["test", "dev"], log)
        T.repair({"pre": (py, orig), "gold": (py, gold)}, tests, repairs)
        report["provisioning"] = {"steps": len(log), "failed_steps": [s for s in log if s.get("exit")][:6], "repairs": repairs}
        args = {"orig": str(orig), "gold": str(gold), "work": str(work / "run"), "out": str(work / "inner.json"), "vet": rec,
                "issue": issue, "pr_title": pr_title, "models": models, "reps": int(reps), "seed": seed_for(seed_prefix, name),
                "cap_usd": float(cap_usd), "runner": "pytest", "n_draws": int(n_draws)}
        if oracle == "function":                                  # Study P: draws are direct calls of the edited function
            rel = rec["fn_target"]["file"]
            args.update(oracle="function", fn_target=rec["fn_target"], generator_model=select_models(cfg_all, ["vertex-gemini-flash"])[0],
                        issue_text=("%s\n\n%s" % (issue["title"], issue["body"])) if issue else pr_title,
                        fn_diff=(V.sh([*V.GIT, "diff", rec["pre"], rec["gold"], "--", rel], cwd=repo, check=False).stdout or "")[:4000])
        (work / "args.json").write_text(json.dumps(args, default=str))
        env = dict(os.environ, PYTHONPATH=str(ROOT), GK_TOKEN_CMD=os.environ.get("GK_TOKEN_CMD", ""))
        p = subprocess.run([str(py), str(ROOT / "tools" / "cohort_inner.py"), str(work / "args.json")], env=env,
                           capture_output=True, text=True, timeout=7200)
        report["inner_tail"] = (p.stdout + p.stderr)[-1500:]
        inner = json.loads((work / "inner.json").read_text()) if (work / "inner.json").exists() else {"status": "ERROR", "error": "inner produced no output"}
        report.update(inner=inner, status="FINISHED")
    except subprocess.TimeoutExpired:
        report.update(status="TIMEOUT")
    except Exception as exc:
        report.update(status="ERROR", error=("%s: %s" % (type(exc).__name__, exc))[:500])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / ("COHORT_%s.json" % name)).write_text(json.dumps(report, indent=1, default=str))
    print(json.dumps({k: report.get(k) for k in ("name", "status", "error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:11]))
