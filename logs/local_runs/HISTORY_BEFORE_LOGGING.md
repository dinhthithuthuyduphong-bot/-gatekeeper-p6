# Local runs before logging existed (written 1/11/2026)

Before `tools/local_run.py` existed (1/11/2026), the following were run locally in the agent's container and their output was **not
stored**; only this description remains. None of them produced a number reported in the paper: every reported number comes from a
GitHub Actions workflow and is recomputed by `tools/check_paper_numbers.py`. Runs that can be repeated are repeated through
`tools/local_run.py` (see INDEX.md).

| When | What | Purpose | Affects a reported number? |
|---|---|---|---|
| 30/10 – 1/11 | `python -m unittest discover -s tests` (many times) | regression check before commits | No (CI re-runs on push) |
| 30/10 – 1/11 | `python tools/check_paper_numbers.py` (many times) | every quoted number recomputed | No (submission check and paper build re-run it) |
| 31/10 | Study R2 pre-flight on psf/requests, pallets/flask and the standard library | crash test of the 10 new families on non-target code | No |
| 31/10 | Study S smoke tests on synthetic repositories `/tmp/fk`, `/tmp/fk2` | harness check before S, S-A1, S-A2 | No |
| 31/10 | `tools/library_census.py --dynamic` on the committed R2 census | first look at enabling edges; superseded by the workflow re-run (commit 7da8592) | No (workflow numbers reported) |
| 31/10 | theory checks C10 and C11 with few repetitions | development of the checks | No (workflow `Gatekeeper theory checks`) |
| 1/11 | `tools/market_analyze.py` on Study T results with the LLM-judge files | merge test; its output was committed once (690ad38 area) and later replaced by the workflow analysis | No (workflow re-ran the analysis) |
| 1/11 | `tools/rare_harm_study.py` into `/tmp/u_check` | preview of U-A1 (e-BH) before the workflow | No (workflow run, commit 8048fb7) |
| 1/11 | `tools/results_report.py` | generates `docs/paper/RESULTS_REPORT.md` from committed result files | Report only, regenerated from committed files |

**Re-run as Actions evidence (1/11):** workflow `Gatekeeper evidence of local tasks` (`tools/evidence_local_tasks.py`) re-runs, with a pass/fail condition, the R2 pre-flight (requests v2.32.3, flask 3.0.3, standard library), the Study S smoke test, `library_census --dynamic` (must equal the committed analysis), the Study U recomputation (must equal the committed result) and the results report (must equal the committed report). Unit tests and the paper's numbers are re-run by `Gatekeeper CI`. Theory checks have their own workflow.
