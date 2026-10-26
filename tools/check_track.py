"""Guard: every candidate in a track file must belong to that track under the frozen split rule (amendment M-A1).

python tools/check_track.py CANDIDATES.json ASTAR|RR

The seed is recomputed from the frozen study_m exactly as the discovery workflow does (drand round after the freeze).
Run at the start of any workflow that touches a candidate list, so that clicking "Run workflow" on the wrong branch,
or committing the wrong file, cannot send the RR half into vetting before in-principle acceptance.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from split_candidates import track  # noqa: E402


def wrong_track(cands, expected, seed):
    return [c for c in cands if track(seed, c["repo"]) != expected]


def frozen_seed():
    from run_study_d import drand_seed
    cfg = json.loads((ROOT / "study_m" / "config_study_m.json").read_text())
    h = hashlib.sha256((ROOT / "study_m" / "FREEZE.json").read_bytes()).hexdigest()
    return str(drand_seed(cfg.get("seed_freeze_sha256") or h, cfg["seed_time_utc"])["seed"])


def main(path, expected):
    if expected not in ("ASTAR", "RR"):
        raise SystemExit("track must be ASTAR or RR")
    cands = json.loads(Path(path).read_text())
    bad = wrong_track(cands, expected, frozen_seed())
    if bad:
        raise SystemExit("%d of %d candidates do not belong to track %s, e.g. %s" % (len(bad), len(cands), expected, bad[0]["repo"]))
    print("ok: all %d candidates belong to track %s" % (len(cands), expected))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
