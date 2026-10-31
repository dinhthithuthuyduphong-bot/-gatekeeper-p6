"""Record exactly what was submitted (PAPER_TODO 6.1).

python tools/snapshot_submission.py OUT_DIR --venue V --paper-id ID --pdf PAPER.pdf [--artifact-zip Z] [--artifact-manifest M]
                                      [--artifact-url URL] [--date YYYY-MM-DD] [--commit SHA]

Copies the PDF (and the artifact manifest) into OUT_DIR and writes SUBMISSION.json with the venue, paper id, date, the git commit the
PDF was built from, and the SHA-256 of the PDF, the artifact zip and its manifest, so that the submitted version can be identified
and rebuilt later.  Refuses to overwrite an existing snapshot.
"""
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv):
    out = Path(argv[0])
    venue, pid, pdf = arg(argv, "--venue"), arg(argv, "--paper-id"), arg(argv, "--pdf")
    if not (venue and pid and pdf):
        raise SystemExit("need --venue, --paper-id and --pdf")
    if (out / "SUBMISSION.json").exists():
        raise SystemExit("snapshot already exists: %s" % out)
    out.mkdir(parents=True, exist_ok=True)
    commit = arg(argv, "--commit") or subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    rec = {"venue": venue, "paper_id": pid, "date": arg(argv, "--date") or datetime.date.today().isoformat(), "commit": commit,
           "paper_pdf": "paper.pdf", "paper_pdf_sha256": sha(pdf), "artifact_url": arg(argv, "--artifact-url")}
    shutil.copy(pdf, out / "paper.pdf")
    z, m = arg(argv, "--artifact-zip"), arg(argv, "--artifact-manifest")
    if z:
        rec["artifact_zip_sha256"] = sha(z)
    if m:
        shutil.copy(m, out / "ARTIFACT_MANIFEST_SHA256.json")
        rec["artifact_manifest_sha256"] = sha(m)
        rec["artifact_files"] = len(json.loads(Path(m).read_text()))
    (out / "SUBMISSION.json").write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
