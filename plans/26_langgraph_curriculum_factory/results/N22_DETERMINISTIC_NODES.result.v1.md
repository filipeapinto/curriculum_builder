# N22_DETERMINISTIC_NODES result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N22_deterministic_nodes.prompt.v2.md (dbc64fa8a419f0a2a3e41096b11b4b61bea9e153df113deecf8d39fa9fb2f744)
generation: 5

## Inputs

Predecessor result records consumed (`depends_on: [N11_STATE_REDUCERS, N12_EVIDENCE_ARTIFACTS]`, join `all_of`):

- `N11_STATE_REDUCERS`: c89f166596633e2027f04daa03fca9a33e9f23f2c1346f77817e44b8c03dc30e
- `N12_EVIDENCE_ARTIFACTS`: 6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f
- `N00_BASELINE_FREEZE` (transitive; source of the binding contracts below): c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5

Other frozen inputs read:

| Path | sha256 |
|---|---|
| `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` (sections 2.3, 5.1-5.2, 6.1-6.2, 8.1-8.2, 9, 12, 13, 14, 15) | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| `contracts/node_ownership.v1.md` | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| `contracts/shared_names_and_paths.v1.md` | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| `contracts/result_record_schema.v1.md` | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| `contracts/digest_algorithm.v1.md` | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| `contracts/baseline.v1.md` | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| `contracts/traceability_matrix.v1.md` | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| `runtime/langgraph_factory/state.py` (N11, post-erratum) | 4c8942bf4a8c5ee42591531dc5e5b8c3fd668b58efd05aed4daeb623f507a298 |
| `runtime/langgraph_factory/reducers.py` (N11) | 05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf |
| `contracts/erratum_checkpoint_ns_rename.v1.md` (generation 4) | 10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1 |

Plan 25 modules read for adaptation (read-only, not modified): `runtime/controller.py`,
`runtime/checks.py`, `runtime/routing.py`, `runtime/io.py`, `runtime/visual_maps.py`,
`runtime/lesson_render.py`, `runtime/pdf_inspect.py`, `runtime/curriculum_factory_graph.py`,
`runtime/langgraph_factory/evidence.py`, `runtime/langgraph_factory/artifacts.py`,
`runtime/langgraph_factory/transport.py`, `runtime/langgraph_factory/egress.py`.

## Outputs

| Declared `writes` path | Actual path | sha256 |
|---|---|---|
| `runtime/langgraph_factory/nodes` | `runtime/langgraph_factory/nodes/__init__.py` | 9f04100a02bfb1d5dcc5fd69e1fef4da8bc5def79690ced6494972023f1087c8 |
| | `runtime/langgraph_factory/nodes/inputs.py` | 0ba94888a1c601adbed50e477b37575788387bb4489e8a62363f230c622d5627 |
| | `runtime/langgraph_factory/nodes/sources.py` | 21ae3780bad01eada01ecd173783702787f4b766e9965e33f360c03b23832f39 |
| | `runtime/langgraph_factory/nodes/domain.py` | 89d6608a6fdd5ebf3c9ddb9b0f70a310d19bb283aa6145d3474e6e24594a5d93 |
| | `runtime/langgraph_factory/nodes/content.py` | 18fbe517a0c701fa24253cb47029b3525a79bd0e5a9b0ccf28845c43f621a937 |
| | `runtime/langgraph_factory/nodes/visuals.py` | 70d13f8e6d8ec96284dbc3ad6c3a0a31b803e7462fc2b349efbbffe4488693b8 |
| | `runtime/langgraph_factory/nodes/render.py` | 76fa183ad8fc26c054a33901d42c3635e3cb5c0094bca70b9f797517e19152b4 |
| | `runtime/langgraph_factory/nodes/review.py` | fd1b61f25cdf96a82b5f9307b1dd3dbeae9cd8b8eb4605ce182f7980e641cb5e |
| `runtime/langgraph_factory/terminal.py` | `runtime/langgraph_factory/nodes/terminal.py` (see finding F-01) | 66e7b92752d8ab8e0a93e00fc50114331f74f34538358b9b2938a6f02c17f28d |
| `tests/runtime/test_plan26_deterministic_nodes.py` | same | 47a56efa6e83642aec99b1a7683337af3c9ecd8ec34d1dab7ff611b29850c67e |
| `plans/.../results/N22_DETERMINISTIC_NODES.result.v1.md` | this file | (not self-hashed) |

4419 lines of production node code, 2578 lines of test.

## Node ownership

Exactly one implementation per node, resolved against `node_ownership.v1.md` (binding)
rather than the abbreviated list in the prompt. 22 D-nodes, not the 40 the prompt's GOAL
line implies (see finding F-02).

| Stable ID | Module | Authorized input channels | Output channels | Failure classes | Guard values |
|---|---|---|---|---|---|
| `D00_BOOTSTRAP_EPISODE` | `nodes/inputs.py` | invocation, run_id, frozen_digest, terminal, terminal_history | bootstrap_kind, invocation | system | fresh, resume, recover_orphan |
| `D00R_REVALIDATE_RESUME_IDENTITY` | `nodes/inputs.py` | invocation + 13 identity fields, terminal_history | validated_recovery_envelope, evidence_index_entries | system | resume_identity_proven |
| `D01_VALIDATE_AND_FREEZE_INPUTS` | `nodes/inputs.py` | invocation | 13 write-once identity fields | system | inputs_frozen |
| `D02_COMPILE_EFFECTIVE_RUN` | `nodes/inputs.py` | engine_root, curriculum_root, active_manifest_path, mode, requested_unit_id, frozen_inputs | effective_run | system | effective_run_compiled |
| `D03_PROVE_CAPABILITIES` | `nodes/inputs.py` | invocation, validated_recovery_envelope, effective_run, frozen_executable_identities, external_authorizations, frozen_digest, run_id, engine_root, output_root | capability_receipts | system, pause | capabilities_proven, prerequisite_unavailable |
| `D04_INITIALIZE_OR_RESUME` | `nodes/inputs.py` | bootstrap_kind, invocation, validated_recovery_envelope, capability_receipts, effective_run, identity fields, terminal_history, artifact_heads, attempt_counters, cursor, unit_status, accepted_unit_receipts | episode_id, checkpoint_thread_id, checkpoint_namespace, resume_from, terminal_history, artifact_heads, attempt_counters, cursor, unit_status, effective_run, identity fields | system | fresh_initialized, resume_imported |
| `D92_REENTER_VALIDATED_FRONTIER` | `nodes/inputs.py` | resume_frontier, artifact_heads, attempt_counters, model_execution_receipts, activation_receipts, capability_receipts, external_authorizations | evidence_index_entries, pending_guard | system | deterministic_reentry, incomplete_model_activation |
| `D96_GRACEFUL_INTERRUPT_GATE` | `nodes/inputs.py` | invocation, validated_recovery_envelope, resume_frontier, artifact_heads, attempt_counters, checkpoint_metadata, evidence_index_entries, selected_unit_id, episode_id, run_id | terminal_candidate, resume_frontier | system | interrupted |
| `D05_SELECT_NEXT_UNIT` | `nodes/sources.py` | effective_run, cursor, accepted_unit_receipts, unit_status | selected_unit_id, unit_status, cursor | system | unit_selected, manifest_exhausted |
| `D06_COMPILE_SOURCE_REQUESTS` | `nodes/sources.py` | effective_run, selected_unit_id, source_admissions, engine_root | source_requests, source_denominators | pause | discovery_fanout |
| `D06B_RETRIEVE_SOURCE_CANDIDATES` | `nodes/sources.py` | selected_unit_id, source_requests, source_denominators, source_discoveries, external_authorizations | retrievals | system, pause | interpretation_fanout |
| `D07_CORRELATE_AND_ADMIT_SOURCES` | `nodes/sources.py` | selected_unit_id, source_requests, source_denominators, source_discoveries, retrievals, source_interpretations | source_admissions, source_join_evidence | system | sources_admitted, prerequisite_unresolved |
| `D30_CLASSIFY_PREREQUISITE` | `nodes/sources.py` | selected_unit_id, pending_failure, source_requests, source_denominators, retrievals, attempt_counters | evidence_index_entries, terminal_candidate, resume_frontier | system | prerequisite_pause |
| `D08_VALIDATE_DOMAIN` | `nodes/domain.py` | selected_unit_id, effective_run, artifact_versions, artifact_heads, source_admissions, engine_root | artifact_heads, deterministic_checks | system | domain_admitted, domain_repairable |
| `D09_VALIDATE_CONTENT` | `nodes/content.py` | selected_unit_id, effective_run, artifact_versions, artifact_heads, engine_root | artifact_heads, deterministic_checks | system | content_admitted, content_repairable |
| `D10_COMPILE_VISUAL_BRIEFS` | `nodes/visuals.py` | selected_unit_id, artifact_heads, artifact_versions, engine_root | visual_briefs, visual_denominators | system | deterministic_visual_fanout, no_deterministic_visuals |
| `D11_CREATE_DETERMINISTIC_VISUALS` | `nodes/visuals.py` | pending_packet | visual_results | system | visual_produced |
| `D12_VISUAL_BARRIER_AND_JOIN` | `nodes/visuals.py` | selected_unit_id, visual_denominators, visual_briefs, visual_results, artifact_versions, artifact_heads | visual_join_evidence, artifact_heads, deterministic_checks, pending_packet | system | model_visual_fanout, visuals_admitted, visuals_repairable |
| `D13_RENDER_UNIT` | `nodes/render.py` | selected_unit_id, artifact_heads, engine_root, output_root | artifact_versions, deterministic_checks | system | unit_rendered |
| `D14_INVENTORY_AND_INSPECT_UNIT_PAGES` | `nodes/render.py` | selected_unit_id, artifact_heads, artifact_versions, output_root | unit_page_inventories, unit_page_inspections, deterministic_checks | system | pages_inspected, layout_repairable |
| `D15_FREEZE_UNIT_REVIEW_PACKET` | `nodes/review.py` | selected_unit_id, artifact_heads, unit_page_inventories, unit_page_inspections, deterministic_checks, source_admissions, artifact_versions, engine_root | review_packets | system | review_packet_frozen |
| `D98_WRITE_TERMINAL` | `nodes/terminal.py` | terminal_candidate, terminal, terminal_history, episode_id, run_id, mode, requested_unit_id, effective_run, accepted_unit_receipts, final_release_audits, workbook_head, artifact_heads, attempt_counters, failure_fingerprints, checkpoint_metadata, evidence_index_entries, pending_failure, resume_frontier, output_root | terminal, terminal_history | system | terminated |

Every node additionally may write the two common channels of spec 6.1
(`pending_failure`, `pending_guard`) and nothing else; `deterministic_node` raises
`CatalogueViolation` on any other channel, which is what makes sole ownership a
mechanism rather than a convention.

Nodes explicitly NOT implemented here (owned by N31/N32 per `node_ownership.v1.md`):
D16-D29, D31, D32. D90/D91 and M01-M08 are N23's.

## D98 truth table

`validate_terminal_candidate()` re-derives each guard from state without consulting the
guard that produced the candidate. A candidate that fails is written as `SYSTEM_FAILURE`
with the rejection list attached — never as the outcome it requested, and never as no
terminal at all.

| Terminal | Exit | Resume | Claims success | Independently re-derived precondition | Rejected when |
|---|---:|---|---|---|---|
| `UNIT_ACCEPTED` | 0 | no | yes | mode is `one`; candidate unit equals `requested_unit_id` and is in the frozen closure; every closure member has an accepted receipt; declared closure receipt hashes equal current ones; target receipt hash equals the current accepted receipt hash; checkpoint id is the current checkpoint; log high-water mark not above recorded evidence | mode is `all`; wrong unit; any closure member unaccepted; any stale closure hash; forged target receipt hash; stale/absent checkpoint; inflated log mark; any of 6 required fields missing |
| `COMPLETE` | 0 | no | yes | mode is `all`; a final release audit exists, passes, and is the one named; audit's workbook hash is the current workbook head; accepted receipt id set equals the frozen manifest order exactly; declared per-unit receipt hashes equal current ones; checkpoint/log correlation | mode is `one`; no audit; audit `FAIL`; wrong audit key; forged workbook hash; no workbook head; audit against a superseded workbook; missing, extra, or stale unit receipt |
| `INTERRUPTED` | 10 | yes | no | classification is `graceful_signal` or `crashed_episode`; a resume frontier, the current heads, and high-water marks are present; declared heads equal current heads | invented classification; no frontier; no heads; stale head hash; no high-water marks |
| `PAUSED_PREREQUISITE` | 11 | yes | no | exactly one named external fact; a non-negative attempt count; a named resume condition; a frontier; and `pending_failure`, if present, is class `pause` | unnamed fact; negative/non-integer attempts; no resume condition; a `system`-class failure wearing a pause candidate (a tool/integrity fault may not pause) |
| `CONVERGENCE_EXHAUSTED` | 12 | no | no | a named bound (`attempt_bound` or `fingerprint_bound`); counters and fingerprints supplied; state actually holds recorded counters or fingerprints; last findings present; the full acceptance denominator has not passed | invented bound; no recorded attempts anywhere in state; no last findings; every closure member already accepted |
| `SYSTEM_FAILURE` | 20 | no | no | a typed failure record carrying both class and cause; the failing node; safe heads; a non-negative audit high-water mark | untyped failure; no class or cause; no node; no safe heads; negative/absent audit mark |

Cross-cutting rejections: a non-object candidate, an unknown `kind` (including
`ACCEPTED_PENDING_REVIEW`, the Plan 25 value spec 2.4 item 8 forbids), and any candidate
arriving when the episode already holds a terminal (which fails as `persistence` rather
than overwriting).

## Adapter disposition

Spec 2.3's reuse table, as actually applied. Every adapter lost its orchestration/loop
authority: no node in this package contains a unit loop, a retry loop, a branch table, or
a graph edge.

| Plan 25 mechanism | Disposition here | Note |
|---|---|---|
| `controller.CurriculumRuntime.manifest_path` / `validated_manifest` | adapted into `D01._resolve_active_manifest` and `D02.manifest_unit_records` | version selection kept; the curricula-root containment check moved to D01's canonical-path guard; no `RuntimeFailure`, typed `SystemFailure` instead |
| `CurriculumFactoryGraph.run`'s `add_prerequisites` closure | replaced by `inputs.compile_prerequisite_closure` | the Plan 25 version recurses (stack-exhausts on a cycle) and raises bare `StopIteration` on an unknown id; the replacement is iterative, detects cycles by name, and rejects unknown ids explicitly. Proven to 2000-deep chains |
| `controller.static_preflight` | decomposed across D01 (freeze/hash) and D03 (capability proof) | the single preflight blob became two nodes so the frozen identity and the current capability proof are separately checkable on resume |
| `io.py` hashing / canonical paths | pattern reused, not imported | content-addressing goes through N12's `artifacts.py` per the frozen Plan 26 convention; file hashing is a local streaming helper to avoid importing Plan 25's `BoundaryError` lifecycle |
| `checks.py` schema/derivation/grounding checks | shape reused in D08/D09 (`jsonschema.Draft202012Validator`, JSON-pointer resolution, per-check records) | Plan 25's signatures take whole `unit`/`engine`/`domain` documents from a controller; the nodes take a projection and emit `deterministic_checks` records under N11's frozen `(scope, owner, head_hash, check_id, attempt)` key |
| `lesson_render.py` / `pdf_inspect.py` / `visual_maps.py` | reached through `RuntimeContext.transport_registry` (`render_unit`, `inspect_pages`, `render_deterministic_visual`) | D13/D14/D11 own hash verification and classification; the renderer/rasterizer own bytes. A tool fault from any of them is a `SystemFailure`, never a product finding |
| `routing.Selector` | not consumed | route validation is N13's/N23's; no deterministic node has a prompt path or reaches a transport |
| `FactoryStateStore`, `Checkpoints`, `_activate`, `_model`, `_produce_unit`, `_workbook` | replaced, not adapted | channel reducers and the graph own state and continuation |
| `controller.simulate`, `ACCEPTED_PENDING_REVIEW`, `CROSS_FAMILY_BYPASS` | unreachable | `ACCEPTED_PENDING_REVIEW` is asserted rejected by D98 |

## Commands

| Command | Exit | Evidence |
|---|---:|---|
| `python3 -m pytest tests/runtime/test_plan26_deterministic_nodes.py -q` | 0 | `results/evidence/N22_DETERMINISTIC_NODES/node_tests.txt` (ce3080fca29fc581081ec7c006fae52af8c1bfb18bb69799d79160d895be8ae3) |
| `python3 -m pytest -q -rs` | 0 | `results/evidence/N22_DETERMINISTIC_NODES/full_suite.txt` (243fd9483ca5c66770993d464c761f36c1ef66d23221cff66116d1601335d378) |
| `grep -rn --include='*.py' checkpoint_ns runtime/langgraph_factory/nodes/ tests/runtime/test_plan26_deterministic_nodes.py` | 1 (no match) | zero residual occurrences in the write set after the rename |
| `shasum -a 256 <each input and output path>` | 0 | hash table below |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_deterministic_nodes.py -q` | 0 | `results/evidence/N22_DETERMINISTIC_NODES/venv_node_tests.txt` (**235 passed** in the hash-locked environment) |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_unit_graph.py -q -k '<N30 B-2 rows>'` | 1 | `results/evidence/N22_DETERMINISTIC_NODES/n30_b2_acceptance.txt` (**8 failed** — the designed inversion; see the generation-5 rework note) |

Re-run at generation 4, after the `checkpoint_namespace` rename and against N11's
completed `state.py`. Node suite: **217 passed** (unchanged count; the rename retargeted an
assertion, it did not remove one). Full ambient suite: **746 passed, 4 skipped, 282
subtests passed**. All four skips are pre-existing and explained (`langgraph` absent from
the ambient interpreter for N10's API contract, N21's persistence suite, and N20's topology
suite; `pip-tools` absent for N10's lock-drift generator) — the fourth skip is N20's new
topology suite, which did not exist at generation 3, not a newly-skipped test of this
node's. No test in this node skips. The N10-N13 baseline of 377 passed/2 skipped is not
regressed.

No isolated venv was needed: node bodies are framework-agnostic `(state, runtime_context)
-> update` callables and import no `langgraph` symbol (asserted by
`test_no_node_body_declares_a_graph_edge_or_references_end`).

## Tests

| TEST item | Backing tests | Verdict | Assertion backing the verdict |
|---|---|---|---|
| 1. Exactly one implementation per D node; D98/terminal module solely owned by N22 | `test_catalogue_covers_exactly_the_owned_node_set`, `test_every_owned_node_has_exactly_one_implementation`, `test_terminal_module_is_the_sole_terminal_writer`, `test_no_node_but_d98_can_write_a_terminal_even_if_it_tries`, `test_write_terminal_is_the_only_terminal_producing_callable` | PASS | Registry resolves exactly the 22 owned ids; AST scan finds each id defined once, in its assigned module; no dict literal whose keys are all state channels contains `terminal` outside `terminal.py`; all 21 non-D98 nodes raise `CatalogueViolation` when they attempt a terminal write; `write_terminal` is the sole terminal-producing function |
| 2. Projection/update fields equal the frozen catalogue | `test_output_reducer_classes_match_the_spec_catalogue` (22), `test_failure_classes_match_the_spec_catalogue` (22), `test_projection_is_exactly_the_authorized_input_set` (22), `test_no_node_writes_an_unauthorized_channel`, `test_writing_an_unauthorized_channel_is_rejected` | PASS | Each node's output channels resolve, through N11's `FIELD_REDUCER_CLASSES`, to exactly the reducer words spec 6.2 uses in its "Output / reducer" column; failure classes equal the "failure class" column; handed a state where all 61 channels are populated, each node's projection contains exactly its declared inputs |
| 3. Expected failures typed; unexpected failures route system failure | `test_expected_pause_lands_in_pending_failure_with_the_pause_class`, `test_expected_system_failure_...`, `test_a_retrieval_tool_fault_is_a_system_failure_not_a_pause`, `test_an_unexpected_exception_is_not_caught_inside_the_node`, `test_every_declared_failure_class_is_reachable_by_a_typed_exception` | PASS | A named missing external fact lands in `pending_failure` with `class=pause`, `cause=required_external_fact_unavailable`, and no partial `retrievals` update; a cursor inconsistency lands with `class=system, cause=integrity`; a `ConnectionResetError` from the retriever becomes `class=system, cause=tool` (not a pause); an unclassified exception raised inside a node body propagates out of the node uncaught |
| 4. Manifest closure/order neutral for 1, 7, 41-unit DAGs | 6 parametrized closure tests + 5 negative tests (17 cases) | PASS | Linear chains of 1/7/41 close to the exact prefix; under 3 shuffle seeds × 3 sizes the closure set is invariant and is emitted in the manifest's own declared order; a 41-unit manifest with a shallow target closes to exactly 3 units; a diamond admits each ancestor once; `all` mode closes to the whole ordered manifest; 3-cycles, self-cycles, unknown prerequisite ids, unknown targets, and post-freeze manifest drift are each rejected by name; a 2000-deep chain does not exhaust the stack |
| 5. Retrieval/admission/check/render/page/evidence paths fail closed on stale inputs | 12 tests across D07, D08, D09, D12, D13, D14, D15, D92 | PASS | An interpretation derived from superseded retrieval bytes → `integrity`, no `source_admissions`; a cross-unit join member → `join`; a domain candidate whose parent is not the current head → `integrity`, no `artifact_heads`; content derived from a superseded domain → `integrity`; a visual denominator or deterministic visual built against a superseded content head → `integrity`; a missing denominator member → `join` naming it; a renderer misreporting its own PDF hash → `integrity`, no version admitted; PDF bytes changed after render → `integrity`; a packet whose page set is not the full inventory → `join`; a resume frontier whose parents are no longer current → `integrity` |
| 6. Repair plans one-owner/one-boundary (reinterpreted per `node_ownership.v1.md`) | `test_repair_and_acceptance_nodes_are_not_in_the_n22_catalogue`, `test_d30_prerequisite_classification_is_one_owner_scoped`, `test_d30_refuses_to_pause_on_a_non_pause_failure`, `test_d30_refuses_to_pause_on_more_than_one_unresolved_fact`, `test_d30_emits_a_pause_candidate_for_one_named_fact` | PASS | D16-D25/D28/D32 appear in neither the catalogue nor any node module's source; only D30 and D96 may write `terminal_candidate`; D30 refuses a `system`-class failure and refuses more than one named unresolved fact, and produces a pause candidate only for exactly one. See finding F-03 for the prompt/contract discrepancy this item resolves |
| 7. D98 independently rejects invalid unit, workbook, failure, pause, interrupt, success candidates | 2 accept tests + 9 + 8 parametrized reject cases + 7 further reject tests + `test_d98_terminal_guard_table_matches_spec_section_14` | PASS | Fully supported `UNIT_ACCEPTED` and `COMPLETE` candidates are accepted with exit 0; 9 distinct `UNIT_ACCEPTED` mutations and 8 `COMPLETE` mutations are each rejected with a named reason and written as `SYSTEM_FAILURE` carrying `rejected_candidate_kind`; an extra accepted unit breaks exact coverage; an invented interrupt classification and stale heads are rejected; a pause candidate carrying a `system`/`tool` failure is rejected; exhaustion with no recorded attempts, and exhaustion after the denominator passed, are rejected; an untyped system failure is rejected; `None`, a bare string, an int, a list, `{}`, and `ACCEPTED_PENDING_REVIEW` are all rejected; the six-row exit/resume/success table equals spec section 14 |
| 8. D98 writes exactly one episode terminal and is the only node connected to END | `test_a_second_terminal_write_is_refused`, `test_the_write_once_reducer_refuses_a_differing_second_terminal`, `test_no_node_body_declares_a_graph_edge_or_references_end`, `test_no_node_module_imports_a_forbidden_model_dependency`, `test_the_interrupt_gate_reaches_no_transport_retrieval_or_renderer`, `test_d96_...` (2) | PASS | A second D98 call against a state already holding a terminal produces no `terminal` key and fails as `persistence`; N11's `write_episode_terminal_once` is idempotent on replay and raises `TerminalConflict` on a differing second write; no node module references `END`, `add_edge`, `add_node`, `add_conditional_edges`, `StateGraph`, or `Send`, and none imports `langgraph` or any forbidden model dependency; D96's AST contains no transport, retriever, renderer, or inspector attribute |
| 9. Static scan finds no curriculum constants or second terminal writer | `test_the_owned_file_set_is_exactly_the_frozen_layout`, `test_no_curriculum_name_appears_in_production_source` (9), `test_no_unit_id_literal_appears_in_production_source` (9), `test_no_hardcoded_unit_count_appears_in_production_source` (9), `test_the_closure_algorithm_reads_unit_ids_only_from_the_manifest` | PASS | The package contains exactly the 8 frozen module names plus `__init__.py`; no installed curriculum's directory name or >3-character token appears in any production file; no `[LU]\d{2,3}` literal appears on any production line; no integer literal in any production file equals an installed manifest's unit count (the scan derives both the names and the counts from the installed curricula at run time, so it cannot go stale); no unit-id-shaped string constant exists in `inputs.py` |

## Findings

**Rework note (generation 5) — dispatching nodes stage their worker packets
(N30_UNIT_GRAPH finding B-2, `plan26/n30/model-packet-not-staged` and
`plan26/n30/visual-fanout-packet-not-staged`).**

N30 executed the real graph and found that a dispatch out of this node's catalogue
carried nothing a worker could accept: D06/D06B/D10 declared a fan-out with no staged
material, and D07 -> M02, D08 -> M03, D15 -> M05 were plain conditional edges, which hand
the target the whole `FactoryState`. Every N23 adapter requires a bounded packet, so those
dispatches failed with `AttemptNotReserved` / `ProjectionViolation`. D12 did stage a
packet, but its members were bare brief records rather than M04 packets.

Six catalogue rows now authorize `pending_packet` as an output — `D06_COMPILE_SOURCE_REQUESTS`,
`D06B_RETRIEVE_SOURCE_CANDIDATES`, `D07_CORRELATE_AND_ADMIT_SOURCES`, `D08_VALIDATE_DOMAIN`,
`D10_COMPILE_VISUAL_BRIEFS`, `D15_FREEZE_UNIT_REVIEW_PACKET` — and all seven dispatching
rows (those six plus `D12_VISUAL_BARRIER_AND_JOIN`) now authorize `run_id` and `episode_id`
as inputs, because a dispatch with no run and episode identity has no correlation. D07
additionally reads `effective_run` and `engine_root`, and D06B reads `effective_run`, for
the same reason: the packet's own contents come from them.

What each stages, keyed to `model_nodes.PROJECTION_SPECS`:

| Node | Dispatch | Members | Projection |
|---|---|---:|---|
| D06 | `M01_RESEARCH_UNIT_SOURCES` (`phase=DISCOVER`) | one per request key | `request`, `unit`, `source_rules`, `discovery_authority` |
| D06B | `M01_RESEARCH_UNIT_SOURCES` (`phase=INTERPRET`) | one per retrieval | `request`, `unit`, `source_rules`, `retrieval_group` |
| D07 | `M02_CREATE_UNIT_DOMAIN_DATA` | one | `unit`, `admitted_sources`, `domain_schema`, `verifier_interface`, `calibration` |
| D08 | `M03_WRITE_UNIT_CONTENT` | one | `unit`, `admitted_domain`, `curriculum_contracts`, `admitted_evidence_references` |
| D10 | `D11_CREATE_DETERMINISTIC_VISUALS` | one per deterministic brief | `brief`, `permitted_facts` (D11 is deterministic, so no model projection applies) |
| D12 | `M04_CREATE_UNIT_VISUALS` | one per pending model brief | `brief`, `permitted_facts`, `visual_contract` |
| D15 | `M05_REVIEW_ACTUAL_UNIT` | one | `unit_artifacts`, `unit_pdf`, `page_inventory`, `pages`, `deterministic_evidence`, `rubric` |

Each member is built by `nodes.worker_packet`, which carries the projection plus a
`correlation` of `run_id`, `episode_id` and a code-computed `correlation_key`. Every packet
is built from the denominator the node has just committed and returned in the same update,
so it is persisted before the fan-out guard can fire; no projection is materialized at
routing time. `nodes.staged_dispatch` refuses to stage an empty member list, so a
fan-out guard can never be taken over nothing.

**No `reservation` is staged here.** N23's `D90_RESERVE_MODEL_ATTEMPT` reads
`pending_packet`, commits one attempt counter per member, and restages each member with its
reservation attached; it derives the `activation_id` and counter key from the member's own
correlation. A deterministic node minting its own reservation would be committing a counter
it does not own, which is exactly what spec 6.2's D90 row forbids.
`test_no_staged_packet_carries_a_reservation_it_did_not_earn` asserts by AST-free source
scan that no staging module names `reservation_kind` or `attempt_ordinal`.

Two supporting corrections were needed inside this node's own write set:

- **D14 now records `page_sha256` and `image_path` per inspected page, and fails closed
  without them.** M05's page denominator is per page and by hash, so a page inventory that
  cannot identify its own bytes cannot support a review D15 could freeze. D15 requires both
  again before it stages the packet.
- **`classify_visual_brief` now treats M04's whole refusal list as deterministic.** D10
  previously classified `circuit`, `pinout`, `pin_map`, `breadboard`, `wiring`,
  `electrical`, and `terminal_block` as model-eligible, but M04's
  `_assert_visual_brief_eligible` refuses all seven. Staging a packet the worker would
  bounce would have reproduced B-2 in a new place, and classifying them deterministic is
  the safety-positive direction.
  (`test_a_kind_m04_would_refuse_is_classified_deterministic`.)

Verified end to end in the hash-locked environment, not by inspection: for each of D06,
D07, D08, D12 and D15, the real node body's staged packet was passed through the real
`D90_RESERVE_MODEL_ATTEMPT`, and each restaged member then satisfied
`_resolve_reservation`, `_resolve_correlation(needs_key=True)` and `build_projection`
for its adapter's spec. For D12 the real `routing.route_visual_barrier` translated two
staged members into exactly two `Send(M04_CREATE_UNIT_VISUALS, member)` objects, each
carrying only `brief`, `permitted_facts`, `visual_contract`, `correlation` and
`reservation`.

N30's own acceptance test `test_blocked_no_dispatching_node_authorizes_a_worker_packet`
fails on all six parametrized rows against this fix, which is the inversion N30 designed;
`test_blocked_a_source_fanout_has_no_staged_packet_to_dispatch` and
`test_blocked_the_staged_m04_briefs_are_not_m04_packets` invert with it. Two consequences
are handed back to N30 rather than worked around here:

- `test_a_visual_fanout_dispatches_one_send_per_staged_denominator_member` (previously
  green) now fails, because its `_visual_state` helper supplies no `run_id`/`episode_id`
  and it reads the member list as `packet["briefs"]`. The member key is now uniformly
  `packets`, which `routing._staged_fanout` and N23's `_staged_dispatch` both prefer. That
  test file is N30's write set and was not edited.
- Both M01 phases must keep `correlation_key == request_key`, because D06B indexes
  `source_discoveries` and D07 indexes `source_interpretations` by request key. D90 derives
  its attempt counter from `correlation_key` alone, so discovery and interpretation for one
  request share a counter and, at the frozen limit of 2, one transient retry in the
  interpretation phase is unavailable. Not caused by this rework and not fixable inside this
  write set: it needs either a phase-bearing counter key in D90 (N23) or a change to how
  those two joins are indexed (which N30 has proven exact and which is not this node's to
  re-key).

**Rework note (generation 4) — reserved-channel rename applied.** Following
`contracts/erratum_checkpoint_ns_rename.v1.md` (frozen at generation 4 after
N20_GRAPH_COMPILER's BLOCKED finding F-01: LangGraph 1.2.9 reserves the channel name
`checkpoint_ns`, so `StateGraph(FactoryState, ...)` raised `ValueError` before any Plan 26
code could run), the `FactoryState` channel `checkpoint_ns` is renamed
`checkpoint_namespace`. Three call sites in this node's write set were renamed, and
nothing else:

| Path | Site | Change |
|---|---|---|
| `runtime/langgraph_factory/nodes/inputs.py:887` | D04/D00R episode-init state update dict | `"checkpoint_ns": ""` -> `"checkpoint_namespace": ""` |
| `runtime/langgraph_factory/nodes/__init__.py:286` | D04's `NodeSpec.outputs` authorized-channel tuple | `"checkpoint_ns"` -> `"checkpoint_namespace"` |
| `tests/runtime/test_plan26_deterministic_nodes.py:1852` | D04 fresh-init assertion | `update["checkpoint_ns"]` -> `update["checkpoint_namespace"]` |

A case-sensitive grep for `checkpoint_ns` across the whole write set
(`runtime/langgraph_factory/nodes/**`, including `nodes/terminal.py`, and
`tests/runtime/test_plan26_deterministic_nodes.py`) now returns no hits, so the erratum's
call-site list was exhaustive for this node. Each of the three was checked against the
erratum's distinction before renaming: all three build or assert the top-level key of a
state *update* that N11's reducer sees, so all three are the `FactoryState` channel. No
LangGraph invoke-config key (`config["configurable"]["checkpoint_ns"]`) and no
`evidence.py` JSONL record key was touched — this node's write set contains neither.
`state.py`, `reducers.py` (N11), `persistence.py` (N21), and `evidence.py` (N12) are
outside this write set and were not modified.

No test was deleted, weakened, or retargeted: the D04 assertion still asserts the same
value (`""`) on the same update, under the channel's new name. TEST items 2 and 8 are the
ones that touch this channel and both still pass — item 2's
`test_projection_is_exactly_the_authorized_input_set` and
`test_no_node_writes_an_unauthorized_channel` are what would have caught a half-applied
rename, since D04's declared `outputs` tuple and its actual update dict must agree channel
for channel or `deterministic_node` raises `CatalogueViolation`.

Status remains **PASSED**, fully green rather than green-pending-a-sibling: N11's primary
rename to `state.py` (`FactoryState.checkpoint_namespace`, hash
`4c8942bf4a8c5ee42591531dc5e5b8c3fd668b58efd05aed4daeb623f507a298`) had already landed at
verification time, so this node's 217 tests and the full ambient suite were both re-run
against the completed rename, not against a half-migrated tree. No timing dependency
remains outstanding.

Three non-blocking findings. None blocks this node's `PASSED` status; each names an owner
for reconciliation.

- **F-01 — `terminal.py` write path differs from the graph's `writes` entry.**
  Owner: N00_BASELINE_FREEZE (contract reconciliation), consumer N32_WORKBOOK_TERMINALS.
  Evidence key: `writes[1]` of `N22_DETERMINISTIC_NODES` in `implementation.graph.v2.yaml`
  vs. `node_ownership.v1.md` line 40 and `shared_names_and_paths.v1.md` line 39.
  Fingerprint: `path-drift:terminal.py`.
  The graph declares `runtime/langgraph_factory/terminal.py`; both N00 contracts place the
  one `write_terminal` implementation at `runtime/langgraph_factory/nodes/terminal.py`.
  Resolved in favour of the contracts, as instructed and as `node_ownership.v1.md`
  self-describes ("later node prompts MUST follow it"). Nothing was written to the
  top-level path. N32 must import from `runtime.langgraph_factory.nodes.terminal`.

- **F-02 — the prompt's GOAL names a node range wider than this node owns.**
  Owner: N00_BASELINE_FREEZE. Evidence key: `N22_deterministic_nodes.prompt.v2.md` GOAL
  line 4 ("every deterministic node D00–D98") vs. `node_ownership.v1.md`'s table, which
  assigns D16-D29, D31, D32 to N31/N32 and D90/D91 to N23. Fingerprint:
  `scope-drift:D00-D98`. Followed the ownership contract: 22 nodes implemented, 18 left to
  their owners. Implementing them here would have produced two implementations of each.

- **F-03 — the prompt's TEST item 6 assumes repair-plan ownership this node does not have.**
  Owner: N31_REPAIR_ACCEPTANCE (the actual owner of D17-D21). Evidence key: prompt TEST
  item 6 ("Repair plans are one-owner/one-boundary with descendants/retests/bounds") vs.
  `node_ownership.v1.md` line 30. Fingerprint: `scope-drift:repair-plan-test`.
  Discharged as instructed by proving the boundary instead: that no repair or acceptance
  node exists in this package, and that D30's prerequisite classification is
  single-owner-scoped and refuses to pause on anything but one named external fact.
  N31 must carry the repair-plan partition/boundary/bound assertions.

Two cross-node interface observations for the nodes that will consume this one. Neither is
a defect in this node's write set; both would surface as a runtime rejection if not
reconciled.

- **F-04 — N21's orphan-recovery candidate shape does not match D98's.**
  Owner: N21_PERSISTENCE_RESUME. Evidence key:
  `runtime/langgraph_factory/persistence.py:1129-1133`, which builds a candidate as
  `{"terminal": "INTERRUPTED", ...}`. Fingerprint: `contract-drift:terminal-candidate-key`.
  D98 reads `candidate["kind"]` (the value `write_episode_terminal_once` validates against
  `TERMINAL_KINDS`) and additionally requires `classification`, `resume_frontier`, `heads`,
  and `high_water_marks`. A candidate in N21's current shape is rejected by D98 and written
  as `SYSTEM_FAILURE`, which is the safe outcome but not the intended one. The frozen
  candidate shape is the `D96_GRACEFUL_INTERRUPT_GATE` output in `nodes/inputs.py`.
  N21's file was read but not modified; it is outside this node's write set.

- **F-05 — `RuntimeContext` has no persistence service field.**
  Owner: N00_BASELINE_FREEZE / N21_PERSISTENCE_RESUME. Evidence key:
  `node_ownership.v1.md` line 20 ("using N21's persistence primitives via `RuntimeContext`")
  vs. `state.py:288-295`, whose eight frozen fields include no persistence handle.
  Fingerprint: `contract-gap:runtime-context-persistence`.
  Resolved without changing N11's frozen type: D04 and D92 consume the resume envelope and
  frontier from state (`invocation`, `validated_recovery_envelope`, `resume_frontier`),
  which `prepare_episode_invocation()` populates *before* invocation. This is the better
  factoring — a node that could reach the checkpoint store at runtime could also
  reconstruct continuation outside the graph, which is exactly spec 2.4 item 7's defect —
  but the contract sentence should be corrected so no later node adds the field.

## Invalidated descendants

None. This node passed first-pass at generation 3; the generation-4 rework was a mechanical
rename inbound from `erratum_checkpoint_ns_rename.v1.md`, not a re-derivation, and it
changed no node's inputs, outputs, guards, failure classes, or terminal semantics — only
the spelling of one channel. Descendants that read `checkpoint_ns` from `FactoryState`
must read `checkpoint_namespace` instead, which the erratum already binds on them
independently of this record.

## Hashes

| Path | sha256 |
|---|---|
| `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| `plans/26_langgraph_curriculum_factory/prompts/N22_deterministic_nodes.prompt.v2.md` | dbc64fa8a419f0a2a3e41096b11b4b61bea9e153df113deecf8d39fa9fb2f744 |
| `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md` | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md` | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md` | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md` | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md` | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md` | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| `plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md` | c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5 |
| `plans/26_langgraph_curriculum_factory/results/N11_STATE_REDUCERS.result.v1.md` | c89f166596633e2027f04daa03fca9a33e9f23f2c1346f77817e44b8c03dc30e |
| `plans/26_langgraph_curriculum_factory/results/N12_EVIDENCE_ARTIFACTS.result.v1.md` | 6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f |
| `plans/26_langgraph_curriculum_factory/contracts/erratum_checkpoint_ns_rename.v1.md` | 10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1 |
| `runtime/langgraph_factory/state.py` | 428c78edd53b73fd3458d469b36e1bb528dea37d4565f3b37995d63e4a075167 |
| `runtime/langgraph_factory/reducers.py` | 05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf |
| `runtime/langgraph_factory/model_nodes.py` (N23, read for the D90 handoff) | 4b81e4754c04d26635e239e1f55b330979c020ae9aff2cc0f4506afe99769496 |
| `plans/.../results/N30_UNIT_GRAPH.result.v1.md` (finding B-2) | 83c75350d23fadfafc804f4cc4d410a433ca43311eb83fa4c3acc65d3d152e87 |
| `runtime/langgraph_factory/nodes/__init__.py` | 9f04100a02bfb1d5dcc5fd69e1fef4da8bc5def79690ced6494972023f1087c8 |
| `runtime/langgraph_factory/nodes/inputs.py` | 0ba94888a1c601adbed50e477b37575788387bb4489e8a62363f230c622d5627 |
| `runtime/langgraph_factory/nodes/sources.py` | 21ae3780bad01eada01ecd173783702787f4b766e9965e33f360c03b23832f39 |
| `runtime/langgraph_factory/nodes/domain.py` | 89d6608a6fdd5ebf3c9ddb9b0f70a310d19bb283aa6145d3474e6e24594a5d93 |
| `runtime/langgraph_factory/nodes/content.py` | 18fbe517a0c701fa24253cb47029b3525a79bd0e5a9b0ccf28845c43f621a937 |
| `runtime/langgraph_factory/nodes/visuals.py` | 70d13f8e6d8ec96284dbc3ad6c3a0a31b803e7462fc2b349efbbffe4488693b8 |
| `runtime/langgraph_factory/nodes/render.py` | 76fa183ad8fc26c054a33901d42c3635e3cb5c0094bca70b9f797517e19152b4 |
| `runtime/langgraph_factory/nodes/review.py` | fd1b61f25cdf96a82b5f9307b1dd3dbeae9cd8b8eb4605ce182f7980e641cb5e |
| `runtime/langgraph_factory/nodes/terminal.py` | 66e7b92752d8ab8e0a93e00fc50114331f74f34538358b9b2938a6f02c17f28d |
| `tests/runtime/test_plan26_deterministic_nodes.py` | 47a56efa6e83642aec99b1a7683337af3c9ecd8ec34d1dab7ff611b29850c67e |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/node_tests.txt` | ce3080fca29fc581081ec7c006fae52af8c1bfb18bb69799d79160d895be8ae3 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/full_suite.txt` | 243fd9483ca5c66770993d464c761f36c1ef66d23221cff66116d1601335d378 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/venv_node_tests.txt` | c49d9df22963948dbee49f84601b6b2f377132b31ffbc6f5905670b7497a52a4 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/n30_b2_acceptance.txt` | 8b08f2abe4c12b3d130a2e131b546a5eaea5f1e7d4a61c34e8c224150e943e6a |
