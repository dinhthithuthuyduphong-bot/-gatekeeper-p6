"""Vetting, version 2: same classification as tools/vet_target.py, with a registered environment-provisioning procedure.

python tools/vet_target2.py SPEC.json OUT_DIR

Why: in Study M stage S2, 169 of 250 candidates could not run their tests only because a Python module was missing
(tools/vet_target.py stops at the first `pip install` that exits 0, and pip exits 0 even when the requested extra does
not exist; requirement files, tox, dependency groups and setuptools were never installed).  tools/vet_target.py is
frozen and is not modified; this file reuses its helpers.

Provisioning (identical for both arms, decided before any outcome; recorded step by step in the report):
  1. pip, setuptools, wheel upgraded (Python 3.12 venvs have no setuptools, hence no pkg_resources).
  2. the package with ALL extras it declares (pyproject optional-dependencies, setup.cfg extras_require); fallbacks:
     [test], [dev], plain, editable.
  3. dependency groups (PEP 735), Poetry groups, Hatch environment dependencies, except docs/lint/typing/release groups.
  4. requirement files at the root, in requirements/, in tests/ (names containing "requirement", not "doc").
  5. tox [testenv] deps.  6. pytest.
  7. collection repair: at most 4 rounds of `pytest --collect-only`; every `No module named X` seen in EITHER arm, that is
     not a module of the repository itself, is installed in BOTH arms (a fixed table maps import names to package names).
Tests are never edited and test OUTCOMES are never used by the provisioning.
"""
import configparser
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import vet_target as V  # noqa: E402  (frozen helpers: sh, pr_info, resolve, checkout_to, run_tests, _test_sources)

SKIP_GROUP = re.compile(r"doc|lint|typ|mypy|release|publish|format|style|bench", re.I)
IMPORT_TO_PACKAGE = {
    "yaml": "PyYAML", "sklearn": "scikit-learn", "PIL": "Pillow", "cv2": "opencv-python-headless", "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil", "jwt": "PyJWT", "Crypto": "pycryptodome", "attr": "attrs", "OpenSSL": "pyOpenSSL",
    "magic": "python-magic", "dotenv": "python-dotenv", "pkg_resources": "setuptools", "docx": "python-docx",
    "serial": "pyserial", "usb": "pyusb", "git": "GitPython", "google": "protobuf", "jose": "python-jose",
    "multipart": "python-multipart", "pytest_asyncio": "pytest-asyncio", "pytest_mock": "pytest-mock",
    "pytest_django": "pytest-django", "pytest_httpx": "pytest-httpx", "pytest_lazyfixture": "pytest-lazy-fixture",
    "lxml": "lxml", "zmq": "pyzmq", "Levenshtein": "python-Levenshtein", "skimage": "scikit-image", "fitz": "PyMuPDF",
    "telegram": "python-telegram-bot", "slugify": "python-slugify", "socks": "PySocks", "nacl": "PyNaCl",
}
MAX_REPAIR_ROUNDS = 4


def _toml(src):
    p = Path(src) / "pyproject.toml"
    try:
        return tomllib.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        return {}


def declared_extras(src):
    extras = list(((_toml(src).get("project") or {}).get("optional-dependencies") or {}).keys())
    cfg = Path(src) / "setup.cfg"
    if cfg.exists():
        cp = configparser.ConfigParser()
        try:
            cp.read(cfg, encoding="utf-8")
            if cp.has_section("options.extras_require"):
                extras += list(cp["options.extras_require"].keys())
        except configparser.Error:
            pass
    return sorted(set(e for e in extras if not SKIP_GROUP.search(e)))


def _names(specs):
    out = []
    for s in specs:
        if isinstance(s, str):
            name = re.split(r"[\s;<>=!~\[]", s.strip(), 1)[0]
            if name and not name.startswith(("-", "{", "#", ".")) and name.lower() != "python":
                out.append(s.split(";")[0].strip())
    return out


def group_dependencies(src):
    """Package specifiers from PEP 735 groups, Poetry groups and Hatch environments (docs/lint/typing groups skipped)."""
    t, out = _toml(src), []
    for g, deps in (t.get("dependency-groups") or {}).items():
        if not SKIP_GROUP.search(g):
            out += _names(d for d in deps if isinstance(d, str))
    poetry = (t.get("tool") or {}).get("poetry") or {}
    for g, body in (poetry.get("group") or {}).items():
        if not SKIP_GROUP.search(g):
            out += [k for k in (body.get("dependencies") or {}) if k.lower() != "python"]
    out += [k for k in (poetry.get("dev-dependencies") or {}) if k.lower() != "python"]
    for name, env in ((t.get("tool") or {}).get("hatch") or {}).get("envs", {}).items():
        if not SKIP_GROUP.search(name):
            out += _names(env.get("dependencies") or []) + _names(env.get("extra-dependencies") or [])
    return sorted(set(out))


def requirement_files(src):
    src = Path(src)
    found = []
    for d in (src, src / "requirements", src / "tests", src / "test"):
        if d.is_dir():
            found += [p for p in sorted(d.glob("*.txt")) if "requirement" in p.name.lower() or d.name == "requirements"]
    found = [p for p in found if "doc" not in p.name.lower()]
    rel = [str(p.relative_to(src)) for p in found]
    return sorted(rel, key=lambda r: (r.lower() != "requirements.txt", r))      # the root runtime file first


def tox_deps(src):
    p = Path(src) / "tox.ini"
    if not p.exists():
        return []
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    try:
        cp.read(p, encoding="utf-8")
        raw = cp.get("testenv", "deps", fallback="")
    except configparser.Error:
        return []
    return _names(ln for ln in raw.splitlines() if ln.strip() and not ln.strip().startswith(("-r", "-c")))


def local_modules(src):
    src = Path(src)
    mods = set()
    for base in (src, src / "src"):
        if base.is_dir():
            mods |= {p.name for p in base.iterdir() if p.is_dir() and (p / "__init__.py").exists()}
            mods |= {p.stem for p in base.glob("*.py")}
    return mods


def missing_modules(text):
    return sorted({m.split(".")[0] for m in re.findall(r"No module named '([\w\.]+)'", text or "")})


def package_for(module):
    return IMPORT_TO_PACKAGE.get(module, module.replace("_", "-"))


def pip(py, args, log, cwd=None):
    r = V.sh([str(py), "-m", "pip", "install", "-q", *args], check=False, cwd=cwd, timeout=900)
    log.append({"pip": args, "exit": r.returncode, "tail": (r.stderr or "")[-300:] if r.returncode else ""})
    return r.returncode


def provision(py, src, extras_fallback, log):
    pip(py, ["--upgrade", "pip", "setuptools", "wheel"], log)
    extras = declared_extras(src)
    tries = ([extras] if extras else []) + [[e] for e in extras_fallback] + [[]]
    for ex in tries:
        target = "%s[%s]" % (src, ",".join(ex)) if ex else str(src)
        if pip(py, [target], log) == 0:
            break
    else:
        pip(py, ["-e", str(src)], log)
    deps = group_dependencies(src)
    if deps:
        pip(py, deps, log)
    for req in requirement_files(src):
        pip(py, ["-r", req], log, cwd=src)
    tox = tox_deps(src)
    if tox:
        pip(py, tox, log)
    pip(py, ["pytest"], log)


def collect(py, src, tests):
    r = V.sh([str(py), "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", "-o", "addopts=",
              "--continue-on-collection-errors", *tests], cwd=src, check=False, timeout=900)
    return (r.stdout or "") + (r.stderr or "")


def repair(arms, tests, repairs):
    """arms: {name: (py, src)}.  Installs the union of missing third-party modules into every arm."""
    local = set().union(*(local_modules(src) for _, src in arms.values()))
    installed = set()
    for rnd in range(MAX_REPAIR_ROUNDS):
        missing = set()
        for py, src in arms.values():
            missing |= set(missing_modules(collect(py, src, tests)))
        new = sorted(m for m in missing - installed - local)
        repairs.append({"round": rnd + 1, "missing": sorted(missing), "installing": new})
        if not new:
            break
        for name, (py, src) in arms.items():
            for m in new:
                pip(py, [package_for(m)], repairs[-1].setdefault("log_" + name, []))
        installed |= set(new)


def classify(pre_r, gold_r):
    coll = {t for t in set(pre_r) | set(gold_r) if t.startswith("::")}
    cls = {}
    for t in sorted((set(pre_r) | set(gold_r)) - coll):
        a, b = pre_r.get(t), gold_r.get(t)
        if a is None and b is not None:
            cls[t] = "ERR(pre)"
        elif b is None:
            cls[t] = "ERR(gold)"
        else:
            cls[t] = "%s->%s" % ("P" if a["passed"] else "F", "P" if b["passed"] else "F")
    return coll, cls


def main(spec_path, out_dir):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="vet2_"))
    report = {"name": spec["name"], "repo": spec["repo"], "python": sys.version.split()[0], "tool": "vet_target2"}
    try:
        repo = work / "repo"
        repo.mkdir()
        info = V.pr_info(spec)
        report["pr_info"] = info
        if (info.get("mergeCommit") or {}).get("oid"):
            spec = dict(spec, gold=info["mergeCommit"]["oid"], pre="parent")
        pre, gold = V.resolve(spec, repo)
        report.update(pre=pre, gold=gold)
        changed = V.sh([*V.GIT, "diff", "--name-only", pre, gold], cwd=repo).stdout.split()
        test_files = [f for f in changed if "test" in f.split("/")[-1] and f.endswith(".py")]
        src_files = [f for f in changed if f.endswith(".py") and f not in test_files]
        report.update(changed_files=changed, gold_test_files=test_files)
        report["gold_source_diff"] = V.sh([*V.GIT, "diff", pre, gold, "--", *src_files], cwd=repo).stdout[-12000:] if src_files else ""
        arms, logs = {}, {}
        for arm, rev in (("pre", pre), ("gold", gold)):
            src = work / arm
            V.checkout_to(repo, rev, src)
            if arm == "pre":
                for f in test_files:
                    blob = subprocess.run([*V.GIT, "show", "%s:%s" % (gold, f)], cwd=repo, capture_output=True)
                    if blob.returncode == 0:            # a test file deleted by the fix is simply not copied
                        (src / f).parent.mkdir(parents=True, exist_ok=True)
                        (src / f).write_bytes(blob.stdout)
            venv.EnvBuilder(with_pip=True).create(work / ("venv_" + arm))
            py = work / ("venv_" + arm) / "bin" / "python"
            logs[arm] = []
            provision(py, src, spec.get("extras", ["test", "dev"]), logs[arm])
            arms[arm] = (py, src)
        tests = spec.get("tests") or [f for f in test_files if (work / "gold" / f).exists()]
        repairs = []
        repair(arms, tests, repairs)
        res = {arm: V.run_tests(py, src, tests, work / ("junit_%s.xml" % arm)) for arm, (py, src) in arms.items()}
        coll, cls = classify(res["pre"]["results"], res["gold"]["results"])
        report["collection_errors"] = {t: {"pre": t in res["pre"]["results"], "gold": t in res["gold"]["results"]} for t in sorted(coll)}
        report.update(classification=cls, summary={k: sum(v == k for v in cls.values()) for k in sorted(set(cls.values()))},
                      eligible_oracle=[t for t, c in cls.items() if c == "F->P"],
                      arms={k: {"exit": v["exit"], "tail": v["tail"]} for k, v in res.items()},
                      provisioning={"pre": logs["pre"], "gold": logs["gold"], "repairs": repairs})
        report["eligible_sources"] = V._test_sources(work / "gold", report["eligible_oracle"])
        dump = {}
        for f in test_files:
            p = work / "gold" / f
            for cand in [p] + [q / "conftest.py" for q in p.parents if work / "gold" in q.parents or q == work / "gold"]:
                if cand.exists():
                    dump[str(cand.relative_to(work / "gold"))] = cand.read_text(encoding="utf-8", errors="replace")[:60000]
        report["test_file_sources"] = dump
        report["verdict"] = "ELIGIBLE" if report["eligible_oracle"] else "NOT_ELIGIBLE (no fail-before/pass-after test)"
    except Exception as exc:
        report["verdict"] = ("VETTING_ERROR: %s: %s" % (type(exc).__name__, exc))[:500]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / ("VETTING_%s.json" % spec["name"])).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report.get(k) for k in ("name", "summary", "verdict")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
