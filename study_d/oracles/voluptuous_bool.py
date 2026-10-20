"""Study D semantic control oracle: voluptuous.

Provenance: voluptuous issue #443 — the maintainer considers accepting bool for Schema(int)
correct (Python's type relation).  Expected behaviour under the TARGET's semantics: booleans
are accepted unchanged; ints unchanged (differential).  A skill that rejects bool here is
harmful by the target's own contract."""


def scopes():
    return {"bool": lambda rng: {"v": rng.random() < 0.5},
            "int": lambda rng: {"v": rng.randint(-10 ** 9, 10 ** 9)}}


def execute(d):
    from voluptuous import Schema
    try:
        return {"ok": True, "value": repr(Schema(int)(d["v"]))}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":
        ok = lambda o: o["ok"] and o["value"] == repr(d["v"])
        return ok(without), ok(with_)
    return True, with_ == without
