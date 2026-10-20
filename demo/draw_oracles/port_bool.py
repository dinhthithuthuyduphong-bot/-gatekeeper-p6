"""Draw oracle for demo target T5 (config.parse_port).  Spec: booleans are not ports."""

VIAS = ("direct", "config", "list")


def scopes():
    def bool_gen(rng):
        return {"via": rng.choice(VIAS), "arg": rng.random() < 0.5}

    def int_gen(rng):
        return {"via": rng.choice(VIAS), "arg": rng.randint(-5, 70000)}
    return {"bool": bool_gen, "int": int_gen}


def execute(draw):
    from config import load_config, parse_port, parse_ports
    call = {"direct": lambda v: parse_port(v), "config": lambda v: load_config({"port": v}),
            "list": lambda v: parse_ports([80, v])}[draw["via"]]
    try:
        return {"ok": True, "value": repr(call(draw["arg"]))}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, draw, without, with_):
    if scope == "bool":     # specification oracle
        ok = lambda o: (not o["ok"]) and o["exc"] == "TypeError"
        return ok(without), ok(with_)
    return True, with_ == without   # differential oracle: int behaviour must not change
