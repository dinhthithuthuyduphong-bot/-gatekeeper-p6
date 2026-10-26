"""Study M stage S1: outcome-blind discovery of bug-fix pull requests (read-only GitHub search, 0 cost).

python tools/discover_m_candidates.py OUT_DIR --seed SEED [--target 500] [--max-examined 3500] [--start 0] [--time-budget-min 330]

Nothing here looks at test outcomes, skills or patches.  Queries, windows and filters are those of
study_m/INCLUSION_RULES.md.  Version 2 (amendment M-A2): the first version made two API calls for every hit
and wrote its outputs only at the end, so it could not finish within the GITHUB_TOKEN rate limit and left nothing
behind.  Now: (1) cheap filters use only fields of the search result; (2) hits are ordered by sha256(seed:repo#pr)
BEFORE the expensive step, and the changed-file filters are evaluated lazily in that order, which yields exactly the
prefix of the ordered passing list that the original procedure would have produced; (3) one API call per examined PR;
(4) the client waits for the rate-limit reset; (5) a checkpoint is written every 25 examined PRs.
"""
import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.github.com"
WINDOWS = [(y, m) for y in (2023, 2024, 2025) for m in range(1, 13)] + [(2026, m) for m in range(1, 7)]
QUERIES = ['fix in:title is:pr is:merged language:Python created:{lo}..{hi}',
           'bug in:title is:pr is:merged language:Python created:{lo}..{hi}']
PAGES = 2
TITLE_EXCLUDE = re.compile(r"\b(typo|docs?|documentation|readme|ci|bump|lint|format|formatting|style|refactor|deps?|dependenc\w*|release|changelog|"
                           r"pre-commit|black|ruff|flake8|mypy|typing|type hints?|spelling|license|merge)\b", re.I)
MAX_FILES, MAX_SRC_LINES = 8, 60
TEST_PATH = re.compile(r"(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)tests\.py$")


class Client:
    """GitHub REST client that respects rate limits (injectable for tests)."""

    def __init__(self, token, opener=urllib.request.urlopen, sleep=time.sleep, clock=time.time):
        self.token, self.opener, self.sleep, self.clock, self.calls, self.waited = token, opener, sleep, clock, 0, 0.0
        self._last_search = 0.0

    def _wait(self, seconds):
        seconds = max(0.0, min(float(seconds), 3700.0))
        self.waited += seconds
        self.sleep(seconds)

    def _until_reset(self, headers):
        reset = headers.get("X-RateLimit-Reset") if headers else None
        return (float(reset) - self.clock() + 5.0) if reset else 60.0

    def get(self, url, search=False):
        if search:                                      # the search API allows 30 requests per minute
            gap = 2.5 - (self.clock() - self._last_search)
            if gap > 0:
                self._wait(gap)
            self._last_search = self.clock()
        headers_in = {"Accept": "application/vnd.github+json", "User-Agent": "gatekeeper-m"}
        if self.token:
            headers_in["Authorization"] = "Bearer " + self.token
        for _ in range(8):
            try:
                self.calls += 1
                with self.opener(urllib.request.Request(url, headers=headers_in), timeout=60) as r:
                    body = json.loads(r.read())
                    remaining = r.headers.get("X-RateLimit-Remaining")
                    if remaining is not None and int(remaining) < 3:
                        self._wait(self._until_reset(r.headers))
                    return body
            except urllib.error.HTTPError as e:
                if e.code in (403, 429):
                    self._wait(self._until_reset(e.headers))
                    continue
                return {"error": "HTTP %d" % e.code}
        return {"error": "rate limited"}


def repo_of(item):
    return item["repository_url"].rsplit("/repos/", 1)[-1]


def cheap_filter(item, excluded):
    """Filters (a)-(c) of INCLUSION_RULES.md using only fields of the search result."""
    pr = item.get("pull_request") or {}
    if repo_of(item).lower() in excluded:
        return False, "repository already used or exposed"
    if item.get("draft") or not pr.get("merged_at"):
        return False, "not merged"
    if TITLE_EXCLUDE.search(item.get("title", "")):
        return False, "title looks like maintenance, not a bug fix"
    return True, "ok"


def file_filter(files):
    """Filters (d)-(h) of INCLUSION_RULES.md (they need the list of changed files)."""
    if len(files) == 0 or len(files) > MAX_FILES:
        return False, "number of changed files outside 1..%d" % MAX_FILES
    py = [f for f in files if f["filename"].endswith(".py")]
    tests = [f for f in py if TEST_PATH.search(f["filename"])]
    src = [f for f in py if not TEST_PATH.search(f["filename"])]
    if not src:
        return False, "no non-test python source file changed"
    if not tests:
        return False, "no test file changed (no upstream oracle)"
    if sum(f.get("additions", 0) + f.get("deletions", 0) for f in src) > MAX_SRC_LINES:
        return False, "source diff larger than %d lines" % MAX_SRC_LINES
    if any(f.get("status") in ("removed", "renamed") for f in src):
        return False, "source file removed or renamed"
    return True, "ok"


def passes_filters(item, files, excluded):
    ok, why = cheap_filter(item, excluded)
    return (file_filter(files) if ok else (ok, why))


def order_key(seed, item):
    return hashlib.sha256(("%s:%s#%s" % (seed, repo_of(item), item["number"])).encode()).hexdigest()


def spec_for(item, files):
    repo = repo_of(item)
    return {"name": re.sub(r"[^a-z0-9]+", "_", repo.split("/")[1].lower())[:24] + "_pr%d" % item["number"], "family": "general bug fix",
            "role": "cohort candidate (vetting decides)", "repo": "https://github.com/%s.git" % repo, "default_branch": "HEAD",
            "python": "3.12", "extras": ["test", "dev"], "pr": item["number"], "gold": "PR_MERGE", "pre": "merge-base",
            "evidence": "%s (%s)" % (item["title"][:120], item["html_url"]),
            "changed": [{"file": f["filename"], "additions": f.get("additions"), "deletions": f.get("deletions")} for f in files]}


def collect_hits(client, excluded, log, windows=WINDOWS, queries=QUERIES, pages=PAGES):
    seen, hits = set(), []
    for (y, m) in windows:
        lo, hi = "%04d-%02d-01" % (y, m), "%04d-%02d-28" % (y, m)
        for q in queries:
            for page in range(1, pages + 1):
                res = client.get("%s/search/issues?q=%s&per_page=100&page=%d" % (API, urllib.parse.quote(q.format(lo=lo, hi=hi)), page), search=True)
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
                    ok, why = cheap_filter(it, excluded)
                    if ok:
                        hits.append(it)
                    else:
                        log["rejected_cheap"][why] = log["rejected_cheap"].get(why, 0) + 1
                if len(items) < 100:
                    break
    log["unique_prs"] = len(seen)
    return hits


def run(out_dir, client, seed, excluded, target=500, max_examined=3500, start=0, time_budget_min=330,
        windows=WINDOWS, queries=QUERIES, pages=PAGES, clock=time.time):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = clock()
    log = {"version": 2, "queries": queries, "windows": len(windows), "pages": pages, "seed": str(seed), "target": target,
           "max_examined": max_examined, "start": start, "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "search_hits": 0, "unique_prs": 0, "rejected_cheap": {}, "rejected_files": {}, "examined": 0, "kept": 0,
           "errors": [], "stopped_because": None}
    hits = sorted(collect_hits(client, excluded, log, windows, queries, pages), key=lambda it: order_key(seed, it))
    log["after_cheap_filters"] = len(hits)
    kept = []

    def checkpoint():
        log.update(api_calls=client.calls, seconds_waiting=round(client.waited), seconds_total=round(clock() - t0))
        (out / "M_CANDIDATES.json").write_text(json.dumps(kept, indent=1))
        (out / "M_ORDERED.json").write_text(json.dumps(kept, indent=1))
        (out / "M_DISCOVERY_LOG.json").write_text(json.dumps(log, indent=1))

    for pos in range(start, len(hits)):
        if len(kept) >= target:
            log["stopped_because"] = "target reached"
            break
        if log["examined"] >= max_examined:
            log["stopped_because"] = "max_examined reached"
            break
        if (clock() - t0) / 60.0 > time_budget_min:
            log["stopped_because"] = "time budget"
            break
        it = hits[pos]
        files = client.get((it["pull_request"]["url"]) + "/files?per_page=100")
        log["examined"] += 1
        log["next_position"] = pos + 1
        if isinstance(files, dict):
            log["rejected_files"]["api error"] = log["rejected_files"].get("api error", 0) + 1
        else:
            ok, why = file_filter(files)
            if ok:
                kept.append(spec_for(it, files))
            else:
                log["rejected_files"][why] = log["rejected_files"].get(why, 0) + 1
        log["kept"] = len(kept)
        if log["examined"] % 25 == 0:
            checkpoint()
    else:
        log["stopped_because"] = log["stopped_because"] or "list exhausted"
    log["kept"] = len(kept)
    checkpoint()
    print(json.dumps({k: log[k] for k in ("search_hits", "unique_prs", "after_cheap_filters", "examined", "kept", "stopped_because")}), "errors:", len(log["errors"]))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--seed", required=True)
    ap.add_argument("--target", type=int, default=500)
    ap.add_argument("--max-examined", type=int, default=3500)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--time-budget-min", type=float, default=330)
    a = ap.parse_args(argv)
    import os
    excluded = set(json.loads((ROOT / "study_m" / "EXCLUDED_REPOS.json").read_text())["repos"])
    return run(a.out_dir, Client(os.environ.get("GITHUB_TOKEN", "")), a.seed, excluded, a.target, a.max_examined, a.start, a.time_budget_min)


if __name__ == "__main__":
    sys.exit(main())
