# Folder refactoring — plan v2

**Date:** 2026-07-30
**Supersedes:** `deprecated/folder_refactoring.plan.v1.md`
**Status:** accepted, not started. No file has been moved or edited under this plan.
**Scope:** folder layout, file placement, the references that name them, and a committed
harness that proves each phase. Not curriculum content.

**What v2 adds over v1.** Every gate now has a stable ID, an activation phase, an exact
command, pass criteria, a rejection fixture where one applies, and a stated failure
meaning. Gates are cumulative: phase *N* runs its own gates plus every earlier gate.
A gate belonging to a later phase must never block an earlier one.

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

Root holds only what a human or tool expects at top level: `AGENTS.md`, `readme.md`.

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

- `schema/` → `schemas/` happened on disk outside version control: `git status` shows
  four deletions under `schema/` plus an untracked `schemas/`. **22 live references
  still say `schema/`** — `assets/calibration.v1.yaml` (8), the meta prompt (6),
  `assets/checks.v1.yaml` (3), `AGENTS.md` (2), `docs/how_it_works.md` (2),
  `pedagogy.md` (1).
- Four kit files moved into `curricula/arduino_kit/` earlier
  (`arduino_kit_curriculum.v4.yaml`, `kit_evidence.md`, `official_kit_photo.jpg`,
  `lab_brief.md`) and no reference was updated. `AGENTS.md:16`'s validation command
  opens `assets/curriculum.v4.yaml`, which no longer exists, so it fails today.
- `meta_prompt/deprecated/` exists on disk, is empty, and is therefore absent from the
  baseline commit — a convention that disappears on clone.
- `.pytest_cache/v/cache/nodeids` is `[]`. No automated test has ever been collected.
  The harness in §7 is the first executable check in this repository.

---

## 4. Target tree

```
curriculum_builder/
├── AGENTS.md                                   conventions + the retention rule
├── readme.md
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
│   ├── fixtures/
│   └── results/
│
├── docs/                                       ORIENTATION ONLY, never constraints
│   ├── how_it_works.md · how_it_works.typ · how_it_works.png
│   └── infographic.prompt.v1.md
│
└── plans/
    ├── folder_refactoring/
    │   ├── folder_refactoring.plan.v2.md       this file
    │   ├── folder_refactoring.prompt.v1.md     the execution prompt
    │   └── deprecated/folder_refactoring.plan.v1.md
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

| From | To | Reason |
|---|---|---|
| `schema/*.json` (4) | `schemas/` | already on disk; commit it |
| `assets/*.yaml` (6) | `policy/` | rules, not assets |
| `assets/legacy/` (3) | `plans/legacy_v3/` | history cited as evidence; `plans/` owns history |
| `assets/roster.md` | `curricula/arduino_kit/` | ELEGOO-specific |
| `assets/teacher_framework.md` | `curricula/arduino_kit/` | ELEGOO-specific |
| `assets/teacher_audit.md` | `curricula/arduino_kit/` | ELEGOO-specific |
| `assets/l01_unpowered_power_path.json` | `curricula/arduino_kit/` | L01 circuit data |
| `assets/fixtures/l01_polarity_asserted.reject.json` | `curricula/arduino_kit/fixtures/` | kit-specific fixture |
| `pedagogy.md` | `meta_prompt/pedagogy.v1.md` | constraint-bearing prose; versioned per `AGENTS.md:29` |
| `meta_prompt/routing/*.yaml` (4) | `policy/routing/` | data code reads |
| `meta_prompt/routing/readme.md` | `policy/routing/` | index of those files |
| `meta_prompt/routing/model_selector_prompt.v1.md` | `meta_prompt/` | prose a model reads |
| `meta_prompt/routing/routing_decision.schema.v1.json` | `schemas/` | all contracts in one folder |

Nothing is deleted. Use `git mv` so history follows.

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
│   ├── common.py                 path constants, fixture runner, result recorder
│   ├── fr_p0_structure.py        FR-P0-*
│   ├── fr_p1_retention.py        FR-P1-*
│   ├── fr_p2_selector.py         FR-P2-*
│   ├── fr_p3_calibration.py      FR-P3-*
│   └── fr_p4_policy_schemas.py   FR-P4-*
├── fixtures/                     negative fixtures, named <subject>.reject.<ext>
│                                 per the existing convention
└── results/                      gate_results.p<phase>.<utc-timestamp>.json
```

**Harness contract — five rules, none optional.**

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
   `tests/results/` containing, per gate: id, activation phase, command, exit code,
   stdout digest, pass/fail/skip, and each fixture's outcome with the matched error.
   Files are never overwritten. Per `AGENTS.md:25`, an unexecuted check is never
   reported as passing.
5. **`APPROVED` requires all four:** every gate through the current phase passes; every
   negative fixture failed for its intended reason; results are written; the worktree is
   clean. Any missing element returns `BLOCKED` with the specific cause.

---

## 8. Gate catalogue

Format: **ID** · activation phase · command · pass criteria · rejection fixture ·
failure meaning.

### Phase 0 — structure and existing validation

**`FR-P0-DEPS`** · 0
`python3 -c "import jsonschema, yaml; print('DEPS OK')"`
**Pass:** prints `DEPS OK`.
**Fixture:** none — environment precondition.
**Failure means:** the environment, not the repo. Record as a blocking external fact and
return `BLOCKED`; never skip the schema gates and call the phase passed.

**`FR-P0-TREE`** · 0
`python3 tests/gates/fr_p0_structure.py --check tree`
**Pass:** all 13 destination paths in §5 exist; none of `assets/`, `schema/`,
`meta_prompt/routing/`, or root `pedagogy.md` exists. Prints
`FR-P0-TREE PASS (13 destinations, 0 legacy paths)`.
**Fixture:** none — the tree is its own oracle.
**Failure means:** a move was missed or half-applied; the tree is in the same broken
intermediate state §3 describes.

**`FR-P0-NOSTALE`** · 0
`python3 tests/gates/fr_p0_structure.py --check stale`
**Pass:** zero hits for `assets/`, `schema/` (excluding `schemas/`),
`meta_prompt/routing/`, `work/elegoo_labs`, and root-relative `pedagogy.md`, searching
all tracked files except `plans/**` and `.git/**`. Prints `FR-P0-NOSTALE PASS (0 hits)`.
**Fixture:** `tests/fixtures/stale_reference.reject.md` — contains the literal
`assets/calibration.v1.yaml`; the detector must flag it, `expected_error:
stale-path:assets/`.
**Failure means:** reference debt survived the move; some consumer will resolve a dead
path. This is the exact failure that produced the `work/elegoo_labs/…` ghosts.

**`FR-P0-PARSE`** · 0
`python3 tests/gates/fr_p0_structure.py --check parse`
**Pass:** every `*.yaml` under `policy/` and `curricula/` and every `*.json` under
`schemas/` and `curricula/` parses. Prints the file count parsed.
**Fixture:** `tests/fixtures/malformed_manifest.reject.yaml`, `expected_error:
yaml.scanner.ScannerError`.
**Failure means:** a move or edit corrupted a file.

**`FR-P0-SCHEMA`** · 0
`python3 tests/gates/fr_p0_structure.py --check schema`
**Pass:** `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` validates against
`schemas/curriculum.schema.v4.json`, and `policy/calibration.v1.yaml` against
`schemas/calibration.schema.v1.json`. This is `AGENTS.md:16`'s command at the new paths.
**Fixture:** `tests/fixtures/curriculum_missing_labs.reject.yaml`, `expected_error:
ValidationError:'labs' is a required property`.
**Failure means:** the move broke a manifest, or `AGENTS.md` still documents paths that
do not validate.

**`FR-P0-HISTORY`** · 0
`python3 tests/gates/fr_p0_structure.py --check history`
**Pass:** `git log --follow` returns pre-move commits for every file in §5.
**Fixture:** none.
**Failure means:** a file was copied and deleted rather than `git mv`'d; provenance lost.

**`FR-P0-CLEAN`** · 0
`git status --porcelain` → empty
**Pass:** no output.
**Failure means:** the phase is not committed, or untracked artifacts leaked in. Blocks
`APPROVED` per harness rule 5.

### Phase 1 — retention

**`FR-P1-GITKEEP`** · 1
`python3 tests/gates/fr_p1_retention.py --check gitkeep`
**Pass:** `policy/deprecated/`, `curricula/deprecated/`, `schemas/deprecated/`,
`meta_prompt/deprecated/` each contain a `.gitkeep` **and** `git ls-files` lists it.
**Fixture:** `tests/fixtures/untracked_deprecated.reject/` — a `deprecated/` directory
with no `.gitkeep`; `expected_error: untracked-convention`.
**Failure means:** the convention vanishes on clone — the precise defect
`meta_prompt/deprecated/` exhibits today.

**`FR-P1-DOC`** · 1
`python3 tests/gates/fr_p1_retention.py --check agents-doc`
**Pass:** `AGENTS.md` contains a retention table naming every top-level folder with an
explicit yes/no and a reason.
**Fixture:** `tests/fixtures/agents_missing_folder.reject.md` — a table omitting `docs/`;
`expected_error: retention-unanswered:docs`.
**Failure means:** a folder's retention answer is left to inference, which is how three
conventions (`deprecated/`, `legacy/`, `vN`) accumulated.

**`FR-P1-SCHEMA-RETENTION`** · 1
`python3 tests/gates/fr_p1_retention.py --check schema-gate`
**Pass:** for every file in `schemas/deprecated/`, a repository-wide search for its
basename returns zero hits outside that folder. Vacuously true while empty — and
recorded as `PASS (0 files, gate armed)`, not skipped.
**Fixture:** `tests/fixtures/retired_but_referenced.reject.json` plus a manifest citing
it; `expected_error: retired-schema-still-referenced`.
**Failure means:** a schema was retired while an accepted artifact still depends on it,
breaking the audit trail `--resume` relies on.

### Phase 2 — routing and selector

**`FR-P2-BOUND`** · 2
`python3 tests/gates/fr_p2_selector.py --check bound`
**Pass:** all five `policy/routing/` files and `schemas/routing_decision.schema.v1.json`
are named in the meta prompt's authorized-input table.
**Fixture:** `tests/fixtures/prompt_missing_routing_input.reject.md`, `expected_error:
unbound-input:model_registry.v1.yaml`.
**Failure means:** the routing package is orphaned again — the state at `:63` today,
where one bare table row stands in for six files.

**`FR-P2-NOVALUES`** · 2
`python3 tests/gates/fr_p2_selector.py --check no-values`
**Pass:** no model id, effort level, or candidate-pool value from `policy/routing/*.yaml`
appears literally in the meta prompt.
**Fixture:** `tests/fixtures/prompt_inlines_model_id.reject.md`, `expected_error:
duplicated-value`.
**Failure means:** a routing fact now has two owners — the F-series defect this refactor
exists to stop. The prompt binds; the data obeys.

**`FR-P2-SEL-ADVERTISED`** · 2
`python3 tests/gates/fr_p2_selector.py --check advertised`
**Pass:** the five `SEL-*` ids appear in `policy/checks.v1.yaml` **and** each is executed
by an assertion in this harness — both directions.
**Fixture:** `tests/fixtures/check_id_without_assertion.reject.yaml`, `expected_error:
advertised-not-executed`.
**Failure means:** gate **B3** and `DRIFT-NO-MISREPORTING` — a check named but never run.
This is exactly what `:157`'s "selector enforcement" claims today, backed by none of the
39 existing check ids.

**`FR-P2-DECISION-VALID`** · 2
`python3 tests/gates/fr_p2_selector.py --check decision`
**Pass:** a well-formed decision record validates against
`schemas/routing_decision.schema.v1.json`; all nine required fields present.
**Fixtures:** `decision_missing_effort.reject.json` (`expected_error:
'reasoning_effort' is a required property`); `decision_model_not_in_registry.reject.json`
(`expected_error: model-not-in-registry`).
**Failure means:** decisions can be recorded that no one can check — an audit trail that
cannot be audited.

**`FR-P2-NO-BYPASS`** · 2
`python3 tests/gates/fr_p2_selector.py --check bypass`
**Pass:** a call whose executed model differs from its decided model is rejected.
**Fixture:** `tests/fixtures/model_override_bypass.reject.json`, `expected_error:
executed-differs-from-decided`.
**Failure means:** `--model` can bypass the selector, contradicting
`controller.v1.yaml:148`.

**`FR-P2-UNRECORDED-FATAL`** · 2
`python3 tests/gates/fr_p2_selector.py --check unrecorded`
**Pass:** a simulated model call with no decision record terminates as
`META_SYSTEM_FAILURE`.
**Fixture:** `tests/fixtures/call_without_decision.reject.json`, `expected_error:
META_SYSTEM_FAILURE`.
**Failure means:** the routing obligation binds only in tests, not at runtime — the
decision recorded as (c).

**`FR-P2-GATEITEMS`** · 2
`python3 tests/gates/fr_p2_selector.py --check gate-items`
**Pass:** every gate item advertised in the meta prompt's release table maps to a check
id in `policy/checks.v1.yaml`.
**Fixture:** `tests/fixtures/gate_item_without_check.reject.md`, `expected_error:
gate-item-unbacked`.
**Failure means:** the build advertises coverage it does not have.

### Phase 3 — calibration boundaries

**`FR-P3-SPLIT`** · 3
`python3 tests/gates/fr_p3_calibration.py --check split`
**Pass:** `policy/calibration.v1.yaml` contains no `power` block and no kit term;
`curricula/arduino_kit/kit_calibration.v1.yaml` contains the permitted inputs, rails and
3–5 V range; both validate against their schemas.
**Fixture:** `tests/fixtures/global_calibration_with_kit_power.reject.yaml`,
`expected_error: kit-fact-in-global-calibration`.
**Failure means:** a second curriculum would silently inherit ELEGOO's supplies.

**`FR-P3-NO-LITERALS`** · 3
`python3 tests/gates/fr_p3_calibration.py --check literals`
**Pass:** no file in `schemas/` contains a learner-age literal or a kit name.
**Fixture:** `tests/fixtures/schema_with_learner_literal.reject.json`, `expected_error:
data-fact-in-contract`.
**Failure means:** F03 persists — `lab.schema.v3.json:54,675` hard-code
`"nine-year-old"`, so the contract cannot serve a different learner.

**`FR-P3-CAPS-OWNED`** · 3
`python3 tests/gates/fr_p3_calibration.py --check caps`
**Pass:** each pedagogy cap value appears in `policy/calibration.v1.yaml` and in the
schema constraint named by `enforced_by`, and nowhere in prose. Covers the six copies in
`pedagogy.v1.md` at `:27`, `:55`, `:85–86`, `:87`, `:99,105`, `:100–101`.
**Fixture:** `tests/fixtures/prose_with_cap_value.reject.md`, `expected_error:
unowned-cap-copy`.
**Failure means:** F05–F07, F09, F10 persist — prose copies that drift silently because
nothing keeps them equal.

**`FR-P3-CAL-AGREE`** · 3
`python3 tests/gates/fr_p3_calibration.py --check cal-agree`
**Pass:** `CAL-SCHEMA-AGREE` holds after the split — every value in `pedagogy_caps`
equals the schema constraint named in `enforced_by`.
**Fixture:** `tests/fixtures/cap_schema_mismatch.reject.yaml`, `expected_error:
cap-schema-disagreement`.
**Failure means:** the split broke the one derivation this repo already enforces
correctly.

**`FR-P3-KIT-SOURCE`** · 3
`python3 tests/gates/fr_p3_calibration.py --check kit-source`
**Pass:** `CAL-SOURCE-VERIFIED` resolves against `kit_calibration.v1.yaml`; every powered
lab cites exactly one input id present there, whose verification is `verified_official`.
**Fixture:** `tests/fixtures/lab_cites_unverified_input.reject.yaml`, `expected_error:
unverified-source-cited`.
**Failure means:** a lab can cite a supply nobody photographed — the safety premise the
whole calibration file exists to hold.

### Phase 4 — policy schemas and agreement

**`FR-P4-ALL-VALIDATE`** · 4
`python3 tests/gates/fr_p4_policy_schemas.py --check validate`
**Pass:** all six `policy/*.yaml` and all four `policy/routing/*.yaml` validate against a
schema in `schemas/`.
**Fixture:** `tests/fixtures/policy_manifest_unschemaed.reject.yaml`, `expected_error:
no-schema-for-manifest`.
**Failure means:** a file code depends on can be malformed without anything noticing.

**`FR-P4-AGREEMENT`** · 4
`python3 tests/gates/fr_p4_policy_schemas.py --check agreement`
**Pass:** each policy schema has at least one executed agreement check —
`checks.v1.yaml` ids ↔ executed assertions; every `limits` entry has a number and a flag;
`controller` states ↔ implemented states; every `routes` entry carries recorded proof;
every `failures` id ↔ a correction and a proving test.
**Fixture:** `tests/fixtures/limit_without_number.reject.yaml`, `expected_error:
limit-missing-value`.
**Failure means:** shape is proven but agreement is not — a manifest can describe a
machine that does not exist. `limits.v1.yaml`'s own header states the consequence: a
limit without a number can never be exceeded, so its drift rule never fires.

**`FR-P4-FIXTURE-BITES`** · 4
`python3 tests/gates/fr_p4_policy_schemas.py --check fixture-bites`
**Pass:** `curricula/arduino_kit/fixtures/l01_polarity_asserted.reject.json` is rejected
by `schemas/circuit_data.schema.v1.json` with the polarity-assertion violation.
**Fixture:** the file itself; `expected_error: polarity-asserted-on-unpowered-path`.
**Failure means:** the reject fixture is inert — declared in `checks.v1.yaml:63,65` but
rejected by nothing, which is `L01-POLARITY-NEUTRAL` in name only.

**`FR-P4-COVERAGE`** · 4
`python3 tests/gates/fr_p4_policy_schemas.py --check coverage`
**Pass:** every id in `policy/checks.v1.yaml` is executed by the suite, and every id the
suite reports appears in `policy/checks.v1.yaml` — both directions, no orphans.
**Fixture:** `tests/fixtures/orphan_executed_id.reject.json`, `expected_error:
executed-not-advertised`.
**Failure means:** gate **B3** in its original form — the defect that failed the previous
build, where six ids were advertised and two asserted.

### Final regression

**`FR-ALL`** · after phase 4
`./tests/run_gates.sh 4`
**Pass:** every gate above executes and passes; every negative fixture fails for its
declared `expected_error`; a result file is written to `tests/results/`;
`git status --porcelain` is empty.
**Failure means:** return `BLOCKED` naming the failing gate id and its stated failure
meaning. `APPROVED` is legal only when all four conditions in harness rule 5 hold.

---

## 9. Phases

One commit per phase. A phase begins only after the previous phase's gates pass.
`run_gates.sh N` runs phase *N*'s gates **plus all earlier gates** — earlier gates are
regressions from the moment they activate.

| Phase | Work | Gates run | New gates |
|---|---|---|---|
| **0** | every move in §5 plus every fix in §10, one atomic commit; create `tests/` with `common.py`, `run_gates.sh` and the phase-0 gates | `run_gates.sh 0` | 7 |
| **1** | the four `deprecated/` folders, `.gitkeep`s, retention rule written into `AGENTS.md` | `run_gates.sh 1` | 3 |
| **2** | `§ Routing` in the meta prompt; the five `SEL-*` ids in `checks.v1.yaml`; unrecorded call ⇒ `META_SYSTEM_FAILURE` | `run_gates.sh 2` | 7 |
| **3** | calibration split; strip data literals from `schemas/`; reduce `pedagogy.v1.md` to rationale | `run_gates.sh 3` | 5 |
| **4** | six policy schemas + `circuit_data.schema.v1.json`; agreement checks | `run_gates.sh 4` | 4 |
| **final** | no new work — full regression | `FR-ALL` | — |

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

---

## 10. Reference-fix ledger

Rewritten in phase 0, in the same commit as the moves. Line numbers verified 2026-07-30;
re-verify each against the file at the moment of editing.

| File | What to fix |
|---|---|
| `AGENTS.md` | `:5` asset/fixture locations · `:7` the `pedagogy.md` sentence · `:16` the validation command (both paths dead today) · `:29` note the retention rule · add `tests/` to the structure section |
| `policy/calibration.v1.yaml` | 8 `schema/` refs incl. the whole `enforced_by` block · `:9` names four prose docs that have moved · `:38` `assets/official_kit_photo.jpg` |
| `policy/checks.v1.yaml` | `:3` schema path · `:63`, `:65` the fixture path |
| `policy/failures.v1.yaml` | the `assets/legacy/` citation requirement → `plans/legacy_v3/` · `:52` `work/elegoo_labs/…` provenance |
| `meta_prompt/meta_curriculum_builder.prompt.v5.md` | `:54–68` the input table · `:63` the bare `routing/` row · `:78–88` precedence · `:157` gate 2 · `:230` generated layout |
| `schemas/lab.schema.v3.json` | `:59` bare `see pedagogy.md` → explicit relative path |
| `meta_prompt/pedagogy.v1.md` | `:3` `schema/lab.schema.v3.json` |
| `docs/how_it_works.md` | `:80`, `:113`, `:287` |
| `docs/infographic.prompt.v1.md` | `:30`, `:33` |
| `policy/routing/readme.md` | design rules move into the prompt (phase 2); keep the file index |
| `plans/folder_refactoring/folder_refactoring.prompt.v1.md` | `:5` points at `folder_refactoring.plan.v1.md`, now in `deprecated/` — retarget to this file |

Pre-existing defects fixed while these files are open — the `work/elegoo_labs/…` ghost
paths (F25) in `arduino_kit_curriculum.v4.yaml:20`, `l01_unpowered_power_path.json:6`,
and `l01_polarity_asserted.reject.json:6`.

---

## 11. Risks

| Risk | Mitigation |
|---|---|
| Phase 0 is a large commit | entirely path changes, gated by `FR-P0-*`; smaller commits mean rewriting the same lines repeatedly |
| The harness is new code with no test of its own | harness rule 3 — every gate must be demonstrated by a negative fixture that fails for its stated reason; a gate with no fixture is limited to tree/parse facts that are self-evidencing |
| A moved schema breaks an accepted lab's audit trail | `FR-P1-SCHEMA-RETENTION`; supersession stays in place via the version suffix |
| Moving `legacy/` breaks `failures.v1.yaml` citations | edited in the same commit; `FR-P0-NOSTALE` greps for survivors |
| `redundancy.analysis.v1.md` line numbers are stale — it cites `readme.md:63`, now a one-line file | findings hold, line refs do not; re-verify at edit time |
| Later phases silently block earlier ones | harness rule 2 — `activation_phase`, with skips recorded explicitly and never counted as passes |

---

## 12. Out of scope

Curriculum content; the F86 finding that 14 of 35 labs declare
`adult_led_controller_station` while four prose documents forbid a controller; the 25
contradictions in `redundancy.analysis.v1.md` beyond the paths named in §10; rendering
`docs/how_it_works.png`; anything under `plans/` except the prompt retarget in §10.

F86 is a substantive contradiction about what the workbook *is* and needs its own
decision. It is recorded here only so this refactor is not mistaken for having addressed
it.
