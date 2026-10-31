"""Before freezing Study P: put EVERY file of study_p and every tool and document the study depends on into extra_tracked
(the lesson of Study M, whose gates were not hashed).  Refuses if a listed tool is missing.  study_p must be DRAFT.
python tools/p_prepare_freeze.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ["tools/" + t for t in (
    "discover_m_candidates.py", "discover_n_continue.py", "discover_p_extend.py", "n_assemble.py", "p_assemble_ext.py", "p_frames.py",
    "split_candidates.py", "check_track.py", "vet_target.py", "vet_target2.py", "vet_dev.py", "vet_slice.py", "n_s3_check.py",
    "fn_probe.py", "fn_probe_inner.py", "fn_probe_llm.py", "cohort_instance.py", "cohort_inner.py", "p_stream.py", "p_analyze.py",
    "p_thresholds.py", "pilot_summary.py", "pilot_select.py", "rq3_target.py", "rq3_oracle_inner.py", "rq3_summary.py",
    "freeze_doctor.py", "repo_hygiene.py", "fetch_real_targets.py")] + ["gatekeeper_ext/" + m for m in (
    "fn_inputs.py", "fn_llm_gen.py", "fn_draws.py", "gates.py", "issue_fetch.py", "b9_cohort.py", "usage.py", "draws.py", "testmut.py", "mutants.py")]
DOCS = ["research_closure/results/STUDY_P_PLAN.md", "research_closure/results/ALIGNMENT_WITH_FSE.md", "research_closure/results/RQ3_PLAN.md",
        "research_closure/pilot/models.json", "research_closure/pilot/DEV_FN.json", "research_closure/pilot/PP0_RESULT.json"]


def prepare(root=ROOT):
    root = Path(root)
    p = root / "study_p" / "config_study_p.json"
    cfg = json.loads(p.read_text())
    if cfg.get("status") != "DRAFT":
        raise SystemExit("study_p is %r, not DRAFT" % cfg.get("status"))
    missing = [t for t in TOOLS + DOCS if not (root / t).is_file()]
    if missing:
        raise SystemExit("REFUSED: missing files: %s" % missing)
    own = sorted(f.relative_to(root).as_posix() for f in (root / "study_p").rglob("*") if f.is_file() and f.name != "FREEZE.json")
    cfg["extra_tracked"] = sorted(set(TOOLS + DOCS + own))
    p.write_text(json.dumps(cfg, indent=2))
    return cfg["extra_tracked"]


if __name__ == "__main__":
    print(len(prepare()), "paths in extra_tracked")
