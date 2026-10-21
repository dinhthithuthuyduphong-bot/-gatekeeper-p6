"""Read-only B6-R source/target environment contract inventory.

No target tests, oracle calls, model calls, or admission decisions.
Reports missing evidence as MISSING, not as an observed mismatch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def inventory(root: Path, study: str = "study_d") -> dict:
    base = root / study
    cfg = json.loads((base / "config_study_d.json").read_text(encoding="utf-8"))
    skill = json.loads((base / cfg["skill"]).read_text(encoding="utf-8"))
    contract = skill.get("D") or {}
    required_python = contract.get("python")
    required_packages = contract.get("packages") or {}
    rows = []
    for path in sorted((base / "eval_targets").glob("*/gk_target.json")):
        target = json.loads(path.read_text(encoding="utf-8"))
        packages = target.get("packages") or {}
        missing = []
        if not required_python:
            missing.append("source_python_constraint")
        if not required_packages:
            missing.append("source_package_constraints")
        if required_python and not target.get("python"):
            missing.append("target_python_version")
        for package in required_packages:
            if packages.get(package) in (None, ""):
                missing.append("target_package:" + package)
        rows.append({
            "target": path.parent.name,
            "declared_source_python": required_python,
            "declared_source_packages": required_packages,
            "target_python": target.get("python"),
            "target_packages": packages,
            "missing": missing,
            "evidence_completeness": "INCOMPLETE" if missing else "DECLARED_ONLY",
            "admission_decision": "NOT_EVALUATED",
            "source_provenance_verified": False,
        })
    return {
        "type": "EXPLORATORY_CONTRACT_INVENTORY",
        "study": study,
        "skill_id": skill.get("skill_id"),
        "source_contract": contract,
        "targets": rows,
        "interpretation": (
            "DECLARED_ONLY does not prove provenance, runtime compatibility, "
            "source replay validity, or semantic safety. Do not use this "
            "inventory to retroactively change frozen B6-R decisions."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data = inventory(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Inventory written: {args.out} ({len(data['targets'])} targets)")


if __name__ == "__main__":
    main()
