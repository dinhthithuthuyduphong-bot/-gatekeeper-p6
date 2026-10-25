"""Pinned source discovery only: no upstream import/test or treatment execution."""
import argparse
import ast
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from next_evidence.common import checkout, digest, new_output, verify_source, write_json


def call_name(node):
    if isinstance(node,ast.Name):return node.id
    if isinstance(node,ast.Attribute):return node.attr
    return None


def is_test(path):
    return bool(set(path.parts[:-1]) & {"test","tests","testing"}) or path.name.startswith("test_") or path.name.endswith("_test.py")


def production(path):
    return not is_test(path) and not set(path.parts[:-1]) & {"doc","docs","examples","example","benchmarks","bench",".git"} and not path.name.startswith(("example", "benchmark"))


def source_scan(source, candidate):
    from gatekeeper_ext.none_identity import register
    from gatekeeper_lite.skill import Skill
    from gatekeeper_lite.transforms import Abstain
    register()
    skills={"bool_guard":"study_d/skills/bool-excluded-from-int.json", "none_identity":"study_g/skills/none-identity.json"}
    transforms={k:Skill.load(ROOT/v).transform() for k,v in skills.items()}
    sites={k:[] for k in skills};tests=[];functions=[];errors=[];matcher_errors=[]
    for path in sorted(source.rglob("*.py")):
        if path.is_symlink() or ".git" in path.relative_to(source).parts:continue
        rel=path.relative_to(source)
        if not is_test(rel) and not production(rel):continue
        text=path.read_text(encoding="utf-8",errors="replace")
        try:tree=ast.parse(text)
        except SyntaxError as exc:
            errors.append({"file":rel.as_posix(),"line":exc.lineno,"error":exc.msg});continue
        for fn in ast.walk(tree):
            if not isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef)):continue
            calls=sorted({call_name(n.func) for n in ast.walk(fn) if isinstance(n,ast.Call)}-{None})
            assertions=[ast.get_source_segment(text,n) for n in ast.walk(fn) if isinstance(n,ast.Assert)
                        or isinstance(n,ast.Call) and str(call_name(n.func)).startswith("assert")]
            row={"file":rel.as_posix(),"function":fn.name,"line":fn.lineno,
                 "sha256":digest(path),"calls":calls,"assertions":assertions}
            row["id"]="%s::%s@L%s"%(rel.as_posix(),fn.name,fn.lineno)
            if is_test(rel) and fn.name.startswith("test"):tests.append(row)
            elif production(rel):functions.append(row)
        if not production(rel):continue
        for name,transform in transforms.items():
            try:bound=transform.apply(text,single_site=False)
            except Abstain:continue
            except Exception as exc:
                matcher_errors.append({"file":rel.as_posix(),"skill":name,"error":type(exc).__name__+": "+str(exc)});continue
            sites[name].extend({"file":rel.as_posix(),"line":s.lineno,"function":s.function,
                                "snippet":s.snippet,"sha256":digest(path)} for s in bound.sites)
    referenced=set()
    for name,rows in sites.items():
        for site in rows:
            symbols={site["function"]};chains=[]
            for depth in range(2):
                callers={f["function"] for f in functions if symbols.intersection(f["calls"])}
                chains.append(sorted(callers));symbols|=callers
            site["possible_test_references"]=[t["id"] for t in tests if symbols.intersection(t["calls"])]
            referenced.update(site["possible_test_references"])
            site["name_based_caller_layers"]=chains
    focus=[t["id"] for t in tests if set(t["calls"]) & {"clean_perms","sync_roles"}] if candidate["id"]=="airflow" else []
    referenced.update(focus)
    return {"status":"STATIC_SCAN_WITH_ERRORS" if errors or matcher_errors else "STATIC_SCAN_COMPLETE_NOT_ELIGIBLE",
            "candidate":candidate,"skill_hashes":{p:digest(ROOT/p) for p in skills.values()},
            "sites":sites,"parse_errors":errors,"matcher_errors":matcher_errors,
            "test_catalog":{t["id"]:t for t in tests if t["id"] in referenced},
            "license_files":{p.name:digest(p) for p in source.iterdir() if p.is_file() and p.name.lower().startswith(("license","copying"))},
            "airflow_focus_tests":focus,"test_functions_inspected":len(tests),"model_calls":0,
            "test_runs":0,"treatment_runs":0,"oracle_tier":None,
            "caveat":"Function-name reach is an overapproximation, not dynamic coverage or oracle validation. No upper bound is inferred when files fail to parse."}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("action",choices=["fetch-pydantic","scout"])
    p.add_argument("--target");p.add_argument("--out",required=True,type=Path);args=p.parse_args()
    out=new_output(args.out)
    if args.action=="fetch-pydantic":
        cfg=json.loads((ROOT/"next_evidence/config.json").read_text())["pydantic"]
        src=checkout(cfg["repository"],cfg["revision"],out/"work/source",out)
        verify_source(src,cfg["revision"],cfg["source_sha256"])
        write_json(out/"SOURCE.json",{"status":"SOURCE_VERIFIED_TESTS_NOT_RUN","config":cfg,"model_calls":0})
        return
    roster=json.loads((ROOT/"next_evidence/scout_roster.json").read_text())["candidates"]
    candidate=next((x for x in roster if x["id"]==args.target),None)
    if candidate is None:raise ValueError("Unknown pinned candidate")
    source=checkout(candidate["repo"],candidate["sha"],out/"work/source",out)
    result=source_scan(source,candidate);write_json(out/"SCAN_RESULT.json",result)
    lines=["# Source scan: "+candidate["repo"],"", "Status: **"+result["status"]+"**. Tests/treatment/model calls: **0**.","",
           "| Skill | Production matcher sites | Sites with possible test-name references |", "|---|---:|---:|"]
    for name,sites in result["sites"].items():
        lines.append("| %s | %d | %d |"%(name,len(sites),sum(bool(s["possible_test_references"]) for s in sites)))
    lines += ["", "Parse errors: %d; matcher errors: %d."%(len(result["parse_errors"]),len(result["matcher_errors"])),
              "",result["caveat"],"", "No candidate is called beneficial, harmful, tier-1, admitted or prospectively validated from this scan."]
    (out/"SCAN_RESULT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"target":candidate["id"],"status":result["status"],"sites":{k:len(v) for k,v in result["sites"].items()}}),flush=True)


if __name__=="__main__":main()
