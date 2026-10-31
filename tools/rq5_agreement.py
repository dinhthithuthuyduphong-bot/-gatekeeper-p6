"""RQ5 step 3: agreement of the two raters and the confirmed regressions.
python tools/rq5_agreement.py ITEMS.json ASSISTANT.json SECOND.json RQ5_CLASSIFIED.json OUT_DIR"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p_analyze import wilson  # noqa: E402


def kappa_nominal(a, b, cats=("R", "B", "U")):
    """Cohen (1960) kappa for two raters and nominal categories; None when chance agreement is 1 (no variation)."""
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return None if pe == 1 else (po - pe) / (1 - pe)


def main(items_p, a_p, b_p, cls_p, out):
    items = {i["id"]: i for i in json.loads(Path(items_p).read_text())}
    a = {r["id"]: r["code"] for r in json.loads(Path(a_p).read_text())}
    sec = json.loads(Path(b_p).read_text())
    b = {r["id"]: r["code"] for r in sec["ratings"]}
    ids = sorted(items)
    ca, cb = [a[i] for i in ids], [b[i] for i in ids]
    confirmed = sorted({items[i]["patch"] for i in ids if a[i] == "R" and b[i] == "R"})
    cls = json.loads(Path(cls_p).read_text())
    in_band_c1 = {p["name"] for p in cls["patches"] if p["reproduced"] and p["in_band_c1"]}
    planned = sorted(p for p in confirmed if p in in_band_c1)
    res = {"items": len(ids), "agreement": sum(x == y for x, y in zip(ca, cb)) / len(ids), "kappa": kappa_nominal(ca, cb),
           "codes_assistant": {c: ca.count(c) for c in "RBU"}, "codes_second": {c: cb.count(c) for c in "RBU"},
           "disagreements": [{"id": i, "assistant": a[i], "second": b[i]} for i in ids if a[i] != b[i]],
           "confirmed_patches": confirmed, "second_rater_model": sec.get("model"), "second_rater_spent_usd": sec.get("spent_usd"),
           "planned_confirmed_in_band": {"patches": planned, "share_of_205": len(planned) / 205, "wilson95": wilson(len(planned), 205) if planned else None}}
    Path(out).mkdir(parents=True, exist_ok=True)
    (Path(out) / "RQ5_AGREEMENT.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:6]))
