"""Draw oracle for demo target T6 (metrics.add_count).  Spec: booleans count as 0/1."""


def scopes():
    return {"bool": lambda rng: {"total": rng.randint(0, 50), "arg": rng.random() < 0.5},
            "int": lambda rng: {"total": rng.randint(0, 50), "arg": rng.randint(-100, 100)}}


def execute(draw):
    from metrics import add_count
    try:
        return {"ok": True, "value": add_count(draw["total"], draw["arg"])}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, draw, without, with_):
    if scope == "bool":
        ok = lambda o: o["ok"] and o["value"] == draw["total"] + int(draw["arg"])
        return ok(without), ok(with_)
    return True, with_ == without
