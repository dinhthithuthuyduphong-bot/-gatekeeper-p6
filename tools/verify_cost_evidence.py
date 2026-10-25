"""Recompute the cost summary and outcome counts from saved XML/draw journals.

No tests, downloads or providers are executed. Timing is a recorded measurement;
this verifies internal consistency, not clock accuracy or generalization.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from study_i.run import xml_cases


def verify(root, output):
    root=Path(root); result={"status":"VERIFIED_FROM_RAW", "model_calls":0, "targets":{}}
    for name in ("sqlalchemy","networkx"):
        folder=root/name; path=folder/"COST_RESULT.json"
        doc=json.loads(path.read_text()); rows=doc["measurements"]
        if doc["repetitions"]!=3 or len(rows)!=6: raise ValueError("missing measurement")
        if doc["code_sha256"]!=hashlib.sha256((ROOT/"tools/benchmark_admission_cost.py").read_bytes()).hexdigest():
            raise ValueError("benchmark code differs from recorded measurement")
        expected={(r,m) for r in range(3) for m in ("sequential","full_draws")}
        if {(r["rep"],r["mode"]) for r in rows}!=expected: raise ValueError("duplicate/missing policy arm")
        files={}; total_pairs=0
        for row in rows:
            run=folder/(str(row["rep"])+"_"+row["mode"])
            if json.loads((run/"RESULT.json").read_text())!=row: raise ValueError("measurement differs from raw result")
            states={arm:xml_cases(run/(arm+".xml")) for arm in ("baseline","treated")}
            if states["baseline"].keys()!=states["treated"].keys(): raise ValueError("census inventory changed")
            if any(v["status"] not in ("passed","skipped") for v in states["baseline"].values()): raise ValueError("invalid baseline census")
            if any(v["status"]=="error" for v in states["treated"].values()): raise ValueError("invalid treated census")
            regressions=[k for k,v in states["baseline"].items() if v["status"]=="passed" and states["treated"][k]["status"]!="passed"]
            if sorted(regressions)!=sorted(row["census_regressions"]): raise ValueError("regressions mismatch")
            journals=defaultdict(list)
            for line in (run/"draws.jsonl").read_text().splitlines():
                item=json.loads(line);journals[item["scope"]].append([item["z"],item["z"]>0])
            if set(journals)!=set(row["draw_result"]["scopes"]): raise ValueError("scope inventory mismatch")
            pairs=sum(map(len,journals.values()));total_pairs+=pairs
            if pairs!=row["paired_draws"]: raise ValueError("draw count mismatch")
            for scope, info in row["draw_result"]["scopes"].items():
                if journals[scope]!=info["trace"]: raise ValueError("journal/trace mismatch")
                prefix=journals[scope][:info["draws"]]
                counts={"help":sum(z<0 for z,h in prefix),"hurt":sum(z>0 for z,h in prefix),
                        "tie":sum(z==0 for z,h in prefix),"harness_error":0}
                if counts!=info["counts"]: raise ValueError("stopped counts mismatch")
                if row["mode"]=="full_draws" and len(journals[scope])!=300: raise ValueError("incomplete full budget")
            for f in run.iterdir():
                if f.is_file(): files[f.relative_to(folder).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
        for rep in range(3):
            a,b=[next(r for r in rows if r["rep"]==rep and r["mode"]==m) for m in ("sequential","full_draws")]
            for scope,x in a["draw_result"]["scopes"].items():
                y=b["draw_result"]["scopes"][scope]
                if any(x[k]!=y[k] for k in ("decision","draws","e_min")): raise ValueError("policies differ in stopped evidence")
                if x["trace"]!=y["trace"][:len(x["trace"])]: raise ValueError("policies use different draw prefixes")
        for mode,mean in doc["means"].items():
            for field,value in mean.items():
                computed=statistics.mean(r[field] for r in rows if r["mode"]==mode)
                if not math.isclose(value,computed,rel_tol=1e-12,abs_tol=1e-12): raise ValueError("mean mismatch")
        result["targets"][name]={"measurements":6,"paired_draws":total_pairs,
             "saving_fraction":1-doc["means"]["sequential"]["seconds"]/doc["means"]["full_draws"]["seconds"],
             "summary_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"raw_sha256":files}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2))
    print(json.dumps({"status":result["status"],"targets":{k:{f:v[f] for f in ("measurements","paired_draws","saving_fraction")} for k,v in result["targets"].items()}},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--root",default="research_closure/results/cost");p.add_argument("--out",required=True);a=p.parse_args();verify(a.root,a.out)
