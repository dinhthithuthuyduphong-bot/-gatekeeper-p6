"""Recompute Study K from raw XML and every paired draw, without target packages."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import importlib.util
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from study_i.run import digest, write_json, xml_cases
from gatekeeper_lite.eprocess import BettingEProcess, HarmCertEProcess, HarmAlarmEProcess, e_holm


def require(value, message):
    if not value:
        raise ValueError(message)


def counts(values):
    return {"help":sum(z < 0 for z in values), "tie":sum(z == 0 for z in values),
            "hurt":sum(z > 0 for z in values), "harness_error":0}


def audit(directory, output=None, markdown=None):
    directory = Path(directory)
    cfg = json.loads((HERE / "target.json").read_text())
    result = json.loads((directory / "RESULT.json").read_text())
    require(result["status"] == "VERIFIED_EXPLORATORY" and result["not_preregistered"], "Invalid status")
    require(result["config"] == cfg and result["config_sha256"] == digest(HERE / "target.json"), "Config changed")
    require(result["source_revision"] == cfg["revision"] and result["source_test_sha256"] == cfg["source_sha256"], "Wrong source")
    require(result["llm_calls"] == 0 and result["model_cost_usd"] == 0, "Unexpected model use")
    required_code = {"study_k/run.py", "study_k/oracles/control_frequency.py", "study_i/run.py"}
    require(set(result["code_sha256"]) == required_code, "Missing measured code hash")
    for rel, sha in result["code_sha256"].items():
        require(digest(ROOT / rel) == sha, "Measured code changed: " + rel)
    for rel, sha in cfg["gatekeeper_sha256"].items():
        require(digest(ROOT / rel) == sha, "Frozen engine/skill changed: " + rel)
    for rel, sha in cfg["vendor_sha256"].items():
        require(digest(HERE / rel) == sha, "Upstream vendor file changed: " + rel)
    expected_runs = {(a,n) for a in ("baseline","treated","gold") for n in range(1,cfg["repetitions"]+1)}
    require(Counter((r["arm"],r["repetition"]) for r in result["runs"]) == Counter(expected_runs), "Missing/duplicate run")
    states = {}
    for run in result["runs"]:
        cases = xml_cases(directory / run["xml"])
        labels = {k:v["status"] for k,v in cases.items()}
        require(len(cases) == cfg["n_tests"] and all(s in ("passed","failure") for s in labels.values()), "Invalid test inventory/outcome")
        require(labels == run["case_status"], "XML/JSON disagreement")
        c = {s:sum(v == s for v in labels.values()) for s in ("passed","failure")}
        require(c == run["counts"] and run["returncode"] == int(c["failure"] > 0), "Exit/count mismatch")
        require(math.isfinite(run["seconds"]) and run["seconds"] > 0 and (directory/run["log"]).stat().st_size > 0, "Missing log/time")
        if run["arm"] == "baseline":
            failures = [k for k,v in labels.items() if v == "failure"]
            require(len(failures) == 1 and failures[0].endswith("TestFRD::testNyquist"), "Unexpected baseline failure")
            detail = cases[failures[0]]["detail"]+cases[failures[0]]["message"]
            require("truth value of an array" in detail and "nyquist_plot" in detail, "Unclassified functional failure")
        else:
            require(c["failure"] == 0, "Skill/gold module not clean")
        if run["arm"] in states:
            require(states[run["arm"]] == labels, "Unstable repetitions")
        states[run["arm"]] = labels
    require(states["treated"] == states["gold"] and set(states["treated"]) == set(states["baseline"]), "Gold/test inventory mismatch")
    resolved = sorted(k for k,v in states["baseline"].items() if v == "failure" and states["treated"][k] == "passed")
    require(resolved == sorted(result["resolved_upstream_tests"]) and result["census_regressions"] == [], "Transfer summary mismatch")
    spec = importlib.util.spec_from_file_location("control_oracle_audit", HERE/"oracles/control_frequency.py")
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    observed = defaultdict(list)
    for line in (directory/"draws.jsonl").read_text().splitlines():
        row = json.loads(line)
        require("harness_error" not in row["without"] and "harness_error" not in row["with"], "Harness failure")
        require("/baseline/" in row["without"].get("module","") and "/treatment/" in row["with"].get("module",""), "Wrong imports")
        pw,pt = map(bool,oracle.judge(row["scope"],row["draw"],row["without"],row["with"]))
        require([pw,pt] == [row["passed_without"],row["passed_with"]] and row["z"] == int(not pt)-int(not pw), "Oracle/Z mismatch")
        observed[row["scope"]].append(row)
    require(set(observed) == set(oracle.scopes()) == set(result["diagnostic_draws"]["scopes"]), "Missing/extra scope")
    settings=cfg["diagnostic_draws"]
    cells=[]
    for scope, rows in observed.items():
        require(len(rows) == settings["n_max"] and [r["n"] for r in rows] == list(range(1,settings["n_max"]+1)), "Incomplete draws")
        rng=random.Random("%s:%s:%s" % (settings["seed"],cfg["target_id"],scope))
        generator=oracle.scopes()[scope]
        require(all(r["draw"] == generator(rng) for r in rows), "Generator/order/seed mismatch")
        raw=result["diagnostic_draws"]["scopes"][scope]
        trace=[[r["z"],r["passed_without"] and not r["passed_with"]] for r in rows]
        require(trace == raw["trace"] and raw["b8"]["draws"] == len(rows), "Raw trace mismatch")
        require(counts([r["z"] for r in rows]) == raw["b8"]["counts"], "Full counts mismatch")
        ben,cert,alarm=BettingEProcess(settings["theta"]),HarmCertEProcess(settings["eta"]),HarmAlarmEProcess(settings["eta"])
        decision,stop="UNDECIDED",len(rows)
        for n,(z,harm) in enumerate(trace,1):
            ben.update(z);cert.update(harm);alarm.update(harm)
            if alarm.value >= 1/settings["alpha_alarm"]:
                decision,stop="REJECT_HARM",n;break
            if min(ben.value,cert.value) >= len(settings["cells"])/settings["alpha"]:
                decision,stop="ADMIT",n;break
        require((decision,stop) == (raw["decision"],raw["draws"]), "Stopping mismatch")
        require(counts([r["z"] for r in rows[:stop]]) == raw["counts"], "Stopped counts mismatch")
        for field,value in (("e_benefit",ben.value),("e_cert",cert.value),("e_alarm",alarm.value),("e_min",min(ben.value,cert.value))):
            require(math.isfinite(raw[field]) and math.isclose(raw[field],value,rel_tol=1e-10,abs_tol=1e-12), "E-value mismatch: "+field)
        reach={str(s["line"]):sum(s["line"] in r["without"]["reached_lines"] for r in rows) for s in result["bindings"]}
        cells.append({"cell":cfg["target_id"]+"/"+scope,"raw_decision":decision,"draws_to_stop":stop,
                      "full_counts":raw["b8"]["counts"],"e_for_family":min(ben.value,cert.value),"baseline_line_reach":reach})
    require(Counter(c["cell"] for c in cells) == Counter(settings["cells"]), "Family mismatch")
    admitted=e_holm({c["cell"]:c["e_for_family"] for c in cells},settings["alpha"])
    for c in cells:
        c["final_decision"]="ADMIT_DIAGNOSTIC" if c["cell"] in admitted else "QUARANTINE"
    stability=[json.loads(x) for x in (directory/"statelessness.jsonl").read_text().splitlines()]
    require(Counter((r["scope"],r["n"]) for r in stability) == Counter((s,n) for s in observed for n in range(1,101)), "Missing/duplicate state check")
    clean=lambda x:{k:v for k,v in x.items() if k != "module"}
    for row in stability:
        original=observed[row["scope"]][row["n"]-1]
        require(not row["mismatch"] and clean(row["without"]) == clean(original["without"])
                and clean(row["with"]) == clean(original["with"]), "State/order mismatch")
    require(result["statelessness"] == {s:{"compared":100,"mismatches":0} for s in observed}, "State summary mismatch")
    receipt={"status":"VERIFIED_EXPLORATORY","not_preregistered":True,"model_calls":0,"B9":"HOLD",
             "runs":len(expected_runs),"upstream_test_executions":len(expected_runs)*cfg["n_tests"],
             "baseline_passing_tests_preserved":15,"resolved_upstream_tests":resolved,"new_regressions":0,
             "paired_draws":sum(map(len,observed.values())),"state_rechecks":len(stability),"cells":cells,
             "limitations":["Historical convenience selection; not prospective or population-representative.",
                            "Upstream testNyquist is a smoke oracle, not numerical accuracy.",
                            "Draw oracle is researcher-authored; only supplied SISO scopes are covered.",
                            "Selected 16-test module; not full repository census; gangof4_plot not covered.",
                            "Diagnostics execute the full draw budget; not a cost-saving experiment."]}
    if output:write_json(Path(output),receipt)
    if markdown:
        lines=["# Python-control: kết quả hồi cứu được kiểm tra từ log thô", "",
               "**VERIFIED_EXPLORATORY**; 0 lời gọi model; B9 HOLD.", "",
               "| Nhánh | Pass | Fail chức năng | Lặp tiến trình mới |", "|---|---:|---:|---:|",
               "| Baseline | 15 | 1 | 3 |", "| Skill đóng băng | 16 | 0 | 3 |", "| Gold upstream | 16 | 0 | 3 |", "",
               "Giữ nguyên toàn bộ 16 test của module upstream. Một test Nyquist F→P, 15 test đang pass được giữ; không có regression mới.", "",
               "| Scope | Quyết định chẩn đoán | Draws đến dừng | Help / tie / hurt trong 300 draws |", "|---|---|---:|---|"]
        for c in cells:
            n=c["full_counts"]
            lines.append("| %s | %s | %s | %s / %s / %s |"%(c["cell"],c["final_decision"],c["draws_to_stop"],n["help"],n["tie"],n["hurt"]))
        lines += ["", "Kiểm tra lại 100 draws/scope bằng thứ tự khác và worker mới mỗi 25 draws: không thấy sai khác.", "",
                  "Giới hạn: hồi cứu, một repo/phiên bản, selected-module census; test upstream là smoke test. Oracle số học riêng do nhóm nghiên cứu viết. Hai trong ba vị trí sửa được các draw scopes đi qua; gangof4_plot chưa được bao phủ. Không tuyên bố an toàn cho toàn repo, prospective success hay tiết kiệm chi phí từ lượt replay đầy đủ này.", "",
                  "Raw: RESULT.json, PRE_EXECUTION.json, 9 XML + log, skill.patch, draws.jsonl và statelessness.jsonl."]
        Path(markdown).write_text("\n".join(lines)+"\n")
    print(json.dumps(receipt,indent=2),flush=True)
    return receipt


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results",type=Path,required=True)
    p.add_argument("--output",type=Path)
    p.add_argument("--markdown",type=Path)
    a=p.parse_args();audit(a.results,a.output,a.markdown)
