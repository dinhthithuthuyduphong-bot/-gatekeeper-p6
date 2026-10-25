# Study K — exploratory python-control transfer

This is an **explicitly retrospective follow-up**, not a new prospective study.
The frozen `none_identity` skill was applied to historical python-control
`fb5ebf6296079229705792cc508ad23d45e326aa`. The transformed module is AST-equivalent
to the same module in upstream fix `60aba3ab39cef2ac11c4bc08c2b08a9abd084205`.
No learned rule, gate threshold, or upstream test was edited.

See [RESULT_VI.md](RESULT_VI.md) and the raw result at
[results/local-20261025-clean/RESULT.md](results/local-20261025-clean/RESULT.md).
The complete selected 16-test FRD module is run for all three arms, three times.
The 15 baseline-passing tests form the regression census; the known failing
upstream `testNyquist` is the repair witness. No test is deselected or rewritten.

## Evidence boundaries

- Upstream `testNyquist` is a **no-exception smoke test**. Its provenance is
  strong; it does not assert numerical accuracy or plot quality.
- The separate draw oracle checks the analytic complex frequency response of
  `gain / (s*s + a*s + b)`. It is researcher-authored, not an upstream tier-1 test.
- `array_frequencies` and `default_frequencies` are two scopes of one repository,
  not two independent targets. The 300 draws and three repetitions are not
  independent repositories either.
- Two of the three rewritten comparison sites are reached by the declared
  scopes. `gangof4_plot` is unexercised. The result is neither full-repo safety
  nor admission for unrestricted use of the entire patch.
- The engine executes all 300 draws per scope for diagnostics. A stopping index
  is reported, but this run is **not** a measured production cost saving.
- Historical code is evaluated with a pinned compatibility environment from
  later years; this is not reconstruction of the original 2014 environment.
- Prior D/E/G/H data and Study I results are unchanged; B9 remains HOLD.

## Read-only audit

From the repository root with Python 3.12, without target dependencies:

```bash
python study_k/verify.py --results study_k/results/local-20261025-clean --output study-k-verified.json
```

This recomputes labels, exact generator draws/ordering, test counts, stopped
e-values, the complete two-cell e-Holm family, line reach and state-check results
from XML/JSONL. It fails on missing or contradictory evidence.

## Run again

Use GitHub Actions **Gatekeeper Study K zero-cost reproduction**, branch `main`.
It restores Python 3.8.20 with uv, compiles Matplotlib 2.2.5 with the declared
system headers, restores a checksum-pinned conda-forge Slycot binary, fetches
the exact source commit, and executes `study_k/run.py`. The result artifact is
**study-k-python-control**. No API key or paid provider is used.

The workflow records setup logs before reproduction, so setup failures are
visible in the artifact. It has `contents: read`; it never updates the repository.
This workflow has been parsed and its Python commands exercised locally; a new
GitHub-hosted run is still required after the user updates main.

Local Linux x86_64 reproduction requires a fresh CPython 3.8.20 environment,
the packages in `requirements-build.txt`, Matplotlib 2.2.5, and the Slycot binary
installed by `install_slycot.py`. Native dependencies are listed in the workflow.
Use a new output directory on every run:

```bash
python -u study_k/run.py --output study-k-new-run
```

## Search and installation history

[search_evidence/SEARCH_RESULT.md](search_evidence/SEARCH_RESULT.md) records
the additional unsuccessful searches and the independent Airflow revert lead.
`results/pilot_attempts/` preserves collection failure, missing-Slycot failures
and the first successful paired test. `results/environment_setup/` preserves
failed and successful installation attempts. The first complete measured run
in `results/local-20261025/` had stale duplicate Matplotlib distribution metadata;
the reported run is a full rerun in a fresh environment at
`results/local-20261025-clean/`. The outcome is the same. Neither run is discarded.

The license for the upstream source is retained in the full module headers in
`vendor/`; the test file is an unmodified byte-for-byte copy. Slycot is downloaded
from conda-forge under its upstream license; no compiled binary is distributed
in this repository or update ZIP.
