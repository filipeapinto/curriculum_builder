# Subscription-Only Model Execution Architecture Plan v1 — Focused QA (round 2)

## Verdict

**CHANGES REQUIRED — 2 Critical, 1 High.** Round 1's three findings were addressed at
the surface the plan's own text names (widened "Exact work"/reconciliation scope to
include `policy/routes.v1.yaml`, `policy/routing/model_registry.v1.yaml`, and P3;
committed to `codex exec` specifically over `codex review`; named an explicit receipt
field contract with a test). But two of those fixes do not hold up against the actual
schema and prompt text they claim to reconcile. The step-2 policy fix assumes
`schemas/routes.schema.v1.json` can express a "no command, no proof" worker route with
"less structural change" than the alternative — it cannot, without either fabricating a
non-execution "proof" object (violating the file's own real-execution-only Rule) or
setting `status: UNPROVEN` on a route the file's own preflight semantics then require to
stop the run as `META_SYSTEM_FAILURE`, since it is unremovable and required. And the
widened P2/P3 reconciliation still treats plan 19's P2 phase as needing only a
containment-wording fix and a P2-T18 retarget, when P2's own Hard Constraint #1 — one
subprocess-based invocation interface serving authoring, research, review *and*
revision, "never a separate code path with its own boundary rules" — is structurally
incompatible with plan 20's mandate that authoring runs in-session with no subprocess at
all. This is the same failure mode round 1's Critical named (silently leaving a sibling
plan's approved, unexecuted design uncontradicted), recurring one layer deeper than the
patch reached.

## Findings

### 1. Critical — `schemas/routes.schema.v1.json` cannot express the "no command, no subprocess" worker route the way step 2 assumes, and the plan's own stop condition is the actual outcome

**Evidence.**
- `policy/routes.v1.yaml`'s file-level Rule states: *"help text, installed binaries, and
  configuration files are never capability proof... Each route below carries the command
  that was actually executed and what it returned... a route that cannot be proven is
  removed, not assumed."* `schemas/routes.schema.v1.json`'s own `description` restates
  this as the file's only two legal states: real execution proof, or `status: "UNPROVEN"`.
- Structurally: every route object requires `id`, `purpose`, `command`, `proof`
  (`schemas/routes.schema.v1.json:51-56`). `command` may be `null`. `proof` may be `null`
  or an object requiring `executed`/`returned` strings — but that `required` only binds
  when `proof` is an object; `proof: null` trivially satisfies it. The `allOf`/`if`/`then`
  block (lines 115-134) then requires `status` (enum-locked to `"UNPROVEN"`) *only* when
  `proof` is `null`. There is no third schema-legal shape for "command is null and there
  is no proof object because nothing was executed."
- `policy/routes.v1.yaml`'s `preflight.on_failure` (lines 129-131): *"Remove the
  unavailable route before generation, or stop as `META_SYSTEM_FAILURE` if the route is
  required."* The worker/authoring route is required on every run (there is no unit
  without an authoring step). If step 2 marks it `status: UNPROVEN` (the only schema-legal
  way to have no proof), preflight's own documented rule makes every run stop as
  `META_SYSTEM_FAILURE` before generation — exactly what happens today to the `imagegen`
  route, which is `UNPROVEN` and explicitly conditional/removable, unlike `worker`.
- The plan's step 2 text (`subscription_only_execution_model.plan.v1.md:148-158`) offers
  this as one of two options with "no command, no subprocess proof shape — state
  explicitly why this route type has no command field," phrased as though the schema
  accommodates it "whichever the route schema supports with less structural change" —
  without having verified against the actual schema content that either option clears
  validation without either (a) fabricating a "proof" object that isn't real execution
  evidence (contradicting the file's own Rule this plan elsewhere promises to preserve),
  or (b) triggering the required-route `UNPROVEN` → `META_SYSTEM_FAILURE` stop.
- The plan's own stop conditions (lines 300-311) already name this exact scenario:
  *"`schemas/routes.schema.v1.json`... cannot express an in-session, no-command worker
  entry without a schema change this plan did not scope... a schema change is a
  stop-and-report, not a silent workaround."* Given the schema content above, this stop
  condition is not a remote edge case the plan hedges against — it is the actual, provable
  outcome of executing step 2 as written.

**Impact.** An implementer following step 2 literally will either (a) write a
non-execution "proof" object for the worker route to dodge `UNPROVEN`, silently
violating the file's own documented proof discipline the plan claims to preserve, or (b)
mark it `UNPROVEN` and immediately hit the plan's own stop condition at the first
preflight run — meaning the plan's central "worker = in-session Claude" architecture
cannot reach `ACCEPTANCE CRITERIA` item 3 ("routes.v1.yaml no longer names codex exec as
the authoring route... the QA-gate route instead") without either a policy-file
integrity violation or an immediate, plan-halting stop the plan did not budget for as the
likely outcome (it is written as a low-probability hedge, not the load-bearing design
question it actually is).

**Minimal required remediation.** Before authorizing step 2: resolve, in the plan text
itself, whether the in-session worker is (a) not represented as a `routes.v1.yaml` entry
at all (the file's own docstring scopes it to "every *external* capability the run
depends on" — an in-session call may simply not belong in this file), or (b) represented
with an explicit, named exception to the file's real-execution-only Rule, stated as a
deliberate schema-intent change, not inferred from "whichever the schema supports." Do
not leave this decision to be discovered mid-execution as a stop condition when the
schema content already answers it now.

### 2. Critical — The widened P2/P3 reconciliation still doesn't resolve P2's Hard Constraint #1, which is incompatible with the corrected architecture; P3's own state-machine deliverable is left unaddressed

**Evidence.**
- Round 1's Critical was specifically that plan 19's P1-T04, P2-T18 and P3's
  session-bridge mandate were outside the plan's scope. The revision widened scope to
  include these three items by name — but P2 is a full, separately-approved phase whose
  design commitments extend well past the one test id (P2-T18) the plan now names.
- `plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md`
  Hard Constraint #1 (lines 54-56): *"One invocation interface serves the authoring,
  research, review and revision roles. Role identity is a parameter of the request,
  **never a separate code path with its own boundary rules.**"* P2-T11 (lines 159-163)
  makes this a mandatory, order-blocking test: a "Role × failure-class matrix" exercising
  all four roles — including **authoring** — through the same subprocess-based adapter,
  with "a meta-assertion [that] fails if any role/class pair in the matrix is
  unexercised." P2-T18 (the live canary the plan does retarget) is explicitly *not*
  scoped to the judge role alone — it proves "the smallest valid artifact of a registered
  type," which per Hard Constraint #1 includes authoring artifacts.
- Plan 20's own architecture requires the opposite: authoring is in-session Claude with
  **no subprocess at all** (`subscription_only_execution_model.plan.v1.md:34-43,
  62-67`), while the cross-family judge is a real `codex exec` subprocess. These two
  roles cannot share "one invocation interface... never a separate code path with its own
  boundary rules" — one has a sandboxed subprocess boundary to enforce (P2-T05, P2-T06,
  P2-T14 all test this boundary), the other structurally has none.
- Plan 20's reconciliation bullet for P2 (`subscription_only_execution_model.plan.v1.md:228-231`)
  addresses only: *"P2's references to 'P1-frozen' containment — stay correct in concept...
  but now bind to the Codex subprocess boundary. P2-T18's 'live canary'... must be
  retargeted at the `qa_gate` route."* This never names Hard Constraint #1, P2-T11's role
  matrix, or the fact that P2's Allowlist (`P2_schema_bound_worker_execution.prompt.v1.md:100-108`)
  forbids editing `runtime/session_bridge.py` within P2's own scope — i.e., P2 as approved
  builds a second, independent worker-invocation module (`runtime/worker.py`) that plan
  20's P3 reconciliation elsewhere treats as interchangeable with "the codex exec-as-worker
  adapter," when it is actually a separate, already-scoped deliverable with its own
  4-role subprocess design.
- Separately, the P3 reconciliation bullet (lines 232-239) asserts *"`session_bridge.py`
  (corrected per step 4) **is** the production worker path"* — but P3's own prompt
  requires a **state-handler registry with exactly one production handler per each of the
  P0-frozen unit states** (P3-T01, T02, T03; `P3_production_unit_state_machine.prompt.v1.md:130-138`,
  56: "25 states `VALIDATE`…`FINAL_ACCEPTANCE`"), while `session_bridge.py` implements only
  two opaque steps (`prepare`/`finalize`) around one manual `INTERRUPTED` handoff. Plan
  20's step 4 instructs preserving `finalize()`'s existing checks "exactly as-is," which
  does not produce a 25-state handler registry. The plan does not say whether P3's
  state-machine deliverable (P3-T01 through P3-T24, all of P3's "Build" section) is also
  superseded, retained as-is on top of the unchanged `session_bridge.py`, or something
  else — it addresses only the one "session-bridge disposition" sentence P3 contains, not
  the phase's actual architecture.

**Impact.** If plan 20 executes and step 5 produces a reconciliation list scoped the way
the plan's own text currently guides it (containment wording + one test retarget for P2;
one disposition sentence for P3), the underlying phase-19 approvals for P2's Hard
Constraint #1 and P3's state-handler registry remain live, unexecuted, and
uncontradicted — precisely the condition round 1's Critical was raised to prevent. Plan
19's next execution of P2 or P3 would either silently rebuild the subprocess-uniform
worker adapter (re-entrenching the mechanism this plan exists to retire) or discover the
contradiction only mid-phase, past the point this plan's own review was supposed to
catch it.

**Minimal required remediation.** Step 5's guidance for P2 must name Hard Constraint #1
and P2-T11 explicitly and state the correction (e.g., split the "one invocation
interface" into two role-scoped mechanisms, or state that P2's authoring/revision roles
are struck from scope and only research/review remain subprocess-routed) rather than
treating P2-T18 as the sole affected item. Step 5's guidance for P3 must state explicitly
whether the P0-frozen 25-state handler-registry requirement is retained on top of the
unmodified `session_bridge.py`, and if so, how a two-step prepare/finalize bridge
satisfies P3-T01–T03's one-handler-per-state totality requirement — not merely that the
one "session-bridge disposition" sentence is superseded.

## Observations (non-blocking)

- Step 3's Codex receipt field contract (`status`, `returncode`, `executed_model`,
  `events`) is materially more concrete than round 1 found it and now carries a
  regression test obligation. It still does not enumerate which Codex `item.completed`
  `item.type` values should count as "tool activity" for the ported predicate (real
  top-level Codex event types — `thread.started`, `item.completed`, `turn.completed` —
  never themselves contain the substring `"tool"`, so a naive reuse of the old predicate
  against raw Codex events would silently undercount to zero). This falls short of High
  only because the plan already commits to a concrete test that would surface a shape
  mismatch; it would not necessarily surface a silent semantic undercount. Worth
  tightening before implementation, not a blocker to plan approval.
