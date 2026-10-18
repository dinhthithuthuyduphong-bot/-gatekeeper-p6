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


class LazyText:
    """gettext_lazy-style proxy: NOT a str subclass, but compares and renders as text."""

    def __init__(self, fn):
        self._fn = fn

    def __str__(self):
        return self._fn()

    def __eq__(self, other):
        return str(self) == other

    __hash__ = object.__hash__


def cases():
    out = _common()
    for word in ["Hello", "Xin chao", "Bonjour", "Hola"]:
        out.append((f"lazy_text_{word.replace(' ', '_')}",
                    lambda w=word: _expect(LazyText(lambda: w), w)))
    for i in range(16):
        out.append((f"lazy_empty_{i}", lambda: _expect(LazyText(lambda: ""), '""')))
    return out
