"""Study E control oracles (trino, tomlkit, redis-py): bool is handled before the int
branch, so the skill must not change behaviour.  Both scopes are differential: any change
with the skill is a regression.  The target is recognised by the package directory present
in the worker's snapshot (its working directory), so no shared runner file changes."""
import os


def scopes():
    return {"bool": lambda rng: {"v": rng.random() < 0.5},
            "int": lambda rng: {"v": rng.randint(-10 ** 9, 10 ** 9)}}


def execute(d):
    which = "trino" if os.path.isdir("trino") else "tomlkit" if os.path.isdir("tomlkit") else "redis"
    try:
        if which == "trino":
            from trino.dbapi import Cursor
            out = Cursor._format_prepared_param(None, d["v"])
        elif which == "tomlkit":
            import tomlkit
            out = tomlkit.item(d["v"]).as_string()
        else:
            from redis._parsers.encoders import Encoder
            out = Encoder("utf-8", "strict", False).encode(d["v"])
        return {"ok": True, "value": repr(out)}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__, "msg": str(exc)[:120]}


def judge(scope, d, without, with_):
    return True, with_ == without
