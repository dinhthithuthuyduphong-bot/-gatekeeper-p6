"""Run the function-level feasibility probe on one shard (instance i goes to shard i mod K), each instance in its own
process group with a time limit.  python tools/fn_probe_shard.py ELIGIBLE.json OUT_DIR SHARD K [TIMEOUT_SECONDS]"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from vet_dev import run_group  # noqa: E402


def main(elig, out, shard, k, timeout=2400):
    recs = json.loads(Path(elig).read_text())[int(shard)::int(k)]
    Path(out).mkdir(parents=True, exist_ok=True)
    rows = []
    for r in recs:
        try:
            p = run_group([sys.executable, str(ROOT / "tools" / "fn_probe.py"), elig, r["name"], out], int(timeout), cwd=str(ROOT))
            rows.append({"name": r["name"], "status": "FINISHED", "returncode": p.returncode})
            (Path(out) / ("log_%s.txt" % r["name"])).write_text(p.stdout[-4000:], encoding="utf-8")
        except subprocess.TimeoutExpired:
            rows.append({"name": r["name"], "status": "TIMEOUT"})
            (Path(out) / ("FNPROBE_%s.json" % r["name"])).write_text(json.dumps({"name": r["name"], "repo": r["repo"], "status": "TIMEOUT",
                                                                                "verdict": "snapshots or environment failed", "functions": []}))
    (Path(out) / ("SHARD_%s_SUMMARY.json" % shard)).write_text(json.dumps({"shard": int(shard), "of": int(k), "instances": rows}, indent=1))
    print("shard", shard, ":", len(rows), "instances")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:6]))
