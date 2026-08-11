# N00 traceability matrix (frozen)

Every normative (MUST/MUST NOT/SHOULD/MAY) Plan 26 spec section, every QA
criterion, and every adversarial case maps to exactly one owning N-node.
Built from spec section 19 (already-proposed mapping) plus [[node_ownership.v1]]
for D/M-node-level detail, and cross-checked against
`implementation.graph.v2.yaml` write sets so no owner is asserted without a
corresponding `writes` entry.

## Spec section -> owning N-node

| Spec section | Subject | Owning N-node |
|---|---|---|
| 0, 1 | governing decision, scope/non-goals | N00 (contract only; no code) |
| 2 | baseline assessment, reuse/adapt/replace table | N00 (baseline record); individual adaptations owned by the N-node that touches the adapted file |
| 3 | dependency/API contract | N10 |
| 4 | compiled graph ownership, one production path, `prepare_episode_invocation` | N20 (builder), N21 (`prepare_episode_invocation`), N40 (CLI sole-path enforcement) |
| 5 | typed state, reducers, persisted-state table | N11 |
| 6.1 | common node rules (idempotent replay, checkpoint boundary, guard ordering) | N22 (deterministic bodies), N23 (model bodies) |
| 6.2 | D00-D98 catalogue | per [[node_ownership.v1]] table |
| 6.3 | eight model job types | N23 |
| 7.1-7.3 | transport envelope, Codex/Gemini CLI contracts | N13 |
| 7.4 | external-data authorization | N13 |
| 8.1 | normal graph edges | N20 (skeleton), N30 (unit loop), N32 (workbook branch) |
| 8.2 | conditional-edge/guard table | N20 (`routing.py`), extended by N30/N32 registrations |
| 9 | context graph / structural isolation | N13 (workspace isolation), N23 (projection builders) |
| 10 | fan-outs/joins/correlation keys | N30 (source/visual), N32 (page review joins) |
| 11.1-11.2 | SqliteSaver, thread/namespace, dual persistence | N21, N12 (evidence layer) |
| 11.3 | graceful interruption / crash recovery | N21 (mechanics), N22 (D96 body) |
| 11.4 | resume algorithm | N21 |
| 12 | targeted repair architecture | N31 |
| 13.1 | unit denominator / acceptance | N31 |
| 13.2 | workbook denominator | N32 |
| 14 | terminal design / exit codes | N22 (`nodes/terminal.py` writer), N32 (product-terminal call sites), N40 (CLI exit-code mapping) |
| 15 | filesystem/artifact layout | N12 (artifact/evidence paths); layout resolution frozen in [[node_ownership.v1]] |
| 16 | CLI contract | N40 |
| 17.1 | test layers | every N-node owns its own layer's tests per its `writes` set; N50 owns the adversarial layer specifically |
| 17.2 | adversarial case matrix | N50 (all cases); see mapping below |
| 18 | migration/retirement boundary | N40 (cutover gates), N90 (final audit of the cutover) |
| 19 | (the spec's own traceability matrix) | superseded by this document for N-node purposes; spec section 19 remains authoritative for spec-internal cross-references |
| 20.1 | resolved decisions | N00 (already incorporated into this contract set) |
| 20.2 | external prerequisites before activation | N60 (gates `PASSED` vs `NOT_AVAILABLE`) |
| 21 | spec quality-gate checklist | N90 (final audit re-verifies every checked item against implementation, not against the spec's own self-assessment) |

## QA criteria (`qa_criteria.v2.md`) -> owning N-node

| Criterion | Owning N-node |
|---|---|
| reject project-management graph / handwritten controller / legacy fallback | N20, N40 (structural enforcement); N90 (final check) |
| reject LangChain/provider-SDK/HTTP model imports | N10 (forbidden-import lock check), N13 (transport), N50 (`test_no_second_production_factory`-adjacent import audit) |
| reject model-controlled routing/joins/retries/admission/acceptance/terminals | N20/N30/N31/N32 (guards remain code-owned), N50 (`test_models_have_no_control_fields`) |
| reject non-product success claims | N90 (`test_no_nonproduct_success` verified independently) |
| reject partial/duplicate/extra/stale/failed/NOT_RUN/cross-unit denominator members | N30 (source/visual joins), N32 (page joins), N50 (adversarial proof) |
| reject replay of committed external calls / mutated accepted bytes | N21, N31 |
| reject resume after drift | N21 |
| reject misuse of PAUSED_PREREQUISITE | N22 (D30 classification) |
| exact pinned dependency + API-contract tests | N10 |
| complete typed state/reducer authority and topology reports | N11, N20 |
| exactly eight model jobs, package-relative prompts/schemas | N13, N23 |
| structural model-workspace isolation + authorization before transmission | N13 |
| exact fan-out/barrier and every-page denominators | N30, N32 |
| dual checkpoint/evidence correlation + crash/resume matrix | N21, N12 |
| targeted immutable repair + accepted-unit/workbook release denominators | N31, N32 |
| one production CLI path, no legacy/simulation fallback | N40 |
| full deterministic/integration/adversarial/regression suites | every N-node (own layer) + N50 (adversarial/regression) |
| authorized live product evidence before activation, else `IMPLEMENTED_NOT_ACTIVATED` | N60, N90 |
| runtime egress enforcement | N13 |
| CI regenerates lock, fails on drift | N10 |

## Adversarial case (section 17.2) -> verification test -> owning N-node

All owned by N50 (`tests/runtime/test_plan26_adversarial.py`), since that is
the sole node whose `writes` set includes this file. N50 exercises behavior
implemented by the N-nodes named per case (source of truth for *why* the
test should pass), but does not modify their files:

| Case (abbreviated) | Behavior owner | Test name |
|---|---|---|
| non-product success claims | N90/N22 terminal writer | `test_no_nonproduct_success` |
| manifest-neutral dynamic run (1/7/41 units) | N22 (D02) | `test_manifest_neutral_dynamic_run` |
| model output proposes control fields | N23 schemas | `test_models_have_no_control_fields` |
| prompt resolved outside package | N13 | `test_prompts_are_package_relative` |
| malformed/multiple/trailing CLI JSON | N13 | `test_malformed_cli_output_fails_closed` |
| decided vs. executed model mismatch | N13 | `test_executed_model_must_match_route` |
| same-family reviewer | N13/N23 | `test_same_family_review_rejected` |
| exact fan-out denominator violations | N30 | `test_exact_fanout_denominators` |
| every-page review requirement | N32 | `test_every_unit_page_required`, `test_every_workbook_page_required` |
| stale hash | N31 | `test_stale_hash_rejected` |
| repair boundary/immutability | N31 | `test_repair_boundary_and_immutability` |
| local repair not whole-unit regen | N31 | `test_local_repair_is_targeted` |
| repair bound reserved before activation | N23 (D90), N31 | `test_repair_bound_reserved_first` |
| resume preserves accepted bytes | N21 | `test_resume_preserves_accepted_bytes` |
| duplicate continuation prevented | N21 | `test_duplicate_continuation_prevented` |
| workbook exact manifest coverage | N32 | `test_workbook_exact_manifest_coverage` |
| workbook repair cannot change unit | N32 | `test_workbook_repair_cannot_change_unit` |
| no second production factory | N40 | `test_no_second_production_factory` |
| external-data authorization precedes transmission | N13 | `test_external_data_authorization_precedes_transmission` |
| worker context structurally bounded | N13 | `test_worker_context_is_structurally_bounded` |
| dual persistence correlation | N21/N12 | `test_dual_persistence_correlation` |
| resume bootstrap skips fresh write-once nodes | N21/N22 | `test_resume_bootstrap_skips_fresh_write_once_nodes` |
| orphan recovery is read-only/terminal-only | N21/N22 | `test_orphan_recovery_is_read_only_and_terminal_only` |
| checkpoint thread/namespace contract | N21 | `test_checkpoint_thread_and_namespace_contract` |
| visual Send/reduce barrier (mixed/empty) | N30 | `test_visual_send_reduce_barrier` |

## Coverage check

Every normative section (0-21) and every QA criterion has exactly one primary
owner above; sections spanning multiple N-nodes are split by sub-responsibility,
never left dual-owned for the same artifact. Cross-checked against
`implementation.graph.v2.yaml`: every N-node referenced above appears with a
matching `writes` entry for the artifact it is credited with; no owner is
asserted for a file outside that node's declared write set.
