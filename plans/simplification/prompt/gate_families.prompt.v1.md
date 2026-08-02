# Make the simplification approach testable

Runs unattended. Takes no arguments, asks no questions, and never waits on a person.
Every decision it could ask about is already taken below.

## Goal

Today the simplification approach has **zero tests and cannot get any**.
`FR-P0-REGISTRY` requires `tests/gates/registry.py` to equal §8 of
`plans/folder_refactoring/folder_refactoring.plan.v6.md` in both directions — that
section says *31 gates*, and a 32nd registered gate is reported
`gate-registered-not-in-plan` and fails. So no gate can be written for any plan except
a finished one about folder structure.

Two things must hold when this run ends:

1. **A gate can belong to a plan other than the folder plan.** The registry composes
   from several plans, each owning its own family, and `FR-P0-REGISTRY` checks each
   family against its own plan's catalogue section. This is
   `plans/fix_meta_prompt/fix_meta_prompt.plan.v1.md` §5 recommendation **(iii)**,
   which `plans/simplification/plan/simplification.plan.v3.md` §7 declares a
   dependency and does not itself perform.
2. **The first such gate exists and executes**: `plans/simplification/plan/`'s phase-0
   assertion — no engine file names a curriculum directory, and no engine check id
   encodes a domain term — as a real gate with fixtures, registered, running, and
   reporting the repository's true state.

**Done is "the test exists and is honest", never "the repository passes it."** The
engine today has at least thirteen electronics leaks. The new gate is *expected to
report FAIL against the working tree*, and that FAIL is the deliverable — it is the
first measurement this project has ever had of how much domain is welded into its
engine. **Cleaning the engine is not in this run.** An agent that deletes leaks to
turn the new gate green has destroyed the measurement and must return `HALTED`.

## Non-goals, stated so they are not drifted into

- Removing any electronics from `policy/`, `schemas/` or `meta_prompt/`. Out of scope.
- The phase-4 generic checks — readability, Bloom, cross-document derivation, hash
  resolution. They need the unit contract, which does not exist yet. Out of scope.
- Writing `meta_prompt/curriculum.prompt.v1.md`. Out of scope.
- Any change to what the 31 existing gates assert.

## Agents

- **Coordinator** — assigns work, owns commits, owns the iteration budget.
- **Implementer** — makes the changes.
- **Validator** — independently runs the harness and reads the result JSON.
- **Reviewer** — independently checks the diff against this prompt.

Only the coordinator changes Git history. Keep the three roles separate.

## Loop

Read `readme.md`, `plans/fix_meta_prompt/fix_meta_prompt.plan.v1.md` §5,
`plans/simplification/plan/simplification.plan.v3.md` §§2, 6, 7, and
`plans/folder_refactoring/folder_refactoring.plan.v6.md` §8 before step 1.

**Step 1 — record the baseline.** Run `./tests/run_gates.sh 4`. Record the counts. It
must read 31 PASS, 0 FAIL, 0 BLOCKED, 0 SKIPPED with a clean worktree. If it does not,
fix the worktree — not the gates — and re-run. `FR-P0-CLEAN` fails intermittently on
this filesystem with `.git/index: unable to map index file`; that is the environment,
so re-run once before treating it as real. **This baseline is the regression contract
for every later step.**

**Step 2 — generalise the registry.** Make gate-family ownership *declared data*, not
a constant inside a gate. The mapping from gate-id prefix to owning plan and to that
plan's catalogue section must be readable, versioned, and validated the way every
other manifest in this repository is. `common.active_plan_path()` resolves one plan
today; whatever replaces it must resolve one plan **per family** and must keep
resolving the folder family exactly as it does now.

**Step 3 — prove the generalisation bites.** Add a reject fixture to `FR-P0-REGISTRY`
under `tests/fixtures/` for a gate registered under a family no plan owns. Its
expected error is declared, and a fixture that fails for a different reason is `FAIL`,
not `PASS`. Fixtures are not compared against §8, so adding one changes no existing
gate's contract.

**Step 4 — give the simplification plan a catalogue section.** It has none:
`simplification.plan.v3.md` §8 is *Out of scope*, and the section parser keys on the
literal heading number. Append a new numbered section holding the new family's gate
catalogue in the encoding §8 of the folder plan documents — id, activation phase,
claim class, depends-on, command, pass criteria, fixtures, failure meaning. Do not
renumber the plan's existing sections; other documents cite them.

**Step 5 — write the gate.** One gate. It asserts, over the engine layer — `policy/`,
`schemas/`, `meta_prompt/meta_curriculum_builder.prompt.v6.md` and
`meta_prompt/assets/*.md`, excluding every `deprecated/` — that

  (a) no file names a `curricula/<name>/` path, and
  (b) no check id declared in `policy/checks.v1.yaml` as engine-owned encodes a
      domain term.

Give it an **accept fixture** and a **reject fixture**, per the existing convention. It
depends on `FR-P0-HARNESS`. Its `activation_phase` is **5** — above the folder family's
range, so `./tests/run_gates.sh 4` stays at 31 PASS and this gate is reached only by
`./tests/run_gates.sh 5`. Its declared claim class must equal the mechanisms its
implementation actually reports, or `FR-P0-REGISTRY`'s drift sweep fails it.

The list of domain terms the gate matches is **data in the engine's own manifests**,
not a literal list inside the gate — a gate that hardcodes "circuit" is the leak it
was written to detect.

**Step 6 — validate.** The coordinator commits a candidate; gates run against a
commit, never a dirty tree. The validator then runs **both**:

- `./tests/run_gates.sh 4` → must still be **31 PASS, 0 FAIL, 0 BLOCKED**.
- `./tests/run_gates.sh 5` → 32 gates registered; the 31 pass; the new gate **runs**,
  and both its fixtures behave as declared.

Validation passes when both hold, results are written, and the worktree is clean. It
passes **whether the new gate reports PASS or FAIL against the working tree** — its
verdict on the repository is the measurement, not the pass condition. What must never
happen is the new gate being `BLOCKED`, crashing, or not executing.

**Step 7 — record what it measured.** Write the new gate's verdict and, if it failed,
every file and reason it named, into a result note beside the plan. This is the
inventory `simplification.plan.v3.md` phase 0 asks for, and it is the input to
deciding whether that plan's `G1`–`G6` table is complete. State plainly whether it is.

## Iteration budget and the stall rule

The coordinator owns both.

- **Six correction cycles.** A seventh is `HALTED`, not a seventh.
- **Every cycle must narrow the failing set.** The identical failing set twice is
  `HALTED`; report the set.
- **Two cycles that add files without reducing failures** is `HALTED`.
- Record every cycle: what failed, what changed, what the next run measured.

## Standing constraints

- **The measurement is the product.** A green new gate obtained by editing `policy/`,
  `schemas/` or `meta_prompt/` content is a fabricated result. Only the harness, the
  registry, the plan's catalogue section, and `tests/` may change.
- **A gate's implementation may be corrected; its criteria may not be relaxed.** Wrong
  scan root, bad regex, misparsed path — fix it, record it as `gate_impl_fix` with a
  one-line reason, have the reviewer re-check it. Never widen an exclusion so a leaking
  file stops counting.
- **Never report an unexecuted check as passing**, and never report a gate that was
  `BLOCKED` as one that ran.
- **`BLOCKED` is a gate outcome; `HALTED` is the run verdict.** They are never
  interchanged.
- **The 31 existing gates are the regression contract.** If a change to `common.py` or
  `registry.py` costs even one of them, the change is wrong, not the gate.
- Anything the run discovers but was not sent to do is **surfaced, not acted on** —
  under an `RT-` id in `policy/deferred.v1.yaml` if it belongs there, in the report
  otherwise.

## Finish

Return `APPROVED` only when all of these hold:

1. `./tests/run_gates.sh 4` reports 31 PASS, 0 FAIL, 0 BLOCKED — unchanged from the
   step-1 baseline.
2. `./tests/run_gates.sh 5` registers 32 gates, and the new one **executed**.
3. Both of the new gate's fixtures behaved as declared, each for its declared reason.
4. `FR-P0-REGISTRY`'s new reject fixture bites.
5. The simplification plan owns its family through its own catalogue section, and the
   folder plan was not edited.
6. No file under `policy/`, `schemas/` or `meta_prompt/` changed.
7. The worktree is clean and the report states the new gate's verdict on the
   repository, in these terms: the engine is measured, the engine is not yet clean, and
   cleaning it was not this run's job.

Otherwise return `HALTED`, naming the failing gate id or step, its stated failure
meaning, and — where the cause is external or needs a decision — the exact blocker or
decision required.
