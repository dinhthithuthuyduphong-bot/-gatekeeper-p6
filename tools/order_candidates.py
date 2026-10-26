"""Order candidates by a seed that did not exist at freeze time (drand), so order cannot depend on any outcome.
python tools/order_candidates.py M_CANDIDATES.json SEED OUT.json [N]"""
import hashlib
import json
import sys


def order(cands, seed):
    key = lambda c: hashlib.sha256(("%s:%s#%s" % (seed, c["repo"], c["pr"])).encode()).hexdigest()
    return sorted(cands, key=key)


def main(path, seed, out, n="0"):
    ordered = order(json.load(open(path)), seed)
    if int(n):
        ordered = ordered[:int(n)]
    json.dump(ordered, open(out, "w"), indent=1)
    print(len(ordered), "candidates ordered")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))
