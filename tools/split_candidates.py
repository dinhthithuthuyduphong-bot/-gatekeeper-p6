"""Split the ordered Study M candidates into two DISJOINT tracks, by repository (rule frozen in amendment M-A1).

    track(repo) = RR    if sha256("{seed}:track:{repo}") is even, else ASTAR

Splitting by repository (not by pull request) keeps the two cohorts independent: no repository, and therefore no
shared code, tests or maintainers, appears in both.  The RR half is never vetted, executed or examined until
in-principle acceptance; the ASTAR half proceeds to stages S2 and S3.

python tools/split_candidates.py M_ORDERED.json SEED OUT_DIR
"""
import hashlib
import json
import sys
from pathlib import Path


def track(seed, repo):
    h = hashlib.sha256(("%s:track:%s" % (seed, repo.lower())).encode()).hexdigest()
    return "RR" if int(h, 16) % 2 == 0 else "ASTAR"


def split(cands, seed):
    out = {"RR": [], "ASTAR": []}
    for c in cands:                                   # keeps the seed-derived order inside each track
        out[track(seed, c["repo"])].append(c)
    return out


def main(path, seed, out_dir):
    cands = json.loads(Path(path).read_text())
    parts = split(cands, seed)
    repos = {k: sorted({c["repo"].lower() for c in v}) for k, v in parts.items()}
    assert not set(repos["RR"]) & set(repos["ASTAR"]), "tracks share a repository"
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "M_TRACK_RR.json").write_text(json.dumps(parts["RR"], indent=1))
    (out / "M_TRACK_ASTAR.json").write_text(json.dumps(parts["ASTAR"], indent=1))
    summary = {"seed": str(seed), "candidates": len(cands), "pull_requests": {k: len(v) for k, v in parts.items()},
               "repositories": {k: len(v) for k, v in repos.items()}, "shared_repositories": 0,
               "input_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
    (out / "SPLIT_SUMMARY.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
