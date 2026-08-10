# Make the executor prompt use the gate that now exists

Runs unattended. Takes no arguments, asks no questions, and never waits on a person.
Every decision it could ask about is already taken below.

## Goal

`simplification.prompt.v2.md` was written when the simplification plan had **no test
and could not get one**. It therefore validates each plan phase with
`./tests/run_gates.sh <phase>` against 31 gates that all belong to a *different* plan,
and its only statement about the engine/domain boundary is prose in its Goal.

That is no longer true. `FR-P5-ENGINE-GENERIC` exists, is registered, executes, and
reports the boundary's true state — see `../plan/simplification.plan.v3.md` §9 and
`../plan/simplification.phase0.result.v1.md`. Nothing in v2 knows about it.

**Produce `simplification.prompt.v3.md`**: the same executor, wired to the test.
Three defects to close, and they are the whole job.

1. **Two different things are both called "phase".** v2's loop runs plan phases in the
   order 0, 4, 1, 2, 3, 5 and validates each with `./tests/run_gates.sh <phase>`, using
   the plan phase as the harness argument. They are different axes: the harness
   argument is an `activation_phase`, the folder family occupies 0–4, and the
   simplification family's only gate activates at **5**. `run_gates.sh 4` during plan
   phase 4 runs the folder plan's phase-4 gates and is unrelated to the work being
   validated. v3 must name, per plan phase, **which harness phase to run**, and must
   never let one number stand for both.

2. **The new gate is expected to FAIL at plan phase 0 and to PASS by the end.** v2's
   step 6 requires every gate at or below the requested phase to pass. Applied to
   `run_gates.sh 5` at plan phase 0 that is wrong twice over: it would fail a phase
   whose deliverable *is* the failing measurement, and it would invite an agent to
   delete the leaks early to go green — destroying the inventory §6 phase 0 exists to
   produce. v3 must state where the gate is a **measurement** and where it becomes an
   **acceptance criterion**, and must forbid the shortcut explicitly.

3. **One of the leaks the gate reports is scheduled by no phase.** The gate names three
   files. `meta_prompt/assets/inputs.v1.md` is `G2` and is retired by plan phase 5;
   `policy/checks.v1.yaml` is `G3` and is split by plan phase 3;
   **`policy/calibration.v1.yaml` is in no row of the plan's `G1`–`G6` table.** Its
   precedence comment binds the engine to one curriculum's four prose documents. As
   things stand the gate cannot go green, so v2 cannot reach `APPROVED` — it would
   `HALT` at the last phase on a defect nobody assigned.

## The decisions, taken here so no run re-asks them

- **The calibration leak is `G7`, and plan phase 3 owns it.** It is one manifest's
  header comment naming four curriculum files; it belongs with the check-inventory
  separation, which is the phase that already edits the engine's ownership of
  curriculum-specific references.
- **The plan is amended in place, not superseded.** `simplification.plan.v3.md` §2
  gains the `G7` row and §6 phase 3 gains the sentence that closes it. **No
  `simplification.plan.v4.md` is created** — that plan's own §7 forbids a v4 before
  phase 6 produces a unit, and a seventh specification document is the failure mode
  this project is named after. Record the amendment in the plan's own text.
- **Adding gates to this family is data, not code.** `tests/gates/gate_families.v1.yaml`
  gives the simplification family the `FR-P5-` prefix. A gate this family adds at a
  later `activation_phase` needs its prefix listed there too, or `FR-P0-REGISTRY`
  reports `gate-family-unowned` and fails — which is the reject fixture doing its job,
  not a defect. v3 must say this where it tells a phase to add a gate.
- **Superseded prompts are archived.** `plans/simplification/prompt/v1` and `v2` move to
  `plans/simplification/prompt/deprecated/` when v3 becomes active, per readme.md's
  retention table.

## Non-goals, stated so they are not drifted into

- **Executing the simplification plan.** This run edits a prompt. It does not implement
  phase 0, 1, 2, 3, 4, 5 or 6, and it does not clean a single leak.
- **Any change to `policy/`, `schemas/`, `meta_prompt/` or `curricula/`.** The `G7`
  leak is *scheduled*, not fixed.
- **Any change to what the 32 registered gates assert**, to `tests/gates/registry.py`,
  or to §9 of the plan. The test is finished; this run is about the prompt that uses it.
- Writing `meta_prompt/curriculum.prompt.v1.md`. That is plan phase 5's deliverable.
- Rewriting v2's stage B, its Judge rules, its iteration budget or its reporting
  constraints. They are sound and carry forward.

## Agents

- **Coordinator** — assigns work, owns commits, owns the iteration budget.
- **Implementer** — writes v3 and the plan amendment.
- **Validator** — independently runs the harness and reads the result JSON.
- **Reviewer** — independently checks the diff against this prompt.

Only the coordinator changes Git history. Keep the three roles separate.

## Loop

Read `readme.md`, `../plan/simplification.plan.v3.md` §§2, 6, 7, 9,
`../plan/simplification.phase0.result.v1.md`, `simplification.prompt.v2.md`,
`tests/gates/gate_families.v1.yaml` and `tests/gates/registry.py` before step 1.

**Step 1 — record the baseline.** Run `./tests/run_gates.sh 4`, then
`./tests/run_gates.sh 5`. Phase 4 must read 31 PASS, 0 FAIL, 0 BLOCKED, 1 SKIPPED with
a clean worktree. Phase 5 must read 31 PASS, 1 FAIL, 0 BLOCKED, 0 SKIPPED, the single
FAIL being `FR-P5-ENGINE-GENERIC` and its detail naming three files. **This pair is
the regression contract for every later step**, and it does not change: nothing in this
run is supposed to move either number. `git` on this filesystem fails intermittently
with `.git/index: unable to map index file` and `mmap failed: Operation timed out`;
that is the environment, so re-run before treating any git-invoking gate's failure as
real.

**Step 2 — amend the plan.** Add `G7` to §2's leak table —
`policy/calibration.v1.yaml`, the precedence comment naming four
`curricula/arduino_kit/` prose documents — and give §6 phase 3 the sentence that
retires it. Do not renumber sections; other documents cite them. Do not touch §9.

**Step 3 — separate the two phase axes in v3.** Give the stage-A loop an explicit
table: plan phase → the harness phase its validation runs → what that run must report.
Every row states its own expected counts. The plan phases keep v2's order — 0, 4, 1,
2, 3, 5 — and the reason v2 gives for it.

**Step 4 — wire in the gate, in both of its roles.** At plan phase 0 the validation is
`./tests/run_gates.sh 5`, `FR-P5-ENGINE-GENERIC` is **expected to FAIL**, and the phase
passes on the measurement being *recorded*, not on it being green. From plan phase 5
onward the same gate is an acceptance criterion and must PASS. State the transition
once, in one place, and name the phase that owns each of the three leaks — `G2`/phase
5, `G3`/phase 3, `G7`/phase 3.

**Step 5 — say what the harness does not cover.** v2's step 6 reads as though passing
gates evidences the phase. For plan phases 1, 2 and 4 no gate exists yet. v3 must
either require each such phase to add its gate to the simplification family — §9, the
registry, the family manifest's prefixes, with an accept and a reject fixture — or
state plainly, per phase, that its evidence is review and fixtures rather than a gate.
Choose per phase; do not leave the reader to infer it.

**Step 6 — archive and activate.** v3 names the plan it executes in its goal line. v1
and v2 move to `plans/simplification/prompt/deprecated/`. If that trips
`FR-P1-GITKEEP`, add the `.gitkeep` the retention convention requires — that is the
convention working, not a failure.

**Step 7 — validate.** The coordinator commits a candidate; gates run against a commit,
never a dirty tree. The validator then re-runs **both** harness phases and compares
against step 1. Both must be **identical to the baseline**. This run changes prompts
and plan prose only: a moved count means something was edited that this run was not
sent to edit.

**Step 8 — prove v3 is executable against reality.** Walk v3's stage-A table against
the working tree and confirm each row's stated expectation matches what the harness
actually reports today for the phases that can be run now — plan phase 0's row against
the real `run_gates.sh 5` result. A row that asserts a count the harness does not
produce is a defect in v3, not in the harness.

## Iteration budget and the stall rule

The coordinator owns both.

- **Six correction cycles.** A seventh is `HALTED`, not a seventh.
- **Every cycle must narrow the failing set.** The identical failing set twice is
  `HALTED`; report the set.
- **Two cycles that add files without reducing failures** is `HALTED`.
- Record every cycle: what failed, what changed, what the next run measured.

## Standing constraints

- **Do not confuse the prompt you are editing with the prompt it produces.**
  `simplification.prompt.v3.md` is this run's deliverable. `meta_prompt/curriculum.prompt.v1.md`
  is *its* deliverable, and does not exist. Neither is this file.
- **The measurement stays failing.** `FR-P5-ENGINE-GENERIC` must still report FAIL on
  the same three files when this run ends. A green gate here means the engine was
  edited, which is out of scope and is failure A5.
- **Schedule a leak; never silence one.** `G7` is closed by assigning it a phase. Adding
  an exclusion to the gate, or an exemption to the manifest, so that
  `policy/calibration.v1.yaml` stops counting is the defect this whole gate exists to
  detect.
- **v3 may not be weaker than v2.** Every constraint in v2's §Standing constraints and
  §Finish survives into v3 unless this prompt names it for change. Nothing here names
  any of them.
- **Never report an unexecuted check as passing**, and never report a gate that was
  `BLOCKED` as one that ran.
- **`BLOCKED` is a gate outcome; `HALTED` is the run verdict.** Never interchanged.
- **The 31 folder-family gates plus the phase-5 measurement are the regression
  contract.** If a change costs one of them, the change is wrong, not the gate.
- Anything the run discovers but was not sent to do is **surfaced, not acted on** —
  under an `RT-` id in `policy/deferred.v1.yaml` if it belongs there, in the report
  otherwise.

## Finish

Return `APPROVED` only when all of these hold:

1. `simplification.prompt.v3.md` exists, names `../plan/simplification.plan.v3.md` in
   its goal, and v1 and v2 are under `prompt/deprecated/`.
2. v3 states, per plan phase, the harness phase its validation runs and the counts that
   run must report — and no number in v3 does duty as both a plan phase and a harness
   phase.
3. v3 states where `FR-P5-ENGINE-GENERIC` is a measurement expected to fail, where it
   becomes an acceptance criterion, and which plan phase owns each of `G2`, `G3` and
   `G7`.
4. v3 states, for every plan phase, whether its evidence is a gate or is review and
   fixtures — and where it is a gate, that the family manifest's prefixes must carry it.
5. `simplification.plan.v3.md` §2 declares `G7` and §6 phase 3 closes it; no
   `simplification.plan.v4.md` was created; §9 is unchanged.
6. `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5` both report **exactly** the
   step-1 baseline, including `FR-P5-ENGINE-GENERIC` still failing on the same three
   files.
7. No file under `policy/`, `schemas/`, `meta_prompt/`, `curricula/` or `tests/`
   changed.
8. The worktree is clean, and the report states plainly that this run made the
   executor prompt able to reach `APPROVED` and implemented none of the work that would
   get it there.

Otherwise return `HALTED`, naming the failing gate id or step, its stated failure
meaning, and — where the cause is external or needs a decision — the exact blocker or
decision required.
