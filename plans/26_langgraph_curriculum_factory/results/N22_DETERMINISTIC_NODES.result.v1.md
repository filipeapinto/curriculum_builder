# N22_DETERMINISTIC_NODES result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N22_deterministic_nodes.prompt.v2.md (dbc64fa8a419f0a2a3e41096b11b4b61bea9e153df113deecf8d39fa9fb2f744)
generation: 7

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
| `runtime/langgraph_factory/nodes` | `runtime/langgraph_factory/nodes/__init__.py` | c591775a214e0e7b51c051f2e297a8af8e9dc2dba844ed8b5b4944015a02ca02 |
| | `runtime/langgraph_factory/nodes/inputs.py` | 3b42770b83b389ae99d0cc4f3175b8942218f0f8f1adbcf5fcdb89cb412536a9 |
| | `runtime/langgraph_factory/nodes/sources.py` | 32785995c3e54d94cb84baa511b725bc09f6e7f43b0c56878b4060d3e733bb14 |
| | `runtime/langgraph_factory/nodes/domain.py` | a7318d9bd880a792d9b9a773e58e89902fb56b441c4767604d93150e208d3038 |
| | `runtime/langgraph_factory/nodes/content.py` | e103557cb83a7850cabe1ca4ed94cdbfc76755e0840f7ef7b5055859e3aa4ef0 |
| | `runtime/langgraph_factory/nodes/visuals.py` | 9b07577f5df151e7fd6169d182e6fd881d5fedb8f860a573f5e771859e8f4907 |
| | `runtime/langgraph_factory/nodes/render.py` | 76fa183ad8fc26c054a33901d42c3635e3cb5c0094bca70b9f797517e19152b4 |
| | `runtime/langgraph_factory/nodes/review.py` | 7b030939f97d03e503fad39e9f181ef273855e712b2c5780a284cfe24308a8b6 |
| `runtime/langgraph_factory/terminal.py` | `runtime/langgraph_factory/nodes/terminal.py` (see finding F-01) | 66e7b92752d8ab8e0a93e00fc50114331f74f34538358b9b2938a6f02c17f28d |
| `tests/runtime/test_plan26_deterministic_nodes.py` | same | 1a878db51e63e1969d8e6a27e85e7957220b6265bb22c0aa88e99506a0107ad8 |
| (outside the declared `writes`, see finding F-05) | `schemas/unit_content.schema.v1.json` | 9055922e3af160209c0dea15b1af23daca8940a3f487b1928aea3cfde5233ef1 |
| `plans/.../results/N22_DETERMINISTIC_NODES.result.v1.md` | this file | (not self-hashed) |

4942 lines of production node code, 3141 lines of test.

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
| `python3 -m pytest tests/runtime/test_plan26_deterministic_nodes.py -q` (generation 6) | 0 | `results/evidence/N22_DETERMINISTIC_NODES/node_tests_b7.txt` (2536df2e39530e95b41f541579378c316e18b975ba3af4874098a79e61844949) — **243 passed** |
| `python3 -m pytest -q` (generation 6) | 0 | `results/evidence/N22_DETERMINISTIC_NODES/full_suite_b7.txt` (cbf2990cdf13351054f8ecd5d9fc6ebd39a7b129fe52c8c1fb2ad7343f79e54b) — **806 passed, 12 skipped, 282 subtests** |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_deterministic_nodes.py -q` (generation 6) | 0 | `results/evidence/N22_DETERMINISTIC_NODES/venv_node_tests_b7.txt` (8edf3adcfb7a101d6b6a336ca414ee6e05942a8ebd8f8ae02e3636c865cd7398) — **243 passed** in the hash-locked environment |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_unit_graph.py -q -k '<N30 B-7 rows>'` | 1 | `results/evidence/N22_DETERMINISTIC_NODES/n30_b7_acceptance.txt` (401347c7ff5ee2ff33bedce9a2379bb3e6379941a4d6e9f392d8f54b7313dcad) — **1 failed, 3 passed**: the designed inversion of `test_blocked_a_model_candidate_record_is_not_an_admissible_artifact_version` |
| `python3 -m pytest tests/runtime/test_plan26_deterministic_nodes.py -q` (generation 7) | 0 | `results/evidence/N22_DETERMINISTIC_NODES/node_tests_b10_b12.txt` (cd668fd2c9892a3036177b69538eb60a46684558499e4b88f26bd077668d4e9a) — **245 passed** |
| `python3 -m pytest -q` (generation 7) | 0 | `results/evidence/N22_DETERMINISTIC_NODES/full_suite_b10_b12.txt` (d5fa0e847948d876618d0347494a3020f6a1c230546a58a3ca4cf3f099f9d5ad) — **831 passed, 12 skipped, 282 subtests** |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_deterministic_nodes.py -q` (generation 7) | 0 | `results/evidence/N22_DETERMINISTIC_NODES/venv_node_tests_b10_b12.txt` (df355c6afdb59311bcca7d7b68d9fcb09db479427cfb353349f8f8294fab5fb8) — **245 passed** in the hash-locked environment |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_unit_graph.py -q` (generation 7) | 1 | `results/evidence/N22_DETERMINISTIC_NODES/n30_b10_b12_acceptance.txt` (a275bd2de088b41eb2e87581f486653f860aca38c7b3104eb4b5fb456e431737) — **7 failed, 67 passed**; every failure is a declared inversion, see the generation-7 rework note |
| `/tmp/plan26_n30_verify/bin/python <trace probe over N30's own `_build_episode_fixture`/`_run_episode`>` | 0 | `results/evidence/N22_DETERMINISTIC_NODES/unit_path_trace_b10_b12.txt` (73b5f94b69b632908f1ba5c86b8aac1ee5d3014d912f97f27de1fa1a191537c2) — the committed path now runs D09 -> D10 -> D12 -> D13 -> D14 -> D15 -> D90 and stops at N31's deferred D16 |

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

**Rework note (generation 7) — the unit-content contract, D15's layout resolution,
and D11's own input (N30_UNIT_GRAPH findings B-10, B-11, B-12).**

N30 ran a real episode over the committed graph and found the unit path could not
leave D09. Three defects, all in this node's write set, all fixed here.

*B-10 (`plan26/n30/unit-content-contract-is-unsatisfiable`).* `CURRICULUM_CONTRACTS[0]`
named `schemas/curriculum.schema.v5.json` — the whole-**curriculum manifest**
schema, requiring `manifest_version`/`curriculum`/`domain`/`labs` under
`additionalProperties: false`. D09 validates M03's *per-unit* content body,
`{unit_id, sections, evidence_references}`, also closed. The two vocabularies are
disjoint in both directions, so `content_schema_valid` could never pass for any
document at all. No per-unit content contract existed in the repository to point
at: `curriculum.schema.v5.json`'s `$defs/lab` requires 14 manifest-row properties
and forbids all three of M03's, and `schemas/lab.schema.v4.json` describes the
*finished* seven-block unit document assembled downstream of this stage, not the
prose body M03 writes. The contract was therefore added —
`schemas/unit_content.schema.v1.json`, disclosed as finding F-05 — and
`CURRICULUM_CONTRACTS[0]` points at it. D08's `curriculum_contracts` projection
and D09's `schema_path` both read that one constant, so the author is handed
exactly the contract that admits the answer; the defect was invisible precisely
because the constant could name something unsatisfiable without either side
noticing. The contract admits the `visuals` declaration D10 compiles the visual
denominator from, which N23 added to M03's output schema in the same round.
`test_the_contract_d09_validates_against_admits_every_legal_m03_body` is the
regression: it proves the two schemas describe one language as algebra
(D09's `required` is inside M03's property set; M03's property set is inside
D09's) and then on the real validator, so it holds for every legal body rather
than for one sample.

*B-11 (`plan26/n30/d15-requires-a-layout-head-nothing-admits`).* D15 required an
admitted head for a `layout` channel, but spec 8.1 admits heads at D08/D09/D12/D20
only and gives D13/D14 `append-unique`, so no node in the graph is authorized to
write one. The requirement was unsatisfiable by construction. `layout` is out of
`PACKET_ARTIFACT_CHANNELS`; D15 now resolves the layout from D13's appended
version — the same `latest_candidate` lookup it already used for its PDF-bytes
check — and freezes that version's hash into `artifact_hashes["layout"]`. The
resolution is *required*, not optional, and the PDF-bytes check that was
conditional on it is now unconditional, so the packet still cannot name bytes the
inventory did not measure. Nothing was weakened: the layout is not independently
admitted product evidence, the rendered PDF is, and the packet names it exactly.
`test_d15_refuses_a_packet_with_no_resolvable_layout` covers the refusal.

*B-12 (`plan26/n30/d11-cannot-read-its-own-send-member`).* `_staged_fanout`
translates each staged member into `Send(destination, member)` unchanged, so the
member arrives as the worker's whole input state. D11 is the graph's only
*deterministic* `Send` target, and a deterministic node is narrowed by `project()`,
which reads its authorized inputs by **state channel name** and takes each one's
declared reducer default. A model adapter takes its member unprojected and can
therefore be staged flat with keys like `brief`; D11 cannot — `brief` and
`permitted_facts` are not channels, and making them channels would put worker-local
values into the graph's persisted state schema, which is the wrong direction. D10
therefore stages each deterministic member as `{"pending_packet": {brief,
permitted_facts, correlation}}`, and D11's catalogue row keeps its honest
`("pending_packet",)` input: the member now names the channel it delivers on.
`test_a_staged_deterministic_visual_packet_is_what_d11_consumes` asserts the
member's key set is a subset of the declared channels and hands the member to the
real D11 unadapted.

**Acceptance.** On committed code the unit path now runs
`D09 -> D10 -> D12 -> D13 -> D14 -> D15 -> D90` and stops at
`D16_REDUCE_UNIT_EVIDENCE`, a declared deferred edge owned by N31, with a real
2-page PDF, a frozen review packet whose four artifact hashes include the layout
resolved from D13's version, and domain/content/visuals heads admitted
(`unit_path_trace_b10_b12.txt`). All seven failures in N30's suite are declared
inversions rather than regressions: the four `test_blocked_*` rows for B-10/B-11/B-12
each state "Inverts when ..." and each has now inverted;
`test_the_committed_path_stops_at_a_declared_deferred_edge` and
`test_the_unobservable_boundary_is_excluded_for_a_stated_reason` both assert the
path halts *at* D09 and now halt at D16; and
`test_blocked_the_production_runtime_context_has_no_capability_surface` is N13's
B-8, fixed in the same round. Rewriting those rows is N30's, whose file is
read-only here.

**F-05 — one file was written outside the declared `writes` set.** The B-10 fix
needs an engine-root contract file, and `CURRICULUM_CONTRACTS` entries resolve
against `engine_root`, which for a production run is the repository root. No
existing schema described a per-unit content document, so
`schemas/unit_content.schema.v1.json` was created. It is a new file, owned by no
other node, and adjacent to the curriculum contracts it sits beside; the
alternative — pointing the constant at a schema that admits nothing — is the
defect itself.

**Rework note (generation 6) — the deterministic node mints the artifact version
(N30_UNIT_GRAPH finding B-7, `plan26/n30/model-candidate-record-not-admissible`).**

N30 ran the real M02 adapter against the real D08 body and found that D08 could not see a
candidate M02 had genuinely produced. A model adapter writes a *pre-admission* record keyed
on its activation, with the model's own output quarantined under `payload` and no
`version`/`hash`/`parent_hash` — which is correct and is spec 2.4's code-owned-admission
rule, now enforced by N23's `ADMISSION_OWNED_CANDIDATE_FIELDS`. This node's consuming
bodies, however, resolved that record as though the model had already minted a versioned
artifact: D08/D09 looked it up by `stream` and then read `body`, `schema_path`,
`parent_hash` and `verifier_result` off it, D06B read `locators`, D07 read
`retrieval_sha256`, and D12 read `subset` and `content_hash`. None of those keys exists on
the record the adapter writes, so D08 reported `no candidate domain version exists` against
a real candidate and no artifact head could ever advance.

The gap is closed in the direction N30 specified: **admission mints the version here.**
Four shared helpers now live in `nodes/__init__.py` and are the only way a candidate
becomes a version:

- `latest_model_candidate(versions, channel=, unit_id=)` resolves a pre-admission record by
  its correlation (`record_kind == "model_candidate"`, plus the channel and unit lineage
  N23 stamps), not by a `stream` key the model never wrote.
- `candidate_payload(record, label)` reads the model's own output, failing closed as
  `schema_contract` if the record carries none.
- `candidate_field(record, field, default)` reads a lineage field off the record and falls
  back to the payload. Every model job schema is closed and `additionalProperties: false`,
  so a payload physically cannot carry an admission field; the fallback can only reach
  lineage the projection itself declared.
- `mint_version(candidate, heads, stream, body=, **lineage)` mints the record. `version` is
  `advance_head`'s own rule read off the current head (`head.version + 1`, genesis 1),
  `parent_hash` is the current head's `hash` (`None` at genesis), and `hash` is
  `canonical_digest(body)` under `contracts/digest_algorithm.v1.md`'s canonical-JSON rule —
  computed from the body this node derived, never read off the model's record. The minted
  record is stamped `minted_by: deterministic_admission` and keyed
  `canonical_digest({stream, hash})` so `append_unique` cannot confuse it with the
  pre-admission record it descends from.

Per node:

| Node | How the version is now derived | Body / join field |
|---|---|---|
| D08_VALIDATE_DOMAIN | `_mint_domain_version` resolves M02's candidate on `channel="domain"` for the selected unit, then `mint_version` off `artifact_heads[units/<id>/domain]`. `require_current_parent` still runs, and is now satisfied by construction rather than by trusting the model. | body is `payload.domain_version.fields` — the open document the curriculum's own schema and the `/verifier_result` pointer both address; `evidence_references` carries over as lineage. `schema_path` is the run's declared `domain.manifest_schema`, falling back to `DOMAIN_SCHEMA_CONTRACT` (the schema D07 handed the model), never a path the model chose. `verifier_result` is read at the pointer D07's `verifier_interface` declares, i.e. inside the body. |
| D09_VALIDATE_CONTENT | `_mint_content_version` resolves M03's candidate on `channel="content"`, then `mint_version` off the content head. | body is `payload.unit_content`; `schema_path` is this node's own frozen `CURRICULUM_CONTRACTS[0]`; `domain_hash` is the candidate's declared lineage when it has one and otherwise the domain head this node is about to validate it against. |
| D06B_RETRIEVE_SOURCE_CANDIDATES | unchanged (it admits nothing) | `locators` is read through `candidate_field`, so it resolves from M01-discovery's payload. This is the one B-7 join N23's lineage fields do not cover, because a locator set *is* the model's answer. |
| D07_CORRELATE_AND_ADMIT_SOURCES | unchanged (it admits sources, not versions) | `retrieval_sha256`, `unit_id` and `scope` are read through `candidate_field`; `scope` falls back to the request's own declared scope, which is where it belongs. |
| D12_VISUAL_BARRIER_AND_JOIN | already minted its own `version`/`parent_hash`/`hash` off the visual head and still does; B-7's gap here was the join, not the mint | `_visual_result` normalizes an M04 candidate into the exact record shape D11 writes: it re-keys the member from the activation correlation key to the `brief_id` the denominator is indexed by, takes `unit_id`/`content_hash`/`domain_hash` from the compiled brief, fixes `subset` to `model` and `provenance` to `model_candidate`, and computes `sha256` as this node's own canonical digest of the candidate. |

One adjacent derivation was required and is recorded here rather than left implicit: with
the model no longer supplying `schema_path`, D08 has to choose the domain schema itself.
`D02_COMPILE_EFFECTIVE_RUN` now carries the curriculum's declared
`domain.manifest_schema` on `effective_run` (read from the manifest it has already frozen
and digested), because the engine's `manifest_domain.metaschema.v1.json` constrains the
*shape of that contract*, not a domain instance. A run that declares no contract still
validates against the engine's named one, which is what D07 tells the model it will be
held to.

Nine tests were added (`243 passed`, up from 235). They run the *real* model adapters over
a `FakeCliTransport` and feed their real output to the real node bodies: D08 admitting an
M02 candidate that carries no version, the minted version being the current head's
successor, two candidates differing only in body minting different hashes, D09 admitting an
M03 candidate against the admitted domain head, the run's declared contract being the one
the body is held to, `locators` resolving out of M01-discovery's payload, an M04 candidate
joining under its brief key, and `mint_version` covering every field
`ADMISSION_OWNED_CANDIDATE_FIELDS` denies a model.

Acceptance against N30: `test_blocked_a_model_candidate_record_is_not_an_admissible_artifact_version`
now fails on `KeyError: 'pending_failure'` — its own docstring's stated inversion ("inverts
when D08 derives the versioned record from the model candidate"). Reproduced end to end
outside the harness: real M02 adapter -> real D08 -> `domain_admitted`, head
`{version: 1, parent_hash: null, hash: 4acf6223...}`, and a staged `M03_WRITE_UNIT_CONTENT`
packet that `build_projection("M03_content", ...)` accepts. The six other N30 failures in
the hash-locked environment are the `Send`-shape assertions superseded by N20's in-flight
B-6 rework (`route_source_discovery_fanout` now returns D90), not this node's write set.
`test_plan26_unit_graph.py` was run, never edited.

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

Generation 6 (B-7) invalidates no predecessor. It adds four helpers to `nodes/__init__.py`
and one key (`manifest_schema`) to `effective_run`; both are additive, and no node's
inputs, guards, failure classes, or terminal semantics changed. `artifact_versions` joins
D08's and D09's declared outputs, which is a widening: both channels already reduced
through `append_unique`, so `SPEC_OUTPUT_REDUCERS` is unchanged and N11's reducer contract
is untouched. `model_nodes.py` and `tests/runtime/test_plan26_unit_graph.py` were read, not
written. N31 and N32 inherit an artifact stream that can now actually advance: a repair
candidate from M06 arrives on `artifact_versions` in the same pre-admission shape and is
minted by the same `mint_version` rule, so a repaired child is version `head+1` parented on
the head it was planned against.

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
| `runtime/langgraph_factory/model_nodes.py` (N23, read for the D90 handoff and the B-7 candidate shape) | ff471867ef2c6aa4fa78f6aac9942c85416d1e6305f3c49d9b8f1fb5861718e1 |
| `plans/.../results/N30_UNIT_GRAPH.result.v1.md` (findings B-2, B-7, B-10, B-11, B-12) | 87afe808a4d331405edcbd72165b5c5d254cbaba74f130947ceb286ced090c6e |
| `runtime/langgraph_factory/nodes/__init__.py` | c591775a214e0e7b51c051f2e297a8af8e9dc2dba844ed8b5b4944015a02ca02 |
| `runtime/langgraph_factory/nodes/inputs.py` | 3b42770b83b389ae99d0cc4f3175b8942218f0f8f1adbcf5fcdb89cb412536a9 |
| `runtime/langgraph_factory/nodes/sources.py` | 32785995c3e54d94cb84baa511b725bc09f6e7f43b0c56878b4060d3e733bb14 |
| `runtime/langgraph_factory/nodes/domain.py` | a7318d9bd880a792d9b9a773e58e89902fb56b441c4767604d93150e208d3038 |
| `runtime/langgraph_factory/nodes/content.py` | e103557cb83a7850cabe1ca4ed94cdbfc76755e0840f7ef7b5055859e3aa4ef0 |
| `runtime/langgraph_factory/nodes/visuals.py` | 9b07577f5df151e7fd6169d182e6fd881d5fedb8f860a573f5e771859e8f4907 |
| `runtime/langgraph_factory/nodes/render.py` | 76fa183ad8fc26c054a33901d42c3635e3cb5c0094bca70b9f797517e19152b4 |
| `runtime/langgraph_factory/nodes/review.py` | 7b030939f97d03e503fad39e9f181ef273855e712b2c5780a284cfe24308a8b6 |
| `runtime/langgraph_factory/nodes/terminal.py` | 66e7b92752d8ab8e0a93e00fc50114331f74f34538358b9b2938a6f02c17f28d |
| `tests/runtime/test_plan26_deterministic_nodes.py` | 1a878db51e63e1969d8e6a27e85e7957220b6265bb22c0aa88e99506a0107ad8 |
| `schemas/unit_content.schema.v1.json` (new, finding F-05) | 9055922e3af160209c0dea15b1af23daca8940a3f487b1928aea3cfde5233ef1 |
| `runtime/langgraph_factory/schemas/M03_write_unit_content.schema.json` (N23, read for the B-10 contract agreement) | 5f8893a218f3ccb979a1c025721666b1e634bdaaf46bfa2be35de6f3113e35fe |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/node_tests.txt` | ce3080fca29fc581081ec7c006fae52af8c1bfb18bb69799d79160d895be8ae3 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/full_suite.txt` | 243fd9483ca5c66770993d464c761f36c1ef66d23221cff66116d1601335d378 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/venv_node_tests.txt` | c49d9df22963948dbee49f84601b6b2f377132b31ffbc6f5905670b7497a52a4 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/n30_b2_acceptance.txt` | 8b08f2abe4c12b3d130a2e131b546a5eaea5f1e7d4a61c34e8c224150e943e6a |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/node_tests_b7.txt` | 2536df2e39530e95b41f541579378c316e18b975ba3af4874098a79e61844949 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/full_suite_b7.txt` | cbf2990cdf13351054f8ecd5d9fc6ebd39a7b129fe52c8c1fb2ad7343f79e54b |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/venv_node_tests_b7.txt` | 8edf3adcfb7a101d6b6a336ca414ee6e05942a8ebd8f8ae02e3636c865cd7398 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/n30_b7_acceptance.txt` | 401347c7ff5ee2ff33bedce9a2379bb3e6379941a4d6e9f392d8f54b7313dcad |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/node_tests_b10_b12.txt` | cd668fd2c9892a3036177b69538eb60a46684558499e4b88f26bd077668d4e9a |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/full_suite_b10_b12.txt` | d5fa0e847948d876618d0347494a3020f6a1c230546a58a3ca4cf3f099f9d5ad |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/venv_node_tests_b10_b12.txt` | df355c6afdb59311bcca7d7b68d9fcb09db479427cfb353349f8f8294fab5fb8 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/n30_b10_b12_acceptance.txt` | a275bd2de088b41eb2e87581f486653f860aca38c7b3104eb4b5fb456e431737 |
| `plans/.../results/evidence/N22_DETERMINISTIC_NODES/unit_path_trace_b10_b12.txt` | 73b5f94b69b632908f1ba5c86b8aac1ee5d3014d912f97f27de1fa1a191537c2 |
