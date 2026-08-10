# Plan 21 v2 prompt/subscription/security QA — new-version review 1

**Verdict: CHANGES_REQUIRED**

**Unresolved:** 3 Critical, 3 High. Version 2 cannot be approved under its
zero-Critical/High exit rule.

## Scope and frozen-byte checks

I independently reviewed the digest-bound v1 base, v2 overlay and schema, every
v2 contract, every v1 prompt plus v2 GOAL/TEST/LOOP addendum, and the complete
v2 validator. I did not use another review as evidence.

The base binding is correct: the current v1 manifest hashes to
`171af5dff71d33331f263bf73c84219790209700cd15d403f63ee207805b561e`, exactly
the value pinned by the v2 overlay
(`graph_engineered_subscription_execution.plan.v2.yaml:4-6`). Both shipped
commands pass:

```text
python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan_v2.py
plan21_v2_bootstrap=PASS

python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan_v2.py --self-test
plan21_v2_bootstrap=PASS
```

Those passes do not cover the adversarial cases below.

## Findings

### Critical C1 — Existing bytes that explicitly report failure can admit P6 PASS

The byte-level improvement is real: the controller checks regular-file
existence, root containment, size and SHA-256, exact compiled test/artifact sets,
event hash agreement, and symlink escape (`tools/validate_plan_v2.py:101-157`).
It now rejects a missing file or a digest that disagrees with source bytes.

It never validates what test evidence bytes mean. The evidence schema puts a
manifest-owned constant `status: PASS` beside an opaque nonempty file; the file
has no media type, result schema, test-run identity, command/exit status, or
semantic binding (`contracts/evidence_manifest.schema.v2.json:12-16`). The
validator hashes those bytes but never parses them (`tools/validate_plan_v2.py:125-135`).
Likewise, artifact files are accepted from `current.resolved_artifact_paths`
without this admission function deriving those paths from the compiled output
contract (`tools/validate_plan_v2.py:136-154`).

A direct exact-denominator P6 probe created every required test source with the
literal bytes `{"status":"FAIL","assertions":0}`, labelled each envelope PASS,
and used non-authorized dummy artifact content. All sizes, hashes, bindings, and
event ID were genuine recomputations. The result was:

```text
explicit_FAIL_bytes_as_P6_PASS=ACCEPTED
```

This still permits fabricated success, now by truthfully hashing false evidence.
It directly violates P6's requirement that failing evidence cannot admit PASS
(`prompts/v2/P6_end_to_end_release_and_supersession.addendum.v2.md:9-12`).

Required remediation: define and validate a closed, test-runner-owned evidence
record per test with command/fixture identity, exit status, assertions/check IDs,
result, stdout/stderr or receipt hashes, and current bindings; require the
controller to derive artifact source paths from the compiled contract rather
than accept them in caller-supplied current state. Add a negative fixture whose
correctly hashed source record says FAIL and prove P6 admission rejects it.

### Critical C2 — Signed resume is verified, but consumption is neither atomic nor durable

The external authorization record is materially improved. It binds the exact
continuation, run, node, next attempt, nonce, validity interval, signer and
Ed25519 signature (`contracts/resume_authorization.schema.v2.json:3-7`). The
validator checks canonical external bytes, root separation/mode, pinned public
key bytes, signature, time, and current consumed sets
(`tools/validate_plan_v2.py:171-222`). Forged signatures fail.

The claimed atomic transition is not implemented. `validate_resume_once`
copies a caller-provided dictionary, appends IDs in memory, increments an
in-memory generation, and returns it; it does not open a durable checkpoint,
compare-and-swap any stored generation/hash, commit consumption, fsync, or make
activation contingent on that commit (`tools/validate_plan_v2.py:221-227`). Its
self-test only passes the returned dictionary to a second call in the same
process (`tools/validate_plan_v2.py:455-461`), despite the P3/P6 addenda requiring
same-process and cold-process replay rejection and crash-boundary behavior
(`prompts/v2/P3_durable_graph_runtime.addendum.v2.md:9-14`;
`prompts/v2/P6_end_to_end_release_and_supersession.addendum.v2.md:13-14`).

Using one valid real Ed25519 authorization and invoking the function twice from
the same original persisted-state snapshot produced:

```text
resume_from_same_persisted_snapshot_1=ACCEPTED
resume_from_same_persisted_snapshot_2=ACCEPTED
```

A restarted process will receive that same unmodified snapshot and accept the
same capability again. This contradicts the overlay's declared atomic
compare-and-swap transition (`graph_engineered_subscription_execution.plan.v2.yaml:27-32`).

Required remediation: implement a real durable transaction against the runtime
checkpoint store: lock or transactional CAS on current checkpoint hash and
generation, atomically append both continuation and command IDs, durably commit,
then and only then return an activation token. Exercise two competing processes
and crash-before/after-commit subprocesses; both the loser and every cold replay
must fail from persisted state, not from a returned Python object.

### Critical C3 — Sandbox admission accepts a fake engine, invented denial logs, and contradictory roots

The assurance schema now names profile, engine, root-evidence and probe sources,
and the validator checks their bytes, owner/mode and hashes
(`contracts/baseline_assurance_addendum.schema.v2.json:4-9`;
`tools/validate_plan_v2.py:230-276`). But no engine is ever executed. The
“profile” is a JSON metadata document, not an engine-specific executable policy;
no code passes it to `sandbox-exec`, a container runtime, or a VM. Probe evidence
is any file whose bytes match a manifest-provided hash. The validator trusts the
root document's `status: DENIED` and never parses a runner receipt, command,
exit status, attempted path, engine/profile identity, or observed denial
(`contracts/sandbox_root_evidence.schema.v2.json:4-9`;
`tools/validate_plan_v2.py:249-276`).

Purpose relations remain unenforced. `sandbox_profile.schema.v2.json` still
permits writable staged input and readable credential-broker roots while
claiming `BROKERED_OUTSIDE_SANDBOX` (`contracts/sandbox_profile.schema.v2.json:4-10`).
The shipped positive fixture itself uses a plain-text “engine” file and creates
DENIED JSON files directly without launching that file
(`tools/validate_plan_v2.py:395-420`).

A direct probe used a mode-0500 plain-text file as `other_verified`, writable
`staged_input`, readable `credential_broker`, an invalid public-key file, and
seven files containing only `invented denial claim`. Admission returned:

```text
fake_engine_fake_probes_contradictory_roots=ACCEPTED
```

This is not structural containment and can falsely certify credential and
repository isolation before a live model launch.

Required remediation: use an engine-discriminated executable profile contract;
validate/compile the actual engine policy; launch the pinned engine bytes for
every escape probe; record a closed runner receipt containing argv/profile/
engine hashes, attempted resource, exit/signal and observed denial; independently
derive canonical roots; and enforce purpose relations (`staged_input` read-only,
model output separated from controller output, and no readable credential root
under an outside-broker boundary). Reject unknown engines unless a versioned
runner implementation is compiled and tested.

### High H1 — Registry schema presence is checked, but owner and resolved-value typing are not

The revision now rejects unused entries, absent schema files, meta-invalid
schemas, and nonexistent dotted properties (`tools/validate_plan_v2.py:76-90`).
The frozen current entries therefore have syntactically resolvable schema paths.

It does not check registry `owner`, producer precedence, the actual P0 runtime
value, or whether the resolver's property schema/value has the contract's
required type. This is narrower than the v1 defect but contradicts both the
overlay rule and P1 addendum
(`graph_engineered_subscription_execution.plan.v2.yaml:33-34`;
`prompts/v2/P1_graph_ir_and_static_compiler.addendum.v2.md:9-14`). A direct
mutation changed the P4-tests entry to owner `PLAN` and resolver `version`—an
existing property of the wrong type. `validate_registry` returned:

```text
wrong_owner_wrong_type_registry=ACCEPTED
```

Required remediation: bind each entry to one typed producer port; verify owner
and topological precedence; resolve against the actual digest-bound owner value;
validate the resolved value against the property's subschema; normalize concrete
paths and bind their digest. Add wrong-owner, wrong-type, absent-runtime-value,
future-owner, and post-freeze mutation tests.

### High H2 — Ledger denominator is fixed, but committed outputs and event linkage remain self-asserted

Every node now has an overlay-owned required subtask set
(`graph_engineered_subscription_execution.plan.v2.yaml:37-65`), and
`validate_phase_ledger_v2` correctly compares the ledger against that external
set (`tools/validate_plan_v2.py:165-168`). The prior one-subtask denominator
bypass is closed.

The validator still does not resolve or recompute any subtask `input_digest` or
`output_hashes`, verify that outputs exist, bind ledger completion to the phase
event, or atomically order side-effect commit before ledger commit. The v2
ledger schema merely references the v1 shape
(`contracts/phase_ledger.schema.v2.json:1-5`). A P6 ledger with the complete
eleven-ID denominator, every task marked COMMITTED, and every output set to an
all-zero fabricated hash returned:

```text
exact_denominator_zero_hash_ledger=ACCEPTED
```

That violates P6's requirement that committed outputs exist and hash correctly
(`prompts/v2/P6_end_to_end_release_and_supersession.addendum.v2.md:11-12`) and
does not establish phase-level idempotency.

Required remediation: give each compiled subtask an exact input and output
contract; recompute all referenced bytes/receipts; require a controller-authored
commit record after its side effect; bind the exact complete ledger hash into
the phase event; and run subprocess crash tests before/after every P3–P6 commit.

### High H3 — P0 is instructed to repair assurance source files it is not authorized to create

P0's addendum requires actual profile, engine, root-evidence and public-key files
before P1, treats missing files as failure, and tells P0 to repair the inventory
or its source files (`prompts/v2/P0_contract_and_evidence_freeze.addendum.v2.md:8-22`).
The current package contains no sandbox profile, root-evidence instance,
operator public key, or assurance-addendum instance. `/usr/bin/sandbox-exec`
exists, but there is no executable profile or external authority material.

The digest-bound P0 base permits only repository read access and its original
declared outputs (`graph_engineered_subscription_execution.plan.v1.yaml:197-209`).
The v2 overlay adds only
`results/P0.assurance_addendum.v2.yaml`—not the profile, root-evidence, public
key, or authority root—as a P0 output
(`graph_engineered_subscription_execution.plan.v2.yaml:37-41`). Thus “repair its
source files” would either exceed P0's write scope or require an undeclared
external provisioning step. There is no typed pre-P0 operator-provisioning
input/command and no prerequisite-pause route for its absence.

Required remediation: either declare immutable pre-P0 operator-provisioned
paths, ownership, creation procedure and prerequisite-pause semantics, or assign
workspace profile/root-evidence generation to one explicit node with exact
outputs while keeping the private operator authority external. Make P0 inventory
only inputs it is authorized to read and never instruct it to repair external
authority bytes.

## Subscription, CLI and identity disposition

No additional Critical/High finding remains in the included-subscription-only
typing or driver identity policy. Current read-only facts are:

```text
Claude Code 2.1.226
claude auth status -> loggedIn=false, authMethod=none, apiProvider=firstParty

codex-cli 0.147.0
codex login status -> Logged in using ChatGPT
```

The installed Claude CLI exposes the planned `-p`, `--safe-mode`,
`--no-session-persistence`, `--tools`, `--output-format`, and `--json-schema`
primitives. Codex exposes `exec`, `-m`, `--ephemeral`, `--ignore-user-config`,
`--output-schema`, `--json`, `-C`, and `-s`; its output contract still exposes no
native executed-model field. The frozen base therefore remains honest in
recording Codex as `DRIVER_BOUND_REQUEST` with a null native observation
(`prompts/P2_subscription_worker_adapter.prompt.v1.md:21-26`;
`contracts/identity_assurance_policy.v1.yaml:11-18`).

The capability schema requires Claude subscription OAuth, an included seat,
credits disabled and no API fallback; it separately requires ChatGPT login,
included plan subtype, ChatGPT credits disabled and no API fallback for Codex
(`contracts/baseline_contract.schema.v1.json:15-22,31-33`). P2 explicitly treats
login alone or unprovable metering as non-launching
(`prompts/P2_subscription_worker_adapter.prompt.v1.md:30-33`;
`prompts/v2/P2_subscription_worker_adapter.addendum.v2.md:9-15`). This matches
current official provider guidance that Claude extra usage and some enterprise
usage are separately billed, and that Codex usage on ChatGPT plans can be
extended with credits
([Claude subscription use](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan),
[Claude usage credits](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans),
[Team/Enterprise metering](https://support.claude.com/en/articles/12005970-manage-usage-credits-for-team-and-seat-based-enterprise-plans),
[official OpenAI pricing](https://learn.chatgpt.com/docs/pricing)).

Accordingly, the current truthful execution outcome is a P2
`AUTHENTICATION_MISSING` prerequisite pause for Claude. ChatGPT login alone must
not be promoted into Codex included-only entitlement; absent additional
machine-verifiable plan/credit evidence, Codex must likewise remain
`SUBSCRIPTION_ENTITLEMENT_UNPROVEN`. No live model call was attempted.

## Conclusion

The v2 overlay is substantially stronger than its base in byte hashing,
signature verification, denominator ownership and entitlement modeling. It is
not yet executable at its claimed security boundary: correctly hashed failure
bytes can approve P6, resume consumption is not persisted atomically, sandbox
probes are never executed, and registry/ledger/P0-source contracts retain High
gaps. A version 3 is required by the overlay's own iteration rule
(`graph_engineered_subscription_execution.plan.v2.yaml:78-82`).
