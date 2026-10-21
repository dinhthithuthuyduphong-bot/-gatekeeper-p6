"""Freeze a study other than Study D (e.g. study_e): FROZEN + seed time = now + delay,
then hash every input.  Refuses to freeze twice.
python tools/freeze_named_study.py study_e [--delay-minutes 60]"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser()
ap.add_argument("study")
ap.add_argument("--delay-minutes", type=int, default=60)
a = ap.parse_args()
d = ROOT / a.study
cfg_path = next(d.glob("config_*.json"))
cfg = json.loads(cfg_path.read_text())
if cfg.get("status") == "FROZEN":
    sys.exit("already FROZEN; changes after freeze need an amendment")
now = datetime.now(timezone.utc).replace(microsecond=0)
cfg.update(status="FROZEN", frozen_on=now.isoformat().replace("+00:00", "Z"),
           seed_time_utc=(now + timedelta(minutes=a.delay_minutes)).isoformat().replace("+00:00", "Z"))
cfg_path.write_text(json.dumps(cfg, indent=2))
subprocess.run([sys.executable, str(ROOT / "tools" / "freeze_study.py"), "freeze", a.study], check=True)
print(f"{a.study} frozen at {cfg['frozen_on']}; seed from the first drand round at/after {cfg['seed_time_utc']}")
