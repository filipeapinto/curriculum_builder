# Subscription-Only Model Execution Architecture Plan v1 — Focused QA (round 3)

## Verdict

**CHANGES REQUIRED — 2 Critical, 1 High.** Round 2's two Criticals were addressed at the
surface they named: `schemas/routes.schema.v1.json` now gets an explicit `IN_SESSION` status
value, and it genuinely works — verified directly against the schema's actual `allOf`/`required`
structure and against `runtime/capabilities.py:22-34`, whose `remove_unavailable_route` checks the
literal string `"UNPROVEN"` and is only ever called from `runtime/capability_cycle.py` (retired by
this plan's own step 1) and from tests; an `IN_SESSION` route is never passed to it, so the
pre-check claim holds. P2's Hard Constraint #1 and P3's session-bridge disposition also each got a
named, explicit resolution this round, as instructed. But both resolutions are shallower than the
plan now claims. P2's reconciliation names Hard Constraint #1 and retargets P2-T18, but never says
what happens to P2-T04/T05/T06/T08/T13/T14 — the adversarial containment tests P2's own Loop
section requires re-running after *any* adapter change — for an in-session interface that
structurally has no subprocess boundary for those tests to exercise; "in spirit" is the plan's own
hedge admitting this. P3's reconciliation asserts `session_bridge.py`'s corrected logic becomes
"the implementation inside" a one-handler-per-frozen-state registry, but the plan's own step 4
instructs preserving `finalize()` "exactly as-is" — one monolithic function that today does what
maps to at least six or seven of P0's 25 frozen states in a single un-checkpointed sweep, with no
per-state resumability and no targeted-revision mechanism at all. These two claims cannot both be
true, and neither was checked against the repository content this round.

## Findings

### 1. Critical — The two-interface reconciliation never says what happens to P2's adversarial containment tests (T04/T05/T06/T08/T13/T14) for the in-session interface, and "in spirit" is not a resolution

**Evidence.**
- Plan text (`subscription_only_execution_model.plan.v1.md:255-260`): *"The in-session Claude
  interface (authoring) must still satisfy P2's other four hard constraints in spirit — sealed
  request, staged filesystem, atomic admission, normalized failure classes — using
  `session_bridge.py`'s existing `worker_request.json` / authorized-paths / `workers/` staging
  pattern as the structural equivalent of a sealed request and staged output for a call that has
  no subprocess to sandbox."*
- Reading `runtime/session_bridge.py` directly: `prepare()` (lines 53-172) does write a
  `worker_request.json` with `authorized_inputs`/`authorized_outputs` and stage a per-run `inputs/`
  and `workers/` directory — but nothing in `prepare()` or `finalize()` (lines 193-393) *enforces*
  that the authoring agent writes only the declared outputs. There is no fake-executor abstraction,
  no sandbox argument, and no boundary check of any kind, because the "worker" is the same
  in-session agent with full session file access — there is no process boundary to deny an
  undeclared read or reject a symlink escape. `finalize()`'s admission logic (lines 219-226) checks
  only that `workers/domain.json` and `workers/lab.json` exist and that two specific hashes match;
  it does not reject an *extra* file alongside them, does not classify malformed JSON into one of
  P2's four normalized failure classes (a malformed `domain.json` raises an uncaught
  `json.JSONDecodeError`, not a normalized `RuntimeFailure`), and has no notion of an "out-of-scope
  path" rejection at all.
- P2's own text is explicit that this is not optional: P2-T05 ("Undeclared read denied... assert
  the invocation's sandbox arguments equal the P1-frozen containment command exactly"), P2-T06
  ("Path escape denied... through a symlink"), P2-T08 ("six separate assertions: output absent; an
  extra file... malformed JSON... schema-invalid JSON... malformed structured output... artifact
  written to an out-of-scope path"), and P2-T14 ("containment is structural, not instructional")
  are all adversarial, structural tests — and P2's `# LOOP` section (line 213-214) requires
  re-running exactly this set — P2-T04, P2-T05, P2-T06, P2-T13, P2-T14 — "because any adapter
  change can move a boundary."
- Plan 20's step 5 P2 bullet (`subscription_only_execution_model.plan.v1.md:251-268`) names only
  Hard Constraint #1 and retargets P2-T18 (`lines 264-266`) and "whichever test id covers Hard
  Constraint #1" (implicitly P2-T11). It never states whether P2-T04/T05/T06/T08/T13/T14 apply
  unchanged, are retargeted to something meaningful for a no-subprocess interface, or are retired
  as inapplicable — the exact three-way disposition the plan's own P1 reconciliation bullet
  (`lines 244-250`) correctly demands for *other* superseded test ids, but does not apply to
  itself here.

**Impact.** An implementer following the plan's "in spirit" language has no way to know whether the
in-session interface is supposed to pass P2-T05/T06/T08/T14 as literally written (which it
structurally cannot — there is no sandbox to assert arguments against, no subprocess to deny a read
to), or whether those tests are retired for this interface (which the plan never says). Left
unresolved, this reproduces exactly the failure mode round 1 and round 2's Criticals were raised to
stop: a live, unexecuted phase-19 design (P2's adversarial containment suite) left uncontradicted
and unreconciled against an architecture that cannot satisfy it as written, discovered only when
P2 next executes.

**Minimal required remediation.** In step 5's P2 bullet, state explicitly, test id by test id, the
disposition of P2-T04, P2-T05, P2-T06, P2-T08, P2-T13 and P2-T14 for the in-session interface:
either state plainly that structural containment is inapplicable to a no-subprocess interface and
these tests apply only to the `codex exec` interface (with the in-session interface's actual
integrity guarantee named — e.g., schema validation plus hash-verified resume, not sandboxed
denial), or specify the concrete mechanism (not the same tests, not "in spirit") that gives the
in-session interface an equivalent guarantee.

### 2. Critical — The P3 disposition ("session_bridge.py's logic becomes the per-state handler implementation") contradicts the plan's own step 4 instruction and is not achievable against P3-T01/T03/T09/T14/T15/T20 without a redesign this plan does not scope

**Evidence.**
- Plan text, step 5's P3 bullet (`subscription_only_execution_model.plan.v1.md:269-282`): *"Plan
  20 selects the first: the corrected `session_bridge.py` (step 4) supplies the authoring and
  finalize/accept logic *inside* P3's P0-frozen state-handler registry (P3-T01–P3-T03: exactly one
  production handler per frozen unit state)... 'In-session model writes files' in the corrected
  architecture means the Claude agent driving the relevant state handler produces the artifact as
  part of executing that handler..."*
- Plan text, step 4 (`subscription_only_execution_model.plan.v1.md:227-230`): *"Preserve every
  other check in `finalize()` exactly as-is (schema validation, domain verifier, receipt hashes,
  readability, PDF legibility/asset resolution, visual review); this step only replaces the bypass
  branch and the worker-identity fields."*
- Reading `runtime/session_bridge.py` directly: `finalize()` (lines 193-393) is one function that,
  in a single uninterrupted call, runs schema validation, the domain verifier subprocess, receipt
  checks, visual-role completeness, derivation/entailment checks, PDF render, readability, Bloom
  verb scoring, PDF text-legibility, PDF asset resolution, and visual review — before writing one
  terminal decision. `prepare()` writes exactly one checkpoint (`state="VALIDATE"`, line 163-166)
  and then returns `INTERRUPTED`; nothing between `prepare()` and the terminal write in `finalize()`
  is separately checkpointed. `policy/controller.v1.yaml`'s 25 frozen states (`VALIDATE` …
  `FINAL_ACCEPTANCE`, per P3's own text at `P3_production_unit_state_machine.prompt.v1.md:56`) map
  to what `finalize()` does internally, but `finalize()` records none of those intermediate states
  as distinct handler completions.
- P3-T01 requires "exactly one production handler per P0-frozen unit state: no state without a
  handler... Deleting or duplicating one entry fails the test." P3-T03 requires every frozen state
  be independently reachable and traversed. P3-T09 requires that a targeted revision "revises only
  that artifact's bytes" while every other artifact's SHA-256 stays identical — `session_bridge.py`
  has no revision mechanism at all; `finalize()` runs its full check sweep exactly once per call.
  P3-T14/P3-T15/P3-T20 require an interrupt at an *arbitrary* state to leave a valid last checkpoint
  and resume without rebuilding anything already valid — impossible against a function that performs
  ten-plus logically distinct pieces of work with only one checkpoint before and after all of them.
- Step 4's instruction to preserve `finalize()` "exactly as-is" is therefore incompatible with the
  step 5 P3 bullet's claim that this same logic becomes "the implementation inside" a 25-state
  one-handler-each registry: preserving it exactly as-is keeps it as two opaque steps; satisfying
  P3-T01/T03/T09/T14/T15/T20 requires decomposing it into many independently checkpointed handlers.
  This is the identical structural gap round 2's Critical #2 raised for P3 ("a two-step
  prepare/finalize bridge" vs. "P3-T01–T03's one-handler-per-state totality requirement") — the
  round-2 remediation added a sentence naming which disposition was "selected," but did not resolve,
  or even re-examine, the structural incompatibility round 2 asked it to resolve.

**Impact.** If executed as written, an implementer has two mutually exclusive instructions in the
same document: preserve `finalize()` unchanged (step 4), and make its logic satisfy a one-handler-
per-frozen-state registry with independent resumability (step 5). Following step 4 fails P3-T01,
P3-T03, P3-T09, P3-T14, P3-T15 and P3-T20 outright when plan 19's P3 next executes; attempting to
satisfy P3 by decomposing `finalize()` violates step 4's explicit "exactly as-is" instruction and is
work this plan's own scope statement disclaims ("does not touch the unit-state machine, checkpoint,
or resume logic P0/P3/P5 froze"). Either way, the plan's stated architecture cannot be executed as
written without either breaking its own step 4 or leaving P3 unsatisfiable — precisely the
"reconciliation is stale text, not an actual resolution" failure mode round 1 and round 2 were each
raised to catch.

**Minimal required remediation.** Resolve the contradiction in the plan text itself, not by
assertion: either (a) state plainly that `session_bridge.py`'s current two-phase structure is
retained only as a bridge for *this* plan's scope, and that decomposing it into a P3-compliant
per-state handler registry is explicitly out of this plan's scope and left as unstarted P3 work
(dropping the "supplies the implementation inside the registry" claim), or (b) scope step 4's
finalize() work as a decomposition into named, independently checkpointed pieces sufficient to
satisfy P3-T01/T03/T09/T14/T15/T20, and drop "preserve... exactly as-is." Do not leave both
statements standing together.

## Observations (non-blocking)

- `policy/routing/model_registry.v1.yaml`'s Claude entry, as step 2 describes it
  (`subscription_only_execution_model.plan.v1.md:154-157`, *"`reasoning_efforts` and
  `supports_pro_mode` stated honestly as 'not applicable — no dispatch command'"*), is ambiguous
  against `schemas/model_registry.schema.v1.json:72-74`, which types `supports_pro_mode` strictly
  as `boolean` — a literal string value there fails schema validation, contradicting the plan's own
  Verification sequence item 3 ("`model_registry.v1.yaml` validate[s] against their (updated)
  schemas"). There is an obvious schema-conformant resolution (`supports_pro_mode: false`, with the
  "not applicable" honesty carried in `role`/`strengths` prose instead), so this falls short of a
  blocking finding, but the same imprecision was rated High in round 1 (`codex exec` vs.
  `codex review`) for the identical reason — an implementer could plausibly attempt the literal
  string value first and lose a cycle to schema validation before self-correcting. Worth tightening
  before implementation, not a blocker to plan approval.
