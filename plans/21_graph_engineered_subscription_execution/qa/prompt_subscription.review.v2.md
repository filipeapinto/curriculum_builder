# Plan 21 prompt/subscription/security QA — round 2

## Verdict

**CHANGES REQUIRED — 1 Critical, 4 High, 1 Medium.** Round 1's provider
corrections are materially sound: Codex identity is now stated as
driver-bound/requested rather than natively observed, Claude's current logout
takes a prerequisite pause, paid/provider overrides fail closed, and Codex read
containment now requires an outer readable-root OS boundary rather than treating
`-C` plus `--sandbox read-only` as a read allowlist. The bootstrap commands also
exist and pass, phase execution is sequential, shared log writes are gone, and
the Anthropic monthly-credit statement is corrected.

Approval is still blocked. Most importantly, the typed meta-plan has no
machine-readable per-phase result event on which its guard ids can operate. The
only declared phase results are Markdown reports, so P_ALL cannot select edges
deterministically without parsing narrative prose—the exact behavior P1 and the
plan prohibit. Pause/resume, QA non-convergence routing, the P0 scope/auth
contract, and bootstrap mutation coverage also remain incomplete.

## Checks performed

- Read every current Plan 21 source artifact, schema, tool, and prompt, plus this
  reviewer's round-1 report. Other reviewers' reports were not used as review
  evidence.
- Ran both shipped bootstrap commands from the repository root:
  - `python3 plans/21_graph_engineered_subscription_execution/tools/validate_plan.py`
    → `plan21_bootstrap=PASS`.
  - The same command with `--self-test` → `plan21_bootstrap=PASS`.
- Reconfirmed current local facts without exposing credentials:
  - Claude Code `2.1.226`; `loggedIn: false`, `authMethod: none`,
    `apiProvider: firstParty`.
  - Codex CLI `0.147.0`; `Logged in using ChatGPT`.
- Confirmed `/usr/bin/sandbox-exec` exists and the installed `codex sandbox`
  surface supports an explicit sandbox state/readable root. This makes P2's new
  outer-containment requirement locally plausible; the live P2 test must still
  prove the final profile.
- Ran an in-memory negative mutation deleting only P1's `SYSTEM_FAILURE` edge.
  The shipped bootstrap validator accepted it (`missing_P1_system_edge=ACCEPTED`).
  No repository file was changed by that check.

## Findings

### 1. Critical — Edge guards have no typed result-event input or executable definition, so deterministic phase routing and P1 self-compilation remain impossible

**Evidence.** The revised manifest now names guard ids and outcomes on every edge
(`graph_engineered_subscription_execution.plan.v1.yaml:243-273`), and P_ALL says
deterministic code validates an immutable result event and selects that typed
edge (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:17-23,30-36`). P1 makes the
same requirement explicit: executable guard ids, first-class failure/repair/
resume/exhaustion edges, outcome totality, and self-compilation without prompt
prose supplying missing semantics
(`prompts/P1_graph_ir_and_static_compiler.prompt.v1.md:3-12,19-20,27-30`).

But no machine-readable phase-result event is declared or schema-bound. Every
phase authorizes only `results/P<n>.result.v1.md` as its result record, and every
node maps that report to the opaque symbolic schema
`contract://markdown/phase-result-v1`
(`graph_engineered_subscription_execution.plan.v1.yaml:69-81,102-109,130-137,
155-162,180-186,204-209,227-232`). The package contains no phase-result JSON/YAML
schema and no per-attempt event path. The plan schema types `guard_id` only as a
string matching a naming pattern; it defines no guard registry, input field,
predicate, exclusivity set, or outcome enum
(`graph_engineered_subscription_execution.schema.v1.json:81-94`).

The missing semantics are observable in the manifest. For example, P1 has
`P1_PASS`, `P1_REVISABLE`, `P1_SYSTEM_FAILURE`, and `P1_INTERRUPTED` edges, but
there is no typed P1 output field whose value is compared by those guards. The
seven `failure_classes` at manifest lines 49-56 are not mapped to phase-result
fields or guards. Repair edges have `max_attempts`, but no explicit
repeat-signature input or convergence-exhausted edge even though P1-T05 requires
both. A Markdown report can describe these facts, but making code parse or infer
them from prose violates P1-T12 and P_ALL's own control-plane rule.

**Impact.** P0→P1 cannot be selected from a typed result event as required. P1
cannot self-compile the manifest without inventing a completion-event schema and
guard implementation that is absent from both its authorized outputs and the
current plan. If an implementation accepts the manifest anyway, outcome
totality, guard exclusivity, repair exhaustion, and terminal selection are
claims rather than compiled properties.

**Required remediation.** Add a strict machine-readable phase-result/event
schema and one immutable per-node/per-attempt output path. At minimum it must
bind node id, attempt, P0 digest, test results, status/outcome enum, failure
class, repeat signature, stop/pause reason, and artifact hashes. Define guard ids
as deterministic predicates over named fields, map every possible result enum to
exactly one edge, and add explicit convergence-exhaustion routing. Markdown can
remain a secondary human report, never the edge input. Add all new files to each
node's authorized outputs and make P1-T12 compile the actual registry/schema.

### 2. High — `PAUSED_PREREQUISITE` is an irreversible terminal, not a resumable pause, and fixed immutable result paths cannot record a resumed attempt

**Evidence.** The plan calls missing Claude entitlement a pause
(`graph_engineered_subscription_execution.plan.v1.yaml:22,146-147`) and routes P2
to `PAUSED_PREREQUISITE` through a `kind: terminal` edge (lines 259-259). P_ALL
then activates no downstream node (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:25-28,32-35`).
The edge schema allows `resume` as a kind but allows `from` only `START` or a
phase id—not `PAUSED_PREREQUISITE` or `INTERRUPTED`
(`graph_engineered_subscription_execution.schema.v1.json:81-94`). The manifest
contains no resume edge at all.

The output contract makes an informal rerun unsafe. P2 has one fixed result path,
`plans/21_graph_engineered_subscription_execution/results/P2.result.v1.md`
(`graph_engineered_subscription_execution.plan.v1.yaml:130-137`), while the plan
says phase result/events are immutable (line 29) and its P2 idempotency key varies
by request and attempt (line 142). A truthful paused P2 result occupies that only
path. The plan defines neither an attempt-qualified result event nor a rule for
starting a new plan run that reuses P0/P1 after the user restores OAuth.

**Impact.** Current Claude logout is classified honestly, but the advertised
"pause" cannot continue. The operator must either overwrite an immutable P2
record, silently discard the paused attempt, or restart without a specified
new-run/migration rule. External interrupt has the same plan-level issue.

**Required remediation.** Either implement real pause/resume edges and
attempt-qualified immutable events (with digest-pinned resumption at P2), or name
the state honestly as a terminal prerequisite stop and specify that restored
auth starts a new plan run that may reuse only explicitly validated immutable
predecessors. Apply the same decision to `INTERRUPTED`.

### 3. High — P6 still instructs an illegal unit `BLOCKED` result for plan-QA non-convergence

**Evidence.** The revised manifest correctly separates unit and plan terminals,
states that no phase targets unit `BLOCKED`, and routes P6 defects to
`SYSTEM_FAILURE`
(`graph_engineered_subscription_execution.plan.v1.yaml:46-48,240-242,266,280-282`).
P_ALL repeats that contract (`prompts/P_ALL_graph_orchestrator.prompt.v1.md:25-28`).
Yet P6's LOOP still says that if a Critical/High remains after round three,
"record BLOCKED" (`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:36-42`).

QA non-convergence is neither a missing external safety-critical curriculum fact
nor a schema-legal plan terminal. Following the node prompt literally produces
the exact false-block condition the revision otherwise forbids.

**Required remediation.** Replace that instruction with the canonical plan
disposition (normally `SYSTEM_FAILURE` with
`failure_class: CONVERGENCE_EXHAUSTED`, or a separately declared plan terminal)
and add a negative test proving QA non-convergence can never emit unit
`BLOCKED`.

### 4. High — The baseline contract schema still does not type the path selectors or subscription evidence on which P2–P6 safety depends

**Evidence.** P0-T09 now requires every symbolic scope to resolve to canonical
paths and schemas, and P2-T03/T04 require an exact subscription entitlement plus
provider/key/helper precedence evidence
(`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:30-35`;
`prompts/P2_subscription_worker_adapter.prompt.v1.md:28-34`). P4–P6 consume
`contract://P0/authorized_paths/...` selectors and P2 consumes P0 capability
facts (`graph_engineered_subscription_execution.plan.v1.yaml:126-140,179-186,
203-209,226-232`).

The new baseline schema does not encode those contracts. `authorized_paths`
merely requires keys `P4`, `P5`, and `P6`, with each value any object;
`capability_facts` is any object; `baseline_results` accepts arbitrary objects;
and `status_vocabularies` requires only three untyped keys
(`contracts/baseline_contract.schema.v1.json:5-13`). Thus empty P4/P5/P6 objects
and empty capability facts are schema-valid even though all canonical selectors
and subscription evidence are absent. The schema also has no exact field/value
for Claude's versioned subscription entitlement, Codex's ChatGPT auth class,
provider override statuses, or the outer sandbox policy digest.

**Impact.** Downstream prompts can only enforce these requirements with bespoke
code or prose not described by the declared input schema. P1-T12 cannot prove
that all output selectors resolve from a schema-valid P0 artifact, and P2 cannot
claim its auth/sandbox preconditions are contract-bound merely because the
baseline validates.

**Required remediation.** Make the baseline schema closed and concrete: enumerate
every P4/P5/P6 selector and require canonical path arrays plus schema ids;
define the exact capability-evidence object, including auth/entitlement fields,
override-name statuses, CLI hashes/versions, and sandbox policy digest; and type
the unit/run/plan vocabularies. Add negative fixtures for empty objects, missing
selectors, relative/escaping paths, ambiguous entitlement, and missing policy
digests.

### 5. High — The shipped bootstrap self-test does not enforce the mandatory failure/exhaustion edges that P0-T11 says it mutation-tests

**Evidence.** P0-T11 says that omitting a mandatory IR field/edge must make the
bootstrap check fail (`prompts/P0_contract_and_evidence_freeze.prompt.v1.md:33-35`).
The validator checks ids, prompt headers, reachability, terminal reachability,
bounded self-loops, and absence of plan `BLOCKED`, but it never asserts that each
phase has success, repair, system-failure, interrupt, pause where applicable, or
exhaustion coverage (`tools/validate_plan.py:35-125`). Its shipped self-tests
delete an edge set that makes P4 unreachable but do not remove a mandatory
failure edge while leaving reachability intact (lines 132-168).

The in-memory mutation performed for this review deleted only
`E-P1-SYSTEM`. The validator still returned success because P1 could reach the
`INTERRUPTED` terminal. That mutated graph violates manifest invariants and
P1's declared stop routing but passes both schema and semantic bootstrap checks.

**Impact.** P0-T00 can pass while a mandatory failure disposition is absent, and
P0-T11 can be made to pass only by choosing a convenient edge whose deletion
also breaks reachability. This is not a biting test of the failure edge class it
claims to protect.

**Required remediation.** Have the bootstrap validate a minimal per-phase edge
contract and explicit repair-exhaustion disposition, then add mutations deleting
each class independently. Alternatively narrow P0-T11's claim to the properties
the bootstrap actually proves and leave complete outcome totality exclusively to
the production compiler—but do not claim the existing bootstrap rejects a
mandatory failure edge.

### 6. Medium — Four node prompts still name result paths relative to an unspecified working directory

**Evidence.** The manifest authorizes repository-root paths under
`plans/21_graph_engineered_subscription_execution/results/...`, but P3, P4, P5,
and P6 instruct executors to write `results/P3.result.v1.md`,
`results/P4.result.v1.md`, `results/P5.result.v1.md`, and
`results/P6.result.v1.md`/`supersession.v1.md`
(`prompts/P3_durable_graph_runtime.prompt.v1.md:41-44`;
`prompts/P4_curriculum_graph_migration.prompt.v1.md:52-56`;
`prompts/P5_evaluator_optimizer_acceptance.prompt.v1.md:47-51`;
`prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:44-49`). The
bootstrap is explicitly run from repository root, and neither P_ALL nor the node
prompts changes working directory.

**Impact.** A literal shell executor can write a top-level `results/` directory
outside the authorized path. P0's canonical scope check should catch the
mismatch, but the prompt should not direct it in the first place.

**Required remediation.** Use the exact repository-root paths from the manifest
in every prompt, or state one canonical phase working directory and have the
compiler normalize/verify relative paths before activation.

## Round-1 remediation status

| Round-1 item | Round-2 disposition |
|---|---|
| Terminal namespaces and system/interrupt edges | **Partially fixed.** Manifest/schema routing is improved; P6 still says `BLOCKED`, and result guards remain untyped. |
| Codex native identity overclaim | **Fixed.** `DRIVER_BOUND_REQUEST`, pinned argv/registry evidence, and null native model are honest and tested. |
| Compiler bootstrap deadlock | **Fixed.** The shipped deterministic validator and self-test exist and pass before P0; production compilation begins after P1. |
| Shared log/write race | **Fixed.** Phase prompts prohibit shared log append and execution is sequential. Exact downstream scopes remain weakly schema-bound (Finding 4). |
| Claude subscription entitlement ambiguity | **Substantially fixed/fail-closed.** Generic first-party/Console OAuth is explicitly insufficient and current logout pauses. The evidence object still needs a concrete schema (Finding 4). |
| Codex readable-root containment | **Fixed at plan level.** The prompt requires an outer OS sandbox and biting relative/absolute/traversal/symlink denials; `-C` plus read-only is explicitly rejected. |
| Anthropic monthly-credit statement | **Fixed.** The assessment now records the June 2026 pause and subscription-limit behavior. |

## Positive observations

- All phase prompts retain explicit GOAL/TEST/LOOP sections, bounded repair
  scope, mandatory retests, and honest stop conditions.
- Current Claude logout is not mislabeled as a factory or curriculum failure.
  No live Claude capability is fabricated, and P3 cannot start while P2 is
  paused.
- Codex's current identity limitation is handled with the correct epistemic
  boundary: binary/driver/auth/request evidence is recorded, native model is
  null, and self-report is rejected.
- The one-adapter design is plausible as a normalized contract with two
  provider-specific drivers. The revision correctly avoids claiming that the
  native CLI security and identity surfaces are identical.
- Evaluator independence remains strong: context manifests exclude author
  sessions and sibling verdicts, deterministic checks run first, verdicts are
  schema-bound/fail-closed, and the author cannot aggregate or accept.

## Exit decision

**NOT APPROVED.** Resolve the Critical and High findings, rerun both bootstrap
commands and biting mutations, validate the strengthened P0 contracts, and repeat
the complete independent review round. PASS remains available only at zero
unresolved Critical/High findings.
