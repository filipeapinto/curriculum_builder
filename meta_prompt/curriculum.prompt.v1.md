# Curriculum Prompt — v1

Given a curriculum root, produce that curriculum. Do not learn what it teaches.

## Mission

```text
ENGINE      = the directory containing this prompt's `meta_prompt/` folder
PROMPT      = ENGINE/meta_prompt/curriculum.prompt.v1.md
COMPANIONS  = ENGINE/meta_prompt/assets
CURRICULUM  = supplied by --curriculum; required, no default
OUTPUT_ROOT = supplied by --output-root; required, no default, and must resolve beneath ENGINE/outputs/
```

`ENGINE` is **derived, never written down**: resolve it from this file's own location.
An absolute path here would be correct on exactly one machine and would silently
resolve to nothing on any clone.

`CURRICULUM` is a directory under `ENGINE/curricula/`. It holds its manifest, its
domain data, its calibration, its evidence and its domain verifier. **This prompt never
names one.** A prompt that named a curriculum would be one curriculum's prompt, and the
whole objective is that the same file, unmodified, runs a second curriculum in an
unrelated subject with no edit to it.

Read `CURRICULUM`'s manifest. Produce every unit it declares, in the order it declares
them, then the assembled product. Never hardcode how many there are.

Write only under `OUTPUT_ROOT`, and `OUTPUT_ROOT` itself is required to resolve
beneath `ENGINE/outputs/` — a supplied path outside it is refused before any artifact
and before any model call, the same boundary error a path outside `ENGINE` entirely
would raise. `ENGINE`'s own contract — `meta_prompt/`, `policy/`, `schemas/`,
`curricula/` — remains immutable; `ENGINE/outputs/` is the one designated subtree
carved out of it for writes, and nothing under `meta_prompt/`, `policy/`, `schemas/`
or `curricula/` is ever written by a run. If `OUTPUT_ROOT` already holds a run, stop
as `SYSTEM_FAILURE` with failure id `PRECONDITION-OUTPUT-ROOT-EXISTS`, before any
artifact and before any model call. Report the occupied path and the next free
version name. Never auto-increment, merge or replace: choosing which evidence to
keep is a human decision an unattended run must not make. Fail closed rather than
ask.

## Inputs

Everything required is under `ENGINE` or `CURRICULUM`. Validate each **manifest**
against its schema before reading a value from it; the prose inputs have no schema and
cannot have one — read them as prose.

| Input | Role |
|---|---|
| `policy/calibration.v1.yaml` | **the engine-wide premises** — learner age band, the pedagogy caps derived from it, the reading band, the taxonomy verb table, the safety floor. Never one curriculum's supplies |
| `CURRICULUM`'s own calibration | **that curriculum's premises** — what it may draw on, and the evidence each is verified against. Outranked by the engine-wide premises, and outranks the manifest |
| `CURRICULUM`'s manifest | which units exist, in order, and **how many**; the schema its units' domain block is validated against; its domain verifier; its domain configuration |
| `CURRICULUM`'s domain schema | the shape of a unit's domain block. Named by the manifest, supplied by the curriculum, unknown to this prompt |
| `CURRICULUM`'s domain verifier | executable code that decides whether the domain content is right. **Absent verifier is a startup refusal** |
| `CURRICULUM`'s fixtures | inputs the verifier and the checks must **reject**, never inputs to a unit |
| `CURRICULUM`'s prose | its brief, its teaching context, its audit, its roster — outranked by everything above |
| `policy/limits.v1.yaml` | every resource limit, with its numeric default and flag |
| `policy/routes.v1.yaml` | every external capability, with the exact proven invocation |
| `policy/checks.v1.yaml` | the engine's check inventory. A curriculum's own inventory sits beside its manifest |
| `policy/failures.v1.yaml` | A1–A10 and B1–B4, with diagnoses and required corrections |
| `policy/controller.v1.yaml` | states, transitions, ownership, CLI surface |
| `policy/deferred.v1.yaml` | the obligations this contract states and nothing yet executes |
| `schemas/curriculum.schema.v5.json`, `schemas/lab.schema.v4.json`, `schemas/calibration.schema.v1.json`, `schemas/kit_calibration.schema.v1.json` | the shapes for a curriculum, a finished unit, and the two calibrations |
| `schemas/routing_decision.schema.v2.json` | the routing-decision record format — ten required fields, decided and executed |
| `schemas/execution_log.schema.v2.json` | the execution-log record format — typed `action_kind`, conditional `decision_id` |
| `policy/routing/model_registry.v1.yaml` | model capabilities and availability |
| `policy/routing/task_taxonomy.v2.yaml` | task classes and their risk profiles |
| `policy/routing/routing_policy.v1.yaml` | candidate-pool and escalation policy |
| `policy/routing/quality_gates.v1.yaml` | observable acceptance gates, never model self-confidence |
| `meta_prompt/assets/pedagogy.v1.md` | why each pedagogy field exists, never what its value is |
| `meta_prompt/assets/unit_prose.v1.md` | unit structure in prose — tone, child-language rules, the safety baseline in sentences |
| `meta_prompt/assets/model_selector_prompt.v1.md` | the selector's own prompt, read by the selector call and by nothing else |
| `plans/legacy_v3/` | the failed v3 generator and runner — cite by path and line |

Three reads reach outside `ENGINE` and `CURRICULUM`, all declared and bounded: the
sandbox policy `policy/routes.v1.yaml` names; the primary-source capability, which
fetches over the network; and `OUTPUT_ROOT`, read to evaluate the startup precondition
and, on `--resume`, to re-read this run's own checkpoints. Nothing else outside them is
read, and nothing outside `OUTPUT_ROOT` is written.

`RESEARCH` — the network capability the sourcing rule depends on. Fetching a
primary source is a read outside `ENGINE`, so it is declared here; it is a capability
and not a directory, which is why no boundary line defines it as a path.
`policy/routes.v1.yaml` declares four routes and none of them is this one, so the
capability gate proves those four and cannot preflight this. That is a known divergence,
not a detail: record it in the run's report, and never report the route set as fully
proven while it stands.

## Precedence

When sources disagree, this order settles it — always, and without averaging:

1. `policy/calibration.v1.yaml` — the engine-wide premises
2. `CURRICULUM`'s own calibration — what that curriculum may draw on
3. `CURRICULUM`'s manifest — which units exist and what its domain is
4. `schemas/` and the domain schema the manifest names — the shapes those must take
5. the remaining `policy/` manifests — checks, controller, limits, routes, failures,
   deferred, and `policy/routing/`
6. this prompt
7. `meta_prompt/assets/unit_prose.v1.md` — governs only where the schema has no field:
   tone, child-language, the safety baseline in sentences
8. `meta_prompt/assets/pedagogy.v1.md` — why a pedagogy field exists, never what its
   value is
9. `meta_prompt/assets/model_selector_prompt.v1.md` — how the selector decides, never
   which route it may decide on: that is `policy/routing/`, ranked above at 5
10. `CURRICULUM`'s prose documents
11. `docs/` and `readme.md` — orientation only, never a constraint

Every source that is read is ranked. An unranked document is one whose contradictions
get settled by whoever reads it last, which is how four prose files came to promise
something fourteen units contradict.

`meta_prompt/deprecated/` is not ranked because it is never read. It holds superseded
versions of this contract, retained as history; each is a complete and contradicting set
of instructions, so a run that opens one is taking orders from a document this contract
replaced.

A prose document that contradicts calibration loses, **and the divergence is recorded as
a defect in the run's report** rather than resolved silently. A curriculum whose prose
states a different learner age or an exclusive supply has a known divergence, and it
must appear in that report rather than being quietly reconciled.

Never hardcode a unit count. Read it from the manifest at run time, assert it against
the ids present, and derive every "all units" test and command from it. A change to the
manifest must change the run with no code edit. Never hardcode the curriculum's name,
its subject, or any word that belongs to its domain.

## What a unit is

`schemas/lab.schema.v4.json` is the contract. Seven blocks, none optional: `identity`,
`pedagogy`, `sequence`, `content`, `safety`, `visuals` — the engine's six — and
`domain`.

**The domain block is the curriculum's.** Its shape is fixed by the schema the manifest
names in `domain.schema`, and this contract says nothing about what is in one. A unit
validates against both: the engine's contract for the six, the curriculum's for the
seventh. Do not restate either schema here. They already encode the pedagogy caps, the
5E ordering, the Predict-Observe-Explain rule, the provenance fields and the receipt
format. `meta_prompt/assets/unit_prose.v1.md` carries what a schema cannot — tone,
child-language rules, the safety baseline in sentences — and governs where the schema
has no field.

## One parent

**Every fact in a unit has exactly one parent, and it is the domain block.** Prose
steps, tables, maps, diagrams, troubleshooting and adult checks are generated from that
same data. Each rendered fact names the pointer it came from, and the check that decides
this is `DOC-DERIVED-FROM-SOURCE` — resolved mechanically, never asserted.

Fail closed on any inconsistency between a rendered fact and its parent. This is the
sole mechanism the evidence reports as working: the best published contradiction
detector *"contributes negligibly"*, and deriving everything from one fixed source is
what remains.

## Grounding

**Every domain value carries a primary source, retrieved during this run by exact
identifier, never recalled.** `RESEARCH` locates the official document for each value
and records its identifier, its access date and its scope beside the value and its
measurement condition. No primary sources ship in `ENGINE`; acquiring them is part of
the run.

This is the strongest measured control in the whole corpus — corpus restriction moves
hallucination from over 10% to 1–2%, and removing retrieval collapses citation recall
from 83.48% to 60.11%. A value that cannot be sourced stops the unit. A value recalled
rather than sourced is a failed check, not a shortcut.

The stop is **deterministic and never a judgement**: did the fetch succeed, does the
hash resolve. A model deciding that a fact cannot be sourced is abstention, and
abstention measures at 36.1% accuracy on multi-document questions while over 73% of
predictions are made at maximum confidence.

## The domain verifier

`CURRICULUM` declares a verifier. **A curriculum that declares none does not run.**

The engine never knows what the verifier checks. It knows it must exist, must be code,
must be executable, and must have been proven against the fixtures the curriculum
declares before any unit is generated. Run it before any review, on every unit, and
treat its refusal as final.

This is the whole reason the engine can be indifferent to a subject without being
unsafe: a domain is generatable exactly to the extent that it has a verifier which is
not a model. **Never use a model to check a model's domain work.** That is the one role
the evidence specifically rules out.

## Generic checks

These the engine owns, and they run on every unit in every subject:

- **schema validity** — against the engine's contract and the curriculum's domain
  schema. Note what this does not mean: 100% schema validity has been measured
  alongside 2.0% semantic success. A valid unit is a shaped unit, not a correct one;
- **readability** — `TEXT-READABILITY-BAND`, against the band in
  `policy/calibration.v1.yaml`, on the child-facing text;
- **taxonomy verbs** — `TEXT-BLOOM-VERBS`, against the level the objective declares.
  **It flags and never blocks.** Human raters agree with each other on the level of an
  objective only 46.58% of the time, so a disagreement is recorded for a person to look
  at and is never a failed gate;
- **cross-document derivation** — `DOC-DERIVED-FROM-SOURCE`, above;
- **receipt resolution** — `RECEIPT-HASH-RESOLVES`. Every receipt's hash is recomputed
  from the bytes of the artifact it names, in the artifact actually shipped. A receipt
  that does not resolve is a failed gate, not a warning.

Order reasoning before structure. Free-text reasoning first, structured conclusions
after: forcing a conclusion field ahead of the reasoning that supports it degrades the
reasoning, and the domain work is reasoning-heavy.

## Review

**One judge per pass, from a different model family than the generator**, with an
explicit rubric and a randomised presentation order. Record the verdict, the rubric and
the order. Check id `REV-JUDGE-SINGLE-CROSS-FAMILY`.

Not twelve. Nine cross-family judges provide **2.18 effective votes** — 24.2%
independence — and the best single judge matched the full panel. Twelve reviewers buy
about two independent opinions at twelve times the cost. Spend what that recovers on
deterministic checks, which beat judges by 1.2×–7× where both were measured.

Isolation is structural, not instructed: a reviewer's authorized input set must not
include any sibling's verdict file, and a test fails if such a path exists. Check id
`REV-ISOLATED`. Isolation addresses collusion, and **it does nothing about correlated
error** — nine judges from seven families still collapsed to 2.18 independent votes.
Recording that limit here is the point of stating it.

## Routing

Which model serves which task is data, and this section is what binds that data. It
names the authorized routing inputs and states the invariants no data file can express.
It **never inlines a value**: no model id, no reasoning level, no candidate pool appears
here. The prompt binds; the data obeys. A routing fact with two owners is the defect
this separation exists to stop.

`policy/routes.v1.yaml` and `policy/routing/` are different things and are never merged:
the first is the set of external capabilities proven by a real preflight call, the
second is which model serves which task.

**The invariants.**

- The selector runs first and code applies its result. A model never chooses its own
  route.
- `--model` is a fallback only and **may not bypass the selector** in
  `policy/routing/`, promoted here from `policy/controller.v1.yaml`. Check id
  `SEL-NO-MODEL-BYPASS`.
- No model at all for merging, validating, hashing, rendering, aggregating, auditing or
  logging — those are deterministic work. Check id `SEL-NO-MODEL-FOR-DETERMINISTIC`.
- The cheapest eligible route serves bounded drafting; a stronger route serves domain
  design and QA; maximum reasoning is reached only through a failed safety escalation,
  and never as a default. Check id `SEL-ESCALATION-BOUNDED`.
- No redundant drafts. Runs are serial by default. Parallelise retrieval and analysis;
  **serialise composition** — parallel section writing was measured at −6% coherence and
  was shipped and then withdrawn by its author for producing disjoint output.
- No model approves its own unsupported technical claim.

**The obligation.** Every model call emits a schema-valid routing decision before the
call is made, validating against `schemas/routing_decision.schema.v2.json`
(`SEL-DECISION-VALID`), and the decision records the route **actually executed** in
`executed_model` beside the route decided in `decided_model`
(`SEL-EXECUTED-MATCHES-DECIDED`). The execution log's act for that call carries the
decision's id in `decision_id`, required by `action_kind: model_call` in
`schemas/execution_log.schema.v2.json`.

**What this section does and does not achieve.** It makes these rules stated, owned and
representable in records a validator can check. It does not make them enforced, because
nothing in this repository executes a model, applies a routing decision or refuses a
call. Prose states the rule, JSON Schema proves both fields exist, and a gate compares
them; only a controller could refuse to act on the difference. `RT-3`, `RT-4` and `RT-5`
in `policy/deferred.v1.yaml` name that work, and until each is discharged no document or
report may state that the selector is enforced.

## Proving it

Six gates, in order. Record every result with a timestamp and a category label. Five
labels are the stage vocabulary `policy/checks.v1.yaml` owns — `logger`, `static`,
`deterministic`, `live-capability`, `golden` — and are never spelled differently here.
The sixth, `simulated`, is this contract's own: it labels runs driven by fake workers,
and no check id carries it, because a simulated result is evidence about the controller
and never evidence about a unit.

| # | Gate | Check ids | Proves |
|---|---|---|---|
| 0 | **Logger** | `LOG-*` | append-only ordering, monotonic ids, start/completion pairing, concurrent-append safety, coverage of every checkpoint, and failure when an operation lacks its record. **Passes before any other artifact exists.** |
| 1 | **Static** | `CAL-*`, `CUR-*`, `SEL-*` | every one of those checks in `policy/checks.v1.yaml`, each backed by an executed assertion. A `SEL-*` id whose method is `execution` is reported `MAPPED, NOT EXECUTED` with its `RT-` id, never as covered. This table advertises the **engine's** inventory; a curriculum's own ids are its release responsibility and are named beside its manifest |
| 2 | **Deterministic** | `LAB-*`, `REV-ISOLATED`, `TEXT-*`, `DOC-*`, `RECEIPT-*` | transitions, aggregation, failure classification, checkpoints, hashes, resource limits, derivation from one parent, reading level, taxonomy verbs against the declared level, receipt resolution, terminal audits — plus every fixture marked `reject` in either inventory, each of which must fail. `TEXT-BLOOM-VERBS` **flags and never blocks**: it is recorded here and it does not decide the gate |
| 3 | **Simulated** | — | fake workers drive clean acceptance, revision, malformed output, transient retry, repeated failure, legal block, system failure, interrupt and resume, then one clean pass over every unit |
| 4 | **Live capability** | `ROUTE-PROVEN` | one real preflight call on every route in `policy/routes.v1.yaml`, under the exact recorded invocation |
| 5 | **Golden unit** | `PDF-*`, `REV-JUDGE-SINGLE-CROSS-FAMILY`, `LAB-SCHEMA-VALID` | one complete unit: the declared judge, sourced data, required visuals with resolving receipts, targeted revision evidence, the artifact rendered and every page rasterized and inspected, forced interrupt and resume with before/after hashes, final audit |

Gate 1 exists because a previous build advertised six static checks and asserted two. A
meta-test must fail if any check id named in a result has no executed assertion, or if
any id in either inventory is never executed. Reporting a check as present without
running it is evidence misreporting — a drift stop, not a bug.

Static and simulated coverage is never described as generated-unit coverage.

## Acceptance

**Code decides, models write.** Python owns unit order, state transitions, routing,
retries, checkpoints, revision targeting, every audit, and every acceptance decision. A
model never advances a state, never aggregates a verdict, never decides a unit is done.
The full contract is `policy/controller.v1.yaml`.

Workers are deliberately starved. Each receives only its role, its stable check ids, the
selected unit's data, accepted prerequisite artifacts, its authorized input paths, its
authorized output paths, and one output schema — the block it is authorized to write. A
worker cannot choose a transition, scan prior versions, change acceptance rules, or
create an undeclared file. Check id `CUR-BOUNDED-PROMPTS`.

**The output is a draft.** Human review of the content happens downstream of this
pipeline, as editorial practice on the produced artifact. It is not a run gate, not a
required argument, and not a condition this run waits on. The claim this pipeline makes
is *"every declared automated check passed"*, and only that. It is never "child-ready"
and never "reviewed". Whatever review, compliance check or approval the product needs
happens outside this repository's runs, and no report may state that it happened here.

## Never hardcode

Not the unit count. Not the curriculum's name. Not its subject, or any word belonging to
it. Not the number of anything the manifest declares. Read them, assert them, and derive
every command from them.

If a fix requires a word from one curriculum's subject to appear in `policy/`,
`schemas/` or this file, the fix is in the wrong layer. It belongs under that
curriculum's own directory. `FR-P5-ENGINE-GENERIC` is the gate that reports it, and
adding an exclusion to that gate is the defect it was written to detect, never a repair.

## Companions

A companion is not part of this contract. It is an input, read where this prompt says so
and ranked where §Precedence ranks it — below this file, above the project prose.

| Asset | Kind | Carries |
|---|---|---|
| `meta_prompt/assets/unit_prose.v1.md` | companion | unit structure in prose — tone, child-language rules, the safety baseline in sentences |
| `meta_prompt/assets/pedagogy.v1.md` | companion | why each pedagogy field exists, never what its value is |
| `meta_prompt/assets/model_selector_prompt.v1.md` | companion | the selector's own prompt, read by the selector call |

**There are no `section` assets, and that is the change.** v6 was a short prompt plus six
assets that composed into the contract, because it was building a generator and the
generator's rules needed room. This file is not building anything: it runs a curriculum,
and its rules fit in one file that can be read start to finish. A rule that needed a
seventh file would be a rule this prompt is too big to state.

Nothing else belongs in `COMPANIONS`. A file there that no row above names is prose with
no owner, and prose with no owner is how a contract acquires a second author. A row that
names a file which does not resolve is the reverse defect, and it is fatal: stop as
`SYSTEM_FAILURE` before any artifact, because the contract you were handed is not the
contract you are reading. Check id `PRECONDITION-ASSETS-RESOLVE`.

## Execution

1. Resolve `ENGINE` from this file's location. Read `--curriculum` and `--output-root`.
   Refuse to start if either was not supplied.
2. Check that every row of the companion table resolves. A run that begins without them
   is executing a fragment of its own contract.
3. Check the startup precondition stated in §Mission — `OUTPUT_ROOT` must not hold a
   run — before any artifact and before any model call.
4. Create `OUTPUT_ROOT` and its results folder, and nothing else. This is the only write
   that precedes the logger, and it exists because the logger must have somewhere legal
   to append.
5. Build the logger and run gate 0. Pass it before creating any other artifact. From
   this point on every action is logged before it is taken.
6. Validate every manifest against its schema. Read no value before it validates.
7. **Refuse to continue if `CURRICULUM` declares no domain verifier, or if its declared
   fixtures have not been executed.** Run the verifier against every fixture the
   curriculum declares and require each refusal to carry its declared code.
8. Record the run's state: authorized roots, and the hash of this file.
9. Read the manifest's unit list. Assert the count against the ids present.
10. For each unit in declared order: retrieve its primary sources, assemble its domain
    block, run the domain verifier, generate the six engine blocks from it, run the
    generic checks, run one judge, and record the acceptance decision.
11. Run gates 1–3, then gate 4, then gate 5 on the first accepted unit.
12. Assemble the product, render it, and rasterize and inspect every page.
13. Audit for drift before and after generation, tests and revisions.
14. Revise only affected artifacts until a terminal state.
15. Write the run's report and the full-run command, only if earned.

Log the planned action before making any change. Use conservative documented defaults;
do not ask the user for ordinary implementation decisions. Stop before exceeding any
limit and preserve the safest resumable checkpoint.

## Final response

Report: terminal state; the output and golden-unit paths; write-scope and drift results;
every gate result; the rendered artifact and resume outcome; the log path, hash, action
totals and pairing result; each B1–B4 failure beside its evidence of correction;
revision and resource totals; unresolved failures and the safest restart point; and the
full-run command only on acceptance.

An action record is appended when an action **starts** and again when it **ends**, so a
started record is not a completed one. Report the pairing, not the raw count, and do not
present failure records as a general success log.

Three claims that are never merged, and each must be stated separately:

- **the pipeline produced N units** — a count of artifacts;
- **each unit passed every declared automated check** — the only quality claim this
  pipeline makes;
- **the units are drafts pending downstream human review** — always true, per
  §Acceptance.

Never claim the curriculum is complete unless every unit has been generated and accepted
and the final audited product exists. Never describe static or simulated coverage as
generated-unit coverage. Never report a check as passing that did not execute.
