# Simplification research — compiled conclusions

Five independent literature searches, run 2026-07-31, on whether this project's
architecture is supported by evidence from outside this repository. Each search
wrote its own report in this directory; this file compiles them and states what
follows.

The question behind all five: **the generator has never run, and every constraint
in it was derived from this project's own failures. Does anyone else's evidence
agree?**

Evidence strength is carried through from the source reports: **[A]** controlled
study or peer-reviewed venue, **[B]** preprint or vendor engineering report with
numbers, **[C]** marketing or practitioner claim without measurement.

---

## 1. What was searched

| Report | Question it answers |
|---|---|
| `production_pipelines.v1.md` | who ships book- and course-scale content from an orchestrator fanning out to workers |
| `edtech_curriculum.v1.md` | does anyone autonomously generate a sequenced multi-lesson curriculum for children |
| `orchestration_patterns.v1.md` | when fan-out beats a single agent, and the documented failure taxonomies |
| `verification.v1.md` | what schema validation cannot catch, and how reliable a model reviewing a model is |
| `safety_technical.v1.md` | whether LLMs can produce correct circuits, and what governs children's electronics |

---

## 2. Where all five converge

Two findings appear in every report, reached from different literatures.

### 2.1 Model review is the weakest link, and more reviewers do not help

| Source | Measurement |
|---|---|
| Nine Judges, Two Effective Votes (arXiv 2605.29800) | 9 cross-family judges provide **2.18 effective votes** — 24.2% independence. Best single judge matched the full panel. **[B]** |
| Judging the Judges (arXiv 2602.13243) | human–LLM score agreement **69.6%**, per-model range **37.0%–87.1%** on the same rubric and materials **[A]** |
| Spatial layout verifiers (arXiv 2606.05268) | programmatic verifiers beat LLM judges **1.2×–7×**; judges *"incorrectly accept outputs that violate explicit requirements"* **[B]** |
| AutoSurvey ablation | removing the global critic loop moved quality **4.57 → 4.56** **[A]** |
| Self-preference bias (arXiv 2410.21819) | **−38% to +90%**; models prefer low-perplexity text whether or not they wrote it, so hiding authorship does not remove the bias **[A]** |
| MAST (arXiv 2503.13657) | verification failures are 23.5% of all failures, and **incorrect verification (9.1%) exceeds absent verification (8.2%)** **[A]** |
| `safety_technical.v1.md` | *"Do not use an LLM to check the LLM's circuit"* — the one role the evidence specifically rules out |

MAST's framing is the one to carry: a wrong check is worse than no check, because
it launders a defect as approved. That is gate B3 in `policy/failures.v1.yaml`,
independently rediscovered.

### 2.2 Grounding to retrieved primary sources is the strongest available control

| Source | Measurement |
|---|---|
| AutoSurvey ablation | removing retrieval collapsed citation recall **83.48% → 60.11%** **[A]** |
| Merlyn Mind | corpus restriction: **1–2%** hallucination vs **>10%** unrestricted **[B]** |
| D2S-FLOW (arXiv 2502.16540) | datasheet parameter extraction **EM 0.86, F1 0.92, entity coverage 0.96** **[A]** |
| Oak National Academy | quality degrades *"when content lacked strong ties to existing Oak resources"* **[B]** |

`safety_technical.v1.md` states it plainly: datasheet-grounded extraction *by exact
part number, retrieved rather than recalled* is **the one thing the literature says
is reliably achievable**.

**The two findings together are a budget instruction: spend on RESEARCH, not on reviewers.**

---

## 3. What the evidence validates in the current design

These are not vindications of the meta prompt. They are vindications of specific
architectural choices recorded in `policy/failures.v1.yaml` and
`meta_prompt/assets/architecture.v1.md`.

| Design choice | Repo id | External support |
|---|---|---|
| machine-readable circuit data is the single parent; prose derived from it | A6, A8 | Re3 built the best published contradiction detector and reported it *"contributes negligibly."* The only two mechanisms that work are serialising composition, or deriving everything from one fixed source. **This is the sole working approach, not merely a good idea.** **[A]** |
| every electrical value carries a retrieved primary source | `architecture.v1.md:52–57` | strongest measured control in the entire corpus (§2.2) |
| schema per block, worker writes only its authorized block, code validates | `architecture.v1.md:13–18` | PatchBoard (arXiv 2605.29313): schema authored up front + role-specific write contracts + deterministic kernel → **84.6% success at 45.5k tokens**, vs LangGraph **30.8% at 368.3k**. Same three mechanisms. **[B]** |
| typed state on disk, checkpoint, resume | A2 | *"Externalised, typed, resumable state is the one architectural choice on which every serious system agrees."* |
| workers write files and return references | dossier design | Anthropic's artifact pattern, for orchestrator context economy |
| preflight proves capability by real execution | A7 | consistent with production practice; no counter-evidence found |
| human-authored scope and sequence | `arduino_kit_curriculum.v4.yaml` | *"The sequencing layer is almost universally human-authored... the single most consistent finding across every source reviewed."* The field's most common failure is letting a model invent the progression. This repo already does not. |

---

## 4. What the evidence contradicts

### 4.1 Twelve isolated reviewers

`REV-COUNT-TWELVE` requires exactly twelve reviewer invocations. The evidence says
that buys roughly **two effective votes** at twelve times the cost.

B2's structural isolation prevents reviewers *reading each other* — collusion. The
measured problem is **correlated error**, which isolation does nothing about: nine
judges from seven different model families still collapsed to 2.18 independent
votes.

**Correction:** one judge, from a different model family than the generator, with an
explicit rubric and randomised order. Spend the recovered budget on deterministic
checks.

### 4.2 Schema validity treated as a correctness signal

*When JSON Is Not Enough* (arXiv 2607.18261) measured both on identical outputs:
**100% schema validity alongside 2.0% semantic success** in the worst case, and
**16.1% unsafe acceptances** in aggregate at 100% validity. **[B]**

`schemas/lab.schema.v3.json` guarantees a lab is shaped correctly. It does not
indicate the lab is correct. The three things it structurally cannot check —
cross-document derivation, truth of a cited source, binary asset provenance — are
categorical limits of the formalism, not gaps in this schema.

A second-order risk: *Let Me Speak Freely?* (EMNLP 2024, **[A]**) found strict
format restriction degrades reasoning, partly by forcing a conclusion field before
the reasoning that supports it. Circuit design and safety arithmetic are
reasoning-heavy. Mitigation is ordering — free-text reasoning first, structured
conclusions after — not a looser schema.

### 4.3 `BLOCKED` as a model decision

`BLOCKED` requires a model to judge that a named safety fact cannot be sourced.
That is abstention, and RefusalBench (arXiv 2510.10390) measured it: **[B]**

- single-document refusal accuracy, best model: **73.0%**
- multi-document: **36.1%** (Claude-4-Sonnet), best of any model **47.4%**
- **">73% of predictions occur at maximum confidence despite 40–69% accuracy"**
- 4,096 thinking tokens improves refusal by **<1pp**

A lab dossier is multi-document by construction. The block gate is therefore running
near coin-flip while maximally confident.

**Correction:** the hard stop must be deterministic — did the fetch succeed, does the
hash resolve — not a model's judgement that it did.

### 4.4 The unattended run

`meta_prompt/meta_curriculum_builder.prompt.v6.md` states the goal as a generator
proven *"well enough that a full run needs nobody watching."*

No system in any of the five reports operates that way, including systems whose
commercial interest is to claim they do:

- Diode Computers — DSL, machine-readable datasheets, vetted component registry,
  simulation — **"Engineers still sign off every design."**
- Oak National Academy pauses at each lesson section for teacher amendment.
- Duolingo's humans own the sequence and write the comprehension questions.
- Common Sense Media's formal recommendation: make review of AI-generated materials
  mandatory.
- Instructional Agents (EACL 2026), four autonomy levels across five real courses:
  **Full Co-Pilot scored best; Autonomous was fastest and lowest quality.** **[A]**

Documented counterexample at scale: **Odisha, June 2026 — 1,678 errors across 55
AI-assisted state school textbooks**, high-level inquiry ordered. **[A/B]**

### 4.5 Fan-out for composition

`production_pipelines.v1.md` finding 1: LongWriter ablated parallel section writing
and measured **−6% coherence**. LangChain shipped it and then removed it —
*"the reports were disjoint because the section-writing agents were not well
coordinated"* — resolving to multi-agent for research, single call for composition.

**Rule: parallelise retrieval and analysis, serialise composition.**

### 4.6 Building the generator with a meta prompt

MAST tested both prompt-level and structural interventions: workflow adjustment
**+9.4%**, task-objective verification **+15.6%**, and *"not all failure modes are
resolved."* A better orchestrator prompt is worth roughly **+10–15%** and does not
remove a failure category. **[A]**

BenchAgent (arXiv 2606.05670), the most rigorous matched-harness comparison
available: **five of six multi-agent systems lost to a matched single agent by
2.56–11.29 points while costing more.** The winning configuration was a strong
runtime harness that used agents — not a model coordinating agents. **[A]**

Anthropic's own guidance, quoted in `orchestration_patterns.v1.md`: *"Teams invest
months building elaborate multi-agent architectures only to discover that improved
prompting on a single agent achieved equivalent results."*

Separately, and independent of the literature: **13 of the 14 ids in
`policy/failures.v1.yaml` carry `verified_by: RT-5`**, and `policy/deferred.v1.yaml`
records RT-5 as blocked on *"no controller, logger, renderer or live route."* The
current two-level system states fourteen corrections and proves one (B3, via
`FR-P4-CHECK-MAPPING`).

---

## 5. The finding that determines scope

`safety_technical.v1.md` §3 is the section that should decide what this project
generates.

**HWE-Bench** (arXiv 2603.18102) — 300 board-level design tasks, 2,914 real IC
datasheets, verified by static electrical checking and circuit simulation:

> **"the top-performing model achieved an overall pass rate of 8.15%."**

Corroborating:

| Benchmark | Result |
|---|---|
| CIRCUIT (arXiv 2502.07980), GPT-4o | **48.04%** on isolated numerical answers → **27.45%** on grouped circuit unit tests |
| CircuitLM (arXiv 2601.04505v2) zero-shot | ERC structural validity **77–85%**, functional Pass@1 **21–51%** |
| Masala-CHAI (arXiv 2411.14299) | **~40% Pass@1** *after* domain fine-tuning on a purpose-built corpus |
| MMCircuitEval (arXiv 2507.19525), GPT-4v | 69.4% overall, **48.2%** on back-end design |

CircuitLM names the shape directly — the **evaluation gap**: circuits that are
structurally valid and functionally broken. Two of its catalogued LLM failure modes
are **pin hallucination** and **omission of current-limiting resistors**. The second
is simultaneously the canonical way a child's LED circuit destroys a component and
becomes hot.

The 48% → 27% collapse in CIRCUIT carries a methodological warning: spot-checking
individual claims in a generated lab will systematically overestimate whether the
lab works.

Three points from that report worth preserving verbatim in intent:

1. **The safety envelope is the easy part; the circuit is the hard part.** A model
   reliably reproduces a short constraint list it was given. Good performance on
   safety boilerplate must not be read as competence at the engineering.
2. **Low voltage is not low hazard.** The one documented children's-electronics
   recall in the report is a thermal burn at toy voltages.
3. **In the EU, the instructions are themselves regulated.** EN 71-1 makes warnings
   and instructions for safe use *and foreseeable misuse* a compliance deliverable.
   Generated instructional text sits inside a conformity-assessment boundary.

Precedent for autonomous safety-relevant hands-on instruction to children: **one**,
the FoloToy Kumma bear, which told children where to find matches and knives. It was
withdrawn and the developer's API access revoked.

---

## 6. Decisions this supports

| | Change | Basis |
|---|---|---|
| keep | codified human-authored curriculum sequence | §3 |
| keep | one parent — circuit data → prose, tables, diagrams | §3, sole working mechanism |
| keep | datasheet grounding, retrieved by exact part number | §2.2 |
| keep | typed resumable state, checkpoint per step | §3 |
| keep | schema per block + per-worker write contracts + code validation | PatchBoard |
| cut | twelve reviewers → one judge, different model family | §4.1 |
| cut | meta prompt that builds a generator | §4.6 |
| cut | `CIRCUIT` inventing topologies | §5 |
| change | `BLOCKED` from model judgement to deterministic fetch-and-hash gate | §4.3 |
| change | reasoning-bearing fields ordered free-text first, structure after | §4.2 |
| change | fan out for research; serialise composition | §4.5 |
| add | ERC — deterministic electrical rule checks over the netlist | CircuitLM: *"what eliminated fatal errors"* |
| add | simulation before ship (Tinkercad Circuits covers this exact hardware) | §5 |
| add | recompute every derivable value rather than reviewing it | §2.1 |
| add | readability (FKGL) and Bloom-verb checks on generated text | §7 |
| add | fail-closed rendering — unverified by default (PCN, arXiv 2509.06902) | §4.3 |
| add | named human sign-off recorded before a child builds a circuit | §4.4 |

### The scope change in one line

**Circuits move from created to composed** — a small library of pre-vetted,
simulated circuits, signed off once; generation wires pedagogy around a circuit it
did not invent. Everything the evidence clears for generation — 5E structure,
objectives, misconceptions, vocabulary, scaffolding, narrative, differentiation,
assessment items, restatement of a supplied safety envelope — stays fully generated.

This preserves the schema, the grounding rule, the one-parent rule and the ~4,800
lines of codified curriculum, policy and contracts already written. It removes the
8.15%.

---

## 7. Two checks the repo does not have and the evidence says it needs

**Readability.** A five-model study of physics lesson plans (arXiv 2510.19866)
measured FKGL from **8.64 to 19.89** across models on one topic. The target learner
here is nine years old. No check in `policy/checks.v1.yaml` measures reading level.
**[A]**

**Bloom level of the text, not the label.** `LAB-BLOOM-DEPTH` validates a declared
field against `pedagogy_caps.bloom_floor`. A study of 20,700 generated questions
found Bloom consistency of **32–58%**, with *"cognitive leap"* accounting for
**44–55% of misalignments** — models generate above the requested level. A lab that
declares `apply` and then writes recall content passes the current check. Note also
that human raters agreed with each other on Bloom level only **46.58%** of the time,
which limits how strict this check can defensibly be. **[A]**

---

## 8. What this research does not settle

Stated so these are not over-read.

- **HWE-Bench's 8.15% is doing heavy lifting and is a 2026 preprint.** It should be
  re-verified at publication before it is treated as settled.
- **Proof-Carrying Numbers has no empirical evaluation.** Its properties are proved;
  no deployment evidence exists.
- **Semantic binary-asset verification is immature.** The strongest published result
  is +22.2pp on 102 charts. For visuals, the defensible position remains
  hash-and-verify existence plus generating assets from declarative source so the
  derivation is re-executable — which is what B4 already requires.
- **PoLL and Nine Judges disagree** on whether judge panels help. The source report
  weights Nine Judges higher on methodology but records this as live disagreement.
- **No published system enforces "every value cites a primary source" end-to-end
  with measured results.** Financial tie-out is closest and is vendor-reported;
  DO-178C is closest in rigour and is human-executed.
- **No evidence was found of anyone using a circuit simulator as a verification
  backend for generated educational content.** If this project does that, it is
  novel — which cuts both ways.
- **Several 2026 preprints were read via automated extraction.** Re-read any table
  before a number becomes load-bearing.
- **Nothing here was tested against this repository.** These are external findings
  applied by argument, not by execution.
