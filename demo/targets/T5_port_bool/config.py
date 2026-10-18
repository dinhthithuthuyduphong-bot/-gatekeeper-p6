"""Configuration loader (constructed demo target)."""

DEFAULT_PORT = 8080


def parse_port(value):
    if isinstance(value, int):
        if 0 < value < 65536:
            return value
        raise ValueError(f"port out of range: {value}")
    raise TypeError(f"port must be an integer, got {type(value).__name__}")


def load_config(raw):
    return {"port": parse_port(raw.get("port", DEFAULT_PORT)),
            "host": str(raw.get("host", "localhost"))}


def parse_ports(values):
    return [parse_port(v) for v in values]
