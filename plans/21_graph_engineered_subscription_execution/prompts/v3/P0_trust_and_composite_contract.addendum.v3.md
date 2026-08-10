# GOAL

Produce one composite `P0_contract_bundle` containing the frozen v1 baseline and
v3 assurance facts. Discover external controller/operator trust and sandbox
engine registry; never create, repair, sign, or bless those external sources.

# TEST

- Recompute `base_contract_hash` from canonical `baseline_v1`; P4 receives the
  composite schema, not the obsolete standalone baseline.
- An available authority root is absolute, pre-existing, non-model-writable,
  owned by a UID distinct from the model UID, and contains hash-matching pinned
  keys and a signed allowlisted engine registry.
- Missing trust is represented as `UNAVAILABLE` and later pauses before P2;
  invented files, same-UID self-authority, and P0-created keys fail.
- Preserve exact observed unit states including `ACCEPTED_PENDING_REVIEW`.

# LOOP

Repair only P0 inventory or composite serialization. External trust is not a P0
repair target: record it unavailable and stop the execution path honestly.
Retest bundle hash, schema, lifecycle, ownership, and P4 consumer binding.
