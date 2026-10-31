"""RQ5 step 3, second rater (plan: research_closure/results/rq5/RQ5_PLAN.md): the strong model codes each review item
R / B / U, BLIND to the item's category, origin and the study's hypotheses.  One call per item, temperature 0.
python tools/rq5_rate_llm.py ITEMS.json OUT.json MODELS.json [MODEL_NAME=vertex-gemini-argon] [CAP_USD=2]"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from gatekeeper_lite import b9  # noqa: E402

CODEBOOK = """You compare two versions of one Python function on the same input: the REFERENCE version (the developers' fix)
and a CANDIDATE version (a patch). You see the candidate's change as a diff, the reference's output and the candidate's
output on that input (["ok", type, repr] for a returned value, ["exc", exception type, message] for a raised exception;
memory addresses are masked as 0x?). The input itself is not available.

Code the difference with exactly one letter:
R = a meaningful difference in the function's behaviour (a different value, a crash where the reference returns, a value
    where the reference raises, a different kind of failure) that a caller could observe and act on;
B = only a difference of representation without meaning (order of an unordered collection, floating-point noise below
    1e-9, whitespace, the text of a message for the same kind of failure);
U = cannot be decided from what is shown.

Reply with JSON only: {"code": "R" | "B" | "U", "reason": "<one sentence>"}"""


def prompt(item):
    return ("Function: %s (file %s)\n\nCandidate change:\n```diff\n%s\n```\n\nReference output: %s\nCandidate output: %s"
            % (item["function"], item["file"], item["diff"][:3000], json.dumps(item["reference_output"]), json.dumps(item["patch_output"])))


def parse(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
    except ValueError:
        d = {}
    code = d.get("code") if d.get("code") in ("R", "B", "U") else "U"
    return code, str(d.get("reason", ""))[:300]


def rate(items, client, model_id, prices, cap):
    guard = b9.SpendGuard(cap)
    out = []
    for it in items:
        msgs = [{"role": "system", "content": CODEBOOK}, {"role": "user", "content": prompt(it)}]
        guard.check(msgs, 2000, prices)
        r = client.complete(model_id, msgs, 2000, 0.0, 1)
        guard.add(r["usage"], prices)
        code, reason = parse(r["text"])
        out.append({"id": it["id"], "code": code, "reason": reason})
    return out, guard.spent_usd


def main(argv):
    items_path, out_path, models_path = argv[:3]
    name = argv[3] if len(argv) > 3 else "vertex-gemini-argon"
    cap = float(argv[4]) if len(argv) > 4 else 2.0
    from cohort_inner import RefreshingClient
    cfg = next(m for m in json.loads(Path(models_path).read_text())["models"] if m["name"] == name)
    client = RefreshingClient(cfg["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", "")), cfg["key_env"], cfg.get("extra", {}))
    items = json.loads(Path(items_path).read_text())
    blind = [{k: it[k] for k in ("id", "function", "file", "diff", "reference_output", "patch_output")} for it in items]   # no origin, no category
    ratings, spent = rate(blind, client, cfg["model_id"], cfg["prices_usd_per_mtok"], cap)
    Path(out_path).write_text(json.dumps({"model": cfg["model_id"], "spent_usd": spent, "ratings": ratings}, indent=1))
    print(json.dumps({"items": len(ratings), "spent_usd": round(spent, 4)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
