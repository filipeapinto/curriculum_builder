# Subscription-Only Model Execution Architecture Plan v1 — Focused QA

## Verdict

**CHANGES REQUIRED — 1 Critical, 2 High.** The plan's negative-control checks are
sound (subscription-only constraint is real: `codex --version` succeeds, `~/.codex/auth.json`
confirms `auth_mode: "chatgpt"` with a live token, and a real bounded `codex exec --json
--output-schema ... --output-last-message ...` call produces a genuinely parseable
structured verdict — this part of the plan is achievable exactly as described). But the
plan's central architectural claim — that `session_bridge.py`'s in-session,
no-subprocess authoring pattern is "the correct shape" needing only an honest model
name — is factually wrong against this repository's own already-approved policy and
plan-19 design, which define the worker itself as a real `codex exec` subprocess call
to a registered `gpt-5.6-sol` model. The plan's "Exact work" and reconciliation steps
never touch the files that state this (`policy/routes.v1.yaml`,
`policy/routing/model_registry.v1.yaml`, plan 19's P3 prompt), so executing this plan as
written would silently overwrite a sibling plan's live design decision rather than
reconcile it — precisely the failure mode the plan's own stop conditions exist to catch.

## Findings

### 1. Critical — Worker-is-Claude premise contradicts the already-approved (unexecuted) plan 19 P1/P2/P3 design, and the plan's own files are missing from scope

**Evidence.**
- `runtime/session_bridge.py:36` hardcodes `MODEL_ID = "gpt-5.6-sol"`, and the plan calls
  this a placeholder "belonging to a different family" that should be renamed to Claude.
- `policy/routes.v1.yaml`'s `worker` route (proven and dated 2026-07-29/2026-07-31, i.e.
  pre-existing, not hypothetical) declares: *"purpose: every bounded model call —
  authoring, review, acceptance"*, command `codex exec -s workspace-write
  --skip-git-repo-check -m <decided_model> -c model_reasoning_effort=<decided_effort>`,
  with a captured proof transcript of a real `codex exec -m gpt-5.6-luna` call.
- `policy/routing/model_registry.v1.yaml` formally registers `gpt-5.6-sol` as
  `provider: OpenAI`, `allowed_for: [safety_critical, technical_authority,
  final_acceptance, pedagogy_authority]` — exactly the `risk: safety_critical`,
  `task_class: final_acceptance` combination `session_bridge.py:130-139` already uses.
  `gpt-5.6-sol` is not an arbitrary wrong value; it is the policy-designated worker model
  for precisely this task class, reached via `codex exec`.
- Plan 19's **P1** prompt (`plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md`)
  requires, as test **P1-T04**, "One real call on the exact command in
  `policy/routes.v1.yaml` (`codex exec ... -m <decided_model> ...`)... the observed
  identity equals the decision's `decided_model`" — i.e. the *worker* route, not just the
  cross-family judge, must be a live `codex exec` subprocess call.
- Plan 19's **P2** prompt states: *"Today `policy/routes.v1.yaml` declares `worker` as
  `codex exec -s workspace-write ... -m <decided_model> ...`; P1 freezes what is actually
  proven."* Its acceptance test **P2-T18** is a mandatory "live canary... over the
  P1-frozen `worker` route," explicitly a real (never mocked) call.
- Plan 19's **P3** prompt is unambiguous that the current in-session/human-writes-files
  pattern is a stopgap, not architecture: *"`runtime/session_bridge.py` — the manual
  bridge this phase must migrate or reduce... deliberately returns `INTERRUPTED` so a
  human/in-session model writes `workers/domain.json` and `workers/lab.json` by
  hand."* P3's "Build" section requires *"Integration of session preparation, research,
  domain and lab production, visuals, rendering, reviews, acceptance, checkpoints and
  resume **through the P2 worker adapter for every model-produced artifact**"* and lists
  as a required deliverable: *"**Session-bridge disposition**: migrate
  `runtime/session_bridge.py` into the controller path, or reduce it to a tested internal
  adapter with no production CLI entry point and no manual prepare/finalize handoff.
  Record which, and why."*
- None of plan 19's P0, P1, P2 or P3 phases has executed (`plans/19_curriculum_factory_production_loop_closure/results/`
  does not exist), so this is a currently-live, approved (`status: approved` in the plan
  YAML) design commitment this plan would supersede, not stale text.
- Plan 20's own reconciliation step 5 lists only three items to correct — P0's ground-truth
  table wording, P1's "scope statement" (about `capability_cycle.py` as a Gemini proof
  harness) and P1-T08's judge requirement, and P2's containment references — and never
  mentions P3, the `worker` route in `policy/routes.v1.yaml`, or
  `policy/routing/model_registry.v1.yaml` anywhere in its "Exact work" or reconciliation
  sections (confirmed by grep of the plan document for "P3", "routes.v1.yaml", and
  "model_registry").

**Impact.** If implemented as written, the plan would permanently entrench
`session_bridge.py`'s manual, in-session-writes-files pattern as the production worker
mechanism — exactly the "manual bridge" plan 19's P3 is explicitly chartered to retire —
while never touching `policy/routes.v1.yaml`'s `worker` route or
`policy/routing/model_registry.v1.yaml`, which would continue to declare, with dated
"proof," that the worker is a `codex exec` subprocess dispatching to a registered OpenAI
model. The result is a repository left in an internally contradictory state: policy
documents assert one worker mechanism (`codex exec`), corrected runtime code implements
another (Claude in-session, no subprocess), and none of this plan's own verification
steps (a `gemini`/`Gemini` grep) would catch it, because the contradiction is not about
Gemini at all. Executing plan 19's P1/P2/P3 afterward — as approved and written — would
either silently re-implement the very mechanism this plan just retired, or fail outright
against a `worker` route this plan left pointing at a mechanism the codebase no longer
supports the way P1-T04/P2-T18 require it to be proven.

**Minimal required remediation.** Before this plan is authorized: either (a) explicitly
supersede plan 19's P1 `worker`-route and P2 `worker`-adapter design and P3's
session-bridge disposition mandate — naming this as a deliberate, disclosed scope
collision with a rewrite of the affected P1/P2/P3 prompt text, not a silent
reconciliation — or (b) drop the "worker = in-session Claude, no subprocess" architecture
and instead keep the worker as a real `codex exec -m <decided_model>` subprocess call
(satisfying invariant #1(b) as already written), reserving the "no subprocess" pattern
only for cases plan 19 does not already commit to a different mechanism. Either way, the
plan's "Exact work" section must add `policy/routes.v1.yaml`'s `worker` route and
`policy/routing/model_registry.v1.yaml` to its change scope, and step 5's reconciliation
list must include plan 19's P3 prompt.

### 2. High — `codex exec` vs `codex review` are not interchangeable, and the plan does not pick one

**Evidence.** Step 2 says the new module should shell out to *"`codex exec` (or `codex
review`, whichever subcommand best matches a bounded 'judge this artifact against these
criteria' call)."* Live inspection of the installed CLI (`codex-cli 0.147.0`,
`~/.codex/auth.json` `auth_mode: "chatgpt"` confirmed) shows:
- `codex exec --help` exposes `--json` (JSONL event stream to stdout),
  `--output-schema <FILE>` (a JSON Schema constraining the final response shape), and
  `-o/--output-last-message <FILE>` (writes just the final structured message). A real
  bounded call (`codex exec --json --sandbox read-only --skip-git-repo-check
  --output-schema schema.json --output-last-message last.json "Reply with verdict
  PROVEN and a one-sentence reason..."`) returned exit 0 and a clean, schema-conformant
  `last.json`: `{"verdict":"PROVEN","reason":"..."}` — genuinely parseable structured
  output.
- `codex review --help` exposes no `--json`, no `--output-schema`, and no
  `--output-last-message`. Its only inputs are `--uncommitted`, `--base <BRANCH>`, and
  `--commit <SHA>` — it is scoped to reviewing a git diff against the working tree, a base
  branch, or a specific commit, not to judging an arbitrary artifact (e.g.
  `workers/domain.json`/`workers/lab.json`) against a set of check ids.

**Impact.** `codex review` cannot produce the structured, parseable `PROVEN`/`FAILED`
verdict `validate_cross_family_proof`'s replacement is required to check (per the plan's
own step 2 and acceptance criteria), and it is not designed to judge non-diff content at
all. An implementer following the plan's literal wording ("whichever subcommand best
matches") could reasonably build the gate around `codex review`, discover only at the
"one real Codex proof call" verification step that it cannot express the required
judgment, and hit the plan's own stop condition ("a real `codex exec`/`codex review` call
cannot be made to return a structured, parseable verdict at all") — a false negative,
since `codex exec` demonstrably can, right now, with flags already in the installed
binary.

**Minimal required remediation.** State in step 2 that the gate must use `codex exec
--json --output-schema <schema> --output-last-message <file>` specifically, not `codex
review`, and name the output-schema contract (the JSON Schema constraining
`verdict`/reasoning fields) the gate writes and depends on.

### 3. High — `finalize_evidence.py`'s Gemini-shaped field assumptions are described as a path change, not the schema rewrite they require, with no test to catch a mismatch

**Evidence.** `runtime/finalize_evidence.py:66-82` reads
`capability_cycle/gemini_proof/live_proof_receipt.json` and directly indexes
Gemini-specific receipt shape: `proof["status"]`, `proof["returncode"]`,
`proof["executed_model"]`, and `sum("tool" in str(event.get("type", "")).lower() for
event in proof["events"])` — a flat `{"type": "init"/"tool_call"/...}` event shape that
`runtime/gemini.py`'s `audit_stream_events` also assumes. The plan's step 1 describes the
fix only as: *"Update `runtime/finalize_evidence.py`'s references to
`capability_cycle/gemini_proof/live_proof_receipt.json` to point at the Codex gate's
receipt path instead."* A real bounded `codex exec --json` call in this review showed
Codex's actual event stream is structurally different — top-level `type` values are
`thread.started`/`item.completed`/`turn.started`/`turn.completed`, with tool/command
activity nested under `item.type` inside `item.completed`, not a bare `tool_call` type —
so the `"tool" in str(event.get("type",""))` substring check would silently
undercount (or the field access would need a different shape entirely) if the Codex
receipt's `events` field is populated with raw Codex JSONL rather than translated into
the old shape. No test file references `finalize_evidence` at all (confirmed by repo-wide
grep of `tests/`), so nothing in the plan's verification sequence would catch a
field-shape mismatch here.

**Impact.** `finalize_evidence.py` is not on any currently-tested or CI-gated path (its
only callers are prior plans' one-off closure invocations), which bounds the blast
radius, but the plan explicitly claims to have handled this file in its change scope and
acceptance criteria ("No file under `runtime/` or `policy/` references
`gemini`/`Gemini`") without specifying the field contract the Codex receipt must actually
carry for this consumer, risking a silent `KeyError` or miscomputed audit field the next
time the script runs.

**Minimal required remediation.** Either state explicitly in step 2 that the new Codex
receipt must preserve exactly the field names and shapes `finalize_evidence.py` consumes
(`status`, `returncode`, `executed_model`, and an `events` list whose entries can be
tested with the same "did this include a tool-use event" predicate), or add one assertion
to the plan's verification sequence that exercises `finalize_evidence.main` end-to-end
against a real Codex receipt.
