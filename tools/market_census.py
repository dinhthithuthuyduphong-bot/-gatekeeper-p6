"""Study T phase 1 (study_t/PROTOCOL.md): census of market skills (Ruff autofix rules) and the twelve R2 families on the 60 most
downloaded pure-Python PyPI packages.  No target code runs; no model calls; no outcome is computed.

python tools/market_census.py WORK_DIR OUT_DIR [--targets 60] [--top TOP_JSON]

Writes TOP_PYPI_SNAPSHOT.json (the ranking used), TARGETS.json (selection, with every skipped project and why) and
MARKET_CENSUS.json (per package: fixable diagnostics by rule with Ruff's applicability and touched functions; cells; totals).
"""
import ast
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from footprint_census import is_test  # noqa: E402

TOP_URL = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
MAX_SDIST = 20 * 1024 * 1024
MIN_PY_FILES = 5


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "gatekeeper-study-t"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ------------------------------------------------------------------ target selection (protocol section 2)
def qualifies(meta):
    """(ok, reason, sdist) for one PyPI JSON document of a project's latest release."""
    name = meta["info"]["name"]
    if name.lower().startswith("types-") or name.lower().endswith("-stubs"):
        return False, "stub package", None
    files = meta.get("urls", [])
    if not any(f["packagetype"] == "bdist_wheel" and f["filename"].endswith("py3-none-any.whl") for f in files):
        return False, "no py3-none-any wheel", None
    sd = [f for f in files if f["packagetype"] == "sdist"]
    if not sd:
        return False, "no sdist", None
    if sd[0]["size"] > MAX_SDIST:
        return False, "sdist larger than 20 MB", None
    return True, "", sd[0]


def extract(blob, filename, dest):
    dest.mkdir(parents=True, exist_ok=True)
    if filename.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for m in z.namelist():
                if m.endswith(".py") and ".." not in m:
                    p = dest / m
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(z.read(m))
    else:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:*") as t:
            for m in t.getmembers():
                if m.isfile() and m.name.endswith(".py") and ".." not in m.name and not m.name.startswith("/"):
                    p = dest / m.name
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(t.extractfile(m).read())
    return dest


def source_files(root):
    return [p for p in sorted(root.rglob("*.py")) if not is_test(p.relative_to(root).as_posix())]


def select_targets(top, work, k, skip=0):
    """The first k qualifying projects after the first `skip` qualifying ones (Study T2 continues Study T's list)."""
    chosen, skipped, passed = [], [], 0
    for row in top["rows"]:
        if len(chosen) >= k:
            break
        name = row["project"]
        try:
            meta = json.loads(fetch("https://pypi.org/pypi/%s/json" % name))
        except Exception as exc:  # noqa: BLE001 - network or missing project: skipped with the reason
            skipped.append({"project": name, "reason": "PyPI metadata: %s" % type(exc).__name__})
            continue
        ok, why, sd = qualifies(meta)
        if not ok:
            skipped.append({"project": name, "reason": why})
            continue
        blob = fetch(sd["url"], 300)
        root = extract(blob, sd["filename"], work / name)
        n = len(source_files(root))
        if n < MIN_PY_FILES:
            skipped.append({"project": name, "reason": "fewer than %d non-test .py files (%d)" % (MIN_PY_FILES, n)})
            continue
        if passed < skip:
            passed += 1
            continue
        chosen.append({"rank": skip + len(chosen) + 1, "download_rank": top["rows"].index(row) + 1, "project": name,
                       "version": meta["info"]["version"], "sdist": sd["filename"], "sha256": hashlib.sha256(blob).hexdigest(),
                       "py_files": n, "root": str(root)})
    return chosen, skipped


# ------------------------------------------------------------------ sites
def function_index(src):
    """[(start, end, qualname)] of every def (nested included, innermost wins when looked up)."""
    out = []

    def walk(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, ast.ClassDef):
                walk(ch, prefix + ch.name + ".")
            elif isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append((ch.lineno, ch.end_lineno, prefix + ch.name))
                walk(ch, prefix + ch.name + ".<locals>.")
            else:
                walk(ch, prefix)
    walk(ast.parse(src), "")
    return out


def enclosing(index, line):
    best = None
    for s, e, q in index:
        if s <= line <= e and (best is None or s >= best[0]):
            best = (s, e, q)
    return best[2] if best else "<module>"


def ruff_version():
    return subprocess.run(["ruff", "--version"], capture_output=True, text=True).stdout.strip()


def ruff_rules():
    """{code: {"name", "fix", "has_example"}} from `ruff rule --all`."""
    r = subprocess.run(["ruff", "rule", "--all", "--output-format", "json"], capture_output=True, text=True, check=True)
    out = {}
    for d in json.loads(r.stdout):
        expl = d.get("explanation", "") or ""
        out[d["code"]] = {"name": d.get("name"), "fix": d.get("fix") or d.get("fix_availability"),
                          "preview": d.get("preview", False),
                          "has_example": "## Example" in expl and "Use instead" in expl}
    return out


def ruff_sites(root):
    files = [str(p) for p in source_files(root)]
    if not files:
        return []
    r = subprocess.run(["ruff", "check", "--isolated", "--no-cache", "--select", "ALL", "--output-format", "json", "--exit-zero",
                        *files], capture_output=True, text=True, timeout=1800)
    diags = json.loads(r.stdout or "[]")
    idx_cache, out = {}, []
    for d in diags:
        if not d.get("fix"):
            continue
        path = Path(d["filename"])
        rel = path.relative_to(root).as_posix()
        if rel not in idx_cache:
            try:
                idx_cache[rel] = function_index(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError, ValueError):
                idx_cache[rel] = None
        if idx_cache[rel] is None:
            continue
        line = d["location"]["row"]
        out.append({"rule": d["code"], "file": rel, "line": line, "function": enclosing(idx_cache[rel], line),
                    "applicability": d["fix"].get("applicability")})
    return out


def r2_sites(root):
    from library_census import load_skills, apply_all
    skills = load_skills()
    out = []
    for p in source_files(root):
        rel = p.relative_to(root).as_posix()
        try:
            src = p.read_text(encoding="utf-8")
            index = function_index(src)
        except (SyntaxError, UnicodeDecodeError, ValueError, RecursionError):
            continue
        for name, sk in skills.items():
            try:
                _, sites = apply_all(sk, src)
            except (SyntaxError, ValueError, RecursionError):
                continue
            for func, _snip in sites:
                out.append({"rule": "R2:" + name, "file": rel, "line": None, "function": func, "applicability": "r2"})
    return out


def cells_of(sites):
    by = defaultdict(list)
    for s in sites:
        by[s["rule"]].append(s)
    cells = {}
    for rule, ss in sorted(by.items()):
        app = sorted({s["applicability"] for s in ss})
        cells[rule] = {"sites": len(ss), "functions": sorted({"%s::%s" % (s["file"], s["function"]) for s in ss}),
                       "applicability": app[0] if len(app) == 1 else "mixed"}
    return cells


def census(work, out, k, top_path=None, skip=0):
    top = json.loads(Path(top_path).read_text()) if top_path else json.loads(fetch(TOP_URL))
    (out / "TOP_PYPI_SNAPSHOT.json").write_text(json.dumps(top))
    targets, skipped = select_targets(top, work, k, skip)
    (out / "TARGETS.json").write_text(json.dumps({"selected": targets, "skipped": skipped,
                                                   "top_last_update": top.get("last_update")}, indent=1))
    rules = ruff_rules()
    pk = []
    for t in targets:
        root = Path(t["root"])
        sites = ruff_sites(root) + r2_sites(root)
        pk.append({"project": t["project"], "version": t["version"], "cells": cells_of(sites)})
    all_cells = [(p["project"], r, c) for p in pk for r, c in p["cells"].items()]
    rule_counts = Counter(r for _, r, _ in all_cells)
    total = {"ruff_version": ruff_version(), "targets": len(targets), "skipped": len(skipped),
             "cells": len(all_cells), "cells_ruff": sum(1 for _, r, _ in all_cells if not r.startswith("R2:")),
             "cells_r2": sum(1 for _, r, _ in all_cells if r.startswith("R2:")),
             "skills_with_a_cell": len(rule_counts),
             "ruff_rules_fixable_stable": sum(1 for v in rules.values() if v["fix"] and "not" not in str(v["fix"]).lower()
                                              and not v["preview"]),
             "cells_by_applicability": dict(Counter(c["applicability"] for _, _, c in all_cells)),
             "cells_ruff_rules_with_doc_example": sum(1 for _, r, _ in all_cells if rules.get(r, {}).get("has_example")),
             "rule_prefixes": dict(Counter(''.join(ch for ch in r if ch.isalpha()) for r in rule_counts if not r.startswith("R2:")))}
    res = {"total": total, "rules": rules, "packages": pk}
    (out / "MARKET_CENSUS.json").write_text(json.dumps(res, indent=1))
    return res


def main(argv):
    work, out = Path(argv[0]), Path(argv[1])
    k = int(argv[argv.index("--targets") + 1]) if "--targets" in argv else 60
    top = argv[argv.index("--top") + 1] if "--top" in argv else None
    skip = int(argv[argv.index("--skip") + 1]) if "--skip" in argv else 0
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    res = census(work, out, k, top, skip)
    print(json.dumps(res["total"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
