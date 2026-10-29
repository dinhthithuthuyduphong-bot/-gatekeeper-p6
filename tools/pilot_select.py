"""Outcome-blind selection of the pilot instances: the first N by position in the frozen candidate order, at most one
per repository (so that one repository with a very large test suite cannot dominate a pilot).
python tools/pilot_select.py RECORDS.json N     -> prints the names, one per line"""
import json
import sys
from pathlib import Path


def select(records, n):
    seen, out = set(), []
    for r in sorted(records, key=lambda r: r["position"]):
        key = r["repo"].lower()
        if key not in seen:
            seen.add(key)
            out.append(r["name"])
        if len(out) == n:
            break
    return out


if __name__ == "__main__":
    print("\n".join(select(json.loads(Path(sys.argv[1]).read_text()), int(sys.argv[2]))))
