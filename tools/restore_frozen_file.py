"""Restore one file of a frozen study from its freeze tag, only if the restored bytes match what was frozen.

python tools/restore_frozen_file.py STUDY TAG [PATH]        (PATH defaults to the study's config_*.json)

Why: a development package that contains a file of an already-frozen study (for instance a DRAFT config) overwrites it
silently.  Re-freezing would create a NEW freeze (new timestamp, new hash, and the tag already exists).  Restoring the
original bytes keeps the original freeze intact.  The restore is refused unless
  (1) the study's FREEZE.json is byte-identical to the one at the tag, and
  (2) sha256 of the file at the tag equals the hash FREEZE.json recorded for that path.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _git_show(root, spec):
    r = subprocess.run(["git", "show", spec], cwd=str(root), capture_output=True)
    if r.returncode:
        raise SystemExit("git show %s failed: %s" % (spec, r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout


def restore(study, tag, rel=None, root=ROOT, write=True):
    root = Path(root)
    d = root / study
    cfg = sorted(d.glob("config_*.json"))
    if rel is None:
        if not cfg:
            raise SystemExit("no config_*.json in %s and no PATH given" % study)
        rel = cfg[0].relative_to(root).as_posix()
    freeze_now = (d / "FREEZE.json").read_bytes()
    freeze_tag = _git_show(root, "%s:%s/FREEZE.json" % (tag, study))
    if hashlib.sha256(freeze_now).hexdigest() != hashlib.sha256(freeze_tag).hexdigest():
        raise SystemExit("REFUSED: %s/FREEZE.json differs from the one at tag %s; the freeze record itself changed" % (study, tag))
    expected = json.loads(freeze_tag)["files"].get(rel)
    if expected is None:
        raise SystemExit("REFUSED: %s was not hashed in FREEZE.json at tag %s" % (rel, tag))
    blob = _git_show(root, "%s:%s" % (tag, rel))
    got = hashlib.sha256(blob).hexdigest()
    if got != expected:
        raise SystemExit("REFUSED: %s at tag %s has sha256 %s, but FREEZE.json recorded %s" % (rel, tag, got[:12], expected[:12]))
    target = root / rel
    current = target.read_bytes() if target.exists() else None
    if current == blob:
        return "already identical to the frozen version: %s" % rel
    if write:
        target.write_bytes(blob)
    return "restored %s from tag %s (sha256 %s...)" % (rel, tag, got[:12])


if __name__ == "__main__":
    print(restore(*sys.argv[1:4]))
