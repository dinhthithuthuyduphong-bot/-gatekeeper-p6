"""Freeze Study D (+ B9 config) on the freeze date.

python tools/freeze_study_d.py [--delay-minutes 60]
Sets status FROZEN, frozen_on, and seed_time_utc = now + delay (so the drand round used
for the seed is unknown at freeze time), then recomputes study_d/FREEZE.json.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay-minutes", type=int, default=60)
    a = ap.parse_args(argv)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    seed_time = (now + timedelta(minutes=a.delay_minutes)).isoformat().replace("+00:00", "Z")
    cfg_p, b9_p = ROOT / "study_d" / "config_study_d.json", ROOT / "study_d" / "b9_config.json"
    cfg, b9 = json.loads(cfg_p.read_text()), json.loads(b9_p.read_text())
    if cfg.get("status") == "FROZEN":
        raise SystemExit("already FROZEN; changes after freeze need an amendment")
    cfg.update(status="FROZEN", frozen_on=now.isoformat().replace("+00:00", "Z"), seed_time_utc=seed_time)
    b9.update(status="FROZEN", frozen_on=cfg["frozen_on"])
    cfg_p.write_text(json.dumps(cfg, indent=2))
    b9_p.write_text(json.dumps(b9, indent=2))
    subprocess.run([sys.executable, str(ROOT / "tools" / "freeze_study.py"), "freeze", "study_d"], check=True)
    print(f"frozen at {cfg['frozen_on']}; seed from the first drand quicknet round at/after {seed_time}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
