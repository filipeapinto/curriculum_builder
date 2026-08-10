# Plan 21 v3 prompt/subscription/security QA — review 1

**Verdict: FAIL**

**Unresolved:** 3 Critical, 3 High. The frozen v3 package does not satisfy its
zero-Critical/High exit rule.

## Scope and verification

I independently reviewed the v3 manifest/schema, all v3 contracts, the complete
v3 validator, all v3 GOAL/TEST/LOOP addenda, and the digest-selected behavioral
base needed to evaluate subscription, identity, trust, evidence, sandbox,
ledger, artifact, and resume behavior. I did not use another review as evidence.

The behavioral base is internally pinned: the validator selects 45 files and
recomputes the manifest's bundle digest. Both documented commands pass:

```text
python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan_v3.py
plan21_v3_bootstrap=PASS

python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan_v3.py --self-test
plan21_v3_bootstrap=PASS
```

The self-test does not compose the attack paths below.

## Findings

### Critical C1 — One signed test receipt can satisfy every P6 test, and the artifact registry remains injectable

The v3 receipt schema correctly rejects an assertion whose own status is FAIL,
requires exit zero, and binds run/node/attempt, subject, command, assertions,
output hashes and timestamps (`contracts/test_receipt.schema.v3.json:3-9`). The
controller also verifies its Ed25519 signature and subject digest
(`tools/validate_plan_v3.py:183-210`). This closes the explicit-FAIL shape tested
in isolation.

The composed manifest loop never requires the receipt's internal `test_id` to
equal the manifest slot currently being checked. `validate_test_receipt` merely
requires that the receipt's ID appears somewhere in the node's required set;
after it returns, the loop binds the file hash to the outer `test_id`
(`tools/validate_plan_v3.py:200-210,266-287`). It also does not compare
`command_digest` or assertion IDs to a compiled per-test contract. Unique paths
therefore do not prevent one signed receipt's bytes from being copied into every
required receipt path.

The new `artifact_contract_registry` has no schema, concrete output path, or
validated P1 artifact. The manifest describes it as P1-produced, but P1 receives
no v3 output and the validator accepts `current.artifact_contract_registry`
directly (`graph_engineered_subscription_execution.plan.v3.yaml:30-34`;
`tools/validate_plan_v3.py:288-299`). Consequently an arbitrary absolute path
with media type `application/octet-stream` and no schema is admissible.

I built one real Ed25519-signed P6-T01 PASS receipt, copied the exact bytes into
all twenty-four compiler-shaped P6 test paths, used the complete inherited P6
test/artifact denominators, and pointed one artifact registry entry to the real
`/etc/hosts`. All hashes, sizes, manifest signature, event bindings and event ID
were correct. Both the inherited phase validator and v3 evidence validator
accepted it:

```text
copied_T01_receipt_all_tests_plus_etc_hosts=ACCEPTED
```

This is the precise repeated-file/unrelated-file approval bypass that P5/P6 say
must fail (`prompts/v3/P5_signed_evaluator_evidence.addendum.v3.md:8-14`;
`prompts/v3/P6_provenance_release.addendum.v3.md:9-12`).

Required remediation: compare `receipt.test_id == outer test_id`; require unique
receipt IDs and content hashes across the compiled test set; compile exact
command and assertion-ID denominators per test; bind stdout/stderr hashes to
existing controller-owned sources; add a closed artifact-registry schema and an
immutable P1 output; derive paths from that admitted registry rather than
caller-supplied state; restrict paths to compiled authorized roots and require a
declared media/schema validator for every output class. Re-run the full copied-
receipt and `/etc/hosts` fixture, not only isolated schema checks.

### Critical C2 — Claimed model UID and signed metadata can still manufacture the trust and sandbox boundary

The external-trust checker verifies authority-root existence, owner/mode, key
file hashes and workspace non-overlap. It compares the root UID only to
`trust.model_uid`, however; that value is supplied by the same unsigned trust
document rather than obtained from the actual model process/launcher credential
(`contracts/external_trust.schema.v3.json:3-6`;
`tools/validate_plan_v3.py:160-180`). A directory and keys created by the current
real OS user passed merely by claiming `model_uid = current_uid + 1`:

```text
same_real_uid_claimed_distinct_model_uid=ACCEPTED
```

Thus the same real user can provision the supposed external authority and sign
controller/operator records. The checker also cannot establish that the root
pre-existed P0.

Sandbox verification remains metadata-driven. `validate_engine_entry` treats
execute permission plus four Mach-O/ELF magic bytes as a valid executable and
never loads or invokes the binary (`tools/validate_plan_v3.py:431-443`). The
sandbox profile still permits writable staged input and readable credential-
broker roots under `BROKERED_OUTSIDE_SANDBOX`; v3 checks only existence and
non-symlink status (`tools/validate_plan_v3.py:324-344`). The signed probe receipt
has no compiled expected command digest and its observed assertion digests are
not tied to independently captured executions.

A full signed assurance probe used a fake file beginning with Mach-O magic,
writable `staged_input`, readable `credential_broker`, and a controller-signed
seven-PASS receipt with an arbitrary command digest. It returned:

```text
fake_magic_engine_writable_input_readable_credential=ACCEPTED
```

This can certify a nonexistent containment boundary before model launch.

Required remediation: obtain the model UID from the actual sandboxed child
credential and the controller/authority UIDs from OS process/stat facts outside
the P0 document; require a signed, pre-P0 provisioning record with creation
epoch/nonce and distinct owners; parse pinned public keys as Ed25519 keys. Use an
engine-specific registry runner that loads/executes the exact binary and exact
profile, pins the expected command per probe, captures actual exit/signal and
denial output, and signs only that runner-owned record. Enforce purpose
relations: staged input read-only, controller output unavailable to the model,
and no readable credential root for an outside-broker boundary.

### Critical C3 — Event, manifest, and ledger linkage forms an unconstructible hash cycle

The v3 artifact registry claims coverage of every effective authorized output
(`graph_engineered_subscription_execution.plan.v3.yaml:30-34`). Every base node's
authorized outputs include its phase-ledger file (for P6, the inherited manifest
entry is at `graph_engineered_subscription_execution.plan.v1.yaml:404-409`). The
evidence manifest therefore must include and hash that ledger as an artifact,
and its signed `manifest_id` covers the artifact entry
(`contracts/evidence_manifest.schema.v3.json:4-9`;
`tools/validate_plan_v3.py:183-186,288-302`). The event binds the ledger artifact
hash and its own `event_id` hashes the complete event
(`tools/validate_plan_v3.py:298-304`).

But the ledger bytes are required to contain both that final `admitted_event_id`
and that final `evidence_manifest_id`
(`contracts/phase_ledger.schema.v3.json:4-7`). Therefore:

```text
ledger_hash = H(ledger(event_id, manifest_id))
event_id    = H(event(ledger_hash, ...))
manifest_id = H(manifest(ledger_hash, ...))
```

No acyclic production order exists, and finding a simultaneous SHA-256 fixed
point is not an executable protocol. The self-test validates receipts and
SQLite independently but never constructs a complete event + manifest + ledger
triple. An honest phase cannot satisfy the linkage required for PASS.

Required remediation: define a directed provenance DAG. For example, signed
test/artifact/subtask receipts feed a manifest; the manifest feeds a ledger that
does not contain a future event ID; the manifest and ledger hashes feed the
final admitted event. If a post-admission acknowledgement is needed, write a
separate controller record that references the event but is not itself hashed
by that event or manifest. Add an end-to-end constructor/revalidator test for
every node, especially P6.

### High H1 — Missing external trust cannot use the declared honest pause route

The current frozen package provides no trust instance or declared external
authority location, so external trust is presently unproven. V3 correctly says
P0 must record it as unavailable and may not repair it
(`prompts/v3/P0_trust_and_composite_contract.addendum.v3.md:11-21`). It declares
an absence route of `PAUSED_PREREQUISITE` with failure class
`EXTERNAL_FACT_BLOCK` (`graph_engineered_subscription_execution.plan.v3.yaml:35-40`).

The inherited phase-event contract permits a prerequisite pause only for
`AUTHENTICATION_MISSING`, `SUBSCRIPTION_ENTITLEMENT_UNPROVEN`, or
`PROTECTED_DIRTY_OVERLAP`; its pause-reason enum is equally closed
(`contracts/phase_result.schema.v1.json:23-27,49-50`). The inherited graph has
only those three guards and only P2 auth/entitlement plus P6 protected-overlap
pause edges (`graph_engineered_subscription_execution.plan.v1.yaml:180-182,451-455`).
V3 defines no phase-result override, guard, edge, reason or continuation class
for trust absence. A direct `EXTERNAL_FACT_BLOCK + PAUSED_PREREQUISITE` event
fails schema validation:

```text
external_trust_pause_schema_errors=1
```

Thus the package cannot honestly represent its current pre-P2 trust blocker,
contradicting the P2/P_ALL addenda
(`prompts/v3/P2_signed_execution_evidence.addendum.v3.md:13-20`;
`prompts/v3/P_ALL_graph_orchestrator.addendum.v3.md:14-19`).

Required remediation: add a typed `EXTERNAL_TRUST_UNAVAILABLE` prerequisite
class/reason, phase-result schema mapping, P2 guard and pause edge, continuation
reason, and same-node resume path, or deliberately map trust absence to another
semantically exact new prerequisite class. Add a current-absence end-to-end
route test.

### High H2 — SQLite consumption is durable, but it is not composed with authorization or recoverable activation

The SQLite primitive is a real improvement. It uses `BEGIN IMMEDIATE`, checks
checkpoint hash/generation, inserts three unique IDs, updates generation, and
commits durably; the same stored snapshot rejects a second call
(`tools/validate_plan_v3.py:386-414,521-527`).

It is a separate function from v2's signature/continuation validation. It
accepts only caller-provided strings and never loads or verifies an external
authorization, continuation, command, authorization hash, signer, or current
checkpoint record. There is no composed API or transactionally staged validated
authorization token. Calling it with wholly invented unsigned IDs returned:

```text
unsigned_unresolved_ids_atomic_consume=ACCEPTED
```

Moreover, the database contains only consumed rows and generation. It has no
durable pending-activation/outbox state. A crash after COMMIT but before node
activation can therefore leave the capability permanently consumed with zero
activation, while replay is rejected. The P3 addendum requires authorization,
consumption and activation ordering as one crash-safe behavior
(`prompts/v3/P3_atomic_resume_store.addendum.v3.md:3-18`).

Required remediation: expose one controller transaction that takes canonical
continuation/command/authorization records, verifies the pinned signature and
all bindings, stores their hashes, performs the CAS/unique inserts, and writes a
durable pending-activation/outbox record in the same commit. Recovery must
complete exactly one pending activation without re-consuming. Test unsigned
IDs, validation/commit TOCTOU, two processes, crash after commit/before
activation, and cold recovery.

### High H3 — Signed ledgers allow every subtask to reuse one output and do not validate idempotency keys

The exact compiler-owned subtask sets, receipt signatures, source existence,
source hashes, event ID and manifest ID are now checked
(`tools/validate_plan_v3.py:347-383`). This closes all-zero output claims and the
self-denominated ledger.

The validator's source-path uniqueness set is local to one subtask receipt. It
is reset for every receipt, so all required subtasks may cite the same output
file. There is no compiled per-subtask input/output artifact contract, no global
source ownership check across ledger receipts, and no check that
`idempotency_key` equals the compiled phase/subtask/input formula. A direct P6
ledger used all eleven correctly signed receipts and exact IDs, but every receipt
cited one identical output file and every idempotency key was merely twenty
`x` characters:

```text
all_subtasks_reuse_one_output=ACCEPTED
```

This does not prove eleven committed operations or phase-level exactly-once
behavior and contradicts the P5/P6 ledger tests
(`prompts/v3/P5_signed_evaluator_evidence.addendum.v3.md:11-14`;
`prompts/v3/P6_provenance_release.addendum.v3.md:11-14`).

Required remediation: compile exact input and output artifact IDs/path templates
per subtask; enforce global output ownership and allowed sharing explicitly;
recompute the phase key and every idempotency key; bind receipt output IDs to the
artifact registry; and reject same-path/same-hash reuse across unrelated
subtasks.

## Subscription, current prerequisites, and identity

No separate Critical/High defect was found in the included-subscription-only
typing or Codex identity claim. Current read-only probes remain truthful:

```text
Claude Code 2.1.226
claude auth status -> loggedIn=false, authMethod=none, apiProvider=firstParty

codex-cli 0.147.0
codex login status -> Logged in using ChatGPT
```

The inherited capability schema requires Claude subscription OAuth, an included
seat, separately billed credits disabled and API fallback disabled. Codex
requires ChatGPT login plus proved included plan subtype, ChatGPT credits
disabled and API fallback disabled
(`contracts/baseline_contract.schema.v1.json:15-22,31-33`). Login alone is not
entitlement proof, and the P2 base/v3 addendum correctly prohibit launch on
unproven metering (`prompts/P2_subscription_worker_adapter.prompt.v1.md:30-35,49-62`;
`prompts/v3/P2_signed_execution_evidence.addendum.v3.md:9-20`). This matches
current provider documentation on separately billed Claude usage credits and
ChatGPT credit extensions for Codex
([Claude subscription use](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan),
[Claude usage credits](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans),
[Team/Enterprise metering](https://support.claude.com/en/articles/12005970-manage-usage-credits-for-team-and-seat-based-enterprise-plans),
[official OpenAI pricing](https://learn.chatgpt.com/docs/pricing)).

Codex CLI 0.147.0 still exposes no native executed-model identity field. The
frozen policy honestly records `DRIVER_BOUND_REQUEST`, pinned requested-model
authorization, and null native observation
(`prompts/P2_subscription_worker_adapter.prompt.v1.md:21-26`;
`contracts/identity_assurance_policy.v1.yaml:11-18`).

The current execution should pause before any live model call because external
trust is unproven and Claude is logged out. Claude's
`AUTHENTICATION_MISSING` mapping is schema-valid; the separate external-trust
pause is not, as H1 explains. No live call was attempted.

## Conclusion

V3 materially improves semantic receipt shape, signature verification, strict
legacy registry typing, source hashing, schema-aware artifacts, fixed subtask
denominators and SQLite uniqueness. It remains unapproved because the composed
protocol still admits receipt substitution and unrelated artifacts, can
self-manufacture trust/sandbox assurance, contains a provenance hash cycle, and
does not fully compose pause, resume, or ledger semantics. Under the frozen
review protocol, these findings end in-place repair
(`graph_engineered_subscription_execution.plan.v3.yaml:84-87`).
