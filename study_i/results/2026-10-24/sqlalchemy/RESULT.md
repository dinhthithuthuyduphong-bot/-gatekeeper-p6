# I1_sqlalchemy — exploratory reproduction

Status: **VERIFIED_EXPLORATORY**. Model calls: **0**. B9 remains HOLD.

This is selected-module census plus retrospective/diagnostic evidence, not a new pre-registered confirmatory study.

Upstream: `10f4d1e2d706a7722ca78e79ce05b00333a7aa5b`; Python: `3.12.14`.

| Arm / group | Passed | Failure | Error | Skip | Repetitions |
|---|---:|---:|---:|---:|---:|
| baseline / census | 1552 | 0 | 0 | 1 | 3 |
| treated / census | 1543 | 9 | 0 | 1 | 3 |

Persistent census regressions: **9**. Resolved upstream witnesses: **0**.

A Nose witness 'error' is a target-call ValueError, not an import/setup failure; its full traceback is retained.

| Scope | Raw sequential decision | Draws to stop | Full help / tie / hurt |
|---|---|---:|---|
| null_semantics | REJECT_HARM | 3 | 0 / 69 / 231 |
| plain_queries | UNDECIDED | 300 | 0 / 300 / 0 |

Any census regression vetoes admission for the whole target. See aggregate output for the four-cell family.

Raw evidence: RESULT.json, PRE_EXECUTION.json, every .log/.xml, skill.patch, and draws.jsonl.
Draw adapters are researcher-authored. The separate upstream witness/census tests are unchanged.
