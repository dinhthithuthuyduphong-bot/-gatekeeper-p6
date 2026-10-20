"""Study D oracle for pycubrid (frozen before evaluation).

Provenance: upstream PR #479 (merged 2026-10-02) and its regression test in
tests/test_types.py: DBAPIType equality must not treat a bool as an integer type code,
while integer type codes (and IntEnum codes) keep matching.  Expected for a bool b and any
module-level DBAPIType T: (T == b) is False and (T != b) is True.  Integer codes behave as
before (differential).
"""


def _types():
    import pycubrid.types as t
    return [v for _, v in sorted(vars(t).items()) if isinstance(v, t.DBAPIType)]


def scopes():
    def bool_gen(rng):
        return {"t": rng.randrange(10 ** 6), "v": rng.random() < 0.5}

    def int_gen(rng):
        return {"t": rng.randrange(10 ** 6), "v": rng.randint(-5, 300), "pick_code": rng.random() < 0.5}
    return {"bool": bool_gen, "int": int_gen}


def execute(d):
    types = _types()
    T = types[d["t"] % len(types)]
    v = d["v"]
    if d.get("pick_code") and T.values:
        codes = sorted(c for c in T.values if isinstance(c, int))
        if codes:
            v = codes[d["t"] % len(codes)]
    try:
        return {"ok": True, "eq": bool(T == v), "ne": bool(T != v), "v": repr(v)}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":
        ok = lambda o: o["ok"] and o["eq"] is False and o["ne"] is True
        return ok(without), ok(with_)
    return True, with_ == without
