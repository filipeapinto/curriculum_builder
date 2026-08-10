# Plan 23 harness graph — brief

This is the execution graph of `plans/23_graph_eng_evol_01/run.prompt.md`'s
`plan23.run_evolution_graph.v1` harness: a bounded evolutionary run over a
population of prompt graphs, gated by an external, skill-owned QA process
before any candidate can become champion. Dark neon-glow theme, matching
`plans/22_graph_eng_evol_01/graph.v1.png`'s look — this supersedes `v2`, which
rendered the same content on white and is kept only for history (see that
version's own prompt.md for why white was tried and dropped).

Four zones, top to bottom:

- **SEED · EVALUATE · ARCHIVE** (cyan) — seed a gen-0 population, compile it,
  and (for whichever candidates compiled) run the checks that produce one
  fitness record per candidate.
- **PARALLEL CHECKS** (green) — `dispatch_candidate_checks` fans each compiled
  candidate out to `test_candidate` (public dev/regression) and
  `review_candidate` (internal verdict) in parallel; `join_candidate_checks`
  is the fan-in, one join per candidate ID.
- **QA GATE** (amber) — the standardized, skill-owned `qa_gate.py` process.
  Its four exit codes (`10`/`0`/`1`/`2`) branch the run: a round with findings
  feeds those findings back into evolution as selection pressure (dashed —
  see below); a verified pass goes to champion comparison; a verified fail
  goes to a fresh-session postmortem; a verified error or any
  verification-integrity problem ends the run without a promotion.
- **EVOLUTION** (purple) — `select_parents` fans out to the four variation
  operators (`repair_candidate`, `mutate_prompts`, `mutate_topology`,
  `recombine_candidates`), which fan back in at `merge_offspring`.

Terminals: `PROMOTED` (green, the one goal state) and five non-goal
terminals — `CONVERGENCE_EXHAUSTED`, `QA_GATE_FAILED`, `QA_ERROR`,
`QA_INTEGRITY_BREACH` (all red) — reached when budgets run out or the gate
cannot certify a pass. `CONVERGENCE_EXHAUSTED` sits directly beside
`decide_generation` in the main lane (matching where `graph.v1.png` puts its
own `EXHAUSTED` terminal next to `Decide Generation`), even though three
different nodes can reach it — it is the harness's most central "budget ran
out" outcome, so it earns the central position; the other two paths into it
(`compare_with_champion`, `merge_offspring`) route to it as ordinary elbows.

**Only one loop-back is drawn as the big outer rail**: `merge_offspring`'s
"next generation" edge back to `compile_population`, because that is the only
edge that genuinely restarts an earlier point in the run. The other two
feedback paths into evolution — a QA round's admitted findings, and losing
the champion race — land in the already-adjacent EVOLUTION zone one row down,
so they're drawn as short dashed elbows straight into `select_parents`
instead. An earlier iteration (`v2`) routed all three as separate rails
stacked along the bottom of the canvas; it was technically correct but
unreadable, and is the concrete example behind this schema's guidance to
reserve `style: "loop"` for a genuine restart.

Compression choices made when transcribing this from `run.prompt.md`, so a
future re-render from the same source lands on the same picture: consecutive
deterministic reducers with no branch between them were merged into one node
(`join_population` + `score_population` + `update_archive` →
`score_population → update_archive`; `open_qa_attempt` +
`prepare_qa_artifact`/`prepare_qa_revision` → one `open_qa_attempt →
prepare_qa_artifact` node; `qa_gate_start`/`qa_gate_round` → one
`qa_gate_start / qa_gate_round` node; `qa_gate_verify` +
`capture_qa_verification` → `qa_gate_verify`; `qa_gate_postmortem` +
`capture_qa_postmortem` → one node). The generic fail-closed edges to
`SYSTEM_FAILURE`/`INTERRUPTED` that exist on every node per `run.prompt.md`'s
guard table are not drawn individually — they would add ~28 near-identical
edges with no diagnostic value. The 24 remaining nodes are each a real,
separately named node in `run.prompt.md`'s own MODEL NODES / DETERMINISTIC
NODES / STANDARDIZED QA-GATE NODES tables — none are invented, and none of the
six model-authored prompt nodes in `prompts/` were dropped or merged.

## Reconstructing this diagram

```bash
python3 .claude/skills/harness-graph-create/scripts/render_graph.py \
  plans/23_graph_eng_evol_01/plan23.harness_graph.v3.json \
  -o plans/23_graph_eng_evol_01/plan23.harness_graph.v4.png
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
    {"id": "qa3", "label": "QA GATE", "role": "caution"},
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
    {"id": "dispatch_candidate_checks", "kind": "stage", "lane": "main", "col": 3, "label": "dispatch_candidate_checks"},
    {"id": "join_candidate_checks", "kind": "stage", "lane": "main", "col": 5, "label": "join_candidate_checks"},
    {"id": "score_and_archive", "kind": "stage", "lane": "main", "col": 6, "label": "score_population → update_archive"},
    {"id": "decide_generation", "kind": "gate", "lane": "main", "col": 7, "label": "decide_generation"},

    {"id": "test_candidate", "kind": "stage", "lane": "test", "col": 4, "label": "test_candidate", "detail": "public dev + regression"},
    {"id": "review_candidate", "kind": "stage", "lane": "review", "col": 4, "label": "review_candidate", "detail": "internal verdict only"},

    {"id": "prepare_qa_submission", "kind": "stage", "lane": "qa", "col": 8, "label": "open_qa_attempt → prepare_qa_artifact"},
    {"id": "qa_gate_run", "kind": "stage", "lane": "qa", "col": 9, "label": "qa_gate_start / qa_gate_round"},
    {"id": "capture_qa_result", "kind": "gate", "lane": "qa", "col": 10, "label": "capture_qa_result", "detail": "exit 10 / 0 / 1 / 2"},
    {"id": "verify_qa_result", "kind": "gate", "lane": "qa", "col": 11, "label": "qa_gate_verify"},
    {"id": "compare_with_champion", "kind": "gate", "lane": "qa", "col": 12, "label": "compare_with_champion"},
    {"id": "promote_prompt_graph", "kind": "stage", "lane": "qa", "col": 13, "label": "promote_prompt_graph"},
    {"id": "promoted", "kind": "terminal", "lane": "qa", "col": 14, "label": "PROMOTED", "role": "success"},

    {"id": "qa_postmortem", "kind": "stage", "lane": "qa2", "col": 11, "label": "qa_gate_postmortem"},
    {"id": "close_qa_attempt", "kind": "stage", "lane": "qa2", "col": 12, "label": "close_qa_attempt"},
    {"id": "qa_gate_failed", "kind": "terminal", "lane": "qa2", "col": 13, "label": "QA_GATE_FAILED", "role": "failure"},

    {"id": "qa_error", "kind": "terminal", "lane": "qa3", "col": 11, "label": "QA_ERROR", "role": "failure"},
    {"id": "qa_integrity_breach", "kind": "terminal", "lane": "qa3", "col": 12, "label": "QA_INTEGRITY_BREACH", "role": "failure"},

    {"id": "select_parents", "kind": "stage", "lane": "select", "col": 8, "label": "select_parents"},
    {"id": "repair_candidate", "kind": "stage", "lane": "op1", "col": 9, "label": "repair_candidate", "detail": "local findings only"},
    {"id": "mutate_prompts", "kind": "stage", "lane": "op2", "col": 9, "label": "mutate_prompts", "detail": "prompt genes only"},
    {"id": "mutate_topology", "kind": "stage", "lane": "op3", "col": 9, "label": "mutate_topology", "detail": "graph genes only"},
    {"id": "recombine_candidates", "kind": "stage", "lane": "op4", "col": 9, "label": "recombine_candidates", "detail": "two compatible parents"},
    {"id": "merge_offspring", "kind": "gate", "lane": "merge", "col": 10, "label": "merge_offspring"},
    {"id": "convergence_exhausted", "kind": "terminal", "lane": "main", "col": 8, "label": "CONVERGENCE_EXHAUSTED", "role": "failure"}
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

    {"from": "decide_generation", "to": "prepare_qa_submission", "label": "eligible", "style": "flow"},
    {"from": "decide_generation", "to": "select_parents", "label": "no eligible, evolve", "style": "flow"},
    {"from": "decide_generation", "to": "convergence_exhausted", "label": "no budget", "style": "flow"},

    {"from": "prepare_qa_submission", "to": "qa_gate_run", "style": "flow"},
    {"from": "qa_gate_run", "to": "capture_qa_result", "style": "flow"},
    {"from": "capture_qa_result", "to": "select_parents", "label": "exit 10: admit findings", "style": "check"},
    {"from": "capture_qa_result", "to": "verify_qa_result", "style": "flow"},

    {"from": "verify_qa_result", "to": "compare_with_champion", "label": "verified pass", "style": "flow"},
    {"from": "verify_qa_result", "to": "qa_postmortem", "label": "verified fail", "style": "flow"},
    {"from": "verify_qa_result", "to": "qa_error", "style": "flow"},
    {"from": "verify_qa_result", "to": "qa_integrity_breach", "label": "verification problem", "style": "check"},

    {"from": "compare_with_champion", "to": "promote_prompt_graph", "label": "eligible", "style": "flow"},
    {"from": "compare_with_champion", "to": "close_qa_attempt", "label": "ineligible", "style": "flow"},
    {"from": "compare_with_champion", "to": "convergence_exhausted", "label": "no budget", "style": "flow"},
    {"from": "promote_prompt_graph", "to": "promoted", "style": "flow"},
    {"from": "qa_postmortem", "to": "qa_gate_failed", "style": "flow"},
    {"from": "close_qa_attempt", "to": "select_parents", "label": "lost champion race", "style": "check"},

    {"from": "select_parents", "to": "repair_candidate", "style": "flow"},
    {"from": "select_parents", "to": "mutate_prompts", "style": "flow"},
    {"from": "select_parents", "to": "mutate_topology", "style": "flow"},
    {"from": "select_parents", "to": "recombine_candidates", "style": "flow"},
    {"from": "repair_candidate", "to": "merge_offspring", "style": "flow"},
    {"from": "mutate_prompts", "to": "merge_offspring", "style": "flow"},
    {"from": "mutate_topology", "to": "merge_offspring", "style": "flow"},
    {"from": "recombine_candidates", "to": "merge_offspring", "style": "flow"},
    {"from": "merge_offspring", "to": "compile_population", "label": "next generation", "style": "loop"},
    {"from": "merge_offspring", "to": "select_parents", "label": "shortfall", "style": "check"},
    {"from": "merge_offspring", "to": "convergence_exhausted", "style": "flow"}
  ]
}
```
