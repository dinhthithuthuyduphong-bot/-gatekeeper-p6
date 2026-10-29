"""Study P (development): deterministic, signature-driven input generator for calling an edited function directly.
Standard library only.  Inputs are drawn i.i.d. from a fixed distribution given (seed, qualified name), so the same
inputs are replayed in every snapshot (original, upstream fix, candidate patch).

Values are chosen from the parameter annotation when it is a simple type, else from the type of the default value, else
from a mixed pool of scalars and small containers.  Encoded as tagged JSON so they cross process boundaries exactly.
"""
import inspect
import json
import math
import random
import typing

INTS = [0, 1, -1, 2, 3, 7, 10, -10, 100, 255, 256, 1024, 2 ** 31 - 1, -2 ** 31, 10 ** 9]
FLOATS = [0.0, -0.0, 1.0, -1.5, 0.5, 1e-9, 1e9, 3.14159, math.inf, -math.inf, math.nan]
STRS = ["", "a", "A", "abc", " ", "  x  ", "0", "1", "-1", "True", "None", "\u00e9", "\u65e5\u672c", "a\nb", "\t", "x" * 50,
        "http://a.b/c?d=1", "/tmp/x", "a,b,c", "{}", "[]", "a.b", "A_b-C"]
SIMPLE = {int: INTS, float: FLOATS, str: STRS, bool: [True, False], bytes: [b"", b"a", b"\x00\xff", b"abc"]}


def _scalar(rng):
    pool = rng.choice([INTS, FLOATS, STRS, [None, True, False]])
    return rng.choice(pool)


def value_for(annotation, default, rng, depth=0):
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)
    if annotation in SIMPLE:
        return rng.choice(SIMPLE[annotation])
    if origin is typing.Union and args:
        return value_for(rng.choice(args), inspect.Parameter.empty, rng, depth)
    if annotation is type(None):
        return None
    if origin in (list, set, frozenset, tuple) or annotation in (list, tuple, set):
        inner = args[0] if args else inspect.Parameter.empty
        n = rng.randint(0, 4) if depth < 2 else 0
        vals = [value_for(inner, inspect.Parameter.empty, rng, depth + 1) for _ in range(n)]
        return tuple(vals) if (origin is tuple or annotation is tuple) else vals
    if origin is dict or annotation is dict:
        n = rng.randint(0, 3) if depth < 2 else 0
        vt = args[1] if len(args) == 2 else inspect.Parameter.empty
        return {rng.choice(STRS): value_for(vt, inspect.Parameter.empty, rng, depth + 1) for _ in range(n)}
    if default is not inspect.Parameter.empty and default is not None and type(default) in SIMPLE:
        return rng.choice(SIMPLE[type(default)])
    if depth < 2 and rng.random() < 0.15:
        return [_scalar(rng) for _ in range(rng.randint(0, 3))]
    return _scalar(rng)


def generate(fn, n, seed, skip_first=False):
    """n calls [args, kwargs] for fn.  Returns (calls, unsupported_reason or None)."""
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return [], "no signature"
    params = list(sig.parameters.values())[1 if skip_first else 0:]
    try:
        hints = typing.get_type_hints(fn)
    except Exception:
        hints = {}
    rng = random.Random("%s:%s" % (seed, getattr(fn, "__qualname__", "")))
    calls = []
    for _ in range(n):
        args, kwargs = [], {}
        for p in params:
            if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                continue
            ann = hints.get(p.name, p.annotation)
            required = p.default is p.empty
            if not required and rng.random() < 0.5:
                continue
            v = value_for(ann, p.default, rng)
            if p.kind == p.KEYWORD_ONLY or (not required and kwargs):
                kwargs[p.name] = v
            else:
                args.append(v)
        calls.append([args, kwargs])
    return calls, None


def encode(x):
    if isinstance(x, float):
        if math.isnan(x):
            return {"__f": "nan"}
        if math.isinf(x):
            return {"__f": "inf" if x > 0 else "-inf"}
        return x
    if isinstance(x, bytes):
        return {"__b": x.hex()}
    if isinstance(x, tuple):
        return {"__t": [encode(v) for v in x]}
    if isinstance(x, list):
        return [encode(v) for v in x]
    if isinstance(x, dict):
        return {"__d": [[encode(k), encode(v)] for k, v in x.items()]}
    return x


def decode(x):
    if isinstance(x, dict):
        if "__f" in x:
            return float(x["__f"])
        if "__b" in x:
            return bytes.fromhex(x["__b"])
        if "__t" in x:
            return tuple(decode(v) for v in x["__t"])
        if "__d" in x:
            return {decode(k): decode(v) for k, v in x["__d"]}
    if isinstance(x, list):
        return [decode(v) for v in x]
    return x


def dumps_calls(calls):
    return json.dumps([[encode(a), {k: encode(v) for k, v in kw.items()}] for a, kw in calls])


def loads_calls(text):
    return [[decode(a), {k: decode(v) for k, v in kw.items()}] for a, kw in json.loads(text)]
