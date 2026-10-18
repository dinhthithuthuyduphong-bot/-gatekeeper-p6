"""pytest plugin: record which tests call the edited function(s) (baseline code only).

Enabled with  -p gatekeeper_lite.pytest_reach  and env GK_REACH_FUNCS (comma list),
GK_REACH_FILE (path suffix of the edited module) and GK_REACH_OUT (JSON output).
Uses plain hooks only, so it imports nothing from pytest.  Tracing covers setup, call
and teardown of each test (a conservative superset of reach).
"""
import json
import os
import sys

_FUNCS = {f for f in os.environ.get("GK_REACH_FUNCS", "").split(",") if f}
_FILE = os.environ.get("GK_REACH_FILE", "").replace("\\", "/")
_state = {"current": None, "reached": set(), "seen": set()}


def junit_id(nodeid: str) -> str:
    """'tests/test_x.py::Cls::test_a[p]' -> 'tests.test_x.Cls::test_a[p]' (JUnit style)."""
    parts = nodeid.split("::")
    module = parts[0][:-3] if parts[0].endswith(".py") else parts[0]
    module = module.replace("/", ".").replace("\\", ".")
    return ".".join([module] + parts[1:-1]) + "::" + parts[-1]


def _tracer(frame, event, arg):
    if event == "call" and _state["current"] is not None:
        code = frame.f_code
        if code.co_name in _FUNCS and code.co_filename.replace("\\", "/").endswith(_FILE):
            _state["reached"].add(_state["current"])
    return None


def pytest_runtest_setup(item):
    _state["current"] = junit_id(item.nodeid)
    _state["seen"].add(_state["current"])
    sys.settrace(_tracer)


def pytest_runtest_teardown(item, nextitem):
    sys.settrace(None)
    _state["current"] = None


def pytest_sessionfinish(session, exitstatus):
    out = os.environ.get("GK_REACH_OUT")
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump({"functions": sorted(_FUNCS), "file": _FILE,
                       "seen": len(_state["seen"]), "reached": sorted(_state["reached"])}, fh)
