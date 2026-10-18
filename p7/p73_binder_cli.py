"""CLI wrapper: P7.3 binder v3 (frozen) behind Gatekeeper-Lite's external_command contract.

python p7/p73_binder_cli.py --in SRC --out DST --receipt RECEIPT.json
Refuses to run if any frozen file differs from BINDER_FREEZE.json (fail closed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent / "p7_3"


def _verify_freeze() -> None:
    freeze = json.loads((HERE / "BINDER_FREEZE.json").read_text(encoding="utf-8"))
    for name, digest in freeze["files"].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if actual != digest:
            raise SystemExit(f"frozen file changed: {name}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--receipt", required=True)
    args = ap.parse_args(argv)
    _verify_freeze()
    sys.path.insert(0, str(HERE))
    import anchored_binder  # noqa: E402  (frozen P7.3 code)

    source = Path(args.src).read_text(encoding="utf-8")
    v2 = json.loads((HERE / "GUARDED_TEMPLATE_V2.json").read_text(encoding="utf-8"))
    output, decision = anchored_binder.apply(source, v2)
    Path(args.dst).write_text(output, encoding="utf-8")
    applied = decision["decision"].startswith("APPLIED")
    scope = decision.get("scope", "")
    function = scope.split(".")[-1] if scope else "?"
    receipt = {"status": "APPLIED" if applied else "ABSTAIN",
               "reason": decision["decision"],
               "binder_decision": decision,
               "sites": [{"line": 0, "function": function, "snippet": scope}] if applied else [],
               "footprint": [f"func:{function}", "subject:default_value"] if applied else []}
    Path(args.receipt).write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
