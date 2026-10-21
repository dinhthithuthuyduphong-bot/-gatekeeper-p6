"""B9: budget-matched LLM repair baseline (Study D).

Protocol (fixed before evaluation):
  * one repair instance -> at most ONE submitted patch, evaluated on every scope;
  * same edit rights as the skill: only the target's declared modules may change
    (adding helpers inside them is allowed);
  * candidates are filtered with a VISIBLE check only; the hidden oracle (draw scopes +
    census) scores the submitted patch and is never used for selection;
  * budget fixed in advance: max model calls, max output tokens per call, max visible
    test runs; exhausted budget without a passing candidate -> NO_PATCH (baseline kept);
  * primary metric: outcome of the submitted patch.  pass@k is secondary.
Before paid runs, the pipeline is exercised with a scripted fake model and a cassette
(record/replay) so no money is spent; those runs are not B9 evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

SYSTEM_PROMPT = (
    "You repair Python code. Reply with ONE unified diff (git format, a/ and b/ prefixes) "
    "that edits only the files you were given. No explanations, no code fences.")


# ----------------------------------------------------------------- model clients
class ModelClient:
    def complete(self, model: str, messages: List[dict], max_tokens: int, temperature: float,
                 seed: int) -> dict:
        raise NotImplementedError


def prompt_token_upper_bound(messages: List[dict]) -> int:
    """Sound upper bound for byte-level BPE / byte-fallback tokenizers: every token covers at
    least one UTF-8 byte, so tokens <= bytes; plus a fixed per-message overhead."""
    return sum(len(m["content"].encode("utf-8")) + 64 for m in messages)


class OpenAICompatibleClient(ModelClient):
    """Chat-completions over HTTP (DeepSeek, Gemini via AI Studio, and Vertex AI expose
    OpenAI-compatible endpoints).  The credential is read from an environment variable and is
    never stored.  The raw response metadata (id, served model, finish reason, full usage
    including reasoning tokens) is returned so that the cassette keeps it as evidence.  A
    response WITHOUT usage is flagged and accounted at the worst case, never as zero."""

    def __init__(self, base_url: str, key_env: str, extra: Optional[dict] = None):
        self.base_url, self.key_env, self.extra = base_url.rstrip("/"), key_env, dict(extra or {})

    def complete(self, model, messages, max_tokens, temperature, seed):
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens,
                   "temperature": temperature, "seed": seed, **self.extra}
        req = urllib.request.Request(f"{self.base_url}/chat/completions", data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json",
                                              "Authorization": f"Bearer {os.environ[self.key_env]}"})
        data = json.loads(urllib.request.urlopen(req, timeout=300).read())
        usage = data.get("usage")
        choice = (data.get("choices") or [{}])[0]
        missing = not usage or "prompt_tokens" not in usage or "completion_tokens" not in usage
        inp = prompt_token_upper_bound(messages) if missing else int(usage["prompt_tokens"])
        out = max_tokens if missing else int(usage["completion_tokens"])
        return {"text": (choice.get("message") or {}).get("content") or "",
                "usage": {"input": inp, "output": out, "usage_missing": missing},
                "raw": {"id": data.get("id"), "model": data.get("model"),
                        "finish_reason": choice.get("finish_reason"), "usage": usage,
                        "request_params": {k: v for k, v in payload.items() if k != "messages"}}}


class CassetteClient(ModelClient):
    """record: call the inner client and store responses; replay: answer only from the
    cassette and fail loudly on a miss (no silent paid call)."""

    def __init__(self, path: Path, mode: str, inner: Optional[ModelClient] = None):
        self.path, self.mode, self.inner = Path(path), mode, inner
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}

    @staticmethod
    def key(model, messages, max_tokens, temperature, seed) -> str:
        blob = json.dumps([model, messages, max_tokens, temperature, seed], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def complete(self, model, messages, max_tokens, temperature, seed):
        k = self.key(model, messages, max_tokens, temperature, seed)
        if k in self.data:
            return self.data[k]
        if self.mode != "record" or self.inner is None:
            raise KeyError(f"cassette miss for {model} (replay mode)")
        out = self.inner.complete(model, messages, max_tokens, temperature, seed)
        self.data[k] = out
        self.path.write_text(json.dumps(self.data, indent=1))
        return out


class ScriptedFakeModel(ModelClient):
    """Returns pre-written replies in order (acceptance tests of the harness)."""

    def __init__(self, replies: List[str]):
        self.replies, self.i = list(replies), 0

    def complete(self, model, messages, max_tokens, temperature, seed):
        text = self.replies[min(self.i, len(self.replies) - 1)]
        self.i += 1
        return {"text": text, "usage": {"input": sum(len(m["content"]) // 4 for m in messages),
                                         "output": len(text) // 4}}


# ----------------------------------------------------------------- patch handling
def extract_diff(text: str) -> str:
    text = re.sub(r"^```[a-zA-Z]*\n|```\s*$", "", text.strip(), flags=re.M)
    start = text.find("diff --git")
    if start < 0:
        start = text.find("--- a/")
    return text[start:] + ("\n" if not text.endswith("\n") else "") if start >= 0 else ""


def touched_files(diff: str) -> List[str]:
    return sorted(set(re.findall(r"^\+\+\+ b/(\S+)", diff, flags=re.M)) |
                  set(re.findall(r"^--- a/(\S+)", diff, flags=re.M)))


def apply_diff(root: Path, diff: str) -> tuple:
    proc = subprocess.run(["git", "apply", "--recount", "--whitespace=nowarn", "-"], cwd=root,
                          input=diff, text=True, capture_output=True)
    return proc.returncode == 0, proc.stderr[-300:]


# ----------------------------------------------------------------- spend guard
class BudgetExceeded(RuntimeError):
    pass


class SpendGuard:
    """Hard cap on money: before every model call the WORST-CASE cost of that call
    (estimated input tokens + the full output allowance) must fit in what is left."""

    def __init__(self, cap_usd: float):
        self.cap_usd, self.spent_usd, self.calls = cap_usd, 0.0, 0

    def check(self, messages: List[dict], max_tokens: int, prices: dict) -> None:
        est_in = prompt_token_upper_bound(messages)                       # tokens <= UTF-8 bytes
        worst = est_in / 1e6 * prices.get("input", 0) + max_tokens / 1e6 * prices.get("output", 0)
        if self.spent_usd + worst > self.cap_usd:
            raise BudgetExceeded(f"next call worst case {worst:.4f} USD would exceed cap "
                                 f"{self.cap_usd:.4f} USD (spent {self.spent_usd:.4f})")

    def add(self, usage: dict, prices: dict) -> float:
        cost = usage.get("input", 0) / 1e6 * prices.get("input", 0) + usage.get("output", 0) / 1e6 * prices.get("output", 0)
        self.spent_usd += cost
        self.calls += 1
        if self.spent_usd > self.cap_usd:      # only possible if the provider exceeded max_tokens
            self.overshoot = True
        return cost

    overshoot = False


def b9_verdict(run: dict, bug_scope: str = "bool") -> str:
    """Final B9 outcome of ONE repetition (protocol section 7, primary metric):
    NO_PATCH | BUDGET_CAP | CENSUS_INVALID | HARMFUL (persistent census failure or any hidden regression)
    | SUCCESS (helps the bug scope, no harm anywhere) | NO_EFFECT (submitted, neither)."""
    if run.get("status") != "SUBMITTED":
        if any(a.get("verdict") == "BUDGET_CAP" for a in run.get("attempts", [])):
            return "BUDGET_CAP"          # reported separately (B9 analysis plan, section 4)
        return "NO_PATCH"
    census = run.get("census", {})
    if census.get("status") == "INVALID":
        return "CENSUS_INVALID"
    hidden = run.get("hidden_oracle", {})
    if census.get("new_failures") or any(v.get("hurt", 0) for v in hidden.values()):
        return "HARMFUL"
    if hidden.get(bug_scope, {}).get("help", 0) > 0:
        return "SUCCESS"
    return "NO_EFFECT"


# ----------------------------------------------------------------- visible filter
ORACLE_DRAW_RUNNER = (
    "import importlib.util, json, sys\n"
    "spec = importlib.util.spec_from_file_location('gk_visible_oracle', sys.argv[1])\n"
    "o = importlib.util.module_from_spec(spec); spec.loader.exec_module(o)\n"
    "d = json.loads(sys.argv[3]); out = o.execute(d)\n"
    "sys.exit(0 if o.judge(sys.argv[2], d, out, out)[1] else 1)\n")


def run_visible(root: Path, spec: dict, pythonpath: List[str]) -> bool:
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(root / p) for p in pythonpath] + [str(root)]),
               PYTHONDONTWRITEBYTECODE="1")
    if spec["kind"] == "oracle_draw":      # one fixed draw (the upstream case) through the frozen oracle
        cmd = [sys.executable, "-c", ORACLE_DRAW_RUNNER, spec["oracle"], spec["scope"], json.dumps(spec["draw"])]
    elif spec["kind"] == "python":
        cmd = [sys.executable, "-c", spec["code"]]
    else:
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts=", *spec["tests"]]
    return subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True,
                          timeout=spec.get("timeout", 600)).returncode == 0


# ----------------------------------------------------------------- repair loop
@dataclass
class Budget:
    max_calls: int = 5
    max_output_tokens: int = 4000
    max_visible_runs: int = 5


@dataclass
class RepairResult:
    status: str                          # SUBMITTED / NO_PATCH
    treated: Dict[str, str] = field(default_factory=dict)
    attempts: List[dict] = field(default_factory=list)
    calls: int = 0
    visible_runs: int = 0
    tokens: Dict[str, int] = field(default_factory=lambda: {"input": 0, "output": 0})
    cost_usd: float = 0.0
    seconds: float = 0.0
    usage_missing: int = 0


def build_messages(issue: str, sources: Dict[str, str], visible_desc: str) -> List[dict]:
    files = "\n\n".join(f"### File: {rel}\n{src}" for rel, src in sources.items())
    user = (f"Issue:\n{issue}\n\nFailing check (visible):\n{visible_desc}\n\n"
            f"You may edit only these files:\n{files}\n\nReturn one unified diff.")
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


def repair(target, instance: dict, client: ModelClient, model: str, budget: Budget,
           prices: dict, seed: int, guard: Optional[SpendGuard] = None) -> RepairResult:
    """instance: {"issue", "visible": {...}, "visible_desc"}; edit rights = target.modules."""
    t0 = time.perf_counter()
    allowed = set(target.modules)
    sources = {rel: target.source_of(rel) for rel in target.modules}
    messages = build_messages(instance["issue"], sources, instance["visible_desc"])
    res = RepairResult("NO_PATCH")
    for i in range(budget.max_calls):
        temperature = 0.0 if i == 0 else 0.8
        if guard is not None:
            try:
                guard.check(messages, budget.max_output_tokens, prices)
            except BudgetExceeded as exc:
                res.attempts.append({"call": i + 1, "verdict": "BUDGET_CAP", "detail": str(exc)})
                break
        reply = client.complete(model, messages, budget.max_output_tokens, temperature, seed + i)
        if guard is not None:
            guard.add(reply["usage"], prices)
        res.calls += 1
        for k in ("input", "output"):
            res.tokens[k] += int(reply["usage"].get(k, 0))
        res.usage_missing += int(bool(reply["usage"].get("usage_missing")))
        att = {"call": i + 1}
        diff = extract_diff(reply["text"])
        files = touched_files(diff)
        if not diff:
            att["verdict"] = "NO_DIFF"
        elif not set(files) <= allowed:
            att["verdict"] = f"OUTSIDE_EDIT_RIGHTS {sorted(set(files) - allowed)}"
        else:
            work = Path(tempfile.mkdtemp(prefix="b9_"))
            try:
                snap = work / "s"
                shutil.copytree(target.root, snap, symlinks=True,
                                ignore=shutil.ignore_patterns(".git", "__pycache__"))
                ok, err = apply_diff(snap, diff)
                if not ok:
                    att["verdict"] = "DOES_NOT_APPLY"
                    att["error"] = err
                elif res.visible_runs >= budget.max_visible_runs:
                    att["verdict"] = "BUDGET_VISIBLE_RUNS"
                else:
                    res.visible_runs += 1
                    passed = run_visible(snap, instance["visible"], target.manifest.get("pythonpath", []))
                    att["verdict"] = "PASSES_VISIBLE" if passed else "FAILS_VISIBLE"
                    if passed:
                        res.status = "SUBMITTED"
                        res.treated = {rel: (snap / rel).read_text(encoding="utf-8") for rel in files}
            finally:
                shutil.rmtree(work, ignore_errors=True)
        res.attempts.append(att)
        if res.status == "SUBMITTED":
            break
    res.cost_usd = round(res.tokens["input"] / 1e6 * prices.get("input", 0)
                         + res.tokens["output"] / 1e6 * prices.get("output", 0), 6)
    res.seconds = round(time.perf_counter() - t0, 3)
    return res
