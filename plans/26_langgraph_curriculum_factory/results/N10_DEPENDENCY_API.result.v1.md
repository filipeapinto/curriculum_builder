# N10_DEPENDENCY_API result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N10_dependency_api.prompt.v2.md (f0488a7a2bf9f161041db7a9a672f67c1ad8fe309f5242e941062d346c2d288b)
generation: 2

## Inputs

- `N00_BASELINE_FREEZE: c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5`
- `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml`: `96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8`
- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` (sections 3.1-3.3, 20.2): `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`
- `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md`: `896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af`
- `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md`: `063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0`
- `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md`: `c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2`
- `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md`: `d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad`
- `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md`: `7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7`
- `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md`: `edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b`

## Outputs

- `requirements/plan26.in`: `155bf4bb188b3a5ff38bf1284b32b0ed38c8540d2c5235795341731588dd4d94`
- `requirements/plan26.lock`: `df971a783b9d027db96eae800e33e7bc65471b94f7a3b0a151eec075e0824835`
- `.github/workflows/plan26-lock-drift.yml`: `b10b933f5f9abd6b4760d43988f3ac3d3c5907692df94eb608227f825120925b`
- `tests/runtime/test_plan26_api_contract.py`: `773834e14b01a17e50f89535ab4a5967d55832512568741d3eaf4ff2156eae28`
- `tests/runtime/test_plan26_lock_drift.py`: `3f134dcaf6efca2a754eb6746777b2ab26971a40298ffe6b242c85e1d4b04510`
- `plans/26_langgraph_curriculum_factory/results/N10_DEPENDENCY_API.result.v1.md`: this file (hashed externally per result_record_schema.v1 hash discipline)

No path in the node `writes` set is `NOT_CREATED`.

## Commands

All commands run from repository root `/Users/filipepinto/Projects/curriculum_builder`
unless a `cwd` is stated. Every captured output was under 4 KiB after
truncation to its verdict line, so verdicts are inlined here rather than
referenced to a separate evidence file; no evidence path outside this node's
`writes` set was created.

| # | Command | Exit | Evidence |
|---|---|---:|---|
| 1 | `which pip-compile uv` | 1 | neither pinned generator preinstalled; throwaway venv built instead |
| 2 | `curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://pypi.org/simple/` | 0 | `200` — PyPI reachable, so no hash-lock blocker |
| 3 | `/opt/homebrew/bin/python3 -m venv /tmp/plan26_lockgen` | 0 | throwaway generator venv, outside the repo |
| 4 | `/tmp/plan26_lockgen/bin/python -m pip install pip-tools` | 0 | installed `pip-tools 7.6.0` on `pip 26.2.1` |
| 5 | `/tmp/plan26_lockgen/bin/pip-compile --generate-hashes --no-header --strip-extras --output-file requirements/plan26.lock requirements/plan26.in` | 1 | `TypeError: RequirementCommand.make_requirement_preparer() missing 1 required keyword-only argument: 'allow_editables'` — pip 26.x/pip-tools 7.6.0 incompatibility, see Findings F1 |
| 6 | `/tmp/plan26_lockgen/bin/python -m pip install "pip==25.3"` | 0 | generator pip pinned to the compatible major |
| 7 | `/tmp/plan26_lockgen/bin/pip-compile --generate-hashes --no-header --strip-extras --output-file requirements/plan26.lock requirements/plan26.in` | 0 | 48 distributions, 1142 `--hash=sha256:` entries |
| 8 | `/opt/homebrew/bin/python3 -m venv /tmp/plan26_verify` | 0 | clean environment with no prior Plan 26 packages |
| 9 | `/tmp/plan26_verify/bin/python -m pip install --require-hashes -r requirements/plan26.lock` | 0 | clean-environment hash-verified install succeeded |
| 10 | `/tmp/plan26_verify/bin/python -c "import langgraph, langgraph.checkpoint.sqlite; ..."` | 0 | `py 3.13.1`, `langgraph 1.2.9`, `ckpt-sqlite 3.1.0` |
| 11 | `/tmp/plan26_verify/bin/python -m pytest -q tests/runtime/test_plan26_api_contract.py` | 0 | `19 passed, 30 subtests passed` |
| 12 | `diff -u requirements/plan26.lock <regenerated copy in temp dir>` | 0 | byte-identical; both sides `df971a78...4835` |
| 13 | `/opt/homebrew/bin/python3 -m pytest -q tests/runtime/test_plan26_lock_drift.py` | 0 | `19 passed, 1 skipped, 70 subtests passed` (ambient python lacks the pinned generator, so regeneration skips) |
| 14 | `/tmp/plan26_lockgen/bin/python -m pytest -q tests/runtime/test_plan26_lock_drift.py` | 0 | `20 passed, 70 subtests passed` — regeneration test ran for real |
| 15 | `git init` in temp dir; `sed -i '' 's/langgraph==1.2.9/langgraph==1.2.8/' requirements/plan26.in`; `python -m piptools compile --generate-hashes --no-header --strip-extras --output-file requirements/plan26.lock requirements/plan26.in`; `git diff --exit-code -- requirements/plan26.lock` | 1 | controlled pin change: `3 3 requirements/plan26.lock`, diff shows `-langgraph==1.2.9` / `+langgraph==1.2.8` with both hash lines replaced |
| 16 | `/tmp/plan26_lockgen/bin/python -m pip install --require-hashes -r requirements/plan26.lock` | 0 | CI-mirroring env: pinned generator + hash-locked runtime in one interpreter |
| 17 | `/tmp/plan26_lockgen/bin/python -m pytest -q tests/runtime/test_plan26_api_contract.py tests/runtime/test_plan26_lock_drift.py` | 0 | `39 passed, 100 subtests passed` — the exact CI test step, nothing skipped |
| 18 | `/opt/homebrew/bin/python3 -m pytest -q` | 0 | `194 passed, 2 skipped, 124 subtests passed in 102.79s` |

Command 18 versus the N00 baseline (`175 passed, 54 subtests, zero failures`):
`+19 passed` and `+70 subtests` are exactly this node's static lock-drift tests;
the 2 skips are `test_plan26_api_contract.py` (whole module, ambient interpreter
has no `langgraph`) and `test_regeneration_is_byte_identical_to_the_committed_lock`
(ambient interpreter has no pinned generator). Zero pre-existing tests changed
state, so the baseline is preserved.

Environments used (none committed to the repository):
`/tmp/plan26_lockgen` (generator: CPython 3.13.1, `pip==25.3`, `pip-tools==7.6.0`)
and `/tmp/plan26_verify` (clean-environment proof: CPython 3.13.1, lock only).

## Tests

Prompt TEST items, each mapped to the assertion that backs it:

| TEST item | Verdict | Backing assertion |
|---|---|---|
| 1. Direct pins and complete hash lock reproduce in a clean environment | PASS | Command 9: `pip install --require-hashes -r requirements/plan26.lock` exit 0 in a venv created fresh from `python3 -m venv`; command 10 confirms `langgraph 1.2.9` / `langgraph-checkpoint-sqlite 3.1.0` on CPython 3.13.1. `TestLockCompleteness.test_every_locked_distribution_carries_at_least_one_sha256_hash` checks all 48 distributions; `test_lock_is_installable_with_require_hashes_semantics` rejects any unpinned line. |
| 2. API tests prove `StateGraph`, reducers, `START`, `END`, conditional edges, `Send`, compile/invoke/state/history, and `SqliteSaver` pending-write behavior | PASS | `test_plan26_api_contract.py`, 19 tests / 30 subtests, exit 0 (command 11). `TestApiSignatures` proves `StateGraph(state_schema, context_schema, input_schema, output_schema)`, `compile(checkpointer=, name=)`, `Send(node, arg)`, `add_node`/`add_edge`/`add_conditional_edges`, `CompiledStateGraph.invoke`/`get_state`/`get_state_history`, `SqliteSaver(conn)` + `get_tuple`/`list`. `TestGraphBehavior` executes an `Annotated` reducer graph (`operator.add` accumulation, output_schema filtering `secret` out), a two-way conditional branch, a conditional-edge loop terminating at 3 attempts, and a `Send` fan-out of 3 workers joining once at a barrier (`barrier == [3]`). `TestSqliteSaverBehavior.test_pending_writes_survive_a_failed_superstep` fails one of two parallel tasks, asserts channel `ok` is present in `CheckpointTuple.pending_writes`, and asserts on resume `resumed["ok"].count("good") == 1` (completed task replayed its write rather than re-running). |
| 3. SQLite saver works synchronously with the selected Python/package versions | PASS | `TestSqliteSaverBehavior.test_invoke_get_state_and_history_over_saver`: synchronous `SqliteSaver` over `sqlite3.connect(path, check_same_thread=False)`, compiled with `name="plan26_curriculum_factory"`, thread id `run:episode:000001`, `checkpoint_ns == ""`; asserts `snapshot.next == ()`, accumulated `seen == ["first","second"]`, `len(get_state_history) > 1` with unique checkpoint ids, `saver.get_tuple(config)` non-None with matching thread id/ns, `len(saver.list(config)) > 1`. |
| 4. Import audit rejects LangChain wrappers, provider SDKs, and model HTTP clients | PASS | `TestForbiddenImports.test_forbidden_model_wrappers_absent_from_locked_environment` proves `langchain`, `langchain_openai`, `langchain_google_genai`, `openai`, `google.generativeai` have no importable spec in the hash-locked environment. `TestForbiddenDependencyAudit` proves the same five distributions are absent from both `plan26.in` and the resolved lock. `test_langchain_core_is_transitive_and_langchain_umbrella_is_not` pins the authorized exception: `langchain-core==1.5.3` is present transitively while the `langchain` umbrella is not, and `langchain-core` is not a direct pin. |
| 5. Lock regeneration is byte-identical on pass, and a controlled pin/hash change fails the same CI command with a nonempty drift report | PASS | Pass direction: command 12 (`diff -u` exit 0, identical sha256 `df971a78...4835`) and command 14 (`test_regeneration_is_byte_identical_to_the_committed_lock` executed, not skipped). Fail direction: command 15 ran the literal CI command pair after changing `langgraph==1.2.9` to `1.2.8` and `git diff --exit-code` returned exit 1 with a 3-added/3-removed-line drift report. Offline mutation coverage: `TestDriftDetection.test_a_controlled_hash_change_...` (first `--hash=sha256:` corrupted) and `..._pin_change_...` both assert diff exit 1 with nonempty output, and `test_identical_lock_produces_an_empty_drift_report` asserts exit 0 / empty stdout. |
| 6. The committed CI configuration invokes that exact lock-drift command; deleting the CI step or the test fails a static ownership test | PASS | `TestCiOwnership`, 7 tests. `test_workflow_invokes_the_exact_regeneration_command` asserts the workflow contains the byte-exact `REGENERATE_COMMAND` constant; `test_workflow_fails_the_build_on_drift` asserts `git diff --exit-code -- requirements/plan26.lock`; `test_workflow_pins_the_lock_generator` asserts `"pip-tools==7.6.0"` and `"pip==25.3"`; `test_workflow_installs_with_require_hashes` asserts the `--require-hashes` install; `test_workflow_runs_both_plan26_dependency_tests` asserts both test paths are named in the workflow, so removing either from CI fails here; `test_workflow_is_valid_yaml_and_triggers_on_push_and_pull_request` and `test_workflow_uses_python_3_13` bound the trigger and interpreter. `setUp` fails outright if the workflow file is deleted. |

Full-suite regression: command 18, `python3 -m pytest -q`, exit 0,
`194 passed, 2 skipped, 124 subtests passed`, zero failures.

## Findings

- **F1 — pip-tools 7.6.0 requires pip 25.x; pip 26.x breaks lock regeneration.**
  Owner: N10 (resolved in-node, no rework edge fired). Evidence key: command 5
  exit 1, `TypeError: RequirementCommand.make_requirement_preparer() missing 1
  required keyword-only argument: 'allow_editables'`. Fingerprint:
  `piptools-7.6.0/pip-26.x-make_requirement_preparer-signature`. Resolution: the
  regenerating pip is pinned alongside pip-tools in both
  `.github/workflows/plan26-lock-drift.yml` and the test constants
  (`PIP_VERSION_FOR_GENERATION = "25.3"`, `PIP_TOOLS_VERSION = "7.6.0"`). This
  constrains only the lock-generation toolchain; the hash-verified runtime
  install in command 9 used the venv's own pip 24.3.1 unmodified, so runtime
  reproducibility does not depend on the generator pin.
- **F2 — `test_plan26_api_contract.py` self-skips where the locked environment
  is absent.** Owner: N10. Evidence key: command 13 / command 18 skip counts.
  Fingerprint: `api-contract-module-skip-without-lock-env`. This keeps the
  repository's ambient `python3 -m pytest -q` green (baseline preservation) while
  the CI job installs the lock with `--require-hashes` and therefore always runs
  the module for real, as proven by command 17 (`39 passed`, nothing skipped) and
  enforced by `TestCiOwnership.test_workflow_runs_both_plan26_dependency_tests`.
  Not a blocking finding; the gate cannot silently disappear.
- **F3 — `langsmith` transitively pulls `httpx`/`requests` into the lock.**
  Owner: N13 (`transport.py`/`egress.py` per `rework_edges`). Evidence key:
  `requirements/plan26.lock` lines for `httpx==0.28.1`, `requests==2.34.2`.
  Fingerprint: `langsmith-transitive-http-clients`. Spec section 3.1 forbids "any
  HTTP client introduced to call a model endpoint"; these are resolved
  transitively by `langgraph` -> `langchain-core` -> `langsmith` and are not
  introduced by Plan 26. They are not in the forbidden-distribution list and no
  Plan 26 module may import them to reach a model endpoint. N13 owns proving the
  production path calls models only through `codex exec`/`gemini` subprocess
  transport with egress restriction.

No blocking finding is open. Spec section 20.2's first external prerequisite
("generate and commit the hash lock from the selected pins, then run the
specified API-contract smoke test against the 1.2.9 wheel") is discharged by this
node; the remaining 20.2 prerequisites (CLI identity, authorization record, live
credentials, sandbox denial) are outside N10's ownership.

## Invalidated descendants

None. First-pass `PASSED`; no rework edge fired.

## Hashes

Repository files (sha256 over raw bytes, per `digest_algorithm.v1`):

| Path | sha256 |
|---|---|
| `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` | `96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8` |
| `plans/26_langgraph_curriculum_factory/prompts/N10_dependency_api.prompt.v2.md` | `f0488a7a2bf9f161041db7a9a672f67c1ad8fe309f5242e941062d346c2d288b` |
| `plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md` | `c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5` |
| `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` | `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` |
| `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md` | `896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af` |
| `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md` | `063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0` |
| `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md` | `c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2` |
| `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md` | `d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad` |
| `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md` | `7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7` |
| `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md` | `edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b` |
| `requirements/plan26.in` | `155bf4bb188b3a5ff38bf1284b32b0ed38c8540d2c5235795341731588dd4d94` |
| `requirements/plan26.lock` | `df971a783b9d027db96eae800e33e7bc65471b94f7a3b0a151eec075e0824835` |
| `.github/workflows/plan26-lock-drift.yml` | `b10b933f5f9abd6b4760d43988f3ac3d3c5907692df94eb608227f825120925b` |
| `tests/runtime/test_plan26_api_contract.py` | `773834e14b01a17e50f89535ab4a5967d55832512568741d3eaf4ff2156eae28` |
| `tests/runtime/test_plan26_lock_drift.py` | `3f134dcaf6efca2a754eb6746777b2ab26971a40298ffe6b242c85e1d4b04510` |

Selected package hashes (the two Plan 26 core packages plus the transitive
checkpoint core; the full 1142-hash table is `requirements/plan26.lock` itself,
whose file digest is recorded above):

| Distribution | sha256 (wheel, sdist) |
|---|---|
| `langgraph==1.2.9` | `385f87bc1802c35af7e0aa479278ecba8582d103515eb48256cb2ddcd42d0bd4`, `c2d98ad94333937922ba04148641c1da2bfe45b5b8e55d7b6dcb0bb2df809e76` |
| `langgraph-checkpoint-sqlite==3.1.0` | `cc9b40df0076feae8a9ad42ae713621b148b00ac23adc09dc1dc66090a46e5ad`, `f926916ebc1b985d802cc9c820026036e84db9d910d62c97b57e4ba64f67d5ae` |
| `langgraph-checkpoint==4.2.0` | `0547fd228935a0b758865de3a3d6d7a2537c308895d0f9ab092ce9151b5da942`, `51a593b6bee684b0818e5d6e58e28ab340c6db7794575056ce7bd1b746a84ed7` |

Resolution shape: 48 distributions, 1142 `--hash=sha256:` entries, 6 direct
pins, transitive `langchain-core==1.5.3` (authorized as transitive only), zero
forbidden distributions.
