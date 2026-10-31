"""Before freezing Study Q: every file of study_q and every tool and document it depends on go into extra_tracked.
python tools/q_prepare_freeze.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ["tools/" + t for t in ("q_instance.py", "q_probe_inner.py", "q_analyze.py", "q_f0.py", "q_f2.py", "q_prepare_freeze.py", "fn_probe.py",
                                "fn_probe_inner.py", "fn_probe_llm.py", "cohort_inner.py", "p_analyze.py", "p_thresholds.py", "freeze_doctor.py", "repo_hygiene.py")]
TOOLS += ["gatekeeper_ext/" + m for m in ("q_classify.py", "fn_draws.py", "fn_inputs.py", "fn_llm_gen.py", "b9_cohort.py", "usage.py", "gates.py")]
DOCS = ["research_closure/pilot/models.json", "research_closure/results/STUDY_Q_DRAFT.md", "research_closure/results/study_q/QF1_RESULT.json",
        "research_closure/results/study_q/QF2_SUMMARY.json", "research_closure/results/rq5/RQ5_RESULT.md"]
REQUIRED = ["study_q/evidence/POOL.jsonl.gz", "study_q/evidence/VERIFIED.json"]


def prepare(root=ROOT):
    root = Path(root)
    p = root / "study_q" / "config_study_q.json"
    cfg = json.loads(p.read_text())
    if cfg.get("status") != "DRAFT":
        raise SystemExit("study_q is %r, not DRAFT" % cfg.get("status"))
    missing = [t for t in TOOLS + DOCS + REQUIRED if not (root / t).is_file()]
    if missing:
        raise SystemExit("REFUSED: missing files: %s" % missing)
    own = sorted(f.relative_to(root).as_posix() for f in (root / "study_q").rglob("*") if f.is_file() and f.name != "FREEZE.json")
    cfg["extra_tracked"] = sorted(set(TOOLS + DOCS + own))
    p.write_text(json.dumps(cfg, indent=2))
    return cfg["extra_tracked"]


if __name__ == "__main__":
    print(len(prepare()), "paths in extra_tracked")
