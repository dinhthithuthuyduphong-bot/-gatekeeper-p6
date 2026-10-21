"""Fail-closed, zero-cost preflight for B9 Actions runs.

This tool never authenticates to a model or sends an API request.
It does not replace a billing hard cap or the provider-side quota.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {
    "study_d/b9_config.json",
    "study_f/b9_config_f.json",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def check_freeze(study: str) -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools/freeze_study.py"), "verify", study],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        fail(f"{study} freeze verification failed:\n{proc.stdout}\n{proc.stderr}")


def validate(config: str, target: str, model: str, mode: str, now=None,
             *, verify_freezes=True) -> str:
    """Return a human-readable preflight result or raise ValueError.

    An explicit reviewer signoff is needed to lift the paid-run hold.
    The hold is not a billing guarantee: direct invocation of the original
    frozen tools/run_b9.py is outside this Actions workflow.
    """
    if config not in ALLOWED:
        fail("B9 config must be one of the two exact approved repository paths")
    if mode not in ("record", "replay"):
        fail("B9 mode must be record or replay")
    if not target or not model:
        fail("Target and model are required")

    b9 = load_json(config)
    study_f = load_json("study_f/config_study_f.json")
    model_configs = study_f.get("b9_configs", {})
    if model_configs.get(model) != config:
        fail(f"Study F does not map model {model!r} to config {config!r}")
    if model not in {m.get("name") for m in b9.get("models", [])}:
        fail(f"Model {model!r} is absent from B9 config")
    if target not in b9.get("instances", []):
        fail(f"Target {target!r} is absent from B9 instances")
    if target not in study_f.get("cells", []):
        fail(f"Target {target!r} is absent from Study F target family")
    if b9.get("status") != "FROZEN" or study_f.get("status") != "FROZEN":
        fail("Study F and the selected B9 config must both be FROZEN")

    if verify_freezes:
        check_freeze("study_d")
        check_freeze("study_f")

    if mode == "replay":
        return "REPLAY_PREFLIGHT_OK (no model call authorized by this check)"

    now = now or datetime.now(timezone.utc)
    for name, cfg in (("B9 config", b9), ("Study F", study_f)):
        raw = cfg.get("not_before_utc") if name == "B9 config" else cfg.get("frozen_on")
        if not raw:
            fail(f"{name}: missing time field")
        ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if name == "Study F" and ts >= now:
            fail("Study F freeze timestamp is not in the past")
        if name == "B9 config" and now < ts:
            fail(f"Paid B9 forbidden before {raw}")
    for item in b9["models"]:
        if item["name"] != model:
            continue
        prices = item.get("prices_usd_per_mtok", {})
        if any(float(prices.get(k, 0)) <= 0 for k in ("input", "output")):
            fail("Positive input and output list prices are required")
        if "VERIFY_AT_FREEZE" in json.dumps(item):
            fail("Unverified model metadata remains")

    release = load_json("pre_b9/RELEASE_GATE.json")
    if release.get("status") != "GO":
        fail("PRE_B9_REVIEW_HOLD: paid record disabled pending independent audit and explicit GO change")
    if release.get("approved_for") != "study-f-v1":
        fail("Release gate must explicitly name study-f-v1")
    return "RECORD_PREFLIGHT_OK (software checks only; not a billing cap)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--mode", required=True)
    args = parser.parse_args()
    try:
        print(validate(args.config, args.target, args.model, args.mode))
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
