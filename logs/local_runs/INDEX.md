# Local runs

Every local run made through `tools/local_run.py`; each row links its full log.

| UTC start | Name | Command | Exit | Seconds | HEAD | Log |
|---|---|---|---|---|---|---|
| 2026-11-01 03:52 | unit-tests | `python3 -W ignore -m unittest discover -s tests -q` | 0 | 73.0 | 61c4143 | [log](20261101T035203Z_unit-tests.log) |
| 2026-11-01 03:53 | paper-numbers | `python3 tools/check_paper_numbers.py` | 0 | 0.3 | bd63a42 | [log](20261101T035319Z_paper-numbers.log) |
| 2026-11-01 03:53 | results-report | `python3 tools/results_report.py` | 0 | 0.0 | c2e29ab | [log](20261101T035323Z_results-report.log) |
| 2026-11-01 03:53 | todo-rule-check | `python3 -c print(open('docs/PAPER_TODO.md').read().count('local_run.py'))` | 0 | 0.0 | 148fd2e | [log](20261101T035336Z_todo-rule-check.log) |
