"""Exploratory census-first policy cost on the known Study I targets.

All policies pay the same selected census; a regression veto stops evaluation
before any draw worker. This is a cost comparison, not a new population study.
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import random
import shutil
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from next_evidence.common import checkout, digest, execute, new_output, verify_source, write_json, xml_cases


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("target",choices=["sqlalchemy","networkx"])
    p.add_argument("--out",type=Path,required=True);args=p.parse_args();out=new_output(args.out)
    follow=json.loads((ROOT/"next_evidence/config.json").read_text());settings=follow["cost"]
    if (follow["model_calls_allowed"] or settings["b9_allowed"] or not settings["early_census_veto"]
            or follow["repetitions"]!=3 or settings["modes"]!=["census_only","census_then_gate","census_then_full"]):
        raise ValueError("Unsupported policy protocol; do not silently change the comparison")
    cfg=json.loads((ROOT/"study_i/targets.json").read_text());target_cfg=cfg["targets"][args.target]
    if list(sys.version_info[:2])!=target_cfg["python"]:raise ValueError("Wrong Python minor version")
    for rel,expected in cfg["gatekeeper_sha256"].items():
        if digest(ROOT/rel)!=expected:raise ValueError("Frozen engine/skill changed")
    known=json.loads((ROOT/"study_i/results/ci-40084717332/inputs"/args.target/"RESULT.json").read_text())
    src=checkout(target_cfg["repository"],target_cfg["revision"],out/"work/source",out)
    verify_source(src,target_cfg["revision"],known["source_and_test_sha256"])
    from gatekeeper_ext.none_identity import register
    from gatekeeper_lite.gatekeeper import bind_modules, replay
    from gatekeeper_lite.skill import Skill, Target
    from gatekeeper_lite import drawharness
    register();skill=Skill.load(ROOT/"study_g/skills/none-identity.json")
    if not replay(skill)["passed"]:raise ValueError("Source skill replay failed")
    # Latin-square order: each policy occurs once at each order position.
    modes=list(settings["modes"]);random.Random(settings["schedule_seed"]).shuffle(modes)
    schedule=[(rep,modes[(position+rep)%len(modes)]) for rep in range(3) for position in range(len(modes))]
    record={"status":"RUNNING","kind":settings["label"],"model_calls":0,"api_cost_usd":0,"B9":"HOLD",
            "target":args.target,"source_revision":target_cfg["revision"],"schedule":schedule,
            "code_sha256":digest(Path(__file__)),"config_sha256":digest(ROOT/"next_evidence/config.json"),
            "source_sha256":known["source_and_test_sha256"],"python":sys.version,
            "environment":sorted((d.metadata["Name"],d.version) for d in importlib.metadata.distributions()),
            "excluded_costs":["source download","dependency installation"],"measurements":[]}
    write_json(out/"PRE_EXECUTION.json",record)
    for rep,mode in schedule:
        directory=out/("%s_%s"%(rep,mode));directory.mkdir();start=time.perf_counter()
        target=Target(target_cfg["target_id"],src,{"modules":target_cfg["modules"],"pythonpath":target_cfg["pythonpath"]})
        bound=bind_modules([skill],target)
        if len(bound["sites"])!=target_cfg["site_count"]:raise ValueError("Binding changed")
        states={};runs=[]
        for arm in ("baseline","treated"):
            snap=directory/"work"/arm
            shutil.copytree(src,snap,ignore=shutil.ignore_patterns(".git","__pycache__","*.pyc",".pytest_cache"))
            if arm=="treated":
                for rel,text in bound["treated"].items():(snap/rel).write_text(text)
            for rel in target_cfg["census"]:
                if digest(snap/rel)!=known["source_and_test_sha256"][rel]:raise ValueError("Upstream census test changed")
            xml=directory/(arm+".xml")
            if target_cfg["test_runner"]=="pytest":
                command=[sys.executable,"-m","pytest","-q","-o","addopts=","-p","no:cacheprovider","--junitxml="+str(xml),*target_cfg["census"]]
            else:
                command=[sys.executable,"-m","nose","--with-xunit","--xunit-file="+str(xml),*target_cfg["census"]]
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",PYTHONHASHSEED="0",
                     PYTHONPATH=os.pathsep.join([str(snap/v) for v in target_cfg["pythonpath"]]+[str(snap)]))
            run=execute(command,snap,directory/(arm+".log"),env=env,timeout=600)
            if run["returncode"] not in (0,1) or not xml.exists():raise RuntimeError("Census environment/collection failure")
            states[arm]=xml_cases(xml)
            if "error" in states[arm].values():raise RuntimeError("Census setup/teardown failure")
            if (run["returncode"]==1)!=("failure" in states[arm].values()):
                raise RuntimeError("Census exit code and JUnit failures disagree")
            run.update(arm=arm,xml=xml.name,xml_sha256=digest(xml),case_status=states[arm]);runs.append(run)
        if set(states["baseline"])!=set(states["treated"]):raise RuntimeError("Census inventory mismatch")
        if "failure" in states["baseline"].values():raise RuntimeError("Baseline census not clean")
        regressions=sorted(k for k,v in states["baseline"].items() if v=="passed" and states["treated"][k]!="passed")
        expected=sorted(known["census_regressions"])
        if regressions!=expected:raise RuntimeError("Census behavior differs from previous evidence")
        draws=None;draw_seconds=0.0
        if not regressions and mode!="census_only":
            previous_load=drawharness._load
            def logged_load(path):
                module=previous_load(path);judge=module.judge
                def logged(scope,draw,without,with_):
                    pw,pt=map(bool,judge(scope,draw,without,with_))
                    with (directory/"draws.jsonl").open("a") as stream:
                        stream.write(json.dumps({"scope":scope,"draw":draw,"without":without,"with":with_,
                                     "passed_without":pw,"passed_with":pt,"z":int(not pt)-int(not pw)},allow_nan=False)+"\n")
                    return pw,pt
                module.judge=logged;return module
            drawharness._load=logged_load;draw_start=time.perf_counter()
            try:
                draws=drawharness.run_draw_study(target,bound["treated"],ROOT/"study_i"/target_cfg["draw_oracle"],
                         dict(cfg["diagnostic_draws"],b8_full=mode=="census_then_full"),len(cfg["diagnostic_draws"]["cells"]))
            finally:drawharness._load=previous_load
            draw_seconds=time.perf_counter()-draw_start
            if any((v.get("b8") or v)["counts"]["harness_error"] for v in draws["scopes"].values()):
                raise RuntimeError("Draw harness failure")
        elapsed=time.perf_counter()-start;census_seconds=sum(r["seconds"] for r in runs)
        row={"repetition":rep,"mode":mode,"seconds":elapsed,"census_seconds":census_seconds,
             "setup_copy_seconds":elapsed-census_seconds-draw_seconds,"draw_pipeline_seconds":draw_seconds,
             "paired_draws":sum(len(v["trace"]) for v in draws["scopes"].values()) if draws else 0,
             "census_regressions":regressions,"census_veto":bool(regressions),"draw_result":draws,"runs":runs}
        write_json(directory/"RESULT.json",row);record["measurements"].append(row)
        write_json(out/"execution_progress.json",record)
        shutil.rmtree(directory/"work")
        print(json.dumps({k:row[k] for k in ("repetition","mode","seconds","paired_draws","census_veto")}),flush=True)
    means={m:{k:statistics.mean(r[k] for r in record["measurements"] if r["mode"]==m)
               for k in ("seconds","census_seconds","setup_copy_seconds","draw_pipeline_seconds","paired_draws")} for m in modes}
    record.update(status="MEASURED_AWAITING_RAW_AUDIT",means=means)
    write_json(out/"COST_RESULT.json",record)
    lines=["# Census-first cost: "+args.target,"","Exploratory, known target; no model call. All policies stop after a census veto.","",
           "| Policy | Total mean seconds | Census mean seconds | Mean paired draws |", "|---|---:|---:|---:|"]
    for m,v in means.items():lines.append("| %s | %.4f | %.4f | %.0f |"%(m,v["seconds"],v["census_seconds"],v["paired_draws"]))
    lines += ["", "Census-only does not certify a benefit margin or generator-wide harm rate. Timing comparisons are not equal-guarantee comparisons.",
              "On SQLAlchemy the expected census veto should suppress all draw work. Differences among such arms are timing noise, not statistical power.",
              "On NetworkX compare the extra cost of draw certification with census-only. Do not call a slower method a speedup.",
              "Three repetitions on one machine/target are not independent repositories; download/install excluded. Raw logs, XML, JSONL and schedule retained."]
    (out/"COST_RESULT.md").write_text("\n".join(lines)+"\n")


if __name__=="__main__":main()
