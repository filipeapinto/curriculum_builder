# Simplification — plan v3

**Date:** 2026-08-01
**Goal:** derive **one prompt that creates a curriculum**, generic over `curricula/<name>/`.
**Status:** proposed, not started. No file has been edited under this plan.
**Supersedes:** `simplification.plan.v2.md`. v3 changes exactly one thing: the two
human decisions v2 §4 left open are now **resolved and recorded** (§4 below), and the
in-pipeline sign-off gate that hung off decision (b) is removed. Everything else —
the objective, the leak inventory, the verifier precondition, the phase structure —
carries forward unchanged.
**Evidence:** `../research/conclusions.v1.md` and the five reports beside it.

---

## 1. The objective, stated so it can be failed

**One prompt. Given a curriculum root, it produces that curriculum. It does not know
what subject it is teaching.**

Today the design has two prompts — a meta prompt that builds a generator, and a
runtime prompt the generator was to write — and both are bound to electronics. The
target is one prompt, bound to nothing.

The test of the objective is not a document. It is this:

> The same prompt, unmodified, runs `curricula/arduino_kit/` and a second curriculum in
> an unrelated domain. Neither run edits the prompt.

Until a second curriculum runs, "generic" is a claim about a file, not a property of
one. **Phase 7 exists solely to make that claim falsifiable.**

**Explicit non-objective.** This plan does not make electronics work. It makes the
engine indifferent to electronics, and requires each curriculum to supply what makes
its own domain checkable.

---

## 2. What "generic" means, and how much of it already exists

The repository is already half-built for this, and the boundary is already stated.
`meta_prompt/assets/inputs.v1.md:12-13` draws it explicitly: `policy/calibration.v1.yaml`
holds *"the engine-wide premises... Never the supplies: those belong to one kit"*,
while `curricula/arduino_kit/kit_calibration.v1.yaml` holds *"that kit's premises"*.

That is the whole architecture, and it needs only to be finished:

| Layer | Holds | Knows about electronics |
|---|---|---|
| **engine** — `policy/`, `schemas/`, the prompt | premises, precedence, unit contract, generic checks, routing, the run | never |
| **curriculum** — `curricula/<name>/` | its manifest, its domain data, its calibration, its evidence, **its domain verifier** | entirely |

**Six places leak the domain into the engine.** Each is a defect id used by §5.

| # | Where | Leak |
|---|---|---|
| **G1** | `schemas/lab.schema.v3.json` | one of the seven required blocks is literally named `electronics`, and carries circuit, ratings, calculations and measurements. A music or chemistry unit cannot validate. |
| **G2** | `meta_prompt/assets/inputs.v1.md:10-34` | the authorized-input table names `curricula/arduino_kit/` paths directly, so the input set is one curriculum's, not any curriculum's |
| **G3** | `policy/checks.v1.yaml` | engine checks and electronics checks share one namespace — `L01-*`, `LAB-CURRENT-MARGIN`, `LAB-VALUE-SOURCED` are domain assertions living in the engine's inventory |
| **G4** | `meta_prompt/assets/component_lab_template.v1.md` | *"Component-Oriented Electronics Lab Template"* — the prose contract for a unit is written for one domain |
| **G5** | `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml`, `schemas/curriculum.schema.v4.json` | `kit_power_profile` and `visual_system` are top-level curriculum-schema concepts; "kit" and "power" are electronics words in an engine contract |
| **G6** | `policy/routes.v1.yaml` | route names are generic, but `RESEARCH` — the datasheet fetch — is described as a component-datasheet capability rather than "the domain's primary-source capability" |

**What is already generic and must not be disturbed.** `meta_prompt/assets/pedagogy.v1.md`
is domain-independent as written — 5E, Bloom, Predict-Observe-Explain, cognitive load
are teaching structure, not electronics. It transfers whole.

---

## 3. The finding that makes genericity safe

The research produced one number that governs this plan's shape: the closest published
proxy to "design a working circuit from datasheets", verified by simulation, has a
top-model pass rate of **8.15%** (`../research/safety_technical.v1.md` §3.1).

The naive reading is "electronics is too hard." The correct reading is more useful:

> **A domain is generatable exactly to the extent that it has a verifier which is not a
> model.**

Electronics has one — electrical rule checking plus simulation, ordinary code over a
netlist, reported in CircuitLM as *"what eliminated fatal errors."* A vocabulary
curriculum's verifier is a dictionary lookup. A music-theory curriculum's is an
interval checker. A curriculum with **no** verifier is one where nothing but a human
can tell whether the content is right.

So genericity and safety are the same requirement, and it becomes a startup
precondition:

> **A curriculum declares a domain verifier, and the run refuses to start without one.**
> The engine never knows what the verifier checks. It knows it must exist, must be
> code, must be executable, and must have been proven against fixtures before any unit
> is generated.

This is `S1` from v1, generalised. It also resolves the twelve-reviewer problem
without argument: reviewers were carrying a load that belongs to the verifier.

---

## 4. The decisions — resolved

v2 held phase 6 hostage to two open human decisions. Both are now taken, by the
project owner, recorded here so no run ever re-asks them.

**(a) For electronics, the domain data is composed.** Decided 2026-08-01: **composed**
— `CIRCUIT` selects from a small library of pre-vetted, simulated circuits. This was
v2's own recommendation: it removes the 8.15% failure mode, the expert work is done
once rather than per run, and it is the only option under which an unattended run
stays coherent. The curriculum declares it explicitly: `circuit_policy: composed` in
`arduino_kit_curriculum.v4.yaml`, added as part of phase 2's verifier declaration.
The created/ungated option remains rejected — no evidence supports it.

**(b) There is no in-pipeline sign-off gate.** Decided 2026-08-01: human review of the
content happens **downstream of the pipeline**, as editorial practice on the produced
artifact — it is not a run gate, not a required argument, and not a condition the run
waits on. Consequences, stated so they are not rediscovered later:

- The pipeline's output is a **draft**. Whatever review, compliance check (EN 71-1
  included) or approval the product needs happens outside this repository's runs.
- The run is fully unattended. No condition asks a person to read or sign anything.
- Nothing in this plan or its prompt may claim the output is child-ready. The claim
  the pipeline makes is "every declared automated check passed", and only that.

**Phase 6 is no longer blocked.** Nothing remains for a human to answer before it.

---

## 5. The single prompt

### 5.1 What it must carry

Ten sections. Nothing domain-specific appears in any of them.

| # | Section | Says |
|---|---|---|
| 1 | Mission | given `CURRICULUM = <root>`, produce every unit its manifest declares, then the assembled product |
| 2 | Inputs and precedence | engine premises outrank curriculum premises outrank the manifest outrank schemas outrank this prompt outrank templates outrank prose |
| 3 | What a unit is | the engine's seven blocks, one of which is the **domain block**, whose shape the curriculum supplies |
| 4 | One parent | the domain's machine-readable data is the single authority; prose, tables and diagrams are generated from it; fail closed on inconsistency |
| 5 | Grounding | every domain value carries a primary source, retrieved during the run by exact identifier, never recalled |
| 6 | The domain verifier | declared by the curriculum, executable, proven against fixtures, run before any review; **absent verifier is a startup refusal** |
| 7 | Generic checks | schema validity, readability band, Bloom verbs against declared level, cross-document derivation, receipt hash resolves in the shipped artifact |
| 8 | Review | one judge per pass, from a different model family than the generator, explicit rubric, randomised order |
| 9 | Acceptance | code decides; the output is a draft for downstream human review, outside the run (§4(b)) |
| 10 | Never hardcode | not the unit count, not the domain, not the curriculum name — read them, assert them, derive every command from them |

### 5.2 Where each section comes from

This is the derivation. Most of it already exists and is being moved, not written.

| Section | Source | Work |
|---|---|---|
| 1 Mission | new | write |
| 2 Precedence | `inputs.v1.md:63-104` | generalise `curricula/arduino_kit/` → `CURRICULUM`; carry the recorded divergences at `:96-100` |
| 3 What a unit is | `lab.schema.v3.json`, `architecture.v1.md:29-41` | G1 — split the `electronics` block out |
| 4 One parent | `architecture.v1.md:44-50` | replace "circuit and experiment data" with "the domain's data" |
| 5 Grounding | `architecture.v1.md:52-57` | replace "datasheet" with "the domain's primary-source authority" |
| 6 Domain verifier | new, from `../research/safety_technical.v1.md` §3, §7 | write |
| 7 Generic checks | new, from `../research/conclusions.v1.md` §7 and §2.1 | write |
| 8 Review | replaces `architecture.v1.md:20-27` | twelve → one; keep `REV-ISOLATED`, record that isolation addresses collusion and not correlated error |
| 9 Acceptance | `architecture.v1.md:6-11`, `routing.v1.md:23-25` | keep; record the §4(b) resolution — draft output, review downstream |
| 10 Never hardcode | `inputs.v1.md:102-104` | generalise from lab count to domain and curriculum |
| companion: unit prose | `component_lab_template.v1.md` | G4 — split generic tone and child-language rules from electronics content |
| companion: pedagogy | `pedagogy.v1.md` | none; already generic |

**What dies with the meta level, roughly 485 lines:** `proving.v1.md` (the six gates),
`deliverables.v1.md`, `logging.v1.md:28-65` (meta state, drift, terminal states),
`model_selector_prompt.v1.md`, and the main prompt's mission, write boundary, asset
table and execution order. All exist to build a generator. When nothing is being
built, they have no subject.

---

## 6. The work

**Phase 0 — prove the split.** Inventory every electronics-bound assumption in the
engine layer and confirm G1–G6 is the complete set. A gate asserts that no engine file
names a curriculum directory, and no engine check id encodes a domain term. This is
cheap, executable today, and it is what stops the split being a claim.

**Phase 1 — generalise the unit contract (G1, G5).** `lab.schema.v4.json`: six engine
blocks plus a `domain` block validated against a schema the curriculum supplies and
names. `curriculum.schema.v5.json`: `kit_power_profile` and `visual_system` become
curriculum-declared domain configuration. v3 and v4 are retained under the existing
retention rule; zero accepted labs exist, so the transition is clean now and will not
be later.

**Phase 2 — the verifier contract (§3).** A curriculum declares its verifier: entry
point, the fixtures it must reject, and its proven result. `curricula/arduino_kit/`
declares ERC — current-limit presence, polarity, shorts, floating inputs, supply match
— plus simulation, and declares `circuit_policy: composed` per §4(a). **The engine
refuses to start when the declaration is missing or its fixtures have not been
executed.**

**Phase 3 — separate the check inventory (G3).** `policy/checks.v1.yaml` keeps engine
checks. Domain checks move to `curricula/<name>/checks.v1.yaml`. Both validate against
the same schema; only the owner changes.

**Phase 4 — generic checks (V1, V3).** Readability against a band in
`policy/calibration.v1.yaml`; Bloom verbs against the declared level; cross-document
derivation; hash resolution. Each with a `reject` fixture, per the existing convention.
**These are provable today** — they operate on a unit file, so a hand-written fixture
exercises them with no generator in existence. Sequence them first among the
substantive work for that reason.

`TEXT-BLOOM-VERBS` carries a stated ceiling: human raters agree with each other on
Bloom level only 46.58% of the time. It flags; it must not block.

**Phase 5 — write the prompt (§5), then retire the meta level (E2).** In that order.
Retiring before extraction destroys the six rules that exist nowhere else — precedence,
recorded divergences, no-hardcoded-count, one parent, grounding, no-model-for-
deterministic-work. `meta_prompt/` then holds one prompt and two companions;
everything else moves to `meta_prompt/deprecated/`.

**Phase 6 — one unit.** L01 of `arduino_kit`, generated and rendered. Unblocked: §4
is resolved. The rendered unit is a draft; its human reading happens downstream,
per §4(b), and is not a condition of this phase.

**Phase 7 — the second curriculum.** A deliberately small curriculum in an unrelated
domain, with a trivially checkable verifier, run by the same prompt with no edit to it.
**This is the acceptance test for the whole plan.** Its cost is low by construction and
its evidentiary value is the entire objective.

---

## 7. How this is verified — and the structural problem in doing so

Phases 0–5 are verifiable by the existing harness: they are manifest, schema and
executable-check changes over fixtures. Adding gate families meets the same
`FR-P0-REGISTRY` constraint that `plans/fix_meta_prompt/fix_meta_prompt.plan.v1.md` §5
documents, and depends on that plan's recommendation (iii). **This plan does not
duplicate that work.**

Phases 6 and 7 are not verifiable here — nothing in this repository executes a model,
renders a PDF or fetches a source. Each gets an `RT-` id in `policy/deferred.v1.yaml`
rather than a gate that cannot run.

**The structural problem.** This plan proposes changes to a specification for a
generator that has never run, justified by evidence gathered outside it.
`../research/conclusions.v1.md` §8 states it: *"nothing here was tested against this
repository."*

That is the same shape as the thing being replaced. Six meta-prompt versions produced a
better specification and zero curricula. A seventh document that produces a better
specification and zero curricula is not progress because it cites arXiv. Two
consequences, and they bind:

1. **Phase 4 runs first among the substantive work**, because it is the only part
   provable today.
2. **If Phase 6 has not produced one readable unit, no further specification work is
   authorised** — not a v4 of this plan, not another research round. The next artifact
   after Phase 6 is a unit or a stop.

**Acceptance:**

1. G1–G6 resolved, and a gate fails if an engine file names a curriculum directory or an
   engine check id encodes a domain term.
2. Every Phase 4 check executes and rejects the fixture built to break it — no id
   advertised without an executed assertion, per B3.
3. The six rules named in Phase 5 resolve from outside `meta_prompt/` before anything
   there is retired.
4. `curricula/arduino_kit/` declares a verifier whose fixtures have been executed, and a
   curriculum without one is refused at startup, demonstrated.
5. §4(a) and §4(b) are resolved and recorded in this document, with the option and the
   date — satisfied by §4 above.
6. One unit of `arduino_kit` exists, rendered, reported as a draft per §4(b).
7. **A second curriculum in an unrelated domain runs to completion under the same
   prompt, with no edit to the prompt.**

Nothing here may be reported as satisfied by a static or simulated pass. That is
failure A5.

---

## 8. Out of scope

Building the controller. Authoring the vetted circuit library, which follows from the
§4(a) decision rather than preceding it. Changing the human-authored **sequence** in
`curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` — the evidence says it stays
that way; adding the `circuit_policy` declaration in phase 2 is a declaration, not a
sequence change, and is in scope. The registry generalisation, which belongs to
`plans/fix_meta_prompt/`. Deciding P2, P7 or P12. Any claim about learning outcomes: no
evidence was found that an LLM-generated multi-unit curriculum produces sound learning
in children, and this plan does not create any.
