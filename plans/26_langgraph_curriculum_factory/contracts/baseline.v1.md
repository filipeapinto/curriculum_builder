# N00 baseline record (frozen)

Frozen at graph digest below. Any later divergence from these values is a
finding, not a silent update.

## Repository baseline

- HEAD commit: `ac7ff3a7507c2adefbcbbd3e5d3938edf1924a39`
- Commit date: `2026-08-11 10:42:59 -0400`
- Python: `3.13.1` at `/opt/homebrew/bin/python3`
- `codex` CLI present at `/opt/homebrew/bin/codex`; `gemini` CLI present at
  `/opt/homebrew/bin/gemini` (presence only; D03 alone may prove executable
  identity/version/capability).
- `langgraph` NOT importable in the current environment (`ModuleNotFoundError`).
  This is expected pre-N10 and MUST be resolved only through
  `requirements/plan26.lock` (N10), never an ad hoc `pip install`.
- No `.github/workflows/` directory exists yet. N10 creates
  `plan26-lock-drift.yml` as a new file, not a merge into an existing workflow.
- No `pyproject.toml`/`setup.py`/`setup.cfg`/`requirements*` exists at repo
  root. N10 introduces `requirements/plan26.in` and `requirements/plan26.lock`
  as the first dependency contract in this repository.

## Baseline test command and result

Command:

```bash
python3 -m pytest -q
```

Result: `175 passed, 54 subtests passed in 100.80s (0:01:40)`, zero failures,
zero errors, zero skips. This is the pre-Plan-26 green baseline. Any Plan 26
node that leaves this command red without an explicit, owned, in-progress
finding has regressed unrelated work and must self-block.

## Dirty worktree at N00 start

`git status --porcelain=v1` at N00 start (recorded verbatim, not modified by
N00):

```
 M plans/26_langgraph_curriculum_factory/README.md
 D plans/26_langgraph_curriculum_factory/implementation.graph.schema.v1.json
 D plans/26_langgraph_curriculum_factory/implementation.graph.v1.yaml
 D plans/26_langgraph_curriculum_factory/prompts/N10_dependency_api.prompt.v1.md
 D plans/26_langgraph_curriculum_factory/prompts/N13_transport_authorization.prompt.v1.md
 D plans/26_langgraph_curriculum_factory/prompts/N20_graph_compiler.prompt.v1.md
 D plans/26_langgraph_curriculum_factory/prompts/N22_deterministic_nodes.prompt.v1.md
 D plans/26_langgraph_curriculum_factory/prompts/N31_repair_acceptance.prompt.v1.md
 D plans/26_langgraph_curriculum_factory/prompts/N32_workbook_terminals.prompt.v1.md
 D plans/26_langgraph_curriculum_factory/prompts/N50_adversarial_regression.prompt.v1.md
 D plans/26_langgraph_curriculum_factory/qa_criteria.v1.md
 M plans/26_langgraph_curriculum_factory/run.prompt.md
?? plans/26_langgraph_curriculum_factory/deprecated/
?? plans/26_langgraph_curriculum_factory/implementation.graph.schema.v2.json
?? plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml
?? plans/26_langgraph_curriculum_factory/prompts/N10_dependency_api.prompt.v2.md
?? plans/26_langgraph_curriculum_factory/prompts/N13_transport_authorization.prompt.v2.md
?? plans/26_langgraph_curriculum_factory/prompts/N20_graph_compiler.prompt.v2.md
?? plans/26_langgraph_curriculum_factory/prompts/N22_deterministic_nodes.prompt.v2.md
?? plans/26_langgraph_curriculum_factory/prompts/N31_repair_acceptance.prompt.v2.md
?? plans/26_langgraph_curriculum_factory/prompts/N32_workbook_terminals.prompt.v2.md
?? plans/26_langgraph_curriculum_factory/prompts/N50_adversarial_regression.prompt.v2.md
?? plans/26_langgraph_curriculum_factory/prompts/deprecated/
?? plans/26_langgraph_curriculum_factory/qa_criteria.v2.md
```

Every dirty path is confined to `plans/26_langgraph_curriculum_factory/`
(the v1->v2 graph/prompt migration itself). No path under `runtime/`,
`tests/`, `curricula/`, or repo root is dirty. N00 therefore treats this dirty
set as pre-existing, in-scope plan authoring, not unrelated user work, and
does not touch, stage, or revert it. No production edit occurred during N00.

## Baseline artifact digests (SHA-256)

```
96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8  plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml
3bc685b87fe49f62cfe6178e47d9c0f57b6d067f4d17d2760a46c5f4decf90b4  plans/26_langgraph_curriculum_factory/implementation.graph.schema.v2.json
44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6  plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md
163154480dc0a851ca597fdfaf62a71840a2cdd212fad8fa196b02dc152edded  plans/26_langgraph_curriculum_factory/qa_criteria.v2.md
```

Computed with `shasum -a 256 <path>` (macOS/BSD toolchain, matches
[[digest_algorithm.v1]]).
