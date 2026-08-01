# Phase 0 result — what `FR-P5-ENGINE-GENERIC` measured

**Date:** 2026-08-01
**Plan:** `simplification.plan.v3.md` §6 phase 0, catalogued at §9
**Gate:** `FR-P5-ENGINE-GENERIC`, `./tests/run_gates.sh 5`
**Verdict on the repository: FAIL.**

This is the inventory §6 phase 0 asks for. It is the first time this project has
measured how much domain is welded into its engine rather than asserting it.

**The FAIL is the deliverable.** The gate was written to be run against an engine that
has not been cleaned; cleaning it is §6 phases 1–5. A green result obtained by editing
`policy/`, `schemas/` or `meta_prompt/` content ahead of those phases would delete the
measurement, not the leak.

---

## What ran

| | |
|---|---|
| Curricula found | 1 — `arduino_kit` |
| Domain terms declared | 7, all from `curricula/arduino_kit/kit_calibration.v1.yaml` `kit_terms` |
| Engine files scanned | 41 — `policy/**`, `schemas/**`, `meta_prompt/meta_curriculum_builder.prompt.v6.md`, `meta_prompt/assets/*.md`, every `deprecated/` excluded |
| Engine-owned check ids | 37 of the 47 in `policy/checks.v1.yaml` (the other 10 declare an `owner` under `curricula/`) |

Both fixtures behaved as declared: `engine_domain_leak.reject.yaml` was rejected for
**both** codes, `engine-check-id-domain-term + engine-names-curriculum-path`, and
`engine_generic.accept.yaml` was accepted.

---

## (a) Engine files naming a `curricula/<name>/` path — **3 files, 27 lines**

### `meta_prompt/assets/inputs.v1.md` — 11 lines

Lines 13, 14, 30, 31, 32, 68, 69, 82, 83, 84, 98.

The authorized-input table and the precedence list name one curriculum's files
directly — its calibration, its manifest, its photo and evidence, its fixtures folder,
and its four prose documents. **The input set is `arduino_kit`'s, not any
curriculum's.** This is `G2` exactly as §2 states it, and it is the largest single
binding: a second curriculum cannot be run by this contract without editing it.

### `policy/checks.v1.yaml` — 13 lines

Lines 43, 45, 57, 72, 78, 84, 90, 105, 112, 118, 120, 123, 131.

Ten `owner:` fields, one `artifact:`, one `fixture:` and one prose line inside an
`asserts:`. Every one of them points from the engine's check inventory into
`curricula/arduino_kit/`. This is `G3` in the form it actually takes: the leak is not
only that domain checks share the engine's id namespace, it is that the engine's
inventory holds the **paths** of one curriculum's files as the subjects of its checks.

### `policy/calibration.v1.yaml` — 3 lines

Lines 9, 10, 15.

Both hits are in the manifest's header comments: the precedence rule names
`lab_brief.md`, `teacher_framework.md`, `teacher_audit.md` and `roster.md` under
`curricula/arduino_kit/` as the documents this file outranks, and the "what is NOT
here" note names `curricula/arduino_kit/kit_calibration.v1.yaml` as where the supplies
went.

**This one is not in the `G1`–`G6` table.** It is a real leak — the engine-wide
premise manifest states its precedence over one named curriculum's documents rather
than over *the curriculum's* documents — and it is mild: prose in comments, stating a
rule that is correct in general and written in the particular. It is still a binding a
second curriculum would fall outside of.

## (b) Engine-owned check ids encoding a domain term — **0 of 37**

**Zero is a bound, not a clean bill, and it must not be read as one.**

The gate holds no domain word of its own, by design: a detector that hard-codes
`circuit` is the leak it exists to detect, and it would go stale the moment a
curriculum in an unrelated domain arrives. Its vocabulary is what a curriculum
*declares about itself* — the `*_terms` blocks, with anchored `prose_pattern`s, that
`FR-P3-SPLIT` and `FR-P3-NO-LITERALS` already match on.

Today the only such declaration is `kit_terms`, seven terms, and all seven are proper
nouns and part identifiers: the vendor, the kit id, the kit name, two supply ids, the
evidence photograph, and one component. **No engine check id encodes any of them, and
that is what the zero says.**

What the zero does **not** say is that the engine's check namespace is domain-free.
§2's `G3` names `LAB-CURRENT-MARGIN` and `LAB-VALUE-SOURCED` — both engine-owned, both
declared by `schemas/lab.schema.v3.json` — and the gate cannot see them, because no
curriculum declares `current` or `value` as a term of its domain. The detector is
correct and its vocabulary is incomplete.

**The consequence for the plan:** the curriculum layer must declare its domain
vocabulary, not only its proper nouns, before (b) can measure anything. §6 phase 2 is
where that belongs — the verifier declaration is already the place a curriculum says
what its domain *is*, and a `domain_terms` block beside it costs nothing and arms this
gate. Until then, (b) is armed and near-blind, and this note is the record of that.

---

## Is the `G1`–`G6` table complete?

**No — stated plainly, as §6 phase 0 requires.**

Two findings, in opposite directions.

**1. One leak the table does not name.** `policy/calibration.v1.yaml` binds the engine
to `curricula/arduino_kit/` in its precedence rule. `G1`–`G6` names
`schemas/lab.schema.v3.json`, `meta_prompt/assets/inputs.v1.md`,
`policy/checks.v1.yaml`, `meta_prompt/assets/component_lab_template.v1.md`,
`curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` with
`schemas/curriculum.schema.v4.json`, and `policy/routes.v1.yaml`. It does not name
`policy/calibration.v1.yaml`. The table needs a seventh row, or `G2` needs widening
from "the authorized-input table" to "every engine manifest that names one
curriculum's files".

**2. Most of the table is outside what this gate can decide.** The gate measures two
relations. `G1` (an engine unit contract with a required block named for one domain),
`G4` (a unit-prose companion written for one domain), `G5` (`kit_power_profile` and
`visual_system` as top-level curriculum-schema concepts) and `G6` (a route described
as a component-datasheet capability) are none of them a curriculum path or a
curriculum-declared term. **They are unmeasured, not absent.** Nothing here confirms
them and nothing here refutes them.

So the honest statement is: `G1`–`G6` is **not proven complete**, it is **proven
incomplete by one**, and four of its six rows remain a reading of the repository
rather than a measurement of it. Closing that gap needs the vocabulary declaration
above, plus criteria this gate does not carry — which is the sort of thing §6 phase 1's
unit contract makes checkable, and the reason §7 sequences phase 4 first among the
substantive work.

---

## What was not done here, deliberately

Nothing under `policy/`, `schemas/` or `meta_prompt/` was changed. The 27 lines above
are all still there. The engine is measured; the engine is not yet clean; cleaning it
was not this run's job.
