"""Worker-side oracle of the gold-differential harness (Study L, amendment L-A1).

Algorithmic, target-independent: a draw names a recorded call (function, call index) and an optional
type-confusion mutation of one argument.  execute() replays the call in the snapshot the worker was
started for and returns a canonical string of (result or exception type, arguments after the call).
Standard library only; compatible with Python 3.8.  A file `pool.json` must sit next to this file.
"""
import base64
import contextlib
import importlib
import io
import json
import pickle
import re
import signal
from pathlib import Path

# Fixed, pre-declared replacement values for the type-confusion mutation.
CONFUSION = [lambda: None, lambda: True, lambda: False, lambda: 0, lambda: 1, lambda: -1,
             lambda: 2 ** 31, lambda: 1.5, lambda: "", lambda: "a", lambda: [], lambda: {}]
N_CONFUSION = len(CONFUSION)
_ADDR = re.compile(r"0x[0-9a-fA-F]+")
_POOL = [None]
_CAP = 200


def _pool():
    if _POOL[0] is None:
        _POOL[0] = json.loads(Path(__file__).with_name("pool.json").read_text())
    return _POOL[0]


def canon(obj, depth=0, seen=None):
    """Deterministic textual form of a value; type names are part of it (True != 1)."""
    seen = set() if seen is None else seen
    t = type(obj).__name__
    if obj is None or isinstance(obj, (bool, int, str)):
        return "%s:%r" % (t, obj)
    if isinstance(obj, float):
        return "float:%r" % (obj,)
    if isinstance(obj, (bytes, bytearray)):
        return "%s:%r" % (t, bytes(obj))
    if depth >= 6:
        return t + ":<deep>"
    if id(obj) in seen:
        return t + ":<cycle>"
    seen = seen | {id(obj)}
    try:
        if isinstance(obj, (list, tuple)):
            items = [canon(x, depth + 1, seen) for x in list(obj)[:_CAP]]
            return "%s[%s;n=%d]" % (t, ",".join(items), len(obj))
        if isinstance(obj, (set, frozenset)):
            items = sorted(canon(x, depth + 1, seen) for x in list(obj)[:_CAP])
            return "%s{%s;n=%d}" % (t, ",".join(items), len(obj))
        if isinstance(obj, dict):
            items = sorted((canon(k, depth + 1, seen), canon(v, depth + 1, seen)) for k, v in list(obj.items())[:_CAP])
            return "dict{%s;n=%d}" % (",".join(a + "=>" + b for a, b in items), len(obj))
        if isinstance(obj, BaseException):
            return "exc:%s" % t
        d = getattr(obj, "__dict__", None)
        if isinstance(d, dict):
            return "%s.%s<%s>" % (type(obj).__module__, t, canon(d, depth + 1, seen))
        return _ADDR.sub("0x", "%s:%s" % (t, repr(obj)[:200]))
    except Exception:
        return t + ":<uncanonical>"


def _alarm(signum, frame):
    raise TimeoutError("gk-timeout")


def execute(draw):
    pool = _pool()
    f = pool["functions"][draw["f"]]
    obj = importlib.import_module(f["module"])
    for part in f["qualname"].split("."):
        obj = getattr(obj, part)
    args, kwargs = pickle.loads(base64.b64decode(f["calls"][draw["c"]]))
    m = draw.get("m")
    if m is not None:
        kind, key, vi = m
        value = CONFUSION[vi]()
        if kind == "p":
            args = list(args)
            args[key] = value
            args = tuple(args)
        else:
            kwargs = dict(kwargs)
            kwargs[key] = value
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, 5.0)
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                result = ("ok", canon(obj(*args, **kwargs)))
            except Exception as exc:          # an exception is part of the observable behaviour
                result = ("exc", type(exc).__name__)
            after = canon((args, kwargs))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)
    return {"out": json.dumps([result, after])}
