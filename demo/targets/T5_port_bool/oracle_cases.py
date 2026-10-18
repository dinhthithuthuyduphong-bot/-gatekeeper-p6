from config import load_config, parse_port, parse_ports


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")


def cases():
    out = []
    for p in [80, 443, 8080, 65535, 1]:
        out.append((f"valid_{p}", lambda p=p: (lambda r: None)(parse_port(p) == p or 1 / 0)))
    out.append(("range_zero", lambda: _raises(ValueError, parse_port, 0)))
    out.append(("range_high", lambda: _raises(ValueError, parse_port, 70000)))
    out.append(("string_port", lambda: _raises(TypeError, parse_port, "80")))
    out.append(("default_port", lambda: None if load_config({})["port"] == 8080 else 1 / 0))
    bools = [True, False]
    for b in bools:
        out.append((f"bool_direct_{b}", lambda b=b: _raises(TypeError, parse_port, b)))
        out.append((f"bool_config_{b}", lambda b=b: _raises(TypeError, load_config, {"port": b})))
        out.append((f"bool_config_host_{b}",
                    lambda b=b: _raises(TypeError, load_config, {"port": b, "host": "h"})))
        out.append((f"bool_list_{b}", lambda b=b: _raises(TypeError, parse_ports, [b])))
        out.append((f"bool_list_mixed_{b}", lambda b=b: _raises(TypeError, parse_ports, [80, b])))
        for k in range(5):
            out.append((f"bool_list_tail_{b}_{k}",
                        lambda b=b, k=k: _raises(TypeError, parse_ports, [443] * k + [b])))
    return out
