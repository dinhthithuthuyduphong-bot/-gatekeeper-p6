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


def cases():
    return _common()
