# Plan 22 — evolutionary prompt graph — harness execution graph

This depicts the controller-owned execution graph run by
`plans/22_graph_eng_evol_01/run.prompt.md`: a population-based search over
prompt graphs, where a generation is seeded, compiled, tested and reviewed in
parallel per candidate, scored, and then either sent to external review
(challenge review → final review → champion comparison, each of which can
reject back to `select_parents`) or varied into a new generation via
repair/mutation/recombination and merged back into `compile_population`. It is
drawn here to replace `plans/22_graph_eng_evol_01/graph.v1.png` — a dark,
neon-glow image with no saved source — with a reproducible equivalent: the same
JSON spec below, run through `scripts/render_graph.py`, always produces this
same picture.

Nodes are compressed from the plan's own `MODEL NODES` / `DETERMINISTIC NODES`
tables to the level `graph.v1.png` itself used (about twenty nodes): each fan-out
step (`dispatch_candidate_checks` into `test_candidate` / `review_candidate`) is
drawn as the fan itself rather than as a separate dispatcher node, and
`update_archive` is folded into `score_population` since it has no branching of
its own. `REVIEW_AUTHORITY_UNPROVEN` and `EVALUATOR_UNAVAILABLE` are omitted as
terminals, matching the same simplification the original image made.

```json
{
  "title": "Plan 22 — Evolutionary Prompt Graph",
  "lanes": [
    {"id": "top", "label": null, "role": "neutral"},
    {"id": "eval_a", "label": "EVALUATION", "role": "primary"},
    {"id": "eval_b", "label": "EVALUATION", "role": "primary"},
    {"id": "evo_top", "label": "EVOLUTION", "role": "accent"},
    {"id": "evo_mid", "label": "EVOLUTION", "role": "accent"},
    {"id": "evo_bottom", "label": "EVOLUTION", "role": "accent"},
    {"id": "review", "label": "EXTERNAL REVIEW", "role": "caution"}
  ],
  "nodes": [
    {"id": "start", "kind": "start", "lane": "top", "col": 0, "label": "START"},
    {"id": "seed", "kind": "stage", "lane": "top", "col": 1, "label": "Seed Population"},
    {"id": "compile", "kind": "stage", "lane": "eval_a", "col": 2, "label": "Compile Population"},
    {"id": "test_candidate", "kind": "stage", "lane": "eval_b", "col": 3, "label": "Test Candidate"},
    {"id": "review_candidate", "kind": "stage", "lane": "eval_b", "col": 4, "label": "Review Candidate"},
    {"id": "join_checks", "kind": "stage", "lane": "eval_a", "col": 5, "label": "Join Checks"},
    {"id": "join_population", "kind": "stage", "lane": "eval_a", "col": 6, "label": "Join Population"},
    {"id": "score_population", "kind": "gate", "lane": "eval_a", "col": 7, "label": "Score Population"},
    {"id": "decide_generation", "kind": "gate", "lane": "eval_a", "col": 8, "label": "Decide Generation"},
    {"id": "exhausted", "kind": "terminal", "lane": "eval_a", "col": 9, "label": "EXHAUSTED", "role": "failure"},
    {"id": "select_parents", "kind": "stage", "lane": "evo_top", "col": 6, "label": "Select Parents"},
    {"id": "repair", "kind": "stage", "lane": "evo_mid", "col": 7, "label": "Repair"},
    {"id": "mutate_prompts", "kind": "stage", "lane": "evo_mid", "col": 8, "label": "Mutate Prompts"},
    {"id": "mutate_topology", "kind": "stage", "lane": "evo_mid", "col": 9, "label": "Mutate Topology"},
    {"id": "recombine", "kind": "stage", "lane": "evo_mid", "col": 10, "label": "Recombine"},
    {"id": "merge_offspring", "kind": "stage", "lane": "evo_bottom", "col": 9, "label": "Merge Offspring"},
    {"id": "freeze_for_review", "kind": "stage", "lane": "review", "col": 11, "label": "Freeze for Review"},
    {"id": "challenge_review", "kind": "stage", "lane": "review", "col": 12, "label": "Challenge Review"},
    {"id": "final_review", "kind": "stage", "lane": "review", "col": 13, "label": "Final Review"},
    {"id": "compare_champion", "kind": "gate", "lane": "review", "col": 14, "label": "Compare Champion"},
    {"id": "promoted", "kind": "terminal", "lane": "review", "col": 15, "label": "PROMOTED", "role": "success"}
  ],
  "edges": [
    {"from": "start", "to": "seed", "style": "flow"},
    {"from": "seed", "to": "compile", "style": "flow"},
    {"from": "compile", "to": "test_candidate", "style": "flow"},
    {"from": "compile", "to": "review_candidate", "style": "flow"},
    {"from": "test_candidate", "to": "join_checks", "style": "flow"},
    {"from": "review_candidate", "to": "join_checks", "style": "flow"},
    {"from": "join_checks", "to": "join_population", "style": "flow"},
    {"from": "join_population", "to": "score_population", "style": "flow"},
    {"from": "score_population", "to": "decide_generation", "style": "flow"},
    {"from": "decide_generation", "to": "exhausted", "label": "budget exhausted", "style": "flow"},
    {"from": "decide_generation", "to": "freeze_for_review", "label": "review target ready", "style": "flow"},
    {"from": "decide_generation", "to": "select_parents", "label": "no target, budget remains", "style": "flow"},
    {"from": "select_parents", "to": "repair", "style": "flow"},
    {"from": "select_parents", "to": "mutate_prompts", "style": "flow"},
    {"from": "select_parents", "to": "mutate_topology", "style": "flow"},
    {"from": "select_parents", "to": "recombine", "style": "flow"},
    {"from": "repair", "to": "merge_offspring", "style": "flow"},
    {"from": "mutate_prompts", "to": "merge_offspring", "style": "flow"},
    {"from": "mutate_topology", "to": "merge_offspring", "style": "flow"},
    {"from": "recombine", "to": "merge_offspring", "style": "flow"},
    {"from": "merge_offspring", "to": "compile", "label": "next generation", "style": "loop"},
    {"from": "freeze_for_review", "to": "challenge_review", "style": "flow"},
    {"from": "challenge_review", "to": "final_review", "style": "flow"},
    {"from": "final_review", "to": "compare_champion", "style": "flow"},
    {"from": "compare_champion", "to": "promoted", "label": "eligible", "style": "flow"},
    {"from": "challenge_review", "to": "select_parents", "label": "findings", "style": "loop"},
    {"from": "final_review", "to": "select_parents", "label": "findings", "style": "loop"},
    {"from": "compare_champion", "to": "select_parents", "label": "ineligible", "style": "loop"}
  ]
}
```
