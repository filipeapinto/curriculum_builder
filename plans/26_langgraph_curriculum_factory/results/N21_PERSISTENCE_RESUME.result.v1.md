# N21_PERSISTENCE_RESUME result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N21_persistence_resume.prompt.v1.md (3b0d3ee5aabe8cc77401cad14314f36f5af2635d752d996955ec1e6e863f1d36)
generation: 7 (B-5 rework pass; original pass was generation 3)

Generation derivation: N00 executed in generation 1; N10-N13 (`depends_on:
[N00_BASELINE_FREEZE]`) in generation 2; this node's `depends_on` is
`[N10_DEPENDENCY_API, N11_STATE_REDUCERS, N12_EVIDENCE_ARTIFACTS]` with
`join: all_of`, so its earliest admissible generation is 3.

## Inputs

Predecessor result records consumed (`depends_on`, `all_of`):

- `N10_DEPENDENCY_API`: `1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658`
- `N11_STATE_REDUCERS`: `c89f166596633e2027f04daa03fca9a33e9f23f2c1346f77817e44b8c03dc30e`
- `N12_EVIDENCE_ARTIFACTS`: `6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f`
- `N00_BASELINE_FREEZE` (transitive, cited for the baseline count): `c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5`

Other frozen inputs read:

- `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml`: `96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8` — this node's `writes` set
- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md`: `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` — sections 4 (pre-invocation helper), 10 (correlation keys/denominators), 11.1-11.4 in full, 3.3 (selected API surface)
- `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md`: `063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0`
- `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md`: `d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad`
- `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md`: `c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2`
- `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md`: `7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7`
- `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md`: `896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af`
- `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md`: `edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b`
- `plans/26_langgraph_curriculum_factory/qa_criteria.v2.md`: `163154480dc0a851ca597fdfaf62a71840a2cdd212fad8fa196b02dc152edded`
- `requirements/plan26.lock`: `df971a783b9d027db96eae800e33e7bc65471b94f7a3b0a151eec075e0824835` — the hash-locked environment this node's proof runs in
- `runtime/langgraph_factory/state.py`: `873d640ff2b7e677818fa74d514211e104797b3d3d48dfad4d7d7d47197cd74a` — real `FactoryState`/`RuntimeContext` types, not redefined here
- `runtime/langgraph_factory/reducers.py`: `05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf`
- `runtime/langgraph_factory/evidence.py`: `95ddef6f9e1e5e7031f223d88b285b2b0ffbdd604c70181ae87ad8a21220c199` — `EvidenceStore`/`checkpoints` log called into, not reinvented
- `runtime/langgraph_factory/artifacts.py`: `dfb1efa93c0c267b0ae282c9687d769ef043b31c363526871e7212e2890b86cf` — `canonical_digest`, `canonical_json_bytes`, `file_digest`, `resolve_within`
- `runtime/langgraph_factory/nodes/terminal.py`: `66e7b92752d8ab8e0a93e00fc50114331f74f34538358b9b2938a6f02c17f28d` — N22's D98, read (not modified) as the source of truth for the `INTERRUPTED` candidate contract during the F-04 rework

## Outputs

- `runtime/langgraph_factory/persistence.py`: `c2b3eb236d2ea7bb6ca7f0ff5d6258c8bd1fdec8cf36d9520c2b2ddb9298b289` (B-5 rework)
- `tests/runtime/test_plan26_persistence.py`: `c3863a74512ee8d79e0ed92db768553a605265984be489191c0b9084e2ab6a94` (B-5 rework)
- `plans/26_langgraph_curriculum_factory/results/N21_PERSISTENCE_RESUME.result.v1.md`: this file (hashed externally per [[result_record_schema.v1]] hash discipline)

No path in the node `writes` set is `NOT_CREATED`. No file outside the `writes`
set was created or modified by this node.

## Configuration

Every value below is asserted against a live connection and the committed
SQLite file by `TestCheckpointConfiguration`, not read back from a constant.

| Item | Value | Source |
|---|---|---|
| Checkpoint database | `<output_root>/.langgraph/checkpoints.sqlite3` | spec 11.1 |
| Execution lock | `<output_root>/.langgraph/execution.lock` | spec 11.1 |
| Saver | `SqliteSaver(sqlite3.connect(path, check_same_thread=False))`, synchronous, `setup()` called | spec 3.3, 11.1 |
| `journal_mode` | `wal` (verified on the connection *and* in file-header bytes 18/19 == `(2, 2)`) | spec 11.1 |
| `synchronous` | `2` (FULL) | spec 11.1 |
| `foreign_keys` | `1` | spec 11.1 |
| `busy_timeout` | `30000` ms | spec 11.1 |
| Strict persisted values | `LANGGRAPH_STRICT_MSGPACK=true`, set at module import before any langgraph serde import | spec 11.1 |
| `checkpoint_ns` | `""` always; `SELECT DISTINCT checkpoint_ns FROM checkpoints` returns exactly `""` | spec 11.1 |
| Compiled graph name | `plan26_curriculum_factory` | spec 3.3 |
| Invoke config | exactly `{"configurable": {"thread_id": ..., "checkpoint_ns": ""}}` — no other configurable key | spec 11.1 |
| Episode thread id | `f"{run_id}:episode:{episode_ordinal:06d}"` | spec 11.1 |
| Recovery thread id | `f"{run_id}:recover:{orphan_episode_ordinal}"` | spec 11.1 |
| Durability flush | `commit()` + `PRAGMA wal_checkpoint(FULL)` + `fsync` of db, `-wal`, and the containing directory | spec 11.1 |

`SqliteSaver.setup()` is allowed to touch journal/synchronous settings, so the
pragmas are re-asserted after `setup()` and then *proved* by
`verify_connection_pragmas()`, which raises `CheckpointCorrupt` on any relaxed
value (`test_a_relaxed_pragma_is_refused_rather_than_silently_accepted`).

Persistence layers are kept separate exactly as spec 11.2 requires. The
checkpoint store is SQLite; the append-only layer is N12's six hash-chained
evidence logs plus two ledgers this node owns under `.langgraph/`:
`episodes.jsonl` (episode leases, compare-and-swap ordinal) and
`admissions.jsonl` (idempotent admission of committed work). Correlation
records are written into N12's `checkpoints` log by
`record_checkpoint_correlation()`, carrying `run_id`, `episode_id`, `node_id`,
`activation_id`, `checkpoint_id`, `parent_checkpoint_id`, `checkpoint_ns`,
`thread_id`, `state_digest`, `next`, `tasks`, `pending_writes`, and the
evidence high-water mark of every other log.

## Episode algorithm

`prepare_episode_invocation()` is the one pre-invocation helper. It requires the
exclusive output lock to already be held, performs no product work, transmits
nothing, and returns a typed `EpisodeInvocation`.

1. **Lock.** Refuse unless an `ExecutionLock` for this output root is held
   (spec 11.4 step 1).
2. **Identity.** Fresh: derive `run_id = "run-" + canonical_digest(seed)` over
   the eight frozen identity fields, then exclusively create the immutable
   identity envelope at `.langgraph/identity_envelope.json` (mode `0o444`, hash
   covering its own bytes). Resume: read `run_id` back out of the envelope; a
   supplied seed that recomputes to a different `run_id` is refused. D01/D00R
   recompute independently, so disagreement is detectable.
3. **Drift.** `validate_resume_inputs()` compares the envelope merged with the
   caller's durable resume baseline against freshly recomputed values, keyed by
   the drift class table. Any mismatch — or any key with no assigned drift
   class — raises `ResumeRefused` before product work.
4. **Integrity.** `verify_persistence_integrity()` proves SQLite
   (`PRAGMA integrity_check` + presence of the saver's tables) and both
   append-only ledgers, and the evidence logs when a store is supplied. Nothing
   is repaired.
5. **Orphan.** An open lease with no matching close means the process died
   before D98. The orphan thread is read with `get_state`/`get_state_history`/
   `SqliteSaver.get_tuple`/`list` only, through `ReadOnlyCheckpointView`, and a
   **new** thread `f"{run_id}:recover:{orphan_ordinal}"` is prepared with
   `bootstrap_kind=RECOVER_ORPHAN`. The orphaned thread is never continued.
6. **Resume.** Otherwise the last lease's terminal must be `INTERRUPTED` or
   `PAUSED_PREREQUISITE`; `UNIT_ACCEPTED`, `COMPLETE`,
   `CONVERGENCE_EXHAUSTED`, and `SYSTEM_FAILURE` are refused. The prior episode
   is read out read-only and a new thread at `episode_ordinal + 1` is opened.
7. **Lease.** `EpisodeLeaseLedger.open_episode()` appends under a
   compare-and-swap ordinal; a non-recovery episode cannot open while any lease
   is open, and at most one recovery lease may exist at a time.
8. **Empty state.** Each episode's thread is genuinely new:
   `saver.get_tuple(new_config)` is `None` and `graph.get_state(new_config).values`
   is `{}` (`test_each_episode_gets_a_new_thread_with_empty_langgraph_state`).
   D04 (N22) is what reducer-imports prior state; `prepare_episode_invocation()`
   only hands it `resume_from`.

`EpisodeInvocation.as_state_update()` returns exactly the `FactoryState` fields
D00 writes (`bootstrap_kind`, `run_id`, `episode_id`, `checkpoint_thread_id`,
`checkpoint_namespace`, `resume_from`), each asserted to exist in N11's
`FACTORY_STATE_FIELDS`. The fifth key is spelled `checkpoint_namespace` per
[[erratum_checkpoint_ns_rename.v1]]; the dataclass *field* it reads from is
still `EpisodeInvocation.checkpoint_ns`, which is this node's own attribute and
out of the erratum's scope.

Structural guarantees, asserted rather than documented:

- `ReadOnlyCheckpointView` uses `__slots__` and binds only four read callables;
  `invoke`, `stream`, `ainvoke`, `batch`, and `update_state` are absent
  (`hasattr` is `False`, calling raises `AttributeError`).
- An AST scan of `persistence.py` proves it calls no `.invoke()`, `.ainvoke()`,
  `.stream()`, `.astream()`, `.update_state()`, or `.batch()` anywhere.
- An AST import scan proves it imports no transport, egress, model-node, node,
  workbook, LangChain, provider-SDK, or HTTP/socket module.

## Crash matrix

Each row is a real operating-system process that was actually `SIGKILL`ed;
`returncode == -signal.SIGKILL` is asserted before the row's claim is evaluated.
The committed-work key is one activation key in `admissions.jsonl`.

| # | Injected fault | Where | Committed records before retry | After retry | Assertion |
|---|---|---|---:|---:|---|
| 1 | `SIGKILL` before admission | inside node `D13`, before `AdmissionLedger.admit` | 0 | 1 | `admit` returns `was_new=True`; exactly one record for the key |
| 2 | `SIGKILL` after admission, before checkpoint | inside node `D13`, after `admit`, before the superstep checkpoint | 1 | 1 | `admit` returns `was_new=False`; no duplicate |
| 3 | `SIGKILL` after checkpoint + WAL flush | after `invoke()` and `flush_checkpoint_durability()` | 1 | 1 | `admit` returns `was_new=False`; no duplicate |
| 4 | second retry after any of the above | in-process | 1 | 1 | still exactly one record |
| 5 | differing bytes replayed under a committed key | in-process | 1 | 1 | `AdmissionConflict` raised; ledger unchanged |
| 6 | sibling task raises mid-superstep | real fan-out, two parallel nodes | — | — | completed sibling's write is in `CheckpointTuple.pending_writes`; on resume the completed task **replays its write instead of re-executing** (`executions == ["good"]`, `ok.count("good") == 1`) |
| 7 | sibling task raises, join evaluated | real fan-out | — | — | `pending_writes` preserves the survivor, but `classify_join_members` reports `satisfied=False`, `pending=["bad"]` — a partial fan-out is never admitted |
| 8 | `SIGKILL` after a full episode, before D98 | real child process holding the lock and lease | — | — | lease left open; next `--resume` returns `bootstrap_kind=RECOVER_ORPHAN` on a **new** `:recover:1` thread; product bytes byte-identical before/after |
| 9 | second process races for the output root | real child process | — | — | winner keeps the lock, loser exits `3`, and every file under the output root (control files included) has identical mtime_ns and sha256 before/after |
| 10 | 512 bytes of a data page overwritten in `checkpoints.sqlite3` | after `wal_checkpoint(TRUNCATE)` | — | — | `verify_checkpoint_integrity`, `verify_persistence_integrity`, and `prepare_episode_invocation(resume=True)` all raise `CheckpointCorrupt`; database digest unchanged (no self-repair); the append-only layer still audits `PASS` on its own |
| 11 | one byte flipped in `episodes.jsonl` | append-only layer only | — | — | ledger audits `FAIL`, `verify_persistence_integrity` and resume raise `CheckpointCorrupt`, file digest unchanged; SQLite still verifies `ok` on its own |
| 12 | trailing bytes removed from `admissions.jsonl` | append-only layer only | — | — | torn append detected, audit `FAIL` |
| 13 | one byte flipped in N12's `evidence/events.jsonl` | append-only layer only | — | — | SQLite verifies `ok`; `verify_persistence_integrity` still raises `CheckpointCorrupt` |

The two directions of row 10/11 are what discharges TEST item 10: corruption in
either layer alone blocks recovery, and neither verification path writes.

## Commands

All commands run from repository root `/Users/filipepinto/Projects/curriculum_builder`.
Every captured output was under 4 KiB after truncation to its verdict line, so
verdicts are inlined here per [[digest_algorithm.v1]]; no evidence path outside
this node's `writes` set was created.

| # | Command | Exit | Evidence |
|---|---|---:|---|
| 1 | `/opt/homebrew/bin/python3 -m venv /tmp/plan26_n21_verify` | 0 | throwaway isolated environment, outside the repository |
| 2 | `/tmp/plan26_n21_verify/bin/python -m pip install --require-hashes -r requirements/plan26.lock` | 0 | hash-verified install of the N10 lock: `langgraph-1.2.9`, `langgraph-checkpoint-sqlite-3.1.0`, `langgraph-checkpoint-4.2.0`, 48 distributions |
| 3 | `PYTHONPATH=<repo> /tmp/plan26_n21_verify/bin/python - <<'PY' ... PY` (module smoke: real saver, real graph, real readout) | 0 | `pragmas {'journal_mode': 'wal', 'synchronous': 2, 'foreign_keys': 1, 'busy_timeout': 30000}`; `tables ['checkpoints', 'writes']`; `inv FRESH run-e395a5a5...:episode:000001`; `hasattr invoke on view: False` |
| 4 | `PYTHONPATH=<repo> /tmp/plan26_n21_verify/bin/python - <<'PY' ... PY` (aborted model node, fan-out crash, page corruption) | 0 | `next ('M03',)` -> `dest ['D91'] reclass [{'from': 'M03', 'to': 'D91'}]`; `join {... 'pending': ['bad'], 'satisfied': False}`; `detected: sqlite refused the checkpoint database: database disk image is malformed` |
| 5 | `PYTHONPATH=<repo> /tmp/plan26_n21_verify/bin/python -m pytest -q tests/runtime/test_plan26_persistence.py` (first attempt) | 1 | `4 failed, 50 passed, 42 subtests passed` — see Findings F1 |
| 6 | `PYTHONPATH=<repo> /tmp/plan26_n21_verify/bin/python -m pytest -q tests/runtime/test_plan26_persistence.py` (after the F1 fix) | 0 | **`51 passed, 45 subtests passed in 3.35s`** — the primary evidence for this node |
| 7 | `PYTHONPATH=<repo> /tmp/plan26_n21_verify/bin/python -m pytest tests/runtime/test_plan26_persistence.py -v` | 0 | 51 named tests listed, all `PASSED`, none skipped in the locked environment |
| 8 | `PYTHONPATH=<repo> /tmp/plan26_n21_verify/bin/python -m pytest -q tests/runtime/test_plan26_api_contract.py tests/runtime/test_plan26_state_reducers.py tests/runtime/test_plan26_evidence.py tests/runtime/test_plan26_persistence.py` | 0 | `141 passed, 233 subtests passed` — no cross-node regression against N10/N11/N12 in the locked environment |
| 9 | `/opt/homebrew/bin/python3 -c "from runtime.langgraph_factory import persistence as P; ..."` | 0 | `ambient import OK .langgraph/checkpoints.sqlite3 run-a3de27ab78e042ba` — the module imports and derives ids without langgraph installed |
| 10 | `/opt/homebrew/bin/python3 -m pytest -q tests/runtime/test_plan26_persistence.py -rs` | 0 | `1 skipped` — `SkipTest: plan26 hash-locked environment not installed ... No module named 'langgraph'` (module-level, same technique as N10's `test_plan26_api_contract.py`) |
| 11 | `/opt/homebrew/bin/python3 -m pytest -q` | 0 | **`377 passed, 3 skipped, 282 subtests passed in 108.06s`** |
| 12 | `shasum -a 256 <every path hashed in this record>` | 0 | the Hashes table below |
| 13 | `PYTHONPATH=<repo> /tmp/plan26_n21_verify/bin/python -m pytest -q tests/runtime/test_plan26_persistence.py` (after the F-04 rework) | 0 | **`53 passed, 45 subtests passed in 2.64s`** — the 51 originals plus the two new D98 interop tests |
| 14 | `PYTHONPATH=<repo> /tmp/plan26_n21_verify/bin/python -m pytest -q tests/runtime/test_plan26_api_contract.py tests/runtime/test_plan26_state_reducers.py tests/runtime/test_plan26_evidence.py tests/runtime/test_plan26_deterministic_nodes.py tests/runtime/test_plan26_persistence.py` | 0 | `360 passed, 233 subtests passed` — N22's own D98 suite still green alongside this node after the rework |
| 15 | `python3 -m pytest -q` (ambient, after the F-04 rework) | 0 | **`746 passed, 3 skipped, 282 subtests passed in 112.94s`** — this module still self-skips ambiently; the skip set is unchanged |
| 16 | `/tmp/plan26_n21_verify/bin/python -m pytest tests/runtime/test_plan26_persistence.py -q` (after the B-5 rework) | 0 | **`53 passed, 45 subtests passed in 2.48s`** — same test count as command 13; the previously failing subtest `field='checkpoint_ns'` is now `field='checkpoint_namespace'` and green |
| 17 | `python3 -m pytest -q` (ambient, after the B-5 rework) | 0 | **`746 passed, 5 skipped, 282 subtests passed in 108.64s`** — matches N30's recorded ambient baseline exactly; the two additional skips are N30's and a sibling's own module self-skips, not this node's |

Command 11 versus the pre-N21 state (`377 passed, 2 skipped`): `+0 passed`,
`+1 skipped`. The added skip is this node's own module self-skipping in the
ambient interpreter; no pre-existing test changed status, so the N00 baseline
(175 passed / 54 subtests, fully contained in the current run) is preserved.
The three ambient skips are `test_plan26_api_contract.py` (N10, whole module),
`test_regeneration_is_byte_identical_to_the_committed_lock` (N10), and
`test_plan26_persistence.py` (N21, whole module) — all three run for real in a
hash-locked environment, this node's under command 6.

Commands 1-12 are the original pass; commands 13-15 are the F-04 rework. The
ambient total rose from 377 to 746 between them because sibling nodes landed in
the interim; the skip set is unchanged at 3, and this node's module is still one
of them.

Environment used (not committed): `/tmp/plan26_n21_verify` — CPython 3.13.1,
`requirements/plan26.lock` installed with `--require-hashes`.

## Tests

Prompt TEST items, each mapped to the assertions that back it. Every verdict
below comes from command 6 (real `SqliteSaver` over real `sqlite3`, real
compiled graphs, real killed processes), not from a mock.

| TEST item | Verdict | Backing assertion |
|---|---|---|
| 1. Checkpoint path/pragmas/thread/namespace match the spec | PASS | `TestCheckpointConfiguration`, 11 tests. `test_checkpoint_database_lives_at_the_spec_path` asserts the file exists at `<output_root>/.langgraph/checkpoints.sqlite3`; `test_live_connection_reports_the_required_pragmas` asserts `journal_mode=wal`, `synchronous=2`, `foreign_keys=1`, `busy_timeout=30000` off the live connection; `test_wal_mode_is_visible_in_the_actual_sqlite_file_header` reads bytes 18/19 of the committed file and asserts `(2, 2)`; `test_a_relaxed_pragma_is_refused_rather_than_silently_accepted` sets `synchronous=OFF` and asserts `CheckpointCorrupt`; `test_saver_tables_exist_in_the_real_database` asserts `checkpoints`/`writes` in `sqlite_master`; `test_a_real_checkpoint_is_stored_under_the_root_namespace` asserts `SELECT DISTINCT thread_id, checkpoint_ns FROM checkpoints == [(thread_id, "")]` after a real invoke; `test_thread_ids_follow_the_frozen_format` and `test_invoke_config_is_exactly_thread_id_and_root_namespace` pin both id formats and the exact config dict; `test_strict_msgpack_is_enforced_for_persisted_values` asserts the env var. |
| 2. State snapshots, `next/tasks`, pending writes, and evidence high-water marks correlate | PASS | `TestSupersepCorrelation.test_snapshot_next_tasks_and_evidence_marks_correlate_after_a_superstep`: real two-node graph invoked over the saver; asserts `snapshot.next == ()`, `tasks == ()`, `pending_writes == ()`, `history_length > 1`, and `state_digest == canonical_digest({"seen": ["D05","D13"]})`; then writes an activation and an execution record into N12's `EvidenceStore` and asserts the emitted `checkpoints` record carries the same `checkpoint_id`, `checkpoint_ns == ""`, matching `state_digest`, `thread_id`, `evidence_ordinal == 1`, and `evidence_high_water == {activations: 1, executions: 1, ...}`. `test_a_correlation_record_is_hash_chained_and_tamper_evident` flips the recorded digest in the log file and asserts the chain audit flips from pass to fail. |
| 3. Crash around every checkpoint/admission boundary duplicates no committed work | PASS | `TestCrashMatrix.test_a_real_sigkill_at_every_boundary_duplicates_no_committed_work`, 3 subtests (`before_admit`, `after_admit`, `after_checkpoint`). Each spawns a real child process that acquires the lock, opens the real saver, runs a real graph, and calls `os.kill(os.getpid(), SIGKILL)` at the named boundary; the test asserts `returncode == -SIGKILL`, then asserts the admission count before retry (0/1/1), that the retry's `was_new` matches, and that exactly one record exists for the key afterwards — twice. `test_a_differing_replay_under_a_committed_key_is_an_integrity_failure` asserts `AdmissionConflict` and an unchanged ledger. `test_completed_sibling_work_replays_its_write_instead_of_re_executing` asserts `ok.count("good") == 1` and `executions == ["good"]`, i.e. the committed task replayed its write rather than re-running. |
| 4. Successful fan-out pending writes survive sibling crash but cannot satisfy a partial join | PASS | `TestFanoutSiblingCrash.test_surviving_pending_write_cannot_satisfy_a_partial_join`: real two-way fan-out where one node raises; asserts the surviving `ok` channel is present in the real `CheckpointTuple.pending_writes`, that the readout preserves it, that `readout.next` still contains the crashed sibling, and that `frontier["joins"]["visual_result"]` is `satisfied=False` with `pending=["bad"]`, `completed=["good"]`. `test_join_is_satisfied_only_when_every_denominator_member_completed` additionally rejects an empty denominator and raises on a completed member outside the denominator. |
| 5. Resume refuses identity/digest/executable/evidence/accepted-byte drift | PASS | `TestResumeRefusal`, 9 tests / 16 subtests. `test_every_drift_class_refuses_resume` covers all six drift rows (`identity`, `frozen_digest`, `executable`, `evidence`, `accepted_bytes` for both accepted receipt hashes and accepted byte digests) and asserts the exact `drift_class`/`field` on the raised `ResumeRefused`; `test_matching_inputs_are_admitted` proves the negative control; `test_an_unclassified_input_is_refused_rather_than_ignored` and `test_a_missing_baseline_key_is_refused` close the "unknown difference" hole; `test_non_resumable_terminals_are_rejected` covers all four non-resumable and both resumable terminals; `test_refused_resume_performs_no_product_work` snapshots every product file's mtime_ns+sha256 and the whole episode ledger, drives a real refusal through `prepare_episode_invocation`, and asserts both are byte-identical afterwards; `test_run_id_disagreement_with_the_envelope_refuses`, `test_a_fresh_invocation_over_a_prior_identity_is_refused`, and `test_identity_envelope_bytes_are_immutable` pin identity handling. |
| 6. Graceful interrupt writes one episode terminal and deterministic safe frontier | PASS | `TestGracefulInterrupt`, 4 tests. `test_sigint_sets_the_token_and_blocks_new_transmission` installs the token, asserts transmission is allowed before, raises a **real** `SIGINT` via `signal.raise_signal`, then asserts the token is set, the reason is `SIGINT`, `guard_transmission` raises `InterruptionRequested`, and the durable marker file contains `INTERRUPTED`; `test_sigterm_is_handled_the_same_way` repeats for `SIGTERM`. `test_interrupt_writes_one_terminal_and_a_deterministic_safe_frontier` aborts a real graph at a node boundary, computes the frontier twice and asserts equal `frontier_digest` and equal dicts, asserts `destinations == ["D13"]`, builds exactly one `INTERRUPTED` terminal candidate bound to that digest, closes the lease, asserts exactly one `CLOSED` record, and asserts a second close raises `EpisodeLedgerError`. `test_frontier_digest_changes_when_the_frontier_changes` proves the digest is not a constant. After the F-04 rework this class also holds `test_the_candidate_is_accepted_by_the_real_d98_validator` — the candidate is passed through N22's real `nodes.terminal.validate_terminal_candidate` and `write_terminal`, asserting `accepted is True`, `kind == "INTERRUPTED"`, `exit_code == 10`, `resumable is True`, and that a stale-head variant is still rejected — and `test_the_classification_vocabulary_matches_d98s_authority`. Verdicts from command 13. |
| 7. Orphan recovery runs only D00/D96/D98 and performs zero product side effects | PASS | `TestOrphanRecovery`, 6 tests. `test_recovery_after_sigkill_uses_a_new_thread_and_touches_no_product` writes real accepted product bytes, runs a real child that prepares a fresh episode, invokes a real graph, and then `SIGKILL`s itself before D98; asserts the lease is left open, snapshots every product file, then asserts the resume yields `bootstrap_kind == RECOVER_ORPHAN`, `prior_thread_id == <orphan>`, `thread_id == f"{run_id}:recover:1"` (a different thread), `checkpoint_ns == ""`, a populated `resume_from`, and a byte-identical product snapshot. `test_recovery_services_raise_on_any_touch` (3 subtests) asserts every attribute access and every call on the transport registry, source retriever, and renderer raises `RecoveryServiceForbidden`. `test_a_recovery_runtime_context_carries_only_forbidden_product_services` builds a real N11 `RuntimeContext` with them and asserts transport/retriever access raises while the evidence writer still works (D96/D98 must record). `test_the_read_only_view_cannot_continue_a_prior_thread` (5 subtests) and the two AST tests make "never invoke a prior thread" and "never reach a product module" structural. |
| 8. Uncertain model activation enters D91 after D03, never direct redispatch | PASS | `TestModelFrontierRouting`, 3 tests / 8 subtests. `test_an_aborted_model_node_frontier_becomes_d91` runs a real `START -> D03 -> M03` graph whose `M03` raises, asserts the **real** `snapshot.next == ("M03",)`, then asserts `compute_resume_frontier` yields `destinations == ["D91"]`, `reclassified == [{"from": "M03", "to": "D91"}]`, and that no member of `MODEL_NODE_IDS` survives as a destination. `test_every_model_node_id_is_reclassified` repeats for all eight of M01-M08. `test_deterministic_destinations_are_preserved_unchanged` proves deterministic nodes are not rewritten. |
| 9. Duplicate process has one lock winner; loser mutates nothing | PASS | `TestExecutionLockRace`, 3 tests. `test_two_real_processes_race_and_the_loser_mutates_nothing` has the parent hold the lock and open the real saver, writes an accepted product file, snapshots `(mtime_ns, sha256)` for **every** file under the output root including `.langgraph/` control files, spawns a real second process, and asserts it exits `LOCK_LOSER_EXIT_CODE == 3` printing `LOSER` and never `WINNER`, and that the full snapshot is identical before and after. `test_the_lock_is_reacquirable_once_the_winner_releases` proves the lock is not simply always-failing. `test_a_second_in_process_acquisition_is_also_refused` covers the in-process case. |
| 10. Either checkpoint or append-log corruption blocks recovery without self-repair | PASS | `TestCorruptionBlocksRecovery`, 5 tests. `test_a_healthy_root_verifies_on_both_layers` is the negative control. `test_corrupt_sqlite_blocks_recovery_and_is_not_repaired` truncates the WAL, overwrites 512 bytes of a real data page, asserts both ledgers still audit `PASS` (independent layer), asserts `verify_checkpoint_integrity`, `verify_persistence_integrity`, and `prepare_episode_invocation(resume=True)` all raise `CheckpointCorrupt`, and asserts the database digest is unchanged afterwards. `test_corrupt_append_log_blocks_recovery_and_is_not_repaired` is the mirror image: SQLite still verifies `ok`, the flipped `episodes.jsonl` audits `FAIL`, resume raises, and the file digest is unchanged. `test_a_truncated_append_log_is_detected` covers a torn append. `test_evidence_log_corruption_alone_blocks_recovery` covers N12's logs as the third independent surface. |

Additional coverage beyond the prompt's ten items, all in command 6:
`TestEpisodeLifecycle` (3 tests / 6 subtests) proves each episode gets a new
thread whose LangGraph state is genuinely empty (`saver.get_tuple(new_config)`
is `None`, `get_state(new_config).values == {}`), that lease ordinals are
compare-and-swap protected against double-open and out-of-order open, and that
every field of `EpisodeInvocation.as_state_update()` exists in N11's
`FACTORY_STATE_FIELDS`.

## Findings

- **B-5 REWORK (generation 7) — `as_state_update()` emitted the pre-erratum
  channel name `checkpoint_ns`.** Owner: N21 (this node). Disclosed by
  N30_UNIT_GRAPH as finding B-5, fingerprint
  `plan26/n30/erratum-under-applied-persistence-state-update`. Cause: when
  [[erratum_checkpoint_ns_rename.v1]] landed, `persistence.py`'s surviving
  `checkpoint_ns` occurrences were audited and classified wholesale as "the
  LangGraph invoke-config key or this node's own dataclass field". That was true
  of eight of the nine; `persistence.py:1264` is the ninth, and it is neither —
  it is the top-level key of a `FactoryState` *update* dict, which the erratum
  puts squarely in scope. A prepared episode's seed update therefore named a
  channel the compiled graph does not have. Resolution: that one key is now
  `"checkpoint_namespace"`; `tests/runtime/test_plan26_persistence.py`'s
  assertion follows it. The remaining eight occurrences were re-classified
  individually rather than in bulk this time, and each is confirmed out of
  scope: `invoke_config()` (line 277) builds LangGraph's own required
  `config["configurable"]["checkpoint_ns"]`; `ResumeReadout.as_dict()` (686) and
  the resume-frontier dict (1114) are nested payloads *inside* the `resume_from`
  / `resume_frontier` channels, which the erratum exempts explicitly; the
  `checkpoints` evidence record (1186) is the append-only JSONL schema the
  erratum also exempts by name; and 1248/1324/1368/1399 are the
  `EpisodeInvocation.checkpoint_ns` dataclass field and its three constructor
  sites, an internal attribute of this node with no channel identity. Nothing
  outside this node's `writes` set changed; the erratum itself was left
  unedited because concurrent siblings hold that directory.
- **F-04 REWORK (same generation) — `build_interrupt_terminal_candidate()`
  emitted a shape D98 would reject.** Owner: N21 (this node). Disclosed by
  N22_DETERMINISTIC_NODES as finding F-04. Fingerprint:
  `interrupt-candidate-shape-mismatch-with-d98`. Cause: this node and N22 built
  the interrupt candidate and its validator concurrently. The candidate carried
  `terminal="INTERRUPTED"`, a free-text `reason`, and only
  `resume_frontier_digest`; `nodes/terminal.py`'s `_validate_interrupted`
  requires `kind="INTERRUPTED"`, a `classification` in
  `{graceful_signal, crashed_episode}`, the full `resume_frontier` dict,
  `heads` (cross-checked against `projection["artifact_heads"]` and rejected if
  stale), and `high_water_marks`. D98 would have downgraded every graceful
  interrupt to `SYSTEM_FAILURE` — safe, but wrong — the moment N30 wired D96
  through to D98.
  Fix, entirely inside this node's `writes` set:
  `build_interrupt_terminal_candidate()` now takes `classification`, `heads`,
  and `high_water_marks` instead of `reason`, and emits `kind`,
  `classification`, `resume_frontier` (the whole frontier dict),
  `resume_frontier_digest` (kept for correlation), `destinations`, `heads`,
  `high_water_marks`, `run_id`, `episode_id`, `candidate_digest`. `heads` and
  `high_water_marks` are parameters rather than internal computations because
  the caller — D96 in N22's `nodes/inputs.py`, wired by N30 — is what holds
  live artifact heads; `persistence.py` does not own that runtime context under
  [[node_ownership.v1]] and must keep importing no node module (the AST import
  scan still passes). A new module constant `INTERRUPT_CLASSIFICATIONS` mirrors
  D98's `_INTERRUPT_CLASSIFICATIONS` rather than importing it, for the same
  reason; an out-of-vocabulary classification now raises `PersistenceError` at
  build time instead of producing a candidate D98 would reject.
  Backing evidence: two new tests in `TestGracefulInterrupt`, run in the
  hash-locked environment (command 13).
  `test_the_candidate_is_accepted_by_the_real_d98_validator` builds a real
  frontier from a real readout, builds the candidate, projects a realistic D98
  state through N22's own `nodes.project("D98_WRITE_TERMINAL", ...)`, and
  asserts `nodes.terminal.validate_terminal_candidate(...).accepted is True`
  with `kind == "INTERRUPTED"`; it then calls the real
  `nodes.terminal.write_terminal(projection)` and asserts the written record is
  `INTERRUPTED` / `exit_code == 10` / `resumable is True` carrying the full
  frontier, and finally asserts a candidate with a stale head is still rejected,
  so the test proves interoperability rather than merely disabling the check.
  `test_the_classification_vocabulary_matches_d98s_authority` asserts
  `P.INTERRUPT_CLASSIFICATIONS == terminal._INTERRUPT_CLASSIFICATIONS`, so the
  restated constant cannot silently diverge. `generation` stays 3: this is a
  same-generation correction to this node's own output, not a new scheduler
  pass. `runtime/langgraph_factory/nodes/terminal.py` was read as the contract's
  source of truth (`66e7b92752d8ab8e0a93e00fc50114331f74f34538358b9b2938a6f02c17f28d`)
  and was not modified; no file outside this node's `writes` set changed.
- **F1 — a recovery lease must be openable while its orphan lease is still
  open.** Owner: N21 (resolved in-node; no rework edge fired). Evidence key:
  command 5, `EpisodeLedgerError: an episode lease is still open; close or
  recover it first` raised from `prepare_episode_invocation` in
  `test_recovery_after_sigkill_uses_a_new_thread_and_touches_no_product`.
  Fingerprint: `episode-lease-cas-blocks-orphan-recovery`. Cause: the first
  compare-and-swap rule refused any new lease while one was open, which is
  correct for a product episode but contradicts spec 11.3 — recovery exists
  *because* the orphan is still open. Resolution: `open_episode()` admits a
  `RECOVER_ORPHAN` lease over exactly one open non-recovery lease, refuses a
  second concurrent recovery, and refuses a recovery with no orphan;
  `open_lease()` returns the earliest open non-recovery lease so the orphan (not
  the recovery) is what a resume must close; `close_episode()` closes by
  ordinal rather than assuming the newest lease. Command 6 is green.
- **F2 — `test_plan26_persistence.py` self-skips where the locked environment
  is absent.** Owner: N21. Evidence key: command 10 / command 11 skip counts.
  Fingerprint: `persistence-module-skip-without-lock-env`. Same technique and
  same rationale as N10's F2: the ambient interpreter has no `langgraph`, so
  the module skips at import to preserve the repository baseline, while the
  hash-locked environment runs all 51 tests for real (command 6). Not blocking.
  Open obligation for N10's owner: `.github/workflows/plan26-lock-drift.yml`
  currently names only `test_plan26_api_contract.py` and
  `test_plan26_lock_drift.py` in its test step, so CI does not yet execute this
  module. That file is outside this node's `writes` set and was deliberately not
  edited. Until it names `tests/runtime/test_plan26_persistence.py`, this node's
  proof rests on command 6 rather than on CI.
- **F3 — `classify_join_members()` lives in `persistence.py`, adjacent to
  N31's acceptance engine.** Owner: N31_REPAIR_ACCEPTANCE. Evidence key:
  `compute_resume_frontier(... denominators=...)`. Fingerprint:
  `join-classification-shared-with-acceptance`. The resume frontier cannot be
  computed without deciding which denominator members are still pending, so the
  primitive is here; it is deliberately minimal (expected/completed/pending/
  satisfied, rejecting members outside the denominator) and asserts nothing
  about acceptance. N31 owns the acceptance semantics and should call this
  rather than write a second, divergent partial-join rule.
- **F4 — the identity envelope holds only the eight identity-seed fields.**
  Owner: N22_DETERMINISTIC_NODES (D00R/D01/D04 bodies). Evidence key:
  `write_identity_envelope` / `validate_resume_inputs(expected=...)`.
  Fingerprint: `resume-baseline-assembled-by-caller`. `frozen_digest`,
  `frozen_executable_identities`, evidence chain hashes, accepted receipt
  hashes, and accepted byte digests are not knowable at pre-invocation time and
  several of them legitimately change as a run progresses, so they are supplied
  by the caller as `resume_baseline` from what the prior episode durably
  recorded. D00R must assemble that baseline from the append-only receipts;
  passing an empty baseline while also passing recomputed values raises
  `ResumeRefused` rather than silently admitting, so the failure mode is closed.

No blocking finding is open.

## Invalidated descendants

None. First-pass `PASSED`; no rework edge fired. F1 was diagnosed and fixed
inside this node's LOOP bound (one repair, one repeat of the same command), so
no descendant was invalidated.

## Hashes

Consolidated, deduplicated. `sha256` over raw file bytes per
[[digest_algorithm.v1]], computed with `shasum -a 256`.

| Path | sha256 |
|---|---|
| `plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml` | `96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8` |
| `plans/26_langgraph_curriculum_factory/prompts/N21_persistence_resume.prompt.v1.md` | `3b0d3ee5aabe8cc77401cad14314f36f5af2635d752d996955ec1e6e863f1d36` |
| `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md` | `44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6` |
| `plans/26_langgraph_curriculum_factory/qa_criteria.v2.md` | `163154480dc0a851ca597fdfaf62a71840a2cdd212fad8fa196b02dc152edded` |
| `plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md` | `896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af` |
| `plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md` | `063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0` |
| `plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md` | `c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2` |
| `plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md` | `d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad` |
| `plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md` | `7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7` |
| `plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md` | `edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b` |
| `plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md` | `c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5` |
| `plans/26_langgraph_curriculum_factory/results/N10_DEPENDENCY_API.result.v1.md` | `1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658` |
| `plans/26_langgraph_curriculum_factory/results/N11_STATE_REDUCERS.result.v1.md` | `c89f166596633e2027f04daa03fca9a33e9f23f2c1346f77817e44b8c03dc30e` |
| `plans/26_langgraph_curriculum_factory/results/N12_EVIDENCE_ARTIFACTS.result.v1.md` | `6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f` |
| `requirements/plan26.lock` | `df971a783b9d027db96eae800e33e7bc65471b94f7a3b0a151eec075e0824835` |
| `runtime/langgraph_factory/state.py` | `873d640ff2b7e677818fa74d514211e104797b3d3d48dfad4d7d7d47197cd74a` |
| `runtime/langgraph_factory/reducers.py` | `05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf` |
| `runtime/langgraph_factory/evidence.py` | `95ddef6f9e1e5e7031f223d88b285b2b0ffbdd604c70181ae87ad8a21220c199` |
| `runtime/langgraph_factory/artifacts.py` | `dfb1efa93c0c267b0ae282c9687d769ef043b31c363526871e7212e2890b86cf` |
| `runtime/langgraph_factory/nodes/terminal.py` | `66e7b92752d8ab8e0a93e00fc50114331f74f34538358b9b2938a6f02c17f28d` |
| `runtime/langgraph_factory/persistence.py` | `c2b3eb236d2ea7bb6ca7f0ff5d6258c8bd1fdec8cf36d9520c2b2ddb9298b289` |
| `tests/runtime/test_plan26_persistence.py` | `c3863a74512ee8d79e0ed92db768553a605265984be489191c0b9084e2ab6a94` |

Locked-environment distributions this node's proof actually executed against
(from `requirements/plan26.lock`, installed with `--require-hashes` in
`/tmp/plan26_n21_verify`):

| Distribution | sha256 (wheel, sdist) |
|---|---|
| `langgraph==1.2.9` | `385f87bc1802c35af7e0aa479278ecba8582d103515eb48256cb2ddcd42d0bd4`, `c2d98ad94333937922ba04148641c1da2bfe45b5b8e55d7b6dcb0bb2df809e76` |
| `langgraph-checkpoint-sqlite==3.1.0` | `cc9b40df0076feae8a9ad42ae713621b148b00ac23adc09dc1dc66090a46e5ad`, `f926916ebc1b985d802cc9c820026036e84db9d910d62c97b57e4ba64f67d5ae` |
| `langgraph-checkpoint==4.2.0` | `0547fd228935a0b758865de3a3d6d7a2537c308895d0f9ab092ce9151b5da942`, `51a593b6bee684b0818e5d6e58e28ab340c6db7794575056ce7bd1b746a84ed7` |
