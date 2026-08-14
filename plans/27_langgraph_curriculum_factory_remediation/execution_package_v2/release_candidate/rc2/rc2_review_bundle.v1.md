# RC2 review bundle — Run 27 execution package v2 release candidate

## Why this document exists

This is the single artifact submitted to `qa-gate-codex-run` for this session. It is
**not** a summary or a pointer file — every file below whose logic PKGV2-T01–T11
depend on is embedded verbatim, in full, so that Codex's judged content *is* the
reviewed logic itself, not a description of it or a `--ground` source held outside the
chain.

This bundle exists because the immediately prior release candidate,
`release_candidate/rc1/` (session `019ffcaa-f6b4-7d71-9005-0e53c79a5cc4`), returned a
real, specific `FAIL`: finding `RC1-QA-001`, "Automated suite does not prove
fresh-prompt consistency." The automated suite defined graph/scanner/validator paths
but no prompt paths or prompt-content assertions, so it stayed green while all three
fresh node prompts (`N00`, `N20`, `N30`) instructed a scan against
`implementation.graph.v1.yaml` — a filename this package does not contain — instead of
the package's actually enforced and graph-bound `implementation.graph.v4.yaml`. RC1 and
its `QA_FAILED` / `MAX_ITERATIONS_EXHAUSTED` verdict are preserved exactly as they were
and are **not** reopened, edited, or overridden by this bundle or this session.

This rc2 snapshot fixes exactly that defect: N00, N20, and N30 are corrected to version
4 (`*.prompt.v4.md`; the superseded `*.prompt.v3.md` files, and the failed rc1 session
that reviewed them, are preserved unchanged as historical record), every graph-path
reference in their own text now resolves to `implementation.graph.v4.yaml`, and the
automated suite gained a real, deterministic, mutation-proven regression test
(`test_each_fresh_prompt_references_the_exact_enforced_graph` and its companion
mutation-based negative proofs) that parses all three prompts' actual text and rejects
a missing, stale, or mismatched graph reference. Every other reviewed file
(`controller/scan_node.py`, `tools/validate_plan_v2.py`, `tools/validate_result_v2.py`,
`implementation.graph.v4.yaml`'s node topology) is otherwise unchanged since rc1 —
confirmed by SHA-256 against the live `execution_package_v2/` files at snapshot time
(see `manifest.v1.json` beside this file).

Read every section below as source you are being asked to judge, exactly as if you had
opened each file directly at its path (given for traceability only — judge the text
below, not a live version at that path, since this bundle is the frozen, versioned
review target).

---

## `implementation.graph.v4.yaml`

Execution graph, corrected: N00/N20/N30's `prompt:` bindings now point at the graph-consistent v4 prompts. SHA-256 at snapshot time: `0d5b5af8b0c60847e3b52ac93c4c10328f48a1404130a6b785485bcbbae3d571`.

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
# implementation.graph.v2.yaml's own correction of N20-F01/N20-F02 was
# structurally right but its QA round 1 found PKG-QA-001: its node-scoped
# verification command never passed --graph, so the extended scanner script
# silently defaulted to loading the *parent* v1 graph
# (plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml)
# instead of the corrected v2 write sets -- a stale-default failure, not a
# scanning-logic failure. This package fixes that class of defect at the
# root: every node-scoped verification command below passes --graph
# explicitly to this package's own graph file, and this package's own scanner
# entry point (execution_package_v2/controller/scan_node.py) defaults to
# *this* file, never to the parent v1 graph, if --graph is ever omitted.
#
#   N20-F01: the bare whole-tree forbidden-reference scan
#   (controller/check_forbidden_production_refs.py, no node scoping) is
#   unsatisfiable for any node before the last one to touch a
#   migration-affected test, because it depends on every later node's
#   not-yet-migrated files already being clean. N20-N50 now use
#   execution_package_v2/controller/scan_node.py --node <NODE_ID> --graph
#   <this file>. N60 alone still runs the scanner in complete-tree mode as
#   the final zero-occurrence denominator.
#
#   N20-F02: the frozen anthropic/openai authorization classes v4 (spec v3)
#   S7.4 requires cannot be expressed while N20 (which owns the frozen route
#   table and the eight job schemas) and N30 (which v1 assigned egress.py and
#   its provider allowlist to) are different write-set owners; N20 has no
#   path to change the allowlist its own routes must validate against.
#   runtime/langgraph_factory/egress.py and tests/runtime/test_plan26_egress.py
#   move from N30's write set to N20's. N30 consumes that boundary read-only.
#
# No other node's write set, dependency edge, verification shape, or
# terminal changed from v1's structure beyond: (a) every node's own
# result/evidence write path now points at this package's own
# execution_package_v2/results/ root, never v1's results/ or the failed
# package's results/v2/ root; (b) N20-N60's forbidden-reference verification
# now invokes this package's own scan_node.py instead of the parent
# controller/check_forbidden_production_refs.py; (c) N00/N10/N20/N30/N40/N50/
# N60/N70/N80/N90's validate_result invocation now invokes this package's own
# tools/validate_result_v2.py instead of the parent tools/validate_result.py,
# and N00's validate_plan invocation now invokes this package's own
# tools/validate_plan_v2.py; (d) N40/N50/N70/N80/N90's existing v1 controller
# commands (verify_ownership.py, verify_evidence_determinism.py,
# verify_requirements_lineage.py, run27_controller.py) are invoked unmodified,
# read-only, but now with an explicit --graph flag bound to this file. N10's
# admitted controller code, schemas, and tests are reused unmodified; N40's,
# N50's, N60's, N70's, N80's, and N90's own prompts are reused unmodified
# from the v1 package's prompts/ directory because this correction does not
# change their scope. Only N00, N20, and N30's prompts are freshly authored
# inside this package (execution_package_v2/prompts/), because only their
# scope actually changed.
#
# This file is this package's fourth gate-tracked artifact version
# (implementation.graph.v4.yaml), submitted for round 4 of QA session
# 019ffc3b-6379-7ef3-839d-759ed5c7fc9c after round 3's PKGV2-QA-002 finding:
# round 2's fix counted occurrences by matching the exact token "--node" or
# "--graph", which caught a second separated-form pair but missed Python
# argparse's equals-form spelling (--node=value) entirely, so a command with
# one separated --node and one equals-form --node=<other> still read as a
# single occurrence while argparse itself resolved it to the second, wrong
# value. The fix replaces the hand-rolled token match with an
# argparse.ArgumentParser shaped exactly like scan_node.py's own, using a
# custom Action that records every invocation, so occurrence counting goes
# through argparse's real option-matching rules -- exact spelling, equals
# form, and unambiguous prefix abbreviation alike -- once, rather than
# chasing one spelling at a time; tests now also cover the abbreviation form
# to demonstrate this closes the class rather than the instance. The fix is
# in the proof (tests/test_execution_package_v2.py, tools/validate_plan_v2.py)
# and its two hardcoded self-references (controller/scan_node.py's
# DEFAULT_GRAPH_PATH, tools/validate_result_v2.py's GRAPH_PATH), not in this
# graph's own content: no node, write set, edge, or verification command
# changed in substance from implementation.graph.v3.yaml (preserved at
# deprecated/implementation.graph.v3.yaml by the QA gate script), beyond
# every command's own literal --graph value now naming this file instead of
# that one, which qa_gate.py's `round` requires -- it accepts a fix only as
# a strictly newer same-named artifact version, never a same-path
# resubmission. This is a gate-lineage rename, not a graph semantic version
# bump; ``version: 2`` below is unchanged from v1's Phase D correction and
# does not become 3.

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
    scan_roots:
      - tests/runtime
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
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N00_spec_approval_gate.prompt.v4.md
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
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N20_provider_transport.prompt.v4.md
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
      - tests/runtime/test_gemini.py
      - tests/runtime/test_capabilities.py
      - tests/runtime/test_curriculum_factory_graph.py
      - tests/runtime/test_plan26_adversarial.py
      - tests/runtime/test_plan26_api_contract.py
      - tests/runtime/test_plan26_lock_drift.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/N20_PROVIDER_TRANSPORT.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/evidence/N20_PROVIDER_TRANSPORT
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_transport.py, tests/runtime/test_plan26_model_nodes.py, tests/runtime/test_plan26_egress.py, tests/runtime/test_capabilities.py, tests/runtime/test_curriculum_factory_graph.py, tests/runtime/test_plan26_adversarial.py, tests/runtime/test_plan26_api_contract.py, tests/runtime/test_plan26_lock_drift.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N20_PROVIDER_TRANSPORT, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N20_PROVIDER_TRANSPORT]
    allowed_results: [PASSED, BLOCKED]

  N30_PREFLIGHT_EGRESS:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N30_preflight_egress.prompt.v4.md
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
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N30_PREFLIGHT_EGRESS, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml]
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
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N40_INTEGRATION_OWNERSHIP, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_ownership.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml]
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
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_evidence_determinism.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/evidence_determinism.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_requirements_lineage.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N50_EVIDENCE_AUDIT_CONTROLS, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml]
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
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml]
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
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml, verify-live-proof, --node, N70_LIVE_UNIT_PROOF]
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
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml, verify-live-proof, --node, N80_LIVE_WORKBOOK_PROOF]
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
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml, verify-final-audit, --node, N90_REQUIREMENTS_FINAL_AUDIT]
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

---

## `controller/scan_node.py`

Node-scoped / complete-tree forbidden-reference scanner entry point. Unchanged since rc1. SHA-256 at snapshot time: `a68141343848f2cfdb5f4656f103c84c2d79a7883f01bf5bdd95c078ce33f11f`.

```python
#!/usr/bin/env python3
"""Package-v2 node-scoped and complete-tree forbidden-reference scanner.

This is execution package v2's own versioned entry point, required because
the parent v1 controller module
(``plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py``)
must not be edited by this package (see this package's ``implementation.graph.v4.yaml``
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

DEFAULT_GRAPH_PATH = _PACKAGE_DIR / "implementation.graph.v4.yaml"


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

---

## `tools/validate_plan_v2.py`

Package-v2 structural plan validator. Unchanged since rc1. SHA-256 at snapshot time: `18afb393c19adcf7eb1191b7f8d4286ee62134ce7ee2d6654e5e7bc1155ffc74`.

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
* ``result_pattern`` must live under this package's own ``results/`` root,
  never the parent v1 package's ``results/`` root or the failed correction's
  ``results/v2/`` root.
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
  under this package's own ``results/`` root, matching
  ``results/{node_id}.result.v1.json`` and ``results/evidence/{node_id}``
  exactly for that node's own ID -- never the parent v1 package's
  ``results/`` root nor the failed correction's ``results/v2/`` root.
* ``N60_ADVERSARIAL_REGRESSION`` must be the only node whose ``scan_node.py``
  verification command omits ``--node`` (complete-tree mode); every other
  node that invokes ``scan_node.py`` must do so in node-scoped mode.
* ``runtime/langgraph_factory/egress.py`` and
  ``tests/runtime/test_plan26_egress.py`` must be owned by
  ``N20_PROVIDER_TRANSPORT`` and must be absent from
  ``N30_PREFLIGHT_EGRESS``'s write set; ``N30_PREFLIGHT_EGRESS`` must declare
  ``runtime/langgraph_factory/egress.py`` as a read-only input.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import jsonschema
import yaml


PACKAGE_DIR = Path(__file__).resolve().parents[1]
PLAN_DIR = PACKAGE_DIR.parent
REPO_ROOT = PLAN_DIR.parents[1]
GRAPH_PATH = PACKAGE_DIR / "implementation.graph.v4.yaml"
RESULT_SCHEMA_PATH = PLAN_DIR / "schemas/node_result.schema.v1.json"
APPROVAL_SCHEMA_PATH = PLAN_DIR / "schemas/spec_approval.schema.v1.json"
RESULT_VALIDATOR_PATH = PACKAGE_DIR / "tools/validate_result_v2.py"
SCAN_NODE_PATH = PACKAGE_DIR / "controller/scan_node.py"

REQUIRED_SOURCE_SPEC = "plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md"
REQUIRED_SOURCE_SPEC_SHA256 = "e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c"
RESULT_PATTERN_PREFIX = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/"
NODE_SCOPED_SCAN_NODES = {
    "N20_PROVIDER_TRANSPORT",
    "N30_PREFLIGHT_EGRESS",
    "N40_INTEGRATION_OWNERSHIP",
    "N50_EVIDENCE_AUDIT_CONTROLS",
}
EGRESS_MODULE = "runtime/langgraph_factory/egress.py"
EGRESS_TEST = "tests/runtime/test_plan26_egress.py"


class ValidationError(RuntimeError):
    pass


def repo_path(value: str) -> Path:
    return REPO_ROOT / value


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
    import hashlib

    digest = hashlib.sha256(spec_path.read_bytes()).hexdigest()
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
    graph_flag = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml"
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
    for root_value in test_scan["scan_roots"]:
        if not repo_path(root_value).is_dir():
            raise ValidationError(f"active test scan root does not exist: {root_value}")
    test_terms = [value.casefold() for value in test_scan["prohibited_terms"]]
    scan_node_relative = SCAN_NODE_PATH.relative_to(REPO_ROOT).as_posix()
    affected_owners: set[str] = set()
    for root_value in test_scan["scan_roots"]:
        root_path = repo_path(root_value)
        for test_path in sorted(root_path.rglob("*.py")):
            relative = test_path.relative_to(REPO_ROOT).as_posix()
            text = test_path.read_text(encoding="utf-8").casefold()
            if not any(term in text for term in test_terms):
                continue
            owners = owners_of(nodes, relative)
            if len(owners) != 1:
                raise ValidationError(
                    f"migration-affected active test must have exactly one owner: "
                    f"{relative} -> {owners}"
                )
            affected_owners.add(owners[0])
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
        validate_schema_file(APPROVAL_SCHEMA_PATH)
        validate_result_schema_semantics()
        graph = load_yaml(GRAPH_PATH)
        order = validate_graph(graph)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, jsonschema.SchemaError, ValidationError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, sort_keys=True))
        return 1
    print(json.dumps({"valid": True, "graph_id": graph["graph_id"], "order": order}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## `tools/validate_result_v2.py`

Package-v2 result validator entry point. Unchanged since rc1. SHA-256 at snapshot time: `6b6b1c261864a95e009a663224bce127527c29ad4fd414e9c9c2013f9d40d89a`.

```python
#!/usr/bin/env python3
"""Validate one Run 27 node result against the package-v2 graph, paths, and hashes.

This is execution package v2's own versioned entry point. It is bound to
this package's own ``implementation.graph.v4.yaml``, never to the parent v1
package's graph -- there is no ``--graph`` flag to omit here, because this
script has exactly one graph binding and it is this package's own file.
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
GRAPH_PATH = PACKAGE_DIR / "implementation.graph.v4.yaml"


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

---

## `tests/test_execution_package_v2.py`

Automated proof suite for PKGV2-T01..T11, extended with the RC1-QA-001 fresh-prompt graph-reference regression tests. SHA-256 at snapshot time: `72481922a4b6df1754e962f9c801902b228ffa986669d1392426ddfd2d70f7c7`.

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

PACKAGE_GRAPH = PACKAGE_DIR / "implementation.graph.v4.yaml"
SCAN_NODE = PACKAGE_CONTROLLER_DIR / "scan_node.py"
VALIDATE_PLAN_V2 = PACKAGE_TOOLS_DIR / "validate_plan_v2.py"
VALIDATE_RESULT_V2 = PACKAGE_TOOLS_DIR / "validate_result_v2.py"
PACKAGE_PROMPTS_DIR = PACKAGE_DIR / "prompts"

for _dir in (str(PACKAGE_CONTROLLER_DIR), str(PARENT_CONTROLLER_DIR)):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

import scan_node as scanner  # noqa: E402
from core import Graph  # noqa: E402


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
    code, payload = run(
        [str(SCAN_NODE), "--node", "N20_PROVIDER_TRANSPORT", "--graph", str(PACKAGE_GRAPH), "--json"]
    )
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
    prefix = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/"
    assert f"{prefix}{node_id}.result.v1.json" in writes
    assert f"{prefix}evidence/{node_id}" in writes
    for write in writes:
        if "/results/" in write:
            assert write.startswith(prefix), f"{node_id}: {write!r} is not under the package-v2 results root"


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
    package_result = (
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/"
        "results/N40_INTEGRATION_OWNERSHIP.result.v1.json"
    )
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
    package_evidence = (
        "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/"
        "results/evidence/N50_EVIDENCE_AUDIT_CONTROLS"
    )
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
    """No node has executed under this package, so this proves the tool is
    correctly wired to this package's own graph/result root without
    fabricating a result artifact."""

    code, payload = run([str(VALIDATE_RESULT_V2), "--node", "N00_SPEC_APPROVAL_GATE"])
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
    assert process.stdout.strip() == "", process.stdout


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

# Matches an explicit `--graph <path>` flag value inside a shell command shown
# in prompt text, e.g. "...scan_node.py --node N20_PROVIDER_TRANSPORT --graph
# execution_package_v2/implementation.graph.v4.yaml".
_GRAPH_FLAG_PATTERN = re.compile(r"--graph\s+(\S+\.yaml)")

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


def _enforced_graph_suffix() -> str:
    return f"execution_package_v2/{PACKAGE_GRAPH.name}"


def _fresh_prompt_path(node_id: str) -> Path:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    return REPO_ROOT / document["nodes"][node_id]["prompt"]


@pytest.mark.parametrize("node_id", FRESH_PROMPT_NODE_IDS)
def test_each_fresh_prompt_references_the_exact_enforced_graph(node_id: str) -> None:
    """RC1-QA-001 regression: the graph-bound prompt for N00/N20/N30 must
    reference this package's actually enforced graph file -- never a missing,
    stale, or mismatched one."""

    prompt_path = _fresh_prompt_path(node_id)
    text = prompt_path.read_text(encoding="utf-8")
    references = _graph_references(text)
    assert references, f"{node_id}: prompt {prompt_path} contains no graph-path reference at all"
    expected_suffix = _enforced_graph_suffix()
    for reference in references:
        assert reference.endswith(expected_suffix), (
            f"{node_id}: prompt {prompt_path} references {reference!r}, which does not "
            f"resolve to the enforced graph ({expected_suffix!r})"
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
    expected_suffix = _enforced_graph_suffix()
    assert any(not reference.endswith(expected_suffix) for reference in references), (
        f"{node_id}: expected the superseded v3 prompt's stale graph reference to be "
        "caught as mismatched by this check, but every reference it found already "
        "matches the enforced graph -- the check would not have caught RC1-QA-001"
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
        assert not mutated.endswith(_enforced_graph_suffix())
```

---

## `prompts/N00_spec_approval_gate.prompt.v4.md`

N00 gate prompt, corrected: now requires implementation.graph.v4.yaml to exist, not the nonexistent v1 filename. SHA-256 at snapshot time: `06200109bbaca5513ba4738164d818a8cdc84caaf3527923495880b88165dea9`.

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
does not supersede them in place, it gates a new, independent package. This
v4 prompt corrects `N00_spec_approval_gate.prompt.v3.md`, which named a
stale, nonexistent graph filename left over from an earlier package
generation instead of this package's actually enforced and bound graph,
`implementation.graph.v4.yaml` — the exact class of defect an
independent QA round found in this package's own release-candidate process
(`RC1-QA-001`). The v3 file is preserved unchanged as historical record.

This node is a gate, not a specification-writing or graph-writing task. Do
not create, edit, approve, or repair the v4 specification artifact, this
package's own graph, QA evidence, an approval record, runtime, tests,
policy, or any Plan 26/Run 27 v1 or failed-v2 historical artifact. Its only
authorized writes are its own result and evidence directory under
`execution_package_v2/results/`.

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
4. Require this package's own execution-package QA result
   (`execution_package_v2/QA/`) to exist with the same witnessed,
   hash-chain-valid `QA_PASSED` discipline, verified the same way.
5. Require `execution_package_v2/implementation.graph.v4.yaml` to exist, to
   declare `version: 2`, to validate via
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`,
   and to declare `source_spec` as the specification path above.
6. Validate a new `execution_package_v2/contracts/spec_approval.v1.yaml`
   against `plans/27_langgraph_curriculum_factory_remediation/schemas/spec_approval.schema.v1.json`
   with format checking enabled. (The schema itself is frozen and
   unversioned per `rules.frozen_before_entry`; only the approval record is
   new to this package.)
7. Recompute digests and require exact equality across: the specification
   file, its QA verification artifact hash, this package's graph file, this
   package's QA verification artifact hash, and the corresponding hashes
   bound inside the approval record.
8. Require the approval record to authorize `plan27_implementation_remediation`
   and to carry the exact Claude model/effort decision already supplied by
   the user for `USER_DECISION_REQUIRED-01`, unchanged from
   `plans/27_langgraph_curriculum_factory_remediation/contracts/spec_approval.v1.yaml`'s
   `approval_statement`.
9. Enumerate every `USER_DECISION_REQUIRED` item in the specification. If
   any affects a node's intended implementation and lacks a separately
   recorded answer, block.
10. Prove no Run 27 v1 result, evidence file, receipt, patch, log, the v1
    execution graph, the failed `implementation.graph.v2.yaml` and its QA
    session, runtime, test, policy, or model-job file was changed by this
    node.
11. Record command output and hashes under
    `execution_package_v2/results/evidence/N00_SPEC_APPROVAL_GATE/` and emit
    a JSON result conforming to
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

---

## `prompts/N20_provider_transport.prompt.v4.md`

N20 provider-transport prompt, corrected: both scan_node.py --graph bindings now point at implementation.graph.v4.yaml. SHA-256 at snapshot time: `f9e468c92b1c0afabfbb07c475b45f8c2de42187264827c274672858cbe16200`.

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
--graph execution_package_v2/implementation.graph.v4.yaml`**, explicitly
bound to this package's own graph (never the parent v1 package's graph, and
never omitting `--graph`, which is exactly the defect an independent QA
round found in this package's own predecessor attempt,
`implementation.graph.v2.yaml`'s `PKG-QA-001` finding) — instead of the bare
whole-tree form N60 alone still runs. This v4 prompt further corrects
`N20_provider_transport.prompt.v3.md`, which bound this same command to
`implementation.graph.v1.yaml`, a filename that does not exist in this
package, instead of the package's actually enforced graph,
`implementation.graph.v4.yaml` — an independent QA round found this exact
defect (`RC1-QA-001`) in this package's release-candidate process. The v3
file is preserved unchanged as historical record.

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
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py --node N20_PROVIDER_TRANSPORT --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml`
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

---

## `prompts/N30_preflight_egress.prompt.v4.md`

N30 preflight-egress prompt, corrected: the required zero-occurrence scan's --graph binding now points at implementation.graph.v4.yaml. SHA-256 at snapshot time: `37e983cc0b68f9140514ae4a71479951d2707d33c82b74ce7db83d8d5076d465`.

```markdown
# GOAL

Make preflight, authentication, authorization, and the production CLI
truthful for the approved subscription-only production drivers, consuming
the `anthropic`/`openai`/`primary_source_hosts` egress boundary N20 now owns
and proves (moved from N30's v1 write set to N20's, per this package's
correction of N20-F02 — see `N20_provider_transport.prompt.v4.md`). Correct
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
not something to patch locally. This v4 prompt further corrects
`N30_preflight_egress.prompt.v3.md`, which bound its required zero-occurrence
scan to `implementation.graph.v1.yaml`, a filename that does not exist in
this package, instead of the package's actually enforced graph,
`implementation.graph.v4.yaml` — an independent QA round found this exact
defect (`RC1-QA-001`) in this package's release-candidate process. The v3
file is preserved unchanged as historical record.

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
(`python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py --node N30_PREFLIGHT_EGRESS --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v4.yaml`)
to remain green.

# LOOP

Classify each failure as capability semantics, production call-site wiring,
CLI status/exit mapping, or test fixture. If the failure traces to
`egress.py`'s own boundary rather than how N30 calls it, stop and route it
to N20 rather than patching it here. Repair the owning layer and rerun the
production-path negative case plus the full N30 slice. Never make readiness
easier to obtain to satisfy a test.
```

