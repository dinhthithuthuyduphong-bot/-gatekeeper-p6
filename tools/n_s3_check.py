"""Study N stage N-S3 for one instance: rebuild the two snapshots, provision ONE venv (vet_target2 v2.1 rules, both
arms' missing modules installed), and run the frozen harness inside it.

python tools/n_s3_check.py ELIGIBLE.json NAME OUT_DIR
ELIGIBLE.json: the list written from the N-S2 results (name, repo, pre, gold, changed_files, gold_test_files).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import vet_target as V  # noqa: E402  (frozen helpers)
import vet_target2 as T  # noqa: E402  (frozen provisioning v2.1)

TEST_PATH = re.compile(r"(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)tests\.py$")


def instance_plan(rec):
    """Editable modules, census entries and pythonpath, by the rules of gatekeeper_ext/b9_cohort.py."""
    modules = [f for f in rec["changed_files"] if f.endswith(".py") and not TEST_PATH.search(f)]
    tests = list(rec.get("gold_test_files") or [])
    dirs = [os.path.dirname(f) for f in tests]
    common = os.path.commonpath(dirs) if dirs else ""
    census = [common] if common else tests
    pythonpath = ["src"] if modules and all(m.startswith("src/") for m in modules) else []
    return modules, census, pythonpath, tests


def seed_for(name):
    return int(hashlib.sha256(("study-n-s3:" + name).encode()).hexdigest()[:8], 16)


def main(eligible_path, name, out_dir):
    rec = next(r for r in json.loads(Path(eligible_path).read_text()) if r["name"] == name)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="ns3_"))
    report = {"name": name, "repo": rec["repo"], "pre": rec["pre"], "gold": rec["gold"], "status": "started"}
    try:
        modules, census, pythonpath, tests = instance_plan(rec)
        report.update(modules=modules, census=census, pythonpath=pythonpath)
        repo = work / "repo"
        repo.mkdir()
        V.sh([*V.GIT, "init", "-q"], cwd=repo)
        V.sh([*V.GIT, "remote", "add", "origin", rec["repo"]], cwd=repo)
        V.sh([*V.GIT, "fetch", "-q", "--filter=blob:none", "origin", rec["pre"], rec["gold"]], cwd=repo, timeout=900)
        orig, gold = work / "orig", work / "gold"
        V.checkout_to(repo, rec["pre"], orig)
        V.checkout_to(repo, rec["gold"], gold)
        for f in tests:                                        # the fix's tests are available in the original snapshot
            blob = subprocess.run([*V.GIT, "show", "%s:%s" % (rec["gold"], f)], cwd=repo, capture_output=True)
            if blob.returncode == 0:
                (orig / f).parent.mkdir(parents=True, exist_ok=True)
                (orig / f).write_bytes(blob.stdout)
        venv.EnvBuilder(with_pip=True).create(work / "venv")
        py = work / "venv" / "bin" / "python"
        log, repairs = [], []
        T.provision(py, orig, ["test", "dev"], log)
        T.repair({"pre": (py, orig), "gold": (py, gold)}, tests, repairs)
        report["provisioning"] = {"log": log, "repairs": repairs}
        args = {"orig": str(orig), "gold": str(gold), "modules": modules, "pythonpath": pythonpath, "census": census,
                "work": str(work / "run"), "seed": seed_for(name), "out": str(work / "harness.json")}
        (work / "args.json").write_text(json.dumps(args))
        env = dict(os.environ, PYTHONPATH=str(ROOT))
        p = subprocess.run([str(py), str(ROOT / "tools" / "n_s3_analyze.py"), str(work / "args.json")], env=env,
                           capture_output=True, text=True, timeout=5400)
        report["analyze_tail"] = (p.stdout + p.stderr)[-1500:]
        report["harness"] = json.loads((work / "harness.json").read_text()) if (work / "harness.json").exists() else {"eligible": False, "reason": "analyzer produced no output"}
        report["status"] = "FINISHED"
    except Exception as exc:
        report["status"] = "ERROR"
        report["error"] = ("%s: %s" % (type(exc).__name__, exc))[:500]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / ("S3_%s.json" % name)).write_text(json.dumps(report, indent=1, default=str))
    print(json.dumps({k: report.get(k) for k in ("name", "status", "error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
