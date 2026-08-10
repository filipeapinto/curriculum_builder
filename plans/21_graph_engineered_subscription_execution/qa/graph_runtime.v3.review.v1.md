# Plan 21 v3 graph-formalism and durable-runtime review — round 1

## Verdict

**FAIL — 2 Critical, 6 High, 1 Medium.** The 45-file inherited behavioral
bundle is selected and hashed correctly. Exact v3 prompt/subtask maps, inherited
additional-output maps, output collisions, obvious registry owner/type errors,
signed-document cryptography, executable-file magic checks, and the isolated
SQLite `BEGIN IMMEDIATE` generation CAS all bite.

The complete v3 control plane does not. A signed manifest and receipt set was
accepted for P6 using caller-shrunk one-test/one-artifact contracts and an event
with stale run, node, attempt, digest, and incomplete schema. Separately, the
required event/manifest/ledger/subtask hash links form a cryptographic dependency
cycle, so a correctly linked phase cannot be constructed in normal execution.
The effective graph is still checked as parallel declarations rather than
materialized and digest-bound, same-type registry resolver swaps pass, ledger
receipts can globally reuse one output and idempotency key, distinct model UID is
self-asserted, signed sandbox assurance accepts a non-runnable magic-prefix file
and a stale-run probe receipt, and the real CAS accepts arbitrary IDs without any
signed resume capability validation.

The v3 exit rule permits PASS only with zero unresolved Critical and High
findings (`graph_engineered_subscription_execution.plan.v3.yaml:84-87`).

## Frozen-byte basis

The validator-selected inherited bundle independently recomputed to exactly:

```text
file_count: 45
sha256: 29369fd1cfce2a13aac39a3e5b27ed03b0a016cf500a7deb2828948fb082e755
```

The complete reviewed source set—those 45 inherited files plus the v3
plan/schema/tool/log, all v3 contracts, and all v3 prompt addenda—contained 66
files and had canonical path/hash-record digest:

```text
174e6d729b8197f582e387f2018ff7784d44e767fe11f0f183c70a741d137f84
```

Principal v3 file hashes were:

```text
plan.v3.yaml       abf1ef32d26983e4780ba96a6cb4b25d66da65ead5a24e146f99169bfb54d573
schema.v3.json     db7d9b9403c10d74b3000c4336174d5ff1674a33de2ba6f38106a13cb2512d33
validate_plan_v3.py fd9c3a9f6eff6cabf6edfe89ebe7fb03ca70804277623b2ba5c7d242ac52df8a
plans.v3.log.md    b8614b1789ef7f871b9f618dafd22c94bce372da32e8f02b6c2efbeba01bb8b8
```

## Executed checks and independent probes

Both shipped commands passed:

```text
python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan_v3.py
plan21_v3_bootstrap=PASS

python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan_v3.py --self-test
plan21_v3_bootstrap=PASS
```

I independently enumerated the selected behavioral paths, recomputed every
record hash and the bundle digest, and then imported the frozen validator for
no-write mutations. Temporary files, Ed25519 keys, receipts, and SQLite stores
were confined to operating-system temporary directories. Results:

```text
REJECTED  altered behavioral-bundle hash or count
REJECTED  wrong v3 prompt map or hard-coded subtask map
REJECTED  inherited output collision, P0 additional-output removal, or inherited
          P6 subtask shrink
ACCEPTED  every assurance-rule list replaced by arbitrary strings

REJECTED  registry wrong owner and existing scalar resolver
ACCEPTED  P4 tests resolver swapped to P4 runtime-policy-schema array
ACCEPTED  P5 tests resolver swapped to P4 tests array

ACCEPTED  externally signed P6 manifest/receipt set with caller-declared one-test
          and one-fake-artifact denominators plus an event naming stale run,
          node P0, attempt 999, wrong graph digest, and missing required envelope
          fields

ACCEPTED  exact P3 subtask denominator where every signed subtask receipt reused
          one uncompiled output file and every ledger entry reused the same
          idempotency key

ACCEPTED  authority root owned by the current process uid after merely claiming
          a different model_uid in the unsigned trust record
ACCEPTED  executable-mode file containing only ELF magic plus arbitrary text
ACCEPTED  signed sandbox registry/profile/probe package using that non-runnable
          file and a probe receipt from another run and attempt

SQLite two-connection results: one True, one False
SQLite cold replay after reopen: False
ACCEPTED  first CAS using arbitrary unsigned/unvalidated continuation, command,
          and authorization IDs
```

The two-connection probe used a barrier and two independently opened SQLite
connections against the same generation-1 checkpoint. The cold probe reopened
the store after both returned.

## V2 Critical/High reprobe

| V2 finding | V3 disposition |
|---|---|
| Critical — unrelated bytes can admit PASS | **UNRESOLVED at a new boundary.** Signed semantic receipt shape, fixed test filenames, media parsing, and byte hashes now bite, but admission trusts caller-supplied compiled denominators/subjects/artifact registry and never validates the event envelope. Finding 1. |
| Critical — sandbox proof can be fabricated | **PARTIAL, STILL HIGH.** Registry and probe signatures, existing roots, and basic binary magic are checked. A magic-prefix non-executable file and stale-run signed probe still pass; actual execution is not observed. Finding 7. |
| High — resume is only returned in memory | **CAS PRIMITIVE FIXED, COMPOSITION UNRESOLVED.** Two connections and cold replay yield one winner, but arbitrary IDs are consumed without continuation, command, authorization, signature, or trust validation. Finding 8. |
| High — no applied effective graph | **UNRESOLVED.** Exact mapping constants now bite, but validation returns the unchanged v2 delta and v1 base, not a normalized applied graph/digest. Finding 3. |
| High — registry validates names but not semantics | **PARTIAL, STILL HIGH.** Owner/schema and scalar-vs-array errors fail. Same-type semantic resolver swaps and actual resolved-value validation do not. Finding 4. |
| High — committed ledger output claims unverified | **PARTIAL, STILL HIGH.** Signed receipt files and source hashes are checked, but output ownership/reuse/idempotency remain uncompiled and the complete linkage is cyclic. Findings 2 and 5. |

## Findings

### 1. Critical — Evidence admission does not bind the admitted event or denominators to the effective graph

The v3 receipt schema is a real improvement: it requires deterministic-runner
identity, exit zero, nonempty all-PASS assertions, subject and command digests,
output digests, timestamps, and a signature
(`contracts/test_receipt.schema.v3.json:3-9`). Test receipt files are fixed under
the controller root and validated against a pinned controller public key
(`tools/validate_plan_v3.py:200-210,251-287`). Artifact paths, media types,
schemas, bytes, and reuse within one manifest are also checked
(`tools/validate_plan_v3.py:288-300`).

The admission boundary still trusts the critical compiled inputs:

- The exact test set comes from `current.required_test_ids`, and subject digests
  come from `current.test_subject_digests`; neither is compared with the base
  node or an immutable effective-graph object (`tools/validate_plan_v3.py:200-207,266-269`).
- The artifact denominator, paths, media types, and schemas come entirely from
  caller-supplied `current.artifact_contract_registry`
  (`tools/validate_plan_v3.py:267-271,288-299`). No v3 artifact-registry schema or
  compiled registry artifact exists in the v3 contract list
  (`graph_engineered_subscription_execution.plan.v3.yaml:14-23,30-34`).
- `validate_evidence_manifest()` never invokes the inherited phase-result schema
  or `V1.validate_phase_event`. It compares only `event.test_results`,
  `event.artifact_hashes`, and the recomputed event ID
  (`tools/validate_plan_v3.py:251-304`). Event run, node, attempt, current pinned
  digests, outcome/failure mapping, exact inherited test/artifact sets, and the
  required event envelope are never checked.
- `command_digest`, `stdout_sha256`, and `stderr_sha256` are signed fields, but
  admission does not compare the command to a compiled command descriptor or
  recompute stdout/stderr source bytes.

The independent counterexample created a valid Ed25519-signed P6-T01 receipt and
manifest at the expected controller paths, with correct bytes, sizes, semantic
schema, signature, subject, artifact media, manifest ID, and event ID. The
caller supplied only P6-T01 and one fake Markdown artifact as the “compiled”
registries. The event itself named `stale-run`, node P0, attempt 999, a wrong
graph digest, and omitted most mandatory phase-result fields. Admission returned
success.

This can select a phase edge without proving the frozen P6 24-test/five-output
contract or current event bindings. It directly contradicts the compiled-source
and effective-graph invariants
(`graph_engineered_subscription_execution.plan.v3.yaml:41-46,72-75,79,82`) and
is Critical.

**Required remediation.** Produce one immutable effective-node object containing
exact test IDs, signed runner command descriptors, subject digests, artifact
contracts, state bindings, and its graph digest. A single controller admission
function must first validate the complete inherited phase event against that
node/current checkpoint, then validate v3 evidence. Remove denominator and
registry authority from arbitrary `current` maps. Bind and recompute command,
stdout, and stderr sources. Add the accepted stale-event, one-test P6, fake
artifact-registry, wrong-command, and incomplete-envelope mutations.

### 2. Critical — Event, manifest, ledger, and subtask receipts form an unconstructable hash cycle

V3 requires the artifact registry to cover every effective node authorized
output (`graph_engineered_subscription_execution.plan.v3.yaml:30-34`). Every
base node authorizes its phase-ledger file as an output (representative P6 at
`graph_engineered_subscription_execution.plan.v1.yaml:397-409`). Therefore the
evidence manifest must include the ledger path and hash.

At the same time:

- the signed manifest ID hashes its payload, including every artifact source and
  thus the ledger hash (`contracts/evidence_manifest.schema.v3.json:4-9`;
  `tools/validate_plan_v3.py:183-197,288-302`);
- the ledger contains both `admitted_event_id` and `evidence_manifest_id`, plus
  every subtask-receipt hash (`contracts/phase_ledger.schema.v3.json:4-7`);
- every subtask receipt itself contains both IDs
  (`contracts/subtask_receipt.schema.v3.json:4-5`); and
- the event ID hashes the complete event, whose artifact hashes include the
  ledger hash (`contracts/phase_result.schema.v1.json:6-29`;
  `tools/validate_plan_v3.py:303-304`).

The required dependency is therefore:

```text
E = H(event including L)
M = H(manifest including L)
R_i = H(subtask receipt including E and M)
L = H(ledger including E, M, and every R_i)
```

No provisional-ID, detached-link, two-phase-finalization, or cycle-breaking
canonicalization rule exists. Constructing valid bytes requires solving coupled
SHA-256 fixed points, which is computationally infeasible. The validators can
check arbitrarily supplied IDs in isolation, but no normal writer can order the
writes and derive the required final hashes. This violates graph executability
and makes PASS impossible for every phase, including P0.

**Required remediation.** Define an acyclic provenance order. For example,
subtask receipts may bind pre-event phase/input IDs; the ledger may hash those
receipts; the manifest may hash the finalized ledger and artifacts; and the
event may finally hash/bind the manifest ID. Do not put a later object's ID into
an earlier object whose hash the later object includes. Add a constructive
end-to-end fixture that generates all bytes from scratch in declared order and
then validates them, rather than seeding arbitrary IDs.

### 3. High — Exact overlay constants are checked, but no effective graph is applied or emitted

V3 correctly hard-codes expected prompt and subtask maps and inherited v2
additional outputs (`tools/validate_plan_v3.py:47-62`). Independent mutations of
the prompt map, subtask map, output collision, output removal, and inherited
subtask set were rejected. The P0 state override and the other override records
are also compared with exact dictionaries
(`tools/validate_plan_v3.py:125-157`).

That function returns no effective graph. `validate()` validates v2/base,
validates v3 declarations, calls `validate_effective_overlays`, and returns the
unchanged `v2_delta, base` tuple (`tools/validate_plan_v3.py:446-461`). It never
applies the P0 state schema, prompt addenda, controller evidence ports, artifact
registry, trust prerequisite, or resume store to a normalized graph and never
re-runs v1 validation on an applied result.

The unchanged base still declares `P0_contract_bundle` under the v1 schema and
P4 still lists `baseline_contract.schema.v1.json` rather than the required
composite v3 input (`graph_engineered_subscription_execution.plan.v1.yaml:93-100,336-350`).
There is also no v3 runtime-state schema capable of typing the numerous
`current` fields used by evidence, ledger, trust, and resume. The only inherited
runtime schema is closed and lacks those fields
(`contracts/runtime_state.schema.v1.json:4-28`).

Finally, every `assurance_rules` list can be replaced with arbitrary strings and
full `validate()` still passes because the v3 schema only requires generic rule
strings and the tool does not compare them with compiled authority
(`graph_engineered_subscription_execution.schema.v3.json:14,19`).

**Required remediation.** Materialize and serialize a closed effective IR after
all overlays, attach every v3 contract/prompt/state/output port, validate it with
the inherited graph invariants, and compute a graph digest consumed by every
runtime helper. Add a v3 runtime-state schema and typed artifact-registry schema.
Return the immutable effective graph—not the unchanged base—from bootstrap.

### 4. High — Registry checking still permits semantically wrong same-type resolvers

The strict registry function now fixes expected owners and source schemas and
rejects scalar-vs-array mismatches
(`tools/validate_plan_v3.py:98-122`). Wrong-owner and scalar `goal`/`version`
mutations were independently rejected.

It does not bind each contract key to its exact expected resolver or validate an
actual resolved value. Any nonempty array subschema in the expected source
schema satisfies the check. The independent mutations therefore accepted:

- `contract://P0/authorized_paths/P4/tests` resolving to
  `authorized_paths.P4.runtime_policy_schema`; and
- `contract://P0/authorized_paths/P5/tests` resolving across scope to
  `authorized_paths.P4.tests`.

Both can send schema/policy paths to a test-output contract while retaining the
right JSON type. This violates exact artifact ownership and path resolution.

**Required remediation.** Hard-code or compile the exact key/owner/schema/resolver
map, resolve the actual P0/PLAN value, validate its element schema and canonical
path scope, and compare it with the consuming port's media/schema contract. Add
same-type, cross-node, cross-purpose, empty-value, and wrong-cardinality
mutations.

### 5. High — Signed subtask receipts are not globally output- or idempotency-bound

Ledger validation now requires the exact hard-coded node denominator, fixed
per-subtask receipt filenames, correct receipt bytes, current event/manifest IDs,
input digests, and valid signatures (`tools/validate_plan_v3.py:347-383`). This
fixes self-denominated and simple fabricated-hash ledgers in isolation.

The output-source validator scopes its `seen` set to one receipt and checks only
path bytes (`tools/validate_plan_v3.py:347-359`). It does not compare artifact IDs,
paths, hashes, media, or schema with the compiled artifact registry/evidence
manifest, and it does not prevent one source from being claimed by every
subtask. Ledger `idempotency_key` is only a free string of length 20 in the
schema; the function neither recomputes it nor requires uniqueness
(`contracts/phase_ledger.schema.v3.json:6-7`).

The independent exact-denominator P3 ledger passed with all five signed receipts
claiming the same uncompiled output file and all five entries using the same
idempotency key. That permits key collision and replay-skipping despite correct
local signatures.

**Required remediation.** Compile per-subtask input/output descriptors and key
templates into the effective node. Enforce exact artifact ownership, global
source/path uniqueness where required, media/schema validation, manifest/hash
agreement, and domain-separated unique idempotency keys. Resolve the cyclic
linkage in Finding 2 before testing the final ledger.

### 6. High — Distinct external model UID is a self-asserted fact

External trust correctly verifies an existing non-symlink authority directory,
its actual owner uid, non-group/world-writable modes, in-root public key bytes,
and path separation from supplied model roots
(`tools/validate_plan_v3.py:160-180`). A record whose declared authority and
model UIDs are equal fails.

The model uid itself comes only from the unsigned trust document. It is never
compared with the actual worker process uid, sandbox launcher identity, or a
signed OS identity record. Evidence admission separately trusts another
`current.model_uid` and never proves it equals `trust.model_uid`
(`tools/validate_plan_v3.py:251-258`).

The independent probe created the authority root and keys under the current
process uid, then merely declared an unused numeric model uid. Trust validation
succeeded. The validator cannot distinguish that fixture from a real
distinct-identity deployment. In the repository's normal same-user CLI model,
this allows the model/controller boundary to claim separation without proving
it.

**Required remediation.** Bind model execution uid from the actual launcher or
OS credential evidence, bind controller service uid and authority uid in one
externally signed trust record, and compare all three with file/process stats at
admission. The trust record itself needs external authenticity and immutable P0
binding; it cannot supply the fact used to validate itself.

### 7. High — Sandbox assurance accepts a non-runnable magic-prefix file and stale probe provenance

The engine registry is schema-checked and signature-verified, selected engines
must be unique, root paths must exist, and the signed probe receipt must contain
the exact seven assertion IDs (`tools/validate_plan_v3.py:307-345`). Plain-text
engine files no longer pass.

Two executable counterexamples remain:

- `validate_engine_entry()` treats any executable-mode bytes beginning with ELF
  or Mach-O magic as a recognized executable; it does not parse headers, inspect
  architecture/code signature, invoke a version/probe command, or execute the
  sandbox (`tools/validate_plan_v3.py:431-443`). A short file containing ELF
  magic plus arbitrary text passed even though the OS cannot execute it.
- `validate_sandbox_assurance()` constructs `probe_current` by replacing the
  actual current run and attempt with values read from the receipt itself
  (`tools/validate_plan_v3.py:336-340`). A correctly signed receipt from
  `stale-run-999`, attempt 99 therefore passed against current
  `run-current-1`, attempt 1.

The full independently signed engine registry, profile, and seven-assertion
probe package using both defects passed. No function executes the engine or
escape probes; a signature authenticates the claims but does not establish the
claimed command ran.

**Required remediation.** Parse and identify the complete allowlisted binary,
verify platform/code-signature/version policy, and execute a controller-owned
health command. Run all seven probes through that exact binary/profile and
derive signed receipts from observed process results. Preserve the caller's
current run/node/attempt and reject any receipt mismatch; never populate current
bindings from the receipt being checked.

### 8. High — The real SQLite CAS is not composed with signed resume admission

The isolated store is genuine. `initialize_resume_store()` creates durable state
and unique continuation, command, and authorization columns. The consumer uses
`BEGIN IMMEDIATE`, reads expected checkpoint/generation, inserts unique IDs,
performs a guarded generation update, and commits
(`tools/validate_plan_v3.py:386-414`). Two independent connections sharing
generation 1 produced exactly one success; a fresh connection after completion
rejected replay.

The transaction accepts only six raw strings and does not receive or validate a
continuation, resume command, signed authorization, external trust, active node,
or authorization time. There is no v3 wrapper composing inherited
`V2.validate_resume_once()` with the transaction, and no call site outside the
self-test. A fresh store accepted arbitrary `a…`, `b…`, and `c…` IDs as a valid
consumption.

Thus the durable primitive gives uniqueness to unproven capabilities. The
overlay promises `external_signed_authorization` and activation only after a
valid committed consumption (`graph_engineered_subscription_execution.plan.v3.yaml:47-53,76,81`),
but executable code proves only the latter half.

**Required remediation.** Expose one fail-closed resume-admission transaction
that verifies continuation and command schemas/current bindings, exact external
authorization bytes and signature against P0 trust, expiry/nonce, active
continuation, checkpoint and generation inside the same transaction, then
inserts hashes/IDs and commits before emitting an activation record. Test forged,
expired, cross-run/phase, stale-checkpoint, changed-command, two-connection, and
cold-process cases through that single public entry point.

### 9. Medium — Inherited denominator source integrity remains relationally unchecked

The 45-file bundle intentionally inherits the v1 coverage denominator and
validator. Its helper still checks category-local ID uniqueness and aggregate
lengths only (`tools/validate_plan.py:94-101`). It does not recompute the source
digest, bind record source hashes, or define cross-category identity scope. V3
does not override that contract. This remains Medium and does not change the
failed verdict.

## Confirmed working controls

Independent probes confirmed the following on the frozen bytes:

- the fixed selection returns the listed 45 inherited files and exact recorded
  digest; altered count/hash fails;
- v3 prompt/subtask maps and v2 inherited output maps are exact; wrong maps,
  collisions, output removal, and subtask shrink fail;
- obvious registry owner/schema and scalar-vs-array errors fail;
- signed semantic receipt shape rejects explicit FAIL and nonzero exit;
- fixed test receipt filenames, local byte/size hashes, artifact JSON/YAML/Markdown
  parsing, declared JSON Schema validation, and same-manifest direct path reuse
  checks bite when the compiled inputs are held constant;
- same-declared-UID trust and plaintext engines fail;
- signed-document ID and Ed25519 signature verification are real; and
- SQLite `BEGIN IMMEDIATE` with two connections and cold reopen provides exactly
  one generation-CAS winner.

These controls are meaningful but insufficient to offset the accepted
counterexamples and unconstructable provenance graph.

## Exit decision

**FAIL.** The current frozen Plan 21 v3 remains unapproved. Per its review
protocol, this review reports the defects without editing the target version
(`graph_engineered_subscription_execution.plan.v3.yaml:84-87`).
