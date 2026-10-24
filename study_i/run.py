"""Reproduce the exploratory skill-2 extension without any model/API calls.

Run under the target's pinned Python environment. Never modifies source checkouts.
An output directory must be new/empty, so failed and successful runs stay visible.
"""
from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False), encoding="utf-8")


def run_command(cmd, cwd, log, timeout=300, env=None):
    start = time.perf_counter()
    print("RUN", json.dumps(cmd), "CWD", str(cwd), flush=True)
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                           errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or b""
        log.write_bytes(partial if isinstance(partial, bytes) else partial.encode())
        raise
    log.write_text(p.stdout + p.stderr, encoding="utf-8")
    print(p.stdout + p.stderr, end="", flush=True)
    row = {"command": cmd, "cwd": str(cwd), "returncode": p.returncode,
           "seconds": time.perf_counter() - start, "log": log.name}
    print("MEASURE", json.dumps(row), flush=True)
    return row


def xml_cases(path):
    out = {}
    for c in ET.parse(path).getroot().iter("testcase"):
        key = c.attrib.get("classname", "") + "::" + c.attrib["name"]
        if key in out:
            raise ValueError("Duplicate test identity: " + key)
        tag = next((t for t in ("failure", "error", "skipped") if c.find(t) is not None), "passed")
        node = c.find(tag) if tag != "passed" else None
        out[key] = {"status": tag, "message": node.attrib.get("message", "") if node is not None else "",
                    "detail": (node.text or "") if node is not None else ""}
    if not out:
        raise ValueError("No test cases in " + str(path))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=["sqlalchemy", "networkx"])
    parser.add_argument("--checkout", type=Path, help="Optional clean upstream checkout at the exact pin")
    parser.add_argument("--gatekeeper", type=Path, default=HERE.parent)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args()
    if args.repetitions < 3:
        parser.error("At least three fresh-process repetitions are required")
    out, gk = args.output.resolve(), args.gatekeeper.resolve()
    if out.exists() and any(out.iterdir()):
        parser.error("Output is not empty; choose a new directory to preserve all logs")
    out.mkdir(parents=True, exist_ok=True)
    config = json.loads((HERE / "targets.json").read_text())
    cfg = config["targets"][args.target]
    if list(sys.version_info[:2]) != cfg["python"]:
        raise RuntimeError("Wrong Python minor version: " + sys.version)
    for rel, expected in config["gatekeeper_sha256"].items():
        if digest(gk / rel) != expected:
            raise RuntimeError("Frozen core/skill hash mismatch: " + rel)
    for rel, expected in config["vendor_sha256"].items():
        if digest(HERE / rel) != expected:
            raise RuntimeError("Upstream oracle hash mismatch: " + rel)
    sys.path.insert(0, str(gk))
    from gatekeeper_ext.none_identity import register
    from gatekeeper_lite.gatekeeper import bind_modules, replay, screen
    from gatekeeper_lite.skill import Skill, Target
    register()

    source = args.checkout.resolve() if args.checkout else out / "work/upstream"
    if not args.checkout:
        source.mkdir(parents=True)
        for i, cmd in enumerate((["git", "init", "-q"],
                                 ["git", "fetch", "--depth=1", "https://github.com/"+cfg["repository"]+".git", cfg["revision"]],
                                 ["git", "checkout", "--detach", "FETCH_HEAD"])):
            row = run_command(cmd, source, out / ("fetch_%s.log" % i), timeout=600)
            if row["returncode"]:
                raise RuntimeError("Checkout failed")
    actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if actual != cfg["revision"]:
        raise RuntimeError("Wrong upstream revision: " + actual)
    if subprocess.check_output(["git", "-C", str(source), "diff", "HEAD"], text=True).strip():
        raise RuntimeError("Upstream tracked files are modified")
    # Verify the explicit file selection before looking at outcomes.
    hashes = {p: digest(source / p) for p in cfg["modules"] + cfg["census"]}
    skill = Skill.load(gk / "study_g/skills/none-identity.json")
    target = Target(cfg["target_id"], source, {"modules": cfg["modules"],
                    "python": ".".join(map(str, cfg["python"])), "platform": "linux",
                    "packages": {}, "pythonpath": cfg["pythonpath"]})
    bound = bind_modules([skill], target)
    if len(bound["sites"]) != cfg["site_count"]:
        raise RuntimeError("Unexpected binding sites")
    if not replay(skill)["passed"] or not screen(skill, target).in_scope:
        raise RuntimeError("Source replay or declared environment screen failed")
    arms = {}
    for arm in ["baseline", "treated"] + (["gold"] if cfg.get("gold") else []):
        path = out / "work" / arm
        shutil.copytree(source, path, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".pytest_cache"))
        if arm == "treated":
            for rel, content in bound["treated"].items():
                (path / rel).write_text(content, encoding="utf-8")
        if arm == "gold":
            for rel, vendor in cfg["gold"].items():
                gold_source = (HERE / vendor).read_text()
                if ast.dump(ast.parse(gold_source)) != ast.dump(ast.parse(bound["treated"][rel])):
                    raise RuntimeError("Skill output differs from the upstream gold fix")
                (path / rel).write_text(gold_source, encoding="utf-8")
        for rel in cfg["census"]:
            if digest(path / rel) != hashes[rel]:
                raise RuntimeError("A census test was altered")
        arms[arm] = path
    patch = "".join("".join(difflib.unified_diff((source / rel).read_text().splitlines(True),
                     content.splitlines(True), fromfile="a/"+rel, tofile="b/"+rel))
                    for rel, content in bound["treated"].items())
    (out / "skill.patch").write_text(patch)
    record = {"status": "RUNNING_EXPLORATORY", "target": cfg["target_id"],
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "upstream_revision": actual, "gatekeeper_commit": config["gatekeeper_commit"],
              "target_config": cfg, "config_sha256": digest(HERE / "targets.json"),
              "study_code_sha256": {str(p.relative_to(HERE)): digest(p) for p in HERE.rglob("*.py")
                                     if "results" not in p.parts},
              "source_and_test_sha256": hashes, "bindings": bound["sites"],
              "source_replay": replay(skill), "python": sys.version,
              "environment": sorted((d.metadata["Name"], d.version) for d in importlib.metadata.distributions()),
              "llm_calls": 0, "model_cost_usd": 0, "runs": []}
    write_json(out / "PRE_EXECUTION.json", record)
    states = {}
    groups = {"census": cfg["census"]}
    if cfg.get("witness"):
        groups["witness"] = [str(HERE / cfg["witness"]["path"]) + cfg["witness"]["selector"]]
    for arm, path in arms.items():
        states[arm] = {}
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0",
                   PYTHONPATH=os.pathsep.join([str(path / p) for p in cfg["pythonpath"]] + [str(path)]))
        for group, tests in groups.items():
            repetitions = []
            for rep in range(1, args.repetitions + 1):
                name = "%s_%s_%s" % (arm, group, rep)
                xml = out / (name + ".xml")
                if cfg["test_runner"] == "pytest":
                    cmd = [sys.executable, "-m", "pytest", "-q", "-o", "addopts=", "-p", "no:cacheprovider",
                           "--junitxml="+str(xml), *tests]
                else:
                    cmd = [sys.executable, "-m", "nose", *tests, "--with-xunit", "--xunit-file="+str(xml), "-v"]
                run = run_command(cmd, path, out / (name + ".log"), env=env)
                if run["returncode"] not in (0, 1) or not xml.exists():
                    raise RuntimeError("Environment/collection failure, see " + run["log"])
                cases = xml_cases(xml)
                if any(v["status"] == "error" for v in cases.values()):
                    # Nose calls an uncaught exception in a test body an 'error'.
                    # Only this documented target-call ValueError is functional.
                    allowed = (args.target == "networkx" and group == "witness" and arm == "baseline"
                               and len(cases) == 1 and all(
                                   "ValueError" in (v["detail"]+v["message"])
                                   and "truth value of an array" in (v["detail"]+v["message"])
                                   and "_fruchterman_reingold" in v["detail"] for v in cases.values()))
                    if not allowed:
                        raise RuntimeError("Unclassified test error; never count it as benefit")
                labels = {k: v["status"] for k,v in cases.items()}
                repetitions.append(labels)
                run.update(arm=arm, group=group, repetition=rep, xml=xml.name,
                           counts={s: sum(v == s for v in labels.values()) for s in ("passed", "failure", "error", "skipped")},
                           case_status=labels)
                record["runs"].append(run)
                write_json(out / "execution_progress.json", record)
            if any(x != repetitions[0] for x in repetitions):
                raise RuntimeError("Unstable test outcomes: " + arm + "/" + group)
            states[arm][group] = repetitions[0]
    b, t = states["baseline"]["census"], states["treated"]["census"]
    if set(b) != set(t) or sum(v == "passed" for v in b.values()) < 5:
        raise RuntimeError("Census inventory mismatch or insufficient passing tests")
    if any(v in ("failure", "error") for v in b.values()):
        raise RuntimeError("Baseline census is not clean")
    regressions = sorted(k for k in b if b[k] == "passed" and t[k] in ("failure", "error"))
    resolved = []
    if "witness" in groups:
        wb, wt = states["baseline"]["witness"], states["treated"]["witness"]
        if set(wb) != set(wt) or states["gold"] != states["treated"]:
            raise RuntimeError("Witness inventory/gold mismatch")
        resolved = sorted(k for k in wb if wb[k] in ("failure", "error") and wt[k] == "passed")
    if cfg["direction"] == "harmful" and not regressions:
        raise RuntimeError("Harmful result was not reproduced")
    if cfg["direction"] == "beneficial" and (regressions or not resolved):
        raise RuntimeError("Beneficial result was not reproduced")
    record.update(status="UPSTREAM_VERIFIED_DRAW_PENDING", census_regressions=regressions,
                  resolved_upstream_witnesses=resolved,
                  all_statuses_stable=True, selected_census_not_whole_repository=True)
    write_json(out / "RESULT.json", record)
    # Reuse the unchanged engine; the coordinator wrapper only persists observations.
    from gatekeeper_lite import drawharness
    original_load = drawharness._load
    log_path = out / "draws.jsonl"
    def logged_load(path):
        module = original_load(path)
        original_judge = module.judge
        counter = {scope: 0 for scope in module.scopes()}
        def logged_judge(scope, d, ow, ot):
            pw, pt = original_judge(scope, d, ow, ot)
            counter[scope] += 1
            with log_path.open("a", encoding="utf-8") as log:
                log.write(json.dumps({"scope":scope, "n":counter[scope], "draw":d,
                          "without":ow, "with":ot, "passed_without":bool(pw), "passed_with":bool(pt),
                          "z":int(not pt)-int(not pw)}, allow_nan=False)+"\n")
            if counter[scope] % 100 == 0:
                print("DRAW_PROGRESS", cfg["target_id"], scope, counter[scope], flush=True)
            return pw, pt
        module.judge = logged_judge
        return module
    drawharness._load = logged_load
    try:
        draw_cfg = config["diagnostic_draws"]
        draw = drawharness.run_draw_study(target, bound["treated"], HERE / cfg["draw_oracle"],
                                        draw_cfg, k_cells=len(draw_cfg["cells"]))
    finally:
        drawharness._load = original_load
    if any(s["b8"]["counts"]["harness_error"] for s in draw["scopes"].values()):
        write_json(out / "INVALID_DRAW_RESULT.json", draw)
        raise RuntimeError("Draw harness failure; no admission may be reported")
    record["diagnostic_draws"] = draw
    record["status"] = "VERIFIED_EXPLORATORY"
    record["diagnostic_only_not_preregistered"] = True
    record["finished_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(out / "RESULT.json", record)
    lines = ["# " + cfg["target_id"] + " — exploratory reproduction", "",
             "Status: **VERIFIED_EXPLORATORY**. Model calls: **0**. B9 remains HOLD.", "",
             "This is selected-module census plus retrospective/diagnostic evidence, not a new pre-registered confirmatory study.", "",
             "Upstream: `"+actual+"`; Python: `"+sys.version.split()[0]+"`.", "",
             "| Arm / group | Passed | Failure | Error | Skip | Repetitions |", "|---|---:|---:|---:|---:|---:|"]
    for arm in states:
        for group in states[arm]:
            c = next(r["counts"] for r in record["runs"] if r["arm"]==arm and r["group"]==group)
            lines.append("| %s / %s | %s | %s | %s | %s | %s |" % (arm,group,c["passed"],c["failure"],c["error"],c["skipped"],args.repetitions))
    lines += ["", "Persistent census regressions: **%d**. Resolved upstream witnesses: **%d**." % (len(regressions),len(resolved)),
              "", "A Nose witness 'error' is a target-call ValueError, not an import/setup failure; its full traceback is retained.",
              "", "| Scope | Raw sequential decision | Draws to stop | Full help / tie / hurt |", "|---|---|---:|---|"]
    for scope,s in draw["scopes"].items():
        c=s["b8"]["counts"]
        lines.append("| %s | %s | %d | %d / %d / %d |" % (scope,s["decision"],s["draws"],c["help"],c["tie"],c["hurt"]))
    lines += ["", "Any census regression vetoes admission for the whole target. See aggregate output for the four-cell family.",
              "", "Raw evidence: RESULT.json, PRE_EXECUTION.json, every .log/.xml, skill.patch, and draws.jsonl.",
              "Draw adapters are researcher-authored. The separate upstream witness/census tests are unchanged."]
    (out / "RESULT.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("VERIFIED", cfg["target_id"], "regressions",len(regressions),"resolved",len(resolved),flush=True)


if __name__ == "__main__":
    main()
