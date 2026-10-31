"""Build the anonymous artifact for double-blind review (PAPER_TODO 5.2).

python tools/make_anonymous_artifact.py OUT_DIR --owner GITHUB_OWNER [--identifier STR ...]

1. Copies the files tracked by git, minus internal or identifying material (EXCLUDE): process logs, tracking and to-do notes,
   archived update packages, the AI-generated draft PDFs, and the .git directory (author names and e-mails).
2. Replaces every link to the GitHub repository by an anonymous placeholder.
3. Scans the result (text files, and the content of .gz / .tar.gz members) for identifiers: the repository owner, the author
   names and e-mails found in `git log` (bots excluded), and any --identifier.  Any hit makes the script fail.
4. Writes ANON_REPORT.json (what was excluded, what was replaced, residual hits) and MANIFEST_SHA256.json, then a zip.
Frozen files never contain the owner's name (checked when this tool was written), so study freezes still verify inside the
artifact; the submission-check workflow verifies that.
"""
import gzip
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_PREFIXES = ("archive/", "docs/history/", "docs/paper/source/", ".git/")
EXCLUDE_FILES = {"docs/PROCESS_LOG.md", "docs/TRACKING_FSE.md", "docs/PAPER_TODO.md", "docs/paper/PAPER_AUDIT.md",
                 "docs/paper/REVIEW_FSE.md", "docs/paper/CITATIONS_AUDIT.md", "research_closure/PRIVATE_SOURCE_DIGESTS.json"}
PLACEHOLDER_REPO = "ANONYMOUS/gatekeeper-artifact"
BOTS = ("gatekeeper-freeze-bot", "actions@users.noreply.github.com", "Claude", "noreply@anthropic.com", "github-actions")


def tracked_files():
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    return [f for f in out if f]


def git_identifiers():
    out = subprocess.check_output(["git", "log", "--format=%an%n%ae"], cwd=ROOT).decode().split("\n")
    ids = set()
    for s in out:
        s = s.strip()
        if s and not any(b == s for b in BOTS):
            ids.add(s)
            if "@" in s:
                ids.add(s.split("@")[0])
    return ids


def excluded(rel):
    return rel.startswith(EXCLUDE_PREFIXES) or rel in EXCLUDE_FILES


def scan_bytes(data, needles):
    low = data.lower()
    return sorted({n for n in needles if n.lower().encode() in low})


def scan_file(path, needles):
    data = path.read_bytes()
    hits = scan_bytes(data, needles)
    name = path.name
    try:
        if name.endswith((".tar.gz", ".tgz")):
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
                for m in t.getmembers():
                    if m.isfile():
                        hits += scan_bytes(t.extractfile(m).read(), needles)
        elif name.endswith(".gz"):
            hits += scan_bytes(gzip.decompress(data), needles)
    except (OSError, tarfile.TarError):
        pass
    return sorted(set(hits))


def build(out_dir, owner, extra_ids=()):
    out = Path(out_dir)
    tree = out / "gatekeeper-artifact"
    if tree.exists():
        shutil.rmtree(tree)
    tree.mkdir(parents=True)
    repo_pat = re.compile(r"(https?://(?:api\.)?github\.com/(?:repos/)?)%s/-?gatekeeper-p6" % re.escape(owner))
    plain_pat = re.compile(r"%s/-?gatekeeper-p6" % re.escape(owner))
    report = {"excluded": [], "replaced": {}, "residual_hits": {}}
    for rel in tracked_files():
        src = ROOT / rel
        if excluded(rel):
            report["excluded"].append(rel)
            continue
        if not src.is_file():
            continue
        dst = tree / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            dst.write_bytes(data)
            continue
        new, n1 = repo_pat.subn(lambda m: m.group(1) + PLACEHOLDER_REPO, text)
        new, n2 = plain_pat.subn(PLACEHOLDER_REPO, new)
        new, n3 = re.subn(re.escape(owner), "ANONYMOUS", new)
        if n1 + n2 + n3:
            report["replaced"][rel] = n1 + n2 + n3
        dst.write_text(new, encoding="utf-8")
    readme = ROOT / "docs/paper/ARTIFACT_README.md"
    if readme.is_file():
        shutil.copy(readme, tree / "README_ARTIFACT.md")
    needles = {owner} | git_identifiers() | set(extra_ids)
    needles = {n for n in needles if len(n) >= 4}
    manifest = {}
    for p in sorted(tree.rglob("*")):
        if p.is_file():
            rel = p.relative_to(tree).as_posix()
            hits = scan_file(p, needles)
            if hits:
                report["residual_hits"][rel] = hits
            manifest[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    report["identifiers_checked"] = len(needles)
    report["files"] = len(manifest)
    (out / "ANON_REPORT.json").write_text(json.dumps(report, indent=1))
    (out / "MANIFEST_SHA256.json").write_text(json.dumps(manifest, indent=1))
    with zipfile.ZipFile(out / "gatekeeper-artifact.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(tree.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(out).as_posix())
    return report


def main(argv):
    out = argv[0]
    owner = argv[argv.index("--owner") + 1]
    extra = [argv[i + 1] for i, a in enumerate(argv) if a == "--identifier"]
    rep = build(out, owner, extra)
    print(json.dumps({"files": rep["files"], "excluded": len(rep["excluded"]), "files_with_replacements": len(rep["replaced"]),
                      "replacements": sum(rep["replaced"].values()), "residual_hits": rep["residual_hits"]}, indent=1))
    return 1 if rep["residual_hits"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
