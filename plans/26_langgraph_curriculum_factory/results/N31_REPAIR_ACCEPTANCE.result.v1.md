# N31_REPAIR_ACCEPTANCE result

status: PASSED
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N31_repair_acceptance.prompt.v2.md
predecessor: N30_UNIT_GRAPH (compact state supplied by the controller, status PASSED)
generation: 1

## What this node built

Two new top-level modules, per `contracts/node_ownership.v1.md` ("N31 owns
repair/acceptance modules, not terminal.py"):

- `runtime/langgraph_factory/repair.py` — D17 (finding classification), D18
  (targeted repair planning), D19 (deterministic-vs-model routing), D20
  (boundary-checked admission), D21 (retest dispatch).
- `runtime/langgraph_factory/acceptance.py` — D16 (unit denominator
  reduction), D22 (recompute-and-accept), D23 (checkpoint correlation +
  cursor advance), plus `prove_exact_manifest_coverage()`, the D24 coverage
  predicate N32 will call.

Neither module is registered into the compiled graph yet. `routing.py`'s
guard tables for D16-D23 already exist (built by N20) and this generation's
functions emit exactly the guard values those tables declare
(`unit_denominator_passed`/`unit_findings_repairable`,
`partition_complete`/`convergence_exhausted`, `repair_planned`,
`model_repair`/`deterministic_repair`, `repair_admitted`,
`retest_frontier_incomplete`/`retest_frontier_complete`, `unit_accepted`,
`checkpoint_correlated`) — but `add_node`/`add_conditional_edges` wiring
these into `graph.py`'s `StateGraph` is N32's write
(`implementation.graph.v3.yaml`: N32 owns `runtime/langgraph_factory/graph.py`,
N31 does not). Every function here is therefore a plain, narrowly-scoped
`(state, runtime_context) -> update` callable in the same shape N23's
`model_nodes.py` already uses for D90/D91 — not wrapped in
`nodes.deterministic_node()`, since that decorator requires a
`NODE_CATALOGUE` row this generation is not permitted to add (`nodes/__init__.py`
is not in N31's write set). A future node binds these to catalogue rows
without changing this module's bodies.

`tests/runtime/test_plan26_repair_acceptance.py` calls every function
directly against hand-built `FactoryState` fixtures, merged step-to-step
through the real field reducers (`state.FIELD_REDUCERS`), not a mock merge.

## Owner / retest map

| Owner | Channel | Repair route (this generation) | First retest node |
|---|---|---|---|
| source interpretation | domain | model (M06) | `D07_CORRELATE_AND_ADMIT_SOURCES` |
| curriculum domain | domain | model (M06) | `D08_VALIDATE_DOMAIN` |
| unit content | content | model (M06) | `D09_VALIDATE_CONTENT` |
| unit visual | visuals | model (M06) unless every named key is an authoritative/library brief, then deterministic | `D10_COMPILE_VISUAL_BRIEFS` |
| unit layout | layout | deterministic (boundary-scoped pointer correction) | `D13_RENDER_UNIT` |

`repair.RETEST_ORDER_BY_OWNER` carries each owner's full fixed chain (spec
section 12's table); D21 dispatches only the first node of that chain — the
remaining steps are the already-wired unit-path edges (N30) that node's own
success guard reaches on its own, so D21 is never re-entered for the same
repair admission.

Frozen limits, enforced exactly where spec section 6.2 assigns them: D17
owns the repeated-fingerprint bound (`MAX_FINGERPRINT_REPEATS = 2`); D18 owns
the numeric attempt bound (`MAX_REPAIR_CHILDREN_PER_CHAIN = 3`). An earlier
draft of this generation checked both bounds in D17, which made
`test_attempt_bound_exhausts_before_a_fourth_repair_child` fail (D17 was
exhausting a case the prompt's own TEST item expects D18 to exhaust) — fixed
by removing the attempt-bound check from D17, per spec's own row split ("D17
... repeated bound = exhaustion" vs. "D18 ... attempt bound = exhaustion").

## Denominator trace (D16 / D22, `acceptance.compute_unit_denominator`)

Recomputed identically by D16 (before repair) and D22 (immediately before
minting an accepted receipt) off whatever heads are *current* at call time.
Categories enforced this generation: source admission (sha256-resolved),
domain check set (`DOMAIN_CHECK_IDS`, matched by current head hash), content
check set (`CONTENT_CHECK_IDS`, matched by current head hash), visual join
result, page inventory + inspection set (exact page count, all PASS), one
independent unit review with every blocking finding's `category` mapped
through the code-owned `owner_for_review_category()` table (never trusted
verbatim from the model), and repair-request closure (no request left
unresolved). `test_removing_or_failing_any_single_member_makes_d22_reject`
independently removes/fails each of the five owner-bearing categories and
confirms D22 raises every time; `test_staling_the_content_head_makes_d22_reject`
confirms a check recorded against a superseded head is invisible to the
reduction (stale evidence cannot pass) without needing to delete anything —
`compute_unit_denominator` only counts a check whose `head_hash` equals the
*current* head.

Documented, not silently assumed, scope limit: this generation's denominator
treats the append-only evidence/log layer and the LangGraph checkpoint layer
as structurally present (state reducers already enforce their shape) rather
than independently re-auditing their hash chain from inside D22 (spec
section 13.1 items 13-14). `acceptance.py`'s module docstring records this so
a future generation tightens it rather than rediscovering the gap.

## Real-D98 traces (TEST 9)

`tests/runtime/test_plan26_repair_acceptance.py` imports
`runtime.langgraph_factory.nodes.terminal` unmodified and calls
`terminal.write_terminal()` directly — the identical function N22 wrote and
N32 will call for its two product-terminal sites — never a stand-in:

- `test_a_unit_accepted_candidate_traverses_the_real_d98_and_is_accepted`:
  a `UNIT_ACCEPTED` candidate built from this generation's real D22/D23
  output is independently re-derived and accepted by D98's own
  `_validate_unit_accepted`.
- `test_a_tampered_unit_accepted_candidate_is_rejected_by_the_real_d98`: the
  same candidate with a forged `receipt_hash` is rejected and D98 writes
  `SYSTEM_FAILURE` in its place — no N31 code decided that; D98's own
  re-derivation did.
- `test_a_convergence_exhausted_candidate_from_d17_traverses_the_real_d98`:
  the `terminal_candidate` D18 proposes on attempt-bound exhaustion is
  independently accepted by D98's `_validate_exhausted`.

No test in this file, and no code in `repair.py`/`acceptance.py`, writes to
`nodes/terminal.py`; `terminal.write_terminal.__module__` is asserted to
still be `runtime.langgraph_factory.nodes.terminal`.

## Commands and results

```
/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_repair_acceptance.py -v
=> 32 passed in 0.08s
(results/evidence/N31_REPAIR_ACCEPTANCE/focused_test_run.txt)

/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/ -k plan26 -q
=> 916 passed, 1 skipped, 175 deselected, 345 subtests passed, 4 failed
(results/evidence/N31_REPAIR_ACCEPTANCE/full_plan26_suite.txt)
```

The 4 failures are all in `test_plan26_prompt_graph_controller.py`
(`test_mechanical_revalidation_*`, `test_passed_nodes_remain_admissible_and_n31_is_the_sole_frontier_after_harness_change`)
and are pre-existing environment state, not a regression this node
introduced: the working tree at session start already carried numerous
deleted `results/v3/*.receipt.v1.json` and `results/v3/logs/**` files (see
`git status` at session start), which is exactly the receipt evidence those
controller tests read to decide whether `N30_UNIT_GRAPH` shows `PASSED`.
Neither `repair.py`, `acceptance.py`, nor the new test file touches
`prompt_graph_controller.py` or any receipt file; `N31_REPAIR_ACCEPTANCE`'s
own declared writable-paths set does not include them either. Re-verified by
inspection: the 4 failing tests assert on `state["statuses"]["N30_UNIT_GRAPH"]
== "PASSED"`, sourced from those now-missing receipts, not from anything this
node wrote.

## Hashes

| File | SHA-256 (shasum -a 256) |
|---|---|
| `runtime/langgraph_factory/repair.py` | `9e9013e51d4e339838e9d72916ee04cf47ff0a6e3dcf80383bd7f2d0a744af1e` |
| `runtime/langgraph_factory/acceptance.py` | `f5c0445eec0f3a4685ac4847565e22294db5ac3a7c030fa1c5a0fea267ae89bb` |
| `tests/runtime/test_plan26_repair_acceptance.py` | `99add3d695747e901a458d07e673130a999936e91f0fab6657ccd0a2cb651ee8` |

## TEST item verdicts

1. **PASSED** — `test_d17_rejects_a_finding_with_no_owner`,
   `test_d17_rejects_a_finding_with_an_unknown_owner`,
   `test_d17_partitions_a_multi_owner_findings_list_into_separate_owner_entries`,
   `test_review_finding_category_is_never_trusted_as_an_owner`.
2. **PASSED** — `test_a_correctly_scoped_model_repair_admits`,
   `test_a_broad_repair_outside_its_boundary_is_refused`,
   `test_an_in_place_no_op_repair_is_refused`,
   `test_a_stale_parent_repair_is_refused`,
   `test_a_deterministic_layout_repair_changes_only_its_allowed_pointer`.
3. **PASSED** — `test_attempt_bound_exhausts_before_a_fourth_repair_child`,
   `test_fingerprint_repeat_bound_exhausts_at_d17`.
4. **PASSED** — `test_d21_dispatches_the_first_retest_node_of_the_owners_fixed_chain`,
   `test_stale_evidence_at_an_old_head_cannot_pass_the_denominator`.
5. **PASSED** — `test_d22_accepts_a_fully_passing_denominator`,
   `test_removing_or_failing_any_single_member_makes_d22_reject` (×5),
   `test_staling_the_content_head_makes_d22_reject`.
6. **PASSED** — `test_accept_once_refuses_a_differing_second_write_for_the_same_unit`,
   `test_an_already_accepted_unit_can_never_re_enter_classification_or_planning`.
7. **PASSED** — `test_d23_writes_checkpoint_metadata_and_cursor_in_the_same_update`,
   `test_d23_refuses_to_advance_the_cursor_with_no_accepted_receipt`.
8. **PASSED** — `test_coverage_proof_rejects_missing_extra_reordered_and_wrong_hash`.
9. **PASSED** — `test_a_unit_accepted_candidate_traverses_the_real_d98_and_is_accepted`,
   `test_a_tampered_unit_accepted_candidate_is_rejected_by_the_real_d98`,
   `test_a_convergence_exhausted_candidate_from_d17_traverses_the_real_d98`.
10. **PASSED** — `test_repeating_d22_after_a_crash_replays_idempotently`,
    `test_repeating_d23_after_a_crash_replays_idempotently`,
    `test_re_admitting_the_same_repair_after_the_head_already_advanced_fails_closed`,
    `test_a_crash_before_the_terminal_write_still_lets_d98_be_invoked_cleanly`.

## Known scope limitations (for N32 and future generations)

- The deterministic-vs-model routing table for `source interpretation` is
  simplified to always route to M06 in this generation; spec section 12
  allows a deterministic refetch when a locator remains authorized, which
  would require a source-retrieval integration this node's write set does
  not include (`repair.py`'s module docstring records the reasoning).
- `compute_unit_denominator()`'s coverage of spec section 13.1 items 13-14
  (append-log/evidence-index and checkpoint/state-digest integrity) is
  structural, not a byte-level hash-chain re-audit from inside D22.
- Registration of D16-D23 into the compiled `StateGraph` (`add_node`,
  `add_conditional_edges`) is N32's write, per `implementation.graph.v3.yaml`
  and `contracts/node_ownership.v1.md`; this generation does not add or edit
  a line of `graph.py`, `unit_graph.py`, `routing.py`, or `nodes/__init__.py`.
