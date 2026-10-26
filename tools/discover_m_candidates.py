"""Study M stage S1: outcome-blind discovery of bug-fix pull requests (read-only GitHub search, 0 cost).

python tools/discover_m_candidates.py OUT_DIR           (needs GITHUB_TOKEN for rate limits)

Nothing here looks at test outcomes, skills or patches.  Queries, windows and filters are fixed in
study_m/INCLUSION_RULES.md and frozen before the run; every step's counts are written to the log.
"""
import json
import os
import re
import sys
import time
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


def passes_filters(pr, files, excluded):
    """Return (ok, reason).  pr: pull request json; files: list of file dicts from the API."""
    repo = pr["base"]["repo"]["full_name"].lower()
    if repo in excluded:
        return False, "repository already used or exposed"
    if pr.get("draft") or not pr.get("merged_at") or not pr.get("merge_commit_sha"):
        return False, "not merged"
    if TITLE_EXCLUDE.search(pr.get("title", "")):
        return False, "title looks like maintenance, not a bug fix"
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


def _get(url, token):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "gatekeeper-m",
                                               **({"Authorization": "Bearer " + token} if token else {})})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 4:
                time.sleep(40 * (attempt + 1))
                continue
            return {"error": "HTTP %d" % e.code}
    return {"error": "rate limited"}


def spec_for(pr, files):
    repo = pr["base"]["repo"]["full_name"]
    return {"name": re.sub(r"[^a-z0-9]+", "_", repo.split("/")[1].lower())[:24] + "_pr%d" % pr["number"], "family": "general bug fix",
            "role": "cohort candidate (vetting decides)", "repo": "https://github.com/%s.git" % repo, "default_branch": "HEAD",
            "python": "3.12", "extras": ["test", "dev"], "pr": pr["number"], "gold": "PR_MERGE", "pre": "merge-base",
            "evidence": "%s (%s)" % (pr["title"][:120], pr["html_url"]),
            "changed": [{"file": f["filename"], "additions": f.get("additions"), "deletions": f.get("deletions")} for f in files]}


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("GITHUB_TOKEN", "")
    excluded = set(json.loads((ROOT / "study_m" / "EXCLUDED_REPOS.json").read_text())["repos"])
    log = {"queries": QUERIES, "windows": len(WINDOWS), "pages": PAGES, "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "search_hits": 0, "unique_prs": 0, "rejected": {}, "kept": 0, "errors": []}
    seen, kept = set(), []
    for (y, m) in WINDOWS:
        lo = "%04d-%02d-01" % (y, m)
        hi = "%04d-%02d-28" % (y, m)
        for q in QUERIES:
            for page in range(1, PAGES + 1):
                res = _get("%s/search/issues?q=%s&per_page=100&page=%d" % (API, urllib.parse.quote(q.format(lo=lo, hi=hi)), page), token)
                if "error" in res:
                    log["errors"].append({"q": q, "window": lo, "page": page, "error": res["error"]})
                    break
                items = res.get("items", [])
                log["search_hits"] += len(items)
                for it in items:
                    url = (it.get("pull_request") or {}).get("url")
                    if not url or url in seen:
                        continue
                    seen.add(url)
                    pr = _get(url, token)
                    files = _get(url + "/files?per_page=100", token)
                    if "error" in pr or isinstance(files, dict):
                        log["rejected"]["api error"] = log["rejected"].get("api error", 0) + 1
                        continue
                    ok, why = passes_filters(pr, files, excluded)
                    if ok:
                        kept.append(spec_for(pr, files))
                    else:
                        log["rejected"][why] = log["rejected"].get(why, 0) + 1
                if len(items) < 100:
                    break
    log["unique_prs"], log["kept"] = len(seen), len(kept)
    (out / "M_CANDIDATES.json").write_text(json.dumps(kept, indent=1))
    (out / "M_DISCOVERY_LOG.json").write_text(json.dumps(log, indent=1))
    print(json.dumps({k: log[k] for k in ("search_hits", "unique_prs", "kept")}), "errors:", len(log["errors"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
