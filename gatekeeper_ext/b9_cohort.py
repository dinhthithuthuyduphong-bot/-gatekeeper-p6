"""Patch generation for the Study M cohort (reuses the frozen B9 repair loop; nothing in gatekeeper_lite is modified).

Instance builder: from a `vet_target` result (pre/gold commits, changed files, fail-to-pass tests) and an issue text,
build the B9 instance.  Policies, fixed here before any patch is generated:
  * issue text: the title and body of the issue linked from the pull request ("fixes #N") when there is one, else the
    pull request TITLE only.  Never the pull request body (it often describes the fix).  Fenced code blocks that share
    a line of at least 20 characters with the gold diff are removed.  At most 4,000 characters.
  * edit rights: the non-test python files changed by the gold fix (the same rule as the six development instances).
  * visible check: ONE fail-to-pass test (the first by id), shown with its source.  All other fail-to-pass tests and
    the pass-to-pass tests are hidden labels and are never shown or used for selection.
  * accounting: output tokens = provider total - prompt (gatekeeper_ext.usage), so thinking tokens are counted.
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_ext.usage import output_tokens  # noqa: E402
from gatekeeper_lite import b9  # noqa: E402

TEST_PATH = re.compile(r"(^|/)(tests?|testing)/|(^|/)test_[^/]*\.py$|_test\.py$|(^|/)tests\.py$")
FENCE = re.compile(r"```.*?```", re.S)
LINK = re.compile(r"\b(?:fix(?:e[sd])?|close[sd]?|resolve[sd]?)\s*:?\s*#(\d+)", re.I)
ISSUE_LIMIT = 4000
VISIBLE_SOURCE_LIMIT = 6000


def linked_issue_numbers(pr_body):
    return sorted({int(n) for n in LINK.findall(pr_body or "")})


def _gold_lines(gold_diff):
    out = set()
    for ln in (gold_diff or "").splitlines():
        if ln[:1] in "+-" and ln[:3] not in ("+++", "---"):
            s = ln[1:].strip()
            if len(s) >= 20:
                out.add(s)
    return out


def issue_text(pr_title, issue, gold_diff, limit=ISSUE_LIMIT):
    """issue: {"title", "body"} of the linked issue, or None.  Returns (text, provenance)."""
    if not issue:
        return pr_title.strip()[:limit], {"source": "pull request title only", "removed_code_blocks": 0}
    gold = _gold_lines(gold_diff)
    removed = 0

    def keep(m):
        nonlocal removed
        if any(ln.strip() in gold for ln in m.group(0).splitlines()):
            removed += 1
            return ""
        return m.group(0)
    body = FENCE.sub(keep, issue.get("body") or "")
    text = ("%s\n\n%s" % (issue.get("title", "").strip(), body.strip())).strip()
    return text[:limit], {"source": "linked issue", "removed_code_blocks": removed}


def to_nodeid(test_id, test_files):
    """vet id 'tests.unit.test_x.TestC::test_f[p]' -> pytest node id 'tests/unit/test_x.py::TestC::test_f[p]'."""
    cls, _, name = test_id.rpartition("::")
    for f in sorted(test_files, key=len, reverse=True):
        dotted = f[:-3].replace("/", ".")
        if cls == dotted or cls.startswith(dotted + "."):
            rest = cls[len(dotted):].lstrip(".")
            return "::".join([f] + ([rest] if rest else []) + [name])
    raise ValueError("cannot map test %r to one of %s" % (test_id, list(test_files)))


def build_instance(vet, issue, pr_title, source_limit=VISIBLE_SOURCE_LIMIT):
    """Returns (manifest, instance).  Raises ValueError when the vetting result cannot define a repair task."""
    if vet.get("verdict") != "ELIGIBLE":
        raise ValueError("vetting verdict is %r, not ELIGIBLE" % vet.get("verdict"))
    modules = [f for f in vet["changed_files"] if f.endswith(".py") and not TEST_PATH.search(f)]
    if not modules:
        raise ValueError("the fix changes no non-test python file")
    f2p = sorted(vet.get("eligible_oracle") or [])
    if not f2p:
        raise ValueError("no fail-to-pass test")
    test_files = vet.get("gold_test_files") or []
    visible_id = f2p[0]
    visible_node = to_nodeid(visible_id, test_files)
    text, provenance = issue_text(pr_title, issue, vet.get("gold_source_diff", ""))
    src = (vet.get("eligible_sources") or {}).get(visible_id, "")[:source_limit]
    desc = "This test currently fails and must pass after your change (%s):\n%s" % (visible_node, src)
    p2p = sorted(k for k, v in (vet.get("classification") or {}).items() if str(v).startswith("P->P"))
    dirs = [os.path.dirname(f) for f in test_files]
    census = [os.path.commonpath(dirs)] if dirs and os.path.commonpath(dirs) else list(test_files)
    manifest = {"target_id": vet["name"], "modules": modules,
                "pythonpath": ["src"] if all(m.startswith("src/") for m in modules) else [], "census_tests": census,
                "checkout": {"repo": vet["repo"], "ref": vet["pre"]}, "gold": vet["gold"], "python": vet.get("python")}
    instance = {"issue": text, "issue_provenance": provenance, "visible": {"kind": "pytest", "tests": [visible_node], "timeout": 600},
                "visible_desc": desc, "hidden_f2p": [to_nodeid(t, test_files) for t in f2p[1:]],
                "hidden_p2p": [to_nodeid(t, test_files) for t in p2p]}
    return manifest, instance


class CohortClient(b9.OpenAICompatibleClient):
    """Same request as the frozen client, but output tokens come from gatekeeper_ext.usage (thinking is billed)."""

    def complete(self, model, messages, max_tokens, temperature, seed):
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature, "seed": seed, **self.extra}
        req = urllib.request.Request("%s/chat/completions" % self.base_url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer %s" % os.environ[self.key_env]})
        data = json.loads(urllib.request.urlopen(req, timeout=300).read())
        usage = data.get("usage") or {}
        choice = (data.get("choices") or [{}])[0]
        out = output_tokens(usage)
        missing = "prompt_tokens" not in usage or out is None
        inp = b9.prompt_token_upper_bound(messages) if missing else int(usage["prompt_tokens"])
        return {"text": (choice.get("message") or {}).get("content") or "",
                "usage": {"input": inp, "output": max_tokens if missing else out, "usage_missing": missing},
                "raw": {"id": data.get("id"), "model": data.get("model"), "finish_reason": choice.get("finish_reason"), "usage": usage,
                        "request_params": {k: v for k, v in payload.items() if k != "messages"}}}


class RecordingClient(b9.ModelClient):
    """Wraps a client and keeps every finish reason, so truncation by thinking is visible in the results."""

    def __init__(self, inner):
        self.inner, self.finish_reasons = inner, []

    def complete(self, model, messages, max_tokens, temperature, seed):
        reply = self.inner.complete(model, messages, max_tokens, temperature, seed)
        self.finish_reasons.append((reply.get("raw") or {}).get("finish_reason"))
        return reply


def generate(target, instance, client, model, budget, prices, seed, guard=None):
    """Run the frozen B9 repair loop on a cohort instance; returns (RepairResult, finish_reasons)."""
    rec = RecordingClient(client)
    res = b9.repair(target, instance, rec, model, budget, prices, seed, guard)
    return res, rec.finish_reasons
