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
**Amended in place, 2026-08-01.** §2 gains a seventh leak row, `G7`, and §6 phase 3
gains the sentence that retires it. The leak was found by `FR-P5-ENGINE-GENERIC` and
recorded in `simplification.phase0.result.v1.md`, which states plainly that the table
was incomplete by one. This is an amendment and **not** a v4: §7 forbids further
specification work before phase 6 produces a unit, and a plan that cannot absorb its
own measurement is the failure mode this project is named after. The amendment adds
no phase, changes no phase's meaning, and leaves §9 untouched. Two consequential
sentences move with it and nothing else does: §6 phase 0 now asks whether §2's table is
complete rather than whether a fixed range of ids is, and §7's first acceptance
criterion reads `G1`–`G7`.

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

**Seven places leak the domain into the engine.** Each is a defect id used by §5.
`G1`–`G6` were read out of the repository; `G7` was **measured** out of it by
`FR-P5-ENGINE-GENERIC` and is marked as such, because the difference between a leak
someone noticed and a leak a gate reports is the difference this plan exists to make.

| # | Where | Leak |
|---|---|---|
| **G1** | `schemas/lab.schema.v3.json` | one of the seven required blocks is literally named `electronics`, and carries circuit, ratings, calculations and measurements. A music or chemistry unit cannot validate. |
| **G2** | `meta_prompt/assets/inputs.v1.md:10-34` | the authorized-input table names `curricula/arduino_kit/` paths directly, so the input set is one curriculum's, not any curriculum's |
| **G3** | `policy/checks.v1.yaml` | engine checks and electronics checks share one namespace — `L01-*`, `LAB-CURRENT-MARGIN`, `LAB-VALUE-SOURCED` are domain assertions living in the engine's inventory |
| **G4** | `meta_prompt/assets/component_lab_template.v1.md` | *"Component-Oriented Electronics Lab Template"* — the prose contract for a unit is written for one domain |
| **G5** | `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml`, `schemas/curriculum.schema.v4.json` | `kit_power_profile` and `visual_system` are top-level curriculum-schema concepts; "kit" and "power" are electronics words in an engine contract |
| **G6** | `policy/routes.v1.yaml` | route names are generic, but `RESEARCH` — the datasheet fetch — is described as a component-datasheet capability rather than "the domain's primary-source capability" |
| **G7** | `policy/calibration.v1.yaml:9-10,15` | the engine-wide premise manifest's own header comments name one curriculum's files: the precedence rule outranks `lab_brief.md`, `teacher_framework.md`, `teacher_audit.md` and `roster.md` under `curricula/arduino_kit/` by path rather than outranking *the curriculum's* prose, and the "what is NOT here" note names `curricula/arduino_kit/kit_calibration.v1.yaml` as where the supplies went. Mild — comments, stating a rule correct in general and written in the particular — and still a binding a second curriculum falls outside of. **Measured, not read:** reported by `FR-P5-ENGINE-GENERIC` (§9) and recorded in `simplification.phase0.result.v1.md`. Retired by §6 phase 3. |

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
engine layer and confirm §2's leak table is the complete set — the table as it stands,
not a fixed range of ids, because a phase whose job is to find the leaks may not assume
their number. It found one the table did not name, and §2 now names it as `G7`. A gate
asserts that no engine file names a curriculum directory, and no engine check id encodes
a domain term. This is cheap, executable today, and it is what stops the split being a
claim.

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

**Phase 3 — separate the check inventory (G3, G7).** `policy/checks.v1.yaml` keeps engine
checks. Domain checks move to `curricula/<name>/checks.v1.yaml`. Both validate against
the same schema; only the owner changes. **In the same phase, `G7`:**
`policy/calibration.v1.yaml`'s header comments are rewritten to state precedence over
*the curriculum's* prose documents and premises rather than over four files under
`curricula/arduino_kit/` by name — the same edit in the same layer for the same reason,
which is why this phase owns it and no new phase is created for it. The rule is
generalised, never deleted, and never exempted from the gate.

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

1. G1–G7 resolved, and a gate fails if an engine file names a curriculum directory or an
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

---

## 9. Gate catalogue

This plan's own gate family. It exists because the harness now composes its registry
from several plans — `plans/fix_meta_prompt/fix_meta_prompt.plan.v1.md` §5's
recommendation **(iii)**, performed — and `tests/gates/gate_families.v1.yaml` gives
this plan the `FR-P5-` prefix and names **this section** as its catalogue.

The section number is 9 and not 8 because §8 is *Out of scope* and the harness's
section parser keys on the literal heading number. Sections 1–8 are cited by other
documents and are not renumbered.

Format: **ID** · activation phase · claim class · depends on · command · pass criteria ·
fixtures · failure meaning. **7 gates.**

**Parsing this section** — `FR-P0-REGISTRY` reads it, so the encoding is the one §8 of
`plans/folder_refactoring/folder_refactoring.plan.v6.md` fixes: everything after an em
dash in any header field is rationale for a human, and `depends_on` is the set of
backticked `FR-` ids appearing anywhere in that field.

**Activation phase 5** puts this family above the folder family's range, which ends at
4. `./tests/run_gates.sh 4` is therefore unchanged at 31 gates, and this gate is
reached only by `./tests/run_gates.sh 5`. That is deliberate: the folder plan is
finished and accepted, and its regression run must not start reporting a failure that
belongs to a different plan.

### Phase 5 — the engine/domain boundary (§6 phase 0)

**`FR-P5-ENGINE-GENERIC`** · 5 · `tree+parse+text+mapping` · depends on:
`FR-P0-HARNESS` — it needs a trustworthy harness and nothing else; it reads manifests
and files, and no earlier gate establishes anything it consumes
`python3 tests/gates/fr_p5_engine.py --check engine-generic`
**Pass:** two relations over the **engine layer** — `policy/**`, `schemas/**`, the meta
prompt named by `tests/meta_prompt_source.py`, and `meta_prompt/assets/*.md`, excluding
every `deprecated/` —
 (a) **no engine file names a `curricula/<name>/` path.** The curriculum names are the
 directories under `curricula/`, minus `deprecated/`, read at run time; the engine may
 know that curricula exist and must not know which one. This is `G2` in §2's leak
 table, and it is what makes the input set one curriculum's rather than any
 curriculum's;
 (b) **no check id declared in `policy/checks.v1.yaml` as engine-owned encodes a domain
 term.** Engine-owned is `owner` not under `curricula/`. The domain terms are **not a
 list in the gate** — a gate that hard-codes `circuit` is the leak it was written to
 detect. They are the terms a curriculum declares about itself, in the `*_terms` blocks
 of the curriculum manifests `policy/checks.v1.yaml` itself names as owners, each with
 the anchored `prose_pattern` that `FR-P3-SPLIT` and `FR-P3-NO-LITERALS` already match
 on. A declared term without a pattern is a failure, never a skip, and a run in which
 **no** curriculum declares any term fails as unmeasurable rather than passing empty.
Prints
`FR-P5-ENGINE-GENERIC <verdict> (C curricula, T declared domain terms, F engine files; (a) N files name a curriculum directory, (b) M of K engine-owned check ids carry a domain term)`.
**Fixtures:** `engine_domain_leak.reject.yaml` — a manifest that both names
`curricula/arduino_kit/` and declares an engine-owned check id carrying that kit's
vendor name; its `expected_error` is **both** codes,
`engine-check-id-domain-term + engine-names-curriculum-path`, so a fixture that trips
only one leg is `FAIL`, and each leg of the detector is proven to bite by its own code.
`engine_generic.accept.yaml` — the same shape with no curriculum path and no domain
term in any id; it must pass.
**Failure means:** the engine layer is not yet indifferent to electronics, and the
report names every file and every id that binds it. **This is a measurement, not a
regression.** The gate is expected to fail against the working tree on the day it is
written; §6 phase 0 is the inventory, and phases 1–5 are what make it pass. A green
result obtained by editing `policy/`, `schemas/` or `meta_prompt/` content ahead of
those phases destroys the measurement and is failure A5.

**What this gate does not assert.** It does not check `meta_prompt/docs/`, which
AGENTS.md declares orientation only, nor `docs/`, nor `curricula/**`, which is the
layer that is *supposed* to know its domain. It does not decide whether `G1`–`G6` is
complete — it produces the evidence §6 phase 0 needs in order to decide, and the
completeness of `G1`–`G6` is stated in the result note beside this plan, not inferred
from a green gate.

### Phase 5 — the generic checks (§6 phase 4)

Four gates, one per check §6 phase 4 names. **What they cover today is stated in each
of them and must not be over-read:** a unit is a file under `curricula/<name>/units/`,
there are none, and the executed assertion is the fixture pair. Real coverage over
generated work is `RT-7`. Reporting fixture coverage as generated-lab coverage is
failure A5.

The subject is read from the curricula directory at run time rather than from a name
written into a gate, so none of these knows which curriculum exists — the same rule
`FR-P5-ENGINE-GENERIC` follows and for the same reason.

**`FR-P5-READABILITY`** · 5 · `tree+mapping` · depends on: `FR-P0-SCHEMA` — the band is
read out of a manifest, so the manifest must be known to validate first
`python3 tests/gates/fr_p5_unit.py --check readability`
**Pass:** every unit's `child_facing_text` scores inside the band
`policy/calibration.v1.yaml` declares under `readability`, by the metric that block
names. A band and not a ceiling: text far below it is as wrong as text far above it. A
missing band is `readability-band-missing` and fails — a check with no premise is not a
check — and a unit with nothing to score is `readability-no-subject`, never a skip.
Prints `FR-P5-READABILITY <verdict> (N units scanned, band B, metric M; …)`.
**Fixtures:** `unit_readability_above_band.reject.json` — child-facing text written for
an adult; `expected_error` is `readability-out-of-band`.
`unit_readability_in_band.accept.json` — the same shape, inside the band.
**Failure means:** the generated text is not addressed to the learner
`policy/calibration.v1.yaml` describes. Both directions are defects.

**`FR-P5-BLOOM-VERBS`** · 5 · `tree+mapping` · depends on: `FR-P0-SCHEMA` — the verb
table is read out of a manifest
`python3 tests/gates/fr_p5_unit.py --check bloom-verbs`
**Pass:** the flagging machinery is present and usable — `policy/calibration.v1.yaml`
declares an ordered `bloom_verbs` table and no level lists no verbs — and every
disagreement between an objective's declared `bloom_level` and the verb that opens its
statement is **raised and recorded**. **A flag never blocks and never fails this gate.**
Human raters agree with each other on Bloom level only 46.58% of the time, so what is
asserted here is that the disagreement was reported, never that the verdict is right.
The strict check on the declared field is the schema's; this one reads the sentence.
Prints `FR-P5-BLOOM-VERBS <verdict> (N units scanned, L levels, F flags raised …)`.
**Fixtures:** `unit_bloom_verb_below_level.reject.json` — an objective declaring `apply`
whose verb is a `remember` verb, the cognitive leap a declared-field check cannot see;
`expected_error` is `bloom-verb-below-declared-level`.
`unit_bloom_verb_matches_level.accept.json` — verbs agreeing with their declared levels,
raising nothing.
**Failure means:** the table that makes the flag possible is gone, so a unit could
declare any level and nothing would read the sentence beneath it.

**`FR-P5-DERIVATION`** · 5 · `tree+mapping` · depends on: `FR-P0-HARNESS` — it reads one
unit against itself and consumes nothing an earlier gate establishes
`python3 tests/gates/fr_p5_unit.py --check derivation`
**Pass:** one parent, checked rather than asserted. Every entry of a unit's `derived`
list names a pointer into that unit's own `domain` block, that pointer resolves, and the
rendered string equals what is there. A unit that renders no fact from its domain data
is `derivation-absent` and fails: prose with no parent is the defect, not the absence of
a check. The pointer walk is strict — a segment is a mapping key or a list index and
nothing else — because a fuzzy walk lets a wrong pointer resolve to a
coincidentally-named neighbour, which is the drift this gate exists to catch.
Prints `FR-P5-DERIVATION <verdict> (N units scanned; …)`.
**Fixtures:** `unit_derivation_unparented.reject.json` — prose stating a number its own
domain data contradicts, and a pointer resolving to nothing; `expected_error` is
`derivation-value-mismatch`. `unit_derivation_one_parent.accept.json` — every rendered
fact resolving to the value it cites.
**Failure means:** a fact in the unit has a second author, which is `A6` and `A8`.

**`FR-P5-RECEIPT-HASH`** · 5 · `tree+mapping` · depends on: `FR-P0-HARNESS` — it hashes
bytes and consumes nothing an earlier gate establishes
`python3 tests/gates/fr_p5_unit.py --check receipt-hash`
**Pass:** `B4` generalised out of PDFs. Every visual's `provenance.file_hash` equals the
SHA-256 recomputed from the artifact its `embedded_as` names, resolved under the unit's
`artifact_root`. The hash is recomputed from the bytes and never trusted as recorded. A
unit shipping no receipt at all is `receipt-absent` and fails.
Prints `FR-P5-RECEIPT-HASH <verdict> (N units scanned; …)`.
**Fixtures:** `unit_receipt_unresolved.reject/` — a receipt recording a hash, an artifact
shipped, and nothing in agreement between them, which is `B4` as it was observed;
`expected_error` is `receipt-hash-mismatch`. `unit_receipt_resolves.accept/` — the same
shape whose receipt resolves.
**Failure means:** provenance that does not resolve to the shipped artifact, which
proves nothing and is recorded as a failed gate rather than a warning.

### Phase 5 — the unit contract (§6 phase 1)

**`FR-P5-UNIT-CONTRACT`** · 5 · `parse+mapping` · depends on: `FR-P0-PARSE` — it reads
two contracts as data, so they must be known to parse before their shape means anything
`python3 tests/gates/fr_p5_unit.py --check unit-contract`
**Pass:** four relations over the two contracts §6 phase 1 authors —
 (a) `schemas/lab.schema.v4.json` **states** exactly the engine's six blocks —
 `identity`, `pedagogy`, `sequence`, `content`, `safety`, `visuals` — plus `domain`,
 **requires** the same seven, and closes additional properties. The six are written into
 the gate on purpose: they are the engine's own, and only a fixed expectation catches a
 seventh arriving. `G1` was that seventh block, and it was called `electronics`. The
 property set and the required list are asserted separately, because a contract may state
 a block it does not require and an *optional* `electronics` block is `G1` exactly as much
 as a required one — reading `required` alone was how the leg came to admit it;
 (b) **no name the contract states — at any depth — is a term a curriculum declares
 about itself.** The vocabulary is the `*_terms` blocks, exactly as `FR-P5-ENGINE-GENERIC`
 reads them, so there is one declared vocabulary and not two. Its reach is the same and
 is reported the same way: the declarations are anchored for prose, so an identifier-style
 name matches only where a curriculum declared an identifier-style term;
 (c) `schemas/curriculum.schema.v5.json` carries neither `kit_power_profile` nor
 `visual_system` at the top level — `G5` — and requires a `domain` block whose `schema`
 pointer is constrained to `curricula/`, because an engine-held domain schema is the same
 leak wearing a different name;
 (d) the `domain` block of the unit contract **fixes nothing about its own contents**,
 checked as a permission list rather than as a list of refusals. The block may say that it
 is an object, that it must carry at least one property, and what it is for — `type`,
 `minProperties: 1`, `description`, `title`, `$comment` — and **any** other keyword is
 shape. Naming the leaks instead (`properties`, `required`, `$ref`, `patternProperties`,
 closed additional properties) let `allOf`, `anyOf`, `oneOf`, `not`, `propertyNames`,
 `if`/`then`, `dependentSchemas`, `enum` and `const` straight through, each of which fixes
 the block's contents just as firmly. A curriculum supplies that shape. An engine contract
 that fixed it would have re-created `G1` inside the block written to end it.
Prints
`FR-P5-UNIT-CONTRACT <verdict> (6 engine blocks plus domain, N names checked against T declared domain terms; …)`.
**Fixtures:** `unit_contract_domain_block.reject.json` — a contract requiring a seventh
block named `electronics` and stating a property carrying one kit's supply id; its
`expected_error` is **both** codes, `unit-block-named-for-domain + unit-block-set-wrong`,
so a fixture tripping one leg is `FAIL`. `unit_contract_generic.accept.json` — the six
blocks plus `domain`, and no subject named.
`unit_contract_optional_seventh_block.reject.json` — the seven required and closed, and
`electronics` stated as an *optional* eighth property, which reading `required` alone
called generic; `expected_error` `unit-block-set-wrong`.
`unit_contract_domain_constrained_sideways.reject.json` — a `domain` block carrying none
of the five keywords the old blacklist named and constraining its contents with `allOf`
and `propertyNames` anyway; `expected_error` `unit-domain-block-constrained`.
`curriculum_contract_kit_concept.reject.json`
— `G5` as it stood, `expected_error` `curriculum-schema-domain-concept`.
`curriculum_contract_generic.accept.json` — the same shape with the domain declared
rather than assumed.
**Failure means:** the unit contract still cannot describe a unit in a second subject,
so the prompt §6 phase 5 writes would be generic over a contract that is not.

### Phase 5 — the verifier precondition (§6 phase 2)

**`FR-P5-VERIFIER-REQUIRED`** · 5 · `tree+parse+mapping+execution` · depends on:
`FR-P0-SCHEMA` — the declaration is a manifest field, so the manifest must be known to
validate before its contents are executed
`python3 tests/gates/fr_p5_verifier.py --check verifier-required`
**Pass:** §3's precondition, exercised rather than stated. Every curriculum under
`curricula/` — read from the directory at run time, never by name — declares
`domain.verifier` with an entry point that exists under **its own** directory, fixtures
it must refuse each with the code it must refuse them for, at least one fixture it must
accept, and a `proven` record. Then the gate **runs the declared verifier against every
one of those fixtures** and requires each rejection to carry its declared code. A
detector that only ever accepts is not a verifier; one that rejects for the wrong reason
has stopped seeing what it was written to see; and one that refuses everything would
satisfy `must_reject` entirely, which is what `must_accept` is for. The `proven` block is
re-executed rather than believed — what it adds is the curriculum's own claim, so a
curriculum recording `not_executed` is refused before the engine spends anything on it.
Prints
`FR-P5-VERIFIER-REQUIRED <verdict> (C curricula, each declaring a verifier; N declared fixtures executed against it, each refused for its own declared code)`.
**Fixtures:** `curriculum_without_verifier.reject.yaml` — a curriculum declaring its
domain's shape and nothing that checks it; `expected_error` is `verifier-undeclared`.
`curriculum_verifier_unproven.reject.yaml` — a verifier declared and never run;
`expected_error` is `verifier-unproven`, because "declared" and "proven" are different
words and `B2` is what happens when they are treated as one.
`curriculum_verifier_declared.accept.yaml` — the shape the precondition accepts.
**Failure means:** the engine would start on a curriculum where nothing but a human or a
model can tell whether the content is right. A model checking a model's work in this
domain is the one role the evidence specifically rules out, so this is the failure that
makes genericity unsafe rather than merely incomplete.

**What this gate does not assert.** It does not judge a verifier's rules — it cannot,
and a gate that tried would be the engine learning the domain. It asserts that one
exists, that it is code, that it runs, and that it refuses what its curriculum says it
refuses. Whether those are the right rules is the curriculum's responsibility and a
human's.

### Phase 5 — the constraints `G5` moved out of the engine (§6 phase 0)

**`FR-P5-DOMAIN-CONSTRAINED`** · 5 · `tree+parse+mapping+schema` · depends on:
`FR-P0-SCHEMA` — the declaration is a manifest field, so the manifest must be known to
validate before the contract it names is resolved
`python3 tests/gates/fr_p5_manifest.py --check domain-constrained`
**Pass:** `G5` removed `kit_power_profile` and `visual_system` from the engine's manifest
contract. A constraint that leaves the engine has to arrive somewhere, and this gate is
what requires it to have arrived. Every curriculum under `curricula/` — read from the
directory at run time, never by name — declares `domain.manifest_schema`, a real JSON
Schema **under its own directory**, because an engine-held one is `G5` wearing a different
name. That contract is then validated against `schemas/manifest_domain.metaschema.v1.json`,
which requires the *shape of constraining* and names no subject term: a closed
`$defs/config` with at least one required key, and a closed `$defs/core_activity` that
requires and **enumerates** `mode` and `domain_state`. Only then is the manifest's own
content read against it — `domain.config` against `$defs/config`, every lab's
`core_activity` against `$defs/core_activity`. A curriculum whose contract accepts anything
fails the second step and never reaches the third. Prints
`FR-P5-DOMAIN-CONSTRAINED <verdict> (C curricula, each declaring a constraining manifest contract; N curriculum-declared terms enumerated, L core_activity blocks validated against them)`.
**Fixtures:** `manifest_domain_unconstrained.reject.json` — both definitions declared and
neither constraining, `config` as any object and `mode` as any string, which is what v5
did when `G5` was closed by deleting rather than relocating; `expected_error` is
`domain-unconstrained`. `manifest_domain_constrained.accept.json` — the same two
definitions, constraining, for a Latin reading curriculum, so the positive fixture also
demonstrates that nothing here is electronics.
`core_activity_mode_undeclared.reject.json` — a lab naming a `mode` its curriculum never
declared, refused as `core-activity-invalid`; under v5 as first written it passed.
**Failure means:** the engine's contract is looser than the one it replaced and calls the
looseness genericity. Moving a constraint out of the engine is this plan's intent;
dropping it is the failure this plan is named after, arriving through the schema instead
of through a gate.
