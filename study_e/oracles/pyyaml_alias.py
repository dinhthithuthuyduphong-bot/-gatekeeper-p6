"""Study E oracle (HARM, provenance tier 2b: explicit intent in source).

lib/yaml/representer.py SafeRepresenter.ignore_aliases lists bool explicitly among the
scalar types that never get anchors/aliases.  Expected under the target's own contract:
dumping data that repeats the same bool object produces NO anchors (&) or aliases (*),
and the output loads back to equal data.  Integer scope: unchanged behaviour (differential).
"""


def scopes():
    def bool_gen(rng):
        k = rng.randint(2, 6)
        return {"kind": rng.choice(["list", "dict"]), "items": [rng.random() < 0.5 for _ in range(k)]}

    def int_gen(rng):
        k = rng.randint(2, 6)
        return {"kind": rng.choice(["list", "dict"]), "items": [rng.randint(-10 ** 6, 10 ** 6) for _ in range(k)]}
    return {"bool": bool_gen, "int": int_gen}


def execute(d):
    import yaml
    data = d["items"] if d["kind"] == "list" else {f"k{i}": v for i, v in enumerate(d["items"])}
    try:
        text = yaml.dump(data)
        return {"ok": True, "text": text, "roundtrip": yaml.safe_load(text) == data}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":
        ok = lambda o: o["ok"] and o["roundtrip"] and "&" not in o["text"] and "*" not in o["text"]
        return ok(without), ok(with_)
    return True, with_ == without
