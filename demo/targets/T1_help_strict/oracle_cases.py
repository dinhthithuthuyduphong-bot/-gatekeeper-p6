from helpfmt import render_default

def _expect(value, expected, **kw):
    got = render_default(value, **kw)
    assert got == expected, (got, expected)


def _common():
    out = []
    for s in ["abc", "x y", "0", "None", "default"]:
        out.append((f"plain_str_{s.replace(' ', '_')}", lambda s=s: _expect(s, s)))
    out.append(("empty_string", lambda: _expect("", '""')))
    out.append(("none_hidden", lambda: _expect(None, None)))
    out.append(("int_zero", lambda: _expect(0, "0")))
    out.append(("show_default_off", lambda: _expect("abc", None, show_default=False)))
    out.append(("sequence", lambda: _expect(["a", "b"], "a, b")))
    return out


class StrictEq:
    """Value whose __eq__ refuses foreign comparisons (like numpy arrays)."""

    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        if not isinstance(other, StrictEq):
            raise ValueError("ambiguous comparison")
        return self.label == other.label

    __hash__ = object.__hash__

    def __str__(self):
        return f"<{self.label}>"


class _Ambiguous:
    def __bool__(self):
        raise ValueError("truth value of an array is ambiguous")


class ArrayLike:
    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        return _Ambiguous()

    __hash__ = object.__hash__

    def __str__(self):
        return f"array({self.n})"


def cases():
    out = _common()
    for i in range(12):
        out.append((f"strict_eq_{i}", lambda i=i: _expect(StrictEq(f"v{i}"), f"<v{i}>")))
    for n in range(8):
        out.append((f"array_like_{n}", lambda n=n: _expect(ArrayLike(n), f"array({n})")))
    return out
