"""Study Q amendment Q-A1, step 3 report: agreement of the two raters and the share of HQ1 units WITHOUT a confirmed
contract regression (descriptive; written after the main result).
python tools/q_review_agreement.py QA1_DIR [OUT.json]
QA1_DIR holds REPRO.json, KEY.json, RATINGS_ASSISTANT.json (list of {id, code, reason}) and RATINGS_SECOND.json
({"ratings": [...]}, tools/rq5_rate_llm.py)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p_analyze import wilson  # noqa: E402
from rq5_agreement import kappa_nominal  # noqa: E402


def report(d):
    d = Path(d)
    repro = json.loads((d / "REPRO.json").read_text())["units"]
    key = {k["id"]: k for k in json.loads((d / "KEY.json").read_text())}
    a = {r["id"]: r["code"] for r in json.loads((d / "RATINGS_ASSISTANT.json").read_text())}
    s2 = json.loads((d / "RATINGS_SECOND.json").read_text())
    b = {r["id"]: r["code"] for r in s2["ratings"]}
    ids = sorted(key)
    missing = [i for i in ids if i not in a or i not in b]
    if missing:
        raise SystemExit("items without both codes: %s" % missing[:5])
    ca, cb = [a[i] for i in ids], [b[i] for i in ids]
    agree = sum(x == y for x, y in zip(ca, cb))
    confirmed = sorted({key[i]["instance_id"] for i in ids if a[i] == "R" and b[i] == "R"})
    units = len(repro)
    reproduced = [u for u in repro if u["reproduced"]]
    nr = len(reproduced)
    without = sum(1 for u in reproduced if u["instance_id"] not in confirmed)
    lost = units - nr
    res = {
        "items": len(ids), "agreement": agree, "agreement_share": agree / len(ids) if ids else None,
        "kappa": kappa_nominal(ca, cb) if ids else None,
        "codes_assistant": {c: ca.count(c) for c in "RBU"}, "codes_second": {c: cb.count(c) for c in "RBU"},
        "second_rater_model": s2.get("model"), "second_rater_usd": s2.get("spent_usd"),
        "hq1_units": units, "reproduced": nr, "not_reproduced": lost,
        "units_with_confirmed_contract_regression": len(confirmed), "confirmed_units": confirmed,
        "without_confirmed_regression": {"k": without, "n": nr, "share": without / nr if nr else None,
                                         "wilson95": wilson(without, nr) if nr else None},
        "bounds_over_all_units": {"low": without / units if units else None, "high": (without + lost) / units if units else None},
        "cohort_reference": "HQ1 as registered: 6/55 without a contract regression (STUDY_Q_RESULT.md)",
    }
    return res


def main(argv):
    res = report(argv[0])
    out = Path(argv[1]) if len(argv) > 1 else Path(argv[0]) / "QA1_RESULT.json"
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("items", "agreement", "kappa", "reproduced", "units_with_confirmed_contract_regression",
                                          "without_confirmed_regression")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
