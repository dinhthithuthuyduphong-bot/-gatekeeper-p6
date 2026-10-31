"""Study Q-A1 with a third, model rater (stand-in for the human second rater; scorecard S8; post hoc, labelled).
python tools/qa1_three_raters.py QA1_DIR [OUT.json]
Raters: the assistant (RATINGS_ASSISTANT.json), gemini-4-argon (RATINGS_SECOND.json), gemini-3.8-flash (RATINGS_THIRD.json), each
blind and with the same codebook (tools/rq5_rate_llm.py).  Majority code per item (R if at least two raters say R, B likewise,
else U); a unit has a confirmed contract regression if some item of it is majority-R.  Reports pairwise Cohen kappa, Fleiss
kappa and the Q-A1 share recomputed with the majority rule."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p_analyze import wilson  # noqa: E402
from rq5_agreement import kappa_nominal  # noqa: E402

CATS = "RBU"


def majority(codes):
    c = Counter(codes)
    for k in "RB":
        if c[k] >= 2:
            return k
    return "U"


def fleiss(rows):
    """rows: list of per-item code lists (same number of raters).  Fleiss' kappa over categories R, B, U."""
    n_items, m = len(rows), len(rows[0])
    if n_items == 0 or m < 2:
        return None
    p_j = {k: sum(r.count(k) for r in rows) / (n_items * m) for k in CATS}
    p_i = [(sum(r.count(k) ** 2 for k in CATS) - m) / (m * (m - 1)) for r in rows]
    p_bar, p_e = sum(p_i) / n_items, sum(v * v for v in p_j.values())
    return None if p_e == 1 else (p_bar - p_e) / (1 - p_e)


def report(d):
    d = Path(d)
    repro = json.loads((d / "REPRO.json").read_text())["units"]
    key = {k["id"]: k for k in json.loads((d / "KEY.json").read_text())}
    raters = {"assistant": {r["id"]: r["code"] for r in json.loads((d / "RATINGS_ASSISTANT.json").read_text())}}
    for name, f in (("argon", "RATINGS_SECOND.json"), ("flash", "RATINGS_THIRD.json")):
        raters[name] = {r["id"]: r["code"] for r in json.loads((d / f).read_text())["ratings"]}
    ids = sorted(key)
    missing = [i for i in ids if any(i not in r for r in raters.values())]
    if missing:
        raise SystemExit("items without three codes: %s" % missing[:5])
    names = list(raters)
    rows = [[raters[n][i] for n in names] for i in ids]
    maj = {i: majority(r) for i, r in zip(ids, rows)}
    pair = {"%s~%s" % (a, b): {"agreement": sum(raters[a][i] == raters[b][i] for i in ids) / len(ids),
                               "kappa": kappa_nominal([raters[a][i] for i in ids], [raters[b][i] for i in ids])}
            for k, a in enumerate(names) for b in names[k + 1:]}
    confirmed = sorted({key[i]["instance_id"] for i in ids if maj[i] == "R"})
    reproduced = [u for u in repro if u["reproduced"]]
    nr = len(reproduced)
    without = sum(1 for u in reproduced if u["instance_id"] not in confirmed)
    return {"items": len(ids), "raters": {n: dict(Counter(raters[n][i] for i in ids)) for n in names},
            "pairwise": pair, "fleiss_kappa": fleiss(rows), "unanimous": sum(len(set(r)) == 1 for r in rows),
            "majority_codes": dict(Counter(maj.values())),
            "units_with_majority_regression": len(confirmed),
            "without_majority_regression": {"k": without, "n": nr, "share": without / nr if nr else None,
                                            "wilson95": wilson(without, nr) if nr else None},
            "note": "post hoc; the third rater is a model (gemini-3.8-flash), not a human"}


def main(argv):
    res = report(argv[0])
    out = Path(argv[1]) if len(argv) > 1 else Path(argv[0]) / "QA1_THREE_RATERS.json"
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
