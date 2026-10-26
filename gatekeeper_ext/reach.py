"""Which tests execute the edited code (harness v4: reach-filtered sampling).  Standard library only; Python 3.8.

A test is in the sampling scope only if, run unchanged at the original commit, it enters at least one function
that the fix edits.  Code objects are identified by (real file path, first line), so decorator-registered callbacks
and unpicklable receivers are not a problem (unlike the call replay of Study L gate G1).
"""
import json
import os
import sys


def load_targets(path):
    """JSON list of [real_path, first_line]; both the def line and the first decorator line are accepted."""
    return set((os.path.realpath(p), int(n)) for p, n in json.loads(open(path).read()))


def key_from_nodeid(nodeid):
    """pytest node id -> (junit-style classname, test function name without parameters)."""
    path, *rest = nodeid.split("::")
    mod = path[:-3].replace("\\", "/").replace("/", ".") if path.endswith(".py") else path
    return ".".join([mod] + rest[:-1]), rest[-1].split("[")[0]


class ReachTracker:
    def __init__(self, targets):
        self.targets, self.current, self.reached, self._real = set(targets), None, set(), {}

    def _profile(self, frame, event, arg):
        if event == "call" and self.current is not None:
            co = frame.f_code
            real = self._real.get(co.co_filename)
            if real is None:
                real = self._real[co.co_filename] = os.path.realpath(co.co_filename)
            if (real, co.co_firstlineno) in self.targets:
                self.reached.add(self.current)

    def start(self, key):
        self.current = key
        sys.setprofile(self._profile)

    def stop(self):
        sys.setprofile(None)
        self.current = None

    def dump(self, path):
        with open(path, "w") as fh:
            json.dump(sorted([list(k) for k in self.reached]), fh)
