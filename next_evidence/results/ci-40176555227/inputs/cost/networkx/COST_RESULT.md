# Census-first cost: networkx

Exploratory, known target; no model call. All policies stop after a census veto.

| Policy | Total mean seconds | Census mean seconds | Mean paired draws |
|---|---:|---:|---:|
| census_only | 2.2862 | 2.1226 | 0 |
| census_then_full | 5.3116 | 2.1606 | 600 |
| census_then_gate | 4.9612 | 2.1365 | 380 |

Census-only does not certify a benefit margin or generator-wide harm rate. Timing comparisons are not equal-guarantee comparisons.
On SQLAlchemy the expected census veto should suppress all draw work. Differences among such arms are timing noise, not statistical power.
On NetworkX compare the extra cost of draw certification with census-only. Do not call a slower method a speedup.
Three repetitions on one machine/target are not independent repositories; download/install excluded. Raw logs, XML, JSONL and schedule retained.
