# Plan 23 harness graph — brief

This is the execution graph of `plans/23_graph_eng_evol_01/run.prompt.md`'s
`plan23.run_evolution_graph.v1` harness: a bounded evolutionary run over a
population of prompt graphs, gated by an external, skill-owned QA process
before any candidate can become champion. It has four zones, top to bottom:

- **SEED · EVALUATE · ARCHIVE** — seed a gen-0 population, compile it, and (for
  whichever candidates compiled) run the checks that produce one fitness
  record per candidate.
- **PARALLEL CHECKS** — `dispatch_candidate_checks` fans each compiled
  candidate out to `test_candidate` (public dev/regression) and
  `review_candidate` (internal verdict) in parallel; `join_candidate_checks`
  is the fan-in, one join per candidate ID.
- **QA GATE** — the standardized, skill-owned `qa_gate.py` process. Its four
  exit codes (`10`/`0`/`1`/`2`) branch the run: a round with findings feeds
  those findings back into evolution as selection pressure; a verified pass
  goes to champion comparison; a verified fail goes to a fresh-session
  postmortem; a verified error or any verification-integrity problem ends the
  run without a promotion.
- **EVOLUTION** — `select_parents` fans out to the four variation operators
  (`repair_candidate`, `mutate_prompts`, `mutate_topology`,
  `recombine_candidates`), which fan back in at `merge_offspring`. Three
  distinct paths loop back into this zone: a new generation from
  `merge_offspring`, a QA round's admitted findings, and losing the champion
  race — drawn as three separate rails along the bottom so each stays
  legible instead of collapsing into one line.

Terminals: `PROMOTED` (the one goal state) and five non-goal terminals —
`CONVERGENCE_EXHAUSTED`, `QA_GATE_FAILED`, `QA_ERROR`, `QA_INTEGRITY_BREACH`
— reached when budgets run out or the gate cannot certify a pass.

Compression choices made when transcribing this from `run.prompt.md`, so a
future re-render from the same source lands on the same picture: consecutive
deterministic reducers with no branch between them were merged into one node
(`join_population` + `score_population` + `update_archive` →
`score_population → update_archive`; `open_qa_attempt` +
`prepare_qa_artifact`/`prepare_qa_revision` → one `prepare_qa_submission`
node; `qa_gate_start`/`qa_gate_round` → one `qa_gate_run` node;
`qa_gate_verify` + `capture_qa_verification` → `verify_qa_result`;
`qa_gate_postmortem` + `capture_qa_postmortem` → one node). The generic
fail-closed edges to `SYSTEM_FAILURE`/`INTERRUPTED` that exist on every node
per `run.prompt.md`'s guard table are not drawn individually — they would add
~28 near-identical edges with no diagnostic value; the terminals still name
the outcome in the brief above.

## Reconstructing this diagram

```bash
python3 .claude/skills/harness-graph-create/scripts/render_graph.py \
  plans/23_graph_eng_evol_01/plan23.harness_graph.v2.json \
  -o plans/23_graph_eng_evol_01/plan23.harness_graph.v3.png
```

Full JSON spec:

```json
{
  "title": "Plan 23: Evolutionary Prompt-Graph Run",
  "lanes": [
    {"id": "top", "label": null, "role": "neutral"},
    {"id": "main", "label": "SEED · EVALUATE · ARCHIVE", "role": "primary"},
    {"id": "test", "label": "PARALLEL CHECKS", "role": "support"},
    {"id": "review", "label": "PARALLEL CHECKS", "role": "support"},
    {"id": "qa", "label": "QA GATE", "role": "caution"},
    {"id": "qa2", "label": "QA GATE", "role": "caution"},
    {"id": "select", "label": "EVOLUTION", "role": "accent"},
    {"id": "op1", "label": "EVOLUTION", "role": "accent"},
    {"id": "op2", "label": "EVOLUTION", "role": "accent"},
    {"id": "op3", "label": "EVOLUTION", "role": "accent"},
    {"id": "op4", "label": "EVOLUTION", "role": "accent"},
    {"id": "merge", "label": "EVOLUTION", "role": "accent"}
  ],
  "nodes": [
    {"id": "start", "kind": "start", "lane": "top", "col": 0, "label": "START"},

    {"id": "seed_population", "kind": "stage", "lane": "main", "col": 1, "label": "seed_population", "detail": "diverse immutable gen-0 population"},
    {"id": "compile_population", "kind": "stage", "lane": "main", "col": 2, "label": "compile_population"},
    {"id": "dispatch_candidate_checks", "kind": "stage", "lane": "main", "col": 3, "label": "dispatch_candidate_checks", "detail": "map each compiled candidate"},
    {"id": "join_candidate_checks", "kind": "stage", "lane": "main", "col": 5, "label": "join_candidate_checks"},
    {"id": "score_and_archive", "kind": "stage", "lane": "main", "col": 6, "label": "score_population → update_archive"},
    {"id": "decide_generation", "kind": "gate", "lane": "main", "col": 7, "label": "decide_generation"},

    {"id": "test_candidate", "kind": "stage", "lane": "test", "col": 4, "label": "test_candidate", "detail": "public dev + regression"},
    {"id": "review_candidate", "kind": "stage", "lane": "review", "col": 4, "label": "review_candidate", "detail": "internal verdict only"},

    {"id": "prepare_qa_submission", "kind": "stage", "lane": "qa", "col": 8, "label": "open_qa_attempt → prepare_qa_artifact/revision"},
    {"id": "qa_gate_run", "kind": "stage", "lane": "qa", "col": 9, "label": "qa_gate_start / qa_gate_round", "detail": "skill-owned qa_gate.py"},
    {"id": "capture_qa_result", "kind": "gate", "lane": "qa", "col": 10, "label": "capture_qa_result", "detail": "exit 10 / 0 / 1 / 2"},
    {"id": "verify_qa_result", "kind": "gate", "lane": "qa", "col": 11, "label": "qa_gate_verify → capture_qa_verification"},
    {"id": "compare_with_champion", "kind": "gate", "lane": "qa", "col": 12, "label": "compare_with_champion"},
    {"id": "promote_prompt_graph", "kind": "stage", "lane": "qa", "col": 13, "label": "promote_prompt_graph"},
    {"id": "promoted", "kind": "terminal", "lane": "qa", "col": 14, "label": "PROMOTED", "role": "success"},

    {"id": "qa_postmortem", "kind": "stage", "lane": "qa2", "col": 12, "label": "qa_gate_postmortem → capture_qa_postmortem"},
    {"id": "close_qa_attempt", "kind": "stage", "lane": "qa2", "col": 13, "label": "close_qa_attempt"},
    {"id": "qa_gate_failed", "kind": "terminal", "lane": "qa2", "col": 14, "label": "QA_GATE_FAILED", "role": "failure"},
    {"id": "qa_error", "kind": "terminal", "lane": "qa2", "col": 15, "label": "QA_ERROR", "role": "failure"},
    {"id": "qa_integrity_breach", "kind": "terminal", "lane": "qa2", "col": 16, "label": "QA_INTEGRITY_BREACH", "role": "failure"},

    {"id": "select_parents", "kind": "stage", "lane": "select", "col": 8, "label": "select_parents"},
    {"id": "repair_candidate", "kind": "stage", "lane": "op1", "col": 9, "label": "repair_candidate", "detail": "local findings only"},
    {"id": "mutate_prompts", "kind": "stage", "lane": "op2", "col": 9, "label": "mutate_prompts", "detail": "prompt genes only"},
    {"id": "mutate_topology", "kind": "stage", "lane": "op3", "col": 9, "label": "mutate_topology", "detail": "graph genes only"},
    {"id": "recombine_candidates", "kind": "stage", "lane": "op4", "col": 9, "label": "recombine_candidates", "detail": "two compatible parents"},
    {"id": "merge_offspring", "kind": "gate", "lane": "merge", "col": 10, "label": "merge_offspring"},
    {"id": "convergence_exhausted", "kind": "terminal", "lane": "merge", "col": 12, "label": "CONVERGENCE_EXHAUSTED", "role": "failure"}
  ],
  "edges": [
    {"from": "start", "to": "seed_population", "style": "flow"},
    {"from": "seed_population", "to": "compile_population", "style": "flow"},
    {"from": "compile_population", "to": "dispatch_candidate_checks", "style": "flow"},
    {"from": "compile_population", "to": "score_and_archive", "label": "all failed", "style": "flow"},
    {"from": "dispatch_candidate_checks", "to": "test_candidate", "style": "flow"},
    {"from": "dispatch_candidate_checks", "to": "review_candidate", "style": "flow"},
    {"from": "test_candidate", "to": "join_candidate_checks", "style": "flow"},
    {"from": "review_candidate", "to": "join_candidate_checks", "style": "flow"},
    {"from": "join_candidate_checks", "to": "score_and_archive", "style": "flow"},
    {"from": "score_and_archive", "to": "decide_generation", "style": "flow"},

    {"from": "decide_generation", "to": "prepare_qa_submission", "label": "eligible, new attempt", "style": "flow"},
    {"from": "decide_generation", "to": "prepare_qa_submission", "label": "eligible, round open", "style": "flow"},
    {"from": "decide_generation", "to": "select_parents", "label": "no eligible, budget remains", "style": "flow"},
    {"from": "decide_generation", "to": "convergence_exhausted", "label": "no budget", "style": "flow"},

    {"from": "prepare_qa_submission", "to": "qa_gate_run", "style": "flow"},
    {"from": "qa_gate_run", "to": "capture_qa_result", "style": "flow"},
    {"from": "capture_qa_result", "to": "select_parents", "label": "exit 10: admit findings", "style": "loop"},
    {"from": "capture_qa_result", "to": "verify_qa_result", "label": "exit 0 / 1 / 2", "style": "flow"},

    {"from": "verify_qa_result", "to": "compare_with_champion", "label": "verified pass", "style": "flow"},
    {"from": "verify_qa_result", "to": "qa_postmortem", "label": "verified fail", "style": "flow"},
    {"from": "verify_qa_result", "to": "qa_error", "label": "verified error", "style": "flow"},
    {"from": "verify_qa_result", "to": "qa_integrity_breach", "label": "verification problem", "style": "check"},

    {"from": "compare_with_champion", "to": "promote_prompt_graph", "label": "eligible", "style": "flow"},
    {"from": "compare_with_champion", "to": "close_qa_attempt", "label": "ineligible, budget remains", "style": "flow"},
    {"from": "compare_with_champion", "to": "convergence_exhausted", "label": "ineligible, no budget", "style": "flow"},
    {"from": "promote_prompt_graph", "to": "promoted", "style": "flow"},
    {"from": "qa_postmortem", "to": "qa_gate_failed", "style": "flow"},
    {"from": "close_qa_attempt", "to": "select_parents", "label": "lost champion race", "style": "loop"},

    {"from": "select_parents", "to": "repair_candidate", "label": "local finding", "style": "flow"},
    {"from": "select_parents", "to": "mutate_prompts", "label": "prompt mutation", "style": "flow"},
    {"from": "select_parents", "to": "mutate_topology", "label": "topology mutation", "style": "flow"},
    {"from": "select_parents", "to": "recombine_candidates", "label": "compatible pair", "style": "flow"},
    {"from": "repair_candidate", "to": "merge_offspring", "style": "flow"},
    {"from": "mutate_prompts", "to": "merge_offspring", "style": "flow"},
    {"from": "mutate_topology", "to": "merge_offspring", "style": "flow"},
    {"from": "recombine_candidates", "to": "merge_offspring", "style": "flow"},
    {"from": "merge_offspring", "to": "compile_population", "label": "exact population → next generation", "style": "loop"},
    {"from": "merge_offspring", "to": "select_parents", "label": "shortfall, budget remains", "style": "loop"},
    {"from": "merge_offspring", "to": "convergence_exhausted", "label": "no budget", "style": "flow"}
  ]
}
```
