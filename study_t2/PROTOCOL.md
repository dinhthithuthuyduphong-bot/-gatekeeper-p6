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
