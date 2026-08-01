# Simplification — plan v1

**Date:** 2026-07-31
**Subject:** the reviewer layer, the verification layer, and what `CIRCUIT` is allowed to do.
**Status:** proposed, not started. No file has been edited under this plan.
**Evidence:** `plans/simplification/research/conclusions.v1.md`, compiled from five
literature searches in the same directory. Every number cited below is traceable to a
report there; none of it was measured against this repository.

---

## 1. The objective, stated so it can be failed

**Stop spending effort on the parts of this design that external evidence measures as
worthless, and spend it on the parts it measures as decisive.**

The repository currently allocates its verification budget almost exactly backwards.
Twelve reviewer invocations per lab are the most expensive commitment in the design;
nine cross-family LLM judges have been measured at **2.18 effective votes**. The
`RESEARCH` state is a single step; retrieval grounding is the strongest measured
control in the entire corpus.

Four sub-objectives, in priority order:

1. **Cut.** Remove what is measured to be negative-value: eleven of twelve reviewers,
   and the meta level that builds a generator.
2. **Convert.** Move every check that can be computed out of a model's judgement and
   into code — arithmetic, readability, rule checking, hash resolution.
3. **Settle.** Get a human decision on the one question this plan cannot answer (§3).
4. **Produce.** One real lab, generated under the changed design.

**Explicit non-objective.** This plan does not improve the meta prompt. Six versions
exist and none has produced a lab. A seventh is the failure mode this plan is written
to avoid, not the work it authorises.

---

## 2. State at the time of writing

Verified 2026-07-31 by direct reading of the files named. Gate status was **not**
re-run and is not claimed.

**What is already right, and must not be disturbed.** Four choices in this repository
are independently supported by the external evidence, and three of them are the
strongest results in their respective literatures:

| Choice | Where | Support |
|---|---|---|
| circuit data is the single parent; prose derived from it | A6, A8 | Re3 built the best published contradiction detector and reported it *"contributes negligibly."* Deriving from one fixed source is one of only two mechanisms that work. |
| every electrical value carries a retrieved primary source | `architecture.v1.md:52-57` | strongest measured control found: retrieval ablation collapsed citation recall 83.48% → 60.11%; datasheet extraction reaches F1 0.92 |
| schema per block, worker writes only its block, code validates | `architecture.v1.md:13-18` | PatchBoard's three mechanisms exactly — 84.6% success at 45.5k tokens vs 30.8% at 368.3k |
| human-authored scope and sequence | `arduino_kit_curriculum.v4.yaml` | *"almost universally human-authored... the single most consistent finding across every source reviewed"* |

**What is wrong.** Six defects, in three classes. Ids are new and are referenced by
the steps in §4.

### E — Effort spent where it is measured not to work.

| # | Where | Defect |
|---|---|---|
| **E1** | `architecture.v1.md:20`, `proving.v1.md:20` | `REV-COUNT-TWELVE` mandates twelve reviewer invocations per lab. Nine cross-family judges measure at 2.18 effective votes (24.2% independence); the best single judge matched the full panel. Eleven of the twelve are paid for and unmeasurable. |
| **E2** | `meta_prompt/` whole | The meta level builds a generator. Prompt-level intervention on the closest measured benchmarks is worth **+9.4% to +15.6%** and resolves no failure category; under a matched harness, five of six multi-agent systems lost to a single agent. Separately, 13 of the 14 ids in `policy/failures.v1.yaml` carry `verified_by: RT-5`, which `policy/deferred.v1.yaml:72` records as blocked on *"no controller, logger, renderer or live route."* The design states fourteen corrections and proves one. |

### V — Verification assigned to the wrong layer.

| # | Where | Defect |
|---|---|---|
| **V1** | `QA_ELECTRONICS`, `PLAN_REVIEW_ELECTRONICS` | A model is asked to check values that are arithmetic — current, `margin_to_rating`, power against package rating, netlist-to-connection-table agreement. Programmatic verifiers beat LLM judges 1.2×–7× where a deterministic check exists. |
| **V2** | `architecture.v1.md:55-57` | `BLOCKED` requires a model to judge that a fact cannot be sourced. That is abstention, measured at **36.1%–47.4%** accuracy on multi-document inputs, with **>73% of predictions at maximum confidence**. A lab dossier is multi-document by construction. |
| **V3** | `policy/checks.v1.yaml` | No check measures reading level, and `LAB-BLOOM-DEPTH` validates a *declared field* rather than the text. Generated lesson text has been measured at FKGL 8.64–19.89 against a nine-year-old target, and Bloom consistency at 32–58% with models overshooting the requested level in 44–55% of misalignments. |

### S — Scope claimed beyond what is achievable.

| # | Where | Defect |
|---|---|---|
| **S1** | `architecture.v1.md:44-50`, the `CIRCUIT` state | `CIRCUIT` designs circuit topology. The closest published proxy — board-level schematic design from real datasheets, verified by simulation — has a top-model pass rate of **8.15%**. Structural validity runs 77–85% while functional validity runs 21–51%: circuits that look right and do not work. Omission of a current-limiting resistor is a catalogued LLM failure mode and simultaneously the canonical way a child's LED circuit overheats. |

---

## 3. The decision this plan cannot make

**Does `CIRCUIT` design circuits, or select them?**

Every step in §4 except Phase 4 holds either way. This one changes the product.

| Option | What `CIRCUIT` does | Cost |
|---|---|---|
| **(a) composed** | selects from a small library of pre-vetted, simulated circuits, one per lab, signed off once by a competent human | Removes the 8.15%. Requires someone to author and verify ~35 circuits — days of expert work that no longer happens per-run. The generator's job becomes wiring pedagogy around a circuit it did not invent. |
| **(b) created, gated** | designs topology as today, but nothing ships without ERC **and** simulation **and** named human sign-off | Keeps the current ambition. Every lab now blocks on a human electronics review, so the run is not unattended and throughput is bounded by that person. |
| **(c) created, ungated** | as today | Not supported by any evidence found. No precedent exists for autonomous safety-relevant hands-on instruction to children; the one instance located was withdrawn after telling children where to find matches and knives. |

**Recommendation: (a).** It preserves the schema, the grounding rule, the one-parent
rule and the ~4,800 lines already codified, and removes the single largest measured
risk. It is also the only option under which the unattended run remains coherent —
under (b) the human is in the loop per lab anyway.

**Two further decisions travel with it, and are for a human:**

- **Is there a named expert sign-off before a child builds anything?** Every serious
  actor found has one, including those with a commercial interest in claiming
  otherwise. `meta_prompt/meta_curriculum_builder.prompt.v6.md:8` states the goal as a
  run that *"needs nobody watching."* Both cannot hold.
- **Who is that person, and are they qualified?** Resourcing, not architecture. In the
  EU, EN 71-1 makes instructions for safe use and foreseeable misuse a compliance
  deliverable, so this is not purely editorial.

**Phase 4 does not start until (a), (b) or (c) is chosen.** Phases 0–3 and 5 do not
depend on it.

---

## 4. The work

### Phase 0 — give the external evidence somewhere to live

`policy/failures.v1.yaml` cannot hold these findings. Its own header requires each
A-series id to *"cite a path and line from `plans/legacy_v3/`"* — external research
cannot. Filing them there would corrupt the one manifest that ties every constraint to
an observed defect in this project.

Create `policy/evidence.v1.yaml` with `schemas/evidence.schema.v1.json`, carrying the
E, V and S ids from §2: the claim, the measurement, the source, its evidence strength,
and the constraint it justifies. Register it in the same pairing
`FR-P4-ALL-VALIDATE` resolves.

**Why a manifest and not a plan section:** code reads `policy/`. A constraint that
lives only in `plans/` is a constraint nothing enforces — which is the whole content
of the RT-5 finding.

### Phase 1 — cut (E1, E2)

**1a.** `REV-COUNT-TWELVE` → one judge per pass, drawn from a **different model family
than the generator**, with an explicit rubric and randomised presentation order.
Self-preference bias is measured at −38% to +90% and survives hiding authorship,
because models prefer low-perplexity text whether or not they wrote it.
`REV-ISOLATED` survives unchanged — isolation still prevents a judge reading a sibling
verdict — but the plan records what it does not buy: isolation addresses collusion,
and the measured problem is correlated error.

**1b.** Do not retire `meta_prompt/` until Phase 2 has extracted the rules that exist
nowhere else. Those are: the precedence order (`inputs.v1.md:63-89`), the recorded
divergences in `lab_brief.md` and `teacher_framework.md` (`inputs.v1.md:96-100`), the
prohibition on hardcoding a lab count (`:102-104`), the one-parent rule
(`architecture.v1.md:44-50`), the sourcing rule (`:52-57`), and
`routing.v1.md:23-25`. **Retiring the prompt before extraction destroys them** — this
is the ordering error the previous approach to this question made.

### Phase 2 — convert judgement to computation (V1, V3)

Each becomes a check id in `policy/checks.v1.yaml` with an executed assertion and a
`reject` fixture, per the existing convention.

| Check | Computes |
|---|---|
| `CALC-OHM` | current from supply and resistance; compares to the declared value |
| `CALC-MARGIN` | `margin_to_rating` from the datasheet limit and the computed value |
| `CALC-POWER` | dissipation against package rating |
| `ERC-CURRENT-LIMIT` | a current-limiting element exists on every LED branch |
| `ERC-POLARITY`, `ERC-SHORT`, `ERC-FLOATING`, `ERC-SUPPLY-MATCH` | the rule set CircuitLM reports as *"what eliminated fatal errors"* |
| `NET-TABLE-AGREES` | the connection table is a faithful projection of the netlist |
| `TEXT-READABILITY` | FKGL of child-facing prose against a band set in `policy/calibration.v1.yaml` |
| `TEXT-BLOOM-VERBS` | objective verbs against the Bloom level declared, so the label is checked against the text |

**These are testable today.** Every one operates on a `lab.json` and a `circuit.yaml`.
A hand-written fixture exercises them without a generator existing. This is the only
part of the design that can be proven before anything runs, and it should be built
first for that reason.

`TEXT-BLOOM-VERBS` carries a stated ceiling: human raters agree with each other on
Bloom level only 46.58% of the time, so this check may flag and must not block.

### Phase 3 — make the hard stops deterministic (V2)

**3a.** `BLOCKED` stops being a model verdict. The condition becomes mechanical: a
required value has no source record whose fetch succeeded and whose content hash
resolves. The model may *report* that it could not find a source; only the gate may
*conclude* it.

**3b.** Adopt fail-closed rendering. A numeric value renders as verified only when a
check resolved it; everything else renders unverified by default. Given 20–25% checker
error rates, a checker failure must be visible rather than silent. `B4` — receipt hash
must resolve to the asset embedded in the shipped PDF — is the existing special case;
this generalises it to every number.

**Recorded limitation:** the protocol this follows (Proof-Carrying Numbers) has proved
properties and **no empirical evaluation**. Adopt the shape, do not cite it as
validated.

### Phase 4 — scope (S1) — *blocked on §3*

Under (a): `CIRCUIT` becomes a selection over a vetted circuit library, and
`schemas/lab.schema.v3.json` gains a reference to the library entry plus its
simulation record. That is a new lab schema version; v3 is retained under the existing
retention rule and enters `schemas/deprecated/` only when nothing references it. Zero
accepted labs exist today, so the transition is clean now and will not be later.

Simulation as ground truth: Tinkercad Circuits covers this exact hardware. The
research found **no evidence of anyone using a simulator as a verification backend for
generated educational content** — so this is novel, and novelty here means the risk is
unquantified in both directions.

### Phase 5 — one lab

Generate L01 under the changed design and inspect it. Not a gate suite, not a
simulated pass — one lab, on paper, that a person reads.

---

## 5. How this is verified — and the structural problem in doing so

**Phases 0–2 are verifiable by this repository's existing machinery.** They are
manifest and schema changes plus executable checks over fixtures, which is what the
gate harness already does. Adding gate families runs into the same `FR-P0-REGISTRY`
constraint that `plans/fix_meta_prompt/fix_meta_prompt.plan.v1.md` §5 documents, and
that plan's recommendation (iii) — let the registry compose from several plans, each
owning its own §8 — is the prerequisite. **This plan does not duplicate that work; it
depends on it.**

**Phases 3–5 are not verifiable here.** Nothing in this repository executes a model,
renders a PDF or fetches a datasheet. Their acceptance is deferred, and each gets an
`RT-` id in `policy/deferred.v1.yaml` rather than a gate that cannot run.

**The structural problem, stated plainly.** This plan proposes changes to a
specification for a generator that has never run. Its evidence is external and applied
by argument. `conclusions.v1.md` §8 says so directly: *"nothing here was tested against
this repository."*

That makes this plan the same shape as the thing it is correcting. Six meta-prompt
versions produced a better specification and zero labs; a seventh document that
produces a better specification and zero labs is not progress because it cites
arXiv.

Two consequences follow, and they are the most important lines in this plan:

1. **Phase 2 is sequenced first among the substantive work** because it is the only
   part provable today. Executable checks over a fixture `lab.json` are real artifacts
   that either pass or fail.
2. **If Phase 5 has not produced one readable lab, no further specification work is
   authorised.** Not a v2 of this plan, not a rewrite of the meta prompt, not another
   research round. The next artifact after Phase 5 is a lab or a stop.

**Acceptance for this plan:**

1. `policy/evidence.v1.yaml` exists, validates, and every E/V/S id in §2 resolves to a
   measurement and a source.
2. Every check in Phase 2 executes against a fixture and fails the fixture built to
   break it — no id advertised without an executed assertion, per B3.
3. The rules named in Phase 1b exist outside `meta_prompt/` before anything there is
   retired, demonstrated by resolving each one from its new location.
4. §3 is answered by a human, recorded with the option chosen and the date.
5. One lab exists, rendered, read by a person, with its checks recorded.

Nothing here may be reported as satisfied by a static or simulated pass. That is
failure A5.

---

## 6. Out of scope

Rewriting the meta prompt. Building the controller. Authoring the vetted circuit
library, which is expert work that follows the §3 decision rather than preceding it.
Changing `curricula/arduino_kit/arduino_kit_curriculum.v4.yaml` — the sequence is
human-authored and the evidence says it should stay that way. The registry
generalisation, which belongs to `plans/fix_meta_prompt/`. Deciding P2, P7 or P12.
Any claim about learning outcomes: no evidence was found that an LLM-generated
multi-lesson curriculum produces sound learning in children, and this plan does not
create any.
