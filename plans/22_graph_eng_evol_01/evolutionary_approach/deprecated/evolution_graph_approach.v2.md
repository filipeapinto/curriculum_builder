# Evolutionary graph approach

Version: `2.0`  
Recorded: `2026-08-10`  
Plan family: `22_graph_eng_evol_01`  
Predecessor: `plans/21_graph_engineered_subscription_execution`  
Observation basis: `plans/22_graph_eng_evol_01/previous_plan.obs.v1.md`

## 1. Purpose

Plan 22 will retain Plan 21's graph-engineering approach while replacing its
patch-and-review authoring cycle with an explicit evolutionary process for the
graph prompts.

The object being evolved is the **prompt graph**: its node prompts, graph
topology, typed prompt interfaces, routing instructions, evaluator prompts,
repair instructions, and orchestration prompt. Candidate prompt graphs will be
generated, compiled, evaluated, compared, selected, frozen, and promoted by
evidence.

This document proposes the strategic changes to Plan 21 and records the user's
governing QA constraint. It does not yet define the complete Plan 22 execution
manifest or its final prompt suite.

## 2. Governing user input

The following user decision is authoritative for Plan 22:

> There will be no QA gates over PNGs; QA gates will apply only to prompts.

This decision applies to both classes of PNG discussed during planning:

1. PNG page images produced by rasterizing a rendered PDF; and
2. PNG visual assets embedded in a page or document.

Accordingly:

- a PNG's appearance, relevance, semantic truthfulness, legibility, placement,
  crop, resolution, or page context will not determine prompt-candidate fitness;
- no per-PNG reviewer verdict is required;
- no rendered-page PNG review is a Plan 22 prompt-graph approval gate;
- no embedded-visual PNG review is a Plan 22 prompt-graph approval gate;
- Plan 22 will not inherit Plan 21's `PDF-VISUAL-REVIEW` or equivalent PNG
  inspection as a prompt-candidate acceptance condition;
- a candidate will not fail prompt QA because a PNG is absent, visually weak,
  semantically wrong, badly placed, illegible, or otherwise defective;
- PNG hashes, rasterization results, visual receipts, perceptual matching, and
  reviewer observations will not be scored as QA fitness dimensions.

This is a scope decision, not a claim that PNG quality is proven by prompt QA.
Plan 22 may approve a prompt graph only as a **prompt graph**. It must not infer
or report that rendered visual assets, page images, PDFs, or curricula passed
visual QA when those outputs were not gated.

## 3. Retained Plan 21 foundation

Plan 22 retains the following useful Plan 21 concepts:

- an explicit, versioned graph rather than an informal linear checklist;
- typed nodes, edges, inputs, outputs, guards, repair edges, and terminals;
- `GOAL -> TEST -> LOOP` structure for every model-bearing node prompt;
- separation of author, evaluator, controller, and orchestration roles;
- explicit context authorization instead of automatically sharing full history;
- bounded repair loops with honest exhaustion;
- deterministic compilation before candidate promotion;
- immutable candidate versions and append-only lineage evidence;
- independent evaluation rather than self-acceptance by the prompt author;
- subscription-only model invocation constraints where model execution is in
  scope;
- prompt, graph, policy, route, model-registry, and schema version binding;
- preservation of earlier failures as regression pressure;
- safe promotion: an active graph is never mutated in place.

These are retained as the architectural foundation, not inherited blindly as
the exact Plan 21 implementation.

## 4. Strategic changes from Plan 21

### 4.1 Replace sequential remediation with candidate evolution

Plan 21 repeatedly repaired one active design through v1, v2, and v3 overlays.
Plan 22 will maintain a population of immutable candidate prompt graphs.

Each candidate will declare:

- parent candidate or seed;
- mutation identifiers;
- mutation hypothesis;
- exact prompt nodes, graph edges, or contracts changed;
- expected fitness improvement;
- known trade-offs;
- complete prompt-package digest;
- evaluation corpus and evaluator versions;
- measured fitness vector;
- selection or rejection disposition.

A rejected candidate remains frozen evidence. Its useful mutations may be
recombined into a later candidate, but the rejected bytes are never relabeled
as passing.

Expected effect: failed ideas become learning data, while successful prompt
changes have an explicit lineage and measured reason for promotion.

### 4.2 Define a prompt-graph genome

The evolvable genome will consist of normalized, addressable genes rather than
an undifferentiated Markdown package.

Proposed gene classes are:

- graph topology gene: nodes, edges, allowed loops, entry, and terminals;
- node-role gene: author, evaluator, optimizer, controller, or orchestrator;
- goal gene: one bounded objective and explicit non-goals;
- input-context gene: permitted source identifiers and exclusions;
- output-contract gene: expected structured prompt response;
- test-instruction gene: checks the node asks an evaluator to apply to prompt
  content;
- repair gene: failure-to-owner mapping and permitted revision scope;
- stop gene: pass, reject, pause, interrupt, or exhaustion conditions;
- evaluator gene: Codex review rubric, scoring method, counterexample
  instructions, and cross-family review requirements;
- orchestration gene: activation order, context routing, selection, and
  promotion instructions;
- complexity gene: token, node, edge, repetition, and verification budgets.

Each mutation targets one or more named genes. Candidate comparison therefore
identifies what changed instead of treating an entire rewritten prompt suite as
one opaque mutation.

Expected effect: mutations become attributable, reversible, recombinable, and
easier to evaluate for causal improvement.

### 4.3 Begin from the Plan 21 failure corpus

The Plan 21 observations are the initial environmental pressure for Plan 22.
Every prompt-relevant Critical/High witness becomes a fixed regression case.

The inherited prompt corpus will include cases for:

- contradictory or incomplete instructions;
- declarations that lack an executable owner;
- self-accepting evaluator instructions;
- caller-controlled denominators presented as compiler-owned;
- base/overlay inconsistencies;
- missing status, guard, edge, or continuation propagation;
- ambiguous failure classifications;
- unbounded or non-convergent repair loops;
- prompt instructions that authenticate bytes without establishing meaning;
- prompt instructions that validate components but omit composition;
- prompt claims stronger than the evidence the prompt requests;
- stale or mutable environment facts embedded as constants;
- duplicated authority across orchestrator, controller, node, and evaluator;
- excessive re-verification and prompt surface area;
- hidden context access and sibling-verdict leakage;
- instructions that permit simulated, prewritten, or substituted evidence;
- active-candidate editing rather than immutable promotion.

PNG-specific failure cases are excluded from the Plan 22 QA corpus by the
governing user input. A prompt candidate is not evaluated on the quality of a
PNG it might eventually produce.

Expected effect: Plan 22 starts with accumulated selection pressure rather than
rediscovering Plan 21's prompt-design failures.

### 4.4 Build a minimal prompt-graph vertical slice first

Plan 21 expanded a complete P0-P6 system before foundational composition was
proven. Plan 22 will first evolve a minimal prompt graph containing:

1. one bounded generator prompt;
2. one independent prompt evaluator;
3. one targeted prompt-repair edge;
4. one pass edge;
5. one honest exhaustion edge;
6. one immutable candidate record; and
7. one promotion decision.

The minimal slice must demonstrate candidate creation, compilation, prompt QA,
targeted mutation, reevaluation, comparison, rejection, and promotion before
the graph expands.

The vertical slice evaluates prompt artifacts only. It does not render or grade
PNG outputs.

Expected effect: evolutionary mechanics and promotion authority are tested
before a large graph prompt suite is authored.

### 4.5 Compile one normalized effective prompt graph

Plan 21 validated bases and overlays without always materializing one effective
runtime authority. Plan 22 will compile every candidate into one normalized,
immutable effective prompt graph.

The compiled candidate will contain:

- exact node prompt IDs and prompt digests;
- exact evaluator prompt IDs and rubric digests;
- exact graph edges, guards, repair routes, and terminals;
- exact authorized prompt inputs and context exclusions;
- exact response schemas;
- exact regression-case denominator;
- exact mutation and lineage metadata;
- exact fitness dimensions and thresholds;
- exact promotion rule;
- one canonical effective-graph digest.

Candidate evaluators receive this compiled object. They may not replace or
shrink its prompt set, rubric, regression denominator, or thresholds through
caller-supplied maps.

Expected effect: the prompt graph evaluated is exactly the prompt graph being
compared and promoted.

### 4.6 Separate prompt-authoring fitness from output quality

Plan 22 will make the evaluation boundary explicit:

```text
in scope for QA                       outside Plan 22 QA
-----------------------------------   ------------------------------------
prompt clarity and completeness       PNG visual quality
graph/prompt consistency              rendered-page appearance
typed prompt interfaces               visual semantic correctness
context minimization                  visual placement or cropping
failure and repair instructions       print legibility observed in a PNG
evaluator independence                PDF/PNG asset correspondence
regression-prompt performance         aesthetic judgment
complexity and efficiency             rendered curriculum acceptance
```

Prompt QA may verify that a prompt clearly asks a downstream actor to do
something. It may not treat that instruction as evidence that the downstream
PNG is correct.

Expected effect: Plan 22 makes a narrower but honest claim and does not confuse
prompt quality with rendered-output quality.

### 4.7 Use multi-objective prompt fitness

Each candidate receives a fitness vector rather than one opaque pass score.

Proposed prompt-only dimensions are:

1. **Contract completeness** — all required prompt fields, roles, inputs,
   outputs, tests, repair routes, and stop conditions are present.
2. **Graph consistency** — prompt instructions agree with the compiled nodes,
   guards, edges, state names, and terminals.
3. **Instruction precision** — obligations and prohibitions are testable and do
   not depend on undefined terms.
4. **Context discipline** — each node receives only declared prompt context and
   cannot depend on hidden sibling material.
5. **Evaluator independence** — a generator cannot accept its own prompt or
   control the decisive rubric.
6. **Adversarial robustness** — prompt mutations, conflicting instructions,
   omitted requirements, and substitution attempts are rejected.
7. **Repair locality** — a failed criterion maps to one prompt gene or owned
   node rather than broad regeneration.
8. **Regression retention** — every applicable inherited prompt failure remains
   rejected.
9. **Process efficiency** — prompt tokens, node count, edge count, repeated
   instructions, repeated evaluations, and unnecessary repair paths are
   minimized.
10. **Claim honesty** — conclusions do not exceed prompt-level evidence and do
    not imply PNG/output QA.

No fitness dimension will score PNGs or conclusions derived from PNG review.

Expected effect: selection rewards robust, comprehensible prompt graphs without
letting specification growth masquerade as improvement.

### 4.8 Introduce mutation operators tailored to graph prompts

Plan 22 will use bounded mutation operators such as:

- clarify one ambiguous obligation;
- add or remove one explicit non-goal;
- narrow one node's context inputs;
- split a prompt with conflicting roles into atomic nodes;
- merge redundant nodes whose contracts are identical;
- add a missing failure or exhaustion edge;
- replace prose routing with one typed guard;
- bind one response field to a schema;
- strengthen evaluator independence;
- convert broad regeneration into targeted repair;
- remove duplicated verification;
- reduce token volume without reducing regression performance;
- introduce one adversarial counterexample instruction;
- repair a base/effective-prompt inconsistency;
- remove an unsupported claim about runtime or rendered outputs.

Forbidden mutation operators include:

- weakening a fixed prompt regression to obtain a higher score;
- deleting a required prompt criterion without an approved scope change;
- editing the active promoted candidate in place;
- importing a PNG assessment as prompt fitness evidence;
- rewarding a candidate for visual/output claims not evaluated by Plan 22;
- changing multiple unrelated prompt genes without attribution.

Expected effect: evolution explores useful variation while maintaining causal
traceability and the user-defined QA boundary.

### 4.9 Use public prompt corpora and official cross-family Codex review

Candidate evaluation will use two prompt-only datasets:

- **development set:** visible examples used while designing mutations; and
- **regression set:** public, frozen Plan 21 and Plan 22 prompt failures that
  every promoted candidate must continue to reject.

Plan 22 does not require secret holdouts. Evaluator independence comes from the
official `openai/codex-plugin-cc` execution path: Claude Code authors the
candidate, then the plugin delegates review to the locally authenticated Codex
CLI/app server in a separate Codex thread. The plugin intentionally uses the
same machine and repository checkout; that shared checkout is not treated as an
isolation defect or as evidence leakage.

The cross-family review protocol is:

1. Claude writes a candidate prompt graph and the deterministic compiler emits
   one immutable effective-candidate digest.
2. The orchestrator invokes `/codex:adversarial-review --wait` for a fresh,
   read-only Codex challenge review focused on the exact candidate and the
   frozen prompt-regression corpus.
3. Codex returns the review through the plugin's own job/result path. Claude
   does not impersonate Codex, fabricate a substitute verdict, or convert a
   failed/malformed Codex run into a PASS.
4. If Codex finds a Critical/High prompt defect, Claude uses the reported
   evidence to create a new immutable candidate. The reviewed candidate is not
   edited in place or relabeled.
5. A candidate eligible for promotion receives a fresh `/codex:review --wait`
   final read-only review. When the optional plugin stop-review gate is used,
   any reported issue blocks completion until a new candidate is reviewed.

For decisive QA, Plan 22 must not use `/codex:transfer`, resume a prior rescue
thread, or provide the generator's full Claude conversation as evaluator
context. Codex receives the repository candidate, frozen regression artifacts,
and explicit review focus through the plugin's normal review command. A review
receipt binds the candidate digest, effective-graph digest, regression-corpus
digest, Codex thread/job identifier, review command/mode, model/config evidence,
structured verdict hash, and attempt.

The plugin itself must pass `/codex:setup` before review. A missing plugin,
unavailable Codex CLI, failed Codex authentication, malformed result, a review
that is not read-only, stale candidate binding, or missing result is an honest
`EVALUATOR_UNAVAILABLE`/failed-QA outcome. It is never replaced by Claude
self-review.

Expected effect: Plan 22 obtains an independent OpenAI-family critique through
the supported Claude-to-Codex bridge without inventing container, separate-OS-
identity, or private-holdout requirements that the plugin does not claim.

### 4.10 Select by constrained Pareto improvement

A candidate is eligible for promotion only when it:

- passes all mandatory prompt-contract and graph-consistency gates;
- passes every inherited prompt regression;
- contains zero unresolved Critical/High prompt findings;
- does not use PNG QA as evidence;
- improves at least one scored fitness dimension;
- does not regress a protected dimension;
- stays within the complexity budget; and
- survives independent Codex adversarial and final review.

Among eligible candidates, selection prefers the Pareto-optimal candidate with
the smallest normalized prompt graph. A larger candidate must demonstrate a
measured benefit that cannot be obtained by a smaller equivalent.

Expected effect: the evolutionary process produces strict evidence-backed
improvement rather than accumulating addenda.

### 4.11 Freeze promotion and lineage

The evolutionary lifecycle is:

```text
seed
  -> mutate named genes
  -> compile effective prompt graph
  -> run prompt QA
  -> run inherited regressions
  -> run independent Codex adversarial review
  -> calculate fitness vector
  -> compare with parent/champion
  -> reject or promote
  -> freeze candidate and lineage record
```

An active run is pinned to one promoted prompt-graph digest. Evolution happens
offline and cannot alter an in-progress run. Resume, if later introduced into
the execution design, returns to the same pinned prompt graph.

Expected effect: selection is reproducible, candidate identity is stable, and
prompt evolution cannot silently change active semantics.

## 5. Prompt QA gates

Plan 22 proposes the following mandatory gates over prompt artifacts.

### PG-01 — Prompt inventory exactness

The candidate contains exactly the prompts declared by the compiled prompt
graph. Missing, extra, duplicated, aliased, or caller-substituted prompts fail.

### PG-02 — Prompt digest binding

Every node and evaluator references the exact candidate prompt digest. Stale or
cross-candidate prompt use fails.

### PG-03 — Goal boundedness

Every node has one bounded goal, explicit non-goals, and a defined completion
condition.

### PG-04 — Typed input/output contract

Every prompt declares authorized context and a response contract. Undeclared
context dependency or untyped decisive output fails.

### PG-05 — Goal/test/loop completeness

Every model-bearing prompt has a goal, prompt-level tests, targeted repair
instructions, retest order, convergence bound, and exhaustion disposition.

### PG-06 — Graph/prompt agreement

Node names, states, guards, edges, terminals, and repair routes named in prompts
must match the compiled graph exactly.

### PG-07 — Failure classification totality

Every prompt-level failure condition maps to one legal class, owner, route, and
terminal or repair behavior. Ambiguous or overlapping mappings fail.

### PG-08 — Evaluator independence

Claude may author and repair candidates but cannot write, replace, edit, or
reinterpret the decisive Codex verdict. A fresh official-plugin Codex review
thread must inspect the exact digest-bound candidate in read-only mode and
return its result through the plugin job/result path defined in §4.9. Claude
self-review, `/codex:transfer`, a resumed authoring/rescue thread, missing Codex
execution, a fabricated/substituted verdict, or a verdict bound to another
candidate fails this gate.

### PG-09 — Context noninterference

Adding an unauthorized sibling prompt, verdict, or hidden context item cannot
change a node's permitted evaluation result.

### PG-10 — Adversarial instruction robustness

Conflicting embedded instructions, prompt injection, authority substitution,
denominator shrinking, and “fixed elsewhere” waivers fail.

### PG-11 — Repair locality

A failing criterion identifies one owned prompt gene or graph element. Repair
cannot broadly rewrite accepted siblings without a declared dependency reason.

### PG-12 — Regression completeness

Every applicable inherited prompt-regression identifier has an executed result.
Missing and `NOT_RUN` regressions are non-passing.

### PG-13 — Independent Codex review

The candidate passes a fresh `/codex:adversarial-review --wait` and final
`/codex:review --wait` with zero unresolved Critical/High prompt findings. The
review receipts bind the exact candidate, effective graph, regression corpus,
Codex job/thread, command mode, configuration evidence, verdict, and attempt.
Unavailable Codex execution, malformed output, missing/stale bindings, or a
Claude-authored substitute verdict fails this gate.

### PG-14 — Complexity budget

Prompt tokens, duplicated clauses, node count, edge count, verification count,
and repair-path count remain within the declared budget or show a measured
fitness justification.

### PG-15 — Claim boundary

Candidate conclusions accurately state that QA covered prompts only. Any claim
that PNGs, rendered pages, visual assets, PDFs, or curriculum outputs passed QA
fails this gate.

## 6. Explicitly excluded QA gates

The following are not Plan 22 gates under the governing user input:

- PNG page inspection;
- PNG visual-asset inspection;
- rasterized PDF visual review;
- per-page relevance or semantic-truth review;
- per-image subject visibility or correctness review;
- crop, bounding-box, placement, layout, resolution, or aesthetic review;
- perceptual comparison between source images and embedded images;
- PNG legibility, contrast, clipping, or blankness assessment;
- reviewer verdicts bound to PNG hashes;
- image-generation output grading;
- approval or rejection derived from any PNG's contents.

Plan 22 must not silently reintroduce these under a different label such as
“artifact quality,” “visual truth,” “page fitness,” or “render acceptance.”

## 7. Expected outcomes

If the proposed approach works as intended, Plan 22 should produce:

- a smaller and more inspectable effective prompt graph;
- explicit lineage from Plan 21 prompts to candidate mutations;
- permanent retention of prompt-relevant Plan 21 failures;
- measurable comparison rather than repeated subjective rewriting;
- less base/addendum divergence;
- less duplicated authority between node, evaluator, and orchestrator prompts;
- earlier detection of contradictory or incomplete prompt contracts;
- reduced author blind spots through independent cross-family Codex review;
- targeted prompt repair instead of whole-package regeneration;
- reproducible candidate promotion and rollback;
- an honest approval claim limited to prompt quality.

The approach is **not expected** to prove:

- that generated PNG visual assets are correct;
- that rendered pages are legible or well composed;
- that visuals are relevant, truthful, or correctly placed;
- that a PDF or curriculum is visually ready for release;
- that strong prompts necessarily produced strong visual outputs.

Those outcomes are outside the QA boundary chosen for Plan 22.

## 8. Proposed promotion rule

A Plan 22 candidate becomes the champion prompt graph only when:

```text
all mandatory prompt gates pass
AND all inherited prompt regressions pass
AND independent Codex adversarial and final reviews pass
AND unresolved Critical/High prompt findings = 0
AND no protected fitness dimension regresses
AND complexity budget passes or has measured justification
AND the candidate makes no PNG/output-QA claim
```

If no candidate satisfies the rule within the declared generation budget, the
evolution run ends as `CONVERGENCE_EXHAUSTED`. The current champion remains
unchanged. The process must not weaken prompt gates, use PNG evidence, or relabel
an inferior candidate as promoted merely to complete the plan.

## 9. Proposed next design artifacts

After this approach is approved, Plan 22 should define:

1. a normalized prompt-graph candidate schema;
2. a prompt-gene and mutation schema;
3. a candidate-lineage record;
4. a prompt-only fitness schema;
5. the inherited prompt-regression corpus;
6. development and public frozen regression-corpus rules;
7. an official-plugin capability preflight and Codex review-receipt schema;
8. a deterministic prompt-graph compiler;
9. a minimal Claude-generator/Codex-reviewer/repair vertical slice;
10. the candidate selection and promotion controller; and
11. the final expanded Plan 22 prompt graph.

None of these artifacts may introduce PNG QA gates unless the user explicitly
changes the governing scope decision in a later version of this approach.
