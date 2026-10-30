"""Rebuild the two Study P frames from the committed evidence alone (idempotent; study_p must be DRAFT).

python tools/p_frames.py SEED [--check]

exposed (first 500 of Study M + 800 of Study N)  ->  A* part of part A first, RR part first-1300 then part A   (n_assemble)
part B (study_p/evidence/P_EXT_CANDIDATES.json, all batches in order)  ->  appended by track, unique names   (p_assemble_ext)
--check compares with the committed frames instead of writing them.  Replaces appending batch by batch, so a run that
crashed after a checkpoint, or a batch appended twice, can never leave the frames in a state the evidence does not explain.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from n_assemble import assemble  # noqa: E402
from p_assemble_ext import extend  # noqa: E402


def build(seed, root=ROOT):
    root = Path(root)
    load = lambda rel: json.loads((root / rel).read_text())
    exposed = load("study_m_astar/evidence/s1/M_ORDERED.json") + load("study_n/evidence/N_CANDIDATES.json")
    part_a = load("study_p/evidence/N_CANDIDATES.json")
    pb = root / "study_p/evidence/P_EXT_CANDIDATES.json"
    part_b = json.loads(pb.read_text()) if pb.exists() else []
    astar, rr, s_a = assemble(exposed, part_a, seed)
    astar, rr, s_b = extend(astar, rr, part_b, seed)
    return astar, rr, {"part_a": s_a, "part_b": s_b, "candidates_astar": len(astar), "frame_rr": len(rr)}


def main(argv):
    seed = argv[0]
    astar, rr, summary = build(seed)
    d = ROOT / "study_p"
    if "--check" in argv:
        same = (json.loads((d / "candidates_astar.json").read_text()) == astar and json.loads((d / "frame_rr.json").read_text()) == rr)
        print("frames match the evidence:", same, json.dumps({k: summary[k] for k in ("candidates_astar", "frame_rr")}))
        return 0 if same else 1
    (d / "candidates_astar.json").write_text(json.dumps(astar, indent=1))
    (d / "frame_rr.json").write_text(json.dumps(rr, indent=1))
    (d / "evidence" / "SPLIT_P_FRAMES.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: summary[k] for k in ("candidates_astar", "frame_rr")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
