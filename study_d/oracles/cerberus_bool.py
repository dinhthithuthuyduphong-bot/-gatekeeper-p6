"""Study D draw oracle for Cerberus (frozen before evaluation).

Provenance: upstream commit d25ae8f test TestValidation::test_boolean_is_not_a_number and
the Cerberus docs ('number' = int or float, excluding bool).  Integer/float behaviour
must not change (differential oracle).
"""


def scopes():
    return {"bool": lambda rng: {"v": rng.random() < 0.5},
            "number": lambda rng: {"v": rng.choice([rng.randint(-10 ** 6, 10 ** 6),
                                                     rng.uniform(-1e6, 1e6)])}}


def execute(d):
    from cerberus import Validator
    try:
        return {"ok": True, "value": bool(Validator({"x": {"type": "number"}}).validate({"x": d["v"]}))}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":
        ok = lambda o: o["ok"] and o["value"] is False
        return ok(without), ok(with_)
    return True, with_ == without
