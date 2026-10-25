"""Record real calls to the functions a fix edited, while the repository's own tests run.

python -m gatekeeper_ext.record_run TARGETS.json OUT.json (pytest|unittest) [runner args...]

TARGETS.json: list of {"module", "qualname", "file"}.  Each function is wrapped BEFORE the tests are
imported; every distinct call (positional and keyword arguments, pickled before the call) is stored.
Calls through a name bound earlier than the wrapper (e.g. `from m import f` done at import time of an
earlier module) are not seen; functions with no recorded call are reported and dropped by the caller.
Compatible with Python 3.8.
"""
import base64
import functools
import hashlib
import importlib
import inspect
import json
import pickle
import sys
import threading

MAX_CALLS = 300
MAX_BLOB = 200000
_state = threading.local()


def _wrap(fn, entry):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        if not getattr(_state, "busy", False) and len(entry["calls"]) < MAX_CALLS:
            _state.busy = True
            try:
                blob = pickle.dumps((a, k), protocol=4)       # copy BEFORE the call can mutate arguments
                if len(blob) <= MAX_BLOB:
                    digest = hashlib.sha1(blob).hexdigest()
                    if digest not in entry["_seen"]:
                        entry["_seen"].add(digest)
                        entry["calls"].append(base64.b64encode(blob).decode("ascii"))
                        entry["shape"].append([len(a), sorted(k)])
                else:
                    entry["unpicklable"] += 1
            except Exception:
                entry["unpicklable"] += 1
            finally:
                _state.busy = False
        return fn(*a, **k)
    return wrapper


def install(targets):
    entries = []
    for t in targets:
        entry = {"module": t["module"], "qualname": t["qualname"], "file": t["file"], "calls": [], "shape": [],
                 "skip_first": False, "note": None, "unpicklable": 0, "_seen": set()}
        entries.append(entry)
        try:
            parent = importlib.import_module(t["module"])
            parts = t["qualname"].split(".")
            for p in parts[:-1]:
                parent = getattr(parent, p)
            raw = vars(parent).get(parts[-1])
        except Exception as exc:
            entry["note"] = "import failed: %s" % type(exc).__name__
            continue
        if raw is None:
            entry["note"] = "attribute not found"
        elif isinstance(raw, (staticmethod, classmethod)):
            entry["note"] = "static/class method (not supported)"
        elif not inspect.isfunction(raw):
            entry["note"] = "not a plain function"
        elif inspect.isgeneratorfunction(raw) or inspect.iscoroutinefunction(raw) or inspect.isasyncgenfunction(raw):
            entry["note"] = "generator/coroutine (not supported)"
        else:
            try:
                first = next(iter(inspect.signature(raw).parameters), "")
            except (TypeError, ValueError):
                first = ""
            entry["skip_first"] = first in ("self", "cls")
            setattr(parent, parts[-1], _wrap(raw, entry))
    return entries


def main(argv):
    targets = json.loads(open(argv[1]).read())
    out_path, runner, rest = argv[2], argv[3], argv[4:]
    entries = install(targets)
    if runner == "pytest":
        import pytest
        rc = int(pytest.main(rest))
    else:
        import unittest
        prog = unittest.main(module=None, argv=["unittest"] + rest, exit=False)
        rc = 0 if prog.result.wasSuccessful() else 1
    for e in entries:
        e.pop("_seen", None)
    with open(out_path, "w") as fh:
        json.dump({"functions": entries, "runner_exit": rc}, fh)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
