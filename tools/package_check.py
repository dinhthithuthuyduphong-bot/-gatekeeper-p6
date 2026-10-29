"""Check that a delivered package is COMPLETE and UNCHANGED in the repository (read-only).

python tools/package_check.py MANIFEST.json [--out DIR]

MANIFEST.json: {"name": ..., "files": {"path": "sha256", ...}}.  Reports, per file: OK, MISSING (and where a file of the
same name exists instead), or DIFFERENT (present with other content).  Catches partial uploads (some files of a package
arrived and others did not) and files extracted into the wrong folder.  Exit code is always 0; read `PROBLEMS`.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", "node_modules", "__pycache__"}


def locate(root, name):
    return sorted(str(p.relative_to(root)).replace("\\", "/") for p in Path(root).rglob(name)
                  if not (set(p.relative_to(root).parts) & SKIP))[:4]


def check(manifest, root=ROOT):
    root = Path(root)
    rows = []
    for rel, want in sorted(manifest["files"].items()):
        p = root / rel
        if not p.is_file():
            rows.append((rel, "MISSING", "found instead at: %s" % locate(root, Path(rel).name) if locate(root, Path(rel).name) else "not found anywhere"))
        elif hashlib.sha256(p.read_bytes()).hexdigest() != want:
            rows.append((rel, "DIFFERENT", "present, but the content is not the delivered one"))
        else:
            rows.append((rel, "OK", ""))
    return rows


def render(name, rows):
    bad = [r for r in rows if r[1] != "OK"]
    lines = ["# Package check: %s" % name, "", "**PROBLEMS: %d of %d files**" % (len(bad), len(rows)), "", "| File | Status | Detail |", "|---|---|---|"]
    lines += ["| `%s` | %s | %s |" % r for r in rows]
    return "\n".join(lines) + "\n"


def main(argv):
    manifest = json.loads(Path(argv[0]).read_text())
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    report = render(manifest.get("name", argv[0]), check(manifest))
    print(report)
    if out:
        Path(out).mkdir(parents=True, exist_ok=True)
        (Path(out) / "PACKAGE_CHECK.md").write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
