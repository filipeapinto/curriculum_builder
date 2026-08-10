# GOAL

Compile v1, v2, and v3 into one effective graph and validate that graph after
all overrides. Emit the complete artifact contract registry and fixed evidence
path resolvers.

# TEST

- Recompute the fixed 45-file behavioral-base digest before compilation.
- Apply composite P0 state, prompt addenda, outputs, registries, and exact
  hard-coded subtask sets; rerun all v1 reachability, ownership, state-port,
  failure-edge, context, and idempotency checks on the effective result.
- Reject output collision/removal, wrong addendum mapping, subtask shrink,
  unused/wrong-owner/wrong-type resolver, and missing artifact schema mapping.

# LOOP

Repair one compiler-owned mapping and rerun the complete effective graph plus
all mutations. Never let an overlay or registry validate itself. Repeated
failure routes to `SYSTEM_FAILURE`.
