# Plan 21 historical-regression QA — v3 targeted closure

## Verdict

**FAILED_TARGETED_CLOSURE — 2 Critical, 1 High, 0 Medium, 0 Low.** The frozen package closes the literal empty-array, cross-run, cross-node, and illegal failure-class examples from v3, but it still admits connected false-evidence and continuation-replay counterexamples. Its run vocabulary is now exact; its claimed observed unit vocabulary is still false to the repository and Plan 19 migration boundary. Under `review_protocol.design_qa_exhaustion.failed_closure_status`, this requires a new Plan 21 version (`graph_engineered_subscription_execution.plan.v1.yaml:499-508`).

## Targeted audit and executable results

I re-tested only the v3 Critical/High findings and the connected controls authorized by the targeted-closure rule. I did not edit or review any source artifact.

- `python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py` -> `plan21_bootstrap=PASS`.
- The same command with `--self-test` -> `plan21_bootstrap=PASS`.
- An independently constructed P6 `PASS` with empty `test_results` and `artifact_hashes` is rejected by `validate_phase_event`.
- The same event with the exact 24-test and authorized-output keys, but with every evidence/artifact value fabricated as `000...000`, is accepted: `fabricated_all_zero_evidence=ACCEPTED`.
- Independent resume mutations report `cross_run=REJECTED` and `cross_node=REJECTED`.
- Calling `validate_resume` twice with the identical continuation, command, and current state reports `same_continuation_admission_1=ACCEPTED` and `same_continuation_admission_2=ACCEPTED`.
- Validating the live run enum `IN_PROGRESS, PARTIAL, INTERRUPTED, BLOCKED, COMPLETE` against P0's observed-run contract succeeds. Validating the live controller policy enum `ACCEPTED, BLOCKED, SYSTEM_FAILURE` against P0's observed-unit contract fails.

## Findings and dispositions

### Critical — C1 remains open through a connected false-evidence PASS

**Disposition: literal empty-evidence example closed; required evidence authenticity remains open.** The schema now requires nonempty tests/artifacts and a PASS-specific all-PASS shape (`contracts/phase_result.schema.v1.json:6-46`). `validate_phase_event` also checks the exact node test/artifact denominators and their set digests (`tools/validate_plan.py:48-70`), so the exact v3 empty-array witness is rejected.

The admission helper never reads evidence or artifact bytes and never recomputes any supplied hash. After schema validation it compares only current bindings, identifier sets, set digests, status, and nullness (`tools/validate_plan.py:48-70`). Its own supposed-valid P6 fixture fills every evidence and artifact hash with the same 64-zero string and admits it (`tools/validate_plan.py:537-553`). My independently constructed equivalent is also admitted. Thus an event can satisfy `P6_PASS` and select `E-P6-APPROVED` (`graph_engineered_subscription_execution.plan.v1.yaml:151,397-423,436`) with no evidence or authorized output having those bytes.

This contradicts the registered `artifact_hash_recompute` admission check and graph invariant (`graph_engineered_subscription_execution.plan.v1.yaml:31-43,482`) and the orchestrator's explicit requirement to recompute instead of trust claims (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:17-25,34-37`). Naming a future controller behavior does not close the current executable counterexample used to certify the frozen graph.

**Required remediation in a new version.** Give the bootstrap admission check a byte/path evidence map (or an independently recomputed trusted digest map) and compare every test evidence and authorized artifact value against it before any PASS guard is evaluated. Replace the all-zero positive fixture with real temporary bytes, then add a same-denominator wrong-hash mutation and prove rejection.

### Critical — C2 remains open through replayable, self-attested resume authority

**Disposition: origin/run/node/digest binding closed; single-use and authorization ownership remain open.** The continuation now binds run, suspended/allowed node, source event/checkpoint, all pinned digests, attempt, reason, and `consumed` (`contracts/continuation.schema.v1.json:4-10`). The resume command binds the continuation id/hash and target (`contracts/resume_command.schema.v1.json:4-6`). `validate_resume` correctly rejects cross-run, cross-node, stale-source, and unbound-continuation examples (`tools/validate_plan.py:73-91,609-642`). This closes the P2-pause-to-P6 and originless-resume bypasses from v3.

However, `validate_resume` receives no runtime state or consumed-id set and performs no consumption/update. It only validates that the submitted continuation says `consumed: false` (`tools/validate_plan.py:73-91`; `contracts/continuation.schema.v1.json:9`). The identical continuation and command therefore pass twice in the independent counterexample. It also treats any syntactically valid `operator_authorization_hash` as authorized; neither that hash nor `command_id` is recomputed or matched to a trusted operator authorization (`contracts/resume_command.schema.v1.json:4-6`; `tools/validate_plan.py:73-91,625-631`). The RESUME guards then trust controller-claimed admission/binding booleans (`graph_engineered_subscription_execution.plan.v1.yaml:183-189`).

This directly violates the registered `single_use_resume`, runtime `consumed_continuation_ids`, invariant, and P1 negative-test promise (`graph_engineered_subscription_execution.plan.v1.yaml:43,53-76,483`; `prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:25-27`). It preserves the duplicate-resume case explicitly required by the v3 remediation and can replay a stale capability after its first successful use.

**Required remediation in a new version.** Validate against the current persisted `active_continuation_hash` and `consumed_continuation_ids`; atomically append the id and clear the active continuation before emitting RESUME; reject a second use. Bind `command_id` and `operator_authorization_hash` to independently verified command/operator bytes rather than caller-supplied shape. Add executable duplicate, fabricated-authorization, and already-consumed witnesses to the bootstrap and P1/P3 release denominator.

### High — C3's run repair is exact, but the observed unit lifecycle is still impossible

**Disposition: v3 run-status contradiction closed; exact Plan 19 unit/run migration remains incomplete.** P0 now separates observed and target vocabularies, preserves the live run enum exactly, and adds run-level `SYSTEM_FAILURE` in the target migration (`contracts/baseline_contract.schema.v1.json:23-27`). That matches the authoritative run schema (`schemas/run_lifecycle.schema.v1.json:20-28`) and Plan 19's instruction to extend the single run record (`plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:30-44`).

The same baseline contract hard-codes observed unit states as only `ACCEPTED, BLOCKED`, while the live authoritative controller policy already declares `ACCEPTED, BLOCKED, SYSTEM_FAILURE` (`contracts/baseline_contract.schema.v1.json:23-25`; `policy/controller.v1.yaml:58`). The independent schema probe confirms that this live list is rejected. The repository also emits `ACCEPTED_PENDING_REVIEW` and counts it as completed today (`runtime/session_bridge.py:352-392`; `runtime/run_state.py:24-27`), exactly the Plan 19 defect that P4 must migrate rather than erase from the observed baseline (`plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:30-40,145-157`).

Consequently P0 cannot truthfully freeze its required separate observed unit vocabulary (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:12-19`) and the single generic `added_status: SYSTEM_FAILURE` falsely describes an already-observed unit-policy value as newly added. This remains an impossible-baseline/lifecycle-truth defect connected to v3 C3.

**Required remediation in a new version.** Freeze each live namespace separately (policy terminal states, emitted unit receipt states, run states, and plan-document states), then provide explicit typed mappings/retirements for `ACCEPTED_PENDING_REVIEW`, policy `SYSTEM_FAILURE`, legacy meta states, and the added run-level `SYSTEM_FAILURE`. Make a live-policy/emitter mutation fixture reject every omitted or invented observed value.

### v3 H1 is closed

The result schema now defines closed outcome/failure-class pairs and exact prerequisite reason relationships (`contracts/phase_result.schema.v1.json:49-58`). The three pause guards bind node, outcome, failure class, exact reason, controller admission, and continuation validity (`graph_engineered_subscription_execution.plan.v1.yaml:180-182`). The bootstrap's concrete `FACTORY_DEFECT` prerequisite-pause mutation is rejected (`tools/validate_plan.py:571-574`). No unresolved Critical/High remains in this disposition.

## Affected round-2 controls

| Historical control | Targeted recheck |
|---|---|
| Cold second-process resume | **Intact at prompt level.** P6-T14 requires a first real process and a separate clean `--resume` process (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:24`). The replay hole in C2 prevents assurance that this is single-use. |
| Live multi-unit `--all` | **Intact at prompt level.** P6-T21 requires a bounded three-unit real `--all`, termination during unit 3, separate clean `--resume`, and a fresh Arduino `--all` (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:31`). |
| Exactly four isolated reviews | **Intact.** P6-T22 requires exactly four and retains 3/5, duplicate-role/identity, shared-session, sibling-verdict, and malformed negatives (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:32`). |
| Exact RT-7 scope, mirror, gates, dirty-overlap pause | **Intact.** P6-T23 retains every named site, exact locator replacement, all six gates, and fail-closed pre-existing-dirty overlap behavior (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:33`). The typed pause mapping remains closed (`contracts/phase_result.schema.v1.json:50,58`). |
| Format-aware census/anomaly contract | **Intact.** P0-T03/T10/T11 retain Markdown/YAML/issue parsing, counts, anomalies, mutations, and later-fixed findings; P6-T24 independently reruns it (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:28,35-36`; `prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:34`; `contracts/historical_findings.schema.v1.json:6-30`). |

These controls remain assigned, but C1 allows their evidence to be counterfeited and C2 allows a resume capability to be replayed. The targeted closure therefore cannot PASS.
