# Plan 21 prompt/subscription/security QA — round 3 targeted closure

**Verdict: FAILED_TARGETED_CLOSURE**

**Disposition:** 2 Critical and 3 High findings remain unresolved. H2 and H5
are closed; C1, C2, H1, H3, and H4 are not. Per the frozen-byte targeted
closure rule (`graph_engineered_subscription_execution.plan.v1.yaml:499-508`),
this package remains unapproved and requires a new version.

## Frozen-byte verification

The two documented bootstrap commands still pass:

```text
python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py
plan21_bootstrap=PASS

python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py --self-test
plan21_bootstrap=PASS
```

Current local authentication probes remain:

```text
claude auth status
{"loggedIn":false,"authMethod":"none","apiProvider":"firstParty"}

codex login status
Logged in using ChatGPT
```

No live model call was attempted: the frozen P2 rules require the current
Claude state to pause before launch.

## Targeted dispositions

### Critical C1 — UNRESOLVED: success is run-bound but not evidence-byte-bound

The revision closes the empty-denominator and stale run/policy/schema/route
forms of the original bypass. The event schema now requires nonempty evidence
and artifact containers and conditions `PASS` on PASS-shaped records
(`contracts/phase_result.schema.v1.json:6-38,40-47`). The executable helper also
checks the event against current bindings and the node's exact test and artifact
sets (`tools/validate_plan.py:48-70`).

It still never resolves an evidence hash, recomputes an artifact hash from
bytes, verifies an artifact path, recomputes `event_id`, or binds an actual
phase-ledger hash. A direct probe supplied every P6 test and authorized-output
key with an all-zero hash, while the declared P6 result and supersession files
did not exist. `validate_phase_event` returned:

```text
fabricated_nonexistent_P6_evidence=ACCEPTED
```

The shipped self-test positively relies on the same defect: it calls an all-zero
hash fixture a valid P6 PASS and admits it (`tools/validate_plan.py:537-553`).
`artifact_hash_recompute` is only a declared controller check
(`graph_engineered_subscription_execution.plan.v1.yaml:31-43`); no current
executable code performs it. This remains an approval-path acceptance bypass.

Required remediation: implement controller admission over an immutable
artifact/evidence manifest: resolve each authorized output to canonical bytes,
recompute every hash and receipt, verify evidence objects rather than non-null
hash strings, recompute the event identity, require the externally fixed phase
ledger denominator and committed ledger hash, and add a negative test proving
the all-zero/nonexistent P6 fixture is rejected.

### Critical C2 — UNRESOLVED: resume origin binding exists, but authorization and single-use ownership do not

The continuation now binds run, suspended/allowed node, source event,
checkpoint, all pinned digests, reason, and next attempt
(`contracts/continuation.schema.v1.json:4-10`), and the command binds the
continuation hash, same node, and next attempt
(`contracts/resume_command.schema.v1.json:4-6`). `validate_resume` rejects
cross-run, cross-phase, stale-source, and unbound commands
(`tools/validate_plan.py:73-91`). Those are real improvements.

However, `operator_authorization_hash` is an unconstrained opaque hash with no
authorization artifact/schema, actor, signature, or resolver. More decisively,
`validate_resume` neither reads nor atomically updates the declared
`consumed_continuation_ids` state
(`graph_engineered_subscription_execution.plan.v1.yaml:53-76`). The continuation
schema permanently requires `consumed: false`, and the self-test exercises no
replay (`contracts/continuation.schema.v1.json:9-10`;
`tools/validate_plan.py:609-642`). Calling the current validator twice with the
exact same continuation and command produced:

```text
identical_resume_1=ACCEPTED
identical_resume_2=ACCEPTED
```

This contradicts the claimed single-use controller route and leaves resume
authorization self-assertable/replayable.

Required remediation: define an immutable operator-authorization record with
identity, scope, source-event/continuation hash, expiry or nonce, and verifier;
make the controller validate it and atomically compare-and-set the continuation
ID into runtime state's consumed set before emitting RESUME; reject duplicate
command IDs and already-consumed continuations; add same-process and cold-process
double-resume mutations.

### High H1 — UNRESOLVED: state/P6 coverage is fixed, but contract registry entries are not actually resolved

P6 now explicitly receives immutable P0–P5 state bundles plus the historical
source contract, with matching predecessor context and state reads
(`graph_engineered_subscription_execution.plan.v1.yaml:397-414`). P4–P6 use a
nonempty typed artifact bundle (`contracts/artifact_bundle.schema.v1.json:4-8`),
and state references are checked for writer, ancestry, context, and declared
read access (`tools/validate_plan.py:293-302`). This closes the missing P6
evidence-input portion of H1.

The remaining `contract://` selectors are only name-registered. A registry
entry's `resolver` and `schema_ref` are arbitrary nonempty strings
(`graph_engineered_subscription_execution.schema.v1.json:135-137`), and the
validator treats membership in the registry as complete resolution without
checking the resolver, owner/value type, schema existence, or resolved digest
(`tools/validate_plan.py:303-306`). A direct mutation changed the P4 tests
selector to `resolver: does.not.exist` and
`schema_ref: contracts/does-not-exist.schema.json`; full validation returned:

```text
unresolvable_registered_contract=ACCEPTED
```

Required remediation: make each registry entry point to a typed state producer
and a machine-resolvable JSON Pointer (or equivalent); verify the referenced
schema file exists, the pointer exists in that schema and runtime P0 value, the
resolved value has the required path-list type, and its canonical resolved
value/digest is included in the execution contract. Add missing-resolver,
missing-schema, wrong-owner, wrong-type, and post-freeze-value mutations.

### High H2 — CLOSED: included-subscription-only metering now fails closed

The baseline contract now distinguishes Claude subscription OAuth and seat
subtypes from Console/API/usage-based Enterprise, and requires included-only
Claude to have separately billed credits and API fallback disabled. It applies
the analogous ChatGPT-login, plan-subtype, ChatGPT-credit, and API-fallback
constraints to Codex (`contracts/baseline_contract.schema.v1.json:15-22,31-33`).
The provider override set is closed, and the self-test rejects Claude credits,
Codex credits, API override, and a usage-based seat
(`tools/validate_plan.py:576-607`). P2-T03/T04 explicitly treat login alone,
unprovable metering, credit/overage, API fallback, and usage-based seats as
prelaunch pauses/failures (`prompts/P2_subscription_worker_adapter.prompt.v1.md:30-33`).

That matches current provider documentation: Anthropic documents separately
billed usage credits and usage-based Enterprise, while OpenAI documents that
ChatGPT plans can extend Codex usage using credits
([Claude subscription use](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan),
[Claude usage credits](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans),
[Team/Enterprise metering](https://support.claude.com/en/articles/12005970-manage-usage-credits-for-team-and-seat-based-enterprise-plans),
[OpenAI pricing](https://learn.chatgpt.com/docs/pricing)). Current Codex
`Logged in using ChatGPT` is therefore not sufficient by itself; the frozen
prompt correctly pauses if plan subtype and included-only allocation cannot be
machine-proven. Codex identity remains honestly limited to
`DRIVER_BOUND_REQUEST` with null native observation
(`prompts/P2_subscription_worker_adapter.prompt.v1.md:21-26`;
`contracts/identity_assurance_policy.v1.yaml:11-18`). C1 still prevents trusting
unrecomputed evidence globally, but the specific H2 capability and routing
contract is remediated.

### High H3 — UNRESOLVED: sandbox description is richer but neither reconstructable nor relationally contained

The revised schema adds engine/version, absolute roots and purposes, mount,
symlink, network, and credential-boundary fields, and enforces write implies read
(`contracts/baseline_contract.schema.v1.json:18`). It still stores only
`profile_sha256` and `policy_digest`: there is no authorized sandbox profile
artifact/path or profile bytes among P0 outputs
(`graph_engineered_subscription_execution.plan.v1.yaml:202-209`). Therefore
P2-T07's instruction to reconstruct the frozen profile “from bytes” has no input
from which to do so (`prompts/P2_subscription_worker_adapter.prompt.v1.md:36`).

The schema also applies no purpose-specific relations. A direct full-baseline
probe used `engine: other_verified`, arbitrary hash-only profile metadata, a
writable `staged_input` root, and a readable `credential_broker` root while
claiming `BROKERED_OUTSIDE_SANDBOX`. Draft 2020-12 validation returned:

```text
writable_staged_input_readable_broker_hash_only_profile_errors=0
```

This permits input mutation and in-sandbox credential-broker readability while
asserting the opposite boundary.

Required remediation: freeze the exact canonical sandbox profile bytes as a P0
artifact and bind its recomputed digest; restrict engine variants to a verified
profile schema; enforce `staged_input` read-only, controller/model output
separation, credential-broker roots absent from model-readable roots when the
boundary is outside, canonical nonoverlapping roots, and executable mount,
symlink, and network rules. Add mutations for each contradictory relation.

### High H4 — UNRESOLVED: every phase has a ledger, but each ledger chooses its own denominator

P3–P6 now declare stable phase keys and ledger outputs
(`graph_engineered_subscription_execution.plan.v1.yaml:302-329,336-360,367-390,397-421`).
The ledger records subtask IDs, keys, input/output hashes, states, and completion
(`contracts/phase_ledger.schema.v1.json:4-10`). This closes the absence of a
phase-ledger shape.

But no node manifest or compiled contract declares the immutable required
subtask set. `required_subtask_ids` is supplied by the ledger itself, and
`validate_phase_ledger` compares `subtasks` only to that same self-declared list
(`tools/validate_plan.py:104-123`). A P6 ledger containing one invented committed
subtask named `only`, omitting release tests and evidence commit, returned:

```text
self_denominated_one_task_ledger=ACCEPTED
```

The self-test similarly chooses its own two-item denominator rather than deriving
it from P6 (`tools/validate_plan.py:677-699`). Thus a phase can skip work and
still claim a complete ledger.

Required remediation: declare an exact immutable `required_subtask_ids` set (and
digest) per node in the manifest/compiler output; pass that external denominator
to ledger validation; require exact input/output key sets and recomputed output
hashes; bind the admitted event to the complete ledger hash; add missing, extra,
renamed, reordered, and fabricated-hash subtask mutations for P3–P6.

### High H5 — CLOSED: logged-out Claude maps honestly to a prerequisite pause

The event schema now permits only authentication, entitlement, or protected
overlap classes for `PAUSED_PREREQUISITE` and binds each class to its exact reason
and pause kind (`contracts/phase_result.schema.v1.json:50,56-58`). P2's loop maps
the observed logged-out state to `AUTHENTICATION_MISSING`, unproven included-only
metering to `SUBSCRIPTION_ENTITLEMENT_UNPROVEN`, and controller/runtime defects
to `SYSTEM_FAILURE` (`prompts/P2_subscription_worker_adapter.prompt.v1.md:49-62`).
Direct validation produced:

```text
honest_logged_out_pause=ACCEPTED
factory_defect_as_pause=REJECTED
```

The current `claude auth status` therefore has an honest, schema-valid fail-closed
route and does not need to be mislabeled or worked around.

## Closure result

The revision materially improves binding, P6 inputs, entitlement modeling,
Codex identity honesty, and failure routing. It does not meet the round-three
acceptance rule because executable acceptance still trusts invented hashes,
resume remains replayable and authorization-unverified, registered contracts can
be unresolvable, the sandbox contract accepts contradictory boundaries, and
phase ledgers remain self-denominated.
