"""Pin every GitHub Action used by the workflows to a full commit SHA (supply-chain safety and reproducibility of frozen evidence).

python tools/pin_actions.py [--check] [--resolve-only] [--mapping FILE] [--upgrade OWNER/REPO=TAG ...]

Rewrites `uses: owner/repo@vX` as `uses: owner/repo@<40-hex sha> # vX`, resolving tags with `gh api` (annotated tags are peeled
to their commit).  Already pinned uses keep their SHA.  --upgrade replaces a tag before resolving (e.g. move
google-github-actions/auth from v2, which runs on the deprecated Node 20, to v3 if that tag exists).  --check only reports what is
not pinned and exits 1 if anything is.  --resolve-only resolves every tag and prints the mapping without touching files (run it in
GitHub Actions: GITHUB_TOKEN can read public action repositories but may not modify workflow files); --mapping FILE then applies
that mapping offline (a JSON object "owner/repo@tag" -> sha).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USES = re.compile(r"^(\s*-?\s*uses:\s*)([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+)@([^\s#]+)(\s*#\s*(\S+))?\s*$")
SHA = re.compile(r"^[0-9a-f]{40}$")


def resolve(repo, tag, api=None):
    api = api or (lambda path: json.loads(subprocess.check_output(["gh", "api", path])))
    obj = api("repos/%s/git/ref/tags/%s" % (repo.split("/")[0] + "/" + repo.split("/")[1], tag))["object"]
    if obj["type"] == "tag":                               # annotated tag: peel to the commit
        obj = api("repos/%s/git/tags/%s" % ("/".join(repo.split("/")[:2]), obj["sha"]))["object"]
    return obj["sha"]


def rewrite(text, upgrades, resolver, cache):
    out, changed, unpinned = [], 0, []
    for line in text.splitlines(keepends=True):
        m = USES.match(line.rstrip("\n"))
        if not m or m.group(2).startswith("./"):
            out.append(line)
            continue
        prefix, repo, ref, comment_tag = m.group(1), m.group(2), m.group(3), m.group(5)
        if SHA.match(ref):
            out.append(line)                               # already pinned
            continue
        tag = upgrades.get(repo, ref)
        unpinned.append("%s@%s" % (repo, ref))
        if resolver is None:
            out.append(line)
            continue
        key = (repo, tag)
        if key not in cache:
            cache[key] = resolver(repo, tag)
        out.append("%s%s@%s # %s\n" % (prefix, repo, cache[key], tag))
        changed += 1
    return "".join(out), changed, unpinned


def main(argv):
    check = "--check" in argv
    upgrades = dict(a.split("=", 1) for i, a in enumerate(argv) if i > 0 and argv[i - 1] == "--upgrade")
    cache, total, report = {}, 0, {}
    resolver = resolve
    if "--mapping" in argv:
        mapping = json.loads(Path(argv[argv.index("--mapping") + 1]).read_text())
        resolver = lambda repo, tag: mapping["%s@%s" % (repo, tag)]   # noqa: E731
    if "--resolve-only" in argv:
        for wf in sorted((ROOT / ".github/workflows").glob("*.y*ml")):
            rewrite(wf.read_text(), upgrades, resolver, cache)
        print("MAPPING_JSON=" + json.dumps({"%s@%s" % k: v for k, v in cache.items()}, sort_keys=True))
        return 0
    for wf in sorted((ROOT / ".github/workflows").glob("*.y*ml")):
        text = wf.read_text()
        new, n, unpinned = rewrite(text, upgrades, None if check else resolver, cache)
        if unpinned:
            report[wf.name] = sorted(set(unpinned))
        if not check and n:
            wf.write_text(new)
            total += n
    print(json.dumps({"files_with_unpinned": len(report), "rewritten_uses": total,
                      "resolved": {"%s@%s" % k: v for k, v in cache.items()}}, indent=1))
    return 1 if (check and report) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
