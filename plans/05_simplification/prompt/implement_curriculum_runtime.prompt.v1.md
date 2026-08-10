# Implement the Missing Runtime and Complete Simplification Phase 6 — Prompt v1

## Objective

Implement the missing reusable curriculum runtime, then use it to generate, verify,
review, render, rasterize, and inspect Arduino Kit unit L01 end-to-end.

## Goal, acceptance test, and execution loop

### Goal

Create the missing reusable runtime/controller required to execute the active curriculum
meta-prompt as a real, deterministic, resumable workflow.

### Acceptance test — Arduino Lab 1 (L01)

**The test of the runtime is the complete Arduino Kit Lab 1 (`L01`) run.** The runtime
is not considered implemented merely because its unit tests pass or its interfaces
exist. It passes this task only when it uses the active Arduino curriculum manifest to
generate L01, execute every applicable validation and review gate, render the PDF,
rasterize and inspect every page, survive a forced interrupt/resume test, and reach the
Phase 6 acceptance conditions below. L01 is the end-to-end acceptance test and proof of
the implementation.

### Loop

1. Implement the smallest missing runtime capability needed for the L01 run.
2. Run or resume L01 through the controller.
3. Evaluate L01 and the runtime against all applicable deterministic checks, domain
   checks, model-routing requirements, judge requirements, render checks, and Phase 6
   acceptance conditions.
4. Diagnose each failure without weakening any contract or gate.
5. Repair the runtime or only the failed L01 artifact, according to ownership.
6. Rerun only the affected checks, then continue or resume the L01 workflow.
7. Repeat steps 2–6 until L01 is `ACCEPTED` or a declared limit produces an honestly
   evidenced terminal condition.

This is an implementation-and-execution task. Do not stop after analysis, planning, or
another specification. The missing controller is the work. After the controller exists,
L01 is the proof.

Do not ask the user ordinary implementation questions. Make conservative decisions from
the ranked repository contracts, record assumptions, and keep working until L01 reaches
a genuine terminal state. Diagnose and fix implementation failures within the declared
limits. Never weaken a schema, fixture, gate, verifier, evidence rule, or acceptance
criterion to obtain a pass.

## Repository and run inputs

```text
ENGINE       = derive from this repository; never hardcode the user's absolute path
PROMPT       = meta_prompt/curriculum.prompt.v1.md
CURRICULUM   = curricula/arduino_kit
MANIFEST     = curricula/arduino_kit/arduino_kit_curriculum.v5.yaml
LAB_ID       = L01
OUTPUT_ROOT  = outputs/arduino_kit_phase6_v1
```

`OUTPUT_ROOT` is intentionally supplied here. Confirm it does not exist before creating
it. If it exists, obey `PRECONDITION-OUTPUT-ROOT-EXISTS`: stop before writing and report
the next free version; never overwrite, merge, delete, or auto-increment.

Preserve `outputs/arduino_kit_run_v1` unchanged. It is evidence from an earlier mistaken
attempt and is not the Phase 6 run root. Preserve every pre-existing user change in the
worktree. Never reset, stash, discard, overwrite, or commit unrelated changes.

## Read first, in this order

1. `plans/simplification/simplification.handoff.v1.md`, especially §§6–8.
2. `plans/simplification/plan/simplification.phase6.result.v1.md`.
3. `plans/simplification/plan/simplification.plan.v3.md`, especially §§4, 6–8.
4. `meta_prompt/curriculum.prompt.v1.md`, completely.
5. Every active manifest, schema, companion, policy, routing file, and curriculum input
   that the active prompt ranks and authorizes.
6. `plans/legacy_v3/run_curriculum.v3.py` and the other two files the active prompt
   explicitly authorizes under `plans/legacy_v3/`, citing useful inherited behavior by
   path and line. Do not revive their architecture blindly.

Do not read `meta_prompt/deprecated/` or other deprecated contracts. The active prompt
explicitly excludes them. Documentation and plans orient the work; active policy,
schemas, the curriculum verifier, and the active prompt decide it.

## Correct interpretation of the unfinished work

Phases 0–5 simplified and generalized the contract. They did not implement the runtime.
Phase 6 remains unfinished. The absence of a controller is not a reason to halt this
task; implementing the smallest deterministic controller and append-only v2 logger is
the first required deliverable.

The handoff's binding next action is:

> Implement the smallest deterministic controller and append-only v2 logger that can
> enforce and record one L01 run, including live route preflights, then rerun stage B
> from condition 1.

Do exactly that. Do not attempt all 35 units. Do not attempt Phase 7. Do not author
another plan explaining why execution is unavailable.

## Deliverable 1 — reusable deterministic runtime

Create a curriculum-neutral runtime in a new active engine directory such as `runtime/`.
Use `runtime/run_curriculum.py` as the CLI entry point unless an existing active
convention discovered in the repository requires a better generic location. The runtime
must not contain Arduino-, electronics-, kit-, or L01-specific logic. Curriculum-owned
behavior comes from the supplied manifest, schemas, configuration, checks, and verifier.

Implement the minimum CLI surface required by `policy/controller.v1.yaml`:

- `--curriculum`
- `--lab-id`
- `--all`
- `--output-root`
- `--resume`
- `--preflight`
- `--test-static`
- `--test-simulated-all`
- `--test-live-capabilities`
- `--test-golden-l01`
- every numeric limit flag declared by `policy/limits.v1.yaml`
- `--model` only as a fallback after the selector; it must never bypass selection

For this task, fully execute `--lab-id L01`. Other declared modes may be implemented and
tested at the smallest honest level needed to satisfy the controller contract; do not
pretend that `--all` generated units it did not generate.

The runtime must implement:

1. Manifest validation before reading manifest values.
2. Output-root precondition and strict write boundary.
3. Companion resolution.
4. Domain-verifier declaration and fixture execution before generation.
5. Manifest-derived unit order and count; no hardcoded count or domain words.
6. The controller states and legal transitions in `policy/controller.v1.yaml` needed by
   an L01 run.
7. Atomic checkpoints after every executed state, with input/output hashes, attempt,
   elapsed time, worker identity, executed model/effort where applicable, and next state.
8. Resume from the first missing or invalid checkpoint without rebuilding valid accepted
   work.
9. Limits, retry policy, repeat-failure detection, targeted revision, and honest terminal
   states.
10. Deterministic merge, validation, hashing, rendering, aggregation, audits, and
    acceptance. No model may perform or decide those operations.

### Logger requirements

Implement and prove the append-only v2 logger before any other run artifact:

- Durable append-only records conforming to
  `schemas/execution_log.schema.v2.json` when parsed.
- Monotonic ids allocated by construction, never by counting text in the log.
- Explicit `closes` references for completions and failures.
- Exclusive locking and concurrent-append safety.
- Zero unpaired starts at every release/terminal audit.
- Coverage of every checkpoint and state transition.
- An operation without its start record is refused.
- A model call requires a valid `decision_id` before invocation; an unrecorded call is a
  fatal runtime error, not a later schema observation.

Add deterministic tests for every `LOG-*` check, including negative fixtures. The
run-local logger created under `outputs/arduino_kit_run_v1` may be inspected as evidence,
but do not copy it uncritically and do not modify that run root.

### Routing and model-call enforcement

Implement the selector and enforce all `SEL-*` obligations:

- Classify each model task from `policy/routing/task_taxonomy.v2.yaml`.
- Apply `policy/routing/routing_policy.v1.yaml` and the active model registry.
- Emit and schema-validate `routing_decision.schema.v2.json` before every model call.
- Record `decided_model` and `executed_model`; refuse a mismatch.
- Pass both model and effort explicitly through the worker invocation.
- Never use a model for deterministic work.
- Respect limits and bounded escalation.
- Workers receive only their role, stable check ids, selected unit data, accepted
  prerequisite artifacts, authorized input/output paths, and one output schema.

Add selector/controller tests proving bypass refusal, unrecorded-call failure, bounded
prompts, deterministic-work exclusion, decision validity, and decided/executed equality.

## Deliverable 2 — prove every required live route

Before L01 generation, make one real minimal preflight call for every route the run will
use. Help output, installed binaries, and configuration files are not proof.

At minimum prove and record:

1. The Codex worker route with the selected model and effort explicitly passed.
2. A primary-source retrieval route that fetches official material by exact identifier,
   stores the retrieved bytes under the run root, and records access date, scope, URL or
   document identifier, SHA-256, HTTP/result status, and the claim(s) it supports.
3. The PDF route exactly as declared: Pandoc with Typst and an explicit font.
4. The Poppler rasterizer route at 200 dpi over every shipped PDF page.
5. A real Gemini CLI invocation for the required cross-family judge. Add a generic,
   schema-valid route and real proof to `policy/routes.v1.yaml` if the active contracts
   require the route to be declared there. Do not call Gemini before its route is proven
   and logged.
6. ImageGen only if L01 uses a generated nontechnical support visual. Prove the callable
   route before use and record the receipt. Never use a generated image for exact kit
   identity, wiring, positions, orientation, values, geometry, or safety authority.

Update active route policy and schemas only where necessary to represent genuinely
executed capabilities. Add tests/fixtures for the new generic routes. Do not encode a
curriculum name or domain term in engine policy.

## Deliverable 3 — generate and accept L01

Run the newly implemented runtime against `L01` and `OUTPUT_ROOT`. The model writes;
controller code decides.

### Grounding and domain data

- Retrieve every primary source during this run; never rely on memory or a URL alone.
- Store source bytes and resolving hashes under the output root.
- Record exact identifier, access date, scope, measurement/observation condition, and
  supported domain pointer beside each value.
- Start from curriculum-owned, validated data such as
  `curricula/arduino_kit/l01_unpowered_power_path.json` only after verifying its schema,
  provenance, and compatibility with the active manifest/calibration.
- Compose the L01 domain block, validate it against the curriculum domain schema, and
  execute `curricula/arduino_kit/verify_domain.py` against it.
- Re-execute every declared verifier fixture in the same run.

### Unit generation

- Generate all seven required blocks in `schemas/lab.schema.v4.json`.
- The domain block is the sole parent of every rendered technical fact.
- Every rendered fact records a resolving domain pointer and exactly matches its source
  value.
- Generate the child text, adult guide, tables, troubleshooting, evidence card, and
  visuals from the same domain data.
- Follow the active calibration, 5E order, Predict–Observe–Explain ordering, reading
  band, Bloom rules, vocabulary caps, safety baseline, and L01 manifest content.
- L01 remains fully unpowered. Do not invent polarity, current, powered measurements,
  or physical-kit signoff that L01 cannot establish.

### Visuals

- Use the verified official kit photograph for exact identification only when its bytes
  and hash resolve.
- Produce the power-path/orientation map deterministically from the domain data.
- Produce the evidence card deterministically.
- If a photorealistic safe-context visual is generated, keep it non-authoritative and
  free of exact connection facts, then record a resolving generation receipt.
- Every visual receipt must hash the exact shipped asset.

### Checks and review

Run, record, and enforce every applicable declared automated check directly against the
generated L01 artifact, including:

- Engine schema plus curriculum domain schema.
- Curriculum domain verifier.
- `LAB-BLOOM-DEPTH` and `LAB-POE-ORDER`.
- `TEXT-READABILITY-BAND`.
- `TEXT-BLOOM-VERBS` as a flag that never blocks.
- `DOC-DERIVED-FROM-SOURCE`.
- `RECEIPT-HASH-RESOLVES`.
- Curriculum-owned L01/domain checks.
- `REV-ISOLATED`.

Run exactly one judge per pass using the proven Gemini cross-family route. The judge
must receive an explicit rubric and randomized presentation order, must not see another
verdict, and must write only its authorized verdict schema/path. The controller—not the
judge—aggregates the result and decides the transition.

Revise only failed artifacts and rerun only affected checks. Continue within the
declared revision and convergence limits. A tool, model, render, schema, or image failure
is `SYSTEM_FAILURE`, never a safety `BLOCKED` result. `BLOCKED` is legal only for a named
safety-critical fact that remains unavailable after the required primary-source search.

### Render and visual QA

- Assemble the L01 draft document.
- Render the shipped PDF with the proven Pandoc/Typst command.
- Rasterize the shipped PDF—not a re-rendered substitute—at 200 dpi with Poppler.
- Inspect every page visually.
- Enforce page count, nonblank pages, effective body text at least 9 pt, no clipping or
  overlap, readable tables/labels, correct image-text placement, and receipt-to-shipped-
  asset resolution.
- Force one interrupt after a valid checkpoint, resume, and prove before/after hashes of
  preserved work.

## Supporting runtime tests and regression protection

These tests support the implementation but do not replace the L01 acceptance test. Add
focused unit and integration tests for the new runtime. Exercise at least:

- Fresh-run output-root refusal.
- Manifest/schema failure before value consumption.
- Missing/unproven verifier refusal.
- Logger append-only, monotonic, pairing, concurrency, coverage, and orphan refusal.
- Selector decision validation, bypass refusal, unrecorded-call fatality, and
  decided/executed equality.
- Legal/illegal state transitions.
- Atomic checkpoint/resume and hash mismatch refusal.
- Retry and convergence limits.
- Strict read/write authorization.
- L01 domain validation and derivation.
- PDF and receipt checks.
- Clean simulated acceptance, targeted revision, malformed output, transient failure,
  repeated failure, legal block, system failure, interrupt, and resume.

Run the existing repository suites and the new runtime tests. The handoff requires:

```text
./tests/run_gates.sh 4
./tests/run_gates.sh 5
python3 tests/check_meta_prompt.py
```

Record the pre-existing dirty-worktree baseline before editing. Do not clean it by
discarding user work. If `FR-P0-CLEAN` alone fails because of changes that predate this
task, report that fact separately and run the directly affected gate/test commands; do
not misreport a dirty-tree harness run as a full pass. Never alter a gate to accommodate
the dirty tree.

## Phase 6 acceptance

Phase 6 is accepted only when all of the following are true and evidenced:

1. The deterministic controller proves authorized reads/writes and an append-only,
   paired execution log.
2. L01 exists as genuinely model-generated content, not a hand-authored fixture.
3. L01 validates against the engine and domain schemas.
4. The domain verifier and all of its declared fixtures execute successfully in the
   same run.
5. Every applicable generic and curriculum check executes against L01; fixture-only or
   zero-unit coverage is never reported as generated-unit coverage.
6. Every domain value resolves to primary-source bytes fetched during the run.
7. Every rendered fact derives mechanically from its one domain parent.
8. Exactly one proven cross-family Gemini judge runs per pass with rubric, randomized
   order, and structural isolation.
9. The PDF is rendered, every shipped page is rasterized and inspected, and every
   visual receipt resolves to an asset actually shipped.
10. Forced interrupt/resume preserves valid work and hashes.
11. L01 reaches `ACCEPTED` by controller decision with zero failed blocking checks.
12. The output is described only as a draft pending downstream human review.

If acceptance is not earned after exhausting safe fixes and declared limits, preserve
the resumable checkpoint and report the exact terminal condition. Do not call an
unfinished unit accepted.

## Final response

Lead with the outcome. Report:

- Runtime files created or changed.
- L01 terminal state and artifact paths.
- Source, domain, routing, model, effort, and cross-family review evidence.
- Every gate/check result, clearly separating repository fixtures from generated-L01
  coverage.
- PDF path, page count, raster paths, and visual-inspection result.
- Interrupt/resume hashes and outcome.
- Execution-log path, SHA-256, start/completion/failure totals, unclosed starts, and
  duplicate closes.
- Resource and revision totals.
- Write-scope/drift audit and pre-existing dirty-tree caveat.
- Any unresolved failures and the safest restart command.

Never claim the curriculum is complete. This task implements the missing runtime and
proves it with L01 only. The remaining 34 Arduino units and simplification Phase 7 are
explicitly outside this task.
