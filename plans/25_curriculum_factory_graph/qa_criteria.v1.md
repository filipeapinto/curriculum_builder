# Curriculum Factory Graph v1 — QA criteria

## Verdict rule

Evaluate the complete `plans/25_curriculum_factory_graph/` package and, when a run is
claimed, the actual output root. The package passes only if it defines one closed,
manifest-expanded, executable graph whose successful products are accepted curriculum
artifacts. Promises, filenames, diagrams, prompt prose, and self-reported readiness
are not evidence that a condition holds.

One blocking finding fails the package. A finding must name the criterion, exact
artifact/section or runtime evidence, trigger, and operational consequence.

## Package structure and product boundary

1. **Exact package** — The package contains the four required top-level Markdown files
   and exactly the eight required prompt files. Every graph/prompt reference resolves;
   no hidden phase, generic-worker, graph-construction, routing, validation,
   acceptance, or release prompt exists.
2. **Factory identity** — `curriculum_factory.graph.v1.md` is itself the factory
   authority: it declares executable inputs, outputs, state, nodes, edges, guards,
   context, reducers, joins, loops, repairs, checkpoints, terminals, and acceptance.
   It does not make later factory construction the workload.
3. **Curriculum product only** — The sole successful outcomes are the accepted
   requested unit or accepted complete workbook. The graph must be rejected if a plan,
   graph specification/candidate, prompt, prompt score, completed work phase,
   capability probe, simulation, visualization, QA record, or review report can satisfy
   success without accepted curriculum bytes.
4. **Historical separation** — Plans 23 and 24 remain untouched and are referenced
   only as rejected historical abstractions. No Plan 23 evolution/promotion route or
   Plan 24 phase dependency is an execution edge.

## Graph closure and authority

5. **Immutable identity** — Run identity binds graph, engine/curriculum contracts,
   manifest, output root, run mode, limits, and executable bytes. Resume cannot alter
   identity inside an existing root.
6. **Typed state and reducers** — Every node read/write has a declared typed field and
   controller reducer. Write-once, append-only, version, monotonic status/counter,
   join, acceptance, and terminal semantics fail closed on collision or rollback.
7. **Node closure** — Every node is reachable where intended and appears in the node
   catalogue, state access, execution edge, applicable context definition, and failure
   routing. There are no dangling, implicit, filename-ordered, or prose-only edges.
8. **Deterministic authority** — Input/manifest validation, expansion, routing
   application, transitions, schema/verifier/check execution, source admission,
   hashing, joins, reducers, counters, repair routing, rendering commands, page
   inventory, acceptance, checkpoint/resume, workbook assembly/coverage, audit, and
   terminal decisions are controller nodes. A model cannot control any of them.
9. **One prompt per model job** — Exactly eight model nodes exist and each names exactly
   one matching prompt: source research, domain creation, content writing, visual
   creation, unit review, unit repair, workbook review, workbook repair. No deterministic
   node has or requires a prompt.
10. **Routing containment** — Every model activation has a validated prior route
    decision, observed executed identity, isolated authorized reads, and one declared
    writable result. Mismatch, extra write, escape, malformed output, or undeclared
    context prevents state mutation.

## Manifest expansion and execution

11. **Manifest authority** — Unit IDs, count, order, prerequisites, subject, domain
    schema/config/verifier, checks, and visual roles derive from the validated supplied
    manifest and curriculum contracts. Any engine-graph hardcoding of a curriculum,
    unit identifier, count, or subject fails.
12. **Unit selection** — Single-unit mode proves the requested manifest unit is legal.
    Full mode advances in manifest order and never activates a later unit before the
    current required unit is accepted. Accepting the last unit alone cannot complete a
    full run.
13. **Fan-outs and joins** — Research and visual denominators are frozen before
    dispatch. Joins use run, unit, denominator, and member correlation keys and reject
    missing, duplicate, stale, failed, extra, or cross-unit members.
14. **Guard exclusivity** — Each conditional edge has a code-owned mutually exclusive
    guard. No model recommendation, filename order, conversation order, or report text
    activates a node.

## Context graph

15. **Adjacency is not context** — The package separates execution edges from context
    edges. No model receives full conversation history, repository-wide reads, sibling
    artifacts, hidden tests, terminal intent, or controller authority.
16. **Exact model contexts** — Source research sees one question and allowed retrieval
    results; domain creation sees manifest unit/admitted sources/domain contracts and
    calibration; writing sees accepted domain/engine contracts; visual creation sees one
    brief and parent facts; unit review sees the frozen actual unit/PDF/all pages without
    author history or sibling verdicts; repairs see named findings and owned boundaries;
    workbook review sees actual workbook/all pages/frozen rubric; workbook repair sees
    workbook defects and immutable unit hashes.
17. **Review independence** — Every required unit/workbook review activation is
    structurally isolated; unit review uses a different model family from the generator
    wherever active policy requires it. Review denominators derive from frozen active
    checks/rubrics, bind exact artifact/PDF/page/rubric hashes and randomized
    presentation order, and expose no sibling verdict or aggregate/terminal authority.

## Actual curriculum QA

18. **Complete unit denominator** — Unit acceptance requires current, exact results for
    source grounding, domain schema/verifier, engine and curriculum checks, one-parent
    derivation, claim entailment, pedagogy/readability, safety, visual roles/assets,
    receipt/hash resolution, render/page inspection, independent review, repairs,
    retests, logs, and checkpoint. Missing, stale, duplicate, invalid, failed, or
    `NOT_RUN` blocking evidence prevents acceptance.
19. **Actual visuals** — Declared roles resolve to shipped visual bytes and provenance.
    Exact technical authority uses deterministic renders. A visual brief, description,
    prompt, or receipt without resolving artifact bytes does not pass.
20. **Actual unit pages** — The exact shipped unit PDF is rasterized and every page
    enters a positive contiguous denominator. Each page receives deterministic and
    declared review coverage. Sampling, re-render substitution, successful rasterization
    alone, or review of source Markdown alone cannot establish product quality.
21. **Review of output, not prompts** — Unit/workbook review examines actual frozen
    structured artifacts, actual visuals, actual shipped PDFs, and every rendered page.
    Prompt quality is never used as curriculum-quality evidence.
22. **Exact workbook coverage** — Assembly requires accepted IDs and hashes equal the
    ordered manifest exactly. Partial, pending-review, missing, changed, duplicate,
    extra, or out-of-order units prevent assembly acceptance and `COMPLETE`.
23. **Actual workbook pages and review** — Every page of the exact shipped workbook is
    rasterized, hashed, inspected, and independently reviewed under the frozen rubric.
    The workbook cannot pass from concatenation, page count, or nonblank checks alone.
24. **Independent release recomputation** — Final audit recomputes identity, hashes,
    denominators, transitions, accepted coverage, review bindings, repairs, page
    coverage, and terminal guard from raw records without trusting prior controller
    aggregate fields.

## Repair and resume

25. **Unique targeted repair** — Every repairable check maps before execution to one
    artifact owner, exact allowed change boundary, immutable parent, new version,
    invalidated descendants, retest order, numeric maximum, and exhaustion route.
    Ambiguous, broad, in-place, or self-approved repair fails.
26. **Minimal invalidation** — A local defect reactivates only its invalidated
    descendants in topological order. Unaffected artifacts retain their hashes. A local
    defect cannot regenerate an entire unit.
27. **Biting bounds** — Attempt counters persist and increment before activation. The
    numeric maximum and repeated non-narrowing threshold route to
    `CONVERGENCE_EXHAUSTED`; exhaustion cannot become acceptance, prerequisite pause,
    or an unbounded retry.
28. **Workbook-only repair** — Workbook layout/navigation/front-matter/assembly repairs
    cannot change accepted unit content, visuals, PDFs, hashes, or receipts. A requested
    unit mutation is an integrity failure, not a workbook repair.
29. **Durable resume** — Checkpoints bind identity, position, current heads, accepted
    receipts, hashes, counters, and next node. Resume validates the prefix, preserves
    accepted work, refuses changed inputs and duplicate/out-of-order continuation, and
    cannot overwrite an accepted unit.

## Terminals and truthful failure

30. **Exact terminal vocabulary** — Only `UNIT_ACCEPTED`, `COMPLETE`, `INTERRUPTED`,
    `PAUSED_PREREQUISITE`, `CONVERGENCE_EXHAUSTED`, and `SYSTEM_FAILURE` exist. Every
    terminal has one declared guard and is reachable only under that guard.
31. **Narrow prerequisite pause** — `PAUSED_PREREQUISITE` requires a named unavailable
    externally supplied safety-critical fact and declared source-attempt evidence.
    Factory, graph, tool, route, schema, renderer, worker, containment, state, or
    evidence faults must be `SYSTEM_FAILURE`.
32. **Controller-owned success** — Only controller code writes acceptance and terminal
    state. A model `PASS`, review verdict, completed prompt, or generated artifact cannot
    by itself advance or terminate the run.
33. **Run prompt executes** — `run_curriculum_factory.prompt.v1.md` instructs execution
    of this factory for supplied runtime inputs until an accepted curriculum product or
    honest terminal. It never asks the caller to implement, redesign, phase, evolve, or
    promote the factory.
34. **Executable repository binding** — `python3 -m runtime.run_curriculum` resolves
    this graph and its eight package-relative prompts, accepts the exact active manifest
    path or curriculum directory, and activates the declared controller/model nodes.
    A prose-only graph with no bound entry point, a root-level `prompts/` assumption, or
    delegation to the legacy simulation FSM fails this criterion. The runtime binding
    is a mechanism that executes the graph; it is not a substitute product or a later
    factory-implementation phase.

## Mandatory adversarial rejection tests

The QA verdict is failure unless each mutation is demonstrably rejected:

1. route `START` directly to a success terminal;
2. remove one required source, check, review, artifact, or page result;
3. mark a stale subject hash `PASS`;
4. hardcode one unit ID/count/order in the engine graph;
5. give a model permission to validate, aggregate, accept, route, checkpoint, assemble,
   audit, or write a terminal;
6. give a reviewer an author history or sibling verdict;
7. allow a join with one missing or cross-unit member;
8. replace an actual visual asset with its brief or provenance text;
9. sample rather than inspect every shipped page;
10. retry a repair beyond its bound or without a versioned parent;
11. repair one local defect by replacing the entire unit;
12. let workbook repair alter one accepted-unit byte;
13. resume after a frozen digest changes or overwrite an accepted artifact;
14. assemble partial/duplicate/out-of-order accepted coverage;
15. substitute a prompt review for actual curriculum review;
16. classify a renderer, route, model, or controller failure as prerequisite pause; and
17. claim success from a graph, prompt, simulation, capability receipt, or QA report
    while no accepted curriculum product exists.

## Passing evidence

A package-only audit may establish graph closure and prompt agreement but cannot claim
a curriculum run passed. A runtime claim requires raw current output evidence showing
the exact accepted unit or workbook, every denominator, all artifact and page hashes,
independent review, bounded repair/retest history, checkpoints, append-only logs, and
the controller-written terminal. Report these two scopes separately.
