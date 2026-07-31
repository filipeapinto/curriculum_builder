<!-- section asset of meta_curriculum_builder.prompt.v6.md · read whole -->

## Inputs

Everything required is under `CREATOR`, and every path in the table below is
relative to it. Validate each **manifest** against its schema before reading a value
from it; the prose inputs have no schema and cannot have one — read them as prose.

| Input | Role |
|---|---|
| `policy/calibration.v1.yaml` | **the engine-wide premises** — learner age band, the pedagogy caps derived from it, safety floor. Never the supplies: those belong to one kit |
| `curricula/arduino_kit/kit_calibration.v1.yaml` | **that kit's premises** — permitted supplies, power envelope, the evidence each is verified against. Outranked by the engine-wide premises, and outranks the curriculum |
| `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` | the curriculum — which labs exist, in order, and **how many** |
| `policy/limits.v1.yaml` | every resource limit, with its numeric default and flag |
| `policy/routes.v1.yaml` | every external capability, with the exact proven invocation |
| `policy/checks.v1.yaml` | every stable check id and what it asserts |
| `policy/failures.v1.yaml` | A1–A10 and B1–B4, with diagnoses and required corrections |
| `policy/controller.v1.yaml` | states, transitions, ownership, CLI surface |
| `policy/deferred.v1.yaml` | RT-1…RT-6 — the obligations this contract states but nothing yet executes |
| `schemas/curriculum.schema.v4.json`, `schemas/lab.schema.v3.json`, `schemas/calibration.schema.v1.json`, `schemas/kit_calibration.schema.v1.json` | the shapes for the curriculum, a finished lab, and the two calibrations |
| `schemas/routing_decision.schema.v2.json` | the routing-decision record format — ten required fields, decided and executed |
| `schemas/execution_log.schema.v2.json` | the execution-log record format — typed `action_kind`, conditional `decision_id` |
| `meta_prompt/assets/component_lab_template.v1.md` | lab structure in prose — tone, child-language rules, safety baseline |
| `policy/routing/model_registry.v1.yaml` | model capabilities and availability |
| `policy/routing/task_taxonomy.v2.yaml` | task classes and their risk profiles |
| `policy/routing/routing_policy.v1.yaml` | candidate-pool and escalation policy |
| `policy/routing/quality_gates.v1.yaml` | observable acceptance gates, never model self-confidence |
| `plans/legacy_v3/` | the failed v3 generator and runner — cite by path and line |
| `curricula/arduino_kit/official_kit_photo.jpg`, `curricula/arduino_kit/kit_evidence.md` | the verified kit evidence L01 depends on |
| `curricula/arduino_kit/fixtures/` | fixtures the tests must **reject**, never inputs |
| `curricula/arduino_kit/lab_brief.md`, `curricula/arduino_kit/roster.md`, `curricula/arduino_kit/teacher_framework.md`, `curricula/arduino_kit/teacher_audit.md` | project scope and teaching context |
| `meta_prompt/assets/pedagogy.v1.md`, `docs/how_it_works.md` | why each pedagogy field exists; how the machine fits together |
| `meta_prompt/assets/model_selector_prompt.v1.md` | the selector's own prompt, read by the selector call and by nothing else |

### Retained contracts

These are **not** authorized inputs. Each is a superseded version kept so that work
already accepted under it still validates; a validator checking an old record may
read one, and nothing else may. A new run is never validated against a superseded
contract. Both are retirable under `RT-6` in `policy/deferred.v1.yaml`, once a
logger emits `v2`-valid records and a selector emits `v2`-valid decisions.

| Retained contract | Readable only to |
|---|---|
| `schemas/execution_log.schema.v1.json` | validate execution logs already accepted under v1 |
| `schemas/routing_decision.schema.v1.json` | validate routing decisions already accepted under v1 |

Three reads reach outside `CREATOR`, all declared and bounded: `~/.codex/config.toml`
determines the sandbox policy in `policy/routes.v1.yaml`; `RESEARCH` fetches
manufacturer datasheets over the network; and `OUTPUT_ROOT` is read to evaluate the
startup precondition and, on `--resume`, to re-read this run's own checkpoints.
Nothing else outside `CREATOR` is read, and nothing outside `V7` is written.

## Precedence

When sources disagree, this order settles it — always, and without averaging:

1. `policy/calibration.v1.yaml` — the premises
2. `curricula/arduino_kit/kit_calibration.v1.yaml` — that kit's supplies and evidence
3. `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` — which labs exist
4. `schemas/` — the shapes those must take
5. the remaining `policy/` manifests — checks, controller, limits, routes, failures,
   deferred, and `policy/routing/`
6. `meta_prompt/meta_curriculum_builder.prompt.v6.md` and its `section` assets,
   which rank together: a rule is no weaker for having been written in the asset
   that had room for it
7. `meta_prompt/assets/component_lab_template.v1.md` — governs only where the schema
   has no field: tone, child-language, the safety baseline in sentences
8. `meta_prompt/assets/pedagogy.v1.md` — why a pedagogy field exists, never what its
   value is
9. the prose documents `curricula/arduino_kit/lab_brief.md`,
   `curricula/arduino_kit/roster.md`, `curricula/arduino_kit/teacher_framework.md`
   and `curricula/arduino_kit/teacher_audit.md`
10. `docs/` and `readme.md` — orientation only, never a constraint

Every source is ranked. An unranked document is one whose contradictions get settled
by whoever reads it last, which is how four prose files came to promise something
fourteen labs contradict.

A prose document that contradicts calibration loses, **and the divergence is
recorded as a defect in `remediation_report.md`** rather than resolved silently.
`curricula/arduino_kit/lab_brief.md` and `curricula/arduino_kit/teacher_framework.md`
currently state a different
learner age and an exclusive supply; both are known divergences, and both must
appear in that report.

Never hardcode a lab count. Read it from the curriculum at run time, assert it
against the ids present, and derive every "all labs" test and command from it. A
change to the manifest must change the run with no code edit.
