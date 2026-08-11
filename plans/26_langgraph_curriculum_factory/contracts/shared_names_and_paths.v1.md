# N00 frozen shared names and paths

Canonical reference for every later node. Derived from
`implementation.graph.v2.yaml` write sets plus the resolutions in
[[node_ownership.v1]]. A later node prompt citing a path not listed here (or
citing it differently) has drifted from the frozen contract and must be
reconciled against this file, not the other way around.

## Package layout (final, resolved)

```text
runtime/langgraph_factory/
  __init__.py                # N11 (created alongside state.py)
  state.py                   # N11 — FactoryInput, FactoryState, FactoryOutput,
                              #        RuntimeContext (TypedDict/frozen dataclass)
  reducers.py                # N11 — write_once, append_unique, union_disjoint,
                              #        advance_head, replace_current,
                              #        monotonic_status, monotonic_max,
                              #        accept_once, write_episode_terminal_once
  evidence.py                 # N12 — append-only ACT/EXEC evidence writer
  artifacts.py                 # N12 — artifact version/head records
  transport.py                # N13 — Codex/Gemini subprocess transport
  egress.py                   # N13 — network/process egress restriction
  config/model_jobs.v1.yaml   # N13 — frozen job-to-task/family/model routes
  schemas/                    # N13 — eight model output schemas + internal receipts
  prompts/                    # N13 — eight package-relative model prompts
  graph.py                    # N20 (created) + N30 (extended) + N32 (extended)
                              #   — build_curriculum_factory_graph(), RuntimeContext factory
  routing.py                  # N20 — pure guard functions (section 8.2 table)
  persistence.py               # N21 — prepare_episode_invocation(), SqliteSaver wiring
  nodes/
    inputs.py                  # N22 — D00, D00R, D01, D02, D03, D04, D92, D96
    sources.py                  # N22 — D05, D06, D06B, D07, D30
    domain.py                   # N22 — D08
    content.py                  # N22 — D09
    visuals.py                  # N22 — D10, D11, D12
    render.py                   # N22 — D13, D14
    review.py                   # N22 — D15
    terminal.py                 # N22 — D98 writer (all six terminals; N32 calls it
                                #        for UNIT_ACCEPTED/COMPLETE)
  model_nodes.py               # N23 — M01-M08, D90, D91
  unit_graph.py                # N30 — per-unit Send fan-out/loop registration
  repair.py                    # N31 — D17, D18, D19, D20, D21 (shared engine)
  acceptance.py                # N31 — D16, D22, D23 (unit); D28 reuses this engine
  workbook.py                  # N32 — D24, D25, D26, D27, D29, D31, D32

runtime/run_curriculum.py      # N40 — sole production CLI entry (adapted, not new)

requirements/plan26.in         # N10
requirements/plan26.lock       # N10
.github/workflows/plan26-lock-drift.yml   # N10

tests/runtime/
  test_plan26_api_contract.py        # N10
  test_plan26_lock_drift.py          # N10
  test_plan26_state_reducers.py      # N11
  test_plan26_evidence.py            # N12
  test_plan26_transport.py           # N13
  test_plan26_egress.py              # N13
  test_plan26_topology.py            # N20
  test_plan26_persistence.py         # N21
  test_plan26_deterministic_nodes.py # N22
  test_plan26_model_nodes.py         # N23
  test_plan26_unit_graph.py          # N30
  test_plan26_repair_acceptance.py   # N31
  test_plan26_workbook.py            # N32
  test_plan26_cli.py                 # N40
  test_plan26_adversarial.py         # N50

plans/26_langgraph_curriculum_factory/
  contracts/                          # N00 (this directory)
  results/{node_id}.result.v1.md      # every node
```

No `context.py` file (see [[node_ownership.v1]] "context.py gap").
No `nodes/repair.py` or `nodes/workbook.py` (basenames reserved for the
top-level engine modules instead).

## Frozen names used across node prompts

- Builder entry point: `runtime.langgraph_factory.graph.build_curriculum_factory_graph(*, engine_root: Path, output_root: Path) -> CompiledStateGraph`.
- Pre-invocation helper: `runtime.langgraph_factory.persistence.prepare_episode_invocation()`.
- CLI module: `python3 -m runtime.run_curriculum`.
- Compiled graph `name=` argument: `"plan26_curriculum_factory"` (spec section 3.3).
- Checkpoint DB path: `<output_root>/.langgraph/checkpoints.sqlite3`; lock:
  `<output_root>/.langgraph/execution.lock`.
- Thread ID format: `f"{run_id}:episode:{episode_ordinal:06d}"`; orphan
  recovery: `f"{run_id}:recover:{orphan_episode_ordinal}"`.
- `checkpoint_ns` is always `""`.

## Forbidden production imports (repeated from graph rule, binding on every node)

`langchain`, `langchain_openai`, `langchain_google_genai`, `openai`,
`google.generativeai`. N10's lock-drift/API-contract tests are the
enforcement point; every other node MUST NOT introduce these regardless.
