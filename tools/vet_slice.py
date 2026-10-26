"""Vet one shard of the ASTAR-track candidates (stage S2) with the existing tools/vet_target.py.

python tools/vet_slice.py CANDIDATES.json OUT_DIR SHARD K [LIMIT] [TIMEOUT_SECONDS]

Candidate i goes to shard i mod K.  Only the first LIMIT candidates (in the frozen order) are considered.  A timeout
or crash is recorded as a result of that candidate; nothing is retried or replaced, so the attrition table stays honest.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slice_for(cands, shard, k, limit):
    return cands[:limit][shard::k]


def default_runner(spec_path, out_dir, timeout):
    return subprocess.run([sys.executable, str(ROOT / "tools" / "vet_target.py"), str(spec_path), str(out_dir)],
                          capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))


def run(cands_path, out_dir, shard, k, limit=250, timeout=1500, runner=default_runner):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cands = json.loads(Path(cands_path).read_text())
    mine = slice_for(cands, int(shard), int(k), int(limit))
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for c in mine:
            spec = Path(tmp) / ("%s.json" % c["name"])
            spec.write_text(json.dumps({key: v for key, v in c.items() if key != "changed"}, indent=1))
            row = {"name": c["name"], "repo": c["repo"], "pr": c["pr"]}
            try:
                p = runner(spec, out, int(timeout))
                row.update(status="FINISHED", returncode=p.returncode)
                (out / ("log_%s.txt" % c["name"])).write_text((p.stdout + "\n" + p.stderr)[-4000:], encoding="utf-8")
            except subprocess.TimeoutExpired:
                row.update(status="TIMEOUT", returncode=None)
            except Exception as exc:                  # a crash of the vetting tool is a result, not a reason to skip
                row.update(status="CRASH", returncode=None, error=type(exc).__name__)
            rows.append(row)
    (out / ("SHARD_%s_SUMMARY.json" % shard)).write_text(json.dumps({"shard": int(shard), "of": int(k), "candidates": rows}, indent=1))
    print("shard", shard, "of", k, ":", len(rows), "candidates;", sum(r["status"] != "FINISHED" for r in rows), "not finished")
    return 0


if __name__ == "__main__":
    sys.exit(run(*sys.argv[1:7]))
