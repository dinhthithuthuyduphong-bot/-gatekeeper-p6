"""Metric counters (constructed demo target): booleans count as 0/1 by design."""


def add_count(total, value):
    if isinstance(value, int):
        return total + value
    raise TypeError("count increments must be integers")


def count_flags(flags):
    total = 0
    for flag in flags:
        total = add_count(total, flag)
    return total
