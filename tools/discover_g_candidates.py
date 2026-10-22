"""Study G candidate discovery (read-only, 0 cost): GitHub search for
  (a) merged PRs that rewrite `== None` / `!= None` into `is None` / `is not None`
      (candidate BENEFICIAL targets; vetting later checks for a fail-before/pass-after test),
  (b) code that keeps `== None` deliberately and says so (`# noqa: E711`), typically ORM or
      DSL expressions (candidate HARMFUL targets with an explicit-intent oracle).
Every query, hit and exclusion reason is recorded, so the selection can be audited.
python tools/discover_g_candidates.py out_dir      (needs GITHUB_TOKEN for rate limits)
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
PR_QUERIES = [
    '"is None" "== None" is:pr is:merged language:Python',
    '"E711" is:pr is:merged language:Python',
    '"comparison to None" is:pr is:merged language:Python',
    '"use is None" is:pr is:merged language:Python',
]
CODE_QUERIES = [
    '"noqa: E711" language:Python',
    '"== None  # noqa" sqlalchemy language:Python',
]
REWRITE = re.compile(r"^-.*[!=]=\s*None", re.M)
FIXED = re.compile(r"^\+.*\bis(\s+not)?\s+None", re.M)


def get(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "gatekeeper-g",
                                               **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
                                                  if os.environ.get("GITHUB_TOKEN") else {})})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt < 3:
                time.sleep(30 * (attempt + 1))
                continue
            return {"error": f"HTTP {e.code}", "items": []}
    return {"error": "rate limited", "items": []}


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rec = {"pr_queries": {}, "code_queries": {}, "beneficial_candidates": [], "harmful_candidates": [], "excluded": []}
    seen = set()
    for q in PR_QUERIES:
        res = get(f"{API}/search/issues?q={urllib.parse.quote(q)}&per_page=50&sort=updated")
        rec["pr_queries"][q] = {"total": res.get("total_count"), "error": res.get("error")}
        for it in res.get("items", []):
            pr_url = it.get("pull_request", {}).get("url")
            if not pr_url or pr_url in seen:
                continue
            seen.add(pr_url)
            files = get(pr_url + "/files?per_page=100")
            if isinstance(files, dict):
                rec["excluded"].append({"pr": it["html_url"], "reason": files.get("error", "no files")})
                continue
            py = [f for f in files if f["filename"].endswith(".py")]
            src = [f for f in py if not re.search(r"(^|/)(tests?|testing)/|(^|/)test_", f["filename"])]
            tst = [f for f in py if f not in src]
            rewrites = sum(len(REWRITE.findall(f.get("patch", ""))) for f in src)
            fixed = sum(len(FIXED.findall(f.get("patch", ""))) for f in src)
            entry = {"pr": it["html_url"], "title": it["title"][:120], "repo": it["repository_url"].split("/repos/")[1],
                     "source_files": [f["filename"] for f in src][:10], "test_files": [f["filename"] for f in tst][:10],
                     "none_rewrites": min(rewrites, fixed), "changed_files": len(files)}
            if entry["none_rewrites"] == 0:
                rec["excluded"].append({"pr": entry["pr"], "reason": "no == None -> is None rewrite in source files"})
            elif not tst:
                rec["excluded"].append({"pr": entry["pr"], "reason": "no test file changed (no upstream oracle)"})
            elif len(files) > 30:
                rec["excluded"].append({"pr": entry["pr"], "reason": "too large to isolate the rewrite (>30 files)"})
            else:
                rec["beneficial_candidates"].append(entry)
    for q in CODE_QUERIES:
        res = get(f"{API}/search/code?q={urllib.parse.quote(q)}&per_page=50")
        rec["code_queries"][q] = {"total": res.get("total_count"), "error": res.get("error")}
        for it in res.get("items", []):
            rec["harmful_candidates"].append({"repo": it["repository"]["full_name"], "path": it["path"],
                                              "url": it["html_url"]})
    by_repo = {}
    for h in rec["harmful_candidates"]:
        by_repo.setdefault(h["repo"], []).append(h["path"])
    rec["harmful_by_repo"] = {r: sorted(set(p))[:10] for r, p in sorted(by_repo.items(), key=lambda kv: -len(kv[1]))}
    (out / "G_CANDIDATES.json").write_text(json.dumps(rec, indent=2))
    lines = ["# Study G — ứng viên (tìm kiếm chỉ đọc)", "",
             f"Ứng viên có lợi: {len(rec['beneficial_candidates'])}; bị loại: {len(rec['excluded'])}; "
             f"repo có `noqa: E711`: {len(rec['harmful_by_repo'])}", "",
             "## Có lợi (PR đã merge, có đổi test)", "", "| PR | Repo | Số chỗ đổi | Test |", "|---|---|---|---|"]
    for c in sorted(rec["beneficial_candidates"], key=lambda c: -c["none_rewrites"]):
        lines.append(f"| {c['pr']} | {c['repo']} | {c['none_rewrites']} | {', '.join(c['test_files'][:2])} |")
    lines += ["", "## Có hại tiềm năng (mã ghi `noqa: E711`)", "", "| Repo | File |", "|---|---|"]
    for r, paths in list(rec["harmful_by_repo"].items())[:40]:
        lines.append(f"| {r} | {', '.join(paths[:3])} |")
    (out / "G_CANDIDATES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
