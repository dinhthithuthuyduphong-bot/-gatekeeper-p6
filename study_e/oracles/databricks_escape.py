"""Study E oracle (illustrative only, provenance tier 3: characterization of existing
behaviour; no documentation states that bool inline parameters are supported).
Expected: ParamEscaper.escape_item(True/False) keeps returning a value (no exception)."""


def scopes():
    return {"bool": lambda rng: {"v": rng.random() < 0.5},
            "int": lambda rng: {"v": rng.randint(-10 ** 9, 10 ** 9)}}


def execute(d):
    from databricks.sql.utils import ParamEscaper
    try:
        return {"ok": True, "value": repr(ParamEscaper().escape_item(d["v"]))}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":
        return True, with_["ok"] or not without["ok"]
    return True, with_ == without
