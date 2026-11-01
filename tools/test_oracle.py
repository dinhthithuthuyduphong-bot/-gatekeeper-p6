"""Study T-A4 (study_t/AMENDMENTS.md): the package's own test suite as a baseline (TS: admit iff CI stays green) and as an
independent oracle for Gatekeeper's admissions.  No model calls.

python tools/test_oracle.py WORK_DIR OUT_DIR --shard I --shards K [--budget-min 320]
Reads GK_T_RES (default research_closure/results/study_t): TARGETS.json, MARKET_CENSUS.json, STUDY_T_RESULT.json.
Writes OUT_DIR/TS_<project>.json per package.
"""
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import composition_study as CS  # noqa: E402
import market_census as MC  # noqa: E402
import market_trials as MT  # noqa: E402
from library_census import load_skills  # noqa: E402

RUN_CAP_S = 900
EXTRAS = ("test", "tests", "testing", "dev")


def run_group(cmd, timeout, env, cwd):
    """Run in its own process group; kill the group afterwards (as T2-A2).  Returns (returncode or None on timeout, tail)."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, cwd=cwd, start_new_session=True,
                         preexec_fn=CS._memcap if (CS.MEMCAP_BYTES or CS.NPROC_CAP) else None)
    try:
        out, _ = p.communicate(timeout=timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, rc = "", None
    finally:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        if p.poll() is None:
            p.wait()
    return rc, (out or "")[-600:]


def junit_outcomes(path):
    """{test id: 'pass' | 'fail' | 'skip'} from a JUnit XML report; {} if missing or unreadable."""
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError):
        return {}
    out = {}
    for tc in tree.iter("testcase"):
        tid = "%s::%s" % (tc.get("classname", ""), tc.get("name", ""))
        tags = {ch.tag for ch in tc}
        out[tid] = "fail" if tags & {"failure", "error"} else "skip" if "skipped" in tags else "pass"
    return out


def pytest_run(py, root, ir, work, tag):
    xml = work / (tag + ".xml")
    if xml.exists():
        xml.unlink()
    env = dict(os.environ, PYTHONPATH=str(root / ir) if ir else str(root), PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    rc, tail = run_group([str(py), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts=", "--timeout", "60",
                          "--junitxml", str(xml)], RUN_CAP_S, env, str(root))
    return {"rc": rc, "seconds": round(time.time() - t0, 1), "outcomes": junit_outcomes(xml) if rc is not None else {},
            "timeout": rc is None, "tail": tail if rc not in (0, 1) else ""}


def setup_env(work, root, proj, version):
    py, log = MT.env_for(work, root, proj, version)
    pip = lambda *a: subprocess.run([str(py), "-m", "pip", "install", "-q", *a], capture_output=True, text=True, timeout=1800)  # noqa: E731
    log["pytest_rc"] = pip("pytest", "pytest-timeout").returncode
    log["extra"] = None
    for ex in EXTRAS:
        if pip("%s[%s]==%s" % (proj, ex, version)).returncode == 0:
            log["extra"] = ex
            break
    subprocess.run([str(py), "-m", "pip", "uninstall", "-y", "-q", proj], capture_output=True, timeout=600)
    return py, log


def cell_files(cell):
    return sorted({MT.strip_top(x.split("::", 1)[0]) for x in cell["functions"]})


def run_package(pkg, rows, census_pkg, work, skills, deadline):
    proj = pkg["project"]
    meta = json.loads(MC.fetch("https://pypi.org/pypi/%s/%s/json" % (proj, pkg["version"])))
    sd = next(f for f in meta["urls"] if f["filename"] == pkg["sdist"])
    data = MC.fetch(sd["url"], 300)
    if hashlib.sha256(data).hexdigest() != pkg["sha256"]:
        return {"project": proj, "error": "sdist sha256 differs from the census"}
    root = MT.extract_all(data, sd["filename"], work / "src")
    ir = "src" if (root / "src").is_dir() else ""
    py, log = setup_env(work, root, proj, pkg["version"])
    o1 = pytest_run(py, root, ir, work, "o1")
    o2 = pytest_run(py, root, ir, work, "o2")
    stable = sorted(t for t, v in o1["outcomes"].items() if v == "pass" and o2["outcomes"].get(t) == "pass")
    res = {"project": proj, "version": pkg["version"], "env": log, "import_root": ir,
           "original": [{k: r[k] for k in ("rc", "seconds", "timeout", "tail")} | {"tests": len(r["outcomes"])} for r in (o1, o2)],
           "stable_passes": len(stable), "applicable": bool(stable), "cells": {}}
    if not stable:
        return res
    for row in rows:
        rule = row["cell"].split("/", 1)[1]
        if time.time() > deadline:
            res["cells"][rule] = {"status": "not run (budget)"}
            continue
        snap = work / "snap"
        shutil.rmtree(snap, ignore_errors=True)
        shutil.copytree(root, snap, symlinks=True)
        MT.apply_skill(rule, snap, cell_files(census_pkg["cells"][rule]), skills)
        r = pytest_run(py, snap, ir, work, "c")
        failed = [t for t in stable if r["outcomes"].get(t) != "pass"] if not r["timeout"] else stable
        rec = {"status": "run", "admit": not r["timeout"] and not failed, "timeout": r["timeout"], "seconds": r["seconds"],
               "failed": len(failed), "failed_tests": failed[:10]}
        if not rec["admit"] and row.get("G"):
            r2 = pytest_run(py, snap, ir, work, "c2")
            again = [t for t in stable if r2["outcomes"].get(t) != "pass"] if not r2["timeout"] else stable
            rec["confirmed"] = bool(again)
        res["cells"][rule] = rec
        shutil.rmtree(snap, ignore_errors=True)
    return res


def main(argv):
    work, out = Path(argv[0]), Path(argv[1])
    opt = lambda key, d: type(d)(argv[argv.index(key) + 1]) if key in argv else d   # noqa: E731
    shard, shards, budget = opt("--shard", 0), opt("--shards", 1), opt("--budget-min", 320)
    deadline = time.time() + budget * 60
    MT.configure_harness()
    targets = {t["project"]: t for t in json.loads((MT.RES / "TARGETS.json").read_text())["selected"]}
    census = {p["project"]: p for p in json.loads((MT.RES / "MARKET_CENSUS.json").read_text())["packages"]}
    rows = json.loads((MT.RES / "STUDY_T_RESULT.json").read_text())["rows"]
    by = {}
    for r in rows:
        by.setdefault(r["cell"].split("/", 1)[0], []).append(r)
    skills = load_skills()
    out.mkdir(parents=True, exist_ok=True)
    for proj in sorted(by)[shard::shards]:
        du = shutil.disk_usage("/tmp")
        print("package", proj, "cells", len(by[proj]), "free_disk_gb %.1f" % (du.free / 1e9), flush=True)
        try:
            res = run_package(targets[proj], by[proj], census[proj], work / proj, skills, deadline)
        except Exception as exc:  # noqa: BLE001 - recorded, never dropped
            res = {"project": proj, "error": "%s: %s" % (type(exc).__name__, str(exc)[:300])}
        shutil.rmtree(work / proj, ignore_errors=True)
        (out / ("TS_%s.json" % re.sub(r"[^A-Za-z0-9_.-]", "_", proj))).write_text(json.dumps(res))
        print(" ->", "applicable" if res.get("applicable") else res.get("error") or "not applicable",
              "stable", res.get("stable_passes"), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
