"""Study S amendment S-A1: call one function or METHOD of one snapshot on G0 inputs, building the receiver from the class's
constructor signature (the frozen tools/fn_probe_inner.py only builds classes without arguments).  Runs inside the target's
virtual environment, one fresh process per snapshot.

python tools/composition_inner.py ARGS.json      (ARGS as fn_probe_inner, mode "generate" | "run")

generate: calls = [[ctor_args, ctor_kwargs, args, kwargs], ...] (ctor parts null for plain functions, static and class methods).
run:      outcome per call = [outcome of the call, state of the receiver after the call]; for an __init__ unit the call is the
          construction and the outcome is the constructed object's state.  A constructor that raises is itself an outcome.
"""
import json
import os
import signal
import sys
import tempfile
import inspect
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import fn_probe_inner as FPI  # noqa: E402  (frozen; reused, not modified)


def mangled(cls_name, name):
    """Python name mangling for a private method: Class.__m is stored as _Class__m."""
    if name.startswith("__") and not name.endswith("__"):
        return "_%s%s" % (cls_name.lstrip("_"), name)
    return name


def resolve_target(a):
    parts = a["qualname"].split(".")
    if len(parts) >= 2:
        parts[-1] = mangled(parts[-2], parts[-1])
    mod, parent, name, why = FPI.load_target(a["root"], a.get("pythonpath", []), a["file"], ".".join(parts))
    return mod, parent, name, why


def subst(value, rng):
    """Amendment S-A2: replace each int (not bool) by True/False with probability 1/4; bool is a subclass of int."""
    if type(value) is int:
        return rng.choice([True, False]) if rng.random() < 0.25 else value
    if isinstance(value, list):
        return [subst(v, rng) for v in value]
    if isinstance(value, tuple):
        return tuple(subst(v, rng) for v in value)
    if isinstance(value, dict):
        return {k: subst(v, rng) for k, v in value.items()}
    return value


def state(obj):
    try:
        d = vars(obj)
    except TypeError:
        return FPI.canonical(obj)
    return FPI.canonical({k: d[k] for k in sorted(d)})


def main(path):
    a = json.loads(Path(path).read_text())
    from gatekeeper_ext import fn_inputs as FI
    os.chdir(tempfile.mkdtemp(prefix="gk_comp_cwd_"))
    mod, parent, name, why = resolve_target(a)
    if why:
        Path(a["out"]).write_text(json.dumps({"status": "UNCALLABLE", "reason": why}))
        return 0
    raw = inspect.getattr_static(parent, name)
    is_method = inspect.isclass(parent) and parent is not mod and not isinstance(raw, (staticmethod, classmethod))
    n, seed = int(a.get("n", 200)), a.get("seed", 0)
    if a["mode"] == "generate":
        if is_method:
            ctor, why1 = FI.generate(parent, n, seed, False)
            meth, why2 = ([[[], {}]] * n, None) if name == "__init__" else FI.generate(raw, n, seed, True)
            why = why1 or why2
            calls = [[c[0], c[1], m[0], m[1]] for c, m in zip(ctor, meth)]
        else:
            fn = getattr(parent, name)
            plain, why = FI.generate(fn, n, seed, False)
            calls = [[None, None, c[0], c[1]] for c in plain]
        if a.get("subtype"):
            import random
            out_calls = []
            for i, c in enumerate(calls):
                rng = random.Random("%s:subtype:%d" % (seed, i))
                out_calls.append([subst(c[0], rng) if c[0] is not None else None, subst(c[1], rng) if c[1] is not None else None,
                                  subst(c[2], rng), subst(c[3], rng)])
            calls = out_calls
        Path(a["calls"]).write_text(json.dumps([[FI.dumps_calls([[c[0] or [], c[1] or {}]]), FI.dumps_calls([[c[2], c[3]]]),
                                                 c[0] is None] for c in calls]))
        Path(a["out"]).write_text(json.dumps({"status": "UNCALLABLE" if (why or not calls) else "GENERATED", "reason": why,
                                              "n": len(calls), "method": is_method}))
        return 0
    raw_calls = json.loads(Path(a["calls"]).read_text())
    signal.signal(signal.SIGALRM, FPI._alarm)
    outcomes = []
    for ctor_s, call_s, plain in raw_calls:
        (cargs, ckw), = FI.loads_calls(ctor_s)
        (args, kw), = FI.loads_calls(call_s)
        signal.alarm(int(a.get("timeout", 2)))
        try:
            if plain:
                outcomes.append([FPI.canonical(getattr(parent, name)(*args, **kw)), None])
                continue
            try:
                inst = parent(*cargs, **ckw)
            except FPI.CallTimeout:
                raise
            except BaseException as exc:                     # a constructor that raises is an outcome
                outcomes.append([["ctor_exc", type(exc).__name__, FPI.mask(str(exc))[:120]], None])
                continue
            if name == "__init__":
                outcomes.append([["ok", "constructed", ""], state(inst)])
                continue
            try:
                r = getattr(inst, name)(*args, **kw)
                out = FPI.canonical(r)
            except FPI.CallTimeout:
                raise
            except BaseException as exc:
                out = ["exc", type(exc).__name__, FPI.mask(str(exc))[:120]]
            outcomes.append([out, state(inst)])
        except FPI.CallTimeout:
            outcomes.append(["timeout"])
        finally:
            signal.alarm(0)
    Path(a["out"]).write_text(json.dumps({"status": "RAN", "outcomes": outcomes}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
