# The 6 prompts in plans/23_graph_eng_evol_01/prompts/ — brief

Scope: **only** the 6 files in `plans/23_graph_eng_evol_01/prompts/` —
`seed_population`, `review_candidate`, `repair_candidate`, `mutate_prompts`,
`mutate_topology`, `recombine_candidates`. Nothing from `run.prompt.md`'s
GRAPH STATE / QA-gate / deterministic-reducer machinery is in this diagram —
an earlier draft pulled that in and it does not belong here.

Every edge below is quoted directly from that node's own `## GRAPH INTERFACE`
block — nothing inferred, nothing borrowed from another plan:

- `seed_population`: `input edge: START -> seed_population` /
  `next edge on exact count + unique digests: compile_population`
- `review_candidate`: `input edge: dispatch_candidate_checks -> review_candidate(candidate_id)` /
  `parallel sibling: test_candidate(candidate_id)` / `next edge: join_candidate_checks(candidate_id)`
- `repair_candidate`, `mutate_prompts`, `mutate_topology`, `recombine_candidates`:
  each states `input edge: select_parents -> <this node>` and `next edge: merge_offspring`

`compile_population`, `dispatch_candidate_checks`, `test_candidate`,
`join_candidate_checks`, `select_parents`, and `merge_offspring` are drawn
because the 6 files name them as their own predecessor/successor — they are
**not** themselves files in `prompts/`, which is why they're grey instead of
blue and every one carries a "referenced, not authored here" note. Blue
(`primary`, cyan border) = an actual file in `prompts/`. Grey (`neutral`) =
named by one of those files but not itself one of the 6.

White background (`--theme light`, now the render script's default).

## Reconstructing this diagram

```bash
python3 .claude/skills/harness-graph-create/scripts/render_graph.py \
  plans/23_graph_eng_evol_01/plan23_prompts_only.harness_graph.v1.json \
  -o plans/23_graph_eng_evol_01/plan23_prompts_only.harness_graph.v2.png
```

Full JSON spec:

```json
{
  "title": "Plan 23: The 6 Prompts in prompts/",
  "lanes": [
    {"id": "top", "label": null, "role": "neutral"},
    {"id": "main", "label": "AUTHORED IN prompts/", "role": "primary"},
    {"id": "sibling", "label": null, "role": "neutral"},
    {"id": "op1", "label": "AUTHORED IN prompts/", "role": "primary"},
    {"id": "op2", "label": "AUTHORED IN prompts/", "role": "primary"},
    {"id": "op3", "label": "AUTHORED IN prompts/", "role": "primary"},
    {"id": "op4", "label": "AUTHORED IN prompts/", "role": "primary"}
  ],
  "nodes": [
    {"id": "start", "kind": "start", "lane": "top", "col": 0, "label": "START", "role": "neutral"},

    {"id": "seed_population", "kind": "stage", "lane": "main", "col": 1, "label": "seed_population",
     "detail": "seed_population.prompt.v1.md"},
    {"id": "compile_population", "kind": "stage", "lane": "main", "col": 2, "label": "compile_population",
     "detail": "referenced, not authored here", "role": "neutral"},
    {"id": "dispatch_candidate_checks", "kind": "stage", "lane": "main", "col": 3, "label": "dispatch_candidate_checks",
     "detail": "referenced, not authored here", "role": "neutral"},
    {"id": "review_candidate", "kind": "stage", "lane": "main", "col": 4, "label": "review_candidate",
     "detail": "review_candidate.prompt.v1.md"},
    {"id": "join_candidate_checks", "kind": "stage", "lane": "main", "col": 5, "label": "join_candidate_checks",
     "detail": "referenced, not authored here", "role": "neutral"},
    {"id": "select_parents", "kind": "stage", "lane": "main", "col": 6, "label": "select_parents",
     "detail": "referenced, not authored here", "role": "neutral"},
    {"id": "merge_offspring", "kind": "stage", "lane": "main", "col": 8, "label": "merge_offspring",
     "detail": "referenced, not authored here", "role": "neutral"},

    {"id": "test_candidate", "kind": "stage", "lane": "sibling", "col": 4, "label": "test_candidate",
     "detail": "review_candidate's stated “parallel sibling” — not itself in prompts/", "role": "neutral"},

    {"id": "repair_candidate", "kind": "stage", "lane": "op1", "col": 7, "label": "repair_candidate",
     "detail": "repair_candidate.prompt.v1.md"},
    {"id": "mutate_prompts", "kind": "stage", "lane": "op2", "col": 7, "label": "mutate_prompts",
     "detail": "mutate_prompts.prompt.v1.md"},
    {"id": "mutate_topology", "kind": "stage", "lane": "op3", "col": 7, "label": "mutate_topology",
     "detail": "mutate_topology.prompt.v1.md"},
    {"id": "recombine_candidates", "kind": "stage", "lane": "op4", "col": 7, "label": "recombine_candidates",
     "detail": "recombine_candidates.prompt.v1.md"}
  ],
  "edges": [
    {"from": "start", "to": "seed_population", "style": "flow"},
    {"from": "seed_population", "to": "compile_population", "style": "flow"},
    {"from": "compile_population", "to": "dispatch_candidate_checks", "style": "flow"},
    {"from": "dispatch_candidate_checks", "to": "review_candidate", "style": "flow"},
    {"from": "dispatch_candidate_checks", "to": "test_candidate", "label": "parallel sibling", "style": "check"},
    {"from": "review_candidate", "to": "join_candidate_checks", "style": "flow"},
    {"from": "test_candidate", "to": "join_candidate_checks", "style": "check"},
    {"from": "join_candidate_checks", "to": "select_parents", "style": "flow"},

    {"from": "select_parents", "to": "repair_candidate", "style": "flow"},
    {"from": "select_parents", "to": "mutate_prompts", "style": "flow"},
    {"from": "select_parents", "to": "mutate_topology", "style": "flow"},
    {"from": "select_parents", "to": "recombine_candidates", "style": "flow"},
    {"from": "repair_candidate", "to": "merge_offspring", "style": "flow"},
    {"from": "mutate_prompts", "to": "merge_offspring", "style": "flow"},
    {"from": "mutate_topology", "to": "merge_offspring", "style": "flow"},
    {"from": "recombine_candidates", "to": "merge_offspring", "style": "flow"}
  ]
}
```
