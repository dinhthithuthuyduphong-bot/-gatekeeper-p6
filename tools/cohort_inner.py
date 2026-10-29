"""Study N: everything that must run INSIDE the instance's virtual environment (the visible check, the hidden tests and
the harness all use sys.executable): build the repair task, measure the draws once, then for every model and repetition
generate a patch, label it with the hidden tests, score it on the draws and apply the gates.

python tools/cohort_inner.py ARGS.json
ARGS: {"orig","gold","work","out","vet","issue","pr_title","models":[model configs],"reps","seed","cap_usd","runner",
       "n_draws","scripted" (tests only: {"model name": [reply texts]}), "visible_override" (tests only)}
Money: one SpendGuard for the whole instance; each call is checked at its worst case first.  No call is retried.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gatekeeper_ext import b9_cohort, draws, gates  # noqa: E402
from gatekeeper_ext import testmut as T  # noqa: E402
from gatekeeper_lite import b9  # noqa: E402
from gatekeeper_lite.skill import Target  # noqa: E402


class RefreshingClient(b9_cohort.CohortClient):
    """CohortClient that refreshes its bearer token (they last about an hour) with GK_TOKEN_CMD when set."""
    _last = 0.0

    def complete(self, model, messages, max_tokens, temperature, seed):
        cmd = os.environ.get("GK_TOKEN_CMD")
        if cmd and time.time() - RefreshingClient._last > 1500:
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            if out.returncode == 0 and out.stdout.strip():
                os.environ[self.key_env] = out.stdout.strip()
                RefreshingClient._last = time.time()
        return super().complete(model, messages, max_tokens, temperature, seed)


def hidden_labels(orig_root, treated, test_files, classification, pythonpath, runner, work, tag):
    """Run the tests of the upstream fix's test files on the patched tree; plausible = every fail-to-pass and every
    pass-to-pass test passes."""
    patched = Path(work) / ("patched_" + tag)
    shutil.rmtree(patched, ignore_errors=True)
    shutil.copytree(orig_root, patched, ignore=shutil.ignore_patterns(".git"))
    for rel, src in treated.items():
        (patched / rel).write_text(src, encoding="utf-8")
    recs, err = T.run_tests(patched, runner, test_files, pythonpath, None, Path(work), "labels_" + tag)
    shutil.rmtree(patched, ignore_errors=True)
    if recs is None:
        return {"error": err}
    status = {"%s::%s" % (r["classname"], r["name"]): r["status"] for r in recs}
    f2p = sorted(k for k, v in classification.items() if v == "F->P")
    p2p = sorted(k for k, v in classification.items() if str(v).startswith("P->P"))
    f2p_fail = [k for k in f2p if status.get(k) != "passed"]
    p2p_fail = [k for k in p2p if status.get(k) != "passed"]
    return {"f2p_total": len(f2p), "f2p_failing": f2p_fail[:10], "p2p_total": len(p2p), "p2p_failing": p2p_fail[:10],
            "plausible": not f2p_fail and not p2p_fail}


def make_client(cfg, scripted):
    if scripted is not None:
        return b9.ScriptedFakeModel(list(scripted))
    base = cfg["base_url"].replace("{GCP_PROJECT}", os.environ.get("GCP_PROJECT", ""))
    return RefreshingClient(base, cfg["key_env"], cfg.get("extra", {}))


def run(a):
    t0 = time.time()
    orig, gold, work, out = Path(a["orig"]), Path(a["gold"]), Path(a["work"]), Path(a["out"])
    runner = a.get("runner", "pytest")
    res = {"name": a["vet"]["name"], "repo": a["vet"]["repo"], "status": "started", "models": [m["name"] for m in a["models"]], "attempts": []}
    try:
        manifest, instance = b9_cohort.build_instance(a["vet"], a.get("issue"), a.get("pr_title", ""))
        if a.get("visible_override"):
            instance["visible"] = a["visible_override"]
        (orig / "gk_target.json").write_text(json.dumps(manifest))
        res["instance"] = {"modules": manifest["modules"], "census": manifest["census_tests"], "pythonpath": manifest["pythonpath"],
                           "issue_provenance": instance["issue_provenance"], "visible": instance["visible"]["tests"] if "tests" in instance["visible"] else "custom",
                           "hidden_f2p": len(instance["hidden_f2p"]), "hidden_p2p": len(instance["hidden_p2p"])}
        base, why = draws.prepare_base(orig, gold, manifest["modules"], manifest["pythonpath"], runner, manifest["census_tests"], work / "base", a["seed"], a.get("n_draws", 200))
        if base is None:
            res.update(status="HARNESS_NOT_ELIGIBLE", harness=why)
            return res
        res["harness"] = dict(base["info"], deterministic=base["deterministic"])
        test_files = list(a["vet"].get("gold_test_files") or [])      # the fix's test files, present in the original snapshot
        guard = b9.SpendGuard(a["cap_usd"])
        target = Target.load(orig)
        for cfg in a["models"]:
            prices = {"input": cfg["prices_usd_per_mtok"]["input"], "output": cfg["prices_usd_per_mtok"]["output"]}
            for rep in range(a.get("reps", 2)):
                tag = "%s_r%d" % (cfg["name"], rep)
                client = make_client(cfg, (a.get("scripted") or {}).get(cfg["name"]) if a.get("scripted") is not None else None)
                budget = b9.Budget(5, cfg.get("max_output_tokens", 8000), 5)
                att = {"model": cfg["name"], "rep": rep, "tag": tag}
                try:
                    r, finish = b9_cohort.generate(target, instance, client, cfg["model_id"], budget, prices, a["seed"] + 100 * rep, guard)
                except Exception as exc:                          # a model or network error is a result, never a retry
                    att.update(status="GENERATION_ERROR", error=("%s: %s" % (type(exc).__name__, exc))[:300])
                    res["attempts"].append(att)
                    continue
                att.update(status=r.status, calls=r.calls, verdicts=[x.get("verdict") for x in r.attempts], tokens=r.tokens, cost_usd=r.cost_usd,
                           usage_missing=r.usage_missing, finish_reasons=finish, seconds=r.seconds, spent_usd_total=round(guard.spent_usd, 6))
                if r.status == "SUBMITTED":
                    att["files"] = sorted(r.treated)
                    lab = hidden_labels(orig, r.treated, test_files, a["vet"].get("classification") or {}, manifest["pythonpath"], runner, work, tag)
                    att["labels"] = lab
                    sc, err = draws.score_patch(base, orig, r.treated, manifest["pythonpath"], runner, work / "base", tag)
                    if sc is None:
                        att["scoring_error"] = err
                    else:
                        flags = sc["harm"]
                        att["draws"] = {"complete": sc["complete"], "missing": sc["missing"], "deterministic": sc["deterministic"], "harm": sum(flags),
                                        "help": sc["help"], "still_wrong": sc["still_wrong"], "h_hat": gates.h_hat(flags), "in_band": gates.band(flags),
                                        "acceptable": gates.acceptable(flags)}
                        att["gates"] = gates.decisions(flags, bool(lab.get("plausible")), sc["help"])
                res["attempts"].append(att)
        res["status"] = "FINISHED"
        res["spent_usd"] = round(guard.spent_usd, 6)
    except Exception as exc:
        res.update(status="ERROR", error=("%s: %s" % (type(exc).__name__, exc))[:500])
    finally:
        res["seconds"] = round(time.time() - t0, 1)
    return res


def main(path):
    a = json.loads(Path(path).read_text())
    res = run(a)
    Path(a["out"]).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res.get(k) for k in ("name", "status", "spent_usd", "error")}, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
