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


def load_target(root, pythonpath, rel, qualname):
    """Import the module that holds `qualname` from this snapshot.  Returns (module, parent, name, reason)."""
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
            return None, None, None, "import failed: %s / %s" % (type(exc).__name__, type(exc2).__name__)
    if "<locals>" in qualname:
        return None, None, None, "nested function"
    parts = qualname.split(".")
    parent = mod
    for i, part in enumerate(parts[:-1]):
        try:
            parent = getattr(parent, part)
        except BaseException:
            return None, None, None, "attribute %s not found" % ".".join(parts[: i + 1])
    if inspect.getattr_static(parent, parts[-1], None) is None:
        return None, None, None, "attribute %s not found" % qualname
    return mod, parent, parts[-1], None


def load_function(root, pythonpath, rel, qualname):
    """Callable for the signature-driven generator.  Returns (callable, skip_first, reason)."""
    mod, parent, name, why = load_target(root, pythonpath, rel, qualname)
    if why:
        return None, False, why
    raw = inspect.getattr_static(parent, name, None)
    if parent is mod or isinstance(raw, (staticmethod, classmethod)) or not inspect.isclass(parent):
        try:
            return getattr(parent, name), False, None
        except BaseException as exc:
            return None, False, "attribute access raised %s" % type(exc).__name__
    try:
        inst = parent()
    except BaseException as exc:
        return None, False, "instance method of a class that cannot be built without arguments (%s)" % type(exc).__name__
    try:
        return getattr(inst, name), False, None
    except BaseException as exc:                                 # a property or descriptor that raises
        return None, False, "attribute access raised %s" % type(exc).__name__


def run_calls(items, resolve, timeout):
    """items: [(receiver, args, kwargs)]; resolve(receiver) -> the callable.  One canonical outcome per item."""
    outcomes = []
    for receiver, args, kwargs in items:
        signal.alarm(int(timeout))
        try:
            fn = resolve(receiver)
            r = fn(*args, **kwargs)
            if inspect.iscoroutine(r):
                r = asyncio.run(r)
            outcomes.append(canonical(r))
        except CallTimeout:
            outcomes.append(["timeout"])
        except BaseException as exc:                             # including SystemExit raised by the function
            outcomes.append(["exc", type(exc).__name__, ADDR.sub("0x?", str(exc))[:120]])
        finally:
            signal.alarm(0)
    return outcomes


def run_generator(a):
    """Mode run_gen: execute a model-written `make_inputs(rng, n)` INSIDE this snapshot and call the function."""
    import random
    import traceback
    mod, parent, name, why = load_target(a["root"], a.get("pythonpath", []), a["file"], a["qualname"])
    if why:
        return {"status": "UNCALLABLE", "reason": why}
    ns = {"module": mod, "target_class": parent if inspect.isclass(parent) else None, "target_name": name, "random": random}
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(60)
    try:
        exec(compile(Path(a["gen_code"]).read_text(), "make_inputs.py", "exec"), ns)
        items = list(ns["make_inputs"](random.Random(a.get("seed", 0)), int(a.get("n", 200))))[: int(a.get("n", 200))]
        items = [(it[0], list(it[1]), dict(it[2])) for it in items]
    except CallTimeout:
        return {"status": "GEN_FAILED", "error": "the generator did not finish within 60 seconds"}
    except BaseException as exc:
        return {"status": "GEN_FAILED", "error": "".join(traceback.format_exception_only(type(exc), exc))[-600:]}
    finally:
        signal.alarm(0)
    if not items:
        return {"status": "GEN_FAILED", "error": "make_inputs returned no input"}

    def resolve(receiver):
        return getattr(receiver, name) if receiver is not None else getattr(parent, name)
    return {"status": "RAN", "outcomes": run_calls(items, resolve, a.get("timeout", 2))}


def main(path):
    a = json.loads(Path(path).read_text())
    from gatekeeper_ext import fn_inputs as FI
    os.chdir(tempfile.mkdtemp(prefix="gk_probe_cwd_"))           # side effects of the function land in a scratch directory
    if a["mode"] == "run_gen":
        Path(a["out"]).write_text(json.dumps(run_generator(a)))
        return 0
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
    outcomes = run_calls([(None, args, kwargs) for args, kwargs in calls], lambda _r: fn, a.get("timeout", 5))
    Path(a["out"]).write_text(json.dumps({"status": "RAN", "outcomes": outcomes}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
