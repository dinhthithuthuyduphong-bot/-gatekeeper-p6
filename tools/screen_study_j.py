"""Static screening only: no upstream import, tests, provider call or treatment execution.

Match both frozen transforms and record possible test references. A matching name
and literal is NOT an executable oracle or a tier-1 evidence designation.
"""
import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gatekeeper_lite.skill import Skill
from gatekeeper_lite.transforms import Abstain
from gatekeeper_ext.none_identity import register

SKILLS = {"bool_guard": "study_d/skills/bool-excluded-from-int.json",
          "none_identity": "study_g/skills/none-identity.json"}


def inspect_candidate(candidate, output):
    row = dict(candidate)
    log = []
    repo = candidate.get("canonical_repository", candidate["repository"])
    row.update(status="STATIC_ONLY_NOT_ELIGIBLE", treatment_runs=0, test_runs=0)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            checkout = Path(tmp)
            for command in (["git", "init", "-q"],
                            ["git", "-c", "gc.auto=0", "fetch", "--depth=1", "https://github.com/"+repo+".git", candidate["revision"]],
                            ["git", "checkout", "--detach", "FETCH_HEAD"],
                            ["git", "rev-parse", "HEAD"]):
                result = subprocess.run(command, cwd=checkout, text=True, capture_output=True, timeout=90)
                log.append({"command": command, "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr})
                if result.returncode: raise RuntimeError("source fetch/checkout failed")
            if result.stdout.strip() != candidate["revision"]: raise ValueError("revision mismatch")
            row["license_files"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in checkout.iterdir() if p.is_file() and p.name.lower().startswith(("license", "copying"))}
            tests, sources, parse_errors = [], [], []
            for path in sorted(checkout.rglob("*.py")):
                if path.is_symlink(): continue
                rel = path.relative_to(checkout).as_posix()
                source = path.read_text(encoding="utf-8", errors="replace")
                try: tree = ast.parse(source)
                except SyntaxError as exc:
                    parse_errors.append({"file": rel, "error": str(exc)}); continue
                parts = path.relative_to(checkout).parts
                is_test = any(p in ("test", "tests", "testing") for p in parts[:-1]) or path.name.startswith("test_")
                if is_test:
                    for fn in ast.walk(tree):
                        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or not fn.name.startswith("test"): continue
                        nodes = list(ast.walk(fn))
                        tests.append({"file": rel, "test": fn.name, "line": fn.lineno,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "names": {n.id for n in nodes if isinstance(n, ast.Name)} | {n.attr for n in nodes if isinstance(n, ast.Attribute)},
                            "bool_guard": any(isinstance(n, ast.Constant) and type(n.value) is bool for n in nodes),
                            "none_identity": any(isinstance(n, ast.Constant) and n.value is None for n in nodes)})
                elif not any(p in ("docs", "doc", "examples", ".git") for p in parts[:-1]):
                    sources.append((rel, source, hashlib.sha256(path.read_bytes()).hexdigest()))
            row["skills"] = {}
            for name, skill_path in SKILLS.items():
                transform = Skill.load(ROOT/skill_path).transform()
                sites, errors = [], []
                for rel, source, digest in sources:
                    try: transformed = transform.apply(source, single_site=False)
                    except Abstain: continue
                    except Exception as exc:
                        errors.append({"file": rel, "error": type(exc).__name__+": "+str(exc)}); continue
                    for site in transformed.sites:
                        witnesses = [{k: t[k] for k in ("file", "test", "line", "sha256")}
                            for t in tests if t[name] and site.function in t["names"]]
                        sites.append({"file": rel, "line": site.lineno, "function": site.function,
                                      "snippet": site.snippet, "sha256": digest,
                                      "possible_test_references": witnesses})
                row["skills"][name] = {"n_sites": len(sites), "n_sites_with_possible_test_reference": sum(bool(s["possible_test_references"]) for s in sites),
                                       "sites": sites, "matcher_errors": errors}
            row["parse_errors"] = parse_errors
    except Exception as exc:
        row.update(status="SCREEN_ERROR", error=type(exc).__name__+": "+str(exc))
    key = candidate["repository"].replace("/", "__")
    (output/(key+".log.json")).write_text(json.dumps(log, indent=2))
    (output/(key+".json")).write_text(json.dumps(row, indent=2))
    print(json.dumps({"repo": repo, "status": row["status"], "matches": {k:v["n_sites"] for k,v in row.get("skills",{}).items()}}), flush=True)
    return row


def main(roster, output):
    out=Path(output); out.mkdir(parents=True, exist_ok=False)
    register()
    data=json.loads(Path(roster).read_text())
    receipt={"evidence":"STATIC_SCREEN_NOT_PROSPECTIVE_OUTCOMES", "model_calls":0,
             "treatment_runs":0, "test_runs":0, "roster_sha256":hashlib.sha256(Path(roster).read_bytes()).hexdigest(),
             "code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "skill_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SKILLS.values()}}
    (out/"PRE_EXECUTION.json").write_text(json.dumps(receipt,indent=2))
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda c: inspect_candidate(c,out),data["candidates"]))
    receipt["candidates"]=rows
    (out/"SCREEN_RESULT.json").write_text(json.dumps(receipt,indent=2))
    lines=["# Study J: static candidate screen", "", "No test or treatment execution. Name/literal matches are leads, not validated oracles.", "",
           "| Repository | Bool sites | None sites | Possible test references (bool / none) | Status |", "|---|---|---|---|---|"]
    for r in rows:
        b,n=(r.get("skills",{}).get(k,{}) for k in ("bool_guard","none_identity"))
        lines.append(f"| {r['repository']} | {b.get('n_sites','—')} | {n.get('n_sites','—')} | {b.get('n_sites_with_possible_test_reference','—')} / {n.get('n_sites_with_possible_test_reference','—')} | {r['status']} |")
    lines += ["", "Study J remains BLOCKED. Check real license text, baseline stability, oracle semantics, coverage and prior exposure before eligibility; publicly freeze before treatment."]
    (out/"SCREEN_RESULT.md").write_text("\n".join(lines)+"\n")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--roster",default="study_j/CANDIDATE_ROSTER.json");p.add_argument("--out",required=True);a=p.parse_args();main(a.roster,a.out)
