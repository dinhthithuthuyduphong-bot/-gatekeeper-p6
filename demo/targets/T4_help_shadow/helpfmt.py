"""Help text rendering for a CLI toolkit (constructed demo target)."""
from compat import text_type as str


def render_default(default_value, show_default=True):
    """Return the text shown after '[default: ...]', or None to hide it."""
    if not show_default:
        return None
    if default_value is None:
        return None
    if isinstance(default_value, (list, tuple)):
        return ", ".join(str(d) for d in default_value)
    elif default_value == "":
        return '""'
    return str(default_value)
