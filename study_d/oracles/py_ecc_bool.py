"""Study D draw oracle for py_ecc (frozen before evaluation).

Provenance: the expected behaviour for booleans is taken from upstream py_ecc PR #161
tests (tests/core/test_bn128_and_bls12_381.py::test_FQ_and_FQP_reject_bools and
tests/bls/ciphersuites/test_g2_basic.py::test_sk_to_pk[True-False]): FQ(True),
FQ(1) + True, FQ2([True, 2]), FQ2([1, 2]) * True raise TypeError; G2Basic.SkToPk(True)
raises ValidationError.  Integer behaviour must not change (differential oracle).
"""
import importlib

CURVES = ("py_ecc.bn128", "py_ecc.bls12_381", "py_ecc.optimized_bn128", "py_ecc.optimized_bls12_381")
OPS = ("FQ(v)", "FQ(n)+v", "FQ2([v,n])", "FQ2([n,m])*v", "SkToPk(v)")
EXPECTED_EXC = {"SkToPk(v)": "ValidationError"}          # everything else: TypeError


def scopes():
    def gen(kind):
        def g(rng):
            v = (rng.random() < 0.5) if kind == "bool" else rng.randint(1, 2 ** 16)
            return {"op": rng.choice(OPS), "curve": rng.choice(CURVES), "v": v,
                    "n": rng.randint(1, 2 ** 16), "m": rng.randint(1, 2 ** 16)}
        return g
    return {"bool": gen("bool"), "int": gen("int")}


def _norm(x):
    if hasattr(x, "n"):
        return ["FQ", int(x.n)]
    if hasattr(x, "coeffs"):
        return ["FQP", [int(c.n) if hasattr(c, "n") else int(c) for c in x.coeffs]]
    if isinstance(x, (bytes, bytearray)):
        return ["bytes", bytes(x).hex()]
    return ["repr", repr(x)]


def execute(d):
    mod = importlib.import_module(d["curve"])
    FQ, FQ2 = mod.FQ, mod.FQ2
    v, n, m = d["v"], d["n"], d["m"]
    try:
        if d["op"] == "FQ(v)":
            out = FQ(v)
        elif d["op"] == "FQ(n)+v":
            out = FQ(n) + v
        elif d["op"] == "FQ2([v,n])":
            out = FQ2([v, n])
        elif d["op"] == "FQ2([n,m])*v":
            out = FQ2([n, m]) * v
        else:
            from py_ecc.bls import G2Basic
            out = G2Basic.SkToPk(v)
        return {"ok": True, "value": _norm(out)}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":
        want = EXPECTED_EXC.get(d["op"], "TypeError")
        ok = lambda o: (not o["ok"]) and o["exc"] == want
        return ok(without), ok(with_)
    return True, with_ == without
