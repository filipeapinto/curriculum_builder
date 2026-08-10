# Plan 21 prompt/subscription/security QA — round 3

**Verdict: FAIL**

**Unresolved:** 2 Critical, 5 High, 1 Medium. Under the review protocol, this
package cannot be approved.

## Scope and verification

I independently reviewed the exact current Plan 21 manifest, sibling schema,
bootstrap validator, contract schemas and policy, and P0–P6/P_ALL prompts from
the prompt-executability, subscription-only, identity, containment, replay, and
evaluator-independence perspectives. Findings below are based on those source
artifacts, direct schema probes, current local CLI facts, and current official
provider documentation; no other review is cited or used as evidence.

The documented commands both pass:

```text
python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py
plan21_bootstrap=PASS

python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py --self-test
plan21_bootstrap=PASS
```

Current read-only capability probes are truthful and unchanged:

```text
claude --version
2.1.226 (Claude Code)

claude auth status
{"loggedIn":false,"authMethod":"none","apiProvider":"firstParty"}

codex --version
codex-cli 0.147.0

codex login status
Logged in using ChatGPT
```

Local help also confirms the planned primitive flags exist: Claude has
`--safe-mode`, `-p`, `--no-session-persistence`, `--tools`, `--output-format`,
and `--json-schema`; Codex has `exec`, `-m`, `--ephemeral`,
`--ignore-user-config`, `--output-schema`, `--json`, `-C`, and `-s`. Codex help
does not expose a native executed-model identity field. The Plan 21 choice to
record Codex as `DRIVER_BOUND_REQUEST` with a pinned requested model and null
native observation is therefore honest
(`prompts/P2_subscription_worker_adapter.prompt.v1.md:19-24`,
`contracts/identity_assurance_policy.v1.yaml:9-14`). The one-adapter design and
the evaluator context/cross-family tests are plausible. Those strengths do not
close the failures below.

## Findings

### Critical — C1: A schema-valid, evidence-free phase event can select every success edge, including plan approval

**Evidence.** The routing schema requires the names `test_results` and
`artifact_hashes`, but permits `test_results: []` and `artifact_hashes: {}`. It
does not condition `PASS` on every declared test passing, exact declared-output
hash coverage, or equality of `run_id`, attempt, and
`execution_contract_digest` to current controller state
(`contracts/phase_result.schema.v1.json:5-35`). Every success guard tests only
constant `node_id` plus `outcome: PASS`
(`graph_engineered_subscription_execution.plan.v1.yaml:111-117`), and those
guards directly advance P0 through P6 and finally select `PLAN_APPROVED`
(`graph_engineered_subscription_execution.plan.v1.yaml:353-360`). P_ALL calls
the registered guard predicates the edge selector, so its prose-only digest
check is not an executable guard (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:17-23,32-38`).

I instantiated a P6 event with a made-up run id, `"0" * 64` contract digest,
attempt 999, `outcome: PASS`, empty tests, and empty artifacts. Draft 2020-12
validation returned `forged_pass_errors=0`; it also matches `P6_PASS`. The
bootstrap checks field existence and static guard/edge shape, not evidence
completeness or binding (`tools/validate_plan.py:52-66,82-93,121-140`). This is
an executable acceptance bypass, not merely missing documentation.

**Required remediation.** Make a phase event carry graph/prompt/policy/schema
digests, exact run and predecessor/checkpoint identity, declared test-set
digest, exact required-output set, and immutable event identity. Extend the
guard IR beyond constant `equals` so success predicates executable by code
require equality to current pinned state, all mandatory tests `PASS`, exact
artifact coverage and recomputed hashes, and a monotonic authorized attempt.
Add biting schema/compiler/runtime mutations for an empty test set, missing or
extra output hash, wrong run/contract/predecessor digest, filename/attempt
mismatch, and forged P6 success.

### Critical — C2: Resume is both authorization-deadlocked and capable of cross-phase/cross-run jumps

**Evidence.** All phase interrupts collapse into the single `INTERRUPTED`
state, which has resume edges to every P0–P6 node
(`graph_engineered_subscription_execution.plan.v1.yaml:386-399`). The resume
guards bind only the new event's `node_id`, `outcome`, and `resume_node_id`
(`graph_engineered_subscription_execution.plan.v1.yaml:148-154`). The event has
no prior event/checkpoint hash, interrupted origin, pause reason, graph digest,
or controller authorization (`contracts/phase_result.schema.v1.json:5-35`). A
made-up-run P4 `RESUME` event with a zero contract digest validated with
`cross_run_resume_errors=0`. Therefore an interruption at P0 can select P6,
bypassing the declared sequential P1–P5 dependency chain.

There is also no authorized resume-event writer. Each target phase owns only
its own `Pn.attempt-{attempt}` event path (for example P2 at
`graph_engineered_subscription_execution.plan.v1.yaml:231-237` and P6 at
`:334-339`), while P_ALL prohibits activating that phase until the resume event
already exists (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:32-38`). Letting
an undeclared external actor create the file violates the single-owner/output
contract; requiring the paused phase to create it is circular.

**Required remediation.** Define a controller-owned resume-command schema and
authorized immutable command path, separate from phase-result outputs. Bind it
to current run, exact prior pause/interrupt event and checkpoint hashes,
interrupted node, allowed target (normally the same node), pinned graph/prompt/
policy/schema/route digests, next attempt, reason, and operator authorization.
Either use phase-specific pause states or store the only legal resume target in
typed state. Add negative tests for cross-run, cross-phase, stale-checkpoint,
replayed, phase-self-authored, and P0-interrupt-to-P6 resume events.

### High — H1: Required symbolic input and output-schema contracts have no declared producer or resolvable typed value

**Evidence.** The manifest consumes `contract://P2/adapter_contract`,
`contract://P4/curriculum_graph`, and `contract://P5/evaluation_subgraph`
(`graph_engineered_subscription_execution.plan.v1.yaml:256,309,333`), but none
is a declared concrete output or a registered state-port URI. P4–P6 also use
`contract://P0/P4_output_schemas`, `P5_output_schemas`, and
`P6_output_schemas` (`graph_engineered_subscription_execution.plan.v1.yaml:292,316,341`).
The closed P0 baseline schema has no property capable of storing any of those
three schema maps (`contracts/baseline_contract.schema.v1.json:5-18,45-48`).
P0-T09 resolves only `contract://P0/authorized_paths/...` selectors
(`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:33`), while the bootstrap
resolves producer ownership only for `artifact://` references and silently
accepts every other string (`tools/validate_plan.py:142-162`).

This also leaves P6's evidence scope non-executable: its tests demand direct
validation of graph IR, routes, requests, receipts, checkpoints, migration
results, all guards, and live subscription receipts
(`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:11-34`), but its
authorized inputs name only three P0 contracts plus the undefined P5 handle
(`graph_engineered_subscription_execution.plan.v1.yaml:332-340`).

**Required remediation.** Replace every symbolic producer input with an exact
`artifact://<producer>/<declared-output>` reference, or add a closed typed port
registry mapping every `contract://` URI to one producer, concrete path, schema,
and digest. Add the missing P4/P5/P6 output-schema maps to a pre-existing P0
schema and require nonempty file-to-schema entries, or use producer-owned schema
artifacts. Make the compiler reject every unresolved contract URI and add a
mutation for each class. Give P6 explicit read authorization for every immutable
artifact its tests must independently recompute.

### High — H2: Subscription login/entitlement does not prove subscription-only metering; paid credits remain an unmodeled route

**Evidence.** P2 requires subscription entitlement and rejects keys and common
provider overrides (`prompts/P2_subscription_worker_adapter.prompt.v1.md:28-31,53-56`),
but neither the baseline capability schema nor the pre-existing identity policy
records whether separately billed usage credits/overage are disabled
(`contracts/baseline_contract.schema.v1.json:31-37`,
`contracts/identity_assurance_policy.v1.yaml:1-14`). Authentication and metering
are not the same fact.

Current official Anthropic guidance says Pro/Max subscription users can enable
usage credits after plan limits and that this subsequent usage is billed at
standard API rates; strict plan-only use requires declining/avoiding that route
([Use Claude Code with Pro or Max](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan),
[Manage usage credits](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans)).
Official guidance also says usage-based Enterprise has no included allowance
and is billed at API rates from the first token, while the Plan 21 schema accepts
the undifferentiated entitlement `ENTERPRISE`
([Team and Enterprise usage credits](https://support.claude.com/en/articles/12005970-manage-usage-credits-for-team-and-seat-based-enterprise-plans)).
Official OpenAI pricing likewise states that Codex is included with ChatGPT
plans but Plus and Business can extend usage with ChatGPT credits
([OpenAI/ChatGPT pricing](https://learn.chatgpt.com/docs/pricing)). Thus local
`Logged in using ChatGPT` alone does not establish included-plan-only metering.

**Required remediation.** Define the intended boundary explicitly (included
subscription allocation only, with all separately billed credits/overage
forbidden). Add closed, versioned per-provider fields for plan/seat subtype,
metering mode, credit/overage enablement, API fallback, and evidence provenance;
enforce their legal combinations in JSON Schema and recheck before every live
call. Require receipts to record the proved metering assurance without secrets.
If either installed CLI cannot expose reliable machine-verifiable proof, route
to `PAUSED_PREREQUISITE` rather than infer it from login or plan name.

### High — H3: The baseline sandbox contract accepts contradictory, non-reconstructable containment claims

**Evidence.** `outer_sandbox` contains only a digest, unconstrained arrays of
repo-style path strings, and `DENY|ALLOWLIST`; it has no sandbox engine/profile
version, canonical OS-root identity, credential-broker boundary, symlink/mount
policy, allowlisted network destinations, or constraint that writable roots are
a subset of readable/authorized roots
(`contracts/baseline_contract.schema.v1.json:37,45-48`). The shared path regex
rejects absolute OS paths even though P2 requires an outer OS sandbox. P2's
negative read tests are well chosen (`prompts/P2_subscription_worker_adapter.prompt.v1.md:10-11,34-38`),
but P0 cannot freeze a reconstructable policy against which those tests run.

I validated a baseline with writable root `outside`, readable root `x`, network
mode `ALLOWLIST` with no destinations, an irrelevant one-item override list,
Claude `API_KEY + PRO`, and Codex `API_KEY + native_executed_model_available:
true`; Draft 2020-12 returned `contradictory_baseline_errors=0`. This shows both
the sandbox and auth portions are descriptive fields, not a biting fail-closed
contract.

**Required remediation.** Use discriminated auth/metering unions and a required
closed override-name registry. Model the sandbox engine and version, canonical
resolved roots, root purpose, read/write relationship, mount and symlink rules,
network destinations, credential acquisition boundary, and policy bytes/digest.
Add relational validation in deterministic code where JSON Schema is
insufficient. Mutate writable-root expansion, omitted override names, absolute/
relative aliases, symlink escape, network destination expansion, and auth/
entitlement contradictions.

### High — H4: P3–P6 declare subtask keys, not phase-level replay contracts

**Evidence.** P2 now correctly defines a phase-level key and explicitly tests
composition across build and both canaries
(`graph_engineered_subscription_execution.plan.v1.yaml:243-245`,
`prompts/P2_subscription_worker_adapter.prompt.v1.md:42`). In contrast, P3's
key varies by runtime node, P4's by migration unit, P5's by evaluator, and P6's
by test (`graph_engineered_subscription_execution.plan.v1.yaml:271-272,296-297,320-321,345-346`).
Each phase writes multiple repository artifacts and/or makes multiple external
calls before emitting one phase attempt event, but none declares a phase ledger
that composes those subtask keys into an atomic attempt. P3 tests replay of the
runtime it is building (`prompts/P3_durable_graph_runtime.prompt.v1.md:21-24`),
not crash/restart of the P3 implementation phase itself; P4–P6 likewise do not
test death before/after every meta-phase subtask commit.

**Required remediation.** Give every mixed/workspace-writing phase a stable
`{execution_contract_digest}:Pn:{phase_attempt}` key plus an immutable phase
ledger of declared subtask ids, input/output hashes, state (`ABSENT`,
`INCOMPLETE`, `COMMITTED`), and subtask idempotency keys. Test process death
before/after every phase side effect and event commit. A phase `PASS` event must
be admitted only after the complete declared subtask/output set is committed;
replay must neither repeat model calls nor skip an uncommitted task.

### High — H5: The currently required Claude logout pause cannot be classified honestly by the phase-event schema

**Evidence.** The local CLI is logged out, and both the manifest and P2 prompt
correctly require `PAUSED_PREREQUISITE` rather than a workaround
(`graph_engineered_subscription_execution.plan.v1.yaml:22,247-249`,
`prompts/P2_subscription_worker_adapter.prompt.v1.md:30,53-58`). But a paused
phase event must use a non-null `failure_class`, and the closed enum has no
authentication-missing, entitlement-unproven, or protected-dirty-overlap class
(`contracts/phase_result.schema.v1.json:12-13,35`). `EXTERNAL_FACT_BLOCK` is
reserved by the graph for unavailable safety-critical curriculum facts, not
plan prerequisites (`graph_engineered_subscription_execution.plan.v1.yaml:408`).
The same mismatch affects P6's protected RT-7 pause. Using another enum value
would make the required routing event schema-valid only by lying about cause.

**Required remediation.** Add distinct phase prerequisite classes such as
`AUTHENTICATION_MISSING`, `SUBSCRIPTION_ENTITLEMENT_UNPROVEN`, and
`PROTECTED_DIRTY_OVERLAP`, and condition each pause guard on its exact class as
well as node/outcome. Add conditional schema rules defining legal failure
classes for every outcome. With the current machine state, P2 must emit the
Claude authentication-missing pause and perform no canary.

### Medium — M1: Round-three exhaustion is defined for future P6 execution but not for the current pre-implementation plan QA protocol

**Evidence.** P6 correctly says that after three final-QA rounds a remaining
Critical/High produces `CONVERGENCE_EXHAUSTED` and routes to plan
`SYSTEM_FAILURE` (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:41-45`),
and the graph has the matching edge
(`graph_engineered_subscription_execution.plan.v1.yaml:374`). However, the
current review protocol is itself pre-P0: it allows at most three author/review
rounds but declares no status/event/disposition when its third round still fails
(`graph_engineered_subscription_execution.plan.v1.yaml:419-423`). A P6 event
cannot truthfully be emitted now because P6 has not been activated and its
outputs do not exist.

**Required remediation.** Distinguish design-package QA from executed P6 QA.
Add an explicit pre-execution review-exhausted status and owner/disposition, or
state that unresolved round-three design QA leaves the package unapproved and
requires a new version/review cycle rather than a fabricated P6 event. Preserve
the existing P6 `CONVERGENCE_EXHAUSTED → SYSTEM_FAILURE` route for actual P6
execution.

## Required disposition

Do not mark Plan 21 approved and do not start P0 under this package version.
Repair C1 and C2 first because they invalidate the routing authority itself;
then close H1–H5, rerun the bootstrap and all mutation tests, add the adversarial
probes named above, and run a fresh independent review set against the revised
bytes. Independently of those repairs, the current Claude state requires an
honest P2 prerequisite pause until subscription authentication and included-
allocation-only metering can both be proven.
