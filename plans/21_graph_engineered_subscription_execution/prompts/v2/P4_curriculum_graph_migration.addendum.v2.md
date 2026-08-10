# GOAL

Migrate the effective v2 graph while preserving every live lifecycle value and
making `ACCEPTED_PENDING_REVIEW` an explicit nonterminal unit state.

# TEST

- Existing `ACCEPTED`, `ACCEPTED_PENDING_REVIEW`, `BLOCKED`, and
  `SYSTEM_FAILURE` records round-trip without reinterpretation.
- Only P4 performs status migration; acceptance still requires the frozen judge
  join, and pending review cannot assemble or become complete.
- Every migrated phase uses its compiled subtask denominator and v2 evidence
  manifest admission.

# LOOP

Repair one status mapping or migration adapter, rerun lifecycle and checkpoint
fixtures, then every dependent acceptance test. Never coerce an unknown state;
route irreconcilable factory defects to `SYSTEM_FAILURE`.
