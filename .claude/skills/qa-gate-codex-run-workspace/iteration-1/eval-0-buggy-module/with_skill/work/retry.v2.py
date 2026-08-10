import time


def retry(fn, attempts=3, backoff=0.5):
    """Call fn(), retrying on exception. Returns fn()'s value, or raises the
    last exception if every attempt fails.

    Sleeps backoff * 2**i between attempts, and never after the final one.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(backoff * (2 ** i))
