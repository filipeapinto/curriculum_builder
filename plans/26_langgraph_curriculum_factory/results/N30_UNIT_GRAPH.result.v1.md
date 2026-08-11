# N30_UNIT_GRAPH result

status: BLOCKED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N30_unit_graph.prompt.v1.md (f78e98cb44f95a2aa108e87301d3e5fcddd0924e68a47333181bf5ebcd7f5e3e)
generation: 8

**B-6, B-7 and B-9 are RESOLVED and re-verified here by real execution.** The
committed path now runs, on one real `.stream()` of the one real compiled graph:
D00 through D05, then D06 -> D90 -> `Send(M01)` x2 -> D06B -> D90 -> `Send(M01)`
x2 -> D07 (exact join, both sources admitted) -> D90 -> M02 -> **D08, which
admitted a real domain head** -> D90 -> M03 -> D09. Six real model activations,
four attempt counters committed before their dispatches, and **the first artifact
head this plan has ever advanced** (`units/U001/domain`, version 1, parent
`null`, hash `b657f541…`), minted by D08 from M02's `payload` — not by the model.
The episode ends on a *declared* deferred edge (D09 `content_repairable` -> D17,
owner N31), not on a failure and not on a fabricated destination.

**74 of this node's tests pass** in the hash-locked environment, the full
`-k plan26` selection is **823 passed / 0 failed** (B-9 is gone: N20's two rows
are green), and the ambient suite is **806 passed / 0 failed**.

The node is nevertheless still **BLOCKED**, on gaps that were invisible until
D08 through D16 could be *reached* for the first time. Three of them are
decisive, and all three are outside this node's write set:

- **B-10** — no unit content document can satisfy both of its contracts. M03's
  output schema and D09's validation schema are each `additionalProperties:
  false` with **disjoint** property sets, so `content_schema_valid` can never
  pass whatever the model writes. This is proven as schema algebra, not from one
  failing sample. No content head can be admitted, so D10-D16 are unreachable.
- **B-11** — D15 requires an admitted `layout` head that no node in the spec's
  own authority table ever admits.
- **B-12** — D11, the only deterministic `Send` target, cannot read the member
  the fan-out delivers to it.

All three recipes were **verified before being reported**, stacked, in memory
only: with them applied the same episode runs the *entire* unit path — D09
admits, D10 fans out, D11 renders a real deterministic visual, D12 dispatches
M04 through D90 and joins both subsets, D13 renders a real PDF, D14 inventories
and inspects two real pages, D15 freezes a review packet with denominator
`{pages: 2, artifacts: 3, checks: 11, sources: 2}`, and **M05 returns a real
independent review answering both pages by hash** — stopping exactly at
`D16_REDUCE_UNIT_EVIDENCE`, which is this node's declared handoff to N31. Eight
model activations, three admitted heads. Nothing from that probe is committed;
`routing.py`, `nodes/content.py`, `nodes/domain.py`, `nodes/review.py`,
`nodes/visuals.py` and N23's M03 schema are all byte-identical to their owners'.

Prompt TEST items 5, 6, 7 remain unprovable from committed code, and this record
says so rather than substituting a stand-in.

## Inputs

Predecessor result records consumed (all re-read at their current hashes, since
three of them reworked since generation 7):

- `N00_BASELINE_FREEZE`: c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5
- `N10_DEPENDENCY_API`: 1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658
- `N11_STATE_REDUCERS` (generation 5): 9633ac27f94f1fa97ebf50c0119eb76124f233c3f75311b07697b3281818a0e9
- `N12_EVIDENCE_ARTIFACTS`: 6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f
- `N13_TRANSPORT_AUTH`: aacb3187bfe11f1e16b4eafebab6fba5a8ae7ba0136148b26fafac7f3adb2a71
- `N20_GRAPH_COMPILER` (generation 7): c44d8d4caaebdf540fd80b3b875af062f7ba3d49979b6a310e9e874b4bbbdd7c
- `N21_PERSISTENCE_RESUME` (generation 7): cd8f08eac498c14370d31578b056d8e12477293dfad03378cb9680e106fd9841
- `N22_DETERMINISTIC_NODES` (generation 6): c0352f7b8b1d3c02a12a13326dda8a8da0d290e8235dca33d6246381b9181db6
- `N23_MODEL_NODES` (generation 4): d4a273e80302f47e12ad8ac11a0589399a691b3bd4ecc774c06e7acaf452c73d

The generation-7/6/4 rework Findings of N20, N22 and N23 were read in full and
each claim independently re-verified here by execution rather than taken on
report; see the RESOLVED findings below for what was checked and how.

Other frozen inputs read:

| Path | SHA-256 |
|---|---|
| `spec/langgraph_curriculum_factory.spec.v1.md` (sections 5, 6.1-6.3, 8.1, 8.2, 9, 10, 12, 14, 11.3, 11.4) | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| `implementation.graph.v2.yaml` | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| `contracts/baseline.v1.md` | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| `contracts/digest_algorithm.v1.md` | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| `contracts/erratum_checkpoint_ns_rename.v1.md` | 10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1 |
| `contracts/node_ownership.v1.md` | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| `contracts/result_record_schema.v1.md` | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| `contracts/shared_names_and_paths.v1.md` | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| `contracts/traceability_matrix.v1.md` | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| `runtime/langgraph_factory/routing.py` (N20 gen 7, unmodified) | 6be93bf8bd951ae9984f74dc9dbe91c709a41edca0a1a6ff6d72be52cd998079 |
| `runtime/langgraph_factory/state.py` (N11, unmodified) | 428c78edd53b73fd3458d469b36e1bb528dea37d4565f3b37995d63e4a075167 |
| `runtime/langgraph_factory/reducers.py` (N11, unmodified) | 05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf |
| `runtime/langgraph_factory/nodes/__init__.py` (N22 gen 6, unmodified) | c591775a214e0e7b51c051f2e297a8af8e9dc2dba844ed8b5b4944015a02ca02 |
| `runtime/langgraph_factory/nodes/domain.py` (N22, unmodified) | 88b30263219fa98ba19dc12110a9c1754c7c8e494eb3c0c8eb78f68b4a1c6487 |
| `runtime/langgraph_factory/nodes/content.py` (N22, unmodified) | e103557cb83a7850cabe1ca4ed94cdbfc76755e0840f7ef7b5055859e3aa4ef0 |
| `runtime/langgraph_factory/nodes/visuals.py` (N22, unmodified) | e1bd9ea786c29ada3484f7bd64097eefb725849a99cbcace7e8a8b69b054800d |
| `runtime/langgraph_factory/nodes/render.py` (N22, unmodified) | 76fa183ad8fc26c054a33901d42c3635e3cb5c0094bca70b9f797517e19152b4 |
| `runtime/langgraph_factory/nodes/review.py` (N22, unmodified) | fd1b61f25cdf96a82b5f9307b1dd3dbeae9cd8b8eb4605ce182f7980e641cb5e |
| `runtime/langgraph_factory/model_nodes.py` (N23 gen 4, unmodified) | ff471867ef2c6aa4fa78f6aac9942c85416d1e6305f3c49d9b8f1fb5861718e1 |
| `runtime/langgraph_factory/persistence.py` (N21, unmodified) | c2b3eb236d2ea7bb6ca7f0ff5d6258c8bd1fdec8cf36d9520c2b2ddb9298b289 |
| `runtime/langgraph_factory/transport.py` (N13, unmodified) | 111474fc70ae5cb8a3e95ea8e53f035141eca795138956a1c9879159958d87af |

## Outputs

| Path | SHA-256 |
|---|---|
| `runtime/langgraph_factory/unit_graph.py` | b5067d25fce248bba1cb699124e7696cd10a6495c08ab4abb2a9a365a982c28d |
| `tests/runtime/test_plan26_unit_graph.py` | e3b022d1ee46050c043cf3004b33296a050167af090e157a55f2807046f1f85a |
| `plans/26_langgraph_curriculum_factory/results/N30_UNIT_GRAPH.result.v1.md` | this file |

`runtime/langgraph_factory/graph.py` is **unchanged at generation 8**
(`6361e12c…`, the same hash it carried at generation 7). Its generation-6/7 edits
— importing `unit_graph`, calling `register_unit_path`, extending
`_validate_topology`, shrinking `DEFERRED_TOPOLOGY`, and folding
`model_nodes.MODEL_BOOKKEEPING_NODES` into `binding_inventory()` — are the
registration `contracts/node_ownership.v1.md` explicitly assigns to this node,
and none of them was revisited this generation.

The only change to `unit_graph.py` this generation is `BLOCKING_GAPS`: the two
rows for B-6 and B-7 were removed because they are fixed, and four rows were
added for B-10 through B-13. **No edge, guard, branch or registration changed in
this node's write set.** The compiled graph is still **34 nodes, 100 edges**, but
its digest moved from generation 7's
`5cdd450b52625b16479f0b3008e9b5d9816a283fa088c7437d8ddbac17413577` to
`10a65426089adc6dcaa6a54339fca33065af48f78c5212224c8e5aafee63cab1` — the same
count over rewired edges, because N20's B-6 fix redirected six dispatch edges
through D90. That delta is N20's, not this node's, and it is exactly the property
N20's digest tests exist to hold.

## Commands

| Command | Exit | Evidence |
|---|---:|---|
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/test_plan26_unit_graph.py -q` | 0 | `results/evidence/N30_UNIT_GRAPH/venv_unit_graph.txt` (**74 passed**) |
| `/tmp/plan26_n30_verify/bin/python -m pytest tests/runtime/ -q -k plan26` | 0 | `results/evidence/N30_UNIT_GRAPH/venv_plan26_all.txt` (**823 passed, 1 skipped, 345 subtests passed, 0 failed**) |
| `python3 -m pytest -q -rs` (ambient) | 0 | `results/evidence/N30_UNIT_GRAPH/ambient_pytest.txt` (**806 passed, 12 skipped, 282 subtests passed, 0 failed**) |
| real episode of the real compiled graph, committed code, no pytest in the path | 0 | `results/evidence/N30_UNIT_GRAPH/e2e_trace.txt` |
| B-10/B-11/B-12 recipe: the same episode with the three recipes patched in memory only | 0 | `results/evidence/N30_UNIT_GRAPH/blocker_probe_b10_b11_b12_recipe.txt` |
| B-10 schema algebra: the two content contracts have an empty intersection | 0 | `results/evidence/N30_UNIT_GRAPH/blocker_probe_unit_content_contract.txt` |
| B-13 probe: M01's attempt budget across its two phases | 0 | `results/evidence/N30_UNIT_GRAPH/blocker_probe_m01_attempt_budget.txt` |
| B-8 probe: `CliTransport`'s capability/renderer surface | 0 | `results/evidence/N30_UNIT_GRAPH/blocker_probe_capability_surface.txt` |
| interrupt matrix: 14 real episodes, one per reachable boundary | 0 | `results/evidence/N30_UNIT_GRAPH/interrupt_matrix.txt` |
| compile + topology dump | 0 | `results/evidence/N30_UNIT_GRAPH/compiled_topology.txt` |

The generation-7 evidence files `blocker_probe_d90_recipe.txt` and
`blocker_probe_candidate_record.txt` were deleted: they sized B-6 and B-7, both
of which are now fixed and re-verified by the primary evidence above, and no
claim in this record rests on them.

Ambient is green and not regressed; all 12 ambient skips are the pre-existing
"langgraph absent from the ambient interpreter" module skips plus N10's
`pip-tools` skip, each reported by `-rs`.

## Tests

### LangGraph trace — one real episode of the committed graph

Reproduced verbatim in `evidence/N30_UNIT_GRAPH/e2e_trace.txt`:

```text
D00_BOOTSTRAP_EPISODE            guard=fresh
D01_VALIDATE_AND_FREEZE_INPUTS   guard=inputs_frozen
D02_COMPILE_EFFECTIVE_RUN        guard=effective_run_compiled
D03_PROVE_CAPABILITIES           guard=capabilities_proven
D04_INITIALIZE_OR_RESUME         guard=fresh_initialized
D05_SELECT_NEXT_UNIT             guard=unit_selected
D06_COMPILE_SOURCE_REQUESTS      guard=discovery_fanout
D90_RESERVE_MODEL_ATTEMPT        guard=authorized       <- 2 counters committed (B-6 closed)
M01_RESEARCH_UNIT_SOURCES        (Send worker 1 of 2)
M01_RESEARCH_UNIT_SOURCES        (Send worker 2 of 2)
D06B_RETRIEVE_SOURCE_CANDIDATES  guard=interpretation_fanout
D90_RESERVE_MODEL_ATTEMPT        guard=authorized       <- 2 more
M01_RESEARCH_UNIT_SOURCES        (Send worker 1 of 2)
M01_RESEARCH_UNIT_SOURCES        (Send worker 2 of 2)
D07_CORRELATE_AND_ADMIT_SOURCES  guard=sources_admitted <- exact join, 2 admissions
D90_RESERVE_MODEL_ATTEMPT        guard=authorized
M02_CREATE_UNIT_DOMAIN_DATA
D08_VALIDATE_DOMAIN              guard=domain_admitted  <- B-7 closed: a head advances
D90_RESERVE_MODEL_ATTEMPT        guard=authorized
M03_WRITE_UNIT_CONTENT
(D09_VALIDATE_CONTENT executes; guard=content_repairable -> D17, a declared
 deferred edge owned by N31 — see B-10 for why it can never be anything else)
```

Committed heads at the end of that episode:

```json
{"units/U001/domain": {"version": 1, "parent_hash": null,
                       "hash": "b657f5410bbf9587644246d388fcab257c3c8af5d27a3bafa11da5c65f48cb01"}}
```

With the B-10/B-11/B-12 recipes patched in memory only
(`evidence/N30_UNIT_GRAPH/blocker_probe_b10_b11_b12_recipe.txt`), the same
episode runs the whole path:

```text
... D09_VALIDATE_CONTENT              guard=content_admitted
    D10_COMPILE_VISUAL_BRIEFS         guard=deterministic_visual_fanout
    D11_CREATE_DETERMINISTIC_VISUALS  guard=visual_produced      (real SVG written)
    D12_VISUAL_BARRIER_AND_JOIN       guard=model_visual_fanout
    D90_RESERVE_MODEL_ATTEMPT         guard=authorized
    M04_CREATE_UNIT_VISUALS
    D12_VISUAL_BARRIER_AND_JOIN       guard=visuals_admitted     (both subsets joined)
    D13_RENDER_UNIT                   guard=unit_rendered        (real PDF)
    D14_INVENTORY_AND_INSPECT_UNIT_PAGES guard=pages_inspected   (2 pages, by hash)
    D15_FREEZE_UNIT_REVIEW_PACKET     guard=review_packet_frozen
    D90_RESERVE_MODEL_ATTEMPT         guard=authorized
    M05_REVIEW_ACTUAL_UNIT                                       (real review returned)
    -> D16_REDUCE_UNIT_EVIDENCE  (this node's declared handoff to N31)
```

with heads `units/U001/{domain,content,visuals}` all at version 1, eight model
execution receipts (M01 x4, M02, M03, M04, M05), and a frozen review packet whose
denominator is `{pages: 2, artifacts: 3, checks: 11, sources: 2}`.

### Registered topology (spec 8.1 / 8.2)

**34 nodes, 100 edges**, digest
`10a65426089adc6dcaa6a54339fca33065af48f78c5212224c8e5aafee63cab1`
(`evidence/N30_UNIT_GRAPH/compiled_topology.txt`). Unchanged from generation 7
except that every model dispatch is now mediated by D90:

```text
D06  -[discovery_fanout]->      D90 -> Send(M01) per request key
M01  -[discoveries present]->   D06B
D06B -[interpretation_fanout]-> D90 -> Send(M01) per retrieval group
M01  -[interpretations present]-> D07
D07  -[sources_admitted]->      D90 -> Send(M02) -> D08
D07  -[prerequisite_unresolved]-> D30 -> D98
D08  -[domain_admitted]->       D90 -> Send(M03) -> D09
D09  -[content_admitted]->      D10
D10  -[deterministic_visual_fanout]-> Send(D11) per deterministic brief
D10  -[no_deterministic_visuals]->    D12
D11  --normal edge-->           D12
D12  -[model_visual_fanout]->   D90 -> Send(M04) per model brief
M04  --normal edge-->           D12
D12  -[visuals_admitted]->      D13 -> D14 -> D15
D15  -[review_packet_frozen]->  D90 -> Send(M05)
M01/M02/M03/M05 -[model_failure]-> D91
D91  -[retry]->                 D90
D90/D91 -[exhausted|system]->   D98
every branch additionally -> D96 (graceful interrupt) and -> D98 (system failure)
```

`test_every_model_dispatch_is_routed_through_d90` asserts both halves against the
really-compiled edge set: every one of the six dispatchers has an edge to D90,
and **no model node has any predecessor other than D90**.

`DEFERRED_EDGES` is unchanged at 7 rows and is asserted exactly total by
`test_deferred_edges_are_exactly_the_destinations_with_no_node_body`:

| From | Guard value | To | Owner |
|---|---|---|---|
| D05 | `manifest_exhausted` | D24 | N32_WORKBOOK_TERMINALS |
| D08 | `domain_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D09 | `content_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D12 | `visuals_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D14 | `layout_repairable` | D17 | N31_REPAIR_ACCEPTANCE |
| D91 | `repair` | D17 | N31_REPAIR_ACCEPTANCE |
| M05 | `review_returned` | D16 | N31_REPAIR_ACCEPTANCE |

### Fan-out denominators (spec section 10)

| Join | Correlation key | Denominator source | Proven |
|---|---|---|---|
| source discovery | `(run_id, episode_id, request_key)` | D06 `source_denominators[unit/epoch].request_keys` | **executed on committed code**: D06 committed a 2-key denominator, D90 committed 2 counters, the guard dispatched exactly 2 `Send`s, 2 real M01 workers ran in one superstep |
| source retrieval | `(run_id, episode_id, request_key)` | D06B `retrievals` | **executed on committed code**: 2 retrievals, 2 interpretation packets, 2 `Send`s |
| source interpretation | same key both phases | D06B, joined by D07 | **executed on committed code**: D07's exact join admitted both, and the admitted keys equal the committed denominator (`test_the_source_map_reduce_supersteps_execute_as_real_send_fanouts`); 4 mutations rejected |
| deterministic visual | `(run_id, unit_id, content_hash, brief_id)` | D10 `visual_denominators` | body + guard proven; **executed only under the B-10/B-12 recipe**, where D11 produced a real visual and D12's deterministic subset equalled its denominator |
| model visual | `(run_id, unit_id, content_hash, brief_id)` | D12 | join proven exact (4 mutations); staging + D90 + dispatch proven one-for-one on committed code; **the full round trip executed only under the recipe** |
| unit page review | `(run_id, unit_id, pdf_sha256, page_number, page_sha256, …)` | D14/D15 | **executed only under the recipe**: D15 froze a 2-page packet and M05's review answered exactly those two pages by hash |

`test_a_visual_fanout_dispatches_one_send_per_staged_denominator_member` now
runs the whole dispatch hop on committed code: the real D12 body stages two M04
packets, the real `route_visual_barrier` returns `D90_RESERVE_MODEL_ATTEMPT`, the
real D90 restages them with one reservation each, and the real
`route_attempt_reservation` emits exactly two `Send`s whose correlation keys are
the committed denominator's and whose activation ids are distinct.
`test_a_fanout_with_no_staged_packet_refuses_to_improvise_one` asserts the
refusal in both places a guard now translates members — D10's deterministic map
at the dispatcher, and every model map at D90.

### Prompt TEST items

| # | TEST item | Verdict | Backing assertion |
|---:|---|---|---|
| 1 | Fresh bootstrap executes D01 once; resume uses D00R/D04 and validated state import | **PASS (fresh) / PARTIAL (resume)** | `test_a_fresh_episode_executes_the_bootstrap_spine_once_through_langgraph` streams a real episode: the trace opens with exactly D00-D06, D01 appears exactly once, D00R and D92 do not appear, and the committed state carries `bootstrap_kind=fresh`, a real `run_id` and the computed closure. The resume half is exercised structurally (D00R/D92 wired, D92's 12 destinations asserted); a full resume episode needs a legally-resumable terminal, which needs the path to reach one — blocked by B-10. |
| 2 | `one` mode computes complete prerequisite closure in manifest order | **PASS** | `test_one_mode_computes_the_complete_prerequisite_closure_in_manifest_order` over synthetic 1/7/41-unit chains (real D02 body, real manifest files), then the real D05 body and the real `route_unit_selection`; `test_a_diamond_closure_admits_each_ancestor_exactly_once`. Confirmed end to end: the real episode's committed `effective_run.target_closure` is the manifest closure. |
| 3 | Source join rejects missing/extra/duplicate/stale/cross-unit members | **PASS** | `test_the_source_join_refuses_a_denominator_that_is_not_exact` (4 mutations against the real D07 body); `test_a_duplicate_fanout_member_with_a_different_body_is_an_integrity_failure`. And the positive now runs for real: `test_the_source_map_reduce_supersteps_execute_as_real_send_fanouts` proves 4 M01 activations, no `D91` in the trace at all, and admitted keys equal to the committed denominator. |
| 4 | Domain/content heads advance only after code-owned admission | **PASS (domain) / BLOCKED (content, B-10)** | `test_the_domain_head_advances_only_after_code_owned_admission` runs a real episode: M02 ran before D08, its candidate carries no `version`/`hash`/`parent_hash`, D08 minted a head at version 1 with `parent_hash: null`, and no model node's update in the whole episode wrote `artifact_heads`. The content head cannot advance while B-10 is open. |
| 5 | Visual denominator permutations produce identical admitted heads; empty subsets work | **PARTIAL** | Empty subset proven on committed code (`test_an_empty_deterministic_visual_subset_routes_straight_to_the_barrier`, real D10 body and real guard). Permutation-invariance of an *admitted* head is unproven: admitting one needs B-10 and B-12. Under the recipe a visual head really is admitted, but a claim resting on an in-memory patch is not made here. |
| 6 | Actual PDF/assets and positive contiguous page inventory are required | **BLOCKED (B-10, B-12)** | D13/D14 are wired and, on committed code, unreachable. Under the recipe D13 rendered a real PDF and D14 inventoried two real pages by hash — recorded as recipe evidence, not claimed. |
| 7 | D15 packet contains exact PDF and every page once; M05 result matches it | **BLOCKED (B-10, B-11, B-12)** | `D15 -> D90 -> M05` is registered and D15 stages a real M05 packet. On committed code D15 cannot run at all (B-11). Under the recipe the packet froze a 2-page denominator and M05's review answered exactly those pages by hash. Not claimed. |
| 8 | D16 rejects any absent/failed/stale/`NOT_RUN` denominator member | **OUT OF SCOPE / BLOCKED** | D16's body is N31's per `contracts/node_ownership.v1.md`; this node's declared frontier is the handoff edge, asserted by `test_blocked_the_review_handoff_to_n31_is_declared_not_wired`. Under the recipe the real graph routed M05's accepted result to `D16_REDUCE_UNIT_EVIDENCE`, which is the furthest this node's ownership extends. |
| 9 | Interrupt/hard crash at every node/map/barrier boundary resumes without repeated valid calls | **PASS over every observable boundary** | `test_a_graceful_interrupt_at_every_reachable_boundary_writes_one_terminal` is parametrized over **14** boundaries — the 7 of generation 7 plus D90, the M01 `Send` map, D06B, the D07 join barrier, M02, D08 and M03 — and runs a real episode for each. See the crash matrix below. `test_a_hard_crash_is_recovered_as_an_orphan_without_continuing_its_thread` abandons a real episode mid-stream and proves the lease open with no terminal, a non-empty incomplete frontier, and no model node in it. |
| 10 | No capability, intermediate artifact, review, or D16 pass emits success | **PASS** | `test_no_node_in_this_path_can_emit_a_product_success_terminal`: no node module reachable from this path names `UNIT_ACCEPTED` or `COMPLETE` (word-bounded, so the join verdict `INCOMPLETE` is not a false hit), and neither `D22_ACCEPT_UNIT` nor `D24_PROVE_EXACT_MANIFEST_COVERAGE` is in the wired path or any deferred destination. Confirmed at runtime: no episode in this record, including the recipe run that reached M05, ends on a success terminal. `test_the_model_path_uses_only_a_test_transport_and_no_product_output_root` confirms the fake transport is reachable only through `build_test_model_node_context`. |

Totals in the hash-locked environment: **74 passed, 0 failed, 0 skipped** for this
node's file. Of the ten prompt TEST items: **4 unqualified PASS** (2, 3, 9, 10),
**3 PARTIAL** (1, fresh proven and resume structural; 4, domain proven and
content blocked; 5, empty subset proven and permutation-invariance not),
**2 BLOCKED** (6, 7), and 1 out of scope by ownership (8). Counted the same way,
generation 7 was 3 PASS (2, 3, 10) / 3 PARTIAL (1, 5, 9) / 3 BLOCKED (4, 6, 7) /
1 out of scope — its own summary line read "4 PASS, 3 PARTIAL, 2 BLOCKED", which
counted TEST 1's mixed verdict as a pass and is corrected here. The movement this
generation is TEST 9 PARTIAL -> PASS (the crash matrix now covers every
observable boundary, including a map and a join barrier) and TEST 4 BLOCKED ->
PARTIAL (the domain half is proven on a real episode).

### Crash matrix

Every row is one real `.stream()` of the real compiled graph
(`evidence/N30_UNIT_GRAPH/interrupt_matrix.txt`):

| Boundary the signal is raised after | Gate | Terminal | Exit | Resumable | Terminals written | D98 entries |
|---|---|---|---:|---|---:|---:|
| `D00_BOOTSTRAP_EPISODE` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D01_VALIDATE_AND_FREEZE_INPUTS` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D02_COMPILE_EFFECTIVE_RUN` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D03_PROVE_CAPABILITIES` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D04_INITIALIZE_OR_RESUME` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D05_SELECT_NEXT_UNIT` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D06_COMPILE_SOURCE_REQUESTS` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D90_RESERVE_MODEL_ATTEMPT` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `M01_RESEARCH_UNIT_SOURCES` (inside the `Send` map) | D96 | `INTERRUPTED` | 10 | yes | **1** | **2** |
| `D06B_RETRIEVE_SOURCE_CANDIDATES` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D07_CORRELATE_AND_ADMIT_SOURCES` (join barrier) | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `M02_CREATE_UNIT_DOMAIN_DATA` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `D08_VALIDATE_DOMAIN` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| `M03_WRITE_UNIT_CONTENT` | D96 | `INTERRUPTED` | 10 | yes | 1 | 1 |
| hard crash (stream abandoned before D98) | — | none committed; lease left open | — | — | 0 | 0 |

The M01 row is the interesting one and is asserted rather than smoothed over: an
interrupt raised *inside* a `Send` map sends every in-flight branch to the gate,
so D96 and D98 each run twice. Exactly **one** terminal is written; the second
D98 entry refuses with `class=system, cause=persistence, "this episode already
holds a terminal record"`. The test asserts the terminal count, requires the
extra entry to carry exactly that refusal, and additionally asserts that no model
node runs after the gate — which is prompt TEST 9's "without repeated valid
calls".

`D09_VALIDATE_CONTENT` is deliberately **excluded** from the matrix and the
exclusion is itself asserted by `test_the_unobservable_boundary_is_excluded_for_a_stated_reason`:
D09 really executes (the committed episode's final `pending_guard` is D09's own),
but the branch that would emit its update resolves to the deferred D17 and aborts
the superstep, so no stream consumer can observe it and no signal can be raised
after it. That test fails the moment the path extends past D09, which forces the
row back into the matrix.

### Artifact tree

On committed code, still none: D13 is unreachable while B-10 is open. Under the
B-10/B-11/B-12 recipe the graph wrote a real deterministic SVG, a real unit PDF
and layout source, and two real page images into an ephemeral sandbox — recorded
in the probe, not claimed as this node's artifact tree. Ephemeral roots only: a
`tempfile` output root per episode for the `SqliteSaver`, and a separate
system-temp sandbox for the fake transport, which refuses any root that is not
under the system temp directory and is separately asserted never to address a
product root.

## Findings

### Resolved since generation 7

- **B-6 (RESOLVED) — no registered edge routed a model dispatch through D90.**
  Fixed by `N20_GRAPH_COMPILER` generation 7 (`results/N20_GRAPH_COMPILER.result.v1.md`,
  "Generation-7 rework"), which applied this node's four-part recipe to
  `routing.py` and found a fifth row of its own on the workbook path
  (`D27.workbook_packet_frozen`, which N30 could not have seen). Re-verified here
  by execution, not taken on report: `test_every_model_dispatch_is_routed_through_d90`
  reads the really-compiled edge set and finds all six dispatchers routed to D90
  **and no model node with any other predecessor**; `test_d90s_authorized_guard_expresses_a_map`
  proves a 2-member packet becomes two `Send`s and a 1-member packet one, so
  D07/D08/D15's single dispatches no longer collapse into a whole-state edge; and
  a real episode ran four D90-mediated dispatches with `D91` never entered.

- **B-7 (RESOLVED) — the model candidate record was not an admissible version.**
  Fixed by `N22_DETERMINISTIC_NODES` generation 6 (admission mints the version:
  `latest_model_candidate`, `candidate_payload`, `candidate_field`,
  `mint_version`) with `N23_MODEL_NODES` generation 4 supplying the lineage
  fields and enforcing `ADMISSION_OWNED_CANDIDATE_FIELDS`. Re-verified here:
  `test_a_model_candidate_is_minted_into_an_admissible_artifact_version` runs the
  real M02 adapter and the real D08 body and shows the candidate still carrying
  no `version`/`hash`/`parent_hash` *and* D08 resolving it;
  `test_each_join_reads_a_lineage_field_the_candidate_record_now_writes` asserts
  the lineage on records a real episode produced (`retrieval_sha256`, `unit_id`,
  and `locators` still quarantined inside `payload`) rather than by scanning
  N23's source, which would have passed for the wrong reason; and, decisively, a
  real episode advanced a real domain head.

- **B-9 (RESOLVED) — two N20 assertions were superseded by D90/D91 registration.**
  Fixed by `N20_GRAPH_COMPILER` generation 7, which re-scoped those two and three
  further assertions the same change superseded. Re-verified here: the whole
  `-k plan26` selection is now **0 failed** in the hash-locked environment, where
  generation 7 recorded exactly those two rows red.

- **B-1 through B-5** remain resolved as recorded at generation 7 (N11 gen 5,
  N22 gen 5, N23 gen 3, N20 gen 6, N21 gen 7); each is still covered by the
  regression that would catch a reversal, and all of those regressions pass.

### Open

- **B-10 (BLOCKING, new, highest severity) — `deterministic_node` -> N22_DETERMINISTIC_NODES,
  with N23_MODEL_NODES for the M03 output schema.**
  Fingerprint `plan26/n30/unit-content-contract-is-unsatisfiable`.
  Evidence keys: `runtime/langgraph_factory/schemas/M03_write_unit_content.schema.json`
  (`properties.unit_content`) against `runtime/langgraph_factory/nodes/domain.py:46`
  (`CURRICULUM_CONTRACTS`) and `nodes/content.py:76` (`schema_path=CURRICULUM_CONTRACTS[0]`),
  plus `nodes/visuals.py:109` (`body.get("visuals", [])`). Probes:
  `evidence/N30_UNIT_GRAPH/blocker_probe_unit_content_contract.txt` and the
  runtime failure in `e2e_trace.txt`.
  Three owners disagree about what a unit content document *is*, and no document
  satisfies all three. M03's output schema constrains `unit_content` to exactly
  `{unit_id, sections, evidence_references}` with `additionalProperties: false`.
  D09 validates that body against `CURRICULUM_CONTRACTS[0]` =
  `schemas/curriculum.schema.v5.json`, which is the whole-**curriculum manifest**
  schema: also `additionalProperties: false`, requiring `manifest_version`,
  `curriculum`, `domain` and `labs`, and permitting none of M03's three keys. The
  two property sets are **disjoint in both directions**, so
  `content_schema_valid` can never pass — this is a property of the contracts,
  not of any particular candidate, and is asserted as such by
  `test_blocked_no_unit_content_document_can_satisfy_both_its_contracts` rather
  than by one failing sample. D10 then reads `body["visuals"]`, a key
  `additionalProperties: false` forbids M03 from ever writing, so even a passing
  content head would produce an empty visual denominator forever
  (`test_blocked_a_real_m03_content_head_can_declare_no_visual`).
  Why no predecessor caught it: N22 proved D09 admits a candidate it constructed
  itself, and N23 proved M03's output validates against M03's own schema. Only
  running a real M03 result into a real D09 puts the two contracts in the same
  room.
  **Required rework, verified before reporting** (recipe in
  `evidence/N30_UNIT_GRAPH/blocker_probe_b10_b11_b12_recipe.txt`, in memory only):
  give the engine a real unit-content contract and point `CURRICULUM_CONTRACTS[0]`
  at it. Both D08's `curriculum_contracts` projection and D09's `schema_path`
  read that one constant, so a single change keeps the model held to exactly what
  validates it — which is the property that made this defect invisible when the
  constant pointed somewhere unsatisfiable. The contract must admit the `visuals`
  declaration D10 reads, which also means M03's output schema gains `visuals`
  (N23's half, and the smaller one). Choosing `curriculum.schema.v5.json`'s
  `$defs/lab` instead is *not* a fix: it requires 14 properties and forbids all
  three of M03's, so it is unsatisfiable in the same way.
  With that one change the same episode advances D09 -> D10.

- **B-11 (BLOCKING, new) — `deterministic_node` -> N22_DETERMINISTIC_NODES.**
  Fingerprint `plan26/n30/d15-requires-a-layout-head-nothing-admits`.
  Evidence keys: `runtime/langgraph_factory/nodes/review.py:28`
  (`PACKET_ARTIFACT_CHANNELS` includes `layout`) and `:40-48` (the head
  requirement) against `nodes/render.py:101-124` (D13 appends a versioned layout
  record and writes no head) and spec 8.1's D13/D14 rows ("append-unique") and
  spec section 5's `artifact_heads` row ("admission nodes only").
  D15 requires an admitted head for every one of its four channels, but the
  spec's own authority table admits heads at D08, D09, D12 and D20 only, and none
  of those owns the layout channel. The requirement is therefore unsatisfiable by
  construction, and D15 fails `class=system, cause=invalid_input, "the review
  packet requires an admitted layout head"` on a state that is otherwise
  complete. `test_blocked_d15_requires_a_layout_head_no_node_admits` asserts both
  halves: no node body that writes `artifact_heads` mentions the layout channel,
  and the real D15 body really fails.
  **Required rework, verified before reporting**: D15 resolves the layout from
  D13's appended version rather than from a head — which it already does, at
  `review.py:83`, for its own PDF-bytes check, so the fix is to stop requiring
  the head rather than to add a new lookup. The safety property D15 exists to
  hold (the packet names the bytes the inventory measured) is carried by that
  existing `latest_candidate` check and is not weakened.

- **B-12 (BLOCKING, new) — `deterministic_node` -> N22_DETERMINISTIC_NODES.**
  Fingerprint `plan26/n30/d11-cannot-read-its-own-send-member`.
  Evidence keys: `runtime/langgraph_factory/routing.py:422-449` (`_staged_fanout`
  emits `Send(destination, member)`) against the `D11_CREATE_DETERMINISTIC_VISUALS`
  catalogue row (`inputs == ("pending_packet",)`) and `nodes/visuals.py:200`
  (`packet = projection["pending_packet"]`).
  D11 is the only deterministic `Send` target in the graph and the one worker
  that cannot read its own member. A `Send` delivers the member *as the target's
  whole input state* — which is how every M0x adapter reads its packet — but
  D11's row declares its input as `pending_packet`, so `project()` looks for that
  key on the member and finds nothing. Every deterministic visual fails
  `invalid_input: no visual brief packet`, and D12 then reports a `join` system
  failure because the deterministic subset can never equal its frozen
  denominator. `test_blocked_d11_cannot_read_the_member_the_fanout_delivers`
  drives the real D10 body, the real guard and the real D11 body and shows the
  member carrying `brief` and no `pending_packet`.
  **Required rework, verified before reporting**: D11's catalogue row and body
  read `brief`/`permitted_facts` off their own input, matching the convention
  every model worker already follows. With the member adapted the same episode
  produced a real deterministic visual and D12 joined both subsets.

- **B-13 (BLOCKING for production, not for this node's proof) —
  `model_node_or_projection` -> N23_MODEL_NODES.**
  Fingerprint `plan26/n30/m01-phases-share-one-attempt-counter`.
  Evidence key: D90's counter-key derivation in `runtime/langgraph_factory/model_nodes.py`
  (one counter per `correlation_key`) against N22's own constraint, recorded in
  `N22_DETERMINISTIC_NODES.result.v1.md`, that both M01 phases must keep
  `correlation_key == request_key` because D06B indexes `source_discoveries` and
  D07 indexes `source_interpretations` by it. Probe:
  `evidence/N30_UNIT_GRAPH/blocker_probe_m01_attempt_budget.txt`.
  The discovery and interpretation activations therefore share one counter. A run
  in which **nothing goes wrong** still spends 2 of the frozen limit of 2 — the
  real episode's committed `attempt_counters` show
  `M01_RESEARCH_UNIT_SOURCES|U001/1/required_explanation:000: 2` — so the first
  transport fault on either phase resolves `exhausted` rather than retrying. The
  one retry spec section 12 freezes does not exist for M01 anywhere in a run.
  `test_blocked_a_successful_run_spends_m01s_whole_retry_budget` drives the real
  D06 body and the real D90 three times and shows `authorized`, `authorized`,
  `exhausted`.
  This does not block N30's own evidence — the happy path needs no retry, and
  every episode in this record ran without one — but it removes the retry
  budget from a live run, so it blocks N50 and N60.
  Required rework: the counter key needs the activation's own identity (the M01
  phase, or the job activation kind) alongside the correlation the joins index
  by. The correlation key itself must not change, because D06B and D07 index by
  it; only D90's counter derivation should.

- **B-8 (BLOCKING for production, not for this node's proof) —
  `transport_or_authorization` -> N13_TRANSPORT_AUTH.** Unchanged from generation
  7 and re-verified: `test_blocked_the_production_runtime_context_has_no_capability_surface`
  still finds all five of `prove_capability`, `observe_executable`, `render_unit`,
  `inspect_pages` and `render_deterministic_visual` absent from `CliTransport`.
  This node's proof is scoped to a test-only transport by its own prompt, so B-8
  does not block N30's evidence, but it blocks any real run and therefore
  N40_CLI_CUTOVER and N60_LIVE_PRODUCT_PROOF. Note that B-11's recipe run
  exercised all three renderer methods against the test double, so the shape the
  five methods must satisfy is now demonstrated rather than only specified.

## Invalidated descendants

None. No predecessor artifact was modified this generation: `graph.py` is
byte-identical to generation 7, and `routing.py`, `nodes/*.py`, `model_nodes.py`,
`state.py`, `reducers.py`, `persistence.py` and `transport.py` all carry their
owners' current hashes. The only files this node wrote are `unit_graph.py`
(`BLOCKING_GAPS` only) and its own test file.

The compiled topology, and therefore every N20 claim derived from it (single
builder, single `compile()`, binding validation, guard-table totality, digest
determinism), is unchanged at 34 nodes / 100 edges / digest
`10a65426089adc6dcaa6a54339fca33065af48f78c5212224c8e5aafee63cab1`.

N31 and N32 remain gated: both need B-10, B-11 and B-12 before any unit can reach
D16, and N31 additionally implements D16/D17 against the seven deferred edges
above. B-13 and B-8 additionally gate N50 and N60.

## Hashes

| Artifact | SHA-256 |
|---|---|
| `runtime/langgraph_factory/unit_graph.py` | b5067d25fce248bba1cb699124e7696cd10a6495c08ab4abb2a9a365a982c28d |
| `runtime/langgraph_factory/graph.py` | 6361e12cd0f4daa119d6311b1ecb9bab65102978820e22f24da7a259aa7a72aa |
| `tests/runtime/test_plan26_unit_graph.py` | e3b022d1ee46050c043cf3004b33296a050167af090e157a55f2807046f1f85a |
| `runtime/langgraph_factory/routing.py` | 6be93bf8bd951ae9984f74dc9dbe91c709a41edca0a1a6ff6d72be52cd998079 |
| `runtime/langgraph_factory/state.py` | 428c78edd53b73fd3458d469b36e1bb528dea37d4565f3b37995d63e4a075167 |
| `runtime/langgraph_factory/reducers.py` | 05dc3632dd378946ddc1aee1ca725f99f0be7e1c69b516c00061aee336fb26cf |
| `runtime/langgraph_factory/nodes/__init__.py` | c591775a214e0e7b51c051f2e297a8af8e9dc2dba844ed8b5b4944015a02ca02 |
| `runtime/langgraph_factory/nodes/domain.py` | 88b30263219fa98ba19dc12110a9c1754c7c8e494eb3c0c8eb78f68b4a1c6487 |
| `runtime/langgraph_factory/nodes/content.py` | e103557cb83a7850cabe1ca4ed94cdbfc76755e0840f7ef7b5055859e3aa4ef0 |
| `runtime/langgraph_factory/nodes/visuals.py` | e1bd9ea786c29ada3484f7bd64097eefb725849a99cbcace7e8a8b69b054800d |
| `runtime/langgraph_factory/nodes/render.py` | 76fa183ad8fc26c054a33901d42c3635e3cb5c0094bca70b9f797517e19152b4 |
| `runtime/langgraph_factory/nodes/review.py` | fd1b61f25cdf96a82b5f9307b1dd3dbeae9cd8b8eb4605ce182f7980e641cb5e |
| `runtime/langgraph_factory/model_nodes.py` | ff471867ef2c6aa4fa78f6aac9942c85416d1e6305f3c49d9b8f1fb5861718e1 |
| `runtime/langgraph_factory/persistence.py` | c2b3eb236d2ea7bb6ca7f0ff5d6258c8bd1fdec8cf36d9520c2b2ddb9298b289 |
| `runtime/langgraph_factory/transport.py` | 111474fc70ae5cb8a3e95ea8e53f035141eca795138956a1c9879159958d87af |
| `implementation.graph.v2.yaml` | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| `prompts/N30_unit_graph.prompt.v1.md` | f78e98cb44f95a2aa108e87301d3e5fcddd0924e68a47333181bf5ebcd7f5e3e |
| `spec/langgraph_curriculum_factory.spec.v1.md` | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| `contracts/baseline.v1.md` | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| `contracts/digest_algorithm.v1.md` | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| `contracts/erratum_checkpoint_ns_rename.v1.md` | 10d0fe61a98ffcf1f32b1721874758c211765d30f37eae3163e98979205dc1f1 |
| `contracts/node_ownership.v1.md` | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| `contracts/result_record_schema.v1.md` | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| `contracts/shared_names_and_paths.v1.md` | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| `contracts/traceability_matrix.v1.md` | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| `results/N00_BASELINE_FREEZE.result.v1.md` | c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5 |
| `results/N10_DEPENDENCY_API.result.v1.md` | 1788ebb199b74744233107585a22a361ccb3019e529635324a4bd5bb62611658 |
| `results/N11_STATE_REDUCERS.result.v1.md` | 9633ac27f94f1fa97ebf50c0119eb76124f233c3f75311b07697b3281818a0e9 |
| `results/N12_EVIDENCE_ARTIFACTS.result.v1.md` | 6c4a2bbbacb325e4f4b28c36a8811415f5e7d96b24a8e95ce2c10cb70f18c06f |
| `results/N13_TRANSPORT_AUTH.result.v1.md` | aacb3187bfe11f1e16b4eafebab6fba5a8ae7ba0136148b26fafac7f3adb2a71 |
| `results/N20_GRAPH_COMPILER.result.v1.md` | c44d8d4caaebdf540fd80b3b875af062f7ba3d49979b6a310e9e874b4bbbdd7c |
| `results/N21_PERSISTENCE_RESUME.result.v1.md` | cd8f08eac498c14370d31578b056d8e12477293dfad03378cb9680e106fd9841 |
| `results/N22_DETERMINISTIC_NODES.result.v1.md` | c0352f7b8b1d3c02a12a13326dda8a8da0d290e8235dca33d6246381b9181db6 |
| `results/N23_MODEL_NODES.result.v1.md` | d4a273e80302f47e12ad8ac11a0589399a691b3bd4ecc774c06e7acaf452c73d |
| `evidence/N30_UNIT_GRAPH/venv_unit_graph.txt` | ea53869cc612ee40786ad57a7bdd15d516df68c61a5415f7663cad7bfe97ccfb |
| `evidence/N30_UNIT_GRAPH/venv_plan26_all.txt` | 54cbc1bb6caaf650b21dfb4a3901078eaa83a77b24cdef6343029d60808c1b24 |
| `evidence/N30_UNIT_GRAPH/ambient_pytest.txt` | 76e329119fe4034ff39b0c8edc27157f01fadbae1f549be863eaedd9855bd8e0 |
| `evidence/N30_UNIT_GRAPH/compiled_topology.txt` | 4e6448757500bec89a7850fc9b678f73ca21cfc4e8d3655ae9370d1fbe9c1370 |
| `evidence/N30_UNIT_GRAPH/e2e_trace.txt` | 23de886c4d994248907664adf4d19ed7f75df0997f4026f00aa684d925248971 |
| `evidence/N30_UNIT_GRAPH/interrupt_matrix.txt` | c5da834d6123060eec8f9489766f614bec061af2137fb3d6d860732ef868a55b |
| `evidence/N30_UNIT_GRAPH/blocker_probe_b10_b11_b12_recipe.txt` | dc5b10cc99d29c9b8762129e51bb7688045cea20fe9f097913bec43e86d91864 |
| `evidence/N30_UNIT_GRAPH/blocker_probe_unit_content_contract.txt` | 3726142be8ab93ca91178e5df0f2cae641241360b4b641d217532743b6b6d94b |
| `evidence/N30_UNIT_GRAPH/blocker_probe_m01_attempt_budget.txt` | 1733f1757525cf64e5b75b0c5eb18c1d63fee3d2a21a2d0994381c81edf35eaa |
| `evidence/N30_UNIT_GRAPH/blocker_probe_capability_surface.txt` | c8667afd01849bdba86bda942c8a3288b3d7caadc6e50e19f42b0d541872df0b |

Compiled unit-path graph digest (real, reproducible):
`10a65426089adc6dcaa6a54339fca33065af48f78c5212224c8e5aafee63cab1`.
</content>
</invoke>
