def status_code(value):
    if isinstance(value, int):
        return value
    raise TypeError("status must be int")
