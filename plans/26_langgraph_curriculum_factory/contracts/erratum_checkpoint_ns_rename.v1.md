# Erratum: `FactoryState` channel renamed `checkpoint_ns` -> `checkpoint_namespace`

Frozen at generation 4, following N20_GRAPH_COMPILER's BLOCKED finding F-01.
This is an addendum, not a rewrite: `shared_names_and_paths.v1.md` and the
original N00 contract set are left as committed (their hashes remain valid
citations of what N10-N23 actually read), and this file is the one later
node must also read before touching anything named `checkpoint_ns`.

## The defect

`runtime/langgraph_factory/state.py`'s `FactoryState.checkpoint_ns` is a
TypedDict channel. LangGraph 1.2.9 reserves the channel name `checkpoint_ns`
internally (along with `checkpoint_id` and `configurable`); `StateGraph(
FactoryState, ...).compile()` raises `ValueError: Channel name 'checkpoint_ns'
is reserved` before any Plan 26 code runs. N11, N21, N22, and N23 each built
and passed their own isolated tests without ever constructing a real
`StateGraph(FactoryState, ...)`, so none of them could have observed this; it
only surfaces at real compilation, which is N20's job.

## The fix (frozen, binding)

The `FactoryState` channel is renamed `checkpoint_namespace`. Its value is
unchanged (`""`, the LangGraph root namespace). Every other reference to the
string `checkpoint_ns` in the codebase is a DIFFERENT thing and MUST NOT be
renamed:

- LangGraph's own invoke-config key, `config["configurable"]["checkpoint_ns"]`
  (spec section 11.1's exact invoke config, `persistence.py`'s `CHECKPOINT_NS`
  constant and every place it populates that config dict) — this is the
  framework's own hardcoded key name, not ours to choose, and is not a
  `StateGraph` channel so LangGraph's reserved-name check does not apply to
  it.
- `evidence.py`'s internal JSONL record schema
  (`"checkpoints": ("checkpoint_id", "checkpoint_ns", "state_digest",
  "evidence_ordinal")`) is a plain dict key in an append-only log, not a
  registered channel, and is unaffected.
- Any nested key inside another channel's payload (e.g. a dict stored under
  `resume_from` or `resume_frontier` that happens to carry a `checkpoint_ns`
  key describing the target LangGraph config) is not a top-level channel
  either and is unaffected — though node authors should prefer
  `checkpoint_namespace` there too for reading consistency where it is cheap
  to do so, this is not a correctness requirement.

Only a literal `FactoryState` field (`state.py`'s `TypedDict` line) and every
call site that builds or asserts a dict intended to satisfy that specific
channel (i.e. a state *update* — the top-level key a reducer will see, not a
LangGraph invoke config and not an evidence record) must change to
`checkpoint_namespace`.

## Known call sites requiring the rename (as of generation 4)

- `runtime/langgraph_factory/state.py:108` — the channel declaration itself.
- `runtime/langgraph_factory/nodes/inputs.py:887` — D04/D00R's episode-init
  state update dict.
- `runtime/langgraph_factory/nodes/__init__.py:286` — D04's `NodeSpec`
  declared `outputs` tuple (the projection/authority catalogue entry).
- `tests/runtime/test_plan26_state_reducers.py:60`,
  `tests/runtime/test_plan26_deterministic_nodes.py:1852` — assertions
  against the old field name.

A later node that finds another genuine `FactoryState`-channel call site
missed here should fix it under the same rework owner
(`state_or_reducer -> N11_STATE_REDUCERS` if the channel declaration itself
is implicated, or the node that owns the file with the stale reference
otherwise) and append a note to this erratum rather than opening a new
contract file.

## Traceability

Supersedes, for this one field only, `shared_names_and_paths.v1.md`'s line
"`checkpoint_ns` is always `""`" — read that sentence as describing the
LangGraph invoke-config key (still true, still spelled `checkpoint_ns`
because that is LangGraph's name for it), not the `FactoryState` channel
(now `checkpoint_namespace`). The two concepts sharing a near-identical name
across the framework boundary is exactly what produced this defect; this
erratum exists so the distinction is written down once instead of
re-derived, incorrectly, by a future node under time pressure.
