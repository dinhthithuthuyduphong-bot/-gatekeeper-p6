"""Fetch the text a repair prompt may use: the issue linked from the pull request, else only the pull request title.
Policy (frozen with gatekeeper_ext/b9_cohort.py): never the pull request body itself.  Network access is injectable."""
import json
import re
import urllib.error
import urllib.request

from gatekeeper_ext.b9_cohort import linked_issue_numbers


def _get(url, token, opener):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "gatekeeper-n",
                                               **({"Authorization": "Bearer " + token} if token else {})})
    try:
        with opener(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": "HTTP %d" % e.code}
    except Exception as e:                                   # network, JSON
        return {"error": type(e).__name__}


def fetch(repo_url, pr_number, token="", opener=urllib.request.urlopen):
    """Returns (pr_title, issue or None, provenance)."""
    m = re.search(r"github\.com[/:]([^/]+/[^/.]+?)(?:\.git)?$", repo_url)
    if not m:
        return "", None, {"error": "cannot read the repository from %r" % repo_url}
    repo = m.group(1)
    pr = _get("https://api.github.com/repos/%s/pulls/%d" % (repo, pr_number), token, opener)
    if "error" in pr:
        return "", None, {"error": "pull request: " + pr["error"]}
    prov = {"pr_title_fetched": True, "linked_numbers": linked_issue_numbers(pr.get("body"))}
    for n in prov["linked_numbers"]:
        it = _get("https://api.github.com/repos/%s/issues/%d" % (repo, n), token, opener)
        if "error" in it or "pull_request" in it:             # skip errors and links that are themselves pull requests
            continue
        prov["issue_used"] = n
        return pr.get("title", ""), {"title": it.get("title", ""), "body": it.get("body") or ""}, prov
    return pr.get("title", ""), None, prov
