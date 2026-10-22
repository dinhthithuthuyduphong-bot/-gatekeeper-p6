"""Study G CONTROL oracle for hera_pspec.utils.get_delays (`n_dlys == None` on ordinary values).
Differential in both scopes: rewriting to `is None` must not change any output."""


def scopes():
    def none_gen(rng):
        return {"n": rng.randint(2, 64), "f0": rng.uniform(50e6, 150e6), "df": rng.uniform(1e4, 1e6), "n_dlys": None}

    def int_gen(rng):
        n = rng.randint(2, 64)
        return {"n": n, "f0": rng.uniform(50e6, 150e6), "df": rng.uniform(1e4, 1e6), "n_dlys": rng.randint(1, 2 * n)}
    return {"none": none_gen, "int": int_gen}


def execute(d):
    import numpy as np
    from hera_pspec import utils
    try:
        freqs = d["f0"] + d["df"] * np.arange(d["n"])
        out = utils.get_delays(freqs, n_dlys=d["n_dlys"])
        return {"ok": True, "out": [float(x) for x in out]}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    return True, with_ == without
