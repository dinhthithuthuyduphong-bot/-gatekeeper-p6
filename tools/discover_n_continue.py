"""Study N frame: continue the Study M stage-S1 discovery in the SAME seed order, after the first 500 candidates.

python tools/discover_n_continue.py OUT_DIR --seed S1_SEED --exclude M_ORDERED.json [--target 800] [--max-examined 7000]

Uses the frozen functions of tools/discover_m_candidates.py unchanged (queries, windows, filters, order key).  Search
results can change between runs, so the continuation is defined by the ORDER KEY, not by a list position: only hits
whose key sha256("{seed}:{owner/repo}#{pr}") is greater than the largest key among the first 500 candidates are
examined, and none of those 500 can reappear.  The result is therefore the next part of the same ordering.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import discover_m_candidates as D  # noqa: E402  (frozen in study_m; imported, not modified)


def key_of_candidate(seed, cand):
    """Same key as D.order_key, computed from a stored candidate (repo URL + pr)."""
    repo = re.sub(r"^https://github\.com/|\.git$", "", cand["repo"])
    return D.order_key(seed, {"repository_url": "https://api.github.com/repos/" + repo, "number": cand["pr"]})


def run(out_dir, client, seed, excluded_repos, first_500, target=800, max_examined=7000, time_budget_min=330,
        windows=D.WINDOWS, queries=D.QUERIES, pages=D.PAGES, clock=time.time):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = clock()
    after = max(key_of_candidate(seed, c) for c in first_500)
    first_names = {c["name"] for c in first_500}
    log = {"version": 1, "seed": str(seed), "after_key": after, "excluded_first": len(first_500), "target": target,
           "search_hits": 0, "unique_prs": 0, "rejected_cheap": {}, "rejected_files": {}, "examined": 0, "kept": 0,
           "errors": [], "stopped_because": None, "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    hits = sorted(D.collect_hits(client, excluded_repos, log, windows, queries, pages), key=lambda it: D.order_key(seed, it))
    log["after_cheap_filters"] = len(hits)
    hits = [it for it in hits if D.order_key(seed, it) > after]
    log["after_the_first_500"] = len(hits)
    kept = []

    def checkpoint():
        log.update(api_calls=client.calls, seconds_total=round(clock() - t0), kept=len(kept))
        (out / "N_CANDIDATES.json").write_text(json.dumps(kept, indent=1))
        (out / "N_DISCOVERY_LOG.json").write_text(json.dumps(log, indent=1))

    for it in hits:
        if len(kept) >= target:
            log["stopped_because"] = "target reached"
            break
        if log["examined"] >= max_examined:
            log["stopped_because"] = "max_examined reached"
            break
        if (clock() - t0) / 60.0 > time_budget_min:
            log["stopped_because"] = "time budget"
            break
        files = client.get(it["pull_request"]["url"] + "/files?per_page=100")
        log["examined"] += 1
        if isinstance(files, dict):
            log["rejected_files"]["api error"] = log["rejected_files"].get("api error", 0) + 1
        else:
            ok, why = D.file_filter(files)
            spec = D.spec_for(it, files) if ok else None
            if ok and spec["name"] not in first_names:
                kept.append(spec)
            elif not ok:
                log["rejected_files"][why] = log["rejected_files"].get(why, 0) + 1
        if log["examined"] % 25 == 0:
            checkpoint()
    else:
        log["stopped_because"] = log["stopped_because"] or "list exhausted"
    checkpoint()
    print(json.dumps({k: log[k] for k in ("search_hits", "after_cheap_filters", "after_the_first_500", "examined", "kept", "stopped_because")}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--seed", required=True)
    ap.add_argument("--exclude", required=True)
    ap.add_argument("--target", type=int, default=800)
    ap.add_argument("--max-examined", type=int, default=7000)
    ap.add_argument("--time-budget-min", type=float, default=330)
    a = ap.parse_args(argv)
    excluded = set(json.loads((ROOT / "study_m" / "EXCLUDED_REPOS.json").read_text())["repos"])
    first = json.loads(Path(a.exclude).read_text())
    return run(a.out_dir, D.Client(os.environ.get("GITHUB_TOKEN", "")), a.seed, excluded, first, a.target, a.max_examined, a.time_budget_min)


if __name__ == "__main__":
    sys.exit(main())
