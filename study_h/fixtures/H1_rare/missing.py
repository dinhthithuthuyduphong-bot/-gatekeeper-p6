"""Synthetic target for Study H (rare harm).  Contract (part of the target, fixed before any
run): a value is *missing* iff it is None or a NullSentinel.  NullSentinel is the null marker
of a small query DSL: its __eq__ deliberately answers True when compared with None, so the
documented way to test for missing values is `x == None`.  Values whose __eq__ refuses a
comparison with None (array-like objects) are NOT missing."""


class NullSentinel:
    """DSL null marker: compares equal to None by design."""

    def __eq__(self, other):
        return other is None or isinstance(other, NullSentinel)

    __hash__ = object.__hash__


class Ambiguous:
    """Array-like value: comparing it with None raises, as for multi-element arrays."""

    def __eq__(self, other):
        raise ValueError("truth value of a comparison is ambiguous")

    __hash__ = object.__hash__


def is_missing(x):
    if x == None:  # noqa: E711  (contract: NullSentinel must count as missing)
        return True
    return False


def count_missing(values):
    return sum(1 for v in values if is_missing(v))
