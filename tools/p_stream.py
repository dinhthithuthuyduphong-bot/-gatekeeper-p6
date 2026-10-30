"""Study P, confirmatory cohort, streaming: every candidate goes straight through the stages, without waiting for the
other candidates (study_p/STUDY_P_PROTOCOL.md; gates are evaluated afterwards on the totals).

python tools/p_stream.py CANDIDATES.json OUT_DIR SHARD K MODELS.json [--timeout-vet S] [--timeout-fn S] [--timeout-gen S]

Per candidate (candidate i belongs to shard i mod K, frame order kept):
  P-S2  vet with tools/vet_target2.py (v2.1)                                   -> VETTING_<name>.json
  P-S3  if ELIGIBLE: function-level oracle; the light model writes the input generator ONCE; the generator code and
        its sha256 are stored before any patch exists                         -> FNPROBE_<name>.json
  P-GEN if usable: one patch per model (light, then strong), function-level scoring on the SAME stored generator
                                                                               -> COHORT_<name>.json
  summary                                                                      -> STREAM_<name>.json
Each stage runs in its own process group with a time limit; a stage that fails or times out ends that candidate and is
recorded, never retried, never replaced.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
TRIM = ("name", "repo", "pre", "gold", "changed_files", "gold_test_files", "gold_source_diff", "eligible_oracle", "eligible_sources",
        "classification", "verdict", "python")
MODELS = "vertex-gemini-flash,vertex-gemini-argon"
CAP_GEN_PER_INSTANCE = 1.0      # worst-case ceiling for both patches of one instance; the expected spend is about 0.05 USD
CAP_FN_PER_INSTANCE = 0.15      # as in feasibility step 2


def _run(cmd, timeout):
    from vet_dev import run_group
    try:
        p = run_group([sys.executable] + [str(c) for c in cmd], int(timeout), cwd=str(ROOT))
        return {"status": "FINISHED", "returncode": p.returncode, "tail": p.stdout[-1500:]}
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT"}


def first_usable(fnrec):
    funcs = sorted(fnrec.get("functions") or [], key=lambda f: (f.get("file", ""), f.get("qualname", "")))
    return next((f for f in funcs if f.get("usable") and f.get("generator_code")), None)


def process(cand, out, stages):
    """stages: object with vet(cand, out), fn(vetting, cand, out), gen(vetting, cand, fn_target, out).  Pure control flow."""
    s = {"name": cand["name"], "repo": cand["repo"], "pr": cand.get("pr"), "stage_reached": "P-S2"}
    v = stages.vet(cand, out)
    s["vet_verdict"] = (v or {}).get("verdict", "NO_RESULT")
    if not v or v.get("verdict") != "ELIGIBLE":
        return s
    s["stage_reached"] = "P-S3"
    fnrec = stages.fn(v, cand, out)
    s["fn_verdict"] = (fnrec or {}).get("verdict", "NO_RESULT")
    f = first_usable(fnrec or {})
    if f is None:
        return s
    target = {"file": f["file"], "qualname": f["qualname"], "generator_code": f["generator_code"],
              "generator_sha256": hashlib.sha256(f["generator_code"].encode()).hexdigest()}
    s.update(stage_reached="P-GEN", fn_target={k: target[k] for k in ("file", "qualname", "generator_sha256")})
    g = stages.gen(v, cand, target, out)
    inner = (g or {}).get("inner") or {}
    s["gen_status"] = inner.get("status") or (g or {}).get("status", "NO_RESULT")
    s["attempts"] = [{"model": a.get("model"), "status": a.get("status"), "plausible": (a.get("labels") or {}).get("plausible"),
                      "h_hat": (a.get("draws") or {}).get("h_hat"), "in_band": (a.get("draws") or {}).get("in_band")}
                     for a in inner.get("attempts", [])]
    return s


class RealStages:
    def __init__(self, models_path, t_vet=1500, t_fn=2400, t_gen=5400):
        self.models, self.t = models_path, (t_vet, t_fn, t_gen)

    def vet(self, cand, out):
        spec = Path(tempfile.mkdtemp()) / "spec.json"
        spec.write_text(json.dumps({k: v for k, v in cand.items() if k != "changed"}))
        r = _run([ROOT / "tools" / "vet_target2.py", spec, out], self.t[0])
        f = Path(out) / ("VETTING_%s.json" % cand["name"])
        return json.loads(f.read_text()) if f.exists() else {"verdict": "VET_" + r["status"]}

    def _records(self, vetting, cand, extra=None):
        rec = {k: vetting.get(k) for k in TRIM}
        rec.update(pr=cand["pr"], position=cand.get("position", 0), **(extra or {}))
        p = Path(tempfile.mkdtemp()) / "records.json"
        p.write_text(json.dumps([rec]))
        return p

    def fn(self, vetting, cand, out):
        r = _run([ROOT / "tools" / "fn_probe_llm.py", self._records(vetting, cand), cand["name"], out, self.models, CAP_FN_PER_INSTANCE], self.t[1])
        f = Path(out) / ("FNPROBE_%s.json" % cand["name"])
        return json.loads(f.read_text()) if f.exists() else {"verdict": "FN_" + r["status"]}

    def gen(self, vetting, cand, target, out):
        recs = self._records(vetting, cand, {"fn_target": target})
        r = _run([ROOT / "tools" / "cohort_instance.py", recs, cand["name"], out, self.models, MODELS, 1, CAP_GEN_PER_INSTANCE,
                  "study-p-cohort:", 200, "function"], self.t[2])
        f = Path(out) / ("COHORT_%s.json" % cand["name"])
        return json.loads(f.read_text()) if f.exists() else {"status": "GEN_" + r["status"]}


def main(argv):
    cands_path, out, shard, k, models = argv[:5]
    opt = lambda key, d: int(argv[argv.index(key) + 1]) if key in argv else d
    stages = RealStages(models, opt("--timeout-vet", 1500), opt("--timeout-fn", 2400), opt("--timeout-gen", 5400))
    cands = json.loads(Path(cands_path).read_text())
    for i, c in enumerate(cands):
        c.setdefault("position", i)
    mine = cands[int(shard)::int(k)]
    Path(out).mkdir(parents=True, exist_ok=True)
    for c in mine:
        s = process(c, out, stages)
        (Path(out) / ("STREAM_%s.json" % c["name"])).write_text(json.dumps(s, indent=1))
        print(json.dumps({x: s.get(x) for x in ("name", "stage_reached", "vet_verdict", "fn_verdict", "gen_status")}), flush=True)
    (Path(out) / ("SHARD_%s_SUMMARY.json" % shard)).write_text(json.dumps({"shard": int(shard), "of": int(k), "candidates": len(mine)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
