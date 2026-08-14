# QA criteria — Run 27 execution package v2 (n20_recovery.plan.v2.md, Phase E)

The primary artifact under review is
`plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v1.yaml`
(graph semantic `version: 2`), together with its three fresh node prompts
(`execution_package_v2/prompts/N00_spec_approval_gate.prompt.v3.md`,
`execution_package_v2/prompts/N20_provider_transport.prompt.v3.md`,
`execution_package_v2/prompts/N30_preflight_egress.prompt.v3.md`), its
node-scoped scanner entry point
(`execution_package_v2/controller/scan_node.py`), its two validator entry
points (`execution_package_v2/tools/validate_plan_v2.py`,
`execution_package_v2/tools/validate_result_v2.py`), and its automated test
suite (`execution_package_v2/tests/test_execution_package_v2.py`). Together
these are "execution package v2" that
`plans/27_langgraph_curriculum_factory_remediation/n20_recovery.plan.v2.md`'s
Phase D requires.

This package is a from-scratch, isolated rebuild, not an edit, of the first
execution-package correction
(`plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml`,
unchanged and immutable). That first correction's own independent QA round 1
found `PKG-QA-001`: its node-scoped verification command never passed
`--graph`, so its extended scanner silently defaulted to loading the
*parent* v1 graph
(`plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml`)
instead of the corrected v2 write sets. That failed attempt, its QA session
(`019ffbfc-edce-7750-a58a-a008cefbd95e`), and the `PKG-QA-001` finding are
provided as grounding and must be treated as immutable historical record,
not as a target for further QA action. This package's job is to prove the
same class of defect is now structurally impossible, not merely absent by
convention.

A correct package v2 satisfies every criterion below. Attempt to falsify
each one against the actual text and behavior of the artifacts — do not
accept a claim the artifact makes about itself without checking it.

## Criteria (PKGV2-T00–PKGV2-T10)

1. **PKGV2-T00 — Historical immutability.** `implementation.graph.v1.yaml`
   (the parent v1 package's graph) and `implementation.graph.v2.yaml` (the
   failed correction) are byte-unchanged from the live repository state, as
   are every `results/N00_SPEC_APPROVAL_GATE.result.v1.json`,
   `results/N10_HARNESS_PROTOCOL.result.v1.json`,
   `results/N20_PROVIDER_TRANSPORT.result.v1.json`, their
   `results/evidence/` directories, and the root `QA/` session directory
   with its `PKG-QA-001` finding. The three Phase-A-restored files
   (`controller/check_forbidden_production_refs.py`,
   `tools/validate_plan.py`, `tools/validate_result.py` in the parent
   package, not this one) retain their required admitted hashes
   (`cb530b32...`, `9f534ba3...`, `0beef6ed...`) — verify directly against
   the live repository.
2. **PKGV2-T01 — No silent v1 graph fallback (the direct PKG-QA-001 fix).**
   Read `execution_package_v2/controller/scan_node.py`'s `DEFAULT_GRAPH_PATH`
   and its argument parser. Confirm the default, and every fallback path, is
   this package's own graph file, never
   `plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml`.
   Separately, read every `N20_PROVIDER_TRANSPORT` through
   `N50_EVIDENCE_AUDIT_CONTROLS` verification command in this package's
   graph and confirm each node-scoped `scan_node.py --node <ID>` invocation
   also carries an explicit `--graph <this package's graph path>` — the
   binding must be visible in the graph itself, not merely correct by the
   scanner's internal default. Confirm
   `execution_package_v2/tools/validate_plan_v2.py` actively rejects a
   node-scoped scan command that omits this explicit binding (not merely
   documents that it should be present).
3. **PKGV2-T02 — Node mode is a genuine narrowing.** Read
   `scan_node.py`'s `run_node`/`restrict_to_write_set` functions. Confirm
   node mode is computed by calling the parent module's unmodified
   whole-tree `scan_production`/`scan_tests` and then filtering the
   resulting scanned-file and violation lists to the node's own write-set
   intersection — not a reimplementation of the term/credential/guard-
   region/occurrence rules. Confirm it cannot scan more broadly than the
   whole-tree scopes would, and cannot skip a file within the node's write
   set that either whole-tree scope would have scanned.
4. **PKGV2-T03 — atomic N20 ownership of the egress boundary.**
   `runtime/langgraph_factory/egress.py` and
   `tests/runtime/test_plan26_egress.py` are in
   `N20_PROVIDER_TRANSPORT`'s `writes` list and absent from
   `N30_PREFLIGHT_EGRESS`'s. `N30_PREFLIGHT_EGRESS` declares
   `runtime/langgraph_factory/egress.py` under `read_only_inputs`. The N30
   prompt (`prompts/N30_preflight_egress.prompt.v3.md`) explicitly states
   N30 consumes this boundary read-only and does not claim ownership.
5. **PKGV2-T04 — per-node scan coverage matches the graph's own write sets.**
   For every scanning node, the files the node-scoped scan actually covers
   (verify by reading `scan_node.py`'s logic and, if useful, by running it)
   are exactly the intersection of that node's `writes` list with the two
   whole-tree scan scopes' roots — not a hardcoded or hand-maintained file
   list that could drift from the graph.
6. **PKGV2-T05 — N60 alone uses complete-tree mode.** Read every node's
   verification list. Confirm `scan_node.py` is invoked without `--node`
   only for `N60_ADVERSARIAL_REGRESSION`, and with `--node <exact node ID>`
   for every other scanning node (`N20`–`N50`).
7. **PKGV2-T06 — result/evidence versioning never reuses v1 paths.** Every
   node's own result/evidence write path in this package's graph lives
   under `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/`,
   never the parent v1 package's `results/` root nor the failed
   correction's `results/v2/` root. `result_pattern` in the graph header
   reflects this.
8. **PKGV2-T07 — source_spec binding.** The graph's `source_spec` field
   points at the QA-passed specification artifact
   (`plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`,
   sha256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`),
   not v1, v2, or v3-by-filename. `validate_plan_v2.py` enforces both the
   path and the digest, not merely the path.
9. **PKGV2-T08 — no write-set overlap.** Every write path in this package's
   graph belongs to exactly one node; no two nodes claim overlapping paths.
   You may verify this by reading every node's `writes` list directly, or
   by noting that
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`
   reports `valid: true`, which includes this exact check (cited as a fact
   to confirm, not evidence to accept unchecked).
10. **PKGV2-T09 — no implementation performed; no production edit.** No file
    under `runtime/`, `policy/`, `schemas/routes.schema.v1.json`, or
    `schemas/model_registry.schema.v1.json` was created or changed while
    authoring this package. `git status` (available to you read-only) shows
    changes confined to `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/`
    and the three Phase-A restorations only.
11. **PKGV2-T10 — automated proof, not narrative.**
    `execution_package_v2/tests/test_execution_package_v2.py` is a real,
    passing, automated suite (not a documentation file) that positively
    proves PKGV2-T01 through PKGV2-T09 above, including at least one seeded
    violation in a synthetic tree proving node-scope narrowing actually
    rejects a defect, one proving the same defect surfaces in complete-tree
    mode, and one proving `git status` shows no production/policy/schema/
    active-test change from authoring this package. Run
    `python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py`
    yourself if useful and confirm it passes.

## Falsification targets

- `scan_node.py`'s default graph path is computed once at import time from
  `Path(__file__).resolve()`; confirm this genuinely resolves to
  `execution_package_v2/implementation.graph.v1.yaml` and not, by an
  off-by-one `.parent` chain, to the parent v1 package's directory.
- The three fresh prompts' claimed write-set/ownership language matches the
  graph's actual `writes`/`read_only_inputs` for that node exactly (no
  prompt claiming an ownership the graph does not grant, or vice versa).
- `validate_plan_v2.py`'s node-scoped-graph-binding check
  (`node_scoped_scan_commands`/the loop that requires `--graph`) is not
  itself silently vacuous — for example by matching on a substring that
  would also match an unrelated command, or by only checking nodes that
  happen to already be correct.
- The package's `rules:` block (scan-scope declarations, `frozen_before_entry`,
  etc.) is unchanged in substance from the parent v1 package except where
  this criteria file says it should differ.
- N40, N50, N60, N70, N80, N90's prompts are reused unmodified from the
  parent v1 package's `prompts/` directory because this correction does not
  change their scope — confirm the graph actually points at those unmodified
  files rather than silently forking them.

## Severity guidance

Use `major` threshold: a finding is reportable only if it defeats one of the
eleven numbered criteria above (a stated criterion fails on a realistic
reading of the artifacts, not merely a stylistic quibble). Anything you
notice that does not defeat a numbered criterion belongs in observations,
not findings.
