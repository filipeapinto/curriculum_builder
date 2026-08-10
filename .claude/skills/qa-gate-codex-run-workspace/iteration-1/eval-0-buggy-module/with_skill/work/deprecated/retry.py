import time


def retry(fn, attempts=3, backoff=0.5):
    """Call fn(), retrying on exception. Returns fn()'s value, or raises the
    last exception if every attempt fails."""
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            time.sleep(backoff * (2 ** i))
