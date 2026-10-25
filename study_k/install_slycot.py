"""Install one checksum-pinned conda-forge Slycot binary into a fresh Linux CPython 3.8 venv.

This is a dependency restore, not a target-code shim. BLAS/LAPACK/gfortran shared
libraries must already be installed. No provider credentials or model calls.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import sysconfig
import tarfile
import urllib.request

URL = "https://api.anaconda.org/download/conda-forge/slycot/0.4.0.0/linux-64/slycot-0.4.0.0-py38hf9f4372_4.tar.bz2"
SHA256 = "6ca4f5e8df4140f3ee9361a6449b4074226e3422f67976a5967946ee174b4fd3"


def main(output):
    if sys.version_info[:2] != (3,8) or sys.platform != "linux" or platform.machine() != "x86_64":
        raise RuntimeError("This pinned binary is only for Linux x86_64 CPython 3.8")
    site = Path(sysconfig.get_paths()["purelib"]).resolve()
    if (site / "slycot").exists():
        raise RuntimeError("Use a fresh environment; do not overwrite an existing Slycot installation")
    with urllib.request.urlopen(URL, timeout=90) as response:
        raw = response.read()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise RuntimeError("Slycot archive checksum mismatch")
    prefix = "lib/python3.8/site-packages/"
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:bz2") as archive:
        for member in archive.getmembers():
            if not member.name.startswith(prefix) or not member.isfile():
                continue
            rel = Path(member.name[len(prefix):])
            if rel.is_absolute() or ".." in rel.parts:
                raise RuntimeError("Unsafe archive path")
            dest = site / rel
            try:
                dest.resolve().relative_to(site)
            except ValueError:
                raise RuntimeError("Archive destination escapes site-packages")
            payload = archive.extractfile(member).read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(payload)
            files[str(rel)] = hashlib.sha256(payload).hexdigest()
        metadata = json.loads(archive.extractfile("info/index.json").read())
    command=[sys.executable,"-c","import slycot; from slycot import tb04ad; print(slycot.__version__, slycot.__file__)"]
    check=subprocess.run(command,capture_output=True,text=True)
    record={"source_url":URL,"sha256":SHA256,"metadata":metadata,"installed_sha256":files,
            "command":command,"returncode":check.returncode,"stdout":check.stdout,"stderr":check.stderr}
    Path(output).write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({k:record[k] for k in ("source_url","sha256","returncode","stdout","stderr")}),flush=True)
    if check.returncode:
        raise RuntimeError("Slycot shared-library/import check failed; see receipt")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt",required=True)
    main(parser.parse_args().receipt)
