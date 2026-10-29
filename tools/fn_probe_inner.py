"""Study P (development): call ONE edited function on a list of inputs inside ONE snapshot; runs inside the instance's
virtual environment, in a fresh process per snapshot (no module cache shared between original, fix and patch).

python tools/fn_probe_inner.py ARGS.json
ARGS: {"root", "pythonpath": [...], "file", "qualname", "mode": "generate" | "run", "n", "seed", "calls" (path), "out" (path),
       "timeout" (seconds per call)}
generate: import the function from this snapshot and write the inputs (gatekeeper_ext.fn_inputs) to "calls".
run:      run every input and write one canonical outcome per input: ["ok", type, repr] or ["exc", type, message].
Memory addresses are masked; reprs are truncated.  Each call has a time limit; a call over the limit is ["timeout"].
"""
import asyncio
import importlib.util
import inspect
import json
import os
import re
import signal
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
ADDR = re.compile(r"0x[0-9a-fA-F]+")


class CallTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise CallTimeout()


def canonical(value):
    try:
        if inspect.isgenerator(value) or type(value).__name__ in ("map", "filter", "zip"):
            value = list(__import__("itertools").islice(value, 50))
        text = repr(value)
    except Exception as exc:                                     # a repr that raises is itself an outcome
        text = "<repr raised %s>" % type(exc).__name__
    return ["ok", type(value).__name__, ADDR.sub("0x?", text)[:300]]


def load_function(root, pythonpath, rel, qualname):
    """Import the module that holds `qualname` from this snapshot.  Returns (callable, skip_first, reason)."""
    for p in reversed([str(Path(root) / q) for q in pythonpath] + [str(root)]):
        sys.path.insert(0, p)
    modname = rel[:-3].replace("/", ".")
    for prefix in [str(Path(q)).replace("/", ".") + "." for q in pythonpath]:
        if modname.startswith(prefix):
            modname = modname[len(prefix):]
    if modname.endswith(".__init__"):
        modname = modname[: -len(".__init__")]
    try:
        mod = importlib.import_module(modname)
    except BaseException as exc:                                 # SystemExit and friends count as import failure
        spec = importlib.util.spec_from_file_location("gk_probe_target", str(Path(root) / rel))
        try:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except BaseException as exc2:
            return None, False, "import failed: %s / %s" % (type(exc).__name__, type(exc2).__name__)
    if "<locals>" in qualname:
        return None, False, "nested function"
    parts = qualname.split(".")
    obj = mod
    for i, part in enumerate(parts):
        if not hasattr(obj, part):
            return None, False, "attribute %s not found" % ".".join(parts[: i + 1])
        parent, obj = obj, getattr(obj, part)
    if len(parts) == 1:
        return obj, False, None
    raw = inspect.getattr_static(parent, parts[-1], None)
    if isinstance(raw, (staticmethod, classmethod)):
        return obj, False, None
    if inspect.isclass(parent):
        try:
            inst = parent()
        except BaseException as exc:
            return None, False, "instance method of a class that cannot be built without arguments (%s)" % type(exc).__name__
        return getattr(inst, parts[-1]), False, None
    return obj, False, None


def main(path):
    a = json.loads(Path(path).read_text())
    from gatekeeper_ext import fn_inputs as FI
    os.chdir(tempfile.mkdtemp(prefix="gk_probe_cwd_"))           # side effects of the function land in a scratch directory
    fn, skip_first, why = load_function(a["root"], a.get("pythonpath", []), a["file"], a["qualname"])
    if fn is None:
        Path(a["out"]).write_text(json.dumps({"status": "UNCALLABLE", "reason": why}))
        return 0
    if a["mode"] == "generate":
        calls, why = FI.generate(fn, a.get("n", 200), a.get("seed", 0), skip_first)
        Path(a["calls"]).write_text(FI.dumps_calls(calls))
        Path(a["out"]).write_text(json.dumps({"status": "UNCALLABLE" if why else "GENERATED", "reason": why, "n": len(calls)}))
        return 0
    calls = FI.loads_calls(Path(a["calls"]).read_text())
    signal.signal(signal.SIGALRM, _alarm)
    outcomes = []
    is_coro = inspect.iscoroutinefunction(fn)
    for args, kwargs in calls:
        signal.alarm(int(a.get("timeout", 5)))
        try:
            r = fn(*args, **kwargs)
            if is_coro:
                r = asyncio.run(r)
            outcomes.append(canonical(r))
        except CallTimeout:
            outcomes.append(["timeout"])
        except BaseException as exc:                             # including SystemExit raised by the function
            outcomes.append(["exc", type(exc).__name__, ADDR.sub("0x?", str(exc))[:120]])
        finally:
            signal.alarm(0)
    Path(a["out"]).write_text(json.dumps({"status": "RAN", "outcomes": outcomes}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
