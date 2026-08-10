# Plan 24 — Graph-engineered curriculum factory

- Version: `1.0`
- Recorded: `2026-08-10`
- Status: `ready_for_execution`
- Supersedes the product intent of: `plans/23_graph_eng_evol_01`
- Reuses verified ideas from: Plans 19, 21, and 23
- Canonical execution prompt: `run.prompt.md`
- Canonical QA criteria: `qa_criteria.v1.md`

## 1. Non-negotiable objective

Build and prove an operational, curriculum-neutral **curriculum factory**.

The factory accepts:

```text
ENGINE + one CURRICULUM manifest + OUTPUT_ROOT + run mode
```

and autonomously produces:

```text
validated curriculum inputs
  -> sourced and verified unit packages
  -> rendered, reviewed, accepted unit PDFs
  -> assembled, reviewed, accepted workbook
  -> append-only evidence and resumable run state
```

The graph is the factory's implementation architecture. A prompt graph, graph
specification, population of graph candidates, review dossier, visualization,
or QA record is **not** the product.

Plan 24 succeeds only when the repository can execute the production graph and
produce curriculum artifacts from a supplied manifest without a coding agent
manually carrying files between stages or authoring intermediate curriculum
content.

## 2. Correction of Plan 23

Plan 23 optimized and promoted prompt graphs. Its objective, fitness,
terminals, and QA criteria permitted success without generating a curriculum.
That is the central defect Plan 24 corrects.

Plan 24 retains only generally useful graph-engineering controls:

- explicit nodes, typed ports, state, reducers, guards, joins, loops, and
  terminals;
- separate execution and context graphs;
- controller-owned routing and state transitions;
- immutable inputs and append-only evidence;
- bounded repair with honest exhaustion;
- deterministic validation and independent review;
- exact artifact identity and safe resume.

Plan 24 rejects these Plan 23 product choices:

- evolving prompts as the principal workload;
- promoting a prompt-graph champion as the success terminal;
- fitness that can be computed without curriculum output;
- prompt-only QA as evidence of curriculum quality;
- excluding rendered curriculum, PDFs, pages, or visuals from product QA;
- spending the run on candidate populations instead of production units.

No Plan 23 prompt is an execution dependency of Plan 24.

## 3. Scope lock

### In scope

1. Reconcile the active runtime, prompt, policy, schemas, checks, routes, and
   lifecycle records into one executable authority.
2. Implement a graph IR and deterministic compiler that expands any valid
   curriculum manifest into one closed effective production graph.
3. Replace the current simulation-only/live-refusal path with bounded live
   worker execution through policy-selected routes.
4. Execute every unit through research, domain construction, authoring,
   deterministic verification, independent review, rendering, page QA,
   targeted repair, acceptance, and checkpointing.
5. Execute manifest order, interruption, cold resume, exact accepted-unit
   coverage, workbook assembly, workbook QA, targeted workbook repair, and
   release.
6. Produce auditable evidence binding every model call, source, artifact,
   check, transition, and terminal claim to exact bytes and identities.
7. Prove curriculum neutrality with a bounded non-Arduino fixture and exercise
   the Arduino curriculum without hardcoding its name, subject, or unit count.

### Out of scope

- A general-purpose agent framework unrelated to curriculum production.
- A prompt optimizer, prompt marketplace, prompt-graph champion, or graph
  visualization as the deliverable.
- Manually writing units to make the demonstration pass.
- Hardcoding Arduino concepts, identifiers, counts, or domain logic in engine
  code.
- Redesigning a curriculum's pedagogy or domain contract unless an executable
  contradiction blocks the factory.
- Weakening checks, review, rendering, evidence, safety, or release criteria to
  obtain a pass.
- Treating static tests, simulation, route probes, prompt QA, or file presence
  as generated-curriculum evidence.

## 4. Product contract

### Factory inputs

The run freezes before execution:

- engine root and engine contract digest;
- exact curriculum root, manifest, manifest digest, ordered unit IDs, domain
  schema, domain verifier, verifier fixtures, calibration, and curriculum-owned
  checks;
- effective policy, route catalogue, model registry, schemas, prompts, and
  check denominator;
- output root, run mode, resource limits, and resume intent;
- graph compiler version and effective graph digest.

The output root is the only production write boundary. A fresh run refuses an
existing output root. Resume reads and writes only the selected run and refuses
changed frozen inputs.

### Factory outputs

For every attempted unit, the factory owns and records:

- primary-source retrieval records and content hashes;
- a curriculum-schema-valid domain artifact;
- one engine-schema-valid unit artifact whose rendered facts resolve to their
  declared parents;
- visual assets and provenance receipts when the unit contract requires them;
- deterministic check results using the complete compiled denominator;
- independent review records with actual route/model identity;
- targeted revision receipts for every failed check;
- a rendered PDF and a complete page inventory;
- page-level deterministic and declared visual QA results;
- an acceptance or honest terminal record;
- checkpoints sufficient for cold-process resume.

For a complete manifest run, the factory additionally owns and records:

- exact accepted-unit coverage in manifest order;
- an assembled workbook and hash-bound assembly manifest;
- rendered page inventory for the full workbook;
- workbook-level deterministic and independent QA;
- targeted workbook-only revision receipts;
- final audit and the sole legitimate `COMPLETE` record.

### Legitimate terminals

- `UNIT_ACCEPTED` — requested `--lab-id` unit accepted; no workbook-complete
  claim.
- `COMPLETE` — every manifest unit accepted and the workbook passed release.
- `INTERRUPTED` — durable checkpoint exists and the exact resume command is
  emitted.
- `PAUSED_PREREQUISITE` — a named, externally supplied, safety-critical fact is
  unavailable; resumable and never used for a factory/tool defect.
- `CONVERGENCE_EXHAUSTED` — a bounded repair loop repeated valid failures and
  preserved all evidence; no acceptance claim.
- `SYSTEM_FAILURE` — contract, graph, tool, worker, schema, integrity, or
  evidence failure; no curriculum obstacle is invented.

No terminal named `PROMPT_PROMOTED`, `GRAPH_PROMOTED`, or equivalent is legal.

## 5. Factory graph model

### 5.1 Graph IR

The compiler materializes one immutable effective graph per run. Its normalized
IR contains:

```text
graph_id, compiler_version, contract_digest, manifest_digest
entry_node, terminal_nodes
nodes:
  node_id, kind, owner, input_ports, output_ports,
  state_reads, state_writes, context_projection,
  check_ids, retry_policy, artifact_contract
execution_edges:
  source, guard_id, destination, payload_projection
context_edges:
  source_artifact, destination_node, field_projection
joins:
  join_id, correlation_key, required_branches, reducer
loops:
  loop_id, entry, repair_owner, invalidation_set,
  counter, maximum, exhaustion_terminal
manifest_expansion:
  ordered unit instance nodes and dependencies
output_contracts, check_denominators, route_bindings
canonical_effective_graph_digest
```

Model prompts are payloads bound to model nodes. They do not define graph
authority, transitions, acceptance, or terminals.

### 5.2 State and reducers

The controller owns one versioned run state:

```text
run_identity and frozen_inputs                 write once
effective_graph and graph_digest               write once
capability_receipts                            append-only by route/probe
source_records                                 append-only by source request
unit_artifacts                                 versioned by unit/type/version
unit_checks                                    append-only by unit/version/check
unit_reviews                                   append-only by unit/version/review
unit_status                                    monotonic controller transition
checkpoints                                    append-only by graph position
revision_counters                              monotonic by unit/check set
accepted_unit_hashes                           write once by unit
workbook_artifacts/checks/reviews               versioned append-only
run_terminal                                   write once
```

Conflicting duplicate keys, counter rollback, overwritten accepted bytes,
cross-unit joins, incomplete denominators, or state transitions not represented
by a declared execution edge are `SYSTEM_FAILURE`.

### 5.3 Execution graph

```text
START
  -> freeze_run_inputs
  -> validate_curriculum_contract
  -> compile_effective_factory_graph
  -> validate_graph_closure
  -> prove_live_capabilities
  -> initialize_run_state
  -> select_next_manifest_unit
       | requested unit exists and prerequisites accepted
       v
     prepare_unit
       -> dispatch_research -------------------------------+
            -> retrieve_primary_source (map by need)       |
            -> join_research (by unit_id + request_id) <---+
       -> construct_domain
       -> run_domain_schema_and_verifier
            | local defect -> targeted_domain_repair ------+
            | external fact absent -> PAUSED_PREREQUISITE  |
            | pass                                         |
            +----------------------------------------------+
       -> author_engine_blocks
       -> validate_unit_schema_and_derivations
            | failed owned checks -> targeted_unit_repair --+
            | pass                                          |
            +-----------------------------------------------+
       -> produce_declared_visuals
       -> resolve_visual_receipts
            | failed visual artifact -> targeted_visual_repair --+
            | pass                                              |
            +---------------------------------------------------+
       -> render_unit_pdf
       -> inspect_all_unit_pages
       -> independent_unit_review
       -> reduce_unit_verdicts
            | repairable named failures -> route_targeted_repair
            | same check set within bound -> re-run invalidated descendants
            | same check set exhausted -> CONVERGENCE_EXHAUSTED
            | pass -> accept_unit -> checkpoint_unit
       -> select_next_manifest_unit
            | more units -> prepare_unit
            | --lab-id completed -> UNIT_ACCEPTED
            | full manifest accepted -> assemble_workbook
  -> render_all_workbook_pages
  -> independent_workbook_review
  -> reduce_workbook_verdicts
       | workbook-owned failure + budget -> targeted_workbook_repair
            -> assemble_workbook
       | exhausted -> CONVERGENCE_EXHAUSTED
       | pass -> final_release_audit -> COMPLETE
```

Every box above is either a deterministic node, a policy-routed model node, or
an explicit fan-out/join. There is no filename-ordered implicit execution.

### 5.4 Execution guards

Every dynamic source has one code-owned routing function returning exactly one
declared guard. Mandatory guards include:

- no model activation without a validated routing decision and observed
  executed model identity;
- no authoring before source and domain prerequisites are admitted;
- no review before the complete deterministic check denominator exists;
- no unit acceptance with any blocking check absent, stale, invalid, failed, or
  `NOT_RUN`;
- no next-unit activation before the previous required unit is accepted;
- no workbook assembly without exact accepted-manifest coverage;
- no `COMPLETE` outside successful workbook release audit;
- no repair without named failed checks, an artifact owner, remaining budget,
  and a declared invalidation/retest set.

### 5.5 Context graph

Execution adjacency never grants conversation history or filesystem access.

| Node class | Receives | Must not receive |
| --- | --- | --- |
| selector | task taxonomy, registry, route policy, bounded task facts | candidate content, worker self-preference |
| retrieval worker | bounded source request and allowed network capability | author/reviewer conversations, unrelated unit files |
| domain author | manifest unit, admitted sources, domain schema/calibration | hidden tests, sibling units beyond declared prerequisites |
| unit author | admitted domain artifact, engine unit contract, pedagogy/prose rules | reviewer verdicts, mutable source aliases |
| visual worker | visual brief, exact parent facts, allowed asset route | unrelated prose/history, acceptance authority |
| reviewer | frozen candidate artifact, rubric, required evidence | author history, sibling verdicts, transition authority |
| repair worker | named findings, owned artifacts, allowed diff, retest list | unrelated artifacts or permission to broaden repair |
| controller | typed records required to route | private model reasoning or undeclared semantic content |

Worker sandboxes enforce the allowed reads and writes; prompt instructions alone
do not count as isolation.

## 6. Product QA and evidence boundary

Plan 24 evaluates the product, not merely the instructions that could produce
it. The following evidence classes remain distinct:

| Evidence | What it can prove | What it cannot prove |
| --- | --- | --- |
| static graph/compiler tests | graph structure and contract enforcement | live curriculum production |
| simulated worker tests | routing and failure-path behavior | model capability or content quality |
| capability probes | a route worked under a frozen invocation | a unit was generated or accepted |
| prompt review | prompt/graph agreement | output correctness or usability |
| unit run evidence | one exact unit's production and acceptance | complete curriculum/workbook |
| workbook release evidence | exact accepted coverage and final artifact QA | other curricula not executed |

All pages shipped to the user are rasterized and included in the page
denominator. Deterministic inspection covers existence, renderability,
dimensions, nonblank content, clipping/overflow signals where available,
asset/hash resolution, and text/artifact consistency. Declared visual and
pedagogical review examines the rendered output itself. A prompt asking for a
good page is never evidence of a good page.

## 7. Implementation phases

### P0 — Baseline, contradiction census, and authority freeze

**Goal:** Establish the truthful current baseline and one executable contract
before implementation.

Required work:

- Inventory active runtime, prompt, policies, schemas, routes, checks, tests,
  curriculum contracts, and dirty/untracked work without overwriting it.
- Reproduce current test and CLI behavior, including the live-capability
  refusal and simulation-only path.
- Resolve active contradictions such as stale documentation, legacy controller
  states versus the current one-judge contract, and workbook completion claims.
- Freeze the terminal vocabulary, artifact ownership, graph node catalogue,
  complete check denominator, and exact baseline digests.
- Add failing acceptance tests for live `--lab-id`, live `--all`, targeted
  repair, cold resume, and workbook release.

Exit proof: failures are caused by missing factory behavior, not environment or
fixture breakage; every planned node/check/artifact/terminal has one owner.

### P1 — Effective graph IR and compiler

**Goal:** Compile any valid curriculum manifest into one closed executable
factory graph.

Required work:

- Define and validate the normalized IR described in section 5.1.
- Expand manifest unit IDs and declared dependencies without subject-specific
  engine code.
- Bind every node to exact inputs, outputs, checks, route class, state fields,
  reducers, guards, and failure edges.
- Validate reachability, type compatibility, single ownership, guard
  exclusivity, loop bounds, join correlation, output collisions, and terminal
  closure.
- Materialize and hash the effective graph; refuse base/overlay or prompt/graph
  ambiguity.

Exit proof: positive Arduino and unrelated fixtures compile; adversarial graphs
with dangling edges, hidden context, cross-unit joins, unbounded loops, missing
checks, or duplicate writers are rejected.

### P2 — Live worker and route execution

**Goal:** Turn graph model nodes into bounded, observable, schema-bound live
calls while code retains all control authority.

Required work:

- Implement selector-first routing and observed decided/executed identity.
- Prove required routes, primary-source retrieval, PDF/raster tools, and any
  declared visual route under exact frozen invocations.
- Stage each worker's allowed inputs into an isolated workspace and admit only
  its declared output artifact.
- Capture request, route, model, sandbox, exit, stdout/stderr, artifact digest,
  elapsed time, and normalized failure class.
- Reject missing, extra, path-escaping, malformed, stale, or schema-invalid
  output before state mutation.

Exit proof: live canaries for every retained route and worker class pass;
negative controls prove selector bypass, model mismatch, path escape, extra
write, malformed output, and unavailable route fail closed.

### P3 — Executable per-unit production subgraph

**Goal:** Autonomously produce and accept one complete unit from manifest data.

Required work:

- Implement research fan-out/join, source admission, domain construction and
  verification, six engine blocks, derivation checks, visuals, receipts,
  rendering, all-page inspection, independent review, verdict reduction,
  targeted repair, acceptance, and checkpointing.
- Map every blocking check to exactly one owned repair scope or a non-repair
  terminal.
- Re-run all invalidated descendants after repair; preserve unaffected accepted
  artifacts and forbid broad regeneration for a local defect.
- Keep `PAUSED_PREREQUISITE` restricted to a named unavailable external fact.

Exit proof: a fresh live unit reaches `UNIT_ACCEPTED` with no manually authored
intermediate file; injected defects exercise each targeted repair family and
repeat-failure exhaustion honestly.

### P4 — Manifest orchestration and durable resume

**Goal:** Execute `--lab-id`, `--all`, interrupt, and cold resume from the
compiled graph.

Required work:

- Replace CLI live refusal with the P1–P3 execution path after successful
  preflight.
- Derive unit order and count only from the frozen manifest.
- Atomically commit checkpoints and consume resume commands before activation.
- Refuse changed digests, out-of-order units, accepted-unit overwrite,
  duplicate activation, or continuation from an invalid checkpoint.
- Emit truthful lifecycle state and an exact resume command at interruption or
  prerequisite pause.

Exit proof: a bounded three-unit non-Arduino fixture completes through `--all`;
a killed process cold-resumes at the first incomplete valid graph position and
preserves accepted hashes.

### P5 — Workbook assembly and release subgraph

**Goal:** Turn exact accepted-unit coverage into a reviewed final workbook.

Required work:

- Assemble units exactly once in manifest order and bind source PDFs and output
  bytes in an assembly manifest.
- Render and inspect every workbook page, execute the frozen workbook review
  denominator, and reduce verdicts in code.
- Route navigation, front matter, TOC, pagination, layout, and assembly defects
  only to workbook-owned repairs; never reopen accepted unit content for a
  workbook-layout defect.
- Make final release audit the only writer of `COMPLETE`.

Exit proof: incomplete coverage, missing/duplicate/out-of-order units, blank or
bad pages, invalid reviews, changed accepted bytes, and false completion are
rejected; a clean fixture emits an accepted workbook.

### P6 — End-to-end proof and truthful handoff

**Goal:** Prove that the repository is a curriculum factory, not a collection
of factory plans.

Required work:

- Run the full unit, three-unit unrelated fixture, resume, workbook, fault
  injection, and independent recomputation suites from clean output roots.
- Start an Arduino curriculum production run using manifest-derived units. It
  either advances normally or pauses only at a proven external prerequisite.
- Have an independent auditor recompute graph identity, denominators, hashes,
  transitions, unit acceptance, coverage, and workbook terminal from raw
  evidence rather than controller conclusions.
- Update only documentation and deferred claims made true by recorded evidence.
- Record exact operator commands for preflight, live unit, full run, resume,
  inspection, and failure recovery.

Exit proof: all acceptance criteria in `qa_criteria.v1.md` pass with no
unresolved blocker; the canonical demo was produced by the factory with zero
manual intermediate artifact edits.

## 8. Phase dependency graph

```text
P0 -> P1 -> P2 -> P3 -> P4 -> P5 -> P6
```

Phases are sequential because each freezes an executable contract consumed by
the next. Within a phase, independent research, test, and inspection work may
fan out only when its join, correlation key, and reducer are declared.

No phase may report complete from authored prose alone. Completion requires its
specified executable evidence.

## 9. Global verification matrix

1. `FACTORY-T01 PRODUCT_IDENTITY` — The only success products are accepted
   curriculum unit/workbook artifacts and their evidence; graph or prompt
   promotion cannot terminate successfully.
2. `FACTORY-T02 GRAPH_CLOSURE` — The effective graph is typed, reachable,
   bounded, context-explicit, and has one owner per write and route.
3. `FACTORY-T03 MANIFEST_NEUTRALITY` — Unit IDs, count, order, dependencies,
   domain schema, and verifier derive from the selected curriculum.
4. `FACTORY-T04 LIVE_EXECUTION` — Live generation performs real selected model
   calls with observed identity and admits schema-valid artifacts.
5. `FACTORY-T05 SOURCE_AND_DERIVATION` — Domain facts bind retrieved primary
   sources and rendered claims bind admitted parent fields.
6. `FACTORY-T06 COMPLETE_DENOMINATORS` — Every required check/review/page is
   present exactly once or acceptance is impossible.
7. `FACTORY-T07 TARGETED_REPAIR` — Named failures route only to owned artifacts,
   invalidate descendants, retest, and terminate at a biting bound.
8. `FACTORY-T08 ISOLATION` — Workers cannot read undeclared files, sibling
   verdicts, hidden tests, or controller authority and cannot write elsewhere.
9. `FACTORY-T09 RESUME` — Cold resume preserves accepted bytes, consumes one
   continuation once, and refuses changed frozen inputs.
10. `FACTORY-T10 OUTPUT_QA` — Unit and workbook PDFs render; all pages enter the
    denominator; visual, factual, pedagogical, and structural product checks
    apply to actual output.
11. `FACTORY-T11 RELEASE_TRUTH` — Only exact manifest coverage plus accepted
    workbook audit can write `COMPLETE`.
12. `FACTORY-T12 END_TO_END_AUTONOMY` — The clean demonstration requires no
    coding-agent shepherding or hand-authored intermediate curriculum artifact.

## 10. Execution rule

Run Plan 24 only through `run.prompt.md` or the phase prompts it names. The
orchestrator must implement and verify the phases in dependency order. It may
repair implementation defects within the current phase, but it may not redesign
the objective into prompt evolution, graph research, planning-only output, or a
different product.

If the factory cannot be completed, the terminal report must name the first
unmet acceptance criterion, exact evidence, preserved work, and resumable next
action. It must not substitute a polished plan, a graph diagram, or a QA report
for the missing curriculum factory.
