"""Prospective B6-R v2 comparison gate (NO changes to frozen B6-R scores).

This is a conservative proposed comparator, not an executed research baseline.
Eligibility requires:
  1. source replay with independently verifiable receipt,
  2. source provenance receipt with repo + SHA-1 commit,
  3. positive source-vs-target environment compatibility on Python AND packages,
  4. PREDECLARED visible smoke suite receipt (not hidden admission/held-out oracle).

Missing evidence => UNRESOLVED, never silently MATCH or ADMIT.
No network, no subprocesses, no model calls, no target edits.
Current Study D skill has no source package contract, therefore it cannot
produce ADMIT from this tool unless *new independent evidence* is provided.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_receipt(root: Path, entry: dict, name: str) -> dict:
    if not entry or not entry.get("path") or not entry.get("sha256"):
        raise ValueError(f"{name}: no pinned receipt path/hash")
    root = root.resolve()
    candidate = (root / entry["path"]).resolve()
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise ValueError(f"{name}: receipt outside repo or unavailable")
    if _sha(candidate).lower() != entry["sha256"].lower():
        raise ValueError(f"{name}: receipt checksum mismatch")
    return json.loads(candidate.read_text(encoding="utf-8"))


def _numeric_version(value: str) -> tuple[int, ...]:
    """Fail closed for prerelease/PEP-440 strings not supported by this pilot."""
    value = str(value)
    if not re.fullmatch(r"\d+(?:\.\d+){0,3}", value):
        raise ValueError(f"unsupported non-numeric version {value!r}")
    return tuple(map(int, value.split(".")))


def satisfies(version: str, clauses: str) -> bool:
    v = _numeric_version(version)
    if not isinstance(clauses, str) or not clauses:
        raise ValueError("empty version constraints")
    for clause in clauses.split(","):
        m = re.fullmatch(r"\s*(>=|<=|==|!=|>|<)\s*(\d+(?:\.\d+){0,3})\s*", clause)
        if not m:
            raise ValueError(f"unsupported constraint {clause!r}")
        op, ref = m.groups()
        b = _numeric_version(ref)
        max_len = max(len(v), len(b))
        a, b = v + (0,) * (max_len-len(v)), b + (0,) * (max_len-len(b))
        ok = {"==": a == b, "!=": a != b, ">": a > b, ">=": a >= b,
              "<": a < b, "<=": a <= b}[op]
        if not ok:
            return False
    return True


def evaluate(root: Path, record: dict, target: dict) -> dict:
    """Returns a transparent status and rationale; not a historical claim."""
    name = target.get("target_id", "unknown")
    result = {"target": name, "decision": "UNRESOLVED", "checks": {},
              "type": "PROPOSED_PROSPECTIVE_B6R_V2", "paid_calls": 0}
    if not record or record.get("status") != "PREDECLARED_CANDIDATE":
        result["checks"]["source"] = "MISSING_PREDECLARED_SOURCE_CONTRACT"
        return result
    try:
        evidence = _read_receipt(root, record.get("origin"), "origin")
        replay = _read_receipt(root, record.get("replay"), "source replay")
        smoke = _read_receipt(root, record.get("smoke"), "visible smoke")
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        result["checks"]["receipt"] = str(exc)
        return result

    origin = evidence.get("origin", {})
    if not origin.get("repo") or not re.fullmatch(r"[0-9a-f]{40}", origin.get("commit", "")):
        result["checks"]["origin"] = "MISSING_GROUNDED_REPO_OR_COMMIT"
        return result
    result["checks"]["origin"] = "PINNED_RECEIPT_PRESENT (provenance needs independent audit)"
    if replay.get("status") != "PASS" or not isinstance(replay.get("heldout_examples"), int) or replay["heldout_examples"] <= 0:
        result["checks"]["replay"] = "NO_INDEPENDENT_PASS"
        return result
    result["checks"]["replay"] = "PASS_RECEIPT_PRESENT"
    if smoke.get("oracle_kind") != "VISIBLE_PREDECLARED" or smoke.get("uses_hidden_oracle") is not False:
        result["checks"]["smoke"] = "NON_VISIBLE_OR_UNVERIFIABLE_SMOKE"
        return result
    if smoke.get("status") == "FAIL":
        result["decision"] = "REJECT"
        result["checks"]["smoke"] = "VISIBLE_SMOKE_FAIL"
        return result
    if smoke.get("status") != "PASS":
        result["checks"]["smoke"] = "VISIBLE_SMOKE_NOT_RUN"
        return result
    result["checks"]["smoke"] = "PASS_RECEIPT_PRESENT"

    source_env = evidence.get("required_environment", {})
    py_spec = source_env.get("python")
    source_pkgs = source_env.get("packages") or {}
    if not py_spec or not source_pkgs:
        result["checks"]["environment"] = "SOURCE_CONTRACT_INCOMPLETE"
        return result
    checks = [("python", py_spec, target.get("python"))]
    checks += [(p, s, (target.get("packages") or {}).get(p)) for p,s in sorted(source_pkgs.items())]
    unknown = []
    mismatched = []
    for component, spec, observed in checks:
        if observed in ("",None):
            unknown.append(f"{component}:target version absent")
            continue
        try:
            match = satisfies(str(observed), str(spec))
        except ValueError as exc:
            unknown.append(f"{component}:{exc}")
            continue
        if not match:
            mismatched.append(f"{component}:{observed} violates {spec}")
    result["checks"]["environment"] = {"unknown": unknown, "mismatched": mismatched}
    if mismatched:
        result["decision"] = "REJECT"
    elif not unknown:
        result["decision"] = "ADMIT"
        result["note"] = ("All declared checks passed, not proof of semantic safety; "
                          "prospective use only, outside Study D/E freeze")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    p.add_argument("--contract", type=Path, default=Path("pre_b9/phase2/B6R_V2_CONTRACT.json"))
    p.add_argument("--out", type=Path, default=Path("out_phase2/B6R_V2_READINESS.json"))
    args = p.parse_args()
    root = args.root.resolve()
    path = root / args.contract
    record = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    target_folder = root / "study_d/eval_targets"
    rows = [evaluate(root, record, json.loads(f.read_text(encoding="utf-8")))
            for f in sorted(target_folder.glob("*/gk_target.json"))]
    result = {"analysis": "NO_PROSPECTIVE_B6R_V2_RUN_YET",
              "interpretation": "UNRESOLVED != baseline failure or harmful transfer",
              "rows": rows}
    dest = root / args.out
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"B6-R V2 readiness: {len(rows)} targets, "
          f"{sum(x['decision']=='UNRESOLVED' for x in rows)} unresolved")


if __name__ == "__main__":
    main()
