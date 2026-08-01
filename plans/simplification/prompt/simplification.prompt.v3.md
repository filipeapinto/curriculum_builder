# Execute the simplification plan v3

Executes `../plan/simplification.plan.v3.md`, plan phases 0–6.

Supersedes `simplification.prompt.v2.md`; v1 and v2 are in `deprecated/` and nothing may
read them. v2 was written when this plan had **no test and could not get one**: it
validated every phase with `./tests/run_gates.sh <phase>` against 31 gates belonging to
a *different* plan, and its only statement about the engine/domain boundary was prose.
`FR-P5-ENGINE-GENERIC` now exists, is registered, executes, and reports that boundary's
true state. v3 changes exactly three things: it separates the two axes both called
"phase", it wires that gate in as a **measurement** first and an **acceptance criterion**
later, and it says per phase whether the phase's evidence is a gate at all. Everything
else — stage B, the judge rules, the budget, the constraints — carries forward from v2
unchanged.

This prompt takes no arguments and asks no questions. The two decisions v1 demanded as
arguments are resolved in the plan's §4: the domain data is **composed**, declared by the
curriculum as `circuit_policy: composed`, and there is **no in-pipeline sign-off**.

## Goal

Implement `../plan/simplification.plan.v3.md` plan phases 0–6, so that two things hold
at once:

1. **The engine is generic.** No engine file names a curriculum directory, no engine
   check id encodes a domain term, and the unit contract carries a `domain` block whose
   shape the curriculum supplies. G1–G7 resolved — **seven**, because §2 was amended
   after `FR-P5-ENGINE-GENERIC` measured a leak the table had not named.
2. **The prompt works.** One prompt — `meta_prompt/curriculum.prompt.v1.md`, written by
   plan phase 5 — generates **L01 of `curricula/arduino_kit/`**, and that unit passes every
   check the engine and the curriculum declare.

Finish only when §Finish holds. Preserve unrelated changes. Never weaken a requirement
and never report an unexecuted check as passing.

**Three verdicts, never interchanged.** **`BLOCKED`** is a gate-level outcome — a gate
whose dependency failed or was itself blocked, propagating transitively. **`HALTED`** is
the run-level verdict when a phase cannot be approved, whatever the cause.
**`APPROVED`** requires §Finish below.

## Two different things are called "phase". Never let one number mean both.

- A **plan phase** is a numbered step of the plan's §6. There are eight, 0–7, and this
  run covers 0–6.
- A **harness phase** is the single integer argument to `./tests/run_gates.sh`. It is an
  `activation_phase` ceiling: the harness runs every gate registered at or below it and
  records every gate above it as `SKIPPED`.

They are different axes and they do not correspond. The folder-refactoring family
occupies activation phases 0–4 and is a finished, accepted plan whose regression run must
not start reporting this plan's failures. This plan's family activates at **5**.
`./tests/run_gates.sh 4` during plan phase 4 therefore runs the *folder* plan's phase-4
gates and evidences nothing about the work being validated.

**The rule: never write "phase N" alone.** Write "plan phase N" or "harness phase N".
Every validation below names which harness phase it runs, and the §Stage A table is the
only place that mapping is stated.

## Agents

- **Coordinator:** assigns work, enforces plan-phase order, owns commits, and owns the
  iteration budget.
- **Implementer:** makes the current plan phase's changes.
- **Validator:** independently runs the harness and the L01 test, and verifies the result
  record. Reads the result JSON under `tests/results/`, not the terminal summary alone.
- **Reviewer:** independently checks the diff against the plan.
- **Judge** (plan phase 6 only): reviews the generated unit. **Must be a different model
  family than the one that generated it** — self-preference bias is measured at −38% to
  +90% and survives hiding authorship. One judge per pass, not a panel: nine cross-family
  judges measure at 2.18 effective votes.

Only the coordinator changes Git history. Keep implementation, validation, and review
separate.

## The measurement, and where it becomes an acceptance criterion

`FR-P5-ENGINE-GENERIC` is one gate with two roles, and the transition is stated here
once. It reports the leaks in the engine layer; the plan's §6 phases are what remove
them.

- **Through plan phases 0, 4, 1, 2 and 3 it is a measurement, and it is expected to
  FAIL.** A plan phase in this range passes on the measurement being *recorded* and
  matching what that phase was supposed to move — never on the gate being green. A green
  gate here means the engine was edited ahead of the phase that owns the edit, which
  destroys the inventory and is failure A5.
- **From plan phase 5 onward it is an acceptance criterion and must PASS.** Plan phase 5
  closes the last leak it can see.

Three leaks are in its report, and each has exactly one owning plan phase:

| Leak | File | Owned by | Closed how |
|---|---|---|---|
| `G2` | `meta_prompt/assets/inputs.v1.md` (11 lines) | **plan phase 5** | the authorized-input set is generalised into `meta_prompt/curriculum.prompt.v1.md`, then the asset is retired — in that order |
| `G3` | `policy/checks.v1.yaml` (13 lines) | **plan phase 3** | domain checks and their subject paths move to `curricula/<name>/checks.v1.yaml` |
| `G7` | `policy/calibration.v1.yaml` (3 lines) | **plan phase 3** | the header comments state precedence over *the curriculum's* prose, not over four named `curricula/arduino_kit/` files |

`G7` was in no row of the plan's leak table until this prompt's predecessor run amended
§2. Do not re-derive it and do not re-open it.

**Scheduling a leak is the only way to close one.** Adding an exclusion to the gate, an
exemption to a manifest, or a path to a `deprecated/` folder so that a file stops being
scanned is not a fix — it is the defect the gate was written to detect. The one legitimate
retirement, `G2` at plan phase 5, only counts because the rules move into a live file
first, and because that live file is itself scanned: **plan phase 5 must repoint
`tests/meta_prompt_source.py` at `meta_prompt/curriculum.prompt.v1.md` in the same commit
that retires v6.** A gate that goes green because the file it scanned moved out from
under it has measured nothing.

## Loop — stage A, plan phases 0, 4, 1, 2, 3, 5

Read `AGENTS.md`, the complete v3 plan, `../plan/simplification.phase0.result.v1.md`,
`../research/conclusions.v1.md`, `tests/gates/gate_families.v1.yaml` and
`tests/gates/registry.py` before starting.

**That order — 0, 4, 1, 2, 3, 5 — is the plan's, for the plan's reason:** plan phase 4's
checks are the only part provable before anything runs, and §7 sequences them first
among the substantive work because this project has already produced six better
specifications and zero curricula.

For each plan phase `N` in that order:

1. The implementer completes plan phase `N`.
2. The reviewer returns `APPROVE` or actionable findings.
3. Fix findings and repeat review until approved.
4. The coordinator creates the phase's **candidate commit**. Gates run against a commit,
   never a dirty tree.
5. The validator runs the harness phases the table gives for plan phase `N` — **both of
   them where two are named** — and inspects the new JSON results.
6. Validation passes only when the harness root gate ran first and passed, the table's
   row for plan phase `N` is satisfied in **all three of its columns**, **no gate is
   `BLOCKED`**, every `.reject.` fixture fails for its declared reason, every `.accept.`
   fixture validates, results are written, and the worktree is clean.
7. On failure, the implementer fixes the cause, the reviewer rechecks, the coordinator
   **amends** the unshared candidate commit, and validation repeats from 5.
8. Advance only after review returns `APPROVE` and validation returns `PASS`.

### The table

`S` is the number of gates registered under the simplification family — the `FR-P5-`
prefix in `tests/gates/registry.py` — **at the moment of the run**. The validator counts
it from the registry; it is never a literal typed here, because a literal goes stale the
moment a phase adds a gate. `S` is **1** when stage A begins and rises only by §Adding a
gate below.

**Two invariants hold at every row and are the regression contract:**

- **R1** — `./tests/run_gates.sh 4` reports **31 PASS, 0 FAIL, 0 BLOCKED, `S` SKIPPED**.
  The 31 are the folder family, entire. That number never moves in this plan. If a change
  costs one of them, the change is wrong, not the gate.
- **R2** — `./tests/run_gates.sh 5` reports **0 BLOCKED, 0 SKIPPED**, and `PASS + FAIL`
  equals `31 + S`.

| Plan phase | Delivers | Harness runs | The row's own expectation |
|---|---|---|---|
| **0** — prove the split | the inventory, `../plan/simplification.phase0.result.v1.md` | `run_gates.sh 5` | R2 with **31 PASS, 1 FAIL, `S`=1**. The FAIL is `FR-P5-ENGINE-GENERIC`, reporting **3 files** under `engine-names-curriculum-path` — `meta_prompt/assets/inputs.v1.md`, `policy/calibration.v1.yaml`, `policy/checks.v1.yaml` — and **(b) 0 of 37** engine-owned ids. The deliverable exists: re-run the gate against the tree, confirm the note still describes it, and pass on the record, not on the colour. |
| **4** — generic checks | readability band, Bloom verbs, cross-document derivation, hash resolution — each with a `reject` fixture | `run_gates.sh 4` **and** `run_gates.sh 5` | R1 with `S` = 1 + the gates this phase registers. R2 with **PASS = 31 + (S−1)** and **1 FAIL**, still `FR-P5-ENGINE-GENERIC` on the same 3 files: this phase touches no engine content, so the measurement must not move. Every gate this phase adds passes at harness phase 5. |
| **1** — the unit contract (G1, G5) | `lab.schema.v4.json`, `curriculum.schema.v5.json` | `run_gates.sh 4` **and** `run_gates.sh 5` | R1, R2 with **PASS = 31 + (S−1)**, **1 FAIL**, and `FR-P5-ENGINE-GENERIC` still on the same 3 files. A schema gains a `domain` block; no leak closes here. |
| **2** — the verifier contract | `arduino_kit` declares its verifier, its fixtures and `circuit_policy: composed`; a curriculum without one is refused | `run_gates.sh 4` **and** `run_gates.sh 5` | R1, R2 with **PASS = 31 + (S−1)**, **1 FAIL**, same 3 files. The declaration lands under `curricula/`, which the gate does not scan. |
| **3** — the check inventory (G3, G7) | engine checks stay in `policy/checks.v1.yaml`; domain checks move to `curricula/<name>/checks.v1.yaml`; `calibration.v1.yaml`'s precedence comments are generalised | `run_gates.sh 4` **and** `run_gates.sh 5` | R1, R2 with **1 FAIL** — `FR-P5-ENGINE-GENERIC` still fails, and **this is the phase's evidence**: it must now report **(a) 1 file**, `meta_prompt/assets/inputs.v1.md` alone. `policy/checks.v1.yaml` and `policy/calibration.v1.yaml` gone from the report is `G3` and `G7` closed. Either still present is the phase incomplete, whatever the diff looks like. |
| **5** — the prompt (§5), then retire the meta level | `meta_prompt/curriculum.prompt.v1.md`; `tests/meta_prompt_source.py` repointed; the rest of `meta_prompt/` retired | `run_gates.sh 4` **and** `run_gates.sh 5` | R1. R2 with **PASS = 31 + S, 0 FAIL** — `FR-P5-ENGINE-GENERIC` **passes**, and here it is an acceptance criterion, not a measurement. Before accepting it, the validator confirms the gate scanned the new prompt: the file `tests/meta_prompt_source.py` names must be `meta_prompt/curriculum.prompt.v1.md` and must exist outside `deprecated/`. |

A row that asserts a count the harness does not produce is a defect in this prompt, to be
reported as such — not a licence to adjust the harness, and not something to fix by
editing this file mid-run.

### Evidence per plan phase: a gate, or review and fixtures

Passing gates evidence a phase only where a gate for that phase exists. This is stated
per phase so no reader infers it.

| Plan phase | Evidence | |
|---|---|---|
| **0** | **gate** — `FR-P5-ENGINE-GENERIC`, already registered and catalogued at the plan's §9, plus the result note | nothing to add |
| **4** | **gate — this phase must add one per check it makes executable.** The plan's §6 phase 4 names four: readability band, Bloom verbs against declared level, cross-document derivation, hash resolution. A check advertised without an executed assertion is failure B3. `TEXT-BLOOM-VERBS` **flags and never blocks** — its gate asserts that the flag is raised and recorded, never that a Bloom verdict is correct; human raters agree with each other only 46.58% of the time | see §Adding a gate |
| **1** | **gate — this phase must add one.** The unit contract's shape is mechanically checkable today: six engine blocks plus a `domain` block validated against a curriculum-supplied schema, no engine block named for a domain, and `kit_power_profile`/`visual_system` no longer top-level in the curriculum schema | see §Adding a gate |
| **2** | **gate — this phase must add one.** The refusal is the assertion: a fixture curriculum with no declared verifier, and one whose fixtures have not been executed, must both be refused at startup. The plan's §3 makes this the precondition that lets the engine be generic without being unsafe, and a precondition nothing exercises is a sentence | see §Adding a gate |
| **3** | **review and fixtures, plus the existing gate's report.** No new gate: `FR-P5-ENGINE-GENERIC` already measures exactly what this phase changes, and its file list shrinking from three to one is a stronger signal than a second detector agreeing with it. The reviewer additionally confirms both inventories validate against the same schema and that no check id was dropped rather than moved | none |
| **5** | **the existing gate, now as acceptance**, plus review. The six extracted rules must resolve from outside `meta_prompt/` before anything there is retired — precedence (`inputs.v1.md:63-89`), the recorded divergences (`:96-100`), no hardcoded count (`:102-104`), one parent (`architecture.v1.md:44-50`), grounding (`:52-57`), no model for deterministic work (`routing.v1.md:23-25`). The reviewer verifies each by resolving it in the new prompt, one by one, and names where | none |
| **6** | **neither — the L01 test is the evidence**, and it is stage B below, not a harness run. The plan's §7 states why: nothing in this repository executes a model, renders a PDF or fetches a source, so plan phases 6 and 7 get an `RT-` id in `policy/deferred.v1.yaml` rather than a gate that cannot run. Do not add a gate here, and do not report a static or simulated pass as generated coverage. Stage A's rows end at plan phase 5; this row exists so the reader is never left inferring that a missing row means a missing requirement | none |

Surfaced and not acted on, because no phase currently owns it: leg **(b)** of the
measurement is armed and near-blind. It matches engine check ids against the terms a
curriculum *declares about itself*, and today the only declaration is `kit_terms` —
seven proper nouns. `LAB-CURRENT-MARGIN` and `LAB-VALUE-SOURCED` are engine-owned domain
assertions the gate cannot see, because no curriculum declares `current` or `value` as a
term of its domain. `../plan/simplification.phase0.result.v1.md` records this and reasons
that a `domain_terms` block belongs beside plan phase 2's verifier declaration. **The
plan does not require it.** Report it under its own `RT-` id; do not add it to a phase
from inside a run.

### Adding a gate to this family

Four things, and only one of them is code:

1. **A catalogue entry in the plan's §9**, in the encoding that section fixes — everything
   after an em dash in a header field is rationale, and `depends_on` is the set of
   backticked `FR-` ids in that field. Append; never renumber, because other documents
   cite the plan's sections by number.
2. **A registry entry** in `tests/gates/registry.py` with `activation_phase: 5`, so that
   `./tests/run_gates.sh 4` stays at 31 gates and the folder plan's regression run never
   reports this plan's failures.
3. **The id's prefix listed in `tests/gates/gate_families.v1.yaml`** under the
   `simplification` family. `FR-P5-` is already there, so an id beginning `FR-P5-` needs
   nothing. **An id with any other prefix needs the manifest entry**, or `FR-P0-REGISTRY`
   reports `gate-family-unowned` and fails — which is the reject fixture doing its job,
   not a defect to work around. Adding a family is data, not code.
4. **An `.accept.` and a `.reject.` fixture**, with the reject fixture's `expected_error`
   naming every code it must trip, per the existing convention.

## Loop — stage B, plan phase 6, the L01 test

This is the test that decides whether the prompt works. Run
`meta_prompt/curriculum.prompt.v1.md` against `curricula/arduino_kit/`, unit `L01`.

Iterate until every condition holds:

| # | Condition |
|---|---|
| 1 | the run **read no path outside** the curriculum root and the engine layer, and wrote only under the output root |
| 2 | the unit validates against the plan phase 1 unit schema, every block present |
| 3 | the curriculum's declared **domain verifier executed** and passed, and its own fixtures were executed in the same run |
| 4 | every generic check passed: schema, readability band, Bloom verbs against declared level, cross-document derivation, receipt hash resolves in the shipped artifact |
| 5 | every domain value carries a source **fetched during this run**, by exact identifier, and each hash resolves |
| 6 | prose, tables and diagrams are derivable from the domain data — one parent, checked mechanically, not asserted |
| 7 | exactly one judge ran per pass, from a different model family, and its verdict is recorded with the rubric and the presentation order |
| 8 | the artifact rendered, every page rasterised and inspected |

On any failure: the implementer fixes **the named cause only** — the prompt, a check, a
schema, or the curriculum's verifier — never the acceptance criteria. Re-run from
condition 1. The whole test re-runs; a repaired condition is not spot-checked in
isolation.

## Iteration budget and the stall rule

The coordinator owns both.

- **Six correction cycles per plan phase.** Exceeding it is `HALTED`, not a seventh cycle.
- **Every cycle must narrow the failing set.** If the identical failing set recurs twice,
  stop as `HALTED` and report the set. Repeating a fix that did not work is the loop this
  project has already run six times at the meta level.
- **Two cycles that add artifacts without reducing failures** is `HALTED`. Complexity
  that does not buy a pass is drift.
- Record every cycle: what failed, what changed, what the next run measured.

## Standing constraints

- **Do not confuse the prompt you are writing with the prompt you are executing.** This
  file is the executor. `meta_prompt/curriculum.prompt.v1.md` is the deliverable. Editing
  this file to make the deliverable pass is the failure this project is named after.
- **A failing measurement is not a failing run.** Through plan phases 0, 4, 1, 2 and 3 —
  every plan phase before 5, in the order stage A runs them — `FR-P5-ENGINE-GENERIC`
  failing is the expected state and `./tests/run_gates.sh 5` exiting non-zero is expected
  with it. Deleting a leak early to make a plan phase green destroys the inventory that
  plan phase 0 exists to produce.
- **Schedule a leak; never silence one.** An exclusion in the gate, an exemption in a
  manifest, or a scan root that stops covering a live file is the defect the gate detects.
- **The output is a draft, and the report must say so.** Per the plan's §4(b), no human
  reads or signs anything inside the run. The pipeline's claim is "every declared
  automated check passed" — never "child-ready", never "reviewed". Downstream human
  review exists but is outside this run's scope and must not be reported as performed.
- **L01 cannot prove the domain verifier, and the report must say so.** L01 is
  `safe-power`: unpowered, polarity-neutral, and forbidden from labelling a connector
  terminal. Current limiting, polarity and supply match — the ERC rules that matter — are
  **not exercised by it**. Passing the L01 test proves the pipeline end to end. It does
  not prove electronics is safe to generate. Report those as two separate claims, and
  never let the first be read as the second. That is failure A5.
- **Extraction precedes retirement.** Plan phase 5 writes the prompt before anything under
  `meta_prompt/` moves to `deprecated/`. Six rules exist nowhere else — precedence
  (`inputs.v1.md:63-89`), the recorded divergences (`:96-100`), no hardcoded count
  (`:102-104`), one parent (`architecture.v1.md:44-50`), grounding (`:52-57`), and no
  model for deterministic work (`routing.v1.md:23-25`). Retiring first destroys them.
- **A missing verifier is a refusal, not a warning.** A curriculum with no declared,
  executable, fixture-proven domain verifier does not run. This is the plan's §3 and it
  is the whole reason the engine can be generic without being unsafe.
- **`circuit_policy: composed` is declared, not assumed.** Plan phase 2 adds the
  declaration to `arduino_kit_curriculum.v4.yaml` alongside the verifier. If plan phase 6
  finds it absent, that is a plan phase 2 defect, not a licence to default.
- **The engine never learns the domain.** If a fix requires the word "circuit",
  "datasheet", "kit" or "voltage" in `policy/`, `schemas/` or the prompt, the fix is in
  the wrong layer. Put it in `curricula/arduino_kit/`.
- **Fixing a check versus weakening it.** A check's implementation may be corrected when
  it misreads its subject — wrong scan root, bad regex, misparsed path. Record it as
  `gate_impl_fix` with a one-line reason and have the reviewer re-check it. A check's
  **acceptance criteria** may never be relaxed to make a failing repository pass. If the
  repository is what is wrong, fix the repository or return `HALTED`.
- **Never report a static or simulated pass as generated coverage.** "The engine handles
  any curriculum" and "a curriculum exists" are different claims.
- **`TEXT-BLOOM-VERBS` flags and never blocks.** Human raters agree with each other on
  Bloom level only 46.58% of the time.
- **Never report an unexecuted check as passing**, and never report a gate recorded
  `BLOCKED` as one that ran.
- **`git` on this filesystem fails intermittently** with `.git/index: unable to map index
  file` and `mmap failed: Operation timed out`. Every git-invoking gate then fails for the
  environment rather than for the repository. Re-run before treating such a failure as
  real, and never record an environment failure as a repository defect — or the reverse.
- **Scope is plan phases 0–6.** Plan phase 7 — a second curriculum in an unrelated domain
  — is the plan's actual proof of genericity and is **not** in this run. Until it runs,
  report genericity as *structurally enforced, not demonstrated*.
- **Anything in the plan's §8 is out of scope.** Surface it under its `RT-` id; do not act
  on it.

## Finish

Return `APPROVED` only when: stage A passes at every plan phase against its own row of
the table; `./tests/run_gates.sh 4` reports 31 PASS and 0 FAIL at the end as it did at
the start; `./tests/run_gates.sh 5` reports 0 FAIL with `FR-P5-ENGINE-GENERIC` **passing
against the live prompt** `tests/meta_prompt_source.py` names; the L01 test passes all
eight conditions; the six extracted rules resolve from outside `meta_prompt/`; the
worktree is clean; and the report states, separately and in these terms, (a) that the
pipeline produced one unit, (b) that the unit is a draft pending downstream human review,
per the plan's §4(b), (c) that L01 did not exercise the powered-circuit path, and (d)
that genericity is structurally enforced and not yet demonstrated.

Otherwise return `HALTED`, naming the failing gate id or test condition and its stated
failure meaning — and, where the cause is external or needs a decision, the exact blocker
or decision required.
