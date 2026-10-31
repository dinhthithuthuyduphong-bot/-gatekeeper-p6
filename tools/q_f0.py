"""Study Q, feasibility step Q-F0 (0 model cost): on a stratified sample of SWE-bench Verified instances, inside the
official SWE-bench Docker image of each instance, can the functions edited by the developers' fix be called directly,
and does the original differ from the fix on signature-driven inputs (G0)?

python tools/q_f0.py sample OUT_DIR [PER_REPO=3]           fetch the 500 instances, write VERIFIED.json and SAMPLE.json
python tools/q_f0.py one INSTANCE_ID VERIFIED.json OUT_DIR [MODELS.json]
                                                           probe one instance (needs docker); with MODELS.json the
                                                           light model writes the generators (Q-F1, G2)

Inside the container only the target interpreter runs; the snapshots live on the host under /tmp (bind-mounted at the same
path) so tools/fn_probe.py works unchanged, with a wrapper interpreter that executes through `docker exec`.
"""
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
ROWS = "https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Verified&config=default&split=test&offset={o}&length=100"
SAMPLE_SEED = "study-q-f0"                       # feasibility only; the registered cohort will use a drand seed
TESTBED_PY = "/opt/miniconda3/envs/testbed/bin/python"


def image_name(instance_id):
    """Official SWE-bench evaluation image (Docker Hub namespace 'swebench'; '__' is not allowed, so it becomes '_1776_')."""
    return "swebench/sweb.eval.x86_64.%s:latest" % instance_id.lower().replace("__", "_1776_")


def edited_modules(patch):
    """Non-test Python files changed by a unified diff."""
    files = re.findall(r"^\+\+\+ b/(\S+)", patch, re.M)
    return sorted({f for f in files if f.endswith(".py") and not re.search(r"(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$|conftest\.py$", f)})


TRANSIENT = (429, 500, 502, 503, 504)


def get_json(url, tries=6, sleep=time.sleep, opener=urllib.request.urlopen):
    """GET with retries on transient server errors (truncated exponential backoff: 10, 30, 60, 120, 240 s)."""
    waits = (10, 30, 60, 120, 240)
    for k in range(tries):
        try:
            return json.loads(opener(url, timeout=60).read())
        except Exception as exc:
            code = getattr(exc, "code", None)
            if (code is not None and code not in TRANSIENT) or k == tries - 1:
                raise
            sleep(waits[min(k, len(waits) - 1)])


def fetch_rows(get=get_json):
    rows, o = [], 0
    while True:
        page = get(ROWS.format(o=o))
        batch = [r["row"] for r in page.get("rows", [])]
        rows += batch
        if len(batch) < 100:
            return rows
        o += 100


def stratified(rows, per_repo=3, seed=SAMPLE_SEED):
    by = {}
    for r in sorted(rows, key=lambda r: hashlib.sha256(("%s:%s" % (seed, r["instance_id"])).encode()).hexdigest()):
        if edited_modules(r["patch"]):
            by.setdefault(r["repo"], [])
            if len(by[r["repo"]]) < per_repo:
                by[r["repo"]].append(r["instance_id"])
    return [i for repo in sorted(by) for i in by[repo]]


def file_diffs(patch):
    """Split a unified diff into {path: diff of that file}."""
    out = {}
    for part in re.split(r"(?m)^(?=diff --git )", patch):
        m = re.search(r"^\+\+\+ b/(\S+)", part, re.M)
        if m:
            out[m.group(1)] = part
    return out


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def one(iid, verified_path, out_dir, models=None, client=None, cap=0.15):
    row = next(r for r in json.loads(Path(verified_path).read_text()) if r["instance_id"] == iid)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"instance_id": iid, "repo": row["repo"], "image": image_name(iid), "modules": edited_modules(row["patch"]), "status": "started"}
    work = Path(tempfile.mkdtemp(prefix="qf0_", dir="/tmp"))
    cid = None
    t0 = time.time()
    try:
        p = sh(["docker", "pull", "-q", rec["image"]], timeout=1800)
        if p.returncode:
            rec.update(status="NO_IMAGE", error=p.stderr[-300:])
            return rec
        p = sh(["docker", "run", "-d", "-v", "/tmp:/tmp", "-v", "%s:%s" % (ROOT, ROOT), rec["image"], "sleep", "infinity"], timeout=300)
        cid = p.stdout.strip()
        rec["python"] = sh(["docker", "exec", cid, TESTBED_PY, "-c", "import sys;print(sys.version.split()[0])"]).stdout.strip()
        orig, gold = work / "orig", work / "gold"
        sh(["docker", "cp", "%s:/testbed" % cid, str(orig)], timeout=1800, check=True)
        shutil.copytree(orig, gold, symlinks=True)
        (work / "gold.patch").write_text(row["patch"])
        a = sh(["git", "apply", "--whitespace=nowarn", str(work / "gold.patch")], cwd=gold)
        if a.returncode:
            rec.update(status="GOLD_PATCH_DOES_NOT_APPLY", error=a.stderr[-300:])
            return rec
        wrapper = work / "py"
        wrapper.write_text('#!/bin/sh\nexec docker exec -i -w "$PWD" %s %s "$@"\n' % (cid, TESTBED_PY))
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IEXEC)
        import fn_probe as FP
        env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONHASHSEED="0", PYTHONDONTWRITEBYTECODE="1")
        (work / "probe").mkdir()
        if models or client is not None:                          # Q-F1: model-written generators (G2), as Study P step 2
            import fn_probe_llm as FL
            if client is None:
                from cohort_inner import RefreshingClient
                cfg = next(m for m in json.loads(Path(models).read_text())["models"] if m["name"] == "vertex-gemini-flash")
                client = RefreshingClient(cfg["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", "")), cfg["key_env"], cfg.get("extra", {}))
                model_id, prices = cfg["model_id"], cfg["prices_usd_per_mtok"]
            else:
                model_id, prices = "fake", {"input": 1.0, "output": 1.0}
            diffs = file_diffs(row["patch"])
            seed = int(hashlib.sha256(("study-q-f1:" + iid).encode()).hexdigest()[:8], 16) % 2000000000
            res = FL.probe_llm(client, model_id, prices, cap, wrapper, orig, gold, rec["modules"], [], (row.get("problem_statement") or "")[:3000],
                               work / "probe", 200, 3, env, seed, lambda rel: diffs.get(rel, "")[:4000])
            rec["generator"] = "G2"
        else:
            res = FP.probe_roots(wrapper, orig, gold, rec["modules"], [], work / "probe", 200, 3, env)
            rec["generator"] = "G0"
        rec.update(res, status="FINISHED")
    except Exception as exc:
        rec.update(status="ERROR", error=("%s: %s" % (type(exc).__name__, exc))[:400])
    finally:
        rec["seconds"] = round(time.time() - t0)
        if cid:
            sh(["docker", "rm", "-f", cid])
        sh(["docker", "rmi", "-f", rec["image"]])
        shutil.rmtree(work, ignore_errors=True)
        (out / ("QF0_%s.json" % iid)).write_text(json.dumps(rec, indent=1, default=str))
    return rec


def main(argv):
    if argv[0] == "sample":
        out = Path(argv[1])
        out.mkdir(parents=True, exist_ok=True)
        rows = fetch_rows()
        (out / "VERIFIED.json").write_text(json.dumps(rows))
        s = stratified(rows, int(argv[2]) if len(argv) > 2 else 3)
        (out / "SAMPLE.json").write_text(json.dumps(s))
        print(json.dumps({"instances": len(rows), "repos": len({r["repo"] for r in rows}), "sample": len(s)}))
        return 0
    r = one(argv[1], argv[2], argv[3], models=argv[4] if len(argv) > 4 and argv[4] else None)
    print(json.dumps({k: r.get(k) for k in ("instance_id", "status", "python", "verdict", "error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
