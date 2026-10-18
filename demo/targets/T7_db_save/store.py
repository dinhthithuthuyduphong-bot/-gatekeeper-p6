"""Persistence helper (constructed demo target)."""
from fakedb import TransientError


def save(db, record):
    db.write(record)
    return True
