# Search ledger — 25/10/2026

Convenience search, retrospective where historical fixes/reverts were inspected.
No sampling probability or population coverage is claimed. All new runtime
measurements in this follow-up concern python-control, not the static candidates.

| Candidate | Inspected snapshot | Exact `none_identity` production matches | Decision |
|---|---|---:|---|
| pudo/dataset | SHA in `CURRENT_SCREEN.json` | 0 | NO_MATCH |
| thp/minidb | SHA in `CURRENT_SCREEN.json` | 0 | One match is in top-level `example.py`, not the library; not a tier-1 target |
| kvesteri/sqlalchemy-continuum | Current pin, 1.3.13, 1.1.1 | 0 at each pin | NO_MATCH |
| coleifer/sqlite-web | SHA in `CURRENT_SCREEN.json` | 0 | NO_MATCH |
| kayak/pypika | SHA in `CURRENT_SCREEN.json` | 0 | NO_MATCH |
| encode/orm | SHA in `CURRENT_SCREEN.json` | 0 | NO_MATCH |
| tortoise/tortoise-orm | SHA in `CURRENT_SCREEN.json` | 0 | NO_MATCH |
| pudo/normality | SHA in `CURRENT_SCREEN.json` | 0 | NO_MATCH |
| sqlobject/sqlobject | Current pin, 3.0.0 | 0 at each pin | NO_MATCH |
| python-gino/gino | SHA in `python-gino__gino.scan.json` | 0 | NO_MATCH |
| marshmallow-code/marshmallow-sqlalchemy | SHA in its scan JSON | 0 | NO_MATCH |

Eleven repositories and fourteen snapshots were inspected in this follow-up.
The original eight-repository script included a top-level example because its
directory filter only excluded `examples/`. The one minidb site is retained in
raw output and explicitly reclassified here; it is not a production match.
These results do not establish correctness, safety or failed transfer: there
was no applicable production edit. No tests or treatment were run on them.
`scan_current.executed.py.txt` is the exact archived scratch script, with its
original local paths, not the portable reproduction entry point.

## Independent harmful-history lead: Apache Airflow

[PR 6109](https://github.com/apache/airflow/pull/6109) changed two SQLAlchemy
relationship comparisons from `== None` to `is None` in `clean_perms`.
[PR 6222](https://github.com/apache/airflow/pull/6222) reverted that change;
the upstream author explicitly reported that the query was broken. The patches
are exact instances of the skill's transformation and inverse. Primary PR JSON
and both file diffs are retained here.

This is stronger provenance than a researcher inventing an unwanted behavior,
but **not a newly reproduced tier-1 harmful test**: no failing upstream assertion
was executed here. The reviewed `tests/www/test_security.py` at the pre-revert
revision has no dedicated `clean_perms` assertion. Do not count Airflow as a
third verified harmful target or an admission outcome. It remains a lead for
an unchanged upstream test plus a runnable historical environment.

The already measured SQLAlchemy harmful target and NetworkX beneficial target
remain in Study I. The new verified beneficial target is python-control in
Study K. Exposed python-control and Airflow are recorded in Study J's exclusion
ledger so these known outcomes cannot be relabeled as fresh prospective evidence.
