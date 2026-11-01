"""Study T phase 2 (study_t/AMENDMENTS.md, T-A1): trials of every census cell of one shard of packages.  Records raw per-input
change flags of the gate and reference streams; decisions and ground truth are computed by tools/market_analyze.py.

python tools/market_trials.py WORK_DIR OUT_DIR --shard I --shards K [--n 200] [--max-funcs 5]
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import composition_study as CS  # noqa: E402  (S-A5 harness: inner(), fixed hash seed, subtype substitution)
import market_census as MC  # noqa: E402
from library_census import load_skills, apply_all  # noqa: E402

RES = ROOT / "research_closure/results/study_t"
SEEDS = {"gate": 1, "ref": 2}
MIN_STABLE = 50


def configure_harness():
    """The S-A5 configuration of Study S, used unchanged (T-A1)."""
    CS.S_A1 = CS.S_A2 = CS.S_A3 = CS.S_A4 = CS.S_A5 = True
    CS.S_A3_FIXED_HASH = True
    if os.environ.get("GK_MEMCAP_GB"):          # T-A3
        CS.MEMCAP_BYTES = int(float(os.environ["GK_MEMCAP_GB"]) * 1024 ** 3)


def extract_all(blob, filename, dest):
    dest.mkdir(parents=True, exist_ok=True)
    if filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for m in z.namelist():
                if ".." not in m and not m.endswith("/"):
                    p = dest / m
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(z.read(m))
    else:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:*") as t:
            for m in t.getmembers():
                if m.isfile() and ".." not in m.name and not m.name.startswith("/"):
                    p = dest / m.name
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(t.extractfile(m).read())
    tops = [d for d in dest.iterdir() if d.is_dir()]
    return tops[0] if len(tops) == 1 else dest


def import_root(root, rel_file):
    """Directory (relative to root) that must be on sys.path to import rel_file as part of its package."""
    p = (root / rel_file).parent
    while (p / "__init__.py").exists() and p != root:
        p = p.parent
    return p.relative_to(root).as_posix() if p != root else ""


def env_for(work, root, project, version):
    env_dir = work / "venv"
    if not env_dir.exists():
        venv.create(env_dir, with_pip=True)
    py = env_dir / "bin" / "python"
    r = subprocess.run([str(py), "-m", "pip", "install", "-q", "%s==%s" % (project, version)], capture_output=True, text=True,
                       timeout=1800)
    u = subprocess.run([str(py), "-m", "pip", "uninstall", "-y", "-q", project], capture_output=True, text=True, timeout=600)
    return py, {"install_rc": r.returncode, "install_tail": (r.stderr or r.stdout)[-400:], "uninstall_rc": u.returncode}


def strip_top(rel):
    """Census paths start with the sdist's top folder; trial paths are relative to it."""
    return rel.split("/", 1)[1] if "/" in rel else rel


def apply_skill(rule, snap, files, skills):
    if rule.startswith("R2:"):
        sk = skills[rule[3:]]
        for f in files:
            p = snap / f
            p.write_text(apply_all(sk, p.read_text(encoding="utf-8"))[0], encoding="utf-8")
        return {"ok": True}
    r = subprocess.run(["ruff", "check", "--isolated", "--no-cache", "--select", rule, "--fix", "--unsafe-fixes", "--exit-zero",
                        *[str(snap / f) for f in files]], capture_output=True, text=True, timeout=600)
    return {"ok": r.returncode == 0, "tail": (r.stderr or "")[-200:]}


def funcs_of(cell, k):
    out = []
    for fq in cell["functions"]:
        f, q = fq.split("::", 1)
        if q == "<module>" or "<locals>" in q:
            continue
        out.append((strip_top(f), q))
    return out[:k]


def run_package(pkg, census_pkg, work, n, k, skills):
    blob = MC.fetch("https://pypi.org/pypi/%s/%s/json" % (pkg["project"], pkg["version"]))
    meta = json.loads(blob)
    sd = next(f for f in meta["urls"] if f["filename"] == pkg["sdist"])
    data = MC.fetch(sd["url"], 300)
    if hashlib.sha256(data).hexdigest() != pkg["sha256"]:
        return {"project": pkg["project"], "error": "sdist sha256 differs from the census"}
    root = extract_all(data, sd["filename"], work / "src")
    py, log = env_for(work, root, pkg["project"], pkg["version"])
    orig_cache, cells = {}, {}
    for rule, cell in sorted(census_pkg["cells"].items()):
        fs = funcs_of(cell, k)
        rec = {"applicability": cell["applicability"], "functions": []}
        if not fs:
            rec["usable"], rec["why"] = False, "no callable function among the sites"
            cells[rule] = rec
            continue
        snap = work / "snap"
        if snap.exists():
            shutil.rmtree(snap)
        shutil.copytree(root, snap, symlinks=True)
        rec["apply"] = apply_skill(rule, snap, sorted({f for f, _ in fs} | {strip_top(x.split("::", 1)[0]) for x in cell["functions"]}),
                                   skills)
        for f, q in fs:
            pp = [import_root(root, f)] if import_root(root, f) else []
            fr = {"file": f, "qualname": q}
            for stream, seed in SEEDS.items():
                key = (f, q, stream)
                if key not in orig_cache:
                    tag = hashlib.sha1(("%s:%s:%s" % key).encode()).hexdigest()[:12]
                    calls = work / (tag + ".calls.json")
                    gen = CS.inner(py, root, pp, f, q, "generate", calls, work / (tag + ".gen.json"), n, seed)
                    if gen.get("status") != "GENERATED":
                        orig_cache[key] = {"status": "UNUSABLE", "why": str(gen.get("reason") or gen.get("status"))[:150]}
                    else:
                        o1 = CS.inner(py, root, pp, f, q, "run", calls, work / (tag + ".o1.json"), n, seed)
                        o2 = CS.inner(py, root, pp, f, q, "run", calls, work / (tag + ".o2.json"), n, seed)
                        orig_cache[key] = {"status": "OK", "calls": calls, "o1": o1, "o2": o2}
                oc = orig_cache[key]
                if oc["status"] != "OK" or oc["o1"].get("status") != "RAN" or oc["o2"].get("status") != "RAN":
                    fr[stream] = {"usable": False, "why": oc.get("why") or "original did not run"}
                    continue
                tag = hashlib.sha1(("%s:%s:%s:%s" % (rule, f, q, stream)).encode()).hexdigest()[:12]
                v1 = CS.inner(py, snap, pp, f, q, "run", oc["calls"], work / (tag + ".v1.json"), n, seed)
                v2 = CS.inner(py, snap, pp, f, q, "run", oc["calls"], work / (tag + ".v2.json"), n, seed)
                if v1.get("status") != "RAN" or v2.get("status") != "RAN":
                    fr[stream] = {"usable": False, "why": "variant did not run: %s" % v1.get("status")}
                    continue
                a, b = oc["o1"]["outcomes"], oc["o2"]["outcomes"]
                c, d = v1["outcomes"], v2["outcomes"]
                m = min(len(a), len(b), len(c), len(d))
                flags = []
                for i in range(m):
                    if a[i] == b[i] and c[i] == d[i] and a[i] != ["timeout"] and c[i] != ["timeout"]:
                        flags.append(1 if a[i] != c[i] else 0)
                fr[stream] = {"usable": len(flags) >= MIN_STABLE, "stable": len(flags), "flags": "".join(map(str, flags))}
            rec["functions"].append(fr)
        shutil.rmtree(snap, ignore_errors=True)
        rec["usable"] = any(fr.get("gate", {}).get("usable") and fr.get("ref", {}).get("usable") for fr in rec["functions"])
        cells[rule] = rec
    shutil.rmtree(work, ignore_errors=True)
    return {"project": pkg["project"], "version": pkg["version"], "env": log, "cells": cells}


def main(argv):
    work, out = Path(argv[0]), Path(argv[1])
    opt = lambda key, d: type(d)(argv[argv.index(key) + 1]) if key in argv else d   # noqa: E731
    shard, shards, n, k = opt("--shard", 0), opt("--shards", 1), opt("--n", 200), opt("--max-funcs", 5)
    configure_harness()
    targets = json.loads((RES / "TARGETS.json").read_text())["selected"]
    census = {p["project"]: p for p in json.loads((RES / "MARKET_CENSUS.json").read_text())["packages"]}
    skills = load_skills()
    out.mkdir(parents=True, exist_ok=True)
    for pkg in targets[shard::shards]:
        print("package", pkg["project"], flush=True)
        try:
            res = run_package(pkg, census[pkg["project"]], work / pkg["project"], n, k, skills)
        except Exception as exc:  # noqa: BLE001 - recorded, never silently dropped
            res = {"project": pkg["project"], "error": "%s: %s" % (type(exc).__name__, str(exc)[:300])}
        (out / ("TRIALS_%s.json" % re.sub(r"[^A-Za-z0-9_.-]", "_", pkg["project"]))).write_text(json.dumps(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
