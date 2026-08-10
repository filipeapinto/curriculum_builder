# GOAL

Require signed semantic receipts for deterministic checks and isolated judges,
plus schema-valid artifacts at compiler-resolved paths, before evaluator joins.

# TEST

- A file whose content or assertion says FAIL cannot pass because the receipt
  schema requires exit zero and all assertions PASS, and its external signature
  binds that content to the current compiled subject.
- Reusing one file across tests/artifacts, substituting unrelated real bytes, or
  using a wrong path/media type/schema fails.
- Ledger receipt files exist, hash correctly, cover the compiled subtask set,
  and bind the admitted event and evidence manifest IDs.

# LOOP

Repair the one failed artifact/evaluator and rerun its signed receipt, schema,
join, and dependency closure. Never self-sign from a model workspace or accept
file presence as proof.
