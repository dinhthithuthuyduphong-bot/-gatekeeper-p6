# Study V: retirement under a real environment change (pre-registered; no trial of this study has run)

**Question (scorecard S13, roadmap D5).** Gatekeeper's certificate holds for the environment it was earned in. When the environment
changes, the paper's rule retires every certificate whose fingerprint changed and re-certifies in a new epoch, at a fresh share of
the error budget (ledger, epoch factor 6/(π²(k+1)²)). Does a real change of environment flip the harm of admitted cells, does
retirement catch every flip, and what does re-certification cost?

**Environment change.** Study T ran on CPython 3.12 with the dependency versions resolved on its trial day. Study V re-runs the
same 60 projects, same release, same census cells, same harness (T-A1, T-A3 memory cap, T2-A2 process groups, T2-A3 process cap)
and the same seeds and numbers of draws (200 per stream), on **CPython 3.13**, with dependencies resolved on the day of the run.
Each package's fingerprint is recorded: Python version and `pip freeze` of its trial environment.

**Fingerprint policies compared.**
- **F0 (no retirement):** Study T's decisions are kept in the new environment.
- **F1 (the paper's rule):** a changed fingerprint retires the certificate; the cell is re-certified in epoch 1 on Study V's gate
  draws, at the epoch-1 share α·6/(4π²) of the budget.

**Accounting fixed here.** Because Study T's decisions used the whole α (one epoch), Study T is re-analysed at its epoch-0 share
α·6/π², so that epochs 0 and 1 together spend at most α; both versions of Study T's decisions are reported.

**Measures (statistics first).** Usable cells in both environments; cells whose ground truth (reference draws, η = 5%) differs
between the environments, in each direction; among cells Gatekeeper admitted in Study T, the number harmful under 3.13 (what F0
would have kept); under F1, harmful cells re-admitted in epoch 1, safe cells kept, and draws used; packages whose fingerprint
changed.

**Win criteria (fixed here).**
- **V-W1:** under F1, no cell that is harmful under 3.13 is admitted in epoch 1.
- **V-W2:** every cell admitted in Study T that is harmful under 3.13 is retired by F1 (its fingerprint changed).
- **V-W3 (reported, no threshold):** the cost of re-certification, in draws per cell, against always-retest.
If no ground-truth flip occurs, this is reported as such: on this change, retirement costs the re-certification and buys nothing,
which is evidence for the fingerprint granularity question, not for the rule.
