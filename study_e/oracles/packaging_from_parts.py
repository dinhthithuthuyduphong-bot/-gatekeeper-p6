"""Study E oracle (MIXED/contested, provenance tier 2: maintainer statement).

pypa/packaging PR #1425 ('reject bool values in Version parts') was closed by a maintainer
as 'overly defensive' (27/9/2026); the CHANGELOG however rejects TOML booleans in pylock
files.  Pre-registered expectation for this cell: the maintainer's statement on Version
parts, i.e. Version.from_parts accepts the inputs it accepted before (no new exception).
Integer scope: unchanged behaviour (differential).
"""


def scopes():
    def bool_gen(rng):
        return {"field": rng.choice(["epoch", "release", "post", "dev"]), "v": rng.random() < 0.5,
                "n": rng.randint(0, 50)}

    def int_gen(rng):
        return {"field": rng.choice(["epoch", "release", "post", "dev"]), "v": rng.randint(0, 50),
                "n": rng.randint(0, 50)}
    return {"bool": bool_gen, "int": int_gen}


def execute(d):
    from packaging.version import Version
    kw = {"release": (1, d["n"])}
    if d["field"] == "release":
        kw["release"] = (d["v"], d["n"])
    else:
        kw[d["field"]] = d["v"]
    try:
        return {"ok": True, "raised": False, "value": str(Version.from_parts(**kw))}
    except Exception as exc:
        return {"ok": True, "raised": True, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":            # maintainer contract: what was accepted stays accepted
        return True, (with_["raised"] is False) or without["raised"]
    return True, with_ == without
