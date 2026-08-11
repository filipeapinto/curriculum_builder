# GOAL

Implement `N11_STATE_REDUCERS` after N00. Create the complete Plan 26
`FactoryInput`, `FactoryState`, `FactoryOutput`, and frozen runtime context plus
pure reducer functions in `runtime/langgraph_factory/`.

Implement every field and mutation authority from spec section 5. Reducers are
type-checking and fail closed: write-once, append-unique, union-disjoint,
advance-head, replace-current, monotonic status/max, accept-once, and
episode-terminal-once. Persist JSON-compatible values and content-addressed
references only. Models never receive whole state.

# TEST

1. State inventory equals the spec and rejects missing/unknown fields.
2. Every field has one declared reducer and bounded node authorities.
3. Equal replay is idempotent where allowed; conflicting replay fails.
4. Disjoint union is associative/commutative under completion permutations.
5. Heads require immutable parent and exactly version+1.
6. Status/counters cannot regress; acceptance/terminal are once-only.
7. Runtime context is not checkpoint serializable and holds no model client.

Write `results/N11_STATE_REDUCERS.result.v1.md` with the field-authority table,
property-test evidence, commands, and hashes.

# LOOP

Patch one type, reducer, authority, or test at a time. Rerun conflict and
permutation tests after every change. Stop if reducer results depend on task
completion order or a model must merge/control state.

