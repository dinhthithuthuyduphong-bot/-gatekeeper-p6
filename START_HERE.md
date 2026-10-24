# Study I: audited GitHub CI evidence

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
