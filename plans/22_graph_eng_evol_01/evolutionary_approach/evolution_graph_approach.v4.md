# Evolutionary graph approach

- Version: `4.0`
- Recorded: `2026-08-10`
- Plan family: `22_graph_eng_evol_01`
- Predecessor: `plans/21_graph_engineered_subscription_execution`
- Observation basis: `plans/22_graph_eng_evol_01/previous_plan.obs.v1.md`
- Supersedes: `plans/22_graph_eng_evol_01/evolutionary_approach/deprecated/evolution_graph_approach.v3.md`
- Validation basis: Claude-agent `codex@openai-codex` `1.0.4` setup,
  adversarial-review, and native-review test recorded `2026-08-10`
- Prompt-contract scope: universal `GOAL -> TEST -> LOOP` for every
  model-facing prompt class

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
governing QA constraint. It also defines the canonical role-separated folder
structure for the Plan 22 package. It does not yet define the complete Plan 22
execution manifest or its final prompt suite. The approach-version migration is
already reflected under `evolutionary_approach/`; remaining package directories
are created only as their first authoritative artifacts are approved.

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
- `GOAL -> TEST -> LOOP` structure for every model-facing prompt, regardless
  of role or whether the prompt is one-shot;
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
- test-instruction gene: ordered checks the prompt assigns to an explicit test
  owner for its declared output;
- repair gene: failure-to-owner mapping and permitted revision scope;
- stop gene: pass, reject, pause, interrupt, or exhaustion conditions;
- internal-evaluator gene: non-decisive candidate evaluator prompts, scoring
  instructions, and counterexample instructions;
- orchestration gene: activation order, context routing, selection, and
  promotion instructions;
- complexity gene: token, node, edge, repetition, and verification budgets.

Each mutation targets one or more named genes. Candidate comparison therefore
identifies what changed instead of treating an entire rewritten prompt suite as
one opaque mutation.

The external Codex promotion rubric, output schema, severity mapping,
thresholds, regression denominator, and holdout denominator are evaluator-owned
control artifacts, not candidate genes. A candidate mutation cannot modify
them.

Expected effect: mutations become attributable, reversible, recombinable, and
easier to evaluate for causal improvement.

#### 4.2.1 Make `GOAL -> TEST -> LOOP` universal

Every model-facing prompt in the candidate, evaluator-control package, or
execution harness must compile to one normalized contract with these explicit
sections:

```text
GOAL
  prompt_id, role, one bounded objective, explicit non-goals,
  authorized inputs, output contract, completion condition

TEST
  ordered test IDs, test owner, exact criterion, required evidence,
  pass/fail rule, and authority boundary

LOOP
  failure class, repair or rejection owner, permitted change scope,
  invalidated descendants, retest order, attempt bound, and terminal state
```

The headings may be represented structurally in YAML or JSON source, but the
compiler must materialize the complete effective `GOAL`, `TEST`, and `LOOP`
contract for every prompt. A prompt may not satisfy this rule only by linking
to general instructions elsewhere. Empty, implicit, or `N/A` sections fail.

The contract applies by prompt class as follows:

| Prompt class | GOAL | TEST | LOOP |
| --- | --- | --- | --- |
| Generator or producer | One artifact or bounded decision | Exact and semantic acceptance criteria for that artifact | Targeted repair, retest order, round cap, exhaustion |
| Repair | Correct named failed criteria within an allowed diff | Original failure, allowed-field/diff, and regression retests | Return to owning evaluator; never widen scope; bounded by the owner's remaining rounds |
| Internal evaluator | Judge declared criteria without authoring content | Criterion-by-criterion evidence and structured verdict | Return pass or findings only; never repair or self-accept |
| External Codex challenge/final review | Judge the frozen review bundle under the evaluator-owned rubric | Schema, denominator, binding, and severity checks | One-shot result; findings reject the candidate or create a new candidate; never resume the review thread |
| Mutator or optimizer | Propose one attributable candidate mutation | Mutation legality, protected-dimension, complexity, and expected-fitness tests | Generate a new immutable candidate or stop at the generation bound |
| Orchestrator or coordinator | Advance legal graph state without producing semantic content | Preconditions, postconditions, guard, receipt, and state-integrity tests | Follow typed repair/rejection edges; bounded node and generation counters; honest terminal |
| Downstream media or text-generation payload | Produce the bounded payload named by its wrapper | Prompt-level payload-contract tests owned by the caller | Caller-owned repair or one-shot rejection; no output-based PNG QA |

Deterministic compilers, validators, parsers, and shell commands are tools, not
prompts, and therefore do not receive artificial `GOAL/TEST/LOOP` prose. Their
CLI contracts and automated tests remain mandatory under `tools/` and `qa/`.

For a legitimately one-shot prompt, `LOOP` must explicitly say that the prompt
cannot repair or resume itself, identify the caller that owns the next action,
and name the terminal result. “No loop” is not a valid omission.

Expected effect: every model call has a bounded purpose, a biting acceptance
test, and an executable failure path, while evaluator prompts remain unable to
repair or approve their own work.

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
- exact internal evaluator prompt IDs and internal rubric digests;
- a normalized `GOAL`, `TEST`, and `LOOP` contract plus digest for every
  model-facing prompt;
- exact graph edges, guards, repair routes, and terminals;
- exact authorized prompt inputs and context exclusions;
- exact response schemas;
- exact regression-case denominator;
- exact mutation and lineage metadata;
- exact fitness dimensions and thresholds;
- exact promotion rule;
- one canonical effective-graph digest.

Candidate evaluators receive this compiled object. They may not replace or
shrink its prompt set, internal rubric, or public regression denominator through
caller-supplied maps. The external promotion controller separately binds the
evaluator-owned gate artifacts and holdout denominator in the immutable review
bundle defined in §4.9.

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

### 4.9 Use frozen prompt corpora and schema-bound cross-family Codex review

Candidate evaluation will use three prompt-only datasets:

- **development set:** visible examples used while designing mutations;
- **regression set:** public, frozen Plan 21 and Plan 22 prompt failures that
  every promoted candidate must continue to reject; and
- **holdout set:** evaluator-owned prompt cases withheld from the generator
  until the candidate has been frozen for that evaluation attempt.

The holdout set tests instruction conflicts, ambiguity, context leakage,
authority substitution, missing mappings, false claims, overfitting, and
complexity traps. It contains no PNG grading tasks. A used holdout case may be
disclosed after scoring for audit and repair, but it then becomes regression
material and must be replaced before a later decisive evaluation.

Evaluator independence comes from the official `openai/codex-plugin-cc`
execution path: Claude Code authors the candidate, then the plugin delegates
review to the locally authenticated Codex CLI/app server in fresh Codex
threads. The plugin intentionally uses the same machine; that fact alone is not
an isolation boundary. The Claude author sandbox must lack write access to the
evaluator-control store and final receipt store. A deterministic promotion
controller outside the author session owns those stores and their signing or
append-only authority. Plan 22 does not require a separate machine, but it does
require demonstrably separate write authority. Independence means that Codex
generates the decisive review and the controller, not Claude prose, admits or
rejects its structured result.

Before either decisive review, the controller must:

1. freeze the candidate as an exact Git commit and record its commit ID, tree
   ID, prompt-package digest, and effective-graph digest;
2. freeze the evaluator rubric, public regression corpus, single-use holdout
   manifest, output schema, thresholds, and severity mapping before revealing
   the holdout cases to the review thread;
3. materialize an isolated review worktree pinned to an immutable review-bundle
   commit containing the frozen candidate and authorized evaluation artifacts;
4. record the review-bundle commit/tree, its base commit, all corpus and rubric
   digests, and a clean pre-review Git status; and
5. reject the attempt if the review worktree, `HEAD`, tree ID, or any bound
   digest changes before the result is captured.

The cross-family review protocol is:

1. The orchestrator invokes a fresh
   `/codex:adversarial-review --wait --base <frozen-base> --scope branch` with
   challenge-review focus and the frozen prompt-only rubric.
2. Codex returns a schema-validated verdict through the plugin job/result path.
   Missing fields, parse errors, missing cases, or execution failure are
   non-passing.
3. If Codex finds a Critical/High prompt defect, Claude may use the disclosed
   evidence to create a new immutable candidate. The reviewed candidate is not
   edited in place or relabeled.
4. An eligible candidate receives a second fresh
   `/codex:adversarial-review --wait --base <frozen-base> --scope branch` with
   final-acceptance focus, the same frozen rubric and denominator, and a new
   Codex thread. This second schema-bound review is decisive.
5. Native `/codex:review` may be run as supplemental advice, but its free-form
   result is never a mandatory or decisive Plan 22 verdict.

For decisive QA, Plan 22 must not use `/codex:transfer`, resume a prior rescue
thread, use native `/codex:review` as acceptance evidence, review an ordinary
mutable working tree, or provide the generator's full Claude conversation as
evaluator context. The controller must capture the raw plugin result without
rewriting it, before exposing it to the author session; hash it immediately;
parse it with the frozen schema and severity mapping; and sign or anchor the raw
result plus its content hash in the controller-owned append-only receipt store.
The author receives only a read-only copy after capture. Any mismatch between
raw output, parsed verdict, signature or anchor, and receipt fails. If separate
write authority cannot be demonstrated, the attempt fails as
`RECEIPT_AUTHORITY_UNPROVEN`.

Each receipt binds the candidate commit/tree and digests, review-bundle
commit/tree and base, rubric/schema/regression/holdout digests, pre/post Git
status, plugin version and digest, Codex CLI version, provider/auth/configuration
evidence, exact command and mode, Codex job/thread/turn identifiers, raw-result
hash, parsed verdict, timestamps, and attempt number.

The plugin must pass `/codex:setup` before review, but `ready: true` is not
sufficient subscription or provider evidence. The capability preflight must
also enforce the approved plugin and CLI versions, official OpenAI routing,
ChatGPT authentication, absence of API-key/custom-provider/custom-endpoint
overrides, and the separate subscription-only metering policy. Unproven
included-allocation or no-overage status fails closed under the retained
subscription constraint. A missing plugin, unavailable CLI, failed
authentication, malformed result, changed review target, stale binding, or
missing result is `EVALUATOR_UNAVAILABLE` or failed QA and is never replaced by
Claude self-review.

Expected effect: Plan 22 obtains independently generated, schema-bound OpenAI-
family critique against exact frozen bytes, with honest limits on same-machine
identity and tamper resistance.

### 4.10 Select by constrained Pareto improvement

A candidate is eligible for promotion only when it:

- passes all mandatory prompt-contract and graph-consistency gates;
- passes every inherited prompt regression;
- contains zero unresolved Critical/High prompt findings;
- does not use PNG QA as evidence;
- improves at least one scored fitness dimension;
- does not regress a protected dimension;
- stays within the complexity budget; and
- survives both independent schema-bound Codex reviews and holdout scoring.

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
  -> freeze candidate commit and review bundle
  -> run prompt QA
  -> run inherited regressions
  -> run evaluator-owned holdouts
  -> run two fresh schema-bound Codex reviews
  -> verify target and receipt bindings
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

### 4.12 Separate specifications, executable prompts, QA, and run state

Plan 22 will use a role-separated package instead of accumulating full plan
versions, observations, executable prompts, QA evidence, and runtime state in
one flat directory. Each artifact has one authoritative location and one
declared lifecycle:

- approach specifications explain why the design exists and how versions
  supersede one another;
- contracts and corpora provide machine-readable evaluation authority;
- node, internal-evaluator, and orchestration prompts are executable inputs;
- QA contains tests, review exports, and non-authoritative receipt copies;
- tools contain deterministic compilers, validators, and controllers;
- runs contain per-run mutable state and generated evidence; and
- deprecated approach versions remain immutable historical evidence outside
  the active navigation path.

The package root contains only the navigation index and, once authored, the two
stable execution entry points: `plan.md` and `run.prompt.md`. It must not become
a second storage location for artifacts owned by subdirectories.

Expected effect: agents load only the artifacts required for their role, old
versions do not compete with active authority, and path validation can detect
documentation/disk drift before execution.

## 5. Prompt QA gates

Plan 22 proposes the following mandatory gates over prompt artifacts.

### PG-01 — Prompt inventory exactness

The candidate contains exactly the prompts declared by the compiled prompt
graph, classified under the prompt classes in §4.2.1. The frozen evaluator-
control manifest separately contains exactly the external review prompts and
rubrics declared for the attempt. Missing, extra, duplicated, unclassified,
aliased, or caller-substituted prompts fail either inventory.

### PG-02 — Prompt digest binding

Every generator, repair, internal evaluator, mutator/optimizer,
orchestrator/coordinator, and downstream payload references the exact candidate
prompt digest. Every external review prompt references the exact frozen
evaluator-control and review-bundle digests. Stale, unbound, or cross-candidate
prompt use fails.

### PG-03 — Goal boundedness

Every model-facing prompt class named in §4.2.1 has one explicit `GOAL` with a
bounded objective, role, prompt ID, non-goals, authorized inputs, output
contract, and completion condition. A generic inherited goal or a role without
one bounded objective fails.

### PG-04 — Typed input/output contract

Every prompt declares authorized context and a response contract. Undeclared
context dependency or untyped decisive output fails.

### PG-05 — Goal/test/loop completeness

Every model-facing prompt—including generator, repair, internal evaluator,
external Codex review, mutator/optimizer, orchestrator/coordinator, and
downstream generation payload—materializes explicit `GOAL`, `TEST`, and `LOOP`
sections under §4.2.1. Tests name owners, evidence, ordered criteria, and exact
pass/fail rules. Loops map every failure to a repair, rejection, or caller-owned
route; constrain permitted changes; name invalidated descendants and retest
order; enforce an attempt or generation bound; and declare the terminal state.

One-shot evaluator and final-review prompts pass only when `LOOP` explicitly
prohibits self-repair and thread resume, returns structured pass/findings, and
routes the next action to the controller. Missing, empty, implicit, unbounded,
or `N/A` sections fail.

### PG-06 — Graph/prompt agreement

Node names, states, guards, edges, terminals, and repair routes named in prompts
must match the compiled graph exactly.

### PG-07 — Failure classification totality

Every prompt-level failure condition maps to one legal class, owner, route, and
terminal or repair behavior. Ambiguous or overlapping mappings fail.

### PG-08 — Evaluator independence

Claude may author and repair candidates but cannot mutate the frozen evaluator
rubric, schema, thresholds, severity mapping, regression denominator, or
single-use holdout denominator for an active attempt. Changing any evaluator
artifact starts a new evaluation epoch and requires all compared candidates to
be rescored. Fresh official-plugin Codex threads must generate both decisive
verdicts against the exact frozen review bundle. The promotion controller may
parse but may not reinterpret the results, and the author sandbox cannot write
the evaluator-control or receipt stores. Claude self-review,
`/codex:transfer`, a resumed authoring/rescue thread, a native-review substitute,
missing Codex execution, a fabricated or edited result, or a verdict bound to
another commit, tree, rubric, or corpus fails this gate. Missing proof of the
controller's separate write authority also fails.

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
The receipt also binds the evaluator-owned holdout manifest digest, case count,
and executed result count. Missing, caller-removed, and `NOT_RUN` regression or
holdout cases are non-passing. A disclosed holdout case must be added to the
regression corpus and replaced before a later decisive evaluation.

### PG-13 — Independent schema-bound Codex review

The candidate passes two fresh
`/codex:adversarial-review --wait --base <frozen-base> --scope branch` runs in
different Codex threads: one challenge review and one final-acceptance review.
Both use the frozen structured schema and return zero unresolved Critical/High
prompt findings. The controller verifies all bindings and confirms that the
candidate commit/tree, review-bundle commit/tree, and pre/post Git status did
not change. Native `/codex:review` output is supplemental only. Unavailable
Codex execution, malformed or unstructured output, missing or stale bindings,
target mutation, missing denominator results, or a Claude-authored substitute
verdict fails this gate.

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
- reduced overfitting through evaluator-owned, single-use holdout prompts;
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
AND evaluator-owned holdout threshold passes
AND both schema-bound Codex adversarial reviews pass
AND candidate, review-bundle, and receipt bindings verify
AND unresolved Critical/High prompt findings = 0
AND no protected fitness dimension regresses
AND complexity budget passes or has measured justification
AND the candidate makes no PNG/output-QA claim
```

If no candidate satisfies the rule within the declared generation budget, the
evolution run ends as `CONVERGENCE_EXHAUSTED`. The current champion remains
unchanged. The process must not weaken prompt gates, use PNG evidence, or relabel
an inferior candidate as promoted merely to complete the plan.

## 9. Canonical Plan 22 package structure

### 9.1 Target tree

The package will converge on this structure. The `evolutionary_approach/`
portion is already present; the remaining roles are created or migrated only
through the acceptance sequence in §9.4.

```text
22_graph_eng_evol_01/
├── README.md
├── plan.md
├── run.prompt.md
├── evolutionary_approach/
│   ├── evolution_graph_approach.v4.md
│   └── deprecated/
│       ├── evolution_graph_approach.v1.md
│       ├── evolution_graph_approach.v2.md
│       └── evolution_graph_approach.v3.md
├── observations/
│   └── previous_plan.obs.v1.md
├── contracts/
│   ├── schemas/
│   ├── policies/
│   └── manifests/
├── corpora/
│   ├── development/
│   ├── regression/
│   └── holdout_manifests/
├── prompts/
│   ├── nodes/
│   ├── repairs/
│   ├── internal_evaluators/
│   ├── optimization/
│   └── orchestration/
├── qa/
│   ├── tests/
│   ├── reviews/
│   └── receipt_exports/
├── tools/
└── runs/
    └── <run-id>/
        ├── manifest.json
        ├── state.json
        ├── log.jsonl
        ├── candidates/
        ├── work/
        ├── quarantine/
        └── outputs/
```

The tree shows reserved roles, not a requirement to create empty directories.
Directories are created when their first authoritative artifact is authored.
V4 and v1-v3 already occupy their canonical `evolutionary_approach/` paths.
This document does not claim that the other target directories already exist.

### 9.2 Authority and storage boundaries

- `README.md` is the navigation authority. It identifies the active approach,
  executable entry points, current schema/policy versions, and latest completed
  QA evidence by exact relative path.
- `plan.md` is the concise executable graph and artifact contract. It derives
  from the active approach and does not duplicate its full rationale.
- `run.prompt.md` is the thin coordinator contract. It names exact prompt,
  contract, tool, corpus, and output paths.
- `evolutionary_approach/` contains exactly one active version. Superseded
  versions move to `evolutionary_approach/deprecated/` and remain byte-immutable
  evidence.
- `observations/` contains predecessor findings and other design inputs; these
  are evidence, not executable authority.
- `contracts/` contains machine-readable schemas, policies, and frozen bundle
  manifests. Prose cannot override these at runtime.
- `corpora/development/` and `corpora/regression/` are author-visible.
  `corpora/holdout_manifests/` contains only safe-to-disclose identifiers,
  counts, and digests. Single-use holdout contents remain in the protected
  evaluator-control store defined in §4.9.
- `prompts/` separates node producers, repairs, non-decisive internal
  evaluators, optimization, and orchestration. Every file must compile to the
  universal `GOAL/TEST/LOOP` contract. The decisive external Codex rubric is
  not a candidate prompt and cannot be stored as an evolvable gene.
- `qa/` stores deterministic tests, descriptive review records, and read-only
  exports of authoritative receipts. The authoritative signed or anchored
  receipt remains in the controller-owned append-only store; a repository copy
  cannot substitute for it.
- `tools/` contains deterministic compilers, validators, parsers, and the
  promotion-controller implementation. Model prompts do not impersonate these
  tools.
- `runs/<run-id>/` contains only run-scoped mutable state, candidate instances,
  work products, quarantine, and outputs. A run references protected receipts
  by identifier and digest rather than owning their authority.

### 9.3 Naming and navigation rules

1. Directory and file names use correctly spelled lowercase `snake_case`; known
   misspellings such as `evolutionnary` and `postmorten` are prohibited.
2. Generic evidence names such as `review.md`, `result.json`, or `final.md` are
   prohibited. Names declare subject, reviewer or gate, and version or run ID.
3. Every normative cross-reference uses an exact package-root-relative path.
   Basename-only references fail when the file is not actually at the root.
4. The tree printed in `README.md` must be generated from or deterministically
   checked against disk. A documented path that does not exist fails preflight.
5. Only one active approach version may sit outside `deprecated/`. An active
   alias must resolve to exact versioned bytes and may not become a second
   independently editable copy.
6. Source/configuration artifacts never share a directory with mutable run
   state or generated outputs.
7. All prompts remain atomic and independently hashable. One file owns one
   bounded producer, repair, evaluator, optimizer, review-focus, or
   orchestration role and materializes its own `GOAL/TEST/LOOP` contract.
8. All execution manifests bind exact relative paths and SHA-256 digests. A
   move, rename, missing file, extra executable prompt, or hash change requires
   recompilation and a new candidate identity.
9. QA filenames and receipts state that the gate covers prompts only. PNG
   review artifacts are prohibited by the governing scope decision.

### 9.4 Remaining migration sequence

The approach-version move has occurred. Remaining migration and package
construction must be accepted through reviewable changes:

1. Create `README.md` with the current-to-target path map and the active v4
   declaration.
2. Record and verify the current hashes of v4 and deprecated v1-v3 at their
   canonical `evolutionary_approach/` paths.
3. Move the predecessor observation into `observations/`; do not leave an
   editable copy at the old path.
4. Update every repository reference to the new exact relative paths.
5. Create role directories only as their first artifacts are authored.
6. Run a path-integrity check proving that every documented path exists, every
   executable artifact appears exactly once, deprecated bytes match their
   pre-migration hashes, and no governing reference resolves by accident.
7. Record the migration receipt and new package digest under `qa/tests/`.

No move is complete merely because the files exist at their destinations. The
reference rewrite and deterministic path-integrity check are part of the same
acceptance unit.

### 9.5 Next design artifacts

After this approach is approved, Plan 22 should define:

1. `README.md` and the package/path-integrity schema;
2. normalized prompt-graph candidate, prompt-gene, and universal
   `GOAL/TEST/LOOP` schemas;
3. a compiler/linter that rejects every prompt missing a complete effective
   `GOAL`, `TEST`, or `LOOP` contract;
4. negative regression fixtures for each prompt class in §4.2.1;
5. candidate-lineage and prompt-only fitness schemas;
6. development, frozen regression, and single-use holdout corpus rules;
7. immutable candidate/review-bundle manifests and worktree protocol;
8. official-plugin provider/auth/metering preflight;
9. schema-bound Codex review receipt, protected append-only store, and
   deterministic verdict parser;
10. deterministic prompt-graph compiler and package validator;
11. minimal Claude-generator/Codex-reviewer/repair vertical slice;
12. candidate selection and promotion controller;
13. final expanded Plan 22 prompt graph;
14. concise executable `plan.md`; and
15. thin coordinator `run.prompt.md`.

None of these artifacts may introduce PNG QA gates unless the user explicitly
changes the governing scope decision in a later version of this approach.

## 10. V4 provenance and validation evidence

V4 retains the v3 QA corrections and adds the package structure in §9 after a
read-only comparison with:

`/Users/filipepinto/Projects/akwrk/dos/PSIM/19QMM26N0033/phase_2_conops/plans/04_evolution_graph_01`

That package demonstrated the context-efficiency benefit of separating a
governing approach, concise executable plan, coordinator prompt, atomic node
prompts, QA, postmortems, and runs. Its active harness was split into small
role-specific files rather than one execution monolith. It also demonstrated
failure modes that v4 prohibits: misspelled role directories, generic evidence
names, and a `plan.md` reference/layout that placed the active v5 approach at
the root even though the file was nested elsewhere on disk. V4 adopts the
functional separation, not those path and naming defects.

The Claude-agent test that motivated v3 used the installed
`codex@openai-codex` plugin version `1.0.4` and Codex CLI `0.147.0` against v2
without editing repository files:

- `/codex:setup` returned ready with active ChatGPT authentication;
- `/codex:adversarial-review --wait --scope working-tree` completed in Codex
  thread `019fec06-d514-7d22-9ffc-7a7512b8faf5`, returned a structured
  `needs-attention` verdict, and identified candidate-binding and evaluator-
  control defects;
- `/codex:review --wait --scope working-tree` completed in Codex thread
  `019fec08-f802-7222-aad5-67be9e3e3f2a`, but returned free-form findings with
  no decisive pass/fail field; and
- the v2 SHA-256 remained
  `e60ae886ba3cc5ebe5de99cadb742d6c3390f272b57f6bfb7b1047033a6a5d72`
  before and after the test, and Git status was unchanged.

This evidence proves that the official plugin bridge can execute both review
paths. It does not prove that v2's decisive gate was sound. V4 therefore keeps
v3's working bridge corrections: native `/codex:review` is non-decisive,
targets are frozen and exactly bound, holdouts are evaluator-owned, and
receipts are schema-bound and tamper-evident. V4 additionally makes package
paths and artifact roles deterministic. The complete v4 protocol and target
folder migration still require implementation and a vertical-slice test before
promotion.
