# How the curriculum generator works

A walk through the machine: what runs, in what order, who decides what, and why it
is built this way rather than the obvious way.

---

## 1. The obvious way, and why it failed

The obvious way to generate a 35-lab electronics workbook is to write one very good
prompt and call a model 35 times. That was v3. It ran eight times overnight and
produced zero accepted labs.

The failure wasn't prompt quality. It was that **nobody could check the output**. A
single model call produced child text, adult guide, circuit data, visual plan and
QA verdict as one blob. When something was wrong there was no artifact to point at,
no state to resume from, and no way to revise one part without regenerating
everything. Worse, the model that wrote the lab also judged it.

Everything below follows from fixing that.

---

## 2. Two levels

```
meta prompt  ──builds & proves──▶  templates_v7/  ──generates──▶  L01–L35 + workbook
 (run once)                        (the generator)                 (the product)
```

The **meta prompt** (`prompts/`) is a build tool. It writes the generator,
proves it through six test gates, produces one golden lab as evidence, and stops.
It never writes curriculum at scale.

The **generator** (`templates_v7/`, created by the run) is what produces labs. It
is not a prompt — it is a Python controller plus a set of small, bounded worker
prompts and a canonical data file.

Confusing these two is the single most common way to wreck this project. The meta
prompt's job is finished when the generator is proven, not when labs exist.

---

## 3. The division of labour: code decides, models write

This is the core design rule.

| Python controller owns | Model workers own |
|---|---|
| lab order and state transitions | prose for children |
| which worker runs, with which model | prose for adults |
| retries, timeouts, stall detection | circuit and experiment design |
| checkpoints, hashes, resume | review verdicts against fixed check IDs |
| aggregating review verdicts | visual planning |
| revision targeting | — |
| every terminal decision and audit | — |
| permission to advance to the next lab | — |

A model never chooses a state transition, never decides whether a lab is accepted,
never sees another reviewer's verdict, and never creates a file it wasn't
authorized to create. Deterministic work — merging, validating, hashing, rendering,
aggregating, auditing — uses **no model at all**.

Workers are deliberately starved of context. Each one receives only: its role, its
stable check IDs, the canonical data for the selected lab, accepted prerequisite
artifacts, its authorized input paths, its authorized output paths, and one output
schema. That's it. A worker cannot scan prior versions, cannot read sibling
outputs, and cannot renegotiate the acceptance rules.

---

## 4. Where a lab comes from

```
curriculum.v4.yaml   the curriculum: 35 labs, component-first
        ↓  validate, then derive
canonical_curriculum.yaml      the single authority for the run
```

`curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` is the input;
`schemas/lab.schema.v3.json` (section 5)
is the output contract. There is one curriculum file and it is already resolved. Earlier versions shipped a
base plus an override layer that patched 11 labs, and the two disagreed on
`component_set`, `core_activity` and `safety_focus` for labs like L14, L20, L21 and
L35. Carrying both values forward is failure A6, so the layers were merged and the
conflicts settled at source. Nothing downstream reconciles anything.

Each lab in the canonical manifest carries its ID, slug, kind, components,
prerequisites, purpose, age-nine outcome, explanatory depth, evidence question,
power/supervision mode, applications, visual roles, domain gates, and verified
source requirements.

Two fields carry the safety model:

- `core_activity.mode` — `unpowered` | `powered_pending_physical_check` |
  `adult_led_controller_station` | `diagnostic`
- `core_activity.circuit_status` — `not_designed` | `requires_verified_circuit_data`

Neither enum has a value meaning "powered and released." A lab **cannot** declare a
live powered circuit through this schema. The safety rule is enforced by the type
system rather than by asking a model to behave.

---

## 5. What a lab must contain

The curriculum says *which* labs exist. `schemas/lab.schema.v3.json` says what a
finished lab **is** — seven blocks, none optional. A lab that misses any of them
fails validation before a reviewer ever sees it.

| Block | Holds | Enforces |
|---|---|---|
| `identity` | id, slug, kind, title, one-sentence component job | the component is the title; a problem is an application, never the organising principle |
| `pedagogy` | objectives, prior knowledge, misconceptions, vocabulary, scaffolding, cognitive load | named evidence-based methods — see `meta_prompt/pedagogy.v1.md` |
| `sequence` | engage → explore → explain → elaborate → evaluate | the 5E model, with Predict-Observe-Explain inside Explore |
| `electronics` | component spec, quantities taught, circuit, behaviour, ratings, failure modes, calculations, measurements | the electrical model — every value datasheet- or measurement-backed |
| `content` | identification, build map, troubleshooting | physical assembly, generated from the circuit |
| `safety` | mode, power profile, adult verification | separate from every child-facing section |
| `visuals` | role, source kind, supporting section, provenance | dual coding, and receipts that resolve |

Four constraints in that schema do real work, because each blocks a specific way a
lab goes wrong:

**A lab cannot be identification-only.** The schema floors the Bloom level of a
lab's objectives, at the height `pedagogy_caps.bloom_floor` sets in
`policy/calibration.v1.yaml`. Pointing at a stripe on a diode is not a lesson.

**A prediction cannot be recorded after the observation.**
`explore.predict.recorded_before_observing` is a `const true`. Recording it
afterwards is the standard way Predict-Observe-Explain gets hollowed out — with no
commitment, a surprising result produces no conflict and nothing changes.

**A powered circuit cannot ship without arithmetic.** If
`electronics.circuit.status` is `designed_verified`, both `calculations` and
`measurements` become required, and every calculation carries a
`margin_to_rating`. You cannot release a live circuit whose current was never
computed against the part's absolute maximum.

**An electrical value cannot come from memory.** Every entry in
`component_spec.parameters` and `ratings_and_limits` requires a `source`. "Vf is
about 0.7 volts" fails validation; a datasheet citation passes.

The prose companion, `prompts/component_lab_template.v1.md`, carries what a schema
cannot: tone, child-language rules, when a metaphor helps, the safety baseline in
sentences. The two are the same contract in two forms — the schema makes the
structure checkable, the template makes it writable.

## 6. One lab, start to finish

The controller walks 25 explicit states. Every arrow is a checkpoint on disk.

```
VALIDATE
   ↓
PLAN
   ↓
PLAN_REVIEW_ELECTRONICS ─┐
PLAN_REVIEW_PEDAGOGY     ├─ four isolated reviewers, no shared verdicts
PLAN_REVIEW_COMMUNICATION│
PLAN_REVIEW_GRAPHIC     ─┘
   ↓
PLAN_DECISION            ← mechanical aggregation, no model
   ↓
RESEARCH → CIRCUIT → EXPERIMENT
   ↓
CHILD_TEXT → ADULT_GUIDE
   ↓
VISUAL_PLAN → VISUAL_SOURCE_ACQUISITION → VISUAL_PRODUCTION
   ↓
ARTIFACT_CONSISTENCY     ← text vs circuit data vs visuals must agree
   ↓
QA_ELECTRONICS ─┐
QA_PEDAGOGY     ├─ four isolated reviewers again
QA_COMMUNICATION│
QA_GRAPHIC     ─┘
   ↓
QA_DECISION              ← mechanical aggregation
   ↓
LAB_PDF → PDF_RENDER → PDF_VISUAL_QA
   ↓
FINAL_ACCEPTANCE
   ↓
ACCEPTED | BLOCKED | SYSTEM_FAILURE
```

After every state the controller atomically records inputs, outputs, hashes, worker
identity, the model and effort actually executed, elapsed time, attempt number, and
the next state.

The states map onto the schema blocks: `PLAN` fixes `identity` and `pedagogy`,
`CIRCUIT`/`EXPERIMENT` fill `electronics`, `CHILD_TEXT`/`ADULT_GUIDE` write
`sequence` and `safety`, the `VISUAL_*` states fill `visuals`, and
`ARTIFACT_CONSISTENCY` checks them against one another.

Three things about this shape are load-bearing:

**Circuit before prose.** `CIRCUIT` and `EXPERIMENT` produce machine-readable data
— parts, pins, values, endpoints, nets, voltage, current limiting, ratings,
measurements, controller I/O, power sequence. Every downstream artifact (prose
steps, connection tables, maps, schematics, troubleshooting, adult checks) is
*generated from that same data*. Text and diagrams cannot drift apart because they
have one parent. That's failure A8.

**Consistency before QA.** `ARTIFACT_CONSISTENCY` runs before reviewers look at
anything, so reviewers never waste a cycle on a lab whose text and circuit already
disagree.

**PDF review is inside the loop.** `PDF_RENDER` and `PDF_VISUAL_QA` happen before
`FINAL_ACCEPTANCE`, not after. A lab that looks right as markdown and wrong at
print size is caught while revision is still cheap. That's failure A9.

---

## 7. How verdicts become decisions

Reviewers return structured records against stable check IDs. The controller — not
a model — aggregates:

```
invalid record            → reject, retry once
valid sourced safety block → BLOCKED
any failed check          → targeted revision of the named artifacts only
zero failed checks        → advance
```

"Targeted" is literal: if graphic QA fails check `VIS-03`, the controller re-runs
the visual worker for that one asset. It does not regenerate the lab. That's
failure A3.

Every terminal decision is independently audited — including revisions, blocks and
system failures, not just acceptances. V3 audited acceptances rigorously and
everything else loosely, which is how bad outcomes slipped through as "progress."
That's failure A4.

**`BLOCKED` is deliberately hard to reach.** It is legal only when a named
safety-critical fact remains unavailable after recorded official-manufacturer and
primary-source searches. A tool crash, a model timeout, a schema error, a bad
render, a layout bug — none of those are curriculum blocks. They're the system's
problem, and the system must fix them or fail honestly.

---

## 8. Reviewer independence

Four plan reviewers and four QA reviewers, each a separate bounded call. The
guarantee is structural, not behavioural: **a reviewer's authorized input paths do
not include any sibling reviewer's verdict file.** It cannot read the others
because it cannot open the files. A test fails the build if any reviewer's input
set can reach another reviewer's output.

This is gate B2, and it failed in the previous run — the requirement existed but
was never proven. "Required" and "proven" are different words here.

---

## 9. Visuals: two kinds, never mixed

Every lab plans a visual sufficiency matrix across seven roles: component
identification, purpose/application, orientation and pins, mechanism, connection or
unpowered-path map, expected result, and safety/troubleshooting. A role may be
omitted only with a documented reviewer finding.

The hard line:

| Deterministic renderer / verified photograph | ImageGen |
|---|---|
| exact components | context and setting |
| wiring and connections | mechanism illustration |
| pinouts and polarity | observation support |
| values and geometry | polish |
| safety evidence | — |

Overlays are rendered from accepted coordinates and pins, and kept separately
inspectable. **ImageGen may never substitute for missing evidence** — if the
verified photograph doesn't exist, the answer is to find it or block, not to draw
something plausible.

Every visual carries a provenance receipt: URL, manufacturer, part/family, access
date, file hash, crop/transform history, reuse. An executable check confirms the
receipt's hash matches the asset actually embedded in the rendered PDF. A receipt
that doesn't resolve to the shipped asset is a failed gate, not a warning — that's
gate B4.

---

## 10. Model routing

Routing is code, not judgment, configured under `policy/routing/`:

- **no model** — merge, validation, metrics, rendering, aggregation, hashing, audits
- **cheapest eligible route** — bounded drafting
- **stronger route** — electronics design and QA
- **maximum reasoning** — only for failed safety escalation

Runs are serial by default (`--max-concurrency 1`). Redundant drafts are
prohibited. Per-lab limits cap model calls, revisions, images, elapsed time and
storage; the controller stops *before* a limit and leaves a resumable checkpoint
rather than blowing through it.

The route actually executed is recorded — role, model, effort, sandbox policy,
elapsed time. `--model` exists as a fallback and cannot bypass the selector.

**Preflight proves capability by using it.** One real minimal structured call per
route, one real Pandoc render, before generation starts. Installed binaries, help
text and config files are not proof. That's failure A7 — and it's why the two
declared routes in this build (Pandoc for PDF, `codex exec -s workspace-write` for
workers) were chosen from recorded execution evidence rather than from what
*should* work.

---

## 11. Interruption, resume, and the action log

`--resume` validates hashes, preserves valid accepted work, restarts at the first
missing or invalid checkpoint, and refuses to mutate a fully accepted lab without a
new output version. This is tested by actually killing the run mid-lab and
restarting it, with before/after hashes recorded.

Alongside checkpoints, the controller keeps an **append-only action log**
(`test_results/prompt_execution_log.md`). Every action — inspection, file creation,
command, test, model call, render, state transition, revision, audit, resume,
terminal decision — appends one `ACT-NNN` record *before* it starts and one
completion record when it finishes. Failures append `EXEC-NNN` records with a fixed
taxonomy (`missing-input`, `bad-input`, `tool-error`, `wrong-output`,
`partial-run`, `other`).

The logger has strict rules, learned the hard way:

- a completion record takes the started action's ID as an argument and never mints
  a new one;
- the ID counter is monotonic by construction, never recovered by counting text in
  the file being written;
- appends happen under an exclusive lock and never rewrite existing records;
- if an ID can't be allocated or an append can't be proven, the run stops as
  `META_SYSTEM_FAILURE`.

**The logger is built and proven before any other artifact exists.** In the
previous run it wasn't, and a defective logger — one that derived the next ID by
counting `## ACT-` headings, so every completion minted a fresh ID instead of
closing its start — recorded the entire run with six permanently unpaired starts.
The audit trail was the thing that couldn't be audited. That's gate B1.

---

## 12. What must pass before 35 labs are authorized

In order:

| # | Gate | What it proves |
|---|---|---|
| 0 | **Logger** | append-only ordering, start/completion pairing, monotonic IDs, concurrent-append safety, failure when an operation lacks its record |
| 1 | **Static all-35** | canonical schema, L01 contradiction checks, prerequisites, orientations, visual roles, bounded prompt contracts — every *advertised* check ID backed by an *executed* assertion |
| 2 | **Deterministic** | state transitions, aggregation, block eligibility, failure classification, checkpoints, hashes, resource limits, circuit/prose/render consistency, terminal audits. **Not** selector enforcement: the routing rules are stated, owned and representable in a record a validator can check, and nothing executes them. `policy/checks.v1.yaml` records those ids `MAPPED, NOT EXECUTED` against `RT-3` and `RT-5`. |
| 3 | **Simulated all-35** | fake workers drive clean acceptance, plan and artifact revisions, malformed output, transient retry, repeated failure, legal block, system failure, interrupt/resume, then a clean L01–L35 pass |
| 4 | **Live capability** | real structured workers, real electronics review, real ImageGen, real renderer, real PDF, real page rendering |
| 5 | **Golden L01** | one complete lab, four plan reviews, four QA/PDF reviews, sources, child and adult documents, source-backed unpowered data, visuals with resolving receipts, targeted revision evidence, forced interrupt and resume, every page inspected |

Gate 1 exists because of a specific lie: the previous build's static test advertised
six checks and asserted two. Four check IDs appeared in the result record having
never executed. A meta-test now fails the build if any advertised ID has no
corresponding assertion — reporting a check as present without running it is
classified as evidence misreporting, which is a drift stop, not a bug.

Static and simulated coverage may **never** be described as generated-lab coverage.
That's failure A5, and it's the difference between "the system can handle 35 labs"
and "35 labs exist."

---

## 13. All 35, and the workbook

In `--all` mode the controller runs labs in order, advancing only after each is
accepted. Accepting L35 is **not** completion. The run then assembles the final
workbook, renders and inspects every page, runs four independent workbook reviews,
revises only workbook artifacts, and accepts only when all 35 lab acceptances,
assembly hashes, checklist entries, reviews and the final PDF pass.

Nothing may claim the curriculum is complete unless 35 live labs and the audited
final workbook actually exist.

---

## 14. The meta level: stopping a build that's going wrong

The meta run keeps its own state at `V7/test_results/meta_execution_state.json` —
goal hash, prompt hash, authorized roots, phase, revision cycle, completed and
failing gates, stable failure IDs, artifacts allowed to change, resource totals,
last measurable improvement, drift result, next action, terminal state, and the
action-log totals. Updated atomically.

The convergence loop:

```
run gate → record failures → authorize affected artifacts
   → revise → rerun affected and dependent gates
   → record measurable improvement → repeat
```

It stops as `META_DRIFT_STOP` if work leaves the authorized roots, if live L02–L35
generation starts, if tests or gates are weakened to obtain a pass, if manual
curriculum writing replaces building the generator, if evidence is misreported, if
the same failed-check set repeats twice without narrowing, if two cycles add
complexity without reducing failed gates, if revisions exceed six, or if accepted
evidence changes without reopening its gate.

Three terminal states, no others:

| State | Meaning |
|---|---|
| `META_ACCEPTED` | every release gate and drift audit passed; golden L01 accepted |
| `META_SYSTEM_FAILURE` | a required external capability stayed unavailable after bounded retry, with evidence |
| `META_DRIFT_STOP` | scope drift or bounded non-convergence detected |

Note what is *not* an external failure: implementation, prompt, schema, test,
renderer, visual and layout defects. Those require revision. You don't get to call
your own bug an act of God.

---

## 15. Reading the design backwards

Every constraint above traces to something that actually went wrong:

| Constraint | Because |
|---|---|
| bounded workers, not one big call | A1 — a monolithic run can't be checked or revised |
| checkpoint after every state | A2 — no resume meant restarting from zero |
| targeted revision outside the model | A3 — regenerating a lab to fix a caption |
| audit every terminal decision | A4 — weak audits on non-acceptance |
| never call static coverage "generated" | A5 — coverage reported as production |
| resolve base/override conflicts | A6 — L01 data contradicted its own activity |
| preflight by real execution | A7 — presence checks passed, calls failed |
| one parent for text, data and visuals | A8 — artifacts contradicting each other |
| PDF review before acceptance | A9 — inspection too late to matter |
| no "progress" without an accepted lab | A10 — activity reported as achievement |
| prove the logger before using it | B1 — a broken logger recorded a whole run |
| structural reviewer isolation | B2 — independence required but never proven |
| assert every advertised check | B3 — four checks named, never executed |
| receipt hash must match shipped asset | B4 — provenance that didn't resolve |

The system is unusually strict because it is teaching a nine-year-old to handle
electricity, and because five previous attempts produced confident output that
nobody could verify. Strictness here buys one thing: when the generator says a lab
is accepted, there is a file, a hash, an inspection and an audit behind it.
