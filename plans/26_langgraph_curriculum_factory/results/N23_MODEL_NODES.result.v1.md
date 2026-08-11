# N23_MODEL_NODES result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N23_model_nodes.prompt.v1.md (2cc6ccd0adaccc8c4768d5cb0ada3fc196aa8c4339e29a9bbe96a31bd9c24344)
generation: 3

## Inputs

- N00_BASELINE_FREEZE: c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5
- N11_STATE_REDUCERS: c89f166596633e2027f04daa03fca9a33e9f23f2c1346f77817e44b8c03dc30e
- N13_TRANSPORT_AUTH: aacb3187bfe11f1e16b4eafebab6fba5a8ae7ba0136148b26fafac7f3adb2a71
- plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md: 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af
- plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md: 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0
- plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md: c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2
- plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md: d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad
- plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md: 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7
- plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md: edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b
- plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md (sections 6.3, 8.1, 8.2, 9, 10): 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6
- plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
- runtime/langgraph_factory/state.py (N11, read): 873d640ff2b7e677818fa74d514211e104797b3d3d48dfad4d7d7d47197cd74a
- runtime/langgraph_factory/reducers.py (N11, read): 05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf
- runtime/langgraph_factory/transport.py (N13, read): 111474fc70ae5cb8a3e95ea8e53f035141eca795138956a1c9879159958d87af
- runtime/langgraph_factory/egress.py (N13, read): 837410dad45a7deb8ef761e3636700a7fbde9f45ff6d97d8b4ba7b5c96383f52
- runtime/langgraph_factory/config/model_jobs.v1.yaml (N13, read): 7b5d168c106ad428dc59600765a7c2960f16e7dc53e735d0ac232b42096e8a96
- runtime/langgraph_factory/schemas/*.schema.json and runtime/langgraph_factory/prompts/*.prompt.md (N13, read, hashes as recorded in N13_TRANSPORT_AUTH)

No file outside this node's `writes` set was created or modified. N13's `schemas/`
directory was read and audited but not patched (see Findings).

## Generation 3 — rework for N30 Finding B-3

Fingerprint `plan26/n30/d90-d91-not-registrable`, raised by real graph execution in
`N30_UNIT_GRAPH.result.v1.md` (and earlier as N20's F-03). `reserve_model_attempt`
and `classify_model_failure` are keyword-only after their first parameter, so
neither is an `add_node` callable; N30 could not adapt them in `unit_graph.py`
because N20's `validate_bindings` refuses a production binding from any module
other than `runtime.langgraph_factory.nodes` / `.model_nodes`
(`N20-BIND-PLACEHOLDER`), and laundering the wrapper past that audit would have
recorded the wrong owner for real logic. The fix therefore had to live here.

What generation 3 adds, all inside this node's write set:

- `D90_RESERVE_MODEL_ATTEMPT(state, context)` and
  `D91_CLASSIFY_MODEL_FAILURE(state, context)` — two module-level callables with
  exactly two positional parameters, the same convention `graph._boundary` calls
  every N22/N23 body with, plus `MODEL_BOOKKEEPING_NODES` mapping each stable ID
  to its body so a builder can pick both up by name.
- The keyword-only helpers are unchanged and remain the implementation: the node
  callables are adapters that resolve their arguments from graph state.
- `RESERVE_ATTEMPT_WRITABLE_FIELDS` gains `pending_packet` (D90 restages the
  dispatch packet with each member's reservation attached).
- `RETRYABLE_FAILURE_CLASSES` gains `aborted_activation`, the class D91 assigns to
  an activation D92 found with no execution receipt (spec 6.2 D92: an interrupted
  model activation is classified by D91 before D90 may authorize a later attempt).
- `classify_model_failure`'s guard now also carries `detail.destination`, which is
  where `routing.route_model_failure` reads the dynamic `repair` destination from.
  The pre-existing top-level `destination` key is unchanged.

### Why D90 loops over the staged batch rather than reserving once

B-3 requires one reservation per fan-out member: the M01 discovery and
interpretation maps and the M04 visual map each dispatch N workers, and each
worker is a separate attempt against its own correlation. The staged dispatch
packet (`pending_packet`, `{"dispatch": job_id, "packets"|"briefs": [...]}`) is
the only place the committed denominator exists, and `routing._staged_fanout`
translates exactly those members into `Send`s. So D90:

1. reads the staged packet, resolves each member's `correlation` through the same
   `_resolve_correlation` the adapters use, and derives one counter key per member;
2. calls `reserve_model_attempt` once per member, deriving a per-attempt
   `activation_id` that includes the attempt ordinal so D92 can still tell an
   unobserved attempt from an observed one;
3. returns the packet restaged with each member's own reservation attached, so the
   fan-out guard dispatches exactly what was reserved and every worker satisfies
   `_resolve_reservation`;
4. when `pending_guard` is a D91-classified `retry`, restages only the one member
   whose counter key was retried — the sibling members' results are already
   committed and are not re-dispatched;
5. exhausts the whole superstep if any member is at the frozen limit, rather than
   dispatching a partial map, so a sibling can never carry the bound past 2.

D91 reads `pending_failure` (or synthesizes an `aborted_activation` failure from
D92's incomplete-activation guard and the reservation receipt that names the job
and counter), takes `attempts_used` from the committed `attempt_counters` rather
than from the failure record, and clears `pending_failure` on a `retry` — without
that clear, `routing.decide` would send the next node (D90) to the terminal
writer instead of letting it reserve.

### Still owed by another owner

`graph.binding_inventory()` composes `node_registry()` with `MODEL_NODE_ADAPTERS`
only, so the two new bodies are not yet in the inventory the builder registers.
`graph.py` is N20's file and outside this node's write set; the remaining step is
one line there (`bindings.update(model_nodes.MODEL_BOOKKEEPING_NODES)`), after
which N30's `test_blocked_d90_and_d91_have_no_registrable_node_callable` inverts
as it was written to. That the callables themselves satisfy the audit and register
is proven here rather than asserted: see
`test_the_bookkeeping_nodes_register_on_a_real_state_graph`.

## Outputs

- runtime/langgraph_factory/model_nodes.py: 4b81e4754c04d26635e239e1f55b330979c020ae9aff2cc0f4506afe99769496
- tests/runtime/test_plan26_model_nodes.py: 4b0a29c5eaa508ed20f93f981d1eb3ab07a99c108cb6f6b51abcc2b8288ffdb2
- plans/26_langgraph_curriculum_factory/results/N23_MODEL_NODES.result.v1.md: this file

## Node catalogue

Nine adapters over eight frozen jobs (M01 has two distinguishable phase functions),
plus D90 and D91. `MODEL_NODE_ADAPTERS` registers exactly the eight graph node ids
for N20/N30 to `add_node`; `build_model_nodes(context)` binds them to one context.

| Spec node | Function | CLI / family | Placement it is built for (spec 8.1/8.2) |
|---|---|---|---|
| M01 `phase=DISCOVER` | `m01_discover_unit_sources` | codex / openai | `Send` per D06 request key, returns to D06B |
| M01 `phase=INTERPRET` | `m01_interpret_unit_sources` | codex / openai | `Send` per D06B retrieval group, returns to D07 |
| M01 (node body) | `m01_research_unit_sources` | codex / openai | selects the phase from the packet's explicit `phase` |
| M02 | `m02_create_unit_domain_data` | codex / openai | D07 -> M02 -> D08 |
| M03 | `m03_write_unit_content` | codex / openai | D08 -> M03 -> D09 |
| M04 | `m04_create_unit_visuals` | codex / openai | D12 `Send` map superstep, normal edge back to D12 |
| M05 | `m05_review_actual_unit` | gemini / google | D15 -> M05 -> D16 |
| M06 | `m06_repair_named_unit_artifact` | codex / openai | D19 -> D90 -> M06 -> D20 |
| M07 | `m07_review_actual_workbook` | gemini / google | D27 -> M07 -> D28 |
| M08 | `m08_repair_named_workbook_defect` | codex / openai | D29 -> D90 -> M08 -> D31 |
| D90 | `D90_RESERVE_MODEL_ATTEMPT` (over `reserve_model_attempt`) | none | commits one `attempt_counters` entry per staged dispatch member (`monotonic_max`) before dispatch |
| D91 | `D91_CLASSIFY_MODEL_FAILURE` (over `classify_model_failure`) | none | retry -> D90, repair -> D17/D29, else terminal candidate |

## Projection table (spec section 9, materialized)

Every projection is built from its allowlist alone: `build_projection` reads the
allowed names, never the packet's key set, so a whole `FactoryState` handed to a
builder cannot widen the result. Nested structurally-excluded names are rejected,
and every projection additionally passes N13's `assert_no_authoritative_fields`.

| Projection | Included (allowlist) | Required | Structurally excluded |
|---|---|---|---|
| `M01_discovery` | `request`, `unit`, `source_rules`, `discovery_authority` | all four | sibling requests/units, author history, acceptance, output tree |
| `M01_interpretation` | `request`, `unit`, `source_rules`, `retrieval_group` | all four | network/repository access, other retrieval groups, routing/acceptance state; `discovery_authority` is a denied name here |
| `M02_domain` | `unit`, `admitted_sources`, `domain_schema`, `domain_config`, `verifier_interface`, `calibration` | `unit`, `admitted_sources`, `domain_schema`, `verifier_interface` | content drafts, reviews, sibling units, terminals |
| `M03_content` | `unit`, `admitted_domain`, `curriculum_contracts`, `admitted_evidence_references` | first three | rejected domain versions, reviewer history, sibling artifacts, acceptance state |
| `M04_visual` | `brief`, `permitted_facts`, `visual_contract` | all three | authoritative circuit/pin/electrical invention, other briefs, full state |
| `M05_unit_review` | `unit_artifacts`, `unit_pdf`, `page_inventory`, `pages`, `deterministic_evidence`, `rubric` | all six | author/repair history, prompts/outputs from M01-M04/M06, counters, desired verdict |
| `M06_unit_repair` | `owner`, `findings`, `parent`, `boundary`, `allowed_facts`, `invalidated_descendants`, `retest_order` | `owner`, `findings`, `parent`, `boundary` | unrelated findings/artifacts, accepted bytes, sibling units, routing/terminal state |
| `M07_workbook_review` | `coverage_map`, `accepted_unit_hashes`, `workbook_pdf`, `page_inventory`, `pages`, `deterministic_evidence`, `rubric` | all seven | author and unit repair history, desired verdict, mutable unit sources |
| `M08_workbook_repair` | `defect`, `parent`, `allowed_files`, `accepted_unit_hashes`, `workbook_pdf_hash`, `invalidated_descendants`, `retest_order` | first four | unit content/domain/visual sources, unrelated workbook defects, acceptance/terminal authority |

`DENIED_PROJECTION_NAMES` bans every persisted `FactoryState` channel plus
`desired_verdict`/`expected_verdict`/`target_verdict`/`author_history`; review jobs
additionally ban `verdict`, `prior_findings`, `prompt(s)`, `model_output(s)`,
`attempt(s)`, and `counter(s)`. There is therefore no field anywhere in an M05/M07
projection through which a caller could hint the wanted review outcome.

## Output table (candidate -> state channel)

| Job | Validated candidate | State channel / reducer | Head or terminal touched |
|---|---|---|---|
| M01 discovery | `locators[]`, each `request_id` equal to the one projected request | `source_discoveries[correlation_key]` / `union_disjoint` | none |
| M01 interpretation | `interpretations[]`, each bound to the request and a declared `retrieval_id` | `source_interpretations[correlation_key]` / `union_disjoint` | none |
| M02 | `domain_version` for the projected unit, evidence only from admitted sources | `artifact_versions[]` / `append_unique` | none |
| M03 | `unit_content` for the projected unit, evidence bound to its own sections and admitted sources | `artifact_versions[]` / `append_unique` | none |
| M04 | `visual_candidate` + `provenance_declaration` for the one brief, `asserts_authoritative_detail` false, facts ⊆ permitted | `visual_results[correlation_key]` / `union_disjoint` | none |
| M05 | `overall_findings` + `page_findings` covering exactly `1..page_count` with matching page hashes | `unit_reviews[]` / `append_unique` | none |
| M06 | `candidate_child` + `changed_path_manifest`, pointers ⊆ boundary, findings ⊆ named partition, artifact name unchanged | `artifact_versions[]` / `append_unique` | none |
| M07 | `overall_findings` + `page_findings` covering exactly `1..page_count` with matching page hashes | `workbook_reviews[]` / `append_unique` | none |
| M08 | `candidate_child` + `changed_file_manifest`, files ⊆ allowed workbook-owned files, one declared `defect_id` | `workbook_versions[]` / `append_unique` | none |

Every adapter also appends `model_execution_receipts` and `activation_receipts`, and
on failure sets `pending_failure` for D91. `MODEL_NODE_WRITABLE_FIELDS` is the total
write set; `_assert_model_node_update` raises if anything else is proposed.
`artifact_heads`, `workbook_head`, `accepted_unit_receipts`, `terminal`,
`terminal_candidate`, `unit_status`, `source_admissions`, `deterministic_checks` and
`pending_guard` are all in `FORBIDDEN_MODEL_NODE_FIELDS` and unreachable from here.

## Attempt bookkeeping (D90 / D91)

- D90 `reserve_model_attempt` returns `{"attempt_counters": {key: ordinal}}` under
  `monotonic_max` plus an `activation_receipts` reservation record, *before* any
  transport call exists, so a dispatch that never returns still leaves a durable
  attempt. At `MODEL_NODE_ATTEMPT_LIMIT` (2 = one activation plus one D91-authorized
  retry, matching every route's frozen `retry_limit: 1`) it returns
  `decision: exhausted`, mints no reservation, and re-emits the unchanged counter.
- Every adapter requires that reservation record in its packet and validates kind,
  job, ordinal, and limit. Without one it raises `AttemptNotReserved` and the
  transport is never called.
- D91 `classify_model_failure` maps a failure class to exactly one decision:
  malformed/transient under the limit -> `retry` with destination
  `D90_RESERVE_MODEL_ATTEMPT`; policy/content -> `repair` at `D17` (unit) or `D29`
  (workbook), never a transport retry; malformed/transient at the limit ->
  `CONVERGENCE_EXHAUSTED`; identity/capability/workspace/route/unknown ->
  `SYSTEM_FAILURE`. D91 never calls a transport.
- Both are registrable node bodies as of generation 3.
  `D90_RESERVE_MODEL_ATTEMPT(state, context)` reserves per staged dispatch member
  and restages `pending_packet` with each member's reservation;
  `D91_CLASSIFY_MODEL_FAILURE(state, context)` classifies `pending_failure` (or a
  D92 incomplete activation) against the committed counter and clears the failure
  on a retry so D90 can run next.

## Family and authority evidence

- `MODEL_NODE_FAMILIES` is asserted equal to N13's frozen registry: M01/M02/M03/M04/M06/M08
  are `codex`/`openai`; M05/M07 are `gemini`/`google`.
- `_dispatch` raises `FamilyViolation` when a review's executed family is the
  authoring family, and when any executed family differs from the decided one. The
  executed value is read from the receipt's `observed_family` (N13's identity
  observation) and only falls back to `decided_family` when nothing was observed.
- The same boundary is proven against N13's own primitive:
  `tp.assert_identity_matches(route, ObservedIdentity(family="openai"))` raises
  `IdentityMismatch` for both M05 and M07.
- M04 refuses an authoritative brief before dispatch: `authoritative: true`, a
  `visual_class` in `AUTHORITATIVE_VISUAL_CLASSES` (circuit, schematic, netlist,
  pinout, pin_map, breadboard, wiring, electrical, power_path, terminal_block), or a
  brief not marked `model_eligible`. M08 refuses any defect whose component is not
  one of `front_matter`, `navigation`, `layout`, `assembly`.

## Commands

- `python3 -m pytest tests/runtime/test_plan26_model_nodes.py -q` — exit 0 — `plans/26_langgraph_curriculum_factory/results/evidence/N23_MODEL_NODES/node_tests.txt` — **167 passed, 1 skipped** (generation 3; the skip is the real-`add_node` proof, which needs `langgraph`)
- `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_model_nodes.py -q` — exit 0 — `.../evidence/N23_MODEL_NODES/venv_node_tests_b3.txt` — **168 passed** in the hash-locked environment, so the `add_node` registration proof actually ran
- `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_unit_graph.py -q -k "d90 or d91 or model"` — exit 0 — `.../evidence/N23_MODEL_NODES/venv_n30_d90_d91_slice.txt` — 5 passed (N30's file, read-only here)
- `python3 -m pytest -q` — exit 1 — `.../evidence/N23_MODEL_NODES/full_suite.txt` — 753 passed, 8 failed, 11 skipped, 282 subtests passed
- `shasum -a 256 <all writes + inputs>` — exit 0 — hashes reproduced in the Hashes section

Generation 3 test arithmetic: this node's suite moves 152 -> 168 (16 new tests for
the two node callables), and no previously passing test in it changed state.

The 8 ambient failures are all in `tests/runtime/test_plan26_deterministic_nodes.py`
(N22's file), which a sibling agent is editing concurrently for N30's Finding B-2;
none is in this node's write set and none involves `model_nodes.py`. The 10 failures
in N30's `test_plan26_unit_graph.py` in the hash-locked environment are likewise the
B-1/B-2 inversion rows plus one D12 row mid-edit — verified by reading the failure
(`visuals.D12_VISUAL_BARRIER_AND_JOIN` now returns no `pending_guard`), not assumed.
The D90/D91 rows of that suite pass.

## Tests

168 tests in `tests/runtime/test_plan26_model_nodes.py`, all PASS (167 ambient, the
168th needs `langgraph` and runs in the hash-locked environment).

### Generation 3 — B-3 rework rows

| Claim | Backing tests | Verdict and assertion |
|---|---|---|
| D90 mints one reservation per fan-out member, not one per superstep | `test_d90_mints_one_reservation_per_fanout_member`, `test_a_reserved_fanout_member_is_dispatchable_by_the_model_adapter`, `test_a_second_superstep_reserves_the_next_ordinal_per_correlation` | PASS — a 3-member M01 packet yields 3 counter keys at ordinal 1, 3 distinct `activation_id`s, 3 distinct `reservation_id`s and 3 activation receipts, and each restaged member's reservation is accepted by `_resolve_reservation`, the same gate every adapter runs before dispatch |
| A classified retry re-dispatches exactly the failed member | `test_d90_restages_only_the_member_d91_authorized_a_retry_for`, `test_a_retry_that_names_no_staged_member_is_refused` | PASS — with all three members at ordinal 1 and D91's guard naming `req-2`, the update carries one counter key at ordinal 2 and one restaged member; a retry naming an unstaged counter key raises rather than silently dispatching nothing |
| The frozen bound cannot be crossed by a sibling member | `test_one_exhausted_member_exhausts_the_whole_superstep` | PASS — one member at `MODEL_NODE_ATTEMPT_LIMIT` yields guard value `exhausted`, no `pending_packet` and no `activation_receipts`, so no partial map is dispatched |
| Both guards resolve through N20's frozen guard table | `test_d90_guard_routes_through_the_frozen_guard_table`, `test_d91_classifies_the_pending_failure_against_the_committed_counter`, `test_d91_at_the_committed_limit_exhausts_rather_than_retrying`, `test_d91_repair_destination_resolves_through_the_dynamic_guard` | PASS — `routing.route_attempt_reservation` returns the job id for `authorized` and `D98_WRITE_TERMINAL` for `exhausted`; `routing.route_model_failure` returns `D90_RESERVE_MODEL_ATTEMPT`, `D98_WRITE_TERMINAL` and `D17_CLASSIFY_UNIT_FINDINGS` for retry/exhausted/repair, the last through the dynamic `detail.destination` |
| An interrupted activation is classified before any later attempt | `test_d91_classifies_an_activation_d92_could_not_account_for`, `test_an_incomplete_activation_with_no_reservation_receipt_is_refused` | PASS — D92's `incomplete_model_activation` guard plus the reservation receipt yields `failure_class="aborted_activation"` and decision `retry` on the right counter key; an activation with no reservation receipt raises instead of guessing a job |
| Both are genuinely `add_node`-compatible bodies owned by this module | `test_the_bookkeeping_nodes_have_the_node_body_calling_convention` (2 ids), `test_the_bookkeeping_nodes_register_on_a_real_state_graph` | PASS — each body has exactly two positional-or-keyword parameters with no defaults and `__module__ == "runtime.langgraph_factory.model_nodes"`; with real `langgraph` installed, `validate_bindings` accepts both as required bindings and `StateGraph(FactoryState).add_node(id, graph._boundary(id, body, model_node=False))` registers both |

| TEST item | Backing tests | Verdict and assertion |
|---|---|---|
| 1. Exactly eight model nodes/jobs and correct Codex/Gemini family split | `test_exactly_eight_model_nodes_and_adapters`, `test_family_split_matches_the_frozen_registry`, `test_a_projection_exists_for_every_job_and_both_m01_phases`, `test_build_model_nodes_registers_exactly_eight_callables` | PASS — `len(MODEL_NODE_IDS) == 8`, `set(MODEL_NODE_ADAPTERS) == set(load_job_registry())`; the Codex set is exactly {M01,M02,M03,M04,M06,M08} and the Gemini set exactly {M05,M07}, each cross-checked against `registry[job].family` and `.cli` |
| 2. Each input projection/schema equals the spec and excludes whole state/siblings | `test_every_projection_equals_the_spec_section_9_row` (9 rows), `test_a_poisoned_full_state_cannot_widen_any_projection` (9 rows), `test_every_projection_is_control_field_free` (9 rows), `test_a_nested_desired_verdict_is_rejected_for_a_review`, `test_a_review_projection_cannot_carry_author_or_counter_history`, `test_m01_discovery_and_interpretation_are_distinct_projections`, `test_an_interpretation_packet_may_not_smuggle_discovery_authority`, `test_m01_phase_selection_reads_the_explicit_packet_phase`, `test_m04_refuses_an_authoritative_brief`, `test_a_staged_input_the_projection_never_names_is_refused` | PASS — `spec.allowed` equals the literal section-9 row transcribed in the test file; a packet carrying every `FACTORY_STATE_FIELDS` name plus `desired_verdict`/`author_history`/`sibling_units` yields a projection whose key set is inside the allowlist and whose recursive key set intersects neither the state inventory nor the denylist, and the poison value `"ACCEPT"` appears nowhere in it |
| 3. Output schemas reject control fields, undeclared artifacts, and broad repair | `test_every_job_schema_is_closed_and_control_free` (8 jobs), `test_the_frozen_schema_rejects_a_terminal_field`, `test_the_adapter_rejects_an_injected_control_field` (terminal/next_node/accept/verdict/route), `test_the_adapter_closes_the_one_object_the_schema_leaves_open`, `test_n13_still_rejects_the_open_object_at_its_own_parse_boundary`, `test_undeclared_artifacts_are_rejected`, `test_a_model_visual_may_not_assert_authoritative_detail`, `test_m06_rejects_a_pointer_outside_the_declared_boundary`, `test_m06_rejects_an_unnamed_finding_and_a_renamed_artifact`, `test_m06_refuses_findings_spanning_more_than_one_owner`, `test_m06_refuses_an_empty_boundary`, `test_m08_rejects_a_file_outside_the_declared_boundary`, `test_m08_refuses_a_unit_owned_defect`, `test_m08_rejects_a_child_addressing_another_defect` | PASS — a candidate carrying `terminal: UNIT_ACCEPTED` raises `jsonschema.ValidationError` through `FakeCliTransport` against the frozen closed schema, and the adapter independently returns `failure_class == "candidate_control_field"` with no candidate channel in the update; an M06 manifest pointing at `/sections/1/heading` outside the declared `["/sections/0/body"]` boundary and an M08 manifest naming `unit_U01_content.typ` outside the declared workbook-owned file list both yield `candidate_boundary_violation` and write nothing |
| 4. M05/M07 require exact frozen packet/page denominator and different family | `test_review_packets_require_the_exact_frozen_page_denominator` (2 jobs x 5 mutations), `test_review_findings_must_cover_every_page_exactly` (2 jobs x 4 mutations), `test_a_review_executing_in_the_authoring_family_is_a_system_fault`, `test_n13_identity_primitive_also_rejects_the_authoring_family`, `test_a_conforming_review_records_the_page_denominator` | PASS — missing, extra, duplicate, zero-count, and wrong-hash pages each raise `PageDenominatorViolation` with `transport.calls == []`; a finding set missing a page, adding page 3, duplicating page 1, or citing a wrong page hash yields `candidate_page_denominator` and no review channel; an observed `openai` family on M05/M07 raises `FamilyViolation`, and N13's `assert_identity_matches` raises `IdentityMismatch` on the same input |
| 5. Node retry always traverses D91/D90; no hidden transport/graph retry | `test_transport_is_invoked_from_exactly_one_call_site`, `test_no_adapter_holds_a_second_transport_reference`, `test_an_adapter_refuses_to_dispatch_without_a_valid_d90_reservation` (6 cases), `test_a_reservation_beyond_the_frozen_limit_is_refused`, `test_a_malformed_result_yields_a_classifiable_failure_not_a_candidate`, `test_a_retry_traverses_d91_then_d90_before_the_second_transport_call`, `test_d90_commits_the_counter_before_dispatch_and_stops_at_the_limit`, `test_d90_refuses_a_job_that_is_not_one_of_the_eight`, `test_policy_and_content_failures_route_to_repair_never_to_a_transport_retry` (7 classes), `test_a_workbook_content_failure_routes_to_the_workbook_repair_planner`, `test_a_retryable_failure_at_the_limit_becomes_exhaustion`, `test_integrity_failures_are_never_retried` (4 classes), `test_d91_writes_only_deterministic_classification_channels`, `test_reusing_one_reservation_for_a_second_dispatch_conflicts_in_the_ledger` | PASS — an AST walk of `model_nodes.py` finds exactly one `.execute` attribute in the whole module and it lives in `_dispatch`; a forced `ResultParseError("malformed_json")` leaves `len(transport.calls) == 1` and no `artifact_versions`, D91 returns `decision="retry"`/`destination="D90_RESERVE_MODEL_ATTEMPT"` while `len(transport.calls)` is still 1, D90 then mints ordinal 2, and only after that does the second call happen (`len(transport.calls) == 2`); reusing one reservation for two differing results raises `DuplicateConflict` in `append_unique` |
| 6. Candidate output changes no head until deterministic admission | `test_every_adapter_writes_only_pre_admission_candidate_channels` (9 rows), `test_a_model_update_can_never_satisfy_an_advance_head_update` (9 rows), `test_every_candidate_record_is_marked_pre_admission` (9 rows), `test_the_writable_and_forbidden_field_sets_are_real_and_disjoint`, `test_candidate_channels_use_the_reducers_the_spec_declares`, `test_fan_out_updates_merge_through_the_declared_reducers`, `test_an_update_that_names_a_head_is_refused_by_the_module` | PASS — every adapter's update key set is inside `MODEL_NODE_WRITABLE_FIELDS` and disjoint from `FORBIDDEN_MODEL_NODE_FIELDS`; feeding any returned record to `advance_head({}, {...})` raises `HeadAdvanceError` because no candidate record carries the `version`/`hash` pair a head requires; `artifact_heads`/`workbook_head` are confirmed `advance_head` channels and `accepted_unit_receipts` an `accept_once` channel that no adapter can name |
| 7. Fake adapters remain injectable only in test graph builds | `test_the_production_context_refuses_a_fake_transport`, `test_the_production_context_refuses_any_non_transport_object`, `test_only_the_named_test_builder_and_its_guard_mention_the_fake_transport`, `test_the_production_builder_always_passes_through_the_transport_guard`, `test_the_test_builder_produces_a_usable_fake_context`, `test_the_fake_transport_still_refuses_a_product_root` | PASS — `build_model_node_context` raises unless the bound transport is a real `tp.CliTransport`; an AST walk shows `FakeCliTransport` is referenced by exactly two functions, `_assert_production_transport` (which rejects it) and `build_test_model_node_context`, and that the only two functions constructing a `ModelNodeContext` are those two builders, of which the production one provably calls the guard |

## Findings

- **m02-fields-object-is-explicitly-open** — owner: `transport_or_authorization`
  (N13_TRANSPORT_AUTH). Evidence key:
  `schemas/M02_create_unit_domain_data.schema.json:properties.domain_version.properties.fields`.
  Fingerprint: `spec-9:additionalProperties:M02.domain_version.fields`. Spec section 9
  states every projection schema has `additionalProperties: false`; the M02 *output*
  schema declares `additionalProperties: true` on `domain_version.fields`. It is the
  only open object across all eight schemas (verified by a recursive scan). Schema
  validation alone therefore admits `fields: {"terminal": "UNIT_ACCEPTED"}`, proven by
  `test_the_adapter_closes_the_one_object_the_schema_leaves_open`.
  **Non-blocking**, because the field is not actually reachable as a control channel:
  N13's `load_candidate` and `FakeCliTransport` both run
  `assert_no_authoritative_fields` over the whole candidate at parse time and reject
  it (`test_n13_still_rejects_the_open_object_at_its_own_parse_boundary`), and N23
  additionally closes it at its own boundary via `_assert_closed`, which applies the
  banned-name check to every object the schema does not constrain. The schema
  directory was not modified: it is outside this node's write set. N13's owner should
  decide whether free-form domain fields warrant a `propertyNames` constraint or an
  explicit spec-9 exception, since a genuinely free-form unit domain payload may be
  the intended design.

## Invalidated descendants

None. Generation 3 is additive: the two keyword-only helpers, every adapter, and
every previously recorded claim are unchanged, and this node's 152 generation-2
tests still pass alongside the 16 new ones. N30 is unblocked on this finding once
`graph.binding_inventory()` picks up `MODEL_BOOKKEEPING_NODES` (see above).

## Hashes

| Path | sha256 |
|---|---|
| plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| plans/26_langgraph_curriculum_factory/prompts/N23_model_nodes.prompt.v1.md | 2cc6ccd0adaccc8c4768d5cb0ada3fc196aa8c4339e29a9bbe96a31bd9c24344 |
| plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md | c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5 |
| plans/26_langgraph_curriculum_factory/results/N11_STATE_REDUCERS.result.v1.md | c89f166596633e2027f04daa03fca9a33e9f23f2c1346f77817e44b8c03dc30e |
| plans/26_langgraph_curriculum_factory/results/N13_TRANSPORT_AUTH.result.v1.md | aacb3187bfe11f1e16b4eafebab6fba5a8ae7ba0136148b26fafac7f3adb2a71 |
| plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| runtime/langgraph_factory/state.py | 873d640ff2b7e677818fa74d514211e104797b3d3d48dfad4d7d7d47197cd74a |
| runtime/langgraph_factory/reducers.py | 05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf |
| runtime/langgraph_factory/transport.py | 111474fc70ae5cb8a3e95ea8e53f035141eca795138956a1c9879159958d87af |
| runtime/langgraph_factory/egress.py | 837410dad45a7deb8ef761e3636700a7fbde9f45ff6d97d8b4ba7b5c96383f52 |
| runtime/langgraph_factory/config/model_jobs.v1.yaml | 7b5d168c106ad428dc59600765a7c2960f16e7dc53e735d0ac232b42096e8a96 |
| runtime/langgraph_factory/schemas/M02_create_unit_domain_data.schema.json | 311b48b3b85c4fcc2e549a2becfe7b3879a38ec4be59c2ff3e39a3522a5e2232 |
| runtime/langgraph_factory/model_nodes.py | 4b81e4754c04d26635e239e1f55b330979c020ae9aff2cc0f4506afe99769496 |
| tests/runtime/test_plan26_model_nodes.py | 4b0a29c5eaa508ed20f93f981d1eb3ab07a99c108cb6f6b51abcc2b8288ffdb2 |
| runtime/langgraph_factory/routing.py (N20, read for the guard-table proof) | efcc6db169399129e4d3825b3fce5c11501a44a08f0e45433cfadcb7e6361bee |
| runtime/langgraph_factory/unit_graph.py (N30, read for the D90/D91 contract) | fe1226d42c97318f9ddefaefc802510cdb20593040ace894d078201bd040cd6f |
