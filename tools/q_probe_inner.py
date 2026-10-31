"""Study Q inner runner: tools/fn_probe_inner.py (Study P, frozen, imported unchanged) plus ONE extra field on every
raised exception: whether it was raised by an explicit `raise` statement in the project's own code (Python Language
Reference, "The raise statement"; a checked precondition in the sense of design by contract, Meyer 1992) or arose
incidentally (inside the runtime or a library, e.g. IndexError while subscripting).
Outcome of an exception: ["exc", type, message, "explicit" | "incidental"].
python q_probe_inner.py ARGS.json   (same arguments as fn_probe_inner.py)"""
import json
import linecache
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fn_probe_inner as BASE  # noqa: E402

_ROOT = [None]


def origin(exc, root):
    """'explicit' when the innermost frame is in the snapshot (not a dependency inside it) and its line is a raise."""
    tb = exc.__traceback__
    last = None
    while tb is not None:
        last = tb
        tb = tb.tb_next
    if last is None or not root:
        return "incidental"
    fn = os.path.realpath(last.tb_frame.f_code.co_filename)
    inside = fn.startswith(os.path.realpath(root) + os.sep) and "site-packages" not in fn
    line = linecache.getline(last.tb_frame.f_code.co_filename, last.tb_lineno).strip()
    return "explicit" if inside and line.startswith("raise") else "incidental"


_BASE_RUN_CALLS = BASE.run_calls


def run_calls(items, resolve, timeout):
    outcomes = []
    for it in items:
        captured = []

        def resolve_wrapped(receiver, _r=resolve):
            fn = _r(receiver)

            def call(*a, **k):
                try:
                    return fn(*a, **k)
                except BaseException as exc:
                    captured.append(origin(exc, _ROOT[0]))
                    raise
            return call
        out = _BASE_RUN_CALLS([it], resolve_wrapped, timeout)[0]
        if out and out[0] == "exc":
            out = out + [captured[-1] if captured else "incidental"]
        outcomes.append(out)
    return outcomes


BASE.run_calls = run_calls


def main(path):
    _ROOT[0] = json.loads(Path(path).read_text()).get("root")
    return BASE.main(path)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
