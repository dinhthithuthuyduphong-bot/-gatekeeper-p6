"""RQ3, inner step (runs in the TARGET's Python, 3.8-compatible): draw inputs with the hand-written oracle of a target
and execute them in ONE snapshot (the working directory and import root is that snapshot).

python rq3_oracle_inner.py ARGS.json      ARGS: {"root", "pythonpath", "oracle", "n", "seed", "out", "timeout"}
For every scope of oracle.scopes(), n inputs are drawn with random.Random("<seed>:<scope>") (same inputs in every
snapshot) and oracle.execute(input) is recorded as canonical JSON, with memory addresses and line numbers masked.
"""
import importlib.util
import json
import os
import random
import re
import signal
import sys

ADDR, LINE = re.compile(r"0x[0-9a-fA-F]+"), re.compile(r"line \d+")


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


def canon(x):
    try:
        text = json.dumps(x, sort_keys=True, default=repr)
    except Exception as exc:
        text = "<unserialisable %s>" % type(exc).__name__
    return LINE.sub("line N", ADDR.sub("0x?", text))[:400]


def main(path):
    with open(path) as f:
        a = json.load(f)
    root = a["root"]
    os.chdir(root)
    for p in reversed([os.path.join(root, q) for q in a.get("pythonpath", [])] + [root]):
        sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("gk_rq3_oracle", a["oracle"])
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    signal.signal(signal.SIGALRM, _alarm)
    out = {}
    for scope, gen in sorted(oracle.scopes().items()):
        rng = random.Random("%s:%s" % (a.get("seed", 0), scope))
        draws = [gen(rng) for _ in range(int(a.get("n", 200)))]
        res = []
        for d in draws:
            signal.alarm(int(a.get("timeout", 5)))
            try:
                res.append(canon(oracle.execute(d)))
            except _Timeout:
                res.append("timeout")
            except BaseException as exc:
                res.append(canon({"raised": type(exc).__name__}))
            finally:
                signal.alarm(0)
        out[scope] = res
    with open(a["out"], "w") as f:
        json.dump({"status": "RAN", "scopes": out}, f)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
