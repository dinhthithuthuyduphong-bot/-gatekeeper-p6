"""Preflight BEFORE freezing a study: every file in the study directory must be hash-bound by the freeze.

python tools/freeze_doctor.py STUDY [--out DIR]

tools/freeze_study.py hashes only fixed patterns plus `extra_tracked`; a protocol file that is in neither is silently
left out (that is how GATES.md and DECISION_RULE.md of study_m_astar went unhashed).  This tool lists every such file as
a BLOCKER, together with missing extra_tracked paths.  Read-only; exit code 0.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def check(study, root=ROOT):
    from freeze_study import digest, tracked
    d = Path(root) / study
    out = []
    cfgs = sorted(d.glob("config_*.json"))
    if not cfgs:
        return [("BLOCKER", "no config_*.json in %s" % study)]
    cfg = json.loads(cfgs[0].read_text())
    out.append(("OK" if cfg.get("status") == "DRAFT" else "BLOCKER", "status is %r (freeze needs DRAFT)" % cfg.get("status")))
    missing = [p for p in cfg.get("extra_tracked", []) if not (Path(root) / p).is_file()]
    out.append(("BLOCKER" if missing else "OK", "extra_tracked paths missing: %s" % missing if missing else "every extra_tracked path exists (%d)" % len(cfg.get("extra_tracked", []))))
    hashed = set(digest(tracked(d.resolve())).keys())
    in_dir = sorted(p.relative_to(Path(root)).as_posix() for p in d.rglob("*") if p.is_file() and p.name != "FREEZE.json")
    unhashed = [p for p in in_dir if p not in hashed]
    out.append(("BLOCKER" if unhashed else "OK", "files in %s that the freeze would NOT hash: %s" % (study, unhashed) if unhashed else "every file in %s would be hashed (%d)" % (study, len(in_dir))))
    from repo_hygiene import strays
    dup, lone = strays(Path(root))
    bad = [n for n, _ in dup] + lone
    out.append(("BLOCKER" if bad else "OK", "files at the repository root that break the unit tests (run `Gatekeeper repo hygiene`): %s" % bad if bad else "no stray files at the repository root"))
    return out


def main(argv):
    study = argv[0]
    out_dir = argv[argv.index("--out") + 1] if "--out" in argv else None
    items = check(study)
    n = sum(1 for lvl, _ in items if lvl == "BLOCKER")
    report = "# Freeze preflight for %s\n\n**BLOCKERS: %d**\n\n" % (study, n) + "\n".join("- [%s] %s" % it for it in items) + "\n"
    print(report)
    if out_dir:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        (Path(out_dir) / "FREEZE_DOCTOR.md").write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
