# Subscription-Only Model Execution Architecture — Implementation Plan v1

## Status and objective

Planning only; no implementation is authorized by this document's creation.

The curriculum factory currently has **two live-model mechanisms that
disagree**, and this plan reconciles both of them against one binding
constraint: the user has only LLM subscriptions (Claude Code, and a ChatGPT
Pro subscription reached through the installed, authenticated `codex` CLI —
`~/.codex/auth.json`: `auth_mode: "chatgpt"`) — never a billed API key, for
this project, ever.

**Mechanism one — already proven, already approved, wrong assignment.**
`policy/routes.v1.yaml`'s `worker` route (proven 2026-07-29/2026-07-31, real
`codex exec` transcript captured) and `policy/routing/model_registry.v1.yaml`
(only OpenAI models registered: `gpt-5.6-sol/terra/luna`) together declare
that **Codex authors curriculum content** — "every bounded model call —
authoring, review, acceptance" runs through `codex exec`. Plan 19's P1-T04,
P2-T18, and P3 (`status: approved`, none of its phases executed yet) commit
to proving and consuming exactly this route, and P3 explicitly charters
retiring `runtime/session_bridge.py`'s in-session pattern as "the manual
bridge this phase must migrate or reduce."

**Mechanism two — broken, and by explicit user instruction not the fix.**
`runtime/capability_cycle.py`, `runtime/gemini.py`, and
`runtime/resolve_gemini_settings.mjs` implement a second mechanism: a
cross-family judge proven by shelling out to a `gemini` CLI binary, required
because `model_registry.v1.yaml` registers only one provider (OpenAI) and
P1-T08 refuses a same-family judge for safety-critical/high-risk task
classes — Codex cannot legally judge Codex's own work under the policy's own
rule. `gemini` is configured for `gemini-api-key` auth with no key present.

**The correction this plan makes, stated once and held:** authoring is
**Claude**, in-session, no subprocess — the pattern `session_bridge.py`
already implements structurally (`decision_rationale`: *"user authorized the
current in-session LLM as the model worker; no separate API"*) but
mis-attributes to `gpt-5.6-sol`. The cross-family judge — the role that
makes the "no same-family judge" rule satisfiable at all — is **Codex**,
via a real, non-interactive `codex exec --json --output-schema ...
--output-last-message ...` subprocess call. This is a two-family split
(Anthropic authors, OpenAI judges) that a Gemini bolt-on was standing in
for and cannot, on this user's subscriptions, actually deliver.

This means the plan does not just retire `capability_cycle.py`'s Gemini
path (mechanism two); it **explicitly and disclosedly supersedes**
mechanism one's worker assignment in `policy/routes.v1.yaml`,
`policy/routing/model_registry.v1.yaml`, and plan 19's P1/P2/P3 text, rather
than silently leaving them contradicting the corrected runtime. That
supersession is deliberate and named, not an oversight: plan 19's `codex
exec`-as-worker design was approved before this constraint was stated as
explicitly as it now has been, and continuing to build toward it would
re-entrench the very confusion this plan exists to end.

This plan does not redesign curriculum pedagogy, schema, or Arduino-kit
content, and does not touch the unit-state machine, checkpoint, or resume
logic P0/P3/P5 froze — only the model-access mechanism and the two policy
files that name it change.

## Architectural end state

1. **No production code path may require a billed API key.** Every model
   invocation in `runtime/` is either (a) the in-session Claude agent
   executing a prompt directly with no subprocess, or (b) a subprocess call
   to the `codex` CLI running under the user's ChatGPT Pro OAuth session. No
   code path may call `gemini`, any raw HTTP API, or read `GEMINI_API_KEY` /
   `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`.
2. **Authoring is Claude; judging is Codex — named as such everywhere.**
   `session_bridge.py`'s routing decision identifies the in-session Claude
   agent as the worker. `policy/routing/model_registry.v1.yaml` registers a
   Claude/Anthropic entry as the authoring model and reclassifies
   `gpt-5.6-sol`'s `allowed_for` roles to the QA/judge task classes it now
   actually serves. `policy/routes.v1.yaml`'s `worker` route no longer
   names `codex exec` as the authoring mechanism; a `qa_gate` route
   (or renamed `worker` route, whichever the schema in
   `schemas/routes.schema.v1.json` accommodates with the smaller diff)
   carries the real, proven `codex exec` command instead.
3. **The cross-family judge is real, never silently bypassed.** A missing
   or failed Codex call is a truthful `BLOCKED`, never the current
   `CROSS_FAMILY_BYPASS` → `ACCEPTED_PENDING_REVIEW` shortcut.
4. **Retired code is retired, not left dual-pathed.** `capability_cycle.py`,
   `gemini.py`, `resolve_gemini_settings.mjs`, and the Gemini-specific
   branches of `capabilities.py` and `finalize_evidence.py` are removed or
   fully repointed at the Codex mechanism, with `finalize_evidence.py`'s
   consumed receipt fields (`status`, `returncode`, `executed_model`, and an
   `events` list a tool-use predicate can scan) preserved by the new
   receipt shape, not just its file path.
5. **Plan 19's text is reconciled, not silently stale.** Every place in
   `plans/19_curriculum_factory_production_loop_closure/` that commits to
   `codex exec` as the *authoring* mechanism (P1-T04, P2-T18, P3's
   session-bridge disposition mandate) is named as explicitly superseded,
   with the exact replacement stated, alongside the smaller Gemini-specific
   corrections (P0's ground-truth table, P1's scope statement and P1-T08,
   P2's containment references).

## Exact work

### 0. Fail-fast prerequisite check

Before any file is touched, confirm and record:

- `codex --version` succeeds and `~/.codex/auth.json` has
  `"auth_mode": "chatgpt"` with a non-null token.
- A real bounded call — `codex exec --json --sandbox read-only
  --skip-git-repo-check --output-schema <schema.json> --output-last-message
  <last.json> "<bounded verdict prompt>"` — returns exit 0 and a
  schema-conformant `last.json`. (Verified achievable during this plan's own
  QA: a call in exactly this shape returned a clean
  `{"verdict":"PROVEN","reason":"..."}`.)
- No `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, or
  `OPENAI_API_KEY` is set in the shell environment or any rc file.

Stop here, without touching any other file, if `codex` is not authenticated
under the ChatGPT Pro subscription or cannot produce a schema-conformant
`--output-last-message` — the plan has no fallback mechanism to implement
instead, by design.

### 1. Retire the Gemini-subprocess mechanism

- Remove `runtime/capability_cycle.py`, `runtime/gemini.py`, and
  `runtime/resolve_gemini_settings.mjs`. Delete them outright unless a later
  step finds a piece of their logic (the receipt-shape contract in
  `validate_cross_family_proof`) worth preserving in the Codex replacement —
  if so, port that logic explicitly rather than importing the retired
  module.
- Remove `capabilities.py`'s import of `GeminiSettingsError`,
  `audit_stream_events`, `resolve_alias` from `.gemini`, and rewrite
  `validate_cross_family_proof` against the Codex receipt shape defined in
  step 3.
- Retire `tests/runtime/test_gemini.py` entirely and rewrite
  `tests/runtime/test_capabilities.py`'s Gemini-specific cases against the
  Codex receipt contract.
- Do not touch `outputs/runtime_task_v6/capability_cycle/gemini_proof/*` or
  any other pre-existing run root under `outputs/` — historical evidence,
  explicitly protected user work.

### 2. Correct the policy layer's worker assignment

- **Schema first.** `schemas/routes.schema.v1.json`'s `status` field is
  currently `"enum": ["UNPROVEN"]` — a route with `proof: null` can *only*
  mean "capability not yet proven, remove or fail," with no way to say "this
  route has no subprocess by design." Add a second enum value (e.g.
  `"IN_SESSION"`) and a matching `allOf` branch: `proof: null` +
  `status: "IN_SESSION"` is valid, requires `command: null`, and — unlike
  `UNPROVEN` — is not a capability gap the file's `preflight.on_failure`
  rule treats as removable-or-`META_SYSTEM_FAILURE`. This is a real,
  disclosed schema change, not a workaround; without it the corrected
  `worker` route cannot be expressed at all, and marking a *required* route
  `UNPROVEN` triggers exactly the failure this plan is trying to fix.
  `schemas/model_registry.schema.v1.json` needs no such change — `provider`,
  `reasoning_efforts`, `allowed_for` are already free-form; a Claude entry
  fits without a structural edit, but still needs its own `prose_patterns`
  entry (every model id requires one, per that file's own convention).
- In `policy/routing/model_registry.v1.yaml`: add a Claude/Anthropic model
  entry as the authoring model (role: in-session worker, `reasoning_efforts`
  and `supports_pro_mode` stated honestly as "not applicable — no dispatch
  command" rather than left implying a subprocess exists) plus its
  `prose_patterns` entry. Reclassify `gpt-5.6-sol`'s `allowed_for` from
  authoring roles (`final_acceptance`, `pedagogy_authority`) to the QA/judge
  roles it now serves, keeping `technical_authority`/`safety_critical` only
  where they describe judging, not authoring.
- In `policy/routes.v1.yaml`: change the `worker` route's `command`/`proof`
  to `null`/`null` with the new `status: "IN_SESSION"`, with `constraints`
  text stating plainly this is not an unproven capability — the worker is
  the in-session Claude agent, always present in the session that runs this
  factory, and there is nothing to probe. Add a new, **required** `qa_gate`
  route carrying the real, already-proven `codex exec` command and its
  existing dated transcript (the transcript remains valid evidence — only
  its *purpose* was mis-assigned, not its execution) — required because,
  unlike `imagegen`, there is no acceptable "remove and continue" for the
  cross-family judge; its absence must be `META_SYSTEM_FAILURE`, same as
  `worker`'s absence would be today. (Pre-checked for this plan: the only
  other `UNPROVEN`-sensitive code today is `capabilities.remove_unavailable_route`,
  which requires the literal string `"UNPROVEN"` to permit removal — an
  `IN_SESSION` route is never passed to that function, so adding the new
  enum value does not change that function's behavior.)

### 3. Build the Codex QA-gate mechanism

- Add a module (e.g. `runtime/codex_gate.py`) that shells out to
  `codex exec --json --sandbox read-only --skip-git-repo-check
  --output-schema <schema> --output-last-message <file>` (not `codex
  review` — verified during QA to expose no `--json`/`--output-schema`
  path and to be scoped to git diffs only, unsuitable for judging an
  arbitrary worker artifact) with a bounded prompt referencing the specific
  worker artifact and the check ids it must satisfy, inside the same
  per-call containment discipline P1 already established (isolated working
  directory, no undeclared reads/writes, no credential widening).
- Define and write the JSON Schema constraining the gate's
  `--output-last-message` shape (at minimum: `verdict` ∈
  `{PROVEN, FAILED}`, a `reason` string, and the check ids evaluated).
- Capture a receipt preserving exactly the fields
  `runtime/finalize_evidence.py:66-82` already consumes — `status`,
  `returncode`, `executed_model`, and an `events` list whose entries a
  "did this include a tool-use event" predicate can scan — either by
  translating Codex's real JSONL event shape (`thread.started`,
  `item.completed` with tool activity nested under `item.type`, `turn.
  completed`, confirmed live during QA) into that predicate-compatible
  shape, or by rewriting the predicate in `finalize_evidence.py` to match
  Codex's real shape directly. Either way, enumerate the exact `item.type`
  values a real `--json` call actually emits for tool/command activity
  (captured during this plan's own live calls) and match against that
  explicit set — never a substring guess like `"tool" in str(type)`, which
  risks a silent always-zero undercount against Codex's real, differently-
  named event types. Add one assertion exercising
  `finalize_evidence.main` end-to-end against a real captured Codex receipt
  so a field-shape mismatch here fails a test, not a future one-off run.
- The gate's verdict is binary for the acceptance decision (`PROVEN` /
  `FAILED`); the full Codex transcript is preserved in the receipt for
  audit.

### 4. Correct `session_bridge.py`

- Replace the hardcoded `MODEL_ID = "gpt-5.6-sol"` with an honest
  identification of the in-session Claude agent as the worker
  (`decided_model`/`executed_model`/`candidate_pool` describe Claude, not a
  Codex model id, per the registry entry added in step 2), and update
  `decision_rationale` to state plainly that the in-session Claude agent is
  the authorized worker under the user's Claude subscription.
- In `finalize()`, replace the `CROSS_FAMILY_BYPASS` branch: instead of
  recording `bypassed = True` and landing on `ACCEPTED_PENDING_REVIEW`,
  invoke the step-3 Codex gate against the produced `workers/domain.json`
  and `workers/lab.json`. Terminal-state logic becomes: `PROVEN` Codex
  receipt plus all other blocking checks passing → `ACCEPTED`; Codex
  receipt `FAILED` or unobtainable → `BLOCKED` with the Codex failure named
  in the claim — never a silent `ACCEPTED_PENDING_REVIEW`.
- Preserve every other check in `finalize()` exactly as-is (schema
  validation, domain verifier, receipt hashes, readability, PDF
  legibility/asset resolution, visual review); this step only replaces the
  bypass branch and the worker-identity fields.

### 5. Reconcile plan 19's text

Produce a reconciliation list (in this plan's result file, not a separate
document) naming every place in
`plans/19_curriculum_factory_production_loop_closure/` that assumed the
superseded design, and the exact correction each now needs:

- **P0**'s ground-truth table and "known active-contract contradictions"
  list, which describe `capability_cycle.py` as performing "a real Gemini
  probe" — retired, not merely reworded.
- **P1**'s scope statement (`capability_cycle.py` as "a real Gemini proof
  harness") and **P1-T04** ("one real call on the exact command in
  `policy/routes.v1.yaml`" against the *old* `worker` route) — P1-T04 must
  be retargeted at whichever route step 2 makes the authoring route (no
  command to prove; its "proof" is that it requires no subprocess at all)
  and a new test proving the `qa_gate` route instead. **P1-T08**'s
  cross-family judge requirement stays conceptually correct but its
  candidate judge is now named as Codex explicitly, not "a judge model from
  another family" left abstract.
- **P2**'s Hard Constraint #1 — *"one invocation interface serves the
  authoring, research, review and revision roles... never a separate code
  path with its own boundary rules"* — is explicitly superseded, not just
  reworded: this plan requires **two** invocation interfaces, named as such.
  The in-session Claude interface (authoring) must still satisfy P2's other
  four hard constraints in spirit — sealed request, staged filesystem,
  atomic admission, normalized failure classes — using
  `session_bridge.py`'s existing `worker_request.json` / authorized-paths /
  `workers/` staging pattern as the structural equivalent of a sealed
  request and staged output for a call that has no subprocess to sandbox.
  The `codex exec` interface (research, review, revision, QA-gate) keeps
  P2's subprocess-based sealed-request/staging/atomic-admission design
  exactly as written, now serving those four roles instead of all five.
  **P2-T18**'s "live canary... over the P1-frozen `worker` route" retargets
  to the `qa_gate` route; whichever test id covers Hard Constraint #1's
  single-interface requirement must be rewritten to assert the two-interface
  boundary instead (each interface internally uniform across its own roles,
  no interface silently reusing the other's boundary rules).
- **P3**'s session-bridge disposition mandate offers two options: *"migrate
  `runtime/session_bridge.py` into the controller path, or reduce it to a
  tested internal adapter with no production CLI entry point and no manual
  prepare/finalize handoff."* Plan 20 selects the **first**: the corrected
  `session_bridge.py` (step 4) supplies the authoring and finalize/accept
  logic *inside* P3's P0-frozen state-handler registry (`P3-T01`–`P3-T03`:
  exactly one production handler per frozen unit state) — it is not left as
  a standalone two-command CLI a human runs by hand. "In-session model
  writes files" in the corrected architecture means the Claude agent driving
  the relevant state handler produces the artifact as part of executing that
  handler, not a human copying output between manual `prepare`/`finalize`
  invocations; P3's "no manual prepare/finalize handoff" requirement is
  therefore satisfied, not waived. State this selection explicitly in P3's
  own text rather than leaving both dispositions open.

State plainly, for each, whether the phase's own test ids still apply
unchanged, need retargeting, or are retired outright. Do not edit the P0–P6
prompt files themselves as part of this plan — that is plan 19's own
territory; this plan only produces the correction list plan 19's next
execution must apply, with the supersession stated as deliberate and
user-authorized, not discovered as a defect.

## Verification sequence

1. **SOEM-T00 baseline capture** — confirm the fail-fast checks in step 0
   pass and record their exact output.
2. **Retirement completeness** — grep the repository (excluding `outputs/`,
   `.gemini/`, `plans/*/reviews/`, and this plan's own documents) for
   `gemini`/`Gemini` after step 1 and confirm no production `runtime/` or
   `policy/` file still references it.
3. **Policy consistency** — `schemas/routes.schema.v1.json`'s updated `status`
   enum accepts `IN_SESSION`; `policy/routes.v1.yaml` and
   `policy/routing/model_registry.v1.yaml` validate against their (updated)
   schemas after step 2's edits; no remaining text in either file describes
   `codex exec` as the authoring mechanism; `capabilities.remove_unavailable_route`'s
   existing tests still pass unchanged (confirming the new enum value didn't
   alter its `"UNPROVEN"`-specific behavior).
4. **Codex gate unit tests** — the rewritten `tests/runtime/test_capabilities.py`
   and a new test module for `runtime/codex_gate.py` pass, including a
   negative control (malformed/missing receipt is rejected).
5. **One real Codex proof call** — `codex_gate`'s live path is exercised
   once against a real bounded prompt (not mocked) and produces a `PROVEN`
   receipt with the exact `--output-schema`/`--output-last-message` flags
   named in step 3.
6. **finalize_evidence regression** — the new assertion from step 3 exercises
   `finalize_evidence.main` end-to-end against a real captured Codex receipt
   without a `KeyError` or shape mismatch.
7. **session_bridge regression** — the existing `prepare`/`finalize`
   integration tests (or a new one covering the corrected bypass branch)
   pass, including a case where the Codex gate fails and the unit correctly
   lands on `BLOCKED`, not `ACCEPTED_PENDING_REVIEW`.
8. **Full suite** — `python3 -m pytest tests/ -q` passes with no regressions
   outside what this plan intentionally changed.

## Acceptance criteria

- No file under `runtime/` or `policy/` references `gemini`/`Gemini`, a
  `GEMINI_API_KEY`, or any other billed API key mechanism.
- `policy/routing/model_registry.v1.yaml` registers a Claude/Anthropic
  authoring entry and no longer classifies `gpt-5.6-sol` under authoring
  roles it doesn't perform.
- `schemas/routes.schema.v1.json` has an `IN_SESSION` status value distinct
  from `UNPROVEN`, and `policy/routes.v1.yaml` validates against it: `worker`
  uses `IN_SESSION` (no command, no proof, not a capability gap) and a new
  required `qa_gate` route carries the real, proven `codex exec` transcript
  that `worker` carried before — `codex exec` is no longer named as the
  authoring mechanism anywhere in the file.
- The plan's result file states explicitly that P2's Hard Constraint #1 (one
  invocation interface for all four roles) is superseded by a named
  two-interface model, and that P3's session-bridge disposition is resolved
  as "migrate into the controller path" — neither reconciliation item is
  left as an open question.
- `codex --version` and one real `codex exec --json --output-schema
  --output-last-message` call succeed and are captured in a receipt
  preserving the exact fields `finalize_evidence.py` consumes.
- `session_bridge.py`'s routing decision identifies Claude as the worker,
  not `gpt-5.6-sol`.
- `session_bridge.finalize()` has no `CROSS_FAMILY_BYPASS`/
  `ACCEPTED_PENDING_REVIEW`-on-bypass branch; a missing or failed Codex
  judgment is `BLOCKED`, not silently accepted.
- The plan's result file lists, by exact file and line reference, every
  place in plan 19 (P0, P1/P1-T04/P1-T08, P2/P2-T18, P3) that named the
  superseded mechanism and what it now needs.
- `python3 -m pytest tests/ -q` passes.

## Stop conditions and result

Stop, without partial or worked-around progress, if: `codex` cannot be
authenticated under the ChatGPT Pro subscription at the fail-fast check; a
real `codex exec --output-schema/--output-last-message` call cannot be made
to return a structured, parseable verdict at all; the `schemas/routes.schema.v1.json`
change in step 2 (the new `IN_SESSION` status) cannot be made without
touching a constraint this plan did not anticipate (e.g. another consumer of
`status: "UNPROVEN"` elsewhere in the repo that the new value would silently
change the meaning of — grep for `UNPROVEN` beyond `routes.v1.yaml` before
implementing step 2 to rule this out); or reconciling plan 19's text would
require changing a frozen P0/P3/P5 invariant (unit-state ownership,
checkpoint contract, resume semantics) rather than only the model-access
mechanism, its two policy files, and P2's Hard Constraint #1 and P3's
session-bridge disposition selection, both of which this plan explicitly and
disclosedly supersedes rather than treating as untouchable.

Write
`plans/20_subscription_only_execution_model/subscription_only_execution_model.result.v1.md`
with: the baseline capture from step 0; every changed, added, and deleted
path; the plan-19 reconciliation list from step 5 in full; each
verification-sequence result with command and outcome; and any remaining
failure. Append the execution outcome to
`plans/20_subscription_only_execution_model/plans.log.md`.
