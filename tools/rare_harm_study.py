"""Study U (study_u/PROTOCOL.md): rare partial harm in resolved SWE-bench Verified agent patches (Study Q records).  No new runs.

python tools/rare_harm_study.py OUT_DIR

Per scored patch: n stable inputs, k harmful (contract regression; naive difference as secondary).  Inputs were generated i.i.d.,
so given (n, k) the harmful positions are exchangeable: a seeded permutation splits them into gate draws (first half) and
reference draws (second half).  Decision rules read the gate draws; the ground truth reads the reference draws.
"""
import gzip
import hashlib
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import market_analyze as MA  # noqa: E402  (same harm certificate, e-Holm and thresholds as Study T)
from gatekeeper_lite.eprocess import e_holm  # noqa: E402

Q = ROOT / "research_closure/results/study_q/Q_RECORDS.jsonl.gz"
ETA, ALPHA = MA.ETA, MA.ALPHA


def patches(harm_key):
    for line in gzip.open(Q, "rt"):
        r = json.loads(line)
        for p in r.get("patches", []):
            if p.get("status") != "SCORED" or not p.get("complete"):
                continue
            c = p.get("classified", {})
            k = c.get("contract_harm") if harm_key == "contract" else c.get("divergent")
            if k is None:
                continue
            yield {"instance": r["instance_id"], "repo": r["repo"], "sha": p["sha"], "n": int(p["complete"]), "k": int(k)}


def split(p):
    seq = [1] * p["k"] + [0] * (p["n"] - p["k"])
    rng = random.Random(int(hashlib.sha256(("study-u:" + p["sha"]).encode()).hexdigest(), 16))
    rng.shuffle(seq)
    h = len(seq) // 2
    return seq[:h], seq[h:]


def study(harm_key):
    rows = []
    ps = list(patches(harm_key))
    kc = len(ps)
    n_fs = math.ceil(math.log(ALPHA / kc) / math.log(1 - ETA))
    for p in ps:
        gate, ref = split(p)
        rate = sum(ref) / len(ref)
        e, used = MA.gatekeeper(gate, kc)
        rows.append({"patch": p["sha"][:12], "instance": p["instance"], "repo": p["repo"], "n": p["n"], "k": p["k"], "ref_rate": rate,
                     "harmful": rate >= ETA, "e": e, "g_draws": used, "U": True, "S20": not any(gate[:20]),
                     "FS": len(gate) >= n_fs and not any(gate[:n_fs]), "B8": not any(gate)})
    adm = set(e_holm({r["patch"] + r["instance"]: r["e"] for r in rows}, ALPHA))
    for r in rows:
        r["G"] = (r["patch"] + r["instance"]) in adm
    rules = ["U", "S20", "FS", "B8", "G"]
    sc = {x: {"harmful_admitted": sum(1 for r in rows if r[x] and r["harmful"]),
              "safe_admitted": sum(1 for r in rows if r[x] and not r["harmful"])} for x in rules}
    band = [r for r in rows if r["harmful"] and r["ref_rate"] < 0.20]
    bsc = {x: sum(1 for r in band if r[x]) for x in rules}
    h = sum(r["harmful"] for r in rows)
    res = {"harm": harm_key, "patches": kc, "harmful": h, "safe": kc - h, "fs_draws": n_fs, "scores": sc,
           "band_5_20": {"patches": len(band), "admitted": bsc},
           "mean_draws": {"G": sum(r["g_draws"] for r in rows) / kc, "S20": 20, "FS": n_fs,
                          "B8": sum(len(split(p)[0]) for p in ps) / kc},
           "U1": sc["G"]["harmful_admitted"] <= math.ceil(ALPHA * h) and sc["G"]["harmful_admitted"] < sc["S20"]["harmful_admitted"]
           and sc["G"]["harmful_admitted"] < sc["U"]["harmful_admitted"],
           "U2": sc["G"]["safe_admitted"] >= max(sc["FS"]["safe_admitted"], sc["B8"]["safe_admitted"]),
           "U3": bsc["G"] < bsc["S20"], "rows": rows}
    return res


def main(argv):
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    res = {k: study(k) for k in ("contract", "naive")}
    (out / "STUDY_U_RESULT.json").write_text(json.dumps(res, indent=1))
    for k, r in res.items():
        print(json.dumps({x: r[x] for x in r if x != "rows"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
