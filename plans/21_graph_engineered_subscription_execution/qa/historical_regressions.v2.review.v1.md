# Plan 21 v2 historical-regression and repository QA — review 1

## Verdict

**CHANGES_REQUIRED — 3 Critical, 1 High, 0 Medium, 0 Low.** The v2 overlay is byte-bound to the current v1 graph manifest and both bootstrap commands pass. It repairs the literal all-zero hash and sequential duplicate-resume witnesses from the v1 closure. The effective package still permits approval from arbitrary non-test bytes outside any controller-verified authorized root, treats hash-shaped P6 subtask outputs as committed, and has no executable atomic compare-and-swap: two independent callers using the same unconsumed checkpoint both succeed. The corrected unit vocabulary is present in v2 but is not incorporated into the typed P0 state that P4 consumes, leaving the false v1 baseline active alongside an unbound addendum.

## Audit basis and executable probes

I independently audited the current v2 overlay, its schemas, controller validator, every v2 GOAL/TEST/LOOP addendum, and the digest-bound v1 plan, prompts, schemas, and historical controls relevant to this review. I did not edit plan, contract, prompt, or tool bytes.

- `python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan_v2.py` -> `plan21_v2_bootstrap=PASS`.
- The same command with `--self-test` -> `plan21_v2_bootstrap=PASS`.
- The declared v1 base SHA-256 is correct: `171af5dff71d33331f263bf73c84219790209700cd15d403f63ee207805b561e` (`graph_engineered_subscription_execution.plan.v2.yaml:4-7`; `tools/validate_plan_v2.py:52-59`).
- The prior fabricated-zero event mutation is rejected when it disagrees with source bytes (`tools/validate_plan_v2.py:323-383`).
- Independent counterexample: I populated all 24 compiled P6 test IDs and all authorized artifact IDs with existing regular files containing only arbitrary non-test/non-artifact bytes, supplied an unrelated `resolved_authorized_roots` value, and called `validate_phase_event_v2` with the arbitrary temporary directory as `evidence_root`. Result: `untrusted_root_arbitrary_test_bytes=ACCEPTED`.
- Independent counterexample: an exact eleven-ID P6 ledger with every subtask `COMMITTED` and every `output_hashes.claimed` value equal to 64 zeroes passes: `exact_11_subtasks_all_zero_outputs=ACCEPTED`.
- Independent counterexample: two calls holding deep copies of the same valid, signed, unconsumed generation-1 resume state both pass and return generation 2: `independent_stale_checkpoint_caller_1=ACCEPTED` and `_2=ACCEPTED`.

## Findings

### Critical — C1: P6 evidence is byte-hashed but not bound to an authorized root or an executing test producer

The overlay promises that evidence sources are existing regular files inside resolved authorized roots and that P6 release independently recomputes real evidence (`graph_engineered_subscription_execution.plan.v2.yaml:22-26,72-74`; `prompts/v2/P6_end_to_end_release_and_supersession.addendum.v2.md:3-12`). The implementation takes `evidence_root` as a caller-supplied argument. `_safe_source` only proves containment inside that argument; neither it nor `validate_evidence_manifest` compares the root to a controller-owned authorized-root set (`tools/validate_plan_v2.py:101-109,112-157`). The `current` fixture itself contains only caller-populated relative path maps and no authorized-root binding (`tools/validate_plan_v2.py:323-353`).

The test-source schema carries only a caller-stated `PASS`, path, size, and hash; it has no command, exit status, runner identity, receipt schema, or trusted producer binding (`contracts/evidence_manifest.schema.v2.json:4-16`). Admission merely requires nonempty bytes and matching hashes, then copies the event's `PASS` claim (`tools/validate_plan_v2.py:125-135`). Consequently arbitrary bytes from an arbitrary supplied root satisfy all 24 P6 tests. This is the exact historical non-executing-test/false-evidence acceptance class that P6-T09–T11 and the v1 stop rule prohibit (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:19-22,47-55`).

The compiled subtask layer provides no backstop. `validate_phase_ledger_v2` checks only the exact subtask-ID set after v1 shape/idempotency validation (`tools/validate_plan_v2.py:165-168`). The inherited ledger schema accepts any hash-shaped `output_hashes` value (`contracts/phase_ledger.schema.v1.json:4-10`). My exact eleven-subtask, all-zero-output ledger passes, contradicting the v2 release requirement that every committed output exist and hash correctly (`prompts/v2/P6_end_to_end_release_and_supersession.addendum.v2.md:9-12`).

**Impact.** `P6_PASS` can be admitted without running the historical matrix, live three-unit sequence, four judges, RT-7 gates, or census. Exact denominators prevent omission but do not prevent fabricated execution, reproducing issues 002/007 and the prior Plans 9–20 false-evidence/non-executing-test class.

**Required remediation.** Make the controller derive—not accept—the canonical authorized evidence roots and compiled source paths from digest-bound state. Require each test source to be a schema-valid immutable runner receipt binding command/test implementation digest, start/finish or exit result, run/node/attempt, and produced bytes; keep model workspaces unable to write those receipts. Validate every committed subtask output against resolved existing files or a trusted receipt and bind the ledger to the admitted evidence manifest. Add arbitrary-content, caller-chosen-root, model-writable-root, fabricated-runner-receipt, and exact-denominator/all-zero-ledger mutations.

### Critical — C2: resume validation is not an atomic durable transition and admits concurrent cold replay

The v2 plan and P3 addendum require a durable compare-and-swap that consumes the continuation and command before activation, including cold-process and crash-boundary rejection (`graph_engineered_subscription_execution.plan.v2.yaml:27-32,51-52,75`; `prompts/v2/P3_durable_graph_runtime.addendum.v2.md:3-14`). Signature, external-record, run/node/attempt, digest, expiry, and sequential consumed-set checks are materially implemented (`tools/validate_plan_v2.py:171-222`). The old forged-authorization and “second call using returned updated state” witnesses therefore fail (`tools/validate_plan_v2.py:431-474`).

But `validate_resume_once` reads no checkpoint store, takes no expected persisted generation, acquires no lock, performs no filesystem/database transaction, and writes nothing. It copies the caller's dictionary, appends IDs, increments a number, and returns the copy (`tools/validate_plan_v2.py:221-227`). Two independent callers that read the same generation-1 durable bytes can therefore both validate successfully and each return generation 2. My independent signed-authorization probe reproduces exactly that result.

**Impact.** Concurrent or cold replay can activate the suspended node twice, duplicating side effects and invalidating the single-use capability guarantee. The bootstrap self-test proves ordinary sequential state threading, not the required atomic cold-process transition.

**Required remediation.** Implement and test a real durable CAS transaction over checkpoint generation, active continuation, consumed continuation IDs, and consumed command IDs. Activation must occur only after one committed consume; a losing stale process must fail. Add two actual processes racing from the same on-disk checkpoint plus crash-before-commit, crash-after-commit-before-activation, and restart-after-commit witnesses.

### Critical — C3: the corrected unit vocabulary is not part of the typed P0 state consumed by P4

The v2 overlay states the exact live vocabulary—`ACCEPTED`, `ACCEPTED_PENDING_REVIEW`, `BLOCKED`, `SYSTEM_FAILURE`—makes pending review nonterminal, and assigns migration to P4 (`graph_engineered_subscription_execution.plan.v2.yaml:67-71`; `prompts/v2/P0_contract_and_evidence_freeze.addendum.v2.md:3-15`; `prompts/v2/P4_curriculum_graph_migration.addendum.v2.md:3-13`). This accurately reflects the live policy and emitter (`policy/controller.v1.yaml:58`; `runtime/session_bridge.py:356-369`) and Plan 19's required migration semantics (`plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:30-41,145-157`).

The effective node merge only adds `P0.assurance_addendum.v2.yaml` to P0's authorized output list and adds required subtask IDs; it does not add the v2 schema to P0's output schemas or typed state (`tools/validate_plan_v2.py:93-98`; `graph_engineered_subscription_execution.plan.v2.yaml:37-45`). The inherited `P0_contract_bundle` still contains only the v1 baseline, findings, and denominator (`contracts/p0_contract_bundle.schema.v1.json:4-10`; `graph_engineered_subscription_execution.plan.v1.yaml:93-100`). That v1 baseline still requires the false observed unit list `ACCEPTED, BLOCKED` (`contracts/baseline_contract.schema.v1.json:23-27`). P4 consumes `state://P0_contract_bundle` and explicitly declares the v1 baseline schema, not the v2 assurance addendum (`graph_engineered_subscription_execution.plan.v1.yaml:336-352`).

Even the addendum's `base_contract_hash` is shape-only: `validate_assurance_bytes` never receives or hashes a baseline contract, and its positive fixture uses 64 zeroes (`contracts/baseline_assurance_addendum.schema.v2.json:4-9`; `tools/validate_plan_v2.py:230-287,419-420`). Thus the correct list can coexist with any contradictory baseline without a relational failure.

**Impact.** P0 must still produce a schema-valid false lifecycle baseline, while P4 has no typed route to the correcting addendum. Plan 19 migration ownership is stated in prose/overlay metadata but absent from the producer-consumer state contract, reproducing the impossible-baseline and stale-lifecycle defects from issue 007 and the v1 closure.

**Required remediation.** Replace or version `P0_contract_bundle` with one effective v2 schema that incorporates the correct observed/intermediate/terminal namespaces and migration contract, add it to P0 output/state and P4 input schemas, and make `base_contract_hash` recompute from the actual base contract bytes. Reject conflicting base/addendum lists and prove P4 consumes the exact v2 state.

### High — H1: the overlay digest freezes only the v1 manifest, not the inherited behavioral package

The overlay calls v1 frozen and digest-bound, but `base` contains only the v1 plan path/hash, and `load()` verifies only those bytes (`graph_engineered_subscription_execution.plan.v2.yaml:4-7`; `tools/validate_plan_v2.py:52-59`). The v2 effective behavior also inherits the v1 validator, schemas, contracts, and P0–P6/P_ALL prompts. None of those bytes or an aggregate dependency digest is recorded in the overlay. `validate()` reads whichever files currently occupy those paths and checks structure/test IDs, not their frozen hashes (`tools/validate_plan_v2.py:28-37,290-308`; `tools/validate_plan.py:226-243`).

**Impact.** Exact historical semantics in the inherited P6 prompt—including cold `--resume`, three-unit `--all`, four-review negatives, and literal RT-7 sites/gates—can drift while the declared v1 base SHA remains valid. That defeats identical-byte review and active-run pinning for the overlay's behavioral base.

**Required remediation.** Bind an effective-package manifest containing canonical hashes for the v1 plan, validator, schemas, all inherited prompts/contracts, v2 overlay/addenda/contracts, and relevant policy/route registries. Bootstrap and runtime compilation must recompute the aggregate before execution/review and reject any dependency drift.

## Named historical-control disposition

| Control | Current assessment |
|---|---|
| Exact live unit vocabulary and Plan 19 migration | **Values/owner are correct in overlay, but structurally unclosed by C3.** The live four-value list and P4 ownership are explicit (`graph_engineered_subscription_execution.plan.v2.yaml:67-71`), yet the typed P0→P4 state remains v1. |
| P6 source-bound evidence | **Open — C1.** Real bytes and recomputed hashes are enforced, but authorized-root and executing-producer provenance are not. |
| Compiled P6 subtask denominator | **Partial — C1.** Exact eleven IDs are externally supplied by the effective node and a one-ID ledger fails (`graph_engineered_subscription_execution.plan.v2.yaml:62-65`; `tools/validate_plan_v2.py:385-393`), but fabricated committed output hashes pass. |
| Atomic cold-process single-use resume | **Open — C2.** Signed binding and sequential replay rejection work; no durable CAS exists. |
| Three-unit live `--all` and cold second process | **Prompt preserved.** The exact live sequence remains at base P6-T21 and is re-required by v2 (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:31`; `prompts/v2/P6_end_to_end_release_and_supersession.addendum.v2.md:13-16`). Its release evidence can be fabricated under C1. |
| Exactly four isolated reviews | **Prompt preserved.** Exact four plus 3/5, duplicate identity/role, shared session, sibling verdict, and malformed negatives remain (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:32`). Its release evidence can be fabricated under C1. |
| RT-7 exact scope and dirty-overlap pause | **Prompt preserved.** All five sites, six gates, literal before/after, and fail-closed dirty-overlap rule remain (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:33`). Current relevant pre-existing work is still dirty (`plans/03_folder_refactoring/folder_refactoring.plan.v6.md`, `policy/checks.v1.yaml`, `tests/gates/fr_p5_unit.py`, `runtime/readability.py`), so execution must pause absent frozen authorization. |
| Format-aware census/anomaly contract | **Prompt/contract preserved.** P0 still requires Markdown/YAML findings, aggregates, anomalies, later-fixed retention, and mutations; P6 independently reruns it (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:28,35-36`; `prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:34`; `contracts/historical_findings.schema.v1.json:6-30`). Its P6 proof can be fabricated under C1. |

The package cannot receive historical-regression PASS until all three Critical findings and H1 are closed in a new version as required by the v2 iteration rule (`graph_engineered_subscription_execution.plan.v2.yaml:78-82`).
