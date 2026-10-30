"""Append part B to the Study P frames (study_p is DRAFT): A*-track candidates go to candidates_astar.json, RR-track ones
to frame_rr.json, each after part A, in key order.  Refuses duplicates and any repository that would be in both tracks.
python tools/p_assemble_ext.py STUDY_DIR P_EXT_CANDIDATES.json SEED"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from split_candidates import split  # noqa: E402


def ident(c):
    return (c["repo"].lower().removesuffix(".git"), int(c["pr"]))


def unique_names(existing, part_b):
    """Candidate names are '<repo name>_pr<N>', so forks with the same repository name collide (e.g. five student
    repositories 'pytest_proj', PR 1).  A colliding name gets '_' + 6 hex digits of sha256(repository URL).  Order and
    membership are unchanged; returns (renamed copy of part_b, {old: new})."""
    import hashlib
    taken, out, ren = set(existing), [], {}
    for c in part_b:
        name = c["name"]
        if name in taken:
            name = "%s_%s" % (c["name"], hashlib.sha256(c["repo"].lower().encode()).hexdigest()[:6])
            ren.setdefault(c["name"], []).append(name)
        taken.add(name)
        out.append(dict(c, name=name))
    return out, ren


def extend(astar, rr, part_b, seed):
    have = {ident(c) for c in astar + rr if "pr" in c}
    if any(ident(c) in have for c in part_b) or len({ident(c) for c in part_b}) != len(part_b):
        raise SystemExit("REFUSED: the same repository and pull request appears twice")
    part_b, renamed = unique_names([c["name"] for c in astar + rr], part_b)
    s = split(part_b, seed)
    new_a, new_r = astar + s["ASTAR"], rr + s["RR"]
    if {c["repo"].lower() for c in new_a} & {c["repo"].lower() for c in new_r}:
        raise SystemExit("REFUSED: a repository would be in both tracks")
    return new_a, new_r, {"part_b": {k: len(v) for k, v in s.items()}, "candidates_astar": len(new_a), "frame_rr": len(new_r), "renamed": renamed}


def main(study_dir, ext_path, seed):
    d = Path(study_dir)
    raw = Path(ext_path).read_bytes()
    a, r, summary = extend(json.loads((d / "candidates_astar.json").read_text()), json.loads((d / "frame_rr.json").read_text()), json.loads(raw), seed)
    summary["part_b_sha256"] = hashlib.sha256(raw).hexdigest()
    (d / "candidates_astar.json").write_text(json.dumps(a, indent=1))
    (d / "frame_rr.json").write_text(json.dumps(r, indent=1))
    (d / "evidence").mkdir(parents=True, exist_ok=True)
    (d / "evidence" / "SPLIT_P_PART_B.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
