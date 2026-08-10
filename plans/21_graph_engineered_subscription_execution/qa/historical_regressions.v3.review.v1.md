# Plan 21 v3 historical-regression and repository QA — review 1

## Verdict

**FAIL — 2 Critical, 2 High, 0 Medium, 0 Low.** The current v3 package passes bootstrap/self-test, binds all 45 inherited behavioral files, implements a real SQLite resume CAS, and repairs the composite P0/P4 lifecycle contract at plan level. It still admits signed PASS evidence for a command other than the compiled test, accepts `/etc/hosts` as valid Markdown or octet-stream artifact content, and has no typed/signed artifact-registry enforcement at admission. Separately, its event, evidence manifest, ledger, and subtask receipts form an infeasible circular commitment because the ledger is an authorized event artifact while embedding the final event and manifest IDs. The exact eleven-subtask validator also accepts one unrelated file and one colliding idempotency key for every signed subtask, and distinct controller/model UID is caller-asserted rather than OS-attested.

## Audit basis and executable probes

I independently audited the exact current v3 plan/schema, all v3 contracts, validator, GOAL/TEST/LOOP addenda, and the digest-selected v1/v2 behavioral base. I did not edit any target artifact.

- `python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan_v3.py` -> `plan21_v3_bootstrap=PASS`.
- The same command with `--self-test` -> `plan21_v3_bootstrap=PASS`.
- Independent recomputation returns exactly `(45, 29369fd1cfce2a13aac39a3e5b27ed03b0a016cf500a7deb2828948fb082e755)`, matching the declared behavioral base (`graph_engineered_subscription_execution.plan.v3.yaml:4-8`; `tools/validate_plan_v3.py:73-87,446-452`).
- An explicit FAIL assertion is schema-invalid, as intended (`contracts/test_receipt.schema.v3.json:4-8`; `tools/validate_plan_v3.py:502-504`).
- A real Ed25519-signed P6 receipt with the correct subject but receipt `command_digest=000...000` passes even when current compiled `test_command_digests[P6-T01]=111...111`: `signed_wrong_compiled_command=ACCEPTED`.
- `_validate_artifact_content` accepts the live `/etc/hosts` bytes as both `text/markdown` and `application/octet-stream`, despite P6's literal `/etc/hosts` negative.
- Eleven correctly signed P6 subtask receipts, all pointing to the same unrelated output and all ledger entries using the same idempotency key, pass: `signed_11_same_unrelated_output_and_idempotency_key=ACCEPTED`.
- Two independent Python processes racing from one SQLite generation produce exactly one `True` and one `False`; a later cold process returns `False`. The prior same-snapshot/cold replay is closed.
- A valid composite P0 fixture passes; changing its recomputed baseline hash or shortening the four-state observed vocabulary fails.
- A trust root owned by the actual calling-process UID passes after the same process merely claims another `model_uid`: `same_process_claimed_distinct_model_uid=True` with actual UID 501 and claimed model UID 502.

## Findings

### Critical — C1: signed P6 evidence is not bound to the compiled command, and unrelated real artifact bytes remain admissible

The test receipt schema carries `command_digest`, but `validate_test_receipt` compares only run, node, attempt, test ID, and subject digest before checking time and signature (`contracts/test_receipt.schema.v3.json:4-8`; `tools/validate_plan_v3.py:200-210`). It never compares `command_digest` to a compiler-owned expected command digest or runner binary digest. My independent receipt was signed by a real Ed25519 key, used the exact current subject, exit zero, and all-PASS assertions, yet named the deliberately wrong command digest; it was admitted. A deterministic controller can therefore sign the result of `true`, a no-op, or another unrelated command under P6-T01–T24.

Artifact admission has the parallel defect. `_validate_artifact_content` requires JSON/YAML parseability, a Markdown `#`, or nothing at all for octet streams; schema validation is optional (`tools/validate_plan_v3.py:222-248`). The current `/etc/hosts` contains comments and therefore passes both Markdown and octet-stream validation. This directly contradicts the v3 P6 negative that `/etc/hosts` and unrelated text fail (`prompts/v3/P6_provenance_release.addendum.v3.md:7-12`).

The full manifest function does not independently close this route. It obtains `artifact_contract_registry` from caller-provided current state and checks the artifact against that mapping (`tools/validate_plan_v3.py:266-299`), but v3 defines no schema, signature, ID, path root, or digest for the P1-produced registry. The plan only declares metadata fields and intended coverage (`graph_engineered_subscription_execution.plan.v3.yaml:30-34`). A registry/current mapping that labels `/etc/hosts` as a schema-less Markdown or octet-stream output is therefore accepted by the available admission logic.

**Impact.** P6 can produce cryptographically valid but semantically unrelated “test” and artifact provenance without executing the compiled historical checks. This reproduces the non-executing-test, false-evidence, and file-presence acceptance classes from issue 002 and prior Plans 9–20.

**Required remediation.** Bind every receipt to compiler-owned `test_command_digest`, deterministic-runner executable hash/version, and the exact test implementation/fixture closure; verify those values in admission. Add a signed, digest-bound artifact-contract-registry schema and compiler output, bind its ID into runtime/event state, constrain every source to its resolved authorized root, and require a non-null semantic schema or type-specific verifier for every acceptance artifact. Run the literal fully assembled `/etc/hosts`, valid-but-unrelated JSON/Markdown, wrong signed command, and no-op runner witnesses through P6 admission.

### Critical — C2: the P6 event, evidence manifest, ledger, and subtask receipts form an impossible hash cycle

The inherited P6 node makes its phase ledger an authorized output (`graph_engineered_subscription_execution.plan.v1.yaml:397-411`). V3 requires the artifact registry to cover every effective-node authorized output (`graph_engineered_subscription_execution.plan.v3.yaml:30-34`), and manifest admission requires exactly that registry while binding each artifact hash into the event (`tools/validate_plan_v3.py:266-271,288-304`). Therefore the event and signed manifest commit to the final ledger bytes.

The v3 ledger simultaneously requires `admitted_event_id` and `evidence_manifest_id`, and every signed subtask receipt embeds those same final IDs (`contracts/phase_ledger.schema.v3.json:3-8`; `contracts/subtask_receipt.schema.v3.json:3-6`; `tools/validate_plan_v3.py:361-383`). The dependency is circular:

`event ID -> ledger hash -> subtask receipt hashes -> event ID + manifest ID`

and

`manifest ID -> ledger hash -> subtask receipt hashes -> manifest ID`.

Because IDs/hashes are SHA-256 commitments, there is no constructive serialization order; satisfying the contracts requires finding a cryptographic fixed point. The bootstrap never constructs a complete valid event/manifest/eleven-receipt ledger fixture, so its separate component tests miss the cycle.

**Impact.** Honest P6 release evidence cannot be produced as specified. Implementations must omit a required artifact, use placeholder IDs/hashes, or bypass final recomputation—each a historical false-evidence or impossible-execution regression.

**Required remediation.** Define a nonrecursive commit order. For example: the signed evidence manifest covers phase outputs excluding controller metadata; the controller admits/signs the event against that manifest; only then does it write signed ledger/subtask receipts referencing the immutable event/manifest IDs. Validate the ledger as a separate controller record required by the success transaction, but do not include its own bytes or descendant receipt bytes in the event/manifest artifact denominator. Add one complete, real, signed eleven-subtask P6 fixture that is serialized in the specified order and independently recomputes every ID/hash.

### High — H1: the exact eleven-subtask ledger does not prove its compiled outputs or idempotency keys

The ledger validator correctly enforces the exact hard-coded P6 ID set, compiler-resolved receipt paths, receipt hashes, event/manifest fields, output-file hashes, and receipt signatures (`tools/validate_plan_v3.py:347-383`). It does not compare each receipt's `output_sources.artifact_id/path` to a compiled per-subtask output contract or the evidence manifest, prevent reuse of one output across receipts, or recompute/uniquely constrain ledger `idempotency_key`. The ledger schema gives that key only `minLength: 20` (`contracts/phase_ledger.schema.v3.json:4-7`).

My independent fixture used all eleven exact IDs and valid signatures, but every receipt claimed the same unrelated file and every ledger entry used `same-idempotency-key-for-all`; validation passed. Thus exact count and signatures coexist with eleven non-executing/colliding subtasks.

**Impact.** Crash recovery can conflate logical subtasks, and a complete P6 ledger can claim full path, guard, live-run, review, history, and supersession work from one unrelated file. This preserves historical idempotency-collision and non-executing-test risk below the event layer.

**Required remediation.** Compile an exact per-subtask input and output contract; recompute each idempotency key from `{execution_contract_digest}:P6:{attempt}:{subtask_id}:{input_digest}`; require uniqueness; and reconcile the union of signed receipt outputs to the event/manifest artifact and test-provenance graph with explicit, compiler-authorized sharing only. Add the independent all-same-output/all-same-key fixture as a rejection test.

### High — H2: controller/model UID separation is self-attested, not proven by OS or signed launch evidence

`validate_external_trust` compares the authority root's actual owner to `trust.authority_uid` and then checks only that this caller-supplied value differs from caller-supplied `trust.model_uid` (`tools/validate_plan_v3.py:160-180`). Evidence-root admission likewise compares the root's actual UID to current `controller_uid`, then only compares two current-state UID claims (`tools/validate_plan_v3.py:251-258`). No signed process-launch receipt or OS query proves the UID under which model workers actually execute.

The independent counterexample ran as UID 501, created/owned the authority root as UID 501, asserted `model_uid: 502`, and passed. The same OS principal can therefore satisfy the nominal “distinct UID” rule by changing a field, even though it retains owner authority over the supposedly non-model-writable root.

**Impact.** The provenance boundary used to justify controller signatures and fixed evidence paths is not established. A same-principal model/controller deployment can be misclassified as isolated, weakening C1's trust premise and reproducing self-authored evidence risk.

**Required remediation.** Bind controller-service and worker-process identities to externally signed launcher/OS credential evidence. Verify controller effective UID directly, require sandbox launch receipts to state and prove the model process UID, bind both into the execution-contract digest, and test a same-actual-UID/different-claimed-UID witness. File modes alone are insufficient when both roles share the owner UID.

## Reprobed closure and historical controls

| Control | Final v3 assessment |
|---|---|
| Behavioral-base digest | **Closed.** The fixed algorithm selects 45 v1/v2 manifests, schemas, validators, contracts, prompts, research, and assessment files; independent count/hash matches (`tools/validate_plan_v3.py:73-87,446-452`). |
| Explicit FAIL P6 evidence | **Closed narrowly.** FAIL assertions are schema-invalid, but a signed wrong-command PASS remains C1. |
| Real-but-unrelated P6 evidence | **Open — C1.** `/etc/hosts` passes the artifact content validator, and signed receipts do not bind compiled commands. |
| Exact signed eleven-subtask ledger | **Open — C2/H1.** Exact IDs, receipt files, hashes, signatures, and event/manifest fields are checked, but the graph is cyclic and unrelated/shared outputs plus colliding keys pass. |
| Same-snapshot and cold resume | **Closed.** SQLite uses `BEGIN IMMEDIATE`, expected checkpoint generation, unique continuation/command/authorization keys, and commit-before-return (`tools/validate_plan_v3.py:386-414`). Two real processes yielded one success/one rejection; cold replay rejected. The v3 P3 prompt retains crash and activation-order tests (`prompts/v3/P3_atomic_resume_store.addendum.v3.md:3-18`). |
| Composite P0 state and P4 lifecycle | **Closed at plan-contract level.** V3 replaces the effective state schema/readers, including P4 (`graph_engineered_subscription_execution.plan.v3.yaml:24-29`); the P4 addendum consumes only the composite (`prompts/v3/P4_composite_state_migration.addendum.v3.md:3-13`). `validate_p0_bundle` recomputes the v1 baseline hash and enforces exact `ACCEPTED`, `ACCEPTED_PENDING_REVIEW`, `BLOCKED`, `SYSTEM_FAILURE` (`tools/validate_plan_v3.py:417-428`). Independent wrong-hash and shortened-list mutations reject. |
| Three-unit `--all` and cold second process | **Retained in the bound base.** Base P6-T21 still requires a real three-unit `--all`, interruption during unit 3, a separate clean `--resume`, and fresh Arduino `--all` (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:31`). |
| Exactly four isolated reviews | **Retained in the bound base.** Exact four plus 3/5, duplicate identity/role, shared session, sibling-verdict, and malformed negatives remain (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:32`). |
| RT-7 exact scope/pause | **Retained in the bound base.** All five sites, six gates, exact locator change, and fail-closed dirty-overlap pause remain (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:33`). Current named overlaps remain pre-existing dirty work, so execution must pause absent frozen authorization. |
| Format-aware census | **Retained in the bound base.** P0 keeps Markdown/YAML/aggregate/anomaly/later-fixed parsing and mutations; P6 independently reruns it (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:28,35-36`; `prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:34`; `contracts/historical_findings.schema.v1.json:6-30`). |

Because C1, C2, H1, and H2 remain unresolved, v3 cannot receive PASS under its own review protocol (`graph_engineered_subscription_execution.plan.v3.yaml:84-87`).
