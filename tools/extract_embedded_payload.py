"""Extract code embedded in a workflow YAML as base64-encoded, xz-compressed payloads.

Usage:  python tools/extract_embedded_payload.py .github/workflows/p7-3-anchored-binder.yml p7/p7_3

Finds every  b64decode('''...''')  block, decodes it (whitespace is ignored), decompresses
xz/lzma when present, then: extracts it if it is a zip archive, otherwise writes the raw
bytes.  A MANIFEST.json with the sha256 of the payload and of every extracted file is
written next to the output, so the readable copy can be checked against the workflow.
Nothing is executed.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import lzma
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

BLOCK = re.compile(r"b64decode\(\s*(?:r|b)?'''(.*?)'''", re.S)


def _safe_member(name: str) -> bool:
    p = PurePosixPath(name)
    return not p.is_absolute() and ".." not in p.parts


def extract(workflow: Path, out_dir: Path) -> dict:
    text = workflow.read_text(encoding="utf-8")
    blocks = BLOCK.findall(text)
    if not blocks:
        raise SystemExit("no embedded b64decode('''...''') payload found")
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"workflow": str(workflow),
                "workflow_sha256": hashlib.sha256(workflow.read_bytes()).hexdigest(),
                "payloads": []}
    for i, block in enumerate(blocks):
        raw = base64.b64decode("".join(block.split()))
        entry = {"index": i, "encoded_sha256": hashlib.sha256(raw).hexdigest(),
                 "compression": "none", "files": {}}
        if raw[:6] == b"\xfd7zXZ\x00":
            raw = lzma.decompress(raw)
            entry["compression"] = "xz"
        entry["decoded_sha256"] = hashlib.sha256(raw).hexdigest()
        target = out_dir / (f"payload_{i}" if len(blocks) > 1 else "")
        target.mkdir(parents=True, exist_ok=True)
        if raw[:4] == b"PK\x03\x04":
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    if not _safe_member(info.filename):
                        raise SystemExit(f"unsafe path in archive: {info.filename}")
                    data = zf.read(info)
                    dest = target / info.filename
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
                    entry["files"][info.filename] = hashlib.sha256(data).hexdigest()
            entry["kind"] = "zip"
        else:
            dest = target / "payload.bin"
            dest.write_bytes(raw)
            entry["files"]["payload.bin"] = entry["decoded_sha256"]
            entry["kind"] = "raw"
        manifest["payloads"].append(entry)
        print(f"payload {i}: {entry['kind']}, {len(entry['files'])} file(s) -> {target}")
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    extract(Path(sys.argv[1]), Path(sys.argv[2]))
