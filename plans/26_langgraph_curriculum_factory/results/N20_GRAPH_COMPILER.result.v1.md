# N20_GRAPH_COMPILER result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N20_graph_compiler.prompt.v2.md (577a251c85b80d00fc0ae3929dc620a5c1b28b79ab970729a0b9428744f4f469)
generation: 6

Generation 6 is a narrow rework answering **N30_UNIT_GRAPH Finding B-4**
(fingerprint `plan26/n30/n20-skeleton-scoped-tests-superseded`, in
`results/N30_UNIT_GRAPH.result.v1.md`,
83c75350d23fadfafc804f4cc4d410a433ca43311eb83fa4c3acc65d3d152e87). N30 extended
this node's `graph.py`/`routing.py` exactly as designed — additive registration
of the section 8.1 per-unit path — which made three assertions in
`tests/runtime/test_plan26_topology.py` false *by design* rather than by defect:
they described a skeleton with no unit path, no `Send` fan-out, and no cycle.
Only the test file changed; `routing.py` is byte-identical to generation 5, and
`graph.py`'s new hash is N30's registration, not an edit by this node. The three
re-scoped tests now assert the same underlying N20 properties against the larger
topology that is actually compiled:

| Test | Was | Now |
|---|---|---|
| `test_an_unwired_undeclared_node_fails_the_build_by_stable_id` | popped `D13_RENDER_UNIT` out of `DEFERRED_TOPOLOGY`, a node N30 has since wired for real | reads the example node off the live `DEFERRED_TOPOLOGY` (`sorted(...)[0]`, currently `M06_REPAIR_NAMED_UNIT_ARTIFACT`), so the fixture follows whichever nodes N31/N32 still owe |
| `test_every_cycle_in_the_compiled_graph_crosses_an_exhaustion_guard` (was `test_the_skeleton_contains_no_cycle_and_every_deferred_cycle_crosses_a_counter`) | asserted the compiled graph contains no cycle | enumerates every simple cycle of the compiled graph and requires each to cross a deterministic bound and to have a product exit; the frozen guard rows for the not-yet-wired cycles are retained |
| `test_every_registered_fanout_has_the_worker_to_barrier_shape` (was `test_the_skeleton_registers_no_send_fanout`) | asserted zero `Send` usage | asserts the worker->barrier shape of every registered fan-out against the compiled graph, and that the shape table is exactly total over `FANOUT_GUARDS` |

The one production `StateGraph(FactoryState, context_schema=RuntimeContext,
input_schema=FactoryInput, output_schema=FactoryOutput).compile()` now compiles
for real against the unmodified production schema, and all 38 of this node's
tests pass unpatched in the hash-locked environment. Generation 5 is a
re-verification, not a rebuild: `graph.py`, `routing.py`, and
`test_plan26_topology.py` are byte-identical to generation 4 (hashes below
unchanged), because the blocker was never in this node's write set. The
generation-4 blocker (F-01) was resolved by N11/N22 under
`contracts/erratum_checkpoint_ns_rename.v1.md`, which renames the `FactoryState`
channel `checkpoint_ns` -> `checkpoint_namespace`.

The diagnostic pytest plugin used in generation 4 to size the blocker
(`diag_plugin.py`, plus its two diagnostic transcripts) has been deleted. It was
scaffolding for a BLOCKED report and no claim in this record rests on it; the
primary evidence below is the real, unpatched compilation and test run.

## Inputs

Predecessor result records consumed:

- `N10_DEPENDENCY_API`: 1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658
- `N11_STATE_REDUCERS` (generation 4): e5ec425ff016d84fb220f8e518733f8b43db8d31e2d86b22fe5371be1b7e2d0c
- `N22_DETERMINISTIC_NODES` (generation 4): b407400ea10fceff335daf9c1be61b9a7145b55f379f3f9197f719ddbe3b1d26
- `N23_MODEL_NODES`: d73373641ebfb1a1ad453f2056853ba0988d1cb0155dbec70c49e53a7bb5b44a

N11's and N22's generation-4 Findings were read and cross-checked against this
node's own re-verification: N11 renamed the `state.py:108` channel declaration
(and follows it through `FACTORY_STATE_FIELDS` / `FIELD_REDUCERS`, which derive
from `__annotations__`); N22 renamed exactly three call sites
(`nodes/inputs.py:887` update dict, `nodes/__init__.py:286` D04 `outputs`
tuple, and one test assertion). Both correctly left `persistence.py`'s
`config["configurable"]["checkpoint_ns"]` invoke-config key and `evidence.py`'s
JSONL record key alone. Independently confirmed here by grep: the only
surviving `checkpoint_ns` occurrences in the tree are in `persistence.py`
(lines 277, 686, 1114, 1186, 1248, 1264, 1324, 1368, 1399), all of them the
LangGraph config key or its dataclass field, none of them a `StateGraph`
channel.

Other frozen inputs read:

| Path | SHA-256 |
|---|---|
| `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` (sections 3.3, 4, 5.2, 6.2, 8.1, 8.2, 9, 10) | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| `contracts/baseline.v1.md` | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| `contracts/digest_algorithm.v1.md` | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| `contracts/node_ownership.v1.md` | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| `contracts/result_record_schema.v1.md` | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| `contracts/shared_names_and_paths.v1.md` | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| `contracts/traceability_matrix.v1.md` | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| `contracts/erratum_checkpoint_ns_rename.v1.md` | 10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1 |
| `runtime/langgraph_factory/state.py` (N11, gen 4) | 4c8942bf4a8c5ee42591531dc5e5b8c3fd668b58efd05aed4daeb623f507a298 |
| `runtime/langgraph_factory/nodes/__init__.py` (N22, gen 4) | 3580f09585a7f472b58a8d717cb27f1dca9e01588b710c9dbc93b8fb13c13906 |
| `runtime/langgraph_factory/model_nodes.py` (N23) | 4cfa7de233e672cfa400315f5e6862563aec56b9cce5818e39e86f2f2f1df75b |
| `runtime/langgraph_factory/persistence.py` (N21) | 35a4ff7602133ae80aa47986823c1f21392dc02bc76add5908b090d13cee4e17 |

## Outputs

| Path | SHA-256 |
|---|---|
| `runtime/langgraph_factory/graph.py` | 3d56e7ff375aa89f3c76fd48932fa5affd195fe62137919c953e31769718bc32 (was `b47b8786…` at generation 5; the delta is N30's additive unit-path registration, not an edit by this node) |
| `runtime/langgraph_factory/routing.py` | efcc6db169399129e4d3825b3fce5c11501a44a08f0e45433cfadcb7e6361bee |
| `tests/runtime/test_plan26_topology.py` | 844883016df59f9c54b2c4d24a312d1af5230754a40aa1b98c02cc6111de8a8c |
| `plans/26_langgraph_curriculum_factory/results/N20_GRAPH_COMPILER.result.v1.md` | this file |

## Commands

| Command | Exit | Evidence |
|---|---:|---|
| `python3 -m venv /tmp/plan26_n20_verify` (reused from generation 4) | 0 | (no output) |
| `/tmp/plan26_n20_verify/bin/python -m pip install --require-hashes -r requirements/plan26.lock` | 0 | `results/evidence/N20_GRAPH_COMPILER/venv_install.txt` |
| `/tmp/plan26_n20_verify/bin/python -m pytest tests/runtime/test_plan26_topology.py -q` | 0 | `results/evidence/N20_GRAPH_COMPILER/venv_topology_real.txt` (**38 passed** — real, unpatched, no plugin, no schema modification) |
| `python3 -m pytest -q` (ambient) | 0 | `results/evidence/N20_GRAPH_COMPILER/ambient_pytest.txt` (746 passed, 4 skipped, 282 subtests passed) |
| `python3 -m pytest tests/runtime/test_plan26_topology.py -q -rs` (ambient) | 0 | 1 skipped: "plan26 hash-locked environment not installed ... No module named 'langgraph'" — the intended module-level skip, same pattern as N10/N21 |

Generation 6 (B-4 rework), run in the hash-locked environment N30 built and left
installed (`/tmp/plan26_n30_verify`, same `requirements/plan26.lock`):

| Command | Exit | Evidence |
|---|---:|---|
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_topology.py -q` | 0 | `results/evidence/N20_GRAPH_COMPILER/venv_topology_gen6.txt` (**38 passed** against the now fully-wired unit path) |
| negative probes: each re-scoped assertion violated on purpose | 0 | `results/evidence/N20_GRAPH_COMPILER/negative_probes_gen6.txt` (all three fail as required — none of the re-scoped assertions passes vacuously) |
| `python3 -m pytest tests/runtime/test_plan26_topology.py -q -rs` (ambient) | 0 | 1 skipped, the same intended module-level skip |

The negative probes exist because "assert the property against a bigger graph"
is exactly the kind of re-scope that can quietly become a tautology. Removing
`D06B` from `FANOUT_GUARDS` leaves the discovery superstep unbounded and the
cycle test fails; naming a non-barrier as `M04`'s return, or dropping a
registered fan-out from the shape table, each fails the fan-out test.

At the time of this run, sibling rework for N30's B-1/B-2/B-3 was still landing,
so `tests/runtime/test_plan26_unit_graph.py` and
`test_plan26_deterministic_nodes.py` were red in the same environment. None of
those rows is `test_plan26_topology.py`, and none is in this node's write set.

Direct compilation proof, run outside pytest against the production builder with
no test harness in the path:

```text
$ /tmp/plan26_n20_verify/bin/python -c "... build_curriculum_factory_graph(...)"
COMPILED: CompiledStateGraph plan26_curriculum_factory
nodes: 30
```

No diagnostic plugin, monkeypatch, schema substitution, or skip is involved in
any verdict in this record.

Installed in the isolated environment: `langgraph 1.2.9`,
`langgraph-checkpoint-sqlite 3.1.0`, `langgraph-checkpoint 4.2.0`,
`jsonschema 4.26.0`, `PyYAML 6.0.3`, `Pillow 12.2.0`, `pytest 9.0.3`.

## Tests

| # | TEST item | Verdict | Backing assertion |
|---:|---|---|---|
| 1 | Exact available catalogue compiles; one START; only real D98 reaches END | **PASS** | `test_the_available_catalogue_compiles_against_real_node_callables`, `test_start_has_exactly_one_edge_and_d98_is_the_only_registered_end_edge`, `test_the_skeleton_wires_exactly_the_declared_edges` — all three pass against the real unmodified schema: 30 registered nodes (22 N22 + 8 N23), `START` has exactly one edge (`D00`), and `D98_WRITE_TERMINAL` is the only source of a *registered* END edge. |
| 2 | Missing/placeholder/test-only/duplicate/dangling/unreachable fails by stable ID | **PASS** | 7 tests: `N20-BIND-MISSING`, `N20-BIND-PLACEHOLDER` (x2: foreign module and test-local callable), `N20-BIND-UNCALLABLE`, `N20-BIND-DUPLICATE`, `N20-EDGE-DANGLING`, `N20-NODE-UNDECLARED`, plus `N20-GUARD-UNROUTED` for a declared guard value with no destination. All raise before `add_node`, so this is a builder guard, not a runtime crash. Generation 6: the `N20-NODE-UNDECLARED` case now reads its example node from the live `DEFERRED_TOPOLOGY` rather than naming `D13_RENDER_UNIT`, which N30 has since wired — the rejection is what is under test, not any one node, and the fixture now follows whatever N31/N32 still owe. |
| 3 | Every cycle crosses a deterministic counter/exhaustion guard | **PASS** (generation 6: re-scoped, no longer "scoped") | `test_every_cycle_in_the_compiled_graph_crosses_an_exhaustion_guard` enumerates every simple cycle of the really-compiled graph. Two exist, both worker/barrier supersteps N30 wired from spec 8.1: `D06B -> M01 -> D06B` (source interpretation) and `D12 -> M04 -> D12` (the visual barrier). Each is required to contain a bounding node — one declaring an exhaustion guard value whose destination leaves the cycle, or a fan-out dispatcher that refuses to dispatch again without a freshly staged worker projection (`RoutingViolation`, proven by calling the guard) — and to have at least one product exit outside itself, so no cycle is a closed trap. D06B and D12 are the bounds; the exits are `M01 -> D07` and `D12 -> D13`. The frozen guard rows for the cycles N31/N32 have yet to wire are still asserted: D17/D18/D29 `convergence_exhausted -> D98`, D90/D91 `exhausted -> D98`, and the unit loop closing only through `D23 -> D05`. Non-vacuity is evidenced, not assumed (`negative_probes_gen6.txt`). |
| 4 | Models have no edge to acceptance/routing/reduction/resume/terminal authority | **PASS** | `test_no_model_node_has_an_edge_to_an_authority_node` (compiled-edge half, now against the real compiled graph), `test_a_model_node_holds_no_acceptance_reduction_or_terminal_channel_authority`, `test_routing_never_lets_a_model_result_name_its_own_destination` (AST: no model-result guard reads any channel in `MODEL_NODE_WRITABLE_FIELDS` except presence of `source_discoveries`/`source_interpretations`, and names only code-owned destinations), and `test_a_stored_frontier_may_not_name_a_model_node`. See Findings F-02 for the deliberate reading of "reduction". |
| 5 | Source/visual fan-outs use supported `Send` worker->barrier; mixed joins fail | **PASS** (generation 6: re-scoped, no longer "scoped") | `test_every_registered_fanout_has_the_worker_to_barrier_shape` checks all four registered fan-outs against the compiled graph: D06/D06B -> M01, D10 -> D11, D12 -> M04. For each, the dispatcher has a compiled edge to a *single* worker, the guard emits exactly one `Send` per staged worker projection with the projection passed through unchanged, and the worker has a compiled edge to the deterministic barrier that owns the denominator (D06B, D07, D12, D12 respectively — never a model node). Each worker's forward successors, recovery destinations aside, are *exactly* its declared barriers, so a fanned-out worker rejoins a denominator and never fans out again. The shape table is asserted total over `FANOUT_GUARDS`, so a fan-out added without a declared shape fails rather than going unchecked. The prior guard-level tests are retained unchanged: `test_a_fanout_guard_emits_one_send_per_staged_worker_projection` and `test_a_fanout_guard_refuses_an_unstaged_or_mixed_dispatch`. |
| 6 | Empty subsets and arbitrary manifest lengths remain legal | **PASS** | Four tests: no unit/lesson identifier or manifest-length constant appears in `graph.py`/`routing.py` (AST + substring); an empty deterministic visual subset routes straight to the barrier; an exhausted manifest routes to coverage proof at any length; and `test_the_builder_registers_a_fixed_node_set_independent_of_any_manifest` confirms against the real compiled graph that the registered node set equals the frozen binding inventory with no per-unit node. |
| 7 | Identical real bindings yield identical digest; callable/schema/prompt drift changes it | **PASS** | All five digest tests pass against the real schema: two independent builds agree, and a changed callable binding, a changed reducer declaration, and a changed prompt file each change the digest; `test_the_digest_ignores_python_object_identity` pins that it is not keyed on object identity. **Production graph digest at generation 6: `d26798042b0499425055fa4eb995deb2071c00f07f520d4be1fcd3f85429125c`.** It moved from generation 5's `4b1f7242…` because N30 registered the per-unit path — the digest is keyed on topology, so a larger topology is a different graph, which is the property these tests exist to hold. Generation 4's provisional diagnostic value `58ef1bd4...` was computed over a patched schema and remains void. |
| 8 | Production imports contain no handwritten fallback controller | **PASS** | `test_production_graph_imports_contain_no_fallback_controller`: no import or textual reference to `runtime.curriculum_factory_graph`, `CurriculumFactoryGraph`, `session_bridge`, `test_simulated`, or `fallback_controller`, and none of the five forbidden model-invocation packages. `test_only_one_builder_and_one_compile_call_exist` asserts exactly one `build_*graph*` function and exactly one `.compile(` call in `graph.py`. |

Totals: **38 passed, 0 failed, 0 errors, 0 skipped** in the hash-locked
environment. The 38th test,
`test_the_state_schema_declares_no_langgraph_reserved_channel_name` — the
assertion that reported the generation-4 blocker — is now green, which is the
acceptance test for the erratum's rework and is retained as a standing
regression guard against any future reserved-name collision.

### Real binding inventory (30 callables, all production modules)

| Source | Node IDs |
|---|---|
| `runtime.langgraph_factory.nodes.inputs` (N22) | D00, D00R, D01, D02, D03, D04, D92, D96 |
| `runtime.langgraph_factory.nodes.sources` (N22) | D05, D06, D06B, D07, D30 |
| `runtime.langgraph_factory.nodes.domain` / `.content` (N22) | D08, D09 |
| `runtime.langgraph_factory.nodes.visuals` (N22) | D10, D11, D12 |
| `runtime.langgraph_factory.nodes.render` / `.review` (N22) | D13, D14, D15 |
| `runtime.langgraph_factory.nodes.terminal` (N22) | D98 |
| `runtime.langgraph_factory.model_nodes` (N23) | M01–M08 |

Absent by construction, not padded: D16–D29, D31, D32 (N31/N32 own the bodies)
and graph-registrable D90/D91 wrappers (see F-03).

### Topology actually registered

```text
START -> D00_BOOTSTRAP_EPISODE
D00  -[fresh]->            D01 -> D02 -> D03
D00  -[legal resume]->     D00R -> D03
D00  -[orphan recovery]->  D96 -> D98 -> END
D03  -[capabilities]->     D04
D04  -[fresh]->            D05     (frontier: outgoing edges owned by N30)
D04  -[resume]->           D92     (frontier: outgoing edges owned by N30)
every skeleton branch additionally -> D96 (graceful interrupt) and -> D98 (system failure)
```

This is the skeleton this node registers, and it is unchanged at generation 6.
What *has* changed is the graph the tests run against: N30 has since registered
the per-unit path into the same builder, so D05, D92, D06, D06B, D07, D08, D09,
D10, D11, D12, D13, D14, D15, D30 and M01–M05 have left `DEFERRED_TOPOLOGY` and
are wired for real. `DEFERRED_TOPOLOGY` now holds exactly M06
(`N31_REPAIR_ACCEPTANCE`), M07 and M08 (`N32_WORKBOOK_TERMINALS`), so an
undeclared unwired node still fails the build. The repair cycle and the whole
D24–D32 workbook branch remain **not** wired and are not claimed here.

### Guard and authority report

`routing.py` implements the complete spec 8.2 table: 39 named pure guard
functions over a frozen `GUARD_DESTINATIONS` table covering all 34 emitting
nodes, plus `DYNAMIC_GUARDS` (4 rows whose destination is state-carried and
validated against a model-node exclusion), `FANOUT_GUARDS` (4 `Send` rows), and
`MODEL_RESULT_DESTINATIONS` (7 rows; M01's two supersteps are resolved by result
presence). Ordering is failure-before-interrupt, deliberately: an episode that
broke *and* was asked to stop terminates as `SYSTEM_FAILURE`, not `INTERRUPTED`.
An undeclared guard value raises `RoutingViolation` rather than resolving to a
terminal, and `assert_guard_table_total()` runs inside the builder so that
disagreement fails compilation instead of waiting for a rare edge.

No model node is a source of any edge into acceptance (D22), checkpoint
initialization/correlation (D04, D23), unit selection (D05), workbook assembly
(D25), release (D32), resume re-entry (D92), or the terminal writer (D98/END).

## Findings

- **F-01 (RESOLVED at generation 5) — was `state_or_reducer` -> N11_STATE_REDUCERS.**
  `FactoryState.checkpoint_ns` collided with LangGraph 1.2.9's reserved channel
  set (`langgraph._internal._constants.RESERVED`), so
  `StateGraph(FactoryState, ...).compile()` raised
  `ValueError: Channel name 'checkpoint_ns' is reserved` before any Plan 26 code
  ran. Resolved by N11 (channel declaration) and N22 (three call sites) under
  `contracts/erratum_checkpoint_ns_rename.v1.md`: the channel is now
  `checkpoint_namespace`, value unchanged (`""`).
  Verified here, not taken on report: (a) the real builder compiles, (b) all 38
  tests pass unpatched, (c)
  `test_the_state_schema_declares_no_langgraph_reserved_channel_name` — the
  acceptance test named in generation 4 — is green, and it computes
  `set(FACTORY_STATE_FIELDS) & set(RESERVED)` dynamically rather than hardcoding
  the old name, so it will also catch `checkpoint_id` or `configurable` if a
  future channel ever takes one.
  This node's own write set required **no change**: the only textual
  `checkpoint_ns` in `graph.py` / `routing.py` / `test_plan26_topology.py` is a
  docstring in that test explaining which names LangGraph reserves, which is
  still factually correct and is deliberately retained.
  Fingerprint `plan26/n20/reserved-channel/checkpoint_ns` — closed.

- **F-02 (informational, resolved here) — spec 8.1 vs this prompt's TEST 4.**
  Spec 8.1 wires `M05_REVIEW_ACTUAL_UNIT -> D16_REDUCE_UNIT_EVIDENCE` and
  `M07 -> D28`, while this node's TEST 4 forbids a model edge to "reduction".
  Resolved in favour of the spec's explicit topology: a review is *evidence for*
  the code-computed denominator, and spec 8.1's own prohibition list names
  acceptance, terminal, checkpoint initialization, unit selection, workbook
  assembly, and release — not reduction. "Models hold no reduction authority" is
  therefore proven where it lives, as a channel-authority property
  (`test_a_model_node_holds_no_acceptance_reduction_or_terminal_channel_authority`:
  no model may write `deterministic_checks`, `artifact_heads`,
  `accepted_unit_receipts`, `cursor`, `resume_frontier`, or any terminal
  channel), not as edge adjacency. No rework requested.
  Re-verified at generation 5: unchanged, and TEST 4's compiled-edge half now
  runs against the really-compiled graph rather than a patched one.

- **F-03 (non-blocking) — `model_node_or_projection` -> N23_MODEL_NODES.**
  D90 and D91 exist only as helper functions (`reserve_model_attempt(state, *,
  job_id, correlation_key, activation_id, ...)`,
  `classify_model_failure(failure, *, attempts_used, ...)`), which are
  keyword-only and cannot be registered with `add_node`. `routing.py` declares
  their guard rows (`D90.exhausted`, `D91.retry/repair/system/exhausted`) so the
  destinations are frozen, but N30 cannot wire the repair cycle until N23 (or
  N30 by agreement) exposes `(state, context)` node callables for them.
  Not blocking N20: the skeleton wires neither node.
  Fingerprint `plan26/n20/d90-d91-not-registrable`.
  Re-verified at generation 5 against N23's current `model_nodes.py` (hash
  unchanged, `4cfa7de2...`): both signatures are still keyword-only after the
  first positional parameter (`model_nodes.py:692`, `model_nodes.py:759`), so
  the finding stands unmodified and is still owed to N23 or N30.

- **F-04 (non-blocking) — `deterministic_node` -> N22_DETERMINISTIC_NODES.**
  D06, D06B and D10 declare fan-out guards but their catalogue rows do not
  authorize `pending_packet`, so they stage no worker projections, while D12
  does (`{"dispatch": ..., "briefs": [...]}`). `routing.py`'s fan-out guards
  translate staged material one-for-one and raise `RoutingViolation` when it is
  absent, rather than materializing a projection at routing time that no
  denominator committed to (spec section 10). Before N30 can register the source
  and deterministic-visual `Send` edges, D06/D06B/D10 must stage their packets
  and have `pending_packet` added to their authorized outputs.
  Fingerprint `plan26/n20/fanout-packet-not-staged`.
  Re-verified at generation 5 against N22's generation-4 catalogue: reading
  `NODE_CATALOGUE[...].outputs` directly still gives `pending_packet` present
  for `D12_VISUAL_BARRIER_AND_JOIN` only, and absent for
  `D06_COMPILE_SOURCE_REQUESTS`, `D06B_RETRIEVE_SOURCE_CANDIDATES`, and
  `D10_COMPILE_VISUAL_BRIEFS`. The `checkpoint_namespace` rework touched only
  D04's row and did not disturb this, so the finding stands unmodified.

- **F-05 (informational) — LangGraph does not enforce reachability.**
  Verified empirically against 1.2.9: an unreachable node and a dead-end node
  both compile without error; only a conditional-edge target that names an
  unregistered node is rejected. The builder's own `N20-NODE-UNDECLARED` and
  `N20-EDGE-DANGLING` checks therefore carry that guarantee, and
  `compiled.get_graph()` draws a dead-end node as reaching `__end__` — which is
  why TEST 1 asserts the single *registered* END edge and then requires every
  other node drawn to `__end__` to be a declared N30 frontier.
  Still true at generation 5, and now load-bearing rather than hypothetical:
  TEST 1 makes that distinction on the real compiled graph's 30 nodes.

- **F-06 (informational) — LangGraph injects `Runtime`, not services.**
  Verified empirically: a node whose second parameter is unannotated receives
  its default (`None`), so N22's and N23's bodies would have run with
  `runtime_context=None` had `graph.py` registered them directly. The common
  node boundary in `graph.py` is what injects `RuntimeContext` from
  `Runtime.context`, marks a graceful interrupt observed at the atomic boundary,
  and classifies an unexpected exception as `pending_failure`
  (`class=system`, `cause=unhandled`) while re-raising LangGraph's own
  `GraphBubbleUp` control flow untouched.
  Still true at generation 5: the four boundary tests
  (`..._injects_the_runtime_context_langgraph_would_not`,
  `..._classifies_an_unexpected_exception_as_a_system_failure`,
  `..._graceful_signal_..._routes_through_the_interrupt_gate`,
  `..._a_classified_failure_outranks_a_graceful_interrupt`) all pass unpatched.

- **F-07 (RESOLVED at generation 6) — N30's B-4, `topology_or_guard`, caused by this node.**
  Fingerprint `plan26/n30/n20-skeleton-scoped-tests-superseded`. Three tests in
  this node's write set asserted properties of a skeleton with no unit path:
  a `DEFERRED_TOPOLOGY` fixture pinned to `D13_RENDER_UNIT`, "the compiled graph
  contains no cycle", and "no `Send` fan-out is registered". N30 wiring spec
  8.1's per-unit path made all three false without breaking anything — the
  additive registration is exactly what `contracts/node_ownership.v1.md` assigns
  to N30. Resolved by re-scoping the three assertions onto the compiled graph as
  it now stands (table at the head of this record) and adding negative probes so
  the wider assertions cannot pass vacuously. No production code changed; the
  properties under test are the same ones, held against a larger topology.
  The lesson worth carrying: an assertion phrased as "X is absent" is a
  statement about the *current* frontier, and a successor doing its job will
  falsify it. Phrase the invariant instead — "every X has shape S" — which is
  what these three now do.

## Invalidated descendants

None. This node has never modified a predecessor's artifact. Generation 5 changed
no code at all, and generation 6 changed only `tests/runtime/test_plan26_topology.py`
— no production module in this node's write set was edited, so no descendant's
inputs moved. The F-01 rework's own invalidation was recorded by N11 and N22 at
their generation 4.

## Hashes

| Artifact | SHA-256 |
|---|---|
| `runtime/langgraph_factory/graph.py` | 3d56e7ff375aa89f3c76fd48932fa5affd195fe62137919c953e31769718bc32 (was `b47b8786…` at generation 5; the delta is N30's additive unit-path registration, not an edit by this node) |
| `runtime/langgraph_factory/routing.py` | efcc6db169399129e4d3825b3fce5c11501a44a08f0e45433cfadcb7e6361bee |
| `tests/runtime/test_plan26_topology.py` | 844883016df59f9c54b2c4d24a312d1af5230754a40aa1b98c02cc6111de8a8c |
| `implementation.graph.v2.yaml` | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| `prompts/N20_graph_compiler.prompt.v2.md` | 577a251c85b80d00fc0ae3929dc620a5c1b28b79ab970729a0b9428744f4f469 |
| `spec/langgraph_curriculum_factory.spec.v1.md` | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| `contracts/baseline.v1.md` | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| `contracts/digest_algorithm.v1.md` | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| `contracts/node_ownership.v1.md` | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| `contracts/result_record_schema.v1.md` | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| `contracts/shared_names_and_paths.v1.md` | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| `contracts/traceability_matrix.v1.md` | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| `contracts/erratum_checkpoint_ns_rename.v1.md` | 10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1 |
| `runtime/langgraph_factory/state.py` | 4c8942bf4a8c5ee42591531dc5e5b8c3fd668b58efd05aed4daeb623f507a298 |
| `runtime/langgraph_factory/nodes/__init__.py` | 3580f09585a7f472b58a8d717cb27f1dca9e01588b710c9dbc93b8fb13c13906 |
| `runtime/langgraph_factory/model_nodes.py` | 4cfa7de233e672cfa400315f5e6862563aec56b9cce5818e39e86f2f2f1df75b |
| `runtime/langgraph_factory/persistence.py` | 35a4ff7602133ae80aa47986823c1f21392dc02bc76add5908b090d13cee4e17 |
| `results/N10_DEPENDENCY_API.result.v1.md` | 1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658 |
| `results/N11_STATE_REDUCERS.result.v1.md` | e5ec425ff016d84fb220f8e518733f8b43db8d31e2d86b22fe5371be1b7e2d0c |
| `results/N22_DETERMINISTIC_NODES.result.v1.md` | b407400ea10fceff335daf9c1be61b9a7145b55f379f3f9197f719ddbe3b1d26 |
| `results/N23_MODEL_NODES.result.v1.md` | d73373641ebfb1a1ad453f2056853ba0988d1cb0155dbec70c49e53a7bb5b44a |
| `evidence/N20_GRAPH_COMPILER/venv_install.txt` | 31bb4772eabad10cce59aa5be2c6be3fc3d25e925cd87a2d5eb3c70909effa8c |
| `evidence/N20_GRAPH_COMPILER/venv_topology_real.txt` | 8f43e90bfe5bb236d1c342ca85a0502229b25efcdbfc8c6d31f594159e54086c |
| `evidence/N20_GRAPH_COMPILER/ambient_pytest.txt` | 845db468fec82eec756226286db95c88c627eb41584370cc0d17ebd2a67bfa92 |

Generation 4's `diag_plugin.py`, `venv_topology_diagnostic.txt`, and
`diagnostic_topology.txt` were deleted, not merely de-listed: no verdict in
this record depends on them, and leaving a schema-patching plugin in an
evidence directory invites a later node to mistake it for a supported harness.

Production graph digest (over the real compiled graph, reproducible):
`4b1f7242be5b2f40ac789b38f154ca32d05ef91bd01bdb3745d93ba027fb7361`.
