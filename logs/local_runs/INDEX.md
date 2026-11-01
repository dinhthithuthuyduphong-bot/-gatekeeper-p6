# Local runs

Every local run made through `tools/local_run.py`; each row links its full log.

| UTC start | Name | Command | Exit | Seconds | HEAD | Log |
|---|---|---|---|---|---|---|
| 2026-11-01 03:52 | unit-tests | `python3 -W ignore -m unittest discover -s tests -q` | 0 | 73.0 | 61c4143 | [log](20261101T035203Z_unit-tests.log) |
| 2026-11-01 03:53 | paper-numbers | `python3 tools/check_paper_numbers.py` | 0 | 0.3 | bd63a42 | [log](20261101T035319Z_paper-numbers.log) |
