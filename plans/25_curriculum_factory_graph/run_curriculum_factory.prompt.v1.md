# Run the curriculum factory graph

## Objective

Execute `curriculum_factory.graph.v1.md` for the supplied runtime inputs. The graph
is the curriculum factory. Do not redesign it, create a different workflow, author
project phases, or stop after producing instructions, scaffolding, a simulation, or
a review report.

## Required runtime inputs

The caller must supply:

```text
ENGINE_ROOT
CURRICULUM_ROOT
MANIFEST_PATH
OUTPUT_ROOT
RUN_MODE = ONE_UNIT | ALL_UNITS | RESUME
REQUESTED_UNIT_ID = required only for a new or resumed one-unit run
RESUME_RUN_ID = required only when resuming an existing run
LIMIT_OVERRIDES = optional, only through flags declared in policy/limits.v1.yaml
```

Resolve and validate these inputs exactly as the canonical graph declares. Never
insert a curriculum name, subject, unit count, unit ID, or order not supplied by the
validated manifest.

## Authorized authority

- `curriculum_factory.graph.v1.md`;
- the eight exact prompt files under `prompts/` named by that graph;
- `qa_criteria.v1.md` for conformance and product audit;
- the supplied engine, curriculum, manifest, output root, mode, and limit values;
- the active files that section 2 of the graph freezes; and
- only controller state and runtime artifacts admitted through graph reducers.

Historical Plans 23 and 24 are observations only. Their candidate promotion and
factory-construction work are not executable dependencies.

## Execution contract

1. Resolve the graph and every referenced prompt before `START`. Refuse an incomplete
   package as `SYSTEM_FAILURE`.
2. Pass the raw runtime inputs to `D01_VALIDATE_AND_FREEZE_RUN`. From that point,
   activate only the exact node reached by a declared execution edge whose guard is
   true.
3. Persist every controller action, model call, source request, artifact admission,
   check, render, review, repair, state transition, checkpoint, and terminal decision
   through the graph's reducer before evaluating the next guard.
4. Apply routing policy in code before every model node. Record the decided and
   observed executed identity and refuse mismatches. Never route deterministic nodes
   through a model.
5. Stage only the context edges declared for the activated model node. One activation
   receives one fresh bounded request and one preallocated output. Execution adjacency
   does not grant conversation or filesystem context.
6. Allocate every fan-out denominator before dispatch and join only on the graph's
   full correlation key. Do not continue past a missing, duplicate, stale, invalid,
   failed, cross-unit, or `NOT_RUN` member.
7. Derive unit expansion and selection solely from the frozen manifest. For a full
   run, advance in manifest order only after the current unit has a section 13.1
   accepted receipt and checkpoint.
8. Run deterministic validation and every required verifier/check against actual
   current artifact bytes. Render the actual unit, rasterize the shipped PDF, and put
   every page into the denominator before independent review.
9. Reduce results in controller code. A model supplies bounded artifacts or findings;
   it never selects the next node, aggregates a verdict, approves itself, writes
   acceptance, checkpoints, assembles the workbook, audits release, or writes a
   terminal.
10. For named repairable failures, use the compiled unique owner, allowed diff,
    immutable parent, new version, invalidation set, retest order, and biting counter.
    Reactivate only invalidated descendants. Never regenerate a whole unit for a local
    defect and never edit accepted unit content during workbook repair.
11. On interruption, complete or fail the current logged action, atomically preserve
    the last valid checkpoint, and emit the exact resume identity. On resume, validate
    the frozen identity and checkpoint prefix, preserve accepted bytes, and continue
    exactly once at the first incomplete legal node.
12. In full mode, assemble only exact accepted-manifest coverage, inspect every actual
    workbook page, independently review the actual workbook, repair only workbook-owned
    defects, and run `D32_FINAL_RELEASE_AUDIT` before `COMPLETE`.

## Failure discipline

- A named externally supplied safety-critical fact that remains unavailable after
  declared retrieval attempts may reach `PAUSED_PREREQUISITE` through
  `D30_CLASSIFY_PREREQUISITE`.
- Factory, graph, contract, route, model, tool, schema-engine, verifier-execution,
  render, state, containment, hash, join, log, checkpoint, or evidence faults are
  `SYSTEM_FAILURE`.
- A valid repair loop that reaches its numeric or repeated-failure bound is
  `CONVERGENCE_EXHAUSTED`.
- Never relabel a system defect as a curriculum prerequisite and never turn missing
  evidence into a pass.

## Completion condition

Continue until exactly one canonical terminal is durably written:

- `UNIT_ACCEPTED` only with the requested accepted unit package and shipped PDF;
- `COMPLETE` only with exact accepted-manifest coverage and the accepted workbook;
- `INTERRUPTED` only with a valid resumable checkpoint;
- `PAUSED_PREREQUISITE` only with the graph's narrow external-fact proof;
- `CONVERGENCE_EXHAUSTED` only with the bounded repair evidence; or
- `SYSTEM_FAILURE` with the exact failing node, invariant, and preserved evidence.

A graph document, prompt package, design, source dossier, candidate artifact,
capability probe, simulation, visualization, test result, or review report is not a
completion condition.

## Final response

Report the terminal, `run_id`, supplied manifest hash, mode, output root, accepted
unit/product paths and hashes actually earned, unit/workbook page denominators,
complete check/review disposition, repair totals, checkpoint/resume information,
log integrity, and any remaining work. Separate produced-artifact counts from accepted
product claims. Never report a unit or workbook accepted when any blocking evidence is
missing, stale, invalid, failed, duplicate, or `NOT_RUN`.
