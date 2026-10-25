"""Audit saved cost artifacts without executing targets, compilers or models."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from next_evidence.common import digest, write_json, xml_cases


def verify(folder):
    folder=Path(folder)
    document=json.loads((folder/"COST_RESULT.json").read_text())
    config=json.loads((ROOT/"next_evidence/config.json").read_text())
    target=document["target"]
    if target not in config["cost"]["targets"]:raise ValueError("Unknown target")
    if document["status"]!="MEASURED_AWAITING_RAW_AUDIT":raise ValueError("Unexpected result status")
    if document["code_sha256"]!=digest(ROOT/"next_evidence/cost.py"):raise ValueError("Runner hash differs")
    if document["config_sha256"]!=digest(ROOT/"next_evidence/config.json"):raise ValueError("Protocol hash differs")
    if document["model_calls"]!=0 or document["api_cost_usd"]!=0 or document["B9"]!="HOLD":
        raise ValueError("Paid policy violation")
    cfg=json.loads((ROOT/"study_i/targets.json").read_text())
    known=json.loads((ROOT/"study_i/results/ci-40084717332/inputs"/target/"RESULT.json").read_text())
    if document["source_revision"]!=cfg["targets"][target]["revision"]:raise ValueError("Source pin differs")
    rows=document["measurements"];modes=config["cost"]["modes"]
    expected={(r,m) for r in range(3) for m in modes}
    if len(rows)!=9 or {(r["repetition"],r["mode"]) for r in rows}!=expected:raise ValueError("Missing/duplicate policy arm")
    if document["schedule"]!=[[r["repetition"],r["mode"]] for r in rows]:raise ValueError("Schedule/order mismatch")
    positions={m:[] for m in modes}
    for rep in range(3):
        block=rows[rep*3:rep*3+3]
        if {r["repetition"] for r in block}!={rep} or {r["mode"] for r in block}!=set(modes):
            raise ValueError("Incomplete counterbalanced block")
        for position,row in enumerate(block):positions[row["mode"]].append(position)
    if any(sorted(p)!=[0,1,2] for p in positions.values()):raise ValueError("Order not counterbalanced")
    total_pairs=0;files={}
    for row in rows:
        directory=folder/("%s_%s"%(row["repetition"],row["mode"]))
        if json.loads((directory/"RESULT.json").read_text())!=row:raise ValueError("Per-arm result differs")
        for key in ("seconds","census_seconds","draw_pipeline_seconds","setup_copy_seconds"):
            if not math.isfinite(row[key]) or row[key]<0:raise ValueError("Invalid timing")
        if not math.isclose(row["seconds"],sum(row[k] for k in ("census_seconds","draw_pipeline_seconds","setup_copy_seconds")),abs_tol=1e-9):
            raise ValueError("Timing components inconsistent")
        states={}
        if [r["arm"] for r in row["runs"]]!=["baseline","treated"]:raise ValueError("Census arm mismatch")
        for run in row["runs"]:
            arm=run["arm"];xml=directory/(arm+".xml");log=directory/(arm+".log")
            if run["xml"]!=xml.name or run["log"]!=log.name:raise ValueError("Unexpected file path")
            if run["xml_sha256"]!=digest(xml) or run["log_sha256"]!=digest(log):raise ValueError("Raw hash mismatch")
            states[arm]=xml_cases(xml)
            if states[arm]!=run["case_status"]:raise ValueError("XML and result differ")
            if run["returncode"] not in (0,1) or "error" in states[arm].values():raise ValueError("Invalid census")
            if (run["returncode"]==1)!=("failure" in states[arm].values()):raise ValueError("Exit/XML mismatch")
        if set(states["baseline"])!=set(states["treated"]):raise ValueError("Inventory differs")
        if "failure" in states["baseline"].values():raise ValueError("Baseline fails")
        regressions=sorted(k for k,v in states["baseline"].items() if v=="passed" and states["treated"][k]!="passed")
        if regressions!=row["census_regressions"] or regressions!=sorted(known["census_regressions"]):
            raise ValueError("Unexpected census outcome")
        if row["census_veto"]!=bool(regressions):raise ValueError("Veto mismatch")
        if not math.isclose(row["census_seconds"],sum(r["seconds"] for r in row["runs"]),abs_tol=1e-9):
            raise ValueError("Census timing mismatch")
        if regressions or row["mode"]=="census_only":
            if row["draw_result"] is not None or row["paired_draws"]!=0 or row["draw_pipeline_seconds"]!=0 or (directory/"draws.jsonl").exists():
                raise ValueError("Draw work executed after census veto or in census-only policy")
        else:
            journals=defaultdict(list)
            for line in (directory/"draws.jsonl").read_text().splitlines():
                item=json.loads(line)
                if type(item["passed_without"]) is not bool or type(item["passed_with"]) is not bool:
                    raise ValueError("Invalid paired outcome type")
                z=int(not item["passed_with"])-int(not item["passed_without"])
                if item["z"]!=z:raise ValueError("Signed loss inconsistent")
                journals[item["scope"]].append([z,z>0])
            scopes=row["draw_result"]["scopes"]
            if set(journals)!=set(scopes):raise ValueError("Scope mismatch")
            if sum(map(len,journals.values()))!=row["paired_draws"]:raise ValueError("Pair count mismatch")
            for scope,info in scopes.items():
                if journals[scope]!=info["trace"]:raise ValueError("Raw trace mismatch")
                for summary,trace in ((info,journals[scope][:info["draws"]]),(info.get("b8"),journals[scope])):
                    if summary is None:continue
                    counts={"help":sum(z<0 for z,h in trace),"hurt":sum(z>0 for z,h in trace),
                            "tie":sum(z==0 for z,h in trace),"harness_error":0}
                    if summary["counts"]!=counts or summary["draws"]!=len(trace):raise ValueError("Draw summary mismatch")
                if row["mode"]=="census_then_full" and len(journals[scope])!=cfg["diagnostic_draws"]["n_max"]:
                    raise ValueError("Incomplete full budget")
            total_pairs+=row["paired_draws"]
        for file in directory.iterdir():
            if file.is_file():files[file.relative_to(folder).as_posix()]=digest(file)
    for rep in range(3):
        gate,full=[next(r for r in rows if r["repetition"]==rep and r["mode"]==m) for m in ("census_then_gate","census_then_full")]
        if gate["census_veto"]:continue
        for scope,x in gate["draw_result"]["scopes"].items():
            y=full["draw_result"]["scopes"][scope]
            if any(x[k]!=y[k] for k in ("decision","draws","e_min")) or x["trace"]!=y["trace"][:len(x["trace"])]:
                raise ValueError("Different policy stopping evidence/draw prefix")
    for mode in modes:
        for key,value in document["means"][mode].items():
            if not math.isclose(value,statistics.mean(r[key] for r in rows if r["mode"]==mode),rel_tol=1e-12,abs_tol=1e-12):
                raise ValueError("Mean not reproduced")
    return {"status":"RAW_CONSISTENCY_VERIFIED","target":target,"measurements":9,"paired_draws":total_pairs,
            "summary_sha256":digest(folder/"COST_RESULT.json"),"raw_sha256":files,
            "limitation":"This verifies internal consistency, not clock accuracy, cross-repo generalization, or equal guarantees of the three policies."}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--root",type=Path,required=True);a=p.parse_args()
    result=verify(a.root);write_json(a.root/"RAW_AUDIT.json",result)
    print(json.dumps({k:result[k] for k in ("status","target","measurements","paired_draws")}),flush=True)
