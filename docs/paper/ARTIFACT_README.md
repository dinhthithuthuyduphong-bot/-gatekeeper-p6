# Artifact: Scope before Reuse: Risk-Controlled Admission of Reusable Code Changes

Anonymous artifact for double-blind review. Links to the original repository are replaced by `ANONYMOUS/gatekeeper-artifact`; the
git history (author names) is not included.

## Requirements
Python 3.12 (standard library only for the core). Studies that call models or Docker need credentials and are run through the
workflows in `.github/workflows/`; their results and raw records are included, so no model call is needed to check the paper.

## Check the paper in four commands (no network, no cost)
```bash
python -m unittest discover -s tests
python tools/theory_checks.py out_theory --reps 2000
python tools/check_paper_numbers.py
for s in study_d study_e study_g study_h study_q; do python tools/freeze_study.py verify $s; done
```
1. The unit tests cover the pipeline, the e-processes and ledger, the execution rule, and the tools used by the studies.
2. `theory_checks.py` reproduces the numerical checks of every theoretical statement (C1–C11, including the exact decision rule of Studies D–H); the output equals
   `research_closure/results/theory/THEORY_CHECKS.json`.
3. `check_paper_numbers.py` recomputes every number quoted in the Evaluation section from the committed result files.
4. The freeze check shows that each study's protocol, configuration and tools are byte-identical to what was hashed before any outcome
   was seen. (Study P is verified at its freeze commit; see `EVIDENCE_LEDGER.md`.)

## Where things are
| Paper | Artifact |
|---|---|
| Problem, Theory (Section 3, 5) | `docs/paper/latex/sections/{problem,theory}.tex`, derivations in `docs/paper/THEORY.md` |
| Gatekeeper (Sections 4, 6) | `gatekeeper_lite/` (pipeline), `gatekeeper_ext/` (oracles, gates, contract classifier, execution rule) |
| RQ1 phase diagram, Study H | `tools/gate_phase_diagram.py`, `study_h/results/` |
| RQ2 skill reuse (Studies D, E, G) | `study_{d,e,g}/` (protocol, FREEZE.json, results) |
| RQ3 LLM patches (Study P, RQ5) | `study_p/`, `research_closure/results/study_p/`, `research_closure/results/rq5/` |
| RQ4 SWE-bench Verified (Study Q, manual review) | `study_q/`, `research_closure/results/study_q/` (raw records `Q_RECORDS.jsonl.gz`, `qa1/`) |
| Library-level control, simulation (Section 7.2) | `tools/library_simulation.py`, `research_closure/results/library_sim/` |
| Twelve-family library census (Study R2, Table 2) | `gatekeeper_ext/skill_library.py`, `study_r2/`, `tools/library_census.py`, `research_closure/results/study_r2/` |
| Real compositions (Study S) | `study_s/` (protocol, amendments S-A1–S-A3), `tools/composition_study.py`, `research_closure/results/study_s/` |
| Execution rule, library ledger, conformance labels | `gatekeeper_ext/{execution,ledger,conformance}.py`; audit `docs/paper/THEORY_CODE_AUDIT.md` |
| Evidence ledger (runs, commits) | `EVIDENCE_LEDGER.md` |
