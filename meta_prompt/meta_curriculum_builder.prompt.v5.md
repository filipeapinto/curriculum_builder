# ELEGOO Meta-Curriculum Prompt — v5

Build and prove a curriculum generator. Do not write curriculum.

## Mission

Create `templates_v7/` — a deterministic controller plus small bounded worker
prompts — and prove it well enough that a full run needs nobody watching. Its
human-readable runtime contract is:

`V7/component_lab_orchestrator_prompt.v7.md`

Produce exactly one live lab, L01, as evidence the generator works. Nothing else.

The v3 generator failed eight overnight runs without producing one accepted lab.
Two rebuilds followed; the second stopped at `META_DRIFT_STOP` with four failed
gates. Every constraint below traces to one of those failures, recorded in
`policy/failures.v1.yaml`.

## Write boundary

```text
CREATOR     = the directory containing this prompt's `meta_prompt/` folder
META_PROMPT = CREATOR/meta_prompt/meta_curriculum_builder.prompt.v5.md
LEGACY      = CREATOR/plans/legacy_v3
OUTPUT_ROOT = supplied by --output-root; required, no default
V7          = OUTPUT_ROOT/templates_v7
```

`CREATOR` is **derived, never written down**: resolve it from this file's own
location. An absolute path here would be correct on exactly one machine and would
silently resolve to nothing on any clone, which is the failure this line replaces.

`OUTPUT_ROOT` is **required at invocation** and has no default. It is deliberately
outside `CREATOR`: the inputs are immutable and a run writes nothing into them.
Refusing to guess is the point — a default would eventually be a directory holding
someone else's evidence. `policy/controller.v1.yaml` already declares the flag.

Write only to `V7`. Everything else is immutable, `CREATOR` included. The v3, v4 and
v5 attempts are not named here as paths: they may not exist at any location, and
naming a directory that is not there protects nothing. They are never read, and every
diagnosis drawn from them is quoted in full in `policy/failures.v1.yaml`.

All names `V7` creates are lowercase, versioned `.vN` where versioned at all.

If `V7` exists at startup, stop as `META_SYSTEM_FAILURE` with failure id
`PRECONDITION-OUTPUT-ROOT-EXISTS`, before any artifact and before any model call.
Report the occupied path and the next free version name. Never auto-increment,
merge, delete or overwrite: choosing which evidence to keep is a human decision an
unattended run must not make. Fail closed rather than ask.

Never create a live dossier for any lab beyond L01 during this task.

## Inputs

Everything required is under `CREATOR`, and every path in the table below is
relative to it. Validate each **manifest** against its schema before reading a value
from it; the prose inputs have no schema and cannot have one — read them as prose.

| Input | Role |
|---|---|
| `policy/calibration.v1.yaml` | **the premises** — learner age band, the pedagogy caps derived from it, permitted supplies, safety floor |
| `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` | the curriculum — which labs exist, in order, and **how many** |
| `policy/limits.v1.yaml` | every resource limit, with its numeric default and flag |
| `policy/routes.v1.yaml` | every external capability, with the exact proven invocation |
| `policy/checks.v1.yaml` | every stable check id and what it asserts |
| `policy/failures.v1.yaml` | A1–A10 and B1–B4, with diagnoses and required corrections |
| `policy/controller.v1.yaml` | states, transitions, ownership, CLI surface |
| `policy/deferred.v1.yaml` | RT-1…RT-6 — the obligations this contract states but nothing yet executes |
| `schemas/curriculum.schema.v4.json`, `schemas/lab.schema.v3.json`, `schemas/calibration.schema.v1.json` | the shapes for the curriculum, a finished lab, and calibration |
| `schemas/routing_decision.schema.v2.json` | the routing-decision record format — ten required fields, decided and executed |
| `schemas/execution_log.schema.v2.json` | the execution-log record format — typed `action_kind`, conditional `decision_id` |
| `meta_prompt/component_lab_template.v1.md` | lab structure in prose — tone, child-language rules, safety baseline |
| `policy/routing/model_registry.v1.yaml` | model capabilities and availability |
| `policy/routing/task_taxonomy.v2.yaml` | task classes and their risk profiles |
| `policy/routing/routing_policy.v1.yaml` | candidate-pool and escalation policy |
| `policy/routing/quality_gates.v1.yaml` | observable acceptance gates, never model self-confidence |
| `plans/legacy_v3/` | the failed v3 generator and runner — cite by path and line |
| `curricula/arduino_kit/official_kit_photo.jpg`, `curricula/arduino_kit/kit_evidence.md` | the verified kit evidence L01 depends on |
| `curricula/arduino_kit/fixtures/` | fixtures the tests must **reject**, never inputs |
| `curricula/arduino_kit/lab_brief.md`, `curricula/arduino_kit/roster.md`, `curricula/arduino_kit/teacher_framework.md`, `curricula/arduino_kit/teacher_audit.md` | project scope and teaching context |
| `meta_prompt/pedagogy.v1.md`, `docs/how_it_works.md` | why each pedagogy field exists; how the machine fits together |

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
6. this prompt
7. `meta_prompt/component_lab_template.v1.md` — governs only where the schema has no
   field: tone, child-language, the safety baseline in sentences
8. `meta_prompt/pedagogy.v1.md` — why a pedagogy field exists, never what its value is
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

## What the generator must be

Code decides, models write. Python owns lab order, state transitions, routing,
retries, checkpoints, revision targeting, every audit, and every acceptance
decision. A model never advances a state, never aggregates a verdict, never
decides a lab is done. Deterministic work — merging, validating, hashing,
rendering, aggregating, auditing, logging — uses no model at all. The full
contract is `policy/controller.v1.yaml`.

Workers are deliberately starved. Each receives only its role, its stable check
ids, the selected lab data, accepted prerequisite artifacts, its authorized input
paths, its authorized output paths, and one output schema — the block of
`schemas/lab.schema.v3.json` it is authorized to write. A worker cannot choose a
transition, scan prior versions, change acceptance rules, or create an undeclared
file.

**Twelve isolated reviewer invocations per lab.** Three passes — plan, dossier QA,
rendered PDF — across four domains: electronics, pedagogy, communication, graphic.
Twelve separate bounded calls, never batched. Reviewing a dossier and reviewing the
printed page are different acts: a diagram correct in the data can be illegible at
print size, passing the first and failing the second. Isolation is structural, not
instructed — a reviewer's authorized input paths must not include any sibling's
verdict file, and a test must fail if such a path exists.

## What a lab must be

`schemas/lab.schema.v3.json` is the contract. Seven blocks, none optional:
identity, pedagogy, sequence (5E), electronics, content, safety, visuals. Every
lab validates against it before acceptance; the controller validates
deterministically, and a failure routes to targeted revision.

Do not restate that schema here or in v7. It already encodes the pedagogy caps,
the 5E ordering, the Predict-Observe-Explain rule, the electrical model, the
provenance fields and the safety enums. `meta_prompt/component_lab_template.v1.md`
carries what a schema cannot — tone, child-language rules, the safety baseline in
sentences — and governs where the schema has no field.

Two rules the schema cannot express on its own:

**One parent for every fact.** Machine-readable circuit and experiment data is the
authority for parts, pins, values, endpoints, nets, voltage, current limiting,
ratings, measurements, controller I/O and power sequence. Prose steps, connection
tables, maps, schematics, troubleshooting and adult checks are generated from that
same data. Fail closed on any inconsistency, unsafe powered circuit, missing
rating, unbounded current, illegal pin, absent current limiting, supply mismatch or
ambiguous endpoint.

**Every electrical value carries a primary source.** `RESEARCH` locates the
official datasheet or manufacturer listing for each component, and records URL,
part or family, and access date beside the value and its measurement condition. No
datasheets ship in `CREATOR`; acquiring them is part of the run. A rating that
cannot be sourced is the one legitimate `BLOCKED` case. A value recalled rather
than sourced is a failed check, not a shortcut.

## Routing

Which model serves which task is data, and this section is what binds that data. It
names the authorized routing inputs and states the invariants no data file can
express. It **never inlines a value**: no model id, no reasoning level, no candidate
pool appears here. The prompt binds; the data obeys. A routing fact with two owners
is the defect this separation exists to stop.

`policy/routes.v1.yaml` and `policy/routing/` are different things and are never
merged: the first is the set of external capabilities proven by a real preflight
call, the second is which model serves which task.

**The invariants.**

- The selector runs first and code applies its result. A model never chooses its own
  route.
- `--model` is a fallback only and **may not bypass the selector** in
  `policy/routing/`, promoted here from `policy/controller.v1.yaml`. Check id
  `SEL-NO-MODEL-BYPASS`.
- No model at all for merging, validating, hashing, rendering, aggregating,
  auditing or logging — those are deterministic work. Check id
  `SEL-NO-MODEL-FOR-DETERMINISTIC`.
- The cheapest eligible route serves bounded drafting; a stronger route serves
  electronics design and QA; maximum reasoning is reached only through a failed
  safety escalation, and never as a default. Check id `SEL-ESCALATION-BOUNDED`.
- No redundant drafts. Runs are serial by default.
- No model approves its own unsupported technical claim, promoted here from
  `policy/routing/readme.md`.

**The obligation.** Every model call emits a schema-valid routing decision before
the call is made, validating against `schemas/routing_decision.schema.v2.json`
(`SEL-DECISION-VALID`), and the decision records the route **actually executed** in
`executed_model` beside the route decided in `decided_model`
(`SEL-EXECUTED-MATCHES-DECIDED`). The execution log's act for that call carries the
decision's id in `decision_id`, required by `action_kind: model_call` in
`schemas/execution_log.schema.v2.json`.

**What this section does and does not achieve.** It makes these rules stated, owned
and representable in records a validator can check. It does not make them enforced,
because nothing in this repository executes a model, applies a routing decision or
refuses a call. Prose states the rule, JSON Schema proves both fields exist, and a
gate compares them; only a controller could refuse to act on the difference.
`RT-3`, `RT-4` and `RT-5` in `policy/deferred.v1.yaml` name that work, and until
each is discharged no document or report may state that the selector is enforced.

## Proving it

Six gates, in order. Record every result with a timestamp and a category label. Five
labels are the stage vocabulary `policy/checks.v1.yaml` owns — `logger`, `static`,
`deterministic`, `live-capability`, `golden` — and are never spelled differently here.
The sixth, `simulated`, is this prompt's own: it labels runs driven by fake workers,
and no check id carries it, because a simulated result is evidence about the
controller and never evidence about a lab.

| # | Gate | Check ids | Proves |
|---|---|---|---|
| 0 | **Logger** | `LOG-*` | append-only ordering, monotonic ids, start/completion pairing, concurrent-append safety, coverage of every checkpoint, and failure when an operation lacks its record. **Passes before any other v7 artifact exists.** |
| 1 | **Static** | `CAL-*`, `CUR-*`, `L01-*`, `SEL-*` | every one of those checks in `policy/checks.v1.yaml`, each backed by an executed assertion. A `SEL-*` id whose method is `execution` is reported `MAPPED, NOT EXECUTED` with its `RT-` id, never as covered |
| 2 | **Deterministic** | `LAB-*`, `REV-ISOLATED` | transitions, aggregation, block eligibility, failure classification, checkpoints, hashes, resource limits, circuit/prose/render consistency, terminal audits — plus every fixture marked `reject` in `policy/checks.v1.yaml`, each of which must fail validation |
| 3 | **Simulated** | — | fake workers drive clean acceptance, plan and artifact revision, malformed output, transient retry, repeated failure, legal block, system failure, interrupt and resume, then one clean pass over every lab |
| 4 | **Live capability** | `ROUTE-PROVEN` | one real preflight call on every route in `policy/routes.v1.yaml`, under the exact recorded invocation |
| 5 | **Golden L01** | `PDF-*`, `REV-COUNT-TWELVE`, `LAB-SCHEMA-VALID` | one complete lab: twelve reviews, sourced data, required visuals with resolving receipts, targeted revision evidence, PDF rendered and every page rasterized and inspected, forced interrupt and resume with before/after hashes, final controller audit |

Gate 1 exists because the previous build advertised six static checks and asserted
two. A meta-test must fail if any check id named in a result has no executed
assertion, or if any id in `policy/checks.v1.yaml` is never executed. Reporting a
check as present without running it is evidence misreporting — a drift stop, not a
bug.

Static and simulated coverage is never described as generated-lab coverage. Do not
start a live full run.

## The action log

`V7/test_results/prompt_execution_log.md`, append-only, validating against
`schemas/execution_log.schema.v2.json`. Every record carries a typed `action_kind`,
and an act whose `action_kind` is `model_call` must carry the `decision_id` of the
routing decision it was made under — the condition keys on the type, never on the
wording of `action`.

Every controller action appends one record before it starts and one when it ends:
a completion `ACT` citing the started id, or an `EXEC` whose mandatory `Closes`
field names it. So the pairing gate is computable — collect every started id,
subtract every id cited by a completion or a `Closes`, and the remainder must be
empty.

The logger takes the closing id as an argument and never derives one; its counter
is monotonic by construction, never recovered by counting text in the file it is
writing; appends hold an exclusive lock and never rewrite what is on disk; and if
an id cannot be allocated or an append cannot be proven, the run stops as
`META_SYSTEM_FAILURE`. That is failure B1, which recorded an entire previous run
through a logger nobody had tested.

`V7/test_results/meta_execution_state.json` records the log path and hash, completed action count,
failure count, unpaired-start ids, last action id and last completion id.

## Convergence and drift

Keep `V7/test_results/meta_execution_state.json` current and atomic: goal hash,
prompt hash, authorized roots, phase, revision cycle, gates passed and failing,
stable failure ids, artifacts authorized to change, resource totals, last
measurable improvement, drift result, next action, terminal state, log totals.

```text
run gate → record failures → authorize affected artifacts
→ revise → rerun affected and dependent gates
→ record measurable improvement → repeat
```

Stop as `META_DRIFT_STOP` on any `DRIFT-*` condition in `policy/checks.v1.yaml`, or
on exceeding any limit in `policy/limits.v1.yaml`. A defective test may change only
where it contradicts this prompt; record both hashes, the contradiction, the
correction and the regression evidence.

Three terminal states, no others:

- `META_ACCEPTED` — every release gate and drift audit passes; golden L01 accepted.
- `META_SYSTEM_FAILURE` — a required capability stays unavailable after bounded
  retry, with evidence; or the log cannot be written; or a startup precondition
  needs a human decision.
- `META_DRIFT_STOP` — scope drift or bounded non-convergence.

Implementation, prompt, schema, test, renderer, visual and layout defects require
revision. They are not external failures — do not classify your own bug as an act
of God.

## Deliverables

```text
V7/                                          = OUTPUT_ROOT/templates_v7
  component_lab_orchestrator_prompt.v7.md    concise runtime contract; delegates to controller and workers
  readme.md                                  derivation, authority, test categories, preflight, run/resume commands
  remediation_report.md                      every id in failures.v1.yaml → correction, proving test, result, residual risk
  canonical_curriculum.yaml + .schema.json   derived from the curriculum manifest, with source hash recorded
  automation/  prompts/  routing/  schemas/  renderers/  tests/  test_results/
```

v7 authors its own artifact schemas under `V7/schemas/`. No legacy artifact schema
is supplied and none is a contract to satisfy — decompose a lab into whatever
artifacts the controller can validate without a model, and justify that
decomposition in `remediation_report.md`.

## Execution

1. Resolve `CREATOR` from this file's location and read `--output-root`. Refuse to
   start if it was not supplied.
2. Check the startup precondition: if `V7` exists, stop as `META_SYSTEM_FAILURE` with
   failure id `PRECONDITION-OUTPUT-ROOT-EXISTS`, before any artifact and before any
   model call.
3. Create `V7` and `V7/test_results/`, and nothing else. This is the only write that
   precedes the logger, and it exists because the logger must have somewhere legal to
   append: authorized writes are confined to `V7`, so `V7` has to exist before the
   first record can be written. Creating it is not logged, because the log does not
   exist yet; it is reconstructible from the directory's own timestamp.
4. Build the logger. Pass its proving tests before creating any other artifact. From
   this point on every action is logged before it is taken.
5. Validate every manifest against its schema. Read no value before it validates.
6. Write the v7 meta state; record authorized roots.
7. Inspect `plans/legacy_v3/` and write failure→fix→test traceability for every id in
   `policy/failures.v1.yaml`.
8. Design v7: canonical data, controller, runtime prompt, worker contracts.
9. Implement controller, prompts, schemas, selector, renderers, audits, reports.
10. Run gates 1–3.
11. Run gate 4 — one real call per route.
12. Run gate 5 — golden L01, including forced interruption, resume, and page
    inspection of the shipped PDF.
13. Drift-audit before and after implementation, tests and revisions.
14. Revise only affected artifacts until a terminal state.
15. Write `V7/remediation_report.md` and the full-run command, only if earned.

Log the planned action before making any change. Use conservative documented
defaults; do not ask the user for ordinary implementation decisions. Stop before
exceeding any limit and preserve the safest resumable checkpoint.

## Release gates

`META_ACCEPTED` requires all of:

- every deliverable above present;
- gates 0–5 passing, with resume and PDF inspection proven;
- every check in `policy/checks.v1.yaml` executed, and every check id in every
  result backed by an executed assertion;
- every fixture marked `reject` in `policy/checks.v1.yaml` actually rejected, and
  every id declaring `fixture_expectation: reject` that names no fixture reported by
  id in `remediation_report.md` as advertised-but-unfixtured. Four do today:
  `LAB-BLOOM-DEPTH`, `LAB-POE-ORDER`, `LAB-CURRENT-MARGIN`, `LAB-VALUE-SOURCED`.
  Silence about them would be the misreporting gate B3 exists to catch;
- golden L01 validating against `schemas/lab.schema.v3.json`, all seven blocks;
- exactly twelve isolated reviewer invocations, with isolation proven structurally;
- every visual receipt hash resolving to an asset embedded in the accepted PDF;
- one real preflight call per route, with the sandbox policy recorded;
- every action paired and ordered, zero unpaired starts, totals agreeing across
  controller state, test results and log;
- every limit recorded with the numeric value in force;
- every id in `policy/failures.v1.yaml` mapped to a correction and a proving test;
- calibration divergences recorded, not resolved;
- immutable inputs unchanged; no unauthorized write; no unlogged model or tool call;
- no live generation beyond L01;
- no evidence-category misreporting.

## Final response

Report: terminal state; `V7` and golden-L01 paths; write-scope and drift results;
every gate result; the golden PDF and resume outcome; the log path, hash, `ACT`/
`EXEC` totals and pairing result; each B1–B4 failure beside its evidence of
correction; meta-revision and resource totals; unresolved failures and the safest
restart point; and the full-run command only on `META_ACCEPTED`.

An `ACT` is appended when an action **starts** and again when it **ends**, so a
started record is not a completed one; an `EXEC` records a failure and closes the
start it terminates. Report the pairing, not the raw count, and do not present the
failure records as a general success log. Never claim the curriculum is
complete unless every lab has been live-generated and accepted and the final
audited workbook exists.
