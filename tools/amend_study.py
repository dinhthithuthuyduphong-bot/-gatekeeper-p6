"""Apply a documented amendment to any frozen study (generalises amend_study_d.py).
python tools/amend_study.py STUDY_DIR AMENDMENT_ID ['FILE:dotted.key=JSON' ...]
Pins the seed to the ORIGINAL freeze hash, applies the listed edits, re-freezes."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _set(doc, dotted: str, value):
    """Set doc[a][b][...] = value for a dotted key; integer parts index lists."""
    keys = dotted.split(".")
    cur = doc
    for k in keys[:-1]:
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    if isinstance(cur, list):
        cur[int(keys[-1])] = value
    else:
        cur[keys[-1]] = value


def main(study_dir, amendment_id, *sets):
    d = ROOT / study_dir
    cfg_path = next(d.glob("config_*.json"))
    cfg = json.loads(cfg_path.read_text())
    if cfg.get("status") != "FROZEN":
        raise SystemExit("amendments apply only to a FROZEN study")
    if amendment_id not in (d / "AMENDMENTS.md").read_text():
        raise SystemExit(f"{amendment_id} is not documented in {study_dir}/AMENDMENTS.md")
    if amendment_id in cfg.get("amendments_applied", []):
        raise SystemExit(f"{amendment_id} already applied")
    cfg.setdefault("seed_freeze_sha256", hashlib.sha256((d / "FREEZE.json").read_bytes()).hexdigest())
    applied = []
    for spec in sets:
        fname, _, rest = spec.partition(":")
        key, _, raw = rest.partition("=")
        if fname == cfg_path.name:
            _set(cfg, key, json.loads(raw))
        else:
            fp = d / fname
            doc = json.loads(fp.read_text())
            _set(doc, key, json.loads(raw))
            fp.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
        applied.append(spec)
    cfg.setdefault("amendments_applied", []).append(amendment_id)
    cfg.setdefault("amendment_log", []).append({"id": amendment_id, "edits": applied,
                                                "applied_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    cfg_path.write_text(json.dumps(cfg, indent=2))
    subprocess.run([sys.executable, str(ROOT / "tools" / "freeze_study.py"), "freeze", study_dir], check=True)
    print(f"{study_dir} {amendment_id} applied; seed stays derived from {cfg['seed_freeze_sha256'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
