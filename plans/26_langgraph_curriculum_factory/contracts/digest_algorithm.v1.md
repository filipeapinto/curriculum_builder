# N00 digest algorithm (frozen)

Binds every later hash reference used by result records, receipts, and the
scheduler's predecessor/result-hash bookkeeping.

## File digest

`SHA-256` over raw file bytes, no normalization, computed with
`hashlib.sha256(path.read_bytes()).hexdigest()` in code and
`shasum -a 256 <path>` for manual verification. Text files are hashed as
committed (repo `.gitattributes` defines line-ending policy; digests are not
recomputed after checkout-time normalization).

## Graph digest

`graph_digest = sha256(implementation.graph.v2.yaml raw bytes)`. Any edit to
the graph (including whitespace) changes the digest and invalidates every
scheduler receipt that cited the prior value. The schema file
(`implementation.graph.schema.v2.json`) is validated but not folded into the
graph digest; its own digest is recorded separately in receipts that perform
schema validation.

## Canonical JSON digest (state, receipts, records)

For any persisted structured record (result records' embedded data, artifact
version records, evidence entries, checkpoint-correlation entries):

1. Serialize with `json.dumps(obj, sort_keys=True, ensure_ascii=False,
   separators=(",", ":"))`.
2. UTF-8 encode.
3. `sha256` the bytes.

This is the one canonical-JSON rule for the whole Plan 26 implementation;
node prompts MUST NOT invent a second serialization convention. `NaN`,
`Infinity`, and non-finite floats are forbidden inputs (fail closed before
serialization) because they are not round-trip-stable JSON.

## Content-addressed artifact paths

Where the spec (section 15) stores an artifact under a `<hash>` path segment,
the hash is the file digest (raw bytes) of that exact artifact, not a
canonical-JSON digest of a wrapping record.

## Result-record command/exit-code capture

A result record's `commands` entries capture the literal invoked command
string and integer exit code; a command's stdout/stderr are captured to the
evidence path referenced from the record, not inlined, when they exceed 4 KiB.
