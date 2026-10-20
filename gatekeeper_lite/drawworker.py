"""Worker process for sequential draw evaluation (one per arm, separate interpreter).

python -m gatekeeper_lite.drawworker ORACLE_PATH
Reads one JSON draw per line on stdin, calls oracle.execute(draw) against the package
importable in THIS process (its own snapshot via PYTHONPATH), writes one JSON outcome
per line.  Exceptions inside execute are outcomes, not worker failures.
"""
import importlib.util
import json
import sys
import traceback


def main(argv):
    spec = importlib.util.spec_from_file_location("gk_draw_oracle", argv[1])
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    print(json.dumps({"ready": True}), flush=True)
    for line in sys.stdin:
        msg = json.loads(line)
        try:
            out = oracle.execute(msg["draw"])
        except Exception as exc:  # the oracle's own failure is reported, never hidden
            out = {"harness_error": f"{type(exc).__name__}: {exc}", "tb": traceback.format_exc()[-400:]}
        print(json.dumps({"id": msg["id"], "outcome": out}), flush=True)


if __name__ == "__main__":
    main(sys.argv)
