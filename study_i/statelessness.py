"""Replay recorded draws in shuffled order and fresh workers every 25 draws.

Checks 100 observations per scope. This is an empirical stability diagnostic,
not a mathematical proof of independence or absence of state in every input.
"""
import argparse
import json
from pathlib import Path
import random
import sys
import time

from run import digest, write_json

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=["networkx", "sqlalchemy"])
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--gatekeeper", type=Path, default=HERE.parent)
    args = parser.parse_args()
    cfg = json.loads((HERE / "targets.json").read_text())
    target = cfg["targets"][args.target]
    if list(sys.version_info[:2]) != target["python"]:
        raise RuntimeError("Wrong Python minor version")
    for rel, sha in cfg["gatekeeper_sha256"].items():
        if digest(args.gatekeeper / rel) != sha:
            raise RuntimeError("Frozen core/skill changed: " + rel)
    sys.path.insert(0, str(args.gatekeeper.resolve()))
    from gatekeeper_lite.drawharness import _Worker, _load
    oracle_path = (HERE / target["draw_oracle"]).resolve()
    oracle = _load(oracle_path)
    rows = [json.loads(line) for line in (args.results / "draws.jsonl").read_text().splitlines()]
    out = args.results / "statelessness.jsonl"
    if out.exists():
        raise RuntimeError("Preserve existing statelessness log; use a new run directory")
    summary = {"status": "RUNNING", "seed": 20261024, "chunk": 25,
               "n_per_scope": 100, "scopes": {}}
    start = time.perf_counter()
    with out.open("w", encoding="utf-8") as log:
        for scope in oracle.scopes():
            selected = [r for r in rows if r["scope"] == scope][:100]
            if len(selected) != 100:
                raise RuntimeError("Incomplete recorded scope")
            random.Random("study-i-stateless:"+scope).shuffle(selected)
            mismatches = errors = 0
            for offset in range(0, len(selected), 25):
                workers = {}
                try:
                    for arm in ("baseline", "treated"):
                        workers[arm] = _Worker((args.results / "work" / arm).resolve(),
                                              target["pythonpath"], oracle_path, cfg["diagnostic_draws"]["seed"])
                    for original in selected[offset:offset+25]:
                        ow = workers["baseline"].run(original["draw"])
                        ot = workers["treated"].run(original["draw"])
                        error = "harness_error" in ow or "harness_error" in ot
                        errors += int(error)
                        pw, pt = (False, False) if error else map(bool, oracle.judge(scope, original["draw"], ow, ot))
                        # Module paths differ between fresh snapshots; compare semantic output.
                        clean = lambda x: {k:v for k,v in x.items() if k != "module"}
                        mismatch = error or clean(ow) != clean(original["without"]) or clean(ot) != clean(original["with"])
                        mismatch |= pw != original["passed_without"] or pt != original["passed_with"]
                        mismatches += int(mismatch)
                        log.write(json.dumps({"scope":scope, "original_n":original["n"], "chunk":offset//25,
                                  "without":ow, "with":ot, "passed_without":pw, "passed_with":pt,
                                  "mismatch":bool(mismatch), "harness_error":error}, allow_nan=False)+"\n")
                        log.flush()
                finally:
                    for w in workers.values():
                        w.close()
            summary["scopes"][scope] = {"compared":len(selected), "mismatches":mismatches, "harness_errors":errors}
            print("STATELESSNESS", target["target_id"], scope, json.dumps(summary["scopes"][scope]), flush=True)
    summary["seconds"] = time.perf_counter()-start
    summary["status"] = "STABLE_ON_CHECKED_DRAWS" if not any(
        s["mismatches"] or s["harness_errors"] for s in summary["scopes"].values()) else "FAILED"
    write_json(args.results / "STATELESSNESS.json", summary)
    if summary["status"] == "FAILED":
        raise RuntimeError("State/order mismatch; inspect raw log before any admission claim")


if __name__ == "__main__":
    main()
