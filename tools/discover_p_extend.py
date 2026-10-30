"""Study P frame, part B: an EXTENDED search space, same queries, filters and seed order as Study M stage S1.

python tools/discover_p_extend.py OUT_DIR --seed S1_SEED --exclude A.json [--exclude B.json ...] [--after PREVIOUS_B.json]
                                  [--target 3000] [--max-examined 25000] [--time-budget-min 330]

Part A (already in study_p) came from the original space: 42 monthly windows 2023-01..2026-06, pages 1-2 of each query.
Part B is defined, before any vetting, as the candidates found in
    (1) pages 3-5 of the same 42 windows and queries, and
    (2) pages 1-5 of 24 new monthly windows 2021-01..2022-12,
that pass the same filters, are not in any excluded list (everything exposed, and part A), ordered by the same key.
--after continues an interrupted part B: only keys greater than the largest key in that file are examined.
Uses the frozen functions of tools/discover_m_candidates.py unchanged.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import discover_m_candidates as D  # noqa: E402
from discover_n_continue import key_of_candidate  # noqa: E402

NET_ERRORS = (OSError, ConnectionError, TimeoutError)        # includes http.client.RemoteDisconnected and urllib URLError
NET_BACKOFF = (5, 15, 45, 120)


def safe_get(client, url, search=False, sleep=time.sleep):
    """The frozen client of Study M retries only HTTP errors; a dropped connection (RemoteDisconnected) killed a 4-hour run.
    Retry network errors with truncated exponential backoff; after the last try return an error record (not an exception)."""
    for wait in NET_BACKOFF + (None,):
        try:
            return client.get(url, search=search)
        except NET_ERRORS as exc:
            if wait is None:
                return {"error": "network: %s" % type(exc).__name__}
            sleep(wait)


OLD_WINDOWS = D.WINDOWS
NEW_WINDOWS = [(y, m) for y in (2021, 2022) for m in range(1, 13)]
SPACE = [(w, (3, 4, 5)) for w in OLD_WINDOWS] + [(w, (1, 2, 3, 4, 5)) for w in NEW_WINDOWS]


def collect(client, excluded_repos, log, space=SPACE, queries=D.QUERIES):
    seen, hits = set(), []
    for (y, m), pages in space:
        lo, hi = "%04d-%02d-01" % (y, m), "%04d-%02d-28" % (y, m)
        for q in queries:
            for page in pages:
                res = safe_get(client, "%s/search/issues?q=%s&per_page=100&page=%d" % (D.API, urllib.parse.quote(q.format(lo=lo, hi=hi)), page), search=True)
                if "error" in res:
                    log["errors"].append({"window": lo, "page": page, "error": res["error"]})
                    break
                items = res.get("items", [])
                log["search_hits"] += len(items)
                for it in items:
                    url = (it.get("pull_request") or {}).get("url")
                    if not url or url in seen:
                        continue
                    seen.add(url)
                    ok, why = D.cheap_filter(it, excluded_repos)
                    if ok:
                        hits.append(it)
                    else:
                        log["rejected_cheap"][why] = log["rejected_cheap"].get(why, 0) + 1
                if len(items) < 100:
                    break
    log["unique_prs"] = len(seen)
    return hits


def run(out_dir, client, seed, excluded_repos, excluded_cands, after_cands=(), target=3000, max_examined=25000, time_budget_min=330,
        space=SPACE, queries=D.QUERIES, clock=time.time):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = clock()
    ident = lambda c: (re.sub(r"\.git$", "", c["repo"].lower()), int(c["pr"]))
    skip = {ident(c) for c in excluded_cands} | {ident(c) for c in after_cands}   # identity is repository + PR, not the name
    after = max((key_of_candidate(seed, c) for c in after_cands), default="")
    log = {"version": 1, "part": "B", "seed": str(seed), "after_key": after or None, "excluded": len(skip), "target": target,
           "space": {"old_windows_pages": "3-5", "new_windows": "2021-01..2022-12 pages 1-5"}, "search_hits": 0, "unique_prs": 0,
           "rejected_cheap": {}, "rejected_files": {}, "examined": 0, "kept": 0, "errors": [], "stopped_because": None,
           "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    hits = sorted(collect(client, excluded_repos, log, space, queries), key=lambda it: D.order_key(seed, it))
    log["after_cheap_filters"] = len(hits)
    hits = [it for it in hits if D.order_key(seed, it) > after]
    kept = []

    def checkpoint():
        log.update(api_calls=client.calls, seconds_total=round(clock() - t0), kept=len(kept))
        (out / "P_EXT_CANDIDATES.json").write_text(json.dumps(kept, indent=1))
        (out / "P_EXT_LOG.json").write_text(json.dumps(log, indent=1))

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
        files = safe_get(client, it["pull_request"]["url"] + "/files?per_page=100")
        log["examined"] += 1
        if isinstance(files, dict):
            log["rejected_files"]["api error"] = log["rejected_files"].get("api error", 0) + 1
        else:
            ok, why = D.file_filter(files)
            if ok:
                spec = D.spec_for(it, files)
                if ident(spec) in skip:
                    log["rejected_files"]["already exposed or in part A"] = log["rejected_files"].get("already exposed or in part A", 0) + 1
                else:
                    kept.append(spec)
            else:
                log["rejected_files"][why] = log["rejected_files"].get(why, 0) + 1
        if log["examined"] % 25 == 0:
            checkpoint()
    else:
        log["stopped_because"] = log["stopped_because"] or "list exhausted"
    checkpoint()
    print(json.dumps({k: log[k] for k in ("search_hits", "after_cheap_filters", "examined", "kept", "stopped_because")}))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--seed", required=True)
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--after", default=None)
    ap.add_argument("--target", type=int, default=3000)
    ap.add_argument("--max-examined", type=int, default=25000)
    ap.add_argument("--time-budget-min", type=float, default=330)
    a = ap.parse_args(argv)
    excluded_repos = set(json.loads((ROOT / "study_m" / "EXCLUDED_REPOS.json").read_text())["repos"])
    excl = [c for f in a.exclude for c in json.loads(Path(f).read_text())]
    after = json.loads(Path(a.after).read_text()) if a.after else []
    return run(a.out_dir, D.Client(os.environ.get("GITHUB_TOKEN", "")), a.seed, excluded_repos, excl, after, a.target, a.max_examined, a.time_budget_min)


if __name__ == "__main__":
    sys.exit(main())
