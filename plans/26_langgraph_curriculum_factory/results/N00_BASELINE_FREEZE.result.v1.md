# N00_BASELINE_FREEZE result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N00_baseline_freeze.prompt.v1.md (fdf358591c1d027c909e17ffaf856e07848c95967667a461cf684f1ae545cede)
generation: 1

## Inputs

- `plans/26_langgraph_curriculum_factory/run.prompt.md` (d615f90d0e4f8614f689166f85fe3d0b1c9303b3cbcf9e27956677950f7a5573)
- `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` (96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8)
- `plans/26_langgraph_curriculum_factory/implementation.graph.schema.v2.json` (3bc685b87fe49f62cfe6178e47d9c0f57b6d067f4d17d2760a46c5f4decf90b4)
- `plans/26_langgraph_curriculum_factory/qa_criteria.v2.md` (163154480dc0a851ca597fdfaf62a71840a2cdd212fad8fa196b02dc152edded)
- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` (44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6), read complete (sections 0-21, lines 1-899)
- current `runtime/` Plan 25 controller (`controller.py`, `curriculum_factory_graph.py`, `factory_state.py`, `checkpoint.py`, `run_curriculum.py`, `model_worker.py`, `run_state.py`, `session_bridge.py`, `workbook.py`), directory-listed to confirm names cited by spec section 2.3/18 exist
- current `tests/runtime/` directory listing
- repository root: confirmed no `pyproject.toml`/`setup.py`/`setup.cfg`/`requirements*`/`.github/workflows/` exist yet (pre-N10 state)

No predecessor result records exist; N00 is the entry node.

## Outputs

- `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md` (896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af)
- `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md` (063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0)
- `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md` (d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad)
- `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md` (c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2)
- `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md` (edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b)
- `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md` (7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7)
- `plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md` (this file; not self-hashed per [[result_record_schema.v1]])

No production path (`runtime/`, `tests/`, `requirements/`) was written by N00.
`plans/26_langgraph_curriculum_factory/contracts` was empty before this node
and now contains exactly the six files above.

## Commands

- `python3 -m pytest -q` — exit 0 — evidence inline in [[baseline.v1]] (`175 passed, 54 subtests passed in 100.80s`)
- `shasum -a 256 <path>` for every hashed path above — exit 0 each
- `git status --porcelain=v1` — exit 0, output recorded verbatim in [[baseline.v1]]
- `git rev-parse HEAD` — exit 0 — `ac7ff3a7507c2adefbcbbd3e5d3938edf1924a39`
- `python3 --version` — exit 0 — `Python 3.13.1`
- `python3 -c "import langgraph"` — exit 1 (`ModuleNotFoundError`), expected pre-N10, recorded as baseline fact not a failure of this node
- `which codex gemini` — exit 0 — both resolved on `PATH`

## Tests

1. Every normative Plan 26 requirement has exactly one owning node — PASS. [[traceability_matrix.v1]] assigns every spec section (0-21), every QA criterion, and every section-17.2 adversarial case to exactly one N-node; cross-checked line by line against `implementation.graph.v2.yaml` write sets, no duplicate primary ownership found.
2. D00-D98 and exactly M01-M08 have complete dispositions — PASS. [[node_ownership.v1]] table enumerates all 40 named D-nodes from spec section 6.2 (D00, D00R, D01-D32, D90, D91, D92, D96, D98) and all 8 M-nodes (M01-M08); count verified by manual enumeration against the spec catalogue, no omission, no node assigned to two owners.
3. Every shared artifact has one writer; graph-parallel write sets are disjoint — PASS. Verified against `implementation.graph.v2.yaml`: the N00 fan-out (N10/N11/N12/N13) writes four disjoint path sets; the N11/N12/N13-gated set (N21, N22, N23) that can become concurrently ready writes three disjoint path sets (`persistence.py` / `nodes/`+`terminal.py` / `model_nodes.py`); N20 (gated additionally on N22+N23) and N21 can be concurrently ready and write disjoint paths (`graph.py`+`routing.py` / `persistence.py`). [[node_ownership.v1]]'s resolution of the spec's illustrative duplicate basenames (`repair.py`, `workbook.py`) into one top-level file per concept removes the only naming collision found in the spec's own proposed layout (section 15); the sequential `graph.py` edits by N20 then N30 then N32 are same-file but never concurrent (N30 depends on N20 `all_of`; N32 depends on N31 which depends on N30), so no write-set conflict exists at any single scheduler generation.
4. The result-record schema requires status, inputs, outputs, hashes, commands, exit codes, tests, findings, and invalidated descendants — PASS. [[result_record_schema.v1]] defines exactly this section set, in order, and this record instantiates it.
5. Baseline tests and dirty paths are recorded without modification — PASS. [[baseline.v1]] records the pre-N00 `git status --porcelain` output and `pytest -q` result verbatim; both were captured before any write in this node and neither command's target files were touched by N00.
6. No framework substitution or weakened product requirement is introduced — PASS. All six contract files affirm LangGraph as the sole orchestration mechanism, preserve the eight-model-job/no-wrapper constraint, keep every routing/acceptance/terminal authority code-owned, and introduce no new terminal, bypass, or simulation path beyond spec section 14's six.

## Findings

None open.

## Invalidated descendants

None (first-pass PASSED, no rework).

## Hashes

See per-section inline hashes above; consolidated:

```
96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8  implementation.graph.v2.yaml
3bc685b87fe49f62cfe6178e47d9c0f57b6d067f4d17d2760a46c5f4decf90b4  implementation.graph.schema.v2.json
44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6  spec/langgraph_curriculum_factory.spec.v1.md
163154480dc0a851ca597fdfaf62a71840a2cdd212fad8fa196b02dc152edded  qa_criteria.v2.md
fdf358591c1d027c909e17ffaf856e07848c95967667a461cf684f1ae545cede  prompts/N00_baseline_freeze.prompt.v1.md
d615f90d0e4f8614f689166f85fe3d0b1c9303b3cbcf9e27956677950f7a5573  run.prompt.md
896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af  contracts/baseline.v1.md
063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0  contracts/digest_algorithm.v1.md
d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad  contracts/result_record_schema.v1.md
c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2  contracts/node_ownership.v1.md
edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b  contracts/traceability_matrix.v1.md
7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7  contracts/shared_names_and_paths.v1.md
```
