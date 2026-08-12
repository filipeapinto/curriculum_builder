# N50_ADVERSARIAL_REGRESSION result

status: PASSED

## 1. What was built

`tests/runtime/test_plan26_adversarial.py` (new, 1841 lines) implements the
complete spec section 17.2 mandatory adversarial matrix as 26 executable
tests, one per table row, using the exact verification-test names the spec
names. Each test drives real production APIs in
`runtime/langgraph_factory/*` and `runtime/run_curriculum.py` (not mocks of
Plan 26 code) — the compiled `StateGraph`, `SqliteSaver`-backed persistence,
`FakeCliTransport` schema validation, real OS-level `SIGKILL` child
processes, and static AST audits of the CLI source. It does not duplicate
prior nodes' test suites; it composes their proven primitives (documented
per-row below) and adds four genuinely new cross-episode/cross-process
compositions that no earlier node exercised: a real fresh→resume two-episode
run, a real SIGKILL→recovery run through the actual compiled graph, a
reserve-before-block ordering proof for the repair bound, and an
exactly-twice proof for the mixed static/dynamic visual barrier.

## 2. Row-to-test matrix (spec 17.2)

| # | Attack/fault (spec row) | Verification test | Locus |
|---|---|---|---|
| 1 | graph/test/prompt/capability/simulation presented as product | `test_no_nonproduct_success` | new file; cites `transport.FakeCliTransport` root refusal, `unit_graph` unreachability of D22/D24 from the test path |
| 2 | manifest has 1, 7, or 41 shuffled/DAG units | `test_manifest_neutral_dynamic_run` | new file; `inputs.D02_COMPILE_EFFECTIVE_RUN` over a synthetic linear-chain DAG, 3 unit counts x 3 shuffle seeds (9 cases) |
| 3 | source/model output proposes next node/acceptance/terminal | `test_models_have_no_control_fields` | new file; poisoned `next_node`/`terminal`/`accepted` fields rejected by schema |
| 4 | prompt resolved from cwd or root `prompts/` | `test_prompts_are_package_relative` | new file; cwd decoy + path-substitution rejection |
| 5 | malformed/multiple/trailing CLI JSON | `test_malformed_cli_output_fails_closed` | new file; one bounded retry then failure via `tp.parse_single_json_document` / `tp.AttemptLedger` |
| 6 | decided model differs from observed executed model | `test_executed_model_must_match_route` | new file; `tp.assert_identity_matches` |
| 7 | reviewer family equals any author/repair family | `test_same_family_review_rejected` | new file |
| 8 | missing/duplicate/extra/stale/cross-unit fan-out member | `test_exact_fanout_denominators` | new file; both source and visual join loci, `P.classify_join_members` + real D07/D12 |
| 9 | page 0, gap, duplicate, wrong hash, or omitted unit review page | `test_every_unit_page_required` | new file; `mn.m05_review_actual_unit` |
| 10 | page 0, gap, duplicate, wrong hash, or omitted workbook review page | `test_every_workbook_page_required` | new file; `mn.m07_review_actual_workbook` |
| 11 | stale artifact/check/review/receipt hash | `test_stale_hash_rejected` | new file; `P.validate_resume_inputs` + `repair.D20_ADMIT_UNIT_REPAIR` |
| 12 | repair changes unrelated pointer/file or parent in place | `test_repair_boundary_and_immutability` | new file; `repair.within_boundary` / `json_pointer_diff` |
| 13 | local defect attempts whole-unit regeneration | `test_local_repair_is_targeted` | new file; positive scoped admit + broad-repair refusal in one test |
| 14 | counter/fingerprint exceeds frozen bound | `test_repair_bound_reserved_first` | new file; proves the counter commits in the same update that blocks the next child, not merely that it eventually blocks |
| 15 | resume tries to rewrite accepted unit/PDF | `test_resume_preserves_accepted_bytes` | new file; byte-tree snapshot identical after a refused resume |
| 16 | two resume processes | `test_duplicate_continuation_prevented` | new file; real second OS process, `P.LOCK_LOSER_EXIT_CODE` |
| 17 | workbook missing/extra/reordered accepted unit | `test_workbook_exact_manifest_coverage` | new file; `acceptance.prove_exact_manifest_coverage` |
| 18 | workbook repair changes any unit hash | `test_workbook_repair_cannot_change_unit` | new file |
| 19 | legacy FSM/session bridge/simulation flag on Plan 26 | `test_no_second_production_factory` | new file; static AST audit of `runtime/run_curriculum.py` |
| 20 | absent OpenAI/Google/retrieval authorization | `test_external_data_authorization_precedes_transmission` | new file; 7-way scope-mismatch matrix + `EgressGuard` zero-connection proof |
| 21 | sibling files visible in worker | `test_worker_context_is_structurally_bounded` | new file; `tp.prove_workspace_isolation` against a sibling-unit path |
| 22 | checkpoint valid but append log corrupt, or converse | `test_dual_persistence_correlation` | new file; both directions via `P.verify_checkpoint_integrity` / `verify_persistence_integrity` |
| 23 | resume reaches D01 or changes a write-once global field | `test_resume_bootstrap_skips_fresh_write_once_nodes` | new file; **new composition** — real fresh episode (interrupted, lease closed) then real resume episode through `RC._prepare_resume`; asserts D01 absent from episode 2, `created_at` byte-identical, whole-run D01 count stays 1 |
| 24 | orphan recovery touches transport/retrieval/render/frontier | `test_orphan_recovery_is_read_only_and_terminal_only` | new file; **new composition** — real `SIGKILL` child running the actual compiled graph, then real recovery episode streamed through the same graph with `P.build_recovery_services()` (raises on any touch); executed set ⊆ {D00, D96, D98} |
| 25 | checkpoint namespace or thread ID contract violation | `test_checkpoint_thread_and_namespace_contract` | new file; real rejections on malformed `episode_thread_id`/`recovery_thread_id`/`invoke_config` inputs, plus a structural audit that every `"configurable"` dict in `persistence.py`/`unit_graph.py` is built only through those three functions (no live runtime path constructs a raw thread id/namespace from external input — documented as a structural, not dynamic, proof) |
| 26 | mixed static/dynamic visual join; empty visual subset | `test_visual_send_reduce_barrier` | new file; topology legality of both D11-> D12 and M04->D12 as plain edges, empty-subset direct route, and a real episode where D12 fires exactly twice (deterministic-subset-proof, then join — see `nodes/visuals.py` D12 docstring) with no third entry |

All 26 are net-new named tests; they compose (not duplicate) primitives
already proven under different names in `test_plan26_unit_graph.py`,
`test_plan26_persistence.py`, `test_plan26_transport.py`,
`test_plan26_egress.py`, `test_plan26_repair_acceptance.py`,
`test_plan26_workbook.py`, `test_plan26_model_nodes.py`,
`test_plan26_topology.py`, and `test_plan26_cli.py` — none of the 26 spec
row names existed anywhere in the suite before this node.

## 3. Crash denominator (SIGINT/hard-death enumeration)

| Boundary class | Coverage |
|---|---|
| every deterministic node (D00-D98) reachable in the default single-unit episode | `test_plan26_unit_graph.py::test_*` parametrized over `REACHABLE_BOUNDARIES` (in-process cooperative interrupt token, one case per node) |
| the one model node reachable pre-transport (M01) | same parametrization, explicit case |
| fan-out member (per-source, per-visual `Send` dispatch) | `test_exact_fanout_denominators` (this node) + `test_plan26_unit_graph.py` join-exactness tests |
| CLI process (real `SIGKILL`) | `test_plan26_persistence.py::TestExecutionLockRace`/`TestOrphanRecovery` (`_run_child`) + `test_duplicate_continuation_prevented`, `test_orphan_recovery_is_read_only_and_terminal_only` (this node) |
| admission (repair/source/visual) | `test_stale_hash_rejected`, `test_exact_fanout_denominators` (this node) |
| checkpoint durability boundary | `test_dual_persistence_correlation` (this node); `test_plan26_persistence.py::TestCorruptionBlocksRecovery` |
| unit/workbook acceptance | `test_every_unit_page_required`, `test_every_workbook_page_required`, `test_workbook_exact_manifest_coverage` (this node) |
| terminal write boundary | `test_resume_bootstrap_skips_fresh_write_once_nodes`, `test_orphan_recovery_is_read_only_and_terminal_only` (this node); `test_plan26_persistence.py::TestGracefulInterrupt` |

Every class in the section 17 closing paragraph ("inject SIGINT
before/after each node and during each CLI process... hard-crash tests seed
snapshots whose saved next task is each of M01-M08") is covered; the
non-M01 model nodes (M02-M08) are unreachable in the default single-unit
fixture's frontier before M01 completes, matching `UNOBSERVABLE_BOUNDARY`
in `test_plan26_unit_graph.py` — this is a structural fact of the graph
(one model node active per superstep), not a gap.

## 4. Egress and CI lock-drift cross-node proof

- **Egress** (routes to N13 on failure): `tests/runtime/test_plan26_egress.py`
  proves zero egress for raw `socket.connect`/`connect_ex`, `urllib`,
  `http.client`, direct model-endpoint hosts (`MODEL_API_HOSTS`), DNS
  rebinding, and HTTP redirect chains to unapproved/model hosts (lines
  223-270). `test_external_data_authorization_precedes_transmission` (this
  node) adds the 7-way authorization-scope matrix plus a live `EgressGuard`
  check that a raw socket connect is still denied after each mismatch.
  `test_worker_context_is_structurally_bounded` (this node) proves
  filesystem-level worker isolation (the sandbox-bypass half) via
  `tp.prove_workspace_isolation`. All pass — see evidence.
- **CI lock-drift** (routes to N10 on failure): `tests/runtime/test_plan26_lock_drift.py::test_regeneration_is_byte_identical_to_the_committed_lock`
  and `::test_workflow_fails_the_build_on_drift` prove clean regeneration is
  byte-identical to the committed lock and that
  `.github/workflows/plan26-lock-drift.yml` fails the build on controlled
  drift. Both pass — see evidence.

## 5. Forbidden imports / second production path

`test_no_second_production_factory` (this node) statically parses
`runtime/run_curriculum.py` and asserts: no `langchain`/`langchain_openai`/
`langchain_google_genai`/`openai`/`google.generativeai` imports, no
Plan 25/legacy runtime module imports, no legacy simulation/session-bridge
CLI flags, and exactly the expected number of
`build_curriculum_factory_graph(` call sites. This is additional to (not a
replacement for) the pre-existing `test_plan26_cli.py::ImportGraphAuditTests`
and `test_plan26_topology.py` static call-graph tests, all of which still
pass.

## 6. Fake-output promotion refusal

`test_no_nonproduct_success` (this node) plus the pre-existing
`FakeCliTransport` sandbox-root refusal (`transport.py`) and unit-path
unreachability of `D22_ACCEPT_UNIT`/`D24_PROVE_EXACT_MANIFEST_COVERAGE`
from any test-transport episode together prove a fake/test run cannot
produce or copy a product-root acceptance artifact.

## 7. Regression comparison (baseline vs. this node)

Command (mandated interpreter, run from repo root):

```
/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime -q --ignore=tests/runtime/test_run_curriculum.py
```

Result: `4 failed, 1227 passed, 1 skipped, 392 subtests passed in 123.70s`,
exit code 1.

The 4 failures are all in `test_plan26_prompt_graph_controller.py`
(`test_mechanical_revalidation_admits_a_receipt_after_a_harness_only_change`,
`test_mechanical_revalidation_rejects_a_receipt_with_a_stale_output_hash`,
`test_mechanical_revalidation_rejects_a_receipt_with_a_recorded_nonzero_exit`,
`test_passed_nodes_remain_admissible_and_n50_is_the_sole_frontier_after_harness_change`)
— a meta-harness test suite for the prompt-graph controller itself, not
Plan 26 runtime code, and not part of the section 17.2 matrix or the
"reducer/topology/transport/persistence/unit/repair/workbook/CLI" suite
list this node's TEST item 2 names. They fail because this attempt's
sandboxed working copy (`.plan26-run/plan26/attempts/.../repo/`) has no
`plans/26_langgraph_curriculum_factory/results/v3/` receipt directory
populated — the harness's own receipt store, external to Plan 26 runtime
code, is absent in this isolated copy. This is a pre-existing environmental
condition of the sandbox, independent of any change in this node: it
reproduces identically with `tests/runtime/test_plan26_adversarial.py`
removed. **Not a new or worsened baseline failure caused by N50.**

Separately, `tests/runtime/test_run_curriculum.py` (a retained Plan 25
historical test file, spec section 18) fails to *collect* —
`ImportError: cannot import name 'parser_for' from 'runtime.run_curriculum'`
— because N40's CLI cutover renamed the parser factory to `build_parser()`.
This is confirmed pre-existing in the actual top-level repository (not
introduced by this node or specific to the sandbox): the same import error
reproduces against `/Users/filipepinto/Projects/curriculum_builder/runtime/run_curriculum.py`
directly. It is outside this node's declared writable paths
(`runtime/run_curriculum.py` is not writable by N50) and is not part of the
Plan 26 test list this node owns; it is reported here as a **harness
finding inherited from N40** rather than silently excluded — full-suite
runs in this report use `--ignore` for that one file so the rest of the
suite is observable. No LOOP routing target in this node's prompt covers
"retained Plan 25 historical test breakage"; recommend N40 or a dedicated
follow-up restore `parser_for` as a thin alias or update the historical
test to `build_parser`.

Excluding those two pre-existing, out-of-scope gaps, the full Plan 26
runtime suite plus this node's new adversarial file is entirely green:
**1227 passed, 1 skipped, 392 subtests passed, 0 unexplained failures.**

## 8. Commands, exits, hashes

| Command | Exit | Evidence file |
|---|---|---|
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_adversarial.py -v` | 0 (63 passed) | `evidence/N50_ADVERSARIAL_REGRESSION/focused_test_run.txt` |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime -q --ignore=tests/runtime/test_run_curriculum.py` | 1 (4 pre-existing, unrelated failures; see section 7) | `evidence/N50_ADVERSARIAL_REGRESSION/full_plan26_suite.txt` |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_run_curriculum.py -q` | 2 (pre-existing collection error, inherited from N40) | `evidence/N50_ADVERSARIAL_REGRESSION/preexisting_legacy_collection_error.txt` |

Environment: interpreter `/tmp/plan26_n30_verify/bin/python`, CPython
3.13.1 (Clang 16.0.0, macOS/arm64, per `sys.version`).
`requirements/plan26.lock` sha256:
`df971a783b9d027db96eae800e33e7bc65471b94f7a3b0a151eec075e0824835`.

## 9. LOOP disposition

- Runtime egress: PASSED, no route to N13 required.
- CI lock/drift: PASSED, no route to N10 required.
- No negative test was weakened; two initially-wrong assertions in this
  node's own new file were corrected against real production semantics
  before being accepted as passing (manifest closure order is
  manifest-declaration order, not a numeric sort; the visual barrier fires
  exactly twice by documented design, not once) — both are documented in
  the test file's inline comments and section 2 above.
- One out-of-scope finding is carried forward per section 7: the retained
  Plan 25 `test_run_curriculum.py` no longer collects after N40's CLI
  cutover. This node cannot fix it (writable paths do not include
  `runtime/run_curriculum.py`) and it predates this node, so it is reported
  rather than silently patched.
