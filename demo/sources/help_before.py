def format_default(default_value, show_default=True):
    if not show_default:
        return None
    if default_value is None:
        return None
    elif default_value == "":
        return '""'
    return str(default_value)
