"""Study Q amendment Q-A1: re-run one instance exactly as tools/q_instance.py does, but KEEP what the frozen tool drops.

python tools/q_review_capture.py INSTANCE_ID VERIFIED.json POOL.jsonl.gz SEED MODELS.json OUT_DIR

tools/q_instance.py (frozen, unchanged) already scores patches with capture on, but stores only the per-category counts
(gatekeeper_ext.q_classify.summarise) and deletes its work directory.  This wrapper changes nothing in the pipeline; it
only intercepts two return values so that the following are written next to the usual Q_<id>.json:
  - classified.outcomes : every per-input outcome (source, index, original, fix, patch, patch_stable) of every patch;
  - inputs/g0.calls.json, inputs/g2.make_inputs.py : the G0 calls and the G2 generator the inputs came from;
  - patches/<sha>.diff : the text of every scored patch (also recoverable from POOL.jsonl.gz).
The model-written G2 generator is produced again, so it may differ from the cohort run; reproduction is checked against
the cohort record (research_closure/results/study_q/Q_RECORDS.jsonl.gz) by tools/q_review_items.py.
"""
import gzip
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import q_instance as QI  # noqa: E402
from gatekeeper_ext import fn_draws  # noqa: E402
from gatekeeper_ext import q_classify as QC  # noqa: E402


def install(out_dir):
    out = Path(out_dir)
    (out / "inputs").mkdir(parents=True, exist_ok=True)
    summarise, prepare = QC.summarise, fn_draws.prepare_fn_base

    def summarise_keep(outcomes):
        return dict(summarise(outcomes), outcomes=outcomes)

    def prepare_keep(*args, **kwargs):
        base, why = prepare(*args, **kwargs)
        if base is not None:
            for key, name in (("calls", "g0.calls.json"), ("gen", "g2.make_inputs.py")):
                if base.get(key) and Path(base[key]).is_file():
                    shutil.copy(base[key], out / "inputs" / name)
        return base, why

    QC.summarise = summarise_keep                 # q_instance calls QC.summarise (same module object)
    fn_draws.prepare_fn_base = prepare_keep       # q_instance imports fn_draws inside run(); attribute looked up at call time
    return summarise, prepare


def main(argv):
    iid, verified, pool_path, seed, models, out_dir = argv[:6]
    install(out_dir)
    rec = QI.run(iid, verified, pool_path, seed, models, out_dir)
    pdir = Path(out_dir) / "patches"
    pdir.mkdir(parents=True, exist_ok=True)
    wanted = {p["sha"] for p in rec.get("patches") or []}
    with gzip.open(pool_path, "rt") as f:
        for line in f:
            if ('"%s"' % iid) in line:
                p = json.loads(line)
                if p["instance_id"] == iid and p["sha"] in wanted and not (pdir / (p["sha"] + ".diff")).exists():
                    (pdir / (p["sha"] + ".diff")).write_text(p["patch"])
    print(json.dumps({k: rec.get(k) for k in ("instance_id", "status", "python", "error")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
