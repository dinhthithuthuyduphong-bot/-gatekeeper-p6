"""pytest plugin for the reach pass: python -m pytest -p gatekeeper_ext.reach_plugin ...
Environment: GK_REACH_TARGETS (json of [path, first_line]) and GK_REACH_OUT (output json)."""
import os

import pytest

from gatekeeper_ext.reach import ReachTracker, key_from_nodeid, load_targets

_tracker = [None]


def pytest_configure(config):
    _tracker[0] = ReachTracker(load_targets(os.environ["GK_REACH_TARGETS"]))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    _tracker[0].start(key_from_nodeid(item.nodeid))
    try:
        yield
    finally:
        _tracker[0].stop()


def pytest_sessionfinish(session, exitstatus):
    _tracker[0].dump(os.environ["GK_REACH_OUT"])
