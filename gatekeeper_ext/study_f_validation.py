"""Fail-closed contracts for recorded-provider Study F evidence (F-A3).

No network calls. Metadata is a consistency check, not provider authentication.
Offline fixtures must never be presented as measured model performance.
"""
import hashlib
import math
from pathlib import Path

from gatekeeper_lite.b9 import CassetteClient, b9_verdict

VERDICTS = ("SUCCESS", "HARMFUL", "NO_EFFECT", "NO_PATCH", "BUDGET_CAP", "CENSUS_INVALID")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def natural(value):
    return type(value) is int and value >= 0


def finite_nonnegative(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def expected_keys(cfg):
    require(type(cfg.get("repetitions")) is int and cfg["repetitions"] > 0, "invalid repetitions")
    require(len(cfg["cells"]) == len(set(cfg["cells"])) and cfg["cells"], "duplicate/empty target family")
    require(cfg["b9_configs"], "empty model family")
    require(set(cfg.get("scopes_by_target", {})) == set(cfg["cells"]), "missing registered scopes")
    for scopes in cfg["scopes_by_target"].values():
        require(bool(scopes) and len(scopes) == len(set(scopes)), "empty/duplicate registered scopes")
    keys = {(m, r, t) for m in cfg["b9_configs"] for r in range(cfg["repetitions"]) for t in cfg["cells"]}
    require(len(keys) == cfg["k_patches"], "registered patch family size mismatch")
    require(0 < cfg["alpha"] < 1, "invalid alpha")
    return keys


class ProviderReplayClient(CassetteClient):
    """Replay only; require raw provider usage for every consumed reply."""
    def __init__(self, path):
        require(Path(path).is_file(), "missing cassette: " + str(path))
        super().__init__(path, "replay")
        self.used_keys = []

    def complete(self, model, messages, max_tokens, temperature, seed):
        reply = super().complete(model, messages, max_tokens, temperature, seed)
        raw = reply.get("raw", {})
        usage = raw.get("usage")
        require(isinstance(usage, dict), "cassette reply has no raw provider usage (mock is not evidence)")
        require(isinstance(raw.get("model"), str) and raw["model"], "missing served model identity")
        normalized = reply.get("usage", {})
        require(not normalized.get("usage_missing", True), "provider usage is missing")
        for original, key in (("prompt_tokens", "input"), ("completion_tokens", "output")):
            require(natural(usage.get(original)), "invalid provider token count")
            require(normalized.get(key) == usage[original], "normalized/provider token counts disagree")
        self.used_keys.append(self.key(model, messages, max_tokens, temperature, seed))
        return reply


def validate_record(record, target_id, model, repetitions, commit):
    require(record.get("evidence") in ("PAID_B9", "REPLAY_OF_RECORDED_B9"), "not recorded-provider B9 evidence")
    require(record.get("target") == target_id and record.get("model") == model, "result target/model mismatch")
    require(record.get("commit") == commit, "B9 target commit differs from frozen target")
    require(not record.get("guard_overshoot", False), "recorded spending guard overshot")
    runs = record.get("runs", [])
    require(len(runs) == repetitions, "missing/extra recorded repetitions")
    seen = set()
    for row in runs:
        r = row.get("repetition")
        require(natural(r) and r < repetitions and r not in seen, "duplicate/invalid recorded repetition")
        seen.add(r)
        require(row.get("usage_missing_calls") == 0, "recorded run lacks provider usage")
        require(row.get("status") in ("SUBMITTED", "NO_PATCH"), "invalid recorded repair status")
        require(natural(row.get("calls")) and natural(row.get("visible_runs")), "invalid recorded execution counts")
        require(finite_nonnegative(row.get("cost_usd")), "invalid recorded cost")
        require(all(natural(row.get("tokens", {}).get(k)) for k in ("input", "output")), "invalid recorded tokens")
    return {row["repetition"]: row for row in runs}


def compare_replay(result, recorded):
    actual = {"status": result.status, "attempts": result.attempts, "calls": result.calls,
              "visible_runs": result.visible_runs, "tokens": result.tokens,
              "patched_modules": sorted(result.treated)}
    for key, value in actual.items():
        require(recorded.get(key) == value, "recorded/replayed repair differs: " + key)
    require(result.usage_missing == 0, "replayed usage is missing")
    require(abs(recorded["cost_usd"] - result.cost_usd) <= 1e-6, "recorded/replayed cost differs")


def validate_observations(counts_by_scope, traces, cfg, target):
    expected = set(cfg["scopes_by_target"][target])
    require(set(counts_by_scope) == expected and set(traces) == expected, "missing/extra observation scope")
    for scope, counts in counts_by_scope.items():
        require(all(natural(counts.get(k)) for k in ("help", "tie", "hurt", "harness_error")), "invalid observation counts")
        require(counts["harness_error"] == 0, "harness errors cannot be functional outcomes")
        trace = traces[scope]
        require(len(trace) == cfg["n_max"], "incomplete paired trace")
        require(all(isinstance(x, list) and len(x) == 2 and x[0] in (-1,0,1)
                    and type(x[1]) is bool and x[1] == (x[0] > 0) for x in trace), "invalid paired observation")
        actual = {"help": sum(x[0] < 0 for x in trace), "hurt": sum(x[0] > 0 for x in trace),
                  "tie": sum(x[0] == 0 for x in trace)}
        require(all(counts[k] == v for k,v in actual.items()), "counts/paired trace mismatch")


def validate_state(state, cfg, target):
    require(state.get("status") in ("NO_PATCH", "SUBMITTED"), "invalid held-out state")
    if state["status"] == "SUBMITTED":
        require(state.get("census", {}).get("status") in ("VALID", "INVALID"), "unknown census status")
        hidden = state.get("hidden_oracle", {})
        validate_observations(hidden, state.get("hidden_traces", {}), cfg, target)
    return b9_verdict(state)


def validate_heldout(cfg, documents, config_sha256):
    expected = expected_keys(cfg)
    require(len(documents) == len(cfg["cells"]), "wrong held-out target file count")
    raw, candidates, seen_targets = {}, {}, set()
    seeds = set()
    for doc in documents:
        target = doc.get("target")
        require(target in cfg["cells"] and target not in seen_targets, "duplicate/unexpected held-out target")
        seen_targets.add(target)
        require(len(doc.get("rows", [])) == 3 + 2*len(cfg["b9_configs"])*cfg["repetitions"],
                "incomplete/extra rows in held-out target")
        require(doc.get("schema_version") == 2, "held-out data requires F-A3 schema_version=2; rerun scorer")
        require(doc.get("evidence") == "RECORDED_PROVIDER_REPLAY", "not recorded-provider held-out evidence")
        require(doc.get("config_sha256") == config_sha256, "held-out config hash mismatch")
        hs, ads = doc.get("heldout_seed", {}).get("seed"), doc.get("admission_seed")
        require(natural(hs) and natural(ads) and hs != ads, "held-out/admission seeds missing or identical")
        seeds.add((hs, ads))
        require(isinstance(doc.get("commit"), str) and len(doc["commit"]) == 40, "missing target commit")
        source = doc.get("source_artifacts", {})
        require(set(source) == set(cfg["b9_configs"]), "missing source artifact provenance")
        for metadata in source.values():
            require(all(isinstance(metadata.get(k), str) and len(metadata[k]) == 64 for k in
                        ("result_sha256", "cassette_sha256")), "missing source hashes")
        skill_rows = set()
        for row in doc.get("rows", []):
            approach = row.get("approach")
            if approach in ("skill+Gatekeeper", "skill+B6R", "skill+B8"):
                require(approach not in skill_rows, "duplicate skill comparator")
                skill_rows.add(approach)
                require(row.get("verdict") == validate_state(row.get("state", {}), cfg, target), "skill verdict/state mismatch")
                continue
            require(approach in ("B9 raw", "B9+Gatekeeper (candidate)"), "unknown result approach")
            require(natural(row.get("repetition")), "invalid repetition type")
            key = (row.get("model"), row["repetition"], target)
            require(key in expected, "out-of-family patch")
            require(finite_nonnegative(row.get("cost_usd")), "invalid row cost")
            if approach == "B9 raw":
                require(key not in raw, "duplicate raw patch")
                require(row.get("verdict") == validate_state(row.get("state", {}), cfg, target), "raw verdict/state mismatch")
                raw[key] = row
            else:
                require(key not in candidates, "duplicate candidate patch")
                require(finite_nonnegative(row.get("e_patch")), "invalid patch e-value")
                gate = row.get("gate", {})
                require(gate.get("e_patch") == row["e_patch"], "gate/row e-value mismatch")
                require(type(gate.get("submitted")) is bool, "missing submission state")
                if not gate["submitted"] or not gate.get("census_ok", False):
                    require(row["e_patch"] == 0, "unsubmitted/census-invalid patch has nonzero evidence")
                if gate["submitted"]:
                    from gatekeeper_ext.patch_rule import patch_evalue
                    validate_observations(gate.get("scope_counts", {}), gate.get("scope_traces", {}), cfg, target)
                    recomputed = patch_evalue(gate["scope_traces"], cfg["theta"], cfg["eta"],
                                              cfg["n_max"], not gate.get("census_ok", False))
                    require(math.isclose(row["e_patch"], recomputed, rel_tol=1e-12, abs_tol=1e-12),
                            "patch e-value does not match raw admission trace")
                candidates[key] = row
        require(skill_rows == {"skill+Gatekeeper", "skill+B6R", "skill+B8"}, "missing skill comparator")
    require(len(seeds) == 1, "mixed seed versions across targets")
    require(set(raw) == expected and set(candidates) == expected, "missing raw/candidate patch rows; no silent zero-fill")
    for key in expected:
        require(candidates[key].get("raw_verdict") == raw[key]["verdict"], "candidate/raw verdict mismatch")
        require(candidates[key]["cost_usd"] == raw[key]["cost_usd"], "candidate/raw generation cost mismatch")
        require(candidates[key]["gate"]["submitted"] == (raw[key]["state"]["status"] == "SUBMITTED"), "candidate/raw submission mismatch")
    return raw, candidates
