retry(fn, attempts, backoff) must:
1. Return fn()'s value on the first successful call.
2. Retry up to `attempts` times when fn() raises.
3. Re-raise the last exception if every attempt fails. It must NOT return None
   silently when all attempts fail — a caller cannot distinguish that from success.
4. Sleep backoff * 2**i between attempts.
