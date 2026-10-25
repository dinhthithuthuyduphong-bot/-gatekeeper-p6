"""External observation plugin: records pytest phases and line reach, never edits tests."""
import json
import os
from pathlib import Path
import sys

import pytest

from next_evidence.site_coverage import site_report

_coverage=None
_out=None


def pytest_sessionstart(session):
    global _coverage, _out
    import coverage
    _out=Path(os.environ["GK_PROBE_OUTPUT"])
    _out.mkdir(parents=True,exist_ok=False)
    source=Path(os.environ["GK_PROBE_SOURCE"]).resolve()
    _coverage=coverage.Coverage(config_file=False,data_file=str(_out/"coverage.data"),
                                source=[str(source/"pydantic_settings")],branch=True)
    _coverage.start()
    _coverage.switch_context("collection")


def pytest_collection_finish(session):
    (_out/"inventory.json").write_text(json.dumps([item.nodeid for item in session.items],indent=2)+"\n")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    _coverage.switch_context(item.nodeid+"|setup")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    _coverage.switch_context(item.nodeid+"|call")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item):
    _coverage.switch_context(item.nodeid+"|teardown")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome=yield
    report=outcome.get_result()
    row={"nodeid":report.nodeid,"phase":report.when,"outcome":report.outcome,
         "wasxfail":getattr(report,"wasxfail",None),"seconds":report.duration}
    with (_out/"phases.jsonl").open("a") as log:log.write(json.dumps(row,allow_nan=False)+"\n")


def pytest_sessionfinish(session, exitstatus):
    if _coverage is None:return
    _coverage.stop();_coverage.save()
    source=Path(os.environ["GK_PROBE_SOURCE"]).resolve()
    import coverage
    sites=json.loads(os.environ["GK_PROBE_SITES"])
    report=site_report(_coverage.get_data(),source,sites,_out/"coverage.data",coverage.__version__)
    (_out/"site_coverage.json").write_text(json.dumps(report,indent=2)+"\n")
    module=sys.modules.get("pydantic_settings")
    receipt={"exitstatus":int(exitstatus),"loaded_module":getattr(module,"__file__",None),
             "source_root":str(source),"site_report_format":report["format"],
             "instrumentation":"coverage.py raw physical-line test-phase contexts; timings are instrumented, not performance benchmarks"}
    (_out/"SESSION.json").write_text(json.dumps(receipt,indent=2)+"\n")
