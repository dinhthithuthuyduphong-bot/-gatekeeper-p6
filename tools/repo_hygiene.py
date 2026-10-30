"""Find (and optionally remove) files left at the repository ROOT by a package extracted to the wrong place.

python tools/repo_hygiene.py [--remove] [--strict]   (--strict: exit 1 when stray files exist)

A root-level file is a stray duplicate when a file with the same name exists in one of the canonical directories.
Such files break `python -m unittest discover -s tests` (a root copy of a test module shadows the one in tests/), so
every workflow that runs the unit tests (freeze, amend) fails.  --remove deletes ONLY root-level duplicates (never a
file that exists nowhere else, never anything inside a directory).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ["tools", "tests", "gatekeeper_ext", "gatekeeper_lite", ".github/workflows", "research_closure/results"]


def strays(root=ROOT):
    root = Path(root)
    where = {}
    for c in CANONICAL:
        d = root / c
        if d.is_dir():
            for p in d.iterdir():
                if p.is_file():
                    where.setdefault(p.name, []).append("%s/%s" % (c, p.name))
    dup = sorted((p.name, where[p.name]) for p in root.iterdir() if p.is_file() and p.name in where)
    lone_tests = sorted(p.name for p in root.glob("test_*.py") if p.name not in where)
    return dup, lone_tests


def main(argv):
    dup, lone = strays()
    for name, canon in dup:
        print("STRAY %s (also at %s)" % (name, ", ".join(canon)))
    for name in lone:
        print("ROOT TEST FILE WITHOUT A COPY IN tests/: %s (not removed; move it by hand if it belongs in tests/)" % name)
    if "--remove" in argv:
        for name, _ in dup:
            (ROOT / name).unlink()
            print("removed", name)
    print("%d stray duplicate(s), %d lone root test file(s)" % (len(dup), len(lone)))
    if "--strict" in argv and (dup or lone) and "--remove" not in argv:
        print("::error::files at the repository root shadow the test modules; run the workflow `Gatekeeper repo hygiene` with mode=remove")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
