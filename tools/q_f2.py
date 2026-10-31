"""Study Q, feasibility Q-F2 (0 cost): census of the public patch pool of SWE-bench Verified.  For every public submission
(SWE-bench/experiments, evaluation/verified/<submission>): its predictions and its list of resolved instances.
Resolved = the submission's patch passes the instance's tests (plausible).

The experiments repository holds ENTRIES, not artifacts: predictions live where the entry's metadata.yaml `assets` block
points (the submitter's public repository, or the public bucket s3://swe-bench-submissions/ for older entries).
python tools/q_f2.py entries EXPERIMENTS_CLONE OUT_DIR     (current layout; records every URL tried)
python tools/q_f2.py SUBMISSIONS.json OUT_DIR              (first attempt: predictions inside the repository, 0/182)
Writes POOL_SUMMARY.json (per submission and per instance) and POOL.jsonl.gz (one line per resolved patch:
instance_id, submission, sha256 of the normalised patch, patch).  Nothing here depends on any measurement of ours.
"""
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

RAW = "https://raw.githubusercontent.com/SWE-bench/experiments/main/evaluation/verified/%s/%s"


def fetch(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as exc:                                      # 404 is final, other errors are retried
            if getattr(exc, "code", None) == 404 or k == tries - 1:
                return None
            time.sleep(5 * (k + 1))


def normalise(patch):
    """Compare patches by content: drop 'index' lines and trailing whitespace."""
    lines = [l.rstrip() for l in (patch or "").splitlines() if not l.startswith("index ")]
    return "\n".join(lines).strip()


def resolved_ids(results):
    if not results:
        return None
    try:
        d = json.loads(results)
    except ValueError:
        return None
    r = d.get("resolved") if isinstance(d, dict) else None
    if isinstance(r, list):
        return set(r)
    if isinstance(r, dict):                                           # some layouts group the ids
        return {x for v in r.values() if isinstance(v, list) for x in v}
    return None


def census(subs, get=fetch):
    per_sub, pool = {}, []
    for s in subs:
        preds, res = get(RAW % (s, "all_preds.jsonl")), get(RAW % (s, "results/results.json"))
        resolved = resolved_ids(res)
        if preds is None or resolved is None:
            per_sub[s] = {"usable": False, "preds": preds is not None, "results": resolved is not None}
            continue
        n = 0
        for line in preds.splitlines():
            try:
                p = json.loads(line)
            except ValueError:
                continue
            iid, patch = p.get("instance_id"), p.get("model_patch")
            if iid in resolved and patch:
                pool.append({"instance_id": iid, "submission": s, "sha": hashlib.sha256(normalise(patch).encode()).hexdigest(), "patch": patch})
                n += 1
        per_sub[s] = {"usable": True, "resolved_listed": len(resolved), "resolved_with_patch": n,
                      "date": (re.match(r"(\d{8})", s) or [None, None])[1] if re.match(r"\d{8}", s) else None}
    per_inst = {}
    for p in pool:
        d = per_inst.setdefault(p["instance_id"], {"patches": 0, "distinct": set()})
        d["patches"] += 1
        d["distinct"].add(p["sha"])
    per_inst = {k: {"patches": v["patches"], "distinct": len(v["distinct"])} for k, v in per_inst.items()}
    return per_sub, per_inst, pool


def asset_urls(meta):
    """Every place an entry's `assets` block may point to, turned into HTTPS URLs of a predictions file."""
    found = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            found.append(x.strip())
    walk((meta or {}).get("assets"))
    urls = []
    for f in found:
        m = re.match(r"https?://github\.com/([^/\s]+)/([^/\s#?]+?)(?:\.git)?(?:/(?:tree|blob)/([^/\s]+)(/[^\s]*)?)?/?$", f)
        if m:
            owner, name, ref, path = m.group(1), m.group(2), m.group(3) or "HEAD", (m.group(4) or "").strip("/")
            base = "https://raw.githubusercontent.com/%s/%s/%s/%s" % (owner, name, ref, path + "/" if path else "")
            urls += [base + "all_preds.jsonl", base + "preds.json"]
            continue
        m = re.match(r"s3://([^/\s]+)/?(\S*)$", f)
        if m:
            bucket, prefix = m.group(1), m.group(2).strip("/")
            base = "https://%s.s3.amazonaws.com/%s" % (bucket, prefix + "/" if prefix else "")
            urls += [base + "all_preds.jsonl", base + "preds.json"]
            continue
        if f.startswith("http") and f.endswith((".jsonl", ".json")):
            urls.append(f)
    return list(dict.fromkeys(urls)), found


def parse_preds(text):
    """all_preds.jsonl (one JSON object per line) or preds.json ({instance_id: {...}} or a list)."""
    out = []
    try:
        d = json.loads(text)
        items = d.values() if isinstance(d, dict) else d if isinstance(d, list) else []
        out = [x for x in items if isinstance(x, dict)]
    except ValueError:
        for line in text.splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return [(p.get("instance_id"), p.get("model_patch")) for p in out]


def entries(clone, get=fetch):
    import yaml
    base = Path(clone) / "evaluation" / "verified"
    per_sub, pool = {}, []
    for d in sorted(x for x in base.iterdir() if x.is_dir()):
        meta = yaml.safe_load((d / "metadata.yaml").read_text()) if (d / "metadata.yaml").exists() else None
        resolved = None
        for f in sorted((d / "results").glob("*.json")) if (d / "results").is_dir() else []:
            resolved = resolved_ids(f.read_text())
            if resolved is not None:
                break
        urls, raw = asset_urls(meta)
        rec = {"assets": raw[:6], "tried": [], "resolved_listed": len(resolved) if resolved is not None else None}
        preds = None
        for u in urls:
            t = get(u)
            rec["tried"].append([u, t is not None])
            if t:
                preds = parse_preds(t)
                rec["preds_url"] = u
                break
        if preds is None or resolved is None:
            rec["usable"] = False
            per_sub[d.name] = rec
            continue
        n = 0
        for iid, patch in preds:
            if iid in resolved and patch:
                pool.append({"instance_id": iid, "submission": d.name, "sha": hashlib.sha256(normalise(patch).encode()).hexdigest(), "patch": patch})
                n += 1
        rec.update(usable=True, resolved_with_patch=n)
        per_sub[d.name] = rec
    return per_sub, pool


def write(out, per_sub, pool):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    per_inst = {}
    for p in pool:
        x = per_inst.setdefault(p["instance_id"], {"patches": 0, "distinct": set()})
        x["patches"] += 1
        x["distinct"].add(p["sha"])
    per_inst = {k: {"patches": v["patches"], "distinct": len(v["distinct"])} for k, v in per_inst.items()}
    with gzip.open(out / "POOL.jsonl.gz", "wt") as f:
        for p in pool:
            f.write(json.dumps(p) + "\n")
    dist = sorted(v["distinct"] for v in per_inst.values())
    summ = {"submissions": len(per_sub), "usable_submissions": sum(bool(v.get("usable")) for v in per_sub.values()), "resolved_patches": len(pool),
            "instances_with_a_resolved_patch": len(per_inst), "distinct_patches_per_instance_median": dist[len(dist) // 2] if dist else 0,
            "per_submission": per_sub, "per_instance": per_inst}
    (out / "POOL_SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: summ[k] for k in ("submissions", "usable_submissions", "resolved_patches", "instances_with_a_resolved_patch", "distinct_patches_per_instance_median")}))


def main(subs_path, out):
    subs = json.loads(Path(subs_path).read_text())
    per_sub, per_inst, pool = census(subs)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    with gzip.open(out / "POOL.jsonl.gz", "wt") as f:
        for p in pool:
            f.write(json.dumps(p) + "\n")
    dist = sorted(v["distinct"] for v in per_inst.values())
    summ = {"submissions": len(subs), "usable_submissions": sum(v["usable"] for v in per_sub.values()), "resolved_patches": len(pool),
            "instances_with_a_resolved_patch": len(per_inst), "distinct_patches_per_instance_median": dist[len(dist) // 2] if dist else 0,
            "per_submission": per_sub, "per_instance": per_inst}
    (out / "POOL_SUMMARY.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: summ[k] for k in ("submissions", "usable_submissions", "resolved_patches", "instances_with_a_resolved_patch", "distinct_patches_per_instance_median")}))
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "entries":
        ps, pl = entries(sys.argv[2])
        write(sys.argv[3], ps, pl)
        sys.exit(0)
    sys.exit(main(*sys.argv[1:3]))
