"""Study D control oracle: jsonschema (already guards bool; the skill must not change behaviour).

Provenance: JSON Schema spec ('boolean' and 'integer' are distinct types); jsonschema's own
_types.is_integer excludes bool.  Expected: bool fails {"type": "integer"}; ints pass and
integer behaviour is unchanged (differential)."""


def scopes():
    return {"bool": lambda rng: {"v": rng.random() < 0.5},
            "int": lambda rng: {"v": rng.randint(-10 ** 9, 10 ** 9)}}


def execute(d):
    import jsonschema
    try:
        jsonschema.validate(d["v"], {"type": "integer"})
        return {"ok": True, "valid": True}
    except jsonschema.ValidationError:
        return {"ok": True, "valid": False}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":
        ok = lambda o: o["ok"] and o["valid"] is False
        return ok(without), ok(with_)
    return True, with_ == without
