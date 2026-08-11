# N30_UNIT_GRAPH result

status: BLOCKED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N30_unit_graph.prompt.v1.md (f78e98cb44f95a2aa108e87301d3e5fcddd0924e68a47333181bf5ebcd7f5e3e)
generation: 6

The full per-unit topology of spec section 8.1 is now registered into N20's one
builder and the one production graph compiles for real with it: **32 nodes, 85
edges**, digest
`79e25311c7f554b8a73c154df84f4e8f0ba3671844b435abd0466444cbc42223`. Both `Send`
map/reduces, the D06/D06B source supersteps, D92's twelve validated deterministic
re-entry destinations, and the D05 -> D06 -> ... -> D15 -> M05 spine are wired,
and 42 of this node's tests pass in the hash-locked environment.

The node is nevertheless **BLOCKED**, because the path cannot be *executed*.
Four gaps outside this node's write set stop it, and the first of them stops
every Plan 26 episode, not just this path:

**No episode can complete D01.** LangGraph initializes a
`BinaryOperatorAggregate` channel to its annotation's empty value, so 17 of
`FactoryState`'s 19 `write_once` channels — including `run_id`, `mode` and
`effective_run` — hand the reducer a non-`None` `existing` on the node's *first*
write and raise `WriteOnceConflict`. This was invisible to every predecessor: N11
tested the reducer directly, N22 tested node bodies directly, and N20 compiled the
graph without ever invoking it. It surfaced here on the first real `invoke`.

The prompt's TEST 9 (interrupt/crash at every boundary) and TEST 1/4/6/7/8 are
therefore **not provable at all** right now, and this record says so rather than
substituting a mock for the run they require. Nothing below is asserted against a
stand-in graph: every passing assertion runs on the real compiled graph or a real
node body, and every failing behaviour is recorded as a named, owned blocker.

## Inputs

Predecessor result records consumed:

- `N00_BASELINE_FREEZE`: c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5
- `N10_DEPENDENCY_API`: 1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658
- `N11_STATE_REDUCERS`: e5ec425ff016d84fb220f8e518733f8b43db8d31e2d86b22fe5371be1b7e2d0c
- `N12_EVIDENCE_ARTIFACTS`: 6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f
- `N13_TRANSPORT_AUTH`: aacb3187bfe11f1e16b4eafebab6fba5a8ae7ba0136148b26fafac7f3adb2a71
- `N20_GRAPH_COMPILER`: 44d6109d51181090c5db299f1436c835d1c6cb407bb343c17701e4658b80d50d
- `N21_PERSISTENCE_RESUME`: 56ff6ede52eee5a462983b0b157a3a476b1767f1273183ee3deb0f1c3ddb00b4
- `N22_DETERMINISTIC_NODES`: b407400ea10fceff335daf9c1be61b9a7145b55f379f3f9197f719ddbe3b1d26
- `N23_MODEL_NODES`: d73373641ebfb1a1ad453f2056853ba0988d1cb0155dbec70c49e53a7bb5b44a

N20's Findings F-03 and F-04 were read as instructed and both were re-verified
here rather than taken on report; see Findings B-2 and B-3, which extend them.

Other frozen inputs read:

| Path | SHA-256 |
|---|---|
| `spec/langgraph_curriculum_factory.spec.v1.md` (sections 6.2, 6.3, 8.1, 8.2, 9, 10, 11.3, 11.4) | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| `implementation.graph.v2.yaml` | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| `contracts/baseline.v1.md` | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| `contracts/digest_algorithm.v1.md` | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| `contracts/erratum_checkpoint_ns_rename.v1.md` | 10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1 |
| `contracts/node_ownership.v1.md` | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| `contracts/result_record_schema.v1.md` | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| `contracts/shared_names_and_paths.v1.md` | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| `contracts/traceability_matrix.v1.md` | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| `runtime/langgraph_factory/routing.py` (N20, unmodified) | efcc6db169399129e4d3825b3fce5c11501a44a08f0e45433cfadcb7e6361bee |
| `runtime/langgraph_factory/state.py` (N11, unmodified) | 4c8942bf4a8c5ee42591531dc5e5b8c3fd668b58efd05aed4daeb623f507a298 |
| `runtime/langgraph_factory/nodes/__init__.py` (N22, unmodified) | 3580f09585a7f472b58a8d717cb27f1dca9e01588b710c9dbc93b8fb13c13906 |
| `runtime/langgraph_factory/model_nodes.py` (N23, unmodified) | 4cfa7de233e672cfa400315f5e6862563aec56b9cce5818e39e86f2f2f1df75b |
| `runtime/langgraph_factory/persistence.py` (N21, unmodified) | 35a4ff7602133ae80aa47986823c1f21392dc02bc76add5908b090d13cee4e17 |

## Outputs

| Path | SHA-256 |
|---|---|
| `runtime/langgraph_factory/unit_graph.py` | fe1226d42c97318f9ddefaefc802510cdb20593040ace894d078201bd040cd6f |
| `tests/runtime/test_plan26_unit_graph.py` | bcc2a678e70321fae13c9117d51b8271b13da2b7a4164067eb94ff0b64736da4 |
| `plans/26_langgraph_curriculum_factory/results/N30_UNIT_GRAPH.result.v1.md` | this file |

One path outside the graph's `writes` set was edited, under
`node_ownership.v1.md`'s explicit resolution ("N30 edits the same file rather
than creating a parallel one ... a sequential write to
`runtime/langgraph_factory/graph.py`"), which that contract self-describes as the
one resolution where it and `implementation.graph.v2.yaml` disagree:

| Path | SHA-256 | Change |
|---|---|---|
| `runtime/langgraph_factory/graph.py` | 3d56e7ff375aa89f3c76fd48932fa5affd195fe62137919c953e31769718bc32 | three edits only: import `unit_graph`; call `unit_graph.register_unit_path(builder, ...)` once at the end of `register_skeleton`; extend `_validate_topology`'s wired set with the unit path, and shrink `DEFERRED_TOPOLOGY` from 22 rows to the 3 that are still genuinely deferred (M06 -> N31, M07/M08 -> N32). No node body, guard, digest input, or `compile()` call was touched; there is still exactly one builder and one `compile()`. |

## Commands

| Command | Exit | Evidence |
|---|---:|---|
| `python3 -m venv /tmp/plan26_n30_verify` | 0 | (no output) |
| `/tmp/plan26_n30_verify/bin/python -m pip install --require-hashes -r requirements/plan26.lock` | 0 | langgraph 1.2.9, langgraph-checkpoint-sqlite 3.1.0, langgraph-checkpoint 4.2.0, jsonschema 4.26.0, PyYAML 6.0.3, Pillow 12.2.0, pytest 9.0.3 |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_unit_graph.py -q` | 0 | `results/evidence/N30_UNIT_GRAPH/venv_unit_graph.txt` (**42 passed**) |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/ -q -k plan26` | 1 | `results/evidence/N30_UNIT_GRAPH/venv_plan26_all.txt` (720 passed, 4 failed — 3 N20 rows this node supersedes by design, 1 pre-existing N21 row; see Findings B-4 and B-5) |
| `python3 -m pytest -q` (ambient) | 0 | `results/evidence/N30_UNIT_GRAPH/ambient_pytest.txt` (**746 passed, 5 skipped**, 282 subtests passed) |
| direct compile + topology dump (no pytest in the path) | 0 | `results/evidence/N30_UNIT_GRAPH/compiled_topology.txt` |
| blocker probe: registrability and catalogue rows | 0 | `results/evidence/N30_UNIT_GRAPH/blocker_probe_topology.txt` |
| blocker probe: runtime behaviour of the four gaps | 0 | `results/evidence/N30_UNIT_GRAPH/blocker_probe_runtime.txt` |
| blocker probe: affected `write_once` channels | 0 | `results/evidence/N30_UNIT_GRAPH/blocker_probe_write_once.txt` |

Ambient skip count moved 4 -> 5; the fifth is this node's own module-level skip,
the same technique N10/N20/N21 use. Ambient pass count is unchanged at 746, so
the baseline is not regressed.

## Tests

### LangGraph trace — the topology actually registered

```text
D04 -[fresh]->  D05_SELECT_NEXT_UNIT
D04 -[resume]-> D92_REENTER_VALIDATED_FRONTIER -> one of 12 deterministic frontiers

D05  -[unit_selected]->        D06_COMPILE_SOURCE_REQUESTS
D06  -[discovery_fanout]->     Send(M01_RESEARCH_UNIT_SOURCES) per request key
M01  -[discoveries present]->  D06B_RETRIEVE_SOURCE_CANDIDATES
D06B -[interpretation_fanout]->Send(M01_RESEARCH_UNIT_SOURCES) per retrieval group
M01  -[interpretations present]-> D07_CORRELATE_AND_ADMIT_SOURCES
D07  -[sources_admitted]->     M02_CREATE_UNIT_DOMAIN_DATA -> D08_VALIDATE_DOMAIN
D07  -[prerequisite_unresolved]-> D30_CLASSIFY_PREREQUISITE -> D98
D08  -[domain_admitted]->      M03_WRITE_UNIT_CONTENT -> D09_VALIDATE_CONTENT
D09  -[content_admitted]->     D10_COMPILE_VISUAL_BRIEFS
D10  -[deterministic_visual_fanout]-> Send(D11) per deterministic brief
D10  -[no_deterministic_visuals]->    D12_VISUAL_BARRIER_AND_JOIN
D11  --normal edge-->          D12_VISUAL_BARRIER_AND_JOIN
D12  -[model_visual_fanout]->  Send(M04_CREATE_UNIT_VISUALS) per model brief
M04  --normal edge-->          D12_VISUAL_BARRIER_AND_JOIN
D12  -[visuals_admitted]->     D13_RENDER_UNIT -> D14 -> D15
D15  -[review_packet_frozen]-> M05_REVIEW_ACTUAL_UNIT
every branch additionally -> D96 (graceful interrupt) and -> D98 (system failure)
```

Registered but deferred, each declared in `unit_graph.DEFERRED_EDGES` with its
owner so an unwireable destination cannot be silently dropped
(`test_deferred_edges_are_exactly_the_destinations_with_no_node_body` asserts the
set is exactly total):

| From | Guard value | To | Owner |
|---|---|---|---|
| D05 | `manifest_exhausted` | D24 | N32_WORKBOOK_TERMINALS |
| D08 | `domain_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D09 | `content_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D12 | `visuals_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D14 | `layout_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D92 | `incomplete_model_activation` | D91 | N23_MODEL_NODES |
| M01/M02/M03/M05 | `model_failure` | D91 | N23_MODEL_NODES |
| M05 | `review_returned` | D16 | N31_REPAIR_ACCEPTANCE |

The last row is this prompt's own declared frontier: "clean D16 evidence is a
handoff to N31". D16's PASS destination stays `D22_ACCEPT_UNIT` in N20's frozen
guard table, so N31 implements against a destination that already exists rather
than inventing one.

### Fan-out denominators (spec section 10)

| Join | Correlation key | Denominator source | Proven |
|---|---|---|---|
| source discovery | `(run_id, unit_id, source_epoch, request_id, "discover")` | D06 `source_denominators[unit/epoch].request_keys` | denominator computed by the real D06 body; **dispatch blocked** (B-2) |
| source retrieval | `(run_id, unit_id, source_epoch, request_id, retrieval_id)` | D06B `retrievals` | denominator computed; **dispatch blocked** (B-2) |
| source interpretation | `(..., retrieval_group_hash, "interpret")` | D06B, joined by D07 | join proven exact (4 mutations) |
| visual result | `(run_id, unit_id, content_head_hash, visual_epoch, brief_id)` | D10 `visual_denominators[unit/content_hash]` | join proven exact (4 mutations); D11 dispatch blocked, M04 dispatch blocked (B-2) |
| unit page review | `(run_id, unit_id, pdf_sha256, review_epoch, review_id, page_number, page_sha256, rubric_sha256)` | D14/D15 | **not reached** (B-1) |

`test_a_visual_fanout_dispatches_one_send_per_staged_denominator_member` runs the
real D12 body and the real `route_visual_barrier`: two staged model briefs produce
exactly two `Send` objects, all to `M04_CREATE_UNIT_VISUALS`. There is no case in
which a projection is created at routing time —
`test_a_fanout_with_no_staged_packet_refuses_to_improvise_one` asserts the guard
raises instead.

### Prompt TEST items

| # | TEST item | Verdict | Backing assertion |
|---:|---|---|---|
| 1 | Fresh bootstrap executes D01 once; resume uses D00R/D04 and validated state import | **BLOCKED (B-1)** | Not provable: D01's first write to any of 17 `write_once` channels raises `WriteOnceConflict`, so no episode reaches D02. `test_blocked_a_write_once_channel_refuses_its_own_first_write` demonstrates the mechanism on a two-node graph and the `X \| None` control case that works; `test_blocked_the_affected_write_once_channels_are_named` reads the 17 affected channels off the real compiled graph. No partial claim is made. |
| 2 | `one` mode computes complete prerequisite closure in manifest order | **PASS** | `test_one_mode_computes_the_complete_prerequisite_closure_in_manifest_order` over synthetic 1/7/41-unit chains (real D02 body, real manifest files), then feeds the closure to the real D05 body and the real `route_unit_selection`, which returns `D06_COMPILE_SOURCE_REQUESTS`; `test_a_diamond_closure_admits_each_ancestor_exactly_once` proves a diamond admits each ancestor once. |
| 3 | Source join rejects missing/extra/duplicate/stale/cross-unit members | **PASS** | `test_the_source_join_refuses_a_denominator_that_is_not_exact` (4 mutations against the real D07 body): `extra`, `stale` and `cross_unit` each yield `pending_failure` class `system`, cause `join`/`integrity`, and no `source_admissions`; `missing` yields `prerequisite_unresolved` routing to D30 (spec 6.2's own rule for a missing fact, which is a pause cause, not a join fault). `test_a_duplicate_fanout_member_with_a_different_body_is_an_integrity_failure` proves equal replay is idempotent and a differing duplicate raises `UnionConflict`. |
| 4 | Domain/content heads advance only after code-owned admission | **BLOCKED (B-1, B-2)** | The topology half is registered and asserted (`D07 -> M02 -> D08`, `D08 -> M03 -> D09`; no model node writes `artifact_heads`, which N23 already proved), but no head can be advanced in a run, because no run exists. Not claimed. |
| 5 | Visual denominator permutations produce identical admitted heads; empty subsets work | **PARTIAL** | Empty subset proven: `test_an_empty_deterministic_visual_subset_routes_straight_to_the_barrier` runs the real D10 body over content declaring only a model visual and the real guard returns `D12_VISUAL_BARRIER_AND_JOIN` directly — no sentinel member. Permutation-invariance of the *admitted head* is **not** proven, because admitting a head requires the D11/M04 dispatches that B-2 blocks. |
| 6 | Actual PDF/assets and positive contiguous page inventory are required | **BLOCKED (B-1, B-2)** | D13/D14 are wired (`D12 -> D13 -> D14`) but unreachable: they require an admitted visual head, which requires the blocked visual dispatch. No fixture PDF was rendered, and no claim about page inventory is made from one. |
| 7 | D15 packet contains exact PDF and every page once; M05 result matches it | **BLOCKED (B-1, B-2)** | `D15 -> M05` is registered; the packet cannot be produced (D14 unreachable) and cannot be dispatched (D15 stages no `pending_packet`). |
| 8 | D16 rejects any absent/failed/stale/`NOT_RUN` denominator member | **OUT OF SCOPE / BLOCKED** | D16's body is N31's per `node_ownership.v1.md`; this node's declared frontier is the handoff edge, asserted by `test_blocked_the_review_handoff_to_n31_is_declared_not_wired`. |
| 9 | Interrupt/hard crash at every node/map/barrier boundary resumes without repeated valid calls | **BLOCKED (B-1)** | Not provable and not simulated. A crash matrix requires committed checkpoints from a real run; B-1 prevents any run from committing a first superstep. What *is* proven structurally: D92 is wired to exactly 12 deterministic re-entry destinations, no model node is among them (`test_no_model_can_be_a_resume_reentry_destination`), and a stored model frontier is refused by the guard (`test_a_stored_model_frontier_is_refused_by_the_reentry_guard`). The crash matrix this record owes is empty, deliberately, rather than fabricated. |
| 10 | No capability, intermediate artifact, review, or D16 pass emits success | **PASS** | `test_no_node_in_this_path_can_emit_a_product_success_terminal`: no node module reachable from this path names `UNIT_ACCEPTED` or `COMPLETE` (word-bounded, so the join verdict `INCOMPLETE` is not a false hit), and neither `D22_ACCEPT_UNIT` nor `D24_PROVE_EXACT_MANIFEST_COVERAGE` is in the wired path or in any deferred destination. `test_the_model_path_uses_only_a_test_transport_and_no_product_output_root` confirms a fake transport is reachable only through `build_test_model_node_context` and that `build_model_node_context` refuses it. |

Totals in the hash-locked environment: **42 passed, 0 failed, 0 skipped** for this
node's file. Of the ten prompt TEST items, 3 PASS, 1 PARTIAL, 5 BLOCKED, 1 out of
scope by ownership.

### Artifact tree

No product artifact tree was produced. This node rendered no PDF, wrote no
evidence record, and created no output root beyond ephemeral `tempfile` roots for
the SqliteSaver the builder opens. That is the honest consequence of B-1: an
artifact tree here would have to be built by calling node bodies directly, which
is exactly the "bypasses LangGraph" stop condition in this prompt's LOOP.

### Crash matrix

Empty. See TEST 9.

## Findings

- **B-1 (BLOCKING, new, highest severity) — `state_or_reducer` -> N11_STATE_REDUCERS.**
  Fingerprint `plan26/n30/write-once-channel-default-conflict`.
  Evidence key: `runtime/langgraph_factory/state.py:85-109` (19 `write_once`
  channel declarations) against `runtime/langgraph_factory/reducers.py:185-205`
  (`write_once`), observed through
  `langgraph.channels.binop.BinaryOperatorAggregate`.
  LangGraph constructs a `BinaryOperatorAggregate`'s initial value from the
  annotation when the annotated type is zero-arg constructible, so a channel
  declared `Annotated[str, write_once]` starts at `""` and one declared
  `Annotated[Record, write_once]` starts at `{}`. `write_once` then sees
  `existing` is not `None` and not equal, and raises `WriteOnceConflict` on the
  node's **first** write. Reproduced minimally
  (`evidence/N30_UNIT_GRAPH/blocker_probe_write_once.txt` and
  `test_blocked_a_write_once_channel_refuses_its_own_first_write`), and the
  affected set read off the real compiled production graph is exactly 17 channels:
  `bootstrap_kind`, `contract_version`, `run_id`, `created_at`, `engine_root`,
  `curriculum_root`, `active_manifest_path`, `output_root`, `mode`,
  `frozen_inputs`, `frozen_digest`, `frozen_executable_identities`,
  `external_authorizations`, `effective_run`, `episode_id`,
  `checkpoint_thread_id`, `checkpoint_namespace`.
  The two unaffected ones (`requested_unit_id`, `resume_from`) are declared
  `X | None`, which LangGraph cannot default-construct, so the channel stays at
  its `MISSING` sentinel and the first write bypasses the operator entirely. That
  is both the diagnosis and the smallest available fix: annotate the 17 channels
  `X | None`, or teach `write_once` to treat the channel's declared empty default
  as absent. The `| None` route is proven working by the control case in the same
  test; the reducer route needs care so that an intentional empty-list write is
  still distinguishable from an unset channel.
  Why no predecessor caught it: N11 tested `write_once` as a function, N22 tested
  node bodies as functions, and N20 compiled the graph but never invoked it. It is
  observable only from a real `invoke`, which is what this node attempted first.
  Consequence: **no Plan 26 episode can execute D01**, so N30, N31, N32, N40, N50
  and N60 are all blocked behind it.

- **B-2 (BLOCKING) — `deterministic_node` -> N22_DETERMINISTIC_NODES.**
  Fingerprints `plan26/n30/model-packet-not-staged`,
  `plan26/n30/visual-fanout-packet-not-staged`. This is N20's F-04, verified and
  found to be wider than F-04 stated.
  F-04 named D06, D06B and D10. Two more classes of dispatch have the same gap:
  (a) D07 -> M02, D08 -> M03 and D15 -> M05 are *plain* conditional edges, and a
  conditional edge that names a node hands the target the whole `FactoryState`;
  every N23 adapter requires a packet carrying a D90 `reservation`, a
  `correlation` (`run_id`, `episode_id`, and a `correlation_key` for the fan-out
  jobs) and its spec section 9 projection, so the dispatch fails with
  `AttemptNotReserved` / `ProjectionViolation`
  (`test_blocked_a_model_node_on_a_plain_edge_receives_no_reservation`).
  (b) D12 *does* stage a packet, but its members are bare brief records; `Send`
  delivers each member as the worker's entire input, and M04 requires a
  `brief`/`permitted_facts`/`visual_contract` packet, so the staged member is
  rejected before any process starts
  (`test_blocked_the_staged_m04_briefs_are_not_m04_packets`).
  Required rework, precisely: add `pending_packet` to the authorized `outputs` of
  `D06_COMPILE_SOURCE_REQUESTS`, `D06B_RETRIEVE_SOURCE_CANDIDATES`,
  `D07_CORRELATE_AND_ADMIT_SOURCES`, `D08_VALIDATE_DOMAIN`,
  `D10_COMPILE_VISUAL_BRIEFS` and `D15_FREEZE_UNIT_REVIEW_PACKET`; have each stage
  the worker projection its dispatch needs; widen D06/D06B/D07/D08/D15's
  authorized `inputs` with the fields the correlation needs (`run_id`,
  `episode_id`, and `effective_run` for D07); and change D12's staged members from
  briefs to M04 packets. `test_blocked_no_dispatching_node_authorizes_a_worker_packet`
  parametrizes all six rows and fails the moment any of them is fixed, so the
  rework cannot land unnoticed.
  This node deliberately did **not** work around it by materializing projections
  inside `routing`/`unit_graph`: spec section 10 requires the denominator to be
  persisted before dispatch, and a projection invented at routing time is one no
  denominator committed to — the exact failure N20's F-04 warned against.

- **B-3 (BLOCKING) — `model_node_or_projection` -> N23_MODEL_NODES.**
  Fingerprint `plan26/n30/d90-d91-not-registrable`. This is N20's F-03, verified
  unchanged (`model_nodes.py` hash `4cfa7de2...`), and the coordination workaround
  the task description offered was tested and found unavailable.
  `reserve_model_attempt(state, *, job_id, correlation_key, activation_id, ...)`
  and `classify_model_failure(failure, *, attempts_used, ...)` are keyword-only
  after the first parameter, so neither is an `add_node` callable. A thin wrapper
  authored in `unit_graph.py` does **not** work: N20's `validate_bindings`
  restricts a production binding to `runtime.langgraph_factory.nodes` and
  `runtime.langgraph_factory.model_nodes` and rejects anything else by stable ID
  (`N20-BIND-PLACEHOLDER`), proven by
  `test_a_node_body_authored_in_the_unit_path_module_is_refused`. Laundering the
  wrapper past that guard (by pointing `node_body` at N23's helper) was rejected as
  a deliberate choice: the registered callable would be this module's, and the
  binding audit would then record the wrong owner for real logic.
  Required rework: export `D90_RESERVE_MODEL_ATTEMPT` and
  `D91_CLASSIFY_MODEL_FAILURE` from `model_nodes.py` as `(state, context) ->
  update` callables, with D90 able to mint one reservation per fan-out member (the
  M01 discovery and M04 visual maps need N reservations, not one).
  Consequence while open: every model node's failure edge and D92's
  `incomplete_model_activation` edge have no destination, so a model transport
  failure or an interrupted activation cannot be classified.

- **B-4 (non-blocking, caused by this node) — `topology_or_guard` -> N20_GRAPH_COMPILER.**
  Fingerprint `plan26/n30/n20-skeleton-scoped-tests-superseded`.
  Three N20 tests assert properties true only of a skeleton with no unit path, and
  are now false by design:
  `test_an_unwired_undeclared_node_fails_the_build_by_stable_id` (pops
  `D13_RENDER_UNIT` from `DEFERRED_TOPOLOGY`, which no longer contains it),
  `test_the_skeleton_contains_no_cycle_and_every_deferred_cycle_crosses_a_counter`
  (the path is now cyclic — `D06B -> M01 -> D06B` is spec 8.1's own discovery
  superstep), and `test_the_skeleton_registers_no_send_fanout` (two `Send`
  fan-outs are now registered, which is this node's purpose).
  `tests/runtime/test_plan26_topology.py` is N20's write set, not this node's, so
  it was not edited. The narrow rework is to re-scope these three: pick a node
  still in `DEFERRED_TOPOLOGY` (M06/M07/M08) for the first; assert every cycle
  crosses an exhaustion guard rather than that no cycle exists, for the second;
  and assert the fan-out shape rather than its absence, for the third. Ambient is
  unaffected — the file self-skips without the lock installed — so this is red only
  in the hash-locked environment.

- **B-5 (non-blocking, pre-existing, discovered here) — `checkpoint_or_resume` -> N21_PERSISTENCE_RESUME.**
  Fingerprint `plan26/n30/erratum-under-applied-persistence-state-update`.
  Evidence key: `runtime/langgraph_factory/persistence.py:1264` and
  `tests/runtime/test_plan26_persistence.py:1244`.
  `EpisodeInvocation.as_state_update()` still emits the key `"checkpoint_ns"`,
  which is no longer a `FactoryState` channel after the erratum renamed it
  `checkpoint_namespace`. N20's generation-5 audit checked `persistence.py`'s
  surviving `checkpoint_ns` occurrences and classified them all as the LangGraph
  invoke-config key or its dataclass field; line 1264 is neither — it is a
  *state update* key, so the erratum's own distinction puts it in scope for the
  rename. N21's own test asserts the stale name and its subtest
  `field='checkpoint_ns'` currently fails in the hash-locked environment. Not
  caused by this node (its file was read, never modified) and not blocking it,
  but it means a prepared episode's seed update names a channel the graph does not
  have.

## Invalidated descendants

None. No predecessor artifact was modified except `graph.py`, whose edit is the
additive registration `node_ownership.v1.md` assigns to this node; N20's own
`graph.py`-derived claims (single builder, single `compile()`, binding validation,
guard-table totality, digest determinism) are all re-verified green by its
remaining 35 tests. B-4 records the three N20 *tests* this node supersedes, which
is a re-scoping obligation rather than an invalidation of N20's verdict.

N31 and N32 are not invalidated but are gated: both are blocked behind B-1, and
N31 additionally needs B-3 before it can wire M06's failure edge.

## Hashes

| Artifact | SHA-256 |
|---|---|
| `runtime/langgraph_factory/unit_graph.py` | fe1226d42c97318f9ddefaefc802510cdb20593040ace894d078201bd040cd6f |
| `runtime/langgraph_factory/graph.py` | 3d56e7ff375aa89f3c76fd48932fa5affd195fe62137919c953e31769718bc32 |
| `tests/runtime/test_plan26_unit_graph.py` | bcc2a678e70321fae13c9117d51b8271b13da2b7a4164067eb94ff0b64736da4 |
| `runtime/langgraph_factory/routing.py` | efcc6db169399129e4d3825b3fce5c11501a44a08f0e45433cfadcb7e6361bee |
| `runtime/langgraph_factory/state.py` | 4c8942bf4a8c5ee42591531dc5e5b8c3fd668b58efd05aed4daeb623f507a298 |
| `runtime/langgraph_factory/nodes/__init__.py` | 3580f09585a7f472b58a8d717cb27f1dca9e01588b710c9dbc93b8fb13c13906 |
| `runtime/langgraph_factory/model_nodes.py` | 4cfa7de233e672cfa400315f5e6862563aec56b9cce5818e39e86f2f2f1df75b |
| `runtime/langgraph_factory/persistence.py` | 35a4ff7602133ae80aa47986823c1f21392dc02bc76add5908b090d13cee4e17 |
| `implementation.graph.v2.yaml` | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| `prompts/N30_unit_graph.prompt.v1.md` | f78e98cb44f95a2aa108e87301d3e5fcddd0924e68a47333181bf5ebcd7f5e3e |
| `spec/langgraph_curriculum_factory.spec.v1.md` | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| `contracts/baseline.v1.md` | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| `contracts/digest_algorithm.v1.md` | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| `contracts/erratum_checkpoint_ns_rename.v1.md` | 10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1 |
| `contracts/node_ownership.v1.md` | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| `contracts/result_record_schema.v1.md` | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| `contracts/shared_names_and_paths.v1.md` | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| `contracts/traceability_matrix.v1.md` | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| `results/N00_BASELINE_FREEZE.result.v1.md` | c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5 |
| `results/N10_DEPENDENCY_API.result.v1.md` | 1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658 |
| `results/N11_STATE_REDUCERS.result.v1.md` | e5ec425ff016d84fb220f8e518733f8b43db8d31e2d86b22fe5371be1b7e2d0c |
| `results/N12_EVIDENCE_ARTIFACTS.result.v1.md` | 6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f |
| `results/N13_TRANSPORT_AUTH.result.v1.md` | aacb3187bfe11f1e16b4eafebab6fba5a8ae7ba0136148b26fafac7f3adb2a71 |
| `results/N20_GRAPH_COMPILER.result.v1.md` | 44d6109d51181090c5db299f1436c835d1c6cb407bb343c17701e4658b80d50d |
| `results/N21_PERSISTENCE_RESUME.result.v1.md` | 56ff6ede52eee5a462983b0b157a3a476b1767f1273183ee3deb0f1c3ddb00b4 |
| `results/N22_DETERMINISTIC_NODES.result.v1.md` | b407400ea10fceff335daf9c1be61b9a7145b55f379f3f9197f719ddbe3b1d26 |
| `results/N23_MODEL_NODES.result.v1.md` | d73373641ebfb1a1ad453f2056853ba0988d1cb0155dbec70c49e53a7bb5b44a |
| `evidence/N30_UNIT_GRAPH/venv_unit_graph.txt` | 4061f41c09f3127a2af2a21fc0d63d814ad749628bd1c10594a02bfc2a80ba6d |
| `evidence/N30_UNIT_GRAPH/venv_plan26_all.txt` | b1b1b63c39343c52b148d2498839c17809a24a4aa999355fc7ffb3975877fff8 |
| `evidence/N30_UNIT_GRAPH/ambient_pytest.txt` | e5c84ea80e865d04febcb161356baa334631801e7b451d62043eb9a60d6d53af |
| `evidence/N30_UNIT_GRAPH/compiled_topology.txt` | 91ef5bd6aa4cb71db835cfb046c008fa94001ec4a1d09c251288bede6a7cef9d |
| `evidence/N30_UNIT_GRAPH/blocker_probe_topology.txt` | 17bb27e5c488dbdb25d20ac0bf6fdce5b75a5bbe9590eeb692d5f9bc65135396 |
| `evidence/N30_UNIT_GRAPH/blocker_probe_runtime.txt` | 70f098382eb8ca748e87f95f14f9351e794f3ff55adfc503a0b9f3729c8f58fe |
| `evidence/N30_UNIT_GRAPH/blocker_probe_write_once.txt` | af83160bb32ef8b25c0c0b9fbc1bae7aa63d20cd6f06e37d44b6f7f27dd8bc41 |

Compiled unit-path graph digest (real, reproducible, supersedes N20's
skeleton-only value for the extended topology):
`79e25311c7f554b8a73c154df84f4e8f0ba3671844b435abd0466444cbc42223`.
