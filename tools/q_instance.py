"""Study Q, one instance (protocol: study_q/STUDY_Q_PROTOCOL.md).  Needs docker.

python tools/q_instance.py INSTANCE_ID VERIFIED.json POOL.jsonl.gz SEED MODELS.json OUT_DIR

1. official SWE-bench image; original = /testbed, fix = original + gold patch (snapshots on the host, common path)
2. the light model writes the input generator ONCE per edited function (at most 3); usable = >= 100 stable inputs and the
   original differs from the fix; the first usable function (sorted by file, qualified name) is the target; its generator
   code and sha256 are recorded BEFORE any patch is scored
3. G0 + G2 inputs (200 each), original twice, fix once (gatekeeper_ext/fn_draws.py, unchanged)
4. up to m = 3 distinct resolved patches, in the order sha256("<seed>:<instance>:<patch sha>"); each applied with git apply
   and scored with capture on; every naive harmful input classified (gatekeeper_ext/q_classify.py)
The interpreter is a wrapper around `docker exec` that also swaps fn_probe_inner.py for tools/q_probe_inner.py, so the
Study P tools run unchanged and every exception carries its origin (explicit raise in project code, or incidental).
"""
import gzip
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import q_f0 as QF  # noqa: E402
from gatekeeper_ext import q_classify as QC  # noqa: E402

M_PATCHES = 3


def select_patches(pool_lines, iid, seed, m=M_PATCHES):
    """Distinct (by normalised content) resolved patches of one instance, in seeded order; the first m."""
    by = {}
    for p in pool_lines:
        if p["instance_id"] == iid:
            d = by.setdefault(p["sha"], {"sha": p["sha"], "patch": p["patch"], "submissions": []})
            d["submissions"].append(p["submission"])
    order = sorted(by.values(), key=lambda d: hashlib.sha256(("%s:%s:%s" % (seed, iid, d["sha"])).encode()).hexdigest())
    return order[:m], len(by)


def wrapper_text(cid, py=QF.TESTBED_PY):
    return ('#!/bin/sh\ns="$1"; shift\ncase "$s" in */fn_probe_inner.py) s="${s%%fn_probe_inner.py}q_probe_inner.py";; esac\n'
            'exec docker exec -i -w "$PWD" %s %s "$s" "$@"\n' % (cid, py))


def treated_files(orig, patch, work, tag):
    """Apply a patch to a copy of the original; return {path: new source} of the files it changes, or None."""
    d = Path(work) / ("apply_" + tag)
    shutil.copytree(orig, d, symlinks=True)
    (Path(work) / (tag + ".diff")).write_text(patch)
    a = subprocess.run(["git", "apply", "--whitespace=nowarn", str(Path(work) / (tag + ".diff"))], cwd=d, capture_output=True, text=True)
    out = None
    if a.returncode == 0:
        out = {rel: (d / rel).read_text(encoding="utf-8", errors="replace") for rel in QF.file_diffs(patch) if (d / rel).is_file()}
    shutil.rmtree(d, ignore_errors=True)
    return out


def run(iid, verified_path, pool_path, seed, models, out_dir, client=None):
    import fn_probe_llm as FL
    from gatekeeper_ext import fn_draws
    row = next(r for r in json.loads(Path(verified_path).read_text()) if r["instance_id"] == iid)
    with gzip.open(pool_path, "rt") as f:
        pool = [json.loads(l) for l in f if ('"%s"' % iid) in l]
    rec = {"instance_id": iid, "repo": row["repo"], "image": QF.image_name(iid), "modules": QF.edited_modules(row["patch"]), "status": "started"}
    work = Path(tempfile.mkdtemp(prefix="q_", dir="/tmp"))
    cid, t0 = None, time.time()
    try:
        p = QF.sh(["docker", "pull", "-q", rec["image"]], timeout=1800)
        if p.returncode:
            rec.update(status="NO_IMAGE")
            return rec
        cid = QF.sh(["docker", "run", "-d", "-v", "/tmp:/tmp", "-v", "%s:%s" % (ROOT, ROOT), rec["image"], "sleep", "infinity"], timeout=300).stdout.strip()
        rec["python"] = QF.sh(["docker", "exec", cid, QF.TESTBED_PY, "-c", "import sys;print(sys.version.split()[0])"]).stdout.strip()
        orig, gold = work / "orig", work / "gold"
        QF.sh(["docker", "cp", "%s:/testbed" % cid, str(orig)], timeout=1800, check=True)
        shutil.copytree(orig, gold, symlinks=True)
        (work / "gold.patch").write_text(row["patch"])
        if QF.sh(["git", "apply", "--whitespace=nowarn", str(work / "gold.patch")], cwd=gold).returncode:
            rec.update(status="GOLD_PATCH_DOES_NOT_APPLY")
            return rec
        py = work / "py"
        py.write_text(wrapper_text(cid))
        py.chmod(py.stat().st_mode | stat.S_IEXEC)
        env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
        # 2. generators once per edited function
        if client is None:
            from cohort_inner import RefreshingClient
            cfg = next(m for m in json.loads(Path(models).read_text())["models"] if m["name"] == "vertex-gemini-flash")
            client = RefreshingClient(cfg["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", "")), cfg["key_env"], cfg.get("extra", {}))
            model_id, prices = cfg["model_id"], cfg["prices_usd_per_mtok"]
        else:
            model_id, prices = "fake", {"input": 1.0, "output": 1.0}
        diffs = QF.file_diffs(row["patch"])
        seed_int = int(hashlib.sha256(("%s:%s" % (seed, iid)).encode()).hexdigest()[:8], 16) % 2000000000
        (work / "gen").mkdir()
        g = FL.probe_llm(client, model_id, prices, 0.15, py, orig, gold, rec["modules"], [], (row.get("problem_statement") or "")[:3000],
                         work / "gen", 200, 3, env, seed_int, lambda rel: diffs.get(rel, "")[:4000])
        funcs = sorted(g["functions"], key=lambda f: (f.get("file", ""), f.get("qualname", "")))
        rec["generator_spent_usd"] = g["spent_usd"]
        rec["functions"] = [{k: f.get(k) for k in ("file", "qualname", "usable", "why", "stable", "divergent")} for f in funcs]
        target = next((f for f in funcs if f.get("usable") and f.get("generator_code")), None)
        if target is None:
            rec.update(status="NOT_USABLE", verdict=g["verdict"])
            return rec
        fn = {"file": target["file"], "qualname": target["qualname"], "generator_code": target["generator_code"]}
        rec["target"] = {"file": fn["file"], "qualname": fn["qualname"], "generator_sha256": hashlib.sha256(fn["generator_code"].encode()).hexdigest()}
        # 3. inputs
        base, why = fn_draws.prepare_fn_base(py, orig, gold, [], fn, work / "fnbase", 200, seed_int, env)
        if base is None:
            rec.update(status="NO_STABLE_INPUT", why=why)
            return rec
        rec["base"] = base["info"]
        # 4. patches
        chosen, distinct = select_patches(pool, iid, seed)
        rec["distinct_patches"] = distinct
        rec["patches"] = []
        for k, ptc in enumerate(chosen):
            entry = {"sha": ptc["sha"], "submissions": sorted(set(ptc["submissions"])), "order": k}
            treated = treated_files(orig, ptc["patch"], work, "p%d" % k)
            if treated is None:
                entry["status"] = "PATCH_DOES_NOT_APPLY"
            else:
                sc, err = fn_draws.score_fn_patch(py, base, orig, treated, [], work / "fnbase", "p%d" % k, env, capture=True)
                entry.update(status="SCORED", complete=sc["complete"], harm=sum(sc["harm"]), help=sc["help"], divergent=sc["divergent"],
                             classified=QC.summarise(sc.get("outcomes") or []))
            rec["patches"].append(entry)
        rec["status"] = "FINISHED"
    except Exception as exc:
        rec.update(status="ERROR", error=("%s: %s" % (type(exc).__name__, exc))[:400])
    finally:
        rec["seconds"] = round(time.time() - t0)
        if cid:
            QF.sh(["docker", "rm", "-f", cid])
        QF.sh(["docker", "rmi", "-f", rec["image"]])
        shutil.rmtree(work, ignore_errors=True)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        (Path(out_dir) / ("Q_%s.json" % iid)).write_text(json.dumps(rec, indent=1, default=str))
    return rec


if __name__ == "__main__":
    r = run(*sys.argv[1:7])
    print(json.dumps({k: r.get(k) for k in ("instance_id", "status", "python", "error")}))
