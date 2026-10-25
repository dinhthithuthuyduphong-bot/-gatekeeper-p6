"""Three untouched baseline runs and dynamic source reach; no treatment branch exists."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from next_evidence.common import baseline_status, digest, execute, new_output, verify_source, write_json, xml_cases
from next_evidence.site_coverage import FORMAT


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout",type=Path,required=True);parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args();out=new_output(args.out);source=args.checkout.resolve()
    config=json.loads((ROOT/"next_evidence/config.json").read_text());cfg=config["pydantic"]
    if cfg["treatment_allowed"] or config["model_calls_allowed"]:raise ValueError("This runner is baseline-only")
    if sys.version.split()[0]!=cfg["python"]:raise ValueError("Wrong pinned Python")
    verify_source(source,cfg["revision"],cfg["source_sha256"])
    record={"status":"RUNNING_BASELINE_ONLY","config":cfg,"config_sha256":digest(ROOT/"next_evidence/config.json"),
            "code_sha256":{n:digest(ROOT/"next_evidence"/n) for n in ("baseline.py","pytest_probe.py","common.py","site_coverage.py")},
            "python":sys.version,"environment":sorted((d.metadata["Name"],d.version) for d in importlib.metadata.distributions()),
            "model_calls":0,"treatment_runs":0,"runs":[]}
    write_json(out/"PRE_EXECUTION.json",record)
    for rep in range(1,config["repetitions"]+1):
        probe=out/("probe_%s"%rep);xml=out/("baseline_%s.xml"%rep)
        env=dict(os.environ,PYTHONPATH=os.pathsep.join([str(source),str(ROOT)]),PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
                 PYTHONDONTWRITEBYTECODE="1",PYTHONHASHSEED="0",GK_PROBE_OUTPUT=str(probe),
                 GK_PROBE_SOURCE=str(source),GK_PROBE_SITES=json.dumps(cfg["bool_sites"]))
        command=[sys.executable,"-m","pytest","-q","--tb=short","-o","addopts=","-p","no:cacheprovider",
                 "-p","pytest_mock","-p","next_evidence.pytest_probe","--junitxml="+str(xml),*cfg["tests"]]
        row=execute(command,source,out/("baseline_%s.log"%rep),env=env,timeout=900)
        row.update(repetition=rep,xml=xml.name,inventory=[],phase_signature=[],phase_errors=[],call_failures=[],passed_calls=0,site_reach=[])
        if row["returncode"] in (0,1) and (probe/"inventory.json").exists() and (probe/"phases.jsonl").exists():
            if not xml.exists():raise ValueError("Missing JUnit evidence")
            row["xml_sha256"]=digest(xml)
            row["xml_counts"]={s:sum(v==s for v in xml_cases(xml).values()) for s in ("passed","failure","error","skipped")}
            row["inventory"]=json.loads((probe/"inventory.json").read_text())
            if len(row["inventory"])!=len(set(row["inventory"])):raise ValueError("Duplicate collected node ID")
            phases=[json.loads(x) for x in (probe/"phases.jsonl").read_text().splitlines()]
            row["phase_signature"]=[[x["nodeid"],x["phase"],x["outcome"],x["wasxfail"]] for x in phases]
            keys=[(x["nodeid"],x["phase"]) for x in phases]
            if len(keys)!=len(set(keys)):raise ValueError("Duplicate phase report")
            if any(x["nodeid"] not in row["inventory"] for x in phases):raise ValueError("Unknown test phase")
            row["phase_errors"]=[x["nodeid"] for x in phases if x["phase"]!="call" and x["outcome"]=="failed"]
            row["call_failures"]=[x["nodeid"] for x in phases if x["phase"]=="call" and x["outcome"]=="failed"]
            row["passed_calls"]=sum(x["phase"]=="call" and x["outcome"]=="passed" for x in phases)
            if not row["phase_errors"] and row["passed_calls"]!=row["xml_counts"]["passed"]:
                raise ValueError("XML and phase pass counts disagree")
            if not all((probe/name).is_file() for name in ("SESSION.json","site_coverage.json","coverage.data")):
                raise ValueError("Probe incomplete; do not infer reach or validity")
            session=json.loads((probe/"SESSION.json").read_text());loaded=session.get("loaded_module")
            if not loaded or not Path(loaded).resolve().is_relative_to(source):
                raise ValueError("Tests imported an installed package instead of the pinned checkout")
            cov=json.loads((probe/"site_coverage.json").read_text())
            if cov["format"]!=FORMAT or cov["coverage_data_sha256"]!=digest(probe/"coverage.data"):
                raise ValueError("Site report format or raw coverage hash mismatch")
            expected_sources={name:cfg["source_sha256"][name] for name in cfg["modules"]}
            if cov["source_sha256"]!=expected_sources:
                raise ValueError("Site report source hashes differ from the pinned config")
            if len(cov["sites"])!=len(cfg["bool_sites"]):raise ValueError("Incomplete site report")
            for site,observed in zip(cfg["bool_sites"],cov["sites"]):
                if any(observed.get(k)!=v for k,v in site.items()):raise ValueError("Site order/config mismatch")
                contexts=observed["all_contexts"]
                calls=sorted({c.rsplit("|",1)[0] for c in contexts if c.endswith("|call")})
                if (observed["executed"]!=bool(contexts) or observed["test_call_contexts"]!=calls
                        or observed["executed_in_test_call"]!=bool(calls)):
                    raise ValueError("Site reach flags and raw contexts disagree")
                if any(node not in row["inventory"] for node in calls):raise ValueError("Unknown call context")
                row["site_reach"].append(observed)
            row["probe_sha256"]={p.name:digest(p) for p in probe.iterdir() if p.is_file()}
        record["runs"].append(row);write_json(out/"execution_progress.json",record)
    verify_source(source,cfg["revision"],cfg["source_sha256"])
    record["status"]=baseline_status(record["runs"])
    record["test_runs"]=len(record["runs"])
    record["oracle_validated"]=False
    write_json(out/"BASELINE_RESULT.json",record)
    lines=["# Pydantic-settings: baseline and dynamic reach", "", "Status: **"+record["status"]+"**.",
           "No treatment or model call. This is not a transfer result or a prospective admission.", "",
           "| Repetition | Exit | Collected | Passed calls | Failed calls | Setup/teardown failures |",
           "|---|---:|---:|---:|---:|---:|"]
    for r in record["runs"]:lines.append("| %s | %s | %s | %s | %s | %s |"%(r["repetition"],r["returncode"],len(r["inventory"]),r["passed_calls"],len(r["call_failures"]),len(r["phase_errors"])))
    lines += ["", "| Candidate site | Raw physical-line trace reached in every baseline run | Tests reaching it in call phase (first run) |", "|---|---|---:|"]
    if all(len(r["site_reach"])==len(cfg["bool_sites"]) for r in record["runs"]):
        for i,site in enumerate(cfg["bool_sites"]):
            lines.append("| %s:%s | %s | %s |"%(site["file"],site["line"],all(r["site_reach"][i]["executed"] for r in record["runs"]),len(record["runs"][0]["site_reach"][i]["test_call_contexts"])))
    else:lines.append("| Coverage incomplete | Not evaluated | Not evaluated |")
    lines += ["", "Reach does not establish that bool inputs occur or assertions cover the changed semantics. Send the compact next-evidence-return artifact for oracle review; coverage.data stays in the separate next-raw-pydantic-baseline artifact. No treatment is authorized by a green baseline status. Timings include instrumentation."]
    (out/"BASELINE_RESULT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":record["status"],"test_runs":len(record["runs"]),"treatment_runs":0}),flush=True)
    if record["status"]!="BASELINE_STABLE_ORACLE_REVIEW_PENDING":raise SystemExit(2)


if __name__=="__main__":main()
