"""Calibration of the model raters (scorecard S8): 20 synthetic review items with a KNOWN code (10 B, 10 R), coded blind by a
model with the unchanged codebook and prompt of tools/rq5_rate_llm.py.  A rater that codes known-B items as R cannot tell a
representation difference from a behaviour difference, and its agreement on Q-A1 items is then uninformative.
python tools/rater_calibration.py OUT_DIR MODELS.json MODEL [CAP_USD=0.5]"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rq5_rate_llm as R  # noqa: E402

DIFF = "--- a/m.py\n+++ b/m.py\n@@ -1,3 +1,3 @@\n def f(x):\n-    return old(x)\n+    return new(x)\n"
B_ITEMS = [  # representation-only differences
    (["ok", "set", "{1, 2, 3}"], ["ok", "set", "{3, 1, 2}"]),
    (["ok", "float", "0.30000000000000004"], ["ok", "float", "0.3"]),
    (["exc", "ValueError", "invalid literal for int(): 'a'"], ["exc", "ValueError", "cannot convert 'a' to int"]),
    (["ok", "frozenset", "frozenset({'a', 'b'})"], ["ok", "frozenset", "frozenset({'b', 'a'})"]),
    (["ok", "str", "'a b'"], ["ok", "str", "'a b'"]),
    (["exc", "TypeError", "unsupported operand type(s) for +: 'int' and 'str'"], ["exc", "TypeError", "can only add int to int"]),
    (["ok", "float", "1.0000000000000002"], ["ok", "float", "1.0"]),
    (["ok", "dict", "{'b': 1, 'a': 2}"], ["ok", "dict", "{'a': 2, 'b': 1}"]),
    (["exc", "KeyError", "'x'"], ["exc", "KeyError", "\"key 'x' not found\""]),
    (["ok", "set", "{'x', 'y'}"], ["ok", "set", "{'y', 'x'}"]),
]
R_ITEMS = [  # behaviour differences
    (["ok", "int", "3"], ["ok", "int", "4"]),
    (["ok", "NoneType", "None"], ["exc", "AttributeError", "'NoneType' object has no attribute 'x'"]),
    (["exc", "ValueError", "negative"], ["ok", "int", "-1"]),
    (["ok", "bool", "True"], ["ok", "bool", "False"]),
    (["ok", "list", "[1, 2]"], ["ok", "list", "[2, 1]"]),
    (["ok", "str", "'abc'"], ["ok", "str", "'ab'"]),
    (["exc", "TypeError", "expected str"], ["exc", "ValueError", "bad value"]),
    (["ok", "int", "0"], ["exc", "ZeroDivisionError", "division by zero"]),
    (["ok", "dict", "{'a': 1}"], ["ok", "dict", "{}"]),
    (["ok", "float", "0.5"], ["ok", "float", "0.25"]),
]


def items():
    out = []
    for code, rows in (("B", B_ITEMS), ("R", R_ITEMS)):
        for k, (ref, pat) in enumerate(rows):
            out.append({"id": "cal-%s-%02d" % (code, k), "known": code, "function": "f", "file": "m.py", "diff": DIFF,
                        "reference_output": ref, "patch_output": pat})
    return out


def score(its, ratings):
    got = {r["id"]: r["code"] for r in ratings}
    res = {}
    for code in "BR":
        sel = [i for i in its if i["known"] == code]
        res[code] = {"items": len(sel), "coded_as": {c: sum(got[i["id"]] == c for i in sel) for c in "RBU"}}
    res["accuracy"] = sum(got[i["id"]] == i["known"] for i in its) / len(its)
    res["discriminates"] = res["B"]["coded_as"]["B"] > 0
    return res


def main(argv):
    out, models_path, name = Path(argv[0]), argv[1], argv[2]
    cap = float(argv[3]) if len(argv) > 3 else 0.5
    from cohort_inner import RefreshingClient
    cfg = next(m for m in json.loads(Path(models_path).read_text())["models"] if m["name"] == name)
    client = RefreshingClient(cfg["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", "")), cfg["key_env"], cfg.get("extra", {}))
    its = items()
    blind = [{k: it[k] for k in ("id", "function", "file", "diff", "reference_output", "patch_output")} for it in its]
    ratings, spent = R.rate(blind, client, cfg["model_id"], cfg["prices_usd_per_mtok"], cap)
    res = {"model": cfg["model_id"], "spent_usd": spent, **score(its, ratings), "ratings": ratings}
    out.mkdir(parents=True, exist_ok=True)
    (out / ("RATER_CALIBRATION_%s.json" % name)).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("model", "B", "R", "accuracy", "discriminates", "spent_usd")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
