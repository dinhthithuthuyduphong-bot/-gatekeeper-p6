"""Study R: footprint census of the two real skill families (study_r/PROTOCOL.md).  No model calls.
python tools/footprint_census.py WORK_DIR OUT_DIR [--targets d,e,g]"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext.none_identity import register  # noqa: E402
from gatekeeper_lite import transforms  # noqa: E402
from gatekeeper_lite.gatekeeper import bind_modules, footprint_overlap  # noqa: E402
from gatekeeper_lite.skill import Skill, Target  # noqa: E402

register()
SKILLS = {"bool": ROOT / "study_d/skills/bool-excluded-from-int.json", "none": ROOT / "study_g/skills/none-identity.json"}
TEST_DIRS = {"test", "tests", "testing"}


def is_test(rel):
    parts = Path(rel).parts
    return any(p in TEST_DIRS for p in parts[:-1]) or parts[-1].startswith("test_") or parts[-1].endswith("_test.py")


def clone(manifest, dest):
    co = manifest.get("checkout") or {}
    repo, ref = co.get("repo"), co.get("ref") or manifest.get("revision")
    if not repo:
        return "no checkout in manifest"
    if dest.exists():
        return None
    r = subprocess.run(["git", "init", "-q", str(dest)], capture_output=True, text=True)
    for cmd in (["git", "-C", str(dest), "fetch", "-q", "--depth", "1", repo, ref], ["git", "-C", str(dest), "checkout", "-q", "FETCH_HEAD"]):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode:
            return (r.stderr or r.stdout)[-300:]
    return None


def scan_repo(root, skill):
    sites, scanned, skipped = set(), 0, 0
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        if ".git/" in rel or is_test(rel):
            continue
        try:
            src = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            skipped += 1
            continue
        scanned += 1
        try:
            res = skill.transform().apply(src, single_site=False)
        except transforms.Abstain:
            continue
        except (SyntaxError, ValueError, RecursionError):
            skipped += 1
            continue
        sites |= {(rel, s.function) for s in res.sites}
    return sites, scanned, skipped


def census(work, targets):
    skills = {k: Skill.load(v) for k, v in SKILLS.items()}
    rows = []
    for study in targets:
        for tdir in sorted((ROOT / ("study_%s" % study) / "eval_targets").iterdir()):
            mf = tdir / "gk_target.json"
            if not mf.is_file():
                continue
            manifest = json.loads(mf.read_text())
            dest = Path(work) / ("%s_%s" % (study, tdir.name))
            err = clone(manifest, dest)
            row = {"study": study.upper(), "target": tdir.name, "repository": manifest.get("repository"), "clone_error": err}
            if err:
                rows.append(row)
                continue
            target = Target(manifest.get("target_id", tdir.name), dest, manifest)
            declared, repo_sites = {}, {}
            for name, sk in skills.items():
                try:
                    b = bind_modules([sk], target)
                    declared[name] = sorted({(s["module"], s["function"]) for s in b["sites"]})
                except (FileNotFoundError, SyntaxError) as exc:
                    declared[name] = "error: %s" % type(exc).__name__
                s, scanned, skipped = scan_repo(dest, sk)
                repo_sites[name] = sorted(s)
                row["files_scanned"], row["files_skipped"] = scanned, skipped
            both_declared = sorted(set(map(tuple, declared["bool"])) & set(map(tuple, declared["none"]))) \
                if isinstance(declared["bool"], list) and isinstance(declared["none"], list) else []
            both_repo = sorted(set(map(tuple, repo_sites["bool"])) & set(map(tuple, repo_sites["none"])))
            row.update(declared_sites=declared, declared_both=both_declared,
                       repo_functions={k: len(v) for k, v in repo_sites.items()}, repo_both=both_repo,
                       footprint_overlap_declared=footprint_overlap(["func:%s:%s" % t for t in declared["bool"]] if isinstance(declared["bool"], list) else [],
                                                                    ["func:%s:%s" % t for t in declared["none"]] if isinstance(declared["none"], list) else []))
            rows.append(row)
    ok = [r for r in rows if not r.get("clone_error")]
    total = {"targets": len(rows), "cloned": len(ok),
             "repo_functions_bool": sum(r["repo_functions"]["bool"] for r in ok),
             "repo_functions_none": sum(r["repo_functions"]["none"] for r in ok),
             "repo_functions_both": sum(len(r["repo_both"]) for r in ok),
             "targets_with_repo_overlap": sum(1 for r in ok if r["repo_both"]),
             "declared_functions_both": sum(len(r["declared_both"]) for r in ok),
             "files_scanned": sum(r.get("files_scanned", 0) for r in ok)}
    return {"total": total, "targets": rows}


def main(argv):
    work, out = Path(argv[0]), Path(argv[1])
    targets = (argv[argv.index("--targets") + 1] if "--targets" in argv else "d,e,g").split(",")
    work.mkdir(parents=True, exist_ok=True)
    res = census(work, targets)
    out.mkdir(parents=True, exist_ok=True)
    (out / "FOOTPRINT_CENSUS.json").write_text(json.dumps(res, indent=1, default=list))
    print(json.dumps(res["total"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
