"""Read-only preflight for `Gatekeeper study amend`: reports every condition that would make the amendment fail.

python tools/amend_doctor.py STUDY AMENDMENT_ID [EDITS_FILE] [--out DIR]

It repeats the checks of the workflow and of tools/amend_study.py without changing anything: study frozen, amendment
documented and not yet applied, edits file present and parsable the way the workflow's shell parses it, every edit
applicable, every file named in extra_tracked present, tag not already taken.  Exit code is always 0 so the report can be
uploaded; read `BLOCKERS` in the output.
"""
import copy
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def _set(doc, dotted, value):
    keys = dotted.split(".")
    cur = doc
    for k in keys[:-1]:
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    if isinstance(cur, list):
        cur[int(keys[-1])] = value
    else:
        cur[keys[-1]] = value


def check(study, amendment, edits_file="", root=ROOT, tags=None):
    """Returns a list of (level, message); level is OK, INFO or BLOCKER."""
    out = []
    add = lambda lvl, msg: out.append((lvl, msg))
    d = Path(root) / study
    if not d.is_dir():
        return [("BLOCKER", "directory %s does not exist at the repository root (extracted into a sub-folder?)" % study)]
    cfgs = sorted(d.glob("config_*.json"))
    if not cfgs:
        return [("BLOCKER", "no config_*.json in %s" % study)]
    cfg = json.loads(cfgs[0].read_text())
    add("OK" if cfg.get("status") == "FROZEN" else "BLOCKER", "study status is %r (an amendment applies only to FROZEN)" % cfg.get("status"))
    if cfg.get("status") != "FROZEN" and (d / "FREEZE.json").exists():
        add("INFO", "FREEZE.json exists although the config says %r: the frozen config was most likely overwritten by a package that contained the DRAFT config. Do NOT freeze again; run `Gatekeeper restore frozen file` with the freeze tag of this study." % cfg.get("status"))
    am = d / "AMENDMENTS.md"
    text = am.read_text(encoding="utf-8") if am.exists() else ""
    add("OK" if amendment in text else "BLOCKER", "amendment id %r %s in %s/AMENDMENTS.md" % (amendment, "is documented" if amendment in text else "is NOT documented", study))
    if amendment in cfg.get("amendments_applied", []):
        add("BLOCKER", "amendment %s was already applied (amendments_applied=%s)" % (amendment, cfg["amendments_applied"]))
    if not (d / "FREEZE.json").exists():
        add("BLOCKER", "%s/FREEZE.json is missing" % study)
    specs = []
    if edits_file:
        ep = d / edits_file
        if not ep.exists():
            found = sorted(str(q.relative_to(root)).replace("\\", "/") for q in Path(root).rglob(edits_file) if ".git" not in q.parts)[:3]
            add("BLOCKER", "edits file %s/%s does not exist%s" % (study, edits_file, "; a file of that name is at: %s (move it into %s/)" % (found, study) if found else " and no file of that name exists anywhere in the repository (the package was not fully uploaded: run `Gatekeeper package check`)"))
        else:
            try:
                specs = shlex.split(ep.read_text(encoding="utf-8"))      # the workflow uses eval, which splits like the shell
                add("OK", "edits file parsed into %d edit(s)" % len(specs))
            except ValueError as exc:
                add("BLOCKER", "edits file cannot be parsed by the shell: %s" % exc)
    trial = copy.deepcopy(cfg)
    for spec in specs:
        fname, _, rest = spec.partition(":")
        key, _, raw = rest.partition("=")
        try:
            value = json.loads(raw)
        except ValueError as exc:
            add("BLOCKER", "edit %r: the value is not valid JSON (%s)" % (spec[:60], exc))
            continue
        if fname == cfgs[0].name:
            try:
                _set(trial, key, value)
                add("OK", "edit %s:%s is applicable" % (fname, key))
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                add("BLOCKER", "edit %s:%s cannot be applied (%s)" % (fname, key, type(exc).__name__))
        elif not (d / fname).exists():
            add("BLOCKER", "edit targets %s/%s, which does not exist" % (study, fname))
    missing = [rel for rel in trial.get("extra_tracked", []) if not (Path(root) / rel).is_file()]
    add("BLOCKER" if missing else "OK", "%d file(s) named in extra_tracked are missing: %s" % (len(missing), missing[:5]) if missing else "every file named in extra_tracked exists (%d)" % len(trial.get("extra_tracked", [])))
    tag = "%s-%s" % (study, amendment.lower())
    if tags is None:
        r = subprocess.run(["git", "tag", "-l", tag], cwd=str(root), capture_output=True, text=True)
        tags = r.stdout.split()
    add("BLOCKER" if tag in tags else "OK", "tag %s %s" % (tag, "already exists" if tag in tags else "is free"))
    try:
        from freeze_study import tracked, digest
        frozen = json.loads((d / "FREEZE.json").read_text())["files"]
        now = digest(tracked(d.resolve()))
        changed = sorted(k for k in set(frozen) | set(now) if frozen.get(k) != now.get(k))
        add("INFO", "files currently differing from FREEZE.json (expected before the amendment: AMENDMENTS.md and the files it adds): %s" % changed[:12])
    except Exception as exc:                                        # informational only
        add("INFO", "could not compare with FREEZE.json: %s" % type(exc).__name__)
    return out


def failing_tests(unittest_output):
    """Names of failing tests from a `unittest discover` log."""
    return sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+ \([^)]+\))", unittest_output, re.M)))


def render(items, fails=None):
    blockers = [m for lvl, m in items if lvl == "BLOCKER"]
    lines = ["# Amendment preflight", "", "**BLOCKERS: %d**" % (len(blockers) + len(fails or [])), ""]
    lines += ["- [%s] %s" % (lvl, m) for lvl, m in items]
    if fails is not None:
        lines += ["", "## Unit tests (the workflow runs them first)", "", "failing tests: %s" % (fails or "none")]
    return "\n".join(lines) + "\n"


def main(argv):
    out_dir = None
    if "--out" in argv:
        i = argv.index("--out")
        out_dir = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    study, amendment = argv[0], argv[1]
    edits = argv[2] if len(argv) > 2 else ""
    fails = None
    tests_log = Path(out_dir or ".") / "unit_tests.log"
    if tests_log.exists():
        fails = failing_tests(tests_log.read_text(errors="replace"))
    report = render(check(study, amendment, edits), fails)
    print(report)
    if out_dir:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        (Path(out_dir) / "AMEND_DOCTOR.md").write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
