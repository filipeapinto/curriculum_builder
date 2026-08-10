# Plan 23 standardized external QA criteria

Codex evaluates the submitted `prompt_graph.vN.md` artifact against every
criterion below. A blocking finding must identify the criterion it defeats, a
concrete trigger, the operational consequence, and exact artifact evidence.
Anything that does not defeat a criterion is an observation.

1. **Artifact binding** — The artifact identifies one immutable candidate and
   binds its candidate digest, prompt digests, topology digest, compilation
   identity, evaluation evidence, lineage, and QA artifact version without
   unresolved aliases.
2. **Graph closure** — Entry, nodes, typed ports, execution edges, guards,
   joins, cycles, counters, outputs, and terminal routes are declared,
   reachable where intended, and contain no dangling or contradictory route.
3. **State and reducers** — Every node read/write maps to a declared state
   field and reducer; immutable and append-only fields cannot be overwritten;
   parallel updates and candidate-bound joins cannot silently conflict.
4. **Context isolation** — Every model node receives only its declared context
   projection. Execution adjacency does not imply conversation access, and no
   route leaks hidden holdouts, sibling context, author history, or QA control.
5. **Prompt-graph agreement** — Every model prompt's role, authorized inputs,
   exclusions, output contract, tests, loop behavior, and next owner agree with
   its graph node and typed ports.
6. **Evolutionary integrity** — Population cardinality, immutable ancestry,
   prompt mutation, topology mutation, local repair, recombination, offspring
   merge, diversity, and reevaluation are explicit and cannot inherit a
   parent's score as child evidence.
7. **Evaluation completeness** — Compilation, public development tests,
   regression tests, internal review, fitness dimensions, protected failures,
   and denominators are complete for the submitted candidate. Missing,
   duplicate, stale, or `NOT_RUN` evidence cannot count as pass.
8. **Selection and complexity** — Frontier membership and champion eligibility
   derive from complete measured evidence under constrained Pareto selection;
   protected regressions cannot be traded for aggregate gain and complexity is
   normalized consistently.
9. **QA-gate standardization** — External QA uses only
   `.claude/skills/qa-gate-codex-run/scripts/qa_gate.py`; criteria, focus,
   threshold, transport, and iteration limit are frozen; the controller does
   not create reviewer prompts, write `QA/`, or reinterpret gate states.
10. **QA lineage and integrity** — Gate rounds use strictly increasing artifact
    versions in one witnessed Codex session; terminal claims bind the exact
    session, artifact, response, hash chain, and successful `verify` output.
11. **Failure semantics** — `ROUND_OPEN`, `QA_PASSED`, `QA_FAILED`, `QA_ERROR`,
    integrity breach, budget exhaustion, and system failure have distinct
    fail-closed routes. Unavailable or malformed QA never becomes success.
12. **Promotion safety** — Promotion requires an unchanged eligible candidate,
    complete protected evidence, verified `QA_PASSED`, strict champion
    comparison, and atomic compare-and-swap. Every other terminal preserves the
    current champion.

