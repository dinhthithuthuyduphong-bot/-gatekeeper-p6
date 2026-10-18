from client import TransientError


def _gk_retry(fn, exc, attempts):
    """Inserted by skill retry_write (bounded retry)."""
    for attempt in range(attempts):
        try:
            return fn()
        except exc:
            if attempt == attempts - 1:
                raise


def push(client, item):
    _gk_retry(lambda: client.write(item), TransientError, 3)
