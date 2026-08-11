# GOAL

Implement `N22_DETERMINISTIC_NODES` after N11/N12. Implement every deterministic
node D00–D98 as a bounded function with the exact authorized projection, typed
update, reducer authority, failure class, and outgoing-guard inputs in section 6.

Adapt reusable Plan 25 manifest/schema/check/render/visual/PDF/workbook logic
behind nodes without retaining orchestration loops. Deterministic nodes alone
own retrieval, admission, validation, joins, rendering, page inventory,
evidence reduction, repair planning/admission, acceptance, release, and terminal
decisions. No deterministic node has a prompt or calls a model transport.

# TEST

1. Exactly one implementation per D node and no undeclared deterministic node.
2. Projection and update fields equal the frozen node catalogue.
3. Expected failures become typed pending failures; unexpected failures route system failure.
4. Manifest closure/order is neutral for 1, 7, and 41-unit DAG fixtures.
5. Retrieval/admission, schema/verifier, checks, rendering, page inventory, and
   evidence reduction fail closed on stale/missing/invalid inputs.
6. Repair plans are one-owner/one-boundary with descendants/retests/bounds.
7. D22/D32/D98 cannot pass without recomputed complete current denominators.
8. Static scan finds no Arduino/unit-count/sequence constants in graph modules.

Write `results/N22_DETERMINISTIC_NODES.result.v1.md` with node-owner table,
adapter disposition, commands, and hashes.

# LOOP

Patch one node or deterministic adapter. Rerun catalogue/projection/authority
tests plus affected semantics. Stop if orchestration remains in an adapter, a
model is needed for deterministic authority, or curriculum constants are embedded.
