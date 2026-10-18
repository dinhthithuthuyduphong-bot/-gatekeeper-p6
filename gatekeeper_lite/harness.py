"""Runs a target's oracle cases inside one arm directory and prints JSON results.

Executed in a fresh subprocess per arm:  python -m gatekeeper_lite.harness DIR SEED
The oracle module must define ``cases()`` returning [(case_id, callable), ...].
"""
from __future__ import annotations

import importlib
import json
import random
import sys
import traceback


def main(argv):
    arm_dir, seed = argv[1], int(argv[2])
    sys.path.insert(0, arm_dir)
    oracle = importlib.import_module("oracle_cases")
    results = {}
    for case_id, fn in oracle.cases():
        random.seed(seed)
        try:
            fn()
            results[case_id] = {"passed": True}
        except Exception as exc:  # a failing case, not a harness error
            results[case_id] = {"passed": False,
                                "error": f"{type(exc).__name__}: {exc}"[:200],
                                "where": traceback.format_exc(limit=2)[-300:]}
    print(json.dumps({"seed": seed, "results": results}))


if __name__ == "__main__":
    main(sys.argv)
