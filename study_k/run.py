"""Reproduce the retrospective python-control transfer with zero model calls.

Preserves the complete 16-test upstream module, including the failing witness.
No test is deselected. New directories are required so failed attempts survive.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from study_i.run import digest, run_command, write_json, xml_cases


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    require(not out.exists() or not any(out.iterdir()), "Choose a new output directory")
    out.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((HERE / "target.json").read_text())
    require(list(sys.version_info[:3]) == cfg["python"], "Wrong Python version")
    for name, version in cfg["runtime_versions"].items():
        require(importlib.metadata.version(name) == version, "Wrong runtime package: " + name)
    for rel, sha in cfg["gatekeeper_sha256"].items():
        require(digest(ROOT / rel) == sha, "Frozen engine/skill changed: " + rel)
    for rel, sha in cfg["vendor_sha256"].items():
        require(digest(HERE / rel) == sha, "Vendor evidence changed: " + rel)
    os.environ.update(MPLBACKEND="Agg", OPENBLAS_NUM_THREADS="1",
                      PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1")
    source = args.checkout.resolve() if args.checkout else out / "work/upstream"
    if not args.checkout:
        source.mkdir(parents=True)
        cmds = [["git", "init", "-q"], ["git", "fetch", "--depth=1",
                "https://github.com/" + cfg["repository"] + ".git", cfg["revision"]],
                ["git", "checkout", "--detach", "FETCH_HEAD"]]
        for i, cmd in enumerate(cmds):
            row = run_command(cmd, source, out / ("fetch_%s.log" % i), timeout=300)
            require(row["returncode"] == 0, "Checkout failed")
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    require(revision == cfg["revision"], "Wrong source revision")
    require(not subprocess.check_output(["git", "diff", "HEAD"], cwd=source, text=True).strip(),
            "Tracked upstream files were modified")
    for rel, sha in cfg["source_sha256"].items():
        require(digest(source / rel) == sha, "Wrong source/test bytes: " + rel)
    from gatekeeper_ext.none_identity import register
    from gatekeeper_lite.gatekeeper import bind_modules, replay, screen
    from gatekeeper_lite.skill import Skill, Target
    register()
    skill = Skill.load(ROOT / "study_g/skills/none-identity.json")
    target = Target(cfg["target_id"], source, {"modules": [cfg["module"]],
                    "python": "3.8.20", "platform": "linux", "packages": {}, "pythonpath": []})
    bound = bind_modules([skill], target)
    require(len(bound["sites"]) == cfg["site_count"], "Binding count changed")
    require(replay(skill)["passed"] and screen(skill, target).in_scope, "Source replay/screen failed")
    gold = (HERE / "vendor/control_freqplot_gold.py").read_text()
    treated = bound["treated"][cfg["module"]]
    require(ast.dump(ast.parse(gold)) == ast.dump(ast.parse(treated)), "Skill differs from upstream fix")
    arms = {}
    for arm in ["baseline", "treated", "gold"]:
        path = out / "work" / arm
        shutil.copytree(source, path, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache"))
        if arm != "baseline":
            (path / cfg["module"]).write_text(treated if arm == "treated" else gold)
        require(digest(path / cfg["test_module"]) == cfg["source_sha256"][cfg["test_module"]],
                "Upstream test was edited")
        arms[arm] = path
    patch = "".join(difflib.unified_diff((source / cfg["module"]).read_text().splitlines(True),
                   treated.splitlines(True), fromfile="a/"+cfg["module"], tofile="b/"+cfg["module"]))
    (out / "skill.patch").write_text(patch)
    code = {str(p.relative_to(ROOT)): digest(p) for p in
            [HERE / "run.py", HERE / "oracles/control_frequency.py", ROOT / "study_i/run.py"]}
    record = {"status": "RUNNING", "not_preregistered": True, "config": cfg,
              "config_sha256": digest(HERE / "target.json"), "code_sha256": code,
              "source_revision": revision, "source_test_sha256": cfg["source_sha256"],
              "started_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
              "environment": sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions()),
              "bindings": bound["sites"], "gold_ast_equal": True, "source_replay": replay(skill),
              "llm_calls": 0, "model_cost_usd": 0, "runs": []}
    write_json(out / "PRE_EXECUTION.json", record)
    states = {}
    for arm, path in arms.items():
        repetitions = []
        env = dict(os.environ, PYTHONPATH=str(path), PYTHONHASHSEED="0")
        for rep in range(1, cfg["repetitions"]+1):
            label = "%s_%s" % (arm, rep)
            xml = out / (label + ".xml")
            cmd = [sys.executable, "-m", "pytest", cfg["test_module"], "-q", "--tb=short",
                   "-o", "addopts=", "-p", "no:cacheprovider", "--junitxml="+str(xml)]
            row = run_command(cmd, path, out / (label + ".log"), env=env)
            require(row["returncode"] in (0, 1) and xml.exists(), "Collection/environment failure")
            cases = xml_cases(xml)
            require(len(cases) == cfg["n_tests"], "Test inventory changed")
            require(all(v["status"] in ("passed", "failure") for v in cases.values()),
                    "Setup/collection errors or skips invalidate the complete-module claim")
            if arm == "baseline":
                failures = [k for k,v in cases.items() if v["status"] == "failure"]
                require(len(failures) == 1 and failures[0].endswith("TestFRD::testNyquist"),
                        "Unexpected baseline failures; do not drop them")
                detail = cases[failures[0]]["detail"] + cases[failures[0]]["message"]
                require("truth value of an array" in detail and "nyquist_plot" in detail,
                        "Witness is not the target functional ValueError")
            labels = {k:v["status"] for k,v in cases.items()}
            repetitions.append(labels)
            row.update(arm=arm, repetition=rep, xml=xml.name, case_status=labels,
                       counts={s: sum(v == s for v in labels.values()) for s in ("passed", "failure")})
            record["runs"].append(row)
            write_json(out / "execution_progress.json", record)
        require(all(x == repetitions[0] for x in repetitions), "Unstable upstream outcomes")
        states[arm] = repetitions[0]
    require(set(states["baseline"]) == set(states["treated"]) == set(states["gold"]), "Test inventory mismatch")
    require(states["gold"] == states["treated"], "Gold/skill outcomes differ")
    regressions = [k for k,v in states["baseline"].items() if v == "passed" and states["treated"][k] != "passed"]
    resolved = [k for k,v in states["baseline"].items() if v == "failure" and states["treated"][k] == "passed"]
    require(not regressions and len(resolved) == 1, "Beneficial transfer did not reproduce")
    record.update(census_regressions=regressions, resolved_upstream_tests=resolved,
                  baseline_passing_census=15, selected_module_only=True)
    from gatekeeper_lite import drawharness
    original_load = drawharness._load
    oracle_path = HERE / "oracles/control_frequency.py"
    def logged_load(path):
        module = original_load(path)
        original_judge = module.judge
        count = {s:0 for s in module.scopes()}
        def judge(scope, d, ow, ot):
            pw, pt = map(bool, original_judge(scope, d, ow, ot))
            count[scope] += 1
            with (out / "draws.jsonl").open("a") as log:
                log.write(json.dumps({"scope":scope, "n":count[scope], "draw":d, "without":ow, "with":ot,
                                     "passed_without":pw, "passed_with":pt, "z":int(not pt)-int(not pw)}, allow_nan=False)+"\n")
            if count[scope] % 100 == 0:
                print("DRAW_PROGRESS", scope, count[scope], flush=True)
            return pw, pt
        module.judge = judge
        return module
    drawharness._load = logged_load
    try:
        record["diagnostic_draws"] = drawharness.run_draw_study(target, bound["treated"], oracle_path,
                                      cfg["diagnostic_draws"], k_cells=len(cfg["diagnostic_draws"]["cells"]))
    finally:
        drawharness._load = original_load
    require(not any(s["b8"]["counts"]["harness_error"] for s in record["diagnostic_draws"]["scopes"].values()),
            "Draw harness failure")
    # Fresh workers plus a different order test finite sample state sensitivity.
    oracle = original_load(oracle_path)
    observations = [json.loads(x) for x in (out / "draws.jsonl").read_text().splitlines()]
    summary = {}
    with (out / "statelessness.jsonl").open("w") as log:
        for scope in oracle.scopes():
            selected = [r for r in observations if r["scope"] == scope][:100]
            random.Random("study-k-shuffle:" + scope).shuffle(selected)
            mismatches = 0
            for offset in range(0, 100, 25):
                workers = {}
                try:
                    for arm in ["baseline", "treated"]:
                        workers[arm] = drawharness._Worker(arms[arm], [], oracle_path, cfg["diagnostic_draws"]["seed"])
                    for row in selected[offset:offset+25]:
                        ow, ot = workers["baseline"].run(row["draw"]), workers["treated"].run(row["draw"])
                        clean = lambda x: {k:v for k,v in x.items() if k != "module"}
                        mismatch = clean(ow) != clean(row["without"]) or clean(ot) != clean(row["with"])
                        mismatches += int(mismatch)
                        log.write(json.dumps({"scope":scope, "n":row["n"], "without":ow, "with":ot,
                                              "mismatch":mismatch}, allow_nan=False)+"\n")
                        log.flush()
                finally:
                    for worker in workers.values():
                        worker.close()
            summary[scope] = {"compared":100, "mismatches":mismatches}
            print("STATELESSNESS", scope, summary[scope], flush=True)
    require(not any(x["mismatches"] for x in summary.values()), "State/order mismatch")
    record.update(status="VERIFIED_EXPLORATORY", statelessness=summary,
                  finished_utc=datetime.now(timezone.utc).isoformat())
    write_json(out / "RESULT.json", record)
    from study_k.verify import audit
    audit(out, out / "VERIFIED.json", out / "RESULT.md")


if __name__ == "__main__":
    main()
