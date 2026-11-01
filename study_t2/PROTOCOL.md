# Study T2: confirmatory replication of Study T on new targets (written before any census or trial of T2)

**Why.** Study T had 11 harmful Ruff cells, so "0 of 11 admitted" bounds the false-admission rate only below about 26% (Wilson).
Two of its best results were analysed post hoc (B6-strong, T-A5; e-BH screening, U-A1). T2 repeats Study T on targets nobody has
looked at, with those analyses **pre-registered**.

**Targets.** The same selection rule as Study T (`study_t/PROTOCOL.md` §2, same snapshot of the ranking committed in
`research_closure/results/study_t/TOP_PYPI_SNAPSHOT.json`), continued past Study T's 60 targets: qualifying projects number 61 to
200 (140 projects).

**Unchanged from Study T:**
- skills (Ruff 0.17.3 autofix rules and the twelve R2 families);
- harness (S-A5, with the 2 GB memory cap of T-A3 for every package);
- streams (gate seed 1, reference seed 2, 200 inputs);
- η = 5%, α = 0.1;
- ground truth;
- fixed-sample size recomputed from K;
- LLM judge (T-A2 prompt, cap 6 USD);
- B6-R.

**Pre-registered here:**
- **B6-strong (T-A5 definition):** sources are the other packages of Study T and T2 where the rule was tried.
- **G-FDR:** same e-values, e-BH at q = 0.1.
- **Win criteria** (Ruff cells; Study T's W1–W4 apply unchanged):
  - **T2-1:** G admits at most ⌈α·H⌉ harmful cells and fewer than B6-strong, B6-R, LJ and U.
  - **T2-2:** G retains at least as many safe cells as Ruff's safe label.
  - **T2-3:** pooled over T and T2, the Wilson upper bound of G's harmful-admission rate is below the lower bound of B6-strong's.

**Results** in `research_closure/results/study_t2/`; Study T's files are not touched.

## T2-A1 (after the census, before any trial; the census has no outcome)
**What the census showed (sizes only).** 140 targets, 6,839 cells (6,459 Ruff, 380 R2), 277 skills.

**Fairness correction.** With K = 6,839 the fixed-sample test needs n_FS = ⌈log(α/K)/log(1−η)⌉ = 218 draws to certify zero harm,
more than the 200 draws per stream of Study T, so FS could never admit. Both streams therefore get **240** inputs per function
(gate and reference). B8 = no change in all gate draws (up to 240). Gatekeeper's budget is 240 draws. Everything else is as in the
protocol.

## T2-A2 (after the trials of shards 0–18 were recorded, before shard 19 was re-run; no outcome of shard 19 was seen)

**Incident.** Shard 19 (colorama, docstring-parser, joblib, anthropic, deprecated, sqlparse, python-docx) was shut down by the
runner after 70 minutes inside joblib, despite the T-A3 memory cap; no artifact was uploaded, so no outcome of this shard exists.

**Cause (environmental, found by a unit test, `tests/test_run_group.py`).** Processes started by the target code (joblib starts
worker pools) outlived the inner process. They held its output pipes, so each such call lasted until the timeout (120 + 2n s), and
they were never killed, so they accumulated over hundreds of calls until the runner died.

**Change.** The inner process runs in its own process group, and the whole group is killed when the call ends or times out
(`composition_study._run_group`). The timeout behaviour, and therefore every outcome, is exactly that of `subprocess.run`: a call
whose leftover processes hold the pipes still ends as PROCESS_TIMEOUT. Only the clean-up is new. Shard 19 is re-run with one
package per runner (`--only`), so a runner failure can lose at most one package, and each package's free disk and memory are logged.
