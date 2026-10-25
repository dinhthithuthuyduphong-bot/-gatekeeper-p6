# Census-first cost: sqlalchemy

Exploratory, known target; no model call. All policies stop after a census veto.

| Policy | Total mean seconds | Census mean seconds | Mean paired draws |
|---|---:|---:|---:|
| census_only | 25.4281 | 24.8929 | 0 |
| census_then_full | 25.0363 | 24.5084 | 0 |
| census_then_gate | 24.9399 | 24.4135 | 0 |

Census-only does not certify a benefit margin or generator-wide harm rate. Timing comparisons are not equal-guarantee comparisons.
On SQLAlchemy the expected census veto should suppress all draw work. Differences among such arms are timing noise, not statistical power.
On NetworkX compare the extra cost of draw certification with census-only. Do not call a slower method a speedup.
Three repetitions on one machine/target are not independent repositories; download/install excluded. Raw logs, XML, JSONL and schedule retained.
