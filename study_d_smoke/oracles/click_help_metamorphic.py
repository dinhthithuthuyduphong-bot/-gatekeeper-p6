"""SMOKE ONLY oracle (Click 8.2.1, development data): help text for a default D must equal
the help text for its string twin str(D).  Scope 'objects': strict-eq objects; scope 'lazy':
lazy text equal to "" (known from development runs to be broken by the empty-string guard)."""


class _StrictEq:
    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        if isinstance(other, str):
            raise ValueError("cannot compare to string")
        return NotImplemented

    __hash__ = object.__hash__

    def __str__(self):
        return self.label


class _LazyText:
    def __init__(self, text):
        self._text = text

    def __str__(self):
        return self._text

    def __eq__(self, other):
        return str(self) == other

    __hash__ = object.__hash__


def scopes():
    return {"objects": lambda rng: {"kind": "strict", "label": f"v{rng.randint(0, 10 ** 6)}"},
            "lazy": lambda rng: {"kind": "lazy"}}


def _help(click, default):
    opt = click.Option(["--limit"], default=default, show_default=True)
    return opt.get_help_record(click.Context(click.Command("cli")))[1]


def execute(d):
    import click
    obj = _StrictEq(d["label"]) if d["kind"] == "strict" else _LazyText("")
    try:
        return {"ok": True, "same": _help(click, obj) == _help(click, str(obj))}
    except Exception as exc:
        return {"ok": False, "exc": type(exc).__name__}


def judge(scope, d, without, with_):
    ok = lambda o: o["ok"] and o["same"]
    return ok(without), ok(with_)
