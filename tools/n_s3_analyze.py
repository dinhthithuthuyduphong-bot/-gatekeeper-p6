"""Study N stage N-S3, inner step: run the frozen test-level harness (gatekeeper_ext/testmut.py, tm-dev-v4-reach) on
one instance.  Runs INSIDE the instance's provisioned venv (so pytest and the dependencies are those of the instance).

python tools/n_s3_analyze.py ARGS.json
ARGS: {"orig", "gold", "modules", "pythonpath", "census", "work", "seed", "out", "runner" (default pytest),
       "n_draws" (default 200), "n_mutants" (default 3)}
The gold fix is passed as the reference patch ("gold_itself"), so the trigger rate and completeness are measured.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main(path):
    a = json.loads(Path(path).read_text())
    from gatekeeper_ext import testmut
    res = testmut.analyze(a["orig"], a["gold"], a["modules"], a["pythonpath"], a.get("runner", "pytest"), a["census"],
                          {"gold_itself": a["gold"]}, a["work"], a["seed"], n_draws=a.get("n_draws", 200), n_mutants=a.get("n_mutants", 3))
    Path(a["out"]).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res.get(k) for k in ("eligible", "reason", "draws_compiled", "bug_trigger_rate", "deterministic")}, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
