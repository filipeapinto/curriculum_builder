import time


def retry(fn, attempts=3, backoff=0.5):
    """Call fn(), retrying on exception. Returns fn()'s value, or raises the
    last exception if every attempt fails."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    last_exc = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as exc:
            last_exc = exc
            if i < attempts - 1:
                time.sleep(backoff * (2 ** i))
    raise last_exc
