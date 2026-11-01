"""Re-run, in GitHub Actions, the checks that were earlier run only locally (logs/local_runs/HISTORY_BEFORE_LOGGING.md), so that
each has an Actions log as evidence.  Every task prints PASS or FAIL with its numbers; the exit code is non-zero if any fails.

python tools/evidence_local_tasks.py [TASK ...]    tasks: r2-preflight s-smoke r2-dynamic u-recompute report-recompute
"""
import json
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
RESULTS = []


def report(task, ok, detail):
    RESULTS.append({"task": task, "ok": bool(ok), "detail": detail})
    print("%s  %-16s %s" % ("PASS" if ok else "FAIL", task, detail), flush=True)


def r2_preflight():
    """The 12 families must run without crashing on non-target code: requests and flask at fixed tags, plus the standard library."""
    import library_census as L
    from gatekeeper_lite import transforms as T
    sk = L.load_skills()
    work = Path(tempfile.mkdtemp())
    crashes, sites = 0, {}
    for repo, tag in (("psf/requests", "v2.32.3"), ("pallets/flask", "3.0.3")):
        d = work / repo.split("/")[1]
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", tag, "https://github.com/%s" % repo, str(d)], check=True)
        funcs, pairs, scanned, skipped = L.scan(d, sk)
        sites[repo] = {k: len(v) for k, v in funcs.items() if v}
    std = Path(sysconfig.get_paths()["stdlib"])
    files = [p for p in sorted(std.glob("*.py"))][:120]
    for p in files:
        try:
            src = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for s in sk.values():
            try:
                s.transform().apply(src, single_site=False)
            except T.Abstain:
                pass
            except Exception:  # noqa: BLE001 - any other exception is a crash of the family
                crashes += 1
    shutil.rmtree(work, ignore_errors=True)
    report("r2-preflight", crashes == 0, "crashes on %d stdlib files: %d; sites on requests/flask: %s" % (len(files), crashes, sites))


def s_smoke():
    """Study S harness on a synthetic package: the order dependence predicted by R2 must appear with S-A2 settings."""
    import composition_study as S
    root = Path(tempfile.mkdtemp()) / "pkg_root"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg/__init__.py").write_text("")
    (root / "pkg/m.py").write_text("from dataclasses import dataclass\n\n\n@dataclass\nclass L:\n    gen: int\n\n"
                                   "    def __post_init__(self):\n        if type(self.gen) is not int:\n            raise ValueError('bad')\n")
    S.S_A1 = S.S_A2 = True
    sk = S.load_skills()
    work = Path(tempfile.mkdtemp())
    py = Path(sys.executable)
    src = (root / "pkg/m.py").read_text()
    q, a, b = "L.__post_init__", "negative_type_guard", "type_eq_isinstance"
    calls = work / "c.json"
    S.inner(py, root, [], "pkg/m.py", q, "generate", calls, work / "g.json", 80)
    o1 = S.inner(py, root, [], "pkg/m.py", q, "run", calls, work / "o1.json", 80)
    o2 = S.inner(py, root, [], "pkg/m.py", q, "run", calls, work / "o2.json", 80)
    runs = {}
    for v in S.VARIANTS:
        snap = work / ("snap_" + v)
        shutil.copytree(root, snap)
        (snap / "pkg/m.py").write_text(S.variant_source(sk, a, b, src, v))
        runs[v] = S.inner(py, snap, [], "pkg/m.py", q, "run", calls, work / (v + ".json"), 80)
    st, L = S.losses(o1, o2, runs)
    it = S.interaction(L, runs, st)
    report("s-smoke", it["order_dependent"] > 0 and sum(L["A"]) == 0, "stable %d, changes %s, interaction %s" % (
        len(st), {v: sum(x) for v, x in L.items()}, it))


def r2_dynamic():
    """`library_census --dynamic` on the committed census must reproduce the committed enabling-edge analysis."""
    import library_census as L
    committed = json.loads((ROOT / "research_closure/results/study_r2/LIBRARY_CENSUS.json").read_text())
    again = L.dynamic(committed)
    same = again == committed["with_enabling_edges"]
    report("r2-dynamic", same, "missed_by_static %s; composite cells %d" % (again["total"]["missed_by_static"],
                                                                            again["total"]["composite_cells_required"]))


def u_recompute():
    """Study U (incl. U-A1) recomputed from the Study Q records must equal the committed result."""
    import rare_harm_study as U
    committed = json.loads((ROOT / "research_closure/results/study_u/STUDY_U_RESULT.json").read_text())
    again = {k: U.study(k) for k in ("contract", "naive")}
    same = json.loads(json.dumps(again)) == committed
    c = again["contract"]["scores"]
    report("u-recompute", same, "G %s, G_FDR %s, S20 %s, B8 %s" % (c["G"], c["G_FDR"], c["S20"], c["B8"]))


def report_recompute():
    """docs/paper/RESULTS_REPORT.md regenerated from the committed result files must equal the committed report."""
    out = Path(tempfile.mkdtemp()) / "R.md"
    subprocess.run([sys.executable, str(ROOT / "tools/results_report.py"), str(out)], check=True, capture_output=True)
    same = out.read_text() == (ROOT / "docs/paper/RESULTS_REPORT.md").read_text()
    report("report-recompute", same, "regenerated report %s the committed one" % ("equals" if same else "DIFFERS FROM"))


TASKS = {"r2-preflight": r2_preflight, "s-smoke": s_smoke, "r2-dynamic": r2_dynamic, "u-recompute": u_recompute,
         "report-recompute": report_recompute}


def main(argv):
    for name in (argv or list(TASKS)):
        try:
            TASKS[name]()
        except Exception as exc:  # noqa: BLE001 - a task that crashes fails, with the reason
            report(name, False, "crashed: %s: %s" % (type(exc).__name__, str(exc)[:200]))
    Path("evidence_out").mkdir(exist_ok=True)
    Path("evidence_out/EVIDENCE.json").write_text(json.dumps(RESULTS, indent=1))
    return 0 if all(r["ok"] for r in RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
