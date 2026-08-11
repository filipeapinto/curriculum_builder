# N11_STATE_REDUCERS result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N11_state_reducers.prompt.v1.md (9a04739d02833f7381c7f3441c8d16ae38329bcd0e092c1ab1d9c13936e0f4d3)
generation: 5 (rework pass for N30 finding B-1; original pass was generation 1)

## Inputs

- `N00_BASELINE_FREEZE: c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5`
  (`plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md`)
- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md`:
  `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`
  (sections 3.3, 4, 5.1, 5.2, 6.1-6.2, 14 read; section 5.2 is the authority
  for the inventory below and is re-parsed at test time)
- `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml`:
  `96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8`
- `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md`:
  `896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af`
- `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md`:
  `063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0`
- `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md`:
  `c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2`
- `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md`:
  `d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad`
- `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md`:
  `7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7`
- `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md`:
  `edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b`
- `plans/26_langgraph_curriculum_factory/qa_criteria.v2.md`:
  `163154480dc0a851ca597fdfaf62a71840a2cdd212fad8fa196b02dc152edded`

Read additionally on the generation-4 rework pass:

- `plans/26_langgraph_curriculum_factory/contracts/erratum_checkpoint_ns_rename.v1.md`:
  `10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1`
- `plans/26_langgraph_curriculum_factory/results/N20_GRAPH_COMPILER.result.v1.md`:
  `4b9699d65f4fbf2d930f9227f088244211ada21cc2e024aded99f4e78f4e50c1`
  (Finding F-01)

Read additionally on the generation-5 rework pass:

- `plans/26_langgraph_curriculum_factory/results/N30_UNIT_GRAPH.result.v1.md`:
  `83c75350d23fadfafc804f4cc4d410a433ca43311eb83fa4c3acc65d3d152e87`
  (Finding B-1, BLOCKING)
- `plans/26_langgraph_curriculum_factory/results/evidence/N30_UNIT_GRAPH/blocker_probe_write_once.txt`
  (the raw reproduction: 17 of 19 `write_once` channels seeded non-`None`)

## Outputs

- `runtime/langgraph_factory/state.py`:
  `428c78edd53b73fd3458d469b36e1bb528dea37d4565f3b37995d63e4a075167`
- `runtime/langgraph_factory/reducers.py`:
  `05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf`
  (unchanged by both reworks; B-1 was fixed in the channel declarations, not in
  the reducer — see the rework note below)
- `tests/runtime/test_plan26_state_reducers.py`:
  `b10f89014c2e17e6e751f38b978a4af4e69be36f55f1c95791699b7f217f51bd`
- `plans/26_langgraph_curriculum_factory/results/N11_STATE_REDUCERS.result.v1.md`:
  this file (not self-hashed, per [[result_record_schema.v1]])

`runtime/langgraph_factory/__init__.py` is NOT in this node's `writes` set and
already existed when N11 ran (created by a concurrent sibling in the same
generation). N11 did not create, overwrite, or modify it.

## Commands

| Command | Exit code | Evidence |
|---|---:|---|
| `python3 -m pytest tests/runtime/test_plan26_state_reducers.py -q` | 0 | `/tmp/n11_evidence/node_tests.txt` (0.3 KiB, inlined below) |
| `python3 -m pytest -q` | 0 | `/tmp/n11_evidence/full_suite.txt` (0.4 KiB, inlined below) |
| `/tmp/plan26_n11_verify/bin/python3 -m pytest tests/runtime/test_plan26_state_reducers.py -q` (gen-5, hash-locked env) | 0 | inlined below |
| `/tmp/plan26_n11_verify/bin/python3 -m pytest tests/runtime -q` (gen-5, hash-locked env) | 1 | inlined below; 4 failures, all outside this node's write set |
| `shasum -a 256 <14 input/output paths>` | 0 | hash table below |
| `python3 -c "from runtime.langgraph_factory.state import ..."` (inventory/reducer-class smoke check) | 0 | `77` fields, reducer-class counter inlined below |

Captured output, node test module:

```
61 passed, 145 subtests passed in 0.08s
```

Captured output, full repository suite:

```
265 passed, 2 skipped, 282 subtests passed in 100.83s (0:01:40)
```

Generation-4 rework re-run, after the `checkpoint_namespace` rename:

```
$ python3 -m pytest tests/runtime/test_plan26_state_reducers.py -q
61 passed, 145 subtests passed in 0.09s

$ python3 -m pytest -q
746 passed, 4 skipped, 282 subtests passed in 108.70s (0:01:48)
```

Baseline comparison: N00 froze `175 passed, 54 subtests passed`, zero
failures. The full suite is still green with zero failures and zero errors.
The increase (+90 tests, +228 subtests) is N11's 61 tests/145 subtests plus
concurrent sibling nodes (N10/N12/N13) landing in the same generation and
worktree. The 2 skips are not N11's: this node's module reports zero skips.

Generation-5 rework re-run, after the `write_once` channel retyping (B-1). The
new proof requires a real `langgraph` import, so it was run for real in an
isolated hash-locked interpreter built from `requirements/plan26.lock`
(`python3 -m venv /tmp/plan26_n11_verify`,
`pip install --require-hashes -r requirements/plan26.lock`):

```
$ /tmp/plan26_n11_verify/bin/python3 -m pytest tests/runtime/test_plan26_state_reducers.py -q
66 passed, 187 subtests passed in 0.26s

$ /tmp/plan26_n11_verify/bin/python3 -m pytest \
      tests/runtime/test_plan26_state_reducers.py -k WriteOnceThroughARealGraph
5 passed, 61 deselected in 0.17s

$ python3 -m pytest tests/runtime/test_plan26_state_reducers.py -q      # ambient
61 passed, 5 skipped, 145 subtests passed in 0.08s

$ python3 -m pytest -q                                                  # ambient
746 passed, 10 skipped, 282 subtests passed in 138.58s (0:02:18)
```

The 5 real-graph tests run **for real** (not skipped) in the locked interpreter
and self-skip in the ambient one, which has no `langgraph`. The skip is scoped to
that one class rather than the module, so the other 61 framework-agnostic tests
still run ambiently; this is a deliberate departure from the module-level
`SkipTest` guard used by N10/N20/N21/N30, whose whole modules require the
framework.

Full runtime suite in the locked interpreter (`pytest tests/runtime -q`):
`899 passed, 4 failed, 1 skipped`. None of the 4 belongs to this node:
3 are `tests/runtime/test_plan26_topology.py` skeleton-vs-full-graph assertions
(N30 finding B-4, N20's rework, failing on `KeyError: 'D13_RENDER_UNIT'` and
skeleton-cycle/fan-out assertions unrelated to any channel), and 1 is N30's own
`test_blocked_the_affected_write_once_channels_are_named`, which asserts
`"run_id" in affected` and now fails with `assert 'run_id' in []` — that is this
fix landing, exactly as N30 designed that test to signal. Both files are outside
this node's write set.

Reducer-class distribution smoke check:

```
77
Counter({'append_unique': 37, 'write_once': 19, 'replace_current': 8,
         'union_disjoint': 6, 'monotonic_max': 2, 'advance_head': 2,
         'monotonic_status': 1, 'accept_once': 1,
         'write_episode_terminal_once': 1})
```

## Tests

| Prompt TEST item | Test(s) | Verdict | Backing assertion |
|---|---|---|---|
| 1. State inventory equals the spec and rejects missing/unknown fields | `StateInventoryTests::test_spec_file_matches_frozen_baseline_digest`, `::test_state_inventory_equals_spec_table_exactly`, `::test_inventory_rejects_missing_and_unknown_fields` | PASS | The test re-parses the section 5.2 table out of the spec file (pinned to the N00 digest `44e63e62…`) and asserts `FACTORY_STATE_FIELDS == spec_section_5_2_fields()` as an **ordered** 77-tuple; `validate_state_inventory` raises `StateInventoryError` naming `terminal` when dropped and `execution_evidence` when added |
| 2. Every field has one declared reducer and bounded node authorities | `::test_every_field_declares_exactly_one_reducer`, `::test_field_reducer_classes_match_spec_authority`, `::test_declared_correlation_key_for_deterministic_checks`, `::test_reducer_for_rejects_unknown_field`, `FailClosedContractTests::test_every_reducer_is_registered_and_typed` | PASS | `Annotated` metadata yields exactly 1 callable per field (77/77, else `StateInventoryError`); `FIELD_REDUCER_CLASSES` equals a 77-row expected map transcribed independently in the test from the spec's "Class/reducer" column; `deterministic_checks` declares the spec's literal key `(scope, owner, head_hash, check_id, attempt)`; `REDUCERS` has exactly 9 entries |
| 3. Equal replay is idempotent where allowed; conflicting replay fails | `FailClosedContractTests::test_equal_replay_is_idempotent_for_every_reducer`, `::test_conflicting_replay_raises_a_typed_reducer_error`, plus per-reducer cases in `WriteOnceTests`, `AppendUniqueTests`, `UnionDisjointTests`, `AdvanceHeadTests`, `ReplaceCurrentTests`, `MonotonicStatusTests`, `MonotonicMaxTests`, `AcceptOnceTests`, `EpisodeTerminalTests` | PASS | All 9 reducer classes are exercised for equal replay (returns the prior value); 8 conflict cases each raise a typed `ReducerError` subclass — nothing is dropped or coerced |
| 4. Disjoint union is associative/commutative under completion permutations | `UnionDisjointTests::test_commutative_and_associative_under_completion_permutations`, `::test_equal_replay_is_idempotent_in_any_order`, `::test_key_conflict_fails_in_every_order` | PASS | All 24 permutations of a 4-worker fan-out fold to the identical map (property test via `itertools.permutations`); all 5 split points satisfy `fold(a) ∪ fold(b) == fold(a+b)`; all 120 permutations containing a conflicting duplicate raise `UnionConflict` regardless of arrival order |
| 5. Heads require immutable parent and exactly version+1 | `AdvanceHeadTests::test_genesis_must_be_version_one_with_null_parent`, `::test_child_requires_parent_match_and_version_plus_one`, `::test_equal_replay_is_idempotent_and_regression_fails`, `::test_independent_heads_advance_independently`, `::test_malformed_head_record_fails` | PASS | Version skip (1→2 then offered 4) raises `HeadAdvanceError`; wrong parent (`parent_hash=h1` against head `h2`) raises; genesis at version 2, genesis with non-null parent, missing `parent_hash`, version 0, and empty hash all raise |
| 6. Status/counters cannot regress; acceptance/terminal are once-only | `MonotonicStatusTests` (7 tests), `MonotonicMaxTests` (4 tests), `AcceptOnceTests` (3 tests), `EpisodeTerminalTests` (3 tests) | PASS | `ACCEPTED` has no outgoing edge except itself (4 regressions each raise `StatusTransitionError`); undeclared jumps and unknown statuses raise; counters raise `CounterRegression` on decrease and on non-integer/negative/bool values; a differing rewrite of an accepted receipt raises `AcceptOnceConflict`; a second differing terminal and any kind outside the six raise `TerminalConflict` (`ACCEPTED_PENDING_REVIEW` explicitly rejected) |
| 7. Runtime context is not checkpoint serializable and holds no model client | `RuntimeContextTests` (7 tests) | PASS | `json.dumps(context)` and `json.dumps(dataclasses.asdict(context))` both raise `TypeError`; `canonical_json` raises `NonSerializableValue`; `FORBIDDEN_RUNTIME_CONTEXT_FIELDS` (model/llm/chat_model/router/routing_authority/selector/state/…) is disjoint from `RUNTIME_CONTEXT_FIELDS` and absent via `hasattr`; a frozen-dataclass subclass adding `model_client` raises `RuntimeContextViolation` at construction; no context service name appears in `FACTORY_STATE_FIELDS` |

Generation-5 addition, closing N30 finding B-1:

| Prompt TEST item | Test(s) | Verdict | Backing assertion |
|---|---|---|---|
| 3 (extended). Equal replay is idempotent and conflicting replay fails **through a real compiled `StateGraph`**, not only as a direct call | `WriteOnceThroughARealGraphTests::test_the_write_once_inventory_is_the_nineteen_declared_channels`, `::test_no_write_once_channel_is_seeded_with_a_constructed_default`, `::test_every_write_once_channel_accepts_its_own_first_write`, `::test_an_equal_second_write_replays_and_a_differing_one_still_conflicts`, `::test_an_intentional_empty_write_is_a_recorded_value_not_an_unset_channel` | PASS (real run, hash-locked env) | Reading any of the 19 `write_once` channels off a real `StateGraph(FactoryState)` raises `EmptyChannelError` — no channel is seeded with a constructed default. A real `.invoke()` of a graph whose node writes all 19 channels at once returns each value unchanged, so no channel rejects its own first write. A second node writing the identical values replays clean; one writing `run_id="run-2"` raises `WriteOnceConflict` out of `invoke`, so the fail-closed guarantee survives the framework. A first write of `frozen_inputs=[]`, `external_authorizations=[]`, `effective_run={}` and `checkpoint_namespace=""` is recorded as those values, and a later differing write of `frozen_inputs` still raises — an intentionally empty write is a value, not an unset channel |

Additional guards beyond the prompt's list: `FailClosedContractTests::test_no_langgraph_import_in_state_or_reducers` proves both modules are framework-agnostic (no `langgraph` import — N11 does not depend on N10); `StateInventoryTests::test_output_schema_is_a_projection_of_persisted_state` proves `FactoryOutput` adds no channel that is not persisted state; `AppendUniqueTests::test_reducer_does_not_mutate_its_input` proves purity.

## Field authority table

`Reducer` is the implementing class from `reducers.py`. `Writer node(s)` is
the spec section 5.2 "Mutation authority" column verbatim in intent; no node
outside the listed set may write the field.

Generation-5 retyping (B-1): all 19 `write_once` channels are now declared
`Annotated[X | None, write_once]`. Seventeen of them changed
(`bootstrap_kind`, `contract_version`, `run_id`, `created_at`, `engine_root`,
`curriculum_root`, `active_manifest_path`, `output_root`, `mode`,
`frozen_inputs`, `frozen_digest`, `frozen_executable_identities`,
`external_authorizations`, `effective_run`, `episode_id`,
`checkpoint_thread_id`, `checkpoint_namespace`); `requested_unit_id` and
`resume_from` were already declared that way. No field was renamed, no reducer
class changed, and no mutation authority moved, so every row below stands. The
`| None` is the *unwritten* state of the channel and never a written value: the
writer node listed for each field writes the real value exactly once, and
`runtime/langgraph_factory/nodes/__init__.py:545` (`project`) already maps an
absent or `None` channel to that reducer class's empty value before any node
body sees it — `write_once`'s empty value there has always been `None`.

| Field | Reducer | Writer node(s) |
|---|---|---|
| `invocation` | `replace_current` | graph input, consumed by D00 |
| `validated_recovery_envelope` | `replace_current` | D00R only |
| `bootstrap_kind` | `write_once` | D00 |
| `contract_version` | `write_once` | D01 fresh; D04 identical import |
| `run_id` | `write_once` | D01 fresh; D04 byte-identical import |
| `created_at` | `write_once` | D01 fresh; D04 byte-identical import |
| `engine_root` | `write_once` | D01 fresh; D04 byte-identical import |
| `curriculum_root` | `write_once` | D01 fresh; D04 byte-identical import |
| `active_manifest_path` | `write_once` | D01 fresh; D04 byte-identical import |
| `output_root` | `write_once` | D01 fresh; D04 byte-identical import |
| `mode` | `write_once` | D01 fresh; D04 byte-identical import |
| `requested_unit_id` | `write_once` | D01 fresh; D04 byte-identical import |
| `frozen_inputs` | `write_once` | D01 fresh; D00R compares, D04 imports identical |
| `frozen_digest` | `write_once` | D01 fresh; D00R compares, D04 imports identical |
| `frozen_executable_identities` | `write_once` | D01 fresh; D00R compares, D04 imports identical |
| `external_authorizations` | `write_once` | D01 fresh; D00R compares, D04 imports identical |
| `effective_run` | `write_once` | D02 fresh; D04 byte-identical import |
| `episode_id` | `write_once` | D04 |
| `checkpoint_thread_id` | `write_once` | D04 |
| `checkpoint_namespace` | `write_once` | D04 (always `""`) |
| `resume_from` | `write_once` | D04 |
| `resume_frontier` | `replace_current` | D04; D30/D96 set the resumable frontier |
| `cursor` | `monotonic_max` | D05/D23 |
| `selected_unit_id` | `replace_current` | D05/D23 |
| `unit_status` | `monotonic_status` | D05, validation/reduction/acceptance nodes |
| `source_requests` | `append_unique` | D06 |
| `source_denominators` | `union_disjoint` | D06 |
| `source_discoveries` | `union_disjoint` | M01 |
| `retrievals` | `union_disjoint` | D06B |
| `source_interpretations` | `union_disjoint` | M01 |
| `source_admissions` | `append_unique` | D07 only |
| `source_join_evidence` | `append_unique` | D07 only |
| `artifact_versions` | `append_unique` | M02/M03/M04/M06 and deterministic producers; admitted by D08/D09/D12/D20 |
| `artifact_heads` | `advance_head` | admission nodes only (D08, D09, D12, D20) |
| `deterministic_checks` | `append_unique` (key `scope, owner, head_hash, check_id, attempt`) | D08, D09, D12–D14, D20–D21, D26, D31–D32 |
| `visual_briefs` | `append_unique` | D10 |
| `visual_denominators` | `union_disjoint` | D10 |
| `visual_results` | `union_disjoint` | D11, M04 |
| `visual_join_evidence` | `append_unique` | D12 |
| `unit_page_inventories` | `append_unique` | D14 |
| `unit_page_inspections` | `append_unique` | D14 |
| `review_packets` | `append_unique` | D15 |
| `unit_reviews` | `append_unique` | M05 |
| `finding_partitions` | `append_unique` | D17 |
| `repair_requests` | `append_unique` | D18 |
| `invalidations` | `append_unique` | D19 |
| `retest_plans` | `append_unique` | D20 |
| `retest_results` | `append_unique` | D21 |
| `attempt_counters` | `monotonic_max` | D90 counter gate |
| `failure_fingerprints` | `append_unique` | D17/D29 classifier |
| `accepted_unit_receipts` | `accept_once` | D22 |
| `accepted_unit_checkpoint_receipts` | `append_unique` | D23 |
| `workbook_versions` | `append_unique` | D25/D31 |
| `workbook_head` | `advance_head` | D25/D31 |
| `workbook_coverage` | `append_unique` | D24 |
| `workbook_page_inventories` | `append_unique` | D26 |
| `workbook_page_inspections` | `append_unique` | D26 |
| `workbook_review_packets` | `append_unique` | D27 |
| `workbook_reviews` | `append_unique` | M07 |
| `workbook_finding_partitions` | `append_unique` | D29 |
| `workbook_repair_requests` | `append_unique` | D29 |
| `workbook_invalidations` | `append_unique` | D29/D31 |
| `workbook_retests` | `append_unique` | D31 |
| `final_release_audits` | `append_unique` | D32 |
| `route_decisions` | `append_unique` | deterministic router |
| `model_execution_receipts` | `append_unique` | transport boundary |
| `activation_receipts` | `append_unique` | transport boundary |
| `capability_receipts` | `append_unique` | D03 |
| `evidence_index_entries` | `append_unique` | evidence writer |
| `log_audit_receipts` | `append_unique` | acceptance reducers |
| `checkpoint_metadata` | `append_unique` | checkpoint-correlation hook after each superstep |
| `pending_failure` | `replace_current` | producing node; next deterministic classifier consumes/clears |
| `pending_packet` | `replace_current` | producing node; next deterministic classifier consumes/clears |
| `pending_guard` | `replace_current` | producing node; next deterministic classifier consumes/clears |
| `terminal_candidate` | `replace_current` | deterministic guard/classifier only |
| `terminal` | `write_episode_terminal_once` | D98 |
| `terminal_history` | `append_unique` | D04 (validated prior resumable terminal only); D98 mirror |

### Resolutions recorded for downstream nodes

1. **Append-only is implemented as `append_unique`.** The spec labels
   `route_decisions`, `evidence_index_entries`, `checkpoint_metadata`, and
   `terminal_history` "append-only". Only nine reducers exist, so append-only
   is realized as `append_unique` over a writer-computed `key`, which is
   strictly stronger: replay is idempotent instead of duplicating.
2. **"Write-once per key" over a map is `union_disjoint`.** The spec's
   "write-once per unit epoch" (`source_denominators`) and "write-once per
   content head" (`visual_denominators`) are exactly `union_disjoint`
   semantics: first write wins, equal replay is a no-op, differing value
   raises `UnionConflict`. `write_once` remains scalar-only.
3. **Correlation-key contract for `append_unique` (binding on N22/N23/N31/N32).**
   Every appended record MUST carry a string `"key"` field that the writing
   node computes deterministically from its declared correlation tuple, except
   `deterministic_checks`, which keys on the spec's literal five fields.
   `reducers.correlation_key()` builds keys canonically.
4. **`advance_head` is keyed.** Both `artifact_heads` and `workbook_head` are
   maps of head key -> `{version, parent_hash, hash}`; `workbook_head` uses the
   single reserved key `"workbook"`. Genesis is version 1 with a null parent.
5. **`FactoryOutput` is a strict projection of persisted channels.** LangGraph's
   `output_schema` keys must be state channels, and section 5.2 is closed, so
   the CLI's printed `accepted_receipt`, `release_receipt`, `checkpoint_id`,
   and `evidence_index_hash` are derived by N40 from `accepted_unit_receipts`,
   `final_release_audits`, `checkpoint_metadata`, and `evidence_index_entries`
   respectively. This is documented in `FactoryOutput`'s docstring.
6. **`write_once` treats a `None` update as a no-op, not a conflict.** In
   `mode: all`, `requested_unit_id` is legitimately null, and an absent field
   and an explicit null are the same persisted state; a null update therefore
   can never contradict a recorded value.
7. **Unit lifecycle for `monotonic_status`.** The spec names the reducer but
   not the status set. N11 declares `PENDING -> SELECTED -> SOURCING ->
   BUILDING -> REVIEWING -> {REPAIRING <-> REVIEWING} -> ACCEPTED`, with
   `BLOCKED` reachable from every non-terminal status; `ACCEPTED` and `BLOCKED`
   have no outgoing edge. N22/N31/N32 may extend the transition table only by
   adding edges that keep `ACCEPTED` terminal.
8. **Every `write_once` channel is declared `X | None` (generation 5, binding
   on all downstream nodes).** `None` is the channel's *unwritten* state and is
   never a written value; the writing node in the field-authority table above
   still writes the real value exactly once. A new `write_once` channel MUST be
   declared `X | None` or LangGraph will seed it with `X()` and the channel will
   reject its own first write.

## Findings

**Generation-5 rework: `write_once` channels are declared `X | None` (N30
finding B-1, BLOCKING).** LangGraph 1.2.9 builds a reduced channel's initial
value by *calling the annotated type* when that type is zero-arg constructible,
so `Annotated[str, write_once]` starts at `''`, `Annotated[RecordList,
write_once]` at `[]`, and `Annotated[Record, write_once]` at `{}`. `write_once`
then sees `existing is not None` and unequal, and raises `WriteOnceConflict` on
the channel's own **first** write. Seventeen of the 19 `write_once` channels
were affected; D01 could never complete, so no episode could execute. It was
unobservable to every predecessor because N11 tested `write_once` as a bare
function, N22 tested node bodies as functions, and N20 compiled the graph
without invoking it — N30 was the first node to call `.invoke()`.

**Fix chosen: N30's option 1** — annotate the affected channels `X | None`,
matching `requested_unit_id`/`resume_from`, which were already declared that way
and are the two channels N30 found unaffected. A union is not zero-arg
constructible, so LangGraph leaves the channel at its own `MISSING` sentinel and
the first write goes through the operator's absent branch. Rationale:

1. It reuses behavior already proven correct in this exact codebase and
   LangGraph version, rather than adding a second, N11-authored notion of
   "unset" that would have to track LangGraph's default-construction rules
   version to version.
2. N30's stated risk for option 2 is real here and not hypothetical. Three of
   the affected channels can legitimately be first-written empty in normal
   operation: `external_authorizations` and `frozen_executable_identities` are
   `[]` for a run that needs neither, and `checkpoint_namespace` is *always*
   `""` (LangGraph's root namespace) per the field-authority table. A reducer
   that treated "the channel's type-appropriate empty value" as "unset" would
   silently accept a later differing write to exactly those three, converting a
   fail-closed channel into a last-write-wins one — the opposite of the
   guarantee this node exists to provide.
3. It leaves `reducers.py` byte-identical, so `write_once`'s semantics are
   unchanged and every existing conflict/idempotence proof still holds
   unmodified.

The type is more honest, not weaker: `| None` is the channel's unwritten state,
which consumers already had to handle, because `project()` in
`nodes/__init__.py` has always mapped an absent `write_once` channel to `None`
before a node body sees it. The regression that would hide a recurrence is now
tested through a real compiled graph, not through a direct reducer call —
see `WriteOnceThroughARealGraphTests`, which asserts both that no channel is
seeded and that an intentional empty write still conflicts with a later
differing one.

**Generation-4 rework: reserved channel renamed.** N20_GRAPH_COMPILER's
Finding F-01 showed that `StateGraph(FactoryState, ...)` raises
`ValueError: Channel name 'checkpoint_ns' is reserved` under LangGraph 1.2.9,
which reserves `checkpoint_ns`, `checkpoint_id`, and `configurable`. N11's
generation-1 tests exercised reducers and the state inventory directly and
never constructed a real `StateGraph`, so the collision was unobservable here.
Per the frozen resolution in
[[erratum_checkpoint_ns_rename.v1]], the `FactoryState` channel is renamed
`checkpoint_namespace` with value semantics unchanged (still `""`, the
LangGraph root namespace).

Changes confined to this node's write set:

- `state.py:108` — channel declaration renamed. `FACTORY_STATE_FIELDS`,
  `FIELD_REDUCERS`, and `FIELD_REDUCER_CLASSES` are all derived from
  `FactoryState.__annotations__`, so they follow the rename with no separate
  edit; no string literal of the old name existed anywhere else in `state.py`.
- `reducers.py` — verified to contain no `checkpoint_ns` reference (reducers
  are generic over field names). Unchanged, hash identical to generation 1.
- `test_plan26_state_reducers.py` — the field->reducer-class table entry
  renamed. Additionally, `spec_section_5_2_fields()` now applies a
  `SPEC_FIELD_ERRATA` mapping when parsing spec section 5.2: the spec file
  stays frozen at its baseline digest (and a sibling test still asserts that
  digest), so the erratum's rename has to be applied at parse time rather than
  by editing the spec, which is neither in this node's write set nor amendable
  without breaking every citation of its hash.

A case-sensitive word-boundary grep across all three files confirms no
remaining `checkpoint_ns` occurrence in this node's write set.

Deliberately NOT renamed (each is a different concept that merely shares the
name, per the erratum): `persistence.py`'s `CHECKPOINT_NS` constant and its
`config["configurable"]["checkpoint_ns"]` invoke-config key (LangGraph's own
hardcoded key, not a channel), and `evidence.py`'s `"checkpoint_ns"` JSONL
record key (a log field, not a channel). Both files are outside this node's
write set and were not touched.

**Ambient suite (non-blocking).** The corresponding N22 follow-up
(`nodes/inputs.py:887`, `nodes/__init__.py:286`, and
`test_plan26_deterministic_nodes.py:1852`) landed concurrently and is outside
this node's write set. With both changes present the full ambient suite is
green: 746 passed, 4 skipped, 282 subtests passed. N20_GRAPH_COMPILER still
owes a re-run to confirm the compile-time `ValueError` is actually cleared —
that verification is N20's, not this node's.

## Invalidated descendants

None. The generation-5 change is a channel *type* change, not a rename or a
semantic change: no field name, reducer class, mutation authority, or written
value moved, so no descendant's contract with this node changed. One
descendant test observes the fix and must be re-scoped by its owner:
`tests/runtime/test_plan26_unit_graph.py::test_blocked_the_affected_write_once_channels_are_named`
(N30) asserts the affected set is non-empty and now correctly fails, which is
the signal N30 built it to give.

## Hashes

| Path | SHA-256 |
|---|---|
| `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` | `96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8` |
| `plans/26_langgraph_curriculum_factory/prompts/N11_state_reducers.prompt.v1.md` | `9a04739d02833f7381c7f3441c8d16ae38329bcd0e092c1ab1d9c13936e0f4d3` |
| `plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md` | `c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5` |
| `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` | `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` |
| `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md` | `896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af` |
| `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md` | `063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0` |
| `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md` | `c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2` |
| `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md` | `d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad` |
| `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md` | `7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7` |
| `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md` | `edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b` |
| `plans/26_langgraph_curriculum_factory/qa_criteria.v2.md` | `163154480dc0a851ca597fdfaf62a71840a2cdd212fad8fa196b02dc152edded` |
| `plans/26_langgraph_curriculum_factory/contracts/erratum_checkpoint_ns_rename.v1.md` | `10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1` |
| `plans/26_langgraph_curriculum_factory/results/N20_GRAPH_COMPILER.result.v1.md` | `4b9699d65f4fbf2d930f9227f088244211ada21cc2e024aded99f4e78f4e50c1` |
| `runtime/langgraph_factory/state.py` | `428c78edd53b73fd3458d469b36e1bb528dea37d4565f3b37995d63e4a075167` |
| `runtime/langgraph_factory/reducers.py` | `05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf` |
| `tests/runtime/test_plan26_state_reducers.py` | `b10f89014c2e17e6e751f38b978a4af4e69be36f55f1c95791699b7f217f51bd` |
| `plans/26_langgraph_curriculum_factory/results/N30_UNIT_GRAPH.result.v1.md` | `83c75350d23fadfafc804f4cc4d410a433ca43311eb83fa4c3acc65d3d152e87` |
