# Folder refactoring — plan v1

**Date:** 2026-07-30
**Status:** accepted, not started. No file has been moved or edited under this plan.
**Scope:** folder layout, file placement, and the references that name them. Not curriculum content.

---

## 1. The rule

Every file lives where its reader is.

| Folder | Consumer | Form |
|---|---|---|
| `policy/` | **code** — the controller, preflight, the gate suite | `*.yaml` |
| `meta_prompt/` | **a model** — prose instructions | `*.md` |
| `schemas/` | **a validator** | `*.json` |
| `curricula/<name>/` | one curriculum's facts and evidence | mixed, by nature |
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
`official_kit_photo.jpg`, which has already moved to `curricula/arduino_kit/`.
What remains is six manifests of rules — including `calibration.v1.yaml`, whose own
header states it outranks every prose document in the project. `policy/` names what
they are: the rules that bind a run.

`policy/` is engine-wide. It is not the policy of one curriculum and not the policy of
the meta prompt; it binds every run of the generator regardless of curriculum.
`calibration.v1.yaml` is the one file with a learner-specific part, which is why its
kit-specific power block splits out in phase 3.

---

## 3. State at the time of writing

Two renames are already mid-flight and neither is finished. This is the reason
phase 0 is a single atomic commit.

- `schema/` → `schemas/` happened on disk outside version control: `git status` shows
  four deletions under `schema/` plus an untracked `schemas/`. **22 live references
  still say `schema/`** — `assets/calibration.v1.yaml` (8), the meta prompt (6),
  `assets/checks.v1.yaml` (3), `AGENTS.md` (2), `docs/how_it_works.md` (2),
  `pedagogy.md` (1).
- Four kit files were moved into `curricula/arduino_kit/` earlier
  (`arduino_kit_curriculum.v4.yaml`, `kit_evidence.md`, `official_kit_photo.jpg`,
  `lab_brief.md`) and no reference was updated. `AGENTS.md:16`'s validation command
  opens `assets/curriculum.v4.yaml`, which no longer exists, so the command fails
  today.
- `meta_prompt/deprecated/` exists on disk, is empty, and is therefore absent from the
  baseline commit — a convention that disappears on clone.
- `.pytest_cache/v/cache/nodeids` is `[]`. No automated test has ever been collected;
  every gate in this plan is a manual or scripted check until phase 4.

---

## 4. Target tree

```
curriculum_builder/
├── AGENTS.md                                   conventions + the retention rule
├── readme.md
│
├── policy/                                     DATA CODE READS            ← was assets/
│   ├── calibration.v1.yaml                     premise: learner, caps, supplies, safety floor
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
│   ├── execution_log.schema.v1.json
│   ├── routing_decision.schema.v1.json         ← meta_prompt/routing/
│   └── deprecated/.gitkeep                     gated — see §6
│
├── meta_prompt/                                PROSE A MODEL READS
│   ├── meta_curriculum_builder.prompt.v5.md    + new § Routing (phase 2)
│   ├── component_lab_template.v1.md            companion: how to write a lab
│   ├── pedagogy.v1.md                          companion: why the pedagogy fields exist ← root
│   ├── model_selector_prompt.v1.md             ← meta_prompt/routing/
│   └── deprecated/.gitkeep
│
├── docs/                                       ORIENTATION ONLY, never constraints
│   ├── how_it_works.md
│   ├── how_it_works.typ
│   ├── how_it_works.png
│   └── infographic.prompt.v1.md
│
└── plans/
    ├── folder_refactoring/
    │   └── folder_refactoring.plan.v1.md       this file
    ├── fix_curriculum_meta_prompt/
    │   ├── research/redundancy.analysis.v1.md
    │   └── prompts/
    │       ├── remediation.plan.promptv7.md
    │       └── deprecated/remediation.plan.v1.md … v6.md
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
| `assets/*` (6 yaml) | `policy/` | rules, not assets |
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
  `failures.v1.yaml` requires a path and line from it for every A-series defect, so
  its citations are updated in phase 0 and never broken again.
- **`name.vN.ext`** — in-place coexistence while both versions are live.

Every empty `deprecated/` gets a `.gitkeep`, or it will not survive a clone.

`schemas/deprecated/` is **gated**: a schema may enter it only when zero accepted
artifacts and zero manifests reference it. Schema paths appear in
`calibration.enforced_by`, in `checks.v1.yaml`, and in the audit records of accepted
labs; `--resume` refuses to mutate accepted work, so the contract a lab was accepted
under must keep resolving at a stable path. The version suffix handles supersession
in place. The folder therefore starts empty and stays empty until a retirement is
provably safe.

`docs/` has no `deprecated/`: its explainers are regenerated from `.typ`, and an
archive of stale claims is a drift risk rather than a record.

---

## 7. Reference-fix ledger

Every path below is rewritten in phase 0, in the same commit as the moves.

| File | What to fix |
|---|---|
| `AGENTS.md` | `:5` asset/fixture locations · `:7` the `pedagogy.md` sentence · `:16` the validation command (both paths are dead today) · `:29` note the retention rule |
| `policy/calibration.v1.yaml` | 8 `schema/` refs incl. the whole `enforced_by` block · `:9` names four prose docs that have moved · `:38` `assets/official_kit_photo.jpg` |
| `policy/checks.v1.yaml` | `:3` schema path · `:63`, `:65` the fixture path |
| `policy/failures.v1.yaml` | the `assets/legacy/` citation requirement → `plans/legacy_v3/` · `:52` `work/elegoo_labs/…` provenance |
| `meta_prompt/meta_curriculum_builder.prompt.v5.md` | `:54–68` the entire input table · `:63` the bare `routing/` row · `:78–88` the precedence list · `:157` gate 2 · `:230` the generated layout |
| `schemas/lab.schema.v3.json` | `:59` bare `see pedagogy.md` → explicit relative path |
| `meta_prompt/pedagogy.v1.md` | `:3` `schema/lab.schema.v3.json` |
| `docs/how_it_works.md` | `:80`, `:113`, `:287` |
| `docs/infographic.prompt.v1.md` | `:30`, `:33` |
| `meta_prompt/routing/readme.md` → `policy/routing/readme.md` | design rules move out (see phase 2); keep the file index |

Pre-existing defects fixed while these files are open — the `work/elegoo_labs/…`
ghost paths (F25) in `arduino_kit_curriculum.v4.yaml:20`,
`l01_unpowered_power_path.json:6`, and `l01_polarity_asserted.reject.json:6`.

---

## 8. Phases

One commit per phase. A phase does not start until the previous phase's gate passes.

### Phase 0 — the atomic move

Every move in §5 plus every fix in §7, in one commit. Splitting them would rewrite the
same reference lines two or three times, which is how the `work/elegoo_labs/…` ghost
paths survived five previous attempts.

**Gate**
1. `git status` clean.
2. `grep -rn "assets/\|schema/\|work/elegoo_labs" --exclude-dir=.git --exclude-dir=plans .` returns nothing.
3. The updated `AGENTS.md` validation command runs green against
   `schemas/curriculum.schema.v4.json` + `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml`
   and `schemas/calibration.schema.v1.json` + `policy/calibration.v1.yaml`.
   Confirm `python3 -c "import jsonschema, yaml"` first; if either is missing, record
   that as the blocking fact rather than declaring the gate passed.
4. Every moved file appears in `git log --follow`.

### Phase 1 — the retention convention

Create the four `deprecated/` folders with `.gitkeep`. Write §6 into `AGENTS.md`,
stating for each folder whether it has one and why, including the `schemas/` gate and
the `docs/` exclusion.

**Gate** — `AGENTS.md` answers the question for every top-level folder; all four
`.gitkeep` files are tracked.

### Phase 2 — routing becomes part of the contract

`routing/` is currently orphaned: the meta prompt names it twice (`:63` a bare table
row, `:230` a directory name) and states no routing rule. Meanwhile gate 2 at `:157`
advertises "selector enforcement", and of 39 check ids none covers model selection —
the only near-match, `ROUTE-PROVEN` at `checks.v1.yaml:193`, is external-capability
preflight. An advertised gate item with no executed assertion is gate **B3** and
`DRIFT-NO-MISREPORTING`. The failed v3 prompt was more explicit than v5 here
(`component_lab_orchestrator_prompt.v3.md:122`).

Add a `§ Routing` section to the meta prompt that **binds, never inlines** — values
stay in `policy/routing/*.yaml`, so no fact is duplicated into prose. It carries:

- the five `policy/routing/` files and `schemas/routing_decision.schema.v1.json` as
  authorized inputs, replacing the bare row at `:63`
- the invariants no data file can express: the selector runs first and code applies the
  result; `--model` is a fallback and may not bypass the selector (promoted from
  `controller.v1.yaml:148`); no model at all for merge, validation, hashing,
  rendering, aggregation, audits or the logger; cheapest eligible route for bounded
  drafting, stronger route for electronics design and QA, maximum reasoning only for
  failed safety escalation; no redundant drafts, serial by default; no model approves
  its own unsupported technical claim (promoted from `routing/readme.md`)
- the obligation: every model call emits a decision record validating against the
  schema, and the route actually executed — role, model, effort, sandbox policy,
  elapsed — is recorded in the execution log
- one sentence separating `policy/routes.v1.yaml` (proven external capabilities) from
  `policy/routing/` (which model serves which task), because "route" currently means
  both

New `selector:` group in `checks.v1.yaml` — `SEL-*`, deliberately not `ROUTE-*`:

| id | asserts |
|---|---|
| `SEL-DECISION-VALID` | every model call has a decision record validating against the schema |
| `SEL-NO-MODEL-BYPASS` | `--model` cannot produce a call whose model differs from the selector's output |
| `SEL-NO-MODEL-FOR-DETERMINISTIC` | zero model calls attributed to merge/validate/hash/render/aggregate/audit/log |
| `SEL-ESCALATION-BOUNDED` | the maximum-reasoning route appears only against a failed safety check |
| `SEL-EXECUTED-MATCHES-DECIDED` | the recorded executed route equals the decided route |

A model call with no valid decision record is a `META_SYSTEM_FAILURE`, matching the
existing rule for an append that cannot be proven. Without that, `SEL-DECISION-VALID`
binds only in tests and not at runtime.

**Gate** — no gate item in the meta prompt lacks a check id; no routing *value*
appears in prose; `policy/routing/readme.md` contains no rule the prompt does not own.

### Phase 3 — schema/data hygiene

1. Split `policy/calibration.v1.yaml`: learner caps and the safety floor stay; the
   `power` block (permitted inputs, rails, 3–5 V range) becomes
   `curricula/arduino_kit/kit_calibration.v1.yaml`, so no curriculum can inherit
   another kit's supplies. Update `enforced_by` and `CAL-SOURCE-VERIFIED`.
2. Remove the data facts embedded in contracts: the `"nine-year-old"` literals at
   `schemas/lab.schema.v3.json:54,675` become references to the owned value (F03).
3. Reduce `meta_prompt/pedagogy.v1.md` to rationale only. It currently copies six
   owned values — `:27` age, `:55` misconceptions, `:85–86` terms, `:87` segments,
   `:99,105` Bloom floor, `:100–101` criterion voice (F03, F05–F07, F09, F10) — each
   replaced by a pointer to `calibration.v1.yaml`.

**Gate** — `CAL-SCHEMA-AGREE` still holds; no file in `schemas/` names a kit, a
learner age, or a lab; no pedagogy cap value appears outside `calibration.v1.yaml`.

### Phase 4 — schemas for the policy manifests

Five of six policy YAMLs have no schema. The implicit rationale was that schemas guard
what *models* produce; that fails here, because these are the files where a typo is
invisible and consequential — a mistyped id in `checks.v1.yaml` silently disables a
check while still appearing advertised (gate B3), and `limits.v1.yaml` says in its own
header that a limit without a number can never be exceeded.

A schema proves shape, not agreement with the code. Each file therefore needs both,
following the one pattern that already works (`calibration` + `CAL-SCHEMA-AGREE`).

| File | Agreement check | Priority |
|---|---|---|
| `checks.v1.yaml` | ids ↔ executed assertions (this *is* B3) | high |
| `limits.v1.yaml` | every limit has a number and a flag | high |
| `controller.v1.yaml` | manifest states ↔ implemented states | medium |
| `routes.v1.yaml` | every route carries recorded proof | medium |
| `failures.v1.yaml` | every id ↔ a correction and a proving test | medium |
| `routing/*.yaml` (4) | selector output ↔ declared policy | with phase 2 |
| `l01_unpowered_power_path.json` | circuit-data schema, so the reject fixture can actually be rejected | medium |

**Gate** — every YAML read by code validates against a schema in `schemas/`; every
schema has at least one agreement check; the reject fixture is rejected by an executed
assertion rather than by assertion in prose.

---

## 9. Risks

| Risk | Mitigation |
|---|---|
| Phase 0 is a large commit | it is entirely path changes with a mechanical gate; smaller commits mean rewriting the same lines repeatedly |
| A moved schema breaks an accepted lab's audit trail | §6 gate on `schemas/deprecated/`; supersession stays in place via the version suffix |
| Moving `legacy/` breaks `failures.v1.yaml` citations | that file is edited in the same commit; gate 2 of phase 0 greps for survivors |
| `redundancy.analysis.v1.md` line numbers are stale — it cites `readme.md:63`, now a one-line file | its findings hold, its line refs do not; re-verify each ref against the file at the moment of editing |
| No test suite exists to catch a bad move | phase 0's gate is grep plus the validation command, run and recorded, not assumed |

---

## 10. Out of scope

Curriculum content; the F86 finding that 14 of 35 labs declare
`adult_led_controller_station` while four prose documents forbid a controller; the 25
contradictions in `redundancy.analysis.v1.md` beyond the paths named in §7; rendering
`docs/how_it_works.png`; anything under `plans/`.

F86 is a substantive contradiction about what the workbook *is* and needs its own
decision. It is recorded here only so that this refactor is not mistaken for having
addressed it.
