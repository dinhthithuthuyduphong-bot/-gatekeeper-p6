# I2_networkx — exploratory reproduction

Status: **VERIFIED_EXPLORATORY**. Model calls: **0**. B9 remains HOLD.

This is selected-module census plus retrospective/diagnostic evidence, not a new pre-registered confirmatory study.

Upstream: `585bb3ee251ab681e7725c07e4e8a569a0e511d5`; Python: `3.8.20`.

| Arm / group | Passed | Failure | Error | Skip | Repetitions |
|---|---:|---:|---:|---:|---:|
| baseline / census | 54 | 0 | 0 | 0 | 3 |
| baseline / witness | 0 | 0 | 1 | 0 | 3 |
| treated / census | 54 | 0 | 0 | 0 | 3 |
| treated / witness | 1 | 0 | 0 | 0 | 3 |
| gold / census | 54 | 0 | 0 | 0 | 3 |
| gold / witness | 1 | 0 | 0 | 0 | 3 |

Persistent census regressions: **0**. Resolved upstream witnesses: **1**.

A Nose witness 'error' is a target-call ValueError, not an import/setup failure; its full traceback is retained.

| Scope | Raw sequential decision | Draws to stop | Full help / tie / hurt |
|---|---|---:|---|
| given_positions | ADMIT | 80 | 300 / 0 / 0 |
| default_positions | UNDECIDED | 300 | 0 / 300 / 0 |

Any census regression vetoes admission for the whole target. See aggregate output for the four-cell family.

Raw evidence: RESULT.json, PRE_EXECUTION.json, every .log/.xml, skill.patch, and draws.jsonl.
Draw adapters are researcher-authored. The separate upstream witness/census tests are unchanged.
