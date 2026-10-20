"""Study D oracle for open-feature python-sdk (frozen before evaluation).

Provenance: upstream PR #621 test test_client_returns_default_on_type_mismatch: for an
INTEGER flag whose stored value is True/False, get_integer_details must return the
caller's default (an int, not a bool) with ErrorCode.TYPE_MISMATCH, and get_integer_value
must return the default.  Integer flag values must behave as before (differential).
Synchronous API only (the async path mirrors it upstream).
"""


def _imports():
    from openfeature import api
    try:
        from openfeature.provider.in_memory_provider import InMemoryFlag, InMemoryProvider
    except ImportError:  # older layout
        from openfeature.provider.in_memory import InMemoryFlag, InMemoryProvider
    return api, InMemoryFlag, InMemoryProvider


def scopes():
    return {"bool": lambda rng: {"stored": rng.random() < 0.5, "default": rng.randint(-1000, 1000)},
            "int": lambda rng: {"stored": rng.randint(-10 ** 6, 10 ** 6), "default": rng.randint(-1000, 1000)}}


def execute(d):
    api, InMemoryFlag, InMemoryProvider = _imports()
    try:
        api.set_provider_and_wait(InMemoryProvider({"flag": InMemoryFlag("enabled", {"enabled": d["stored"]})}))
        client = api.get_client()
        det = client.get_integer_details("flag", d["default"])
        val = client.get_integer_value("flag", d["default"])
        return {"ok": True, "value": repr(det.value), "type": type(det.value).__name__,
                "error": str(det.error_code), "value2": repr(val), "type2": type(val).__name__}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    if scope == "bool":
        def ok(o):
            return (o["ok"] and o["type"] == "int" and o["value"] == repr(d["default"])
                    and "TYPE_MISMATCH" in o["error"] and o["type2"] == "int"
                    and o["value2"] == repr(d["default"]))
        return ok(without), ok(with_)
    return True, with_ == without
