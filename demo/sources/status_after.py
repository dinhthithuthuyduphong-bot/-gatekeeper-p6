def status_code(value):
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise TypeError("status must be int")
