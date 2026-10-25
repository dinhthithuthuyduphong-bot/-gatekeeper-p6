# Pydantic-settings: baseline and dynamic reach

Status: **BASELINE_STABLE_ORACLE_REVIEW_PENDING**.
No treatment or model call. This is not a transfer result or a prospective admission.

| Repetition | Exit | Collected | Passed calls | Failed calls | Setup/teardown failures |
|---|---:|---:|---:|---:|---:|
| 1 | 0 | 1025 | 1021 | 0 | 0 |
| 2 | 0 | 1025 | 1021 | 0 | 0 |
| 3 | 0 | 1025 | 1021 | 0 | 0 |

| Candidate site | Reached in every baseline run | Tests reaching it in call phase (first run) |
|---|---|---:|
| pydantic_settings/sources/providers/cli.py:108 | True | 43 |
| pydantic_settings/sources/utils.py:385 | True | 33 |
| pydantic_settings/sources/utils.py:449 | False | 52 |

Reach does not establish that bool inputs occur or assertions cover the changed semantics. Send the complete artifact for oracle review. No treatment is authorized by a green baseline status. Timings include instrumentation.
