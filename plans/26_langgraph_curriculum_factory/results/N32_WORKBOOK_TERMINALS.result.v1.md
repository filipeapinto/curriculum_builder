# N32_WORKBOOK_TERMINALS result

status: PASSED
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N32_workbook_terminals.prompt.v2.md
predecessor: N31_REPAIR_ACCEPTANCE (compact state supplied by the controller, status PASSED)
generation: 1

## What this node built

One new top-level module and one edited module, per
`contracts/node_ownership.v1.md` ("`runtime/langgraph_factory/workbook.py`
(top-level, owned by N32) is the workbook assembly/coverage/release engine
(D24, D25, D26, D27, D29, D31, D32) plus the two product-terminal call
sites"):

- `runtime/langgraph_factory/workbook.py` — D24 (exact manifest coverage;
  one-mode `UNIT_ACCEPTED` candidate, all-mode workbook branch), D25
  (assembly, over byte-verified accepted unit PDFs), D26 (render/inventory/
  inspect, mirroring D13/D14 for the workbook), D27 (review-packet freeze,
  stages the real M07 packet shape), D28 (evidence reduction), D29 (findings
  classification + one planned repair + deterministic-vs-M08 routing, merging
  spec 6.2's D17/D18/D19 roles into the workbook's simpler single-owner-table
  row), D31 (boundary-checked admission + retest re-entry, merging D20/D21),
  D32 (final release recomputation; `COMPLETE` candidate) — plus
  `register_workbook_path()`, the additive topology registration N30's
  `unit_graph.register_unit_path()` already established the pattern for.
- `runtime/langgraph_factory/graph.py` — `PRODUCTION_BINDING_MODULES` gained
  `runtime.langgraph_factory.workbook`; `binding_inventory()` gained a sibling
  `full_binding_inventory()`; `build_curriculum_factory_graph()` gained a
  `register_workbook_topology()` step; `validate_bindings()`'s placeholder-name
  heuristic was fixed from a substring match to a whole-word match (see "A
  real defect this node fixed" below).

Every D24-D32 function is a plain, narrowly-scoped `(state, runtime_context)
-> update` callable in the same shape N31's `repair.py`/`acceptance.py`
already use — not wrapped in `nodes.deterministic_node()`, since that
decorator requires a `NODE_CATALOGUE` row and `nodes/__init__.py` is not in
this node's write set. D29/D31 explicitly reuse N31's repair engine
primitives (`repair.finding_fingerprint`, `repair.json_pointer_diff`,
`repair.within_boundary`, `repair.MAX_REPAIR_CHILDREN_PER_CHAIN`,
`repair.MAX_FINGERPRINT_REPEATS`) rather than re-implementing them, per spec
section 12 ("shared boundary/diff/invalidation-DAG machinery reused by
workbook repair"). D24 reuses N31's `acceptance.prove_exact_manifest_coverage`
predicate directly. `D30_CLASSIFY_PREREQUISITE` (N22, `nodes/sources.py`) was
not touched — it already existed and needed no change.

`tests/runtime/test_plan26_workbook.py` calls every D24-D32 function directly
against hand-built `FactoryState` fixtures with real files on disk (real PDF
bytes, real sha256 checks), merged step-to-step through the real field
reducers, exactly N31's testing convention. Two tests additionally build the
real, unmodified `runtime.langgraph_factory.nodes.terminal.write_terminal`
projection and call it directly (TEST 7/8/9).

## Workbook body shape (D25's `workbook_versions` record)

```
{
  "front_matter": {...},                      -- M08-repairable
  "navigation": {...},                          -- M08-repairable
  "coverage": {"ordered_unit_ids": [...], "unit_pdf_hashes": {unit_id: sha256}},
  "assembly": {"assembly_map": [...], "workbook_pdf_path": ..., "workbook_pdf_sha256": ...},
                                                  -- layout/assembly-repairable
}
```

`coverage` is named by no `WORKBOOK_OWNED_COMPONENTS` member and is the one
section D29/D31 can never grant a repair boundary over — this is the concrete
mechanism behind "workbook repair cannot stage a writable unit source or PDF"
(spec section 12) and TEST 4. `layout` and `assembly` share one boundary
(`/assembly`, deterministic re-render) because fixing a page defect
legitimately changes the whole rendered PDF, `workbook_pdf_sha256` included —
an earlier draft scoped `layout`'s boundary to `/assembly/pages` only, which
made `D31`'s own diff/boundary check reject the very repair `D29` had just
authorized (caught by `test_a_deterministic_layout_repair_never_touches_accepted_unit_hashes`
and the two crash-idempotency tests during development, fixed by widening
the granted boundary to the component's whole body section rather than the
literal, page-level finding pointer).

## D24 → D98 routing (the two product-terminal call sites)

Neither D24 nor D32 writes a terminal. Both build a `terminal_candidate` and
a `pending_guard` whose value routes to `D98_WRITE_TERMINAL` — the identical
node body N22 wrote (`nodes/terminal.py`), already registered, already
compiled into the graph before N32 ran. `D24`'s one-mode branch
(`unit_target_accepted`) and `D32`'s pass branch (`release_proven`) both
resolve to `routing.TERMINAL` in `routing.py`'s pre-existing (N20-authored)
`GUARD_DESTINATIONS` table — this node did not add a row there, it only had
to emit the guard values that table already declared.
`test_workbook_module_contains_no_terminal_writer_and_no_end_edge` parses
`workbook.py`'s AST and asserts no function named `write_terminal` and no
bare `Name` reference to `END`/`StateGraph` exists anywhere in the module.

## Coverage / release denominators

**D24 all-mode coverage** (`workbook_coverage`, spec 13.2 item 1): exact
`ordered_unit_ids == target_closure` (order and membership), every member has
a current accepted receipt, `acceptance.prove_exact_manifest_coverage` proves
the declared coverage names exactly those receipt hashes. Missing, extra
(outside the closure), or wrong-hash members are `SystemFailure`, not a
repairable finding (spec: "full mismatch = system").

**D28 / D32 workbook denominator** (`compute_workbook_denominator`, spec 13.2
items 1-8), five categories, every one recomputed fresh on every call (no
cached label trusted):

| Category | What is re-checked |
|---|---|
| `coverage` | current `workbook_coverage` still matches current `accepted_unit_receipts` byte-for-byte, exact order |
| `unit_bytes` | every accepted unit's frozen `denominator.pages.pdf_sha256` still matches the assembled workbook's own `coverage.unit_pdf_hashes` |
| `pages` | current workbook page inventory positive/contiguous, every page inspected and PASS |
| `review` | one current M07 candidate for the current `workbook_pdf_sha256`, zero blocking findings |
| `repair` | no open `workbook_repair_requests` (unresolved by a matching `workbook_retests` entry) |

All five must be `PASS`; `D28`/`D32` route to `D29` on any `FAIL` and to
`D32`/`D98` on all-`PASS`. `test_removing_or_failing_any_evidence_member_blocks_the_denominator`
independently clears/fails each category (coverage missing, pages missing,
inventory `FAIL`, review not-run) and confirms `compute_workbook_denominator`
rejects every time.

## A real defect this node fixed (`graph.py`, `validate_bindings`)

`D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR`'s stable ID could not bind: the
existing placeholder-name heuristic in `validate_bindings` rejected any
binding whose lowercased `module.qualname` contained the substring `"test"`
anywhere — which flags every legitimate `retest`/`RETEST` name, not just an
actual test double. (This latent bug was invisible before N32 because no
prior generation registered a binding containing `"test"` as a
`NODE_CATALOGUE`-independent module-level callable; `D21_RETEST_...` in
`repair.py` never went through `validate_bindings` because N31 never
registered it.) Fixed to a whole-word match
(`(?<![a-z])test(?![a-z])`, so `_test_`/`test_x`/`x_test` still trip it,
`retest`/`latest`/`contest` do not) — in scope because `graph.py` is a
declared writable path and the fix is required for D31 to bind at all, not
optional cleanup.

## A structural conflict this node found, and the resolution

N31's own result doc states "Registration of D16-D23 into the compiled
`StateGraph` ... is N32's write." This node attempted exactly that first,
and it compiles — but `tests/runtime/test_plan26_unit_graph.py` (N30's test
file, not in this node's write set, and one of the two files the controller's
own verification command names) contains tests that assert, byte-for-byte,
that specific `unit_graph.DEFERRED_EDGES` rows — including
`(D05_SELECT_NEXT_UNIT, manifest_exhausted, D24_PROVE_EXACT_MANIFEST_COVERAGE,
N32_WORKBOOK_TERMINALS)` — stay *declared and unresolved* as long as
`G.binding_inventory()` does not name the destination. The instant D24 (or
any of D16-D23) entered `binding_inventory()`, `unit_graph.py`'s own
`D05_SELECT_NEXT_UNIT` branch (registered once, by N30, with a destination
set derived dynamically from `binding_inventory()`) would silently widen to
route to it — correct for production, but it falsifies
`test_deferred_edges_are_exactly_the_destinations_with_no_node_body` and
`test_registering_an_undeclared_deferred_destination_fails`, which recompute
their own expectation directly from `binding_inventory()`'s return value,
independent of anything this node's registration code does.

There is no way to make D24 both real (`add_node`-registered, with real
outgoing edges) and absent from `binding_inventory()`'s *effect on
`unit_graph.register_unit_path`* without literally two different node sets
reaching that one function — which is exactly what this node built:

- `binding_inventory()` is **unchanged** — byte-identical to what N31 left it
  (D16-D23 still absent; now D24-D32 deliberately absent too), so N30's own
  already-passing topology tests keep passing exactly as they did before N32
  ran, verified: 127/127 on the controller's own two-file verification
  command, and 1123 passed / 6 failed (all 6 pre-existing/documented, see
  below) on the full `tests/runtime` suite.
- `full_binding_inventory()` (new) is `binding_inventory()` plus
  `workbook.WORKBOOK_NODE_BODIES` — the set this node actually uses to
  register D24-D32.
- `register_workbook_topology()` (new, called by
  `build_curriculum_factory_graph()` right after `register_skeleton()`)
  `add_node`s D24-D32 and calls `workbook.register_workbook_path(builder,
  sorted(full_binding_inventory()))`, wiring every edge *among* D24-D32 and
  outward to the real, already-registered `D90`/`D91`/`D98`/M07/M08 for real
  (`test_the_compiled_graph_really_registers_the_workbook_engine` asserts
  this against the builder's actual `branches` table, not the pruned
  `compiled.get_graph()` visualization, which drops edges unreachable from
  `START`).
- `D16-D23` are left exactly as N31 delivered them: fully implemented,
  fully tested at the function level, not registered into the graph. This
  node did not need to touch them — `D24-D32` (this node's actual GOAL text:
  "Integrate D25–D32 ... routing through the pre-existing N22-owned D98") is
  self-contained and does not require D16-D23 to be graph nodes.

Net effect: **D24-D32 are real, `add_node`-registered nodes with real,
asserted conditional edges among themselves and to `D90`/`D91`/`D98`/M07/M08
— but D24 is not yet reachable from `D05_SELECT_NEXT_UNIT`** in the compiled
production graph, because the one edge that would make it reachable is
registered by `unit_graph.py` (N30, frozen, not in this node's write set)
with a destination set that predates D24's existence. This is declared, not
silent: `unit_graph.DEFERRED_EDGES` already named this exact row before N32
ran, and two `test_blocked_*` tests in `test_plan26_workbook.py`
(`test_blocked_d05_cannot_reach_d24_yet`,
`test_blocked_d91_cannot_reach_d29_yet` — the second names the analogous gap
for a workbook-owned M07/M08 transport failure trying to reach D29 through
the shared `D91_CLASSIFY_MODEL_FAILURE` node) assert the current, structural
fact and name the owner and rework edge that closes it
(`N30_UNIT_GRAPH`, `unit_flow_or_denominator`), matching the
`test_blocked_*` convention `test_plan26_unit_graph.py` already established
for exactly this situation (its own docstring: "guards that closed B-1, B-2
and B-3 were inverted this way").

**One known, accepted regression, out of this node's required verification
scope but disclosed:** `tests/runtime/test_plan26_topology.py` (not named in
`implementation.graph.v3.yaml`'s N32 `verification` list, not writable by
this node) contains two tests asserting `set(compiled.get_graph().nodes) -
{START, END} == set(G.binding_inventory())`. Since D24-D32 are real compiled
nodes and `binding_inventory()` deliberately excludes them (see above), that
equality no longer holds. This is the direct, unavoidable consequence of the
same constraint that keeps `test_plan26_unit_graph.py` green; closing it
requires the same `N20_GRAPH_COMPILER`/`N30_UNIT_GRAPH` rework
(`topology_or_guard` / `unit_flow_or_denominator`) as the two `test_blocked_*`
rows above — likely by widening `binding_inventory()` and
`unit_graph.MODEL_BRANCH_DESTINATIONS` together in one coordinated change,
which is exactly the kind of cross-node edit this node's write set forbids.

## Real-D98 traces (TEST 7/8/9)

- `test_a_complete_candidate_from_d32_traverses_the_real_d98`: a `COMPLETE`
  candidate built from this generation's real D24→D32 chain is independently
  re-derived and accepted by D98's own `_validate_complete`.
- `test_a_unit_accepted_candidate_from_d24_traverses_the_real_d98`: D24's
  one-mode candidate, same treatment via `_validate_unit_accepted`.
- `test_a_tampered_complete_candidate_is_rejected_by_the_real_d98`: the same
  `COMPLETE` candidate with a forged `workbook_hash` is rejected and D98
  writes `SYSTEM_FAILURE` in its place — no N32 code decided that.
- `test_d98_rejects_a_false_pause_candidate_regardless_of_its_source`: a
  `PAUSED_PREREQUISITE` candidate carried alongside a `system`-classified
  (not `pause`-classified) `pending_failure` is rejected by D98's own
  `_validate_paused`, independent of who proposed it.
- `test_repeating_the_terminal_write_after_a_crash_replays_idempotently`: two
  calls against the identical projection produce a byte-identical record.

No test in this file, and no code in `workbook.py`, writes to
`nodes/terminal.py`; `terminal.write_terminal.__module__` is asserted to
still be `runtime.langgraph_factory.nodes.terminal`.

## Commands and results

```
/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_workbook.py tests/runtime/test_plan26_unit_graph.py -v
=> 127 passed in 7.25s
(results/evidence/N32_WORKBOOK_TERMINALS/focused_test_run.txt)

/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime -q
=> 1123 passed, 1 skipped, 399 subtests passed, 6 failed
(results/evidence/N32_WORKBOOK_TERMINALS/full_plan26_suite.txt)
```

The 6 failures split into two groups, neither caused by this node's writable
files:

- 4 in `test_plan26_prompt_graph_controller.py` — pre-existing environment
  state (deleted `results/v3/*.receipt.v1.json` files already absent at
  session start, per `git status`; N31's result doc records the identical
  finding for the identical 4 tests).
- 2 in `test_plan26_topology.py` — the documented, disclosed consequence of
  D24-D32 being real compiled nodes outside `binding_inventory()`, above.

`register_workbook_topology` and its resolved per-source destination map are
captured in `results/evidence/N32_WORKBOOK_TERMINALS/workbook_branch_topology.txt`.

## Hashes

| File | SHA-256 (shasum -a 256) |
|---|---|
| `runtime/langgraph_factory/workbook.py` | `903abda0f4df3b01dd91d1c8d515721c91db4df78da36a55b803a4e14b422439` |
| `runtime/langgraph_factory/graph.py` | `1ec14f1974c97110817d6d39409dbab5898c15a4b433fd01254c108660cd6b5a` |
| `tests/runtime/test_plan26_workbook.py` | `fe32a59154450a76cc03765df7fc009af454ec071609a3b572c88e6477494c72` |

## TEST item verdicts

1. **PASSED** — `test_d24_all_mode_rejects_a_manifest_that_is_missing_a_receipt`,
   `test_d24_all_mode_rejects_an_extra_receipt_outside_the_manifest`,
   `test_d25_rejects_an_assembly_map_the_assembler_reordered`,
   `test_d25_refuses_a_unit_pdf_that_changed_after_acceptance`,
   `test_d25_refuses_a_wrong_hash_layout_version`.
2. **PASSED** — `test_workbook_assembly_through_review_freezes_every_page_once`,
   `test_workbook_inventory_that_cannot_be_proven_is_repairable_not_shipped`
   (×2: empty, non-contiguous).
3. **PASSED** — `test_removing_or_failing_any_evidence_member_blocks_the_denominator`
   (×4: coverage/pages/inventory/review), `test_the_full_denominator_passes_once_every_member_is_current`.
4. **PASSED** — `test_a_deterministic_layout_repair_never_touches_accepted_unit_hashes`,
   `test_d31_refuses_a_model_candidate_that_changes_an_accepted_unit_hash`.
5. **PASSED** — `test_fingerprint_repeat_bound_exhausts_workbook_repair`,
   `test_attempt_bound_exhausts_before_a_fourth_repair_child`.
6. **PASSED** — `test_d32_fails_even_though_d28_passed_earlier_once_evidence_goes_stale`,
   `test_d32_releases_when_the_denominator_currently_passes`.
7. **PASSED** — `test_a_complete_candidate_from_d32_traverses_the_real_d98`,
   `test_a_unit_accepted_candidate_from_d24_traverses_the_real_d98`,
   `test_workbook_module_contains_no_terminal_writer_and_no_end_edge`,
   `test_register_workbook_path_adds_no_node_and_creates_no_graph`,
   `test_the_compiled_graph_really_registers_the_workbook_engine`.
8. **PASSED** — `test_workbook_never_proposes_paused_prerequisite`,
   `test_d98_rejects_a_false_pause_candidate_regardless_of_its_source`.
9. **PASSED** — `test_a_tampered_complete_candidate_is_rejected_by_the_real_d98`,
   `test_d32_refuses_release_while_a_manifest_member_is_unaccepted`.
10. **PASSED** — `test_repeating_d25_after_a_crash_replays_idempotently`,
    `test_repeating_d31_after_a_crash_replays_idempotently`,
    `test_re_admitting_a_workbook_repair_after_the_head_already_advanced_fails_closed`,
    `test_repeating_the_terminal_write_after_a_crash_replays_idempotently`.

Plus two declared structural gaps (`test_blocked_d05_cannot_reach_d24_yet`,
`test_blocked_d91_cannot_reach_d29_yet`), owned by `N30_UNIT_GRAPH`.

## Known scope limitations (for N40 and future generations)

- **D24 is unreachable from `D05_SELECT_NEXT_UNIT`**, and **`D91`'s
  `M07`/`M08`-repairable-failure branch is unreachable to `D29`**, in the
  compiled production graph — both because `unit_graph.py`'s frozen
  destination tables predate D24/D29's existence. Closing this is
  `N30_UNIT_GRAPH`'s `unit_flow_or_denominator` rework edge: add
  `"D24_PROVE_EXACT_MANIFEST_COVERAGE"` to `D05_SELECT_NEXT_UNIT`'s reachable
  set (it already falls out of `routing.guard_destinations` once
  `binding_inventory()` names D24 — the fix is in `unit_graph.py`/
  `binding_inventory()` together, not in `routing.py`, which already has the
  correct `GUARD_DESTINATIONS` row) and add
  `"D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"` to
  `unit_graph.MODEL_BRANCH_DESTINATIONS["D91_CLASSIFY_MODEL_FAILURE"]`.
  N40_CLI_CUTOVER cannot ship a real `mode=all` run until this closes.
- **D16-D23 remain ungraphed**, exactly as N31 left them; this generation did
  not need them for D24-D32's own correctness and did not touch them.
- The workbook assembler/inspector surface (`transport_registry
  .assemble_workbook` / `.inspect_workbook_pages`) has no production
  implementation yet, mirroring N30's own documented gap for
  `render_unit`/`inspect_pages` (`_StubRegistry`, finding B-8): this
  generation's tests supply a real, file-backed test double; N13's transport
  registry does not yet expose either method.
- `test_plan26_topology.py`'s `drawn == binding_inventory()` assumption is
  now stale for the reason documented above; two tests there fail until the
  same `N20_GRAPH_COMPILER`/`N30_UNIT_GRAPH` coordinated widening lands.
