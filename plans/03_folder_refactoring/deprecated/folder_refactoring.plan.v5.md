# Folder refactoring — plan v5

**Date:** 2026-07-30
**Supersedes:** `deprecated/folder_refactoring.plan.v4.md` (and, through it, v3, v2, v1)
**Status:** accepted, not started. No file has been moved or edited under this plan.
**Scope:** folder layout, file placement, the references that name them, the two data
contracts phase 2 depends on, and a committed harness that proves each phase. Not
curriculum content. Not a runtime implementation.

**v2** gave every gate a stable ID, an activation phase, an exact command, pass criteria,
a rejection fixture where one applies, and a stated failure meaning. Gates are cumulative:
phase *N* runs its own gates plus every earlier gate.

**v3** fixed nine defects of intent: the impossible `git mv`, gates claiming runtime
enforcement with no runtime, prompt/plan version drift, `plans/**` excluded from every
check, an untested harness, a wrong file count, detectors that rejected their own
fixtures, results that dirtied the worktree.

**v4** fixed four defects of mechanism: gates ordered before the commit they read,
`R100` commands that print no similarity score, a `PLANREF` gate that rejected its own
plan, and runtime scope still leaking through three "executed by the suite" clauses.

**What v5 adds over v4.** v4 was reviewed against the actual schema files, and the
phase-2 gates turned out to reference fields that do not exist. Six fixes, one of which
expands scope:

1. **Phase 2's data contracts did not exist — scope expanded.**
   `meta_prompt/routing/routing_decision.schema.v1.json:5` requires `selected_model`;
   there is no `decided_model` and no `executed_model`. `schemas/execution_log.schema.v1.json`
   has no `decision_id` on any record. Both phase-2 declaration gates were written
   against fields nobody had authored. **Phase 2 now versions both contracts** —
   `routing_decision.schema.v2.json` and `execution_log.schema.v2.json` — and
   `FR-P2-CONTRACT-VERSIONED` proves the bump was done without breaking v1.
   Separately: JSON Schema cannot generically compare two sibling values, so
   `FR-P2-BYPASS-DECLARED` splits — the schema proves both fields are *present*, gate
   code proves they *match*.
2. **Phase 0 built only phase-0 gates**, while validation required every later gate to be
   recorded as skipped. Phase 0 now installs the **full gate registry** — every id in §8
   with its activation phase and claim class — and `FR-P0-REGISTRY` proves it complete.
3. **Four routing schemas were required in phase 4 and named nowhere.**
   `FR-P4-ALL-VALIDATE` demanded a schema for each `policy/routing/*.yaml`; §4 listed
   none. Four are now named. Not one shared schema: a model registry, a task taxonomy, a
   routing policy and a quality-gate table have nothing structural in common.
4. **The prompt forbade fixing a broken gate.** "Never resolve a gate failure by editing
   the gate" and "fix the detector, never the fixture" contradicted each other. Split: a
   gate's *implementation* may be corrected when it misreads its subject; a gate's
   *acceptance criteria* may never be weakened.
5. **Gate order contradicted itself.** `FR-P0-HARNESS` must run first; ID order puts
   `FR-P0-CLEAN` and `FR-P0-DEPS` ahead of it.
6. **Claim class said "one of"** while `FR-P4-AGREEMENT` declared two. It is an ordered
   set.

Harness rule 6's sentence about the `execution` class, flagged and deferred in v4, is
corrected here as part of fix 6 — it cost one clause.

---

## 1. The rule

Every file lives where its reader is.

| Folder | Consumer | Form |
|---|---|---|
| `policy/` | **code** — the controller, preflight, the gate suite | `*.yaml` |
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
  from content, so history is still recoverable — see the staging rule in §5.
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
    result`. There is no `decision_id` on `act` or on `exec`, so "a model call with no
    decision record" is not expressible either.
  Phase 2 authors `v2` of both. See §9.
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
│   ├── calibration.v1.yaml                     premise: learner, caps, safety floor
│   ├── checks.v1.yaml                          the stable check ids
│   ├── controller.v1.yaml                      states, transitions, ownership, CLI
│   ├── limits.v1.yaml                          numeric ceilings + flags
│   ├── routes.v1.yaml                          external capabilities, proven by execution
│   ├── failures.v1.yaml                        A1–A10, B1–B4
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
│   ├── calibration.schema.v1.json
│   ├── kit_calibration.schema.v1.json          NEW (phase 3)
│   ├── execution_log.schema.v1.json            retained — accepted work validates here
│   ├── execution_log.schema.v2.json            NEW (phase 2) — adds decision_id
│   ├── routing_decision.schema.v1.json         ← meta_prompt/routing/ (retained)
│   ├── routing_decision.schema.v2.json         NEW (phase 2) — decided + executed model
│   ├── checks.schema.v1.json                   NEW (phase 4)
│   ├── controller.schema.v1.json               NEW (phase 4)
│   ├── limits.schema.v1.json                   NEW (phase 4)
│   ├── routes.schema.v1.json                   NEW (phase 4)
│   ├── failures.schema.v1.json                 NEW (phase 4)
│   ├── circuit_data.schema.v1.json             NEW (phase 4)
│   ├── model_registry.schema.v1.json           NEW (phase 4) ┐
│   ├── task_taxonomy.schema.v2.json            NEW (phase 4) │ one per routing manifest;
│   ├── routing_policy.schema.v1.json           NEW (phase 4) │ they share no structure
│   ├── quality_gates.schema.v1.json            NEW (phase 4) ┘
│   └── deprecated/.gitkeep                     gated — see §6
│
├── meta_prompt/                                PROSE A MODEL READS
│   ├── meta_curriculum_builder.prompt.v5.md    + new § Routing (phase 2)
│   ├── component_lab_template.v1.md            companion: how to write a lab
│   ├── pedagogy.v1.md                          companion: why the pedagogy fields exist ← root
│   ├── model_selector_prompt.v1.md             ← meta_prompt/routing/
│   └── deprecated/.gitkeep
│
├── tests/                                      THE GATE HARNESS — see §7
│   ├── run_gates.sh
│   ├── gates/
│   │   ├── registry.py                         every gate id, phase and claim class
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
    │   ├── folder_refactoring.plan.v5.md       this file — the active plan
    │   ├── folder_refactoring.prompt.v5.md     the active execution prompt
    │   └── deprecated/                         plan+prompt pairs v1–v4
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

Both `v1` contracts stay in `schemas/`, not in `schemas/deprecated/` — §6's gate forbids
retiring a schema any accepted artifact was validated under.

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
| 9 | `pedagogy.md` | `meta_prompt/pedagogy.v1.md` | 1 | constraint-bearing prose; versioned per `AGENTS.md:29` |
| 10 | `meta_prompt/routing/*.yaml` | `policy/routing/` | 4 | data code reads |
| 11 | `meta_prompt/routing/readme.md` | `policy/routing/` | 1 | index of those files |
| 12 | `meta_prompt/routing/model_selector_prompt.v1.md` | `meta_prompt/` | 1 | prose a model reads |
| 13 | `meta_prompt/routing/routing_decision.schema.v1.json` | `schemas/` | 1 | all contracts in one folder |

Nothing is deleted. Phase 2 and later *add* files; they move none.

**How to move, so that history follows.**

- **Rules 2–13 — sources still exist in the working tree.** Use `git mv`.
- **Rule 1 — the source no longer exists.** `git mv schema/x.json schemas/x.json` fails:
  there is nothing at the source path (§3). Git stores snapshots and detects renames from
  content, so history is intact provided **both sides are staged in the same commit** and
  the check below is run **before any content edit**:

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
  expected and permitted: the pre-edit `R100` check proves the rename was staged as a
  rename, and `git log --follow` proves the history survived the commit.
  **The final commit will not contain four `R100` entries, and must not be required to.**

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

**This is why phase 2 adds `v2` contracts instead of editing `v1`.** Any execution log
or routing decision already accepted was validated against `v1`; editing `v1` in place
would retroactively invalidate it. `FR-P2-CONTRACT-VERSIONED` enforces the pattern.

`docs/` has no `deprecated/`: its explainers are regenerated from `.typ`, and an archive
of stale claims is a drift risk rather than a record.

---

## 7. The harness

**Location:** `tests/`, committed. Consumer is code, so it obeys §1.

```
tests/
├── run_gates.sh                  ./tests/run_gates.sh <phase>   → FR-P0-HARNESS first,
│                                 then every gate whose activation phase ≤ <phase>,
│                                 in ID order
├── gates/
│   ├── registry.py               EVERY gate id in §8 with activation_phase and claim
│   │                             class — declared in phase 0, implemented per phase
│   ├── common.py                 path constants, scan roots, fixture runner, recorder
│   ├── fr_p0_structure.py        FR-P0-*
│   ├── fr_p1_retention.py        FR-P1-*
│   ├── fr_p2_selector.py         FR-P2-*
│   ├── fr_p3_calibration.py      FR-P3-*
│   ├── fr_p4_policy_schemas.py   FR-P4-*
│   └── selftest.py               FR-P0-HARNESS — proves the harness, see rule 8
├── fixtures/                     negative fixtures, named <subject>.reject.<ext>
├── selftest/                     synthetic inputs for selftest.py only
└── results/.gitkeep              gate_results.p<phase>.<utc-timestamp>.json — ignored
```

**Harness contract — eight rules, none optional.**

1. **Gate IDs are `FR-P<phase>-<NAME>`.** The `FR-` prefix keeps refactor gates
   distinguishable from curriculum check ids in `policy/checks.v1.yaml` (`CAL-`,
   `CUR-`, `L01-`, `LAB-`, `PDF-`, `LOG-`, `REV-`, `DRIFT-`, `SEL-`). A refactor gate
   never appears in `checks.v1.yaml`, and **a curriculum check never appears in
   `tests/gates/`** — which is why no gate in §8 may require a curriculum check to be
   *executed by this harness*. What this harness can prove about a curriculum check is
   that it is declared, owned, and mapped to a verification method. See rule 6 and §12.
2. **One registry, declared in full at phase 0; cumulative execution.**
   `tests/gates/registry.py` lists **every** gate in §8 with its `activation_phase` and
   claim class from the first commit onward — a later gate is declared before it is
   implemented. `run_gates.sh N` runs `FR-P0-HARNESS` first, then gates with
   `activation_phase <= N` in ID order, and *skips* later ones with an explicit
   `SKIPPED (activates at phase M)` line. A skip is recorded, never silent, and never
   counted as a pass. A declared-but-unimplemented gate whose phase has arrived is a
   **failure**, not a skip.
   The harness-first exception exists because ID order would otherwise put
   `FR-P0-CLEAN` and `FR-P0-DEPS` ahead of the gate that proves the runner works.
3. **A negative fixture must fail for its stated reason.** Every fixture declares an
   `expected_error` pattern. A fixture that fails for a different reason — a parse
   error where a constraint violation was expected — is a **gate failure**, not a pass.
4. **Results are recorded, never asserted.** Each run writes one JSON file to
   `tests/results/` containing, per gate: id, activation phase, claim class, command,
   exit code, stdout digest, pass/fail/skip, and each fixture's outcome with the matched
   error. Files are never overwritten. Per `AGENTS.md:25`, an unexecuted check is never
   reported as passing.
   **`tests/results/*.json` is listed in `.gitignore`**; the folder is kept by
   `tests/results/.gitkeep`. This is what makes rule 5's two conditions — "results
   written" and "worktree clean" — simultaneously satisfiable. `git status --porcelain`
   does not list ignored files, so a run leaves the tree clean by construction.
5. **`APPROVED` requires all four:** every gate through the current phase passes; every
   negative fixture failed for its intended reason; results are written; the worktree is
   clean. Any missing element returns `BLOCKED` with the specific cause.
6. **Every gate declares a claim class, and may not claim more.** A claim class is an
   **ordered set** of one or more of:
   - `tree` — a path exists or does not exist.
   - `parse` — a file parses.
   - `schema` — an instance validates, or fails to validate, against a JSON Schema.
   - `text` — a string is present or absent in a tracked file.
   - `mapping` — an advertised id resolves to an owner file that exists and to a stated
     verification method; and no owner or method exists without an advertised id.
   - `declaration` — a manifest or prompt *states* a rule, and a record conforming to
     that rule validates while a violating record does not.
   - `execution` — a program was run and behaved as claimed.

   It is printed and recorded joined by `+`, e.g. `schema+mapping`.

   **No gate claims `execution` of a controller or routing runtime**, because §3 records
   that none exists. Four phase-0 gates *are* class `execution` — over `python3`, `git`
   and the harness itself, all of which do exist. A gate's ID, pass line and failure
   meaning must be phrased in its own class: a `declaration` gate says a rule is *stated
   and checkable*, never *enforced at runtime*; a `mapping` gate says an id is *owned*,
   never *executed*.
7. **A production scan never reads a fixture.** Every detector takes an explicit scan
   root set. The production set excludes `tests/fixtures/**`, `tests/selftest/**`,
   `tests/results/**`, `plans/**` and `.git/**`. A detector is proven against its own
   fixture by a **separate** invocation pointed at the fixture path. Without this,
   `FR-P0-NOSTALE`, `FR-P2-NOVALUES`, `FR-P3-CAPS-OWNED` and `FR-P4-CHECK-MAPPING` all
   fail on their own tracked fixtures.
8. **The harness is proven before it is trusted.** `FR-P0-HARNESS` runs first in phase 0
   and gates every other result. Fixtures under `tests/selftest/` are synthetic and
   never touch the repository tree.

**Fixing a gate versus weakening it.** A gate's *implementation* may be corrected at any
time — a wrong scan root, a bad regex, a misparsed path. A gate's *acceptance criteria* —
its pass conditions, its `expected_error`, its claim class — may never be relaxed to make
a failing repository pass. Every implementation fix is recorded in the result file as
`gate_impl_fix` with a one-line reason and is re-reviewed. If the repository is what is
wrong, fix the repository or return `BLOCKED`.

---

## 8. Gate catalogue

Format: **ID** · activation phase · claim class · command · pass criteria · rejection
fixture · failure meaning. **30 gates.**

### Phase 0 — harness, registry, structure, existing validation

**`FR-P0-HARNESS`** · 0 · class `execution` (of the harness) — **runs first, always**
`python3 tests/gates/selftest.py`
**Pass:** all six self-tests pass, each named in the result record —
 (a) **phase selection**: a gate registered at `activation_phase 4` is reported
 `SKIPPED` at `N=0`;
 (b) **exit propagation**: an injected failing gate makes `run_gates.sh` exit non-zero;
 (c) **result integrity**: the JSON contains exactly one entry per **registered** gate —
 a gate that never ran appears as such and cannot be absent;
 (d) **wrong-reason detection**: a fixture that fails with an error other than its
 `expected_error` is recorded `FAIL`, not `PASS` (rule 3, tested rather than asserted);
 (e) **no-overwrite**: two runs in the same second produce two files;
 (f) **scan isolation**: a production detector pointed at the production root does not
 read `tests/fixtures/**` (rule 7).
**Fixtures:** `tests/selftest/*` — synthetic, never scanned by a production check.
**Failure means:** every other result in this run is unreliable. Return `BLOCKED`
immediately; do not report any other gate's outcome.

**`FR-P0-REGISTRY`** · 0 · class `mapping`
`python3 tests/gates/fr_p0_structure.py --check registry`
**Pass:** both directions between `tests/gates/registry.py` and this section —
 (a) every one of the 30 gate ids in §8 is registered, with the same `activation_phase`
 and the same claim class;
 (b) no registered id is absent from §8;
 (c) every registered gate whose `activation_phase <= ` the current phase resolves to an
 implemented callable; later ones may be declared without implementation.
Prints `FR-P0-REGISTRY PASS (30 declared, K implemented, 30-K pending)`.
**Fixture:** `tests/fixtures/registry_missing_gate.reject.py`, `expected_error:
gate-declared-in-plan-not-registered`.
**Failure means:** `run_gates.sh 0` cannot report later gates as skipped, because it does
not know they exist — the v4 defect, where phase 0 built only phase-0 gates while
validation demanded a skip line for every later one.

**`FR-P0-DEPS`** · 0 · class `execution`
`python3 -c "import jsonschema, yaml; print('DEPS OK')"`
**Pass:** prints `DEPS OK`.
**Fixture:** none — environment precondition, and its own oracle.
**Failure means:** the environment, not the repo. Record as a blocking external fact and
return `BLOCKED`; never skip the schema gates and call the phase passed.

**`FR-P0-TREE`** · 0 · class `tree`
`python3 tests/gates/fr_p0_structure.py --check tree`
**Pass:** **all 26 destination files** enumerated in §5 exist at their destination paths;
none of `assets/`, `schema/`, `meta_prompt/routing/`, or root `pedagogy.md` exists. Prints
`FR-P0-TREE PASS (13 rules, 26/26 files, 0 legacy paths)`. A rule satisfied for three of
its four files is a failure naming the missing file.
**Fixture:** none — the tree is its own oracle.
**Failure means:** a move was missed or half-applied; the tree is in the same broken
intermediate state §3 describes.

**`FR-P0-NOSTALE`** · 0 · class `text`
`python3 tests/gates/fr_p0_structure.py --check stale`
**Pass:** zero hits for `assets/`, `schema/` (excluding `schemas/`),
`meta_prompt/routing/`, `work/elegoo_labs`, and root-relative `pedagogy.md`, searching
all tracked files **except the rule-7 exclusion set**, which includes all of `plans/**`.
Prints `FR-P0-NOSTALE PASS (0 hits, N files scanned)`.
`plans/**` is excluded on purpose and permanently: a plan that describes a move must name
the paths it is moving, so old-path literals in `plans/` are content, not debt. What
`plans/` is checked for instead is version consistency — `FR-P0-PLANREF`.
**Fixture:** `tests/fixtures/stale_reference.reject.md` — contains the literal
`assets/calibration.v1.yaml`; the detector must flag it **when pointed at the fixture
path**, `expected_error: stale-path:assets/`. The same detector run against the
production root must not see this file at all — that is self-test (f).
**Failure means:** reference debt survived the move; some consumer will resolve a dead
path. This is the exact failure that produced the `work/elegoo_labs/…` ghosts.

**`FR-P0-PLANREF`** · 0 · class `mapping`
`python3 tests/gates/fr_p0_structure.py --check planref`
**Pass:** four version relationships, **no literal path scanning** —
 (a) the highest version `V` among `plans/folder_refactoring/*.plan.v*.md` and
 `*.prompt.v*.md` is the same for both, and both exist at the folder root;
 (b) `folder_refactoring.prompt.vV.md` names `folder_refactoring.plan.vV.md` in its goal
 line;
 (c) `folder_refactoring.plan.vV.md` names the `vV` pair as active in its §4 tree and §10
 ledger;
 (d) every plan or prompt below `V` is under `deprecated/`.
Prints `FR-P0-PLANREF PASS (active pair v<V>, 8 superseded files archived)`.
**Fixture:** `tests/fixtures/planref_stale_pair.reject/` — a prompt naming `plan.v4.md`
beside a `plan.v5.md`; `expected_error: plan-ref-stale`.
**Failure means:** the executing agent is reading a superseded plan.

**`FR-P0-PARSE`** · 0 · class `parse`
`python3 tests/gates/fr_p0_structure.py --check parse`
**Pass:** every `*.yaml` under `policy/` and `curricula/` and every `*.json` under
`schemas/` and `curricula/` parses. Prints the file count parsed.
**Fixture:** `tests/fixtures/malformed_manifest.reject.yaml`, `expected_error:
yaml.scanner.ScannerError`.
**Failure means:** a move or edit corrupted a file.

**`FR-P0-SCHEMA`** · 0 · class `schema`
`python3 tests/gates/fr_p0_structure.py --check schema`
**Pass:** `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` validates against
`schemas/curriculum.schema.v4.json`, and `policy/calibration.v1.yaml` against
`schemas/calibration.schema.v1.json`. This is `AGENTS.md:16`'s command at the new paths.
**Fixture:** `tests/fixtures/curriculum_missing_labs.reject.yaml`, `expected_error:
ValidationError:'labs' is a required property`.
**Failure means:** the move broke a manifest, or `AGENTS.md` still documents paths that
do not validate.

**`FR-P0-HISTORY`** · 0 · class `execution` (of `git`) — **runs against the commit**
`python3 tests/gates/fr_p0_structure.py --check history`
**Pass:** two conditions, both read from `HEAD` after the phase-0 commit exists.
 (a) `git log --follow -- <path>` reaches the baseline commit for **each of the 26 files**
 in §5.
 (b) `git show --name-status -M HEAD` lists the four rule-1 files as renames — status
 `R` with **any** similarity score — from their `schema/` sources, rather than as an
 `A`/`D` pair. Prints the four source→destination pairs and their scores.
**Not required:** four `R100` entries in the commit. §10 edits
`schemas/lab.schema.v3.json` in the same commit, so its score is necessarily below 100.
`R100` is verified **pre-edit, at staging time**, by §5's `git diff --cached
--name-status -M100%`.
**Fixture:** none — `git`'s own record is the oracle.
**Failure means:** a file was added and deleted rather than staged as a rename;
provenance is lost. Likely cause: §10's edits were applied before staging — reset, stage
the rename, verify `R100`, then edit.

**`FR-P0-CLEAN`** · 0 · class `execution` (of `git`) — **runs against the commit**
`git status --porcelain` → empty
**Pass:** no output. Ignored files (`tests/results/*.json`) are not listed and do not
count against this gate — see harness rule 4.
**Fixture:** none.
**Failure means:** the phase is not committed, or untracked artifacts leaked in. Blocks
`APPROVED` per harness rule 5.

### Phase 1 — retention

**`FR-P1-GITKEEP`** · 1 · class `tree`
`python3 tests/gates/fr_p1_retention.py --check gitkeep`
**Pass:** `policy/deprecated/`, `curricula/deprecated/`, `schemas/deprecated/`,
`meta_prompt/deprecated/` each contain a `.gitkeep` **and** `git ls-files` lists it.
**Fixture:** **synthesized at runtime** — the gate creates a `deprecated/` directory
containing no `.gitkeep` inside a `tempfile.mkdtemp()` scratch, runs the detector against
it, and asserts `expected_error: untracked-convention`. It cannot be a committed fixture:
an empty directory cannot be committed, which is precisely the defect under test. The
result record marks it `fixture: synthesized`.
**Failure means:** the convention vanishes on clone — the precise defect
`meta_prompt/deprecated/` exhibits today.

**`FR-P1-DOC`** · 1 · class `text`
`python3 tests/gates/fr_p1_retention.py --check agents-doc`
**Pass:** `AGENTS.md` contains a retention table naming every top-level folder with an
explicit yes/no and a reason.
**Fixture:** `tests/fixtures/agents_missing_folder.reject.md` — a table omitting `docs/`;
`expected_error: retention-unanswered:docs`.
**Failure means:** a folder's retention answer is left to inference, which is how three
conventions (`deprecated/`, `legacy/`, `vN`) accumulated.

**`FR-P1-SCHEMA-RETENTION`** · 1 · class `text`
`python3 tests/gates/fr_p1_retention.py --check schema-gate`
**Pass:** for every file in `schemas/deprecated/`, a repository-wide search for its
basename returns zero hits outside that folder. Vacuously true while empty — and
recorded as `PASS (0 files, gate armed)`, not skipped.
**Fixture:** `tests/fixtures/retired_but_referenced.reject.json` plus a manifest citing
it; `expected_error: retired-schema-still-referenced`.
**Failure means:** a schema was retired while an accepted artifact still depends on it,
breaking the audit trail `--resume` relies on.

### Phase 2 — routing, selector, and the two contracts it needs

Every gate here is class `text`, `tree`, `schema`, `mapping` or `declaration`. None claims
execution of a selector: there is none (§3).

**`FR-P2-BOUND`** · 2 · class `text`
`python3 tests/gates/fr_p2_selector.py --check bound`
**Pass:** all five `policy/routing/` files and both routing-decision schema versions are
named in the meta prompt's authorized-input table.
**Fixture:** `tests/fixtures/prompt_missing_routing_input.reject.md`, `expected_error:
unbound-input:model_registry.v1.yaml`.
**Failure means:** the routing package is orphaned again — the state at `:63` today,
where one bare table row stands in for six files.

**`FR-P2-NOVALUES`** · 2 · class `text`
`python3 tests/gates/fr_p2_selector.py --check no-values`
**Pass:** no model id, effort level, or candidate-pool value from `policy/routing/*.yaml`
appears literally in the meta prompt. Production scan excludes `tests/fixtures/**` per
harness rule 7 — this detector would otherwise flag its own fixture.
**Fixture:** `tests/fixtures/prompt_inlines_model_id.reject.md`, `expected_error:
duplicated-value`.
**Failure means:** a routing fact now has two owners — the F-series defect this refactor
exists to stop. The prompt binds; the data obeys.

**`FR-P2-CONTRACT-VERSIONED`** · 2 · class `tree+schema` — **NEW in v5**
`python3 tests/gates/fr_p2_selector.py --check contract-versioned`
**Pass:** five conditions.
 (a) `schemas/routing_decision.schema.v2.json` exists and is a valid JSON Schema; its
 required list is v1's nine fields with `selected_model` **renamed** to `decided_model`,
 plus `executed_model` — ten in all.
 (b) `schemas/execution_log.schema.v2.json` exists and is a valid JSON Schema; its `act`
 definition adds `decision_id`, required **conditionally** — `if action` matches the
 model-call pattern, `then required: ["decision_id"]`. A non-model action must not be
 forced to carry one; a model call must.
 (c) Both **v1 files remain in `schemas/`**, unedited, and neither is in
 `schemas/deprecated/` — §6's gate, because accepted work validates against them.
 (d) A v1-shaped record still validates against v1, and a v2-shaped record against v2.
 (e) Every live manifest reference now names `v2`; the only surviving `v1` references are
 in audit records of already-accepted work.
**Fixtures:** `tests/fixtures/contract_v1_edited_in_place.reject.json` (`expected_error:
v1-contract-mutated`); `tests/fixtures/decision_v2_missing_executed.reject.json`
(`expected_error: 'executed_model' is a required property`).
**Failure means:** the phase-2 gates below are checking fields nobody authored — the v4
defect. Or v1 was mutated, retroactively invalidating accepted records.

**`FR-P2-SEL-MAPPED`** · 2 · class `mapping`
`python3 tests/gates/fr_p2_selector.py --check sel-mapped`
**Pass:** each of the five `SEL-*` ids in `policy/checks.v1.yaml` names (i) an owner file
that exists — the manifest or prompt section stating the rule — and (ii) a verification
method drawn from rule 6's vocabulary. Where the method is `schema` or `declaration`, the
named artifact exists and a gate here exercises it. Where the method is `execution`, the
id carries a `§12` follow-up reference and is recorded `MAPPED, NOT EXECUTED` — never as
covered. Both directions: no `SEL-*` id without an owner, no owner section without an id.
**Fixture:** `tests/fixtures/check_id_without_owner.reject.yaml`, `expected_error:
advertised-without-owner`.
**Failure means:** gate **B3** and `DRIFT-NO-MISREPORTING` — a check named but owned by
nothing. This is what `:157`'s "selector enforcement" claims today, backed by none of the
39 existing check ids.

**`FR-P2-DECISION-VALID`** · 2 · class `schema`
`python3 tests/gates/fr_p2_selector.py --check decision`
**Pass:** a well-formed decision record validates against
`schemas/routing_decision.schema.v2.json`; all ten required fields present; the record's
`decided_model` is a member of `policy/routing/model_registry.v1.yaml`.
**Fixtures:** `decision_missing_effort.reject.json` (`expected_error:
'reasoning_effort' is a required property`); `decision_model_not_in_registry.reject.json`
(`expected_error: model-not-in-registry`).
**Failure means:** decisions can be recorded that no one can check — an audit trail that
cannot be audited. Legitimately static: the contract and the registry are both files.

**`FR-P2-BYPASS-DECLARED`** · 2 · class `declaration`
`python3 tests/gates/fr_p2_selector.py --check bypass-declared`
**Pass:** three conditions, split by what each mechanism can actually do.
 (a) **Stated:** the prohibition on `--model` bypassing the selector appears in the meta
 prompt's `§ Routing` and in `policy/controller.v1.yaml` (promoted from `:148`), with
 `SEL-NO-MODEL-BYPASS` in `policy/checks.v1.yaml`.
 (b) **Representable (schema):** `routing_decision.schema.v2.json` *requires both*
 `decided_model` and `executed_model`, so a record that omits either is rejected. The
 schema is not asked to compare them: standard JSON Schema cannot compare two sibling
 values without enumerating every pair.
 (c) **Compared (gate code):** the gate itself reads both fields and fails the record
 when they differ. This comparison lives in `fr_p2_selector.py`, is named in the result
 record as `comparison: python`, and is the reason this gate is class `declaration` and
 not `schema`.
**Fixture:** `tests/fixtures/model_override_bypass.reject.json` — valid against the
schema, `decided_model != executed_model`; `expected_error:
executed-differs-from-decided`. That it passes (b) and fails (c) is the point.
**Failure means:** the rule is unstated, or unrepresentable in the record format — so no
future runtime could check it. **It does not mean bypass is impossible**: nothing
executes `--model` today. Runtime enforcement is §12.

**`FR-P2-UNRECORDED-DECLARED`** · 2 · class `declaration`
`python3 tests/gates/fr_p2_selector.py --check unrecorded-declared`
**Pass:** three conditions.
 (a) `policy/failures.v1.yaml` carries an id whose condition is "a model call with no
 decision record" and whose outcome is `META_SYSTEM_FAILURE`;
 (b) `policy/controller.v1.yaml` maps that condition to that terminal state, and the meta
 prompt states the obligation that every call emits a schema-valid decision;
 (c) a model-call record without `decision_id` is **rejected by
 `execution_log.schema.v2.json`**, via the conditional requirement in
 `FR-P2-CONTRACT-VERSIONED` (b), while a non-model action without one is accepted.
**Fixtures:** `tests/fixtures/call_without_decision.reject.json` (`expected_error:
'decision_id' is a required property`); `tests/fixtures/nonmodel_action_no_decision.json`
— a **positive** fixture that must validate, proving the condition is not
over-broad.
**Failure means:** the obligation is not written down anywhere a future runtime could read
it. v2 of this plan claimed the gate proved runtime behaviour from a *simulated* call; v4
pointed it at a `decision_id` field that did not exist. Phase 2 now authors the field.

**`FR-P2-GATEITEMS`** · 2 · class `mapping`
`python3 tests/gates/fr_p2_selector.py --check gate-items`
**Pass:** every gate item advertised in the meta prompt's release table maps to a check
id in `policy/checks.v1.yaml`.
**Fixture:** `tests/fixtures/gate_item_without_check.reject.md`, `expected_error:
gate-item-unbacked`.
**Failure means:** the build advertises coverage it does not have.

### Phase 3 — calibration boundaries

**`FR-P3-SPLIT`** · 3 · class `schema`
`python3 tests/gates/fr_p3_calibration.py --check split`
**Pass:** `policy/calibration.v1.yaml` contains no `power` block and no kit term;
`curricula/arduino_kit/kit_calibration.v1.yaml` contains the permitted inputs, rails and
3–5 V range; both validate against their schemas.
**Fixture:** `tests/fixtures/global_calibration_with_kit_power.reject.yaml`,
`expected_error: kit-fact-in-global-calibration`.
**Failure means:** a second curriculum would silently inherit ELEGOO's supplies.

**`FR-P3-NO-LITERALS`** · 3 · class `text`
`python3 tests/gates/fr_p3_calibration.py --check literals`
**Pass:** no file in `schemas/` contains a learner-age literal or a kit name.
**Fixture:** `tests/fixtures/schema_with_learner_literal.reject.json`, `expected_error:
data-fact-in-contract`.
**Failure means:** F03 persists — `lab.schema.v3.json:54,675` hard-code
`"nine-year-old"`, so the contract cannot serve a different learner.

**`FR-P3-CAPS-OWNED`** · 3 · class `text`
`python3 tests/gates/fr_p3_calibration.py --check caps`
**Pass:** each pedagogy cap value appears in `policy/calibration.v1.yaml` and in the
schema constraint named by `enforced_by`, and nowhere in prose. Covers the six copies in
`pedagogy.v1.md` at `:27`, `:55`, `:85–86`, `:87`, `:99,105`, `:100–101`. Production scan
excludes `tests/fixtures/**` per harness rule 7.
**Fixture:** `tests/fixtures/prose_with_cap_value.reject.md`, `expected_error:
unowned-cap-copy`.
**Failure means:** F05–F07, F09, F10 persist — prose copies that drift silently because
nothing keeps them equal.

**`FR-P3-CAL-AGREE`** · 3 · class `schema`
`python3 tests/gates/fr_p3_calibration.py --check cal-agree`
**Pass:** `CAL-SCHEMA-AGREE` holds after the split — every value in `pedagogy_caps`
equals the schema constraint named in `enforced_by`.
**Fixture:** `tests/fixtures/cap_schema_mismatch.reject.yaml`, `expected_error:
cap-schema-disagreement`.
**Failure means:** the split broke the one derivation this repo already enforces
correctly.

**`FR-P3-KIT-SOURCE`** · 3 · class `schema`
`python3 tests/gates/fr_p3_calibration.py --check kit-source`
**Pass:** `CAL-SOURCE-VERIFIED` resolves against `kit_calibration.v1.yaml`; every powered
lab cites exactly one input id present there, whose verification is `verified_official`.
**Fixture:** `tests/fixtures/lab_cites_unverified_input.reject.yaml`, `expected_error:
unverified-source-cited`.
**Failure means:** a lab can cite a supply nobody photographed — the safety premise the
whole calibration file exists to hold.

### Phase 4 — policy schemas and mapping

**`FR-P4-ALL-VALIDATE`** · 4 · class `schema`
`python3 tests/gates/fr_p4_policy_schemas.py --check validate`
**Pass:** all six `policy/*.yaml` and all four `policy/routing/*.yaml` validate against a
named schema in `schemas/`. The routing four validate against the four schemas added this
phase — `model_registry.schema.v1.json`, `task_taxonomy.schema.v2.json`,
`routing_policy.schema.v1.json`, `quality_gates.schema.v1.json` — one each. Prints the
ten manifest→schema pairs.
**Fixture:** `tests/fixtures/policy_manifest_unschemaed.reject.yaml`, `expected_error:
no-schema-for-manifest`.
**Failure means:** a file code depends on can be malformed without anything noticing.
*(v4 required these ten pairs while naming only six of the schemas — the routing four
existed in no tree.)*

**`FR-P4-AGREEMENT`** · 4 · class `schema+mapping`
`python3 tests/gates/fr_p4_policy_schemas.py --check agreement`
**Pass:** three manifest-internal agreements, each checkable against files that exist —
 (a) every `limits` entry carries both a number and a flag;
 (b) every `failures` id names a correction **and** a verification owner — either a gate
 id in `tests/gates/` or a `§12` follow-up id, recorded as which;
 (c) the `checks.v1.yaml` mapping relation of `FR-P4-CHECK-MAPPING`, asserted from the
 manifest side.
**Out of scope, by design:** *"`controller` states ↔ implemented states"* and *"every
`routes` entry carries recorded proof"* — both compare a manifest to a running system
(§12).
**Fixture:** `tests/fixtures/limit_without_number.reject.yaml`, `expected_error:
limit-missing-value`.
**Failure means:** shape is proven but internal agreement is not — a manifest can describe
a machine that contradicts itself. `limits.v1.yaml`'s own header states the consequence: a
limit without a number can never be exceeded, so its drift rule never fires.

**`FR-P4-FIXTURE-BITES`** · 4 · class `schema`
`python3 tests/gates/fr_p4_policy_schemas.py --check fixture-bites`
**Pass:** `curricula/arduino_kit/fixtures/l01_polarity_asserted.reject.json` is rejected
by `schemas/circuit_data.schema.v1.json` with the polarity-assertion violation.
**Fixture:** the file itself; `expected_error: polarity-asserted-on-unpowered-path`. It
lives under `curricula/`, not `tests/fixtures/`, and is therefore in the production scan
set — intentionally: it is curriculum evidence, and its `.reject.` suffix marks it for
the parse gate as an expected-invalid instance.
**Failure means:** the reject fixture is inert — declared in `checks.v1.yaml:63,65` but
rejected by nothing, which is `L01-POLARITY-NEUTRAL` in name only.

**`FR-P4-CHECK-MAPPING`** · 4 · class `mapping`
`python3 tests/gates/fr_p4_policy_schemas.py --check mapping`
**Pass:** for **every** id in `policy/checks.v1.yaml`, both —
 (a) an **owner**: the file that states the rule, and it exists;
 (b) a **verification method** from rule 6's vocabulary, plus the artifact carrying it — a
 schema path, a gate id, or a `§12` follow-up id.
Each id is recorded `VERIFIED HERE` or `MAPPED, NOT EXECUTED`; the gate prints both
counts. Reverse direction: every id this harness touches appears in `checks.v1.yaml`, and
no `FR-*` id appears there (harness rule 1). Production scan excludes `tests/fixtures/**`.
**Explicitly not required:** that every curriculum check be executed by this suite. Many
require a controller, an execution log, a PDF renderer or a live route — none of which
exists (§3) — and harness rule 1 forbids a curriculum check from living in
`tests/gates/`. Execution coverage is §12's acceptance criterion.
**Fixture:** `tests/fixtures/orphan_check_id.reject.yaml`, `expected_error:
advertised-without-owner`.
**Failure means:** gate **B3** in the form this plan *can* close — an id advertised with
no owner and no stated way of ever being verified. The stronger form, where an id has an
owner but nothing executes it, is reported as a count, never hidden as a pass.

### Final regression

**`FR-ALL`** · after phase 4
`./tests/run_gates.sh 4`
**Pass:** `FR-P0-HARNESS` passes first; all 30 gates execute and pass; every negative
fixture fails for its declared `expected_error`; every positive fixture validates; a
result file is written to `tests/results/`; `git status --porcelain` is empty. The report
states the `MAPPED, NOT EXECUTED` count from `FR-P4-CHECK-MAPPING` explicitly — a plan
that ends with unexecuted checks says so.
**Failure means:** return `BLOCKED` naming the failing gate id and its stated failure
meaning. `APPROVED` is legal only when all four conditions in harness rule 5 hold.

---

## 9. Phases

One commit per phase. A phase begins only after the previous phase's gates pass.
`run_gates.sh N` runs `FR-P0-HARNESS`, then phase *N*'s gates **plus all earlier gates** —
earlier gates are regressions from the moment they activate.

**Gates run against a commit, never against a dirty tree.** `FR-P0-HISTORY` reads `HEAD`
and `FR-P0-CLEAN` requires an empty `git status`; neither can pass before the phase is
committed. Each phase is: implement → review → **commit** → validate → amend and
re-validate on failure. The commit is a *candidate* until validation passes, and is
amended, never appended to.

| Phase | Work | Gates run | New gates |
|---|---|---|---|
| **0** | every move in §5 plus every fix in §10, one atomic commit; create `tests/` with `registry.py` declaring **all 30 gates**, `common.py`, `run_gates.sh`, `selftest.py`, `.gitignore`, and the ten phase-0 gates | `run_gates.sh 0` | 10 |
| **1** | the four `deprecated/` folders, `.gitkeep`s, retention rule written into `AGENTS.md` | `run_gates.sh 1` | 3 |
| **2** | **both contract v2 schemas**; `§ Routing` in the meta prompt; the five `SEL-*` ids in `checks.v1.yaml`, each with owner and method; the unrecorded-call failure id and its controller mapping | `run_gates.sh 2` | 8 |
| **3** | calibration split; strip data literals from `schemas/`; reduce `pedagogy.v1.md` to rationale | `run_gates.sh 3` | 5 |
| **4** | six policy schemas + `circuit_data` + **the four routing-manifest schemas**; agreement and check mapping | `run_gates.sh 4` | 4 |
| **final** | no new work — full regression | `FR-ALL` | — |

**Phase 0, in order.**

1. Write `tests/` — `registry.py` first, declaring all 30 gate ids with phase and claim
   class; then `common.py`, `run_gates.sh`, `selftest.py`, the ten phase-0 gates,
   fixtures, `selftest/`, `results/.gitkeep` — and `.gitignore`.
2. Stage rule 1 as a rename: `git add -A schema schemas`, then
   `git diff --cached --name-status -M100%` → **exactly four `R100` lines**. Stop here if
   not; nothing downstream recovers the history once it is committed as add/delete.
3. `git mv` rules 2–13.
4. Apply §10's content edits — **after** step 2, because editing
   `schemas/lab.schema.v3.json` first drops it below the `R100` threshold.
5. **Commit** the candidate.
6. Run `./tests/run_gates.sh 0`. Expect ten passes and twenty
   `SKIPPED (activates at phase M)` lines — the skips are what `FR-P0-REGISTRY` makes
   possible.
7. On any failure: fix, `git commit --amend`, re-run from 6. The commit is unshared, so
   amending is safe.

Phase 0 is one commit because splitting it would rewrite the same reference lines two or
three times, which is how the `work/elegoo_labs/…` ghost paths survived five attempts.

**Phase 2 content — prose *and* contracts.** `routing/` is orphaned today: the meta prompt
names it twice (`:63` a bare row, `:230` a directory name) and states no rule, while
`:157` advertises "selector enforcement" that none of the 39 check ids covers — the only
near-match, `ROUTE-PROVEN` at `checks.v1.yaml:193`, is external-capability preflight. The
failed v3 prompt was more explicit here
(`component_lab_orchestrator_prompt.v3.md:122`).

*The prose.* The new `§ Routing` **binds, never inlines**: it names the six authorized
inputs, states the invariants no data file can express (the selector runs first and code
applies the result; `--model` may not bypass it, promoted from `controller.v1.yaml:148`;
no model at all for merge, validation, hashing, rendering, aggregation, audits or the
logger; cheapest eligible route for bounded drafting, stronger for electronics design and
QA, maximum reasoning only for failed safety escalation; no redundant drafts, serial by
default; no model approves its own unsupported technical claim, promoted from
`routing/readme.md`), states the obligation that every call emits a schema-valid decision
and records the route actually executed, and separates `policy/routes.v1.yaml` (proven
capabilities) from `policy/routing/` (which model serves which task).

*The contracts.* §3 records that neither obligation is currently expressible. Phase 2
authors two new schema versions, additively, per §6:

- **`schemas/routing_decision.schema.v2.json`** — v1's nine required fields with
  `selected_model` renamed `decided_model`, plus a required `executed_model`. The rename
  is deliberate: `selected` names an intention, and the invariant is about the difference
  between what was *decided* and what *ran*. Everything else — `candidate_pool`,
  `reasoning_effort`, `quality_gate`, `status` and the optional `pro_mode`,
  `evidence_inputs`, `escalate_when`, `substitution` — carries over unchanged.
- **`schemas/execution_log.schema.v2.json`** — adds `decision_id` to the `act` record,
  required **conditionally**: `if` the action matches the model-call pattern, `then
  required: ["decision_id"]`. `if/then` is standard draft 2020-12, so this obligation
  *is* schema-expressible, unlike the decided/executed comparison. A file-write or a
  hash action must not be forced to carry a decision id; a model call must.

Both v1 files stay in `schemas/`, unedited (§6): accepted work was validated against them.
`FR-P2-CONTRACT-VERSIONED` proves the bump and the non-mutation together.

*What phase 2 does and does not achieve.* It makes the routing rules stated, owned, and —
now — **representable in a record a future runtime could emit and a validator could
check**. It does not make them enforced, because there is nothing to enforce them in.
`FR-P2-BYPASS-DECLARED` splits its own evidence across schema and gate code precisely so
that this stays legible: JSON Schema proves both fields exist; Python compares them; only
a controller could refuse to act on the difference. §12 names that work.

The five new ids: `SEL-DECISION-VALID`, `SEL-NO-MODEL-BYPASS`,
`SEL-NO-MODEL-FOR-DETERMINISTIC`, `SEL-ESCALATION-BOUNDED`,
`SEL-EXECUTED-MATCHES-DECIDED` — deliberately not `ROUTE-*`, since "route" already means
external capability. Each is added with an owner file and a verification method per
`FR-P2-SEL-MAPPED`; those needing a runtime are added as `MAPPED, NOT EXECUTED` with a
§12 reference, not as covered.

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
| `plans/folder_refactoring/` | move the v1–v4 plan/prompt pairs into `deprecated/`; the active pair is **v5**, and `prompt.v5.md:5` names this file — held true thereafter by `FR-P0-PLANREF` |

Phase 0 changes **paths only**. The `v1`→`v2` contract references are phase-2 work,
proven by `FR-P2-CONTRACT-VERSIONED` (e), and must not be pre-applied here: phase 0 has
no v2 files to point at.

Pre-existing defects fixed while these files are open — the `work/elegoo_labs/…` ghost
paths (F25) in `arduino_kit_curriculum.v4.yaml:20`, `l01_unpowered_power_path.json:6`,
and `l01_polarity_asserted.reject.json:6`.

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Phase 0 is a large commit | entirely path changes, gated by `FR-P0-*`; smaller commits mean rewriting the same lines repeatedly |
| Gates that cannot run when the plan says to run them | §9: commit, then validate, then amend. `FR-P0-HISTORY` and `FR-P0-CLEAN` are marked **runs against the commit** in §8 |
| The runner runs the gates in an order that defeats them | harness rule 2 — `FR-P0-HARNESS` first, then ID order; ID order alone puts `CLEAN` and `DEPS` ahead of the gate that proves the runner |
| A later gate cannot be reported as skipped because it does not exist | harness rule 2's single registry, declared in full at phase 0; `FR-P0-REGISTRY` proves 30 declared and names how many are implemented |
| The rule-1 rename loses history | §5's staging rule with `git diff --cached --name-status -M100%`, run **before** §10's edits; `FR-P0-HISTORY` then verifies four renames in `HEAD` plus `--follow` to baseline |
| **A gate checks a field nobody authored** | §3 records the two contracts' actual required lists; phase 2 authors v2 of both; `FR-P2-CONTRACT-VERSIONED` runs before the gates that depend on them |
| Versioning a contract invalidates accepted work | §6 — v2 is additive and v1 stays in `schemas/`, unedited; `FR-P2-CONTRACT-VERSIONED` (c) proves non-mutation, and `FR-P1-SCHEMA-RETENTION` keeps v1 out of `deprecated/` |
| A rule that JSON Schema cannot express is written as if it could | `FR-P2-BYPASS-DECLARED` splits into stated / representable / compared, with the comparison in Python and recorded as `comparison: python` |
| A conditional requirement is over-broad | `FR-P2-UNRECORDED-DECLARED` carries a **positive** fixture: a non-model action with no `decision_id` must still validate |
| A phase-4 gate requires a schema that exists nowhere | the four routing-manifest schemas are named in §4 and in the phase-4 work row; `FR-P4-ALL-VALIDATE` prints all ten manifest→schema pairs |
| **The harness is new code and is its own oracle** | `FR-P0-HARNESS` runs first and tests the six behaviours no per-gate fixture reaches — phase selection, exit propagation, result integrity, wrong-reason detection, no-overwrite, scan isolation. Its failure invalidates the whole run |
| A gate claims more than it proves | harness rule 6 — claim class is an ordered set, recorded in the result JSON; no gate claims execution of a controller or routing runtime, and `MAPPED, NOT EXECUTED` is a count, never a pass |
| A broken gate cannot be fixed, or a gate is edited to pass | §7's closing rule — implementation may be corrected and is recorded as `gate_impl_fix`; acceptance criteria may never be weakened |
| A gate rejects its own subject | harness rule 7 for fixtures; `FR-P0-PLANREF` checks version relationships rather than scanning a plan for the paths it exists to move |
| Results dirty the worktree | `tests/results/*.json` ignored, folder kept by `.gitkeep` |
| Moving `legacy/` breaks `failures.v1.yaml` citations | edited in the same commit; `FR-P0-NOSTALE` greps for survivors |
| The executing agent reads a superseded plan | `FR-P0-PLANREF`; v1–v4 and their prompts move to `deprecated/` in phase 0 |
| `redundancy.analysis.v1.md` line numbers are stale — it cites `readme.md:63`, now a one-line file | findings hold, line refs do not; re-verify at edit time |

---

## 12. Out of scope

**Runtime enforcement and execution coverage.** This plan makes the rules stated, owned,
mapped, and representable in records a validator can check. It cannot make them
*executed*, because no controller, execution log writer, renderer or live route exists
(§3). The follow-up needs an implementation. Its acceptance criteria are exactly the
obligations this plan records but cannot discharge:

- every state in `policy/controller.v1.yaml` is reachable in an implemented state machine,
  and no implemented state is absent from the manifest;
- every entry in `policy/routes.v1.yaml` carries proof recorded from an actual execution;
- a call whose `executed_model` differs from its `decided_model` is *rejected at runtime*,
  not merely detected by a gate reading a static fixture
  (`FR-P2-BYPASS-DECLARED` → `-ENFORCED`);
- a model call with no `decision_id` *terminates* the run as `META_SYSTEM_FAILURE`, rather
  than merely failing schema validation after the fact
  (`FR-P2-UNRECORDED-DECLARED` → `-FATAL`);
- every id `FR-P4-CHECK-MAPPING` reports as `MAPPED, NOT EXECUTED` becomes executed, and
  every A-series id in `policy/failures.v1.yaml` gains a proving test;
- the logger emits `execution_log.schema.v2.json`-valid records, at which point v1 becomes
  retirable under §6's gate.

Until then, no document, gate name or report may state that the selector is enforced or
that the check suite is fully executed.

**Also out of scope.** Curriculum content; the F86 finding that 14 of 35 labs declare
`adult_led_controller_station` while four prose documents forbid a controller; the 25
contradictions in `redundancy.analysis.v1.md` beyond the paths named in §10; rendering
`docs/how_it_works.png`; anything under `plans/` except the archiving of v1–v4 and the
prompt retarget in §10.

F86 is a substantive contradiction about what the workbook *is* and needs its own
decision. It is recorded here only so this refactor is not mistaken for having addressed
it.
