"""Freeze / verify a study protocol by hashing every input that can change its outcome.

python tools/freeze_study.py freeze study_b     -> writes study_b/FREEZE.json
python tools/freeze_study.py verify study_b     -> exit 1 if any frozen file changed
Hashed: the config, skills, target manifests, oracle templates, the protocol text, the
frozen v3 binder, every gatekeeper_lite module and the fetch tool.  Fetched code is not
hashed here (its commits are pinned in the manifests and recorded in FETCH_RECEIPT.json).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def tracked(study: Path) -> list:
    files = sorted(study.glob("config_*.json")) + sorted(study.glob("*PROTOCOL*.md"))
    files += [study / "AMENDMENTS.md"]
    files += sorted((study / "skills").glob("*.json"))
    files += sorted((study / "targets").glob("*/gk_target.json")) + sorted((study / "targets").glob("*.json"))
    files += sorted((study / "eval_targets").glob("*/gk_target.json")) + sorted((study / "oracles").glob("*.py"))
    files += sorted((study / "oracle_templates").glob("*.py")) + sorted((study / "oracle_templates").glob("*.ini"))
    files += sorted((ROOT / "gatekeeper_lite").glob("*.py"))
    files += sorted((ROOT / "p7").rglob("*.py")) + sorted((ROOT / "p7").rglob("*.json"))
    files += [ROOT / "tools" / n for n in ("fetch_real_targets.py", "install_requirements.py",
                                          "run_study_d.py", "aggregate_study_d.py")]
    return [f for f in files if f.is_file()]


def digest(files) -> dict:
    return {f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in files}


def main(cmd: str, study_dir: str) -> int:
    study = (ROOT / study_dir).resolve()
    current = digest(tracked(study))
    path = study / "FREEZE.json"
    if cmd == "freeze":
        path.write_text(json.dumps({"files": current}, indent=2), encoding="utf-8")
        print(f"frozen {len(current)} files -> {path.relative_to(ROOT)}")
        return 0
    frozen = json.loads(path.read_text(encoding="utf-8"))["files"]
    changed = sorted(k for k in set(frozen) | set(current) if frozen.get(k) != current.get(k))
    if changed:
        print("FROZEN FILES CHANGED:\n  " + "\n  ".join(changed))
        return 1
    print(f"freeze verified: {len(frozen)} files unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
