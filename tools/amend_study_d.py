"""Apply a Study D amendment after freeze: record it in the config, pin the seed to the
ORIGINAL freeze hash (seed_freeze_sha256), and re-freeze the hashes.

python tools/amend_study_d.py A1
The amendment text must already be in study_d/AMENDMENTS.md (it is hashed too).
"""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(amendment_id: str) -> int:
    d = ROOT / "study_d"
    cfg = json.loads((d / "config_study_d.json").read_text())
    if cfg.get("status") != "FROZEN":
        raise SystemExit("amendments apply only to a FROZEN study")
    if amendment_id not in (d / "AMENDMENTS.md").read_text():
        raise SystemExit(f"{amendment_id} is not documented in study_d/AMENDMENTS.md")
    if amendment_id in cfg.get("amendments_applied", []):
        raise SystemExit(f"{amendment_id} already applied")
    cfg.setdefault("seed_freeze_sha256", hashlib.sha256((d / "FREEZE.json").read_bytes()).hexdigest())
    cfg.setdefault("amendments_applied", []).append(amendment_id)
    cfg.setdefault("amendment_log", []).append(
        {"id": amendment_id, "applied_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    (d / "config_study_d.json").write_text(json.dumps(cfg, indent=2))
    subprocess.run([sys.executable, str(ROOT / "tools" / "freeze_study.py"), "freeze", "study_d"], check=True)
    print(f"{amendment_id} applied; seed stays derived from {cfg['seed_freeze_sha256'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
