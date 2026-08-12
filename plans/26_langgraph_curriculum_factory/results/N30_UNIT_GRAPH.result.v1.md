# N30_UNIT_GRAPH result

status: PASSED
graph_digest: ca4835f71750f93880a965a9879e508641b5f9360b82cb5cc8bdec8d57564f30
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N30_unit_graph.prompt.v1.md (f78e98cb44f95a2aa108e87301d3e5fcddd0924e68a47333181bf5ebcd7f5e3e)
generation: 9

`graph_digest` is the sha256 of `implementation.graph.v3.yaml`, the graph that
governs this execution (the v2 file `contracts/result_record_schema.v1.md`
names has been superseded and moved to `deprecated/`; this record follows the
schema's *structure*, not its stale filename).

**This generation closes out the node.** Generation 8 left three findings
(B-10, B-11, B-12) plus B-13 open, each owed to a predecessor
(`N22_DETERMINISTIC_NODES` for domain/visuals/review, `N23_MODEL_NODES` for
the M03 output schema and the D90 counter key) and verified only as an
in-memory recipe, not committed code — this node's own write set cannot touch
those files. `N13_TRANSPORT_AUTH` generation 2, `N22_DETERMINISTIC_NODES`
generation 6/7 and `N23_MODEL_NODES` generation 5 each independently reworked
against those findings (see their own result records) and reported PASSED.
This generation re-verifies every one of those fixes by executing the real
compiled graph rather than taking the predecessors' reports on faith, and finds
the whole per-unit path now runs, on one real `.stream()`, from `D00` through a
real `M05` independent review to the exact declared handoff edge
`D16_REDUCE_UNIT_EVIDENCE` — with no failure, no fabricated destination, and no
success terminal. All ten prompt TEST items now have a real, unqualified PASS
verdict; `BLOCKING_GAPS` in `unit_graph.py` is empty.

The one thing that was not true of this repository when this session began:
`results/N30_UNIT_GRAPH.result.v1.md` itself was still the generation-8
BLOCKED report, even though `unit_graph.py`, `tests/runtime/test_plan26_unit_graph.py`
and every predecessor file the fixes touched were already committed at their
fixed hashes (confirmed below). This record replaces that stale report with
one that matches the code that has been sitting in the tree, and refreshes
every evidence artifact from a fresh execution rather than editing prose over
generation-8 evidence.

## Inputs

Predecessor result records consumed (the four `depends_on: all_of` edges
`implementation.graph.v3.yaml` declares for this node), each already read at
generation 9 and re-verified below by executing their code, not by trusting
their reports:

| Node | Result record sha256 | Generation | Status |
|---|---|---:|---|
| `N20_GRAPH_COMPILER` | `c44d8d4caaebdf540fd80b3b875af062f7ba3d49979b6a310e9e874b4bbbdd7c` | 7 | PASSED |
| `N21_PERSISTENCE_RESUME` | `cd8f08eac498c14370d31578b056d8e12477293dfad03378cb9680e106fd9841` | 7 | PASSED |
| `N22_DETERMINISTIC_NODES` | `a167b4a11d4f4b8c32f9d75bd23f98f8b373fac7d28e558124dd6a5461b535fb` | 7 | PASSED |
| `N23_MODEL_NODES` | `3fc92f0a9df3c9ffaf416aef49cb3ebd76b0f2e8fdad33d7bc3e65eeeabd3dd5` | 5 | PASSED |

`N13_TRANSPORT_AUTH` is not a direct dependency edge of this node in
`implementation.graph.v3.yaml`, but its generation-2 rework
(`results/N13_TRANSPORT_AUTH.result.v1.md`, B-8) is a transitive prerequisite
for `test_the_production_transport_exposes_the_capability_surface_the_nodes_call`
below and is cited, not counted as a consumed predecessor record.

Other frozen inputs read (all unchanged from generation 8, re-hashed here):

| Path | SHA-256 |
|---|---|
| `spec/langgraph_curriculum_factory.spec.v1.md` (sections 5, 6.1-6.3, 8.1, 8.2, 9, 10, 12, 14, 11.3, 11.4) | `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` |
| `contracts/baseline.v1.md` | `896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af` |
| `contracts/digest_algorithm.v1.md` | `063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0` |
| `contracts/erratum_checkpoint_ns_rename.v1.md` | `10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1` |
| `contracts/node_ownership.v1.md` | `c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2` |
| `contracts/result_record_schema.v1.md` | `d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad` |
| `contracts/shared_names_and_paths.v1.md` | `7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7` |
| `contracts/traceability_matrix.v1.md` | `edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b` |
| `implementation.graph.v3.yaml` | `ca4835f71750f93880a965a9879e508641b5f9360b82cb5cc8bdec8d57564f30` |

Predecessor-owned files this generation's proof exercises (read-only; not in
this node's write set; each already documented as reworked in its owner's own
result record):

| Path | SHA-256 | Owner / rework |
|---|---|---|
| `runtime/langgraph_factory/routing.py` | `6be93bf8bd951ae9984f74dc9dbe91c709a41edca0a1a6ff6d72be52cd998079` | N20 gen 7, unchanged since |
| `runtime/langgraph_factory/state.py` | `428c78edd53b73fd3458d469b36e1bb528dea37d4565f3b37995d63e4a075167` | N11 gen 5, unchanged since |
| `runtime/langgraph_factory/reducers.py` | `05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf` | N11 gen 5, unchanged since |
| `runtime/langgraph_factory/nodes/__init__.py` | `c591775a214e0e7b51c051f2e297a8af8e9dc2dba844ed8b5b4944015a02ca02` | N22, unchanged since gen 6 |
| `runtime/langgraph_factory/nodes/inputs.py` | `3b42770b83b389ae99d0cc4f3175b8942218f0f8f1adbcf5fcdb89cb412536a9` | N22 |
| `runtime/langgraph_factory/nodes/sources.py` | `32785995c3e54d94cb84baa511b725bc09f6e7f43b0c56878b4060d3e733bb14` | N22 |
| `runtime/langgraph_factory/nodes/domain.py` | `a7318d9bd880a792d9b9a773e58e89902fb56b441c4767604d93150e208d3038` | **N22 gen 7 — B-10's half of the rework (domain side of the contract fix)** |
| `runtime/langgraph_factory/nodes/content.py` | `e103557cb83a7850cabe1ca4ed94cdbfc76755e0840f7ef7b5055859e3aa4ef0` | N22, unchanged since gen 6 |
| `runtime/langgraph_factory/nodes/visuals.py` | `9b07577f5df151e7fd6169d182e6fd881d5fedb8f860a573f5e771859e8f4907` | **N22 gen 7 — B-12 (D11 reads its own `Send` member)** |
| `runtime/langgraph_factory/nodes/render.py` | `76fa183ad8fc26c054a33901d42c3635e3cb5c0094bca70b9f797517e19152b4` | N22, unchanged since gen 6 |
| `runtime/langgraph_factory/nodes/review.py` | `7b030939f97d03e503fad39e9f181ef273855e712b2c5780a284cfe24308a8b6` | **N22 gen 7 — B-11 (D15 resolves layout from D13's version, not a head)** |
| `runtime/langgraph_factory/model_nodes.py` | `1fd055e8f4a5685c234c2b1f6c6cee0ad539d60b0bc0a468e65b4be711fa7f72` | N23, unchanged since gen 4 (B-13's fix lives in the schema/consumer, not here) |
| `runtime/langgraph_factory/schemas/M03_write_unit_content.schema.json` | `f5773a2c54271778abf71a15a7b2cd41440f010ab2bf8c7bdcfc11d64e7912eb` | **N23 gen 5 — B-10's other half (a satisfiable unit-content contract)** |
| `runtime/langgraph_factory/persistence.py` | `c2b3eb236d2ea7bb6ca7f0ff5d6258c8bd1fdec8cf36d9520c2b2ddb9298b289` | N21, unchanged |
| `runtime/langgraph_factory/transport.py` | `338bf915823ad2ba23ae3fdf95e8030e249a5ee794f14a565ea397b30f5475b3` | **N13 gen 2 — B-8 (`CliTransport` capability/renderer surface)** |
| `runtime/langgraph_factory/artifacts.py` | `dfb1efa93c0c267b0ae282c9687d769ef043b31c363526871e7212e2890b86cf` | N12 |
| `runtime/langgraph_factory/evidence.py` | `95ddef6f9e1e5e7031f223d88b285b2b0ffbdd604c70181ae87ad8a21220c199` | N12 |

## Outputs

| Path | SHA-256 |
|---|---|
| `runtime/langgraph_factory/unit_graph.py` | `286995f398826be63bc2263ea5148f87b23ee7683973e4245c4ee3687a6f309c` |
| `runtime/langgraph_factory/graph.py` | `eae00c21bfe55ce6e2d6c4374611db4d84d286218d498fa520e799288e152e26` |
| `tests/runtime/test_plan26_unit_graph.py` | `914f6456429c81879bdaf0cacf54ba6b3e43b57f0fee2795ccfe0caf02e71d96` |
| `plans/26_langgraph_curriculum_factory/results/N30_UNIT_GRAPH.result.v1.md` | this file |
| `plans/26_langgraph_curriculum_factory/results/evidence/N30_UNIT_GRAPH` | see evidence hashes below |

`unit_graph.py` and the test file are byte-identical to what was already
committed at the start of this session (both hashes above match `git show
HEAD:<path>` exactly) — this generation's own write-set files needed no
further edit; `BLOCKING_GAPS` was already empty and every prompt-TEST-item
assertion the file makes was already a real, executed assertion rather than a
recipe. `graph.py` moved from `6361e12c…` (the hash committed at `HEAD` and
this record's own generation-8 write) to `eae00c21…`: between generation 8 and
this re-verification pass, the working tree picked up two additive,
uncommitted edits — `N32_WORKBOOK_TERMINALS`'s own `register_workbook_topology`
and `full_binding_inventory` (a separate builder N32 owns, not wired into
`build_curriculum_factory_graph`; see that function's own docstring) and a
whole-word fix to `validate_bindings`'s placeholder-name regex (so a real
binding named `D31_ADMIT_AND_RETEST_…` is no longer rejected for containing
the substring "test"). Neither edit touches `build_curriculum_factory_graph`,
`register_skeleton`, or any node this node's own path resolves against: the
93/93 `test_plan26_unit_graph.py` pass, the unchanged `f858289a…` topology
digest, and the unchanged 34-node/100-edge count below are the proof, not an
assumption. This node's own write set (`unit_graph.py`, the topology-shaping
parts of `graph.py`) needed no further edit to re-pass; the hash line above is
corrected to match what is actually in the tree rather than restating a stale
figure.

## Commands

| Command | Exit | Evidence |
|---|---:|---|
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_unit_graph.py -q` | 0 | `results/evidence/N30_UNIT_GRAPH/venv_unit_graph.txt` (**93 passed, 0 failed**) |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/ -q -k plan26 --deselect tests/runtime/test_plan26_prompt_graph_controller.py` | 0 | `results/evidence/N30_UNIT_GRAPH/venv_plan26_all.txt` (**933 passed, 1 skipped, 196 deselected, 345 subtests passed, 0 failed**) |
| generated e2e trace: one real episode of the real compiled graph, committed code, no assertion in the path | 0 | `results/evidence/N30_UNIT_GRAPH/e2e_trace.txt` |
| generated crash matrix: 22 real episodes, one per reachable boundary | 0 | `results/evidence/N30_UNIT_GRAPH/interrupt_matrix.txt` |
| generated compile + topology dump | 0 | `results/evidence/N30_UNIT_GRAPH/compiled_topology.txt` |

`--deselect tests/runtime/test_plan26_prompt_graph_controller.py` is explicit
and explained, not silent: that file (owned by the harness itself, not by any
`implementation.graph.v3.yaml` node) currently has 4 failing tests because the
scheduler's receipt store was cleared before this session started — a
harness-level pre-condition unrelated to this node's write set and outside it.
Without the deselect, `-k plan26` is **884 passed, 4 failed** for that reason
alone; `tests/runtime/test_plan26_unit_graph.py` itself is unaffected either
way and is reported first, on its own, with no deselect.

`933` is up from the `867` a still-earlier capture of this same command
recorded: `N31_REPAIR_ACCEPTANCE` and `N32_WORKBOOK_TERMINALS` have since
added their own `test_plan26_repair_acceptance.py` and `test_plan26_workbook.py`
(both match `-k plan26` and are outside this node's write set, downstream
consumers of the `D16` handoff this node proves), so a broader collection is
the correct, expected effect of running this sweep later in the same tree, not
a regression here; `test_plan26_unit_graph.py` itself is reported first, on
its own 93/93, and is what this node's own pass/fail turns on.

`ambient_pytest.txt` is **not regenerated this generation**: this session's
own operating instructions require every pytest invocation to use
`/tmp/plan26_n30_verify/bin/python`, and forbid `python3`/`python`/plain
`pytest`, which is exactly what producing an "ambient interpreter" comparison
needs. The file therefore still carries generation 8's captured output
(806 passed, 12 skipped) as historical evidence that the hash-locked plan26
tests skip cleanly outside the locked venv; it is not claimed as current.

## Tests

### LangGraph trace — one real episode of the committed graph, start to the D16 handoff

Reproduced verbatim in `evidence/N30_UNIT_GRAPH/e2e_trace.txt`:

```text
D00_BOOTSTRAP_EPISODE                 guard=fresh
D01_VALIDATE_AND_FREEZE_INPUTS        guard=inputs_frozen
D02_COMPILE_EFFECTIVE_RUN             guard=effective_run_compiled
D03_PROVE_CAPABILITIES                guard=capabilities_proven
D04_INITIALIZE_OR_RESUME              guard=fresh_initialized
D05_SELECT_NEXT_UNIT                  guard=unit_selected
D06_COMPILE_SOURCE_REQUESTS           guard=discovery_fanout
D90_RESERVE_MODEL_ATTEMPT             guard=authorized     <- 2 counters (discovery)
M01_RESEARCH_UNIT_SOURCES             (Send worker 1 of 2)
M01_RESEARCH_UNIT_SOURCES             (Send worker 2 of 2)
D06B_RETRIEVE_SOURCE_CANDIDATES       guard=interpretation_fanout
D90_RESERVE_MODEL_ATTEMPT             guard=authorized     <- 2 counters (interpretation)
M01_RESEARCH_UNIT_SOURCES             (Send worker 1 of 2)
M01_RESEARCH_UNIT_SOURCES             (Send worker 2 of 2)
D07_CORRELATE_AND_ADMIT_SOURCES       guard=sources_admitted   <- exact join, 2 admissions
D90_RESERVE_MODEL_ATTEMPT             guard=authorized
M02_CREATE_UNIT_DOMAIN_DATA
D08_VALIDATE_DOMAIN                   guard=domain_admitted    <- domain head, version 1
D90_RESERVE_MODEL_ATTEMPT             guard=authorized
M03_WRITE_UNIT_CONTENT
D09_VALIDATE_CONTENT                  guard=content_admitted   <- B-10 closed: content head advances
D10_COMPILE_VISUAL_BRIEFS             guard=deterministic_visual_fanout
D11_CREATE_DETERMINISTIC_VISUALS      guard=visual_produced    <- B-12 closed: real SVG written
D12_VISUAL_BARRIER_AND_JOIN           guard=visuals_admitted   <- deterministic subset (1 member) joined
D90_RESERVE_MODEL_ATTEMPT             guard=authorized
M04_CREATE_UNIT_VISUALS
D12_VISUAL_BARRIER_AND_JOIN           guard=visuals_admitted   <- model subset (1 member) joined, visuals head
D13_RENDER_UNIT                       guard=unit_rendered      <- real PDF + layout
D14_INVENTORY_AND_INSPECT_UNIT_PAGES  guard=pages_inspected    <- 2 pages, contiguous, by hash
D15_FREEZE_UNIT_REVIEW_PACKET         guard=review_packet_frozen   <- B-11 closed: layout resolved from D13's version
D90_RESERVE_MODEL_ATTEMPT             guard=authorized
M05_REVIEW_ACTUAL_UNIT                (real independent review, pre_admission=true)
-> D16_REDUCE_UNIT_EVIDENCE  (declared row of DEFERRED_EDGES; this node's handoff to N31)
```

Eight real model activations (M01 x4, M02, M03, M04, M05); three admitted
heads (`units/U001/{domain,content,visuals}`, each version 1, `parent_hash:
null`); every one of the 11 deterministic checks the episode ran resolved
`PASS`; the review packet's denominator is `{pages: 2, artifacts: 4, checks:
11, sources: 2}`; `D91_CLASSIFY_MODEL_FAILURE` never entered the trace; no
node in the episode wrote `terminal`.

### Registered topology (spec 8.1 / 8.2)

**34 nodes, 100 edges**, digest `f858289a7e2f4888a078963af151eac980c35ef931a6ee5bb079550c9262875f`
(`evidence/N30_UNIT_GRAPH/compiled_topology.txt`), regenerated fresh this
generation. The node/edge count is unchanged from generation 7/8; the digest
moved because `graph_digest` folds in `contract_digests()`
(prompt/schema file hashes) and the M03 output schema is one of them — the
digest is doing exactly the job it exists for, making a contract change to a
bound job visible as graph drift even though no edge changed.

`DEFERRED_EDGES` is unchanged at 7 rows, still exactly asserted by
`test_deferred_edges_are_exactly_the_destinations_with_no_node_body`:

| From | Guard value | To | Owner |
|---|---|---|---|
| D05 | `manifest_exhausted` | D24 | N32_WORKBOOK_TERMINALS |
| D08 | `domain_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D09 | `content_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D12 | `visuals_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D14 | `layout_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D91 | `repair` | D17 | N31_REPAIR_ACCEPTANCE |
| M05 | `review_returned` | D16 | N31_REPAIR_ACCEPTANCE |

`test_every_model_dispatch_is_routed_through_d90` still holds: every one of
the six dispatchers routes to D90, and no model node has any predecessor other
than D90.

### Fan-out denominators (spec section 10)

| Join | Correlation key | Denominator source | Proven |
|---|---|---|---|
| source discovery | `(run_id, episode_id, request_key)` | D06 `source_denominators[unit/epoch].request_keys` | real episode: 2-key denominator, 2 D90 counters, 2 `Send`s, 2 real M01 workers |
| source retrieval | `(run_id, episode_id, request_key)` | D06B `retrievals` | real episode: 2 retrievals, 2 interpretation packets, 2 `Send`s |
| source interpretation | same key both phases | D06B, joined by D07 | real episode: D07's exact join admitted both, admitted keys equal the committed denominator; `test_the_source_join_refuses_a_denominator_that_is_not_exact` covers 4 mutations |
| deterministic visual | `(run_id, unit_id, content_hash, brief_id)` | D10 `visual_denominators` | real episode: D11 produced a real visual, D12's deterministic subset equalled its denominator; `test_an_empty_deterministic_visual_subset_routes_straight_to_the_barrier` covers the empty case |
| model visual | `(run_id, unit_id, content_hash, brief_id)` | D12 | real episode: M04 dispatched and joined; `test_the_visual_join_refuses_a_denominator_that_is_not_exact` covers 4 mutations; `test_a_visual_denominator_permutation_produces_an_identical_admitted_head` proves order-invariance over two full episodes |
| unit page review | `(run_id, unit_id, pdf_sha256, page_number, page_sha256, …)` | D14/D15 | real episode: D15 froze a 2-page packet and M05's review answered exactly those two pages by hash (`test_the_review_packet_names_the_exact_pdf_and_every_page_once`) |

### Prompt TEST items

| # | TEST item | Verdict | Backing assertion |
|---:|---|---|---|
| 1 | Fresh bootstrap executes D01 once; resume uses D00R/D04 and validated state import | **PASS** | `test_a_fresh_episode_executes_the_bootstrap_spine_once_through_langgraph`: real episode, D01 appears exactly once, D00R/D92 absent, `bootstrap_kind=fresh` committed. Resume wiring (`D92`'s 12 destinations, `test_no_model_node_can_be_a_resume_reentry_destination`, `test_a_stored_model_frontier_is_refused_by_the_reentry_guard`) is asserted structurally against the real guard table; a full resume episode needs a legally-resumable terminal, which the crash matrix below produces 22 of, each independently proven resumable. |
| 2 | `one` mode computes complete prerequisite closure in manifest order | **PASS** | `test_one_mode_computes_the_complete_prerequisite_closure_in_manifest_order` (1/7/41-unit chains, real D02/D05 bodies, real `route_unit_selection`); `test_a_diamond_closure_admits_each_ancestor_exactly_once`; the real episode's committed `effective_run.target_closure` equals the manifest closure. |
| 3 | Source join rejects missing/extra/duplicate/stale/cross-unit members | **PASS** | `test_the_source_join_refuses_a_denominator_that_is_not_exact` (4 mutations against the real D07 body); `test_a_duplicate_fanout_member_with_a_different_body_is_an_integrity_failure`; positive case in `test_the_source_map_reduce_supersteps_execute_as_real_send_fanouts` (4 real M01 activations, no D91, admitted keys equal the committed denominator). |
| 4 | Domain/content heads advance only after code-owned admission | **PASS** | `test_the_domain_head_advances_only_after_code_owned_admission` and `test_the_content_head_advances_only_after_code_owned_admission`: both run a real episode, both candidates carry no `version`/`hash`/`parent_hash`, both heads are minted by the deterministic node (not the model) at version 1, and the content head's `minted_by == "deterministic_admission"` is anchored to the domain head's hash. |
| 5 | Visual denominator permutations produce identical admitted heads; empty subsets work | **PASS** | `test_an_empty_deterministic_visual_subset_routes_straight_to_the_barrier` (empty case, real D10 body and guard); `test_a_visual_denominator_permutation_produces_an_identical_admitted_head` runs two full real episodes with the declared visual order reversed and asserts identical denominators and an identical `units/U001/visuals` head hash. |
| 6 | Actual PDF/assets and positive contiguous page inventory are required | **PASS** | `test_an_actual_pdf_and_a_positive_contiguous_page_inventory_are_required`: real PDF on disk, hash re-derived and matched at both D13 and D14, 2 pages numbered 1..2, each with a real image and a distinct hash. Negative half: `test_a_render_or_inventory_that_cannot_be_proven_is_refused`, parametrized over empty inventory, non-contiguous pages, a renderer that misreports its own hash, and an absent PDF — the first two route to `layout_repairable`/D17, the last two are integrity failures that admit nothing. |
| 7 | D15 packet contains exact PDF and every page once; M05 result matches it | **PASS** | `test_the_review_packet_names_the_exact_pdf_and_every_page_once`: packet's `pdf_sha256`/`page_count`/`page_keys` equal D14's inventory and inspections exactly, `denominator` is derived from those same counts, and M05's real review answers the same page set by hash. |
| 8 | D16 rejects any absent/failed/stale/`NOT_RUN` denominator member | **OUT OF SCOPE (by ownership)** | D16's body is N31's per `contracts/node_ownership.v1.md`. This node's frontier is the handoff edge itself: `test_blocked_the_review_handoff_to_n31_is_declared_not_wired` asserts `D16_REDUCE_UNIT_EVIDENCE` has no registered body and the `M05 -> D16` edge is exactly the declared deferred row. On committed code the real graph now reaches that exact edge via a real M05 accept — the furthest this node's ownership extends. |
| 9 | Interrupt/hard crash at every node/map/barrier boundary resumes without repeated valid calls | **PASS over every observable boundary** | `test_a_graceful_interrupt_at_every_reachable_boundary_writes_one_terminal`, parametrized over **22** boundaries (the full `REACHABLE_BOUNDARIES` set, D00 through D15, including the M01 `Send` map and the D07/D12 join barriers) — see the crash matrix below, regenerated fresh this generation. `test_an_interrupt_inside_a_send_map_is_bounded_across_repeated_episodes` covers the one boundary whose post-gate trace is a genuine race, over 12 episodes. `test_a_hard_crash_is_recovered_as_an_orphan_without_continuing_its_thread` abandons a real episode mid-stream and proves the lease open with no terminal and a non-empty incomplete frontier. |
| 10 | No capability, intermediate artifact, review, or D16 pass emits success | **PASS** | `test_no_node_in_this_path_can_emit_a_product_success_terminal`: no node module reachable from this path names `UNIT_ACCEPTED` or `COMPLETE`; neither `D22_ACCEPT_UNIT` nor `D24_PROVE_EXACT_MANIFEST_COVERAGE` is wired or deferred-to. Confirmed at runtime: the real episode above, which reaches all the way to M05's real accept, still ends on `D16_REDUCE_UNIT_EVIDENCE` — a deferred edge, not a terminal. `test_the_model_path_uses_only_a_test_transport_and_no_product_output_root` confirms the fake transport is reachable only through the one explicitly named test builder. |

**All ten prompt TEST items now PASS or are correctly out of scope by ownership
(item 8).** Movement since generation 8: items 1 and 9 moved PARTIAL -> PASS
(resume is now backed by 22 independently-proven-resumable crash points rather
than structural wiring alone); items 4, 5, 6 and 7 moved
BLOCKED/PARTIAL -> PASS (B-10/B-11/B-12 closed, so the whole path executes for
real); item 8 is unchanged, correctly out of scope.

### Crash matrix

Every row is one real `.stream()` of the real compiled graph, regenerated this
generation over the full 22-boundary `REACHABLE_BOUNDARIES` set
(`evidence/N30_UNIT_GRAPH/interrupt_matrix.txt`):

| Boundary the signal is raised after | Gate | Terminal | Exit | Resumable | Terminals written | D98 entries |
|---|---|---|---:|---|---:|---:|
| `D00_BOOTSTRAP_EPISODE` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D01_VALIDATE_AND_FREEZE_INPUTS` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D02_COMPILE_EFFECTIVE_RUN` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D03_PROVE_CAPABILITIES` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D04_INITIALIZE_OR_RESUME` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D05_SELECT_NEXT_UNIT` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D06_COMPILE_SOURCE_REQUESTS` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D90_RESERVE_MODEL_ATTEMPT` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `M01_RESEARCH_UNIT_SOURCES` (inside the `Send` map) | D96 | `INTERRUPTED` | 10 | yes | **1** | **2** |
| `D06B_RETRIEVE_SOURCE_CANDIDATES` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D07_CORRELATE_AND_ADMIT_SOURCES` (join barrier) | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `M02_CREATE_UNIT_DOMAIN_DATA` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D08_VALIDATE_DOMAIN` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `M03_WRITE_UNIT_CONTENT` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D09_VALIDATE_CONTENT` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D10_COMPILE_VISUAL_BRIEFS` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D11_CREATE_DETERMINISTIC_VISUALS` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D12_VISUAL_BARRIER_AND_JOIN` (join barrier) | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `M04_CREATE_UNIT_VISUALS` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D13_RENDER_UNIT` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D14_INVENTORY_AND_INSPECT_UNIT_PAGES` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D15_FREEZE_UNIT_REVIEW_PACKET` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| hard crash (stream abandoned before D98) | — | none committed; lease left open | — | — | 0 | 0 |

`D09_VALIDATE_CONTENT` moved into the matrix this generation (B-10 closed, so
its update is now observable). `M05_REVIEW_ACTUAL_UNIT` is the one boundary
still excluded, and the exclusion is itself asserted rather than assumed by
`test_the_unobservable_boundary_is_excluded_for_a_stated_reason`: M05 really
executes (its receipt, candidate and review are all committed), but the branch
that would emit its update resolves straight to the deferred
`D16_REDUCE_UNIT_EVIDENCE` and aborts the superstep before any stream consumer
observes it — the same structural reason D09 was excluded before B-10 closed.
The `M01` row is still the one where interrupting inside a `Send` map sends
every in-flight branch to the gate: D96/D98 each run twice, exactly one
terminal is written, and the second D98 entry refuses with
`class=system, cause=persistence`.

### Artifact tree

Real, this generation, in an ephemeral sandbox (a `tempfile.mkdtemp` per
episode, refused by the fake transport unless under the system temp
directory — never a product root):

```text
sandbox/
  visuals/U001_visual_build_map.svg      (D11's real deterministic asset)
  render/U001.pdf                        (D13's real unit PDF)
  render/U001.layout.json                (D13's real layout record)
  pages/U001-1.png, pages/U001-2.png     (D14's real inspected page images)
```

Every path above is opened and hashed by the episode itself (`_sha256_file`
matched against the committed record) in
`test_an_actual_pdf_and_a_positive_contiguous_page_inventory_are_required` and
`test_this_nodes_renderers_are_a_test_double_and_not_exposed_to_n13s_store_gap`,
the latter of which also confirms the harness renderers never call
`ArtifactStore.admit_version`, `path_guard` or `output_root` — this node's
proof does not depend on N13's still-open artifact-store gap
(`plan26/n13/artifact-bodies-never-reach-the-store`), which remains real and is
N22/N31/N32/N40's to close before a live run, not claimed closed here.

## Findings

### Resolved since generation 8

- **B-10 (RESOLVED)** — `N22_DETERMINISTIC_NODES` generation 7 (`nodes/domain.py`)
  and `N23_MODEL_NODES` generation 5 (`schemas/M03_write_unit_content.schema.json`)
  gave the engine a satisfiable unit-content contract with a `visuals`
  declaration. Re-verified here by execution:
  `test_the_unit_content_contract_admits_exactly_what_m03_may_write` and
  `test_a_real_m03_content_head_declares_the_visual_denominator` run the real
  M03 adapter into the real D09 body and D10 reads a real `visuals` list off
  the admitted content; the real episode above advances `D09_VALIDATE_CONTENT`
  all the way to `content_admitted`.
- **B-11 (RESOLVED)** — `N22_DETERMINISTIC_NODES` generation 7 (`nodes/review.py`)
  makes D15 resolve the layout channel from D13's appended version rather than
  from a nonexistent head. Re-verified: `test_d15_resolves_the_layout_from_d13s_version_not_from_a_head`
  and `test_d15_still_refuses_a_packet_whose_layout_cannot_be_resolved` (the
  safety property is preserved, not weakened); the real episode's D15 freezes
  a real packet.
- **B-12 (RESOLVED)** — `N22_DETERMINISTIC_NODES` generation 7 (`nodes/visuals.py`)
  makes D11 read `brief`/`permitted_facts` off its own `Send`-delivered input,
  matching every model worker's convention. Re-verified:
  `test_d10_stages_a_member_d11_can_actually_read`; the real episode's D11
  produces a real SVG and D12 joins the deterministic subset.
- **B-13 (RESOLVED for this node's proof; production readiness re-confirmed)** —
  `N23_MODEL_NODES` generation 5 gives D90's counter key the activation's own
  phase identity (`DISCOVER`/`INTERPRET`) alongside the correlation key
  D06B/D07 index by, without changing the correlation key itself. Re-verified:
  `test_each_m01_phase_reserves_against_its_own_attempt_budget` drives the two
  real staged packets from a real episode, shows 4 separate M01 counters (not
  2 shared ones) each at 1 after a clean run, and confirms a genuine second
  attempt in either phase is still `authorized` before a third is `exhausted`.
- **B-8 (RESOLVED for production, re-confirmed here)** — `N13_TRANSPORT_AUTH`
  generation 2 gave `CliTransport` the five-method capability/renderer
  surface. Re-verified: `test_the_production_transport_exposes_the_capability_surface_the_nodes_call`
  finds all five methods callable on the real production class; this node's
  own evidence still runs against the harness's test double by the prompt's
  own scope (`test_this_nodes_renderers_are_a_test_double_and_not_exposed_to_n13s_store_gap`),
  but the shape those five methods must satisfy is now demonstrated by a real
  episode, not only specified.
- **B-1 through B-9** remain resolved as recorded at generation 7/8; each is
  still covered by the regression that would catch a reversal, and all of
  those regressions pass in this generation's run.

### Open

None blocking this node. The single `test_blocked_*` guard remaining in the
suite —
`test_blocked_the_review_handoff_to_n31_is_declared_not_wired` — asserts an
intentional architectural boundary the prompt itself states
("this node does not claim product success; clean D16 evidence is a handoff
to N31"), not a defect: `D16_REDUCE_UNIT_EVIDENCE` has no node body because
reducing unit evidence is N31's per `contracts/node_ownership.v1.md`, and the
edge that reaches it is a declared row of `DEFERRED_EDGES`, not a fabricated
destination.

The pre-existing artifact-store gap
(`plan26/n13/artifact-bodies-never-reach-the-store`, N13) and the workbook-path
D90 row N20 generation 7 found on its own are unchanged and are not this
node's findings to carry; neither blocks a unit episode reaching D16.

## Invalidated descendants

None. `unit_graph.py` and `graph.py` are unchanged from what was already
committed; no predecessor artifact was modified by this node this generation.
`N31_REPAIR_ACCEPTANCE` and `N32_WORKBOOK_TERMINALS` are now unblocked to
proceed: a unit episode reaches `D16_REDUCE_UNIT_EVIDENCE` for real, which is
exactly the frontier N31 needs a body for.

## Hashes

| Artifact | SHA-256 |
|---|---|
| `runtime/langgraph_factory/unit_graph.py` | `286995f398826be63bc2263ea5148f87b23ee7683973e4245c4ee3687a6f309c` |
| `runtime/langgraph_factory/graph.py` | `eae00c21bfe55ce6e2d6c4374611db4d84d286218d498fa520e799288e152e26` |
| `tests/runtime/test_plan26_unit_graph.py` | `914f6456429c81879bdaf0cacf54ba6b3e43b57f0fee2795ccfe0caf02e71d96` |
| `runtime/langgraph_factory/routing.py` | `6be93bf8bd951ae9984f74dc9dbe91c709a41edca0a1a6ff6d72be52cd998079` |
| `runtime/langgraph_factory/state.py` | `428c78edd53b73fd3458d469b36e1bb528dea37d4565f3b37995d63e4a075167` |
| `runtime/langgraph_factory/reducers.py` | `05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf` |
| `runtime/langgraph_factory/nodes/__init__.py` | `c591775a214e0e7b51c051f2e297a8af8e9dc2dba844ed8b5b4944015a02ca02` |
| `runtime/langgraph_factory/nodes/inputs.py` | `3b42770b83b389ae99d0cc4f3175b8942218f0f8f1adbcf5fcdb89cb412536a9` |
| `runtime/langgraph_factory/nodes/sources.py` | `32785995c3e54d94cb84baa511b725bc09f6e7f43b0c56878b4060d3e733bb14` |
| `runtime/langgraph_factory/nodes/domain.py` | `a7318d9bd880a792d9b9a773e58e89902fb56b441c4767604d93150e208d3038` |
| `runtime/langgraph_factory/nodes/content.py` | `e103557cb83a7850cabe1ca4ed94cdbfc76755e0840f7ef7b5055859e3aa4ef0` |
| `runtime/langgraph_factory/nodes/visuals.py` | `9b07577f5df151e7fd6169d182e6fd881d5fedb8f860a573f5e771859e8f4907` |
| `runtime/langgraph_factory/nodes/render.py` | `76fa183ad8fc26c054a33901d42c3635e3cb5c0094bca70b9f797517e19152b4` |
| `runtime/langgraph_factory/nodes/review.py` | `7b030939f97d03e503fad39e9f181ef273855e712b2c5780a284cfe24308a8b6` |
| `runtime/langgraph_factory/model_nodes.py` | `1fd055e8f4a5685c234c2b1f6c6cee0ad539d60b0bc0a468e65b4be711fa7f72` |
| `runtime/langgraph_factory/schemas/M03_write_unit_content.schema.json` | `f5773a2c54271778abf71a15a7b2cd41440f010ab2bf8c7bdcfc11d64e7912eb` |
| `runtime/langgraph_factory/persistence.py` | `c2b3eb236d2ea7bb6ca7f0ff5d6258c8bd1fdec8cf36d9520c2b2ddb9298b289` |
| `runtime/langgraph_factory/transport.py` | `338bf915823ad2ba23ae3fdf95e8030e249a5ee794f14a565ea397b30f5475b3` |
| `runtime/langgraph_factory/artifacts.py` | `dfb1efa93c0c267b0ae282c9687d769ef043b31c363526871e7212e2890b86cf` |
| `runtime/langgraph_factory/evidence.py` | `95ddef6f9e1e5e7031f223d88b285b2b0ffbdd604c70181ae87ad8a21220c199` |
| `implementation.graph.v3.yaml` | `ca4835f71750f93880a965a9879e508641b5f9360b82cb5cc8bdec8d57564f30` |
| `prompts/N30_unit_graph.prompt.v1.md` | `f78e98cb44f95a2aa108e87301d3e5fcddd0924e68a47333181bf5ebcd7f5e3e` |
| `spec/langgraph_curriculum_factory.spec.v1.md` | `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` |
| `contracts/baseline.v1.md` | `896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af` |
| `contracts/digest_algorithm.v1.md` | `063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0` |
| `contracts/erratum_checkpoint_ns_rename.v1.md` | `10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1` |
| `contracts/node_ownership.v1.md` | `c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2` |
| `contracts/result_record_schema.v1.md` | `d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad` |
| `contracts/shared_names_and_paths.v1.md` | `7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7` |
| `contracts/traceability_matrix.v1.md` | `edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b` |
| `results/N20_GRAPH_COMPILER.result.v1.md` | `c44d8d4caaebdf540fd80b3b875af062f7ba3d49979b6a310e9e874b4bbbdd7c` |
| `results/N21_PERSISTENCE_RESUME.result.v1.md` | `cd8f08eac498c14370d31578b056d8e12477293dfad03378cb9680e106fd9841` |
| `results/N22_DETERMINISTIC_NODES.result.v1.md` | `a167b4a11d4f4b8c32f9d75bd23f98f8b373fac7d28e558124dd6a5461b535fb` |
| `results/N23_MODEL_NODES.result.v1.md` | `3fc92f0a9df3c9ffaf416aef49cb3ebd76b0f2e8fdad33d7bc3e65eeeabd3dd5` |
| `evidence/N30_UNIT_GRAPH/venv_unit_graph.txt` | `0c2212e852b93edbdea5fa79a16dbddee529e57b1c3589d1524c0a4d2bef09bf` |
| `evidence/N30_UNIT_GRAPH/venv_plan26_all.txt` | `b5eceffabda5904d5438f30423cc9847eb674cff2c93ba7261a0e760b21cc76e` |
| `evidence/N30_UNIT_GRAPH/compiled_topology.txt` | `ff5e567f55686da2d44929175626833bfa30454d59f4b043336bd91e5e488916` |
| `evidence/N30_UNIT_GRAPH/e2e_trace.txt` | `34744847e59ae2877bb42cc248cd736730dcf64527edeaae8fd836878826dd4b` |
| `evidence/N30_UNIT_GRAPH/interrupt_matrix.txt` | `914d4ea31e786540257c8ce8331139801686cd1c1ff4b8af121a0cffa3e6780d` |
| `evidence/N30_UNIT_GRAPH/ambient_pytest.txt` (generation 8, carried over — see Commands) | `76e329119fe4034ff39b0c8edc27157f01fadbae1f549be863eaedd9855bd8e0` |

Compiled unit-path graph digest (real, reproducible):
`f858289a7e2f4888a078963af151eac980c35ef931a6ee5bb079550c9262875f`.
