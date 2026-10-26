"""Infrastructure smoke test for the paid-model endpoints (NOT study data; costs a fraction of a cent).

python tools/vertex_smoke.py CONFIG.json OUT_DIR [--burst 5]

For every model in the B9 config whose credential environment variable is set, send BURST tiny requests built exactly
like the B9 client builds them (same path, same payload keys, same extra parameters) and record: HTTP status, latency,
served model, finish reason, usage, error body, and the cost implied by the configured prices.  It answers three
questions before any study money is spent: does the endpoint accept the pipeline's payload, how soon does the quota
push back (HTTP 429), and what do the tokens cost.  Whether the Free Trial credit pays for these calls is read from the
Cloud Billing report afterwards (Billing > Reports > Credits), not from this tool.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROMPT = [{"role": "user", "content": "Reply with the single word: ok"}]


def call(model, base_url, key, extra, opener=urllib.request.urlopen):
    payload = {"model": model["model_id"], "messages": PROMPT, "max_tokens": 16, "temperature": 0, "seed": 1, **extra}
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    t0 = time.time()
    row = {"seconds": None, "status": None}
    try:
        with opener(req, timeout=120) as r:
            data = json.loads(r.read())
            row["status"] = getattr(r, "status", 200)
            choice = (data.get("choices") or [{}])[0]
            row.update(served_model=data.get("model"), finish_reason=choice.get("finish_reason"), usage=data.get("usage"),
                       text=((choice.get("message") or {}).get("content") or "")[:40])
    except urllib.error.HTTPError as e:
        row["status"] = e.code
        row["error"] = e.read().decode("utf-8", "replace")[:500]
    except Exception as e:                                 # network, timeout, JSON
        row["error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    row["seconds"] = round(time.time() - t0, 2)
    return row


def cost_usd(usage, prices):
    if not usage or not prices:
        return None
    return (usage.get("prompt_tokens", 0) * prices["input"] + usage.get("completion_tokens", 0) * prices["output"]) / 1e6


def main(config, out_dir, burst=5, opener=urllib.request.urlopen, env=os.environ):
    cfg = json.loads(Path(config).read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = {"config": config, "burst": burst, "models": {}}
    for m in cfg["models"]:
        key = env.get(m["key_env"])
        if not key:
            result["models"][m["name"]] = {"skipped": "environment variable %s is not set" % m["key_env"]}
            continue
        base = m["base_url"].replace("{GCP_PROJECT}", env.get("GCP_PROJECT", ""))
        rows = [call(m, base, key, m.get("extra", {}), opener) for _ in range(burst)]
        total = sum(c for c in (cost_usd(r.get("usage"), m.get("prices_usd_per_mtok")) for r in rows) if c)
        result["models"][m["name"]] = {"model_id": m["model_id"], "calls": rows, "ok": sum(r["status"] == 200 for r in rows),
                                       "rate_limited": sum(r["status"] == 429 for r in rows), "implied_cost_usd": round(total, 6)}
    (out / "VERTEX_SMOKE.json").write_text(json.dumps(result, indent=1))
    lines = ["# Smoke test of the paid-model endpoints (not study data)", "", "| Model | OK | HTTP 429 | Served model | Implied cost (USD) | First error |", "|---|---|---|---|---|---|"]
    for name, r in result["models"].items():
        if "skipped" in r:
            lines.append("| %s | skipped | | | | %s |" % (name, r["skipped"]))
            continue
        err = next((x.get("error", "") for x in r["calls"] if x.get("error")), "")
        served = next((x.get("served_model") for x in r["calls"] if x.get("served_model")), "")
        lines.append("| %s | %d/%d | %d | %s | %.6f | %s |" % (name, r["ok"], burst, r["rate_limited"], served, r["implied_cost_usd"], err[:120].replace("\n", " ")))
    (out / "VERTEX_SMOKE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("out_dir")
    ap.add_argument("--burst", type=int, default=5)
    a = ap.parse_args()
    sys.exit(main(a.config, a.out_dir, a.burst))
