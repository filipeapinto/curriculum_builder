# Folder refactoring — plan v3

**Date:** 2026-07-30
**Supersedes:** `deprecated/folder_refactoring.plan.v2.md` (and, through it, v1)
**Status:** accepted, not started. No file has been moved or edited under this plan.
**Scope:** folder layout, file placement, the references that name them, and a committed
harness that proves each phase. Not curriculum content. Not a runtime implementation.

**What v2 added over v1.** Every gate got a stable ID, an activation phase, an exact
command, pass criteria, a rejection fixture where one applies, and a stated failure
meaning. Gates are cumulative: phase *N* runs its own gates plus every earlier gate.

**What v3 adds over v2.** v2 was reviewed against the repository as it actually stands and
nine defects were found — three of them gates that could not pass as written, two of them
gates that would reject themselves. v3 fixes all nine:

1. **`git mv` is impossible for the schema files** — the rename already happened outside
   version control. §5 now specifies staging both paths together and verifying `R100`.
2. **Three gates claimed runtime enforcement with no runtime to enforce it.** Renamed and
   restated as declaration/record conformance; the runtime obligation moves to §12 as a
   named follow-up. New harness rule 6 makes the claim class explicit for every gate.
3. **Prompt version drift** — v2's tree and ledger named `prompt.v1.md`. Corrected to v3.
4. **`FR-P0-NOSTALE` excluded all of `plans/**`**, so it could not enforce the one
   in-scope `plans/` edit. New `FR-P0-PLANREF` covers the active plan files only.
5. **Bootstrap trust** — the harness had no test of its own and v2's mitigation was
   self-contradictory. New `FR-P0-HARNESS` self-test suite; §11 corrected.
6. **`FR-P0-TREE`'s count was wrong** — §5's 13 rules cover 26 files, not 13 paths.
7. **Detectors rejected their own fixtures** — tracked rejection fixtures contain the
   very strings the production scans forbid. Global exclusion rule, harness rule 7.
8. **Results vs. clean worktree were mutually exclusive** — every run wrote a tracked
   file into a committed folder while validation demanded an empty `git status`.
   `tests/results/*.json` is now ignored; the folder survives via `.gitkeep`.
9. **`FR-P1-GITKEEP`'s fixture could not exist** — an empty `deprecated/` directory
   cannot be committed, which is the defect it tests. Now synthesized at runtime.

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
  paths no longer exist in the working tree. Git records snapshots, not commands, so
  history is still recoverable — see the staging rule in §5.
- Four kit files moved into `curricula/arduino_kit/` earlier
  (`arduino_kit_curriculum.v4.yaml`, `kit_evidence.md`, `official_kit_photo.jpg`,
  `lab_brief.md`) and no reference was updated. `AGENTS.md:16`'s validation command
  opens `assets/curriculum.v4.yaml`, which no longer exists, so it fails today.
- `meta_prompt/deprecated/` exists on disk, is empty, and is therefore absent from the
  baseline commit — a convention that disappears on clone.
- `.pytest_cache/v/cache/nodeids` is `[]`. No automated test has ever been collected.
  The harness in §7 is the first executable check in this repository.
- **There is no controller implementation.** The only runner in the repository is
  `assets/legacy/run_curriculum.v3.py`, which this plan archives to `plans/legacy_v3/`
  as evidence. Nothing in scope executes a model, records a routing decision, or
  transitions a controller state. Every gate in §8 is therefore a static check over
  files, and §8 says so per gate. See §12.

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
│   ├── execution_log.schema.v1.json
│   ├── routing_decision.schema.v1.json         ← meta_prompt/routing/
│   ├── checks.schema.v1.json                   NEW (phase 4)
│   ├── controller.schema.v1.json               NEW (phase 4)
│   ├── limits.schema.v1.json                   NEW (phase 4)
│   ├── routes.schema.v1.json                   NEW (phase 4)
│   ├── failures.schema.v1.json                 NEW (phase 4)
│   ├── circuit_data.schema.v1.json             NEW (phase 4)
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
    │   ├── folder_refactoring.plan.v3.md       this file
    │   ├── folder_refactoring.prompt.v3.md     the execution prompt
    │   └── deprecated/
    │       ├── folder_refactoring.plan.v1.md · folder_refactoring.prompt.v1.md
    │       └── folder_refactoring.plan.v2.md · folder_refactoring.prompt.v2.md
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

Nothing is deleted.

**How to move, so that history follows.**

- **Rules 2–13 — sources still exist in the working tree.** Use `git mv`.
- **Rule 1 — the source no longer exists.** `schema/` was moved on disk outside version
  control (§3), so `git mv schema/x.json schemas/x.json` fails: there is nothing at the
  source path. Git stores snapshots and detects renames from content, so the history is
  intact provided **both sides are staged in the same commit**:

  ```
  git add -A schema schemas
  git status --porcelain=v1 -M        # expect four R100 lines, none  D + ?? pairs
  ```

  The four files must be byte-identical to their `HEAD` versions at the moment of
  staging. **Stage the rename first and verify `R100` before applying any content edit
  from §10** — editing before staging lowers the similarity score and can break
  `--follow`. `FR-P0-HISTORY` checks the committed result, not the intent.

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

`docs/` has no `deprecated/`: its explainers are regenerated from `.typ`, and an archive
of stale claims is a drift risk rather than a record.

---

## 7. The harness

**Location:** `tests/`, committed. Consumer is code, so it obeys §1.

```
tests/
├── run_gates.sh                  ./tests/run_gates.sh <phase>   → runs every gate whose
│                                 activation phase ≤ <phase>, in ID order
├── gates/
│   ├── common.py                 path constants, scan roots, fixture runner, recorder
│   ├── fr_p0_structure.py        FR-P0-*
│   ├── fr_p1_retention.py        FR-P1-*
│   ├── fr_p2_selector.py         FR-P2-*
│   ├── fr_p3_calibration.py      FR-P3-*
│   ├── fr_p4_policy_schemas.py   FR-P4-*
│   └── selftest.py               FR-P0-HARNESS — proves the harness, see rule 8
├── fixtures/                     negative fixtures, named <subject>.reject.<ext>
│                                 per the existing convention
├── selftest/                     synthetic inputs for selftest.py only
└── results/.gitkeep              gate_results.p<phase>.<utc-timestamp>.json — ignored
```

**Harness contract — eight rules, none optional.**

1. **Gate IDs are `FR-P<phase>-<NAME>`.** The `FR-` prefix keeps refactor gates
   distinguishable from curriculum check ids in `policy/checks.v1.yaml` (`CAL-`,
   `CUR-`, `L01-`, `LAB-`, `PDF-`, `LOG-`, `REV-`, `DRIFT-`, `SEL-`). A refactor gate
   never appears in `checks.v1.yaml`, and a curriculum check never appears in
   `tests/gates/`.
2. **Cumulative, never premature.** Each gate declares `activation_phase`.
   `run_gates.sh N` executes gates with `activation_phase <= N` and *skips* later ones
   with an explicit `SKIPPED (activates at phase M)` line — a skip is recorded, never
   silent, and never counted as a pass.
3. **A negative fixture must fail for its stated reason.** Every fixture declares an
   `expected_error` pattern. A fixture that fails for a different reason — a parse
   error where a constraint violation was expected — is a **gate failure**, not a pass.
   This is the difference between a fixture that proves a rule and one that merely
   errors.
4. **Results are recorded, never asserted.** Each run writes one JSON file to
   `tests/results/` containing, per gate: id, activation phase, claim class (rule 6),
   command, exit code, stdout digest, pass/fail/skip, and each fixture's outcome with
   the matched error. Files are never overwritten. Per `AGENTS.md:25`, an unexecuted
   check is never reported as passing.
   **`tests/results/*.json` is listed in `.gitignore`**; the folder is kept by
   `tests/results/.gitkeep`. This is what makes rule 5's two conditions — "results
   written" and "worktree clean" — simultaneously satisfiable. `git status --porcelain`
   does not list ignored files, so a run leaves the tree clean by construction.
5. **`APPROVED` requires all four:** every gate through the current phase passes; every
   negative fixture failed for its intended reason; results are written; the worktree is
   clean. Any missing element returns `BLOCKED` with the specific cause.
6. **Every gate declares its claim class, and may not claim more.** One of:
   - `tree` — a path exists or does not exist.
   - `parse` — a file parses.
   - `schema` — an instance validates, or fails to validate, against a JSON Schema.
   - `text` — a string is present or absent in a tracked file.
   - `declaration` — a manifest or prompt *states* a rule, and a record conforming to
     that rule validates while a violating record does not.
   - `execution` — a program was run and behaved as claimed.

   **No gate in this plan carries the `execution` class**, because §3 records that no
   controller exists. A gate's ID, pass line, and failure meaning must be phrased in its
   own class: a `declaration` gate says a rule is *stated and checkable*, never that it
   is *enforced at runtime*. Enforcement is §12.
7. **A production scan never reads a fixture.** Every detector takes an explicit scan
   root set. The production set excludes `tests/fixtures/**`, `tests/selftest/**`,
   `tests/results/**`, `plans/**/deprecated/**` and `.git/**`. A detector is proven
   against its own fixture by a **separate** invocation pointed at the fixture path.
   Without this, `FR-P0-NOSTALE`, `FR-P2-NOVALUES`, `FR-P2-SEL-ADVERTISED`,
   `FR-P3-CAPS-OWNED` and `FR-P4-COVERAGE` all fail on their own tracked fixtures.
8. **The harness is proven before it is trusted.** `FR-P0-HARNESS` runs first in phase 0
   and gates every other result. Fixtures under `tests/selftest/` are synthetic and
   never touch the repository tree.

---

## 8. Gate catalogue

Format: **ID** · activation phase · claim class · command · pass criteria · rejection
fixture · failure meaning.

### Phase 0 — harness, structure, existing validation

**`FR-P0-HARNESS`** · 0 · class `execution` (of the harness, the one program that does
exist)
`python3 tests/gates/selftest.py`
**Pass:** all six self-tests pass, each named in the result record —
 (a) **phase selection**: a synthetic gate with `activation_phase 4` is reported
 `SKIPPED` at `N=0` and `PASS` at `N=4`;
 (b) **exit propagation**: an injected failing gate makes `run_gates.sh` exit non-zero;
 (c) **result integrity**: the JSON contains exactly one entry per registered gate — a
 gate that never ran appears as such and cannot be absent;
 (d) **wrong-reason detection**: a fixture that fails with an error other than its
 `expected_error` is recorded `FAIL`, not `PASS` (rule 3, tested rather than asserted);
 (e) **no-overwrite**: two runs in the same second produce two files;
 (f) **scan isolation**: a production detector pointed at the production root does not
 read `tests/fixtures/**` (rule 7).
**Fixtures:** `tests/selftest/*` — synthetic, generated or committed under `selftest/`,
never scanned by a production check.
**Failure means:** every other result in this run is unreliable. Return `BLOCKED`
immediately; do not report any other gate's outcome.

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
all tracked files **except the rule-7 exclusion set and `plans/**`** (active plan files
are covered by `FR-P0-PLANREF`). Prints `FR-P0-NOSTALE PASS (0 hits, N files scanned)`.
**Fixture:** `tests/fixtures/stale_reference.reject.md` — contains the literal
`assets/calibration.v1.yaml`; the detector must flag it **when pointed at the fixture
path**, `expected_error: stale-path:assets/`. The same detector run against the
production root must not see this file at all — that is self-test (f).
**Failure means:** reference debt survived the move; some consumer will resolve a dead
path. This is the exact failure that produced the `work/elegoo_labs/…` ghosts.

**`FR-P0-PLANREF`** · 0 · class `text`
`python3 tests/gates/fr_p0_structure.py --check planref`
**Pass:** within `plans/folder_refactoring/*.v3.md` only — zero stale paths from the
`FR-P0-NOSTALE` pattern set except where quoted as a forbidden literal in §5/§8/§10, and
the prompt's `:5` names `folder_refactoring.plan.v3.md`, the newest plan present.
`plans/**/deprecated/**` and every other plan folder stay excluded: they are history and
are allowed to name dead paths.
**Fixture:** `tests/fixtures/prompt_targets_old_plan.reject.md` — a prompt whose goal
line names `plan.v2.md`; `expected_error: plan-ref-stale`.
**Failure means:** the executing agent is reading a superseded plan — the v2 defect where
the tree and ledger still named `prompt.v1.md` while the live prompt was v2.

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

**`FR-P0-HISTORY`** · 0 · class `execution` (of `git`)
`python3 tests/gates/fr_p0_structure.py --check history`
**Pass:** two conditions.
 (a) `git log --follow -- <path>` returns the pre-move commit for **each of the 26 files**
 in §5.
 (b) For the four rule-1 files specifically, `git show --stat -M --diff-filter=R HEAD`
 lists them as `R100` — proving they were committed as renames of the `schema/` originals
 rather than as fresh additions, which `--follow` alone can mask.
**Fixture:** none — `git`'s own record is the oracle.
**Failure means:** a file was added and deleted rather than staged as a rename;
provenance is lost. If this fires on the rule-1 files, the likely cause is a §10 content
edit applied before staging (see §5) — reset, stage the rename, verify `R100`, then edit.

**`FR-P0-CLEAN`** · 0 · class `execution` (of `git`)
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

### Phase 2 — routing and selector

Every gate here is class `text`, `schema`, or `declaration`. None is class `execution`:
there is no selector to execute (§3). Three of v2's gates are renamed accordingly.

**`FR-P2-BOUND`** · 2 · class `text`
`python3 tests/gates/fr_p2_selector.py --check bound`
**Pass:** all five `policy/routing/` files and `schemas/routing_decision.schema.v1.json`
are named in the meta prompt's authorized-input table.
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

**`FR-P2-SEL-ADVERTISED`** · 2 · class `text`
`python3 tests/gates/fr_p2_selector.py --check advertised`
**Pass:** the five `SEL-*` ids appear in `policy/checks.v1.yaml` **and** each is executed
by an assertion in this harness — both directions.
**Fixture:** `tests/fixtures/check_id_without_assertion.reject.yaml`, `expected_error:
advertised-not-executed`.
**Failure means:** gate **B3** and `DRIFT-NO-MISREPORTING` — a check named but never run.
This is exactly what `:157`'s "selector enforcement" claims today, backed by none of the
39 existing check ids.

**`FR-P2-DECISION-VALID`** · 2 · class `schema`
`python3 tests/gates/fr_p2_selector.py --check decision`
**Pass:** a well-formed decision record validates against
`schemas/routing_decision.schema.v1.json`; all nine required fields present; the record's
model id is a member of `policy/routing/model_registry.v1.yaml`.
**Fixtures:** `decision_missing_effort.reject.json` (`expected_error:
'reasoning_effort' is a required property`); `decision_model_not_in_registry.reject.json`
(`expected_error: model-not-in-registry`).
**Failure means:** decisions can be recorded that no one can check — an audit trail that
cannot be audited. This gate is legitimately static: the contract and the registry are
both files.

**`FR-P2-BYPASS-DECLARED`** · 2 · class `declaration` — *was v2's `FR-P2-NO-BYPASS`*
`python3 tests/gates/fr_p2_selector.py --check bypass-declared`
**Pass:** two conditions, both about files.
 (a) The prohibition on `--model` bypassing the selector is **stated** in the meta
 prompt's `§ Routing` and in `policy/controller.v1.yaml` (promoted from `:148`), with
 `SEL-NO-MODEL-BYPASS` in `policy/checks.v1.yaml`.
 (b) A decision record whose `executed_model` differs from its `decided_model` is
 **rejected by the schema**, and a matching record is accepted.
**Fixture:** `tests/fixtures/model_override_bypass.reject.json`, `expected_error:
executed-differs-from-decided`.
**Failure means:** the rule is unstated, or unstatable in the record format — so no future
runtime could check it. **It does not mean bypass is impossible**: nothing executes
`--model` today. Runtime enforcement is §12.

**`FR-P2-UNRECORDED-DECLARED`** · 2 · class `declaration` — *was
`FR-P2-UNRECORDED-FATAL`*
`python3 tests/gates/fr_p2_selector.py --check unrecorded-declared`
**Pass:** `policy/failures.v1.yaml` carries an id whose condition is "a model call with no
decision record" and whose outcome is `META_SYSTEM_FAILURE`; `policy/controller.v1.yaml`
maps that condition to that terminal state; the meta prompt states the obligation that
every call emits a schema-valid decision.
**Fixture:** `tests/fixtures/call_without_decision.reject.json` — a call record with no
`decision_id`, which the execution-log schema must reject; `expected_error:
missing-decision-reference`.
**Failure means:** the obligation is not written down anywhere a future runtime could read
it. v2 claimed this gate proved behaviour "at runtime" from a *simulated* call — it never
could. §12 carries the real obligation.

**`FR-P2-GATEITEMS`** · 2 · class `text`
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

### Phase 4 — policy schemas and agreement

**`FR-P4-ALL-VALIDATE`** · 4 · class `schema`
`python3 tests/gates/fr_p4_policy_schemas.py --check validate`
**Pass:** all six `policy/*.yaml` and all four `policy/routing/*.yaml` validate against a
schema in `schemas/`.
**Fixture:** `tests/fixtures/policy_manifest_unschemaed.reject.yaml`, `expected_error:
no-schema-for-manifest`.
**Failure means:** a file code depends on can be malformed without anything noticing.

**`FR-P4-AGREEMENT`** · 4 · class `schema` + `text` — *narrowed from v2*
`python3 tests/gates/fr_p4_policy_schemas.py --check agreement`
**Pass:** three manifest-internal agreements, each checkable against files that exist —
 (a) every `limits` entry carries both a number and a flag;
 (b) every `failures` id names a correction **and** a proving test that exists in
 `tests/gates/`;
 (c) every `checks.v1.yaml` id maps to an executed assertion (the `FR-P4-COVERAGE`
 relation, asserted from the manifest side).
**Removed from v2:** *"`controller` states ↔ implemented states"* and *"every `routes`
entry carries recorded proof"*. Both compare a manifest to a running system; §3 records
that no such system exists in scope. They move to §12 verbatim as the follow-up's
acceptance criteria.
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

**`FR-P4-COVERAGE`** · 4 · class `text`
`python3 tests/gates/fr_p4_policy_schemas.py --check coverage`
**Pass:** every id in `policy/checks.v1.yaml` is executed by the suite, and every id the
suite reports appears in `policy/checks.v1.yaml` — both directions, no orphans. `FR-*`
ids are excluded from both directions by harness rule 1; production scan excludes
`tests/fixtures/**` by rule 7.
**Fixture:** `tests/fixtures/orphan_executed_id.reject.json`, `expected_error:
executed-not-advertised`.
**Failure means:** gate **B3** in its original form — the defect that failed the previous
build, where six ids were advertised and two asserted.

### Final regression

**`FR-ALL`** · after phase 4
`./tests/run_gates.sh 4`
**Pass:** `FR-P0-HARNESS` passes first; every gate above executes and passes; every
negative fixture fails for its declared `expected_error`; a result file is written to
`tests/results/`; `git status --porcelain` is empty.
**Failure means:** return `BLOCKED` naming the failing gate id and its stated failure
meaning. `APPROVED` is legal only when all four conditions in harness rule 5 hold.

---

## 9. Phases

One commit per phase. A phase begins only after the previous phase's gates pass.
`run_gates.sh N` runs phase *N*'s gates **plus all earlier gates** — earlier gates are
regressions from the moment they activate.

| Phase | Work | Gates run | New gates |
|---|---|---|---|
| **0** | every move in §5 (rule-1 staging first, `R100` verified) plus every fix in §10, one atomic commit; create `tests/` with `common.py`, `run_gates.sh`, `selftest.py`, `.gitignore`, and the phase-0 gates | `run_gates.sh 0` | 9 |
| **1** | the four `deprecated/` folders, `.gitkeep`s, retention rule written into `AGENTS.md` | `run_gates.sh 1` | 3 |
| **2** | `§ Routing` in the meta prompt; the five `SEL-*` ids in `checks.v1.yaml`; the unrecorded-call failure id and its controller mapping, **declared** | `run_gates.sh 2` | 7 |
| **3** | calibration split; strip data literals from `schemas/`; reduce `pedagogy.v1.md` to rationale | `run_gates.sh 3` | 5 |
| **4** | six policy schemas + `circuit_data.schema.v1.json`; manifest-internal agreement checks | `run_gates.sh 4` | 4 |
| **final** | no new work — full regression | `FR-ALL` | — |

**Phase 0 ordering.** Within the single commit: (i) write `tests/` and `.gitignore`;
(ii) stage rule-1 as a rename and verify four `R100` lines; (iii) `git mv` rules 2–13;
(iv) apply §10's content edits; (v) run `run_gates.sh 0`; (vi) commit. Step (ii) precedes
(iv) because a content edit before staging can drop the similarity below `R100` and cost
the history `FR-P0-HISTORY` exists to protect.

Phase 0 is one commit because splitting it would rewrite the same reference lines two or
three times, which is how the `work/elegoo_labs/…` ghost paths survived five attempts.

**Phase 2 content.** `routing/` is orphaned today: the meta prompt names it twice (`:63`
a bare row, `:230` a directory name) and states no rule, while `:157` advertises
"selector enforcement" that none of the 39 check ids covers — the only near-match,
`ROUTE-PROVEN` at `checks.v1.yaml:193`, is external-capability preflight. The failed v3
prompt was more explicit here (`component_lab_orchestrator_prompt.v3.md:122`). The new
section **binds, never inlines**: it names the six authorized inputs, states the
invariants no data file can express (the selector runs first and code applies the result;
`--model` may not bypass it, promoted from `controller.v1.yaml:148`; no model at all for
merge, validation, hashing, rendering, aggregation, audits or the logger; cheapest
eligible route for bounded drafting, stronger for electronics design and QA, maximum
reasoning only for failed safety escalation; no redundant drafts, serial by default; no
model approves its own unsupported technical claim, promoted from `routing/readme.md`),
states the obligation that every call emits a schema-valid decision and records the route
actually executed, and separates `policy/routes.v1.yaml` (proven capabilities) from
`policy/routing/` (which model serves which task).

The five new ids: `SEL-DECISION-VALID`, `SEL-NO-MODEL-BYPASS`,
`SEL-NO-MODEL-FOR-DETERMINISTIC`, `SEL-ESCALATION-BOUNDED`,
`SEL-EXECUTED-MATCHES-DECIDED` — deliberately not `ROUTE-*`, since "route" already means
external capability.

**What phase 2 does and does not achieve.** It makes the routing rules *stated, owned by
one file each, and checkable*. It does not make them *enforced*, because there is nothing
to enforce them in. That distinction is the whole point of harness rule 6, and §12 names
the work that closes it.

---

## 10. Reference-fix ledger

Rewritten in phase 0, in the same commit as the moves, **after** the rule-1 rename is
staged (§9). Line numbers verified 2026-07-30; re-verify each against the file at the
moment of editing.

| File | What to fix |
|---|---|
| `AGENTS.md` | `:5` asset/fixture locations · `:7` the `pedagogy.md` sentence · `:16` the validation command (both paths dead today) · `:29` note the retention rule · add `tests/` to the structure section |
| `.gitignore` | NEW or amended — `tests/results/*.json`; keep `tests/results/.gitkeep` tracked |
| `policy/calibration.v1.yaml` | 8 `schema/` refs incl. the whole `enforced_by` block · `:9` names four prose docs that have moved · `:38` `assets/official_kit_photo.jpg` |
| `policy/checks.v1.yaml` | `:3` schema path · `:63`, `:65` the fixture path |
| `policy/failures.v1.yaml` | the `assets/legacy/` citation requirement → `plans/legacy_v3/` · `:52` `work/elegoo_labs/…` provenance |
| `meta_prompt/meta_curriculum_builder.prompt.v5.md` | `:54–68` the input table · `:63` the bare `routing/` row · `:78–88` precedence · `:157` gate 2 · `:230` generated layout |
| `schemas/lab.schema.v3.json` | `:59` bare `see pedagogy.md` → explicit relative path |
| `meta_prompt/pedagogy.v1.md` | `:3` `schema/lab.schema.v3.json` |
| `docs/how_it_works.md` | `:80`, `:113`, `:287` |
| `docs/infographic.prompt.v1.md` | `:30`, `:33` |
| `policy/routing/readme.md` | design rules move into the prompt (phase 2); keep the file index |
| `plans/folder_refactoring/` | move `plan.v2.md` and `prompt.v2.md` into `deprecated/`; the active pair is v3, and `prompt.v3.md:5` names this file — held true thereafter by `FR-P0-PLANREF` |

Pre-existing defects fixed while these files are open — the `work/elegoo_labs/…` ghost
paths (F25) in `arduino_kit_curriculum.v4.yaml:20`, `l01_unpowered_power_path.json:6`,
and `l01_polarity_asserted.reject.json:6`.

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Phase 0 is a large commit | entirely path changes, gated by `FR-P0-*`; smaller commits mean rewriting the same lines repeatedly |
| The rule-1 rename loses history | §5's staging rule; `FR-P0-HISTORY` (b) requires four `R100` entries in the phase-0 commit, and §9 orders staging before editing |
| **The harness is new code and is its own oracle** | `FR-P0-HARNESS` runs first and tests the six harness behaviours no per-gate fixture can reach — phase selection, exit propagation, result integrity, wrong-reason detection, no-overwrite, scan isolation. Its failure invalidates the whole run. *(v2 claimed fixtures were the mitigation and that fixtureless gates were limited to tree/parse facts; `DEPS`, `HISTORY` and `CLEAN` are neither, which is why the claim class in harness rule 6 replaces that sentence.)* |
| A gate claims more than it proves | harness rule 6 — every gate declares a claim class, recorded in the result JSON; no gate in this plan may claim `execution` of a controller that does not exist |
| A detector flags its own fixture | harness rule 7 — production scans exclude `tests/fixtures/**` and `tests/selftest/**`; each detector is proven by a separate fixture-pointed invocation; self-test (f) proves the exclusion holds |
| Results dirty the worktree | `tests/results/*.json` ignored, folder kept by `.gitkeep`; `git status --porcelain` does not list ignored files |
| A moved schema breaks an accepted lab's audit trail | `FR-P1-SCHEMA-RETENTION`; supersession stays in place via the version suffix |
| Moving `legacy/` breaks `failures.v1.yaml` citations | edited in the same commit; `FR-P0-NOSTALE` greps for survivors |
| The executing agent reads a superseded plan | `FR-P0-PLANREF`; v2 and its prompt move to `deprecated/` in phase 0 |
| `redundancy.analysis.v1.md` line numbers are stale — it cites `readme.md:63`, now a one-line file | findings hold, line refs do not; re-verify at edit time |
| Later phases silently block earlier ones | harness rule 2 — `activation_phase`, with skips recorded explicitly and never counted as passes; proven by self-test (a) |

---

## 12. Out of scope

**Runtime enforcement of routing.** This plan makes the routing rules stated, owned and
checkable; it cannot make them enforced, because no controller exists (§3). The follow-up
needs an implementation, and its acceptance criteria are the two clauses removed from
`FR-P4-AGREEMENT` plus the two gates renamed in phase 2:

- every state in `policy/controller.v1.yaml` is reachable in an implemented state machine,
  and no implemented state is absent from the manifest;
- every entry in `policy/routes.v1.yaml` carries proof recorded from an actual execution;
- a call whose executed model differs from its decided model is *rejected at runtime*, not
  merely unrepresentable in the record format (`FR-P2-BYPASS-DECLARED` → `-ENFORCED`);
- a model call with no decision record *terminates* the run as `META_SYSTEM_FAILURE`
  (`FR-P2-UNRECORDED-DECLARED` → `-FATAL`).

Until then, no document, gate name or report may state that the selector is enforced.

**Also out of scope.** Curriculum content; the F86 finding that 14 of 35 labs declare
`adult_led_controller_station` while four prose documents forbid a controller; the 25
contradictions in `redundancy.analysis.v1.md` beyond the paths named in §10; rendering
`docs/how_it_works.png`; anything under `plans/` except the v2→`deprecated/` move and the
prompt retarget in §10.

F86 is a substantive contradiction about what the workbook *is* and needs its own
decision. It is recorded here only so this refactor is not mistaken for having addressed
it.
