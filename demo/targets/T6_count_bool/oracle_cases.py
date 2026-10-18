from metrics import add_count, count_flags


def _eq(a, b):
    assert a == b, (a, b)


def cases():
    out = []
    for a, b in [(0, 1), (2, 3), (10, -4), (5, 0), (7, 7)]:
        out.append((f"int_{a}_{b}", lambda a=a, b=b: _eq(add_count(a, b), a + b)))

    def _str_rejected():
        try:
            add_count(0, "1")
        except TypeError:
            return
        raise AssertionError("expected TypeError")
    out.append(("string_rejected", _str_rejected))
    flags = [[True], [False], [True, True], [True, False, True], [False, False],
             [True] * 5, [True, False] * 3, [False, True]]
    for i, f in enumerate(flags):
        out.append((f"flags_{i}", lambda f=f: _eq(count_flags(f), sum(f))))
        out.append((f"bool_increment_{i}", lambda f=f: _eq(add_count(1, f[0]), 1 + int(f[0]))))
    return out
