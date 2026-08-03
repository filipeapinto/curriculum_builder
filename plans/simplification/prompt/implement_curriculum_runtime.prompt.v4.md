# Implement the Missing Curriculum Runtime — Prompt v4

## Objective

Implement the missing reusable curriculum runtime, then use it to generate, verify,
review, render, rasterize, and inspect Arduino Kit unit L01 end-to-end.

## Goal, acceptance test, and bounded development loop

### Goal

Create the missing reusable runtime/controller required to execute the active curriculum
meta-prompt as a real, deterministic, resumable workflow. The runtime—not a hand-built
lab artifact—is the product of this task.

### Acceptance test — Arduino Lab 1 (L01)

Use one complete Arduino Kit Lab 1 (`L01`) execution as the end-to-end acceptance test
of the runtime. Unit tests, interfaces, fixtures, partial stages, and hand-authored
artifacts do not prove completion. The runtime passes only when a clean L01 attempt
generates the lab from the active manifest, executes every applicable validation and
review gate, renders the PDF, rasterizes and inspects every page, survives a forced
interrupt/resume test within that attempt, and meets every runtime acceptance criterion
below.

### Bounded development loop

1. Implement and test the smallest reusable runtime capable of attempting L01.
2. Audit the declared live prerequisites without changing their contracts before
   starting a costly L01 attempt.
3. Start L01 from a new, empty output root outside `ENGINE` and preserve the attempt as
   evidence.
4. If the attempt fails because of the reusable implementation, diagnose the runtime
   defect, improve the runtime, and run its focused deterministic and simulated tests.
5. Keep the failed L01 output unchanged. If budget and convergence conditions still
   permit another attempt, select a new empty external output root and rerun L01 from
   the beginning. Never hand-edit or reuse a failed L01 artifact to manufacture a pass.
6. End successfully when one clean L01 attempt satisfies every acceptance criterion.
7. End honestly with the applicable bounded status when a prerequisite, resource,
   attempt, or convergence limit is reached. Never convert a bounded incomplete result
   into acceptance.

The controller's own retries, targeted revisions, checkpoints, and resume behavior
operate inside a single attempt and are themselves under test. They do not reset or
expand the outer task budget. After any implementation change, the proof must be a new
clean L01 run.

This is an implementation-and-execution task. Do not stop after analysis, planning, or
another specification. The missing controller is the work. After the controller exists,
L01 is the proof.

Do not ask the user ordinary implementation questions. Make conservative decisions from
the ranked repository contracts and record assumptions. Continue while the task-level
budget and convergence rules permit; otherwise preserve evidence and return the exact
bounded status. Never weaken a schema, fixture, gate, verifier, evidence rule, or
acceptance criterion to obtain a pass.

## Repository and run inputs

```text
ENGINE       = derive from this repository; never hardcode the user's absolute path
PROMPT       = meta_prompt/curriculum.prompt.v1.md
CURRICULUM   = curricula/arduino_kit
MANIFEST     = curricula/arduino_kit/arduino_kit_curriculum.v5.yaml
LAB_ID       = L01
EVIDENCE_PARENT      = derive as parent(ENGINE)/curriculum_builder_runs
TASK_ROOT            = EVIDENCE_PARENT/runtime_task_v4
TASK_LEDGER          = TASK_ROOT/task_ledger.json
OUTPUT_ROOT_TEMPLATE = TASK_ROOT/attempt_v<N>
FIRST_OUTPUT_ROOT    = TASK_ROOT/attempt_v1
```

Canonicalize `ENGINE`, `EVIDENCE_PARENT`, and each proposed `OUTPUT_ROOT` before writing.
Require `EVIDENCE_PARENT` to be a durable, writable sibling outside `ENGINE`. Never use
`/tmp`, `/private/tmp`, `$TMPDIR`, a cache directory, or the repository's `outputs/`
directory for task evidence. If durable external write access cannot be established,
return `DURABLE_EVIDENCE_ROOT_UNAVAILABLE` before repository edits or live calls; do not
fall back to volatile storage.

The invoking sandbox must authorize `EVIDENCE_PARENT` as an additional writable root
(for the Codex CLI, use its scoped `--add-dir` mechanism). This grants only the durable
evidence sibling; it does not widen writes elsewhere.

Reject any output root equal to or nested beneath `ENGINE`. Before each outer-loop attempt, the
implementing agent explicitly selects the first confirmed nonexistent version of
`OUTPUT_ROOT_TEMPLATE` and passes that exact path to the runtime. This selection occurs
between attempts and is not runtime auto-increment. The runtime must refuse an existing
supplied root under `PRECONDITION-OUTPUT-ROOT-EXISTS`; it must never overwrite, merge,
delete, or choose another root.

Preserve `outputs/arduino_kit_run_v1` and every other existing run unchanged. Preserve
every pre-existing user change in the worktree. Never reset, stash, discard, overwrite,
or commit unrelated changes. Never place new acceptance evidence under the repository's
`outputs/` directory.

## Development writes versus run writes

There are two non-overlapping intervals:

1. **Development interval.** No curriculum run is active. Writes inside `ENGINE` are
   allowed only for the reusable runtime and its focused tests. Live capability
   contracts are read-only in this task. Record the dirty-worktree baseline first and
   never touch unrelated paths.
2. **Acceptance-run interval.** Freeze and hash all active inputs and runtime code before
   the attempt starts. From startup through the final audit, treat all of `ENGINE` and
   `CURRICULUM` as immutable and write only beneath the external `OUTPUT_ROOT`. Launch
   model workers with `OUTPUT_ROOT` as their working directory and expose only copied,
   hashed, authorized inputs plus their authorized output paths. No development edit may
   occur while an attempt is active.

The active meta-prompt governs the acceptance-run interval. It does not forbid creating
the missing runtime during the preceding development interval. Any implementation change
ends the current attempt; preserve that attempt and start the next one from a clean
external root after tests pass.

## Task-level resource envelope

These limits cover the complete outer development task, not each individual L01 run:

- Maximum clean live L01 attempts: **3**.
- Maximum total wall time after implementation begins: **36,000 seconds**.
- Maximum live model calls across preflights, generation, revisions, and judges: **60**.
- Maximum cross-family CLI calls: **6**.
- Maximum primary-source network fetches: **30**.
- Maximum generated images: **0**; L01 must use deterministic or verified official
  visuals.
- Maximum aggregate new acceptance-output storage: **750 MB**.
- Maximum outer implementation-correction cycles: the smaller of **6** and the active
  `max_meta_revision_cycles` value.

Maintain cumulative counters in `TASK_LEDGER` only between attempts. Before an attempt,
copy its starting counters into that attempt's `OUTPUT_ROOT`; during the attempt update
only the run-local copy. After the attempt reaches a terminal state, freeze it and update
`TASK_LEDGER` during the development interval. Check the envelope before every costly
action and stop before exceeding it. The active per-lab, per-state, retry, and
convergence limits remain binding inside each attempt and may only make this envelope
stricter.

## Read first, in this order

1. `plans/simplification/simplification.handoff.v1.md`, especially the missing-
   runtime diagnosis and binding next action.
2. `plans/simplification/plan/simplification.plan.v3.md`, for the intended contracts
   and acceptance behavior; do not organize the implementation around plan phase labels.
3. `meta_prompt/curriculum.prompt.v1.md`, completely.
4. Every active manifest, schema, companion, policy, routing file, and curriculum input
   that the active prompt ranks and authorizes.
5. `plans/legacy_v3/run_curriculum.v3.py` and the other two files the active prompt
   explicitly authorizes under `plans/legacy_v3/`, citing useful inherited behavior by
   path and line. Do not revive their architecture blindly.

Do not read `meta_prompt/deprecated/` or other deprecated contracts. The active prompt
explicitly excludes them. Documentation and plans orient the work; active policy,
schemas, the curriculum verifier, and the active prompt decide it.

## Missing functionality to implement

The repository has curriculum contracts, policies, schemas, fixtures, and plans, but it
does not yet have the reusable execution runtime that turns those contracts into a real
run. The missing functionality is a deterministic curriculum controller plus an
append-only v2 execution logger capable of enforcing and recording one complete L01
attempt, including live route preflights.

The controller, logger, and selector are three internal modules of one runtime
deliverable, not independent frameworks or services. Implement only the interfaces and
behavior exercised by the declared controller contract, supporting tests, and L01.

The absence of that runtime is the implementation task, not a reason to halt or write
another plan. Build it, prove it with the clean L01 development loop, and do not attempt
the remaining Arduino units.

During development, the complete repository write allowlist is `runtime/**` and
`tests/runtime/**`. Do not edit route or routing policy, the model registry, the
meta-prompt, curriculum files, controller policy, limits, check inventory, schemas, or
unrelated tests. If live prerequisites are missing, return the bounded live-blocked
outcome after completing the runtime's deterministic and simulated tests. Do not expand
scope to repair capability contracts.

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

`--test-golden-l01` is a controller-mandated compatibility spelling, not permission for
curriculum-specific engine logic. Implement it as a thin CLI alias for the generic
golden-unit test using the first unit id read from the validated manifest. The alias
must enter the same `--lab-id` pipeline as every other unit. It may not own a separate
handler, schema, prompt, check, fixture, domain value, or generation branch. The active
curriculum schema currently makes that first id `L01`; the manifest remains the source
of the value.

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

## Deliverable 2 — read-only live-capability readiness

Capability policy is an input to this task, not an implementation target. Hash the
active route manifest, model registry, and routing policy before and after development
and require byte-for-byte equality. Do not add, remove, weaken, reinterpret, or prove
away a route so that `ROUTE-PROVEN` passes.

Before the first live L01 attempt, perform this bounded readiness audit:

1. Validate the existing route and routing manifests against their existing schemas.
2. Treat `RESEARCH` exactly as the active meta-prompt defines it: an accepted, recorded
   divergence used for primary-source reads, not a route in `policy/routes.v1.yaml`.
   Do not add a research route and do not claim the external capability set is fully
   proven while that divergence remains.
3. Evaluate `ROUTE-PROVEN` over the route manifest exactly as found. An unproven
   declared route remains a failed prerequisite even if L01 would not use it. Do not
   delete ImageGen, waive the route, or reduce the quantified route set.
4. Require the cross-family judge to have a declared route, an eligible registered
   model, and a genuinely proven invocation before any L01 generation call. An installed
   Gemini binary or help output is not proof, and this task must not add the missing
   declarations.
5. If any structural prerequisite is absent or unproven, record failure id
   `LIVE_PREREQUISITE_BLOCKED`, finish the runtime's deterministic and simulated tests,
   return `RUNTIME_CORE_VERIFIED_LIVE_BLOCKED` if those tests pass, and make no live L01,
   Gemini, ImageGen, or primary-source calls.
6. Only if every structural prerequisite already passes unchanged, make one real
   minimal preflight call on every declared route before each L01 attempt. Count those
   calls against the task envelope. Help output, installation, and configuration are
   never proof.

This audit has no correction loop. Capability-contract repair belongs to a separate,
explicitly authorized task.

## Deliverable 3 — execute the clean L01 acceptance attempt

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

Run exactly one judge per pass using the proven, declared cross-family route. The judge
must receive an explicit rubric and randomized presentation order, must not see another
verdict, and must write only its authorized verdict schema/path. The controller—not the
judge—aggregates the result and decides the transition.

Inside one attempt, the controller may revise only failed artifacts and rerun only
affected checks according to its generic, declared revision and convergence policy. The
implementing agent must never hand-edit generated L01 artifacts. A tool, model, render,
schema, or image failure is `SYSTEM_FAILURE`, never a safety `BLOCKED` result.
`BLOCKED` is legal only for a named safety-critical fact that remains unavailable after
the required primary-source search.

When an attempt exposes a runtime defect or missing capability, preserve that entire
attempt unchanged. If the task-level budget and convergence rules permit, fix the
reusable implementation, rerun the focused tests, and start L01 again using the next
empty output-root version. No generated artifact or checkpoint from the failed attempt
may enter the new acceptance attempt.

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

## Bounded outcomes

Return exactly one of these task outcomes:

- `ACCEPTED`: supporting runtime tests pass and one clean L01 attempt satisfies every
  runtime acceptance criterion below.
- `DURABLE_EVIDENCE_ROOT_UNAVAILABLE`: the derived durable sibling evidence directory
  cannot be made writable. Return before repository edits or live calls; never substitute
  volatile storage.
- `RUNTIME_CORE_VERIFIED_LIVE_BLOCKED`: the runtime's deterministic and simulated tests
  pass, but the read-only capability audit finds missing or unproven prerequisites. Do
  not start L01 and do not call the runtime accepted.
- `L01_ACCEPTANCE_LIMIT_REACHED`: live prerequisites pass and at least one clean L01
  attempt executes, but none passes before the task-level attempt, resource, or
  convergence boundary. Preserve every attempt and do not call the runtime accepted.
- `RUNTIME_IMPLEMENTATION_INCOMPLETE`: the reusable runtime or its supporting tests do
  not pass before the task-level implementation or resource boundary.

These bounded outcomes preserve useful implementation and evidence without granting
partial acceptance. `DURABLE_EVIDENCE_ROOT_UNAVAILABLE` is selected before development;
every outcome after development begins requires a durable task ledger. Only `ACCEPTED`
proves the runtime end-to-end.

## Runtime acceptance criteria

The curriculum runtime is accepted only when one clean L01 attempt satisfies all of the
following conditions with recorded evidence:

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
8. Exactly one proven, declared cross-family judge runs per pass with rubric, randomized
   order, and structural isolation.
9. The PDF is rendered, every shipped page is rasterized and inspected, and every
   visual receipt resolves to an asset actually shipped.
10. Forced interrupt/resume preserves valid work and hashes.
11. L01 reaches `ACCEPTED` by controller decision with zero failed blocking checks.
12. The output is described only as a draft pending downstream human review.

A failed attempt is diagnostic evidence, not completion. Preserve it unchanged and
continue only while the task-level budget and convergence rules permit. Do not call the
runtime implemented or L01 accepted until one clean attempt satisfies every criterion.

## Final response

Lead with the outcome. Report:

- The exact bounded task outcome and the condition that selected it.
- Runtime files created or changed.
- L01 terminal state and artifact paths.
- Task-ledger path; clean-attempt count; cumulative wall time, model calls,
  cross-family calls, source fetches, generated images, and storage.
- Read-only capability-audit results; before/after hashes for the unchanged route and
  routing contracts; the recorded `RESEARCH` divergence; and whether a live L01 attempt
  was permitted.
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
proves it with L01 only. The remaining 34 Arduino units are explicitly outside this
task.
