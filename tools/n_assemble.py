"""Build the two Study N frames from the S1 order (rule of amendment M-A1, seed of Study M stage S1).

python tools/n_assemble.py M_ORDERED.json N_CANDIDATES.json SEED STUDY_DIR

  candidates_astar.json : A*-track candidates of the CONTINUATION only (the first 500 are exposed), in seed order
  frame_rr.json         : RR-track candidates of the first 500, then RR-track candidates of the continuation, in order
  evidence/SPLIT_N.json : counts, input hashes, and the check that no repository appears in both tracks
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from split_candidates import split  # noqa: E402


def assemble(m_ordered, n_cands, seed):
    first, cont = split(m_ordered, seed), split(n_cands, seed)
    astar = cont["ASTAR"]
    rr = first["RR"] + cont["RR"]
    repos = lambda xs: {c["repo"].lower() for c in xs}
    shared = repos(first["ASTAR"] + astar) & repos(rr)
    if shared:
        raise SystemExit("REFUSED: %d repositories would be in both tracks" % len(shared))
    names = [c["name"] for c in m_ordered + n_cands]
    if len(names) != len(set(names)):
        raise SystemExit("REFUSED: a candidate appears twice in the first 500 and the continuation")
    summary = {"seed": str(seed), "first_500": {k: len(v) for k, v in first.items()}, "continuation": {k: len(v) for k, v in cont.items()},
               "candidates_astar": len(astar), "frame_rr": len(rr), "shared_repositories": 0}
    return astar, rr, summary


def main(m_path, n_path, seed, study_dir):
    m_bytes, n_bytes = Path(m_path).read_bytes(), Path(n_path).read_bytes()
    astar, rr, summary = assemble(json.loads(m_bytes), json.loads(n_bytes), seed)
    summary.update(m_ordered_sha256=hashlib.sha256(m_bytes).hexdigest(), n_candidates_sha256=hashlib.sha256(n_bytes).hexdigest())
    d = Path(study_dir)
    (d / "evidence").mkdir(parents=True, exist_ok=True)
    (d / "candidates_astar.json").write_text(json.dumps(astar, indent=1))
    (d / "frame_rr.json").write_text(json.dumps(rr, indent=1))
    (d / "evidence" / "SPLIT_N.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
