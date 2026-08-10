# GOAL

Compile the frozen v1 graph plus the v2 overlay into one immutable effective
graph. Treat evidence sources, operator authorizations, consumed continuations,
registry resolvers, and compiled phase-subtask denominators as typed ports.

# TEST

- Reject every unused, missing-schema, meta-invalid, owner-invalid, or
  nonexistent resolver registry entry, including entries no node references.
- Compile each P0–P6 `required_subtask_ids` from the v2 node contract; ledgers,
  events, and manifests cannot shrink or replace it.
- Emit witness failures for nonexistent evidence bytes and for resume without
  external authorization plus atomic durable consumption.

# LOOP

Repair one IR owner or resolver, recompile the full effective graph, then rerun
registry, denominator, evidence, and resume mutations. Two repeated signatures
route to `SYSTEM_FAILURE`; no model-written prose can satisfy a compiler edge.
