"""Study P feasibility, step 2 (design fixed in research_closure/results/STUDY_P_PLAN.md): a light model writes the
input generator of each edited function; the generator runs inside each snapshot with the same seed.

python tools/fn_probe_llm.py ELIGIBLE.json NAME OUT_DIR MODELS.json CAP_USD [N_INPUTS=200] [MAX_FUNCS=3]
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import fn_probe as FP  # noqa: E402
from gatekeeper_ext import fn_llm_gen as LG  # noqa: E402
from gatekeeper_lite import b9  # noqa: E402

MODEL_NAME, MAX_TOKENS, TEMPERATURES = "vertex-gemini-flash", 4000, (0.0, 0.4)


def run_gen(py, root, pythonpath, rel, qualname, code_path, out, n, env, seed=0):
    args = {"root": str(root), "pythonpath": pythonpath, "file": rel, "qualname": qualname, "mode": "run_gen", "n": n, "seed": seed,
            "gen_code": str(code_path), "out": str(out), "timeout": 2}
    ap = Path(str(out) + ".args.json")
    try:
        with FP.at_common_path(root) as common:
            args["root"] = str(common)
            ap.write_text(json.dumps(args))
            p = subprocess.run([str(py), str(ROOT / "tools" / "fn_probe_inner.py"), str(ap)], env=env, capture_output=True, text=True, timeout=120 + n * 2)
    except subprocess.TimeoutExpired:
        return {"status": "PROCESS_TIMEOUT"}
    if not Path(out).exists():
        return {"status": "CRASHED", "tail": (p.stdout + p.stderr)[-400:]}
    return json.loads(Path(out).read_text())


def one_function(client, model_id, prices, guard, py, orig, gold, pythonpath, rel, qualname, issue_text, diff, work, n, env, seed):
    rec = {"file": rel, "qualname": qualname, "calls": []}
    try:
        ctx = LG.function_context(orig, rel, qualname)
    except Exception as exc:
        return dict(rec, usable=False, why="did not run: no source (%s)" % type(exc).__name__)
    messages = LG.build_messages(rel, qualname, ctx, issue_text, diff)
    tag = "%s__%s" % (rel.replace("/", "_"), qualname)
    o1 = None
    for attempt, temp in enumerate(TEMPERATURES):
        try:
            guard.check(messages, MAX_TOKENS, prices)
        except b9.BudgetExceeded as exc:
            rec["calls"].append({"verdict": "BUDGET_CAP", "detail": str(exc)[:200]})
            break
        try:
            reply = client.complete(model_id, messages, MAX_TOKENS, temp, seed + attempt)
        except Exception as exc:                                   # a model or network error is a result, not a retry
            rec["calls"].append({"verdict": "MODEL_ERROR", "detail": ("%s: %s" % (type(exc).__name__, exc))[:300]})
            break
        cost = guard.add(reply["usage"], prices)
        call = {"verdict": "REPLY", "cost_usd": round(cost, 6), "usage": reply["usage"], "finish_reason": (reply.get("raw") or {}).get("finish_reason")}
        rec["calls"].append(call)
        code = LG.extract_code(reply["text"])
        if not code:
            call["verdict"] = "NO_CODE"
            messages = messages + [{"role": "assistant", "content": reply["text"]}, {"role": "user", "content": LG.RETRY.format(error="no code block defining make_inputs")}]
            continue
        cp = Path(work) / ("%s.gen%d.py" % (tag, attempt))
        cp.write_text(code)
        o1 = run_gen(py, orig, pythonpath, rel, qualname, cp, Path(work) / ("%s.o1_%d.json" % (tag, attempt)), n, env)
        if o1.get("status") == "GEN_FAILED":
            call["verdict"] = "GENERATOR_FAILED"
            call["error"] = o1.get("error", "")[:300]
            messages = messages + [{"role": "assistant", "content": reply["text"]}, {"role": "user", "content": LG.RETRY.format(error=o1.get("error", "")[:1500])}]
            o1 = None
            continue
        rec["generator_attempt"] = attempt
        o2 = run_gen(py, orig, pythonpath, rel, qualname, cp, Path(work) / ("%s.o2.json" % tag), n, env)
        g = run_gen(py, gold, pythonpath, rel, qualname, cp, Path(work) / ("%s.g.json" % tag), n, env)
        rec.update(FP.compare(o1, o2, g))
        return rec
    return dict(rec, usable=False, why="did not run: no working generator (%s)" % ",".join(c["verdict"] for c in rec["calls"]))


def probe_llm(client, model_id, prices, cap_usd, py, orig, gold, modules, pythonpath, issue_text, work, n=200, max_funcs=3, env=None,
              seed=1, diff_for=lambda rel: ""):
    """The whole step-2 measurement for one instance whose snapshots and environment are ready."""
    from gatekeeper_ext import testmut as T
    edited = T.edited_with_lines(orig, gold, modules)
    guard = b9.SpendGuard(float(cap_usd))
    funcs = [one_function(client, model_id, prices, guard, py, orig, gold, pythonpath, e["file"], e["qualname"], issue_text,
                          diff_for(e["file"]), work, n, env, seed)
             for e in sorted(edited, key=lambda e: (e["file"], e["qualname"]))[:max_funcs]]
    return {"edited_functions": len(edited), "functions": funcs, "verdict": FP.instance_verdict(funcs, None, len(edited)),
            "spent_usd": round(guard.spent_usd, 6), "model_calls": guard.calls}


def file_diff(repo, pre, gold, rel):
    import vet_target as V
    r = V.sh([*V.GIT, "diff", pre, gold, "--", rel], cwd=repo, check=False)
    return (r.stdout or "")[:4000]


def main(eligible_path, name, out_dir, models_path, cap_usd, n=200, max_funcs=3):
    from cohort_inner import RefreshingClient, api_seed
    from gatekeeper_ext import issue_fetch
    rec = next(r for r in json.loads(Path(eligible_path).read_text()) if r["name"] == name)
    cfg = next(m for m in json.loads(Path(models_path).read_text())["models"] if m["name"] == MODEL_NAME)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="fnl_"))
    report = {"name": name, "repo": rec["repo"], "status": "started", "model": cfg["model_id"]}
    try:
        p = FP.prepare(rec, work)
        m = re.search(r"_pr(\d+)$", name)
        title, issue, prov = issue_fetch.fetch(rec["repo"], int(m.group(1)), os.environ.get("GITHUB_TOKEN", "")) if m else ("", None, {"error": "no pr number"})
        report["issue_fetch"] = prov
        issue_text = ("%s\n\n%s" % (issue["title"], issue["body"])) if issue else title
        client = RefreshingClient(cfg["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", "")), cfg["key_env"], cfg.get("extra", {}))
        (work / "probe").mkdir()
        report.update(probe_llm(client, cfg["model_id"], cfg["prices_usd_per_mtok"], cap_usd, p["py"], p["orig"], p["gold"], p["modules"],
                                p["pythonpath"], issue_text, work / "probe", int(n), int(max_funcs), p["env"], api_seed(FP_seed(name)),
                                lambda rel: file_diff(p["repo"], rec["pre"], rec["gold"], rel)), status="FINISHED")
    except Exception as exc:
        report.update(status="ERROR", error=("%s: %s" % (type(exc).__name__, exc))[:400], verdict="snapshots or environment failed")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    (out / ("FNPROBE_%s.json" % name)).write_text(json.dumps(report, indent=1, default=str))
    print(json.dumps({k: report.get(k) for k in ("name", "status", "verdict", "spent_usd")}))
    return 0


def FP_seed(name):
    import hashlib
    return int(hashlib.sha256(("study-p-llmgen:" + name).encode()).hexdigest()[:8], 16)


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:8]))
