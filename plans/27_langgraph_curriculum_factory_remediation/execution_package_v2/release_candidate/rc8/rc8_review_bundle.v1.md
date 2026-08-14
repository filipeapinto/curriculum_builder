# RC8 review bundle — Run 27 execution package v2 release candidate

## Why this document exists

This is the single artifact submitted to `qa-gate-codex-run` for this session. It is **not** a summary or a pointer file — every file below is embedded verbatim, in full, so that Codex's judged content *is* the reviewed logic itself, not a description of it or a `--ground` source held outside the chain (except `deprecated/implementation.graph.v6.yaml`, static historical content supplied separately as `--ground`, mirroring rc7's own treatment of `deprecated/implementation.graph.v5.yaml`).

Independent verification of rc7 (`QA_PASSED`, chain-valid, session `019ffd88-b735-77c0-ad8d-145ba014751a`) found one real execution-lineage blocker not covered by rc7's own QA criteria: `implementation.graph.v6.yaml`'s `result_pattern` (`execution_package_v2/results/{node_id}.result.v1.json`) is byte-identical to `implementation.graph.v5.yaml`'s own. `N00_SPEC_APPROVAL_GATE` and `N10_HARNESS_PROTOCOL` are already ADMITTED (`PASSED`) and `N20_PROVIDER_TRANSPORT` is already `BLOCKED` (finding `N20V2-F01`), all three with real results at that exact shared path. Because graph v6 genuinely moved N00's prompt/schema binding (to prompt v6 / schema v3), the already-admitted N00 result's recorded `prompt_sha256` no longer matches — running `tools/validate_result_v2.py --node N00_SPEC_APPROVAL_GATE` against graph v6 as originally built genuinely returns `{"error": "N00_SPEC_APPROVAL_GATE: prompt hash mismatch", "valid": false}`. If any of N00, N10, or N20 were re-executed under graph v6, the new result JSON would be written to the exact same path as the existing admitted/blocked record, silently overwriting it — directly violating this recovery effort's repeated, explicit "preserve prior attempts, never overwrite an admitted or blocked record" requirement.

This bundle fixes exactly that defect and makes **no other change**: `implementation.graph.v6.yaml` is deprecated properly (preserved byte-for-byte at `deprecated/implementation.graph.v6.yaml`, confirmed unchanged at sha256 `b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26`), and `implementation.graph.v7.yaml` is introduced with `result_pattern` (and every node's own result/evidence write paths) moved to the versioned subdirectory `execution_package_v2/results/v7/`. `schemas/spec_approval.schema.v4.json` and `contracts/spec_approval.v4.yaml` carry forward rc3's already-approved specification/RC-manifest/QA digests and model assignments unchanged, updated only for the new graph's path/digest and schema version. `prompts/N00_spec_approval_gate.prompt.v7.md`, `prompts/N20_provider_transport.prompt.v7.md`, and `prompts/N30_preflight_egress.prompt.v7.md` are mechanical gate-lineage renames of their v6 predecessors, with no substantive `TEST` requirement changed. `controller/scan_node.py`'s `DEFAULT_GRAPH_PATH` and both `tools/validate_*.py` modules' own graph/schema/contract/result-prefix bindings move to this generation's own artifacts, following the exact same per-generation hardcoded-binding discipline already used across v1 through v6 — neither validator grows a mutable `--graph` flag of its own (see `tools/validate_result_v2.py`'s own updated module docstring for why not: doing so would reintroduce the exact PKG-QA-001 defect class this package's tooling already exists to prevent). `tests/test_execution_package_v2.py` gains a dedicated RC8 section proving the collision cannot recur and every prior artifact is preserved (175 tests total, 14 more than rc7's 161).

`implementation.graph.v5.yaml` (preserved at `deprecated/`), `spec_approval.schema.v1.json`/`v2.json`/`v3.json`, `spec_approval.v1.yaml`/`v2.yaml`/`v3.yaml`, every earlier `*.prompt.v(1-6).md` file, rc1 through rc7 in full (including each one's `QA/` session), and every N00/N10/N20 result and its evidence are preserved exactly as they were and are **not** reopened, edited, or overridden by this bundle or this session. No production file (`runtime/`, `policy/`, `schemas/routes*`, `schemas/model_registry*`) is touched by this session.

Read every section below as source you are being asked to judge, exactly as if you had opened each file directly at its path (given for traceability only — judge the text below, not a live version at that path, since this bundle is the frozen, versioned review target).

---

## `implementation.graph.v7.yaml`

Execution graph. Corrects the RC8 result-namespace collision: implementation.graph.v6.yaml (preserved unchanged below and at deprecated/implementation.graph.v6.yaml, sha256 b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26) correctly fixed N20V2-F01 but its own result_pattern (execution_package_v2/results/{node_id}.result.v1.json) was byte-identical to implementation.graph.v5.yaml's own -- N00 and N10 are already ADMITTED (PASSED) and N20 is already BLOCKED, all three with real results at that exact shared path, so a fresh execution of any of them under v6 as originally built would have silently overwritten those historical records. This file moves result_pattern, and every node's own result-write and evidence-root entries in writes, to the versioned subdirectory execution_package_v2/results/v7/, whose per-node filenames never coincide with the flat per-node files directly under execution_package_v2/results/. rules.frozen_before_entry gains schemas/spec_approval.schema.v4.json in place of schema v3. No node, write set (beyond the result/evidence path move), edge, scan rule, or verification logic otherwise changed in substance from v6 -- the N20V2-F01 scan-scope fix (retired_provider_test_scan.scan_roots as the explicit 17-file migration-owned union) is carried forward unchanged. SHA-256 at snapshot time: `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22`.

```yaml
graph_id: plan27_langgraph_curriculum_factory_remediation
version: 2
status: SCAFFOLDED_BLOCKED_BY_SPEC_APPROVAL
source_incident: plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec_correction.result.v1.md
source_spec: plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md
runner: plans/27_langgraph_curriculum_factory_remediation/run.prompt.md
qa_criteria: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/qa_criteria.v1.md
node_result_schema: plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json
entry: N00_SPEC_APPROVAL_GATE
result_pattern: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/{node_id}.result.v1.json

# This is execution package v2: an isolated, from-scratch rebuild of the
# corrected recovery of the v1 attempt that reached BLOCKED at
# N20_PROVIDER_TRANSPORT
# (plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json,
# findings N20-F01, N20-F02, N20-F03, N20-F04, N20-F06). v1's N00-N20 results
# and evidence, implementation.graph.v1.yaml itself, and this same directory's
# sibling implementation.graph.v2.yaml (the first, failed package correction,
# preserved at sha256
# f297d6528375eeeda5b97a54d654997a65f5d0c7100cf50b54d71c4ca4763b1a together
# with its QA/ session and PKG-QA-001 finding) are untouched, immutable,
# historical evidence. This document does not edit any of them.
#
# implementation.graph.v6.yaml (preserved unchanged at
# deprecated/implementation.graph.v6.yaml, sha256
# b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26) correctly
# fixed N20V2-F01 -- the real N20 execution of implementation.graph.v5.yaml
# (preserved unchanged at deprecated/implementation.graph.v5.yaml, sha256
# ce2362787a9760c9db3b2f667a0561ebd877ec89f24d690b2210ec9b6f3777b8, the graph
# approved and executed in the rc3-approved, rc5-schema-corrected lineage)
# reached a genuine, well-evidenced BLOCKED because
# rules.retired_provider_test_scan.scan_roots swept the whole tests/runtime
# directory, catching two unrelated Plan 11/19/20/21 Gemini-pipeline test
# files no node in this graph owns. v6's fix (narrowing scan_roots to the
# explicit 17-file migration-owned union) was itself correct and is carried
# forward unchanged below -- see
# plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json
# finding N20V2-F01 for the full account; that BLOCKED result and its
# evidence directory remain untouched, immutable history.
#
# This file is this package's seventh gate-tracked artifact version
# (implementation.graph.v7.yaml), correcting a second, independently-found
# defect in v6 itself: v6's own result_pattern
# (execution_package_v2/results/{node_id}.result.v1.json) was byte-identical
# to v5's own result_pattern -- v6 changed which prompt/schema a fresh N00,
# N10, or N20 execution would be admitted under, but never changed *where*
# that fresh result would be written. Because N00 and N10 are already
# ADMITTED (PASSED) with real results at
# execution_package_v2/results/N00_SPEC_APPROVAL_GATE.result.v1.json and
# .../N10_HARNESS_PROTOCOL.result.v1.json, and N20 is already BLOCKED with
# real evidence at .../N20_PROVIDER_TRANSPORT.result.v1.json, re-executing
# any of N00, N10, or N20 under v6 as originally built would validate against
# v6's own newer prompt/schema (whose hash the old admitted results do not
# and cannot match -- validate_result_v2.py already reports "prompt hash
# mismatch" for the admitted N00 record under v6) and then silently overwrite
# those exact same three historical files the moment a fresh attempt tried to
# record its own outcome. This directly violates this whole recovery
# lineage's repeated, explicit "preserve prior attempts, never overwrite an
# admitted or blocked record" requirement, and would do so invisibly: nothing
# about the write itself is malformed, so no schema or scan check catches it
# -- only path collision does.
#
# The fix: result_pattern above now points under
# execution_package_v2/results/v7/, a versioned subdirectory whose own
# per-node filenames never coincide with the flat per-node files directly
# under execution_package_v2/results/ (where the three admitted/blocked
# v5-and-earlier-lineage records permanently live) -- not
# execution_package_v2/results/v2/ (already a distinct, pre-existing
# convention: that name is reserved for a *different* generation entirely,
# the first, failed whole-package correction attempt at the parent v1
# package's own plans/27_.../results/v2/ root, a sibling of this package, not
# a subdirectory inside it). Every node's own result write path and evidence
# root in `writes` below moves in lockstep to
# execution_package_v2/results/v7/{node_id}.result.v1.json and
# execution_package_v2/results/v7/evidence/{node_id} -- the same versioned-root
# naming discipline already used to distinguish package generations
# (results/ vs. the failed correction's own results/v2/), now applied one
# level down to distinguish *graph* generations within this one package,
# since this is the first time two graph versions inside execution_package_v2
# have ever needed genuinely distinct result homes. tools/validate_plan_v2.py
# and tools/validate_result_v2.py's own GRAPH_PATH constants move to this
# file, matching the same per-generation hardcoded-binding discipline already
# established across v1 through v6 -- neither tool grows a mutable/omittable
# --graph flag of its own; see tests/test_execution_package_v2.py for the
# collision and preservation proofs this correction adds.
#
# Because this active graph's own path changes, schema v3's approved_graph
# const (locked to implementation.graph.v6.yaml) can no longer describe this
# package's active graph, so this correction also introduces
# execution_package_v2/schemas/spec_approval.schema.v4.json (identical in
# structure, const-locked to this file's path instead) and
# execution_package_v2/contracts/spec_approval.v4.yaml (carrying forward --
# not reinventing -- the exact approval already recorded in
# spec_approval.v3.yaml: the same specification, specification QA record,
# rc3 manifest, and rc3 QA record already approved by the user, unchanged;
# only approved_graph/approved_graph_sha256 move to this file and
# schema_version becomes 4). This is a mechanical result-namespace
# engineering correction, not a new specification or provider decision, and
# does not infer any new user approval beyond what rc3 already carries.
# N00_spec_approval_gate.prompt.v6.md, N20_provider_transport.prompt.v6.md,
# and N30_preflight_egress.prompt.v6.md are renamed to .v7.md, mechanically
# rebinding their own --graph/schema/contract references the same way every
# prior gate-lineage rename did, with no change to any substantive TEST
# requirement. N40/N50/N60's prompts carry no graph-path reference and are
# reused unchanged. rules.frozen_before_entry below gains schema v4 in place
# of schema v3 (v3 remains, unedited, at its own path -- it is simply no
# longer the frozen schema *this* graph's N00 validates against).
#
# No other node, write set, edge, dependency, rule, or verification logic
# changed in substance from implementation.graph.v6.yaml beyond: (a) every
# command's own literal --graph value now names this file instead of v6; (b)
# every node's own result-write and evidence-root entries in `writes` move
# under execution_package_v2/results/v7/ instead of execution_package_v2/results/;
# (c) rules.frozen_before_entry gains spec_approval.schema.v4.json in place of
# spec_approval.schema.v3.json. rules.retired_provider_test_scan.scan_roots
# (the explicit 17-file migration-owned union) and N20_PROVIDER_TRANSPORT's
# write set (already excluding tests/runtime/test_gemini.py and
# tests/runtime/test_capabilities.py) are byte-identical in substance to v6's
# own -- this correction does not reopen or regress the N20V2-F01 fix.
# ``version: 2`` is unchanged and does not become 3 -- this is the same
# discipline v3->v4->v5->v6 already established: the package's own structural
# version tracks its Phase D correction lineage, not its gate-rename,
# scan-scope-correction, or result-namespace-correction count.

rules:
  success_requires_schema_bound_result: true
  preserve_plan26_history: true
  invalidate_all_descendants_on_ancestor_change: true
  markdown_status_is_authority: false
  allow_parallel_ready_nodes: false
  max_attempts_per_finding: 3
  live_proof_required_for_activation: true
  frozen_before_entry:
    - plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json
    - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v4.json
  forbidden_production_scan:
    scan_roots:
      - runtime/langgraph_factory
      - runtime/run_curriculum.py
      - policy/routes.v1.yaml
      - policy/routing/model_registry.v1.yaml
      - schemas/routes.schema.v1.json
      - schemas/model_registry.schema.v1.json
    excluded_globs:
      - "**/__pycache__/**"
      - "**/*.pyc"
    excluded_roots:
      - plans
      - tests
      - outputs
    prohibited_dispatch_or_import_terms:
      - gemini
      - google.generativeai
    prohibited_credential_names:
      - GEMINI_API_KEY
      - GOOGLE_API_KEY
      - OPENAI_API_KEY
      - ANTHROPIC_API_KEY
    credential_absence_guard_paths:
      - runtime/run_curriculum.py
      - runtime/langgraph_factory/transport.py
    credential_occurrence_policy: >-
      Credential names may appear only in explicit absence/denial guards inside
      runtime/run_curriculum.py or runtime/langgraph_factory/transport.py; they
      may never configure, authenticate, authorize, dispatch, or provide fallback.
  retired_provider_test_scan:
    # An explicit, exact file list -- not a directory to walk recursively --
    # naming every migration-owned active test across N20-N60, and nothing
    # else. tests/runtime contains ~30 files; most (including
    # test_gemini.py and test_capabilities.py, which test the unrelated,
    # still-active Plan 11/19/20/21 Gemini pipeline) are deliberately absent
    # from this list. test_plan27_adversarial.py does not exist on disk yet
    # (N60 creates it); its absence causes no error, and it is automatically
    # covered once N60 creates it, with no further edit to this list.
    scan_roots:
      - tests/runtime/test_plan26_transport.py
      - tests/runtime/test_plan26_model_nodes.py
      - tests/runtime/test_plan26_egress.py
      - tests/runtime/test_curriculum_factory_graph.py
      - tests/runtime/test_plan26_adversarial.py
      - tests/runtime/test_plan26_api_contract.py
      - tests/runtime/test_plan26_lock_drift.py
      - tests/runtime/test_plan26_cli.py
      - tests/runtime/test_plan26_deterministic_nodes.py
      - tests/runtime/test_run_curriculum.py
      - tests/runtime/test_plan26_topology.py
      - tests/runtime/test_plan26_unit_graph.py
      - tests/runtime/test_plan26_repair_acceptance.py
      - tests/runtime/test_plan26_workbook.py
      - tests/runtime/test_plan26_evidence.py
      - tests/runtime/test_plan26_persistence.py
      - tests/runtime/test_plan27_adversarial.py
    excluded_globs:
      - "**/__pycache__/**"
      - "**/*.pyc"
    prohibited_terms:
      - gemini
      - google
      - GEMINI_API_KEY
      - GOOGLE_API_KEY
    occurrence_policy: zero_occurrences_in_active_test_source

nodes:
  N00_SPEC_APPROVAL_GATE:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N00_spec_approval_gate.prompt.v7.md
    depends_on: []
    writes:
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N00_SPEC_APPROVAL_GATE.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N00_SPEC_APPROVAL_GATE
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N00_SPEC_APPROVAL_GATE]
    allowed_results: [PASSED, BLOCKED_SPEC_NOT_APPROVED, BLOCKED]

  N10_HARNESS_PROTOCOL:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N10_harness_protocol.prompt.v1.md
    depends_on: [N00_SPEC_APPROVAL_GATE]
    writes:
      - plans/27_langgraph_curriculum_factory_remediation/controller
      - plans/27_langgraph_curriculum_factory_remediation/schemas/scheduler_receipt.schema.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/schemas/attempt_record.schema.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_node_result_protocol.py
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N10_HARNESS_PROTOCOL.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N10_HARNESS_PROTOCOL
    verification:
      - [python3, -m, pytest, -q, plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_node_result_protocol.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N10_HARNESS_PROTOCOL]
    allowed_results: [PASSED, BLOCKED]

  N20_PROVIDER_TRANSPORT:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N20_provider_transport.prompt.v7.md
    depends_on: [N10_HARNESS_PROTOCOL]
    writes:
      - runtime/langgraph_factory/transport.py
      - runtime/langgraph_factory/model_nodes.py
      - runtime/langgraph_factory/config
      - runtime/langgraph_factory/prompts
      - runtime/langgraph_factory/schemas
      - runtime/langgraph_factory/egress.py
      - policy/routes.v1.yaml
      - policy/routing/model_registry.v1.yaml
      - schemas/routes.schema.v1.json
      - schemas/model_registry.schema.v1.json
      - tests/runtime/test_plan26_transport.py
      - tests/runtime/test_plan26_model_nodes.py
      - tests/runtime/test_plan26_egress.py
      - tests/runtime/test_curriculum_factory_graph.py
      - tests/runtime/test_plan26_adversarial.py
      - tests/runtime/test_plan26_api_contract.py
      - tests/runtime/test_plan26_lock_drift.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N20_PROVIDER_TRANSPORT.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N20_PROVIDER_TRANSPORT
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_transport.py, tests/runtime/test_plan26_model_nodes.py, tests/runtime/test_plan26_egress.py, tests/runtime/test_capabilities.py, tests/runtime/test_curriculum_factory_graph.py, tests/runtime/test_plan26_adversarial.py, tests/runtime/test_plan26_api_contract.py, tests/runtime/test_plan26_lock_drift.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N20_PROVIDER_TRANSPORT, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N20_PROVIDER_TRANSPORT]
    allowed_results: [PASSED, BLOCKED]

  N30_PREFLIGHT_EGRESS:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N30_preflight_egress.prompt.v7.md
    depends_on: [N20_PROVIDER_TRANSPORT]
    writes:
      - runtime/langgraph_factory/nodes/inputs.py
      - runtime/run_curriculum.py
      - tests/runtime/test_plan26_cli.py
      - tests/runtime/test_plan26_deterministic_nodes.py
      - tests/runtime/test_run_curriculum.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N30_PREFLIGHT_EGRESS.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N30_PREFLIGHT_EGRESS
    read_only_inputs:
      - runtime/langgraph_factory/egress.py
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_cli.py, tests/runtime/test_run_curriculum.py]
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_deterministic_nodes.py, -k, "D03 or capability"]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N30_PREFLIGHT_EGRESS, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N30_PREFLIGHT_EGRESS]
    allowed_results: [PASSED, BLOCKED]

  N40_INTEGRATION_OWNERSHIP:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N40_integration_ownership.prompt.v1.md
    depends_on: [N30_PREFLIGHT_EGRESS]
    writes:
      - runtime/langgraph_factory/graph.py
      - runtime/langgraph_factory/routing.py
      - runtime/langgraph_factory/unit_graph.py
      - runtime/langgraph_factory/repair.py
      - runtime/langgraph_factory/acceptance.py
      - runtime/langgraph_factory/workbook.py
      - tests/runtime/test_plan26_topology.py
      - tests/runtime/test_plan26_unit_graph.py
      - tests/runtime/test_plan26_repair_acceptance.py
      - tests/runtime/test_plan26_workbook.py
      - plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N40_INTEGRATION_OWNERSHIP.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N40_INTEGRATION_OWNERSHIP
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_topology.py, tests/runtime/test_plan26_unit_graph.py, tests/runtime/test_plan26_repair_acceptance.py, tests/runtime/test_plan26_workbook.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N40_INTEGRATION_OWNERSHIP, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_ownership.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N40_INTEGRATION_OWNERSHIP]
    allowed_results: [PASSED, BLOCKED]

  N50_EVIDENCE_AUDIT_CONTROLS:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N50_evidence_audit_controls.prompt.v1.md
    depends_on: [N40_INTEGRATION_OWNERSHIP]
    writes:
      - runtime/langgraph_factory/evidence.py
      - runtime/langgraph_factory/artifacts.py
      - runtime/langgraph_factory/persistence.py
      - tests/runtime/test_plan26_evidence.py
      - tests/runtime/test_plan26_persistence.py
      - plans/27_langgraph_curriculum_factory_remediation/contracts/evidence_determinism.v1.yaml
      - plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N50_EVIDENCE_AUDIT_CONTROLS.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N50_EVIDENCE_AUDIT_CONTROLS
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_evidence.py, tests/runtime/test_plan26_persistence.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_evidence_determinism.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/evidence_determinism.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_requirements_lineage.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N50_EVIDENCE_AUDIT_CONTROLS, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N50_EVIDENCE_AUDIT_CONTROLS]
    allowed_results: [PASSED, BLOCKED]

  N60_ADVERSARIAL_REGRESSION:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N60_adversarial_regression.prompt.v1.md
    depends_on: [N50_EVIDENCE_AUDIT_CONTROLS]
    writes:
      - tests/runtime/test_plan27_adversarial.py
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_adversarial.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N60_ADVERSARIAL_REGRESSION.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N60_ADVERSARIAL_REGRESSION
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan27_adversarial.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_adversarial.py]
      - [python3, -m, pytest, -q, tests/runtime]
      - [python3, -m, pytest, -q, plans/27_langgraph_curriculum_factory_remediation/tests]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N60_ADVERSARIAL_REGRESSION]
    allowed_results: [PASSED, BLOCKED]

  N70_LIVE_UNIT_PROOF:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N70_live_unit_proof.prompt.v1.md
    depends_on: [N60_ADVERSARIAL_REGRESSION]
    writes:
      - outputs/run27/live_unit
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N70_LIVE_UNIT_PROOF.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N70_LIVE_UNIT_PROOF
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml, verify-live-proof, --node, N70_LIVE_UNIT_PROOF]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N70_LIVE_UNIT_PROOF]
    allowed_results: [PASSED, NOT_AVAILABLE, BLOCKED]

  N80_LIVE_WORKBOOK_PROOF:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N80_live_workbook_proof.prompt.v1.md
    depends_on: [N70_LIVE_UNIT_PROOF]
    writes:
      - outputs/run27/live_workbook
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N80_LIVE_WORKBOOK_PROOF.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N80_LIVE_WORKBOOK_PROOF
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml, verify-live-proof, --node, N80_LIVE_WORKBOOK_PROOF]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N80_LIVE_WORKBOOK_PROOF]
    allowed_results: [PASSED, NOT_AVAILABLE, BLOCKED]
    read_only_inputs:
      - outputs/run27/live_unit

  N90_REQUIREMENTS_FINAL_AUDIT:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N90_requirements_final_audit.prompt.v1.md
    depends_on: [N80_LIVE_WORKBOOK_PROOF]
    writes:
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N90_REQUIREMENTS_FINAL_AUDIT.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N90_REQUIREMENTS_FINAL_AUDIT
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml, verify-final-audit, --node, N90_REQUIREMENTS_FINAL_AUDIT]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N90_REQUIREMENTS_FINAL_AUDIT]
    allowed_results: [PASSED, BLOCKED]

edges:
  - {from: N00_SPEC_APPROVAL_GATE, to: N10_HARNESS_PROTOCOL}
  - {from: N10_HARNESS_PROTOCOL, to: N20_PROVIDER_TRANSPORT}
  - {from: N20_PROVIDER_TRANSPORT, to: N30_PREFLIGHT_EGRESS}
  - {from: N30_PREFLIGHT_EGRESS, to: N40_INTEGRATION_OWNERSHIP}
  - {from: N40_INTEGRATION_OWNERSHIP, to: N50_EVIDENCE_AUDIT_CONTROLS}
  - {from: N50_EVIDENCE_AUDIT_CONTROLS, to: N60_ADVERSARIAL_REGRESSION}
  - {from: N60_ADVERSARIAL_REGRESSION, to: N70_LIVE_UNIT_PROOF}
  - {from: N70_LIVE_UNIT_PROOF, to: N80_LIVE_WORKBOOK_PROOF}
  - {from: N80_LIVE_WORKBOOK_PROOF, to: N90_REQUIREMENTS_FINAL_AUDIT}

terminals:
  ACTIVATED:
    guard: N60 PASSED; N70 and N80 PASSED with authorized live receipts; N90 independently verified all QA criteria
  REMEDIATION_VERIFIED_NOT_ACTIVATED:
    guard: N60 PASSED; N70 or N80 is NOT_AVAILABLE for an approved subscription driver; N90 verifies no fallback or false product claim
  BLOCKED_SPEC_NOT_APPROVED:
    guard: N00 did not prove a corrected independently verified user-approved specification digest
  BLOCKED:
    guard: an implementation, integrity, evidence, convergence, or audit finding remains unresolved
```

SHA-256: `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22` (26856 bytes)

---

## `controller/scan_node.py`

Package-v2 node-scoped and complete-tree forbidden-reference scanner. Only its DEFAULT_GRAPH_PATH constant and one docstring path reference move from implementation.graph.v6.yaml to implementation.graph.v7.yaml (the same per-generation hardcoded-default discipline used since v1); every node-scoped verification command in the graph itself continues to pass --graph explicitly, so this default is a fail-safe, not the primary binding. All scanning logic is byte-identical to rc7's own copy.

```python
#!/usr/bin/env python3
"""Package-v2 node-scoped and complete-tree forbidden-reference scanner.

This is execution package v2's own versioned entry point, required because
the parent v1 controller module
(``plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py``)
must not be edited by this package (see this package's ``implementation.graph.v7.yaml``
header). It imports that module's scan logic read-only and does not duplicate
or reimplement the term/credential/guard-region/occurrence rules.

Why this file exists rather than reusing ``--node`` on the parent module
directly: the first execution-package correction
(``implementation.graph.v2.yaml``, preserved immutable at
plans/27_langgraph_curriculum_factory_remediation/QA/, finding ``PKG-QA-001``)
added ``--node`` to the parent module in place, but every node-scoped
verification command in that graph omitted ``--graph``, so the extended
scanner silently defaulted to the *parent* v1 graph
(``implementation.graph.v1.yaml`` in the plan root) and therefore scanned the
v1 write sets, not the corrected v2 ones -- a stale-default failure. This
package fixes that class of defect at the root, in two independent ways:

1. Every node-scoped verification command in this package's graph passes
   ``--graph <this package's graph path>`` explicitly (enforced by
   ``tools/validate_plan_v2.py``, which rejects a node-scoped scan command
   that omits it).
2. Independently, if ``--graph`` is ever omitted, this script's own default
   is this package's own graph file, never the parent v1 graph -- so an
   omitted flag fails safe onto the correct write sets rather than silently
   falling back onto stale ones.

Node mode scans the intersection of the named node's declared writable
active files with the existing production/test scan roots: it calls the
parent module's whole-tree ``scan_production``/``scan_tests`` unmodified (so
every term, credential, guard-region, and occurrence rule is exactly as
strict as the whole-tree scopes already are), then narrows the scanned-file
and violation lists to paths covered by the node's own write set. It cannot
scan more broadly than the whole-tree scopes would, and it cannot skip a
file within the node's write set that either whole-tree scope would have
scanned, because it starts from that exact whole-tree result and only
removes files outside the node's ownership.

Complete-tree mode (no ``--node``) is the unmodified parent whole-tree scan,
preserving the original production plus active-test semantics byte for byte.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_PACKAGE_CONTROLLER_DIR = Path(__file__).resolve().parent
_PACKAGE_DIR = _PACKAGE_CONTROLLER_DIR.parent
_PLAN_DIR = _PACKAGE_DIR.parent
_PARENT_CONTROLLER_DIR = _PLAN_DIR / "controller"
if str(_PARENT_CONTROLLER_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_CONTROLLER_DIR))

from check_forbidden_production_refs import scan_production, scan_tests  # noqa: E402
from core import ControllerError, Graph, DEFAULT_REPO_ROOT, covers  # noqa: E402

DEFAULT_GRAPH_PATH = _PACKAGE_DIR / "implementation.graph.v7.yaml"


def in_write_set(relative: str, write_set: list[str]) -> bool:
    return any(covers(owner, relative) for owner in write_set)


def restrict_to_write_set(report: dict[str, Any], write_set: list[str]) -> dict[str, Any]:
    """Narrow a whole-tree scope report to files owned by ``write_set``.

    This never re-evaluates a term/credential/guard-region/occurrence rule; it
    only filters the already-computed scanned-file and violation lists, which
    is what makes this a narrowing rather than a reimplementation.
    """

    restricted = dict(report)
    restricted["scanned_files"] = [
        item for item in report["scanned_files"] if in_write_set(item, write_set)
    ]
    restricted["violations"] = [
        item for item in report["violations"] if in_write_set(item["path"], write_set)
    ]
    return restricted


def run_node(graph: Graph, node_id: str) -> dict[str, Any]:
    node = graph.node(node_id)
    write_set = list(node["writes"])
    production_report = restrict_to_write_set(scan_production(graph), write_set)
    tests_report = restrict_to_write_set(scan_tests(graph), write_set)
    scopes = [production_report, tests_report]
    violations = [item for report in scopes for item in report["violations"]]
    return {
        "command": "scan-node",
        "mode": "node",
        "node_id": node_id,
        "graph_sha256": graph.digest,
        "scopes": scopes,
        "violations": violations,
        "valid": not violations,
    }


def run_complete_tree(graph: Graph) -> dict[str, Any]:
    scopes = [scan_production(graph), scan_tests(graph)]
    violations = [item for report in scopes for item in report["violations"]]
    return {
        "command": "scan-node",
        "mode": "complete-tree",
        "node_id": None,
        "graph_sha256": graph.digest,
        "scopes": scopes,
        "violations": violations,
        "valid": not violations,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument("--graph", type=Path, default=DEFAULT_GRAPH_PATH)
    result.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    result.add_argument("--node", default=None, help="scan only this node's write-set intersection; omit for complete-tree mode")
    result.add_argument("--json", action="store_true", help="print the full report")
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        graph = Graph.load(arguments.graph, arguments.repo_root)
        report = run_node(graph, arguments.node) if arguments.node else run_complete_tree(graph)
    except ControllerError as error:
        print(json.dumps({"ok": False, "code": error.code, "error": str(error)}, sort_keys=True))
        return 1
    if arguments.json:
        print(json.dumps({"ok": report["valid"], **report}, sort_keys=True))
    else:
        print(
            json.dumps(
                {
                    "ok": report["valid"],
                    "mode": report["mode"],
                    "node_id": report["node_id"],
                    "scanned_files": sum(len(item["scanned_files"]) for item in report["scopes"]),
                    "violations": report["violations"],
                },
                sort_keys=True,
            )
        )
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
```

SHA-256: `799b51d6c4f71d5082eb0dc75509bca4c67e06b1945777b51e920bebe79ca24b` (6700 bytes)

---

## `tools/validate_plan_v2.py`

Read-only structural validator for the package-v2 graph. GRAPH_PATH, CONTRACT_SCHEMA_PATH, CONTRACT_PATH, RESULT_PATTERN_PREFIX, and the node-scoped-scan-command graph_flag constant all move to this generation's own artifacts (implementation.graph.v7.yaml, schema v4, contract v4, results/v7/) -- the same per-generation hardcoded-binding discipline v1 through v6 already used. All validation logic (unique write ownership, forward edges, PKGV2-QA-001/002 exact-occurrence argparse-based flag counting, retired_provider_test_scan.scan_roots ownership) is byte-identical to rc7's own copy.

```python
#!/usr/bin/env python3
"""Read-only structural validator for the Run 27 execution package v2 scaffold.

This is package v2's own versioned entry point (see the parent v1
``tools/validate_plan.py``, unmodified and bound to the parent
``implementation.graph.v1.yaml``). It never loads the parent v1 graph.

Beyond the v1 structural checks (unique write ownership, forward edges,
existing prompts, typed scan scopes, frozen-before-entry paths, migration-
affected active-test ownership), this validator additionally enforces the
package-v2-specific corrections:

* ``version`` must be ``2``, not ``1``.
* ``source_spec`` must be the QA-passed v4 specification artifact, at its
  required digest.
* ``result_pattern`` must live under this package's own ``results/v7/`` root
  -- never the parent v1 package's ``results/`` root, the failed correction's
  ``results/v2/`` root, nor this package's own earlier
  ``results/`` root (where the graph-v5-and-earlier-lineage admitted
  N00/N10 results and the BLOCKED N20 result permanently live; reusing that
  path was RC8's own defect, see ``implementation.graph.v7.yaml``'s header).
* every node-scoped ``scan_node.py --node <ID>`` verification command must
  also carry an explicit ``--graph <this package's graph path>`` -- this is
  the direct fix for PKG-QA-001 (the first execution-package correction's
  node-scoped verification silently loaded the parent v1 graph because
  ``--graph`` was never passed). A node-scoped scan command that omits the
  explicit graph binding is rejected outright, even though the scanner's own
  default happens to be safe -- the binding must be visible and auditable in
  the graph, not merely correct by the scanner's internal default.
* each such command's ``--node`` value must equal the exact ID of the node
  that owns it, and its ``--graph`` value must equal exactly this package's
  own graph path -- checking only *presence* of these flags (as the round-1
  version of this validator did) would still pass a command whose ``--node``
  names a different node or whose ``--graph`` points elsewhere, per
  PKGV2-QA-001.
* every ``--node`` and every ``--graph`` flag, on both node-scoped and
  complete-tree (N60) commands, must occur **exactly once**, counted by
  actually running the command's arguments through an ``argparse.ArgumentParser``
  shaped exactly like ``scan_node.py``'s own (a custom ``Action`` records
  every invocation, not just the final value). Python's ``argparse`` resolves
  a repeated occurrence of an option to its *last* occurrence, however that
  occurrence is spelled -- the separated form (``--node value``), the equals
  form (``--node=value``), or an unambiguous prefix abbreviation (``--nod
  value``) -- so a command that keeps a correct first pair and appends a
  second, differently-spelled pair still executes against the second pair at
  runtime. A hand-rolled token check for the exact string ``"--node"`` (the
  round-2 version of this validator) still missed the equals-form spelling
  (round 3's PKGV2-QA-002 finding); using argparse itself to count
  occurrences closes that whole spelling space at once rather than each
  variant only after a QA round demonstrates it. A duplicate occurrence is
  rejected outright regardless of whether the extra occurrence's value is
  itself correct or wrong, since the duplication itself, not any one value,
  is what argparse resolves unpredictably from this validator's point of
  view.
* every node's own result write path and evidence root in ``writes`` must sit
  under this package's own ``results/v7/`` root, matching
  ``results/v7/{node_id}.result.v1.json`` and ``results/v7/evidence/{node_id}``
  exactly for that node's own ID -- never the parent v1 package's
  ``results/`` root, the failed correction's ``results/v2/`` root, nor this
  package's own earlier ``results/`` root.
* ``N60_ADVERSARIAL_REGRESSION`` must be the only node whose ``scan_node.py``
  verification command omits ``--node`` (complete-tree mode); every other
  node that invokes ``scan_node.py`` must do so in node-scoped mode.
* ``runtime/langgraph_factory/egress.py`` and
  ``tests/runtime/test_plan26_egress.py`` must be owned by
  ``N20_PROVIDER_TRANSPORT`` and must be absent from
  ``N30_PREFLIGHT_EGRESS``'s write set; ``N30_PREFLIGHT_EGRESS`` must declare
  ``runtime/langgraph_factory/egress.py`` as a read-only input.

Graph v6 additionally corrected N20V2-F01 (the real N20 execution's genuine
``BLOCKED``, found only once N20 actually ran against graph v5), carried
forward unchanged in graph v7 (which fixes only the unrelated
result-namespace collision documented in its own header): no node may
own ``tests/runtime/test_gemini.py`` or ``tests/runtime/test_capabilities.py``
(they test a wholly separate, still-active Plan 11/19/20/21 Gemini pipeline
this migration does not own), and
``rules.retired_provider_test_scan.scan_roots`` is no longer a directory to
walk recursively -- it is the explicit, exact list of every migration-owned
active test file across N20-N60, and this validator now checks that list
directly:

* every ``scan_roots`` entry must be a ``.py`` file path, never a directory,
  and never an existing non-file;
* every ``scan_roots`` entry must have exactly one owning node (an entry a
  future node has not yet created, like N60's own
  ``tests/runtime/test_plan27_adversarial.py``, is still checked for
  ownership even though it does not exist on disk yet);
* ``scan_roots`` must never name ``tests/runtime/test_gemini.py`` or
  ``tests/runtime/test_capabilities.py``;
* every owner of a ``scan_roots`` entry must run the package-v2 scan, exactly
  as the v1-package predecessor of this rule already required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import jsonschema
import yaml


PACKAGE_DIR = Path(__file__).resolve().parents[1]
PLAN_DIR = PACKAGE_DIR.parent
REPO_ROOT = PLAN_DIR.parents[1]
GRAPH_PATH = PACKAGE_DIR / "implementation.graph.v7.yaml"
RESULT_SCHEMA_PATH = PLAN_DIR / "schemas/node_result.schema.v1.json"
# This package's own package-scoped approval schema (execution_package_v2/schemas/),
# never the parent v1 package's plans/27_.../schemas/spec_approval.schema.v1.json --
# that schema const-locks approved_spec to the *parent* package's own spec and
# cannot validate this package's approval record no matter how it is filled in
# (the exact defect implementation.graph.v5.yaml's header documents fixing).
# Schema v4 (this package's current generation) const-locks approved_graph to
# implementation.graph.v7.yaml instead of v6, correcting the RC8 result-namespace
# collision; schema v3 remains, unedited, the frozen contract for records that
# still cite v6, exactly as schema v2 remains frozen for records citing v5.
CONTRACT_SCHEMA_PATH = PACKAGE_DIR / "schemas/spec_approval.schema.v4.json"
CONTRACT_PATH = PACKAGE_DIR / "contracts/spec_approval.v4.yaml"
RESULT_VALIDATOR_PATH = PACKAGE_DIR / "tools/validate_result_v2.py"
SCAN_NODE_PATH = PACKAGE_DIR / "controller/scan_node.py"

REQUIRED_SOURCE_SPEC = "plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md"
REQUIRED_SOURCE_SPEC_SHA256 = "e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c"
RESULT_PATTERN_PREFIX = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/"
NODE_SCOPED_SCAN_NODES = {
    "N20_PROVIDER_TRANSPORT",
    "N30_PREFLIGHT_EGRESS",
    "N40_INTEGRATION_OWNERSHIP",
    "N50_EVIDENCE_AUDIT_CONTROLS",
}
# N20V2-F01: neither file is owned by any node in this graph. Both test a
# wholly separate, still-active Plan 11/19/20/21 Gemini pipeline this
# migration does not own and has no mandate to touch.
GEMINI_TEST = "tests/runtime/test_gemini.py"
CAPABILITIES_TEST = "tests/runtime/test_capabilities.py"
EGRESS_MODULE = "runtime/langgraph_factory/egress.py"
EGRESS_TEST = "tests/runtime/test_plan26_egress.py"


class ValidationError(RuntimeError):
    pass


def repo_path(value: str) -> Path:
    return REPO_ROOT / value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: expected a mapping")
    return value


def validate_schema_file(path: Path) -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def validate_result_schema_semantics() -> None:
    schema = json.loads(RESULT_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    digest = "0" * 64
    base = {
        "schema_version": 1,
        "run_id": "run-1",
        "node_id": "N10_HARNESS_PROTOCOL",
        "attempt_id": "attempt-1",
        "outcome": "PASSED",
        "source_spec_sha256": digest,
        "prompt_sha256": digest,
        "predecessor_receipts": {"N00_SPEC_APPROVAL_GATE": digest},
        "changed_files": [],
        "commands": [],
        "evidence": [],
        "findings": [],
        "invalidated_descendants": [],
    }
    if not validator.is_valid(base):
        raise ValidationError("ordinary node result must validate without a terminal recommendation")
    if validator.is_valid({**base, "terminal_recommendation": "BLOCKED"}):
        raise ValidationError("non-N90 result must reject terminal_recommendation")
    n90 = {
        **base,
        "node_id": "N90_REQUIREMENTS_FINAL_AUDIT",
        "predecessor_receipts": {"N80_LIVE_WORKBOOK_PROOF": digest},
    }
    if validator.is_valid(n90):
        raise ValidationError("N90 result must require terminal_recommendation")
    if not validator.is_valid({**n90, "terminal_recommendation": "ACTIVATED"}):
        raise ValidationError("passing N90 result must admit ACTIVATED")
    if validator.is_valid({**n90, "outcome": "BLOCKED", "terminal_recommendation": "ACTIVATED"}):
        raise ValidationError("blocked N90 result must reject ACTIVATED")
    if not validator.is_valid({**n90, "outcome": "BLOCKED", "terminal_recommendation": "BLOCKED"}):
        raise ValidationError("blocked N90 result must admit BLOCKED")
    n00_blocked = {
        **base,
        "node_id": "N00_SPEC_APPROVAL_GATE",
        "outcome": "BLOCKED_SPEC_NOT_APPROVED",
        "source_spec_sha256": None,
        "predecessor_receipts": {},
    }
    if not validator.is_valid(n00_blocked):
        raise ValidationError("N00 must admit BLOCKED_SPEC_NOT_APPROVED as an outcome")
    if validator.is_valid({**base, "outcome": "BLOCKED_SPEC_NOT_APPROVED"}):
        raise ValidationError("only N00 may emit BLOCKED_SPEC_NOT_APPROVED")


def validate_spec_approval_contract() -> None:
    """Validate execution_package_v2/contracts/spec_approval.v2.yaml against
    this package's own schemas/spec_approval.schema.v2.json, then prove every
    digest the schema requires as a structured field actually matches live
    repository bytes.

    Schema v2's ``pattern``/``const`` checks alone only prove *shape* --
    JSON Schema cannot read or hash a file, so a syntactically well-formed
    but wrong digest, or a digest bound to a path whose live content has
    drifted, would still validate against the schema. This function is the
    validator-level integrity check the schema itself cannot perform: it
    recomputes each of the five approved digests from the live files the
    contract's own bound paths name and requires exact equality, mirroring
    N00's own TEST step 7.
    """

    schema = json.loads(CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    contract = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(contract, dict):
        raise ValidationError(f"{CONTRACT_PATH}: expected a mapping")
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(contract)

    spec_qa_verification = Path(contract["approved_spec"]).parent / "QA" / "verification.json"
    rc_manifest_path = repo_path(contract["approved_rc_manifest"])
    package_qa_verification = rc_manifest_path.parent / "QA" / "verification.json"
    digest_checks = [
        ("approved_spec_sha256", repo_path(contract["approved_spec"])),
        ("spec_qa_verification_sha256", repo_path(str(spec_qa_verification))),
        ("approved_rc_manifest_sha256", rc_manifest_path),
        ("execution_package_qa_verification_sha256", package_qa_verification),
        ("approved_graph_sha256", repo_path(contract["approved_graph"])),
    ]
    for field, path in digest_checks:
        if not path.is_file():
            raise ValidationError(f"{CONTRACT_PATH}: bound path for {field} is missing: {path}")
        actual = sha256_file(path)
        if contract[field] != actual:
            raise ValidationError(
                f"{CONTRACT_PATH}: {field} mismatch against {path}: "
                f"recorded={contract[field]!r}, actual={actual!r}"
            )

    expected_graph = GRAPH_PATH.relative_to(REPO_ROOT).as_posix()
    if contract["approved_graph"] != expected_graph:
        raise ValidationError(
            f"{CONTRACT_PATH}: approved_graph {contract['approved_graph']!r} does not "
            f"name this package's own active graph {expected_graph!r}"
        )


def topological_order(nodes: dict[str, Any]) -> list[str]:
    unknown = {
        dependency
        for node in nodes.values()
        for dependency in node["depends_on"]
        if dependency not in nodes
    }
    if unknown:
        raise ValidationError(f"unknown dependencies: {sorted(unknown)}")
    remaining = {node_id: set(node["depends_on"]) for node_id, node in nodes.items()}
    order: list[str] = []
    while remaining:
        ready = sorted(node_id for node_id, dependencies in remaining.items() if not dependencies)
        if not ready:
            raise ValidationError(f"dependency cycle: {sorted(remaining)}")
        order.extend(ready)
        for node_id in ready:
            remaining.pop(node_id)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    return order


def paths_overlap(left: str, right: str) -> bool:
    left_path = Path(left)
    right_path = Path(right)
    return left_path == right_path or left_path in right_path.parents or right_path in left_path.parents


def owners_of(nodes: dict[str, Any], relative: str) -> list[str]:
    return [
        node_id
        for node_id, node in nodes.items()
        if any(paths_overlap(relative, owner) for owner in node["writes"])
    ]


class _OccurrenceRecordingStore(argparse.Action):
    """A ``store`` action that also remembers every value it was ever called
    with, not just the final (last-wins) one argparse leaves in the
    namespace."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.values_seen: list[str] = []

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Any, option_string: str | None = None) -> None:
        self.values_seen.append(values)
        setattr(namespace, self.dest, values)


def _scan_node_argument_parser() -> tuple[argparse.ArgumentParser, _OccurrenceRecordingStore, _OccurrenceRecordingStore]:
    """A parser with exactly ``scan_node.py``'s own option shape (``--graph``,
    ``--repo-root``, ``--node``, ``--json``), so occurrence counting goes
    through argparse's own option-matching rules -- exact spelling, the
    equals form, and unambiguous prefix abbreviation alike -- instead of a
    hand-rolled pattern that can only ever cover the spellings someone
    thought to test for. This is what makes duplicate detection track
    whatever argparse itself would actually resolve, rather than one
    hard-coded spelling at a time."""

    parser = argparse.ArgumentParser(add_help=False)
    graph_action = parser.add_argument("--graph", action=_OccurrenceRecordingStore)
    parser.add_argument("--repo-root")
    node_action = parser.add_argument("--node", action=_OccurrenceRecordingStore, default=None)
    parser.add_argument("--json", action="store_true", default=False)
    return parser, graph_action, node_action


def flag_values(command: list[str], flag: str) -> list[str]:
    """Every value argparse's own parsing of this ``scan_node.py`` command
    would assign to `flag`, one entry per occurrence in *any* spelling
    argparse accepts, in the order argparse would see them (so the last
    entry is exactly the value that would actually execute)."""

    parser, graph_action, node_action = _scan_node_argument_parser()
    action = {"--graph": graph_action, "--node": node_action}[flag]
    args = list(command[2:])  # strip ["python3", "<scan_node.py path>"]
    try:
        parser.parse_known_args(args)
    except SystemExit as error:
        raise ValidationError(
            f"scan_node.py verification command has arguments argparse itself "
            f"cannot parse: {command!r}"
        ) from error
    return action.values_seen


def has_flag(command: list[str], flag: str) -> bool:
    return bool(flag_values(command, flag))


def node_scoped_scan_commands(node: dict[str, Any]) -> list[list[str]]:
    scan_node_str = SCAN_NODE_PATH.relative_to(REPO_ROOT).as_posix()
    return [
        command
        for command in node["verification"]
        if command and command[0] == "python3" and len(command) > 1 and command[1] == scan_node_str and has_flag(command, "--node")
    ]


def scan_node_commands(node: dict[str, Any]) -> list[list[str]]:
    """Every scan_node.py invocation on this node, node-scoped or not."""

    scan_node_str = SCAN_NODE_PATH.relative_to(REPO_ROOT).as_posix()
    return [
        command
        for command in node["verification"]
        if command and command[0] == "python3" and len(command) > 1 and command[1] == scan_node_str
    ]


def validate_package_v2_corrections(graph: dict[str, Any]) -> None:
    if graph.get("version") != 2:
        raise ValidationError("execution package v2 graph must declare version: 2")

    if graph.get("source_spec") != REQUIRED_SOURCE_SPEC:
        raise ValidationError(
            f"source_spec must be the QA-passed v4 specification, got {graph.get('source_spec')!r}"
        )
    spec_path = repo_path(REQUIRED_SOURCE_SPEC)
    if not spec_path.is_file():
        raise ValidationError(f"missing source_spec artifact: {REQUIRED_SOURCE_SPEC}")
    digest = sha256_file(spec_path)
    if digest != REQUIRED_SOURCE_SPEC_SHA256:
        raise ValidationError(
            f"source_spec digest mismatch: expected {REQUIRED_SOURCE_SPEC_SHA256}, got {digest}"
        )

    result_pattern = graph.get("result_pattern", "")
    if not result_pattern.startswith(RESULT_PATTERN_PREFIX):
        raise ValidationError(
            f"result_pattern must live under {RESULT_PATTERN_PREFIX}, got {result_pattern!r}"
        )

    nodes = graph["nodes"]
    graph_flag = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml"
    for node_id in NODE_SCOPED_SCAN_NODES:
        if node_id not in nodes:
            continue
        commands = node_scoped_scan_commands(nodes[node_id])
        if not commands:
            raise ValidationError(f"{node_id}: missing a node-scoped scan_node.py --node command")
        for command in commands:
            # PKGV2-QA-002 (round 3): occurrences are counted via flag_values,
            # which recognizes both the separated (--graph value) and equals
            # (--graph=value) spellings argparse accepts -- counting only exact
            # "--graph"/"--node" tokens (the round-2 fix) missed an equals-form
            # duplicate entirely, understating the true occurrence count.
            node_values = flag_values(command, "--node")
            if len(node_values) != 1:
                raise ValidationError(
                    f"{node_id}: node-scoped scan command must carry exactly one "
                    f"--node occurrence (either --node value or --node=value), "
                    f"found {len(node_values)} (PKGV2-QA-002): {command!r}"
                )
            graph_values = flag_values(command, "--graph")
            if len(graph_values) != 1:
                raise ValidationError(
                    f"{node_id}: node-scoped scan command must carry exactly one "
                    f"--graph occurrence (either --graph value or --graph=value), "
                    f"found {len(graph_values)} (PKGV2-QA-002): {command!r}"
                )
            # PKGV2-QA-001: presence of --node/--graph is not enough -- each flag's
            # *value* must be this node's own ID and this package's own graph path,
            # or a scan bound to the wrong node/graph would still pass this check.
            node_value = node_values[0]
            if node_value != node_id:
                raise ValidationError(
                    f"{node_id}: node-scoped scan command's --node value is {node_value!r}, "
                    f"not this node's own ID (PKGV2-QA-001): {command!r}"
                )
            graph_value = graph_values[0]
            if graph_value != graph_flag:
                raise ValidationError(
                    f"{node_id}: node-scoped scan command's --graph value is {graph_value!r}, "
                    f"not the package-v2 graph path (PKGV2-QA-001): {command!r}"
                )

    # PKGV2-QA-001 / the N60 whole-tree exception: exactly one node may invoke
    # scan_node.py without --node (complete-tree mode), and it must be N60. A
    # command that carries even one --node occurrence (PKGV2-QA-002: including
    # one erroneously appended alongside an otherwise bare command) is excluded
    # from whole-tree classification here, which is itself enough to fail this
    # check if it leaves N60 without its required whole-tree command below.
    whole_tree_nodes = sorted(
        node_id
        for node_id, node in nodes.items()
        for command in scan_node_commands(node)
        if not flag_values(command, "--node")
    )
    if whole_tree_nodes != ["N60_ADVERSARIAL_REGRESSION"]:
        raise ValidationError(
            f"N60_ADVERSARIAL_REGRESSION must be the sole whole-tree scan_node.py "
            f"invocation, got {whole_tree_nodes}"
        )

    # PKGV2-QA-002: the whole-tree command itself must carry exactly one
    # --graph occurrence, bound to this package's own graph -- a first-
    # occurrence check would miss a second, argparse-winning --graph appended
    # after a correct first one.
    for node_id, node in nodes.items():
        for command in scan_node_commands(node):
            if flag_values(command, "--node"):
                continue
            graph_values = flag_values(command, "--graph")
            if len(graph_values) != 1:
                raise ValidationError(
                    f"{node_id}: complete-tree scan command must carry exactly one "
                    f"--graph occurrence (either --graph value or --graph=value), "
                    f"found {len(graph_values)} (PKGV2-QA-002): {command!r}"
                )
            graph_value = graph_values[0]
            if graph_value != graph_flag:
                raise ValidationError(
                    f"{node_id}: complete-tree scan command's --graph value is "
                    f"{graph_value!r}, not the package-v2 graph path (PKGV2-QA-002): {command!r}"
                )

    # PKGV2-QA-001: every node's own result write and evidence root must live
    # under this package's own results/ root, keyed by its own exact node ID --
    # never the parent v1 package's results/ root or the failed correction's
    # results/v2/ root.
    for node_id, node in nodes.items():
        writes = node.get("writes", [])
        expected_result = f"{RESULT_PATTERN_PREFIX}{node_id}.result.v1.json"
        expected_evidence = f"{RESULT_PATTERN_PREFIX}evidence/{node_id}"
        if expected_result not in writes:
            raise ValidationError(f"{node_id}: missing its own result write path {expected_result!r}")
        if expected_evidence not in writes:
            raise ValidationError(f"{node_id}: missing its own evidence root {expected_evidence!r}")
        for write in writes:
            if "/results/" in write and not write.startswith(RESULT_PATTERN_PREFIX):
                raise ValidationError(
                    f"{node_id}: result/evidence write path {write!r} does not live under "
                    f"{RESULT_PATTERN_PREFIX!r} (PKGV2-QA-001)"
                )

    n20 = nodes.get("N20_PROVIDER_TRANSPORT", {})
    n30 = nodes.get("N30_PREFLIGHT_EGRESS", {})
    if EGRESS_MODULE not in n20.get("writes", []):
        raise ValidationError(f"N20_PROVIDER_TRANSPORT must own {EGRESS_MODULE}")
    if EGRESS_TEST not in n20.get("writes", []):
        raise ValidationError(f"N20_PROVIDER_TRANSPORT must own {EGRESS_TEST}")
    if EGRESS_MODULE in n30.get("writes", []):
        raise ValidationError(f"N30_PREFLIGHT_EGRESS must not own {EGRESS_MODULE}")
    if EGRESS_TEST in n30.get("writes", []):
        raise ValidationError(f"N30_PREFLIGHT_EGRESS must not own {EGRESS_TEST}")
    if EGRESS_MODULE not in n30.get("read_only_inputs", []):
        raise ValidationError(f"N30_PREFLIGHT_EGRESS must declare {EGRESS_MODULE} as a read-only input")

    # N20V2-F01: neither file may be owned by any node -- they test a wholly
    # separate, still-active Plan 11/19/20/21 Gemini pipeline this migration
    # does not own.
    for node_id, node in nodes.items():
        writes = node.get("writes", [])
        if GEMINI_TEST in writes:
            raise ValidationError(f"{node_id}: must not own {GEMINI_TEST} (N20V2-F01)")
        if CAPABILITIES_TEST in writes:
            raise ValidationError(f"{node_id}: must not own {CAPABILITIES_TEST} (N20V2-F01)")


def validate_graph(graph: dict[str, Any]) -> list[str]:
    required = {
        "graph_id", "version", "status", "source_incident", "source_spec",
        "runner", "qa_criteria", "node_result_schema", "entry",
        "result_pattern", "rules", "nodes", "edges", "terminals",
    }
    missing = sorted(required - graph.keys())
    if missing:
        raise ValidationError(f"missing graph keys: {missing}")
    if graph["graph_id"] != "plan27_langgraph_curriculum_factory_remediation":
        raise ValidationError("unexpected graph_id")

    nodes = graph["nodes"]
    if not isinstance(nodes, dict) or not nodes:
        raise ValidationError("nodes must be a non-empty mapping")
    if graph["entry"] not in nodes or nodes[graph["entry"]]["depends_on"]:
        raise ValidationError("entry must exist and have no dependencies")

    for path_key in ("source_incident", "runner", "qa_criteria", "node_result_schema"):
        if not repo_path(graph[path_key]).is_file():
            raise ValidationError(f"missing {path_key}: {graph[path_key]}")
    if not RESULT_VALIDATOR_PATH.is_file():
        raise ValidationError("missing execution_package_v2/tools/validate_result_v2.py")

    result_validator_relative = RESULT_VALIDATOR_PATH.relative_to(REPO_ROOT).as_posix()

    for node_id, node in nodes.items():
        for key in ("prompt", "depends_on", "writes", "verification", "allowed_results"):
            if key not in node:
                raise ValidationError(f"{node_id}: missing {key}")
        if not repo_path(node["prompt"]).is_file():
            raise ValidationError(f"{node_id}: missing prompt {node['prompt']}")
        if not node["writes"]:
            raise ValidationError(f"{node_id}: empty write set")
        if len(node["writes"]) != len(set(node["writes"])):
            raise ValidationError(f"{node_id}: duplicate write path")
        if not node["verification"]:
            raise ValidationError(f"{node_id}: verification must contain machine-runnable commands")
        for command in node["verification"]:
            if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
                raise ValidationError(f"{node_id}: invalid verification command: {command!r}")
        required_result_validation = ["python3", result_validator_relative, "--node", node_id]
        if required_result_validation not in node["verification"]:
            raise ValidationError(f"{node_id}: missing exact schema/result validation command")
        read_only_inputs = node.get("read_only_inputs", [])
        if not isinstance(read_only_inputs, list) or len(read_only_inputs) != len(set(read_only_inputs)):
            raise ValidationError(f"{node_id}: read_only_inputs must be a unique list")
        for read_only in read_only_inputs:
            if any(paths_overlap(read_only, owner) for owner in node["writes"]):
                raise ValidationError(f"{node_id}: read-only input overlaps its write set: {read_only}")

    order = topological_order(nodes)
    positions = {node_id: index for index, node_id in enumerate(order)}
    edge_pairs = {(edge["from"], edge["to"]) for edge in graph["edges"]}
    dependency_pairs = {
        (dependency, node_id)
        for node_id, node in nodes.items()
        for dependency in node["depends_on"]
    }
    if edge_pairs != dependency_pairs:
        raise ValidationError(
            f"edge/dependency mismatch: edges_only={sorted(edge_pairs - dependency_pairs)}, "
            f"dependencies_only={sorted(dependency_pairs - edge_pairs)}"
        )
    for source, target in edge_pairs:
        if positions[source] >= positions[target]:
            raise ValidationError(f"non-forward edge: {source} -> {target}")

    if graph["rules"].get("allow_parallel_ready_nodes") is not False:
        raise ValidationError("Run 27 must remain sequential until harness hardening passes")
    if graph["rules"].get("markdown_status_is_authority") is not False:
        raise ValidationError("Markdown status cannot be admission authority")

    frozen_before_entry = graph["rules"].get("frozen_before_entry")
    if not isinstance(frozen_before_entry, list) or not frozen_before_entry:
        raise ValidationError("rules.frozen_before_entry must be a non-empty list")
    if graph["node_result_schema"] not in frozen_before_entry:
        raise ValidationError("the N00 node-result schema must be frozen before entry")
    for frozen in frozen_before_entry:
        if not repo_path(frozen).is_file():
            raise ValidationError(f"frozen pre-entry path is missing: {frozen}")
        owners = owners_of(nodes, frozen)
        if owners:
            raise ValidationError(f"frozen pre-entry path has a node owner: {frozen} -> {owners}")

    # A path has one graph owner. Ordering alone must not authorize a downstream
    # node to rewrite an admitted predecessor's output.
    for index, left_id in enumerate(order):
        for right_id in order[index + 1:]:
            overlaps = any(
                paths_overlap(left, right)
                for left in nodes[left_id]["writes"]
                for right in nodes[right_id]["writes"]
            )
            if overlaps:
                raise ValidationError(f"overlapping write ownership: {left_id}, {right_id}")
    for node_id, node in nodes.items():
        for read_only in node.get("read_only_inputs", []):
            prior_owners = [
                owner_id
                for owner_id in order[:positions[node_id]]
                if any(paths_overlap(read_only, owner) for owner in nodes[owner_id]["writes"])
            ]
            if len(prior_owners) != 1:
                raise ValidationError(
                    f"{node_id}: read-only input must have exactly one prior owner: "
                    f"{read_only} -> {prior_owners}"
                )

    scan = graph["rules"].get("forbidden_production_scan")
    required_scan_keys = {
        "scan_roots",
        "excluded_globs",
        "excluded_roots",
        "prohibited_dispatch_or_import_terms",
        "prohibited_credential_names",
        "credential_absence_guard_paths",
        "credential_occurrence_policy",
    }
    if not isinstance(scan, dict) or required_scan_keys - scan.keys():
        raise ValidationError("forbidden_production_scan is missing its typed scope")
    for key in required_scan_keys - {"credential_occurrence_policy"}:
        values = scan[key]
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise ValidationError(f"forbidden_production_scan.{key} must be a unique non-empty list")
    excluded_roots = [Path(value) for value in scan["excluded_roots"]]
    for root_value in scan["scan_roots"]:
        root = Path(root_value)
        if any(excluded == root or excluded in root.parents for excluded in excluded_roots):
            raise ValidationError(f"scan root falls under an excluded root: {root_value}")
        if not repo_path(root_value).exists():
            raise ValidationError(f"forbidden production scan root does not exist: {root_value}")
    for guard_value in scan["credential_absence_guard_paths"]:
        guard = Path(guard_value)
        if not any(Path(root) == guard or Path(root) in guard.parents for root in scan["scan_roots"]):
            raise ValidationError(f"credential absence guard is outside scan_roots: {guard_value}")

    test_scan = graph["rules"].get("retired_provider_test_scan")
    required_test_scan_keys = {
        "scan_roots", "excluded_globs", "prohibited_terms", "occurrence_policy"
    }
    if not isinstance(test_scan, dict) or required_test_scan_keys - test_scan.keys():
        raise ValidationError("retired_provider_test_scan is missing its typed scope")
    if test_scan["occurrence_policy"] != "zero_occurrences_in_active_test_source":
        raise ValidationError("active tests must use the zero-occurrence retirement policy")
    for key in ("scan_roots", "excluded_globs", "prohibited_terms"):
        values = test_scan[key]
        if not isinstance(values, list) or not values or len(values) != len(set(values)):
            raise ValidationError(f"retired_provider_test_scan.{key} must be a unique non-empty list")
    # N20V2-F01: scan_roots is now an explicit, exact list of migration-owned
    # test files, not a directory to walk recursively -- walking the whole
    # tests/runtime directory (~30 files, most unrelated to this migration)
    # is exactly the defect that made the real N20 execution's scan catch two
    # unrelated Plan 11/19/20/21 Gemini-pipeline test files. Each entry must
    # be a .py file path (never a directory) and must have exactly one owning
    # node -- an entry a node has not yet created (e.g. N60's own
    # tests/runtime/test_plan27_adversarial.py) is still required to have an
    # owner, even though it does not exist on disk yet, because ownership is
    # a graph-structural fact, not a filesystem fact.
    for root_value in test_scan["scan_roots"]:
        if repo_path(root_value).is_dir():
            raise ValidationError(
                f"retired_provider_test_scan.scan_roots must name explicit test "
                f"files, not a directory (N20V2-F01): {root_value}"
            )
        if not root_value.endswith(".py"):
            raise ValidationError(f"retired_provider_test_scan.scan_roots entry is not a .py file: {root_value}")
        target = repo_path(root_value)
        if target.exists() and not target.is_file():
            raise ValidationError(f"retired_provider_test_scan.scan_roots entry is not a file: {root_value}")
        owners = owners_of(nodes, root_value)
        if len(owners) != 1:
            raise ValidationError(
                f"retired_provider_test_scan.scan_roots entry must have exactly "
                f"one owning node: {root_value} -> {owners}"
            )
    if GEMINI_TEST in test_scan["scan_roots"] or CAPABILITIES_TEST in test_scan["scan_roots"]:
        raise ValidationError(
            f"retired_provider_test_scan.scan_roots must exclude the unrelated "
            f"Plan 11/19/20/21 Gemini-pipeline tests {GEMINI_TEST!r}/{CAPABILITIES_TEST!r} (N20V2-F01)"
        )

    scan_node_relative = SCAN_NODE_PATH.relative_to(REPO_ROOT).as_posix()
    affected_owners = {owners_of(nodes, root_value)[0] for root_value in test_scan["scan_roots"]}
    for owner in affected_owners:
        commands = nodes[owner]["verification"]
        has_scan = any(
            command and command[0] == "python3" and len(command) > 1 and command[1] == scan_node_relative
            for command in commands
        )
        if not has_scan:
            raise ValidationError(
                f"owner of migration-affected tests must run the package-v2 scan: {owner}"
            )

    expected_terminals = {
        "ACTIVATED", "REMEDIATION_VERIFIED_NOT_ACTIVATED",
        "BLOCKED_SPEC_NOT_APPROVED", "BLOCKED",
    }
    if set(graph["terminals"]) != expected_terminals:
        raise ValidationError("terminal set does not match the plan")

    validate_package_v2_corrections(graph)
    return order


def main() -> int:
    try:
        validate_schema_file(RESULT_SCHEMA_PATH)
        validate_schema_file(CONTRACT_SCHEMA_PATH)
        validate_result_schema_semantics()
        validate_spec_approval_contract()
        graph = load_yaml(GRAPH_PATH)
        order = validate_graph(graph)
    except (
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
        jsonschema.SchemaError,
        jsonschema.ValidationError,
        ValidationError,
    ) as error:
        print(json.dumps({"valid": False, "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps({"valid": True, "graph_id": graph["graph_id"], "order": order}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

SHA-256: `346af878bc31785419dd19bccd772831c0953fcfffbaa1a236b0687b51bd324f` (38064 bytes)

---

## `tools/validate_result_v2.py`

Validates one node result against the package-v2 graph, paths, and hashes. Its GRAPH_PATH constant moves to implementation.graph.v7.yaml. It deliberately keeps its no-flag, single-graph-binding design (documented in its own updated module docstring): adding a mutable --graph flag here would reintroduce exactly the class of defect PKG-QA-001 already found and fixed in scan_node.py (a silently-wrong default graph binding). Because it now points at results/v7/, running it against any of N00/N10/N20 honestly reports "missing result" -- proving the RC8 defect cannot recur, since there is no code path by which a fresh result write could land on the historical files' exact path.

```python
#!/usr/bin/env python3
"""Validate one Run 27 node result against the package-v2 graph, paths, and hashes.

This is execution package v2's own versioned entry point. It is bound to
this package's own ``implementation.graph.v7.yaml``, never to the parent v1
package's graph -- there is no ``--graph`` flag to omit here, because this
script has exactly one graph binding and it is this package's own file. This
is deliberate, not an oversight RC8 should "fix" by adding a mutable flag:
adding an omittable ``--graph`` here would reintroduce exactly the class of
defect PKG-QA-001 already found and fixed in ``scan_node.py`` (a
silently-wrong default graph binding) -- the whole point of this script
having *no* flag is that its one binding can never be omitted or pointed
wrong by a caller. Each graph generation bumps this constant in place
(v1->v2->...->v7), the same discipline ``validate_plan_v2.py``'s own
``GRAPH_PATH`` already uses; neither validator has ever taken its own
``--graph`` argument. RC8 (which introduced ``implementation.graph.v7.yaml``
to fix a result-namespace collision with graph v5's already-admitted
records) does not change this design: the collision was a *path*
defect in the graph file itself, not a defect in this validator's
single-graph binding discipline. See
``tests/test_execution_package_v2.py``'s RC8 collision/preservation tests
for the proof that this discipline does not, itself, need to become
version-parametric to fix the collision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import jsonschema
import yaml


PACKAGE_DIR = Path(__file__).resolve().parents[1]
PLAN_DIR = PACKAGE_DIR.parent
REPO_ROOT = PLAN_DIR.parents[1]
GRAPH_PATH = PACKAGE_DIR / "implementation.graph.v7.yaml"


class ResultValidationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ResultValidationError(f"{path}: expected a JSON object")
    return value


def load_graph() -> dict[str, Any]:
    value = yaml.safe_load(GRAPH_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ResultValidationError("execution package v2 graph is not a mapping")
    return value


def covers(owner: str, changed: str) -> bool:
    owner_path = Path(owner)
    changed_path = Path(changed)
    return owner_path == changed_path or owner_path in changed_path.parents


def validate_result(node_id: str) -> dict[str, Any]:
    graph = load_graph()
    nodes = graph["nodes"]
    if node_id not in nodes:
        raise ResultValidationError(f"unknown node: {node_id}")
    node = nodes[node_id]
    relative_result = graph["result_pattern"].format(node_id=node_id)
    result_path = REPO_ROOT / relative_result
    if not result_path.is_file():
        raise ResultValidationError(f"missing result: {relative_result}")

    schema_path = REPO_ROOT / graph["node_result_schema"]
    schema = load_json(schema_path)
    result = load_json(result_path)
    jsonschema.Draft202012Validator(schema).validate(result)

    if result["node_id"] != node_id:
        raise ResultValidationError(
            f"result node_id {result['node_id']!r} does not match {node_id!r}"
        )
    if result["outcome"] not in node["allowed_results"]:
        raise ResultValidationError(
            f"{node_id}: outcome {result['outcome']!r} is not allowed by the graph"
        )

    expected_predecessors = set(node["depends_on"])
    actual_predecessors = set(result["predecessor_receipts"])
    if actual_predecessors != expected_predecessors:
        raise ResultValidationError(
            f"{node_id}: predecessor receipt keys differ: "
            f"expected={sorted(expected_predecessors)}, actual={sorted(actual_predecessors)}"
        )

    prompt_path = REPO_ROOT / node["prompt"]
    actual_prompt_hash = sha256_file(prompt_path)
    if result["prompt_sha256"] != actual_prompt_hash:
        raise ResultValidationError(f"{node_id}: prompt hash mismatch")

    source_spec_path = REPO_ROOT / graph["source_spec"]
    recorded_spec_hash = result["source_spec_sha256"]
    if source_spec_path.is_file():
        if recorded_spec_hash != sha256_file(source_spec_path):
            raise ResultValidationError(f"{node_id}: corrected specification hash mismatch")
    elif node_id != graph["entry"] or recorded_spec_hash is not None:
        raise ResultValidationError(
            f"{node_id}: missing corrected specification is legal only for the entry gate with null hash"
        )

    write_set = node["writes"]
    for item in result["changed_files"]:
        changed = item["path"]
        if changed == relative_result:
            raise ResultValidationError(
                f"{node_id}: result cannot hash itself; the scheduler receipt binds the result record"
            )
        if not any(covers(owner, changed) for owner in write_set):
            raise ResultValidationError(f"{node_id}: changed path outside write set: {changed}")
        changed_path = REPO_ROOT / changed
        if item["change"] == "deleted":
            if changed_path.exists():
                raise ResultValidationError(f"{node_id}: deleted path still exists: {changed}")
        else:
            if not changed_path.is_file():
                raise ResultValidationError(f"{node_id}: changed file is missing: {changed}")
            if sha256_file(changed_path) != item["sha256"]:
                raise ResultValidationError(f"{node_id}: changed-file hash mismatch: {changed}")

    for command in result["commands"]:
        log_path = REPO_ROOT / command["log"]
        if not log_path.is_file():
            raise ResultValidationError(f"{node_id}: command log is missing: {command['log']}")
        if sha256_file(log_path) != command["log_sha256"]:
            raise ResultValidationError(f"{node_id}: command-log hash mismatch: {command['log']}")
        if result["outcome"] == "PASSED" and command["exit_code"] != 0:
            raise ResultValidationError(f"{node_id}: PASSED result contains a nonzero command")

    for evidence in result["evidence"]:
        if not (REPO_ROOT / evidence).exists():
            raise ResultValidationError(f"{node_id}: evidence path is missing: {evidence}")

    return {
        "valid": True,
        "node_id": node_id,
        "outcome": result["outcome"],
        "result": relative_result,
        "result_sha256": sha256_file(result_path),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--node", required=True)
    return result


def main() -> int:
    arguments = parser().parse_args()
    try:
        payload = validate_result(arguments.node)
    except (
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
        jsonschema.ValidationError,
        ResultValidationError,
    ) as error:
        print(json.dumps({"valid": False, "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

SHA-256: `747575ed07e0dbfc4d36bcc4e4b89442183c0080f268f90ffc913543fc016571` (7445 bytes)

---

## `tests/test_execution_package_v2.py`

The full automated suite (175 tests, 14 more than rc7's 161): every PACKAGE_GRAPH/CONTRACT_SCHEMA/CONTRACT reference moves to this generation's artifacts, and a new RC8 section ("RC8: result-namespace collision / preservation proofs") adds: byte-identity checks for the three admitted/blocked N00/N10/N20 result files; a check that graph v7's result_pattern never collides with the legacy results/ path for any of those three nodes; a behavioral check that the live validate_result_v2.py honestly reports "missing result" (never a collision or a stale-hash pass) for all three; a substance-equality check that graph v7 is otherwise unchanged from graph v6 (same write sets apart from the result/evidence path move, same edges, same scan rules); and byte-preservation checks for schema v3, contract v3, deprecated graph v6, and rc6/rc7's own manifest and QA records.

```python
"""Required tests for execution package v2 (n20_recovery.plan.v2.md, Phase D).

These prove, in order: Phase A's restored v1 bytes and N10 result are intact;
this package's node-scoped scanner genuinely binds to this package's own
graph rather than silently falling back to the parent v1 package's graph
(the exact class of defect independent QA found in this package's failed
predecessor, ``implementation.graph.v2.yaml``'s ``PKG-QA-001`` finding); the
scanner's node-mode narrowing is a real intersection, not a reimplementation
that could quietly weaken a rule; the graph's structural corrections (N60
alone in complete-tree mode, no overlapping write ownership); and that
authoring this package touched no production or active-test file.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema
import pytest
import yaml

TESTS_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = TESTS_DIR.parent
PLAN_DIR = PACKAGE_DIR.parent
REPO_ROOT = PLAN_DIR.parents[1]

PACKAGE_CONTROLLER_DIR = PACKAGE_DIR / "controller"
PACKAGE_TOOLS_DIR = PACKAGE_DIR / "tools"
PARENT_CONTROLLER_DIR = PLAN_DIR / "controller"
PARENT_TOOLS_DIR = PLAN_DIR / "tools"
PARENT_GRAPH = PLAN_DIR / "implementation.graph.v1.yaml"

PACKAGE_GRAPH = PACKAGE_DIR / "implementation.graph.v7.yaml"
DEPRECATED_GRAPH_V4 = PACKAGE_DIR / "deprecated/implementation.graph.v4.yaml"
DEPRECATED_GRAPH_V5 = PACKAGE_DIR / "deprecated/implementation.graph.v5.yaml"
DEPRECATED_GRAPH_V6 = PACKAGE_DIR / "deprecated/implementation.graph.v6.yaml"
CONTRACT_SCHEMA_V2 = PACKAGE_DIR / "schemas/spec_approval.schema.v2.json"
CONTRACT_V2 = PACKAGE_DIR / "contracts/spec_approval.v2.yaml"
CONTRACT_SCHEMA_V3 = PACKAGE_DIR / "schemas/spec_approval.schema.v3.json"
CONTRACT_V3 = PACKAGE_DIR / "contracts/spec_approval.v3.yaml"
CONTRACT_SCHEMA_V4 = PACKAGE_DIR / "schemas/spec_approval.schema.v4.json"
CONTRACT_V4 = PACKAGE_DIR / "contracts/spec_approval.v4.yaml"
PARENT_APPROVAL_SCHEMA_V1 = PLAN_DIR / "schemas/spec_approval.schema.v1.json"
RESULTS_V7_PREFIX = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/"
LEGACY_RESULTS_PREFIX = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/"
SCAN_NODE = PACKAGE_CONTROLLER_DIR / "scan_node.py"
VALIDATE_PLAN_V2 = PACKAGE_TOOLS_DIR / "validate_plan_v2.py"
VALIDATE_RESULT_V2 = PACKAGE_TOOLS_DIR / "validate_result_v2.py"
PACKAGE_PROMPTS_DIR = PACKAGE_DIR / "prompts"

for _dir in (str(PACKAGE_CONTROLLER_DIR), str(PARENT_CONTROLLER_DIR), str(PACKAGE_TOOLS_DIR)):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

import scan_node as scanner  # noqa: E402
from core import Graph  # noqa: E402
import validate_plan_v2  # noqa: E402


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run(argv: list[str]) -> tuple[int, dict[str, Any]]:
    process = subprocess.run(
        [sys.executable, *argv], cwd=REPO_ROOT, capture_output=True, text=True
    )
    return process.returncode, json.loads(process.stdout.strip())


# ------------------------------------------------ Phase A restoration proof


PHASE_A_HASHES = [
    (
        PARENT_CONTROLLER_DIR / "check_forbidden_production_refs.py",
        "cb530b326bb68964976b5b074fefa43392af83bd5c3c6a76f744991d30b066ee",
    ),
    (
        PARENT_TOOLS_DIR / "validate_plan.py",
        "9f534ba3597d331c6ba6c64551004bf01044fb221298aaccd914d476cdf396d0",
    ),
    (
        PARENT_TOOLS_DIR / "validate_result.py",
        "0beef6ed7c5f7bbba3adf50818c53d86dd5cff1f5cefd2abbd8c629a8f229cec",
    ),
]


@pytest.mark.parametrize("path,expected", PHASE_A_HASHES, ids=[p.name for p, _ in PHASE_A_HASHES])
def test_phase_a_v1_files_retain_their_admitted_hash(path: Path, expected: str) -> None:
    assert sha256_file(path) == expected


def test_original_n10_result_still_validates() -> None:
    code, payload = run([str(PARENT_TOOLS_DIR / "validate_result.py"), "--node", "N10_HARNESS_PROTOCOL"])
    assert code == 0
    assert payload["valid"] is True
    assert payload["outcome"] == "PASSED"


# --------------------------------------------- package-v2 graph binding proof


def test_node_scoped_scan_defaults_to_the_package_v2_graph_not_the_parent() -> None:
    code, payload = run([str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--json"])
    assert payload["graph_sha256"] == sha256_file(PACKAGE_GRAPH)
    assert payload["graph_sha256"] != sha256_file(PARENT_GRAPH)


def test_using_the_wrong_parent_graph_explicitly_excludes_n20s_new_egress_ownership() -> None:
    """PKG-QA-001 was exactly this: a node-scoped scan bound to the wrong graph
    silently used stale write sets. Proving the *wrong* binding produces a
    visibly different (and wrong) result confirms the scanner is genuinely
    graph-sensitive, not accidentally graph-invariant."""

    code, payload = run(
        [str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--graph", str(PARENT_GRAPH), "--json"]
    )
    scanned = {item for scope in payload["scopes"] for item in scope["scanned_files"]}
    assert "runtime/langgraph_factory/egress.py" not in scanned


# ---------------------------------------- node-mode intersection, real graph


def test_n20_node_mode_includes_its_newly_owned_egress_module_and_test() -> None:
    """This is the exact real command that reached BLOCKED under graph v5
    (finding N20V2-F01): scan_node.py --node N20_PROVIDER_TRANSPORT --graph
    implementation.graph.v7.yaml (v6 originally fixed this; v7 carries the
    fix forward unchanged, correcting only the unrelated result-namespace
    collision documented in its own header). PKGV2-T22(a) requires dedicated
    proof that it now passes with zero violations, not merely that it scans
    the right file scope."""

    code, payload = run(
        [str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--graph", str(PACKAGE_GRAPH), "--json"]
    )
    assert code == 0
    assert payload["ok"] is True
    assert payload["valid"] is True
    assert payload["violations"] == []
    scanned = {item for scope in payload["scopes"] for item in scope["scanned_files"]}
    assert "runtime/langgraph_factory/egress.py" in scanned
    assert "tests/runtime/test_plan26_egress.py" in scanned


def test_n20_node_mode_ignores_a_later_nodes_owned_file() -> None:
    code, payload = run(
        [str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--graph", str(PACKAGE_GRAPH), "--json"]
    )
    scanned = {item for scope in payload["scopes"] for item in scope["scanned_files"]}
    # runtime/run_curriculum.py is owned by N30_PREFLIGHT_EGRESS, a later node.
    assert "runtime/run_curriculum.py" not in scanned


def test_n30_node_mode_excludes_the_egress_module_it_only_reads() -> None:
    code, payload = run(
        [str(SCAN_NODE), "--node", "N30_PREFLIGHT_EGRESS", "--graph", str(PACKAGE_GRAPH), "--json"]
    )
    scanned = {item for scope in payload["scopes"] for item in scope["scanned_files"]}
    assert "runtime/langgraph_factory/egress.py" not in scanned


def test_complete_tree_mode_against_the_real_repo_reports_the_known_pre_remediation_debt() -> None:
    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_complete_tree(graph)
    assert not report["valid"]


# ------------------------------------------- seeded violations, synthetic tree


class FakePackageRepo:
    """A minimal synthetic tree with two nodes owning disjoint files, so a
    seeded violation's node-mode/complete-tree-mode visibility can be proven
    without touching the real repository."""

    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.graph_path = self.repo / "graph.yaml"
        (self.repo / "runtime/langgraph_factory").mkdir(parents=True, exist_ok=True)
        (self.repo / "tests/runtime").mkdir(parents=True, exist_ok=True)
        self.write("runtime/langgraph_factory/transport.py", "CLI = 'codex'\n")
        self.write("runtime/run_curriculum.py", "def main():\n    return 0\n")
        self.write_graph()

    def write(self, relative: str, text: str) -> Path:
        target = self.repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return target

    def graph_document(self) -> dict[str, Any]:
        return {
            "graph_id": "fake",
            "version": 2,
            "source_spec": "spec.md",
            "node_result_schema": "schema.json",
            "entry": "N_EARLY",
            "result_pattern": "results/{node_id}.json",
            "nodes": {
                "N_EARLY": {"writes": ["runtime/langgraph_factory/transport.py"]},
                "N_LATE": {"writes": ["runtime/run_curriculum.py"]},
            },
            "edges": [],
            "terminals": {},
            "rules": {
                "forbidden_production_scan": {
                    "scan_roots": ["runtime/langgraph_factory", "runtime/run_curriculum.py"],
                    "excluded_globs": ["**/__pycache__/**", "**/*.pyc"],
                    "excluded_roots": ["plans", "tests", "outputs"],
                    "prohibited_dispatch_or_import_terms": ["gemini", "google.generativeai"],
                    "prohibited_credential_names": [
                        "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                    ],
                    "credential_absence_guard_paths": [],
                    "credential_occurrence_policy": "guards only",
                },
                "retired_provider_test_scan": {
                    "scan_roots": ["tests/runtime"],
                    "excluded_globs": ["**/__pycache__/**", "**/*.pyc"],
                    "prohibited_terms": ["gemini", "google", "GEMINI_API_KEY", "GOOGLE_API_KEY"],
                    "occurrence_policy": "zero_occurrences_in_active_test_source",
                },
            },
        }

    def write_graph(self) -> None:
        self.graph_path.write_text(yaml.safe_dump(self.graph_document(), sort_keys=True), encoding="utf-8")

    def graph(self) -> Graph:
        return Graph.load(self.graph_path, self.repo)


@pytest.fixture()
def package_repo(tmp_path: Path) -> FakePackageRepo:
    return FakePackageRepo(tmp_path)


def test_a_seeded_violation_in_an_early_owned_file_fails_only_that_node(package_repo: FakePackageRepo) -> None:
    package_repo.write("runtime/langgraph_factory/transport.py", "CLI = 'gemini'\n")
    graph = package_repo.graph()

    early_report = scanner.run_node(graph, "N_EARLY")
    assert not early_report["valid"]
    assert {item["path"] for item in early_report["violations"]} == {"runtime/langgraph_factory/transport.py"}

    late_report = scanner.run_node(graph, "N_LATE")
    assert late_report["valid"]


def test_the_seeded_violation_and_a_later_violation_both_fail_complete_tree_mode(
    package_repo: FakePackageRepo,
) -> None:
    package_repo.write("runtime/langgraph_factory/transport.py", "CLI = 'gemini'\n")
    package_repo.write("runtime/run_curriculum.py", "def main():\n    return 'gemini'\n")
    graph = package_repo.graph()

    report = scanner.run_complete_tree(graph)
    assert not report["valid"]
    paths = {item["path"] for item in report["violations"]}
    assert "runtime/langgraph_factory/transport.py" in paths
    assert "runtime/run_curriculum.py" in paths


# ------------------------------------------------------ graph shape proofs


def test_n60_is_the_only_node_using_complete_tree_mode() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    complete_tree_nodes = [
        node_id
        for node_id, node in document["nodes"].items()
        for command in node["verification"]
        if len(command) > 1 and command[1] == scan_node_relative and "--node" not in command
    ]
    assert complete_tree_nodes == ["N60_ADVERSARIAL_REGRESSION"]


# ------------------------------------------------- PKGV2-QA-001: exact args


NODE_SCOPED_SCAN_NODES = [
    "N20_PROVIDER_TRANSPORT",
    "N30_PREFLIGHT_EGRESS",
    "N40_INTEGRATION_OWNERSHIP",
    "N50_EVIDENCE_AUDIT_CONTROLS",
]


def _node_scoped_scan_commands(node: dict[str, Any], scan_node_relative: str) -> list[list[str]]:
    return [
        command
        for command in node["verification"]
        if len(command) > 1 and command[1] == scan_node_relative and "--node" in command
    ]


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_each_n20_to_n50_scan_command_carries_its_own_exact_node_id(node_id: str) -> None:
    """PKGV2-QA-001: presence of a --node flag is not proof it names the right
    node -- a command could carry another node's ID and still satisfy a
    presence-only check. Assert the value itself."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    commands = _node_scoped_scan_commands(document["nodes"][node_id], scan_node_relative)
    assert commands, f"{node_id}: no node-scoped scan_node.py command found"
    for command in commands:
        assert command[command.index("--node") + 1] == node_id


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_each_n20_to_n50_scan_command_carries_the_exact_package_v2_graph(node_id: str) -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    expected_graph = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    commands = _node_scoped_scan_commands(document["nodes"][node_id], scan_node_relative)
    assert commands, f"{node_id}: no node-scoped scan_node.py command found"
    for command in commands:
        assert command[command.index("--graph") + 1] == expected_graph


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_each_n20_to_n50_node_owns_its_own_exact_result_path_and_evidence_root(node_id: str) -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    writes = document["nodes"][node_id]["writes"]
    prefix = RESULTS_V7_PREFIX
    assert f"{prefix}{node_id}.result.v1.json" in writes
    assert f"{prefix}evidence/{node_id}" in writes
    for write in writes:
        if "/results/" in write:
            assert write.startswith(prefix), f"{node_id}: {write!r} is not under the package-v2 graph-v7 results root"


def test_n60_whole_tree_exception_is_exactly_n60_and_no_other_node() -> None:
    """Complements test_n60_is_the_only_node_using_complete_tree_mode by also
    proving no N20-N50 node was mutated into the whole-tree exception -- i.e.
    every node-scoped node still carries --node."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    for node_id in NODE_SCOPED_SCAN_NODES:
        commands = [
            command
            for command in document["nodes"][node_id]["verification"]
            if len(command) > 1 and command[1] == scan_node_relative
        ]
        assert commands
        for command in commands:
            assert "--node" in command, f"{node_id} must not use whole-tree mode"
    n60_commands = [
        command
        for command in document["nodes"]["N60_ADVERSARIAL_REGRESSION"]["verification"]
        if len(command) > 1 and command[1] == scan_node_relative
    ]
    assert n60_commands
    assert all("--node" not in command for command in n60_commands)


# --------------------------------------- PKGV2-QA-001: validator mutation proofs


def test_validator_rejects_a_node_scoped_scan_command_whose_node_argument_names_another_node() -> None:
    """PKGV2-QA-001's exact trigger: swap N20's --node value for another
    node's ID and confirm the validator now rejects the graph, not just
    documents that it should."""

    module = _load_module("validate_plan_v2_node_swap_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node = document["nodes"]["N20_PROVIDER_TRANSPORT"]
    rewritten = []
    for command in node["verification"]:
        if len(command) > 1 and command[1] == scan_node_relative and "--node" in command:
            command = list(command)
            command[command.index("--node") + 1] = "N30_PREFLIGHT_EGRESS"
        rewritten.append(command)
    node["verification"] = rewritten
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_a_node_scoped_scan_command_bound_to_the_parent_v1_graph_value() -> None:
    """PKGV2-QA-001's other half: swap --graph's *value* to the parent v1
    graph path (rather than removing the flag entirely, which the round-1
    validator already caught) and confirm the validator rejects it."""

    module = _load_module("validate_plan_v2_graph_swap_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    node = document["nodes"]["N30_PREFLIGHT_EGRESS"]
    rewritten = []
    for command in node["verification"]:
        if len(command) > 1 and command[1] == scan_node_relative and "--node" in command:
            command = list(command)
            command[command.index("--graph") + 1] = parent_graph_relative
        rewritten.append(command)
    node["verification"] = rewritten
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_a_node_result_write_moved_to_the_parent_v1_results_root() -> None:
    """PKGV2-QA-001's result/evidence half: move a node's result write back
    to the parent package's results/ root and confirm rejection."""

    module = _load_module("validate_plan_v2_result_path_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    node = document["nodes"]["N40_INTEGRATION_OWNERSHIP"]
    package_result = f"{RESULTS_V7_PREFIX}N40_INTEGRATION_OWNERSHIP.result.v1.json"
    parent_result = (
        "plans/27_langgraph_curriculum_factory_remediation/"
        "results/N40_INTEGRATION_OWNERSHIP.result.v1.json"
    )
    assert package_result in node["writes"]
    node["writes"] = [parent_result if item == package_result else item for item in node["writes"]]
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_an_evidence_root_moved_to_the_parent_v1_results_root() -> None:
    module = _load_module("validate_plan_v2_evidence_path_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    node = document["nodes"]["N50_EVIDENCE_AUDIT_CONTROLS"]
    package_evidence = f"{RESULTS_V7_PREFIX}evidence/N50_EVIDENCE_AUDIT_CONTROLS"
    parent_evidence = (
        "plans/27_langgraph_curriculum_factory_remediation/"
        "results/evidence/N50_EVIDENCE_AUDIT_CONTROLS"
    )
    assert package_evidence in node["writes"]
    node["writes"] = [parent_evidence if item == package_evidence else item for item in node["writes"]]
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_a_second_node_using_whole_tree_scan_mode() -> None:
    """Proves the N60 whole-tree exception is exact: giving N50 an
    additional bare (no --node) scan_node.py invocation, alongside its
    correct node-scoped one, must be rejected even though N50 still also
    carries a valid --node command."""

    module = _load_module("validate_plan_v2_second_whole_tree_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    graph_flag = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    node = document["nodes"]["N50_EVIDENCE_AUDIT_CONTROLS"]
    node["verification"] = list(node["verification"]) + [
        ["python3", scan_node_relative, "--graph", graph_flag]
    ]
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validate_plan_v2_passes_and_thereby_proves_no_write_path_overlaps() -> None:
    code, payload = run([str(VALIDATE_PLAN_V2)])
    assert code == 0
    assert payload["valid"] is True


def test_validator_rejects_a_node_scoped_scan_missing_the_explicit_graph_binding() -> None:
    """Direct proof that the PKG-QA-001 defect class is now caught, not just
    absent by convention: strip --graph from N20's scan command and require
    the validator to refuse the graph."""

    module = _load_module("validate_plan_v2_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node = document["nodes"]["N20_PROVIDER_TRANSPORT"]
    rewritten = []
    for command in node["verification"]:
        if len(command) > 1 and command[1] == scan_node_relative and "--node" in command:
            index = command.index("--graph")
            command = command[:index] + command[index + 2 :]
        rewritten.append(command)
    node["verification"] = rewritten
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validator_rejects_egress_ownership_outside_n20() -> None:
    module = _load_module("validate_plan_v2_ownership_under_test", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    egress = "runtime/langgraph_factory/egress.py"
    document["nodes"]["N20_PROVIDER_TRANSPORT"]["writes"].remove(egress)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_validate_result_v2_entry_point_is_wired_to_this_package_and_reports_honestly() -> None:
    """N30_PREFLIGHT_EGRESS has not executed under this package (N00, N10,
    and N20 are already admitted), so this proves the tool is correctly wired
    to this package's own graph/result root without fabricating a result
    artifact."""

    code, payload = run([str(VALIDATE_RESULT_V2), "--node", "N30_PREFLIGHT_EGRESS"])
    assert code == 1
    assert payload["valid"] is False
    assert "missing result" in payload["error"]


# --------------------------------------- PKGV2-QA-002: exact occurrence counts


def _scan_node_command(node: dict[str, Any], scan_node_relative: str) -> list[str]:
    """The single scan_node.py invocation on this node (every node in this
    graph has exactly one)."""

    commands = [
        command
        for command in node["verification"]
        if len(command) > 1 and command[1] == scan_node_relative
    ]
    assert len(commands) == 1
    return list(commands[0])


def _replace_scan_command(
    document: dict[str, Any], node_id: str, scan_node_relative: str, new_command: list[str]
) -> None:
    node = document["nodes"][node_id]
    rewritten = []
    replaced = False
    for command in node["verification"]:
        if len(command) > 1 and command[1] == scan_node_relative and not replaced:
            rewritten.append(new_command)
            replaced = True
        else:
            rewritten.append(command)
    assert replaced
    node["verification"] = rewritten


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_exactly_one_of_each_flag_is_accepted(node_id: str) -> None:
    """Positive control: the package's own unmodified graph carries exactly
    one --node and one --graph occurrence per node-scoped command, and must
    validate without error."""

    module = _load_module(f"validate_plan_v2_baseline_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    module.validate_graph(document)  # must not raise


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_missing_node_flag_is_rejected(node_id: str) -> None:
    module = _load_module(f"validate_plan_v2_zero_node_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    index = command.index("--node")
    del command[index : index + 2]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_missing_graph_flag_is_rejected(node_id: str) -> None:
    module = _load_module(f"validate_plan_v2_zero_graph_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    index = command.index("--graph")
    del command[index : index + 2]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_duplicate_node_flag_same_value_is_rejected(node_id: str) -> None:
    """PKGV2-QA-002: duplication itself is the exploitable condition, even
    when the appended occurrence repeats the already-correct value -- a
    first-occurrence check sees the same correct value twice and would still
    pass, but argparse still has two occurrences to resolve from."""

    module = _load_module(f"validate_plan_v2_dup_node_same_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + ["--node", node_id]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_duplicate_node_flag_wrong_value_is_rejected(node_id: str) -> None:
    """PKGV2-QA-002's exact trigger: a scan command retains the correct first
    --node pair and appends a second, wrong one. argparse would execute
    against the wrong (last) value; a first-occurrence check would still see
    the correct first value and pass."""

    module = _load_module(f"validate_plan_v2_dup_node_wrong_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    other_node = next(n for n in NODE_SCOPED_SCAN_NODES if n != node_id)
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + ["--node", other_node]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_duplicate_graph_flag_wrong_value_is_rejected(node_id: str) -> None:
    """PKGV2-QA-002's other trigger: a second --graph pointing at the parent
    v1 graph, appended after the correct package-v2 --graph."""

    module = _load_module(f"validate_plan_v2_dup_graph_wrong_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--graph",
        parent_graph_relative,
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_duplicate_graph_flag_same_value_is_rejected(node_id: str) -> None:
    module = _load_module(f"validate_plan_v2_dup_graph_same_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    expected_graph = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--graph",
        expected_graph,
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


# ---- N60: the whole-tree exception's own zero/one/duplicate proofs


def test_n60_whole_tree_command_with_exactly_one_graph_and_zero_node_is_accepted() -> None:
    module = _load_module("validate_plan_v2_n60_baseline", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    module.validate_graph(document)  # must not raise; the unmodified graph is the positive control


def test_n60_whole_tree_command_missing_graph_flag_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_zero_graph", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    index = command.index("--graph")
    del command[index : index + 2]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_duplicate_graph_flag_wrong_value_is_rejected() -> None:
    """The exact scenario the task calls out: N60's complete-tree command
    with a second, wrong --graph appended after the correct one."""

    module = _load_module("validate_plan_v2_n60_dup_graph_wrong", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--graph",
        parent_graph_relative,
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_duplicate_graph_flag_same_value_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_dup_graph_same", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    expected_graph = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--graph",
        expected_graph,
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_erroneous_node_flag_added_is_rejected() -> None:
    """N60 must stay in complete-tree mode: an erroneously appended --node
    (not a duplicate of an existing flag, since N60 has none to begin with)
    must also be rejected, since argparse would then execute this command in
    node-scoped mode instead of the required complete-tree mode."""

    module = _load_module("validate_plan_v2_n60_added_node", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--node",
        "N20_PROVIDER_TRANSPORT",
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


# ------------------------------- PKGV2-QA-002 round 3: argparse equals-form


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_equals_form_duplicate_node_flag_is_rejected(node_id: str) -> None:
    """PKGV2-QA-002's round-3 finding: argparse accepts --node=value as well
    as --node value, and resolves a mix of the two spellings to the last one
    seen just like two of the same spelling. A count of exact "--node" tokens
    alone would miss an equals-form duplicate; flag_values must not."""

    module = _load_module(f"validate_plan_v2_dup_node_equals_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    other_node = next(n for n in NODE_SCOPED_SCAN_NODES if n != node_id)
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [f"--node={other_node}"]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_equals_form_duplicate_graph_flag_is_rejected(node_id: str) -> None:
    module = _load_module(f"validate_plan_v2_dup_graph_equals_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        f"--graph={parent_graph_relative}"
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


@pytest.mark.parametrize("node_id", NODE_SCOPED_SCAN_NODES)
def test_node_scoped_scan_command_with_single_equals_form_occurrence_is_accepted(node_id: str) -> None:
    """The fix must not overcorrect: a command carrying its one --node and
    one --graph occurrence entirely in equals-form (no duplication at all)
    is exactly one occurrence of each and must still validate."""

    module = _load_module(f"validate_plan_v2_single_equals_{node_id}", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    graph_flag = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    node_index = command.index("--node")
    command[node_index : node_index + 2] = [f"--node={node_id}"]
    graph_index = command.index("--graph")
    command[graph_index : graph_index + 2] = [f"--graph={graph_flag}"]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    module.validate_graph(document)  # must not raise


def test_n60_whole_tree_command_with_equals_form_duplicate_graph_flag_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_dup_graph_equals", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        f"--graph={parent_graph_relative}"
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_equals_form_node_flag_added_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_added_node_equals", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--node=N20_PROVIDER_TRANSPORT"
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_single_equals_form_graph_occurrence_is_accepted() -> None:
    module = _load_module("validate_plan_v2_n60_single_equals", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    graph_flag = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative)
    graph_index = command.index("--graph")
    command[graph_index : graph_index + 2] = [f"--graph={graph_flag}"]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    module.validate_graph(document)  # must not raise


# --------------------------- PKGV2-QA-002: argparse abbreviation-form proofs
#
# The round-3 fix moved occurrence counting onto argparse itself rather than
# hand-rolled patterns, specifically to close the whole spelling space at
# once instead of one variant per QA round. These tests prove that actually
# holds for prefix abbreviation (e.g. --nod for --node), the next spelling
# argparse accepts beyond the separated and equals forms already covered
# above, without a corresponding round-4 finding being needed to add it.


def test_node_scoped_scan_command_with_abbreviation_form_duplicate_node_flag_is_rejected() -> None:
    module = _load_module("validate_plan_v2_dup_node_abbrev", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N20_PROVIDER_TRANSPORT"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--nod",
        "N30_PREFLIGHT_EGRESS",
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_node_scoped_scan_command_with_abbreviation_form_duplicate_graph_flag_is_rejected() -> None:
    module = _load_module("validate_plan_v2_dup_graph_abbrev", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    parent_graph_relative = PARENT_GRAPH.relative_to(REPO_ROOT).as_posix()
    node_id = "N30_PREFLIGHT_EGRESS"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        f"--grap={parent_graph_relative}"
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


def test_n60_whole_tree_command_with_abbreviation_form_node_flag_added_is_rejected() -> None:
    module = _load_module("validate_plan_v2_n60_added_node_abbrev", VALIDATE_PLAN_V2)
    document = module.load_yaml(module.GRAPH_PATH)
    scan_node_relative = SCAN_NODE.relative_to(REPO_ROOT).as_posix()
    node_id = "N60_ADVERSARIAL_REGRESSION"
    command = _scan_node_command(document["nodes"][node_id], scan_node_relative) + [
        "--nod",
        "N20_PROVIDER_TRANSPORT",
    ]
    _replace_scan_command(document, node_id, scan_node_relative, command)
    with pytest.raises(module.ValidationError):
        module.validate_graph(document)


# ------------------------------------------------- no production edit proof


def test_no_production_policy_schema_or_active_test_file_was_modified() -> None:
    """This graph-scaffolding/RC-authoring task itself must touch no
    production, policy, schema, or active-test file. N20_PROVIDER_TRANSPORT
    has, separately, already executed for real and legitimately modified a
    known, recorded set of these files (its own admitted result,
    plans/27_.../execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json,
    lists exactly which ones and their exact sha256) -- that is real,
    independently-verified production work this task must not touch or
    undo, not a defect. So this test's real proof obligation is narrower
    than "zero git diff": every path git reports as changed under these
    roots must be explained by N20's own recorded changed_files at exactly
    N20's own recorded hash; nothing else, and nothing further, may differ."""

    process = subprocess.run(
        [
            "git", "status", "--porcelain", "--",
            "runtime", "policy",
            "schemas/routes.schema.v1.json", "schemas/model_registry.schema.v1.json",
            "tests/runtime",
        ],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert process.returncode == 0
    changed_paths = {line[3:] for line in process.stdout.splitlines() if line.strip()}

    n20_result = json.loads(
        (PACKAGE_DIR / "results/N20_PROVIDER_TRANSPORT.result.v1.json").read_text(encoding="utf-8")
    )
    n20_changed = {
        item["path"]: item["sha256"]
        for item in n20_result["changed_files"]
        if item["change"] != "deleted"
    }

    unexplained = changed_paths - n20_changed.keys()
    assert not unexplained, f"unexpected diff outside N20's own recorded changes: {unexplained}"
    for path in changed_paths:
        assert sha256_file(REPO_ROOT / path) == n20_changed[path], (
            f"{path}: live content no longer matches N20's own admitted-result hash"
        )


# ------------------------------------------------- RC1-QA-001: fresh-prompt
# graph-reference consistency
#
# RC1's one-round QA session (release_candidate/rc1/QA/) returned FAIL with
# finding RC1-QA-001: "Automated suite does not prove fresh-prompt
# consistency" -- no test read or validated N00/N20/N30's prompt text, so the
# suite stayed green while all three prompts instructed a scan against
# `implementation.graph.v1.yaml`, a filename this package does not contain,
# instead of the package's actually enforced and graph-bound
# `implementation.graph.v4.yaml`. The tests below close that blind spot by
# parsing the live prompt text itself (not merely the graph's own
# `verification` commands, already covered above by
# test_each_n20_to_n50_scan_command_carries_the_exact_package_v2_graph).

FRESH_PROMPT_NODE_IDS = ["N00_SPEC_APPROVAL_GATE", "N20_PROVIDER_TRANSPORT", "N30_PREFLIGHT_EGRESS"]

# Matches an explicit `--graph <path>` (whitespace-form) or `--graph=<path>`
# (equals-form) flag value inside a shell command shown in prompt text, e.g.
# "...scan_node.py --node N20_PROVIDER_TRANSPORT --graph
# execution_package_v2/implementation.graph.v4.yaml" or
# "...--graph=execution_package_v2/implementation.graph.v4.yaml".
#
# RC2-QA-001: the whitespace-only form of this pattern left every equals-form
# reference -- correct or stale -- entirely invisible to this check, so a
# stale equals-form reference could sit right beside a correct whitespace-form
# one and the suite stayed green. Both spellings are exactly the two argparse
# itself accepts, the same ambiguity validate_plan_v2.py's own
# flag_values()/_scan_node_argument_parser() already had to resolve for
# PKGV2-QA-002 -- mirrored here rather than reinvented.
_GRAPH_FLAG_PATTERN = re.compile(r"--graph(?:\s+|=)(\S+\.yaml)")

# Matches N00's existence-requirement phrasing, e.g. "Require
# `execution_package_v2/implementation.graph.v4.yaml` to exist". Deliberately
# narrow (requires the literal "Require `...` to exist" shape) so it does not
# also match unrelated backtick-quoted historical filenames elsewhere in the
# same prompt (e.g. a past predecessor package's own graph, cited by name as
# context for an unrelated finding, which is a legitimate reference and must
# not be flagged).
_REQUIRE_EXISTS_PATTERN = re.compile(r"Require `([^`]+\.yaml)` to exist")


def _graph_references(text: str) -> list[str]:
    return _GRAPH_FLAG_PATTERN.findall(text) + _REQUIRE_EXISTS_PATTERN.findall(text)


# RC2-QA-001: a suffix/endswith comparison against `execution_package_v2/<name>`
# let a wrong path *prefix* through unpunished as long as the reference merely
# ended with the enforced graph's filename (e.g.
# "other/execution_package_v2/implementation.graph.v4.yaml"). Resolve each
# extracted reference to its real, absolute filesystem path and require exact
# equality against the package graph's own real path -- never a
# substring/suffix relationship.
#
# Two base directories are legitimate here because this package's own live
# prompts use both conventions: N20/N30 spell the reference as a full
# repo-relative path (resolved against REPO_ROOT), and N00 spells it relative
# to the plan directory (resolved against PLAN_DIR). A reference only counts
# as resolving to the enforced graph if at least one of these bases makes it
# land, path-for-path, on the graph's real location -- a wrong prefix fails
# under both bases, since prepending an extra path segment cannot cancel out.
_GRAPH_REFERENCE_BASES = (REPO_ROOT, PLAN_DIR)


def _resolves_to_enforced_graph(reference: str) -> bool:
    target = PACKAGE_GRAPH.resolve()
    return any((base / reference).resolve() == target for base in _GRAPH_REFERENCE_BASES)


def _fresh_prompt_path(node_id: str) -> Path:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    return REPO_ROOT / document["nodes"][node_id]["prompt"]


@pytest.mark.parametrize("node_id", FRESH_PROMPT_NODE_IDS)
def test_each_fresh_prompt_references_the_exact_enforced_graph(node_id: str) -> None:
    """RC1-QA-001 / RC2-QA-001 regression: the graph-bound prompt for
    N00/N20/N30 must reference this package's actually enforced graph file --
    never a missing, stale, mismatched, or wrong-prefixed one -- whether the
    prompt spells --graph in the whitespace-form or the equals-form."""

    prompt_path = _fresh_prompt_path(node_id)
    text = prompt_path.read_text(encoding="utf-8")
    references = _graph_references(text)
    assert references, f"{node_id}: prompt {prompt_path} contains no graph-path reference at all"
    for reference in references:
        assert _resolves_to_enforced_graph(reference), (
            f"{node_id}: prompt {prompt_path} references {reference!r}, which does not "
            f"resolve to the enforced graph ({PACKAGE_GRAPH!r})"
        )


# Mutation-based negative proof (same discipline as the PKGV2-QA-001/002
# fixes above): prove this check is a real regression test, not a vacuously
# green assertion, by running it against the exact historical prompt text
# that produced RC1-QA-001 -- the superseded v3 prompts, preserved unchanged
# on disk -- and confirming it fails there, then against a reference stripped
# entirely.

_RC1_DEFECTIVE_PROMPTS = {
    "N00_SPEC_APPROVAL_GATE": PACKAGE_PROMPTS_DIR / "N00_spec_approval_gate.prompt.v3.md",
    "N20_PROVIDER_TRANSPORT": PACKAGE_PROMPTS_DIR / "N20_provider_transport.prompt.v3.md",
    "N30_PREFLIGHT_EGRESS": PACKAGE_PROMPTS_DIR / "N30_preflight_egress.prompt.v3.md",
}


@pytest.mark.parametrize("node_id", FRESH_PROMPT_NODE_IDS)
def test_graph_reference_check_rejects_the_real_rc1_qa_001_defect(node_id: str) -> None:
    text = _RC1_DEFECTIVE_PROMPTS[node_id].read_text(encoding="utf-8")
    references = _graph_references(text)
    assert references, (
        f"{node_id}: expected the superseded v3 prompt to still contain a graph "
        "reference to mutate-test against"
    )
    assert any(not _resolves_to_enforced_graph(reference) for reference in references), (
        f"{node_id}: expected the superseded v3 prompt's stale graph reference to be "
        "caught as mismatched by this check, but every reference it found already "
        "resolves to the enforced graph -- the check would not have caught RC1-QA-001"
    )


def test_graph_reference_check_rejects_a_prompt_with_no_graph_reference_at_all() -> None:
    stripped_text = "# GOAL\n\nDo something. No graph file is named anywhere in this text.\n"
    assert _graph_references(stripped_text) == []


@pytest.mark.parametrize("node_id", FRESH_PROMPT_NODE_IDS)
def test_fresh_prompt_graph_references_do_not_regress_to_a_different_wrong_version(node_id: str) -> None:
    """Guards against a fix that merely swaps one wrong version for another
    (e.g. a future graph bump to v5 landing while a prompt still says v4)."""

    prompt_path = _fresh_prompt_path(node_id)
    text = prompt_path.read_text(encoding="utf-8")
    for reference in _graph_references(text):
        mutated = reference.replace(PACKAGE_GRAPH.name, "implementation.graph.v999.yaml")
        assert not _resolves_to_enforced_graph(mutated)


# ------------------------------------------------- RC2-QA-001: equals-form and
# wrong-prefix graph references
#
# RC2's one-round QA session (release_candidate/rc2/QA/) returned FAIL with
# finding RC2-QA-001: the check above only ever matched the whitespace-form
# `--graph <path>` spelling (an equals-form `--graph=<path>` reference, stale
# or correct, was invisible to it entirely) and compared references with
# `str.endswith(...)`, so a wrong path *prefix* that merely ended with the
# enforced graph's own filename (e.g.
# "other/execution_package_v2/implementation.graph.v4.yaml") would incorrectly
# pass. These tests mutation-prove both gaps are closed, plus that a
# genuinely correct reference still passes in either spelling.


def test_graph_reference_check_finds_an_equals_form_reference_at_all() -> None:
    """RC2-QA-001: the original whitespace-only pattern would not even see an
    equals-form reference, correct or stale -- prove it is now extracted."""

    text = (
        "python3 controller/scan_node.py --node N20_PROVIDER_TRANSPORT "
        "--graph=plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v1.yaml"
    )
    assert _graph_references(text) == [
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v1.yaml"
    ]


def test_graph_reference_check_rejects_an_equals_form_stale_reference() -> None:
    """RC2-QA-001's trigger example: a stale equals-form reference sitting
    beside what might otherwise look like a correct whitespace-form one must
    still be caught."""

    text = (
        "Use the whitespace form: --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml\n"
        "Retained stale equals form: --graph=execution_package_v2/implementation.graph.v1.yaml\n"
    )
    references = _graph_references(text)
    assert len(references) == 2
    assert not all(_resolves_to_enforced_graph(reference) for reference in references)


def test_graph_reference_check_rejects_a_wrong_prefix_reference_ending_in_the_right_filename() -> None:
    """RC2-QA-001's other trigger: a wrong path prefix that happens to end
    with the enforced graph's own filename must not slip through a
    suffix/endswith comparison."""

    text = (
        "python3 controller/scan_node.py --node N20_PROVIDER_TRANSPORT "
        "--graph other/execution_package_v2/implementation.graph.v7.yaml"
    )
    references = _graph_references(text)
    assert references == ["other/execution_package_v2/implementation.graph.v7.yaml"]
    assert not _resolves_to_enforced_graph(references[0])


@pytest.mark.parametrize(
    "flag_spelling",
    [
        "--graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml",
        "--graph=plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml",
    ],
    ids=["whitespace-form", "equals-form"],
)
def test_graph_reference_check_accepts_a_genuinely_correct_reference_in_either_spelling(flag_spelling: str) -> None:
    """Positive control: a genuinely correct reference must still pass, in
    both spellings, so the RC2-QA-001 fix did not simply reject everything."""

    text = f"python3 controller/scan_node.py --node N20_PROVIDER_TRANSPORT {flag_spelling}"
    references = _graph_references(text)
    assert len(references) == 1
    assert _resolves_to_enforced_graph(references[0])


# ------------------------------------------------- N00 schema-v2 blocker fix
#
# N00 could not actually be executed against implementation.graph.v4.yaml:
# plans/27_.../schemas/spec_approval.schema.v1.json -- the *parent* v1
# package's own frozen schema -- const-locks approved_spec to that package's
# own spec, a path this package's approved spec v4 can never equal, so
# validation failed structurally and unconditionally no matter how the
# approval record was filled in; N00_spec_approval_gate.prompt.v4.md S6 also
# claimed that schema was frozen per this package's own rules.frozen_before_entry,
# which it never was. These tests prove the fix: N00 (graph v5) binds a
# package-scoped schema v2 whose const-locked paths genuinely match this
# package's own live artifacts, contract v2 validates against it, every
# bound digest recomputes against live bytes, a mutated digest/path/model
# assignment is rejected by the real validator (not merely undocumented),
# and the old parent schema is untouched.

CONTRACT_V4_DIGEST_FIELDS = [
    "approved_spec_sha256",
    "spec_qa_verification_sha256",
    "approved_rc_manifest_sha256",
    "execution_package_qa_verification_sha256",
    "approved_graph_sha256",
]


def _schema_v4() -> dict[str, Any]:
    return json.loads(CONTRACT_SCHEMA_V4.read_text(encoding="utf-8"))


def _contract_v4() -> dict[str, Any]:
    return yaml.safe_load(CONTRACT_V4.read_text(encoding="utf-8"))


def _write_mutated_contract_v4(tmp_path: Path, mutate) -> Path:
    contract = _contract_v4()
    mutate(contract)
    mutated_path = tmp_path / "spec_approval.v4.mutated.yaml"
    mutated_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
    return mutated_path


def test_graph_v7_declares_schema_v4_frozen_not_schema_v3_v2_or_the_parent_v1_schema() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    frozen = document["rules"]["frozen_before_entry"]
    schema_v4_relative = CONTRACT_SCHEMA_V4.relative_to(REPO_ROOT).as_posix()
    schema_v3_relative = CONTRACT_SCHEMA_V3.relative_to(REPO_ROOT).as_posix()
    schema_v2_relative = CONTRACT_SCHEMA_V2.relative_to(REPO_ROOT).as_posix()
    parent_v1_relative = PARENT_APPROVAL_SCHEMA_V1.relative_to(REPO_ROOT).as_posix()
    assert schema_v4_relative in frozen
    assert schema_v3_relative not in frozen
    assert schema_v2_relative not in frozen
    assert parent_v1_relative not in frozen
    # node_result.schema.v1.json must remain -- adding schema v4 must not drop it.
    assert document["node_result_schema"] in frozen


def test_n00_prompt_v7_validates_against_schema_v4_not_schema_v3_v2_or_the_parent_v1_schema() -> None:
    """The prompt's own explanatory prose legitimately names the historical
    parent v1 schema and schemas v2/v3 (to explain the defect being fixed,
    exactly as prompt v6 named v2's stale-schema-binding defect) -- so a
    blanket "v3.json not in text" assertion would be too strict. What must
    actually be true is that the load-bearing validation instruction (TEST
    step 6) targets schema v4."""

    prompt_path = _fresh_prompt_path("N00_SPEC_APPROVAL_GATE")
    assert prompt_path.name == "N00_spec_approval_gate.prompt.v7.md"
    text = prompt_path.read_text(encoding="utf-8")
    assert (
        "Validate `execution_package_v2/contracts/spec_approval.v4.yaml` against\n"
        "   `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v4.json`"
    ) in text
    assert "Validate a new `execution_package_v2/contracts/spec_approval.v1.yaml`" not in text


def test_n00_prompt_v7_does_not_repeat_the_false_frozen_claim_about_schema_v1() -> None:
    prompt_path = _fresh_prompt_path("N00_SPEC_APPROVAL_GATE")
    text = prompt_path.read_text(encoding="utf-8")
    assert "is frozen and unversioned per" not in text


def test_schema_v4_spec_path_const_matches_graph_v7_source_spec() -> None:
    schema = _schema_v4()
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    assert schema["properties"]["approved_spec"]["const"] == document["source_spec"]


def test_schema_v4_graph_path_const_matches_this_packages_own_active_graph() -> None:
    schema = _schema_v4()
    expected = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    assert schema["properties"]["approved_graph"]["const"] == expected


def test_schema_v4_spec_path_const_resolves_to_the_live_v4_specification_file() -> None:
    schema = _schema_v4()
    spec_path = REPO_ROOT / schema["properties"]["approved_spec"]["const"]
    assert spec_path.is_file()
    assert spec_path.name == "langgraph_curriculum_factory.spec.v4.md"


def test_contract_v4_validates_against_schema_v4() -> None:
    schema = _schema_v4()
    jsonschema.Draft202012Validator.check_schema(schema)
    contract = _contract_v4()
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(contract)


@pytest.mark.parametrize("field", CONTRACT_V4_DIGEST_FIELDS)
def test_contract_v4_bound_digest_recomputes_against_live_bytes(field: str) -> None:
    contract = _contract_v4()
    rc_manifest_path = REPO_ROOT / contract["approved_rc_manifest"]
    paths_by_field = {
        "approved_spec_sha256": REPO_ROOT / contract["approved_spec"],
        "spec_qa_verification_sha256": (REPO_ROOT / contract["approved_spec"]).parent / "QA" / "verification.json",
        "approved_rc_manifest_sha256": rc_manifest_path,
        "execution_package_qa_verification_sha256": rc_manifest_path.parent / "QA" / "verification.json",
        "approved_graph_sha256": REPO_ROOT / contract["approved_graph"],
    }
    path = paths_by_field[field]
    assert path.is_file(), f"{field}: bound path does not exist: {path}"
    assert contract[field] == sha256_file(path)


def test_contract_v4_recomputed_digests_match_the_v3_contracts_original_approval() -> None:
    """Four of contract v4's five digests must be the *same* already-approved
    values from spec_approval.v3.yaml (spec, spec QA, rc3 manifest, rc3 QA)
    -- carried forward, not reinvented, and rc3 remains the approved
    package-structure snapshot even though this correction's own rc8 lineage
    is what the result-namespace collision was fixed and QA'd against. Only
    approved_graph_sha256 legitimately advances, with the v6->v7
    result-namespace correction this record itself performs."""

    contract = _contract_v4()
    assert contract["approved_spec_sha256"] == "e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c"
    assert contract["spec_qa_verification_sha256"] == "899c9720be48f071d6caf26eceafa81be626cd3bda685afa05eb0cc1dfe9a631"
    assert contract["approved_rc_manifest_sha256"] == "0e4fbfe2c258ae6176931e5490f8a2b55bdf8708d3ef0f257b50a05c9e582a6d"
    assert contract["execution_package_qa_verification_sha256"] == "202e2f214dd732ce24eb758c7cee5965cfcc113d71d03350d8bc5fefa7773217"
    assert contract["approved_rc_manifest"] == (
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc3/manifest.v1.json"
    )


def test_contract_v4_model_assignments_match_user_decision_required_01() -> None:
    assignments = _contract_v4()["model_assignments"]
    expected = {
        "M01_RESEARCH_UNIT_SOURCES": {"model": "claude-sonnet-5", "effort": "xhigh"},
        "M02_CREATE_UNIT_DOMAIN_DATA": {"model": "claude-sonnet-5", "effort": "high"},
        "M03_WRITE_UNIT_CONTENT": {"model": "claude-sonnet-5", "effort": "high"},
        "M04_CREATE_UNIT_VISUALS": {"model": "claude-sonnet-5", "effort": "high"},
        "M05_REVIEW_ACTUAL_UNIT": {"model": "gpt-5.6-sol", "effort": "xhigh"},
        "M06_REPAIR_NAMED_UNIT_ARTIFACT": {"model": "claude-sonnet-5", "effort": "xhigh"},
        "M07_REVIEW_ACTUAL_WORKBOOK": {"model": "gpt-5.6-sol", "effort": "xhigh"},
        "M08_REPAIR_NAMED_WORKBOOK_DEFECT": {"model": "claude-sonnet-5", "effort": "xhigh"},
    }
    assert assignments == expected


def test_validate_plan_v2_module_is_wired_to_schema_v4_not_schema_v3_v2_or_v1() -> None:
    assert validate_plan_v2.CONTRACT_SCHEMA_PATH == CONTRACT_SCHEMA_V4
    assert not hasattr(validate_plan_v2, "APPROVAL_SCHEMA_PATH")
    assert validate_plan_v2.GRAPH_PATH == PACKAGE_GRAPH


def test_validate_plan_v2_passes_end_to_end_against_the_live_contract() -> None:
    code, payload = run([str(VALIDATE_PLAN_V2)])
    assert code == 0, payload
    assert payload["valid"] is True


@pytest.mark.parametrize("field", CONTRACT_V4_DIGEST_FIELDS)
def test_validator_rejects_a_wrong_but_well_formed_bound_digest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, field: str) -> None:
    """JSON Schema cannot hash a file, so a syntactically well-formed but
    wrong digest passes schema-shape validation alone. The validator-level
    recompute-and-compare in validate_spec_approval_contract() must still
    reject it -- proving this is a real integrity check, not documentation."""

    wrong_digest = "0" * 64
    mutated_path = _write_mutated_contract_v4(tmp_path, lambda c: c.__setitem__(field, wrong_digest))
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(validate_plan_v2.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_validator_rejects_a_nonexistent_rc_manifest_generation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """approved_rc_manifest is deliberately not const-locked to rc3 forever
    (a future re-approval must be expressible without a schema bump), so
    schema v4's pattern alone accepts any rc<N> path shape. The validator
    must still reject a generation that does not actually exist on disk."""

    def _mutate(contract: dict[str, Any]) -> None:
        contract["approved_rc_manifest"] = (
            "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/"
            "release_candidate/rc99/manifest.v1.json"
        )

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(validate_plan_v2.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_validator_rejects_a_wrong_approved_spec_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """approved_spec IS const-locked (unlike approved_rc_manifest): a wrong
    value must fail schema validation itself, exactly the class of defect
    (a const pointed at the wrong package's spec) this whole correction
    lineage exists to fix -- proving schema v4 does not repeat it in reverse."""

    def _mutate(contract: dict[str, Any]) -> None:
        contract["approved_spec"] = "plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md"

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(jsonschema.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_validator_rejects_a_wrong_approved_graph_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A value naming graph v6 -- correct for schema v3, wrong for schema v4
    -- must still be rejected: schema v4's const genuinely moved to v7, it
    did not just widen to accept both."""

    def _mutate(contract: dict[str, Any]) -> None:
        contract["approved_graph"] = (
            "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/"
            "deprecated/implementation.graph.v6.yaml"
        )

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(jsonschema.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


@pytest.mark.parametrize(
    "job_id,wrong_assignment",
    [
        ("M01_RESEARCH_UNIT_SOURCES", {"model": "claude-sonnet-5", "effort": "high"}),
        ("M05_REVIEW_ACTUAL_UNIT", {"model": "claude-sonnet-5", "effort": "xhigh"}),
    ],
    ids=["m01-wrong-effort", "m05-wrong-family"],
)
def test_validator_rejects_a_wrong_model_assignment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, job_id: str, wrong_assignment: dict[str, str]
) -> None:
    def _mutate(contract: dict[str, Any]) -> None:
        contract["model_assignments"][job_id] = wrong_assignment

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(jsonschema.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_unmutated_contract_v4_copy_still_passes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Positive control for every mutation test above: an unmutated copy at a
    different path must still pass, so the rejections above are proving a
    real mutation was caught, not that the check always fails."""

    mutated_path = _write_mutated_contract_v4(tmp_path, lambda c: None)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    validate_plan_v2.validate_spec_approval_contract()


def test_parent_v1_approval_schema_is_byte_unchanged() -> None:
    """The parent v1 package's own frozen schema
    (plans/27_.../schemas/spec_approval.schema.v1.json) is untouched by this
    correction: it remains exclusively that package's own frozen contract,
    never edited to accommodate this package."""

    assert sha256_file(PARENT_APPROVAL_SCHEMA_V1) == (
        "829943e745cf6eb550e6319f42df4086f187a08d373f7e08f9fddf822d9fde36"
    )


def test_schema_v2_is_byte_unchanged() -> None:
    """Schema v2 is superseded, not edited: it remains, unchanged, the frozen
    contract for any record that still cites implementation.graph.v5.yaml."""

    assert sha256_file(CONTRACT_SCHEMA_V2) == (
        "d6a160aa79921c0ce0bab57504e5c36f921c7b6a5b66798786f118aec0ab6cd4"
    )


def test_contract_v2_is_byte_unchanged() -> None:
    assert sha256_file(CONTRACT_V2) == (
        "b6519442e532753fde795c892a5d386d1afa060cfa5df9dff8ad86351c0bc4c9"
    )


def test_schema_v3_is_byte_unchanged() -> None:
    """Schema v3 is superseded by RC8, not edited: it remains, unchanged, the
    frozen contract for any record that still cites
    implementation.graph.v6.yaml."""

    assert sha256_file(CONTRACT_SCHEMA_V3) == (
        "cdb71a99ea5714d59a9bf9a360217fda849548eddbd140527e1892c139f7f0c4"
    )


def test_contract_v3_is_byte_unchanged() -> None:
    assert CONTRACT_V3.is_file()
    contract = yaml.safe_load(CONTRACT_V3.read_text(encoding="utf-8"))
    assert contract["schema_version"] == 3
    assert contract["approved_graph"] == (
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml"
    )


def test_deprecated_graph_v4_is_byte_identical_to_the_originally_approved_graph() -> None:
    assert DEPRECATED_GRAPH_V4.is_file()
    assert sha256_file(DEPRECATED_GRAPH_V4) == (
        "0d5b5af8b0c60847e3b52ac93c4c10328f48a1404130a6b785485bcbbae3d571"
    )


def test_deprecated_graph_v5_is_byte_identical_to_the_rc3_rc5_approved_graph() -> None:
    """N20V2-F01: implementation.graph.v5.yaml is the graph the real N20
    execution ran against and reached a genuine BLOCKED on -- it must be
    preserved exactly, not edited to make the defect disappear."""

    assert DEPRECATED_GRAPH_V5.is_file()
    assert sha256_file(DEPRECATED_GRAPH_V5) == (
        "ce2362787a9760c9db3b2f667a0561ebd877ec89f24d690b2210ec9b6f3777b8"
    )


def test_deprecated_graph_v6_is_byte_identical_to_the_rc7_approved_graph() -> None:
    """RC8's own reason for existing: implementation.graph.v6.yaml correctly
    fixed N20V2-F01 but itself carried the result-namespace collision this
    correction fixes -- it must be preserved exactly, not edited to make the
    defect disappear."""

    assert DEPRECATED_GRAPH_V6.is_file()
    assert sha256_file(DEPRECATED_GRAPH_V6) == (
        "b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26"
    )


def test_rc3_manifest_and_qa_are_untouched_by_this_correction() -> None:
    rc3_dir = PACKAGE_DIR / "release_candidate/rc3"
    assert sha256_file(rc3_dir / "manifest.v1.json") == (
        "0e4fbfe2c258ae6176931e5490f8a2b55bdf8708d3ef0f257b50a05c9e582a6d"
    )
    assert sha256_file(rc3_dir / "QA" / "verification.json") == (
        "202e2f214dd732ce24eb758c7cee5965cfcc113d71d03350d8bc5fefa7773217"
    )


def test_rc4_manifest_and_qa_are_untouched_by_this_correction() -> None:
    """rc4 FAILED (MAX_ITERATIONS_EXHAUSTED, RC4-QA-001) and never produced a
    verification.json -- session.json and verdict.json are its QA record."""

    rc4_dir = PACKAGE_DIR / "release_candidate/rc4"
    assert sha256_file(rc4_dir / "manifest.v1.json") == (
        "dbf3fbe87f622ec34d3238164358a325ad755c083af68d8349d8803a02a09961"
    )
    assert sha256_file(rc4_dir / "QA" / "session.json") == (
        "18283d57afce6d637edb51fe6c86a022de2d5101bf5d364d08e267dab15a0e3a"
    )
    assert sha256_file(rc4_dir / "QA" / "verdict.json") == (
        "a78c9e9d4657fe48ce44301bf78870c282494328519cd8e8b7436d92a758cbd2"
    )


def test_rc5_manifest_and_qa_are_untouched_by_this_correction() -> None:
    rc5_dir = PACKAGE_DIR / "release_candidate/rc5"
    assert sha256_file(rc5_dir / "manifest.v1.json") == (
        "75e52f5c04dc67c1450791cea80a838544bb954916348a409beb64f719012722"
    )
    assert sha256_file(rc5_dir / "QA" / "verification.json") == (
        "9118efe12ca553af6e7d7d01657f7705f251d8e8bbaa13ff0f4153af109b4d05"
    )


def test_rc6_manifest_and_qa_are_untouched_by_this_correction() -> None:
    """rc6 FAILED (RC6-QA-001, RC6-QA-002) and never produced a
    verification.json -- session.json and verdict.json are its QA record."""

    rc6_dir = PACKAGE_DIR / "release_candidate/rc6"
    assert sha256_file(rc6_dir / "manifest.v1.json") == (
        "aae9a059a35b3a387ea5e216eb52cbada551c2119a252e15851677eedb0234b8"
    )
    assert sha256_file(rc6_dir / "QA" / "session.json") == (
        "9db0705fdfad8dcabca483fd310b5dbabfb27159b032c3ecb3e568a7f7322232"
    )
    assert sha256_file(rc6_dir / "QA" / "verdict.json") == (
        "a861172224cbfdb84c265ef708f6d304c89b49c2f00e78a60487b36e52687440"
    )


def test_rc7_manifest_and_qa_are_untouched_by_this_correction() -> None:
    """rc7 reached QA_PASSED and is the immediate predecessor RC8 exists to
    correct (the result-namespace collision was found in independent
    verification of rc7's own approved graph, not by rc7's QA session
    itself, which correctly scoped its review to rc6's two findings)."""

    rc7_dir = PACKAGE_DIR / "release_candidate/rc7"
    assert sha256_file(rc7_dir / "manifest.v1.json") == (
        "a6512de76b7e36b3e5548620b22df222a231a4bf00edf35bacec61d999a50d2d"
    )
    assert sha256_file(rc7_dir / "QA" / "verification.json") == (
        "22a89ca64f3db385fd1d8f20f310eb880a6ec2265894924ff78a4a0cbb415901"
    )


def test_spec_approval_v1_contract_is_untouched() -> None:
    v1_contract_path = PACKAGE_DIR / "contracts/spec_approval.v1.yaml"
    contract = yaml.safe_load(v1_contract_path.read_text(encoding="utf-8"))
    assert contract["schema_version"] == 1


def test_spec_approval_v2_contract_is_untouched() -> None:
    contract = yaml.safe_load(CONTRACT_V2.read_text(encoding="utf-8"))
    assert contract["schema_version"] == 2
    assert contract["approved_graph"] == (
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v5.yaml"
    )


# --------------------------------------------------------- RC8: result-
# namespace collision / preservation proofs
#
# implementation.graph.v6.yaml correctly fixed N20V2-F01 (the scan-scope
# defect) but its own result_pattern was byte-identical to
# implementation.graph.v5.yaml's own. N00 and N10 are already ADMITTED
# (PASSED) and N20 is already BLOCKED, all three with real results at
# execution_package_v2/results/{node_id}.result.v1.json -- a fresh execution
# of any of them under graph v6 as originally built would have silently
# overwritten those exact files. implementation.graph.v7.yaml fixes this by
# moving result_pattern (and every node's own result/evidence write paths)
# to the versioned subdirectory execution_package_v2/results/v7/, whose
# per-node filenames never coincide with the flat per-node files directly
# under execution_package_v2/results/. These tests prove the collision
# cannot recur and that the historical records are untouched.

ADMITTED_OR_BLOCKED_RESULT_FILES = [
    "N00_SPEC_APPROVAL_GATE.result.v1.json",
    "N10_HARNESS_PROTOCOL.result.v1.json",
    "N20_PROVIDER_TRANSPORT.result.v1.json",
]

# Recorded once, by hand, from the live files at the start of RC8's own work
# (before any RC8 file was written) -- these are the exact bytes N00/N10 were
# ADMITTED under and N20 was BLOCKED under, and must never change.
ADMITTED_OR_BLOCKED_RESULT_HASHES = {
    "N00_SPEC_APPROVAL_GATE.result.v1.json": "1592643a4d48b011bf5338b77fa949887da960e086ff081907bddd510f65cda6",
    "N10_HARNESS_PROTOCOL.result.v1.json": "a3b678c49c62254517d847b60537e7ed5372b29d81db458f13aadae4ecce7c70",
    "N20_PROVIDER_TRANSPORT.result.v1.json": "894e430aa1c5739d0af638fec10e91f2eaf32f090a917213b1bf7fa2ce5e609a",
}


@pytest.mark.parametrize("filename", ADMITTED_OR_BLOCKED_RESULT_FILES)
def test_admitted_or_blocked_result_file_is_byte_unchanged(filename: str) -> None:
    path = PACKAGE_DIR / "results" / filename
    assert path.is_file()
    assert sha256_file(path) == ADMITTED_OR_BLOCKED_RESULT_HASHES[filename]


def test_graph_v7_result_pattern_never_collides_with_the_legacy_results_root() -> None:
    """The direct proof that the RC8 defect is fixed: graph v7's own
    result_pattern, formatted for every admitted/blocked node, never equals
    the exact legacy path those nodes' real results live at. results/v7/ is
    legitimately a subdirectory of results/ (that is not the defect -- the
    defect was reusing the exact same flat filename), so the proof is exact
    per-node path inequality, not path-prefix disjointness."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    pattern = document["result_pattern"]
    assert pattern.startswith(RESULTS_V7_PREFIX)
    for filename in ADMITTED_OR_BLOCKED_RESULT_FILES:
        node_id = filename.rsplit(".result.v1.json", 1)[0]
        v7_path = pattern.format(node_id=node_id)
        legacy_path = f"{LEGACY_RESULTS_PREFIX}{filename}"
        assert v7_path != legacy_path
        assert (REPO_ROOT / v7_path).resolve() != (REPO_ROOT / legacy_path).resolve()


@pytest.mark.parametrize("node_id", ["N00_SPEC_APPROVAL_GATE", "N10_HARNESS_PROTOCOL", "N20_PROVIDER_TRANSPORT"])
def test_validate_result_v2_reports_missing_not_a_collision_for_admitted_nodes(node_id: str) -> None:
    """The live validator (bound to graph v7's own results/v7/ root) must
    honestly report the v7 result as missing for these three already-admitted
    nodes -- never fabricate a pass by reading the legacy v5-lineage file at
    the old path, and never raise from an accidental write. This is the
    behavioral proof that no code path in this validator can be tricked into
    treating the legacy file as this generation's own result."""

    code, payload = run([str(VALIDATE_RESULT_V2), "--node", node_id])
    assert code == 1
    assert payload["valid"] is False
    assert "missing result" in payload["error"]
    assert "results/v7" in payload["error"]


def test_graph_v7_is_otherwise_unchanged_in_substance_from_graph_v6() -> None:
    """RC8 must not regress rc7's N20V2-F01 fix: every node's write set
    (beyond the result/evidence path prefix, which is exactly what RC8
    changes), every edge, every scan rule, and retired_provider_test_scan's
    scan_roots must be byte-identical in substance between v6 and v7."""

    v6 = yaml.safe_load(DEPRECATED_GRAPH_V6.read_text(encoding="utf-8"))
    v7 = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))

    assert v6["edges"] == v7["edges"]
    assert v6["terminals"] == v7["terminals"]
    assert v6["rules"]["forbidden_production_scan"] == v7["rules"]["forbidden_production_scan"]
    assert v6["rules"]["retired_provider_test_scan"] == v7["rules"]["retired_provider_test_scan"]

    for node_id, v6_node in v6["nodes"].items():
        v7_node = v7["nodes"][node_id]
        assert v6_node["depends_on"] == v7_node["depends_on"]
        assert v6_node.get("read_only_inputs", []) == v7_node.get("read_only_inputs", [])
        assert v6_node["allowed_results"] == v7_node["allowed_results"]

        def _non_result_writes(writes: list[str]) -> set[str]:
            return {w for w in writes if "/results/" not in w}

        assert _non_result_writes(v6_node["writes"]) == _non_result_writes(v7_node["writes"])


def test_graph_v7_result_writes_are_the_exact_v6_writes_moved_under_results_v7() -> None:
    v6 = yaml.safe_load(DEPRECATED_GRAPH_V6.read_text(encoding="utf-8"))
    v7 = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    for node_id, v6_node in v6["nodes"].items():
        v7_node = v7["nodes"][node_id]
        v6_results = {w for w in v6_node["writes"] if "/results/" in w}
        v7_results = {w for w in v7_node["writes"] if "/results/" in w}
        expected_v7 = {w.replace(LEGACY_RESULTS_PREFIX, RESULTS_V7_PREFIX) for w in v6_results}
        assert v7_results == expected_v7


# --------------------------------------------- N20V2-F01: scan-scope narrowing
#
# The real N20 execution against implementation.graph.v5.yaml reached a
# genuine BLOCKED (finding N20V2-F01):
# rules.retired_provider_test_scan.scan_roots was ['tests/runtime'], walked
# recursively, and caught 16 occurrences of "gemini" in exactly two files --
# tests/runtime/test_gemini.py and tests/runtime/test_capabilities.py -- that
# test a wholly separate, still-active Plan 11/19/20/21 Gemini pipeline this
# migration does not own. implementation.graph.v6.yaml fixes this by making
# scan_roots an explicit, exact list of every migration-owned active test
# file across N20-N60, instead of a directory to walk. These tests prove the
# fix against the real repository and real graph, not a synthetic fixture --
# scan_node.py's own scanning logic is unmodified (checked at the top of this
# file); only the graph's configured scan_roots value changed.

GEMINI_TEST = "tests/runtime/test_gemini.py"
CAPABILITIES_TEST = "tests/runtime/test_capabilities.py"

MIGRATION_OWNED_TEST_FILES_BY_NODE = {
    "N20_PROVIDER_TRANSPORT": [
        "tests/runtime/test_plan26_transport.py",
        "tests/runtime/test_plan26_model_nodes.py",
        "tests/runtime/test_plan26_egress.py",
        "tests/runtime/test_curriculum_factory_graph.py",
        "tests/runtime/test_plan26_adversarial.py",
        "tests/runtime/test_plan26_api_contract.py",
        "tests/runtime/test_plan26_lock_drift.py",
    ],
    "N30_PREFLIGHT_EGRESS": [
        "tests/runtime/test_plan26_cli.py",
        "tests/runtime/test_plan26_deterministic_nodes.py",
        "tests/runtime/test_run_curriculum.py",
    ],
    "N40_INTEGRATION_OWNERSHIP": [
        "tests/runtime/test_plan26_topology.py",
        "tests/runtime/test_plan26_unit_graph.py",
        "tests/runtime/test_plan26_repair_acceptance.py",
        "tests/runtime/test_plan26_workbook.py",
    ],
    "N50_EVIDENCE_AUDIT_CONTROLS": [
        "tests/runtime/test_plan26_evidence.py",
        "tests/runtime/test_plan26_persistence.py",
    ],
    "N60_ADVERSARIAL_REGRESSION": [
        "tests/runtime/test_plan27_adversarial.py",
    ],
}


def test_n20_write_set_no_longer_owns_the_unrelated_gemini_pipeline_tests() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    writes = document["nodes"]["N20_PROVIDER_TRANSPORT"]["writes"]
    assert GEMINI_TEST not in writes
    assert CAPABILITIES_TEST not in writes


def test_no_node_in_the_graph_owns_the_unrelated_gemini_pipeline_tests() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    for node_id, node in document["nodes"].items():
        writes = node.get("writes", [])
        assert GEMINI_TEST not in writes, f"{node_id} unexpectedly owns {GEMINI_TEST}"
        assert CAPABILITIES_TEST not in writes, f"{node_id} unexpectedly owns {CAPABILITIES_TEST}"


def test_retired_provider_test_scan_scan_roots_is_the_explicit_migration_owned_union() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_roots = document["rules"]["retired_provider_test_scan"]["scan_roots"]
    expected = sorted(
        path for paths in MIGRATION_OWNED_TEST_FILES_BY_NODE.values() for path in paths
    )
    assert sorted(scan_roots) == expected
    assert GEMINI_TEST not in scan_roots
    assert CAPABILITIES_TEST not in scan_roots


def test_scan_roots_are_directory_free_explicit_file_paths() -> None:
    """N20V2-F01's root cause was scan_roots naming a directory
    (tests/runtime) walked recursively. Prove every entry is a .py file path,
    never a directory."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    scan_roots = document["rules"]["retired_provider_test_scan"]["scan_roots"]
    for root in scan_roots:
        assert root.endswith(".py"), root
        assert not (REPO_ROOT / root).is_dir(), root


@pytest.mark.parametrize("node_id", sorted(MIGRATION_OWNED_TEST_FILES_BY_NODE))
def test_node_scoped_scan_covers_exactly_its_own_migration_owned_test_files(node_id: str) -> None:
    """Real repo, real graph v6: node-scoped mode must scan exactly this
    node's own migration-owned test files (or, for N60's future file, none
    yet on disk) -- never the unrelated Gemini-pipeline tests, never another
    node's files."""

    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_node(graph, node_id)
    tests_scope = next(scope for scope in report["scopes"] if scope["scope"] == "tests")
    expected = {
        path for path in MIGRATION_OWNED_TEST_FILES_BY_NODE[node_id] if (REPO_ROOT / path).is_file()
    }
    assert set(tests_scope["scanned_files"]) == expected
    assert GEMINI_TEST not in tests_scope["scanned_files"]
    assert CAPABILITIES_TEST not in tests_scope["scanned_files"]


def test_n20_real_node_scoped_scan_is_the_regression_proof_that_n20v2_f01_is_fixed() -> None:
    """PKGV2-T22(a): the whole point of graph v6 is that N20's real
    node-scoped command -- which reached a genuine BLOCKED with 16 violations
    under graph v5 -- now passes cleanly. N30/N40/N50 legitimately still
    surface pre-existing, unrelated 'gemini'/'google' occurrences in their own
    test assertions (proven separately by
    test_complete_tree_mode_against_the_real_repo_reports_the_known_pre_remediation_debt),
    so only N20 -- the node this recovery cycle actually corrects -- is
    asserted zero-violations here; asserting it for every node would be
    false."""

    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_node(graph, "N20_PROVIDER_TRANSPORT")
    assert report["valid"] is True
    assert report["violations"] == []
    for scope in report["scopes"]:
        assert scope["violations"] == []


def test_complete_tree_mode_never_scans_the_unrelated_gemini_pipeline_tests() -> None:
    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_complete_tree(graph)
    tests_scope = next(scope for scope in report["scopes"] if scope["scope"] == "tests")
    assert GEMINI_TEST not in tests_scope["scanned_files"]
    assert CAPABILITIES_TEST not in tests_scope["scanned_files"]
    # N60's own future file does not exist yet -- scanning silently omits it
    # rather than erroring, and every other entry that does exist is covered.
    expected = {
        path
        for paths in MIGRATION_OWNED_TEST_FILES_BY_NODE.values()
        for path in paths
        if (REPO_ROOT / path).is_file()
    }
    assert set(tests_scope["scanned_files"]) == expected


def test_missing_future_n60_test_file_causes_no_scan_error_in_either_mode() -> None:
    """tests/runtime/test_plan27_adversarial.py does not exist until N60
    creates it. Its presence in scan_roots must not error out N20-N50's
    node-scoped scans, nor the current complete-tree scan."""

    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    future_file = REPO_ROOT / "tests/runtime/test_plan27_adversarial.py"
    assert not future_file.is_file(), "test assumes N60 has not run yet in this checkout"
    for node_id in MIGRATION_OWNED_TEST_FILES_BY_NODE:
        scanner.run_node(graph, node_id)  # must not raise
    scanner.run_complete_tree(graph)  # must not raise


@pytest.mark.parametrize(
    "node_id,relative_path",
    [
        ("N20_PROVIDER_TRANSPORT", "tests/runtime/test_plan26_transport.py"),
        ("N30_PREFLIGHT_EGRESS", "tests/runtime/test_plan26_cli.py"),
        ("N40_INTEGRATION_OWNERSHIP", "tests/runtime/test_plan26_topology.py"),
        ("N50_EVIDENCE_AUDIT_CONTROLS", "tests/runtime/test_plan26_evidence.py"),
    ],
)
def test_seeded_violation_in_a_migration_owned_file_is_caught_by_its_node_scoped_scan(
    node_id: str, relative_path: str
) -> None:
    target = REPO_ROOT / relative_path
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "\n# gemini\n", encoding="utf-8")
        graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
        report = scanner.run_node(graph, node_id)
        assert not report["valid"]
        assert any(item["path"] == relative_path for item in report["violations"])
    finally:
        target.write_text(original, encoding="utf-8")


@pytest.mark.parametrize(
    "relative_path",
    [
        "tests/runtime/test_plan26_transport.py",
        "tests/runtime/test_plan26_cli.py",
        "tests/runtime/test_plan26_topology.py",
        "tests/runtime/test_plan26_evidence.py",
    ],
)
def test_seeded_violation_in_a_migration_owned_file_is_caught_by_complete_tree_scan(relative_path: str) -> None:
    target = REPO_ROOT / relative_path
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "\n# gemini\n", encoding="utf-8")
        graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
        report = scanner.run_complete_tree(graph)
        assert not report["valid"]
        assert any(item["path"] == relative_path for item in report["violations"])
    finally:
        target.write_text(original, encoding="utf-8")


@pytest.mark.parametrize("relative_path", [GEMINI_TEST, CAPABILITIES_TEST])
def test_seeded_violation_in_the_unrelated_gemini_pipeline_tests_is_never_caught(relative_path: str) -> None:
    """Positive proof of the exemption, not merely an absence: a seeded
    violation in test_gemini.py/test_capabilities.py must not fail either
    scan mode, because these files are genuinely outside scan_roots -- not
    merely clean by coincidence today."""

    target = REPO_ROOT / relative_path
    original = target.read_text(encoding="utf-8")
    try:
        target.write_text(original + "\n# freshly seeded gemini violation\n", encoding="utf-8")
        graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
        complete_tree_report = scanner.run_complete_tree(graph)
        assert not any(item["path"] == relative_path for item in complete_tree_report["violations"])
        node_report = scanner.run_node(graph, "N20_PROVIDER_TRANSPORT")
        assert not any(item["path"] == relative_path for item in node_report["violations"])
    finally:
        target.write_text(original, encoding="utf-8")
```

SHA-256: `99bcd9024aa349c35d50bfb9a9f23a61f3a74a48d14ad63d458298bb9b8abb22` (88533 bytes)

---

## `prompts/N00_spec_approval_gate.prompt.v7.md`

N00 gate prompt. Mechanical rename of prompt v6: validates against schema v4 / contract v4 instead of v3, requires implementation.graph.v7.yaml to exist, and its preservation list (TEST step 10) grows to include implementation.graph.v6.yaml, spec_approval.schema.v3.json, spec_approval.v3.yaml, N00_spec_approval_gate.prompt.v6.md, and rc6/rc7. No substantive TEST requirement changed.

```markdown
# GOAL

Prove that execution package v2 has one corrected, independently verified,
explicitly user-approved specification authority before any implementation
begins. This is package v2's counterpart of
`plans/27_langgraph_curriculum_factory_remediation/prompts/N00_spec_approval_gate.prompt.v1.md`,
which gated the v1 attempt through its `BLOCKED` `N20_PROVIDER_TRANSPORT`
result, and of
`plans/27_langgraph_curriculum_factory_remediation/prompts/N00_spec_approval_gate.prompt.v2.md`,
which gated the first, failed execution-package correction
(`implementation.graph.v2.yaml`, preserved immutable together with its QA
session and `PKG-QA-001` finding). Those v1 and v2 results and evidence
remain untouched, immutable, and readable as historical record — this node
does not supersede them in place, it gates a new, independent package.

This v7 prompt corrects `N00_spec_approval_gate.prompt.v6.md`, which was
itself a correct fix for N20V2-F01 (its own graph, `implementation.graph.v6.yaml`,
genuinely narrowed `retired_provider_test_scan.scan_roots` to the explicit
migration-owned union and dropped the two unrelated Gemini-pipeline test
files from N20's write set) but whose own graph carried an unrelated,
independently-found result-namespace defect: `implementation.graph.v6.yaml`'s
`result_pattern` was byte-identical to `implementation.graph.v5.yaml`'s own
(`execution_package_v2/results/{node_id}.result.v1.json`). Because N00 and
N10 are already ADMITTED (`PASSED`) with real results at
`execution_package_v2/results/N00_SPEC_APPROVAL_GATE.result.v1.json` and
`execution_package_v2/results/N10_HARNESS_PROTOCOL.result.v1.json`, and N20 is
already `BLOCKED` with real evidence at
`execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json`, a fresh
execution of any of these three nodes under graph v6 as originally built
would have validated against v6's own newer prompt/schema hashes and then
silently overwritten those exact same three historical files at their shared
path — violating this recovery lineage's repeated, explicit "preserve prior
attempts, never overwrite an admitted or blocked record" requirement. This is
a mechanical result-namespace engineering defect in the graph's own
`result_pattern` and every node's own result/evidence write paths, not a
specification or provider decision, and not a defect in N20's real,
independently-verified production implementation (preserved untouched). It is
fixed here: this prompt validates against this package's own package-scoped
`execution_package_v2/schemas/spec_approval.schema.v4.json` (which
const-locks the right specification and this package's own active graph, now
`implementation.graph.v7.yaml`, instead of v6), the corresponding
`execution_package_v2/contracts/spec_approval.v4.yaml` (which carries
forward, not reinvents, the exact approval already recorded in
`spec_approval.v3.yaml`, updated only for the new graph's path/digest and
schema version), and `implementation.graph.v7.yaml` genuinely declares schema
v4 in its own `rules.frozen_before_entry`, moves `result_pattern` and every
node's own result/evidence write paths under the versioned subdirectory
`execution_package_v2/results/v7/` (whose per-node filenames never coincide
with the flat per-node files directly under `execution_package_v2/results/`,
where the admitted/blocked N00/N10/N20 records permanently live), and
otherwise carries the N20V2-F01 scan-scope fix forward unchanged. The v6 prompt file, `spec_approval.schema.v3.json`,
`spec_approval.v3.yaml`, and `implementation.graph.v6.yaml` (preserved at
`deprecated/implementation.graph.v6.yaml`) are preserved unchanged as
historical record — this node does not reopen, edit, or supersede any of
them, `implementation.graph.v5.yaml` (at `deprecated/`), `spec_approval.schema.v2.json`,
`spec_approval.v2.yaml`, `N00_spec_approval_gate.prompt.v5.md`, or rc1-rc7
in place.

This node is a gate, not a specification-writing or graph-writing task. Do
not create, edit, approve, or repair the v4 specification artifact, this
package's own graph, QA evidence, an approval record, runtime, tests,
policy, or any Plan 26/Run 27 v1 or failed-v2 historical artifact. Its only
authorized writes are its own result and evidence directory under
`execution_package_v2/results/v7/`.

# TEST

1. Hash Plan 26 v1
   (`44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`) and
   v2 (`99052a181052bbbaf8077a152af22db6f248d552f38dd73302a3c34abc11b758`)
   and require both to still match; neither is edited by this or any prior
   correction task.
2. Require the specification artifact
   `plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md`
   (sha256 `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`
   — physically named `.v4.md` by the QA gate's own round-lineage numbering
   after a round-1 fix; the document is specification v3 and its own header
   says so) to exist and to correct v2 at the exact hash above, not v1.
3. Read that specification's own independent QA session
   (`plans/26_langgraph_curriculum_factory/spec/v3/QA/`, session
   `019ffbeb-3f45-7440-a83e-aa560938dc98`). Require witnessed,
   hash-chain-valid `QA_PASSED` by re-running the QA gate's own `verify`
   command read-only; prose asserting that QA ran is not evidence.
4. Require the approved release candidate's own QA result
   (`execution_package_v2/release_candidate/rc3/QA/`) to exist with the same
   witnessed, hash-chain-valid `QA_PASSED` discipline, verified the same way.
5. Require `execution_package_v2/implementation.graph.v7.yaml` to exist, to
   declare `version: 2`, to validate via
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`,
   and to declare `source_spec` as the specification path above.
6. Validate `execution_package_v2/contracts/spec_approval.v4.yaml` against
   `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v4.json`
   with format checking enabled. This schema is *this package's own* frozen
   schema: it is declared in `implementation.graph.v7.yaml`'s own
   `rules.frozen_before_entry` (alongside `node_result.schema.v1.json`) —
   verify that declaration directly in the live graph file rather than
   trusting this prompt's own account of it. It is not the parent v1
   package's `spec_approval.schema.v1.json`, which remains that package's
   own frozen contract, exclusively, and is never loaded here.
7. Recompute digests and require exact equality across every value schema v4
   requires as a structured field, against live repository bytes: the
   specification file (`approved_spec_sha256`), its QA verification artifact
   hash (`spec_qa_verification_sha256`), the approved release candidate's
   manifest at the path `approved_rc_manifest` names
   (`approved_rc_manifest_sha256`), that release candidate's own QA
   verification artifact hash (`execution_package_qa_verification_sha256`),
   and this package's graph file at the path `approved_graph` names
   (`approved_graph_sha256`). A mismatch on any one of these is not a schema
   *shape* failure (JSON Schema cannot hash a file) — it is a validator-level
   integrity failure and must block exactly as a shape failure would.
8. Require the approval record's `approved_for` to equal
   `plan27_implementation_remediation` and its `model_assignments` to carry
   the exact Claude/Codex model and effort decision already supplied by the
   user for `USER_DECISION_REQUIRED-01`, unchanged from
   `plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v1.yaml`'s
   `approval_statement`: `M01_RESEARCH_UNIT_SOURCES`,
   `M06_REPAIR_NAMED_UNIT_ARTIFACT`, and `M08_REPAIR_NAMED_WORKBOOK_DEFECT` =
   `claude-sonnet-5` at effort `xhigh`; `M02_CREATE_UNIT_DOMAIN_DATA`,
   `M03_WRITE_UNIT_CONTENT`, and `M04_CREATE_UNIT_VISUALS` = `claude-sonnet-5`
   at effort `high`; `M05_REVIEW_ACTUAL_UNIT` and `M07_REVIEW_ACTUAL_WORKBOOK`
   = `gpt-5.6-sol` at effort `xhigh`.
9. Enumerate every `USER_DECISION_REQUIRED` item in the specification. If
   any affects a node's intended implementation and lacks a separately
   recorded answer, block.
10. Prove no Run 27 v1 result, evidence file, receipt, patch, log, the v1
    execution graph, the failed `implementation.graph.v2.yaml` and its QA
    session, `implementation.graph.v5.yaml` (now preserved at
    `deprecated/implementation.graph.v5.yaml`), `implementation.graph.v6.yaml`
    (now preserved at `deprecated/implementation.graph.v6.yaml`),
    `spec_approval.schema.v1.json`, `spec_approval.v1.yaml`,
    `spec_approval.schema.v2.json`, `spec_approval.v2.yaml`,
    `spec_approval.schema.v3.json`, `spec_approval.v3.yaml`,
    `N00_spec_approval_gate.prompt.v5.md`, `N00_spec_approval_gate.prompt.v6.md`,
    rc1, rc2, rc3, rc4, rc5, rc6, rc7 (including each one's `QA/` session),
    `N20_PROVIDER_TRANSPORT`'s `BLOCKED` result and evidence under
    `implementation.graph.v5.yaml`, runtime, test, policy, or model-job file
    was changed by this node.
11. Record command output and hashes under
    `execution_package_v2/results/v7/evidence/N00_SPEC_APPROVAL_GATE/` and
    emit a JSON result conforming to
    `plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json`.

The only success outcome is `PASSED`. Missing, inconsistent, unverifiable, or
unapproved inputs produce `BLOCKED_SPEC_NOT_APPROVED`. An integrity or tool
defect produces `BLOCKED`.

# LOOP

Do not repair a failed approval gate. Re-run read-only checks once to rule
out a transient read error. If the same condition remains, write the honest
result and stop the graph. Never infer user approval from the existence of
this package's scaffold, from a prior agent's report of passing digests, or
from a request to prepare this package — approval binds the exact digests
recorded in the approval record, supplied by the user after seeing them, not
before.
```

SHA-256: `7b7a6b31d0966f484f24711f2f549f1e2044dd422643c007dbc9d62584b541ad` (9992 bytes)

---

## `prompts/N20_provider_transport.prompt.v7.md`

N20 implementation prompt. Mechanical rename of prompt v6: its own --graph values now name implementation.graph.v7.yaml. N20's write set, the two egress paths, and the N20V2-F01 scan-scope fix are unchanged in substance from v6 -- only the graph-level result/evidence path this node's own writes entries point at moved (already reflected in graph v7 itself).

```markdown
# GOAL

Implement the corrected specification's (v4 artifact, specification v3 by
its own header) complete provider-role and transport profile across all
eight production model jobs, using the exact mechanics that specification
proves live against the installed CLIs: an inline CLI-schema projection
(never a schema file path), stdin delivery of the canonical authorized-input
projection (never a staged-file read, since `--tools ""` leaves no read
tool), `--output-format stream-json --verbose` per-turn identity extraction
(never the aggregate `modelUsage` map), and an observed tool/MCP-closure
proof from the initialization event (never inferred from
`--tools`/`--setting-sources` alone).

This is execution package v2's counterpart of
`plans/27_langgraph_curriculum_factory_remediation/prompts/N20_provider_transport.prompt.v1.md`,
which reached `BLOCKED` (findings N20-F01 through N20-F09,
`plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json`).
That v1 attempt's result and evidence are historical and untouched. This
prompt exists because the v1 attempt's blocking findings required both a
specification correction (now the v4 artifact, §7) and an execution-package
correction: N20-F02 found that the frozen `anthropic`/`openai` authorization
classes require **this graph to move `runtime/langgraph_factory/egress.py`
and `tests/runtime/test_plan26_egress.py` into N20's write set**; N20-F01
found the bare whole-tree forbidden-reference scan unsatisfiable for any
node before the last one to touch a migration-affected test, so **this
node's verification uses this package's own node-scoped scanner,
`execution_package_v2/controller/scan_node.py --node N20_PROVIDER_TRANSPORT
--graph execution_package_v2/implementation.graph.v7.yaml`**, explicitly
bound to this package's own graph (never the parent v1 package's graph, and
never omitting `--graph`, which is exactly the defect an independent QA
round found in this package's own predecessor attempt,
`implementation.graph.v2.yaml`'s `PKG-QA-001` finding) — instead of the bare
whole-tree form N60 alone still runs.

This v7 prompt corrects `N20_provider_transport.prompt.v6.md`. That v6
prompt's own N20 execution was real and produced correct, independently
verified production code (`transport.py`, `egress.py`, `model_nodes.py`,
`config/model_jobs.v1.yaml`, `policy/routes.v1.yaml`,
`policy/routing/model_registry.v1.yaml`, and their schemas — none of it is
touched by this correction), and its graph, `implementation.graph.v6.yaml`,
correctly fixed N20V2-F01 (the write-set/scan-scope defect that swept two
unrelated Gemini-pipeline test files). But `implementation.graph.v6.yaml`
itself carried an independently-found result-namespace defect: its
`result_pattern` was byte-identical to `implementation.graph.v5.yaml`'s own,
so a fresh N20 execution under it would validate against v6's own newer
prompt/schema hash and then silently overwrite N20's own already-`BLOCKED`
result and evidence at their shared path. `implementation.graph.v7.yaml`
fixes this at the graph level: `result_pattern`, and every node's own
result-write and evidence-root entries in `writes` — including N20's own —
move under `execution_package_v2/results/v7/` instead of
`execution_package_v2/results/`. This node's own write set below already
reflects that move. N20's write set, the two egress paths, and the
N20V2-F01 scan-scope fix (`retired_provider_test_scan.scan_roots` as the
explicit migration-owned union) are otherwise unchanged in substance from
v6. This prompt's own `--graph` values now name
`implementation.graph.v7.yaml` instead of `implementation.graph.v6.yaml`,
the same rename `implementation.graph.v7.yaml`'s own header applies to the
graph file itself, so this prompt does not go stale relative to the graph it
instructs `N20_PROVIDER_TRANSPORT` to scan against. The v3 through v6 files
are all preserved unchanged as historical record, as is
`implementation.graph.v6.yaml` itself (now at
`deprecated/implementation.graph.v6.yaml`) and `N20_PROVIDER_TRANSPORT`'s
own `BLOCKED` result and evidence under `implementation.graph.v5.yaml`.

The corrected specification is the authority. Do not perform a blind
Gemini-to-Codex string replacement and do not preserve Codex as generator if
the specification assigns generation and repair to Claude/Anthropic. The
specification-review QA plugin is not automatically the production
transport.

# TEST

1. Build a table from the specification for M01–M08 containing role,
   mutability, provider family, subscription driver, input boundary, output
   schema, identity claim, and failure disposition. Fail before editing if
   any field is unresolved.
2. Update transport, configuration, prompts, schemas, model nodes, policy,
   and direct tests consistently with that table.
3. Implement the four corrected Claude transport mechanics as distinct,
   independently testable units in `transport.py`:
   a. a deterministic CLI-schema projection builder that strips `$schema`
      and rejects (never silently drops) an external `$ref`, computed once
      per canonical schema and proven byte-identical across repeated
      builds;
   b. stdin delivery of the JSON-encoded
      `{instruction, authorized_input_projection}` document to the
      `claude --print` subprocess, with no positional instruction argument
      and no reliance on the worker reading `authorized_input.json` from
      `--add-dir`;
   c. executed-identity extraction from
      `--output-format stream-json --verbose` per-turn assistant events'
      `message.model` (`parent_tool_use_id` null), never from the final
      envelope's `modelUsage` map; and
   d. a D03 capability check that inspects the stream-json initialization
      event's tool and MCP-server lists directly and fails closed if any
      tool other than structured output, or any authenticated/invokable
      MCP-server tool, is present — independent of what
      `--tools`/`--setting-sources` claim.
4. Move `egress.py`'s provider allowlist and `PROVIDER_DATA_CLASSES` to the
   `anthropic`/`openai`/`primary_source_hosts` classes the specification
   requires, dropping the retired third-party class and its model-API hosts
   entirely. Update `internal_authorization_receipt.schema.json`'s provider
   enum in the same atomic step so no transport test can construct an
   authorization record `egress.py` would then reject. Update
   `tests/runtime/test_plan26_egress.py` to prove the new allowlist and to
   prove the dropped class is actually unreachable, not merely renamed.
5. Mechanically search production code/config/policy for the retired
   provider's commands, models, credentials, authorization, transmission,
   endpoints, and fallback, using
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py --node N20_PROVIDER_TRANSPORT --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml`
   — the node-scoped scan proves N20's own write set clean without
   depending on N30–N50's not-yet-migrated files, and its explicit `--graph`
   binding proves it is reading this package's corrected write sets, not
   the parent v1 package's. Historical fixtures outside this node's write
   set may remain until their owning node retires them; do not widen this
   node's write set to reach them.
6. Prove no billed API-key environment variable, provider SDK, direct HTTP
   model call, or custom endpoint can activate a production model route.
7. Prove generating/mutating jobs use Claude/Anthropic and independent
   judgment jobs use Codex/OpenAI, with a different-family final judge.
8. Prove every job validates staged inputs before transmission and
   validates its schema-bound output — using the unmodified canonical
   schema, not the CLI-schema projection — before admission.
9. Prove missing, failed, or identity-mismatched drivers fail closed
   without reassignment or fallback.
10. Record requested versus observed identity honestly. Do not claim
    executed model identity or subscription entitlement beyond what the
    driver exposes.
11. Run focused transport, authorization, egress, model-node, and policy
    tests.
12. Emit the schema-valid node result and an eight-job conformance report.

N20 owns the exact transport/model/config/prompt/schema, route/registry,
egress/authorization, and test paths declared in this graph — a superset of
v1's N20 write set, extended by exactly the two egress paths named above.
Preflight orchestration, the production CLI, topology/integration,
evidence, and their other tests belong to later nodes. Route a defect there
rather than widening this node's write set further.

N20 also owns retirement or complete correction of every predecessor test
file named in its write set. No active test may name, import, invoke,
probe, configure, simulate, authorize, or expect the retired provider path.
Delete a test file when its entire subject is retired; rewrite only
genuinely provider-neutral product assertions against the approved
production architecture.

# LOOP

On a failure, identify whether the owner is the job contract, driver,
egress allowlist, staged boundary, output schema, identity receipt, or
policy/config call site. Repair that owner and every affected direct test
in the same attempt. Rerun all N20 tests because an eight-job mapping and
the egress/authorization boundary are each atomic. Stop with `BLOCKED`
rather than inventing an unapproved production transport detail.
```

SHA-256: `29ecc1d83bee06c8c929c71588fba51859bdd8e6ced4e9540a99b5cfc8873f87` (9568 bytes)

---

## `prompts/N30_preflight_egress.prompt.v7.md`

N30 preflight/CLI prompt. Mechanical gate-lineage rename only: its own --graph value now names implementation.graph.v7.yaml. N30's own scope is unaffected by the RC8 result-namespace fix, which touched every node uniformly at the graph level.

```markdown
# GOAL

Make preflight, authentication, authorization, and the production CLI
truthful for the approved subscription-only production drivers, consuming
the `anthropic`/`openai`/`primary_source_hosts` egress boundary N20 now owns
and proves (moved from N30's v1 write set to N20's, per this package's
correction of N20-F02 — see `N20_provider_transport.prompt.v7.md`). Correct
the exact Run 26 false-ready condition before any curriculum content can be
transmitted, and prove the D03 tool/MCP-closure check the specification
requires.

This is execution package v2's counterpart of
`plans/27_langgraph_curriculum_factory_remediation/prompts/N30_preflight_egress.prompt.v1.md`.
That v1 prompt claimed N30 "owns only `egress.py`, the D03 input/capability
node, the production CLI, and the four exact tests declared in the graph" —
**this is no longer true.** `egress.py` and its direct test are N20-owned in
this package; N30 consumes that boundary read-only, exactly as N30 already
consumed `routing.Selector`-style deterministic contracts in v1. Do not
recreate, shadow, or fork the egress module or its provider allowlist here;
if the boundary N20 shipped is wrong, that is an N20 defect to route back,
not something to patch locally. This v7 prompt corrects
`N30_preflight_egress.prompt.v6.md`. N30's own scope is unaffected by the
result-namespace defect fixed in `implementation.graph.v7.yaml` (the defect
belonged entirely to the graph's shared `result_pattern` and every node's
own result/evidence write paths, corrected uniformly across all nodes) —
this is a mechanical gate-lineage rename only, following the same discipline
`N30_preflight_egress.prompt.v6.md` itself used for its
`N30_preflight_egress.prompt.v5.md` correction: only this file's own
`--graph` value now names `implementation.graph.v7.yaml` instead of
`implementation.graph.v6.yaml`, the same rename `implementation.graph.v7.yaml`'s
own header applies to the graph file itself, so this prompt does not go
stale relative to the graph it instructs `N30_PREFLIGHT_EGRESS` to scan
against. The v3 through v6 files are all preserved unchanged as historical
record, as is `implementation.graph.v6.yaml` itself (now at
`deprecated/implementation.graph.v6.yaml`) and `implementation.graph.v5.yaml`
(at `deprecated/implementation.graph.v5.yaml`).

# TEST

1. Define separate capability fields for executable identity, permitted
   auth mode, observable subscription-backed usability, required
   content-free operation, forbidden API-key absence, and approved data
   boundary — the first four proof classes the specification defines.
2. Implement the fifth proof class exactly as specified: D03 inspects the
   stream-json initialization event's tool and MCP-server lists directly
   and fails closed if any tool other than structured output, or any
   authenticated/invokable MCP-server tool, is present. A sandboxing flag
   (`--tools ""`, `--setting-sources ""`) is evidence of intent, never
   proof — do not accept flag presence as satisfying this class.
3. Require every mandatory field for every mandatory driver, across all
   five proof classes, before `ready: true`; one unknown or failed field
   makes readiness false and the CLI exit nonzero per the specification.
4. Reproduce the Run 26 defect: binaries present, one required provider
   unauthenticated. Assert preflight cannot return ready.
5. Reproduce N20-F06's live finding as a permanent regression case: an
   initialization event lists an MCP server under `--setting-sources ""`.
   Assert preflight still correctly evaluates tool-closure from the
   observed event (no tool granted) rather than either trusting the flag
   blindly or failing merely because a server is *listed*.
6. Cover executable spoofing, wrong auth mode, unavailable subscription,
   nonzero bounded probe, malformed output, model/driver mismatch,
   forbidden environment credential, unapproved endpoint, attempted
   fallback, and an exposed non-structured-output tool or an authenticated
   MCP-server tool.
7. Prove probes are content-free and transmit no curriculum artifacts,
   source text, PDFs, rendered pages, evidence, or user-owned files.
8. Prove the production CLI calls only N20-owned egress functions for
   authorization/transmission decisions — read-only consumption, no local
   reimplementation of the provider allowlist or data-class mapping.
9. Prove an unavailable approved driver produces an honest non-success
   state, never a fallback-provider recommendation or alternate-provider
   route.
10. Exercise the production CLI preflight path, not only helper functions.
11. Run focused preflight, CLI, capability-node, and adversarial tests and
    emit a schema-valid result.

N30 owns the D03 input/capability node, the production CLI, and its exact
tests declared in this graph — `egress.py` and its direct test are excluded
from N30's write set in this package. A provider-dispatch or
egress-boundary defect routes to N20; a graph-reachability defect routes to
N40. Do not rewrite their admitted outputs from this node. Remove every
retired-provider reference from N30-owned active tests and require the
zero-occurrence test scan
(`python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py --node N30_PREFLIGHT_EGRESS --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml`)
to remain green.

# LOOP

Classify each failure as capability semantics, production call-site wiring,
CLI status/exit mapping, or test fixture. If the failure traces to
`egress.py`'s own boundary rather than how N30 calls it, stop and route it
to N20 rather than patching it here. Repair the owning layer and rerun the
production-path negative case plus the full N30 slice. Never make readiness
easier to obtain to satisfy a test.
```

SHA-256: `c590af3176ad36f2b021dfdf2a231bbbe525fa92e6d2395f1e284ad88a92e1e8` (5856 bytes)

---

## `schemas/spec_approval.schema.v4.json`

Package-scoped approval schema. Const-locks approved_graph to implementation.graph.v7.yaml instead of v6, and schema_version to 4. Every other field is unchanged in shape and meaning from schema v3. SHA-256 at snapshot time: `49c94c2b43d2ac3c98d8dda98782e462284a0702159dcea47b09d48290577e1b`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Run 27 execution package v2 specification approval v4",
  "$comment": "Package-scoped successor to schemas/spec_approval.schema.v3.json. v3 const-locks approved_graph to implementation.graph.v6.yaml -- the graph that correctly fixed N20V2-F01 (the scan-scope defect that swept two unrelated Gemini-pipeline test files) but itself carried an independently-found result-namespace defect: its result_pattern was byte-identical to implementation.graph.v5.yaml's own, so a fresh N00/N10/N20 execution under v6 would have silently overwritten the already-ADMITTED N00/N10 results and the already-BLOCKED N20 result at their shared results/ root. implementation.graph.v7.yaml corrects exactly that defect (result_pattern moves to the versioned subdirectory results/v7/, whose per-node filenames never coincide with the flat per-node files directly under results/) and is now this package's active graph, so approved_graph must const-lock to v7's path instead -- v6 remains a legitimate historical approved_graph value for the rc7 lineage it governed, preserved unedited at deprecated/implementation.graph.v6.yaml, but it is no longer *this* package's active graph. Every other field is unchanged in shape and meaning from schema v3; this is the same narrow, single-field correction discipline v2 and v3 themselves used.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "approved",
    "approved_spec",
    "approved_spec_sha256",
    "spec_qa_verdict",
    "spec_qa_verification_sha256",
    "approved_rc_manifest",
    "approved_rc_manifest_sha256",
    "execution_package_qa_verdict",
    "execution_package_qa_verification_sha256",
    "approved_graph",
    "approved_graph_sha256",
    "approved_for",
    "model_assignments",
    "approved_at",
    "approval_statement"
  ],
  "properties": {
    "schema_version": {"const": 4},
    "approved": {"const": true},
    "approved_spec": {
      "const": "plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md",
      "$comment": "Unchanged from schema v3: this package's own single governing specification did not change in this correction."
    },
    "approved_spec_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "spec_qa_verdict": {"const": "QA_PASSED"},
    "spec_qa_verification_sha256": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "$comment": "SHA-256 of plans/26_langgraph_curriculum_factory/spec/v3/QA/verification.json, the specification's own independent QA verification record. Unchanged from schema v3."
    },
    "approved_rc_manifest": {
      "type": "string",
      "pattern": "^plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc[1-9][0-9]*/manifest\\.v1\\.json$",
      "$comment": "Unchanged from schema v3: still a versioned review-lineage pointer, not this package's governing identity. This correction does not re-anchor the package's approval-of-record to a new release candidate -- rc3 remains the approved package-structure snapshot; this result-namespace correction is validated by its own rc8 lineage (release_candidate/rc8/, and any rcN+ built to reach QA_PASSED), which is supporting engineering QA, not a fresh package approval. The validator recomputes approved_rc_manifest_sha256 against the file this path names and rejects a mismatch."
    },
    "approved_rc_manifest_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "execution_package_qa_verdict": {"const": "QA_PASSED"},
    "execution_package_qa_verification_sha256": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "$comment": "SHA-256 of the approved RC's own QA/verification.json. Unchanged from schema v3."
    },
    "approved_graph": {
      "const": "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml",
      "$comment": "Const-locked to this package's own active graph, exactly as v3 const-locks to v6. A future graph v8+ requiring fresh approval gets its own schema version, the same discipline this schema itself exists to apply. implementation.graph.v6.yaml remains a legitimate, unedited historical approved_graph value at deprecated/implementation.graph.v6.yaml, governed by schema v3, which is itself unedited and still valid for records that cite it."
    },
    "approved_graph_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "approved_for": {"const": "plan27_implementation_remediation"},
    "model_assignments": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "M01_RESEARCH_UNIT_SOURCES",
        "M02_CREATE_UNIT_DOMAIN_DATA",
        "M03_WRITE_UNIT_CONTENT",
        "M04_CREATE_UNIT_VISUALS",
        "M05_REVIEW_ACTUAL_UNIT",
        "M06_REPAIR_NAMED_UNIT_ARTIFACT",
        "M07_REVIEW_ACTUAL_WORKBOOK",
        "M08_REPAIR_NAMED_WORKBOOK_DEFECT"
      ],
      "$comment": "Unchanged from schema v3: USER_DECISION_REQUIRED-01 is not reopened by this correction.",
      "properties": {
        "M01_RESEARCH_UNIT_SOURCES": {"$ref": "#/$defs/model_assignment_sonnet5_xhigh"},
        "M02_CREATE_UNIT_DOMAIN_DATA": {"$ref": "#/$defs/model_assignment_sonnet5_high"},
        "M03_WRITE_UNIT_CONTENT": {"$ref": "#/$defs/model_assignment_sonnet5_high"},
        "M04_CREATE_UNIT_VISUALS": {"$ref": "#/$defs/model_assignment_sonnet5_high"},
        "M05_REVIEW_ACTUAL_UNIT": {"$ref": "#/$defs/model_assignment_gpt56sol_xhigh"},
        "M06_REPAIR_NAMED_UNIT_ARTIFACT": {"$ref": "#/$defs/model_assignment_sonnet5_xhigh"},
        "M07_REVIEW_ACTUAL_WORKBOOK": {"$ref": "#/$defs/model_assignment_gpt56sol_xhigh"},
        "M08_REPAIR_NAMED_WORKBOOK_DEFECT": {"$ref": "#/$defs/model_assignment_sonnet5_xhigh"}
      }
    },
    "approved_at": {"type": "string", "format": "date-time"},
    "approval_statement": {"type": "string", "minLength": 20}
  },
  "$defs": {
    "model_assignment_sonnet5_xhigh": {
      "type": "object",
      "additionalProperties": false,
      "required": ["model", "effort"],
      "properties": {
        "model": {"const": "claude-sonnet-5"},
        "effort": {"const": "xhigh"}
      }
    },
    "model_assignment_sonnet5_high": {
      "type": "object",
      "additionalProperties": false,
      "required": ["model", "effort"],
      "properties": {
        "model": {"const": "claude-sonnet-5"},
        "effort": {"const": "high"}
      }
    },
    "model_assignment_gpt56sol_xhigh": {
      "type": "object",
      "additionalProperties": false,
      "required": ["model", "effort"],
      "properties": {
        "model": {"const": "gpt-5.6-sol"},
        "effort": {"const": "xhigh"}
      }
    }
  }
}
```

SHA-256: `49c94c2b43d2ac3c98d8dda98782e462284a0702159dcea47b09d48290577e1b` (6775 bytes)

---

## `contracts/spec_approval.v4.yaml`

Approval record. Carries forward, byte-for-byte, all five of contract v3's approved_spec/spec_qa/approved_rc_manifest/execution_package_qa digests, its approved_rc_manifest (still rc3), model_assignments, and approved_at -- only approved_graph/approved_graph_sha256 and schema_version advance, to implementation.graph.v7.yaml (sha256 b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22) and 4. SHA-256 at snapshot time: `8310e6cc21d526fce1555e1a7c4db7f797ee2206a29c40836ec828892308c629`.

```yaml
schema_version: 4
approved: true
approved_spec: plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md
approved_spec_sha256: e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c
spec_qa_verdict: QA_PASSED
spec_qa_verification_sha256: 899c9720be48f071d6caf26eceafa81be626cd3bda685afa05eb0cc1dfe9a631
approved_rc_manifest: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc3/manifest.v1.json
approved_rc_manifest_sha256: 0e4fbfe2c258ae6176931e5490f8a2b55bdf8708d3ef0f257b50a05c9e582a6d
execution_package_qa_verdict: QA_PASSED
execution_package_qa_verification_sha256: 202e2f214dd732ce24eb758c7cee5965cfcc113d71d03350d8bc5fefa7773217
approved_graph: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml
approved_graph_sha256: b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22
approved_for: plan27_implementation_remediation
model_assignments:
  M01_RESEARCH_UNIT_SOURCES: {model: claude-sonnet-5, effort: xhigh}
  M02_CREATE_UNIT_DOMAIN_DATA: {model: claude-sonnet-5, effort: high}
  M03_WRITE_UNIT_CONTENT: {model: claude-sonnet-5, effort: high}
  M04_CREATE_UNIT_VISUALS: {model: claude-sonnet-5, effort: high}
  M05_REVIEW_ACTUAL_UNIT: {model: gpt-5.6-sol, effort: xhigh}
  M06_REPAIR_NAMED_UNIT_ARTIFACT: {model: claude-sonnet-5, effort: xhigh}
  M07_REVIEW_ACTUAL_WORKBOOK: {model: gpt-5.6-sol, effort: xhigh}
  M08_REPAIR_NAMED_WORKBOOK_DEFECT: {model: claude-sonnet-5, effort: xhigh}
approved_at: "2026-08-13T20:57:25Z"
approval_statement: >
  This record carries forward, unchanged and reinvented nowhere, the exact
  approval already given in
  plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/contracts/spec_approval.v3.yaml
  (approved_at 2026-08-13T20:57:25Z, preserved byte-for-byte, not edited by
  this record), which itself carried forward spec_approval.v2.yaml's and
  spec_approval.v1.yaml's approval unchanged. This record fixes a narrower,
  later-discovered defect in v3's own active graph: implementation.graph.v6.yaml
  (the graph spec_approval.v3.yaml's approved_graph named) correctly fixed
  N20V2-F01 -- the write-set/scan-scope defect that swept two unrelated
  Gemini-pipeline test files -- but its own result_pattern
  (execution_package_v2/results/{node_id}.result.v1.json) was byte-identical
  to implementation.graph.v5.yaml's own result_pattern. Because N00 and N10
  are already ADMITTED (PASSED) with real results at
  execution_package_v2/results/N00_SPEC_APPROVAL_GATE.result.v1.json and
  execution_package_v2/results/N10_HARNESS_PROTOCOL.result.v1.json, and N20 is
  already BLOCKED with real evidence at
  execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json, a fresh
  execution of any of these three nodes under graph v6 as originally built
  would have validated against v6's own newer prompt/schema and then silently
  overwritten those exact same three historical files at their shared path --
  violating this recovery lineage's repeated, explicit "preserve prior
  attempts, never overwrite an admitted or blocked record" requirement. This is
  not a specification defect, a provider decision, or a change to the
  package's approved structure: it is a mechanical result-namespace
  engineering correction to the graph's own result_pattern and every node's
  own result/evidence write paths, captured in implementation.graph.v7.yaml
  (preserving implementation.graph.v6.yaml unedited at
  deprecated/implementation.graph.v6.yaml, sha256
  b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26) and its own
  package-scoped schema
  (execution_package_v2/schemas/spec_approval.schema.v4.json, const-locking
  approved_graph to v7 instead of v6). No new user approval is inferred beyond
  what is already on record: the specification, its QA verification, the rc3
  manifest, and rc3's own QA verification are carried forward byte-for-byte
  identical to spec_approval.v3.yaml -- user explicitly approved, by exact
  digest, the following for execution package v2 of
  plan27_implementation_remediation: specification v4 at
  plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md
  (SHA-256 e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c);
  that specification's independent QA verification record at
  plans/26_langgraph_curriculum_factory/spec/v3/QA/verification.json (SHA-256
  899c9720be48f071d6caf26eceafa81be626cd3bda685afa05eb0cc1dfe9a631, session
  019ffbeb-3f45-7440-a83e-aa560938dc98, chain_valid true); the
  release-candidate-3 manifest at
  plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc3/manifest.v1.json
  (SHA-256 0e4fbfe2c258ae6176931e5490f8a2b55bdf8708d3ef0f257b50a05c9e582a6d);
  and that release candidate's independent QA verification record at
  plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc3/QA/verification.json
  (SHA-256 202e2f214dd732ce24eb758c7cee5965cfcc113d71d03350d8bc5fefa7773217,
  session 019ffcc7-a48f-7870-a933-5d80bb61dac3, chain_valid true). Only
  approved_graph/approved_graph_sha256 move, from implementation.graph.v6.yaml
  (SHA-256 b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26) to
  implementation.graph.v7.yaml (SHA-256
  b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22), whose only
  content changes from v6 are: result_pattern and every node's own result/
  evidence write paths move under execution_package_v2/results/v7/ instead of
  execution_package_v2/results/; rules.frozen_before_entry names schema v4 in
  place of schema v3; and every command's own --graph value renames to v7. No
  node, write set, edge, scan rule, or verification logic otherwise changed --
  the N20V2-F01 scan-scope fix (retired_provider_test_scan.scan_roots as the
  explicit 17-file union) is carried forward unchanged. All digests were
  independently recomputed against live repository bytes when this record was
  written and matched exactly. This approval authorizes proceeding
  sequentially from N00 through N90 of
  plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml,
  preserving all prior attempts and evidence -- the Run 27 v1 attempt blocked
  at N20_PROVIDER_TRANSPORT, the first failed execution-package correction
  implementation.graph.v2.yaml, release candidates rc1 through rc7, the
  admitted N00/N10 results, and N20_PROVIDER_TRANSPORT's own BLOCKED result
  under implementation.graph.v5.yaml (finding N20V2-F01) -- without
  redesigning the execution package or reopening USER_DECISION_REQUIRED-01,
  which remains resolved exactly as recorded in spec_approval.v1.yaml, now
  also structured in model_assignments above: M01, M06, and M08 =
  claude-sonnet-5 at effort xhigh; M02, M03, and M04 = claude-sonnet-5 at
  effort high; M05 and M07 = gpt-5.6-sol at effort xhigh.
```

SHA-256: `8310e6cc21d526fce1555e1a7c4db7f797ee2206a29c40836ec828892308c629` (6985 bytes)

---

## `deprecated/implementation.graph.v6.yaml`

Superseded graph, preserved byte-for-byte at its new deprecated/ path -- this is the exact file rc7's own manifest recorded at the package root as implementation.graph.v6.yaml, sha256 unchanged: `b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26`. Supplied here as static historical content (not logic under review), mirroring rc7's own treatment of deprecated/implementation.graph.v5.yaml as --ground material.

```yaml
graph_id: plan27_langgraph_curriculum_factory_remediation
version: 2
status: SCAFFOLDED_BLOCKED_BY_SPEC_APPROVAL
source_incident: plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec_correction.result.v1.md
source_spec: plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md
runner: plans/27_langgraph_curriculum_factory_remediation/run.prompt.md
qa_criteria: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/qa_criteria.v1.md
node_result_schema: plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json
entry: N00_SPEC_APPROVAL_GATE
result_pattern: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/{node_id}.result.v1.json

# This is execution package v2: an isolated, from-scratch rebuild of the
# corrected recovery of the v1 attempt that reached BLOCKED at
# N20_PROVIDER_TRANSPORT
# (plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json,
# findings N20-F01, N20-F02, N20-F03, N20-F04, N20-F06). v1's N00-N20 results
# and evidence, implementation.graph.v1.yaml itself, and this same directory's
# sibling implementation.graph.v2.yaml (the first, failed package correction,
# preserved at sha256
# f297d6528375eeeda5b97a54d654997a65f5d0c7100cf50b54d71c4ca4763b1a together
# with its QA/ session and PKG-QA-001 finding) are untouched, immutable,
# historical evidence. This document does not edit any of them.
#
# This file is this package's sixth gate-tracked artifact version
# (implementation.graph.v6.yaml), correcting N20V2-F01: the real N20
# execution of implementation.graph.v5.yaml (preserved unchanged at
# deprecated/implementation.graph.v5.yaml, sha256
# ce2362787a9760c9db3b2f667a0561ebd877ec89f24d690b2210ec9b6f3777b8, the
# graph approved and executed in the rc3-approved, rc5-schema-corrected
# lineage) reached a genuine, well-evidenced BLOCKED, not an implementation
# gap: v5 placed tests/runtime/test_gemini.py and
# tests/runtime/test_capabilities.py in N20_PROVIDER_TRANSPORT's write set,
# but those two files test runtime/gemini.py and runtime/capabilities.py, a
# wholly separate, still-active Plan 11/19/20/21 arduino_kit curriculum
# pipeline that legitimately uses Gemini and has nothing to do with this
# migration -- runtime/gemini.py is not in forbidden_production_scan's
# scan_roots, is not owned by any node in this graph, and is imported only by
# runtime/capability_cycle.py and runtime/model_worker.py, neither of which
# this migration touches. v5's rules.retired_provider_test_scan.scan_roots
# was ['tests/runtime'], walked recursively with a zero-occurrence policy and
# no exemption mechanism, so it legitimately found 16 real occurrences of
# "gemini" in those two unrelated files and failed -- with no way to pass
# short of vandalizing correct, unrelated test coverage or editing a file
# outside N20's write-set authority. See
# plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json
# finding N20V2-F01 for the full account; that BLOCKED result and its
# evidence directory are untouched, immutable history -- this correction does
# not reopen, edit, or supersede them in place, and does not touch any of the
# real, independently-verified production code N20 already wrote (transport.py,
# egress.py, model_nodes.py, config/model_jobs.v1.yaml, policy/routes.v1.yaml,
# policy/routing/model_registry.v1.yaml, and their schemas).
#
# Removing the two files from N20's write set alone is insufficient: v5's
# N60_ADVERSARIAL_REGRESSION verification runs scan_node.py in complete-tree
# mode (no --node), which -- since scan_roots named the whole tests/runtime
# directory -- would still recursively scan every file under it, including
# the two unrelated Gemini-pipeline test files, and fail identically at N60.
# The fix must narrow the scan's scope itself, in a way that works identically
# in both node-scoped and complete-tree mode, not merely narrow one node's
# write set.
#
# The fix: rules.retired_provider_test_scan.scan_roots below is no longer a
# directory to walk recursively. It is now the explicit, exact list of every
# migration-owned active test file across N20 through N60 -- computed by
# reading every node's own writes list for tests/runtime/test_*.py entries,
# excluding exactly the two Gemini-pipeline files removed from N20's write
# set below. This requires no change to
# plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py
# (which this package must not edit): its own collect_files helper already
# accepts an individual file path in scan_roots exactly as it accepts a
# directory (collect_files checks target.is_file() before target.is_dir()),
# so an explicit file list is not a new scanning mechanism, only a more
# precise value for an existing, unmodified one. tests/runtime/test_gemini.py
# and tests/runtime/test_capabilities.py are never scanned by either mode,
# because collect_files never visits a path that is not itself in scan_roots
# or beneath a directory in scan_roots -- there is no directory root left
# that contains them. scan_node.py's own node-scoped restriction
# (restrict_to_write_set, unchanged) narrows this same explicit list down to
# each node's own write-set intersection automatically: N20 sees only its
# own 7 files, N30 its own 3, and so on, with no further code change,
# exactly as it already narrows forbidden_production_scan's report today.
# N60's complete-tree mode sees the full 17-file union unfiltered, replacing
# v5's accidental scan of the whole tests/runtime directory (~30 files, most
# of them Plan 25 and other unrelated systems' tests) with exactly the files
# this migration actually owns. tests/runtime/test_plan27_adversarial.py
# (N60's own future adversarial-regression test file) is named in this list
# even though it does not exist on disk yet -- collect_files silently omits
# a scan_roots entry that is neither an existing file nor an existing
# directory, so its absence causes no error for N20-N50's scans, and once
# N60 creates it, it is automatically covered without any further graph edit.
#
# Because this correction changes the graph's own rules and one node's write
# set (not merely a sibling addition), implementation.graph.v5.yaml is
# deprecated properly: preserved byte-for-byte at
# deprecated/implementation.graph.v5.yaml, superseded here, never edited in
# place. Because this active graph's own path changes,
# execution_package_v2/schemas/spec_approval.schema.v2.json's approved_graph
# const (locked to implementation.graph.v5.yaml) can no longer describe this
# package's active graph, so this correction also introduces
# execution_package_v2/schemas/spec_approval.schema.v3.json (identical in
# structure, const-locked to this file's path instead) and
# execution_package_v2/contracts/spec_approval.v3.yaml (carrying forward --
# not reinventing -- the exact approval already recorded in
# spec_approval.v2.yaml: the same specification, specification QA record,
# rc3 manifest, and rc3 QA record already approved by the user, unchanged;
# only approved_graph/approved_graph_sha256 move to this file and
# schema_version becomes 3). This is a mechanical write-set/scan-scope
# engineering correction, not a new specification or provider decision, and
# does not infer any new user approval beyond what rc3 already carries.
# N00_spec_approval_gate.prompt.v5.md, N20_provider_transport.prompt.v5.md,
# and N30_preflight_egress.prompt.v5.md are renamed to .v6.md, mechanically
# rebinding their own --graph/schema/contract references the same way the
# v3->v4 and v4->v5 gate-lineage renames each did, with no change to any
# substantive TEST requirement. N40/N50/N60's prompts carry no graph-path
# reference and are reused unchanged. rules.frozen_before_entry below gains
# schema v3 in place of schema v2 (v2 remains, unedited, at its own path --
# it is simply no longer the frozen schema *this* graph's N00 validates
# against).
#
# No other node, write set, edge, dependency, or verification logic changed
# in substance from implementation.graph.v5.yaml beyond: (a) every command's
# own literal --graph value now names this file instead of v5; (b)
# N20_PROVIDER_TRANSPORT.writes drops tests/runtime/test_gemini.py and
# tests/runtime/test_capabilities.py (no other node ever owned them, so no
# other node's write set needs a corresponding change); (c)
# rules.retired_provider_test_scan.scan_roots becomes the explicit 17-file
# union described above, replacing ['tests/runtime']; (d)
# rules.frozen_before_entry gains spec_approval.schema.v3.json in place of
# spec_approval.schema.v2.json. ``version: 2`` is unchanged and does not
# become 3 -- this is the same discipline v3->v4->v5 already established:
# the package's own structural version tracks its Phase D correction
# lineage, not its gate-rename or scan-scope-correction count.

rules:
  success_requires_schema_bound_result: true
  preserve_plan26_history: true
  invalidate_all_descendants_on_ancestor_change: true
  markdown_status_is_authority: false
  allow_parallel_ready_nodes: false
  max_attempts_per_finding: 3
  live_proof_required_for_activation: true
  frozen_before_entry:
    - plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json
    - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v3.json
  forbidden_production_scan:
    scan_roots:
      - runtime/langgraph_factory
      - runtime/run_curriculum.py
      - policy/routes.v1.yaml
      - policy/routing/model_registry.v1.yaml
      - schemas/routes.schema.v1.json
      - schemas/model_registry.schema.v1.json
    excluded_globs:
      - "**/__pycache__/**"
      - "**/*.pyc"
    excluded_roots:
      - plans
      - tests
      - outputs
    prohibited_dispatch_or_import_terms:
      - gemini
      - google.generativeai
    prohibited_credential_names:
      - GEMINI_API_KEY
      - GOOGLE_API_KEY
      - OPENAI_API_KEY
      - ANTHROPIC_API_KEY
    credential_absence_guard_paths:
      - runtime/run_curriculum.py
      - runtime/langgraph_factory/transport.py
    credential_occurrence_policy: >-
      Credential names may appear only in explicit absence/denial guards inside
      runtime/run_curriculum.py or runtime/langgraph_factory/transport.py; they
      may never configure, authenticate, authorize, dispatch, or provide fallback.
  retired_provider_test_scan:
    # An explicit, exact file list -- not a directory to walk recursively --
    # naming every migration-owned active test across N20-N60, and nothing
    # else. tests/runtime contains ~30 files; most (including
    # test_gemini.py and test_capabilities.py, which test the unrelated,
    # still-active Plan 11/19/20/21 Gemini pipeline) are deliberately absent
    # from this list. test_plan27_adversarial.py does not exist on disk yet
    # (N60 creates it); its absence causes no error, and it is automatically
    # covered once N60 creates it, with no further edit to this list.
    scan_roots:
      - tests/runtime/test_plan26_transport.py
      - tests/runtime/test_plan26_model_nodes.py
      - tests/runtime/test_plan26_egress.py
      - tests/runtime/test_curriculum_factory_graph.py
      - tests/runtime/test_plan26_adversarial.py
      - tests/runtime/test_plan26_api_contract.py
      - tests/runtime/test_plan26_lock_drift.py
      - tests/runtime/test_plan26_cli.py
      - tests/runtime/test_plan26_deterministic_nodes.py
      - tests/runtime/test_run_curriculum.py
      - tests/runtime/test_plan26_topology.py
      - tests/runtime/test_plan26_unit_graph.py
      - tests/runtime/test_plan26_repair_acceptance.py
      - tests/runtime/test_plan26_workbook.py
      - tests/runtime/test_plan26_evidence.py
      - tests/runtime/test_plan26_persistence.py
      - tests/runtime/test_plan27_adversarial.py
    excluded_globs:
      - "**/__pycache__/**"
      - "**/*.pyc"
    prohibited_terms:
      - gemini
      - google
      - GEMINI_API_KEY
      - GOOGLE_API_KEY
    occurrence_policy: zero_occurrences_in_active_test_source

nodes:
  N00_SPEC_APPROVAL_GATE:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N00_spec_approval_gate.prompt.v6.md
    depends_on: []
    writes:
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N00_SPEC_APPROVAL_GATE.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N00_SPEC_APPROVAL_GATE
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N00_SPEC_APPROVAL_GATE]
    allowed_results: [PASSED, BLOCKED_SPEC_NOT_APPROVED, BLOCKED]

  N10_HARNESS_PROTOCOL:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N10_harness_protocol.prompt.v1.md
    depends_on: [N00_SPEC_APPROVAL_GATE]
    writes:
      - plans/27_langgraph_curriculum_factory_remediation/controller
      - plans/27_langgraph_curriculum_factory_remediation/schemas/scheduler_receipt.schema.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/schemas/attempt_record.schema.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_node_result_protocol.py
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N10_HARNESS_PROTOCOL.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N10_HARNESS_PROTOCOL
    verification:
      - [python3, -m, pytest, -q, plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_node_result_protocol.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N10_HARNESS_PROTOCOL]
    allowed_results: [PASSED, BLOCKED]

  N20_PROVIDER_TRANSPORT:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N20_provider_transport.prompt.v6.md
    depends_on: [N10_HARNESS_PROTOCOL]
    writes:
      - runtime/langgraph_factory/transport.py
      - runtime/langgraph_factory/model_nodes.py
      - runtime/langgraph_factory/config
      - runtime/langgraph_factory/prompts
      - runtime/langgraph_factory/schemas
      - runtime/langgraph_factory/egress.py
      - policy/routes.v1.yaml
      - policy/routing/model_registry.v1.yaml
      - schemas/routes.schema.v1.json
      - schemas/model_registry.schema.v1.json
      - tests/runtime/test_plan26_transport.py
      - tests/runtime/test_plan26_model_nodes.py
      - tests/runtime/test_plan26_egress.py
      - tests/runtime/test_curriculum_factory_graph.py
      - tests/runtime/test_plan26_adversarial.py
      - tests/runtime/test_plan26_api_contract.py
      - tests/runtime/test_plan26_lock_drift.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N20_PROVIDER_TRANSPORT
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_transport.py, tests/runtime/test_plan26_model_nodes.py, tests/runtime/test_plan26_egress.py, tests/runtime/test_capabilities.py, tests/runtime/test_curriculum_factory_graph.py, tests/runtime/test_plan26_adversarial.py, tests/runtime/test_plan26_api_contract.py, tests/runtime/test_plan26_lock_drift.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N20_PROVIDER_TRANSPORT, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N20_PROVIDER_TRANSPORT]
    allowed_results: [PASSED, BLOCKED]

  N30_PREFLIGHT_EGRESS:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N30_preflight_egress.prompt.v6.md
    depends_on: [N20_PROVIDER_TRANSPORT]
    writes:
      - runtime/langgraph_factory/nodes/inputs.py
      - runtime/run_curriculum.py
      - tests/runtime/test_plan26_cli.py
      - tests/runtime/test_plan26_deterministic_nodes.py
      - tests/runtime/test_run_curriculum.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N30_PREFLIGHT_EGRESS.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N30_PREFLIGHT_EGRESS
    read_only_inputs:
      - runtime/langgraph_factory/egress.py
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_cli.py, tests/runtime/test_run_curriculum.py]
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_deterministic_nodes.py, -k, "D03 or capability"]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N30_PREFLIGHT_EGRESS, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N30_PREFLIGHT_EGRESS]
    allowed_results: [PASSED, BLOCKED]

  N40_INTEGRATION_OWNERSHIP:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N40_integration_ownership.prompt.v1.md
    depends_on: [N30_PREFLIGHT_EGRESS]
    writes:
      - runtime/langgraph_factory/graph.py
      - runtime/langgraph_factory/routing.py
      - runtime/langgraph_factory/unit_graph.py
      - runtime/langgraph_factory/repair.py
      - runtime/langgraph_factory/acceptance.py
      - runtime/langgraph_factory/workbook.py
      - tests/runtime/test_plan26_topology.py
      - tests/runtime/test_plan26_unit_graph.py
      - tests/runtime/test_plan26_repair_acceptance.py
      - tests/runtime/test_plan26_workbook.py
      - plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N40_INTEGRATION_OWNERSHIP.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N40_INTEGRATION_OWNERSHIP
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_topology.py, tests/runtime/test_plan26_unit_graph.py, tests/runtime/test_plan26_repair_acceptance.py, tests/runtime/test_plan26_workbook.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N40_INTEGRATION_OWNERSHIP, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_ownership.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N40_INTEGRATION_OWNERSHIP]
    allowed_results: [PASSED, BLOCKED]

  N50_EVIDENCE_AUDIT_CONTROLS:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N50_evidence_audit_controls.prompt.v1.md
    depends_on: [N40_INTEGRATION_OWNERSHIP]
    writes:
      - runtime/langgraph_factory/evidence.py
      - runtime/langgraph_factory/artifacts.py
      - runtime/langgraph_factory/persistence.py
      - tests/runtime/test_plan26_evidence.py
      - tests/runtime/test_plan26_persistence.py
      - plans/27_langgraph_curriculum_factory_remediation/contracts/evidence_determinism.v1.yaml
      - plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N50_EVIDENCE_AUDIT_CONTROLS.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N50_EVIDENCE_AUDIT_CONTROLS
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_evidence.py, tests/runtime/test_plan26_persistence.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_evidence_determinism.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/evidence_determinism.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_requirements_lineage.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N50_EVIDENCE_AUDIT_CONTROLS, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N50_EVIDENCE_AUDIT_CONTROLS]
    allowed_results: [PASSED, BLOCKED]

  N60_ADVERSARIAL_REGRESSION:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N60_adversarial_regression.prompt.v1.md
    depends_on: [N50_EVIDENCE_AUDIT_CONTROLS]
    writes:
      - tests/runtime/test_plan27_adversarial.py
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_adversarial.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N60_ADVERSARIAL_REGRESSION.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N60_ADVERSARIAL_REGRESSION
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan27_adversarial.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_adversarial.py]
      - [python3, -m, pytest, -q, tests/runtime]
      - [python3, -m, pytest, -q, plans/27_langgraph_curriculum_factory_remediation/tests]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N60_ADVERSARIAL_REGRESSION]
    allowed_results: [PASSED, BLOCKED]

  N70_LIVE_UNIT_PROOF:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N70_live_unit_proof.prompt.v1.md
    depends_on: [N60_ADVERSARIAL_REGRESSION]
    writes:
      - outputs/run27/live_unit
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N70_LIVE_UNIT_PROOF.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N70_LIVE_UNIT_PROOF
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml, verify-live-proof, --node, N70_LIVE_UNIT_PROOF]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N70_LIVE_UNIT_PROOF]
    allowed_results: [PASSED, NOT_AVAILABLE, BLOCKED]

  N80_LIVE_WORKBOOK_PROOF:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N80_live_workbook_proof.prompt.v1.md
    depends_on: [N70_LIVE_UNIT_PROOF]
    writes:
      - outputs/run27/live_workbook
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N80_LIVE_WORKBOOK_PROOF.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N80_LIVE_WORKBOOK_PROOF
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml, verify-live-proof, --node, N80_LIVE_WORKBOOK_PROOF]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N80_LIVE_WORKBOOK_PROOF]
    allowed_results: [PASSED, NOT_AVAILABLE, BLOCKED]
    read_only_inputs:
      - outputs/run27/live_unit

  N90_REQUIREMENTS_FINAL_AUDIT:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N90_requirements_final_audit.prompt.v1.md
    depends_on: [N80_LIVE_WORKBOOK_PROOF]
    writes:
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N90_REQUIREMENTS_FINAL_AUDIT.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N90_REQUIREMENTS_FINAL_AUDIT
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v6.yaml, verify-final-audit, --node, N90_REQUIREMENTS_FINAL_AUDIT]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N90_REQUIREMENTS_FINAL_AUDIT]
    allowed_results: [PASSED, BLOCKED]

edges:
  - {from: N00_SPEC_APPROVAL_GATE, to: N10_HARNESS_PROTOCOL}
  - {from: N10_HARNESS_PROTOCOL, to: N20_PROVIDER_TRANSPORT}
  - {from: N20_PROVIDER_TRANSPORT, to: N30_PREFLIGHT_EGRESS}
  - {from: N30_PREFLIGHT_EGRESS, to: N40_INTEGRATION_OWNERSHIP}
  - {from: N40_INTEGRATION_OWNERSHIP, to: N50_EVIDENCE_AUDIT_CONTROLS}
  - {from: N50_EVIDENCE_AUDIT_CONTROLS, to: N60_ADVERSARIAL_REGRESSION}
  - {from: N60_ADVERSARIAL_REGRESSION, to: N70_LIVE_UNIT_PROOF}
  - {from: N70_LIVE_UNIT_PROOF, to: N80_LIVE_WORKBOOK_PROOF}
  - {from: N80_LIVE_WORKBOOK_PROOF, to: N90_REQUIREMENTS_FINAL_AUDIT}

terminals:
  ACTIVATED:
    guard: N60 PASSED; N70 and N80 PASSED with authorized live receipts; N90 independently verified all QA criteria
  REMEDIATION_VERIFIED_NOT_ACTIVATED:
    guard: N60 PASSED; N70 or N80 is NOT_AVAILABLE for an approved subscription driver; N90 verifies no fallback or false product claim
  BLOCKED_SPEC_NOT_APPROVED:
    guard: N00 did not prove a corrected independently verified user-approved specification digest
  BLOCKED:
    guard: an implementation, integrity, evidence, convergence, or audit finding remains unresolved
```

SHA-256: `b186b58828fd1f490a57dd3cfe7d26bcdff70a37f78d6d996f2f8234ef2b5c26` (27475 bytes)

---
