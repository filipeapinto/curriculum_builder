# GOAL

Release only from externally verifiable semantic provenance and a fully
compiled effective graph. Re-run every historical and boundary test using
controller-resolved paths, signed receipts, and ledger/event linkage.

# TEST

- `/etc/hosts`, arbitrary text, explicit FAIL JSON, repeated files, invented
  DENIED logs, zero hashes, wrong schemas, and self-signed evidence all fail.
- All eleven P6 subtask receipts exist and hash correctly; ledger event and
  evidence-manifest IDs equal the admitted P6 records.
- Concurrent and cold-process resume admits exactly one activation through the
  SQLite store. Composite P0/P4 state and all Plan 19 lifecycle/history tests
  remain intact.
- Three independent v3 reviews report zero Critical/High on identical bytes.

# LOOP

P6 never repairs the plan version it reviews. Attribute implementation defects
to one owner and rerun provenance plus dependency closure. Any plan-level
Critical/High leaves v3 unapproved and ends the in-place loop.
