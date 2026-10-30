"""Study P, amendment P-A2: process the candidates of some shards that have NO stream record yet (their job died and the
artifact was lost before anyone saw it).  Same stages, same order, same shard assignment as tools/p_stream.py (frozen,
imported unchanged); in addition an exception in one candidate is recorded for that candidate instead of ending the shard.

python tools/p_stream_resume.py CANDIDATES.json OUT_DIR SHARD K MODELS.json DONE.json
DONE.json: names that already have a stream record (they are never processed again).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import p_stream as P  # noqa: E402


def todo(cands, shard, k, done):
    for i, c in enumerate(cands):
        c.setdefault("position", i)
    return [c for c in cands[int(shard)::int(k)] if c["name"] not in done]


def run(cands, out, shard, k, done, stages):
    Path(out).mkdir(parents=True, exist_ok=True)
    rows = []
    for c in todo(cands, shard, k, done):
        try:
            s = P.process(c, out, stages)
        except Exception as exc:                                   # recorded for this candidate, never retried
            s = {"name": c["name"], "repo": c["repo"], "pr": c.get("pr"), "stage_reached": "STAGE_ERROR",
                 "error": ("%s: %s" % (type(exc).__name__, exc))[:300]}
        s["resumed_under"] = "P-A2"
        (Path(out) / ("STREAM_%s.json" % c["name"])).write_text(json.dumps(s, indent=1))
        rows.append(s["name"])
        print(json.dumps({x: s.get(x) for x in ("name", "stage_reached", "vet_verdict", "fn_verdict", "gen_status")}), flush=True)
    (Path(out) / ("SHARD_%s_SUMMARY.json" % shard)).write_text(json.dumps({"shard": int(shard), "of": int(k), "resumed": rows}))
    return rows


def main(argv):
    cands_path, out, shard, k, models, done_path = argv[:6]
    done = set(json.loads(Path(done_path).read_text()))
    return 0 if run(json.loads(Path(cands_path).read_text()), out, shard, k, done, P.RealStages(models)) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
