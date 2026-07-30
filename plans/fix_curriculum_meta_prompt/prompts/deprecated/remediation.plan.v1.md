# Plan: make the curriculum creator executable unattended, and reusable for a second curriculum

## 1. Goal — WHY

Take `curriculum_creator` from its current state — two Codex reviews returning NO-GO,
twelve open blockers — to a state where `prompts/meta_curriculum_prompt.prompt.v5.md`
can be started by a human and left alone until it reaches a terminal state, and where
a second curriculum in a different domain can reuse the machinery without editing it.

## 2. Success criteria — WHY

Each is a check, not a judgement.

1. Codex returns **GREEN LIGHT** on an unattended-execution review of `curriculum_creator`.
2. Every input named in the prompt's Inputs table validates against a schema that exists.
3. `grep -rn "3[0-5]\]" schema/` returns nothing — no lab-count regex anywhere.
4. No file under `assets/` references a path outside `CREATOR`.
5. A synthetic execution log whose `EXEC` cites a non-existent `ACT` is **rejected** by
   the controller's pairing computation (schema alone cannot do this — see §8).
6. Every check id in `assets/checks.v1.yaml` is either executed by the proving tests or
   explicitly marked `stage: v7-runtime` as a check v7 must implement.
7. The lab schema splits: `lab.core.schema.v1.json` validates a lab with its `domain`
   block opaque; `schema/domain/electronics.schema.v1.json` validates that block.
8. A stub second-domain file validates against the same core, proving the split is real
   rather than asserted.
9. Every claim in `readme.md` and `how_it_works.md` about counts, files and reviewer
   cardinality matches the repository.

## 3. Scope & non-goals — WHY

**In scope**
- The twelve blockers from the second Codex review.
- Splitting the lab schema into a domain-neutral core plus a domain layer.
- Deciding where the spec/implementation boundary sits for the controller (§5, Step 4).
- Schemas for the five extracted assets that currently have none.

**Non-goals**
- Running the meta prompt. This plan ends at "ready to run", not "run".
- Writing curriculum content, or generating any lab.
- Building the second curriculum. Only proving the split would support one.
- Sourcing datasheets. That is a run-time activity, correctly deferred to `RESEARCH`.
- Rewriting `assets/lab_brief.md` or `assets/teacher_framework.md` to match calibration.
  Their divergence is deliberately recorded, not resolved (see §4, Assumptions).

## 4. Context & assumptions — WHY

**Inputs**
- `prompts/meta_curriculum_prompt.prompt.v5.md` — 292 lines, the thing being made runnable.
- `assets/*.yaml`, `schema/*.json` — the extracted declarative layer.
- Codex review 2 — twelve blockers, four verified independently by this session
  (lab-count regex, external L01 path, unsatisfiable validation rule, unenforced pairing).
- `assets/failures.v1.yaml` — the A1–A10 / B1–B4 ledger this system exists to correct.

**Constraints**
- `ROOT` is not a git repository, and inherits `trust_level = "untrusted"`.
  Every worker call needs `-s workspace-write --skip-git-repo-check`.
- No TeX engine, no Python PDF library. `typst` via pandoc is the only PDF route;
  `pdftoppm` is the only rasterizer. Both proven 2026-07-29.
- ImageGen has **no proven invocation** in this environment.
- The meta prompt must not be written to during a run; `CREATOR` is immutable to it.

**Assumptions**
- The architecture is sound. Twenty-one findings across two reviews, none of which said
  the design is wrong — they said it is under-specified for an unwatched run.
- The learner age band is 9+ and the pedagogy caps derive from it (`calibration.v1.yaml`).
- `lab_brief.md` and `teacher_framework.md` state 12+ and an exclusive USB supply.
  Calibration outranks them; the divergence is a defect to report, not to silence.
- Reviewer isolation cannot be achieved by instruction. It needs a filesystem mechanism.

## 5. Steps — HOW

### Step 1: Mechanical corrections
- **Does:** Fixes the blockers that need no decision. Two lab-id regexes in
  `curriculum.schema.v4.json` (`sequence.prerequisites`, `sequence.prepares_for`);
  repoint both L01 JSON files at `assets/official_kit_photo.jpg`; correct reviewer count
  8→12 in `how_it_works.md` and `infographic.prompt.v1.md`; refresh stale counts in
  `readme.md`; resolve `.vN` vs `templates_v7` naming.
- **Inputs:** Codex blockers 5, 8, 10; non-blocking 1 and 4.
- **Produces:** corrected files; no new artifacts.
- **Depends on:** none. **Parallel?** yes. **Owner:** this session.

### Step 2: Schemas for the unschema'd assets
- **Does:** Writes `schema/limits.schema.v1.json`, `routes.schema.v1.json`,
  `checks.schema.v1.json`, `failures.schema.v1.json`, `pipeline.schema.v1.json`, so the
  prompt's "validate every input against its schema" becomes satisfiable. Each carries
  guard constraints in the style of `calibration.schema.v1.json` — a route with
  `status: UNPROVEN` may not be cited by a gate; a check with `fixture_expectation:
  reject` must name a fixture that exists.
- **Inputs:** the five assets; `calibration.schema.v1.json` as the pattern.
- **Produces:** five schema files.
- **Depends on:** Step 4 (pipeline schema shape depends on the controller decision).
- **Parallel?** partly — four are independent; `pipeline.schema` waits.
- **Owner:** this session.

### Step 3: Split the lab schema by domain
- **Does:** Separates `lab.schema.v3.json` into `lab.core.schema.v1.json` (identity,
  pedagogy, sequence, visual machinery — with `domain` as an opaque object requiring
  `domain_id`) and `schema/domain/electronics.schema.v1.json` (the electronics block,
  `content`, the electrical fields of `safety`, the electronics visual roles, the `kind`
  enum). Moves the `power:` section out of `calibration.v1.yaml` into a domain profile,
  leaving calibration with `learner`, `pedagogy_caps`, `safety_floor` only.
- **Inputs:** the block audit — 2 of 7 blocks are domain-neutral today.
- **Produces:** `schema/lab.core.schema.v1.json`, `schema/domain/electronics.schema.v1.json`,
  `assets/domain/electronics.v1.yaml`, a slimmed `calibration.v1.yaml`, and a stub
  second-domain schema used only to prove the core is genuinely reusable.
- **Depends on:** Step 1. **Parallel?** no. **Owner:** this session.

### Step 4: Decide the spec/implementation boundary — **DECISION REQUIRED**
- **Does:** Resolves Codex blocker 2. `assets/controller.v1.yaml` is a state list with
  prose rules, not a state machine; it has no transition table, guards, retry edges or
  precondition edge. Two ways forward:
  - **(a) Specify further** — author a full transition table in YAML. The meta prompt
    stays the sole builder; more spec surface, more review cycles like today's.
  - **(b) Split engine from pipeline** — write the engine in Python here (checkpointing,
    resume, retry, aggregation, logging, pairing computation) and keep a per-curriculum
    `assets/pipeline.v1.yaml` naming the states, their workers, schema blocks and
    reviewer counts. The meta prompt then builds only the model-facing parts.
- **Recommendation:** (b). It answers blocker 2 with tested code rather than a longer
  spec, it makes blocker 9 (pairing) enforceable, and it preserves per-curriculum
  flexibility where flexibility is actually needed — in the pipeline definition, not in
  the checkpointing logic.
- **Produces:** a recorded decision; if (b), `engine/` plus `assets/pipeline.v1.yaml`.
- **Depends on:** user decision. **Parallel?** no. **Owner:** user, then this session.

### Step 5: Make reviewer isolation structural
- **Does:** Resolves blocker 4. `authorized_paths` is currently a log field, and
  `codex exec -s workspace-write` grants workspace-wide access, so isolation is
  documented rather than enforced. Specifies the mechanism: each reviewer runs against a
  scratch directory containing copies of only its authorized inputs, with the worker
  invoked with that directory as its working root. Adds a test that fails if any sibling
  verdict file is reachable from a reviewer's root.
- **Inputs:** `assets/routes.v1.yaml`, the B2 diagnosis.
- **Produces:** an isolation contract in the prompt; `REV-ISOLATED` becomes executable.
- **Depends on:** Step 4. **Parallel?** no. **Owner:** this session.

### Step 6: Close the remaining contract gaps
- **Does:** Bootstrapping order — the log must exist before `V7`, so name a bootstrap
  location and require migration with a hash check once `V7` is created (blocker 3).
  Routing — `routing/model_selector_prompt.v1.md` has a model choose the model while the
  controller claims code owns routing; make classification a deterministic lookup against
  `task_taxonomy.v2.yaml` and retire the selector prompt (blocker 6). ImageGen — either
  prove an invocation or remove the route and state what a lab does without it, so gate 4
  is satisfiable (blocker 7). Pairing — state that the controller computes
  `unclosed_starts`; the schema is necessary, not sufficient (blocker 9). Calibration
  enforcement — enum `safety.power_profile.source` against the permitted input ids
  (blocker 11). PDF acceptance — define "uniform within 1%" as a computable rule and
  specify output-directory creation, page enumeration and count extraction (blocker 12).
- **Depends on:** Steps 3–5. **Parallel?** partly. **Owner:** this session.

### Step 7: Re-review
- **Does:** Submits the result to Codex for a third unattended-execution verdict, then
  verifies its findings independently rather than accepting them.
- **Produces:** a verdict, and either a done state or a `plan.v2`.
- **Depends on:** Steps 1–6. **Owner:** Codex, then this session.

## 6. Artifacts & output format — HOW

```text
curriculum_creator/
  plans/remediation.plan.v1.md          this file
  schema/
    lab.core.schema.v1.json             NEW  domain-neutral lab contract
    domain/electronics.schema.v1.json   NEW  the electronics layer
    domain/_stub.schema.v1.json         NEW  proves the core is reusable
    limits|routes|checks|failures|pipeline .schema.v1.json   NEW
    calibration|curriculum .schema.*.json                    unchanged
    lab.schema.v3.json                  RETIRED → superseded by core + domain
  assets/
    domain/electronics.v1.yaml          NEW  supplies, rails, domain data
    pipeline.v1.yaml                    NEW if Step 4 = (b)
    calibration.v1.yaml                 SLIMMED — power moves to domain
  engine/                               NEW if Step 4 = (b)
```

Every new schema follows the `calibration.schema.v1.json` pattern: `additionalProperties:
false`, guard constraints that reject the specific defect they exist to prevent, and a
`description` stating which failure it guards against.

## 7. Verification — HOW

| Step | Check |
|---|---|
| 1 | `grep -rn "3[0-5]\]" schema/` empty; no `work/elegoo_labs` reference under `assets/`; docs say twelve |
| 2 | every input in the prompt's Inputs table has a schema, and validates against it |
| 3 | `electronics.v1.yaml` validates; the stub domain validates against the same core; a lab with `domain_id: electronics` passes both passes |
| 4 | decision recorded; if (b), the engine's own tests pass before anything uses it |
| 5 | a test proves no reviewer root can reach a sibling verdict file |
| 6 | each of blockers 3, 6, 7, 9, 11, 12 has a named check id in `assets/checks.v1.yaml` |
| 7 | Codex verdict is GREEN LIGHT; every finding it raises is independently verified before acceptance |

The plan is done when §2's nine criteria all hold — not when the steps are executed.

## 8. Risks, failure handling & escalation — HOW

**Per-step failure policy.** Steps 1–3 and 6 are corrections: on failure, fix and re-verify.
Step 4 is a decision: it blocks everything downstream and does not proceed on assumption.
Step 7 failing is the normal case, not an exception — two reviews have already returned
NO-GO, and a third finding new issues means the review is working.

**Risks**

| Risk | Why it matters | Mitigation |
|---|---|---|
| Partial fixes reported as complete | This session did it three times today — one of three regexes, a photo copied but not repointed, a validation rule asserted while creating five unschema'd assets | Every fix in §7 is a command whose output is checked, not a claim |
| The domain split leaks | If any electronics field survives in the core, the second curriculum inherits it silently | The stub domain in Step 3 exists solely to force this failure early |
| Schema can't express the constraint | Blocker 9 is JSON Schema's cross-record limit, not a bug in ours | State plainly which checks the schema cannot enforce and assign them to the controller |
| Scope creep into curriculum #2 | The generalization invites building the second curriculum | Non-goal, explicitly. Step 3 proves the split with a stub, nothing more |
| Fixing what Codex asserts without verifying | An external reviewer can be wrong | Four of twelve were verified before acceptance; the rest get the same treatment |

**Escalate to a human when**
- Step 4's decision is needed — engine-in-code versus longer spec.
- ImageGen cannot be proven and a lab's visual sufficiency matrix must change as a result.
- A Codex finding contradicts a deliberate decision recorded here — for example, the
  calibration/prose divergence, which is recorded on purpose and must not be "fixed".
