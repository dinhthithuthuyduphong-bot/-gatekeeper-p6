"""Study T-A2: LLM-judge baseline (LJ).  For every census cell of one shard of packages, the diff of the cell's change is shown to
a model that answers safe/unsafe.  It sees no trial outcome.

python tools/market_judge.py WORK_DIR OUT_DIR MODELS.json --shard I --shards K [--model vertex-gemini-flash] [--cap 0.75]
"""
import difflib
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import market_census as MC  # noqa: E402
import market_trials as MT  # noqa: E402
from gatekeeper_lite import b9  # noqa: E402
from library_census import load_skills  # noqa: E402

PROMPT = ("You review an automated code change (a lint autofix or refactoring). Will applying it change the observable behaviour "
          "of the program for any caller (return values, raised exceptions, side effects)? Reply with JSON only: "
          '{"verdict": "safe" | "unsafe", "reason": "<one sentence>"}.')
MAX_DIFF = 2000


def parse(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    try:
        d = json.loads(m.group(0)) if m else {}
    except ValueError:
        d = {}
    v = d.get("verdict")
    return (v if v in ("safe", "unsafe") else "unsafe"), str(d.get("reason", ""))[:200], v in ("safe", "unsafe")


def cell_diff(root, rule, files, skills, work):
    snap = work / "judge_snap"
    if snap.exists():
        shutil.rmtree(snap)
    shutil.copytree(root, snap, symlinks=True)
    MT.apply_skill(rule, snap, files, skills)
    out = []
    for f in files:
        a = (root / f).read_text(encoding="utf-8").splitlines(keepends=True)
        b = (snap / f).read_text(encoding="utf-8").splitlines(keepends=True)
        out.extend(difflib.unified_diff(a, b, "a/" + f, "b/" + f))
    shutil.rmtree(snap, ignore_errors=True)
    return "".join(out)


def judge_package(pkg, census_pkg, work, client, cfg, guard, skills):
    meta = json.loads(MC.fetch("https://pypi.org/pypi/%s/%s/json" % (pkg["project"], pkg["version"])))
    sd = next(f for f in meta["urls"] if f["filename"] == pkg["sdist"])
    root = MT.extract_all(MC.fetch(sd["url"], 300), sd["filename"], work / "src")
    out = {}
    for rule, cell in sorted(census_pkg["cells"].items()):
        files = sorted({MT.strip_top(x.split("::", 1)[0]) for x in cell["functions"]})
        diff = cell_diff(root, rule, files, skills, work)
        user = "Change: %s\n\n```diff\n%s\n```" % (rule, diff[:MAX_DIFF])
        msgs = [{"role": "system", "content": PROMPT}, {"role": "user", "content": user}]
        try:
            guard.check(msgs, 300, cfg["prices_usd_per_mtok"])
        except b9.BudgetExceeded:
            out[rule] = {"judged": False, "why": "budget cap reached"}
            continue
        r = client.complete(cfg["model_id"], msgs, 300, 0.0, 1)
        guard.add(r["usage"], cfg["prices_usd_per_mtok"])
        verdict, reason, parsed = parse(r["text"])
        out[rule] = {"judged": True, "verdict": verdict, "reason": reason, "parsed": parsed, "diff_chars": len(diff)}
    shutil.rmtree(work, ignore_errors=True)
    return out


def main(argv):
    work, out, models = Path(argv[0]), Path(argv[1]), argv[2]
    opt = lambda key, d: type(d)(argv[argv.index(key) + 1]) if key in argv else d   # noqa: E731
    shard, shards = opt("--shard", 0), opt("--shards", 1)
    name, cap = opt("--model", "vertex-gemini-flash"), opt("--cap", 0.75)
    from cohort_inner import RefreshingClient
    cfg = next(m for m in json.loads(Path(models).read_text())["models"] if m["name"] == name)
    client = RefreshingClient(cfg["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", "")), cfg["key_env"], cfg.get("extra", {}))
    guard = b9.SpendGuard(cap)
    targets = json.loads((MT.RES / "TARGETS.json").read_text())["selected"]
    census = {p["project"]: p for p in json.loads((MT.RES / "MARKET_CENSUS.json").read_text())["packages"]}
    skills = load_skills()
    res = {}
    for pkg in targets[shard::shards]:
        try:
            res[pkg["project"]] = judge_package(pkg, census[pkg["project"]], work / pkg["project"], client, cfg, guard, skills)
        except Exception as exc:  # noqa: BLE001 - recorded
            res[pkg["project"]] = {"error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    out.mkdir(parents=True, exist_ok=True)
    (out / ("JUDGE_%02d.json" % shard)).write_text(json.dumps({"model": cfg["model_id"], "spent_usd": guard.spent_usd, "packages": res}))
    print(json.dumps({"shard": shard, "spent_usd": round(guard.spent_usd, 4)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
