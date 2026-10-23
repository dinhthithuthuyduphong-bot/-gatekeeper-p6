"""Study H oracle (synthetic, contract stated in the target).  Each draw is one value:
an Ambiguous object with probability b (the skill helps: `is None` no longer raises),
a NullSentinel with probability rho (the skill harms: it is no longer counted as missing),
otherwise an ordinary value (no change).  Scope name encodes rho in basis points."""

B = 0.5
RHOS = {"rho_0": 0.0, "rho_100": 0.01, "rho_200": 0.02, "rho_300": 0.03, "rho_500": 0.05, "rho_1000": 0.10}


def scopes():
    def make(rho):
        def gen(rng):
            u = rng.random()
            if u < rho:
                return {"kind": "sentinel"}
            if u < rho + B:
                return {"kind": "ambiguous"}
            return {"kind": "plain", "v": rng.choice([None, 0, 1, "", "a", 2.5])}
        return gen
    return {name: make(rho) for name, rho in RHOS.items()}


def execute(d):
    from missing import Ambiguous, NullSentinel, is_missing
    x = NullSentinel() if d["kind"] == "sentinel" else Ambiguous() if d["kind"] == "ambiguous" else d["v"]
    try:
        return {"ok": True, "missing": bool(is_missing(x))}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    expected = d["kind"] == "sentinel" or (d["kind"] == "plain" and d["v"] is None)
    ok = lambda o: o["ok"] and o["missing"] == expected
    return ok(without), ok(with_)
