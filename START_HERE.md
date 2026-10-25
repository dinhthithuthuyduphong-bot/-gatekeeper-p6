# Start here — zero-cost closure update, 24 October 2026

**Latest prepared package, 25/10/2026:** use [next GitHub run instructions](next_evidence/RUN_ON_GITHUB_VI.md)
and [current source findings/status](next_evidence/STATUS_AND_SCAN_VI.md).
Run **Gatekeeper next evidence - zero-cost**, optionally enabling `run_cost`.
The new scripts/tests are prepared but **not executed locally**. Earlier PASS
counts below refer to earlier packages, not validation of this follow-up.
Return the `next-evidence-return-a1` artifact (latest attempt suffix). Paid B9 remains HOLD.

**25/10/2026 — zero-cost follow-up:** [python-control result](study_k/RESULT_VI.md), [reproduce / raw audit](study_k/README.md). A retrospective beneficial transfer was reproduced; B9 remains HOLD. See [cumulative update instructions](research_closure/UPDATE_MAIN.md).


Current result and open research questions: [research_closure/RESULT.md](research_closure/RESULT.md).
Upload/run instructions: [research_closure/UPDATE_MAIN.md](research_closure/UPDATE_MAIN.md).
Run **Gatekeeper zero-cost closure audit** on main after uploading this update.
The local audit passes 125 tests; this statement is not a new GitHub run receipt.
B9 remains HOLD. Study J remains BLOCKED. No paid provider call is part of this update.

## Historical instructions for the earlier Study I evidence-only upload

Run: 40084717332; commit: 5292b6a16ab4e68a62c24032e44c2d99b327498e.
Copy CONTENTS of main_update/ into the existing repository root if you want
to archive this run on main. Only study_i/results/ci-40084717332/ is added.
No code, workflow, frozen study, original ZIP or old result is changed.

Read Study_I_CI_Result_40084717332.md inside that new result directory.
All 70 raw target result files and the original verified artifact are retained
byte-for-byte. Old bootstrap/local logs inherited from root evidence/ are
excluded; no test or draw from this CI run is discarded.

From the repository root, recheck without rerunning targets or models:

```bash
python3.12 study_i/verify.py --results study_i/results/ci-40084717332/inputs --output out-study-i-ci-recheck
```

B9: HOLD. No paid model calls. Evidence remains retrospective/exploratory.
