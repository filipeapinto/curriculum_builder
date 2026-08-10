# P3 — Implement the unit production subgraph

## GOAL

- `prompt_id`: `plan24.P3.unit_production_graph.v1`
- `role`: `unit_graph_implementer`
- `objective`: Make one manifest-selected unit run autonomously from research
  through accepted rendered PDF under the compiled graph.
- `non_goals`: Do not hand-author worker outputs; skip rendering or product QA;
  let a model accept its work; regenerate unrelated artifacts for a local
  failure; use Arduino logic in engine code.
- `authorized_inputs`: P0–P2 receipts and code, selected curriculum contracts,
  compiled unit subgraph, checks, rendering and review policies.
- `output_contract`: Executable unit nodes/edges, artifact registry, checks,
  targeted repair mapping, acceptance reducer, checkpoints, tests, a fresh live
  unit run, and P3 receipt.
- `completion_condition`: One live unit reaches `UNIT_ACCEPTED` with complete
  source, artifact, page, check, review, repair, and audit evidence and no manual
  intermediate edit.

## TEST

1. Research map/join correlates all and only the selected unit's source needs.
2. Domain output validates against curriculum schema and deterministic verifier
   before engine-block authoring.
3. Every rendered fact/visual resolves to an admitted parent and exact bytes.
4. The complete deterministic denominator precedes independent review; every
   PDF page is rendered and included in product QA.
5. The code reducer—not a model—decides pass, targeted repair, prerequisite,
   exhaustion, or system failure from typed records.
6. Each injected blocking check routes to exactly one owned diff, preserves
   unrelated hashes, invalidates descendants, and reruns required checks.
7. Same-check-set repetition hits a biting bound and cannot become acceptance.
8. A clean fresh live run records actual selected/executed workers and reaches
   unit acceptance without prewritten production artifacts.

## LOOP

Unit repair follows the compiled failed-check mapping only. Every repair creates
a new artifact version and preserves lineage; it never edits accepted bytes in
place. Loop through invalidated descendants until all current denominators pass
or the frozen bound reaches `CONVERGENCE_EXHAUSTED`. Advance only after the live
unit proof is independently inspected.
