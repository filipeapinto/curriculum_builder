# Folder refactoring — plan v6

**Date:** 2026-07-30
**Supersedes:** `deprecated/folder_refactoring.plan.v5.md` (and, through it, v4–v1)
**Status:** accepted, not started. No file has been moved or edited under this plan.
**Scope:** folder layout, file placement, the references that name them, the three data
contracts phase 2 depends on, and a committed harness that proves each phase. Not
curriculum content. Not a runtime implementation.

**v2** gave every gate a stable ID, an activation phase, an exact command, pass criteria,
a rejection fixture where one applies, and a stated failure meaning. Gates are cumulative.
**v3** fixed nine defects of intent. **v4** fixed four defects of mechanism.
**v5** fixed six more, and expanded phase 2 to author the contracts its gates depend on.

**What v6 adds over v5.** Six fixes, two of which are ordering or identity defects that
would have failed on the first run:

1. **A prerequisite ran after its dependant.** ID order puts `FR-P2-BYPASS-DECLARED`
   before `FR-P2-CONTRACT-VERSIONED`, which authors the fields it reads. Fixed
   generically, not by renaming: the registry now carries `depends_on`, and the runner
   topologically sorts within a phase, breaking ties by ID. `FR-P0-HARNESS` stops being a
   special case and becomes the root dependency of every gate. A gate whose dependency
   failed is reported `BLOCKED (dependency …)` — never skipped, never passed.
2. **`§12 follow-up id` was not an identifier.** Two gates required one; §12 had prose
   bullets and no ids, so their acceptance criteria could not be evaluated the same way
   twice. Six stable ids `RT-1 … RT-6` now exist in **`policy/deferred.v1.yaml`** — a
   manifest, because code reads it (§1) — mirrored by §12 for humans, with `FR-P2-DEFERRED`
   proving the two agree and that every reference resolves.
3. **v1 and v2 contracts were both authorized.** `FR-P2-BOUND` required both versions in
   the authorized-input table while §6 retains v1 only for validating already-accepted
   work. The table now authorizes **v2 only**; v1 moves to a separate retained-contracts
   table, and naming a v1 in authorized inputs is a gate failure.
4. **"The model-call pattern" was free text.** A record could evade `decision_id` by
   rewording its `action`. `execution_log.schema.v2.json` now requires a typed
   discriminator `action_kind`, and the conditional keys on `action_kind: model_call`.
5. **Claim classes understated what gates do.** Seven gates declared `schema` while also
   scanning text or resolving references across files. All are corrected — and
   `FR-P0-REGISTRY` now compares each gate's declared class against the mechanisms its
   implementation reports, so the labels cannot drift again.
6. **`FR-P3-CAPS-OWNED` would have failed on `1`, `2`, `required`.** Bare value scanning
   is now forbidden. Each cap declares a `prose_pattern` in `policy/calibration.v1.yaml`;
   the gate matches only that, and a cap with no pattern is a failure, not a skip.

Two items the review classed as minor are also fixed, since they are single clauses: the
unverified "39 check ids" count is no longer asserted, and phase 4's schema tally is
stated as a list rather than a number.

*One disagreement, recorded:* fix 5 is ranked **medium** here, not high. A wrong claim
class misdescribes evidence but never makes a gate pass something it should fail. It
matters because the whole plan leans on claim discipline — which is why
`FR-P0-REGISTRY` (d) now enforces it mechanically rather than by review.

---

## 1. The rule

Every file lives where its reader is.

| Folder | Consumer | Form |
|---|---|---|
| `policy/` | **code** — the controller, preflight, the gate suite | `*.yaml` (+ a folder-index `readme.md`, which is a human's map of the directory and never an input to a run) |
| `meta_prompt/` | **a model** — prose instructions | `*.md` |
| `schemas/` | **a validator** | `*.json` |
| `curricula/<name>/` | one curriculum's facts and evidence | mixed, by nature |
| `tests/` | **code** — the gate harness itself | `*.py`, `*.sh`, fixtures |
| `docs/` | a human, for orientation only | `*.md`, `*.typ`, images |
| `plans/` | a human, for history | `*.md` + archived code |

The rule is checkable by file extension, which is why it was chosen over grouping by
subsystem. Two consequences follow that the current tree violates: a YAML inside
`meta_prompt/` is misplaced (the four routing manifests), and a constraint-bearing
prose file at the repo root is misplaced (`pedagogy.md`).

It is also why the deferred-work registry (fix 2) is `policy/deferred.v1.yaml` and not a
section of this plan: two gates read it, and gates read `policy/`, not `plans/`.

Root holds only what a human or tool expects at top level: `AGENTS.md`, `readme.md`,
`.gitignore`.

---

## 2. Why `assets/` is being renamed

The folder is named after static media. It contained exactly one real asset,
`official_kit_photo.jpg`, which has already moved to `curricula/arduino_kit/`. What
remains is six manifests of rules — including `calibration.v1.yaml`, whose own header
states it outranks every prose document in the project. `policy/` names what they are:
the rules that bind a run.

`policy/` is engine-wide. It is not the policy of one curriculum and not the policy of
the meta prompt; it binds every run of the generator regardless of curriculum.
`calibration.v1.yaml` is the one file with a learner-specific part, which is why its
kit-specific power block splits out in phase 3.

---

## 3. State at the time of writing

Two renames are mid-flight and neither is finished. This is why phase 0 is a single
atomic commit.

- `schema/` → `schemas/` happened on disk **outside version control**: `git status` shows
  four deletions under `schema/` plus an untracked `schemas/`. **22 live references
  still say `schema/`** — `assets/calibration.v1.yaml` (8), the meta prompt (6),
  `assets/checks.v1.yaml` (3), `AGENTS.md` (2), `docs/how_it_works.md` (2),
  `pedagogy.md` (1).
  **Consequence for §5:** `git mv` cannot be used on these four files, because the source
  paths no longer exist in the working tree. Git records snapshots and detects renames
  from content, so history is recoverable — see the staging rule in §5.
- Four kit files moved into `curricula/arduino_kit/` earlier
  (`arduino_kit_curriculum.v4.yaml`, `kit_evidence.md`, `official_kit_photo.jpg`,
  `lab_brief.md`) and no reference was updated. `AGENTS.md:16`'s validation command
  opens `assets/curriculum.v4.yaml`, which no longer exists, so it fails today.
- `meta_prompt/deprecated/` exists on disk, is empty, and is therefore absent from the
  baseline commit — a convention that disappears on clone.
- `.pytest_cache/v/cache/nodeids` is `[]`. No automated test has ever been collected.
  The harness in §7 is the first executable check in this repository.
- **The two contracts phase 2 needs are missing fields.** Verified 2026-07-30:
  - `routing_decision.schema.v1.json:5` requires
    `task_id, task_class, risk, candidate_pool, selected_model, reasoning_effort,
    quality_gate, decision_rationale, status` — nine fields. There is no `decided_model`
    and no `executed_model`, so "the executed route differs from the decided route" is
    not expressible at all.
  - `execution_log.schema.v1.json` `$defs.act.required` is
    `id, date, action, status, input_quality, authorized_paths, trigger, expected,
    result`. There is no `decision_id`, and `action` is an unconstrained string — so
    neither "a model call with no decision record" nor even "this record *is* a model
    call" is expressible.
  Phase 2 authors `v2` of both, and adds a typed `action_kind` so the second question has
  an answer that wording cannot dodge. See §9.
- **There is no deferred-work registry.** Gates that must say "this obligation is real but
  belongs to the follow-up" have nothing stable to point at. Phase 2 creates
  `policy/deferred.v1.yaml` with ids `RT-1 … RT-6` (§12).
- **There is no controller implementation.** The only runner in the repository is
  `assets/legacy/run_curriculum.v3.py`, which this plan archives to `plans/legacy_v3/`
  as evidence. Nothing in scope executes a model, records a routing decision, renders a
  PDF, writes an execution log, or transitions a controller state. Every gate in §8 is a
  static check over files, and §8 says so per gate. See §12.

---

## 4. Target tree

```
curriculum_builder/
├── AGENTS.md                                   conventions + the retention rule
├── readme.md
├── .gitignore                                  ignores tests/results/*.json — see §7
│
├── policy/                                     DATA CODE READS            ← was assets/
│   ├── calibration.v1.yaml                     premise: learner, caps + prose_pattern, safety floor
│   ├── checks.v1.yaml                          the stable check ids
│   ├── controller.v1.yaml                      states, transitions, ownership, CLI
│   ├── limits.v1.yaml                          numeric ceilings + flags
│   ├── routes.v1.yaml                          external capabilities, proven by execution
│   ├── failures.v1.yaml                        A1–A10, B1–B4
│   ├── deferred.v1.yaml                        NEW (phase 2) — RT-1…RT-6, mirrors §12
│   ├── routing/                                ← from meta_prompt/routing/
│   │   ├── readme.md                           file index only
│   │   ├── model_registry.v1.yaml
│   │   ├── task_taxonomy.v2.yaml
│   │   ├── routing_policy.v1.yaml
│   │   └── quality_gates.v1.yaml
│   └── deprecated/.gitkeep
│
├── curricula/
│   ├── arduino_kit/
│   │   ├── arduino_kit_curriculum.v4.yaml
│   │   ├── kit_calibration.v1.yaml             NEW — split from calibration (phase 3)
│   │   ├── kit_evidence.md
│   │   ├── official_kit_photo.jpg
│   │   ├── lab_brief.md
│   │   ├── roster.md                           ← assets/
│   │   ├── teacher_framework.md                ← assets/
│   │   ├── teacher_audit.md                    ← assets/
│   │   ├── l01_unpowered_power_path.json       ← assets/
│   │   └── fixtures/
│   │       └── l01_polarity_asserted.reject.json   ← assets/fixtures/
│   └── deprecated/.gitkeep
│
├── schemas/                                    CONTRACTS A VALIDATOR READS
│   ├── curriculum.schema.v4.json
│   ├── lab.schema.v3.json
│   ├── calibration.schema.v1.json              EDITED (phase 3) — power block out,
│   │                                           prose_pattern required
│   ├── kit_calibration.schema.v1.json          NEW (phase 3)
│   ├── execution_log.schema.v1.json            RETAINED — accepted work validates here
│   ├── execution_log.schema.v2.json            NEW (phase 2) — action_kind + decision_id
│   ├── routing_decision.schema.v1.json         ← meta_prompt/routing/   RETAINED
│   ├── routing_decision.schema.v2.json         NEW (phase 2) — decided + executed model
│   ├── checks.schema.v1.json                   NEW (phase 4) ┐
│   ├── controller.schema.v1.json               NEW (phase 4) │ one per policy/*.yaml;
│   ├── limits.schema.v1.json                   NEW (phase 4) │ the seventh, calibration,
│   ├── routes.schema.v1.json                   NEW (phase 4) │ already exists above
│   ├── failures.schema.v1.json                 NEW (phase 4) │
│   ├── deferred.schema.v1.json                 NEW (phase 4) ┘
│   ├── circuit_data.schema.v1.json             NEW (phase 4)
│   ├── model_registry.schema.v1.json           NEW (phase 4) ┐
│   ├── task_taxonomy.schema.v2.json            NEW (phase 4) │ one per routing manifest;
│   ├── routing_policy.schema.v1.json           NEW (phase 4) │ they share no structure
│   ├── quality_gates.schema.v1.json            NEW (phase 4) ┘
│   └── deprecated/.gitkeep                     gated — see §6
│
├── meta_prompt/                                PROSE A MODEL READS — see the note below
│   ├── meta_curriculum_builder.prompt.v6.md    the contract: mission, boundary, assets, order of work
│   ├── assets/                                 the rest of that contract, and its companions
│   │   ├── inputs.v1.md                        section: inputs, retained contracts, precedence
│   │   ├── architecture.v1.md                  section: what the generator and a lab must be
│   │   ├── routing.v1.md                       section: which model serves which task
│   │   ├── proving.v1.md                       section: the six gates and the release gates
│   │   ├── logging.v1.md                       section: action log, convergence, drift
│   │   ├── deliverables.v1.md                  section: what V7 must contain
│   │   ├── component_lab_template.v1.md        companion: how to write a lab
│   │   ├── pedagogy.v1.md                      companion: why the pedagogy fields exist ← root
│   │   └── model_selector_prompt.v1.md         companion: the selector's own prompt ← meta_prompt/routing/
│   ├── docs/                                   orientation only, never a constraint
│   │   └── how_the_meta_prompt_works.html      the contract explained, with diagrams
│   └── deprecated/.gitkeep                     + the v5 prompt, superseded, read by nobody
│
├── tests/                                      THE GATE HARNESS — see §7
│   ├── run_gates.sh
│   ├── gates/
│   │   ├── registry.py                         id, activation_phase, claim class,
│   │   │                                       depends_on — all 31 gates
│   │   └── …
│   ├── fixtures/                               NEVER scanned by a production check
│   ├── selftest/                               proves the harness itself
│   └── results/.gitkeep                        *.json ignored
│
├── docs/                                       ORIENTATION ONLY, never constraints
│   ├── how_it_works.md · how_it_works.typ · how_it_works.png
│   └── infographic.prompt.v1.md
│
└── plans/
    ├── folder_refactoring/
    │   ├── folder_refactoring.plan.v6.md       this file — the active plan
    │   ├── folder_refactoring.prompt.v6.md     the active execution prompt
    │   └── deprecated/                         plan+prompt pairs v1–v5 (10 files)
    ├── fix_curriculum_meta_prompt/
    │   ├── research/redundancy.analysis.v1.md
    │   └── prompts/remediation.plan.promptv7.md + deprecated/v1–v6
    └── legacy_v3/                              ← assets/legacy/
        ├── run_curriculum.v3.py
        ├── component_lab_orchestrator_prompt.v3.md
        └── full_run_preflight.v3.md
```

`meta_prompt/routing/` ceases to exist: its four YAMLs and its readme go to
`policy/routing/`, its prompt to `meta_prompt/`, its schema to `schemas/`.

**The `meta_prompt/` block above is this plan's record and is not the live asset set.**
`simplification.plan.v3.md` §6 phase 5 replaced the v6 prompt and its six `section`
assets with one file, `meta_prompt/curriculum.prompt.v1.md`, and retired the rest under
`meta_prompt/deprecated/`. A finished plan's tree records what was true when that plan
completed, so it is left as written. The live shape is declared in two places that are
compared against each other — `EXPECTED` in `tests/meta_prompt_source.py` and the
`### Contract assets` table in `AGENTS.md` — and this tree is read by neither.

Both `v1` contracts stay in `schemas/`, never in `schemas/deprecated/` (§6) — and, per
fix 3, neither may appear in the meta prompt's authorized-input table.

---

## 5. Moves

**13 rules, 26 files.** `FR-P0-TREE` enumerates all 26 destination files, not the 13 rows.

| # | From | To | Files | Reason |
|---|---|---|---|---|
| 1 | `schema/*.json` | `schemas/` | 4 | already on disk; commit it |
| 2 | `assets/*.yaml` | `policy/` | 6 | rules, not assets |
| 3 | `assets/legacy/` | `plans/legacy_v3/` | 3 | history cited as evidence; `plans/` owns history |
| 4 | `assets/roster.md` | `curricula/arduino_kit/` | 1 | ELEGOO-specific |
| 5 | `assets/teacher_framework.md` | `curricula/arduino_kit/` | 1 | ELEGOO-specific |
| 6 | `assets/teacher_audit.md` | `curricula/arduino_kit/` | 1 | ELEGOO-specific |
| 7 | `assets/l01_unpowered_power_path.json` | `curricula/arduino_kit/` | 1 | L01 circuit data |
| 8 | `assets/fixtures/l01_polarity_asserted.reject.json` | `curricula/arduino_kit/fixtures/` | 1 | kit-specific fixture |
| 9 | `pedagogy.md` | `meta_prompt/assets/pedagogy.v1.md` | 1 | constraint-bearing prose; versioned per `AGENTS.md:29` |
| 10 | `meta_prompt/routing/*.yaml` | `policy/routing/` | 4 | data code reads |
| 11 | `meta_prompt/routing/readme.md` | `policy/routing/` | 1 | index of those files |
| 12 | `meta_prompt/routing/model_selector_prompt.v1.md` | `meta_prompt/assets/` | 1 | prose a model reads |
| 13 | `meta_prompt/routing/routing_decision.schema.v1.json` | `schemas/` | 1 | all contracts in one folder |

Nothing is deleted. Phases 2–4 *add* files; they move none.

Rows 9 and 12 name `meta_prompt/assets/` rather than `meta_prompt/`, and §4 shows that
folder, because a later piece of work — splitting the meta prompt into a short contract
plus the `section` and `companion` assets it names — moved both files one level down.
Their phase-0 destination was `meta_prompt/`; `git log --follow` still reaches the
baseline through both renames, which is what `FR-P0-HISTORY` proves. §4 and §5 state
where each file **is**, so the gates reading them stay a test of the repository rather
than of a frozen snapshot; §10's ledger is the phase-0 record and is not rewritten.

**How to move, so that history follows.**

- **Rules 2–13 — sources still exist in the working tree.** Use `git mv`.
- **Rule 1 — the source no longer exists.** `git mv schema/x.json schemas/x.json` fails:
  there is nothing at the source path (§3). Git stores snapshots and detects renames from
  content, so history is intact provided **both sides are staged in the same commit** and
  the check below runs **before any content edit**:

  ```
  git add -A schema schemas
  git diff --cached --name-status -M100%     # expect exactly four R100 lines,
                                             # no D/A pair for the same basename
  ```

  `git diff --cached --name-status` is the only one of the three forms that prints a
  similarity score. `git status --porcelain -M` prints a bare `R`, and `git show --stat`
  prints no name-status at all.

  **Then, and only then, apply §10's content edits.** §10 edits
  `schemas/lab.schema.v3.json:59`, which drops that file's similarity below 100%. This is
  expected: the pre-edit `R100` check proves the rename was staged as a rename, and
  `git log --follow` proves the history survived the commit. **The final commit will not
  contain four `R100` entries, and must not be required to.**

---

## 6. Retention: three words, three meanings

- **`deprecated/`** — superseded by a newer version of the same artifact. Retained for
  history. **Nothing may read it.**
- **`legacy_v3/`** — a prior *system*, retained as evidence and **actively cited**.
  `failures.v1.yaml` requires a path and line from it for every A-series defect, so its
  citations are updated in phase 0 and never broken again.
- **`name.vN.ext`** — in-place coexistence while both versions are live.

Every empty `deprecated/` gets a `.gitkeep`, or it will not survive a clone.

`schemas/deprecated/` is **gated**: a schema may enter it only when zero accepted
artifacts and zero manifests reference it. Schema paths appear in
`calibration.enforced_by`, in `checks.v1.yaml`, and in the audit records of accepted
labs; `--resume` refuses to mutate accepted work, so the contract a lab was accepted
under must keep resolving at a stable path. Supersession happens in place via the
version suffix. The folder starts empty and stays empty until a retirement is provably
safe — enforced by `FR-P1-SCHEMA-RETENTION`.

**Retained is not authorized.** A `vN` kept for historical validation is readable by a
validator checking old records and by nothing else. It must not appear in the meta
prompt's authorized-input table, because a new run may not be validated against a
superseded contract. `FR-P2-BOUND` enforces the distinction; §12's `RT-6` is what
eventually retires v1.

**This is why phase 2 adds `v2` contracts instead of editing `v1`.** Any execution log or
routing decision already accepted was validated against `v1`; editing `v1` in place would
retroactively invalidate it.

`docs/` has no `deprecated/`: its explainers are regenerated from `.typ`, and an archive
of stale claims is a drift risk rather than a record.

---

## 7. The harness

**Location:** `tests/`, committed. Consumer is code, so it obeys §1.

```
tests/
├── run_gates.sh                  ./tests/run_gates.sh <phase>   → dependency order,
│                                 ties by ID, gates with activation phase ≤ <phase>
├── gates/
│   ├── registry.py               EVERY gate: id, activation_phase, claim class,
│   │                             depends_on — declared at phase 0, implemented per phase
│   ├── common.py                 path constants, scan roots, fixture runner, recorder
│   ├── fr_p0_structure.py        FR-P0-*
│   ├── fr_p1_retention.py        FR-P1-*
│   ├── fr_p2_selector.py         FR-P2-*
│   ├── fr_p3_calibration.py      FR-P3-*
│   ├── fr_p4_policy_schemas.py   FR-P4-*
│   └── selftest.py               FR-P0-HARNESS — proves the harness, see rule 8
├── fixtures/                     negative fixtures <subject>.reject.<ext>;
│                                 positive fixtures <subject>.accept.<ext>
├── selftest/                     synthetic inputs for selftest.py only
└── results/.gitkeep              gate_results.p<phase>.<utc-timestamp>.json — ignored
```

**Harness contract — eight rules, none optional.**

1. **Gate IDs are `FR-P<phase>-<NAME>`.** The `FR-` prefix keeps refactor gates
   distinguishable from the curriculum check ids in `policy/checks.v1.yaml` (`CAL-`,
   `CUR-`, `L01-`, `LAB-`, `PDF-`, `LOG-`, `REV-`, `DRIFT-`, `SEL-`). A refactor gate
   never appears in `checks.v1.yaml`, and **a curriculum check never appears in
   `tests/gates/`** — which is why no gate in §8 may require a curriculum check to be
   *executed by this harness*. What this harness can prove about a curriculum check is
   that it is declared, owned, and mapped to a verification method. See rule 6 and §12.
2. **One registry; dependency order; cumulative execution.**
   `tests/gates/registry.py` lists **every** gate in §8 with its `activation_phase`,
   claim class and `depends_on` list, from the first commit onward — a later gate is
   declared before it is implemented.
   `run_gates.sh N` builds the subgraph of gates with `activation_phase <= N`,
   **topologically sorts it, breaking ties by ID**, and runs it in that order. Later
   gates are *skipped* with an explicit `SKIPPED (activates at phase M)` line.
   - `FR-P0-HARNESS` is the root: every other gate depends on it, directly or
     transitively. This replaces v5's "harness first, then ID order" special case, which
     ID order alone contradicted.
   - A gate whose dependency **failed or was itself `BLOCKED`** is reported
     `BLOCKED (dependency <ID> <failed|blocked>)` — it is not run, not skipped, and never
     counted as a pass. `BLOCKED` **propagates transitively** down the graph. It is a
     distinct outcome in the result record, and it is a **gate-level** outcome only: the
     run-level verdict for "this phase cannot be approved" is `HALTED`, never `BLOCKED`,
     so the two can never be confused in a report.
   - A dependency **cycle** is a hard error: the run aborts before any gate executes.
   - A skip is recorded, never silent. A declared-but-unimplemented gate whose phase has
     arrived is a **failure**, not a skip.
3. **A negative fixture must fail for its stated reason; a positive fixture must pass.**
   Every `.reject.` fixture declares an `expected_error` pattern; failing for a different
   reason — a parse error where a constraint violation was expected — is a **gate
   failure**, not a pass. Where a rule is conditional, the gate also carries an
   `.accept.` fixture that must validate, proving the condition is not over-broad.
4. **Results are recorded, never asserted.** Each run writes one JSON file to
   `tests/results/` containing, per gate: id, activation phase, declared claim class,
   **mechanisms actually used**, `depends_on`, command, exit code, stdout digest, one of
   `PASS | FAIL | SKIPPED | BLOCKED`, and each fixture's outcome with the matched error.
   Files are never overwritten. Per `AGENTS.md:25`, an unexecuted check is never
   reported as passing.
   **`tests/results/*.json` is in `.gitignore`**; the folder is kept by
   `tests/results/.gitkeep`. This is what makes rule 5's two conditions — "results
   written" and "worktree clean" — simultaneously satisfiable, since
   `git status --porcelain` does not list ignored files.
5. **`APPROVED` requires all four:** every gate through the current phase passes; every
   negative fixture failed for its intended reason and every positive fixture validated;
   results are written; the worktree is clean. Any missing element returns **`HALTED`**
   with the specific cause — the run-level verdict, distinct from a gate's `BLOCKED`.
   `HALTED` names what stopped the run whether or not a human is needed; where the cause
   is external or needs a decision, it says so.
6. **Every gate declares a claim class, and may not claim more — or less.** A claim class
   is an **ordered set** of one or more of:
   - `tree` — a path exists or does not exist.
   - `parse` — a file parses.
   - `schema` — an instance validates, or fails to validate, against a JSON Schema.
   - `text` — a string or pattern is present or absent in a tracked file.
   - `mapping` — an id or reference in one file resolves to an owner in another, in both
     directions.
   - `declaration` — a rule is *stated* in a manifest or prompt, a conforming record
     validates while a violating one does not, and any comparison the schema cannot
     express is performed in gate code and recorded as `comparison: python`.
   - `execution` — a program was run and behaved as claimed.

   Printed and recorded joined by `+`, in evidence order, e.g. `schema+mapping`.
   **A gate that reads two files to compare them is at least `mapping`; a gate that
   greps is at least `text`.** Understating is as much a defect as overstating: the
   result record is the only account of what was proven. `FR-P0-REGISTRY` (d) compares
   declared class against the mechanisms each implementation reports, **as sets** —
   evidence order is recorded but never compared, or an implementation that reorders its
   own checks would raise a spurious `claim-class-drift`.

   **The operation→mechanism table is normative.** An implementation reports mechanisms
   from this table and no other, so that (d) compares two things derived from one
   reference rather than two opinions:

   | Operation in gate code | Mechanism |
   |---|---|
   | `os.path.exists` / listing a directory | `tree` |
   | open + deserialize a YAML or JSON file | `parse` |
   | `jsonschema.validate(instance, schema)` | `schema` |
   | regex or substring over file contents | `text` |
   | resolve an id or path found in one file against another | `mapping` |
   | read or import a module under `tests/gates/` to resolve an id against it | `mapping` |
   | import a module under `tests/gates/` in order to call it | `execution` |
   | `subprocess` — `git`, `python3`, the runner | `execution` |
   | all of: state present in prose, record validates, violating record rejected, and **any** residual comparison the schema cannot express performed in gate code | `declaration` |

   **Four subsumption rules**, without which nearly every gate would report `parse` and
   `tree` and the table would say nothing:
   - Deserializing an instance **solely in order to validate it** is reported `schema`,
     not `parse`. `parse` is reported only when parsing is the claim, or when a value is
     read out of the file for some other purpose.
   - Enumerating a directory **solely to select the files to parse or scan** is not
     `tree`. `tree` is the assertion that a *named* path does or does not exist.
   - `declaration` **subsumes** the `text` and `schema` legs it is built from. A gate that
     declares `declaration` reports the composite, never the components as well —
     otherwise (d) drifts in whichever direction the implementer guesses.
   - A mechanism used **only** to reach another mechanism's input is not reported
     separately. The class names what a gate *proves*, not every call it makes.

   Three boundary rules, because each was contested by a real gate:
   - **A scan whose terms are read from another file is `mapping`**, because the term set
     is resolved rather than asserted. `FR-P2-NOVALUES`, `FR-P3-NO-LITERALS` and
     `FR-P3-SPLIT` all depend on this reading.
   - **`schema` means an instance was validated against a JSON Schema.** *Reading* a
     constraint out of a schema file is `mapping` plus, where the file must be loaded,
     `parse`. This is why `FR-P4-AGREEMENT` is `parse+mapping` and not `schema`: its
     `expected_error: limit-missing-value` is a domain name, not a validator message.
   - **`schema` may stand alone only when the instance→schema pairing is *assumed*, not
     *discovered*.** Every validation reads two files, so the maxim above cannot mean
     that `schema` never appears alone. `FR-P0-SCHEMA` and `FR-P4-FIXTURE-BITES` hold
     both paths as literals and are `schema`; `FR-P4-ALL-VALIDATE` resolves the pairing
     from each manifest's own pointer and is `schema+mapping`.

   **No gate claims `execution` of a controller or routing runtime**, because §3 records
   that none exists. Several gates *are* class `execution` — over `python3`, `git` and
   the harness itself, all of which do exist. **This paragraph names no list**: the count
   and membership are derived from §8 by `FR-P0-REGISTRY`, because a hard-coded roster
   here would be a second copy of the class facts that nothing keeps equal — the defect
   this rule exists to prevent. A `declaration` gate says a rule is
   *stated and checkable*, never *enforced at runtime*; a `mapping` gate says an id is
   *owned*, never *executed*.
7. **A production scan never reads a fixture — or a detector.** Every detector takes an
   explicit scan root set. The production set excludes `tests/**` entire —
   `tests/gates/**`, `tests/fixtures/**`, `tests/selftest/**`, `tests/results/**` — plus
   `plans/**` and `.git/**`. A detector is proven against its own fixture by a
   **separate** invocation pointed at the fixture path.
   **`tests/gates/**` is excluded for the same reason as the fixtures**, and the omission
   would have been fatal: `fr_p0_structure.py` must contain the literals `assets/`,
   `schema/`, `meta_prompt/routing/` and `work/elegoo_labs` in order to search for them,
   so `FR-P0-NOSTALE` would have flagged its own implementation on the first run at
   phase 0. Self-test (f) does not catch this — it proves only that the fixtures are
   unread — so the exclusion is stated here rather than inferred.

   **Excluding a root forbids *globbing or grepping* it. It does not forbid opening a
   *named* file under it.** Resolving an id against `tests/gates/registry.py`, or reading
   §4's tree and §8's catalogue out of the active plan, is `mapping` or `text` over a
   named input — not a scan. Six gates depend on this distinction: `FR-P0-REGISTRY`,
   `FR-P0-TREE`, `FR-P0-HISTORY`, `FR-P2-DEFERRED` (c), `FR-P4-AGREEMENT` (b) and
   `FR-P4-CHECK-MAPPING` (b). An implementer who reads the exclusion as "never touch
   `tests/**` or `plans/**`" breaks all six, three of them in phase 0.
   **`FR-P0-PLANREF` is the one further exception, and it does glob.** It enumerates
   `plans/folder_refactoring/` for **version relationships** — which files exist at which
   version, and where the superseded ones live — never for path literals. That is the one
   question `plans/**` must be asked, and it is why `FR-P0-NOSTALE` may ignore the folder
   entirely.

   **No production scan matches a bare value.** Every `text` gate matches an **anchored
   pattern declared in the manifest that owns the term**, never the raw value. A term
   list of `1`, `2`, `high`, `low`, `required` or `9` flags ordinals, list indices and
   ordinary prose across the whole repository. `FR-P3-CAPS-OWNED` establishes the form
   (`prose_pattern` per cap, missing pattern is a `FAIL`); `FR-P2-NOVALUES`,
   `FR-P3-NO-LITERALS` and `FR-P3-SPLIT` obey the same rule, each with a `.accept.`
   fixture proving an incidental occurrence does not trip it.
8. **The harness is proven before it is trusted.** `FR-P0-HARNESS` is the root of the
   dependency graph. Fixtures under `tests/selftest/` are synthetic and never touch the
   repository tree.

**Fixing a gate versus weakening it.** A gate's *implementation* may be corrected at any
time — a wrong scan root, a bad regex, a misparsed path. A gate's *acceptance criteria* —
pass conditions, `expected_error`, claim class — may never be relaxed to make a failing
repository pass. Every implementation fix is recorded as `gate_impl_fix` with a one-line
reason and re-reviewed. If the repository is what is wrong, fix the repository or return
`HALTED`.

**`depends_on` is a third category.** It may be **added or corrected** whenever a gate is
found to read something an earlier gate authors — that is a missing edge, not a weakened
criterion, and finding one is the graph working. It may never be **removed** to let a
gate run before its prerequisite. Every change is recorded as `gate_impl_fix` and
re-reviewed like any other.

---

## 8. Gate catalogue

Format: **ID** · activation phase · claim class · depends on · command · pass criteria ·
fixtures · failure meaning. **31 gates.**

**Parsing this section** — `FR-P0-REGISTRY` reads it, so the encoding is fixed: everything
after an em dash in any header field is rationale for a human, and `depends_on` is the set
of backticked `FR-` ids appearing anywhere in that field. `FR-ALL`'s prose dependency
("every phase-4 gate") is excluded with `FR-ALL` itself, which is not one of the 31.

### Phase 0 — harness, registry, structure, existing validation

**`FR-P0-HARNESS`** · 0 · `execution+mapping` · depends on: — (root)
`python3 tests/gates/selftest.py`
**Pass:** all seven self-tests pass, each named in the result record —
 (a) **phase selection**: a gate registered at `activation_phase 4` is `SKIPPED` at
 `N=0`;
 (b) **exit propagation**: an injected failing gate makes `run_gates.sh` exit non-zero;
 (c) **result integrity**: the JSON contains exactly one entry per **registered** gate — a
 gate that never ran appears as such and cannot be absent;
 (d) **wrong-reason detection**: a fixture failing with an error other than its
 `expected_error` is recorded `FAIL`, not `PASS`;
 (e) **no-overwrite**: two runs in the same second produce two files;
 (f) **scan isolation**: a production detector pointed at the production root does not
 read `tests/fixtures/**`;
 (g) **dependency order** — four parts: a gate never runs before a gate it depends on;
 a gate whose dependency failed is recorded `BLOCKED (dependency …)`, never `PASS` or
 `SKIPPED`; **a two-hop chain propagates — A fails, B is `BLOCKED`, and C depending on B
 is `BLOCKED` too**; and a synthetic cycle aborts the run before any gate executes.
**Fixtures:** `tests/selftest/*` — synthetic, never scanned by a production check.
**Failure means:** every other result in this run is unreliable. Return `HALTED`
immediately; do not report any other gate's outcome.

**`FR-P0-REGISTRY`** · 0 · `text+mapping` · depends on: `FR-P0-PLANREF` — it reads §8 of
the active plan
`python3 tests/gates/fr_p0_structure.py --check registry`
**Pass:** four relations between `tests/gates/registry.py` and this section —
 (a) every one of the 31 gate ids in §8 is registered with the same `activation_phase`,
 the same claim class **compared as a set** (as in (d) — evidence order is recorded, never
 compared) and the same `depends_on` list, also as a set;
 (b) no registered id is absent from §8;
 (c) every registered gate whose `activation_phase <=` the current phase resolves to an
 implemented callable; later ones may be declared without implementation;
 (d) for every gate that ran, the **declared claim class equals the set of mechanisms the
 implementation reported** — a gate that greps while declaring only `schema` fails here.
Prints `FR-P0-REGISTRY PASS (31 declared, K implemented, 31-K pending, 0 class drift)`.
**Fixtures:** `registry_missing_gate.reject.py` (`expected_error:
gate-declared-in-plan-not-registered`); `registry_class_drift.reject.py` — a gate
declaring `schema` whose implementation reports `schema+text`
(`expected_error: claim-class-drift`).
**Failure means:** the runner cannot report later gates as skipped because it does not
know they exist (the v4 defect), or a gate's recorded claim no longer describes what it
did (the v5 defect).

**`FR-P0-DEPS`** · 0 · `execution` · depends on: `FR-P0-HARNESS`
`python3 -c "import jsonschema, yaml; print('DEPS OK')"`
**Pass:** prints `DEPS OK`.
**Fixture:** none — environment precondition, and its own oracle.
**Failure means:** the environment, not the repo. Record as a blocking external fact and
return `HALTED`; never skip the schema gates and call the phase passed.

**`FR-P0-TREE`** · 0 · `tree+text+mapping` · depends on: `FR-P0-PLANREF` — it reads the
active plan, and `FR-P0-PLANREF` is what establishes which plan is active
`python3 tests/gates/fr_p0_structure.py --check tree`
**Pass:** **all 26 destination files** exist at their destination paths; none of
`assets/`, `schema/`, `meta_prompt/routing/`, or root `pedagogy.md` exists. The 26 are
**read from §4's target tree**, which names every file individually — **not from §5**,
whose rows are globs (`schema/*.json`, `assets/*.yaml`, `meta_prompt/routing/*.yaml`) that
cannot be expanded at run time because this very gate asserts their source directories no
longer exist. §5 owns the *rationale* for each move and the rule grouping this gate's print reports;
§4 owns the *destination list*.
**Selection rule:** a destination is any §4 entry carrying a `←` marker, or lying under a
folder carrying one, and not annotated `NEW`. That excludes the four kit files that moved
before this plan (§3) and every artifact a later phase creates; §5's per-rule counts
confirm the total is 26.
That read is why this gate is `tree+text+mapping` and not `tree`. `FR-P0-HISTORY` reads
§4 the same way. Prints
`FR-P0-TREE PASS (13 rules, 26/26 files, 0 legacy paths)`. A rule satisfied for three of
its four files is a failure naming the missing file.
**Fixture:** none — the tree is its own oracle.
**Failure means:** a move was missed or half-applied; the tree is in the same broken
intermediate state §3 describes.

**`FR-P0-NOSTALE`** · 0 · `text+execution` · depends on: `FR-P0-TREE`
`python3 tests/gates/fr_p0_structure.py --check stale`
**Pass:** zero hits for `assets/`, `schema/` (excluding `schemas/`),
`meta_prompt/routing/`, `work/elegoo_labs`, and root-relative `pedagogy.md`, searching
all tracked files **except the rule-7 exclusion set**, which includes all of `plans/**`.
Prints `FR-P0-NOSTALE PASS (0 hits, N files scanned)`.
`plans/**` is excluded on purpose and permanently: a plan that describes a move must name
the paths it is moving, so old-path literals in `plans/` are content, not debt. What
`plans/` is checked for instead is version consistency — `FR-P0-PLANREF`.
**Fixture:** `stale_reference.reject.md` — contains the literal
`assets/calibration.v1.yaml`; the detector must flag it **when pointed at the fixture
path**, `expected_error: stale-path:assets/`. The same detector against the production
root must not see the file at all — self-test (f).
**Failure means:** reference debt survived the move; some consumer will resolve a dead
path. This is the failure that produced the `work/elegoo_labs/…` ghosts.

**`FR-P0-PLANREF`** · 0 · `tree+text+mapping` · depends on: `FR-P0-HARNESS`
`python3 tests/gates/fr_p0_structure.py --check planref`
**Pass:** four version relationships, **no literal path scanning** —
 (a) the highest version `V` among `plans/folder_refactoring/*.plan.v*.md` and
 `*.prompt.v*.md` is the same for both, and both exist at the folder root;
 (b) `folder_refactoring.prompt.vV.md` names `folder_refactoring.plan.vV.md` in its goal
 line;
 (c) `folder_refactoring.plan.vV.md` names the `vV` pair as active in its §4 tree and §10
 ledger;
 (d) every plan or prompt below `V` is under `deprecated/`.
Prints `FR-P0-PLANREF PASS (active pair v<V>, 2×(V−1) superseded files archived)` with
the count **computed**, not literal — a hard-coded `10` is correct at v6 and wrong at v7.
**Fixture:** `planref_stale_pair.reject/` — a prompt naming `plan.v5.md` beside a
`plan.v6.md`; `expected_error: plan-ref-stale`.
**Failure means:** the executing agent is reading a superseded plan.

**`FR-P0-PARSE`** · 0 · `parse` · depends on: `FR-P0-TREE`
`python3 tests/gates/fr_p0_structure.py --check parse`
**Pass:** every `*.yaml` under `policy/` and `curricula/` and every `*.json` under
`schemas/` and `curricula/` parses. Prints the file count parsed.
**Fixture:** `malformed_manifest.reject.yaml`, `expected_error:
yaml.scanner.ScannerError`.
**Failure means:** a move or edit corrupted a file.

**`FR-P0-SCHEMA`** · 0 · `schema` · depends on: `FR-P0-PARSE`, `FR-P0-DEPS`
`python3 tests/gates/fr_p0_structure.py --check schema`
**Pass:** `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` validates against
`schemas/curriculum.schema.v4.json`, and `policy/calibration.v1.yaml` against
`schemas/calibration.schema.v1.json`. This is `AGENTS.md:16`'s command at the new paths.
Both schema paths are literals in this gate, so no cross-file resolution occurs — the
class is `schema` alone, deliberately.
**Fixture:** `curriculum_missing_labs.reject.yaml`, `expected_error:
ValidationError:'labs' is a required property`.
**Failure means:** the move broke a manifest. It does **not** mean `AGENTS.md` documents
a bad path — this gate holds its paths as literals and cannot see `AGENTS.md`. That
relation belongs to `FR-P0-NOSTALE` and `FR-P4-CHECK-MAPPING`.

**`FR-P0-HISTORY`** · 0 · `text+mapping+execution` · depends on: `FR-P0-TREE` — **runs
against the commit**
`python3 tests/gates/fr_p0_structure.py --check history`
**Pass:** two conditions, both read from `HEAD` after the phase-0 commit exists.
 (a) `git log --follow -- <path>` reaches the baseline commit for **each of the 26 files**
 named in §4's tree — the same source `FR-P0-TREE` reads, and for the same reason.
 (b) `git show --name-status -M HEAD` lists the four rule-1 files as renames — status
 `R` at **any** similarity score — from their `schema/` sources, rather than as an
 `A`/`D` pair. Prints the four source→destination pairs and their scores.
**Not required:** four `R100` entries in the commit. §10 edits
`schemas/lab.schema.v3.json` in the same commit, so its score is necessarily below 100.
`R100` is verified **pre-edit, at staging time**, by §5's command.
**Fixture:** none — `git`'s own record is the oracle.
**Failure means:** a file was added and deleted rather than staged as a rename;
provenance is lost. Likely cause: §10's edits were applied before staging — reset, stage
the rename, verify `R100`, then edit.

**`FR-P0-CLEAN`** · 0 · `execution` · depends on: `FR-P0-HARNESS` — **runs against the
commit**
`git status --porcelain` → empty
**Pass:** no output. Ignored files (`tests/results/*.json`) are not listed and do not
count against this gate — harness rule 4.
**Fixture:** none.
**Failure means:** the phase is not committed, or untracked artifacts leaked in. Blocks
`APPROVED` per harness rule 5.

### Phase 1 — retention

**`FR-P1-GITKEEP`** · 1 · `tree+execution` · depends on: `FR-P0-TREE`
`python3 tests/gates/fr_p1_retention.py --check gitkeep`
**Pass:** `policy/deprecated/`, `curricula/deprecated/`, `schemas/deprecated/`,
`meta_prompt/deprecated/` each contain a `.gitkeep` **and** `git ls-files` lists it.
**Fixture:** **synthesized at runtime** — the gate creates a `deprecated/` directory with
no `.gitkeep` inside a `tempfile.mkdtemp()` scratch, runs the detector against it, and
asserts `expected_error: untracked-convention`. It cannot be a committed fixture: an
empty directory cannot be committed, which is the defect under test. Recorded as
`fixture: synthesized`.
**Failure means:** the convention vanishes on clone — the defect `meta_prompt/deprecated/`
exhibits today.

**`FR-P1-DOC`** · 1 · `tree+text+mapping` · depends on: `FR-P0-HARNESS`
`python3 tests/gates/fr_p1_retention.py --check agents-doc`
**Pass:** `AGENTS.md` contains a retention table naming every top-level folder with an
explicit yes/no and a reason.
**Fixture:** `agents_missing_folder.reject.md` — a table omitting `docs/`;
`expected_error: retention-unanswered:docs`.
**Failure means:** a folder's retention answer is left to inference, which is how three
conventions (`deprecated/`, `legacy/`, `vN`) accumulated.

**`FR-P1-SCHEMA-RETENTION`** · 1 · `tree+text+mapping` · depends on: `FR-P1-GITKEEP`
`python3 tests/gates/fr_p1_retention.py --check schema-gate`
**Pass:** for every file in `schemas/deprecated/`, a repository-wide search for its
basename returns zero hits outside that folder. Vacuously true while empty — recorded as
`PASS (0 files, gate armed)`, not skipped. Both `v1` contracts must be **outside**
`deprecated/` for as long as any accepted record cites them (§6).
**Fixtures:** `retired_but_referenced.reject.json` plus a manifest citing it
(`expected_error: retired-schema-still-referenced`); and
`schema_retired_unreferenced.accept.json` — a file in `deprecated/` that nothing cites,
which must pass, since the gate is conditional and rule 3 requires the accepting case be
shown too.
**Failure means:** a schema was retired while an accepted artifact still depends on it,
breaking the audit trail `--resume` relies on.

### Phase 2 — routing, selector, and the three contracts it needs

None of these claims execution of a selector: there is none (§3).
**Dependency order matters here and is declared, not implied by ID:**
`FR-P2-CONTRACT-VERSIONED` and `FR-P2-DEFERRED` run before every gate that reads what
they author. Under ID order alone, `FR-P2-BYPASS-DECLARED` would have run first — the v5
defect.

**`FR-P2-CONTRACT-VERSIONED`** · 2 · `tree+text+schema+mapping+execution` · depends on:
`FR-P0-SCHEMA`
`python3 tests/gates/fr_p2_selector.py --check contract-versioned`
**Pass:** six conditions.
 (a) `schemas/routing_decision.schema.v2.json` exists and is a valid JSON Schema; its
 required list is v1's nine fields with `selected_model` **renamed** `decided_model`,
 plus `executed_model` — ten in all.
 (b) `schemas/execution_log.schema.v2.json` exists and is a valid JSON Schema; its `act`
 required set is **v1's nine fields plus `action_kind`** — a typed discriminator whose
 enum members include `model_call` — with `decision_id` required conditionally per (c).
 Free-text `action` is retained, as description only.
 (c) The `decision_id` requirement is conditional **on the discriminator**:
 `if: {properties: {action_kind: {const: model_call}}}, then: {required:
 ["decision_id"]}`. It must not key on any substring of `action`.
 (d) Both **v1 files remain in `schemas/`**, byte-unchanged from `HEAD~`, and neither is
 in `schemas/deprecated/` (§6).
 (e) A v1-shaped record still validates against v1, and a v2-shaped record against v2.
 (f) Every live manifest reference names `v2`; the only surviving `v1` references are in
 audit records of already-accepted work and in the retained-contracts table (§6).
**Fixtures:** `contract_v1_edited_in_place.reject.json` (`expected_error:
v1-contract-mutated`); `decision_v2_missing_executed.reject.json` (`expected_error:
'executed_model' is a required property`); `act_model_call_wordplay.reject.json` — an act
whose `action` reads "consulted the assistant" with `action_kind: model_call` and no
`decision_id`, which must still be rejected (`expected_error: 'decision_id' is a required
property`). Positive fixtures for (e): `act_v1_shaped.accept.json` must validate against
v1, and `decision_v2_valid.accept.json` against v2 — without them (e) asserts an
acceptance nothing demonstrates.
**Failure means:** the gates below are checking fields nobody authored (the v4 defect), or
the discriminator is dodgeable by wording (the v5 defect), or v1 was mutated —
retroactively invalidating accepted records.

**`FR-P2-DEFERRED`** · 2 · `parse+text+mapping` · depends on: `FR-P0-PARSE`
`python3 tests/gates/fr_p2_selector.py --check deferred`
**Pass:** four relations over `policy/deferred.v1.yaml` —
 (a) it defines ids matching `^RT-[0-9]+$`, each with `obligation`,
 `acceptance_criterion`, `blocked_by` (the missing implementation) and, where one exists,
 **two distinct fields**: `promotes_gate` — an existing gate id, which (c) resolves — and
 `promoted_id`, the name that gate would take once discharged (`FR-P2-BYPASS-ENFORCED`,
 `FR-P2-UNRECORDED-FATAL`). `promoted_id` names a gate that does not exist yet and is
 **never** resolved against the registry;
 (b) the id set equals §12's table exactly, in both directions;
 (c) every `promotes_gate` names a gate in `tests/gates/registry.py`;
 (d) every `RT-` reference **anywhere in the rule-7 production set** resolves to an id
 defined here; an unresolvable reference is a failure, not a warning. The scan root is
 that set as rule 7 defines it — by exclusion, never re-enumerated here, since a second
 hand-maintained copy is the defect this plan keeps closing. It is deliberately wider
 than `policy/**`: the retained-contracts table `FR-P2-BOUND` (c) requires lives in the
 meta prompt and cites `RT-6`.
Prints `FR-P2-DEFERRED PASS (6 ids, 6 mirrored, 0 dangling)`.
**Not a `schema` check, deliberately.** `schemas/deferred.schema.v1.json` is authored in
phase 4; this gate activates in phase 2 and would fail on a contract that does not yet
exist. Structural validation of `policy/deferred.v1.yaml` is `FR-P4-ALL-VALIDATE`'s job.
Until then this gate parses the file and checks relations — `parse+text+mapping`.
**Fixtures:** `deferred_reference_dangling.reject.yaml` — a check citing `RT-9`
(`expected_error: deferred-id-unresolved`); `deferred_no_promoted_id.accept.yaml` — an
`RT-` entry with a `promotes_gate` but no `promoted_id`, which must **pass**: four of the
six real ids are shaped that way, and (a) says "where one exists".
**Failure means:** "`MAPPED, NOT EXECUTED`, see §12" is not a verifiable statement. Two
gates below and one in phase 4 accept a `§12 follow-up id` as evidence; without stable
ids their acceptance criteria are not evaluable twice the same way — the v5 defect.

**`FR-P2-BOUND`** · 2 · `text+mapping` · depends on: `FR-P2-CONTRACT-VERSIONED`,
`FR-P2-DEFERRED` — (c) cites `RT-6`, so the registry must exist first
`python3 tests/gates/fr_p2_selector.py --check bound`
**Pass:** three conditions.
 (a) The meta prompt's **authorized-input table** names all six of: the **four**
 `policy/routing/*.yaml` manifests, `schemas/routing_decision.schema.v2.json` and
 `schemas/execution_log.schema.v2.json`. Not "exactly": the table legitimately carries
 other inputs (`policy/calibration.v1.yaml`, the curriculum and lab schemas), and a
 whitelist reading would delist them. `policy/routing/readme.md` is a folder index, not
 a model input, and is not required here.
 (b) **Neither v1 contract appears in that table.** A retained contract is readable for
 historical validation and is not an authorized input to a new run (§6).
 (c) Both v1 files appear in a separate **retained-contracts** table that states they
 validate already-accepted records only, and cites `RT-6` as the condition for retiring
 them.
**Fixtures:** `prompt_missing_routing_input.reject.md` (`expected_error:
unbound-input:model_registry.v1.yaml`); `prompt_authorizes_v1_contract.reject.md` — a
table listing `routing_decision.schema.v1.json` as an authorized input
(`expected_error: retired-version-authorized`); and
`prompt_extra_authorized_input.accept.md` — a table carrying all six required entries
plus `policy/calibration.v1.yaml`, which must **pass**, proving (a) is not a whitelist.
**Failure means:** the routing package is orphaned again — the state at `:63` today, where
one bare table row stands in for six files — or a new run may be validated against a
superseded contract, which is exactly what versioning them additively was meant to
prevent.

**`FR-P2-NOVALUES`** · 2 · `text+mapping` · depends on: `FR-P0-HARNESS`
`python3 tests/gates/fr_p2_selector.py --check no-values`
**Pass:** no model id, effort level, or candidate-pool value from `policy/routing/*.yaml`
appears in the meta prompt. Per rule 7, the gate matches each entry's declared
`prose_pattern`, not its bare value — an effort level of `high` or `low` scanned literally
would flag "high risk" and "low-cost" in ordinary prose. An entry without a
`prose_pattern` is a **FAIL** (`term-without-prose-pattern`), never a skip. Terms and
patterns are read from the manifests, never hard-coded in the gate. Production scan
excludes `tests/**` per rule 7.
**Fixtures:** `prompt_inlines_model_id.reject.md` (`expected_error: duplicated-value`);
`prompt_incidental_effort_word.accept.md` — prose reading "a high-risk step", which must
**not** match.
**Failure means:** a routing fact now has two owners — the F-series defect this refactor
exists to stop. The prompt binds; the data obeys.

**`FR-P2-SEL-MAPPED`** · 2 · `tree+text+mapping` · depends on: `FR-P2-DEFERRED`
`python3 tests/gates/fr_p2_selector.py --check sel-mapped`
**Pass:** each of the five `SEL-*` ids in `policy/checks.v1.yaml` names (i) an owner file
that exists — the manifest or prompt section stating the rule — and (ii) a verification
method from rule 6's vocabulary. Where the method is `schema` or `declaration`, the named
artifact exists and a gate here exercises it. Where the method is `execution`, the id
carries an `RT-` reference that `FR-P2-DEFERRED` resolves, and is recorded
`MAPPED, NOT EXECUTED` — never as covered. Both directions: no `SEL-*` id without an
owner, no owner section without an id.
**Fixtures:** `check_id_without_owner.reject.yaml` (`expected_error:
advertised-without-owner`); `sel_id_mapped_not_executed.accept.yaml` — a `SEL-*` id whose
method is `execution` and which carries a resolving `RT-` reference, which must **pass**
and be recorded `MAPPED, NOT EXECUTED`, since that branch is the gate's whole reason for
existing and is otherwise untested.
**Failure means:** gate **B3** and `DRIFT-NO-MISREPORTING` — a check named but owned by
nothing. This is what the meta prompt's `:157` "selector enforcement" claims today, backed
by no check id in `policy/checks.v1.yaml`.

**`FR-P2-DECISION-VALID`** · 2 · `schema+mapping` · depends on:
`FR-P2-CONTRACT-VERSIONED`
`python3 tests/gates/fr_p2_selector.py --check decision`
**Pass:** a well-formed decision record validates against
`schemas/routing_decision.schema.v2.json` with all ten required fields; and its
`decided_model` **resolves to** a member of `policy/routing/model_registry.v1.yaml` —
a cross-file resolution, which is why the class includes `mapping`.
**Fixtures:** `decision_missing_effort.reject.json` (`expected_error:
'reasoning_effort' is a required property`); `decision_model_not_in_registry.reject.json`
(`expected_error: model-not-in-registry`); and `decision_wellformed.accept.json`, the
record the pass criterion asserts validates — named, so the acceptance is demonstrated
rather than assumed.
**Failure means:** decisions can be recorded that no one can check — an audit trail that
cannot be audited.

**`FR-P2-BYPASS-DECLARED`** · 2 · `declaration` · depends on: `FR-P2-CONTRACT-VERSIONED`
— `declaration` subsumes its `text` and `schema` legs per rule 6's third subsumption
rule; the legs are named in the pass criteria, not in the class
`python3 tests/gates/fr_p2_selector.py --check bypass-declared`
**Pass:** three conditions, split by what each mechanism can actually do.
 (a) **Stated** (`text`): the prohibition on `--model` bypassing the selector appears in
 the meta prompt's `§ Routing` and in `policy/controller.v1.yaml` (promoted from `:148`),
 with `SEL-NO-MODEL-BYPASS` in `policy/checks.v1.yaml`.
 (b) **Representable** (`schema`): `routing_decision.schema.v2.json` requires *both*
 `decided_model` and `executed_model`, so a record omitting either is rejected. The schema
 is not asked to compare them: standard JSON Schema cannot compare two sibling values
 without enumerating every pair.
 (c) **Compared** (`declaration`, `comparison: python`): the gate reads both fields and
 fails the record when they differ.
**Fixtures:** `model_override_bypass.reject.json` — valid against the schema,
`decided_model != executed_model`; `expected_error: executed-differs-from-decided`. That
it passes (b) and fails (c) is the point. And `model_matches_decision.accept.json` —
`decided_model == executed_model`, which must pass (c), since a comparison gate that only
ever sees violations proves nothing about what it accepts.
**Failure means:** the rule is unstated, or unrepresentable in the record format — so no
future runtime could check it. **It does not mean bypass is impossible**: nothing executes
`--model` today. Runtime enforcement is `RT-3`.

**`FR-P2-UNRECORDED-DECLARED`** · 2 · `mapping+declaration` · depends on:
`FR-P2-CONTRACT-VERSIONED` — `mapping` is reported because (b) resolves a condition in
`failures.v1.yaml` to a state in `controller.v1.yaml`, which `declaration` does not cover
`python3 tests/gates/fr_p2_selector.py --check unrecorded-declared`
**Pass:** three conditions.
 (a) `policy/failures.v1.yaml` carries an id whose outcome is `META_SYSTEM_FAILURE` and
 whose condition is matched by a **declared `prose_pattern` on that failure entry**, not
 by prose the gate interprets — the same discipline rule 7 imposes everywhere else, and
 the last place free-text matching survived;
 (b) `policy/controller.v1.yaml` maps that condition to that terminal state, and the meta
 prompt states the obligation that every call emits a schema-valid decision;
 (c) an act with `action_kind: model_call` and no `decision_id` is **rejected by
 `execution_log.schema.v2.json`**, while an act of any other `action_kind` without one is
 accepted.
**Fixtures:** `call_without_decision.reject.json` (`expected_error: 'decision_id' is a
required property`); `act_file_write_no_decision.accept.json` — a **positive** fixture,
`action_kind: file_write`, no `decision_id`, which must validate, proving the condition is
not over-broad.
**Failure means:** the obligation is not written down anywhere a future runtime could read
it, or the discriminator is missing so wording can dodge it. Runtime termination is `RT-4`.

**`FR-P2-GATEITEMS`** · 2 · `text+mapping` · depends on: `FR-P0-HARNESS`
`python3 tests/gates/fr_p2_selector.py --check gate-items`
**Pass:** both directions, per rule 6 — every gate item advertised in the meta prompt's
release table maps to a check id in `policy/checks.v1.yaml`, **and** every check id the
release table is responsible for appears in that table. A check id advertised by no gate
item is as invisible as a gate item backed by no check.

**Second leg, added when the inventory split.** `simplification.plan.v3.md` §6 phase 3
moved twelve ids out of the engine's inventory into each curriculum's own, and removed the
`L01-*` row from the release table. This gate read only `policy/checks.v1.yaml` and so
reported nothing while four ids — `L01-DISCONNECTED`, `L01-POLARITY-NEUTRAL`,
`L01-NO-INVENTED-SUPPLY`, `L01-NO-UNPERFORMED-OBSERVATION` — were advertised by nothing at
all. A scan root that stops covering live files is the defect, not the repair, so the gate
now reads every inventory: the engine's against the release table as before, and each
curriculum's against the `release` surface that curriculum declares in its own inventory.
Putting one curriculum's ids back into an engine file would be the leak phase 3 closed, so
the surface moves with the ids and is held to the same two directions — every pattern
advertised matches an id that inventory stages **at that stage**, and every staged id is
matched by a pattern at its own stage. An id advertised under the wrong gate item is
claimed by a stage that does not run it.
**Fixtures:** `gate_item_without_check.reject.md`, `expected_error: gate-item-unbacked`.
`curriculum_release_unadvertised.reject.yaml` — a staged id no pattern claims at its
stage, `expected_error: check-id-unadvertised`. `curriculum_release_advertised.accept.yaml`
— the same inventory with every staged id covered.
**Failure means:** the build advertises coverage it does not have, or holds coverage it no
longer advertises.

### Phase 3 — calibration boundaries

**`FR-P3-SPLIT`** · 3 · `parse+text+mapping+schema` · depends on: `FR-P0-SCHEMA`
`python3 tests/gates/fr_p3_calibration.py --check split`
**Pass:** `policy/calibration.v1.yaml` contains no `power` block and no kit term (a
`text` check against the kit-term list in `curricula/arduino_kit/kit_calibration.v1.yaml`,
matched by each term's declared `prose_pattern` per rule 7, never its bare value);
`curricula/arduino_kit/kit_calibration.v1.yaml` contains the permitted inputs, rails and
3–5 V range; both validate against their schemas (`schema`). The "no `power` block" and
"contains the permitted inputs" assertions are read out of the **deserialized** document
(`parse`) — the file is not loaded solely in order to validate it, so subsumption rule 1
does not suppress it, exactly as in `FR-P3-CAPS-OWNED`.
**Fixtures:** `global_calibration_with_kit_power.reject.yaml` (`expected_error:
kit-fact-in-global-calibration`); `global_calibration_incidental_term.accept.yaml` — a
global calibration whose prose uses a kit word in a non-kit sense, which must **not**
match. Rule 7 requires a positive fixture on every bare-value gate, and this is the third
of the three.
**Failure means:** a second curriculum would silently inherit ELEGOO's supplies.

**`FR-P3-NO-LITERALS`** · 3 · `text+mapping` · depends on: `FR-P3-SPLIT`
`python3 tests/gates/fr_p3_calibration.py --check literals`
**Pass:** no file in `schemas/` contains a learner-age literal or a kit name. Both term
lists are read from `policy/calibration.v1.yaml` and
`curricula/arduino_kit/kit_calibration.v1.yaml`, never hard-coded here — and per rule 7
each term is matched by its declared `prose_pattern`, not its bare value: an age of `9`
scanned literally would flag every `9` in every schema. `schemas/kit_calibration.schema.v1.json`
is excluded — it is the kit's own contract and names the kit legitimately in its `title`
and `description`.
**Fixtures:** `schema_with_learner_literal.reject.json` (`expected_error:
data-fact-in-contract`); `schema_incidental_digit.accept.json` — a schema with
`"maxItems": 9`, which must **not** match.
**Failure means:** F03 persists — `lab.schema.v3.json:54,675` hard-code
`"nine-year-old"`, so the contract cannot serve a different learner.

**`FR-P3-CAPS-OWNED`** · 3 · `parse+text+mapping` · depends on: `FR-P3-SPLIT`
`python3 tests/gates/fr_p3_calibration.py --check caps`
**Pass:** for each entry in `policy/calibration.v1.yaml.pedagogy_caps` —
 (a) the entry declares `value`, `enforced_by` (the schema constraint that carries it)
 and **`prose_pattern`**: an anchored regular expression matching the cap *as it would be
 written in prose*, e.g.
 `(?i)\b(no more than|at most|maximum of)\s+(two|2)\s+new\s+components?\b`;
 (b) `value` equals the constraint at `enforced_by` (`mapping`);
 (c) scanning `meta_prompt/**`, `docs/**` and the prose fields of `policy/**` with
 `prose_pattern` yields **zero** matches (`text`). The cap entries themselves are
 excluded — `pedagogy_caps[*].value`, `enforced_by` and `prose_pattern` are where the cap
 is *owned*, so a gate that flagged them would forbid the manifest from stating the fact
 it exists to state;
 (d) a cap with no `prose_pattern` is a **FAIL** (`cap-without-prose-pattern`), never a
 skip — the pattern is part of authoring the cap.
**Bare value scanning is forbidden.** A cap whose value is `1`, `2`, `required` or
`understand` would otherwise flag every ordinal, list index and ordinary sentence in the
repository. This gate matches patterns, never values.
Covers the six prose copies in `pedagogy.v1.md` at `:27`, `:55`, `:85–86`, `:87`,
`:99,105`, `:100–101` — each of which must be removed or rewritten to reference the
manifest.
**Fixtures:** `prose_with_cap_value.reject.md` — prose phrased so `prose_pattern` matches
(`expected_error: unowned-cap-copy`); `prose_incidental_number.accept.md` — a **positive**
fixture containing "step 2 of the build" and "2 minutes", which must **not** match,
proving the pattern is anchored and the gate does not scan bare values.
**Failure means:** F05–F07, F09, F10 persist — prose copies that drift silently because
nothing keeps them equal.

**`FR-P3-CAL-AGREE`** · 3 · `parse+mapping` · depends on: `FR-P3-SPLIT`
`python3 tests/gates/fr_p3_calibration.py --check cal-agree`
**Pass:** `CAL-SCHEMA-AGREE` holds after the split — every value in `pedagogy_caps`
equals the schema constraint named in `enforced_by`, resolved by following the pointer
into the schema file (`mapping`) and loading it to read the constraint (`parse`). No
instance is validated here, so the class is not `schema` — rule 6's second boundary rule.
**Fixture:** `cap_schema_mismatch.reject.yaml`, `expected_error:
cap-schema-disagreement`.
**Failure means:** the split broke the one derivation this repo already enforces
correctly.

**`FR-P3-KIT-SOURCE`** · 3 · `parse+text+mapping` · depends on: `FR-P3-SPLIT`
`python3 tests/gates/fr_p3_calibration.py --check kit-source`
**Pass:** `CAL-SOURCE-VERIFIED` resolves against `kit_calibration.v1.yaml`; every powered
lab — selected by reading each lab record's power field (`parse`, `text`) — cites exactly
one input id present there (`mapping`), whose verification field reads `verified_official`
(`parse` — a data value in a manifest, not a schema constraint).
**Fixture:** `lab_cites_unverified_input.reject.yaml`, `expected_error:
unverified-source-cited`.
**Failure means:** a lab can cite a supply nobody photographed — the safety premise the
whole calibration file exists to hold.

### Phase 4 — policy schemas and mapping

**`FR-P4-ALL-VALIDATE`** · 4 · `schema+mapping` · depends on: `FR-P0-SCHEMA`
`python3 tests/gates/fr_p4_policy_schemas.py --check validate`
**Pass:** every manifest under `policy/` validates against a schema in `schemas/`, and
the manifest→schema pairing is resolved from the manifest's own `$schema`-equivalent
pointer rather than hard-coded here (`mapping`). The set is: the seven `policy/*.yaml`
— `calibration`, `checks`, `controller`, `limits`, `routes`, `failures`, `deferred` —
and the four `policy/routing/*.yaml`, each with its own schema, since a model registry, a
task taxonomy, a routing policy and a quality-gate table share no structure. The gate
prints the pairs it resolved and fails on any manifest without one; no count is asserted
in this plan.
**Fixture:** `policy_manifest_unschemaed.reject.yaml`, `expected_error:
no-schema-for-manifest`.
**Failure means:** a file code depends on can be malformed without anything noticing.

**`FR-P4-AGREEMENT`** · 4 · `parse+mapping` · depends on: `FR-P4-CHECK-MAPPING`
`python3 tests/gates/fr_p4_policy_schemas.py --check agreement`
**Pass:** three manifest-internal agreements, each checkable against files that exist —
 (a) every `limits` entry carries both a number and a flag;
 (b) every `failures` id names a correction **and** a verification owner — either a gate
 id in `tests/gates/registry.py` or an `RT-` id in `policy/deferred.v1.yaml`, recorded as
 which;
 (c) the `checks.v1.yaml` mapping relation of `FR-P4-CHECK-MAPPING`, asserted from the
 manifest side.
**Out of scope, by design:** *"`controller` states ↔ implemented states"* (`RT-1`) and
*"every `routes` entry carries recorded proof"* (`RT-2`) — both compare a manifest to a
running system.
**Fixture:** `limit_without_number.reject.yaml`, `expected_error: limit-missing-value`.
**Failure means:** shape is proven but internal agreement is not — a manifest can describe
a machine that contradicts itself. `limits.v1.yaml`'s own header states the consequence: a
limit without a number can never be exceeded, so its drift rule never fires.

**`FR-P4-FIXTURE-BITES`** · 4 · `schema` · depends on: `FR-P0-SCHEMA`
`python3 tests/gates/fr_p4_policy_schemas.py --check fixture-bites`
**Pass:** `curricula/arduino_kit/fixtures/l01_polarity_asserted.reject.json` is rejected
by `schemas/circuit_data.schema.v1.json` with the polarity-assertion violation. Both paths
are literals here, so the class is `schema` alone.
**Fixture:** the file itself. Its `expected_error` is the **validator's own message** for
the polarity constraint — the string `jsonschema` emits, not the domain name
`polarity-asserted-on-unpowered-path`; rule 3 requires the expected error be what the
declared mechanism actually produces, and this gate's mechanism is `schema`. It
lives under `curricula/`, not `tests/fixtures/`, and is therefore inside the production
scan set — intentionally: it is curriculum evidence, and its `.reject.` suffix marks it
for the parse gate as an expected-invalid instance.
**Failure means:** the reject fixture is inert — the schema accepts a circuit that asserts
polarity on an unpowered path, so `L01-POLARITY-NEUTRAL` is a name with no mechanism
behind it. Whether `checks.v1.yaml:63,65` still *points* at this fixture is not this
gate's claim — its paths are literals — it is `FR-P4-CHECK-MAPPING`'s.

**`FR-P4-CHECK-MAPPING`** · 4 · `tree+text+mapping` · depends on: `FR-P2-DEFERRED`
`python3 tests/gates/fr_p4_policy_schemas.py --check mapping`
**Pass:** for **every** id in `policy/checks.v1.yaml`, both —
 (a) an **owner**: the file that states the rule, and it exists;
 (b) a **verification method** from rule 6's vocabulary, plus the artifact carrying it — a
 schema path, a gate id in `tests/gates/registry.py`, or an `RT-` id in
 `policy/deferred.v1.yaml`.
Each id is recorded `VERIFIED HERE` or `MAPPED, NOT EXECUTED (RT-n)`; the gate prints both
counts. Reverse direction: every id this harness touches appears in `checks.v1.yaml`, and
no `FR-*` id appears there (rule 1). Production scan excludes `tests/**` per rule 7 —
which does not prevent this gate from *opening* `tests/gates/registry.py` to resolve a
named gate id, per rule 7's named-file clause.
**Explicitly not required:** that every curriculum check be executed by this suite. Many
require a controller, an execution log, a PDF renderer or a live route — none of which
exists (§3) — and rule 1 forbids a curriculum check from living in `tests/gates/`.
Execution coverage is `RT-5`.
**Fixture:** `orphan_check_id.reject.yaml`, `expected_error: advertised-without-owner`.
**Failure means:** gate **B3** in the form this plan *can* close — an id advertised with
no owner and no stated way of ever being verified. The stronger form, where an id has an
owner but nothing executes it, is reported as a count, never hidden as a pass.

### Final regression

**`FR-ALL`** · after phase 4 · `tree+mapping+execution` · depends on: every phase-4 gate
**Not one of the 31.** It is the regression *run*, not a gate: it is absent from
`tests/gates/registry.py`, and `FR-P0-REGISTRY` (a)–(b) compare the registry against the
31 gate entries above, excluding this one. §8 therefore contains 32 entries and 31 gates.
`./tests/run_gates.sh 4`
**Pass:** `FR-P0-HARNESS` runs first as the graph root and passes; all 31 gates execute in
dependency order and pass; no gate is `BLOCKED`; every negative fixture fails for its
declared `expected_error` and every positive fixture validates; a result file is written
to `tests/results/`; `git status --porcelain` is empty. The report states the
`MAPPED, NOT EXECUTED` count from `FR-P4-CHECK-MAPPING` and the `RT-` ids it cites — a
plan that ends with unexecuted checks says so, by identifier.
**Failure means:** return `HALTED` naming the failing gate id and its stated failure
meaning. `APPROVED` is legal only when all four conditions in harness rule 5 hold.

---

## 9. Phases

One commit per phase. A phase begins only after the previous phase's gates pass.
`run_gates.sh N` runs every gate with `activation_phase <= N` in **dependency order, ties
broken by ID** — earlier gates are regressions from the moment they activate.

**Gates run against a commit, never against a dirty tree.** `FR-P0-HISTORY` reads `HEAD`
and `FR-P0-CLEAN` requires an empty `git status`; neither can pass before the phase is
committed. Each phase is: implement → review → **commit** → validate → amend and
re-validate on failure. The commit is a *candidate* until validation passes, and is
amended, never appended to.

| Phase | Work | Gates run | New gates |
|---|---|---|---|
| **0** | every move in §5 plus every fix in §10, one atomic commit; create `tests/` with `registry.py` declaring **all 31 gates** and their `depends_on`, `common.py`, `run_gates.sh`, `selftest.py`, `.gitignore`, and the ten phase-0 gates | `run_gates.sh 0` | 10 |
| **1** | the four `deprecated/` folders, `.gitkeep`s, retention rule written into `AGENTS.md` | `run_gates.sh 1` | 3 |
| **2** | **both contract v2 schemas** with `action_kind`; **`policy/deferred.v1.yaml`** (RT-1…RT-6); **a `prose_pattern` on every model id, effort level and candidate-pool entry in `policy/routing/*.yaml`** — `FR-P2-NOVALUES` fails an entry without one — **and on the `META_SYSTEM_FAILURE` entry in `policy/failures.v1.yaml`** (`FR-P2-UNRECORDED-DECLARED` (a)); **retarget every live manifest reference from the v1 contracts to the v2 contracts** (`FR-P2-CONTRACT-VERSIONED` (f)); `§ Routing` in the meta prompt, authorizing v2 only and retaining v1 separately; the five `SEL-*` ids with owner and method | `run_gates.sh 2` | 9 |
| **3** | calibration split **plus `schemas/kit_calibration.schema.v1.json` (new) and an update to `schemas/calibration.schema.v1.json` for the removed `power` block and the newly required `prose_pattern`** — without it phase 3 breaks the cumulative `FR-P0-SCHEMA`; a `prose_pattern` on every cap **and on every learner-age term in `policy/calibration.v1.yaml` and every kit term in `kit_calibration.v1.yaml`** — `FR-P3-NO-LITERALS` and `FR-P3-SPLIT` fail a term without one; strip data literals from `schemas/`; reduce `pedagogy.v1.md` to rationale | `run_gates.sh 3` | 5 |
| **4** | a schema per `policy/*.yaml` (seven, incl. `deferred`) + `circuit_data` + one per routing manifest (four); agreement and check mapping | `run_gates.sh 4` | 4 |
| **final** | no new work — full regression | `FR-ALL` | — |

**Phase 0, in order.**

1. Write `tests/` — `registry.py` first, declaring all 31 gate ids with phase, claim class
   and `depends_on`; then `common.py`, `run_gates.sh` (topological sort, ties by ID),
   `selftest.py`, the ten phase-0 gates, fixtures, `selftest/`, `results/.gitkeep` — and
   `.gitignore`.
2. Stage rule 1 as a rename: `git add -A schema schemas`, then
   `git diff --cached --name-status -M100%` → **exactly four `R100` lines**. Stop here if
   not; nothing downstream recovers the history once it is committed as add/delete.
3. `git mv` rules 2–13.
4. Apply §10's content edits — **after** step 2, because editing
   `schemas/lab.schema.v3.json` first drops it below the `R100` threshold.
5. **Commit** the candidate.
6. Run `./tests/run_gates.sh 0`. Expect ten passes and twenty-one
   `SKIPPED (activates at phase M)` lines — the skips are what `FR-P0-REGISTRY` makes
   possible.
7. On any failure: fix, `git commit --amend`, re-run from 6. The commit is unshared, so
   amending is safe.

Phase 0 is one commit because splitting it would rewrite the same reference lines two or
three times, which is how the `work/elegoo_labs/…` ghost paths survived five attempts.

**Phase 2 content — prose, contracts, and the deferred registry.** `routing/` is orphaned
today: the meta prompt names it twice (`:63` a bare row, `:230` a directory name) and
states no rule, while `:157` advertises "selector enforcement" that no check id in
`policy/checks.v1.yaml` covers — the only near-match, `ROUTE-PROVEN` at
`checks.v1.yaml:193`, is external-capability preflight. The failed v3 prompt was more
explicit here (`component_lab_orchestrator_prompt.v3.md:122`).

*The prose.* The new `§ Routing` **binds, never inlines**: it names the authorized inputs,
states the invariants no data file can express (the selector runs first and code applies
the result; `--model` may not bypass it, promoted from `controller.v1.yaml:148`; no model
at all for merge, validation, hashing, rendering, aggregation, audits or the logger;
cheapest eligible route for bounded drafting, stronger for electronics design and QA,
maximum reasoning only for failed safety escalation; no redundant drafts, serial by
default; no model approves its own unsupported technical claim, promoted from
`routing/readme.md`), states the obligation that every call emits a schema-valid decision
and records the route actually executed, and separates `policy/routes.v1.yaml` (proven
capabilities) from `policy/routing/` (which model serves which task).

Its input tables are **two**, per fix 3: *authorized inputs* — the **four**
`policy/routing/*.yaml` manifests and the two `v2` schemas, `readme.md` being a folder
index rather than a model input — and *retained contracts* — the two `v1` schemas, readable only
to validate already-accepted records, retirable under `RT-6`.

*The contracts.* §3 records that neither obligation is currently expressible. Phase 2
authors two new schema versions, additively, per §6:

- **`schemas/routing_decision.schema.v2.json`** — v1's nine required fields with
  `selected_model` renamed `decided_model`, plus a required `executed_model`. The rename
  is deliberate: `selected` names an intention, and the invariant concerns the difference
  between what was *decided* and what *ran*. Everything else — `candidate_pool`,
  `reasoning_effort`, `quality_gate`, `status`, and the optional `pro_mode`,
  `evidence_inputs`, `escalate_when`, `substitution` — carries over unchanged.
- **`schemas/execution_log.schema.v2.json`** — adds two things to the `act` record: a
  required **typed discriminator** `action_kind`, an enum covering the action families
  the log already describes in prose (`inspection`, `design`, `initialization`,
  `file_write`, `command`, `test`, `model_call`, `render`, `source_request`,
  `state_transition`, `revision`, `audit`, `resume`, `terminal_decision`); and
  `decision_id`, required **conditionally on the discriminator**:
  `if: {properties: {action_kind: {const: "model_call"}}}, then: {required:
  ["decision_id"]}`. `if/then` is standard draft 2020-12, so this obligation *is*
  schema-expressible — unlike the decided/executed comparison. Free-text `action` stays,
  as description; it is never what the condition keys on. A file write must not be forced
  to carry a decision id; a model call must, and cannot escape by calling itself something
  else.

*The deferred registry.* `policy/deferred.v1.yaml` defines `RT-1 … RT-6` (§12), each with
an obligation, an acceptance criterion, what blocks it, and the gate it would promote.
Three gates cite these ids as evidence that an unexecuted obligation is *recorded* rather
than *forgotten*; `FR-P2-DEFERRED` proves every citation resolves and that the file and
§12 agree in both directions. It is a manifest, not a plan section, because code reads it
(§1).

*What phase 2 does and does not achieve.* It makes the routing rules stated, owned, and —
now — **representable in a record a future runtime could emit and a validator could
check**. It does not make them enforced, because there is nothing to enforce them in.
`FR-P2-BYPASS-DECLARED` splits its evidence across text, schema and gate code precisely so
this stays legible: prose states the rule, JSON Schema proves both fields exist, Python
compares them, and only a controller could refuse to act on the difference. `RT-3` and
`RT-4` name that work.

The five new ids: `SEL-DECISION-VALID`, `SEL-NO-MODEL-BYPASS`,
`SEL-NO-MODEL-FOR-DETERMINISTIC`, `SEL-ESCALATION-BOUNDED`,
`SEL-EXECUTED-MATCHES-DECIDED` — deliberately not `ROUTE-*`, since "route" already means
external capability. Each is added with an owner file and a verification method per
`FR-P2-SEL-MAPPED`; those needing a runtime are added as `MAPPED, NOT EXECUTED` with an
`RT-` id, not as covered.

---

## 10. Reference-fix ledger

Rewritten in phase 0, in the same commit as the moves, **after** the rule-1 rename is
staged and its four `R100` lines verified (§9 step 2). Line numbers verified 2026-07-30;
re-verify each against the file at the moment of editing.

| File | What to fix |
|---|---|
| `AGENTS.md` | `:5` asset/fixture locations · `:7` the `pedagogy.md` sentence · `:16` the validation command (both paths dead today) · `:29` note the retention rule · add `tests/` to the structure section |
| `.gitignore` | NEW or amended — `tests/results/*.json`; keep `tests/results/.gitkeep` tracked |
| `policy/calibration.v1.yaml` | 8 `schema/` refs incl. the whole `enforced_by` block · `:9` names four prose docs that have moved · `:38` `assets/official_kit_photo.jpg` |
| `policy/checks.v1.yaml` | `:3` schema path · `:63`, `:65` the fixture path |
| `policy/failures.v1.yaml` | the `assets/legacy/` citation requirement → `plans/legacy_v3/` · `:52` `work/elegoo_labs/…` provenance |
| `meta_prompt/meta_curriculum_builder.prompt.v5.md` | `:54–68` the input table · `:63` the bare `routing/` row · `:78–88` precedence · `:157` gate 2 · `:230` generated layout |
| `schemas/lab.schema.v3.json` | `:59` bare `see pedagogy.md` → explicit relative path — **this is the edit that makes a final-commit `R100` impossible; see §5** |
| `meta_prompt/pedagogy.v1.md` | `:3` `schema/lab.schema.v3.json` |
| `docs/how_it_works.md` | `:80`, `:113`, `:287` |
| `docs/infographic.prompt.v1.md` | `:30`, `:33` |
| `policy/routing/readme.md` | design rules move into the prompt (phase 2); keep the file index |
| `plans/folder_refactoring/` | move the v1–v5 plan/prompt pairs into `deprecated/`; the active pair is **v6**, and `prompt.v6.md:5` names this file — held true thereafter by `FR-P0-PLANREF` |

Phase 0 changes **paths only**. Three things are explicitly *not* pre-applied here,
because their targets do not exist yet: the `v1`→`v2` contract references and the two
input tables (phase 2, proven by `FR-P2-CONTRACT-VERSIONED` (f) and `FR-P2-BOUND`); the
`RT-` citations (phase 2, `FR-P2-DEFERRED`); and `prose_pattern` on each cap (phase 3,
`FR-P3-CAPS-OWNED`).

Pre-existing defects fixed while these files are open — the `work/elegoo_labs/…` ghost
paths (F25) in `arduino_kit_curriculum.v4.yaml:20`, `l01_unpowered_power_path.json:6`,
and `l01_polarity_asserted.reject.json:6`.

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Phase 0 is a large commit | entirely path changes, gated by `FR-P0-*`; smaller commits mean rewriting the same lines repeatedly |
| Gates that cannot run when the plan says to run them | §9: commit, then validate, then amend. `FR-P0-HISTORY` and `FR-P0-CLEAN` are marked **runs against the commit** in §8 |
| **A gate runs before the gate that authors what it reads** | harness rule 2 — `depends_on` in the registry, topological sort with ties by ID, cycle detection, and `BLOCKED (dependency …)` as a distinct outcome; proven by self-test (g). ID order alone put `FR-P2-BYPASS-DECLARED` ahead of `FR-P2-CONTRACT-VERSIONED` |
| A later gate cannot be reported as skipped because it does not exist | one registry declared in full at phase 0; `FR-P0-REGISTRY` proves 31 declared and names how many are implemented |
| **"See §12" is not a checkable reference** | `policy/deferred.v1.yaml` with ids `RT-1…RT-6`; `FR-P2-DEFERRED` proves the file and §12 agree both ways and that every `RT-` citation resolves; three gates depend on it |
| The rule-1 rename loses history | §5's staging rule run **before** §10's edits; `FR-P0-HISTORY` verifies four renames in `HEAD` plus `--follow` to baseline |
| A gate checks a field nobody authored | §3 records the contracts' actual required lists; phase 2 authors v2 of both; `FR-P2-CONTRACT-VERSIONED` is a declared dependency of every gate that reads them |
| **A record dodges a rule by rewording** | `action_kind` is a required typed discriminator and the `decision_id` condition keys on it, never on free-text `action`; `act_model_call_wordplay.reject.json` proves it |
| A retained contract is treated as a live input | §6's retained-vs-authorized distinction; `FR-P2-BOUND` (b)–(c) with `prompt_authorizes_v1_contract.reject.md`; `RT-6` retires v1 |
| Versioning a contract invalidates accepted work | §6 — v2 is additive, v1 stays in `schemas/` byte-unchanged; `FR-P2-CONTRACT-VERSIONED` (d) proves non-mutation against `HEAD~` |
| A rule JSON Schema cannot express is written as if it could | `FR-P2-BYPASS-DECLARED` splits into stated / representable / compared, with the comparison in Python, recorded as `comparison: python` |
| A conditional requirement is over-broad | rule 3 — every conditional gate carries a positive `.accept.` fixture; `act_file_write_no_decision.accept.json` and `prose_incidental_number.accept.md` |
| **A text gate matches values that mean nothing** | harness rule 7's general ban — **no production scan matches a bare value**. `FR-P3-CAPS-OWNED`, `FR-P2-NOVALUES`, `FR-P3-NO-LITERALS` and `FR-P3-SPLIT` each match a declared `prose_pattern`; a term without one fails rather than silently passing; each carries a positive fixture proving an incidental `2`, `9` or `high` does not trip it. The patterns are authored in the same phase as the gate that needs them (§9, phases 2 and 3) |
| A gate's recorded claim overstates or understates its evidence | `FR-P0-REGISTRY` (d) compares declared class against the mechanisms each implementation reports; drift is a failure, with its own fixture |
| A phase-4 gate requires a schema that exists nowhere | every `policy/` manifest and routing manifest has a named schema in §4 and in the phase-4 row; `FR-P4-ALL-VALIDATE` resolves pairs from the manifests and asserts no count |
| **The harness is new code and is its own oracle** | `FR-P0-HARNESS` is the dependency root and tests the seven behaviours no per-gate fixture reaches. Its failure invalidates the whole run |
| A broken gate cannot be fixed, or a gate is edited to pass | §7's closing rule — implementation may be corrected and is recorded as `gate_impl_fix`; acceptance criteria may never be weakened |
| A gate rejects its own subject | rule 7 for fixtures; `FR-P0-PLANREF` checks version relationships rather than scanning a plan for the paths it exists to move |
| Results dirty the worktree | `tests/results/*.json` ignored, folder kept by `.gitkeep` |
| Moving `legacy/` breaks `failures.v1.yaml` citations | edited in the same commit; `FR-P0-NOSTALE` greps for survivors |
| The executing agent reads a superseded plan | `FR-P0-PLANREF`; v1–v5 and their prompts move to `deprecated/` in phase 0 |
| `redundancy.analysis.v1.md` line numbers are stale — it cites `readme.md:63`, now a one-line file | findings hold, line refs do not; re-verify at edit time |

---

## 12. Out of scope — the deferred register

**Runtime enforcement and execution coverage.** This plan makes the rules stated, owned,
mapped, and representable in records a validator can check. It cannot make them
*executed*, because no controller, execution-log writer, renderer or live route exists
(§3). The follow-up needs an implementation.

This table is the authoritative deferral list. It is mirrored **exactly** in
`policy/deferred.v1.yaml`, which is what gates read; `FR-P2-DEFERRED` proves the two
agree in both directions and that every citation elsewhere resolves. `RT-1`–`RT-6` are
this plan's own; ids from `RT-7` are appended by later plans whose gates compose into
the same registry, and they are listed here because the mirror is one list and a second
one would be a second answer to what has been deferred.

Column names match the manifest's fields exactly: `blocked_by` is what the obligation
waits on, `promotes_gate` is an **existing** gate id (which `FR-P2-DEFERRED` (c)
resolves against the registry), and `promoted_id` is the name that gate takes once
discharged — a gate that does not exist yet and is never resolved.

| ID | Obligation | Acceptance criterion | `blocked_by` | `promotes_gate` | `promoted_id` |
|---|---|---|---|---|---|
| **RT-1** | Controller states are real | every state in `policy/controller.v1.yaml` is reachable in an implemented state machine, and no implemented state is absent from the manifest | no controller implementation | `FR-P4-AGREEMENT` | — |
| **RT-2** | Routes are proven by use | every entry in `policy/routes.v1.yaml` carries proof recorded from an actual execution | no executed run to record proof from | `FR-P4-AGREEMENT` | — |
| **RT-3** | Bypass is refused, not just detected | a call whose `executed_model` differs from its `decided_model` is rejected **at runtime**, not merely by a gate reading a static fixture | no selector implementation | `FR-P2-BYPASS-DECLARED` | `FR-P2-BYPASS-ENFORCED` |
| **RT-4** | An unrecorded call is fatal | a model call with no `decision_id` **terminates** the run as `META_SYSTEM_FAILURE`, rather than failing schema validation after the fact | no controller implementation | `FR-P2-UNRECORDED-DECLARED` | `FR-P2-UNRECORDED-FATAL` |
| **RT-5** | Advertised checks are executed | every id `FR-P4-CHECK-MAPPING` reports as `MAPPED, NOT EXECUTED` becomes executed, and every A-series id in `policy/failures.v1.yaml` gains a proving test | no controller, logger, renderer or live route | `FR-P4-CHECK-MAPPING` | — |
| **RT-6** | The v1 contracts are retirable | the logger emits `execution_log.schema.v2.json`-valid records and the selector emits `routing_decision.schema.v2.json`-valid decisions, after which both v1 schemas may enter `schemas/deprecated/` under §6's gate | no logger emitting v2 records | `FR-P1-SCHEMA-RETENTION` | — |
| **RT-8** | A curriculum declares its domain vocabulary | every curriculum declares the terms of its own domain — not only its proper nouns — each with an anchored `prose_pattern`, so that leg (b) of `FR-P5-ENGINE-GENERIC` and leg (b) of `FR-P5-UNIT-CONTRACT` can see a domain word that is not a vendor name | nothing blocks it technically; it is not in this plan. `simplification.plan.v3.md` section 6 phase 2 declares a verifier and no vocabulary, and `simplification.phase0.result.v1.md` reasons that a `domain_terms` block belongs beside the verifier declaration. Until it exists, leg (b) is armed and near-blind: the only declaration is `kit_terms`, seven proper nouns, and `LAB-CURRENT-MARGIN` and `LAB-VALUE-SOURCED` are engine-owned domain assertions the detector cannot see. Zero is a bound, not a clean bill, and this id is where that is written down. | `FR-P5-ENGINE-GENERIC` | — |
| **RT-7** | The unit checks have a generated subject | at least one unit exists under `curricula/<name>/units/`, produced by a real run rather than written by hand, so that `FR-P5-READABILITY`, `FR-P5-BLOOM-VERBS`, `FR-P5-DERIVATION` and `FR-P5-RECEIPT-HASH` assert over generated work instead of over their own fixtures alone | nothing in this repository executes a model, renders an artifact or fetches a source, so no unit has ever been generated. Until then each of those four gates reports the number of units it scanned, and that number is zero. Reporting their fixture coverage as generated-lab coverage would be failure A5. | — | — |
| **RT-10** | Genericity is demonstrated, not only enforced | a second curriculum in an unrelated subject, with a trivially checkable verifier, runs to completion under `meta_prompt/curriculum.prompt.v1.md` with no edit to that file, and `FR-P5-ENGINE-GENERIC` passes with more than one curriculum present | section 6 phase 7 of the simplification plan, which is out of scope for the run that wrote this entry. Until it happens, genericity is structurally enforced and not demonstrated: every gate says the engine names no curriculum, and exactly one curriculum has ever existed. "The engine handles any curriculum" and "a curriculum exists" are different claims and are never reported as each other. | `FR-P5-ENGINE-GENERIC` | — |

Until each is discharged, no document, gate name or report may state that the selector is
enforced or that the check suite is fully executed.

**Also out of scope.** Curriculum content; the F86 finding that 14 of 35 labs declare
`adult_led_controller_station` while four prose documents forbid a controller; the
contradictions in `redundancy.analysis.v1.md` beyond the paths named in §10; rendering
`docs/how_it_works.png`; anything under `plans/` except the archiving of v1–v5 and the
prompt retarget in §10.

F86 is a substantive contradiction about what the workbook *is* and needs its own
decision. It is recorded here only so this refactor is not mistaken for having addressed
it.
