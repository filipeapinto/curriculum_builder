# GOAL

Consume the composite P0 v3 state and migrate lifecycle and artifact contracts
without consulting the obsolete standalone baseline port.

# TEST

- P4 input schema is `p0_contract_bundle.schema.v3.json`; assurance and
  recomputed base hash are mandatory.
- Preserve `ACCEPTED`, `ACCEPTED_PENDING_REVIEW`, `BLOCKED`, and
  `SYSTEM_FAILURE`; pending review remains nonterminal.
- Every migrated output uses the P1 artifact registry and controller evidence
  path, media-type, schema, and signature rules.

# LOOP

Repair one migration mapping, then rerun composite-state, lifecycle, artifact,
and checkpoint tests. Missing assurance pauses before P2 and is never silently
dropped by P4.
