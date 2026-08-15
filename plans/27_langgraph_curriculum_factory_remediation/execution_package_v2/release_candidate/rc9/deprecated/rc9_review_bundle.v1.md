# Run 27 recovery rc9 review bundle

This is the single immutable artifact submitted to the independent QA gate. It
contains the exact active package-v8 recovery artifacts and the complete runtime
sources that implement the retrieval/security path. Every section records the
live file SHA-256 immediately before QA. The approved graph-v7 and improperly
modified recovery input are both embedded in full so byte preservation can be
checked without trusting narrative.

The criteria and deterministic validation record are embedded first. Runtime
test files are not duplicated in full because the package test suite plus the
recorded N20/N30 executions bind their executable outcomes; their live hashes
will be listed in the rc9 manifest and independently rechecked before admission.
No prior QA verdict is a verdict on this bundle.


## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc9/QA_criteria.rc9.v1.md

SHA-256: `f2b8151e42a44160147f3b7fccd8a9a875042c643868349e88fb1bc94f80856d`

<details><summary>Exact content</summary>

````
# QA criteria — Run 27 execution package v2 recovery rc9

The reviewed artifact is `rc9_review_bundle.v1.md`. Review it as the complete
versioned graph-v8 recovery candidate. Use the repository only for read-only
recomputation of hashes and commands named in the bundle. Do not treat earlier QA
verdicts as a verdict on rc9.

Report findings at severity `major` only when a realistic condition defeats a
numbered criterion. Put style or optional hardening in observations.

1. **RC9-T01 — v7 restoration and recovery preservation.** The live
   `implementation.graph.v7.yaml` hashes exactly to
   `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22`.
   The improperly modified bytes remain separately preserved at SHA-256
   `b6c17e81c6e32f32b86183d4577fe9a18894c0657504eca832e36d7daa17865e`.
   Every existing `results/v7/` artifact is preserved and graph v7 is not an
   admission target.
2. **RC9-T02 — true v8 versioning.** Graph v8, schema v5, contract v5, the
   three v8 prompts, scanner, validators, and tests all bind to graph v8 and
   `results/v8/`. No v8 result/evidence path collides with the legacy flat
   results root or `results/v7/`. Validator graph/schema/contract/result
   bindings are explicit and internally consistent.
3. **RC9-T03 — topology and authority unchanged.** Node order is exactly
   N00→N10→N20→N30→N40→N50→N60→N70→N80→N90; edges and legal terminals are
   unchanged. The approved source specification, its witnessed QA record, rc3
   package-structure approval, and all eight model/effort assignments are
   carried forward exactly. Execution remains subscription CLI-only.
4. **RC9-T04 — recovered ownership is complete and non-overlapping.** N30 owns
   `nodes/sources.py`, `runtime/run_curriculum.py`,
   `policy/retrieval_hosts.v1.yaml`, `schemas/curriculum.schema.v5.json`,
   the selected arduino manifest, and direct N30 tests. N40 owns
   `nodes/__init__.py`. N20 retains sole ownership of `egress.py` and its
   direct tests; N30 consumes it read-only. No write path has two owners.
5. **RC9-T05 — WebSearch is locator-only and M01-only.** Only M01 DISCOVER may
   receive Claude WebSearch. Its output is an untrusted locator candidate.
   It cannot become admitted evidence without deterministic SourceRetriever
   fetch, validation, content hashing, and receipt creation. No other worker
   receives WebSearch or unrestricted tooling.
6. **RC9-T06 — named exact-host policy.** Curricula select a named profile and
   cannot supply hosts. The electronics profile contains exactly:
   `learn.sparkfun.com`, `docs.arduino.cc`, `www.arduino.cc`,
   `learn.adafruit.com`, `support.microbit.org`, `www.cpsc.gov`, and
   `www.allaboutcircuits.com`. Wildcards, URLs, mixed-case hosts, duplicate
   hosts, unknown profiles, and model-driven expansion fail closed.
7. **RC9-T07 — per-hop retrieval enforcement.** SourceRetriever remains the
   only fetch path and enforces HTTPS, exact host, DNS resolution, public-IP
   and rebinding checks, redirects at every hop, redirect bounds, response
   size/type/status limits, authorization/data-class matching, content hash,
   and receipt append. Model endpoints and private/link-local/loopback
   addresses fail closed.
8. **RC9-T08 — policy binding and bounded failure.** The selected profile,
   resolved ordered hosts, and policy-file digest are bound into authorization
   and execution evidence. Missing/unknown policy or an unavailable verified
   source yields a typed bounded failure, never a fabricated URL, fake receipt,
   vacuous success, alternate-provider fallback, or `NOT_AVAILABLE`
   substitution for a repairable subscription path.
9. **RC9-T09 — billed model paths remain impossible.** No billed API key,
   provider SDK, direct model HTTP call, custom endpoint, alternate provider,
   wildcard authority, or unrestricted worker environment can activate a
   production model route. Claude and Codex subscription CLIs retain their
   approved model/effort identities.
10. **RC9-T10 — positive and negative automated proof.** The package suite and
    N20/N30 runtime suites genuinely exercise the exact-host loader,
    unknown/wildcard/URL rejection, source fetch authorization, HTTPS/SSRF/DNS
    rebinding/redirect denial, M01-only WebSearch grant, untrusted-locator
    validation, policy binding, and versioned graph/result invariants. The
    deterministic validation record must match executable repository behavior,
    not merely narrative.
11. **RC9-T11 — baseline exception is proved, not waived.** The only permitted
    legacy N10 mismatch is reproduced against unmodified `HEAD`; the live and
    `git show HEAD` bytes have the same stated hash and differ from the older
    hash in the admitted historical result. No v8 result may inherit that
    mismatch.
12. **RC9-T12 — historical preservation and executable plan.** rc1–rc8, their
    QA sessions, all earlier graphs/schemas/contracts/prompts, v7 results and
    evidence, and failed live attempts remain readable and unmodified. The
    active plan validator returns `valid:true`, the package suite passes, and
    the v8 graph has a collision-free executable route through N90.

Falsify the bundle's claims where possible. Pay particular attention to a host
being checked only before the first request but not after redirects/DNS changes;
WebSearch data bypassing SourceRetriever; graph-v8 write ownership omitting a
live-modified file; stale v7 paths hidden in v8 prompts/validators; a structured
contract digest disagreeing with live bytes; and tests whose fixture bypasses the
production call site.
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc9/validation.v1.md

SHA-256: `3e5f3842ad6db6a7306cb1fbc3d20e14d3f673b86a2d850c00ceb279ecb154ee`

<details><summary>Exact content</summary>

````
# RC9 deterministic validation

All commands ran from `/Users/filipepinto/Projects/curriculum_builder` on 2026-08-14.

## N20 full verification

```
$ python3 -m pytest -q tests/runtime/test_plan26_transport.py tests/runtime/test_plan26_model_nodes.py tests/runtime/test_plan26_egress.py tests/runtime/test_capabilities.py tests/runtime/test_curriculum_factory_graph.py tests/runtime/test_plan26_adversarial.py tests/runtime/test_plan26_api_contract.py tests/runtime/test_plan26_lock_drift.py
489 passed, 1 skipped, 140 subtests passed in 28.31s
exit_code=0
```

## N30 CLI and production path

```
$ python3 -m pytest -q tests/runtime/test_plan26_cli.py tests/runtime/test_run_curriculum.py
62 passed, 27 subtests passed in 31.13s
exit_code=0
```

## N30 D03/D06B capability slice

```
$ python3 -m pytest -q tests/runtime/test_plan26_deterministic_nodes.py -k 'D03 or capability or D06B'
18 passed, 234 deselected in 0.13s
exit_code=0
```

## Execution-package v8 suite

```
$ python3 -m pytest -q plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py
175 passed in 11.49s
exit_code=0
```

## Active plan validator

```
$ python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py
{"graph_id":"plan27_langgraph_curriculum_factory_remediation","order":["N00_SPEC_APPROVAL_GATE","N10_HARNESS_PROTOCOL","N20_PROVIDER_TRANSPORT","N30_PREFLIGHT_EGRESS","N40_INTEGRATION_OWNERSHIP","N50_EVIDENCE_AUDIT_CONTROLS","N60_ADVERSARIAL_REGRESSION","N70_LIVE_UNIT_PROOF","N80_LIVE_WORKBOOK_PROOF","N90_REQUIREMENTS_FINAL_AUDIT"],"valid":true}
exit_code=0
```

## Active scoped scanners

```
N20: {"mode":"node","node_id":"N20_PROVIDER_TRANSPORT","ok":true,"scanned_files":35,"violations":[]}
N30: {"mode":"node","node_id":"N30_PREFLIGHT_EGRESS","ok":true,"scanned_files":6,"violations":[]}
```

## Proven baseline exception

The legacy parent-package N10 result validator reports a changed-file hash mismatch for
`plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py`.
The active v8 package test proves this classification against unmodified `HEAD`: the
live file and `git show HEAD:<path>` both hash to
`9ce7fe5b187620968ce289f73bbfc48a38ed1262386c25dc15116d0d8b3b2436`.
The historical N10 result recorded the older hash
`be50925aa5508310a505c438f979597402e006ef3e03746ad186b2451c045e4c`.
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml

SHA-256: `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`

<details><summary>Exact content</summary>

````
graph_id: plan27_langgraph_curriculum_factory_remediation
version: 2
status: SCAFFOLDED_BLOCKED_BY_SPEC_APPROVAL
source_incident: plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec_correction.result.v1.md
source_spec: plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md
runner: plans/27_langgraph_curriculum_factory_remediation/run.prompt.md
qa_criteria: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/qa_criteria.v1.md
node_result_schema: plans/27_langgraph_curriculum_factory_remediation/schemas/node_result.schema.v1.json
entry: N00_SPEC_APPROVAL_GATE
result_pattern: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/{node_id}.result.v1.json


# implementation.graph.v8.yaml is the versioned recovery successor to the
# approved graph-v7 artifact. The approved v7 bytes are restored and preserved
# at SHA-256 b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22.
# A later in-place v7 mutation (SHA-256
# b6c17e81c6e32f32b86183d4577fe9a18894c0657504eca832e36d7daa17865e)
# is preserved byte-for-byte under recovery/ and is used only as recovery
# input. No new result is admitted under v7.
#
# Graph v8 carries forward the live-proven ownership corrections from that
# recovery input without changing the approved node order, edges, terminals,
# model assignments, provider architecture, or subscription-only execution
# design. N30 owns runtime/langgraph_factory/nodes/sources.py, the versioned
# exact-host retrieval policy, the curriculum schema hook, and this run's
# selected curriculum manifest; N40 owns nodes/__init__.py. These additions
# close write-set defects exposed by genuine N70 production executions.
#
# The retrieval policy is closed and versioned: M01 DISCOVER alone may use
# Claude WebSearch to produce untrusted locator candidates; SourceRetriever
# remains the sole fetch/validate/hash/receipt path. Curricula select a named
# policy profile and cannot inject hosts. Every hop requires HTTPS, exact-host
# admission, DNS/IP SSRF checks, redirect revalidation, and the active policy
# digest/resolved-host binding. An unavailable verified source is a typed,
# bounded failure. No wildcard, model-driven authority expansion, billed API
# key, direct model HTTP call, or unrestricted worker tooling is permitted.
#
# All fresh results and evidence live under the collision-free results/v8/
# namespace. The v8 prompt, schema, contract, controller, validator, test, and
# release-candidate bindings are versioned together. Historical graph, release
# candidate, QA, result, receipt, evidence, and live-attempt artifacts remain
# immutable and readable.

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
    - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v5.json
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
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N00_spec_approval_gate.prompt.v8.md
    depends_on: []
    writes:
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N00_SPEC_APPROVAL_GATE.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N00_SPEC_APPROVAL_GATE
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
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N10_HARNESS_PROTOCOL.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N10_HARNESS_PROTOCOL
    verification:
      - [python3, -m, pytest, -q, plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_node_result_protocol.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N10_HARNESS_PROTOCOL]
    allowed_results: [PASSED, BLOCKED]

  N20_PROVIDER_TRANSPORT:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N20_provider_transport.prompt.v8.md
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
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N20_PROVIDER_TRANSPORT.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N20_PROVIDER_TRANSPORT
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_transport.py, tests/runtime/test_plan26_model_nodes.py, tests/runtime/test_plan26_egress.py, tests/runtime/test_capabilities.py, tests/runtime/test_curriculum_factory_graph.py, tests/runtime/test_plan26_adversarial.py, tests/runtime/test_plan26_api_contract.py, tests/runtime/test_plan26_lock_drift.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N20_PROVIDER_TRANSPORT, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N20_PROVIDER_TRANSPORT]
    allowed_results: [PASSED, BLOCKED]

  N30_PREFLIGHT_EGRESS:
    prompt: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N30_preflight_egress.prompt.v8.md
    depends_on: [N20_PROVIDER_TRANSPORT]
    writes:
      - runtime/langgraph_factory/nodes/inputs.py
      # nodes/sources.py added live (N30V7-F03/N20V7-F11 lineage): D06B's own
      # call into egress.py's SourceRetriever.fetch is the only caller of that
      # method's keyword-only authorization_receipt/data_class contract, and no
      # node's write set covered this file until a real N70 production run hit
      # a genuine TypeError there (SourceRetriever.fetch() takes 2 positional
      # arguments but 4 were given). egress.py's fetch signature itself
      # (N20-owned, N30 read-only) is correct and already test-covered exactly
      # as called correctly elsewhere; the defect is this call site.
      - runtime/langgraph_factory/nodes/sources.py
      - runtime/run_curriculum.py
      # Added live (N30V7-F07, user-directed spec decision): the retrieval host
      # allowlist policy, its curriculum-manifest schema hook, and the one
      # curriculum this run exercises, so a named profile can be declared and
      # resolved end to end. egress.py's loader (N20-owned) is called, not
      # written, from here.
      - policy/retrieval_hosts.v1.yaml
      - schemas/curriculum.schema.v5.json
      - curricula/arduino_kit/arduino_kit_curriculum.v5.yaml
      - tests/runtime/test_plan26_cli.py
      - tests/runtime/test_plan26_deterministic_nodes.py
      - tests/runtime/test_run_curriculum.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N30_PREFLIGHT_EGRESS.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N30_PREFLIGHT_EGRESS
    read_only_inputs:
      - runtime/langgraph_factory/egress.py
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_cli.py, tests/runtime/test_run_curriculum.py]
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_deterministic_nodes.py, -k, "D03 or capability or D06B"]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N30_PREFLIGHT_EGRESS, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml]
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
      # nodes/__init__.py added live (N40V7-F13, sibling to the N40V7-F12
      # graph.py boundary fix): deterministic_node's own ExpectedFailure catch
      # has the identical missing-terminal_candidate gap `_boundary` had --
      # same architectural concern, different layer -- and no node's write set
      # covered this file until a real N70 production run hit it (D06B's
      # PrerequisitePause/SystemFailure classification, uncaught until here).
      - runtime/langgraph_factory/nodes/__init__.py
      - tests/runtime/test_plan26_topology.py
      - tests/runtime/test_plan26_unit_graph.py
      - tests/runtime/test_plan26_repair_acceptance.py
      - tests/runtime/test_plan26_workbook.py
      - plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N40_INTEGRATION_OWNERSHIP.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N40_INTEGRATION_OWNERSHIP
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_topology.py, tests/runtime/test_plan26_unit_graph.py, tests/runtime/test_plan26_repair_acceptance.py, tests/runtime/test_plan26_workbook.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N40_INTEGRATION_OWNERSHIP, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_ownership.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml]
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
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N50_EVIDENCE_AUDIT_CONTROLS.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N50_EVIDENCE_AUDIT_CONTROLS
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_evidence.py, tests/runtime/test_plan26_persistence.py]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_evidence_determinism.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/evidence_determinism.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/verify_requirements_lineage.py, --contract, plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --node, N50_EVIDENCE_AUDIT_CONTROLS, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N50_EVIDENCE_AUDIT_CONTROLS]
    allowed_results: [PASSED, BLOCKED]

  N60_ADVERSARIAL_REGRESSION:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N60_adversarial_regression.prompt.v1.md
    depends_on: [N50_EVIDENCE_AUDIT_CONTROLS]
    writes:
      - tests/runtime/test_plan27_adversarial.py
      - plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_adversarial.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N60_ADVERSARIAL_REGRESSION.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N60_ADVERSARIAL_REGRESSION
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan27_adversarial.py, plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_adversarial.py]
      - [python3, -m, pytest, -q, tests/runtime]
      - [python3, -m, pytest, -q, plans/27_langgraph_curriculum_factory_remediation/tests]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N60_ADVERSARIAL_REGRESSION]
    allowed_results: [PASSED, BLOCKED]

  N70_LIVE_UNIT_PROOF:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N70_live_unit_proof.prompt.v1.md
    depends_on: [N60_ADVERSARIAL_REGRESSION]
    writes:
      - outputs/run27/live_unit
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N70_LIVE_UNIT_PROOF.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N70_LIVE_UNIT_PROOF
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml, verify-live-proof, --node, N70_LIVE_UNIT_PROOF]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N70_LIVE_UNIT_PROOF]
    allowed_results: [PASSED, NOT_AVAILABLE, BLOCKED]

  N80_LIVE_WORKBOOK_PROOF:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N80_live_workbook_proof.prompt.v1.md
    depends_on: [N70_LIVE_UNIT_PROOF]
    writes:
      - outputs/run27/live_workbook
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N80_LIVE_WORKBOOK_PROOF.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N80_LIVE_WORKBOOK_PROOF
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml, verify-live-proof, --node, N80_LIVE_WORKBOOK_PROOF]
      - [python3, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py, --node, N80_LIVE_WORKBOOK_PROOF]
    allowed_results: [PASSED, NOT_AVAILABLE, BLOCKED]
    read_only_inputs:
      - outputs/run27/live_unit

  N90_REQUIREMENTS_FINAL_AUDIT:
    prompt: plans/27_langgraph_curriculum_factory_remediation/prompts/N90_requirements_final_audit.prompt.v1.md
    depends_on: [N80_LIVE_WORKBOOK_PROOF]
    writes:
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/N90_REQUIREMENTS_FINAL_AUDIT.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/evidence/N90_REQUIREMENTS_FINAL_AUDIT
    verification:
      - [python3, plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py, --graph, plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml, verify-final-audit, --node, N90_REQUIREMENTS_FINAL_AUDIT]
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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml

SHA-256: `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22`

<details><summary>Exact content</summary>

````
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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/recovery/implementation.graph.v7.modified.b6c17e81.yaml

SHA-256: `b6c17e81c6e32f32b86183d4577fe9a18894c0657504eca832e36d7daa17865e`

<details><summary>Exact content</summary>

````
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
      # nodes/sources.py added live (N30V7-F03/N20V7-F11 lineage): D06B's own
      # call into egress.py's SourceRetriever.fetch is the only caller of that
      # method's keyword-only authorization_receipt/data_class contract, and no
      # node's write set covered this file until a real N70 production run hit
      # a genuine TypeError there (SourceRetriever.fetch() takes 2 positional
      # arguments but 4 were given). egress.py's fetch signature itself
      # (N20-owned, N30 read-only) is correct and already test-covered exactly
      # as called correctly elsewhere; the defect is this call site.
      - runtime/langgraph_factory/nodes/sources.py
      - runtime/run_curriculum.py
      # Added live (N30V7-F07, user-directed spec decision): the retrieval host
      # allowlist policy, its curriculum-manifest schema hook, and the one
      # curriculum this run exercises, so a named profile can be declared and
      # resolved end to end. egress.py's loader (N20-owned) is called, not
      # written, from here.
      - policy/retrieval_hosts.v1.yaml
      - schemas/curriculum.schema.v5.json
      - curricula/arduino_kit/arduino_kit_curriculum.v5.yaml
      - tests/runtime/test_plan26_cli.py
      - tests/runtime/test_plan26_deterministic_nodes.py
      - tests/runtime/test_run_curriculum.py
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N30_PREFLIGHT_EGRESS.result.v1.json
      - plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/evidence/N30_PREFLIGHT_EGRESS
    read_only_inputs:
      - runtime/langgraph_factory/egress.py
    verification:
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_cli.py, tests/runtime/test_run_curriculum.py]
      - [python3, -m, pytest, -q, tests/runtime/test_plan26_deterministic_nodes.py, -k, "D03 or capability or D06B"]
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
      # nodes/__init__.py added live (N40V7-F13, sibling to the N40V7-F12
      # graph.py boundary fix): deterministic_node's own ExpectedFailure catch
      # has the identical missing-terminal_candidate gap `_boundary` had --
      # same architectural concern, different layer -- and no node's write set
      # covered this file until a real N70 production run hit it (D06B's
      # PrerequisitePause/SystemFailure classification, uncaught until here).
      - runtime/langgraph_factory/nodes/__init__.py
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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py

SHA-256: `e3c9bd8c10ff8b7c19a115a13e82a04607db664858cfd908bee0d698fc57d376`

<details><summary>Exact content</summary>

````
#!/usr/bin/env python3
"""Package-v2 node-scoped and complete-tree forbidden-reference scanner.

This is execution package v2's own versioned entry point, required because
the parent v1 controller module
(``plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py``)
must not be edited by this package (see this package's ``implementation.graph.v8.yaml``
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

DEFAULT_GRAPH_PATH = _PACKAGE_DIR / "implementation.graph.v8.yaml"


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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py

SHA-256: `4c75464ba5277934a3f48a455df99455d3d3cb7f32f0b1b8cec2fb5ad566b4dc`

<details><summary>Exact content</summary>

````
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
* ``result_pattern`` must live under this package's own ``results/v8/`` root
  -- never the parent v1 package's ``results/`` root, the failed correction's
  ``results/v2/`` root, nor this package's own earlier
  ``results/`` root (where the graph-v5-and-earlier-lineage admitted
  N00/N10 results and the BLOCKED N20 result permanently live; reusing that
  path was RC8's own defect, see ``implementation.graph.v8.yaml``'s header).
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
  under this package's own ``results/v8/`` root, matching
  ``results/v8/{node_id}.result.v1.json`` and ``results/v8/evidence/{node_id}``
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
forward unchanged in graph v8 (which fixes only the unrelated
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
GRAPH_PATH = PACKAGE_DIR / "implementation.graph.v8.yaml"
RESULT_SCHEMA_PATH = PLAN_DIR / "schemas/node_result.schema.v1.json"
# This package's own package-scoped approval schema (execution_package_v2/schemas/),
# never the parent v1 package's plans/27_.../schemas/spec_approval.schema.v1.json --
# that schema const-locks approved_spec to the *parent* package's own spec and
# cannot validate this package's approval record no matter how it is filled in
# (the exact defect implementation.graph.v5.yaml's header documents fixing).
# Schema v5 (this package's current generation) const-locks approved_graph to
# implementation.graph.v8.yaml instead of v6, correcting the RC8 result-namespace
# collision; schema v3 remains, unedited, the frozen contract for records that
# still cite v6, exactly as schema v2 remains frozen for records citing v5.
CONTRACT_SCHEMA_PATH = PACKAGE_DIR / "schemas/spec_approval.schema.v5.json"
CONTRACT_PATH = PACKAGE_DIR / "contracts/spec_approval.v5.yaml"
RESULT_VALIDATOR_PATH = PACKAGE_DIR / "tools/validate_result_v2.py"
SCAN_NODE_PATH = PACKAGE_DIR / "controller/scan_node.py"

REQUIRED_SOURCE_SPEC = "plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md"
REQUIRED_SOURCE_SPEC_SHA256 = "e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c"
RESULT_PATTERN_PREFIX = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/"
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
    graph_flag = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml"
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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_result_v2.py

SHA-256: `867f4d7fece58fe4781cac6f4f69db0ec20a26cd693f770d66476d5ae5891460`

<details><summary>Exact content</summary>

````
#!/usr/bin/env python3
"""Validate one Run 27 node result against the package-v2 graph, paths, and hashes.

This is execution package v2's own versioned entry point. It is bound to
this package's own ``implementation.graph.v8.yaml``, never to the parent v1
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
``--graph`` argument. RC8 (which introduced ``implementation.graph.v8.yaml``
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
GRAPH_PATH = PACKAGE_DIR / "implementation.graph.v8.yaml"


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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tests/test_execution_package_v2.py

SHA-256: `0750ed9169a1cfe92d0a7202066ab9f8bae26819e3e813ef83ef634e1360d0ba`

<details><summary>Exact content</summary>

````
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

PACKAGE_GRAPH = PACKAGE_DIR / "implementation.graph.v8.yaml"
APPROVED_GRAPH_V7 = PACKAGE_DIR / "implementation.graph.v7.yaml"
RECOVERY_GRAPH_V7_MODIFIED = PACKAGE_DIR / "recovery/implementation.graph.v7.modified.b6c17e81.yaml"
DEPRECATED_GRAPH_V4 = PACKAGE_DIR / "deprecated/implementation.graph.v4.yaml"
DEPRECATED_GRAPH_V5 = PACKAGE_DIR / "deprecated/implementation.graph.v5.yaml"
DEPRECATED_GRAPH_V6 = PACKAGE_DIR / "deprecated/implementation.graph.v6.yaml"
CONTRACT_SCHEMA_V2 = PACKAGE_DIR / "schemas/spec_approval.schema.v2.json"
CONTRACT_V2 = PACKAGE_DIR / "contracts/spec_approval.v2.yaml"
CONTRACT_SCHEMA_V3 = PACKAGE_DIR / "schemas/spec_approval.schema.v3.json"
CONTRACT_V3 = PACKAGE_DIR / "contracts/spec_approval.v3.yaml"
CONTRACT_SCHEMA_V5 = PACKAGE_DIR / "schemas/spec_approval.schema.v5.json"
CONTRACT_V5 = PACKAGE_DIR / "contracts/spec_approval.v5.yaml"
PARENT_APPROVAL_SCHEMA_V1 = PLAN_DIR / "schemas/spec_approval.schema.v1.json"
RESULTS_V8_PREFIX = "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v8/"
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


def test_original_n10_result_failure_is_proven_pre_existing_at_head() -> None:
    code, payload = run([str(PARENT_TOOLS_DIR / "validate_result.py"), "--node", "N10_HARNESS_PROTOCOL"])
    assert code == 1
    assert payload["valid"] is False
    assert payload["error"] == (
        "N10_HARNESS_PROTOCOL: changed-file hash mismatch: "
        "plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py"
    )
    relative = "plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py"
    head_bytes = subprocess.run(
        ["git", "show", f"HEAD:{relative}"], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout
    assert hashlib.sha256(head_bytes).hexdigest() == sha256_file(REPO_ROOT / relative)
    assert sha256_file(REPO_ROOT / relative) == "9ce7fe5b187620968ce289f73bbfc48a38ed1262386c25dc15116d0d8b3b2436"


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
    implementation.graph.v8.yaml (v6 originally fixed this; v7 carries the
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


def test_complete_tree_mode_against_the_real_repo_is_clean_after_n60() -> None:
    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    report = scanner.run_complete_tree(graph)
    assert report["valid"]
    assert report["violations"] == []


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
    prefix = RESULTS_V8_PREFIX
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
    package_result = f"{RESULTS_V8_PREFIX}N40_INTEGRATION_OWNERSHIP.result.v1.json"
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
    package_evidence = f"{RESULTS_V8_PREFIX}evidence/N50_EVIDENCE_AUDIT_CONTROLS"
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
        "Use the whitespace form: --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml\n"
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
        "--graph other/execution_package_v2/implementation.graph.v8.yaml"
    )
    references = _graph_references(text)
    assert references == ["other/execution_package_v2/implementation.graph.v8.yaml"]
    assert not _resolves_to_enforced_graph(references[0])


@pytest.mark.parametrize(
    "flag_spelling",
    [
        "--graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml",
        "--graph=plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml",
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

CONTRACT_V5_DIGEST_FIELDS = [
    "approved_spec_sha256",
    "spec_qa_verification_sha256",
    "approved_rc_manifest_sha256",
    "execution_package_qa_verification_sha256",
    "approved_graph_sha256",
]


def _schema_v5() -> dict[str, Any]:
    return json.loads(CONTRACT_SCHEMA_V5.read_text(encoding="utf-8"))


def _contract_v4() -> dict[str, Any]:
    return yaml.safe_load(CONTRACT_V5.read_text(encoding="utf-8"))


def _write_mutated_contract_v4(tmp_path: Path, mutate) -> Path:
    contract = _contract_v4()
    mutate(contract)
    mutated_path = tmp_path / "spec_approval.v4.mutated.yaml"
    mutated_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
    return mutated_path


def test_graph_v8_declares_schema_v5_frozen_not_schema_v3_v2_or_the_parent_v1_schema() -> None:
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    frozen = document["rules"]["frozen_before_entry"]
    schema_v5_relative = CONTRACT_SCHEMA_V5.relative_to(REPO_ROOT).as_posix()
    schema_v3_relative = CONTRACT_SCHEMA_V3.relative_to(REPO_ROOT).as_posix()
    schema_v2_relative = CONTRACT_SCHEMA_V2.relative_to(REPO_ROOT).as_posix()
    parent_v1_relative = PARENT_APPROVAL_SCHEMA_V1.relative_to(REPO_ROOT).as_posix()
    assert schema_v5_relative in frozen
    assert schema_v3_relative not in frozen
    assert schema_v2_relative not in frozen
    assert parent_v1_relative not in frozen
    # node_result.schema.v1.json must remain -- adding schema v5 must not drop it.
    assert document["node_result_schema"] in frozen


def test_n00_prompt_v8_validates_against_schema_v5_not_schema_v3_v2_or_the_parent_v1_schema() -> None:
    """The prompt's own explanatory prose legitimately names the historical
    parent v1 schema and schemas v2/v3 (to explain the defect being fixed,
    exactly as prompt v6 named v2's stale-schema-binding defect) -- so a
    blanket "v3.json not in text" assertion would be too strict. What must
    actually be true is that the load-bearing validation instruction (TEST
    step 6) targets schema v5."""

    prompt_path = _fresh_prompt_path("N00_SPEC_APPROVAL_GATE")
    assert prompt_path.name == "N00_spec_approval_gate.prompt.v8.md"
    text = prompt_path.read_text(encoding="utf-8")
    assert (
        "Validate `execution_package_v2/contracts/spec_approval.v5.yaml` against\n"
        "   `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v5.json`"
    ) in text
    assert "Validate a new `execution_package_v2/contracts/spec_approval.v1.yaml`" not in text


def test_n00_prompt_v8_does_not_repeat_the_false_frozen_claim_about_schema_v1() -> None:
    prompt_path = _fresh_prompt_path("N00_SPEC_APPROVAL_GATE")
    text = prompt_path.read_text(encoding="utf-8")
    assert "is frozen and unversioned per" not in text


def test_schema_v5_spec_path_const_matches_graph_v8_source_spec() -> None:
    schema = _schema_v5()
    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    assert schema["properties"]["approved_spec"]["const"] == document["source_spec"]


def test_schema_v5_graph_path_const_matches_this_packages_own_active_graph() -> None:
    schema = _schema_v5()
    expected = PACKAGE_GRAPH.relative_to(REPO_ROOT).as_posix()
    assert schema["properties"]["approved_graph"]["const"] == expected


def test_schema_v5_spec_path_const_resolves_to_the_live_v4_specification_file() -> None:
    schema = _schema_v5()
    spec_path = REPO_ROOT / schema["properties"]["approved_spec"]["const"]
    assert spec_path.is_file()
    assert spec_path.name == "langgraph_curriculum_factory.spec.v4.md"


def test_contract_v4_validates_against_schema_v5() -> None:
    schema = _schema_v5()
    jsonschema.Draft202012Validator.check_schema(schema)
    contract = _contract_v4()
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(contract)


@pytest.mark.parametrize("field", CONTRACT_V5_DIGEST_FIELDS)
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
    """Four of contract v5's five digests must be the *same* already-approved
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


def test_validate_plan_v2_module_is_wired_to_schema_v5_not_schema_v3_v2_or_v1() -> None:
    assert validate_plan_v2.CONTRACT_SCHEMA_PATH == CONTRACT_SCHEMA_V5
    assert not hasattr(validate_plan_v2, "APPROVAL_SCHEMA_PATH")
    assert validate_plan_v2.GRAPH_PATH == PACKAGE_GRAPH


def test_validate_plan_v2_passes_end_to_end_against_the_live_contract() -> None:
    code, payload = run([str(VALIDATE_PLAN_V2)])
    assert code == 0, payload
    assert payload["valid"] is True


@pytest.mark.parametrize("field", CONTRACT_V5_DIGEST_FIELDS)
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
    schema v5's pattern alone accepts any rc<N> path shape. The validator
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
    lineage exists to fix -- proving schema v5 does not repeat it in reverse."""

    def _mutate(contract: dict[str, Any]) -> None:
        contract["approved_spec"] = "plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md"

    mutated_path = _write_mutated_contract_v4(tmp_path, _mutate)
    monkeypatch.setattr(validate_plan_v2, "CONTRACT_PATH", mutated_path)
    with pytest.raises(jsonschema.ValidationError):
        validate_plan_v2.validate_spec_approval_contract()


def test_validator_rejects_a_wrong_approved_graph_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A value naming graph v6 -- correct for schema v3, wrong for schema v5
    -- must still be rejected: schema v5's const genuinely moved to v7, it
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
# overwritten those exact files. implementation.graph.v8.yaml fixes this by
# moving result_pattern (and every node's own result/evidence write paths)
# to the versioned subdirectory execution_package_v2/results/v8/, whose
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


def test_graph_v8_result_pattern_never_collides_with_the_legacy_results_root() -> None:
    """The direct proof that the RC8 defect is fixed: graph v8's own
    result_pattern, formatted for every admitted/blocked node, never equals
    the exact legacy path those nodes' real results live at. results/v7/ is
    legitimately a subdirectory of results/ (that is not the defect -- the
    defect was reusing the exact same flat filename), so the proof is exact
    per-node path inequality, not path-prefix disjointness."""

    document = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    pattern = document["result_pattern"]
    assert pattern.startswith(RESULTS_V8_PREFIX)
    for filename in ADMITTED_OR_BLOCKED_RESULT_FILES:
        node_id = filename.rsplit(".result.v1.json", 1)[0]
        v7_path = pattern.format(node_id=node_id)
        legacy_path = f"{LEGACY_RESULTS_PREFIX}{filename}"
        assert v7_path != legacy_path
        assert (REPO_ROOT / v7_path).resolve() != (REPO_ROOT / legacy_path).resolve()


@pytest.mark.parametrize("node_id", ["N00_SPEC_APPROVAL_GATE", "N10_HARNESS_PROTOCOL", "N20_PROVIDER_TRANSPORT"])
def test_validate_result_v2_reports_missing_not_a_collision_for_admitted_nodes(node_id: str) -> None:
    """The live validator (bound to graph v8's own results/v7/ root) must
    honestly report the v7 result as missing for these three already-admitted
    nodes -- never fabricate a pass by reading the legacy v5-lineage file at
    the old path, and never raise from an accidental write. This is the
    behavioral proof that no code path in this validator can be tricked into
    treating the legacy file as this generation's own result."""

    code, payload = run([str(VALIDATE_RESULT_V2), "--node", node_id])
    assert code == 1
    assert payload["valid"] is False
    assert "missing result" in payload["error"]
    assert "results/v8" in payload["error"]


def test_graph_v8_carries_the_modified_recovery_input_in_versioned_form() -> None:
    """The live-mutated v7 bytes are recovery input, never an admission target.
    V8 preserves their approved topology and ownership corrections while moving
    operational bindings to v8."""

    recovered = yaml.safe_load(RECOVERY_GRAPH_V7_MODIFIED.read_text(encoding="utf-8"))
    v8 = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))

    assert sha256_file(APPROVED_GRAPH_V7) == "b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22"
    assert sha256_file(RECOVERY_GRAPH_V7_MODIFIED) == "b6c17e81c6e32f32b86183d4577fe9a18894c0657504eca832e36d7daa17865e"
    assert recovered["edges"] == v8["edges"]
    assert recovered["terminals"] == v8["terminals"]
    assert recovered["rules"]["forbidden_production_scan"] == v8["rules"]["forbidden_production_scan"]
    assert recovered["rules"]["retired_provider_test_scan"] == v8["rules"]["retired_provider_test_scan"]

    for node_id, recovered_node in recovered["nodes"].items():
        v8_node = v8["nodes"][node_id]
        assert recovered_node["depends_on"] == v8_node["depends_on"]
        assert recovered_node.get("read_only_inputs", []) == v8_node.get("read_only_inputs", [])
        assert recovered_node["allowed_results"] == v8_node["allowed_results"]

        def _non_result_writes(writes: list[str]) -> set[str]:
            return {w for w in writes if "/results/" not in w}

        assert _non_result_writes(recovered_node["writes"]) == _non_result_writes(v8_node["writes"])


def test_graph_v8_result_writes_are_the_recovery_writes_moved_under_results_v8() -> None:
    recovered = yaml.safe_load(RECOVERY_GRAPH_V7_MODIFIED.read_text(encoding="utf-8"))
    v8 = yaml.safe_load(PACKAGE_GRAPH.read_text(encoding="utf-8"))
    for node_id, recovered_node in recovered["nodes"].items():
        v8_node = v8["nodes"][node_id]
        recovered_results = {w for w in recovered_node["writes"] if "/results/" in w}
        v8_results = {w for w in v8_node["writes"] if "/results/" in w}
        expected_v8 = {w.replace("/results/v7/", "/results/v8/") for w in recovered_results}
        assert v8_results == expected_v8


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


def test_n60_adversarial_file_causes_no_scan_error_in_either_mode() -> None:
    """The prior v7 N60 produced this migration-owned file. Its presence must
    be scanned cleanly without changing v7's historical admission status."""

    graph = Graph.load(PACKAGE_GRAPH, REPO_ROOT)
    future_file = REPO_ROOT / "tests/runtime/test_plan27_adversarial.py"
    assert future_file.is_file()
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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N00_spec_approval_gate.prompt.v8.md

SHA-256: `04893339f0482440b242e789be276d89bb38e9753fa0c70ec7600ece04d21bb1`

<details><summary>Exact content</summary>

````
# GOAL

Recovery authority: `plans/26_langgraph_curriculum_factory/prompts/RUN27_GPT56_SOL_AUTONOMOUS_V8_RECOVERY_TO_N90.prompt.v1.md` explicitly approves this narrow versioned recovery. Approved v7 is immutable at SHA-256 `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22`; the in-place modified bytes are preserved under `execution_package_v2/recovery/` and are not an admission target. All fresh admissions use graph v8 and `results/v8/`.

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

This v8 recovery prompt corrects `N00_spec_approval_gate.prompt.v6.md`, which was
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
`execution_package_v2/schemas/spec_approval.schema.v5.json` (which
const-locks the right specification and this package's own active graph, now
`implementation.graph.v8.yaml`, instead of v6), the corresponding
`execution_package_v2/contracts/spec_approval.v5.yaml` (which carries
forward, not reinvents, the exact approval already recorded in
`spec_approval.v3.yaml`, updated only for the new graph's path/digest and
schema version), and `implementation.graph.v8.yaml` genuinely declares schema
v4 in its own `rules.frozen_before_entry`, moves `result_pattern` and every
node's own result/evidence write paths under the versioned subdirectory
`execution_package_v2/results/v8/` (whose per-node filenames never coincide
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
`execution_package_v2/results/v8/`.

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
5. Require `execution_package_v2/implementation.graph.v8.yaml` to exist, to
   declare `version: 2`, to validate via
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/tools/validate_plan_v2.py`,
   and to declare `source_spec` as the specification path above.
6. Validate `execution_package_v2/contracts/spec_approval.v5.yaml` against
   `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v5.json`
   with format checking enabled. This schema is *this package's own* frozen
   schema: it is declared in `implementation.graph.v8.yaml`'s own
   `rules.frozen_before_entry` (alongside `node_result.schema.v1.json`) —
   verify that declaration directly in the live graph file rather than
   trusting this prompt's own account of it. It is not the parent v1
   package's `spec_approval.schema.v1.json`, which remains that package's
   own frozen contract, exclusively, and is never loaded here.
7. Recompute digests and require exact equality across every value schema v5
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
    `execution_package_v2/results/v8/evidence/N00_SPEC_APPROVAL_GATE/` and
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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N20_provider_transport.prompt.v8.md

SHA-256: `1dc683636fa45a32004776e889da8cbfe656958575f7d4ea7c26a5782a6c0e26`

<details><summary>Exact content</summary>

````
# GOAL

Recovery authority: `plans/26_langgraph_curriculum_factory/prompts/RUN27_GPT56_SOL_AUTONOMOUS_V8_RECOVERY_TO_N90.prompt.v1.md` explicitly approves this narrow versioned recovery. Approved v7 is immutable at SHA-256 `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22`; the in-place modified bytes are preserved under `execution_package_v2/recovery/` and are not an admission target. All fresh admissions use graph v8 and `results/v8/`.

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
--graph execution_package_v2/implementation.graph.v8.yaml`**, explicitly
bound to this package's own graph (never the parent v1 package's graph, and
never omitting `--graph`, which is exactly the defect an independent QA
round found in this package's own predecessor attempt,
`implementation.graph.v2.yaml`'s `PKG-QA-001` finding) — instead of the bare
whole-tree form N60 alone still runs.

This v8 recovery prompt corrects `N20_provider_transport.prompt.v6.md`. That v6
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
result and evidence at their shared path. `implementation.graph.v8.yaml`
fixes this at the graph level: `result_pattern`, and every node's own
result-write and evidence-root entries in `writes` — including N20's own —
move under `execution_package_v2/results/v8/` instead of
`execution_package_v2/results/`. This node's own write set below already
reflects that move. N20's write set, the two egress paths, and the
N20V2-F01 scan-scope fix (`retired_provider_test_scan.scan_roots` as the
explicit migration-owned union) are otherwise unchanged in substance from
v6. This prompt's own `--graph` values now name
`implementation.graph.v8.yaml` instead of `implementation.graph.v6.yaml`,
the same rename `implementation.graph.v8.yaml`'s own header applies to the
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
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py --node N20_PROVIDER_TRANSPORT --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml`
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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/prompts/N30_preflight_egress.prompt.v8.md

SHA-256: `93ed1d4cc9766d4f1280fe84fc7f39d138e4aeb435586cd68e13ed65feb87874`

<details><summary>Exact content</summary>

````
# GOAL

Recovery authority: `plans/26_langgraph_curriculum_factory/prompts/RUN27_GPT56_SOL_AUTONOMOUS_V8_RECOVERY_TO_N90.prompt.v1.md` explicitly approves this narrow versioned recovery. Approved v7 is immutable at SHA-256 `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22`; the in-place modified bytes are preserved under `execution_package_v2/recovery/` and are not an admission target. All fresh admissions use graph v8 and `results/v8/`.

Make preflight, authentication, authorization, and the production CLI
truthful for the approved subscription-only production drivers, consuming
the `anthropic`/`openai`/`primary_source_hosts` egress boundary N20 now owns
and proves (moved from N30's v1 write set to N20's, per this package's
correction of N20-F02 — see `N20_provider_transport.prompt.v8.md`). Correct
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
not something to patch locally. This v8 recovery prompt corrects
`N30_preflight_egress.prompt.v6.md`. N30's own scope is unaffected by the
result-namespace defect fixed in `implementation.graph.v8.yaml` (the defect
belonged entirely to the graph's shared `result_pattern` and every node's
own result/evidence write paths, corrected uniformly across all nodes) —
this is a mechanical gate-lineage rename only, following the same discipline
`N30_preflight_egress.prompt.v6.md` itself used for its
`N30_preflight_egress.prompt.v5.md` correction: only this file's own
`--graph` value now names `implementation.graph.v8.yaml` instead of
`implementation.graph.v6.yaml`, the same rename `implementation.graph.v8.yaml`'s
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
(`python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py --node N30_PREFLIGHT_EGRESS --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml`)
to remain green.

# LOOP

Classify each failure as capability semantics, production call-site wiring,
CLI status/exit mapping, or test fixture. If the failure traces to
`egress.py`'s own boundary rather than how N30 calls it, stop and route it
to N20 rather than patching it here. Repair the owning layer and rerun the
production-path negative case plus the full N30 slice. Never make readiness
easier to obtain to satisfy a test.
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/schemas/spec_approval.schema.v5.json

SHA-256: `e95e6d862b7f7cb2980e194b21b5b1093a2846a4ea97bfeddfb1c27d3a3fde4d`

<details><summary>Exact content</summary>

````
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Run 27 execution package v2 specification approval v5",
  "$comment": "Package-scoped successor to schema v4 for the explicitly authorized graph-v8 recovery. The approved graph-v7 artifact is restored byte-for-byte at its approved digest and remains historical; the in-place modified v7 bytes are preserved separately as recovery input. Fresh results use results/v8/. This schema changes only the schema version and active-graph const while carrying the approved specification, QA lineage, and eight model assignments forward unchanged.",
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
    "schema_version": {"const": 5},
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
      "$comment": "Still a versioned review-lineage pointer, not this package's governing identity. rc3 remains the approved package-structure snapshot; graph-v8 recovery QA is supporting engineering QA. The validator recomputes the manifest digest."
    },
    "approved_rc_manifest_sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "execution_package_qa_verdict": {"const": "QA_PASSED"},
    "execution_package_qa_verification_sha256": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "$comment": "SHA-256 of the approved RC's own QA/verification.json. Unchanged from schema v3."
    },
    "approved_graph": {
      "const": "plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml",
      "$comment": "Const-locked to the active graph-v8 recovery artifact. A future graph v9+ gets its own schema generation; historical schemas and graphs remain unedited for records that cite them."
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
````

</details>

## FILE: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/contracts/spec_approval.v5.yaml

SHA-256: `0aefb83bc337e7625eb823774647edd80bd1fbcd9701b69599ee018509c8dd6f`

<details><summary>Exact content</summary>

````
schema_version: 5
approved: true
approved_spec: plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md
approved_spec_sha256: e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c
spec_qa_verdict: QA_PASSED
spec_qa_verification_sha256: 899c9720be48f071d6caf26eceafa81be626cd3bda685afa05eb0cc1dfe9a631
approved_rc_manifest: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc3/manifest.v1.json
approved_rc_manifest_sha256: 0e4fbfe2c258ae6176931e5490f8a2b55bdf8708d3ef0f257b50a05c9e582a6d
execution_package_qa_verdict: QA_PASSED
execution_package_qa_verification_sha256: 202e2f214dd732ce24eb758c7cee5965cfcc113d71d03350d8bc5fefa7773217
approved_graph: plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v8.yaml
approved_graph_sha256: c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1
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
  The user explicitly authorized the narrow Run 27 graph-v8 recovery in
  plans/26_langgraph_curriculum_factory/prompts/RUN27_GPT56_SOL_AUTONOMOUS_V8_RECOVERY_TO_N90.prompt.v1.md.
  This record carries forward the already-approved specification, its witnessed
  QA verification, the rc3 package-structure manifest and witnessed QA record,
  and all eight Claude/Codex model and effort assignments without change. It
  binds those authorities to implementation.graph.v8.yaml at SHA-256
  c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1.
  The approved graph-v7 artifact is restored byte-for-byte at SHA-256
  b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22;
  the improperly modified v7 bytes are preserved separately at SHA-256
  b6c17e81c6e32f32b86183d4577fe9a18894c0657504eca832e36d7daa17865e
  as recovery input and are never used for new admissions. Fresh results and
  evidence use the collision-free execution_package_v2/results/v8/ namespace.
  Graph v8 carries forward the live-proven N30 retrieval/source ownership and
  N40 deterministic-boundary ownership corrections, the exact-host retrieval
  policy, subscription-only CLI architecture, and unchanged N00-to-N90 order.
  No historical result, evidence, release candidate, QA session, graph,
  contract, schema, or prompt is superseded in place.
````

</details>

## FILE: policy/retrieval_hosts.v1.yaml

SHA-256: `ee56cf4988691647ebd1f28bd90724208112bcae6a4b7324543b42bbc21c32be`

<details><summary>Exact content</summary>

````
# External-data retrieval host allowlist (N30V7-F07, N20V7-F13's WebSearch decision).
#
# `SourceRetriever` (runtime/langgraph_factory/egress.py) is the only path that ever
# fetches source bytes, and it denies any host not named here -- exact match only,
# never a wildcard or suffix match, and never a host a model proposed for itself.
# A curriculum selects exactly one named profile by name (`retrieval_host_profile` in
# its manifest); it does not supply hosts directly. Adding a host to a profile is a
# deliberate, reviewed change to this file, never a runtime decision.
#
# Every host must be HTTPS-reachable and is still subject to `SourceRetriever`'s own
# DNS-resolution/private-address rejection and allowlisted-redirect-at-every-hop
# checks (egress.py `_check_host`/`fetch`) -- this file only names which hosts may be
# addressed at all; it does not relax any other control.

retrieval_hosts_version: '1.0'

profiles:
  electronics:
    description: >-
      Manufacturer, standards-body, and established reference documentation for
      beginner electronics/maker curricula (e.g. arduino_kit).
    hosts:
      - learn.sparkfun.com
      - docs.arduino.cc
      - www.arduino.cc
      - learn.adafruit.com
      - support.microbit.org
      - www.cpsc.gov
      - www.allaboutcircuits.com
````

</details>

## FILE: schemas/curriculum.schema.v5.json

SHA-256: `7ee2b15e22f14eeb5e297b55dac626df03de072e7d9ee4be86ec3f26498acd89`

<details><summary>Exact content</summary>

````
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/curriculum_builder/curriculum.schema.v5.json",
  "title": "Curriculum manifest v5 — one curriculum, no subject named",
  "description": "v4 required `kit_power_profile` and `visual_system` at the top level. \"kit\" and \"power\" are one subject's words in an engine contract, and a curriculum in an unrelated subject could not satisfy either — that is `G5`. Both are now the curriculum's own domain configuration, held under `domain.config` and shaped by the schema `domain.schema` names. What stays here is what is true of every curriculum: who it is for, what it declares about its own domain, and the human-authored sequence of units.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "manifest_version",
    "curriculum",
    "domain",
    "labs"
  ],
  "properties": {
    "manifest_version": {
      "const": "5.0"
    },
    "curriculum": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "title",
        "learner",
        "delivery",
        "design_rule"
      ],
      "properties": {
        "title": {
          "type": "string",
          "minLength": 1
        },
        "learner": {
          "type": "string",
          "minLength": 1
        },
        "delivery": {
          "type": "string",
          "minLength": 1
        },
        "design_rule": {
          "const": "Component first; a problem is an application, never the organising principle."
        }
      }
    },
    "domain": {
      "description": "What this curriculum declares about its own subject. `schema` is the contract every unit's `domain` block is validated against, supplied and named by the curriculum because the engine cannot know the shape of a subject it has never heard of. `config` is the domain configuration v4 carried at the top level under one subject's names.",
      "type": "object",
      "additionalProperties": false,
      "required": [
        "schema",
        "manifest_schema",
        "verifier",
        "config"
      ],
      "properties": {
        "schema": {
          "description": "Repository-relative path to the schema this curriculum supplies for its units' domain block. It must live under this curriculum's own directory: an engine-held domain schema is the leak again.",
          "type": "string",
          "pattern": "^curricula/[a-z0-9_]+/[A-Za-z0-9_.-]+\\.json$"
        },
        "manifest_schema": {
          "description": "Repository-relative path to the schema this curriculum supplies for its own manifest surfaces — `domain.config` under `$defs/config`, and every lab's `core_activity` under `$defs/core_activity`. This is where v4's `kit_power_profile`, `visual_system`, `mode` and `circuit_status` constraints went. They were moved, not dropped: a constraint that leaves the engine has to arrive somewhere, and the somewhere is the curriculum's own contract. The engine requires the declaration and validates that contract against `schemas/manifest_domain.metaschema.v1.json` — that it closes `config` and enumerates `mode` and `domain_state` — and never reads the values. `FR-P5-DOMAIN-CONSTRAINED` enforces both halves.",
          "type": "string",
          "pattern": "^curricula/[a-z0-9_]+/[A-Za-z0-9_.-]+\\.json$"
        },
        "config": {
          "type": "object",
          "minProperties": 1,
          "description": "The curriculum's domain configuration, shaped by its own contract and never by this one. The shape is real and lives at `manifest_schema#/$defs/config`; what the engine states here is only that the block exists and is not empty."
        },
        "verifier": {
          "description": "The curriculum's domain verifier, and the whole reason the engine can be generic without being unsafe. A domain is generatable exactly to the extent that it has a verifier which is not a model — electrical rule checking over a netlist, a dictionary lookup, an interval checker. The engine never knows what it checks. It knows the verifier must exist, must be code, must be executable, and must have been proven against fixtures before any unit is generated. **A curriculum that declares none does not run**, and that is a refusal rather than a warning.",
          "type": "object",
          "additionalProperties": false,
          "required": [
            "entry_point",
            "invocation",
            "must_reject",
            "must_accept",
            "proven"
          ],
          "properties": {
            "entry_point": {
              "description": "Executable code under this curriculum's own directory. An engine-held verifier would be the engine knowing the domain.",
              "type": "string",
              "pattern": "^curricula/[a-z0-9_]+/[A-Za-z0-9_.-]+$"
            },
            "invocation": {
              "description": "The exact command, with <domain> standing for the unit's domain block. Exit 0 accepts; non-zero rejects and prints one line per rule that fired.",
              "type": "string",
              "minLength": 20
            },
            "must_reject": {
              "description": "Fixtures the verifier must refuse, each with the code it must refuse them for. A detector that only ever accepts is not a verifier, and one that rejects for the wrong reason is a check that has stopped seeing what it was written to see.",
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "additionalProperties": false,
                "required": [
                  "fixture",
                  "expected_code"
                ],
                "properties": {
                  "fixture": {
                    "type": "string",
                    "pattern": "^curricula/[a-z0-9_]+/fixtures/[A-Za-z0-9_.-]+$"
                  },
                  "expected_code": {
                    "type": "string",
                    "minLength": 5
                  }
                }
              }
            },
            "must_accept": {
              "description": "Fixtures the verifier must accept. Without one, a verifier that refused everything would satisfy must_reject entirely.",
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "string",
                "pattern": "^curricula/[a-z0-9_]+/fixtures/[A-Za-z0-9_.-]+$"
              }
            },
            "proven": {
              "description": "The record that the fixtures were executed, not merely listed. The gate re-executes them rather than believing this block — what the block adds is that the curriculum claimed it, so a curriculum that never ran its own fixtures is refused before the engine spends anything on it.",
              "type": "object",
              "additionalProperties": false,
              "required": [
                "executed_utc",
                "result"
              ],
              "properties": {
                "executed_utc": {
                  "type": "string",
                  "format": "date-time"
                },
                "result": {
                  "enum": [
                    "all_fixtures_behaved",
                    "not_executed"
                  ]
                },
                "note": {
                  "type": "string",
                  "minLength": 10
                }
              }
            }
          }
        }
      }
    },
    "labs": {
      "type": "array",
      "minItems": 1,
      "items": {
        "$ref": "#/$defs/lab"
      },
      "description": "The curriculum defines how many labs exist. The schema does not fix a count — it requires at least one lab, ascending, contiguous from L01, with unique ids."
    },
    "lab_count": {
      "description": "Optional declared count. When present it must equal len(labs); the controller asserts this.",
      "type": "integer",
      "minimum": 1
    },
    "retrieval_host_profile": {
      "description": "Optional named profile from policy/retrieval_hosts.v1.yaml (N30V7-F07). A curriculum selects a profile by name; it never declares hosts here. Absent entirely, source retrieval stays fully denied.",
      "type": "string",
      "minLength": 1
    }
  },
  "$defs": {
    "lab": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "id",
        "slug",
        "kind",
        "title",
        "subject_set",
        "sequence",
        "subject_job",
        "learner_outcome",
        "required_explanation",
        "core_activity",
        "applications",
        "visual_roles",
        "safety_focus",
        "qa_focus"
      ],
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^L[0-9]{2,3}$"
        },
        "slug": {
          "type": "string",
          "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$"
        },
        "kind": {
          "enum": [
            "foundation",
            "component",
            "application",
            "integration",
            "diagnostic"
          ]
        },
        "title": {
          "type": "string",
          "minLength": 1
        },
        "sequence": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "prerequisites",
            "prepares_for"
          ],
          "properties": {
            "prerequisites": {
              "type": "array",
              "items": {
                "type": "string",
                "pattern": "^L(0[1-9]|[12][0-9]|3[0-5])$"
              }
            },
            "prepares_for": {
              "type": "array",
              "items": {
                "type": "string",
                "pattern": "^L(0[1-9]|[12][0-9]|3[0-5])$"
              }
            }
          }
        },
        "learner_outcome": {
          "type": "string",
          "minLength": 20
        },
        "required_explanation": {
          "type": "array",
          "minItems": 2,
          "items": {
            "type": "string",
            "minLength": 10
          }
        },
        "core_activity": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "mode",
            "question",
            "domain_state"
          ],
          "properties": {
            "mode": {
              "type": "string",
              "minLength": 3,
              "description": "The unit's hazard class, from the set its curriculum declares."
            },
            "question": {
              "type": "string",
              "minLength": 10
            },
            "domain_state": {
              "type": "string",
              "minLength": 3,
              "description": "How ready this unit's domain data is, in the curriculum's own vocabulary."
            },
            "domain_activity": {
              "type": "object",
              "minProperties": 1,
              "description": "Whatever else this unit's activity needs the curriculum to state — the supply it draws on, the corpus it reads, the interval set it uses. Validated against the curriculum's own domain schema, never against this one. `kit_power_profile` and `power_input` lived at this level in v4 and are why a second curriculum could not use this contract."
            }
          },
          "description": "What the learner does. `mode` is the hazard class, from the set the curriculum declares; `domain_state` is what the curriculum's own contract says about how ready this unit's subject data is. Neither list is fixed here — a fixed list would be one subject's list."
        },
        "applications": {
          "type": "array",
          "minItems": 2,
          "items": {
            "type": "string",
            "minLength": 3
          }
        },
        "visual_roles": {
          "type": "array",
          "minItems": 3,
          "items": {
            "type": "string",
            "minLength": 3
          }
        },
        "safety_focus": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "string",
            "minLength": 6
          }
        },
        "qa_focus": {
          "type": "array",
          "minItems": 2,
          "items": {
            "type": "string",
            "minLength": 6
          }
        },
        "subject_set": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "primary",
            "supporting"
          ],
          "properties": {
            "primary": {
              "type": "string",
              "minLength": 1,
              "description": "What this unit is about."
            },
            "supporting": {
              "type": "array",
              "items": {
                "type": "string",
                "minLength": 1
              }
            }
          }
        },
        "subject_job": {
          "type": "string",
          "minLength": 20
        }
      }
    }
  }
}
````

</details>

## FILE: curricula/arduino_kit/arduino_kit_curriculum.v5.yaml

SHA-256: `0dd0e0d441c3881e136c2be56143a10e49b4bc0a631e2ae9d935b853a1a37280`

<details><summary>Exact content</summary>

````
# Single source of truth for the whole workbook. It defines scope, not unverified wiring.
# v5 = v4 with the two engine-contract concepts that were one subject's words moved into
# this curriculum's own `domain` block, and the domain verifier declared.
#
# `kit_power_profile` and `visual_system` were top-level concepts of the predecessor
# engine curriculum contract, superseded by v5 and now retired. "kit" and "power" are
# electronics words in an engine contract, and a curriculum in an unrelated subject
# could satisfy neither — that is G5 in
# plans/simplification/plan/simplification.plan.v3.md section 2. They are unchanged
# below; only their owner is.
#
# `domain.verifier` is the declaration that makes the engine's genericity safe rather
# than merely broad: this curriculum states what checks its own domain, and the engine
# refuses to start without it. The human-authored sequence below is untouched.
#
# The v4 manifest is retained at curricula/deprecated/ as history. Nothing may read it.
manifest_version: '5.0'
# Selects a named profile from policy/retrieval_hosts.v1.yaml (N30V7-F07); this
# curriculum never supplies hosts directly, only the profile name.
retrieval_host_profile: electronics
curriculum:
  title: Electronics Discoveries — Component-Oriented Workbook
  learner: Supervised beginners aged 9+, with no assumed electronics knowledge
  delivery: One lab is generated, technically checked, pedagogically checked, and accepted before the
    next lab begins.
  design_rule: Component first; a problem is an application, never the organising principle.
domain:
  schema: curricula/arduino_kit/domain.schema.v1.json
  manifest_schema: curricula/arduino_kit/manifest.domain.schema.v1.json
  verifier:
    entry_point: curricula/arduino_kit/verify_domain.py
    invocation: python3 curricula/arduino_kit/verify_domain.py --domain <domain>
    must_reject:
    - fixture: curricula/arduino_kit/fixtures/domain_polarity_asserted.reject.json
      expected_code: polarity-unevidenced
    - fixture: curricula/arduino_kit/fixtures/domain_no_current_limit.reject.json
      expected_code: current-limit-absent
    - fixture: curricula/arduino_kit/fixtures/domain_supply_not_permitted.reject.json
      expected_code: supply-not-permitted
    must_accept:
    - curricula/arduino_kit/fixtures/domain_unpowered_path.accept.json
    proven:
      executed_utc: '2026-08-01T00:00:00Z'
      result: all_fixtures_behaved
      note: FR-P5-VERIFIER-REQUIRED re-executes every fixture named above rather than reading this record.
        What this record adds is the curriculum's own claim, so a curriculum that never ran its fixtures
        is refused before the engine spends anything on it.
  config:
    circuit_policy: composed
    circuit_library: curricula/arduino_kit/circuit_library.v1.yaml
    kit_power_profile:
      id: elegoo-uno-r3-super-starter-kit-power-system
      reference_verification: verified_official
      local_inspection: not_available
      input:
        description: Included 9 V battery with DC connector feeding the kit power-supply module. This
          is the supplied source identified by the official Super Starter Kit listing and product photograph;
          it is not a 9 V/1 A wall adapter.
        evidence: 'Official listing: https://www.elegoo.com/en-gb/products/elegoo-uno-r3-super-starter-kit
          ; cached photograph: curricula/arduino_kit/official_kit_photo.jpg'
      rail_choices:
      - 'OFF'
      - 3.3 V
      - 5 V
      release_rule: Reference evidence authorises curriculum drafting. Every powered technical map must
        cite the verified kit photo, the selected physical jumper position, the module orientation, the
        circuit current calculation, and component/load ratings. Generated imagery never supplies those
        facts.
    visual_system:
      photorealistic_roles:
      - component identification
      - safe working context
      - expected observation or before-after comparison
      technical_map_rule: Technical build maps are deterministically rendered from verified circuit data;
        generative images are never the connection authority.
labs:
- id: L01
  slug: safe-power
  kind: foundation
  title: Power Source and Safe Start
  subject_set:
    primary: Breadboard power module
    supporting:
    - breadboard
    - 9V battery with DC connector
  sequence:
    prerequisites: []
    prepares_for:
    - L02
    - L03
    - L04
    - L05
  subject_job: The power module provides a chosen low-voltage rail to a breadboard when it is correctly
    oriented and switched on.
  learner_outcome: Identify the 9 V battery and DC lead, power module, and chosen breadboard rail from
    the official kit photograph; explain why we move wires only while power is disconnected.
  required_explanation:
  - The battery and DC lead, module, and breadboard rail have different jobs.
  - 'A circuit is a closed loop: electricity goes out from one power terminal through parts and back to
    the other terminal.'
  - A rail colour is only a label; the verified selector position and physical map decide what the rail
    does.
  core_activity:
    mode: unpowered
    question: With the battery lead disconnected, can I trace battery to module to chosen rail and complete
      the adult-check card?
    domain_state: not_designed
  applications:
  - Preparing a safe power-off workspace before every later build
  - Checking a power path before it can damage a component
  visual_roles:
  - verified photorealistic kit-identification photograph
  - safe disconnected setup photograph
  - deterministic verified power-path and orientation map
  - child tick-box evidence card
  safety_focus:
  - Child never connects the battery lead or changes module selectors alone
  - Power source disconnected before rewiring
  - Adult verifies module orientation and selector
  qa_focus:
  - Battery input versus rail output distinction
  - Official kit reference used
  - Foundation activity is entirely disconnected
  - Deterministic map gate
- id: L02
  slug: breadboard
  kind: foundation
  title: 'Breadboard: The Hidden Metal Paths'
  subject_set:
    primary: Breadboard
    supporting:
    - jumper wires
  sequence:
    prerequisites:
    - L01
    prepares_for:
    - L03
    - L05
    - L06
  subject_job: A breadboard joins selected holes with hidden metal clips so circuits can be built without
    soldering.
  learner_outcome: Predict which holes are joined, identify the centre trench and rail breaks, and verify
    a prediction unpowered.
  required_explanation:
  - Five-hole groups form electrical meeting points.
  - The centre trench separates the two sides for parts with legs on both sides.
  - Power rails may be split and must be checked rather than assumed.
  core_activity:
    mode: unpowered
    question: Which holes share the same hidden metal clip?
    domain_state: not_designed
  applications:
  - Placing a resistor without shorting its two legs
  - Building repeatable circuits
  visual_roles:
  - photorealistic breadboard
  - cutaway clip illustration
  - deterministic connectivity map
  - rail-break warning
  safety_focus:
  - Power remains off
  - Do not assume rail continuity
  qa_focus:
  - Correct board-specific topology
  - Trench and rail-break accuracy
- id: L03
  slug: jumper-wires-and-expansion
  kind: foundation
  title: Jumper Wires and Expansion Board
  subject_set:
    primary: Jumper wires
    supporting:
    - breadboard expansion board
  sequence:
    prerequisites:
    - L01
    - L02
    prepares_for:
    - L05
    - L30
  subject_job: Jumper wires deliberately connect two different electrical points; an expansion board makes
    grouped connections easier to reach.
  learner_outcome: Make a labelled connection plan and distinguish a wire route from a component connection.
  required_explanation:
  - A wire joins two points but does not decide what the circuit does.
  - Wire colour is a convention
  - not an electrical property.
  - A connection is defined by its endpoints.
  core_activity:
    mode: unpowered
    question: Can I name the two endpoints of every wire before I insert it?
    domain_state: not_designed
  applications:
  - Extending a rail
  - Connecting sensors and outputs
  visual_roles:
  - photorealistic wire types
  - connection endpoint diagram
  - deterministic route overlay
  - loose-wire hazard
  safety_focus:
  - Power off while moving wires
  - No ambiguous endpoints
  qa_focus:
  - Endpoint traceability
  - Colour never used as sole instruction
- id: L04
  slug: multimeter
  kind: foundation
  title: 'Multimeter: Looking for Evidence'
  subject_set:
    primary: Digital multimeter
    supporting:
    - breadboard
  sequence:
    prerequisites:
    - L01
    - L02
    prepares_for:
    - L05
    - L06
    - L35
  subject_job: A multimeter measures or tests selected electrical properties when its probes, sockets,
    and mode are used correctly.
  learner_outcome: Distinguish voltage, continuity, and current modes and hand an adult a safe measurement
    plan.
  required_explanation:
  - Voltage compares two points; it is not measured at one point alone.
  - Continuity is a low-energy check of a possible connection.
  - Current mode is never placed directly across a supply.
  core_activity:
    mode: unpowered
    question: Which meter mode answers a connection question without powering the circuit?
    domain_state: not_designed
  applications:
  - Checking breadboard paths
  - Checking a battery or rail with adult support
  visual_roles:
  - photorealistic meter
  - deterministic jack-and-dial map
  - probe placement diagram
  - current-mode red-X
  safety_focus:
  - Correct meter socket
  - Adult-led voltage/current measurements
  qa_focus:
  - Socket and mode accuracy
  - Direct-across-supply prohibition
- id: L05
  slug: resistor
  kind: component
  title: 'Resistor: The Current-Controlling Part'
  subject_set:
    primary: Resistor
    supporting:
    - breadboard
    - LED
  sequence:
    prerequisites:
    - L01
    - L02
    - L03
    - L04
    prepares_for:
    - L06
    - L07
    - L15
  subject_job: A resistor limits current so other components can operate safely.
  learner_outcome: Explain why an LED needs a series resistor and recognise that resistor value changes
    the current.
  required_explanation:
  - Voltage and current are different ideas.
  - A resistor makes it harder for charge to move through a path.
  - A series resistor protects an LED by limiting current.
  core_activity:
    mode: powered_pending_physical_check
    question: How does changing a verified series resistor change LED brightness?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - LED current limiting
  - Pull-up and pull-down circuits
  visual_roles:
  - photorealistic resistor markings
  - resistance path illustration
  - deterministic series circuit
  - brightness comparison
  safety_focus:
  - Correct verified resistor value
  - No direct LED-to-rail connection
  qa_focus:
  - Current-limiting calculation
  - Power rating
  - Selected rail stated
- id: L06
  slug: diode
  kind: component
  title: 'Diode: A One-Way Protection Part'
  subject_set:
    primary: Diode
    supporting:
    - resistor
    - LED
  sequence:
    prerequisites:
    - L05
    prepares_for:
    - L07
    - L16
    - L33
  subject_job: A diode strongly resists current in one direction and allows it in the other direction
    when correctly connected.
  learner_outcome: Identify the band, predict forward versus reverse connection, and state two useful
    diode jobs.
  required_explanation:
  - A diode has two semiconductor regions meeting at a junction barrier.
  - Forward bias helps charges cross; reverse bias strongly resists them.
  - A diode can protect against reverse connection and give a coil's stored energy a safe path.
  core_activity:
    mode: powered_pending_physical_check
    question: What changes when a verified diode is turned around in the same protected test circuit?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Reverse-polarity protection
  - Flyback path for a relay or motor coil
  - AC-to-DC rectification
  visual_roles:
  - photorealistic band identification
  - semiconductor junction illustration
  - deterministic forward-reverse comparison
  - coil protection context
  safety_focus:
  - Band orientation
  - Never connect coil circuits without verified flyback design
  qa_focus:
  - Anode/cathode and forward/reverse claims are supported by a primary source and a bounded prediction.
  - The adult execution card records observed forward/reverse evidence; document acceptance does not claim
    an unperformed physical test.
- id: L07
  slug: led
  kind: component
  title: 'LED: A Diode That Makes Light'
  subject_set:
    primary: LED
    supporting:
    - resistor
  sequence:
    prerequisites:
    - L05
    - L06
    prepares_for:
    - L08
    - L19
    - L30
  subject_job: An LED is a diode that releases some electrical energy as visible light when current is
    correctly limited and directed.
  learner_outcome: Identify LED polarity, build a protected light circuit, and explain why the resistor
    is not optional.
  required_explanation:
  - An LED has a direction; its long and short legs or flat edge are physical clues.
  - Light appears when charge changes energy inside the LED.
  - The series resistor controls current and prevents damage.
  core_activity:
    mode: powered_pending_physical_check
    question: Can I make the LED light only when its polarity and resistor are both correct?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Status indicator
  - Light-up signal
  - Seven-segment display element
  visual_roles:
  - photorealistic LED polarity
  - energy-to-light illustration
  - deterministic LED circuit
  - lit-versus-unlit comparison
  safety_focus:
  - Mandatory series resistor
  - Polarity check
  qa_focus:
  - LED forward voltage allowance
  - Resistor calculation
  - Brightness claim bounded
- id: L08
  slug: rgb-led
  kind: component
  title: 'RGB LED: Three Tiny Light Sources'
  subject_set:
    primary: RGB LED
    supporting:
    - resistors
  sequence:
    prerequisites:
    - L07
    prepares_for:
    - L21
    - L30
  subject_job: An RGB LED contains red, green, and blue LED sections that can be controlled separately
    to make many colours.
  learner_outcome: Identify the common lead after verification and predict colour mixing from selected
    light sections.
  required_explanation:
  - Red, green, and blue light can combine to make other colours.
  - Each LED section needs its own current control.
  - Common-anode and common-cathode versions need different wiring and must never be guessed.
  core_activity:
    mode: powered_pending_physical_check
    question: Which light sections must be on to make a chosen mixed colour?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Colour status signal
  - Mood or alarm indicator
  visual_roles:
  - photorealistic RGB LED
  - additive-colour illustration
  - deterministic verified-common circuit
  - colour-state comparison
  safety_focus:
  - Verify common lead type
  - One resistor per colour section
  qa_focus:
  - Kit-specific pinout
  - Per-channel current limiting
- id: L09
  slug: potentiometer
  kind: component
  title: 'Potentiometer: A Turning Voltage Chooser'
  subject_set:
    primary: Potentiometer
    supporting:
    - multimeter
    - LED
  sequence:
    prerequisites:
    - L04
    - L05
    - L07
    prepares_for:
    - L10
    - L11
    - L22
  subject_job: A potentiometer is an adjustable resistor with a moving contact that can choose part of
    a voltage.
  learner_outcome: Identify the three terminals and explain why the centre wiper voltage changes as the
    knob turns.
  required_explanation:
  - The two outer terminals sit at the ends of a resistive track.
  - The wiper touches a position along that track.
  - A voltage divider creates an adjustable fraction of a supply voltage.
  core_activity:
    mode: powered_pending_physical_check
    question: How does the verified wiper voltage change as I turn the knob?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Volume or brightness control signal
  - Adjustable sensor threshold
  visual_roles:
  - photorealistic potentiometer
  - track-and-wiper cutaway
  - deterministic divider map
  - knob-position comparison
  safety_focus:
  - Adult-led measurement
  - Do not use an unknown wiper pinout
  qa_focus:
  - Three-terminal topology
  - Meter mode and probes
- id: L10
  slug: photoresistor
  kind: component
  title: 'Photoresistor: A Part That Notices Light'
  subject_set:
    primary: Photoresistor
    supporting:
    - resistor
    - multimeter
  sequence:
    prerequisites:
    - L05
    - L09
    prepares_for:
    - L31
  subject_job: A photoresistor changes resistance as the light falling on it changes.
  learner_outcome: Compare bright and shaded conditions and explain how a voltage divider turns that change
    into a readable signal.
  required_explanation:
  - Light changes the material's resistance.
  - A divider converts a resistance change into a voltage change.
  - More or less light may raise or lower the chosen signal depending on circuit position.
  core_activity:
    mode: powered_pending_physical_check
    question: What evidence changes when I shade the photoresistor?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Night light trigger
  - Light level sensor
  visual_roles:
  - photorealistic sensor
  - light-and-resistance illustration
  - deterministic divider
  - bright-shaded comparison
  safety_focus:
  - Avoid staring into bright sources
  - Verify resistor value
  qa_focus:
  - Divider direction explained
  - Measurement conditions stated
- id: L11
  slug: thermistor
  kind: component
  title: 'Thermistor: A Part That Notices Temperature'
  subject_set:
    primary: Thermistor
    supporting:
    - resistor
    - multimeter
  sequence:
    prerequisites:
    - L05
    - L09
    prepares_for:
    - L32
  subject_job: A thermistor changes resistance when its temperature changes.
  learner_outcome: Compare safe warm and room-temperature conditions and explain why the signal direction
    depends on the divider arrangement.
  required_explanation:
  - 'Most kit thermistors are NTC: their resistance decreases as temperature rises.'
  - Temperature should be changed gently and safely.
  - A divider turns resistance change into a voltage signal.
  core_activity:
    mode: powered_pending_physical_check
    question: What changes when the thermistor is gently warmed by a hand?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Overheat warning
  - Temperature threshold
  visual_roles:
  - photorealistic thermistor
  - temperature-resistance graph
  - deterministic divider
  - safe hand-warm comparison
  safety_focus:
  - No flame or hot water
  - Verify thermistor type
  qa_focus:
  - NTC/PTC verification
  - Safe stimulus
- id: L12
  slug: pushbutton
  kind: component
  title: 'Pushbutton: A Momentary Connection'
  subject_set:
    primary: Pushbutton
    supporting:
    - resistor
    - LED
  sequence:
    prerequisites:
    - L02
    - L05
    - L07
    prepares_for:
    - L30
    - L35
  subject_job: A pushbutton changes from open to connected only while it is pressed.
  learner_outcome: Identify paired internal legs and explain why a pull resistor prevents a floating signal.
  required_explanation:
  - A button does not always connect the legs beside each other.
  - An open input needs a defined resting state.
  - A pull-up or pull-down resistor gives that resting state.
  core_activity:
    mode: powered_pending_physical_check
    question: Which button legs connect only while the button is pressed?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Doorbell input
  - User control
  visual_roles:
  - photorealistic button orientation
  - internal contacts cutaway
  - deterministic pull circuit
  - pressed-released comparison
  safety_focus:
  - Verify button leg pairs unpowered
  - No short across rail
  qa_focus:
  - Button rotation
  - Pull resistor topology
- id: L13
  slug: tilt-switch
  kind: component
  title: 'Tilt Switch: A Moving Contact Sensor'
  subject_set:
    primary: Tilt switch
    supporting:
    - resistor
    - LED
  sequence:
    prerequisites:
    - L12
    prepares_for:
    - L35
  subject_job: A tilt switch uses a moving internal contact to open or close a circuit in particular orientations.
  learner_outcome: Predict and observe the orientations in which the contact changes state.
  required_explanation:
  - A small conductor moves inside the switch.
  - The switch is not a precise angle meter.
  - A pull resistor provides a known state when the contact is open.
  core_activity:
    mode: powered_pending_physical_check
    question: Which tilt direction closes this verified switch?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Tip-over alarm
  - Orientation detector
  visual_roles:
  - photorealistic tilt switch
  - moving-contact cutaway
  - deterministic input map
  - orientation sequence
  safety_focus:
  - Secure components before tilting
  - Verify actual switch orientation
  qa_focus:
  - State direction verified
  - Pull resistor present
- id: L14
  slug: joystick
  kind: component
  title: 'Joystick: Two Turning Sensors and a Button'
  subject_set:
    primary: Joystick module
    supporting:
    - multimeter
  sequence:
    prerequisites:
    - L09
    - L12
    prepares_for:
    - L23
    - L35
  subject_job: A joystick uses two potentiometers and often a pushbutton to report horizontal, vertical,
    and press actions.
  learner_outcome: Explain the three kinds of joystick signal and test one verified axis with adult support.
  required_explanation:
  - Each axis is an adjustable voltage divider.
  - Centre position is a range
  - not necessarily an exact number.
  - Module labels and pins are kit-specific.
  core_activity:
    mode: powered_pending_physical_check
    question: How does one verified joystick axis change as the stick moves, and how does the push-button
      state change when pressed?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Game control
  - Robot direction input
  visual_roles:
  - photorealistic joystick
  - axis signal illustration
  - verified pin map
  - movement-result comparison
  safety_focus:
  - No universal module pinout
  - Adult-led controller connection
  qa_focus:
  - Module variant confirmed
  - Signal ranges measured
- id: L15
  slug: transistor
  kind: component
  title: 'Transistor: A Small Signal Controls a Bigger Path'
  subject_set:
    primary: NPN transistor
    supporting:
    - resistors
    - LED
  sequence:
    prerequisites:
    - L05
    - L07
    - L12
    prepares_for:
    - L16
    - L31
    - L33
  subject_job: A transistor can use a small control signal to control a larger current path through a
    load.
  learner_outcome: Identify that base, collector, and emitter have different jobs and explain switching
    without calling it a magic amplifier.
  required_explanation:
  - A small base current controls a collector-emitter path in an NPN switch.
  - A base resistor limits the control current.
  - Pin order varies by package and must be verified.
  core_activity:
    mode: powered_pending_physical_check
    question: Can a protected small control path switch a separate LED load path?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Sensor-controlled lamp
  - Relay driver
  visual_roles:
  - photorealistic transistor package
  - switch-path illustration
  - deterministic verified pinout map
  - control-on-off comparison
  safety_focus:
  - Verify transistor pinout
  - Base resistor required
  qa_focus:
  - Load current calculation
  - Saturation assumption bounded
- id: L16
  slug: relay
  kind: component
  title: 'Relay: An Electrically Moved Switch'
  subject_set:
    primary: Relay
    supporting:
    - transistor
    - diode
  sequence:
    prerequisites:
    - L06
    - L15
    prepares_for:
    - L33
  subject_job: A relay uses a coil to move switch contacts, allowing one circuit to control a separate
    low-voltage path.
  learner_outcome: Distinguish coil pins from COM, NO, and NC contacts and explain why a flyback diode
    is needed.
  required_explanation:
  - The coil is an electromagnet
  - not a normal switch contact.
  - COM connects to NO or NC depending on coil state.
  - A flyback diode gives stored coil energy a safe path when power turns off.
  core_activity:
    mode: adult_led_controller_station
    question: Which verified contact path changes when the relay coil is energised?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Low-voltage controlled switch
  - Alarm or doorbell controller
  visual_roles:
  - photorealistic relay labels
  - coil-contact cutaway
  - deterministic low-voltage map
  - NO-NC state comparison
  safety_focus:
  - Never connect mains to relay contacts
  - Verified flyback diode and coil rating
  qa_focus:
  - Coil/contact separation
  - Contact labels verified
- id: L17
  slug: active-buzzer
  kind: component
  title: 'Active Buzzer: A Sound Part With Its Own Oscillator'
  subject_set:
    primary: Active buzzer
    supporting:
    - transistor optional
  sequence:
    prerequisites:
    - L01
    - L15
    prepares_for:
    - L35
  subject_job: An active buzzer makes a preset sound when it receives suitable power.
  learner_outcome: Explain why an active buzzer can make sound from a steady supply while a passive buzzer
    cannot.
  required_explanation:
  - An active buzzer contains an oscillator.
  - Polarity and rated voltage matter.
  - Sound is evidence that the buzzer's internal circuit is running.
  core_activity:
    mode: powered_pending_physical_check
    question: Does the verified active buzzer sound when its correct supply and polarity are applied?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Alarm
  - Timer signal
  visual_roles:
  - photorealistic buzzer markings
  - internal oscillator illustration
  - deterministic test circuit
  - sound-state scene
  safety_focus:
  - Check polarity and rating
  - Keep sound level brief
  qa_focus:
  - Active/passive identification
  - Rated supply verified
- id: L18
  slug: passive-buzzer
  kind: component
  title: 'Passive Buzzer: A Sound Part That Needs a Changing Signal'
  subject_set:
    primary: Passive buzzer
    supporting:
    - controller output
  sequence:
    prerequisites:
    - L17
    prepares_for:
    - L23
    - L35
  subject_job: A passive buzzer makes sound only when a changing electrical signal moves it repeatedly.
  learner_outcome: Contrast a steady signal with a changing signal and predict which will make a tone.
  required_explanation:
  - Sound comes from repeated movement.
  - Signal frequency changes perceived pitch.
  - A static supply is not a complete test for a passive buzzer.
  core_activity:
    mode: adult_led_controller_station
    question: What changes when the adult-controlled signal changes frequency?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Different alert tones
  - Musical notes
  visual_roles:
  - photorealistic passive buzzer
  - vibration-wave illustration
  - controller station map
  - low-high pitch comparison
  safety_focus:
  - Adult-controlled signal source
  - Sound duration limited
  qa_focus:
  - No static-supply claim
  - Frequency explanation
- id: L19
  slug: one-digit-seven-segment
  kind: component
  title: 'One-Digit Seven-Segment Display: Making Numbers With LEDs'
  subject_set:
    primary: One-digit seven-segment display
    supporting:
    - resistors
  sequence:
    prerequisites:
    - L07
    prepares_for:
    - L20
    - L21
  subject_job: A seven-segment display combines separate LED bars to show digits.
  learner_outcome: Map a digit to segments and explain why the display type and pinout must be verified.
  required_explanation:
  - Each segment is an LED.
  - Common-anode and common-cathode displays work differently.
  - Each lit segment requires suitable current control.
  core_activity:
    mode: powered_pending_physical_check
    question: Which verified segments must light to show a chosen digit?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Counter
  - Timer display
  visual_roles:
  - photorealistic display
  - digit-segment map
  - deterministic verified pin map
  - digit comparison
  safety_focus:
  - Verify display type and pinout
  - Segment current limiting
  qa_focus:
  - Common connection verified
  - Segment resistor strategy
- id: L20
  slug: four-digit-seven-segment
  kind: component
  title: 'Four-Digit Display: Sharing Segments Over Time'
  subject_set:
    primary: Four-digit seven-segment display
    supporting:
    - controller outputs
    - per-segment current-limiting components
  sequence:
    prerequisites:
    - L19
    prepares_for:
    - L21
    - L22
  subject_job: A four-digit display reuses segment connections and quickly selects one digit at a time.
  learner_outcome: Explain multiplexing as fast turn-taking rather than four independent static displays.
  required_explanation:
  - Digits take turns quickly enough to look continuously lit.
  - Segment lines are shared.
  - A controller and verified module pinout are required for an honest demonstration.
  core_activity:
    mode: adult_led_controller_station
    question: Why can several digits look lit when they take turns?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Clock
  - Scoreboard
  visual_roles:
  - photorealistic display
  - turn-taking timeline
  - verified connection map
  - slow-motion concept comparison
  safety_focus:
  - Verify display common type and pinout.
  - Use verified per-segment current limiting and total-current budget.
  qa_focus:
  - Multiplexing accurately explained
  - Controller dependencies disclosed
- id: L21
  slug: shift-register
  kind: component
  title: '74HC595: More Outputs From a Small Number of Signals'
  subject_set:
    primary: 74HC595 shift register
    supporting:
    - LEDs
    - per-LED current-limiting resistors
    - controller outputs
  sequence:
    prerequisites:
    - L08
    - L19
    prepares_for:
    - L22
  subject_job: A shift register receives bits in sequence and presents them on more output pins after
    a latch command.
  learner_outcome: Use a physical bit-token model to explain serial input, storage, and parallel outputs.
  required_explanation:
  - A bit is an on/off piece of information.
  - Serial means one after another; parallel means side by side.
  - Exact chip orientation
  - voltage limits
  - and timing come from the verified datasheet.
  core_activity:
    mode: adult_led_controller_station
    question: How can three controller signals update several LED outputs?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - More indicator LEDs
  - Display driver
  visual_roles:
  - photorealistic IC notch
  - bit-token sequence illustration
  - verified chip map
  - input-output comparison
  safety_focus:
  - Verify supply and logic levels.
  - Use current limiting on every LED output and keep total package current within the primary-source
    rating.
  qa_focus:
  - Datasheet pins checked
  - Timing claim observed
- id: L22
  slug: lcd1602
  kind: component
  title: 'LCD1602: A Screen That Needs Instructions'
  subject_set:
    primary: LCD1602 display
    supporting:
    - potentiometer
    - controller output
  sequence:
    prerequisites:
    - L09
    - L21
    prepares_for:
    - L23
    - L35
  subject_job: An LCD1602 shows letters and numbers when a controller sends instructions and data; a potentiometer
    usually sets contrast.
  learner_outcome: Distinguish contrast from text data and identify why a screen needs a verified interface
    and code.
  required_explanation:
  - Contrast changes how visible the pixels are
  - not what they say.
  - A controller sends commands and character information.
  - LCD variants and backpacks require pin verification.
  core_activity:
    mode: adult_led_controller_station
    question: What is the difference between turning contrast and changing the text command?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Sensor readout
  - Message display
  visual_roles:
  - photorealistic LCD
  - pixels-and-contrast illustration
  - verified interface map
  - blank-visible-text comparison
  safety_focus:
  - Verify module/backpack type
  - Adult-led controller connection
  qa_focus:
  - Contrast circuit verified
  - Interface variant identified
- id: L23
  slug: infrared-remote
  kind: component
  title: 'Infrared Remote: Sending Invisible Light Messages'
  subject_set:
    primary: IR remote
    supporting:
    - IR receiver module
    - controller output
  sequence:
    prerequisites:
    - L18
    - L22
    prepares_for:
    - L24
    - L35
  subject_job: An infrared remote sends coded pulses of invisible light; a compatible receiver module
    detects and demodulates the pulses, and controller software interprets the button code.
  learner_outcome: Explain that buttons send patterns, not simply “electricity through the air.”
  required_explanation:
  - Infrared is light beyond what our eyes see.
  - A code is a timed pattern that represents a button.
  - In this lab the accepted receiver station is a black box that shows different button results; L24
    explains how the receiver works.
  core_activity:
    mode: adult_led_controller_station
    question: Can a receiver show that different buttons send different codes?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Remote control
  - Contactless input
  visual_roles:
  - photorealistic remote and receiver
  - invisible-light concept illustration
  - verified station map
  - button-code result
  safety_focus:
  - No eye-safety claims beyond ordinary remote use
  - Adult-led code display
  qa_focus:
  - Receiver module pinout
  - Code observation evidence
- id: L24
  slug: infrared-receiver
  kind: component
  title: 'Infrared Receiver: Turning Light Pulses Into Signals'
  subject_set:
    primary: IR receiver module
    supporting:
    - IR remote
    - controller output
  sequence:
    prerequisites:
    - L23
    prepares_for:
    - L35
  subject_job: An IR receiver module detects suitable infrared pulse patterns and produces an electrical
    output a controller can read.
  learner_outcome: Identify that the receiver senses patterned light and requires a shared reference connection.
  required_explanation:
  - The receiver responds to a pattern
  - helping reject ordinary room light.
  - A common ground gives two connected parts the same reference.
  - Module pin labels are not universal.
  core_activity:
    mode: adult_led_controller_station
    question: What changes in the verified output when a remote button is pressed?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Remote-controlled output
  - Hidden-button game
  visual_roles:
  - photorealistic receiver
  - pattern-filter illustration
  - verified pin map
  - signal result comparison
  safety_focus:
  - Verify module pins
  - Adult-led controller use
  qa_focus:
  - Shared-ground requirement
  - Ambient-light limitation
- id: L25
  slug: ultrasonic-sensor
  kind: component
  title: 'Ultrasonic Sensor: Measuring With Echoes'
  subject_set:
    primary: Ultrasonic sensor
    supporting:
    - controller trigger output
    - controller echo input
  sequence:
    prerequisites:
    - L18
    - L24
    prepares_for:
    - L35
  subject_job: An ultrasonic sensor sends a sound pulse and estimates distance from the time an echo takes
    to return.
  learner_outcome: Explain distance as a measured travel time and identify why soft or angled surfaces
    can give unreliable results.
  required_explanation:
  - Ultrasound is sound above human hearing.
  - The pulse travels out and returns as an echo.
  - Distance calculations need the return trip to be divided by two.
  core_activity:
    mode: adult_led_controller_station
    question: How does echo time change as a flat target moves farther away?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Parking distance helper
  - Robot obstacle sensing
  visual_roles:
  - photorealistic sensor
  - echo travel diagram
  - verified controller map
  - near-far result comparison
  safety_focus:
  - Keep target clear of face
  - No universal module voltage assumption
  qa_focus:
  - Round-trip reasoning
  - Surface limitation explained
- id: L26
  slug: dht11
  kind: component
  title: 'DHT11: Reporting Air Conditions'
  subject_set:
    primary: DHT11 sensor
    supporting:
    - controller output
  sequence:
    prerequisites:
    - L22
    - L25
    prepares_for:
    - L35
  subject_job: A DHT11 module senses temperature and humidity and sends a digital report to a controller.
  learner_outcome: Distinguish a sensor measurement from a screen reading and explain that digital reports
    use a timed protocol.
  required_explanation:
  - Humidity describes water vapour in air.
  - The sensor measures and then sends a coded report.
  - Readings update slowly and have limited accuracy.
  core_activity:
    mode: adult_led_controller_station
    question: What can the controller display from this verified sensor, and what are its limits?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Room comfort display
  - Simple weather station
  visual_roles:
  - photorealistic sensor
  - humidity concept illustration
  - verified module map
  - display reading context
  safety_focus:
  - Verify module variant
  - Avoid water contact
  qa_focus:
  - Accuracy limits stated
  - Timed protocol not simplified into analogue voltage
- id: L27
  slug: servo
  kind: component
  title: 'Servo Motor: Moving to a Chosen Position'
  subject_set:
    primary: Servo motor
    supporting:
    - controller output
    - external power consideration
  sequence:
    prerequisites:
    - L15
    - L18
    prepares_for:
    - L35
  subject_job: A hobby servo uses a feedback system to move its shaft toward a commanded position.
  learner_outcome: Explain position command versus continuous spinning and identify why power capacity
    matters for motors.
  required_explanation:
  - A servo contains a motor, gears, and a position sensor.
  - Control pulses ask for a position.
  - Motor current can exceed what a controller pin or weak rail can safely supply.
  core_activity:
    mode: adult_led_controller_station
    question: How does a verified pulse command choose a servo position?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Pointer
  - Small robot arm
  visual_roles:
  - photorealistic servo horn
  - feedback-loop illustration
  - verified adult station map
  - position sequence
  safety_focus:
  - Adult-approved power budget
  - Keep fingers clear of moving horn
  qa_focus:
  - Power current verified
  - Shared reference and pulse range confirmed
- id: L28
  slug: stepper-motor
  kind: component
  title: 'Stepper Motor: Moving in Small Steps'
  subject_set:
    primary: Stepper motor
    supporting:
    - ULN2003 driver
    - controller outputs
    - verified motor power source
  sequence:
    prerequisites:
    - L16
    - L27
    prepares_for:
    - L29
    - L35
  subject_job: A stepper motor moves in controlled increments when its coils are energised in the correct
    sequence.
  learner_outcome: Explain that the motor needs a coil sequence and a driver rather than a direct controller
    connection.
  required_explanation:
  - Several coils pull the rotor in a planned order.
  - A step is a small controlled movement.
  - Motors need more current than a controller output can provide directly.
  core_activity:
    mode: adult_led_controller_station
    question: What happens when a verified coil sequence is changed or reversed?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Precise dial
  - Small positioning mechanism
  visual_roles:
  - photorealistic motor
  - coil-step illustration
  - verified driver station map
  - direction sequence
  safety_focus:
  - Do not power motor directly from controller pin
  - Adult-led power check
  qa_focus:
  - Coil order verified
  - Driver current limits verified
- id: L29
  slug: uln2003-driver
  kind: component
  title: 'ULN2003: A Driver Between a Controller and a Motor'
  subject_set:
    primary: ULN2003 driver board
    supporting:
    - stepper motor
    - controller output
  sequence:
    prerequisites:
    - L15
    - L28
    prepares_for:
    - L35
  subject_job: A ULN2003 driver board lets small controller signals control higher-current coil paths
    and includes protection suited to inductive loads.
  learner_outcome: Explain why a driver separates control signals from motor current paths.
  required_explanation:
  - Input pins are control signals
  - not motor power.
  - Driver outputs switch coil current.
  - Inductive loads need managed turn-off energy.
  core_activity:
    mode: adult_led_controller_station
    question: Which path carries the controller signal and which path carries motor current?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Stepper motor driver
  - Relay or solenoid driver concept
  visual_roles:
  - photorealistic driver board
  - control-versus-power path diagram
  - verified terminal map
  - coil sequence context
  safety_focus:
  - Verify board labels
  - Adult-led motor supply
  qa_focus:
  - Signal/power separation
  - Motor connector mapping
- id: L30
  slug: led-and-switch-integration
  kind: integration
  title: 'LED and Switch: Making a Clear User Signal'
  subject_set:
    primary: LED
    supporting:
    - pushbutton
    - resistor
  sequence:
    prerequisites:
    - L07
    - L12
    prepares_for:
    - L35
  subject_job: The LED shows an electrical state while the pushbutton creates a controlled user input.
  learner_outcome: Combine known components without introducing a new unexplained electrical principle.
  required_explanation:
  - The LED needs current limiting
  - The button needs a defined resting state
  - One component can communicate the state made by another.
  core_activity:
    mode: powered_pending_physical_check
    question: Can a button make a protected LED show a clear on/off state?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Push-to-light signal
  - Simple user interface
  visual_roles:
  - photorealistic interaction scene
  - component-role diagram
  - deterministic integration map
  - state comparison
  safety_focus:
  - Apply all previous LED/button checks
  qa_focus:
  - No new hidden component behaviour
  - Deterministic map matches steps
- id: L31
  slug: light-controlled-transistor-switch
  kind: application
  title: 'Photoresistor and Transistor: Light Controls a Load'
  subject_set:
    primary: Photoresistor
    supporting:
    - transistor
    - resistors
    - LED
  sequence:
    prerequisites:
    - L10
    - L15
    prepares_for:
    - L35
  subject_job: A photoresistor produces a changing control signal and a transistor uses that signal to
    control a separate load path.
  learner_outcome: Trace sensor, control, and load paths as three different jobs in one circuit.
  required_explanation:
  - The divider turns light into a control voltage
  - The transistor controls the load path
  - Circuit position determines whether darkness or brightness turns the load on.
  core_activity:
    mode: powered_pending_physical_check
    question: Does shading the sensor change the protected load state as the verified design predicts?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Night light
  - Light alarm
  visual_roles:
  - photorealistic sensor-use scene
  - three-path explanation
  - deterministic circuit map
  - light-dark comparison
  safety_focus:
  - Verified transistor pinout and resistor values
  - No direct high-current load
  qa_focus:
  - Threshold behaviour not overstated
  - Sensor/control/load trace
- id: L32
  slug: temperature-threshold
  kind: application
  title: 'Thermistor Threshold: A Temperature Warning Idea'
  subject_set:
    primary: Thermistor
    supporting:
    - fixed resistor
    - adult-led controller station
  sequence:
    prerequisites:
    - L11
    - L15
    prepares_for:
    - L35
  subject_job: A thermistor signal can be compared or read to decide when a temperature-related warning
    should occur.
  learner_outcome: Explain that a threshold is a chosen decision point, not a perfect temperature measurement.
  required_explanation:
  - The thermistor changes gradually
  - A threshold is the point where we choose an action
  - Real temperature alarms need calibration and safety margins.
  core_activity:
    mode: adult_led_controller_station
    question: At what gently warmed condition does the verified demonstration change state?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Overheat warning concept
  - Plant or room monitor
  visual_roles:
  - photorealistic thermistor context
  - threshold graph
  - verified adult station map
  - below-above comparison
  safety_focus:
  - No unsafe heating
  - Adult-led threshold setup
  qa_focus:
  - Temperature not falsely precise
  - Thermistor type and calibration disclosed
- id: L33
  slug: relay-driver
  kind: application
  title: 'Relay Driver: Letting a Small Signal Control a Separate Low-Voltage Circuit'
  subject_set:
    primary: Relay
    supporting:
    - transistor
    - diode
    - resistors
    - controller output
  sequence:
    prerequisites:
    - L06
    - L15
    - L16
    prepares_for:
    - L35
  subject_job: A transistor driver switches relay coil current while a diode safely handles the coil's
    turn-off energy.
  learner_outcome: Identify the control path, coil path, and isolated contact path without touching mains
    electricity.
  required_explanation:
  - The controller signal does not power the coil directly
  - The diode protects the transistor when the coil is switched off
  - Relay contacts remain a separate low-voltage demonstration only.
  core_activity:
    mode: adult_led_controller_station
    question: Can a protected driver change a verified low-voltage contact circuit?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Low-voltage alarm circuit
  - Separate low-voltage load switch
  visual_roles:
  - photorealistic relay driver
  - three-path diagram
  - deterministic low-voltage map
  - contact-state comparison
  safety_focus:
  - Mains forbidden
  - Flyback diode orientation verified
  - Adult-led build
  qa_focus:
  - Coil/contact separation
  - Transistor and diode protection verified
- id: L34
  slug: signals
  kind: integration
  title: 'Signals: One Circuit Can Carry Information'
  subject_set:
    primary: LED and active buzzer
    supporting:
    - pushbutton
    - current-limiting resistors
  sequence:
    prerequisites:
    - L17
    - L18
    - L30
    prepares_for:
    - L35
  subject_job: Outputs such as lights and sounds communicate information about a circuit state.
  learner_outcome: Design a simple, explained signal meaning using components already understood.
  required_explanation:
  - A signal has a meaning chosen by people
  - Light and sound can communicate different states
  - A clear signal needs a consistent rule.
  core_activity:
    mode: powered_pending_physical_check
    question: How can an accepted pushbutton circuit make a protected LED and active buzzer communicate
      two verified states?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Ready/warning indicator
  - Simple accessibility cue
  visual_roles:
  - photorealistic signal context
  - state-meaning chart
  - deterministic verified map
  - two-state comparison
  safety_focus:
  - Keep sound brief
  - Reuse only accepted circuit blocks
  qa_focus:
  - Meaning not confused with mechanism
  - Reused blocks traceable
- id: L35
  slug: repair-shop
  kind: diagnostic
  title: 'Repair Shop: Trace, Test, and Explain'
  subject_set:
    primary: Power-off-first diagnostic method
    supporting:
    - multimeter
    - accepted L30 LED-and-switch circuit
    - known fault fixtures
  sequence:
    prerequisites:
    - L01
    - L04
    - L30
    - L34
    prepares_for: []
  subject_job: A power-off-first diagnostic method uses previously accepted component circuits, observation,
    and one safe check at a time to locate a known connection or orientation fault.
  learner_outcome: Follow a power-off-first troubleshooting tree and explain the evidence for a likely
    fault.
  required_explanation:
  - Start with a clear expected behaviour
  - Check physical orientation and connections with power off
  - Change one thing at a time and record evidence.
  core_activity:
    mode: diagnostic
    question: Which safe power-off check identifies whether the accepted L30 fixture has a loose jumper
      or a reversed LED?
    domain_state: requires_verified_circuit_data
    domain_activity:
      power_input: kit_battery_9v
  applications:
  - Finding a loose wire
  - Checking LED polarity or a button orientation
  visual_roles:
  - photorealistic tidy repair bench
  - diagnostic decision tree
  - deterministic fault-map examples
  - power-off warning
  safety_focus:
  - Power off first
  - No random rewiring
  - Adult checks any powered measurement
  qa_focus:
  - Fault evidence is real
  - No powered release without verified circuit data
````

</details>

## FILE: runtime/langgraph_factory/egress.py

SHA-256: `63c1be5851a9b79b0a74de7b5ba3b2a0c4f9ee5cbe4ab88193ea56ab43d5ea3a`

<details><summary>Exact content</summary>

````
"""Code-owned egress broker and external-data authorization gate (spec 7.4 and 9).

Every network path reachable from this Python process passes through `EgressGuard`.
Only `SourceRetriever` — the deterministic primary-source retriever used by D06B — may
open HTTP(S), and only for a locator and data class the run authorization record
already covers. Every other socket use is denied and receipted.
"""
from __future__ import annotations

import contextlib
import hashlib
import ipaddress
import json
import socket
import threading
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence
from urllib.parse import urlparse

import jsonschema
import yaml

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"

PROVIDERS: tuple[str, ...] = ("anthropic", "openai", "primary_source_hosts")

PROVIDER_DATA_CLASSES: Mapping[str, frozenset[str]] = MappingProxyType({
    "anthropic": frozenset({
        "manifest_unit_projection",
        "bounded_questions",
        "admitted_source_excerpts",
        "retrieved_source_files",
        "domain_parent_artifact",
        "content_parent_artifact",
        "visual_parent_artifact",
        "named_repair_findings",
        "schemas_and_rubrics",
    }),
    "openai": frozenset({
        "frozen_unit_artifacts",
        "frozen_workbook_artifacts",
        "deterministic_evidence",
        "shipped_pdf",
        "rasterized_pages",
        "schemas_and_rubrics",
    }),
    "primary_source_hosts": frozenset({"primary_source_bytes"}),
})

MODEL_API_HOSTS: frozenset[str] = frozenset({
    "api.openai.com",
    "chatgpt.com",
    "api.anthropic.com",
})


class EgressError(RuntimeError):
    """Base class for every containment failure raised by this module."""


class AuthorizationDenied(EgressError):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason


class EgressDenied(EgressError):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def canonical_digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def _load_schema(name: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


@dataclass(frozen=True)
class AuthorizationRecord:
    """Run-scoped external-data authorization (spec 7.4).

    Credentials are not approval: this record is the only thing that grants a
    provider/data-class transmission, and it is checked before any child process or
    socket is created.
    """

    run_id: str
    curriculum_digest: str
    output_root: str
    approved_at_utc: str
    expires_at_utc: str
    providers: Mapping[str, Sequence[str]]

    def __post_init__(self) -> None:
        normalized: dict[str, tuple[str, ...]] = {}
        for provider, classes in dict(self.providers).items():
            if provider not in PROVIDERS:
                raise AuthorizationDenied("unknown_provider", provider)
            declared = tuple(sorted(set(classes)))
            unknown = set(declared) - PROVIDER_DATA_CLASSES[provider]
            if unknown:
                raise AuthorizationDenied(
                    "undeclared_data_class", f"{provider}: {sorted(unknown)}")
            normalized[provider] = declared
        object.__setattr__(self, "providers", MappingProxyType(normalized))
        object.__setattr__(self, "output_root", str(Path(self.output_root).resolve()))
        if len(self.curriculum_digest) != 64:
            raise AuthorizationDenied("malformed_curriculum_digest", self.curriculum_digest)

    def to_record(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "curriculum_digest": self.curriculum_digest,
            "output_root": self.output_root,
            "approved_at_utc": self.approved_at_utc,
            "expires_at_utc": self.expires_at_utc,
            "providers": {p: list(c) for p, c in self.providers.items()},
        }

    def digest(self) -> str:
        return canonical_digest(self.to_record())


def authorize_transmission(
    record: AuthorizationRecord | None,
    *,
    provider: str,
    data_classes: Iterable[str],
    curriculum_digest: str,
    run_id: str,
    output_root: Path | str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return a granted authorization receipt, or raise before anything is transmitted."""
    requested = tuple(sorted(set(data_classes)))
    if not requested:
        raise AuthorizationDenied("no_data_class_requested")
    if record is None:
        raise AuthorizationDenied("authorization_absent", provider)
    if provider not in PROVIDERS:
        raise AuthorizationDenied("unknown_provider", provider)

    moment = now or utc_now()
    expires = datetime.fromisoformat(record.expires_at_utc)
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if moment >= expires:
        raise AuthorizationDenied("authorization_expired", record.expires_at_utc)
    if record.run_id != run_id:
        raise AuthorizationDenied("wrong_run_scope", f"{record.run_id} != {run_id}")
    if record.curriculum_digest != curriculum_digest:
        raise AuthorizationDenied("wrong_curriculum_digest", curriculum_digest)
    if record.output_root != str(Path(output_root).resolve()):
        raise AuthorizationDenied("wrong_output_scope", str(output_root))
    if provider not in record.providers:
        raise AuthorizationDenied("provider_not_authorized", provider)

    permitted = set(record.providers[provider])
    missing = [name for name in requested if name not in permitted]
    if missing:
        raise AuthorizationDenied("data_class_not_authorized", f"{provider}: {missing}")

    receipt = {
        "authorization_digest": record.digest(),
        "provider": provider,
        "data_classes": list(requested),
        "curriculum_digest": curriculum_digest,
        "run_id": run_id,
        "output_root": str(Path(output_root).resolve()),
        "approved_at_utc": record.approved_at_utc,
        "expires_at_utc": record.expires_at_utc,
        "checked_at_utc": moment.isoformat(),
        "decision": "granted",
    }
    receipt["receipt_id"] = canonical_digest(receipt)[:32]
    jsonschema.Draft202012Validator(
        _load_schema("internal_authorization_receipt.schema.json")).validate(receipt)
    return receipt


class ReceiptLog:
    """Append-only egress receipt sink; every allow and every denial lands here."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = Path(path) if path else None
        self._entries: list[dict[str, Any]] = []
        self._validator = jsonschema.Draft202012Validator(
            _load_schema("internal_egress_receipt.schema.json"))
        self._lock = threading.Lock()

    def append(self, receipt: Mapping[str, Any]) -> dict[str, Any]:
        entry = dict(receipt)
        entry.setdefault("recorded_at_utc", utc_now().isoformat())
        self._validator.validate(entry)
        with self._lock:
            self._entries.append(entry)
            if self._path is not None:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                with self._path.open("a", encoding="utf-8") as handle:
                    handle.write(canonical_json(entry) + "\n")
        return entry

    @property
    def entries(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._entries)

    @property
    def denials(self) -> tuple[dict[str, Any], ...]:
        return tuple(e for e in self._entries if e["outcome"] == "denied")

    @property
    def allowed(self) -> tuple[dict[str, Any], ...]:
        return tuple(e for e in self._entries if e["outcome"] == "allowed")


@dataclass(frozen=True)
class _Grant:
    locator: str
    host: str
    port: int
    endpoints: frozenset[tuple[str, int]]
    authorization_receipt_id: str
    data_class: str


def _caller_origin() -> str:
    stack = traceback.extract_stack()[:-2]
    for frame in reversed(stack):
        if not frame.filename.endswith("egress.py"):
            return f"{Path(frame.filename).name}:{frame.lineno}"
    return "unknown"


class EgressGuard:
    """Process-wide socket interception.

    Patching happens on `socket.socket` itself, so raw sockets, `http.client`,
    `urllib`, and any third-party client all reach `_authorize` — there is no wrapper
    to route around. An unauthorized attempt is receipted and then raised.
    """

    def __init__(self, receipts: ReceiptLog) -> None:
        self.receipts = receipts
        self._local = threading.local()
        self._installed = False
        self._saved: dict[str, Any] = {}

    def install(self) -> None:
        if self._installed:
            return
        self._saved = {
            "connect": socket.socket.connect,
            "connect_ex": socket.socket.connect_ex,
            "create_connection": socket.create_connection,
        }
        guard = self

        def connect(sock, address):  # type: ignore[no-untyped-def]
            guard._authorize(address, channel="socket_connect")
            return guard._saved["connect"](sock, address)

        def connect_ex(sock, address):  # type: ignore[no-untyped-def]
            guard._authorize(address, channel="socket_connect_ex")
            return guard._saved["connect_ex"](sock, address)

        def create_connection(address, *args, **kwargs):  # type: ignore[no-untyped-def]
            guard._authorize(address, channel="create_connection")
            return guard._saved["create_connection"](address, *args, **kwargs)

        socket.socket.connect = connect  # type: ignore[method-assign]
        socket.socket.connect_ex = connect_ex  # type: ignore[method-assign]
        socket.create_connection = create_connection  # type: ignore[assignment]
        self._installed = True

    def uninstall(self) -> None:
        if not self._installed:
            return
        socket.socket.connect = self._saved["connect"]  # type: ignore[method-assign]
        socket.socket.connect_ex = self._saved["connect_ex"]  # type: ignore[method-assign]
        socket.create_connection = self._saved["create_connection"]  # type: ignore[assignment]
        self._installed = False

    def __enter__(self) -> "EgressGuard":
        self.install()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.uninstall()

    @property
    def installed(self) -> bool:
        return self._installed

    @property
    def _grant(self) -> _Grant | None:
        return getattr(self._local, "grant", None)

    @contextlib.contextmanager
    def granted(self, grant: _Grant):
        previous = self._grant
        self._local.grant = grant
        try:
            yield
        finally:
            self._local.grant = previous

    def _deny(self, target: str, *, channel: str, reason: str) -> None:
        self.receipts.append({
            "receipt_kind": "egress_denied",
            "channel": channel,
            "requested_target": target,
            "outcome": "denied",
            "denial_reason": reason,
            "traceback_origin": _caller_origin(),
        })
        raise EgressDenied(reason, target)

    def _authorize(self, address: Any, *, channel: str) -> None:
        if not isinstance(address, (tuple, list)) or len(address) < 2:
            self._deny(str(address), channel=channel, reason="unsupported_address_family")
        host, port = str(address[0]), int(address[1])
        target = f"{host}:{port}"
        grant = self._grant
        if grant is None:
            reason = ("direct_model_endpoint" if host in MODEL_API_HOSTS
                      else "unauthorized_socket_no_active_retrieval")
            self._deny(target, channel=channel, reason=reason)
        if host in MODEL_API_HOSTS:
            self._deny(target, channel=channel, reason="direct_model_endpoint")
        if (host, port) not in grant.endpoints:
            try:
                ipaddress.ip_address(host)
            except ValueError:
                self._deny(target, channel=channel, reason="host_not_pinned")
            self._deny(target, channel=channel, reason="dns_rebinding")
        self.receipts.append({
            "receipt_kind": "egress_allowed",
            "channel": channel,
            "requested_target": target,
            "outcome": "allowed",
            "authorization_receipt_id": grant.authorization_receipt_id,
            "locator": grant.locator,
            "resolved_host": grant.host,
            "data_class": grant.data_class,
        })


@dataclass(frozen=True)
class RetrievalPolicy:
    allowed_hosts: frozenset[str]
    max_bytes: int = 25_000_000
    max_redirects: int = 3
    require_tls: bool = True
    allow_private_addresses: bool = False
    allowed_content_types: frozenset[str] = frozenset({
        "text/html", "text/plain", "application/pdf", "application/json",
        "application/xhtml+xml", "text/markdown",
    })


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RETRIEVAL_HOSTS_PATH = REPO_ROOT / "policy" / "retrieval_hosts.v1.yaml"


class RetrievalHostProfileError(EgressError):
    """A named retrieval-host profile could not be loaded exactly as declared."""


def load_retrieval_host_profile(
    profile_name: str, *, path: Path | None = None,
) -> tuple[tuple[str, ...], str]:
    """Return `(hosts, policy_digest)` for one named profile (N30V7-F07, spec decision).

    A curriculum selects a profile by name; it never supplies hosts directly, and
    nothing here ever adds a host a model proposed for itself. Every host must be a
    bare, lowercase, wildcard-free hostname -- `SourceRetriever._check_host` already
    does exact-set membership, HTTPS, DNS/private-address, and allowlisted-redirect
    checks on top of whatever this returns; this function only guards the *shape* of
    the declared allowlist itself, before it ever reaches that enforcement.
    """
    document_path = path or DEFAULT_RETRIEVAL_HOSTS_PATH
    try:
        raw = document_path.read_text(encoding="utf-8")
    except OSError as error:
        raise RetrievalHostProfileError(f"cannot read retrieval host policy: {error}") from error
    document = yaml.safe_load(raw)
    if not isinstance(document, dict):
        raise RetrievalHostProfileError("retrieval host policy is not a mapping")
    profiles = document.get("profiles")
    if not isinstance(profiles, dict):
        raise RetrievalHostProfileError("retrieval host policy declares no profiles")
    profile = profiles.get(profile_name)
    if not isinstance(profile, dict):
        raise RetrievalHostProfileError(
            f"retrieval host profile {profile_name!r} is not declared in {document_path}")
    hosts = profile.get("hosts")
    if not isinstance(hosts, list) or not hosts:
        raise RetrievalHostProfileError(f"profile {profile_name!r} declares no hosts")
    normalized: list[str] = []
    for host in hosts:
        if not isinstance(host, str) or not host:
            raise RetrievalHostProfileError(f"profile {profile_name!r} carries a non-string host")
        if any(character in host for character in "*?/:@ "):
            raise RetrievalHostProfileError(
                f"profile {profile_name!r} host {host!r} is not a bare hostname "
                f"(no wildcards, no scheme, no port, no path)")
        if host != host.lower():
            raise RetrievalHostProfileError(
                f"profile {profile_name!r} host {host!r} must be lowercase")
        normalized.append(host)
    if len(set(normalized)) != len(normalized):
        raise RetrievalHostProfileError(f"profile {profile_name!r} declares a duplicate host")
    policy_digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return tuple(sorted(normalized)), policy_digest


@dataclass(frozen=True)
class RetrievalResponse:
    final_url: str
    status: int
    headers: Mapping[str, str]
    body: bytes
    redirect_chain: tuple[str, ...] = ()
    tls: Mapping[str, str] | None = None


def _default_resolver(host: str) -> tuple[str, ...]:
    infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    return tuple(sorted({info[4][0] for info in infos}))


def _default_opener(url: str, *, timeout: float) -> RetrievalResponse:
    import urllib.request

    chain: list[str] = []

    class _Tracker(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
            chain.append(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(_Tracker)
    with opener.open(url, timeout=timeout) as response:
        body = response.read()
        return RetrievalResponse(
            final_url=response.geturl(),
            status=response.status,
            headers={k.lower(): v for k, v in response.headers.items()},
            body=body,
            redirect_chain=tuple(chain),
        )


class SourceRetriever:
    """The only authorized HTTP(S) egress path in this process (spec 7.4, D06B).

    The concrete retrieval strategy is D06B's; this class owns the boundary: what may
    be reached, under which authorization, and what is recorded about it.
    """

    def __init__(
        self,
        *,
        guard: EgressGuard,
        policy: RetrievalPolicy,
        resolver: Callable[[str], Sequence[str]] | None = None,
        opener: Callable[..., RetrievalResponse] | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.guard = guard
        self.policy = policy
        self._resolver = resolver or _default_resolver
        self._opener = opener or _default_opener
        self.timeout_seconds = timeout_seconds

    def _deny(self, locator: str, reason: str, **extra: Any) -> None:
        payload: dict[str, Any] = {
            "receipt_kind": "egress_denied",
            "channel": "source_retrieval",
            "requested_target": locator,
            "outcome": "denied",
            "denial_reason": reason,
        }
        payload.update(extra)
        self.guard.receipts.append(payload)
        raise EgressDenied(reason, locator)

    def _check_host(self, locator: str, host: str | None) -> str:
        if not host:
            self._deny(locator, "missing_host")
        host = host.lower()
        if host in MODEL_API_HOSTS:
            self._deny(locator, "direct_model_endpoint", resolved_host=host)
        if host not in self.policy.allowed_hosts:
            self._deny(locator, "host_not_allowlisted", resolved_host=host)
        return host

    def fetch(
        self,
        locator: str,
        *,
        authorization_receipt: Mapping[str, Any] | None,
        data_class: str = "primary_source_bytes",
    ) -> tuple[bytes, dict[str, Any]]:
        if authorization_receipt is None:
            self._deny(locator, "authorization_absent")
        if authorization_receipt.get("provider") != "primary_source_hosts":
            self._deny(locator, "wrong_provider_authorization",
                       authorization_receipt_id=authorization_receipt.get("receipt_id"))
        if data_class not in authorization_receipt.get("data_classes", ()):
            self._deny(locator, "data_class_not_authorized",
                       authorization_receipt_id=authorization_receipt.get("receipt_id"))

        parsed = urlparse(locator)
        allowed_schemes = ("https",) if self.policy.require_tls else ("https", "http")
        if parsed.scheme not in allowed_schemes:
            self._deny(locator, "scheme_not_allowed")
        host = self._check_host(locator, parsed.hostname)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        addresses = tuple(self._resolver(host))
        if not addresses:
            self._deny(locator, "unresolvable_host", resolved_host=host)
        if not self.policy.allow_private_addresses:
            for address in addresses:
                if not ipaddress.ip_address(address).is_global:
                    self._deny(locator, "non_global_address", resolved_host=host,
                               resolved_addresses=list(addresses))

        grant = _Grant(
            locator=locator,
            host=host,
            port=port,
            endpoints=frozenset({(host, port)} | {(a, port) for a in addresses}),
            authorization_receipt_id=str(authorization_receipt["receipt_id"]),
            data_class=data_class,
        )
        with self.guard.granted(grant):
            response = self._opener(locator, timeout=self.timeout_seconds)

        if len(response.redirect_chain) > self.policy.max_redirects:
            self._deny(locator, "too_many_redirects",
                       redirect_chain=list(response.redirect_chain))
        for hop in (*response.redirect_chain, response.final_url):
            hop_host = (urlparse(hop).hostname or "").lower()
            if hop_host in MODEL_API_HOSTS:
                self._deny(locator, "redirect_to_model_endpoint",
                           redirect_chain=list(response.redirect_chain), final_url=hop)
            if hop_host not in self.policy.allowed_hosts:
                self._deny(locator, "redirect_to_unapproved_host",
                           redirect_chain=list(response.redirect_chain), final_url=hop)
        if response.status != 200:
            self._deny(locator, "http_status_not_ok", http_status=response.status)
        if len(response.body) > self.policy.max_bytes:
            self._deny(locator, "response_too_large", byte_count=len(response.body))

        content_type = str(response.headers.get("content-type", "")).split(";")[0].strip().lower()
        if content_type and content_type not in self.policy.allowed_content_types:
            self._deny(locator, "content_type_not_allowed", content_type=content_type)

        receipt = self.guard.receipts.append({
            "receipt_kind": "egress_allowed",
            "channel": "source_retrieval",
            "requested_target": locator,
            "outcome": "allowed",
            "authorization_receipt_id": str(authorization_receipt["receipt_id"]),
            "locator": locator,
            "resolved_host": host,
            "resolved_addresses": list(addresses),
            "final_url": response.final_url,
            "redirect_chain": list(response.redirect_chain),
            "http_status": response.status,
            "tls": dict(response.tls) if response.tls else None,
            "content_type": content_type or None,
            "byte_count": len(response.body),
            "bytes_sha256": hashlib.sha256(response.body).hexdigest(),
            "data_class": data_class,
        })
        return response.body, receipt


def authorize_subprocess_transmission(
    record: AuthorizationRecord | None,
    *,
    provider: str,
    data_classes: Iterable[str],
    curriculum_digest: str,
    run_id: str,
    output_root: Path | str,
    receipts: ReceiptLog,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Gate a model-CLI child process on the run authorization record (spec 7.4).

    Called before the child process exists, so a denial cannot follow transmission.
    """
    requested = sorted(set(data_classes))
    try:
        receipt = authorize_transmission(
            record, provider=provider, data_classes=requested,
            curriculum_digest=curriculum_digest, run_id=run_id,
            output_root=output_root, now=now)
    except AuthorizationDenied as denied:
        receipts.append({
            "receipt_kind": "egress_denied",
            "channel": "subprocess_transmission",
            "requested_target": f"{provider}:{','.join(requested)}",
            "outcome": "denied",
            "denial_reason": denied.reason,
        })
        raise
    receipts.append({
        "receipt_kind": "egress_allowed",
        "channel": "subprocess_transmission",
        "requested_target": f"{provider}:{','.join(requested)}",
        "outcome": "allowed",
        "authorization_receipt_id": receipt["receipt_id"],
        "data_class": ",".join(requested),
    })
    return receipt
````

</details>

## FILE: runtime/langgraph_factory/transport.py

SHA-256: `852813cbcd294a86bdbedff539816990321eb991b8037a33913324ee2233483a`

<details><summary>Exact content</summary>

````
"""CLI model transport for the Plan 26 curriculum factory (spec sections 6.3, 7, 9).

Eight frozen job routes, package-relative prompts and schemas, disposable per-activation
workspaces under an OS sandbox, observed-versus-decided model identity, and a single
frozen malformed/transient retry. No LangChain wrapper, no provider SDK, no direct model
HTTP endpoint: the only way to a model is a child process of the pinned CLI.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import signal
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import jsonschema
import yaml

from .. import checks, pdf_inspect, visual_maps
from ..pdf_inspect import MIN_POINT_SIZE
from .artifacts import UNIT_SCOPE, ArtifactStore, ArtifactStream, canonical_digest
from .egress import (
    AuthorizationDenied,
    AuthorizationRecord,
    EgressGuard,
    ReceiptLog,
    authorize_subprocess_transmission,
    canonical_json,
    utc_now,
)

PACKAGE_ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = PACKAGE_ROOT / "config" / "model_jobs.v1.yaml"
SCHEMA_DIR = PACKAGE_ROOT / "schemas"
PROMPT_DIR = PACKAGE_ROOT / "prompts"
REPO_ROOT = PACKAGE_ROOT.parents[1]

AUTHORING_FAMILY = "anthropic"
REVIEW_FAMILY = "openai"

CLAUDE_PERMITTED_TOOLS = frozenset({"StructuredOutput"})

RESERVED_WORKSPACE_NAMES = frozenset({
    "authorized_input.json", "output.schema.json", "result.json",
    "cli_schema_projection.json",
})
STAGED_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")

FORBIDDEN_MODEL_FIELDS = frozenset({
    "accept", "acceptance", "accepted", "admission", "admit", "admitted", "approval",
    "approved", "complete", "decision", "exit_code", "failed", "final", "gate", "join",
    "next", "next_node", "outcome", "pass", "pass_fail", "passed", "resume",
    "resume_frontier", "retries", "retry", "route", "routing", "status", "terminal",
    "terminal_candidate", "terminal_kind", "verdict",
})

REQUIRED_CAPABILITY_FACETS = (
    "filesystem_isolation",
    "python_process_egress_broker",
    "identity_observation",
)


class TransportError(RuntimeError):
    """Base class for every transport rejection."""


class RouteRejected(TransportError):
    pass


class CapabilityProofFailed(TransportError):
    pass


class IdentityUnobservable(TransportError):
    pass


class IdentityMismatch(TransportError):
    pass


class WorkspaceViolation(TransportError):
    pass


class AttemptLimitExceeded(TransportError):
    pass


class TransportRetryable(TransportError):
    """Malformed or transient failure; eligible for the one frozen retry."""

    def __init__(self, failure_class: str, detail: str = "") -> None:
        super().__init__(f"{failure_class}: {detail}" if detail else failure_class)
        self.failure_class = failure_class


class ResultParseError(TransportRetryable):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- registry


@dataclass(frozen=True)
class JobRoute:
    job_id: str
    job_type: str
    cli: str
    family: str
    provider: str
    model: str
    task_class: str | None
    reasoning_effort: str
    schema: str
    prompt: str
    timeout_seconds: int
    retry_limit: int
    data_classes: tuple[str, ...]

    @property
    def is_review(self) -> bool:
        return self.family == REVIEW_FAMILY


_REGISTRY_CACHE: dict[Path, Mapping[str, JobRoute]] = {}


def load_job_registry(path: Path | str = REGISTRY_PATH) -> Mapping[str, JobRoute]:
    resolved = Path(path).resolve()
    if resolved in _REGISTRY_CACHE:
        return _REGISTRY_CACHE[resolved]
    document = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    entries = document.get("jobs") or []
    declared = int(document.get("job_count", 0))
    if declared != 8 or len(entries) != 8:
        raise RouteRejected(
            f"registry must declare exactly eight jobs, found {len(entries)} (declared {declared})")
    routes: dict[str, JobRoute] = {}
    for entry in entries:
        route = JobRoute(
            job_id=entry["job_id"],
            job_type=entry["job_type"],
            cli=entry["cli"],
            family=entry["family"],
            provider=entry["provider"],
            model=entry["model"],
            task_class=entry.get("task_class"),
            reasoning_effort=entry["reasoning_effort"],
            schema=entry["schema"],
            prompt=entry["prompt"],
            timeout_seconds=int(entry["timeout_seconds"]),
            retry_limit=int(entry["retry_limit"]),
            data_classes=tuple(entry["data_classes"]),
        )
        if route.cli not in {"codex", "claude"}:
            raise RouteRejected(f"unknown cli for {route.job_id}: {route.cli}")
        if route.cli == "claude" and route.family != AUTHORING_FAMILY:
            raise RouteRejected(f"claude route {route.job_id} must be family {AUTHORING_FAMILY}")
        if route.cli == "codex" and route.family != REVIEW_FAMILY:
            raise RouteRejected(f"codex route {route.job_id} must be family {REVIEW_FAMILY}")
        if route.job_id in routes:
            raise RouteRejected(f"duplicate job id {route.job_id}")
        routes[route.job_id] = route
    _REGISTRY_CACHE[resolved] = routes
    return routes


def resolve_route(job_id: str, registry: Mapping[str, JobRoute] | None = None) -> JobRoute:
    routes = registry if registry is not None else load_job_registry()
    try:
        return routes[job_id]
    except KeyError:
        raise RouteRejected(f"unknown job id: {job_id!r}") from None


def resolve_prompt_path(route: JobRoute) -> Path:
    """Resolve the prompt relative to this package, never the process cwd."""
    candidate = (PROMPT_DIR / route.prompt).resolve()
    if candidate.parent != PROMPT_DIR:
        raise RouteRejected(f"prompt escapes package prompt directory: {route.prompt!r}")
    if not candidate.is_file():
        raise RouteRejected(f"prompt does not resolve inside the package: {route.prompt!r}")
    return candidate


def resolve_schema_path(route: JobRoute) -> Path:
    candidate = (SCHEMA_DIR / route.schema).resolve()
    if candidate.parent != SCHEMA_DIR:
        raise RouteRejected(f"schema escapes package schema directory: {route.schema!r}")
    if not candidate.is_file():
        raise RouteRejected(f"schema does not resolve inside the package: {route.schema!r}")
    return candidate


def load_output_schema(route: JobRoute) -> dict[str, Any]:
    return _load_json(resolve_schema_path(route))


def collect_property_names(schema: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(schema, Mapping):
        for key, value in schema.items():
            if key == "properties" and isinstance(value, Mapping):
                names.update(str(name) for name in value)
            if isinstance(value, (Mapping, list)):
                names |= collect_property_names(value)
    elif isinstance(schema, list):
        for item in schema:
            names |= collect_property_names(item)
    return names


def assert_no_authoritative_fields(schema_or_value: Any, *, label: str) -> None:
    """Reject any routing/acceptance/terminal field in a model schema or candidate."""
    if isinstance(schema_or_value, Mapping) and "properties" in schema_or_value:
        names = collect_property_names(schema_or_value)
    else:
        names = _collect_object_keys(schema_or_value)
    offending = sorted(name for name in names if name.lower() in FORBIDDEN_MODEL_FIELDS)
    if offending:
        raise TransportError(f"{label} declares control-plane fields: {offending}")


def _collect_object_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        keys.update(str(key) for key in value)
        for item in value.values():
            keys |= _collect_object_keys(item)
    elif isinstance(value, list):
        for item in value:
            keys |= _collect_object_keys(item)
    return keys


# ------------------------------------------------------------------------ executables


@dataclass(frozen=True)
class ExecutableIdentity:
    name: str
    path: str
    sha256: str | None
    version: str


def probe_executable(name: str, *, runner: Callable[..., Any] | None = None) -> ExecutableIdentity:
    located = shutil.which(name)
    if not located:
        raise CapabilityProofFailed(f"executable not on PATH: {name}")
    path = Path(located).resolve()
    try:
        digest: str | None = sha256_file(path)
    except OSError:
        digest = None
    run = runner or subprocess.run
    completed = run([str(path), "--version"], capture_output=True, text=True, timeout=60)
    if completed.returncode != 0:
        raise CapabilityProofFailed(f"{name} --version failed with {completed.returncode}")
    version = (completed.stdout or completed.stderr).strip().splitlines()[0]
    return ExecutableIdentity(name=name, path=str(path), sha256=digest, version=version)


# ---------------------------------------------------------------------- argv builders


def build_codex_argv(
    *,
    workspace: Path | str,
    model: str,
    reasoning_effort: str,
    instruction: str,
) -> list[str]:
    """The pinned Codex invocation (spec 7.3), corrected for observable identity (N30V7-F05).

    `--json` is not decoration: the JSONL event stream is the transport-isolation
    proof channel. But live evidence against the genuinely installed CLI (codex-cli
    0.147.0, N30V7-F05) proved that stream's `thread.started`/`turn.started`/
    `item.completed`/`turn.completed` events never carry a `model` field on any
    variant -- `--ephemeral`'s own on-disk rollout file is the only machine-readable
    Codex receipt that does (`turn_context.payload.model`, spec 7.3's "machine-readable
    Codex event/receipt"). `--ephemeral` is therefore dropped: every caller already runs
    this inside a disposable, per-activation `$CODEX_HOME` (`build_worker_environment`)
    or, for the driver-capability preflight probe, the operator's own real,
    already-authenticated `$CODEX_HOME` (`_probe_env`, by the same design that already
    accepted the real environment for that probe) -- so the rollout file this write adds
    is bounded to one of those two homes, never a shared, uncontrolled location.
    """
    return [
        "codex", "exec", "--ignore-user-config", "--ignore-rules",
        "-s", "read-only", "--skip-git-repo-check", "-C", str(workspace),
        "-m", model, "-c", f'model_reasoning_effort="{reasoning_effort}"',
        "--output-schema", "output.schema.json", "-o", "result.json",
        "--json", instruction,
    ]


def build_claude_argv(
    *,
    workspace: Path | str,
    model: str,
    effort: str,
    cli_schema_projection: Mapping[str, Any],
    tools: str = "",
) -> list[str]:
    """The pinned Claude invocation (spec 7.2).

    No positional instruction: `--tools ""` leaves the worker no file-reading tool, so
    the instruction and the authorized-input projection are delivered together on
    stdin (`build_claude_stdin_payload`), never as an argv token or a staged file the
    worker would have to open. `--json-schema` takes the CLI-schema projection inline
    as JSON text, not a file path — a live probe against the installed CLI proved a
    bare path argument and the canonical schema's own `$schema` dialect reference are
    both rejected (spec 7.2, N20-F03).

    `tools` defaults to empty (no change to every other job's contract). The one
    named exception is M01's `discover` phase (spec decision, N20V7-F13): it is
    dispatched with `tools="WebSearch"` so the worker can find and verify real
    candidate source locators instead of refusing outright when it has no way to
    confirm a URL exists. WebSearch is Claude Code's own built-in, subscription-
    authenticated tool -- it never touches this sandbox's file system or egress
    guard; the worker still cannot write a file (`--tools` grants nothing else),
    and `SourceRetriever` (egress.py) remains the only path that ever fetches,
    validates, hashes, or receipts source bytes. Every other job keeps `tools=""`.

    Permission mode tracks the same grant: `--permission-mode plan` (every other
    job) blocks tool execution outright even when a tool is named in `--tools` --
    live-verified (N20V7-F13): the worker refused to search at all, citing plan
    mode. `default` mode still headless-denies every call (no TTY to approve a
    prompt) -- also live-verified. `bypassPermissions` is the one mode that lets
    an already-`--tools`-restricted worker actually use the single tool it was
    granted without a prompt neither side can answer; it grants nothing `--tools`
    did not already name, so it is used only alongside a non-empty `tools`.
    """
    return [
        "claude", "--print",
        "--output-format", "stream-json", "--verbose",
        "--json-schema", canonical_json(dict(cli_schema_projection)),
        "--model", model, "--effort", effort,
        "--permission-mode", ("bypassPermissions" if tools else "plan"),
        "--tools", tools,
        "--add-dir", str(workspace),
        "--no-session-persistence",
        "--setting-sources", "",
    ]


def build_job_argv(
    route: JobRoute,
    *,
    workspace: Path,
    instruction: str | None = None,
    cli_schema_projection: Mapping[str, Any] | None = None,
    tools: str = "",
) -> list[str]:
    if route.cli == "codex":
        if instruction is None:
            raise RouteRejected(f"{route.job_id}: codex requires an instruction argument")
        return build_codex_argv(workspace=workspace, model=route.model,
                                reasoning_effort=route.reasoning_effort,
                                instruction=instruction)
    if cli_schema_projection is None:
        raise RouteRejected(f"{route.job_id}: claude requires a cli_schema_projection")
    return build_claude_argv(workspace=workspace, model=route.model,
                             effort=route.reasoning_effort,
                             cli_schema_projection=cli_schema_projection,
                             tools=tools)


def build_cli_schema_projection(schema: Mapping[str, Any]) -> dict[str, Any]:
    """The deterministic CLI-schema projection `--json-schema` actually accepts (spec 7.2).

    Strips `$schema` and any other dialect metadata the CLI's schema parameter does not
    accept, and rejects — never silently drops — an external `$ref` (one that does not
    resolve inside the document itself), since a silently dropped external reference
    would change validation semantics the canonical schema expresses. Pure function of
    the input schema, so two calls on the same canonical schema produce byte-identical
    output once serialized by `canonical_json`.
    """

    def _walk(node: Any, *, path: str) -> Any:
        if isinstance(node, Mapping):
            projected: dict[str, Any] = {}
            for key, value in node.items():
                if key == "$schema":
                    continue
                if key == "$ref":
                    if not (isinstance(value, str) and value.startswith("#")):
                        raise TransportError(
                            f"cli schema projection: external $ref not permitted at "
                            f"{path}: {value!r}")
                projected[key] = _walk(value, path=f"{path}/{key}")
            return projected
        if isinstance(node, list):
            return [_walk(item, path=f"{path}[{index}]") for index, item in enumerate(node)]
        return node

    return _walk(dict(schema), path="$")


def build_claude_stdin_payload(*, instruction: str, projection: Mapping[str, Any]) -> str:
    """The JSON-encoded `{instruction, authorized_input_projection}` document (spec 7.2).

    The same canonical projection also staged to `authorized_input.json` for durable
    receipt/audit hashing, delivered here on stdin because `--tools ""` leaves the
    Claude worker no file-reading tool to open that staged file with.
    """

    return canonical_json({
        "instruction": instruction,
        "authorized_input_projection": dict(projection),
    })


def redact_command(argv: Sequence[str]) -> list[str]:
    """Redact any long token, not only the last one.

    Codex's instruction is the final argv token, but Claude's inline CLI-schema
    projection (`--json-schema <text>`) is not last, so redaction cannot assume
    position; any token long enough to carry instruction or schema content is
    redacted by its own hash instead.
    """
    redacted: list[str] = []
    for token in argv:
        if len(token) > 200:
            redacted.append(f"<redacted:{sha256_bytes(token.encode())[:16]}>")
        else:
            redacted.append(token)
    return redacted


# --------------------------------------------------------------------- host sandbox


SANDBOX_UNAVAILABLE = "none"

INSTALL_PREFIXES = ("/opt/homebrew", "/usr/local", "/opt", "/usr", "/Library", "/System")


def executable_read_roots(executable_path: Path | str) -> tuple[Path, ...]:
    """The installation prefix the CLI needs to read to run at all.

    A packaged CLI is a symlink into a versioned cellar and may load its interpreter and
    shared libraries from a sibling package, so allowing only the binary's own directory
    aborts the process before it starts.
    """
    resolved = Path(executable_path).resolve()
    for prefix in INSTALL_PREFIXES:
        if resolved.is_relative_to(prefix):
            return (Path(prefix),)
    return (resolved.parent,)


def sandbox_mechanism() -> str:
    if sys.platform == "darwin" and shutil.which("sandbox-exec"):
        return "sandbox-exec"
    return SANDBOX_UNAVAILABLE


def _subpath_rules(paths: Sequence[Path]) -> str:
    seen: list[str] = []
    for path in paths:
        for candidate in {str(path), str(Path(path).resolve())}:
            if candidate not in seen:
                seen.append(candidate)
    return " ".join(f'(subpath "{candidate}")' for candidate in seen)


def _cli_runtime_scratch_rule() -> str:
    """The Claude Code CLI's own per-UID coordination directory (`/tmp/claude-<uid>`).

    Live-verified (N70): the installed `claude` binary always touches this path on
    startup regardless of `$HOME`/`$TMPDIR` -- it is not workspace content and carries
    no curriculum data, but under this profile's `(deny default)` it is unreachable,
    and a concurrent fan-out of sandboxed launches reproducibly (not merely rarely)
    turned that into a fatal `EPERM` for some fraction of them. `/tmp` is itself a
    symlink to `/private/tmp` on macOS, so both forms are named (`_subpath_rules`'
    existing literal+resolved convention) -- sandbox-exec's own `subpath` matching is
    resolved-path-sensitive and silently would not have matched the symlink form alone.
    """
    return _subpath_rules([Path(f"/tmp/claude-{os.getuid()}")])


# The macOS system services genuinely needed to complete a Keychain item lookup
# (unlock + ACL check + certificate trust evaluation for the TLS handshake that
# follows) -- named individually rather than a blanket `(allow mach-lookup)`,
# live-verified (N70/N20 recovery) as the exact, narrow set sufficient for the
# real installed `claude` CLI's own subscription OAuth lookup.
_KEYCHAIN_MACH_SERVICES = (
    "com.apple.SecurityServer",
    "com.apple.securityd",
    "com.apple.trustd",
    "com.apple.trustd.agent",
    "com.apple.ocspd",
)


def _keychain_access_rule() -> str:
    """Read-only reach to the operator's real login keychain, plus the narrow
    mach-lookup set that completes an OAuth item fetch through it.

    Never the operator's `$HOME`: the isolated worker's own `$HOME` still points at
    its disposable per-activation directory (`build_worker_environment`); this is
    the one, single, explicitly-named exception, and it grants no read access to
    curriculum-unrelated files -- `~/Library/Keychains` is an encrypted database
    macOS itself still gates per-item by requesting-process ACL and Keychain
    unlock state (`security find-generic-password`, live-verified), not a plaintext
    credential this sandbox rule alone exposes.
    """
    keychains = _subpath_rules([Path.home() / "Library" / "Keychains"])
    services = " ".join(f'(global-name "{name}")' for name in _KEYCHAIN_MACH_SERVICES)
    return f"(allow file-read* {keychains})\n(allow mach-lookup {services})\n"


def _codex_auth_file_rule() -> str:
    """Read-only reach to the one real file `codex_auth_provision` symlinks in.

    sandbox-exec's own `subpath` matching resolves symlinks to their target before
    checking access (live-verified: the isolated `$CODEX_HOME`'s own `writable`
    rule did not cover this, since the symlink's *target* sits outside `home`), so
    the profile must name the real, operator-home file explicitly -- scoped to the
    one file, never the whole `~/.codex/` tree (which also holds unrelated session
    history this sandbox has no reason to read).
    """
    return f"(allow file-read* {_subpath_rules([Path.home() / '.codex' / 'auth.json'])})\n"


def claude_auth_provision(home: Path, *, real_home: Path | None = None) -> bool:
    """Give an isolated per-activation `home` the minimal, non-content-bearing local
    state the installed Claude Code CLI needs to recognize an already-authorized
    subscription account and complete the real macOS Keychain OAuth lookup for it.

    Never an API key, never the operator's full `$HOME`: this copies only the four
    fields (`oauthAccount`, `userID`, `hasCompletedOnboarding`, `autoUpdates`) the
    live-verified minimal-config path needs out of the operator's real
    `~/.claude.json` -- never its `projects`/history/session content -- and links
    (never copies) `~/Library/Keychains` read-only so the actual OAuth secret is
    still resolved through the real, ACL-gated Keychain item, never duplicated to
    disk. Returns ``False`` (a legitimate, honest "not provisioned", not an error)
    when the operator's own machine has no real subscription config to draw from --
    the sandboxed CLI then genuinely reports not logged in, exactly as it should.

    `real_home` defaults to `Path.home()`; a test may point it at a synthetic
    directory to prove the copy/link behavior without touching the operator's own
    real account state.
    """
    real_home = Path(real_home) if real_home is not None else Path.home()
    real_config = real_home / ".claude.json"
    if not real_config.is_file():
        return False
    try:
        data = json.loads(real_config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, Mapping):
        return False
    oauth_account = data.get("oauthAccount")
    user_id = data.get("userID")
    if not isinstance(oauth_account, Mapping) or not isinstance(user_id, str) or not user_id:
        return False
    minimal = {
        "oauthAccount": dict(oauth_account),
        "userID": user_id,
        "hasCompletedOnboarding": True,
        "autoUpdates": False,
    }
    home = Path(home)
    (home / ".claude.json").write_text(canonical_json(minimal), encoding="utf-8")
    real_keychains = real_home / "Library" / "Keychains"
    if real_keychains.is_dir():
        library_dir = home / "Library"
        library_dir.mkdir(exist_ok=True)
        link_path = library_dir / "Keychains"
        if not link_path.exists():
            link_path.symlink_to(real_keychains)
    return True


def codex_auth_provision(codex_home: Path, *, real_codex_home: Path | None = None) -> bool:
    """Give an isolated per-activation `$CODEX_HOME` reach to the operator's existing
    Codex CLI subscription session -- never a fresh API key, never the operator's
    full `$HOME`.

    Materially different from `claude_auth_provision`: the installed Codex CLI's own
    subscription auth is not macOS-Keychain-mediated at all -- its ChatGPT OAuth
    session (`auth_mode: "chatgpt"`) lives as a bearer token directly inside
    `~/.codex/auth.json` (mode 0600), which is itself the credential, not a local
    pointer to one an OS access-control layer still gates per read. This still never
    copies the token to a new location (a symlink, resolved fresh on every read, so
    a real token rotation/refresh is reflected rather than silently going stale) and
    still names only this one file -- never `~/.codex/sessions/` or any other real
    Codex CLI state -- but the isolated `$CODEX_HOME` that receives it must remain
    exactly as disposable and workspace-scoped as it already is; this function grants
    no broader reach than that one link.
    """
    real_codex_home = Path(real_codex_home) if real_codex_home is not None else Path.home() / ".codex"
    real_auth = real_codex_home / "auth.json"
    if not real_auth.is_file():
        return False
    codex_home = Path(codex_home)
    codex_home.mkdir(parents=True, exist_ok=True)
    link_path = codex_home / "auth.json"
    if not link_path.exists():
        link_path.symlink_to(real_auth)
    return True


def render_sandbox_profile(
    *,
    workspace: Path,
    home: Path,
    readable: Sequence[Path] = (),
    allow_network: bool = True,
) -> str:
    writable = _subpath_rules([Path(workspace), Path(home)])
    readable_rule = _subpath_rules(list(readable)) if readable else ""
    network = (
        '(allow network-outbound (remote tcp "*:443") (remote tcp "*:80")'
        ' (remote udp "*:53") (remote unix-socket))\n(allow system-socket)\n'
        if allow_network else "(deny network*)\n"
    )
    lines = [
        "(version 1)",
        "(deny default)",
        '(import "system.sb")',
        "(allow process-exec* process-fork)",
        "(allow sysctl-read)",
        "(allow file-read-metadata)",
        "(allow signal (target self))",
        f"(allow file-read* file-write* {_cli_runtime_scratch_rule()})",
        _keychain_access_rule(),
        _codex_auth_file_rule(),
    ]
    if readable_rule:
        lines.append(f"(allow file-read* {readable_rule})")
    lines.append(f"(allow file-read* file-write* {writable})")
    return "\n".join(lines) + "\n" + network


def build_sandboxed_argv(
    argv: Sequence[str],
    *,
    profile_path: Path,
) -> list[str]:
    mechanism = sandbox_mechanism()
    if mechanism == SANDBOX_UNAVAILABLE:
        raise CapabilityProofFailed(
            f"no host process sandbox available on {sys.platform}; refusing to launch a model CLI")
    return ["/usr/bin/sandbox-exec", "-f", str(profile_path), *argv]


def prove_workspace_isolation(
    *,
    workspace: Path,
    home: Path,
    forbidden_paths: Sequence[Path],
    runner: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Run a real probe inside the constructed sandbox and record what it could reach."""
    mechanism = sandbox_mechanism()
    if mechanism == SANDBOX_UNAVAILABLE:
        return {"mechanism": SANDBOX_UNAVAILABLE, "enforced": False,
                "evidence": f"no sandbox mechanism on {sys.platform}",
                "readable_forbidden_paths": [str(p) for p in forbidden_paths]}

    run = runner or subprocess.run
    workspace = Path(workspace).resolve()
    home = Path(home).resolve()
    probe_file = workspace / "isolation_probe.txt"
    probe_file.write_text("probe\n", encoding="utf-8")
    profile_path = home / "isolation_probe.sb"
    profile_path.write_text(
        render_sandbox_profile(workspace=workspace, home=home, allow_network=False),
        encoding="utf-8")

    inside = run(["/usr/bin/sandbox-exec", "-f", str(profile_path), "/bin/cat", str(probe_file)],
                 capture_output=True, text=True, timeout=60)
    leaked: list[str] = []
    for target in forbidden_paths:
        attempt = run(
            ["/usr/bin/sandbox-exec", "-f", str(profile_path), "/bin/cat", str(target)],
            capture_output=True, text=True, timeout=60)
        if attempt.returncode == 0:
            leaked.append(str(target))
    probe_file.unlink()

    enforced = inside.returncode == 0 and not leaked
    return {
        "mechanism": mechanism,
        "enforced": enforced,
        "evidence": (
            f"staged read rc={inside.returncode}; "
            f"{len(forbidden_paths)} forbidden path(s) probed; {len(leaked)} readable"),
        "readable_forbidden_paths": leaked,
    }


# ------------------------------------------------------------------- capability proof


def prove_transport_capabilities(
    *,
    guard: EgressGuard,
    probe_root: Path,
    forbidden_paths: Sequence[Path],
    registry: Mapping[str, JobRoute] | None = None,
    runner: Callable[..., Any] | None = None,
    identity_help: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build the D03 transport capability proof; unproven required facets fail closed."""
    probe_root = Path(probe_root).resolve()
    workspace = probe_root / "workspace"
    home = probe_root / "home"
    workspace.mkdir(parents=True, exist_ok=True)
    home.mkdir(parents=True, exist_ok=True)
    isolation = prove_workspace_isolation(
        workspace=workspace, home=home, forbidden_paths=forbidden_paths, runner=runner)

    routes = registry if registry is not None else load_job_registry()
    clis = sorted({route.cli for route in routes.values()})
    required_flags = {"codex": "--json", "claude": "--json-schema"}
    observed_flags: dict[str, bool] = {}
    for cli in clis:
        help_text = (identity_help or {}).get(cli)
        if help_text is None:
            run = runner or subprocess.run
            args = [cli, "exec", "--help"] if cli == "codex" else [cli, "--help"]
            completed = run(args, capture_output=True, text=True, timeout=60)
            help_text = f"{completed.stdout}\n{completed.stderr}"
        observed_flags[cli] = required_flags[cli] in help_text

    facets: dict[str, dict[str, Any]] = {
        "filesystem_isolation": {
            "required": True,
            "enforced": bool(isolation["enforced"]),
            "mechanism": str(isolation["mechanism"]),
            "evidence": str(isolation["evidence"]),
            "limitation": None,
        },
        "python_process_egress_broker": {
            "required": True,
            "enforced": guard.installed,
            "mechanism": "socket.socket interception by EgressGuard",
            "evidence": f"guard installed={guard.installed}",
            "limitation": None,
        },
        "identity_observation": {
            "required": True,
            "enforced": all(observed_flags.values()),
            "mechanism": (
                "codex --json JSONL events; claude --output-format stream-json --verbose "
                "per-turn assistant message.model"),
            "evidence": canonical_json(observed_flags),
            "limitation": None,
        },
        "subprocess_network_scope": {
            "required": False,
            "enforced": isolation["mechanism"] != SANDBOX_UNAVAILABLE,
            "mechanism": "sandbox-exec network-outbound port scoping",
            "evidence": "outbound restricted to tcp 443/80 and udp 53",
            "limitation": (
                "sandbox-exec cannot pin an outbound host; the model CLI subprocess is "
                "constrained by port, not by provider hostname"),
        },
    }
    unsatisfied = sorted(
        name for name, facet in facets.items() if facet["required"] and not facet["enforced"])
    proof = {
        "proved_at_utc": utc_now().isoformat(),
        "platform": f"{platform.system()} {platform.release()}",
        "facets": facets,
        "satisfied": not unsatisfied,
        "unsatisfied_required_facets": unsatisfied,
    }
    jsonschema.Draft202012Validator(
        _load_json(SCHEMA_DIR / "internal_capability_proof.schema.json")).validate(proof)
    return proof


def require_capability_proof(proof: Mapping[str, Any] | None) -> None:
    if proof is None:
        raise CapabilityProofFailed("no transport capability proof was produced")
    missing = list(proof.get("unsatisfied_required_facets") or [])
    if not proof.get("satisfied") or missing:
        raise CapabilityProofFailed(
            f"required transport capability facets unproven: {missing or 'unknown'}")


# ------------------------------------------------------------------- identity observation


@dataclass(frozen=True)
class ObservedIdentity:
    family: str
    model: str
    model_source: str
    family_source: str


def resolve_codex_home(env: Mapping[str, str]) -> Path:
    """The `$CODEX_HOME` a codex invocation under this exact `env` actually resolves to.

    Mirrors the installed CLI's own precedence: an explicit `CODEX_HOME` wins; absent
    that, it falls back to `$HOME/.codex`.
    """
    codex_home = env.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home)
    home = env.get("HOME") or str(Path.home())
    return Path(home) / ".codex"


def _codex_thread_id(event_stream: str) -> str | None:
    """The `thread_id` this exact `--json` stdout named, or ``None`` if it never did."""
    for line in event_stream.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, Mapping) and event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
            if isinstance(thread_id, str) and thread_id:
                return thread_id
    return None


def _rollout_session_id(path: Path) -> str | None:
    """The rollout file's own declared session id, from its leading `session_meta` line."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            first = handle.readline().strip()
    except OSError:
        return None
    if not first.startswith("{"):
        return None
    try:
        event = json.loads(first)
    except json.JSONDecodeError:
        return None
    if not isinstance(event, Mapping) or event.get("type") != "session_meta":
        return None
    payload = event.get("payload")
    if not isinstance(payload, Mapping):
        return None
    session_id = payload.get("session_id")
    return session_id if isinstance(session_id, str) and session_id else None


def _rollout_files_for_thread(codex_home: Path, thread_id: str) -> list[Path]:
    sessions_root = Path(codex_home) / "sessions"
    if not sessions_root.is_dir():
        return []
    return sorted(
        path for path in sessions_root.glob("**/rollout-*.jsonl")
        if path.is_file() and _rollout_session_id(path) == thread_id)


def _final_rollout_identity(path: Path) -> tuple[str | None, str | None]:
    """The last `turn_context.model` in the file (reroute supersedes initial), plus provider."""
    model: str | None = None
    provider: str | None = None
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, Mapping):
                continue
            payload = event.get("payload")
            if not isinstance(payload, Mapping):
                continue
            event_type = event.get("type")
            if event_type == "session_meta":
                observed_provider = payload.get("model_provider")
                if isinstance(observed_provider, str) and observed_provider:
                    provider = observed_provider
            elif event_type == "turn_context":
                observed_model = payload.get("model")
                if isinstance(observed_model, str) and observed_model:
                    model = observed_model
    return model, provider


def observe_codex_identity(event_stream: str, *, codex_home: Path) -> ObservedIdentity:
    """Read the executed model out of *this exact invocation's* on-disk rollout file.

    Live evidence (N30V7-F05, codex-cli 0.147.0) proved the `--json` stdout stream
    itself never carries a `model` field on any event it emits, so copying that stream
    can never satisfy this check -- there is nothing in it to copy. The on-disk rollout
    file `build_codex_argv` now leaves behind (having dropped `--ephemeral`) does carry
    it, in `turn_context.payload.model`.

    `codex_home` is not necessarily private to this one call: a real job's is a fresh,
    disposable per-activation `$CODEX_HOME`, but the driver-capability preflight probe
    deliberately runs against the operator's real, long-lived `~/.codex`, which can hold
    rollout files from unrelated, concurrent, or historical invocations. Matching "the
    newest rollout file" would silently attribute another process's model to this one.
    The only trustworthy key is `thread.started.thread_id` from *this* stdout, matched
    against each candidate file's own `session_meta.payload.session_id`; zero or more
    than one match is refused as an unobservable identity, never guessed.
    """
    thread_id = _codex_thread_id(event_stream)
    if thread_id is None:
        raise IdentityUnobservable(
            "codex event stream never emitted thread.started; no thread_id to bind a "
            "rollout file to, so route conformance cannot be claimed")
    matches = _rollout_files_for_thread(Path(codex_home), thread_id)
    if not matches:
        raise IdentityUnobservable(
            f"no rollout file under {codex_home} matched thread_id {thread_id!r}; "
            "route conformance cannot be claimed")
    if len(matches) > 1:
        raise IdentityUnobservable(
            f"{len(matches)} rollout files under {codex_home} matched thread_id "
            f"{thread_id!r}; refusing an ambiguous identity binding")
    model, provider = _final_rollout_identity(matches[0])
    if not model:
        raise IdentityUnobservable(
            f"rollout file {matches[0]} for thread_id {thread_id!r} names no "
            "turn_context.model; route conformance cannot be claimed")
    return ObservedIdentity(
        family=REVIEW_FAMILY,
        model=model,
        model_source=f"codex_rollout:turn_context.model:{matches[0].name}",
        family_source=(f"codex_rollout:model_provider={provider}" if provider
                        else "executable_identity:codex-cli"),
    )


def _iter_stream_json_events(stream_text: str) -> list[Mapping[str, Any]]:
    events: list[Mapping[str, Any]] = []
    for line in stream_text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, Mapping):
            events.append(event)
    return events


def observe_claude_identity(stream_text: str) -> ObservedIdentity:
    """Read the executed model from the per-turn assistant event's `message.model`.

    Never from the final envelope's aggregate `modelUsage` map: a live probe against
    the installed CLI (2.1.231) proved that map is not guaranteed single-entry (a
    probe recorded `claude-haiku-4-5-20251001` alongside the requested
    `claude-sonnet-5`), so it cannot be the identity source (spec 7.2, N20-F05). The
    per-turn assistant event with `parent_tool_use_id` null is the unambiguous signal;
    the last such event wins, matching Codex's reroute-supersedes-initial rule.
    """
    model: str | None = None
    for event in _iter_stream_json_events(stream_text):
        if event.get("type") != "assistant":
            continue
        if event.get("parent_tool_use_id") is not None:
            continue
        message = event.get("message")
        if not isinstance(message, Mapping):
            continue
        observed = message.get("model")
        if isinstance(observed, str) and observed:
            model = observed
    if not model:
        raise IdentityUnobservable(
            "claude stream-json output names no per-turn assistant message.model "
            "(parent_tool_use_id null); route conformance cannot be claimed")
    return ObservedIdentity(
        family=AUTHORING_FAMILY,
        model=model,
        model_source="claude_stream_json:assistant.message.model",
        family_source="executable_identity:claude-cli",
    )


def observe_identity(route: JobRoute, *, stdout: str, codex_home: Path | None = None) -> ObservedIdentity:
    if route.cli == "codex":
        if codex_home is None:
            raise IdentityUnobservable(
                f"{route.job_id}: codex identity observation requires codex_home")
        return observe_codex_identity(stdout, codex_home=codex_home)
    return observe_claude_identity(stdout)


def prove_claude_tool_closure(
    stream_text: str, *, permitted_tools: frozenset[str] = CLAUDE_PERMITTED_TOOLS,
) -> dict[str, Any]:
    """Inspect the stream-json init event's tool/MCP-server lists directly (spec 7.1 class 5).

    Independent of what `--tools`/`--setting-sources` claim: a live probe found
    `--setting-sources ""` still listed three claude.ai MCP servers (all
    `needs-auth`, no tool) in the init event (N20-F06). Closure requires no tool
    beyond the permitted structured-output channel, and no MCP server whose status
    is not an auth/connection failure (i.e. nothing actually invokable).
    """
    init_event: Mapping[str, Any] | None = None
    for event in _iter_stream_json_events(stream_text):
        if event.get("type") == "system" and event.get("subtype") == "init":
            init_event = event
            break
    if init_event is None:
        raise CapabilityProofFailed(
            "claude stream-json output carries no system/init event; tool/MCP closure "
            "is unproven")
    tools = init_event.get("tools")
    if not isinstance(tools, list):
        raise CapabilityProofFailed("claude init event carries no tools list")
    observed_tools = sorted(str(item) for item in tools)
    extra_tools = sorted(set(observed_tools) - set(permitted_tools))

    mcp_servers = init_event.get("mcp_servers")
    observed_servers = list(mcp_servers) if isinstance(mcp_servers, list) else []
    non_invokable_status = {"needs-auth", "failed", "disconnected", "error"}
    invokable_servers = [
        server for server in observed_servers
        if isinstance(server, Mapping)
        and str(server.get("status", "")).lower() not in non_invokable_status
    ]
    closed = not extra_tools and not invokable_servers
    return {
        "closed": closed,
        "observed_tools": observed_tools,
        "extra_tools": extra_tools,
        "observed_mcp_servers": observed_servers,
        "invokable_mcp_servers": invokable_servers,
    }


def require_claude_tool_closure(closure: Mapping[str, Any]) -> None:
    if not closure.get("closed"):
        raise CapabilityProofFailed(
            f"claude tool/MCP closure unproven: extra_tools={closure.get('extra_tools')} "
            f"invokable_mcp_servers={closure.get('invokable_mcp_servers')}")


def assert_identity_matches(route: JobRoute, observed: ObservedIdentity) -> None:
    if observed.model != route.model:
        raise IdentityMismatch(
            f"{route.job_id}: decided model {route.model!r} but executed {observed.model!r}")
    if observed.family != route.family:
        raise IdentityMismatch(
            f"{route.job_id}: decided family {route.family!r} but executed {observed.family!r}")
    if route.is_review and observed.family == AUTHORING_FAMILY:
        raise IdentityMismatch(
            f"{route.job_id}: review must not execute in the authoring family")


# ------------------------------------------------------------------------ JSON parsing


def _reject_duplicate_keys(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise ResultParseError("duplicate_json_key", key)
        seen[key] = value
    return seen


def _reject_constant(name: str) -> Any:
    raise ResultParseError("non_finite_json_constant", name)


def parse_single_json_document(text: str) -> dict[str, Any]:
    """Parse exactly one JSON object; anything else is a malformed transport result."""
    if not text or not text.strip():
        raise ResultParseError("empty_result")
    if "```" in text:
        raise ResultParseError("fenced_result")
    stripped = text.lstrip()
    decoder = json.JSONDecoder(
        object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant)
    try:
        value, end = decoder.raw_decode(stripped)
    except json.JSONDecodeError as error:
        raise ResultParseError("malformed_json", str(error)) from error
    if stripped[end:].strip():
        raise ResultParseError("trailing_material", stripped[end:].strip()[:120])
    if not isinstance(value, dict):
        raise ResultParseError("result_is_not_an_object", type(value).__name__)
    return value


def extract_claude_structured_output(stdout: str) -> str:
    """One registered deterministic extractor: the final stream-json result event's
    `structured_output` field.

    The only channel available for a Claude job: `--tools ""` leaves the worker no
    file-write tool, so it can never write `result.json` itself.
    """
    result_event: Mapping[str, Any] | None = None
    for event in _iter_stream_json_events(stdout):
        if event.get("type") == "result":
            result_event = event
    if result_event is None:
        raise ResultParseError("no_claude_result_event")
    structured = result_event.get("structured_output")
    if structured is None:
        raise ResultParseError("claude_result_carries_no_structured_output")
    if isinstance(structured, str):
        return structured
    return canonical_json(structured)


def load_candidate(
    route: JobRoute,
    *,
    workspace: Path,
    stdout: str,
    schema: Mapping[str, Any],
) -> tuple[dict[str, Any], str]:
    result_path = Path(workspace) / "result.json"
    if result_path.is_file():
        document = result_path.read_text(encoding="utf-8")
        source = "result_file"
    elif route.cli == "claude":
        document = extract_claude_structured_output(stdout)
        source = "claude_stream_json_structured_output"
    else:
        raise ResultParseError("no_result_file_and_no_registered_envelope_extractor")
    candidate = parse_single_json_document(document)
    try:
        jsonschema.Draft202012Validator(dict(schema)).validate(candidate)
    except jsonschema.ValidationError as error:
        raise ResultParseError("schema_invalid_result", error.message) from error
    assert_no_authoritative_fields(candidate, label=f"{route.job_id} candidate")
    if route.job_id == "M01_RESEARCH_UNIT_SOURCES" and len(candidate) != 1:
        raise ResultParseError("m01_must_emit_exactly_one_phase_key")
    return candidate, source


# --------------------------------------------------------------------- attempt ledger


@dataclass(frozen=True)
class AttemptReservation:
    reservation_id: str
    activation_id: str
    job_id: str
    attempt_ordinal: int
    reserved_at_utc: str


class AttemptLedger:
    """D90's reservation surface: an attempt is committed before any process exists."""

    def __init__(self, *, attempts_per_activation: int = 2) -> None:
        self.attempts_per_activation = attempts_per_activation
        self._reserved: dict[str, list[AttemptReservation]] = {}

    def reserve(self, *, activation_id: str, job_id: str) -> AttemptReservation:
        existing = self._reserved.setdefault(activation_id, [])
        if len(existing) >= self.attempts_per_activation:
            raise AttemptLimitExceeded(
                f"{activation_id}: {len(existing)} attempts already reserved")
        reservation = AttemptReservation(
            reservation_id=f"{activation_id}#{len(existing) + 1}",
            activation_id=activation_id,
            job_id=job_id,
            attempt_ordinal=len(existing) + 1,
            reserved_at_utc=utc_now().isoformat(),
        )
        existing.append(reservation)
        return reservation

    def reservations(self, activation_id: str) -> tuple[AttemptReservation, ...]:
        return tuple(self._reserved.get(activation_id, ()))

    @property
    def total_reserved(self) -> int:
        return sum(len(items) for items in self._reserved.values())


# ------------------------------------------------------------------------- workspaces


@dataclass(frozen=True)
class StagedInput:
    name: str
    source_path: Path
    sha256: str


@dataclass
class Workspace:
    path: Path
    home: Path
    prompt_sha256: str
    schema_sha256: str
    input_sha256: str
    cli_schema_projection_sha256: str | None = None
    staged_sha256: dict[str, str] = field(default_factory=dict)
    baseline: dict[str, str] = field(default_factory=dict)

    def inventory(self) -> dict[str, str]:
        found: dict[str, str] = {}
        for item in sorted(self.path.rglob("*")):
            if item.is_file():
                found[str(item.relative_to(self.path))] = sha256_file(item)
        return found

    def assert_no_undeclared_writes(self, *, permitted_new: Sequence[str] = ()) -> None:
        after = self.inventory()
        allowed = set(permitted_new)
        for name, digest in after.items():
            if name in self.baseline:
                if self.baseline[name] != digest:
                    raise WorkspaceViolation(f"worker mutated staged file {name!r}")
            elif name not in allowed:
                raise WorkspaceViolation(f"worker wrote undeclared file {name!r}")

    def destroy(self) -> None:
        shutil.rmtree(self.path, ignore_errors=True)
        shutil.rmtree(self.home, ignore_errors=True)


def stage_workspace(
    *,
    output_root: Path | str,
    episode_id: str,
    activation_id: str,
    route: JobRoute,
    projection: Mapping[str, Any],
    authorization_receipt: Mapping[str, Any],
    staged_inputs: Sequence[StagedInput] = (),
    home_root: Path | str | None = None,
    cli_schema_projection: Mapping[str, Any] | None = None,
) -> Workspace:
    """Build the disposable activation directory described by spec 7.1."""
    root = Path(output_root).resolve() / ".workspaces" / episode_id / activation_id
    if root.exists():
        raise WorkspaceViolation(f"activation workspace already exists: {root}")
    root.mkdir(parents=True, mode=0o700)
    os.chmod(root, 0o700)

    home_parent = Path(home_root).resolve() if home_root else Path(tempfile.gettempdir()).resolve()
    home_parent.mkdir(parents=True, exist_ok=True)
    home = Path(tempfile.mkdtemp(prefix="plan26-home-", dir=str(home_parent)))
    os.chmod(home, 0o700)
    if route.cli == "claude":
        claude_auth_provision(home)
    elif route.cli == "codex":
        codex_auth_provision(home / "codex")

    prompt_source = resolve_prompt_path(route)
    schema_source = resolve_schema_path(route)
    schema = _load_json(schema_source)
    assert_no_authoritative_fields(schema, label=f"{route.job_id} output schema")

    payload = {"projection": dict(projection), "authorization_receipt": dict(authorization_receipt)}
    input_path = root / "authorized_input.json"
    input_path.write_text(canonical_json(payload), encoding="utf-8")
    shutil.copyfile(schema_source, root / "output.schema.json")
    shutil.copyfile(prompt_source, root / route.prompt)

    cli_schema_sha256: str | None = None
    if cli_schema_projection is not None:
        cli_schema_text = canonical_json(dict(cli_schema_projection))
        (root / "cli_schema_projection.json").write_text(cli_schema_text, encoding="utf-8")
        cli_schema_sha256 = sha256_bytes(cli_schema_text.encode("utf-8"))

    staged_digests: dict[str, str] = {}
    reserved = RESERVED_WORKSPACE_NAMES | {route.prompt}
    for item in staged_inputs:
        if not STAGED_NAME_PATTERN.match(item.name) or item.name in reserved:
            raise WorkspaceViolation(f"illegal staged input name: {item.name!r}")
        source = Path(item.source_path)
        if source.is_symlink() or not source.is_file():
            raise WorkspaceViolation(f"staged input is not a regular file: {source}")
        actual = sha256_file(source)
        if actual != item.sha256:
            raise WorkspaceViolation(
                f"staged input {item.name!r} hash {actual} != declared {item.sha256}")
        shutil.copyfile(source, root / item.name)
        os.chmod(root / item.name, stat.S_IRUSR)
        staged_digests[item.name] = actual

    workspace = Workspace(
        path=root,
        home=home,
        prompt_sha256=sha256_file(prompt_source),
        schema_sha256=sha256_file(schema_source),
        input_sha256=sha256_file(input_path),
        cli_schema_projection_sha256=cli_schema_sha256,
        staged_sha256=staged_digests,
    )
    workspace.baseline = workspace.inventory()
    return workspace


def build_worker_environment(*, home: Path, passthrough: Sequence[str] = ()) -> dict[str, str]:
    """Allowlisted environment over a dedicated temporary home; secrets pass by name only.

    `USER` is the one identity value carried through unconditionally, not behind
    `passthrough`: it is the real OS username, never a secret (already implicit in
    the process's real UID), but live-verified (N70/N20 recovery) as load-bearing
    for the installed Claude Code CLI's own macOS Keychain OAuth lookup to succeed
    at all under an otherwise fully isolated `$HOME`.
    """
    home = Path(home)
    environment = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin",
        "HOME": str(home),
        "TMPDIR": str(home),
        "XDG_CONFIG_HOME": str(home / "config"),
        "XDG_CACHE_HOME": str(home / "cache"),
        "CODEX_HOME": str(home / "codex"),
        "LANG": "C.UTF-8",
    }
    real_user = os.environ.get("USER")
    if real_user:
        environment["USER"] = real_user
    for child in ("config", "cache", "codex"):
        (home / child).mkdir(parents=True, exist_ok=True)
    for name in passthrough:
        value = os.environ.get(name)
        if value is not None:
            environment[name] = value
    return environment


# ---------------------------------------------------------------------- process runner


@dataclass(frozen=True)
class ProcessOutcome:
    returncode: int | None
    stdout: str
    stderr: str
    pid: int | None
    termination: str


def run_process(
    argv: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
    timeout_seconds: int,
    stdin: str | None = None,
    term_grace_seconds: float = 5.0,
) -> ProcessOutcome:
    """Process-group wall-clock timeout: TERM, wait five seconds, then KILL.

    `stdin` carries a Claude job's JSON-encoded `{instruction,
    authorized_input_projection}` document (spec 7.2); Codex jobs pass `None` and
    inherit no stdin, matching their existing positional-instruction shape.
    """
    process = subprocess.Popen(
        list(argv), cwd=str(cwd), env=dict(env), text=True,
        stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    termination = "exited"
    try:
        stdout, stderr = process.communicate(input=stdin, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        termination = "timeout_term"
        _signal_group(process, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=term_grace_seconds)
        except subprocess.TimeoutExpired:
            termination = "timeout_kill"
            _signal_group(process, signal.SIGKILL)
            stdout, stderr = process.communicate()
    if termination == "exited" and process.returncode is not None and process.returncode < 0:
        termination = "signal"
    return ProcessOutcome(
        returncode=process.returncode, stdout=stdout or "", stderr=stderr or "",
        pid=process.pid, termination=termination)


def _signal_group(process: subprocess.Popen[str], number: int) -> None:
    try:
        os.killpg(os.getpgid(process.pid), number)
    except (ProcessLookupError, PermissionError):
        process.send_signal(number)


# --------------------------------------------------- product capability surface
#
# D03, D11, D13 and D14 reach for five methods on `RuntimeContext.transport_registry`.
# They are capability work, not curriculum work: each does one bounded local job and
# raises on any tool fault, so the calling node classifies it as a system failure
# instead of letting a broken renderer reach the record as a product finding.

RENDER_TOOLS: tuple[str, ...] = ("pandoc", "typst")
RASTER_TOOLS: tuple[str, ...] = ("pdftoppm", "pdfinfo", "pdftotext", "pdfimages")
RENDER_DIRNAME = ".render"

# The nominal type size is recoverable from an ink box by pdf_inspect's constant,
# calibrated against this repository's own pandoc/typst/Helvetica toolchain.
_INK_BOX_RATIO = pdf_inspect._INK_BOX_RATIO
_BLANK_PAGE_RANGE = 2

_PAGE_SIZE_RE = re.compile(r'^width="([\d.]+)" height="([\d.]+)"')
_LINE_BOX_RE = re.compile(
    r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', re.S)


class RenderFault(TransportError):
    """A renderer, rasterizer, or artifact-store fault. Never a product finding."""


class UnavailableExternalFact(TransportError):
    """A named required external fact no local probe can supply (spec 2.4 item 6)."""

    def __init__(self, fact: str, detail: str = "") -> None:
        super().__init__(f"{fact}: {detail}" if detail else fact)
        self.fact = fact


def rasterize_pages(pdf: Path, directory: Path, *, dpi: int = 200) -> list[Path]:
    """One PNG per shipped page.

    `checks.rasterize_and_check_nonblank` aborts on the first blank page. D14 owes a
    result for *every* page and treats a blank one as a product finding, so the blank
    audit happens per page in `inspect_pages` rather than here.
    """
    if not shutil.which("pdftoppm"):
        raise RenderFault("pdftoppm unavailable; the rasterizer capability is unproven")
    directory.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(directory / "page")],
        capture_output=True, text=True, timeout=600)
    if completed.returncode != 0:
        raise RenderFault(f"rasterization failed: {completed.stderr.strip()[:500]}")
    pages = sorted(directory.glob("page-*.png"))
    declared = checks.pdf_page_count(pdf)
    if len(pages) != declared:
        raise RenderFault(f"rasterized {len(pages)} page(s) from a {declared}-page PDF")
    return pages


def page_is_blank(image_path: Path) -> bool:
    from PIL import Image

    with Image.open(image_path) as image:
        extrema = image.convert("L").getextrema()
    return extrema is None or (extrema[1] - extrema[0]) <= _BLANK_PAGE_RANGE


def page_text_problems(pdf: Path) -> dict[int, list[str]]:
    """Undersized and clipped text, per page, from one poppler pass.

    `pdf_inspect.text_legible` answers the same question for a whole document; D14's
    denominator is per page, so the same `-bbox-layout` output is split by page here.
    """
    if not shutil.which("pdftotext"):
        raise RenderFault("pdftotext unavailable; page inspection cannot be proven")
    completed = subprocess.run(
        ["pdftotext", "-bbox-layout", str(pdf), "-"],
        capture_output=True, text=True, timeout=600)
    if completed.returncode != 0:
        raise RenderFault(f"pdftotext failed: {completed.stderr.strip()[:500]}")
    problems: dict[int, list[str]] = {}
    for number, chunk in enumerate(completed.stdout.split("<page ")[1:], start=1):
        size = _PAGE_SIZE_RE.match(chunk)
        width = float(size.group(1)) if size else None
        height = float(size.group(2)) if size else None
        found: set[str] = set()
        for match in _LINE_BOX_RE.finditer(chunk):
            x_max, y_min, y_max = float(match.group(3)), float(match.group(2)), float(match.group(4))
            text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", match.group(5))).strip()
            if len(text) < 3:
                continue
            nominal = round((y_max - y_min) / _INK_BOX_RATIO, 2)
            if nominal < MIN_POINT_SIZE:
                found.add(f"text below {MIN_POINT_SIZE}pt ({nominal}pt): {text[:60]}")
            if width is not None and (x_max > width + 1 or y_max > (height or 0) + 1):
                found.add(f"line runs outside the page box: {text[:60]}")
        problems[number] = sorted(found)
    return problems


def compose_unit_markdown(unit_id: str, content: Mapping[str, Any]) -> str:
    """The deterministic layout source for one admitted unit content body."""
    sections = content.get("sections")
    if not isinstance(sections, list) or not sections:
        raise RenderFault(f"admitted content for {unit_id} declares no sections to render")
    lines = [f"# {unit_id}", ""]
    for ordinal, section in enumerate(sections):
        if not isinstance(section, Mapping):
            raise RenderFault(f"content section {ordinal} of {unit_id} is not an object")
        heading = section.get("heading")
        body = section.get("body")
        if not isinstance(heading, str) or not isinstance(body, str):
            raise RenderFault(f"content section {ordinal} of {unit_id} has no heading and body")
        lines += [f"## {heading}", "", body, ""]
    return "\n".join(lines) + "\n"


# Which deterministic renderer draws a brief of each authoritative kind. Topology kinds
# resolve through `visual_maps.render_map`, so the *domain's* own `map_kind` chooses the
# drawing, not the brief's word for it.
def _render_topology(domain: Mapping[str, Any]) -> str:
    return visual_maps.render_map(dict(domain))


def _render_power_path(domain: Mapping[str, Any]) -> str:
    return visual_maps.render_power_path(
        dict(domain.get("build_map") or {}), dict(domain.get("electrical") or {}))


def _render_parts(domain: Mapping[str, Any]) -> str:
    parts = domain.get("parts") or []
    if not parts:
        raise RenderFault("the domain names no parts to draw")
    return visual_maps.render_parts_diagram(list(parts), subject=str(domain.get("subject", "")))


def _render_safety_inset(domain: Mapping[str, Any]) -> str:
    failures = (domain.get("electrical") or {}).get("failure_modes") or []
    if not failures:
        raise RenderFault("the domain records no failure mode to draw a safety inset from")
    return visual_maps.render_warning_notice(dict(failures[0]))


# Poppler's utilities take `-v`, not `--version`, and print it on stderr.
_VERSION_FLAG = {name: "-v" for name in RASTER_TOOLS}


def tool_versions(names: Sequence[str]) -> dict[str, str]:
    """One real local invocation per tool; an absent or broken tool fails closed."""
    versions: dict[str, str] = {}
    for name in names:
        located = shutil.which(name)
        if not located:
            raise CapabilityProofFailed(f"executable not on PATH: {name}")
        completed = subprocess.run(
            [located, _VERSION_FLAG.get(name, "--version")],
            capture_output=True, text=True, timeout=60)
        printed = (completed.stdout or completed.stderr).strip().splitlines()
        if not printed:
            raise CapabilityProofFailed(f"{name} reports no version")
        versions[name] = printed[0]
    return versions


DETERMINISTIC_VISUAL_RENDERERS: Mapping[str, Callable[[Mapping[str, Any]], str]] = {
    "build_map": _render_topology,
    "breadboard": _render_topology,
    "wiring": _render_topology,
    "circuit": _render_topology,
    "electrical": _render_topology,
    "terminal_block": _render_topology,
    "connectivity": _render_topology,
    "schematic": _render_topology,
    "netlist": _render_topology,
    "power_path": _render_power_path,
    "pinout": _render_parts,
    "pin_map": _render_parts,
    "safety_inset": _render_safety_inset,
}


def _probe_model_cli_identity(transport: "CliTransport") -> dict[str, Any]:
    return {
        "executables": {
            name: transport.observe_executable(name)
            for name in sorted({route.cli for route in transport.registry.values()})
        }
    }


def _probe_retrieval(transport: "CliTransport") -> dict[str, Any]:
    if not transport.guard.installed:
        raise CapabilityProofFailed(
            "the process egress broker is not installed; no retrieval can be contained")
    return {"egress_broker": "EgressGuard", "mechanism": "socket.socket interception"}


def _probe_renderer(transport: "CliTransport") -> dict[str, Any]:
    return {"tools": tool_versions(RENDER_TOOLS)}


def _probe_rasterizer(transport: "CliTransport") -> dict[str, Any]:
    return {"tools": tool_versions(RASTER_TOOLS)}


def _probe_persistence(transport: "CliTransport") -> dict[str, Any]:
    probe_path = transport.output_root / RENDER_DIRNAME / "capability_probe.json"
    probe_path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json({"probe": "persistence", "at": utc_now().isoformat()})
    probe_path.write_text(payload, encoding="utf-8")
    written = probe_path.read_text(encoding="utf-8")
    probe_path.unlink()
    if written != payload:
        raise CapabilityProofFailed(f"the output root at {transport.output_root} does not read back")
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("create table probe (value text)")
        connection.execute("insert into probe values ('ok')")
        rows = connection.execute("select value from probe").fetchall()
    finally:
        connection.close()
    if rows != [("ok",)]:
        raise CapabilityProofFailed("the sqlite checkpoint engine does not round-trip a write")
    return {"output_root": str(transport.output_root), "sqlite_version": sqlite3.sqlite_version}


def _probe_logger(transport: "CliTransport") -> dict[str, Any]:
    evidence_root = transport.evidence_root
    evidence_root.mkdir(parents=True, exist_ok=True)
    probe_path = evidence_root / "capability_probe.log"
    with probe_path.open("a", encoding="utf-8") as handle:
        handle.write("")
    probe_path.unlink()
    return {"evidence_root": str(evidence_root)}


# One local probe per capability, in D03's own order. No entry may reach a model.
CAPABILITY_PROBES: Mapping[str, Callable[["CliTransport"], dict[str, Any]]] = {
    "model_cli_identity": _probe_model_cli_identity,
    "retrieval": _probe_retrieval,
    "renderer": _probe_renderer,
    "rasterizer": _probe_rasterizer,
    "persistence": _probe_persistence,
    "logger": _probe_logger,
}


# -------------------------------------------------------------------------- transport


@dataclass(frozen=True)
class TransportResult:
    candidate: dict[str, Any]
    receipt: dict[str, Any]
    attempts: tuple[dict[str, Any], ...]


class CliTransport:
    """Contained CLI model transport. The only path from this package to a model."""

    def __init__(
        self,
        *,
        output_root: Path | str,
        run_id: str,
        curriculum_digest: str,
        authorization: AuthorizationRecord | None,
        receipts: ReceiptLog,
        guard: EgressGuard,
        ledger: AttemptLedger,
        capability_proof: Mapping[str, Any] | None,
        registry: Mapping[str, JobRoute] | None = None,
        runner: Callable[..., ProcessOutcome] | None = None,
        evidence_root: Path | str | None = None,
        env_passthrough: Sequence[str] = (),
        keep_workspaces: bool = False,
        executables: Mapping[str, ExecutableIdentity] | None = None,
    ) -> None:
        self.output_root = Path(output_root).resolve()
        self.run_id = run_id
        self.curriculum_digest = curriculum_digest
        self.authorization = authorization
        self.receipts = receipts
        self.guard = guard
        self.ledger = ledger
        self.capability_proof = capability_proof
        self.registry = registry if registry is not None else load_job_registry()
        self.runner = runner or run_process
        self.evidence_root = (
            Path(evidence_root).resolve() if evidence_root
            else self.output_root / ".evidence" / "transport")
        self.env_passthrough = tuple(env_passthrough)
        self.keep_workspaces = keep_workspaces
        self._receipt_validator = jsonschema.Draft202012Validator(
            _load_json(SCHEMA_DIR / "internal_execution_receipt.schema.json"))
        self._executables: dict[str, ExecutableIdentity] = dict(executables or {})
        self.render_root = self.output_root / RENDER_DIRNAME
        self._artifacts = ArtifactStore(self.output_root)
        self._render_attempts: dict[str, int] = {}

    def executable(self, name: str) -> ExecutableIdentity:
        if name not in self._executables:
            self._executables[name] = probe_executable(name)
        return self._executables[name]

    # -------------------------------------------- product capability surface (D03)

    def prove_capability(self, capability: str) -> dict[str, Any]:
        """One bounded local probe. Never a curriculum model job (spec 6.2, D03)."""
        probe = CAPABILITY_PROBES.get(capability)
        if probe is None:
            return {"result": "MISSING", "capability": capability,
                    "detail": f"no local probe is registered for {capability!r}"}
        try:
            detail = probe(self)
        except UnavailableExternalFact as error:
            return {"result": "UNAVAILABLE_EXTERNAL_FACT", "capability": capability,
                    "fact": error.fact, "detail": str(error)[:500]}
        except (TransportError, checks.CheckFailure, OSError, sqlite3.Error) as error:
            return {"result": "MISSING", "capability": capability, "detail": str(error)[:500]}
        return {"result": "PASS", "capability": capability, "detail": detail}

    def observe_executable(self, name: str) -> dict[str, Any]:
        """The installed executable's own identity, resolved and hashed on this host."""
        identity = self.executable(name)
        return {"name": identity.name, "path": identity.path,
                "sha256": identity.sha256, "version": identity.version}

    # ------------------------------------ product capability surface (D11/D13/D14)

    def read_artifact_body(self, unit_id: str, channel: str, content_hash: str) -> dict[str, Any]:
        """The admitted artifact those bytes hash to, from the content-addressed store."""
        stream = ArtifactStream(scope=UNIT_SCOPE, channel=channel, unit_id=unit_id)
        path = self._artifacts.resolve(stream.blob_path(content_hash))
        if not path.is_file():
            raise RenderFault(
                f"no admitted {channel} artifact for {unit_id} at {content_hash} "
                f"under {self.output_root}")
        data = path.read_bytes()
        if sha256_bytes(data) != content_hash:
            raise RenderFault(f"the stored {channel} artifact for {unit_id} is not its own hash")
        body = json.loads(data)
        if not isinstance(body, dict):
            raise RenderFault(f"the admitted {channel} artifact for {unit_id} is not an object")
        return body

    def render_unit(self, unit_id: str, parents: Mapping[str, str]) -> dict[str, Any]:
        """Render one layout source and unit PDF from the admitted heads (D13)."""
        content_hash = parents.get("content")
        if not isinstance(content_hash, str) or not content_hash:
            raise RenderFault(f"render of {unit_id} was given no admitted content parent")
        content = self.read_artifact_body(unit_id, "content", content_hash)

        directory = self.render_root / unit_id / canonical_digest(dict(parents))
        directory.mkdir(parents=True, exist_ok=True)
        markdown = directory / f"{unit_id}.md"
        markdown.write_text(compose_unit_markdown(unit_id, content), encoding="utf-8")
        pdf = directory / f"{unit_id}.pdf"
        completed = subprocess.run(
            ["pandoc", str(markdown), "--resource-path", str(directory),
             "--pdf-engine=typst", "-V", "mainfont=Helvetica",
             "-V", "geometry:margin=0.8in", "-V", "fontsize=11pt", "-o", str(pdf)],
            cwd=str(directory), capture_output=True, text=True, timeout=600)
        if completed.returncode != 0:
            raise RenderFault(f"pandoc/typst failed for {unit_id}: {completed.stderr.strip()[:500]}")
        if not pdf.is_file():
            raise RenderFault(f"pandoc reported success but wrote no PDF for {unit_id}")

        self._render_attempts[unit_id] = self._render_attempts.get(unit_id, 0) + 1
        return {
            "layout_path": str(markdown),
            "layout_sha256": sha256_file(markdown),
            "pdf_path": str(pdf),
            "pdf_sha256": sha256_file(pdf),
            "renderer": "pandoc --pdf-engine=typst",
            "attempt": self._render_attempts[unit_id],
        }

    def inspect_pages(self, pdf_path: str, pdf_sha256: str) -> dict[str, Any]:
        """Rasterize and inspect every page of the exact shipped PDF (D14)."""
        path = Path(pdf_path)
        if not path.is_file():
            raise RenderFault(f"the PDF to inspect does not exist: {path}")
        actual = sha256_file(path)
        if actual != pdf_sha256:
            raise RenderFault(
                f"the PDF at {path} hashes to {actual}, not the declared {pdf_sha256}")

        images = rasterize_pages(path, self.render_root / "pages" / pdf_sha256)
        text_problems = page_text_problems(path)
        pages: list[dict[str, Any]] = []
        for number, image in enumerate(images, start=1):
            blank = page_is_blank(image)
            problems = list(text_problems.get(number, ()))
            if blank:
                problems.append("the page renders no ink")
            pages.append({
                "number": number,
                "page_sha256": sha256_file(image),
                "image_path": str(image),
                "problems": sorted(problems),
                "unreadable": blank,
            })
        return {"pdf_sha256": pdf_sha256, "pages": pages}

    def render_deterministic_visual(
        self, brief: Mapping[str, Any], permitted_facts: Sequence[str]
    ) -> dict[str, Any]:
        """Draw one authoritative visual from the admitted domain, never from a model (D11)."""
        kind = brief.get("kind")
        renderer = DETERMINISTIC_VISUAL_RENDERERS.get(str(kind))
        if renderer is None:
            raise RenderFault(f"no deterministic renderer for visual kind {kind!r}")
        unit_id, domain_hash, key = brief.get("unit_id"), brief.get("domain_hash"), brief.get("key")
        if not all(isinstance(value, str) and value for value in (unit_id, domain_hash, key)):
            raise RenderFault(f"visual brief {key!r} names no unit, domain head, and key")

        domain = self.read_artifact_body(str(unit_id), "domain", str(domain_hash))
        svg = renderer(domain)

        directory = self.render_root / str(unit_id) / "visuals" / str(domain_hash)
        directory.mkdir(parents=True, exist_ok=True)
        asset = directory / (re.sub(r"[^A-Za-z0-9._-]", "_", str(key)) + ".svg")
        asset.write_text(svg, encoding="utf-8")
        return {
            "asset_path": str(asset),
            "sha256": sha256_file(asset),
            "format": "svg",
            "permitted_facts": sorted(str(fact) for fact in permitted_facts or ()),
        }

    def execute(
        self,
        *,
        job_id: str,
        activation_id: str,
        episode_id: str,
        projection: Mapping[str, Any],
        staged_inputs: Sequence[StagedInput] = (),
        data_classes: Sequence[str] | None = None,
        web_search: bool = False,
    ) -> TransportResult:
        route = resolve_route(job_id, self.registry)
        resolve_prompt_path(route)
        resolve_schema_path(route)
        requested = tuple(data_classes) if data_classes is not None else route.data_classes
        undeclared = sorted(set(requested) - set(route.data_classes))
        if undeclared:
            raise RouteRejected(f"{route.job_id}: undeclared data classes {undeclared}")
        if web_search and route.cli != "claude":
            raise RouteRejected(f"{route.job_id}: web_search is a Claude-only tool grant")

        authorization_receipt = authorize_subprocess_transmission(
            self.authorization, provider=route.provider, data_classes=requested,
            curriculum_digest=self.curriculum_digest, run_id=self.run_id,
            output_root=self.output_root, receipts=self.receipts)

        require_capability_proof(self.capability_proof)

        attempts: list[dict[str, Any]] = []
        last_error: TransportRetryable | None = None
        for attempt_index in range(route.retry_limit + 1):
            attempt_activation = (
                activation_id if attempt_index == 0 else f"{activation_id}.retry{attempt_index}")
            reservation = self.ledger.reserve(
                activation_id=activation_id, job_id=route.job_id)
            try:
                candidate, receipt = self._attempt(
                    route=route, reservation=reservation,
                    activation_id=attempt_activation, episode_id=episode_id,
                    projection=projection, staged_inputs=staged_inputs,
                    authorization_receipt=authorization_receipt, web_search=web_search)
            except TransportRetryable as error:
                attempts.append(error.receipt)  # type: ignore[attr-defined]
                last_error = error
                continue
            attempts.append(receipt)
            return TransportResult(candidate=candidate, receipt=receipt,
                                   attempts=tuple(attempts))
        assert last_error is not None
        raise last_error

    def _attempt(
        self,
        *,
        route: JobRoute,
        reservation: AttemptReservation,
        activation_id: str,
        episode_id: str,
        projection: Mapping[str, Any],
        staged_inputs: Sequence[StagedInput],
        authorization_receipt: Mapping[str, Any],
        web_search: bool = False,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        executable = self.executable(route.cli)
        cli_schema_projection = (
            build_cli_schema_projection(load_output_schema(route))
            if route.cli == "claude" else None)
        workspace = stage_workspace(
            output_root=self.output_root, episode_id=episode_id, activation_id=activation_id,
            route=route, projection=projection, authorization_receipt=authorization_receipt,
            staged_inputs=staged_inputs, cli_schema_projection=cli_schema_projection)
        instruction = (workspace.path / route.prompt).read_text(encoding="utf-8")
        stdin_text: str | None = None
        if route.cli == "claude":
            argv = build_job_argv(route, workspace=workspace.path,
                                  cli_schema_projection=cli_schema_projection,
                                  tools=("WebSearch" if web_search else ""))
            stdin_text = build_claude_stdin_payload(instruction=instruction, projection=projection)
        else:
            argv = build_job_argv(route, workspace=workspace.path, instruction=instruction)
        profile_path = workspace.home / "profile.sb"
        profile_path.write_text(
            render_sandbox_profile(
                workspace=workspace.path, home=workspace.home,
                readable=executable_read_roots(executable.path)),
            encoding="utf-8")
        sandboxed = build_sandboxed_argv(argv, profile_path=profile_path)
        environment = build_worker_environment(
            home=workspace.home, passthrough=self.env_passthrough)

        started = utc_now()
        monotonic = time.monotonic()
        outcome = self.runner(
            sandboxed, cwd=workspace.path, env=environment,
            timeout_seconds=route.timeout_seconds, stdin=stdin_text)
        ended = utc_now()

        evidence_dir = self.evidence_root / episode_id / activation_id
        evidence_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = evidence_dir / "stdout.txt"
        stderr_path = evidence_dir / "stderr.txt"
        stdout_path.write_text(outcome.stdout, encoding="utf-8")
        stderr_path.write_text(outcome.stderr, encoding="utf-8")

        receipt: dict[str, Any] = {
            "activation_id": activation_id,
            "attempt_ordinal": reservation.attempt_ordinal,
            "reservation_id": reservation.reservation_id,
            "job_id": route.job_id,
            "job_type": route.job_type,
            "decided_family": route.family,
            "decided_model": route.model,
            "decided_reasoning_effort": route.reasoning_effort,
            "observed_family": None,
            "observed_model": None,
            "observed_identity_source": None,
            "executable_path": executable.path,
            "executable_sha256": executable.sha256,
            "executable_version": executable.version,
            "redacted_command": redact_command(sandboxed),
            "returncode": outcome.returncode,
            "pid": outcome.pid,
            "started_utc": started.isoformat(),
            "ended_utc": ended.isoformat(),
            "duration_seconds": round(time.monotonic() - monotonic, 6),
            "timeout_seconds": route.timeout_seconds,
            "termination": outcome.termination,
            "workspace_path": str(workspace.path),
            "authorized_input_sha256": workspace.input_sha256,
            "output_schema_sha256": workspace.schema_sha256,
            "cli_schema_projection_sha256": workspace.cli_schema_projection_sha256,
            "prompt_sha256": workspace.prompt_sha256,
            "staged_input_sha256": dict(workspace.staged_sha256),
            "result_sha256": None,
            "stdout_evidence_path": str(stdout_path),
            "stderr_evidence_path": str(stderr_path),
            "stdout_sha256": sha256_bytes(outcome.stdout.encode("utf-8")),
            "stderr_sha256": sha256_bytes(outcome.stderr.encode("utf-8")),
            "sandbox_mechanism": sandbox_mechanism(),
            "authorization_receipt_id": str(authorization_receipt["receipt_id"]),
            "outcome": "transport_failure",
            "failure_class": None,
            "failure_detail": None,
            "workspace_inventory_before": sorted(workspace.baseline),
            "workspace_inventory_after": sorted(workspace.inventory()),
        }

        try:
            if outcome.termination in {"timeout_term", "timeout_kill"}:
                raise TransportRetryable("timeout", outcome.termination)
            if outcome.returncode != 0:
                raise TransportRetryable("nonzero_exit", str(outcome.returncode))
            observed = observe_identity(
                route, stdout=outcome.stdout, codex_home=workspace.home / "codex")
            receipt["observed_family"] = observed.family
            receipt["observed_model"] = observed.model
            receipt["observed_identity_source"] = (
                f"{observed.model_source}|{observed.family_source}")
            assert_identity_matches(route, observed)
            candidate, source = load_candidate(
                route, workspace=workspace.path, stdout=outcome.stdout,
                schema=load_output_schema(route))
            workspace.assert_no_undeclared_writes(permitted_new=("result.json",))
        except TransportError as error:
            receipt["failure_class"] = getattr(error, "failure_class", type(error).__name__)
            receipt["failure_detail"] = str(error)[:2000]
            receipt["workspace_inventory_after"] = sorted(workspace.inventory())
            self._finalize(receipt, workspace)
            if isinstance(error, TransportRetryable):
                error.receipt = receipt  # type: ignore[attr-defined]
            raise

        result_path = workspace.path / "result.json"
        receipt["result_sha256"] = (
            sha256_file(result_path) if result_path.is_file()
            else sha256_bytes(canonical_json(candidate).encode("utf-8")))
        receipt["observed_identity_source"] = f"{receipt['observed_identity_source']}|{source}"
        receipt["outcome"] = "candidate_produced"
        receipt["workspace_inventory_after"] = sorted(workspace.inventory())
        self._finalize(receipt, workspace)
        return candidate, receipt

    def _finalize(self, receipt: dict[str, Any], workspace: Workspace) -> None:
        self._receipt_validator.validate(receipt)
        if not self.keep_workspaces:
            workspace.destroy()


class FakeCliTransport:
    """Test-only transport.

    It refuses any root outside the system temporary directory and validates its canned
    responses against the real job schema, so it can neither touch a product root nor
    return a field that could be read as a terminal.
    """

    def __init__(
        self,
        *,
        sandbox_root: Path | str,
        responses: Mapping[str, Mapping[str, Any]],
        registry: Mapping[str, JobRoute] | None = None,
    ) -> None:
        root = Path(sandbox_root).resolve()
        temp_root = Path(tempfile.gettempdir()).resolve()
        if not root.is_relative_to(temp_root):
            raise TransportError(
                f"fake transport root must live under {temp_root}, got {root}")
        if root == REPO_ROOT or REPO_ROOT in root.parents or root.is_relative_to(REPO_ROOT):
            raise TransportError("fake transport must not address a product root")
        self.sandbox_root = root
        self.responses = {job: dict(payload) for job, payload in responses.items()}
        self.registry = registry if registry is not None else load_job_registry()

    def execute(self, *, job_id: str, activation_id: str, **_: Any) -> TransportResult:
        route = resolve_route(job_id, self.registry)
        candidate = self.responses.get(job_id)
        if candidate is None:
            raise RouteRejected(f"fake transport has no canned response for {job_id}")
        jsonschema.Draft202012Validator(load_output_schema(route)).validate(candidate)
        assert_no_authoritative_fields(candidate, label=f"fake {job_id} candidate")
        receipt = {
            "activation_id": activation_id,
            "job_id": route.job_id,
            "decided_model": route.model,
            "decided_family": route.family,
            "observed_identity_source": "fake_transport",
            "outcome": "candidate_produced",
            "sandbox_mechanism": "fake_transport_no_process",
        }
        return TransportResult(candidate=dict(candidate), receipt=receipt, attempts=(receipt,))
````

</details>

## FILE: runtime/langgraph_factory/model_nodes.py

SHA-256: `47483f1892f51c33a4986b264966d539c63106909f14b3e5dad817863ff972f4`

<details><summary>Exact content</summary>

````
"""The eight model job adapters (spec 6.3) plus D90/D91 attempt bookkeeping.

Each adapter is thin: it proves a D90 reservation exists, materializes exactly one
authorized projection from spec section 9's allowlist, invokes the frozen N13
transport once, validates the structured candidate against the declared boundary,
and returns a typed pre-admission state update.

A model node can never admit, merge, route, accept, resume, or terminate. It writes
only the candidate channels in ``MODEL_NODE_WRITABLE_FIELDS``; every head, accepted
receipt, and terminal channel is code-owned by a deterministic node.
"""

from __future__ import annotations

import ast
import copy
import dataclasses
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import jsonschema

from . import transport as tp
from .reducers import canonical_digest
from .state import RuntimeContext

__all__ = [
    "MODEL_NODE_IDS",
    "MODEL_NODE_FAMILIES",
    "MODEL_NODE_ATTEMPT_LIMIT",
    "MODEL_NODE_WRITABLE_FIELDS",
    "FORBIDDEN_MODEL_NODE_FIELDS",
    "ADMISSION_OWNED_CANDIDATE_FIELDS",
    "PROJECTION_SPECS",
    "ProjectionSpec",
    "ModelNodeContext",
    "ModelNodeError",
    "ProjectionViolation",
    "RepairBoundaryViolation",
    "PageDenominatorViolation",
    "CandidateRejected",
    "AttemptNotReserved",
    "FamilyViolation",
    "build_projection",
    "build_model_node_context",
    "build_test_model_node_context",
    "build_model_nodes",
    "reserve_model_attempt",
    "classify_model_failure",
    "MODEL_BOOKKEEPING_NODES",
    "D90_RESERVE_MODEL_ATTEMPT",
    "D91_CLASSIFY_MODEL_FAILURE",
    "m01_research_unit_sources",
    "m01_discover_unit_sources",
    "m01_interpret_unit_sources",
    "m02_create_unit_domain_data",
    "m03_write_unit_content",
    "m04_create_unit_visuals",
    "m05_review_actual_unit",
    "m06_repair_named_unit_artifact",
    "m07_review_actual_workbook",
    "m08_repair_named_workbook_defect",
]


# --------------------------------------------------------------------------- errors


class ModelNodeError(RuntimeError):
    """A model node boundary was violated. Never retried by this module."""


class ProjectionViolation(ModelNodeError):
    """The dispatching deterministic node offered an inadmissible packet."""


class RepairBoundaryViolation(ProjectionViolation):
    """A repair packet or candidate reaches outside its one declared boundary."""


class PageDenominatorViolation(ProjectionViolation):
    """A review packet or finding set does not match the exact frozen page set."""


class CandidateRejected(ModelNodeError):
    """A structured model candidate failed schema, control-field, or scope validation."""


class AttemptNotReserved(ModelNodeError):
    """No D90 reservation was committed before this dispatch."""


class FamilyViolation(ModelNodeError):
    """A route executed in a family the frozen registry does not authorize."""


# ------------------------------------------------------------------------ constants

MODEL_NODE_IDS: tuple[str, ...] = (
    "M01_RESEARCH_UNIT_SOURCES",
    "M02_CREATE_UNIT_DOMAIN_DATA",
    "M03_WRITE_UNIT_CONTENT",
    "M04_CREATE_UNIT_VISUALS",
    "M05_REVIEW_ACTUAL_UNIT",
    "M06_REPAIR_NAMED_UNIT_ARTIFACT",
    "M07_REVIEW_ACTUAL_WORKBOOK",
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT",
)

MODEL_NODE_FAMILIES: Mapping[str, str] = {
    "M01_RESEARCH_UNIT_SOURCES": tp.AUTHORING_FAMILY,
    "M02_CREATE_UNIT_DOMAIN_DATA": tp.AUTHORING_FAMILY,
    "M03_WRITE_UNIT_CONTENT": tp.AUTHORING_FAMILY,
    "M04_CREATE_UNIT_VISUALS": tp.AUTHORING_FAMILY,
    "M05_REVIEW_ACTUAL_UNIT": tp.REVIEW_FAMILY,
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": tp.AUTHORING_FAMILY,
    "M07_REVIEW_ACTUAL_WORKBOOK": tp.REVIEW_FAMILY,
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": tp.AUTHORING_FAMILY,
}

# One original activation plus at most one D91-authorized retry, matching the frozen
# per-route `retry_limit: 1`. D91 may never exceed this.
MODEL_NODE_ATTEMPT_LIMIT = 2

RESERVATION_KIND = "model_attempt_reservation"

MODEL_NODE_WRITABLE_FIELDS: frozenset[str] = frozenset({
    "source_discoveries",
    "source_interpretations",
    "artifact_versions",
    "visual_results",
    "unit_reviews",
    "workbook_reviews",
    "workbook_versions",
    "model_execution_receipts",
    "activation_receipts",
    "pending_failure",
})

FORBIDDEN_MODEL_NODE_FIELDS: frozenset[str] = frozenset({
    "artifact_heads",
    "workbook_head",
    "accepted_unit_receipts",
    "accepted_unit_checkpoint_receipts",
    "terminal",
    "terminal_history",
    "terminal_candidate",
    "unit_status",
    "source_admissions",
    "deterministic_checks",
    "final_release_audits",
    "pending_guard",
    "resume_frontier",
    "cursor",
})

ADMISSION_OWNED_CANDIDATE_FIELDS: frozenset[str] = frozenset({
    "version", "hash", "parent_hash",
})

RESERVE_ATTEMPT_WRITABLE_FIELDS: frozenset[str] = frozenset({
    "attempt_counters", "activation_receipts", "pending_guard", "pending_packet",
})

CLASSIFY_FAILURE_WRITABLE_FIELDS: frozenset[str] = frozenset({
    "failure_fingerprints", "pending_failure", "pending_guard", "terminal_candidate",
})

# Transient or malformed transport outcomes: the only class D91 may send back to D90.
RETRYABLE_FAILURE_CLASSES: frozenset[str] = frozenset({
    "empty_result",
    "fenced_result",
    "malformed_json",
    "trailing_material",
    "result_is_not_an_object",
    "duplicate_json_key",
    "non_finite_json_constant",
    "envelope_carries_no_response",
    "schema_invalid_result",
    "m01_must_emit_exactly_one_phase_key",
    "timeout",
    "nonzero_exit",
    # An activation D92 found with no execution receipt: nobody observed its
    # outcome, so it is transient by construction and a later attempt must still
    # pass D90 (spec 6.2 D92, section 11.3).
    "aborted_activation",
    # M01 discover, WebSearch-backed (N20V7-F13): the worker searched and found
    # nothing it could verify. Never a fabricated locator and never a silent
    # success -- bounded retry, then honest CONVERGENCE_EXHAUSTED, exactly like
    # any other transient outcome; never the human-facing prerequisite pause
    # D06B raises for the unrelated case of no discovery having run at all.
    "no_verified_source",
})

# Content the model actually produced but that violates its declared scope. These are
# repaired through the targeted-repair engine; re-running the same transport call
# would only reproduce them.
POLICY_OR_CONTENT_FAILURE_CLASSES: frozenset[str] = frozenset({
    "candidate_control_field",
    "candidate_undeclared_artifact",
    "candidate_boundary_violation",
    "candidate_page_denominator",
    "candidate_authoritative_visual",
    "policy_refusal",
    "content_violation",
})

# Integrity faults. Never retried, never repaired: they become a system terminal.
SYSTEM_FAILURE_CLASSES: frozenset[str] = frozenset({
    "IdentityMismatch",
    "IdentityUnobservable",
    "RouteRejected",
    "CapabilityProofFailed",
    "WorkspaceViolation",
    "AttemptLimitExceeded",
    "AuthorizationDenied",
    "family_violation",
})

# A model brief that would invent an authoritative circuit/pin/electrical fact is
# never eligible for M04; a deterministic producer owns those (spec 9, section 13).
AUTHORITATIVE_VISUAL_CLASSES: frozenset[str] = frozenset({
    "circuit", "schematic", "netlist", "pinout", "pin_map", "breadboard",
    "wiring", "electrical", "power_path", "terminal_block",
})

WORKBOOK_OWNED_COMPONENTS: frozenset[str] = frozenset({
    "front_matter", "navigation", "layout", "assembly",
})

# Persisted state channels and verdict hints that may never enter any projection.
DENIED_PROJECTION_NAMES: frozenset[str] = frozenset({
    "artifact_heads", "workbook_head", "accepted_unit_receipts",
    "accepted_unit_checkpoint_receipts", "terminal", "terminal_history",
    "terminal_candidate", "route_decisions", "pending_guard", "pending_failure",
    "resume_frontier", "resume_from", "attempt_counters", "failure_fingerprints",
    "unit_reviews", "workbook_reviews", "review_packets", "workbook_review_packets",
    "repair_requests", "workbook_repair_requests", "retest_plans", "retest_results",
    "workbook_retests", "invalidations", "workbook_invalidations",
    "finding_partitions", "workbook_finding_partitions", "unit_status", "cursor",
    "model_execution_receipts", "activation_receipts", "capability_receipts",
    "checkpoint_metadata", "final_release_audits", "evidence_index_entries",
    "log_audit_receipts", "external_authorizations", "source_admissions",
    "deterministic_checks", "output_root", "engine_root", "curriculum_root",
    "active_manifest_path", "frozen_inputs", "effective_run", "invocation",
    "desired_verdict", "expected_verdict", "target_verdict", "author_history",
    "repair_history", "reviewer_history", "sibling_units", "full_state", "state",
})

# Additional names a review job may never see: anything that hints at the wanted
# outcome, or that reveals who authored or repaired the artifact under review.
REVIEW_DENIED_NAMES: frozenset[str] = frozenset({
    "verdict", "prior_findings", "previous_findings", "prompt", "prompts",
    "model_output", "model_outputs", "job_outputs", "author_notes", "authored_by",
    "attempt", "attempts", "attempt_count", "counter", "counters", "retry_count",
})


# ------------------------------------------------------------------- projection table


@dataclasses.dataclass(frozen=True)
class ProjectionSpec:
    """One row of spec section 9's context table, materialized as code."""

    name: str
    job_id: str
    family: str
    allowed: tuple[str, ...]
    required: tuple[str, ...]
    denied: frozenset[str]
    excluded_doc: str

    @property
    def is_review(self) -> bool:
        return self.family == tp.REVIEW_FAMILY


def _spec(
    name: str,
    job_id: str,
    allowed: tuple[str, ...],
    required: tuple[str, ...],
    denied: Sequence[str],
    excluded_doc: str,
) -> ProjectionSpec:
    family = MODEL_NODE_FAMILIES[job_id]
    extra = REVIEW_DENIED_NAMES if family == tp.REVIEW_FAMILY else frozenset()
    return ProjectionSpec(
        name=name,
        job_id=job_id,
        family=family,
        allowed=allowed,
        required=required,
        denied=DENIED_PROJECTION_NAMES | frozenset(denied) | extra,
        excluded_doc=excluded_doc,
    )


PROJECTION_SPECS: Mapping[str, ProjectionSpec] = {
    "M01_discovery": _spec(
        "M01_discovery", "M01_RESEARCH_UNIT_SOURCES",
        allowed=("request", "unit", "source_rules", "discovery_authority"),
        required=("request", "unit", "source_rules", "discovery_authority"),
        denied=("sibling_requests", "source_requests", "retrievals", "retrieval_group"),
        excluded_doc="sibling requests/units, author history, acceptance, output tree",
    ),
    "M01_interpretation": _spec(
        "M01_interpretation", "M01_RESEARCH_UNIT_SOURCES",
        allowed=("request", "unit", "source_rules", "retrieval_group"),
        required=("request", "unit", "source_rules", "retrieval_group"),
        denied=("discovery_authority", "browsing_authority", "network_access",
                "repository_access", "other_retrieval_groups"),
        excluded_doc="network/repository access, other retrieval groups, "
                     "routing/acceptance state",
    ),
    "M02_domain": _spec(
        "M02_domain", "M02_CREATE_UNIT_DOMAIN_DATA",
        allowed=("unit", "admitted_sources", "domain_schema", "domain_config",
                 "verifier_interface", "calibration"),
        required=("unit", "admitted_sources", "domain_schema", "verifier_interface"),
        denied=("unit_content", "content_drafts", "sibling_artifacts"),
        excluded_doc="content drafts, reviews, sibling units, terminals",
    ),
    "M03_content": _spec(
        "M03_content", "M03_WRITE_UNIT_CONTENT",
        allowed=("unit", "admitted_domain", "curriculum_contracts",
                 "admitted_evidence_references"),
        required=("unit", "admitted_domain", "curriculum_contracts"),
        denied=("rejected_domain_versions", "sibling_artifacts", "acceptance_state"),
        excluded_doc="rejected domain versions, reviewer history, sibling artifacts, "
                     "acceptance state",
    ),
    "M04_visual": _spec(
        "M04_visual", "M04_CREATE_UNIT_VISUALS",
        allowed=("brief", "permitted_facts", "visual_contract"),
        required=("brief", "permitted_facts", "visual_contract"),
        denied=("visual_briefs", "other_briefs", "authoritative_facts", "netlist",
                "wiring", "schematic", "pinout"),
        excluded_doc="authoritative circuit/pin/electrical invention, other briefs, "
                     "full state",
    ),
    "M05_unit_review": _spec(
        "M05_unit_review", "M05_REVIEW_ACTUAL_UNIT",
        allowed=("unit_artifacts", "unit_pdf", "page_inventory", "pages",
                 "deterministic_evidence", "rubric"),
        required=("unit_artifacts", "unit_pdf", "page_inventory", "pages",
                  "deterministic_evidence", "rubric"),
        denied=("repair_requests", "sibling_artifacts"),
        excluded_doc="author/repair history, prompts/outputs from M01-M04/M06, counters, "
                     "desired verdict",
    ),
    "M06_unit_repair": _spec(
        "M06_unit_repair", "M06_REPAIR_NAMED_UNIT_ARTIFACT",
        allowed=("owner", "findings", "parent", "boundary", "allowed_facts",
                 "invalidated_descendants", "retest_order"),
        required=("owner", "findings", "parent", "boundary"),
        denied=("unrelated_findings", "accepted_bytes", "sibling_units", "routing"),
        excluded_doc="unrelated findings/artifacts, accepted bytes, sibling units, "
                     "routing/terminal state",
    ),
    "M07_workbook_review": _spec(
        "M07_workbook_review", "M07_REVIEW_ACTUAL_WORKBOOK",
        allowed=("coverage_map", "accepted_unit_hashes", "workbook_pdf",
                 "page_inventory", "pages", "deterministic_evidence", "rubric"),
        required=("coverage_map", "accepted_unit_hashes", "workbook_pdf",
                  "page_inventory", "pages", "deterministic_evidence", "rubric"),
        denied=("mutable_unit_sources", "unit_sources", "repair_requests"),
        excluded_doc="author and unit repair history, desired verdict, mutable unit sources",
    ),
    "M08_workbook_repair": _spec(
        "M08_workbook_repair", "M08_REPAIR_NAMED_WORKBOOK_DEFECT",
        allowed=("defect", "parent", "allowed_files", "accepted_unit_hashes",
                 "workbook_pdf_hash", "invalidated_descendants", "retest_order"),
        required=("defect", "parent", "allowed_files", "accepted_unit_hashes"),
        denied=("unit_content", "unit_domain", "unit_visual_sources", "other_defects",
                "acceptance_state"),
        excluded_doc="unit content/domain/visual sources, unrelated workbook defects, "
                     "acceptance/terminal authority",
    ),
}


# --------------------------------------------------------------------------- helpers


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProjectionViolation(f"{label} must be a mapping, got {type(value).__name__}")
    return value


def _collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        keys.update(str(key) for key in value)
        for item in value.values():
            keys |= _collect_keys(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            keys |= _collect_keys(item)
    return keys


def _assert_no_denied_names(projection: Mapping[str, Any], spec: ProjectionSpec) -> None:
    present = _collect_keys(projection)
    offending = sorted(name for name in present if name in spec.denied)
    if offending:
        raise ProjectionViolation(
            f"{spec.name} projection carries structurally excluded fields {offending}; "
            f"spec 9 excludes: {spec.excluded_doc}")


def build_projection(spec_name: str, packet: Mapping[str, Any]) -> dict[str, Any]:
    """Materialize one projection from its allowlist alone.

    The allowlist is read, never the packet's key set, so handing this function a
    whole ``FactoryState`` cannot widen the result: unlisted channels are not copied
    and unreachable, and any excluded name nested inside an allowed value is rejected.
    """

    spec = PROJECTION_SPECS[spec_name]
    _require_mapping(packet, f"{spec.name} packet")
    missing = [name for name in spec.required
               if packet.get(name) is None]
    if missing:
        raise ProjectionViolation(f"{spec.name} packet is missing required {missing}")
    projection = {name: copy.deepcopy(packet[name])
                  for name in spec.allowed if packet.get(name) is not None}
    _assert_no_denied_names(projection, spec)
    tp.assert_no_authoritative_fields(projection, label=f"{spec.name} projection")
    return projection


def _resolve_reservation(packet: Mapping[str, Any], *, job_id: str) -> Mapping[str, Any]:
    reservation = packet.get("reservation")
    if not isinstance(reservation, Mapping):
        raise AttemptNotReserved(
            f"{job_id}: no D90 reservation in the packet; D90_RESERVE_MODEL_ATTEMPT must "
            f"commit a counter before any dispatch")
    if reservation.get("reservation_kind") != RESERVATION_KIND:
        raise AttemptNotReserved(f"{job_id}: reservation is not a {RESERVATION_KIND}")
    if reservation.get("job_id") != job_id:
        raise AttemptNotReserved(
            f"{job_id}: reservation was minted for {reservation.get('job_id')!r}")
    ordinal = reservation.get("attempt_ordinal")
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or not 1 <= ordinal:
        raise AttemptNotReserved(f"{job_id}: reservation has no positive attempt ordinal")
    if ordinal > MODEL_NODE_ATTEMPT_LIMIT:
        raise AttemptNotReserved(
            f"{job_id}: attempt {ordinal} exceeds the frozen limit "
            f"{MODEL_NODE_ATTEMPT_LIMIT}")
    for field in ("activation_id", "reservation_id"):
        if not isinstance(reservation.get(field), str) or not reservation[field]:
            raise AttemptNotReserved(f"{job_id}: reservation is missing {field}")
    return reservation


def _resolve_correlation(packet: Mapping[str, Any], *, job_id: str,
                         needs_key: bool) -> Mapping[str, Any]:
    correlation = _require_mapping(packet.get("correlation"), f"{job_id} correlation")
    for field in ("run_id", "episode_id"):
        if not isinstance(correlation.get(field), str) or not correlation[field]:
            raise ProjectionViolation(f"{job_id}: correlation is missing {field}")
    if needs_key and (not isinstance(correlation.get("correlation_key"), str)
                      or not correlation["correlation_key"]):
        raise ProjectionViolation(
            f"{job_id}: a fan-out job requires a code-computed correlation_key")
    return correlation


def _staged_inputs(packet: Mapping[str, Any], projection: Mapping[str, Any],
                   *, job_id: str) -> tuple[tp.StagedInput, ...]:
    declared = packet.get("staged_inputs") or ()
    if not isinstance(declared, Sequence) or isinstance(declared, (str, bytes)):
        raise ProjectionViolation(f"{job_id}: staged_inputs must be a sequence")
    referenced = _collect_values(projection)
    staged: list[tp.StagedInput] = []
    for item in declared:
        record = _require_mapping(item, f"{job_id} staged input")
        name = record.get("name")
        if not isinstance(name, str) or not name:
            raise ProjectionViolation(f"{job_id}: staged input has no name")
        if name not in referenced:
            raise ProjectionViolation(
                f"{job_id}: staged input {name!r} is not declared by the projection")
        staged.append(tp.StagedInput(name=name,
                                     source_path=Path(str(record["source_path"])),
                                     sha256=str(record["sha256"])))
    return tuple(staged)


def _collect_values(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for item in value.values():
            found |= _collect_values(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            found |= _collect_values(item)
    elif isinstance(value, str):
        found.add(value)
    return found


# ------------------------------------------------------------- candidate validation


def _schema_for(route: tp.JobRoute) -> dict[str, Any]:
    return tp.load_output_schema(route)


def _resolve_ref(schema: Mapping[str, Any], root: Mapping[str, Any]) -> Mapping[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return schema
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _assert_closed(value: Any, schema: Mapping[str, Any], root: Mapping[str, Any],
                   *, path: str, label: str) -> None:
    """Enforce closed-object semantics even where a schema leaves an object open.

    N13's schemas already declare ``additionalProperties: false`` at every level but
    one (``M02.domain_version.fields``, which is intentionally free-form). Rather than
    trust that, every object in a candidate is checked here before it can reach state.
    """

    schema = _resolve_ref(schema, root)
    if isinstance(value, Mapping):
        properties = schema.get("properties")
        if isinstance(properties, Mapping):
            undeclared = sorted(set(map(str, value)) - set(map(str, properties)))
            if undeclared:
                raise CandidateRejected(
                    f"{label}: undeclared properties {undeclared} at {path}")
            for key, item in value.items():
                subschema = properties.get(key)
                if isinstance(subschema, Mapping):
                    _assert_closed(item, subschema, root, path=f"{path}/{key}", label=label)
        else:
            tp.assert_no_authoritative_fields(value, label=f"{label} at {path}")
    elif isinstance(value, list):
        items = schema.get("items")
        if isinstance(items, Mapping):
            for index, item in enumerate(value):
                _assert_closed(item, items, root, path=f"{path}[{index}]", label=label)


CANDIDATE_VALIDATION_ERRORS = (jsonschema.ValidationError, tp.TransportError,
                               CandidateRejected)


def _validate_candidate_shape(candidate: Mapping[str, Any], route: tp.JobRoute) -> None:
    schema = _schema_for(route)
    jsonschema.Draft202012Validator(schema).validate(dict(candidate))
    tp.assert_no_authoritative_fields(candidate, label=f"{route.job_id} candidate")
    _assert_closed(candidate, schema, schema, path="$", label=f"{route.job_id} candidate")


def _assert_subset(actual: Sequence[str], declared: Sequence[str], *, label: str,
                   error: type[ModelNodeError]) -> None:
    extra = sorted(set(actual) - set(declared))
    if extra:
        raise error(f"{label}: undeclared {extra}; declared {sorted(set(declared))}")


def _page_denominator(projection: Mapping[str, Any], *, label: str) -> dict[int, str]:
    inventory = _require_mapping(projection.get("page_inventory"), f"{label} page_inventory")
    count = inventory.get("page_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 1:
        raise PageDenominatorViolation(f"{label}: page_count must be a positive integer")
    declared: dict[int, str] = {}
    entries = inventory.get("pages")
    if not isinstance(entries, list) or not entries:
        raise PageDenominatorViolation(f"{label}: page_inventory.pages is empty")
    for entry in entries:
        record = _require_mapping(entry, f"{label} page entry")
        number = record.get("page_number")
        digest = record.get("page_sha256")
        if not isinstance(number, int) or isinstance(number, bool):
            raise PageDenominatorViolation(f"{label}: page_number must be an integer")
        if number in declared:
            raise PageDenominatorViolation(f"{label}: duplicate page {number}")
        if not isinstance(digest, str) or len(digest) != 64:
            raise PageDenominatorViolation(f"{label}: page {number} has no sha256")
        declared[number] = digest
    expected = set(range(1, count + 1))
    if set(declared) != expected:
        raise PageDenominatorViolation(
            f"{label}: inventory covers {sorted(declared)}, denominator is "
            f"{sorted(expected)}")
    supplied = projection.get("pages")
    if not isinstance(supplied, list):
        raise PageDenominatorViolation(f"{label}: pages must be a list")
    seen: dict[int, str] = {}
    for entry in supplied:
        record = _require_mapping(entry, f"{label} page image")
        number = record.get("page_number")
        digest = record.get("page_sha256")
        if number in seen:
            raise PageDenominatorViolation(f"{label}: duplicate page image {number}")
        if number not in declared:
            raise PageDenominatorViolation(f"{label}: page image {number} is not in the denominator")
        if digest != declared[number]:
            raise PageDenominatorViolation(f"{label}: page {number} image hash differs from inventory")
        seen[number] = str(digest)
    if set(seen) != expected:
        raise PageDenominatorViolation(
            f"{label}: page images cover {sorted(seen)}, denominator is {sorted(expected)}")
    return declared


def _assert_findings_cover_pages(candidate: Mapping[str, Any], denominator: Mapping[int, str],
                                 *, label: str) -> None:
    seen: set[int] = set()
    for entry in candidate.get("page_findings", []):
        number = entry.get("page_number")
        if number in seen:
            raise CandidateRejected(f"{label}: duplicate page finding for page {number}")
        if number not in denominator:
            raise CandidateRejected(f"{label}: finding for undeclared page {number}")
        if entry.get("page_sha256") != denominator[number]:
            raise CandidateRejected(f"{label}: page {number} finding cites the wrong page hash")
        seen.add(int(number))
    if seen != set(denominator):
        missing = sorted(set(denominator) - seen)
        raise CandidateRejected(f"{label}: no finding result for pages {missing}")


def _assert_visual_brief_eligible(brief: Mapping[str, Any]) -> None:
    if brief.get("authoritative") is True:
        raise ProjectionViolation(
            "M04: an authoritative brief is produced deterministically, never by a model")
    klass = str(brief.get("visual_class", "")).lower()
    if klass in AUTHORITATIVE_VISUAL_CLASSES:
        raise ProjectionViolation(
            f"M04: visual_class {klass!r} asserts authoritative circuit/pin/electrical "
            f"detail and is not model-eligible")
    if brief.get("eligibility") != "model_eligible":
        raise ProjectionViolation("M04: brief is not marked model_eligible")


# ---------------------------------------------------------------------------- context


@dataclasses.dataclass(frozen=True)
class ModelNodeContext:
    """Everything a model adapter may reach. No state, no routing, no head authority."""

    transport: Any
    registry: Mapping[str, tp.JobRoute]


def _assert_production_transport(transport: Any) -> None:
    """Production adapters accept the real contained transport and nothing else."""

    if isinstance(transport, tp.FakeCliTransport):
        raise ModelNodeError(
            "a fake transport is only injectable through build_test_model_node_context")
    if not isinstance(transport, tp.CliTransport):
        raise ModelNodeError(
            f"production model nodes require transport.CliTransport, got "
            f"{type(transport).__name__}")


def build_model_node_context(context: RuntimeContext, *,
                             registry: Mapping[str, tp.JobRoute] | None = None,
                             ) -> ModelNodeContext:
    """The one production construction path. It can only bind the real transport."""

    transport = context.transport_registry
    _assert_production_transport(transport)
    return ModelNodeContext(
        transport=transport,
        registry=registry if registry is not None else tp.load_job_registry(),
    )


def build_test_model_node_context(*, sandbox_root: Path | str,
                                  responses: Mapping[str, Mapping[str, Any]],
                                  registry: Mapping[str, tp.JobRoute] | None = None,
                                  ) -> ModelNodeContext:
    """Test-only graph build. Named explicitly so no production path can select it."""

    routes = registry if registry is not None else tp.load_job_registry()
    return ModelNodeContext(
        transport=tp.FakeCliTransport(sandbox_root=sandbox_root, responses=responses,
                                      registry=routes),
        registry=routes,
    )


# ---------------------------------------------------------------- D90 / D91 bookkeeping


def attempt_counter_key(job_id: str, correlation_key: str,
                        phase: str | None = None) -> str:
    """The counter one attempt budget is spent against.

    The phase widens the key without touching `correlation_key` itself: M01's
    discovery and interpretation activations must keep the same correlation key,
    because D06B indexes `source_discoveries` and D07 indexes
    `source_interpretations` by it, but they are two independent activations and
    each owns its own retry budget.
    """

    if phase:
        return f"{job_id}|{phase}|{correlation_key}"
    return f"{job_id}|{correlation_key}"


def reserve_model_attempt(
    state: Mapping[str, Any],
    *,
    job_id: str,
    correlation_key: str,
    activation_id: str,
    phase: str | None = None,
    limit: int = MODEL_NODE_ATTEMPT_LIMIT,
    fingerprints: Sequence[Mapping[str, Any]] = (),
    clock: Callable[[], str] = _utc_now,
) -> dict[str, Any]:
    """D90: commit the counter increment before the transport call exists.

    The increment is returned as a ``monotonic_max`` update, so an attempt that never
    returns still leaves a durable reservation and the bound stays enforceable.
    """

    if job_id not in MODEL_NODE_FAMILIES:
        raise ModelNodeError(f"D90: {job_id!r} is not one of the eight model jobs")
    counters = state.get("attempt_counters") or {}
    key = attempt_counter_key(job_id, correlation_key, phase)
    current = int(counters.get(key, 0))
    now = clock()
    if current >= limit:
        return {
            "attempt_counters": {key: current},
            "pending_guard": {
                "kind": "model_attempt",
                "decision": "exhausted",
                "job_id": job_id,
                "counter_key": key,
                "attempts_used": current,
                "limit": limit,
                "fingerprints": [dict(item) for item in fingerprints],
                "reserved_at_utc": now,
            },
        }
    ordinal = current + 1
    reservation_id = f"{activation_id}#{ordinal}"
    reservation = {
        "reservation_kind": RESERVATION_KIND,
        "reservation_id": reservation_id,
        "activation_id": activation_id,
        "job_id": job_id,
        "counter_key": key,
        "attempt_ordinal": ordinal,
        "limit": limit,
        "reserved_at_utc": now,
    }
    return {
        "attempt_counters": {key: ordinal},
        "activation_receipts": [{"key": f"reservation:{reservation_id}", **reservation}],
        "pending_guard": {
            "kind": "model_attempt",
            "decision": "authorized",
            "job_id": job_id,
            "counter_key": key,
            "reservation": reservation,
        },
    }


def _repair_destination(job_id: Any) -> str:
    if job_id in {"M07_REVIEW_ACTUAL_WORKBOOK", "M08_REPAIR_NAMED_WORKBOOK_DEFECT"}:
        return "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR"
    return "D17_CLASSIFY_UNIT_FINDINGS"


def classify_model_failure(
    failure: Mapping[str, Any],
    *,
    attempts_used: int,
    limit: int = MODEL_NODE_ATTEMPT_LIMIT,
    clock: Callable[[], str] = _utc_now,
    state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """D91: decide retry, repair, exhaustion, or system from one execution failure.

    A retry is authorized only for a malformed/transient transport class that is still
    inside the frozen limit, and it must go back through D90. Policy and content
    failures are repaired, never transport-retried; integrity faults are terminal.

    `state` (the full episode state D91 receives, not a narrowed projection: it is a
    model-bookkeeping node outside `NODE_CATALOGUE`) supplies the fields D98's real
    `validate_terminal_candidate` requires of any CONVERGENCE_EXHAUSTED/SYSTEM_FAILURE
    candidate this function proposes -- optional and defaulting empty so every existing
    direct caller (this module's own unit tests) keeps working unchanged.
    """

    _require_mapping(failure, "D91 failure")
    failure_class = str(failure.get("failure_class") or "unknown")
    job_id = failure.get("job_id")
    counter_key = failure.get("counter_key")
    now = clock()
    fingerprint = (f"{job_id}|{counter_key}|{failure_class}")
    state = state or {}

    if failure_class in SYSTEM_FAILURE_CLASSES:
        decision, destination, terminal = "system", "D98_WRITE_TERMINAL", "SYSTEM_FAILURE"
    elif failure_class in POLICY_OR_CONTENT_FAILURE_CLASSES:
        decision, destination, terminal = "repair", _repair_destination(job_id), None
    elif failure_class in RETRYABLE_FAILURE_CLASSES:
        if attempts_used < limit:
            decision, destination, terminal = "retry", "D90_RESERVE_MODEL_ATTEMPT", None
        else:
            decision, destination, terminal = (
                "exhausted", "D98_WRITE_TERMINAL", "CONVERGENCE_EXHAUSTED")
    else:
        decision, destination, terminal = "system", "D98_WRITE_TERMINAL", "SYSTEM_FAILURE"

    fingerprint_record = {
        "key": f"{fingerprint}|{attempts_used}",
        "fingerprint": fingerprint,
        "job_id": job_id,
        "counter_key": counter_key,
        "failure_class": failure_class,
        "attempts_used": attempts_used,
        "limit": limit,
        "classified_at_utc": now,
    }
    update: dict[str, Any] = {
        "failure_fingerprints": [fingerprint_record],
        "pending_failure": {**dict(failure), "classification": decision},
        "pending_guard": {
            "kind": "model_failure",
            "decision": decision,
            "destination": destination,
            # `routing.route_model_failure` resolves the dynamic `repair`
            # destination out of `detail`, so the same fact is carried where the
            # guard table reads it.
            "detail": {"destination": destination, "job_id": job_id,
                       "counter_key": counter_key},
            "job_id": job_id,
            "counter_key": counter_key,
            "failure_class": failure_class,
            "attempts_used": attempts_used,
            "limit": limit,
        },
    }
    if terminal == "CONVERGENCE_EXHAUSTED":
        # Field names/shape match every other CONVERGENCE_EXHAUSTED writer
        # (repair.py D17/D18, workbook.py D29) exactly: D98's real
        # `validate_terminal_candidate` (nodes/terminal.py) is one shared,
        # independent re-derivation, not a per-writer contract.
        update["terminal_candidate"] = {
            "kind": "CONVERGENCE_EXHAUSTED",
            "bound": "attempt_bound",
            "counters": dict(state.get("attempt_counters") or {}),
            "fingerprints": [fingerprint_record],
            "last_findings": [dict(failure)],
        }
    elif terminal == "SYSTEM_FAILURE":
        artifact_heads = state.get("artifact_heads") or {}
        update["terminal_candidate"] = {
            "kind": "SYSTEM_FAILURE",
            "failure": {"class": "system", "cause": failure_class},
            "node": str(job_id) if job_id else "D91_CLASSIFY_MODEL_FAILURE",
            "safe_heads": {
                stream: head.get("hash")
                for stream, head in sorted(artifact_heads.items())
                if isinstance(head, dict)
            },
            "audit_high_water_mark": len(state.get("evidence_index_entries") or []),
        }
    return update


# --------------------------------------------------------- D90 / D91 node callables


ATTEMPT_RESERVATION_NODE = "D90_RESERVE_MODEL_ATTEMPT"
MODEL_FAILURE_NODE = "D91_CLASSIFY_MODEL_FAILURE"


def _staged_dispatch(state: Mapping[str, Any]) -> tuple[str, str, list[Mapping[str, Any]]]:
    """The job, the member list key, and the members of the staged dispatch packet.

    The member list key is read back rather than normalized because
    `routing._staged_fanout` translates whichever of `packets`/`briefs` the
    dispatching node used, and D90 must restage under the same name.
    """

    packet = state.get("pending_packet")
    if not isinstance(packet, Mapping):
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: no `pending_packet` is staged; a reservation "
            f"can only be minted for a dispatch the denominator already committed to")
    job_id = packet.get("dispatch")
    if job_id not in MODEL_NODE_FAMILIES:
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: staged packet dispatches {job_id!r}, which is "
            f"not one of the eight model jobs")
    member_key = "packets" if packet.get("packets") is not None else "briefs"
    members = packet.get(member_key)
    if (not isinstance(members, Sequence) or isinstance(members, (str, bytes))
            or not members):
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: staged packet carries no non-empty "
            f"{member_key!r} member list")
    return job_id, member_key, [_require_mapping(m, f"{job_id} member") for m in members]


def _retry_counter_key(state: Mapping[str, Any]) -> str | None:
    """The one counter key D91 authorized a further attempt for, if it did."""

    guard = state.get("pending_guard")
    if not isinstance(guard, Mapping) or guard.get("kind") != "model_failure":
        return None
    if guard.get("decision") != "retry":
        return None
    key = guard.get("counter_key")
    if not isinstance(key, str) or not key:
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: a classified retry names no counter key")
    return key


def _activation_phase(member: Mapping[str, Any]) -> str | None:
    """The activation kind a staged member declares, if its job has more than one.

    Only M01 dispatches two structurally different activations (`DISCOVER` and
    `INTERPRET`) under one correlation key, and its dispatchers already stage the
    distinction; every other job stages no `phase` and keeps an unwidened key.
    """

    phase = member.get("phase")
    if phase is None:
        return None
    if not isinstance(phase, str) or not phase:
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: staged member declares a non-string phase "
            f"{phase!r}, so its attempt budget could not be keyed")
    return phase


def _activation_id(correlation: Mapping[str, Any], *, counter_key: str,
                   ordinal: int) -> str:
    """One activation identity per attempt, derived so no two attempts share one.

    D92 accounts for an interrupted attempt by matching activation ids against
    execution receipts, so the ordinal is part of the identity: reusing it across
    attempts would make an unobserved attempt indistinguishable from an observed one.
    """

    return (f"{correlation['run_id']}/{correlation['episode_id']}/{counter_key}"
            f"/attempt-{ordinal}")


def D90_RESERVE_MODEL_ATTEMPT(state: Mapping[str, Any],
                              context: Any) -> dict[str, Any]:
    """D90: commit one attempt counter per staged dispatch member, before dispatch.

    A map superstep stages N worker projections and each is a separate attempt
    against its own correlation, so this reserves per member and returns the
    packet restaged with each member's reservation attached — the fan-out guard
    then translates exactly what was reserved. A D91-authorized retry names one
    counter key, and only that member is re-reserved and restaged: the other
    members' results are already committed and are not re-dispatched.

    Any member at the frozen limit exhausts the whole superstep rather than
    dispatching a partial map, so the bound can never be crossed by a sibling.
    """

    job_id, member_key, members = _staged_dispatch(state)
    retry_key = _retry_counter_key(state)
    counters = state.get("attempt_counters") or {}

    reserved_counters: dict[str, int] = {}
    receipts: list[dict[str, Any]] = []
    restaged: list[dict[str, Any]] = []
    reservations: dict[str, Any] = {}
    exhausted: list[dict[str, Any]] = []

    for member in members:
        correlation = _resolve_correlation(member, job_id=job_id, needs_key=True)
        phase = _activation_phase(member)
        key = attempt_counter_key(job_id, correlation["correlation_key"], phase)
        if retry_key is not None and key != retry_key:
            continue
        ordinal = int(counters.get(key, 0)) + 1
        update = reserve_model_attempt(
            state, job_id=job_id, correlation_key=correlation["correlation_key"],
            phase=phase,
            activation_id=_activation_id(correlation, counter_key=key, ordinal=ordinal))
        guard = update["pending_guard"]
        reserved_counters.update(update["attempt_counters"])
        if guard["decision"] == "exhausted":
            exhausted.append({"counter_key": key, "attempts_used": guard["attempts_used"],
                              "limit": guard["limit"]})
            continue
        reservation = guard["reservation"]
        reservations[key] = reservation
        receipts.extend(update["activation_receipts"])
        restaged.append({**member, "reservation": reservation})

    if retry_key is not None and not (restaged or exhausted):
        raise ModelNodeError(
            f"{ATTEMPT_RESERVATION_NODE}: classified retry {retry_key!r} matches no "
            f"staged member, so there is nothing to re-dispatch")

    if exhausted:
        return {
            "attempt_counters": reserved_counters,
            "pending_guard": {
                "node": ATTEMPT_RESERVATION_NODE,
                "value": "exhausted",
                "kind": "model_attempt",
                "decision": "exhausted",
                "detail": {"job_id": job_id, "exhausted": exhausted,
                           "limit": MODEL_NODE_ATTEMPT_LIMIT},
            },
        }

    packet = dict(state["pending_packet"])
    packet[member_key] = restaged
    return {
        "attempt_counters": reserved_counters,
        "activation_receipts": receipts,
        "pending_packet": packet,
        "pending_guard": {
            "node": ATTEMPT_RESERVATION_NODE,
            "value": "authorized",
            "kind": "model_attempt",
            "decision": "authorized",
            "detail": {"job_id": job_id, "reservations": reservations,
                       "members": len(restaged)},
        },
    }


def _aborted_activation(state: Mapping[str, Any]) -> dict[str, Any]:
    """The failure record for an activation D92 could not account for.

    D92 hands D91 activation ids, not a failure: the reservation receipt is the
    only place the job and counter that attempt belongs to still exist.
    """

    guard = state.get("pending_guard")
    detail = guard.get("detail") if isinstance(guard, Mapping) else None
    activations = detail.get("activations") if isinstance(detail, Mapping) else None
    if not isinstance(activations, Sequence) or isinstance(activations, (str, bytes)):
        raise ModelNodeError(
            f"{MODEL_FAILURE_NODE}: no model failure and no incomplete activation to "
            f"classify")
    pending = sorted(str(item) for item in activations)
    if not pending:
        raise ModelNodeError(f"{MODEL_FAILURE_NODE}: the incomplete activation list is empty")
    activation_id = pending[0]
    reservation = next(
        (record for record in (state.get("activation_receipts") or ())
         if isinstance(record, Mapping)
         and record.get("activation_id") == activation_id
         and record.get("reservation_kind") == RESERVATION_KIND),
        None)
    if reservation is None:
        raise ModelNodeError(
            f"{MODEL_FAILURE_NODE}: activation {activation_id!r} has no reservation "
            f"receipt, so the attempt it belongs to cannot be identified")
    return {
        "job_id": reservation["job_id"],
        "counter_key": reservation["counter_key"],
        "activation_id": activation_id,
        "reservation_id": reservation["reservation_id"],
        "attempt_ordinal": reservation["attempt_ordinal"],
        "failure_class": "aborted_activation",
        "detail": f"activation {activation_id} has no execution receipt",
        "unclassified_activations": pending[1:],
    }


def D91_CLASSIFY_MODEL_FAILURE(state: Mapping[str, Any],
                               context: Any) -> dict[str, Any]:
    """D91: classify one model failure, or one activation D92 could not account for.

    The attempt count is read from the committed counter rather than from the
    failure record, so a retry is authorized against the reservation that is
    actually durable. A `retry` clears `pending_failure`: D90 is the next node,
    and an uncleared failure would route it to the terminal writer instead.
    A `repair` deliberately leaves `pending_failure` set (with its
    `classification` tag): D91's own outgoing edge (`routing.route_model_
    failure`) reads `pending_guard`, never `pending_failure`, so nothing about
    D91's own routing needs it cleared -- and `D17_CLASSIFY_UNIT_FINDINGS`
    (repair.py) reads exactly this classified `pending_failure` to build its
    one raw finding for a model-repair job, then clears it itself once
    consumed (repair.py's own `update["pending_failure"] = None`). Live-
    verified (N70): nulling it here instead left D17 with a `pending_guard`
    that carries no `detail.findings` list at all (D91's guard shape, not
    D08/D09/D12/D14/D16's), so D17 raised "routed with an empty or missing
    findings list" -- a regression from an earlier, mistaken diagnosis that
    D91's own routing was the one being hijacked; it never was.
    """

    failure = state.get("pending_failure")
    if not isinstance(failure, Mapping):
        failure = _aborted_activation(state)
    counter_key = failure.get("counter_key")
    counters = state.get("attempt_counters") or {}
    attempts_used = int(counters.get(counter_key, failure.get("attempt_ordinal") or 1))
    update = classify_model_failure(failure, attempts_used=attempts_used, state=state)
    if update["pending_guard"]["decision"] == "retry":
        update["pending_failure"] = None
    return update


# Registrable by stable ID: both are `(state, context) -> update` callables owned
# by this module, which is what N20's binding-owner audit requires of a node body.
MODEL_BOOKKEEPING_NODES: Mapping[str, Callable[..., dict[str, Any]]] = {
    ATTEMPT_RESERVATION_NODE: D90_RESERVE_MODEL_ATTEMPT,
    MODEL_FAILURE_NODE: D91_CLASSIFY_MODEL_FAILURE,
}


# ------------------------------------------------------------------- shared dispatch


@dataclasses.dataclass(frozen=True)
class _Dispatch:
    spec: ProjectionSpec
    route: tp.JobRoute
    projection: dict[str, Any]
    correlation: Mapping[str, Any]
    reservation: Mapping[str, Any]
    candidate: dict[str, Any]
    receipt: dict[str, Any]
    attempts: tuple[dict[str, Any], ...]


def _execution_receipts(dispatch_receipts: Sequence[Mapping[str, Any]], *,
                        spec: ProjectionSpec, reservation: Mapping[str, Any],
                        correlation: Mapping[str, Any],
                        projection_sha256: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, receipt in enumerate(dispatch_receipts, start=1):
        records.append({
            "key": f"{reservation['reservation_id']}#{index}",
            "job_id": spec.job_id,
            "projection_name": spec.name,
            "reservation_id": reservation["reservation_id"],
            "activation_id": reservation["activation_id"],
            "attempt_ordinal": reservation["attempt_ordinal"],
            "run_id": correlation["run_id"],
            "episode_id": correlation["episode_id"],
            "projection_sha256": projection_sha256,
            "receipt": dict(receipt),
        })
    return records


def _activation_receipt(*, spec: ProjectionSpec, reservation: Mapping[str, Any],
                        correlation: Mapping[str, Any], projection_sha256: str,
                        candidate_sha256: str | None, executed_family: str | None,
                        executed_model: str | None, result: str) -> dict[str, Any]:
    return {
        "key": f"activation:{reservation['reservation_id']}",
        "job_id": spec.job_id,
        "projection_name": spec.name,
        "reservation_id": reservation["reservation_id"],
        "activation_id": reservation["activation_id"],
        "attempt_ordinal": reservation["attempt_ordinal"],
        "run_id": correlation["run_id"],
        "episode_id": correlation["episode_id"],
        "decided_family": spec.family,
        "executed_family": executed_family,
        "executed_model": executed_model,
        "projection_sha256": projection_sha256,
        "candidate_sha256": candidate_sha256,
        "result": result,
    }


def _executed_family(receipt: Mapping[str, Any]) -> str | None:
    observed = receipt.get("observed_family")
    return observed if isinstance(observed, str) and observed else receipt.get("decided_family")


def _failure_update(*, spec: ProjectionSpec, reservation: Mapping[str, Any],
                    correlation: Mapping[str, Any], projection_sha256: str,
                    failure_class: str, detail: str,
                    receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "model_execution_receipts": _execution_receipts(
            receipts, spec=spec, reservation=reservation, correlation=correlation,
            projection_sha256=projection_sha256),
        "activation_receipts": [_activation_receipt(
            spec=spec, reservation=reservation, correlation=correlation,
            projection_sha256=projection_sha256, candidate_sha256=None,
            executed_family=None, executed_model=None, result="failed")],
        "pending_failure": {
            "job_id": spec.job_id,
            "projection_name": spec.name,
            "counter_key": reservation["counter_key"],
            "activation_id": reservation["activation_id"],
            "reservation_id": reservation["reservation_id"],
            "attempt_ordinal": reservation["attempt_ordinal"],
            "failure_class": failure_class,
            "detail": detail[:2000],
            "requires_classification_by": "D91_CLASSIFY_MODEL_FAILURE",
        },
    }


def _dispatch(spec_name: str, packet: Mapping[str, Any], context: ModelNodeContext,
              *, needs_correlation_key: bool = False, web_search: bool = False,
              ) -> tuple[_Dispatch | None, dict[str, Any] | None]:
    """The module's only transport call site.

    Returning ``(None, failure_update)`` rather than raising keeps a model failure a
    routable state fact: D91 classifies it and only D90 may authorize another attempt.

    ``web_search`` defaults to False for every job; only M01's ``discover`` phase
    passes True (N20V7-F13, spec decision) so the worker can find and verify real
    candidate locators instead of refusing when it cannot confirm a URL exists.
    """

    spec = PROJECTION_SPECS[spec_name]
    route = tp.resolve_route(spec.job_id, context.registry)
    if route.family != spec.family:
        raise FamilyViolation(
            f"{spec.job_id}: frozen registry family {route.family!r} != {spec.family!r}")
    reservation = _resolve_reservation(packet, job_id=spec.job_id)
    correlation = _resolve_correlation(packet, job_id=spec.job_id,
                                       needs_key=needs_correlation_key)
    projection = build_projection(spec_name, packet)
    projection_sha256 = canonical_digest(projection)
    staged = _staged_inputs(packet, projection, job_id=spec.job_id)

    try:
        result = context.transport.execute(
            job_id=spec.job_id,
            activation_id=reservation["activation_id"],
            episode_id=correlation["episode_id"],
            projection=projection,
            staged_inputs=staged,
            web_search=web_search,
        )
    except tp.TransportError as error:
        failure_class = getattr(error, "failure_class", type(error).__name__)
        receipts = [getattr(error, "receipt", None) or {"outcome": "transport_failure"}]
        return None, _failure_update(
            spec=spec, reservation=reservation, correlation=correlation,
            projection_sha256=projection_sha256, failure_class=str(failure_class),
            detail=str(error), receipts=receipts)

    executed_family = _executed_family(result.receipt)
    if spec.is_review and executed_family == tp.AUTHORING_FAMILY:
        raise FamilyViolation(
            f"{spec.job_id}: a review executed in the authoring family "
            f"{tp.AUTHORING_FAMILY!r}")
    if executed_family is not None and executed_family != spec.family:
        raise FamilyViolation(
            f"{spec.job_id}: executed family {executed_family!r} != decided {spec.family!r}")

    candidate = dict(result.candidate)
    return _Dispatch(spec=spec, route=route, projection=projection,
                     correlation=correlation, reservation=reservation,
                     candidate=candidate, receipt=dict(result.receipt),
                     attempts=tuple(dict(item) for item in result.attempts)), None


def _reject(dispatch: _Dispatch, failure_class: str, detail: str) -> dict[str, Any]:
    return _failure_update(
        spec=dispatch.spec, reservation=dispatch.reservation,
        correlation=dispatch.correlation,
        projection_sha256=canonical_digest(dispatch.projection),
        failure_class=failure_class, detail=detail, receipts=dispatch.attempts)


def _accept(dispatch: _Dispatch, channel_update: Mapping[str, Any]) -> dict[str, Any]:
    projection_sha256 = canonical_digest(dispatch.projection)
    candidate_sha256 = canonical_digest(dispatch.candidate)
    update: dict[str, Any] = dict(channel_update)
    update["model_execution_receipts"] = _execution_receipts(
        dispatch.attempts, spec=dispatch.spec, reservation=dispatch.reservation,
        correlation=dispatch.correlation, projection_sha256=projection_sha256)
    update["activation_receipts"] = [_activation_receipt(
        spec=dispatch.spec, reservation=dispatch.reservation,
        correlation=dispatch.correlation, projection_sha256=projection_sha256,
        candidate_sha256=candidate_sha256,
        executed_family=_executed_family(dispatch.receipt),
        executed_model=dispatch.receipt.get("observed_model")
        or dispatch.receipt.get("decided_model"),
        result="candidate_produced")]
    _assert_model_node_update(update)
    return update


def _assert_model_node_update(update: Mapping[str, Any]) -> None:
    unknown = sorted(set(update) - MODEL_NODE_WRITABLE_FIELDS)
    if unknown:
        raise ModelNodeError(
            f"a model node may not write {unknown}; admission, heads, and terminals are "
            f"deterministic-node authority")


def _candidate_record(dispatch: _Dispatch, **extra: Any) -> dict[str, Any]:
    """A pre-admission candidate descriptor.

    Two kinds of key, and the split is the point. The model's own output is quarantined
    under ``payload``; every other key is *lineage* the projection already knew before the
    model ran (which unit, which retrieved bytes, which content epoch), so a deterministic
    node can correlate the candidate without trusting the model for it.

    It deliberately carries no ``version``/``hash``/``parent_hash``, so it cannot be
    replayed as an ``advance_head`` update; only a deterministic admission node mints a
    head record, and ``ADMISSION_OWNED_CANDIDATE_FIELDS`` is enforced here rather than
    left to convention.
    """

    minted = sorted(ADMISSION_OWNED_CANDIDATE_FIELDS & set(extra))
    if minted:
        raise ModelNodeError(
            f"{dispatch.spec.job_id}: a model candidate may not carry {minted}; minting an "
            f"artifact version is deterministic admission authority")
    record = {
        "key": f"candidate:{dispatch.reservation['reservation_id']}",
        "record_kind": "model_candidate",
        "pre_admission": True,
        "job_id": dispatch.spec.job_id,
        "projection_name": dispatch.spec.name,
        "run_id": dispatch.correlation["run_id"],
        "episode_id": dispatch.correlation["episode_id"],
        "activation_id": dispatch.reservation["activation_id"],
        "reservation_id": dispatch.reservation["reservation_id"],
        "projection_sha256": canonical_digest(dispatch.projection),
        "candidate_sha256": canonical_digest(dispatch.candidate),
        "payload": dispatch.candidate,
    }
    record.update(extra)
    return record


# --------------------------------------------------------------------- M01 (two phases)


def m01_discover_unit_sources(packet: Mapping[str, Any],
                              context: ModelNodeContext) -> dict[str, Any]:
    """M01 `phase=DISCOVER`: one bounded question under discovery authority.

    Distinct from interpretation by construction, not by an internal branch: this
    projection is the only one that carries discovery authority, and it can never
    carry retrieved bytes.
    """

    dispatch, failure = _dispatch("M01_discovery", packet, context,
                                  needs_correlation_key=True, web_search=True)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    request_id = dispatch.projection["request"].get("request_id")
    if "no_verified_source" in dispatch.candidate:
        # WebSearch (N20V7-F13) ran and found nothing this worker could verify.
        # A typed, retryable-then-exhaustible failure -- never a silent success,
        # never a fabricated locator, and never the human-facing prerequisite
        # pause D06B raises for an unrelated "no discovery ran at all" case.
        for entry in dispatch.candidate["no_verified_source"]:
            if entry.get("request_id") != request_id:
                return _reject(dispatch, "candidate_undeclared_artifact",
                               f"no_verified_source cites request "
                               f"{entry.get('request_id')!r}, projection declared "
                               f"{request_id!r}")
        reasons = "; ".join(
            str(entry.get("reason")) for entry in dispatch.candidate["no_verified_source"])
        return _reject(dispatch, "no_verified_source",
                       f"no source could be verified for {request_id!r}: {reasons}")
    if "locators" not in dispatch.candidate:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       "discovery must emit locators, not interpretations")
    allowed_hosts = set(dispatch.projection["discovery_authority"].get("allowed_hosts") or ())
    for locator in dispatch.candidate["locators"]:
        if locator.get("request_id") != request_id:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"locator cites request {locator.get('request_id')!r}, "
                           f"projection declared {request_id!r}")
        host = (urlparse(str(locator.get("url") or "")).hostname or "").lower()
        # N30V7-F07: every result is rejected before retrieval unless its host is
        # one of the exact strings D06 granted (never a substring/suffix match) --
        # WebSearch is told this list and asked to steer by it, but the model's
        # own output is never trusted for this boundary; D06B enforces the same
        # allowlist again at actual fetch time (egress.py), independently.
        if host not in allowed_hosts:
            return _reject(dispatch, "candidate_boundary_violation",
                           f"locator host {host!r} is not in the granted allowed_hosts "
                           f"{sorted(allowed_hosts)}")
    key = dispatch.correlation["correlation_key"]
    return _accept(dispatch, {"source_discoveries": {key: _candidate_record(
        dispatch, phase="DISCOVER", request_id=request_id,
        unit_id=dispatch.projection["unit"].get("unit_id"))}})


def m01_interpret_unit_sources(packet: Mapping[str, Any],
                               context: ModelNodeContext) -> dict[str, Any]:
    """M01 `phase=INTERPRET`: the same request plus only its retrieved bytes.

    Discovery authority is a denied name here, so an interpretation packet that tries
    to carry browsing authority is rejected before any process starts.
    """

    dispatch, failure = _dispatch("M01_interpretation", packet, context,
                                  needs_correlation_key=True)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    if "interpretations" not in dispatch.candidate:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       "interpretation must emit interpretations, not locators")
    request_id = dispatch.projection["request"].get("request_id")
    group = dispatch.projection["retrieval_group"]
    retrieval_ids = [str(item.get("retrieval_id"))
                     for item in group.get("retrieved_records", [])]
    for interpretation in dispatch.candidate["interpretations"]:
        if interpretation.get("request_id") != request_id:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"interpretation cites request {interpretation.get('request_id')!r}")
        if str(interpretation.get("retrieval_id")) not in retrieval_ids:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"interpretation cites undeclared retrieval "
                           f"{interpretation.get('retrieval_id')!r}")
    key = dispatch.correlation["correlation_key"]
    return _accept(dispatch, {"source_interpretations": {key: _candidate_record(
        dispatch, phase="INTERPRET", request_id=request_id,
        unit_id=dispatch.projection["unit"].get("unit_id"),
        retrieval_sha256=_retrieval_sha256(group))}})


def _retrieval_sha256(group: Mapping[str, Any]) -> str | None:
    """The sha256 of the bytes this interpretation was derived from.

    Read off the retrieval group the dispatcher staged, never off the model's answer:
    D07 stales an interpretation whose parent bytes are no longer the retrieval, and a
    model-supplied parent hash would let a stale interpretation vouch for itself. A
    group whose records disagree has no single parent, so the record claims none and
    D07 refuses it rather than admitting an unproven lineage.
    """

    hashes = {record.get("sha256") for record in group.get("retrieved_records", [])
              if isinstance(record, Mapping)}
    return hashes.pop() if len(hashes) == 1 else None


def m01_research_unit_sources(packet: Mapping[str, Any],
                              context: ModelNodeContext) -> dict[str, Any]:
    """Select the phase from the packet's explicit `phase`, never from hidden state."""

    phase = packet.get("phase")
    if phase == "DISCOVER":
        return m01_discover_unit_sources(packet, context)
    if phase == "INTERPRET":
        return m01_interpret_unit_sources(packet, context)
    raise ProjectionViolation(
        f"M01 packet must declare phase DISCOVER or INTERPRET, got {phase!r}")


# ---------------------------------------------------------------------- M02-M04, M06


def m02_create_unit_domain_data(packet: Mapping[str, Any],
                                context: ModelNodeContext) -> dict[str, Any]:
    dispatch, failure = _dispatch("M02_domain", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    domain = dispatch.candidate["domain_version"]
    unit_id = dispatch.projection["unit"].get("unit_id")
    if domain.get("unit_id") != unit_id:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       f"domain names unit {domain.get('unit_id')!r}, projection declared "
                       f"{unit_id!r}")
    admitted = [str(item.get("source_id"))
                for item in dispatch.projection["admitted_sources"]]
    cited = [str(item.get("source_id")) for item in domain.get("evidence_references", [])]
    try:
        _assert_subset(cited, admitted, label="M02 evidence_references",
                       error=CandidateRejected)
    except CandidateRejected as error:
        return _reject(dispatch, "candidate_undeclared_artifact", str(error))
    return _accept(dispatch, {"artifact_versions": [_candidate_record(
        dispatch, channel="domain", scope="units", unit_id=unit_id)]})


def m03_write_unit_content(packet: Mapping[str, Any],
                           context: ModelNodeContext) -> dict[str, Any]:
    dispatch, failure = _dispatch("M03_content", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    content = dispatch.candidate["unit_content"]
    unit_id = dispatch.projection["unit"].get("unit_id")
    if content.get("unit_id") != unit_id:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       f"content names unit {content.get('unit_id')!r}")
    declared_sections = [str(item.get("section_id")) for item in content.get("sections", [])]
    admitted = [str(item.get("source_id"))
                for item in dispatch.projection.get("admitted_evidence_references", [])]
    for reference in content.get("evidence_references", []):
        if str(reference.get("section_id")) not in declared_sections:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"evidence cites unknown section {reference.get('section_id')!r}")
        if admitted and str(reference.get("source_id")) not in admitted:
            return _reject(dispatch, "candidate_undeclared_artifact",
                           f"evidence cites unadmitted source {reference.get('source_id')!r}")
    return _accept(dispatch, {"artifact_versions": [_candidate_record(
        dispatch, channel="content", scope="units", unit_id=unit_id)]})


def m04_create_unit_visuals(packet: Mapping[str, Any],
                            context: ModelNodeContext) -> dict[str, Any]:
    """Exactly one eligible, non-authoritative brief per activation."""

    brief = _require_mapping(packet.get("brief"), "M04 brief")
    _assert_visual_brief_eligible(brief)
    dispatch, failure = _dispatch("M04_visual", packet, context,
                                  needs_correlation_key=True)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    brief_id = dispatch.projection["brief"].get("brief_id")
    candidate = dispatch.candidate
    if candidate["visual_candidate"].get("brief_id") != brief_id:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       f"visual answers brief {candidate['visual_candidate'].get('brief_id')!r}")
    provenance = candidate["provenance_declaration"]
    if provenance.get("brief_id") != brief_id:
        return _reject(dispatch, "candidate_undeclared_artifact",
                       "provenance declares a different brief")
    if provenance.get("asserts_authoritative_detail") is True:
        return _reject(dispatch, "candidate_authoritative_visual",
                       "a model visual may not assert authoritative circuit/pin detail")
    permitted = [str(item) for item in dispatch.projection["permitted_facts"]]
    try:
        _assert_subset([str(item) for item in provenance.get("permitted_facts_used", [])],
                       permitted, label="M04 permitted_facts_used", error=CandidateRejected)
    except CandidateRejected as error:
        return _reject(dispatch, "candidate_undeclared_artifact", str(error))
    key = dispatch.correlation["correlation_key"]
    return _accept(dispatch, {"visual_results": {key: _candidate_record(
        dispatch, channel="visuals", scope="units", brief_id=brief_id, subset="model",
        unit_id=dispatch.projection["brief"].get("unit_id"),
        content_hash=dispatch.projection["brief"].get("content_hash"))}})


def m06_repair_named_unit_artifact(packet: Mapping[str, Any],
                                   context: ModelNodeContext) -> dict[str, Any]:
    """One named finding boundary against one immutable parent."""

    _assert_unit_repair_boundary(packet)
    dispatch, failure = _dispatch("M06_unit_repair", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    boundary = dispatch.projection["boundary"]
    parent = dispatch.projection["parent"]
    declared_pointers = [str(item) for item in boundary.get("json_pointers", [])]
    finding_ids = [str(item.get("finding_id")) for item in dispatch.projection["findings"]]
    child = dispatch.candidate["candidate_child"]
    if child.get("artifact_name") != parent.get("artifact_name"):
        return _reject(dispatch, "candidate_boundary_violation",
                       f"child renames the artifact to {child.get('artifact_name')!r}")
    try:
        _assert_subset([str(item) for item in child.get("addressed_finding_ids", [])],
                       finding_ids, label="M06 addressed_finding_ids",
                       error=RepairBoundaryViolation)
        _assert_subset([str(item.get("json_pointer"))
                        for item in dispatch.candidate["changed_path_manifest"]],
                       declared_pointers, label="M06 changed_path_manifest",
                       error=RepairBoundaryViolation)
        _assert_subset([str(item.get("finding_id"))
                        for item in dispatch.candidate["changed_path_manifest"]],
                       finding_ids, label="M06 manifest finding_id",
                       error=RepairBoundaryViolation)
    except RepairBoundaryViolation as error:
        return _reject(dispatch, "candidate_boundary_violation", str(error))
    return _accept(dispatch, {"artifact_versions": [_candidate_record(
        dispatch, channel=str(parent.get("channel", "content")), scope="units",
        owner=dispatch.projection["owner"], unit_id=parent.get("unit_id"),
        parent_sha256=parent.get("parent_sha256"))]})


def _assert_unit_repair_boundary(packet: Mapping[str, Any]) -> None:
    boundary = _require_mapping(packet.get("boundary"), "M06 boundary")
    pointers = boundary.get("json_pointers")
    if not isinstance(pointers, list) or not pointers:
        raise RepairBoundaryViolation(
            "M06: repair requires a non-empty declared json_pointers boundary")
    findings = packet.get("findings")
    owner = packet.get("owner")
    if not isinstance(findings, list) or not findings:
        raise RepairBoundaryViolation("M06: exactly one owner's findings are required")
    owners = {item.get("owner") for item in findings if isinstance(item, Mapping)}
    if owners != {owner}:
        raise RepairBoundaryViolation(
            f"M06: findings span owners {sorted(map(str, owners))}, declared {owner!r}")


def _assert_workbook_repair_boundary(packet: Mapping[str, Any]) -> None:
    allowed = _require_mapping(packet.get("allowed_files"), "M08 allowed_files")
    files = allowed.get("files")
    if not isinstance(files, list) or not files:
        raise RepairBoundaryViolation(
            "M08: repair requires a non-empty declared workbook-owned file list")


# ------------------------------------------------------------------------- M05 / M07


def m05_review_actual_unit(packet: Mapping[str, Any],
                           context: ModelNodeContext) -> dict[str, Any]:
    """Codex review of the frozen actual unit packet, every page included."""

    denominator = _page_denominator(packet, label="M05")
    dispatch, failure = _dispatch("M05_unit_review", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    try:
        _assert_findings_cover_pages(dispatch.candidate, denominator, label="M05")
    except CandidateRejected as error:
        return _reject(dispatch, "candidate_page_denominator", str(error))
    return _accept(dispatch, {"unit_reviews": [_candidate_record(
        dispatch, review_kind="unit", page_count=len(denominator),
        unit_pdf_sha256=dispatch.projection["unit_pdf"].get("sha256"))]})


def m07_review_actual_workbook(packet: Mapping[str, Any],
                               context: ModelNodeContext) -> dict[str, Any]:
    """Codex review of the frozen actual workbook packet, every page included."""

    denominator = _page_denominator(packet, label="M07")
    dispatch, failure = _dispatch("M07_workbook_review", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    try:
        _assert_findings_cover_pages(dispatch.candidate, denominator, label="M07")
    except CandidateRejected as error:
        return _reject(dispatch, "candidate_page_denominator", str(error))
    return _accept(dispatch, {"workbook_reviews": [_candidate_record(
        dispatch, review_kind="workbook", page_count=len(denominator),
        workbook_pdf_sha256=dispatch.projection["workbook_pdf"].get("sha256"))]})


# ------------------------------------------------------------------------------- M08


def m08_repair_named_workbook_defect(packet: Mapping[str, Any],
                                     context: ModelNodeContext) -> dict[str, Any]:
    """Exactly one workbook-owned defect against the immutable workbook parent."""

    defect = _require_mapping(packet.get("defect"), "M08 defect")
    component = str(defect.get("component", ""))
    if component not in WORKBOOK_OWNED_COMPONENTS:
        raise RepairBoundaryViolation(
            f"M08: {component!r} is not workbook-owned; unit-owned defects are repaired "
            f"by M06 against the unit, never here")
    _assert_workbook_repair_boundary(packet)
    dispatch, failure = _dispatch("M08_workbook_repair", packet, context)
    if dispatch is None:
        return failure  # type: ignore[return-value]
    try:
        _validate_candidate_shape(dispatch.candidate, dispatch.route)
    except CANDIDATE_VALIDATION_ERRORS as error:
        return _reject(dispatch, "candidate_control_field", str(error))
    allowed_files = [str(item) for item in dispatch.projection["allowed_files"]["files"]]
    defect_id = str(dispatch.projection["defect"].get("defect_id"))
    child = dispatch.candidate["candidate_child"]
    if str(child.get("addressed_defect_id")) != defect_id:
        return _reject(dispatch, "candidate_boundary_violation",
                       f"child addresses defect {child.get('addressed_defect_id')!r}, "
                       f"declared {defect_id!r}")
    try:
        _assert_subset([str(item.get("staged_file_name"))
                        for item in dispatch.candidate["changed_file_manifest"]],
                       allowed_files, label="M08 changed_file_manifest",
                       error=RepairBoundaryViolation)
        _assert_subset([str(item.get("defect_id"))
                        for item in dispatch.candidate["changed_file_manifest"]],
                       [defect_id], label="M08 manifest defect_id",
                       error=RepairBoundaryViolation)
    except RepairBoundaryViolation as error:
        return _reject(dispatch, "candidate_boundary_violation", str(error))
    parent = dispatch.projection["parent"]
    return _accept(dispatch, {"workbook_versions": [_candidate_record(
        dispatch, channel="workbook", scope="workbook", defect_id=defect_id,
        parent_sha256=parent.get("parent_sha256"))]})


# ------------------------------------------------------------------ node registration


MODEL_NODE_ADAPTERS: Mapping[str, Callable[..., dict[str, Any]]] = {
    "M01_RESEARCH_UNIT_SOURCES": m01_research_unit_sources,
    "M02_CREATE_UNIT_DOMAIN_DATA": m02_create_unit_domain_data,
    "M03_WRITE_UNIT_CONTENT": m03_write_unit_content,
    "M04_CREATE_UNIT_VISUALS": m04_create_unit_visuals,
    "M05_REVIEW_ACTUAL_UNIT": m05_review_actual_unit,
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": m06_repair_named_unit_artifact,
    "M07_REVIEW_ACTUAL_WORKBOOK": m07_review_actual_workbook,
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": m08_repair_named_workbook_defect,
}


def build_model_nodes(context: ModelNodeContext) -> dict[str, Callable[[Mapping[str, Any]],
                                                                      dict[str, Any]]]:
    """Bind the eight adapters to one context for `add_node` registration by N20/N30."""

    return {job_id: (lambda packet, _adapter=adapter: _adapter(packet, context))
            for job_id, adapter in MODEL_NODE_ADAPTERS.items()}


def transport_call_sites() -> list[str]:
    """Every function in this module that invokes a transport, for audit by test."""

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    sites: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if (isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "execute"):
                sites.append(node.name)
    return sorted(set(sites))
````

</details>

## FILE: runtime/langgraph_factory/nodes/sources.py

SHA-256: `b96bab07e807b4e1aa93d6d68697c48ea96a2f69f5bb7c78fa760dd9b8f304cf`

<details><summary>Exact content</summary>

````
"""Unit selection, source request/retrieval compilation, admission, and prerequisites.

Owns D05, D06, D06B, D07, and D30. The source path's whole job is to turn a
manifest unit into a *closed* set of admitted primary-source facts: every node
here fails closed rather than admitting a fact whose retrieval, hash, or
correlation cannot be reproduced.
"""

from __future__ import annotations

from typing import Any

from . import (
    PrerequisitePause,
    SystemFailure,
    candidate_field,
    canonical_digest,
    contract_reference,
    deterministic_node,
    guard,
    require,
    staged_dispatch,
    worker_packet,
)
from ..egress import AuthorizationRecord, authorize_transmission

__all__ = [
    "SOURCE_REQUEST_FIELDS",
    "SOURCE_RULES",
    "DOMAIN_SCHEMA_CONTRACT",
    "DOMAIN_CALIBRATION_CONTRACT",
    "compile_unit_source_requests",
    "D05_SELECT_NEXT_UNIT",
    "D06_COMPILE_SOURCE_REQUESTS",
    "D06B_RETRIEVE_SOURCE_CANDIDATES",
    "D07_CORRELATE_AND_ADMIT_SOURCES",
    "D30_CLASSIFY_PREREQUISITE",
]


# The rules an M01 worker is bound by in either phase. They are the engine's own
# invariants, stated to the worker: D06B retrieves every byte, so a locator set
# is all a discovery may produce, and D07 admits nothing whose request
# correlation it cannot reproduce.
SOURCE_RULES: dict[str, Any] = {
    "primary_sources_only": True,
    "max_locators_per_request": 3,
    "must_cite_request_id": True,
    "bytes_retrieved_by": "controller",
}

DOMAIN_SCHEMA_CONTRACT = "schemas/manifest_domain.metaschema.v1.json"
DOMAIN_CALIBRATION_CONTRACT = "policy/calibration.v1.yaml"


SOURCE_REQUEST_FIELDS: tuple[str, ...] = (
    "key",
    "unit_id",
    "source_epoch",
    "fact_id",
    "question",
    "required",
    "scope",
)

# The manifest keys that declare facts a unit's content must be grounded in.
# These are engine-contract key names, not curriculum values: any manifest using
# the frozen schema declares them, whatever its subject.
_FACT_BEARING_KEYS: tuple[str, ...] = (
    "required_explanation",
    "core_activity",
    "safety_focus",
    "applications",
)


def _record(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), "schema_contract", f"{label} must be a JSON object")
    return dict(value)


def _unit_projection(unit: dict[str, Any]) -> dict[str, Any]:
    """The bounded unit facts a worker may see: identity and declared scope only."""

    return {
        "unit_id": unit.get("id"),
        "title": unit.get("title"),
        "declared_scope": {
            key: unit[key] for key in _FACT_BEARING_KEYS if unit.get(key) is not None
        },
    }


def _request_projection(request: dict[str, Any]) -> dict[str, Any]:
    """One source request, named by the identifier the candidate must cite back."""

    return {
        "request_id": request["key"],
        "unit_id": request["unit_id"],
        "source_epoch": request["source_epoch"],
        "fact_id": request["fact_id"],
        "question": request["question"],
        "required": request["required"],
        "scope": request["scope"],
    }


def _unit_record(effective_run: dict[str, Any], unit_id: str) -> dict[str, Any]:
    for unit in effective_run.get("unit_records", []):
        if isinstance(unit, dict) and unit.get("id") == unit_id:
            return unit
    raise SystemFailure(
        "invalid_input",
        f"unit {unit_id!r} is not in the frozen effective run",
        {"unit_id": unit_id},
    )


# --------------------------------------------------------------------------
# D05
# --------------------------------------------------------------------------


@deterministic_node("D05_SELECT_NEXT_UNIT")
def D05_SELECT_NEXT_UNIT(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Select the next required unaccepted unit in frozen manifest order."""

    effective_run = projection["effective_run"]
    require(bool(effective_run), "invalid_input", "unit selection requires a frozen effective run")

    closure = effective_run.get("target_closure")
    require(
        isinstance(closure, list) and bool(closure),
        "invalid_input",
        "the frozen effective run declares an empty target closure",
    )

    accepted = projection["accepted_unit_receipts"]
    cursor = dict(projection["cursor"])
    manifest_ordinal = cursor.get("manifest_ordinal", 0)
    accepted_ordinal = cursor.get("accepted_ordinal", 0)

    require(
        0 <= manifest_ordinal <= len(closure),
        "integrity",
        "the manifest cursor is outside the frozen closure",
        manifest_ordinal=manifest_ordinal,
        closure_size=len(closure),
    )
    require(
        accepted_ordinal == len([unit_id for unit_id in closure if unit_id in accepted]),
        "integrity",
        "the accepted cursor disagrees with the accepted receipt set",
        accepted_ordinal=accepted_ordinal,
        accepted_receipts=len([unit_id for unit_id in closure if unit_id in accepted]),
    )

    remaining = [unit_id for unit_id in closure if unit_id not in accepted]
    if not remaining:
        return {
            "cursor": {"manifest_ordinal": len(closure), "accepted_ordinal": accepted_ordinal},
            "selected_unit_id": None,
            "pending_guard": guard("D05_SELECT_NEXT_UNIT", "manifest_exhausted"),
        }

    selected = remaining[0]
    return {
        "selected_unit_id": selected,
        "unit_status": {selected: "SELECTED"},
        "cursor": {
            "manifest_ordinal": closure.index(selected) + 1,
            "accepted_ordinal": accepted_ordinal,
        },
        "pending_guard": guard("D05_SELECT_NEXT_UNIT", "unit_selected", unit_id=selected),
    }


# --------------------------------------------------------------------------
# D06
# --------------------------------------------------------------------------


def compile_unit_source_requests(unit: dict[str, Any], source_epoch: int) -> list[dict[str, Any]]:
    """Derive one bounded, named request per fact the unit must be grounded in.

    Manifest-neutral: fact identifiers are derived from the unit's own declared
    keys and values, so a unit with more or fewer declared facts produces
    correspondingly more or fewer requests.
    """

    unit_id = unit["id"]
    requests: list[dict[str, Any]] = []
    for key in _FACT_BEARING_KEYS:
        value = unit.get(key)
        if value is None:
            continue
        entries = value if isinstance(value, list) else [value]
        for ordinal, entry in enumerate(entries):
            fact_id = f"{key}:{ordinal:03d}"
            request = {
                "key": f"{unit_id}/{source_epoch}/{fact_id}",
                "unit_id": unit_id,
                "source_epoch": source_epoch,
                "fact_id": fact_id,
                "question": canonical_digest({"unit_id": unit_id, "fact_id": fact_id, "claim": entry}),
                "required": key in ("required_explanation", "safety_focus"),
                "scope": key,
            }
            requests.append(request)
    return requests


@deterministic_node("D06_COMPILE_SOURCE_REQUESTS")
def D06_COMPILE_SOURCE_REQUESTS(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Compile the complete positive source-request denominator for one unit."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")
    unit = _unit_record(projection["effective_run"], unit_id)

    authorizations = projection["external_authorizations"]
    allowed_hosts: list[str] = []
    if authorizations:
        latest = _record(authorizations[-1], "external authorization")
        allowed_hosts = sorted(
            host for host in (latest.get("resolved_hosts") or []) if isinstance(host, str))

    reusable = {
        admission.get("fact_id")
        for admission in projection["source_admissions"]
        if isinstance(admission, dict) and admission.get("unit_id") == unit_id
    }
    source_epoch = 1 + max(
        (
            admission.get("source_epoch", 0)
            for admission in projection["source_admissions"]
            if isinstance(admission, dict) and admission.get("unit_id") == unit_id
        ),
        default=0,
    )

    requests = [
        request
        for request in compile_unit_source_requests(unit, source_epoch)
        if request["fact_id"] not in reusable
    ]

    unresolvable = [
        request["fact_id"]
        for request in requests
        if request["required"] and not request["question"]
    ]
    if unresolvable:
        raise PrerequisitePause(
            "required_external_fact_unavailable",
            "a required fact has no bounded question that could resolve it",
            {"unit_id": unit_id, "fact_ids": sorted(unresolvable)},
        )

    require(
        bool(requests) or bool(reusable),
        "invalid_input",
        f"unit {unit_id!r} declares no fact-bearing content to ground",
        unit_id=unit_id,
    )

    denominator = {
        f"{unit_id}/{source_epoch}": {
            "unit_id": unit_id,
            "source_epoch": source_epoch,
            "request_keys": sorted(request["key"] for request in requests),
            "reused_fact_ids": sorted(reusable),
            "size": len(requests),
        }
    }

    run_id = projection["run_id"]
    episode_id = projection["episode_id"]
    packets = [
        worker_packet(
            run_id=run_id,
            episode_id=episode_id,
            correlation_key=request["key"],
            phase="DISCOVER",
            projection={
                "request": _request_projection(request),
                "unit": _unit_projection(unit),
                "source_rules": dict(SOURCE_RULES),
                "discovery_authority": {
                    "phase": "DISCOVER",
                    "locators_only": True,
                    "may_retrieve_bytes": False,
                    "allowed_hosts": allowed_hosts,
                },
            },
        )
        for request in sorted(requests, key=lambda item: item["key"])
    ]

    return {
        "source_requests": requests,
        "source_denominators": denominator,
        "pending_packet": staged_dispatch("M01_RESEARCH_UNIT_SOURCES", packets),
        "pending_guard": guard(
            "D06_COMPILE_SOURCE_REQUESTS",
            "discovery_fanout",
            unit_id=unit_id,
            request_keys=sorted(request["key"] for request in requests),
        ),
    }


# --------------------------------------------------------------------------
# D06B
# --------------------------------------------------------------------------


@deterministic_node("D06B_RETRIEVE_SOURCE_CANDIDATES")
def D06B_RETRIEVE_SOURCE_CANDIDATES(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Retrieve source bytes deterministically under the frozen host allowlist.

    Retrieval is the controller's job, never a model worker's: a model that could
    fetch its own bytes could also fabricate their provenance.
    """

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    denominator_key = None
    denominator = None
    for key, value in sorted(projection["source_denominators"].items()):
        if isinstance(value, dict) and value.get("unit_id") == unit_id:
            denominator_key, denominator = key, value
    require(
        denominator is not None,
        "invalid_input",
        f"no source denominator exists for unit {unit_id!r}",
    )

    requests = {
        request["key"]: request
        for request in projection["source_requests"]
        if isinstance(request, dict) and request.get("key") in denominator["request_keys"]
    }
    require(
        sorted(requests) == sorted(denominator["request_keys"]),
        "join",
        "the request set does not equal the frozen request denominator",
        expected=sorted(denominator["request_keys"]),
        actual=sorted(requests),
    )

    retriever = getattr(runtime_context, "source_retriever", None)
    require(retriever is not None, "capability", "runtime context exposes no source retriever")
    fetch = getattr(retriever, "fetch", None)
    require(callable(fetch), "capability", "the source retriever exposes no fetch operation")

    authorizations = projection["external_authorizations"]
    require(
        bool(authorizations),
        "authorization",
        "retrieval requires a current external-data authorization record",
    )
    authorization_raw = _record(authorizations[-1], "external authorization")
    authorization_record = AuthorizationRecord(
        run_id=projection["run_id"],
        curriculum_digest=authorization_raw.get("curriculum_digest", ""),
        output_root=authorization_raw.get("output_root", ""),
        approved_at_utc=str(authorization_raw.get("approved_at_utc", "")),
        expires_at_utc=str(authorization_raw.get("expires_at_utc", "")),
        providers=authorization_raw.get("providers") or {},
    )

    retrievals: dict[str, Any] = {}
    unavailable: list[dict[str, Any]] = []
    for request_key, discovery in sorted(projection["source_discoveries"].items()):
        if request_key not in requests:
            continue
        record = _record(discovery, f"discovery for {request_key}")
        locators = candidate_field(record, "locators") or []
        require(
            isinstance(locators, list),
            "schema_contract",
            f"discovery for {request_key} declares a non-list locator set",
        )
        if not locators:
            if requests[request_key].get("required"):
                unavailable.append({"request_key": request_key, "reason": "no locator discovered"})
            continue
        locator = locators[0]
        locator_url = candidate_field(locator, "url")
        require(
            isinstance(locator_url, str) and locator_url,
            "schema_contract",
            f"discovery for {request_key} declares a locator with no url",
        )
        try:
            authorization_receipt = authorize_transmission(
                authorization_record, provider="primary_source_hosts",
                data_classes=["primary_source_bytes"],
                curriculum_digest=authorization_record.curriculum_digest,
                run_id=authorization_record.run_id,
                output_root=authorization_record.output_root)
            response = fetch(locator_url, authorization_receipt=authorization_receipt)
        except FileNotFoundError as error:
            unavailable.append({"request_key": request_key, "reason": str(error)})
            continue
        except Exception as error:  # noqa: BLE001 - classified below, never swallowed
            # A transport, network, or integrity fault is a system failure. Only a
            # named unavailable fact may pause; conflating the two is spec 2.4/6.
            raise SystemFailure(
                "tool",
                f"deterministic retrieval failed for {request_key}: {error}",
                {"request_key": request_key, "locator": locator},
            ) from error

        response_record = _record(response, f"retrieval response for {request_key}")
        for field in ("sha256", "status", "content_type"):
            require(
                field in response_record,
                "integrity",
                f"retrieval response for {request_key} has no {field!r}",
            )
        retrievals[request_key] = {
            "key": request_key,
            "unit_id": unit_id,
            "source_epoch": denominator["source_epoch"],
            "locator": locator,
            "sha256": response_record["sha256"],
            "status": response_record["status"],
            "content_type": response_record["content_type"],
            "tls": response_record.get("tls"),
            "bytes_path": response_record.get("bytes_path"),
        }

    missing_required = [
        {"request_key": key, "reason": "not retrieved"}
        for key, request in sorted(requests.items())
        if request.get("required") and key not in retrievals
    ]
    for entry in missing_required:
        if entry["request_key"] not in {item["request_key"] for item in unavailable}:
            unavailable.append(entry)

    if unavailable:
        raise PrerequisitePause(
            "required_external_fact_unavailable",
            "a named required external fact could not be retrieved",
            {"unit_id": unit_id, "denominator": denominator_key, "facts": unavailable},
        )

    unit = _unit_projection(_unit_record(projection["effective_run"], unit_id))
    run_id = projection["run_id"]
    episode_id = projection["episode_id"]
    packets: list[dict[str, Any]] = []
    for request_key in sorted(retrievals):
        retrieval = retrievals[request_key]
        group = {
            "group_id": canonical_digest(
                {"request_id": request_key, "retrieval_sha256": retrieval["sha256"]}
            ),
            "unit_id": unit_id,
            "source_epoch": retrieval["source_epoch"],
            "retrieved_records": [
                {
                    "retrieval_id": request_key,
                    "locator": retrieval["locator"],
                    "sha256": retrieval["sha256"],
                    "content_type": retrieval["content_type"],
                    "bytes_path": retrieval["bytes_path"],
                }
            ],
        }
        packets.append(
            worker_packet(
                run_id=run_id,
                episode_id=episode_id,
                correlation_key=request_key,
                phase="INTERPRET",
                projection={
                    "request": _request_projection(requests[request_key]),
                    "unit": unit,
                    "source_rules": dict(SOURCE_RULES),
                    "retrieval_group": group,
                },
            )
        )

    return {
        "retrievals": retrievals,
        "pending_packet": staged_dispatch("M01_RESEARCH_UNIT_SOURCES", packets),
        "pending_guard": guard(
            "D06B_RETRIEVE_SOURCE_CANDIDATES",
            "interpretation_fanout",
            unit_id=unit_id,
            retrieval_keys=sorted(retrievals),
        ),
    }


# --------------------------------------------------------------------------
# D07
# --------------------------------------------------------------------------


@deterministic_node("D07_CORRELATE_AND_ADMIT_SOURCES")
def D07_CORRELATE_AND_ADMIT_SOURCES(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Join discovery, retrieval, and interpretation against the exact denominator."""

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    denominator = None
    for value in projection["source_denominators"].values():
        if isinstance(value, dict) and value.get("unit_id") == unit_id:
            denominator = value
    require(denominator is not None, "invalid_input", f"no source denominator for {unit_id!r}")

    expected = set(denominator["request_keys"])
    retrievals = projection["retrievals"]
    interpretations = projection["source_interpretations"]
    requests_by_key = {
        request.get("key"): request
        for request in projection["source_requests"]
        if isinstance(request, dict)
    }

    # Cross-unit contamination is a join failure, not a filterable condition: a
    # member keyed to another unit means the fan-out correlation itself is wrong.
    for label, collection in (("retrievals", retrievals), ("interpretations", interpretations)):
        foreign = sorted(
            key
            for key, value in collection.items()
            if isinstance(value, dict)
            and candidate_field(value, "unit_id") not in (None, unit_id)
            and key in expected
        )
        require(
            not foreign,
            "join",
            f"{label} contain members correlated to another unit",
            keys=foreign,
        )

    interpreted = {key for key in interpretations if key in expected}
    missing = sorted(expected - interpreted)
    extra = sorted(
        key for key in interpretations if key not in expected and _keyed_to(interpretations[key], unit_id)
    )
    require(not extra, "join", "interpretations contain members outside the denominator", keys=extra)

    stale: list[dict[str, Any]] = []
    for key in sorted(interpreted):
        interpretation = _record(interpretations[key], f"interpretation {key}")
        parent = candidate_field(interpretation, "retrieval_sha256")
        retrieval = retrievals.get(key)
        current = retrieval.get("sha256") if isinstance(retrieval, dict) else None
        if parent != current:
            stale.append({"key": key, "interpreted_from": parent, "current": current})
    require(
        not stale,
        "integrity",
        "an interpretation was derived from bytes that are no longer the retrieval",
        stale=stale,
    )

    if missing:
        required_missing = sorted(
            key
            for key in missing
            if any(
                request.get("key") == key and request.get("required")
                for request in projection["source_requests"]
                if isinstance(request, dict)
            )
        )
        return {
            "source_join_evidence": [
                {
                    "key": canonical_digest({"unit_id": unit_id, "missing": missing}),
                    "unit_id": unit_id,
                    "result": "INCOMPLETE",
                    "missing": missing,
                    "required_missing": required_missing,
                }
            ],
            "pending_guard": guard(
                "D07_CORRELATE_AND_ADMIT_SOURCES",
                "prerequisite_unresolved",
                unit_id=unit_id,
                missing=missing,
                required_missing=required_missing,
            ),
        }

    admissions: list[dict[str, Any]] = []
    for key in sorted(expected):
        interpretation = _record(interpretations[key], f"interpretation {key}")
        retrieval = _record(retrievals[key], f"retrieval {key}")
        admissions.append(
            {
                "key": key,
                "unit_id": unit_id,
                "source_epoch": denominator["source_epoch"],
                "fact_id": key.rsplit("/", 1)[-1],
                "locator": retrieval.get("locator"),
                "sha256": retrieval.get("sha256"),
                "content_type": retrieval.get("content_type"),
                "interpretation_hash": canonical_digest(interpretation),
                "scope": candidate_field(
                    interpretation, "scope", requests_by_key.get(key, {}).get("scope")
                ),
            }
        )

    join_evidence = {
        "key": canonical_digest({"unit_id": unit_id, "admitted": [a["key"] for a in admissions]}),
        "unit_id": unit_id,
        "result": "PASS",
        "denominator_size": len(expected),
        "admitted_size": len(admissions),
    }

    engine_root = projection["engine_root"]
    packet = worker_packet(
        run_id=projection["run_id"],
        episode_id=projection["episode_id"],
        correlation_key=f"{unit_id}/{denominator['source_epoch']}/domain",
        projection={
            "unit": _unit_projection(_unit_record(projection["effective_run"], unit_id)),
            "admitted_sources": [
                {
                    "source_id": admission["key"],
                    "fact_id": admission["fact_id"],
                    "locator": admission["locator"],
                    "sha256": admission["sha256"],
                    "content_type": admission["content_type"],
                    "scope": admission["scope"],
                }
                for admission in admissions
            ],
            "domain_schema": contract_reference(engine_root, DOMAIN_SCHEMA_CONTRACT),
            "verifier_interface": {
                "declared_at": "/verifier_result",
                "required_result": "all_fixtures_behaved",
                "proven_by": "D08_VALIDATE_DOMAIN",
            },
            "calibration": contract_reference(engine_root, DOMAIN_CALIBRATION_CONTRACT),
        },
    )

    return {
        "source_admissions": admissions,
        "source_join_evidence": [join_evidence],
        "pending_packet": staged_dispatch("M02_CREATE_UNIT_DOMAIN_DATA", [packet]),
        "pending_guard": guard(
            "D07_CORRELATE_AND_ADMIT_SOURCES", "sources_admitted", unit_id=unit_id
        ),
    }


def _keyed_to(value: Any, unit_id: str) -> bool:
    return isinstance(value, dict) and candidate_field(value, "unit_id") == unit_id


# --------------------------------------------------------------------------
# D30
# --------------------------------------------------------------------------


@deterministic_node("D30_CLASSIFY_PREREQUISITE")
def D30_CLASSIFY_PREREQUISITE(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Classify an unresolved source requirement as a pause, or refuse to.

    Only a named unavailable required external fact may pause an episode. Every
    other cause reaching this node is a system failure: a run that reports
    "waiting for a source" when its renderer is broken is a run that will be
    resumed forever.
    """

    unit_id = projection["selected_unit_id"]
    require(isinstance(unit_id, str) and unit_id, "invalid_input", "no unit is selected")

    failure = projection["pending_failure"]
    named: list[str] = []
    if isinstance(failure, dict):
        failure_class = failure.get("class")
        require(
            failure_class == "pause",
            "invalid_input",
            f"prerequisite classification received a {failure_class!r} failure, which cannot pause",
            failure_cause=failure.get("cause"),
            failure_node=failure.get("node"),
        )
        evidence = failure.get("evidence") or {}
        named = sorted(
            str(entry.get("request_key") or entry.get("fact_id"))
            for entry in evidence.get("facts", [])
            if isinstance(entry, dict)
        )
        named += sorted(str(value) for value in evidence.get("fact_ids", []))

    denominator = None
    for value in projection["source_denominators"].values():
        if isinstance(value, dict) and value.get("unit_id") == unit_id:
            denominator = value
    require(denominator is not None, "invalid_input", f"no source denominator for {unit_id!r}")

    if not named:
        named = sorted(set(denominator["request_keys"]) - set(projection["retrievals"]))

    require(
        bool(named),
        "invalid_input",
        "prerequisite classification found no named unresolved requirement",
        unit_id=unit_id,
    )
    require(
        len(named) == 1,
        "invalid_input",
        "exactly one named required external fact may pause an episode",
        named=named,
    )

    fact = named[0]
    attempts = projection["attempt_counters"].get(f"retrieval:{fact}", 0)

    record = {
        "kind": "prerequisite_classification",
        "unit_id": unit_id,
        "fact": fact,
        "attempts": attempts,
        "source_epoch": denominator["source_epoch"],
        "required_resume_condition": f"named external fact {fact} becomes retrievable",
    }
    record["key"] = canonical_digest(record)

    resume_frontier = {
        "destination": "D06B_RETRIEVE_SOURCE_CANDIDATES",
        "selected_unit_id": unit_id,
        "parent_hashes": {},
        "blocked_on": fact,
    }

    candidate = {
        "kind": "PAUSED_PREREQUISITE",
        "unit_id": unit_id,
        "fact": fact,
        "attempts": attempts,
        "locators": sorted(
            str(value.get("locator"))
            for key, value in projection["retrievals"].items()
            if key == fact and isinstance(value, dict)
        ),
        "required_resume_condition": record["required_resume_condition"],
        "resume_frontier": resume_frontier,
    }

    return {
        "evidence_index_entries": [record],
        "terminal_candidate": candidate,
        "resume_frontier": resume_frontier,
        "pending_guard": guard("D30_CLASSIFY_PREREQUISITE", "prerequisite_pause", fact=fact),
    }
````

</details>

## FILE: runtime/run_curriculum.py

SHA-256: `10236810e66ff4afb064635b77082a840c4f7bf8ba107970ba80d6e80a8d1e8b`

<details><summary>Exact content</summary>

````
#!/usr/bin/env python3
"""`python3 -m runtime.run_curriculum` — the sole production entry to the compiled
Plan 26 LangGraph curriculum factory (spec section 16).

This module parses and validates CLI syntax, canonicalizes paths, acquires the
per-output-root execution lock, prepares one episode invocation, builds the one
production graph (`runtime.langgraph_factory.graph.build_curriculum_factory_graph`),
invokes it exactly once, projects its structured output into the one printed JSON
object, and maps the result to an exit code. It runs no product step itself: it
holds no node body, no guard, no join, no acceptance rule, and no frontier
selection — every one of those lives inside the compiled graph, which is the only
thing here that ever decides what a run produced.

Two narrow, pure, side-effect-free helpers are imported from the graph package
rather than re-implemented: `_resolve_active_manifest` and `_frozen_input_records`
(`runtime.langgraph_factory.nodes.inputs`) are the exact functions the graph's own
input-freezing node uses to pick the active manifest and hash the frozen input
set. This module calls them once, before the graph exists, purely to fix the
identity seed and the authorization/transport digest a `RuntimeContext` needs
before the first invocation; the graph's input-freezing node independently
recomputes the same values inside the episode and is the sole authority the graph
itself trusts. Reusing the functions (rather than duplicating the hashing rule)
is what keeps the two computations from silently drifting apart; it is not a
second product path, because neither call site is reachable from the other and
neither one decides acceptance, routing, or a terminal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import yaml

from runtime.langgraph_factory import persistence as P
from runtime.langgraph_factory import transport as tp
from runtime.langgraph_factory.artifacts import canonical_digest
from runtime.langgraph_factory.egress import (
    PROVIDER_DATA_CLASSES,
    PROVIDERS,
    AuthorizationRecord,
    EgressGuard,
    ReceiptLog,
    RetrievalHostProfileError,
    load_retrieval_host_profile,
)
from runtime.langgraph_factory.graph import build_curriculum_factory_graph, build_runtime_context
from runtime.langgraph_factory.nodes.inputs import (
    DRIVER_CAPABILITY_FIELDS,
    MANDATORY_DRIVER_CLIS,
    REQUIRED_CAPABILITIES,
    _frozen_input_records,
    _resolve_active_manifest,
)

__all__ = ["build_parser", "main"]

PROG = "python3 -m runtime.run_curriculum"
CONTRACT_VERSION = "1"

# spec section 14's exit-code column, restated here rather than imported: this
# module must not import a node body, guard, or terminal-writing function, and
# the mapping itself is fixed, spec-owned data, not a decision this CLI makes.
TERMINAL_EXIT_CODES: dict[str, int] = {
    "UNIT_ACCEPTED": 0,
    "COMPLETE": 0,
    "INTERRUPTED": 10,
    "PAUSED_PREREQUISITE": 11,
    "CONVERGENCE_EXHAUSTED": 12,
    "SYSTEM_FAILURE": 20,
}
SYSTEM_FAILURE_EXIT = 20
ARGUMENT_ERROR_EXIT = 2
NOT_READY_EXIT = 3

# FactoryState channels that belong to *this* episode and must never be seeded
# from a prior episode's checkpointed values: the graph's own bootstrap and
# resume nodes write them fresh, and a stale write_once value here would
# collide with that fresh write instead of being silently ignored.
_EPISODE_SCOPED_STATE_FIELDS: frozenset[str] = frozenset(
    {
        "invocation",
        "bootstrap_kind",
        "validated_recovery_envelope",
        "episode_id",
        "checkpoint_thread_id",
        "checkpoint_namespace",
        "resume_from",
        "pending_failure",
        "pending_packet",
        "pending_guard",
        "terminal_candidate",
        "terminal",
    }
)


class CliError(Exception):
    """Base class for a pre-episode CLI refusal; carries its own exit code."""

    exit_code = ARGUMENT_ERROR_EXIT

    def __init__(self, code: str, message: str, **detail: Any) -> None:
        super().__init__(message)
        self.code = code
        self.detail = detail


class CliArgumentError(CliError):
    """Malformed or contradictory CLI input. Exit 2, before any episode."""

    exit_code = ARGUMENT_ERROR_EXIT


class CliNotReadyError(CliError):
    """A syntactically valid invocation the run cannot safely start. Exit 3."""

    exit_code = NOT_READY_EXIT


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- args


def build_parser() -> argparse.ArgumentParser:
    """The exact preflight/one/all/resume argument surface of spec section 16."""

    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Sole production CLI entry to the compiled Plan 26 curriculum factory.",
    )
    parser.add_argument("--engine-root", required=True, metavar="PATH")
    parser.add_argument("--curriculum", required=True, metavar="PATH")
    parser.add_argument("--output-root", required=True, metavar="PATH")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true", help="read-only readiness check; creates no run")
    mode.add_argument("--unit", metavar="UNIT_ID", help="run one requested unit plus its prerequisite closure")
    mode.add_argument("--all", action="store_true", help="run the full exact manifest")
    mode.add_argument("--resume", action="store_true", help="resume a legally resumable episode")

    parser.add_argument(
        "--authorization",
        metavar="PATH",
        help="external-data authorization record; required for --unit, --all, and --resume",
    )
    return parser


def _validate_args(args: argparse.Namespace) -> None:
    if args.preflight and args.authorization:
        raise CliArgumentError(
            "ARG-PREFLIGHT-NO-AUTHORIZATION",
            "--preflight is a read-only capability check and does not take --authorization",
        )
    if not args.preflight and not args.authorization:
        raise CliArgumentError(
            "ARG-AUTHORIZATION-REQUIRED",
            "--unit, --all, and --resume each require --authorization",
        )


# ---------------------------------------------------------------- path resolution


def _canonical_root(value: str, label: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if not path.is_dir():
        raise CliArgumentError("ARG-NOT-A-DIRECTORY", f"{label} is not a directory: {path}", path=str(path))
    return path


def _canonical_output_root(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def _resolve_curriculum_root(value: str) -> Path:
    """Accept either a manifest file or a curriculum directory (spec section 16)."""

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if path.is_file():
        return path.parent
    if path.is_dir():
        return path
    raise CliArgumentError("ARG-CURRICULUM-NOT-FOUND", f"--curriculum does not exist: {path}", path=str(path))


def _read_authorization(value: str) -> dict[str, Any]:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    if not path.is_file():
        raise CliArgumentError(
            "ARG-AUTHORIZATION-NOT-FOUND", f"--authorization file not found: {path}", path=str(path)
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CliArgumentError(
            "ARG-AUTHORIZATION-UNREADABLE", f"--authorization is not readable JSON: {error}", path=str(path)
        ) from error
    if not isinstance(raw, dict):
        raise CliArgumentError("ARG-AUTHORIZATION-SHAPE", "--authorization must be a JSON object", path=str(path))
    missing = [key for key in ("approved_at_utc", "expires_at_utc", "providers") if key not in raw]
    if missing:
        raise CliArgumentError(
            "ARG-AUTHORIZATION-INCOMPLETE",
            f"--authorization is missing required field(s) {missing}",
            path=str(path),
        )
    return raw


def _collision_reason(output_root: Path) -> str | None:
    """spec section 16: a fresh output root must not exist, or exist empty."""

    if not output_root.exists():
        return None
    if not output_root.is_dir():
        return f"--output-root exists and is not a directory: {output_root}"
    if any(output_root.iterdir()):
        return (
            f"--output-root {output_root} is not empty and carries no resumable run; "
            "a fresh run requires a nonexistent or empty output root"
        )
    return None


# --------------------------------------------------------------------------- authorization/capability


def _retrieval_host_selection(active_manifest_path: Path) -> tuple[str, tuple[str, ...], str]:
    """The curriculum's own named retrieval-host profile, resolved and validated.

    A curriculum selects a profile by name (`retrieval_host_profile:` in its own
    manifest); it never supplies hosts directly (N30V7-F07, spec decision). Absent
    entirely, retrieval stays fully denied -- the pre-existing, safe default -- not
    silently open.
    """
    try:
        manifest = yaml.safe_load(active_manifest_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise CliNotReadyError("MANIFEST-UNREADABLE", str(error)) from error
    profile_name = (manifest or {}).get("retrieval_host_profile") if isinstance(manifest, dict) else None
    if not isinstance(profile_name, str) or not profile_name:
        return "", (), ""
    try:
        hosts, policy_digest = load_retrieval_host_profile(profile_name)
    except RetrievalHostProfileError as error:
        raise CliNotReadyError("RETRIEVAL-HOST-PROFILE-INVALID", str(error)) from error
    return profile_name, hosts, policy_digest


def _authorization_envelope(
    raw: Mapping[str, Any], *, curriculum_digest: str, output_root: Path,
    retrieval_host_profile: str = "", retrieval_hosts: Sequence[str] = (),
    retrieval_hosts_digest: str = "",
) -> dict[str, Any]:
    envelope = dict(raw)
    envelope["curriculum_digest"] = curriculum_digest
    envelope["output_root"] = str(output_root)
    envelope["retrieval_host_profile"] = retrieval_host_profile
    envelope["resolved_hosts"] = list(retrieval_hosts)
    envelope["retrieval_hosts_digest"] = retrieval_hosts_digest
    return envelope


def _authorization_record(
    raw: Mapping[str, Any], *, run_id: str, curriculum_digest: str, output_root: Path
) -> AuthorizationRecord:
    return AuthorizationRecord(
        run_id=run_id,
        curriculum_digest=curriculum_digest,
        output_root=str(output_root),
        approved_at_utc=str(raw["approved_at_utc"]),
        expires_at_utc=str(raw["expires_at_utc"]),
        providers=raw.get("providers") or {},
    )


def _capability_forbidden_paths(engine_root: Path) -> list[Path]:
    return [path for path in (engine_root / "pyproject.toml", engine_root / "runtime") if path.exists()]


# ------------------------------------------------------------- driver capability proof
#
# spec 7.1's five differentiated proof classes, corrected after the Run 26 false-ready
# defect (binaries present, one required provider unauthenticated, preflight still
# reported ready): a single undifferentiated flag never proves a CLI driver is really
# usable. Every field below is genuine and independently checkable; `ready` requires
# every mandatory field for every mandatory driver in `MANDATORY_DRIVER_CLIS`, so one
# unproven field makes the whole driver -- and the whole proof -- not ready.
#
# This is the production CLI's own logic (not a node body, so it may call
# `runtime.langgraph_factory.transport` directly, exactly as `_prove_live_capabilities`
# already does): it never reimplements N20's provider allowlist or data-class mapping,
# consuming `egress.PROVIDERS`/`egress.PROVIDER_DATA_CLASSES` read-only for the
# `approved_data_boundary` field, and it wires N20's tool/MCP-closure check (spec 7.1 class five,
# `transport.prove_claude_tool_closure`/`require_claude_tool_closure`) into this real
# dispatch path rather than leaving it a standalone, unwired function.

_FORBIDDEN_AUTH_ENV_VARS: tuple[str, ...] = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "OPENAI_API_KEY",
    "CLAUDE_API_KEY",
    "CODEX_API_KEY",
)

_PROBE_TIMEOUT_SECONDS = 60

# A fixed, hardcoded literal: no curriculum digest, output root, file path, or source
# text is ever interpolated into it, which is what makes `content_free_operation`
# provable rather than merely asserted.
_PROBE_INSTRUCTION: str = (
    'Preflight capability probe. Do not read, write, or invoke any tool. '
    'Reply with exactly the structured object {"ok": true} and nothing else.'
)

_PROBE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["ok"],
    "properties": {"ok": {"type": "boolean"}},
}

_TOOL_CLOSURE_NOT_APPLICABLE: dict[str, Any] = {
    "status": "not_applicable",
    "reason": "tool/MCP closure applies to the claude worker channel only",
}


def _prove_one_driver(
    cli: str,
    *,
    model: str,
    provider: str,
    data_classes: Sequence[str],
    runner: Callable[..., tp.ProcessOutcome],
    workspace: Path,
) -> dict[str, Any]:
    fields: dict[str, Any] = {}

    try:
        identity = tp.probe_executable(cli)
    except tp.CapabilityProofFailed as error:
        fields["executable_identity"] = {
            "status": "FAIL", "reason": "executable_unproven", "detail": str(error),
        }
    else:
        fields["executable_identity"] = {
            "status": "PASS", "path": identity.path, "sha256": identity.sha256, "version": identity.version,
        }

    forbidden_present = sorted(name for name in _FORBIDDEN_AUTH_ENV_VARS if os.environ.get(name))
    if forbidden_present:
        fields["permitted_auth_mode"] = {
            "status": "FAIL", "reason": "forbidden_api_key_present", "credentials": forbidden_present,
        }
    else:
        fields["permitted_auth_mode"] = {"status": "PASS", "mode": "subscription"}

    # A preflight/driver-level check, never a per-job one: preflight explicitly takes
    # no `--authorization` (spec 16), so it has no run-scoped `AuthorizationRecord` to
    # evaluate a data class against -- that per-job, per-run check is
    # `egress.authorize_subprocess_transmission`'s own job at real dispatch time,
    # already exercised by N20's suite, and not re-derivable here without either
    # fabricating an authorization or reimplementing its rule. What a driver-level
    # proof *can* honestly establish, read-only against `egress.PROVIDERS`, is that
    # this driver's provider is still one of the approved, non-retired classes at
    # all -- an unapproved or retired provider fails closed here rather than only at
    # first real transmission.
    if provider not in PROVIDERS:
        fields["approved_data_boundary"] = {
            "status": "FAIL", "reason": "unapproved_provider", "provider": provider,
        }
    else:
        fields["approved_data_boundary"] = {
            "status": "PASS",
            "provider": provider,
            "registered_data_classes": sorted(set(data_classes)),
            "provider_data_classes": sorted(PROVIDER_DATA_CLASSES.get(provider, frozenset())),
        }

    fields["content_free_operation"] = {
        "status": "PASS",
        "probe_instruction_sha256": hashlib.sha256(_PROBE_INSTRUCTION.encode("utf-8")).hexdigest(),
        "transmitted_authorized_input_projection": {},
    }

    if fields["permitted_auth_mode"]["status"] != "PASS" or fields["executable_identity"]["status"] != "PASS":
        reason = (
            "skipped_forbidden_auth_mode" if fields["permitted_auth_mode"]["status"] != "PASS"
            else "skipped_executable_unproven"
        )
        fields["observable_subscription_backed_usability"] = {"status": "FAIL", "reason": reason}
        fields["tool_mcp_closure"] = (
            {"status": "FAIL", "reason": reason} if cli == "claude"
            else dict(_TOOL_CLOSURE_NOT_APPLICABLE)
        )
        failed_fields = sorted(name for name, detail in fields.items() if detail.get("status") == "FAIL")
        return {
            "cli": cli, "model": model, "provider": provider, "ready": not failed_fields,
            "failed_fields": failed_fields, "fields": fields,
        }

    # The real, sandboxed dispatch route (spec 7.1/7.2) -- the same
    # stage_workspace/render_sandbox_profile/build_worker_environment path every
    # real M0x job uses, not a shortcut that only proves *this* unsandboxed shell
    # is logged in. N70's live proof found those two routes genuinely differ: the
    # installed Claude CLI's macOS Keychain OAuth lookup depends on isolation-
    # breaking state (`USER`, a minimal `~/.claude.json`, and reach to
    # `~/Library/Keychains`) that only `claude_auth_provision` + the sandbox
    # profile's own keychain rule provide -- an unsandboxed probe could not have
    # caught that gap because it never hit it.
    probe_home = Path(workspace) / "_preflight_home"
    probe_home.mkdir(parents=True, exist_ok=True)

    probe_stdin: str | None = None
    if cli == "claude":
        tp.claude_auth_provision(probe_home)
        projection = tp.build_cli_schema_projection(_PROBE_SCHEMA)
        probe_stdin = tp.build_claude_stdin_payload(instruction=_PROBE_INSTRUCTION, projection={})
        argv = tp.build_claude_argv(
            workspace=workspace, model=model, effort="low", cli_schema_projection=projection)
    else:
        tp.codex_auth_provision(probe_home / "codex")
        # `build_codex_argv` pins `--output-schema output.schema.json -o result.json`,
        # both resolved against `-C <workspace>` (spec 7.2): codex reads the schema
        # from that staged file rather than accepting one inline, so the probe must
        # stage it exactly as a real job would, with the same content-free literal.
        (workspace / "output.schema.json").write_text(
            tp.canonical_json(_PROBE_SCHEMA), encoding="utf-8")
        argv = tp.build_codex_argv(
            workspace=workspace, model=model, reasoning_effort="low", instruction=_PROBE_INSTRUCTION)

    profile_path = probe_home / "profile.sb"
    profile_path.write_text(
        tp.render_sandbox_profile(
            workspace=workspace, home=probe_home, readable=tp.executable_read_roots(identity.path)),
        encoding="utf-8")
    sandboxed_argv = tp.build_sandboxed_argv(argv, profile_path=profile_path)
    probe_env = tp.build_worker_environment(home=probe_home)
    try:
        outcome = runner(
            sandboxed_argv, cwd=workspace, env=probe_env, timeout_seconds=_PROBE_TIMEOUT_SECONDS,
            stdin=probe_stdin,
        )
    except OSError as error:
        fields["observable_subscription_backed_usability"] = {
            "status": "FAIL", "reason": "probe_launch_failed", "detail": str(error),
        }
        fields["tool_mcp_closure"] = (
            {"status": "FAIL", "reason": "no_stream_output_to_evaluate_closure"} if cli == "claude"
            else dict(_TOOL_CLOSURE_NOT_APPLICABLE)
        )
        failed_fields = sorted(name for name, detail in fields.items() if detail.get("status") == "FAIL")
        return {
            "cli": cli, "model": model, "provider": provider, "ready": not failed_fields,
            "failed_fields": failed_fields, "fields": fields,
        }

    if outcome.returncode != 0:
        fields["observable_subscription_backed_usability"] = {
            "status": "FAIL", "reason": "nonzero_bounded_probe",
            "returncode": outcome.returncode, "termination": outcome.termination,
            "stderr": outcome.stderr[:500],
        }
    else:
        try:
            observed = (
                tp.observe_claude_identity(outcome.stdout) if cli == "claude"
                else tp.observe_codex_identity(
                    outcome.stdout, codex_home=tp.resolve_codex_home(probe_env))
            )
        except tp.IdentityUnobservable as error:
            fields["observable_subscription_backed_usability"] = {
                "status": "FAIL", "reason": "malformed_or_unobservable_output", "detail": str(error),
            }
        else:
            if observed.model != model:
                fields["observable_subscription_backed_usability"] = {
                    "status": "FAIL", "reason": "model_driver_mismatch",
                    "expected_model": model, "observed_model": observed.model,
                }
            else:
                fields["observable_subscription_backed_usability"] = {
                    "status": "PASS", "observed_model": observed.model,
                }

    if cli == "claude":
        closure: Mapping[str, Any] | None = None
        try:
            closure = tp.prove_claude_tool_closure(outcome.stdout)
            tp.require_claude_tool_closure(closure)
        except tp.CapabilityProofFailed as error:
            fields["tool_mcp_closure"] = {
                "status": "FAIL", "reason": str(error),
                "observed_tools": closure.get("observed_tools") if closure else None,
                "invokable_mcp_servers": closure.get("invokable_mcp_servers") if closure else None,
            }
        else:
            fields["tool_mcp_closure"] = {"status": "PASS", "closure": dict(closure)}
    else:
        fields["tool_mcp_closure"] = dict(_TOOL_CLOSURE_NOT_APPLICABLE)

    failed_fields = sorted(
        name for name, detail in fields.items()
        if detail.get("status") not in ("PASS", "not_applicable")
    )
    return {
        "cli": cli, "model": model, "provider": provider, "ready": not failed_fields,
        "failed_fields": failed_fields, "fields": fields,
    }


def _prove_driver_capabilities(
    *, runner: Callable[..., tp.ProcessOutcome] | None = None, workspace: Path | None = None,
) -> dict[str, Any]:
    """The real, differentiated per-driver capability proof spec 7.1 requires.

    Bounded and content-free: no curriculum artifact, source text, PDF, rendered page,
    evidence, or user-owned file is ever read or transmitted by this probe. Never a
    curriculum model job -- exactly the same "bounded local capability check" contract
    `tp.prove_transport_capabilities` already carries for the transport-isolation
    facets, extended here to the driver identity/auth/usability/closure/boundary
    facets spec 7.1 additionally requires.
    """

    registry = tp.load_job_registry()
    routes_by_cli: dict[str, list[tp.JobRoute]] = {}
    for route in registry.values():
        routes_by_cli.setdefault(route.cli, []).append(route)

    active_runner = runner or tp.run_process
    with tempfile.TemporaryDirectory(prefix="plan26-driver-probe-") as raw_workspace:
        probe_workspace = workspace or Path(raw_workspace)
        drivers: dict[str, dict[str, Any]] = {}
        for cli in MANDATORY_DRIVER_CLIS:
            cli_routes = routes_by_cli.get(cli, ())
            if not cli_routes:
                drivers[cli] = {
                    "cli": cli, "model": None, "provider": None, "ready": False,
                    "failed_fields": list(DRIVER_CAPABILITY_FIELDS),
                    "fields": {
                        name: {"status": "FAIL", "reason": "no_registered_route_for_driver"}
                        for name in DRIVER_CAPABILITY_FIELDS
                    },
                }
                continue
            models = {route.model for route in cli_routes}
            providers = {route.provider for route in cli_routes}
            if len(models) != 1 or len(providers) != 1:
                drivers[cli] = {
                    "cli": cli, "model": sorted(models), "provider": sorted(providers), "ready": False,
                    "failed_fields": list(DRIVER_CAPABILITY_FIELDS),
                    "fields": {
                        name: {"status": "FAIL", "reason": "ambiguous_driver_route_binding"}
                        for name in DRIVER_CAPABILITY_FIELDS
                    },
                }
                continue
            model = next(iter(models))
            provider = next(iter(providers))
            data_classes = sorted({data_class for route in cli_routes for data_class in route.data_classes})
            drivers[cli] = _prove_one_driver(
                cli, model=model, provider=provider, data_classes=data_classes,
                runner=active_runner, workspace=probe_workspace,
            )
        ready = all(detail["ready"] for detail in drivers.values())
    return {"ready": ready, "drivers": drivers}


def _prove_live_capabilities(context: Any, engine_root: Path, output_root: Path) -> dict[str, Any]:
    """Prove the transport isolation facets before the first model transmission.

    Mutates the already-built `context.transport_registry` in place: the proof
    depends on `guard.installed`, and the guard the proof must observe is the
    exact one the transport will use to gate every real transmission, not a
    second guard built only to be thrown away.
    """

    transport = context.transport_registry
    guard = transport.guard
    probe_root = output_root / ".workspaces" / "_cli_capability_probe"
    proof = tp.prove_transport_capabilities(
        guard=guard,
        probe_root=probe_root,
        forbidden_paths=_capability_forbidden_paths(engine_root),
    )
    transport.capability_proof = proof
    # spec 7.1: the same real, differentiated driver-capability proof preflight uses,
    # attached to the exact registry instance the compiled graph's own capability-proof
    # gate reads (best-effort there, for registries that expose it), so a live run's
    # first transmission is gated by the same proof preflight already reported. This
    # is also the hard, unconditional stop that actually closes Run 26's false-ready
    # defect at the one real production entry point: raised here, before
    # `compiled.invoke()` is ever reached, exactly like `prove_transport_capabilities`
    # above already stops a live run on an unproven transport-isolation facet.
    driver_proof = _prove_driver_capabilities(runner=transport.runner)
    transport.driver_capability_proof = driver_proof
    if not driver_proof["ready"]:
        not_ready = sorted(name for name, detail in driver_proof["drivers"].items() if not detail["ready"])
        raise tp.CapabilityProofFailed(
            f"required driver capability unproven for: {not_ready}")
    return proof


def _preflight_capabilities() -> tuple[dict[str, dict[str, Any]], list[str], dict[str, Any]]:
    """Bounded local capability probes only; never populates the real output root."""

    with tempfile.TemporaryDirectory(prefix="plan26-preflight-") as raw_probe_root:
        probe_root = Path(raw_probe_root)
        receipts = ReceiptLog()
        guard = EgressGuard(receipts)
        transport = tp.CliTransport(
            output_root=probe_root,
            run_id="preflight",
            curriculum_digest="0" * 64,
            authorization=None,
            receipts=receipts,
            guard=guard,
            ledger=tp.AttemptLedger(),
            capability_proof=None,
            evidence_root=probe_root / "evidence",
        )
        guard.install()
        try:
            results: dict[str, dict[str, Any]] = {}
            missing: list[str] = []
            for capability in REQUIRED_CAPABILITIES:
                proof = transport.prove_capability(capability)
                results[capability] = proof
                if proof.get("result") != "PASS":
                    missing.append(capability)
            driver_capabilities = _prove_driver_capabilities(runner=transport.runner)
            if not driver_capabilities["ready"]:
                missing.append("driver_capability_proof")
        finally:
            guard.uninstall()
    return results, missing, driver_capabilities


# --------------------------------------------------------------------------- preflight


def _run_preflight(engine_root: Path, curriculum_root: Path, output_root: Path) -> tuple[dict[str, Any], int]:
    collision = _collision_reason(output_root)
    capabilities, missing, driver_capabilities = _preflight_capabilities()
    ready = collision is None and not missing
    payload: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "kind": "PREFLIGHT",
        "ready": ready,
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "output_root": str(output_root),
        "capabilities": capabilities,
        "driver_capabilities": driver_capabilities,
        "missing_capabilities": missing,
        "collision": collision,
    }
    return payload, (0 if ready else NOT_READY_EXIT)


# --------------------------------------------------------------------------- live invocation


def _acquire_lock(output_root: Path) -> P.ExecutionLock:
    lock = P.ExecutionLock(output_root)
    try:
        lock.acquire()
    except P.ExecutionLockUnavailable as error:
        raise CliNotReadyError("LOCK-UNAVAILABLE", str(error)) from error
    return lock


def _prepare_fresh(
    *, engine_root: Path, curriculum_root: Path, output_root: Path, mode: str, requested_unit_id: str | None,
    lock: P.ExecutionLock,
) -> tuple[P.EpisodeInvocation, dict[str, Any], str]:
    active_manifest_path = _resolve_active_manifest(curriculum_root)
    identity_seed = {
        "contract_version": CONTRACT_VERSION,
        "created_at": _utc_now_iso(),
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "active_manifest_path": str(active_manifest_path),
        "output_root": str(output_root),
        "mode": mode,
        "requested_unit_id": requested_unit_id,
    }
    try:
        invocation = P.prepare_episode_invocation(
            output_root=output_root, lock=lock, identity_seed=identity_seed, resume=False
        )
    except P.PersistenceError as error:
        raise CliNotReadyError("BOOTSTRAP-REFUSED", str(error)) from error

    frozen_digest = canonical_digest(_frozen_input_records(engine_root, curriculum_root, active_manifest_path))
    envelope = {
        "kind": "fresh",
        "contract_version": CONTRACT_VERSION,
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "output_root": str(output_root),
        "mode": mode,
        "requested_unit_id": requested_unit_id,
        "authorization": None,  # filled by the caller once it has curriculum_digest
        "episode_ordinal": invocation.episode_ordinal,
        "prior_identity": None,
        "prior_terminal": None,
        "lease_open": False,
    }
    return invocation, envelope, frozen_digest


def _prepare_resume(
    *, output_root: Path, lock: P.ExecutionLock, compiled: Any
) -> tuple[P.EpisodeInvocation, dict[str, Any], str, dict[str, Any]]:
    saver, connection = P.open_checkpoint_saver(output_root)
    try:
        view = P.ReadOnlyCheckpointView(compiled, saver)
        try:
            invocation = P.prepare_episode_invocation(
                output_root=output_root, lock=lock, resume=True, read_view=view
            )
        except P.PersistenceError as error:
            raise CliNotReadyError("RESUME-REFUSED", str(error)) from error

        seed_values: dict[str, Any] = {}
        if invocation.prior_thread_id is not None:
            prior = P.extract_prior_episode(view, invocation.prior_thread_id)
            seed_values = {
                key: value
                for key, value in prior.values.items()
                if key not in _EPISODE_SCOPED_STATE_FIELDS
            }
    finally:
        connection.close()

    identity = invocation.identity_envelope
    prior_terminal = None
    if invocation.resume_from is not None:
        prior_terminal = invocation.resume_from.get("terminal")

    bootstrap_kind = {
        P.BOOTSTRAP_RESUME: "resume",
        P.BOOTSTRAP_RECOVER_ORPHAN: "recover_orphan",
    }.get(invocation.bootstrap_kind, invocation.bootstrap_kind)

    envelope = {
        "kind": bootstrap_kind,
        "contract_version": identity.get("contract_version"),
        "engine_root": identity.get("engine_root"),
        "curriculum_root": identity.get("curriculum_root"),
        "output_root": identity.get("output_root"),
        "mode": identity.get("mode"),
        "requested_unit_id": identity.get("requested_unit_id"),
        "authorization": None,  # filled by the caller once it has curriculum_digest
        "episode_ordinal": invocation.episode_ordinal,
        "prior_identity": identity,
        "prior_terminal": None if bootstrap_kind == "recover_orphan" else prior_terminal,
        "lease_open": bootstrap_kind == "recover_orphan",
    }
    frozen_digest = str(seed_values.get("frozen_digest") or "")
    return invocation, envelope, frozen_digest, seed_values


def _invoke(
    *,
    engine_root: Path,
    output_root: Path,
    envelope: dict[str, Any],
    invocation: P.EpisodeInvocation,
    frozen_digest: str,
    authorization_raw: Mapping[str, Any],
    seed_values: Mapping[str, Any] | None,
    compiled: Any,
    retrieval_host_profile: str = "",
    retrieval_hosts: Sequence[str] = (),
    retrieval_hosts_digest: str = "",
) -> dict[str, Any]:
    context = build_runtime_context(
        engine_root=engine_root,
        output_root=output_root,
        run_id=invocation.run_id,
        curriculum_digest=frozen_digest,
        authorization=_authorization_record(
            authorization_raw, run_id=invocation.run_id, curriculum_digest=frozen_digest, output_root=output_root
        ),
        capability_proof=None,
        retrieval_hosts=retrieval_hosts,
    )
    envelope["authorization"] = _authorization_envelope(
        authorization_raw, curriculum_digest=frozen_digest, output_root=output_root,
        retrieval_host_profile=retrieval_host_profile, retrieval_hosts=retrieval_hosts,
        retrieval_hosts_digest=retrieval_hosts_digest,
    )

    guard = context.transport_registry.guard
    guard.install()
    try:
        _prove_live_capabilities(context, engine_root, output_root)
        graph_input: dict[str, Any] = {**(seed_values or {}), "invocation": envelope}
        return dict(compiled.invoke(graph_input, config=invocation.config, context=context))
    finally:
        guard.uninstall()


# --------------------------------------------------------------------------- output projection


def _project_result(output: Mapping[str, Any]) -> dict[str, Any]:
    terminal = output.get("terminal") or {}
    kind = terminal.get("kind")

    payload: dict[str, Any] = {
        "contract_version": output.get("contract_version"),
        "run_id": output.get("run_id"),
        "episode_id": output.get("episode_id"),
        "terminal": terminal,
        "mode": output.get("mode"),
        "requested_unit_id": output.get("requested_unit_id"),
        "checkpoint_id": None,
        "evidence_index_hash": canonical_digest(list(output.get("evidence_index_entries") or [])),
        "output_root": output.get("output_root"),
    }

    checkpoints = list(output.get("checkpoint_metadata") or [])
    if checkpoints:
        payload["checkpoint_id"] = checkpoints[-1].get("checkpoint_id")

    if kind == "UNIT_ACCEPTED":
        accepted = output.get("accepted_unit_receipts") or {}
        payload["accepted_receipt"] = accepted.get(output.get("requested_unit_id"))
    elif kind == "COMPLETE":
        audits = list(output.get("final_release_audits") or [])
        payload["release_receipt"] = audits[-1] if audits else None

    return payload


def _exit_code_for(payload: Mapping[str, Any]) -> int:
    terminal = payload.get("terminal") or {}
    kind = terminal.get("kind")
    return TERMINAL_EXIT_CODES.get(kind, SYSTEM_FAILURE_EXIT)


def _system_failure_payload(message: str, *, code: str) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "terminal": {
            "kind": "SYSTEM_FAILURE",
            "failure": {"class": "system", "cause": code, "message": message},
        },
    }


# --------------------------------------------------------------------------- main


def _run_live(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    engine_root = _canonical_root(args.engine_root, "--engine-root")
    curriculum_root = _resolve_curriculum_root(args.curriculum)
    output_root = _canonical_output_root(args.output_root)
    authorization_raw = _read_authorization(args.authorization)

    if not args.resume:
        collision = _collision_reason(output_root)
        if collision is not None:
            # Checked before the lock is acquired: acquiring the lock itself
            # would create `.langgraph/` inside `output_root`, which must not
            # happen for a collision this CLI is about to refuse anyway.
            raise CliNotReadyError("COLLISION", collision)

    if args.resume and P.read_identity_envelope(output_root) is None:
        # A read-only check, deliberately before the lock: an output root with no
        # Plan 26 identity envelope (a fresh path, or a Plan 25 root) is refused
        # without acquiring anything or writing a single byte into it — it stays
        # exactly the readable history it was.
        raise CliNotReadyError(
            "RESUME-NO-IDENTITY",
            f"--output-root has no Plan 26 run identity to resume: {output_root}",
        )

    active_manifest_path = _resolve_active_manifest(curriculum_root)
    retrieval_host_profile, retrieval_hosts, retrieval_hosts_digest = _retrieval_host_selection(
        active_manifest_path)

    lock = _acquire_lock(output_root)
    try:
        if args.resume:
            compiled = build_curriculum_factory_graph(engine_root=engine_root, output_root=output_root)
            invocation, envelope, frozen_digest, seed_values = _prepare_resume(
                output_root=output_root, lock=lock, compiled=compiled
            )
        else:
            mode = "all" if args.all else "one"
            requested_unit_id = None if args.all else args.unit
            invocation, envelope, frozen_digest = _prepare_fresh(
                engine_root=engine_root,
                curriculum_root=curriculum_root,
                output_root=output_root,
                mode=mode,
                requested_unit_id=requested_unit_id,
                lock=lock,
            )
            seed_values = None
            compiled = build_curriculum_factory_graph(engine_root=engine_root, output_root=output_root)

        output = _invoke(
            engine_root=engine_root,
            output_root=output_root,
            envelope=envelope,
            invocation=invocation,
            frozen_digest=frozen_digest,
            authorization_raw=authorization_raw,
            seed_values=seed_values,
            compiled=compiled,
            retrieval_host_profile=retrieval_host_profile,
            retrieval_hosts=retrieval_hosts,
            retrieval_hosts_digest=retrieval_hosts_digest,
        )
    finally:
        lock.release()

    payload = _project_result(output)
    return payload, _exit_code_for(payload)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        _validate_args(args)
        if args.preflight:
            engine_root = _canonical_root(args.engine_root, "--engine-root")
            curriculum_root = _resolve_curriculum_root(args.curriculum)
            output_root = _canonical_output_root(args.output_root)
            payload, code = _run_preflight(engine_root, curriculum_root, output_root)
        else:
            payload, code = _run_live(args)
    except CliError as error:
        print(f"{error.code}: {error}", file=sys.stderr)
        # A pre-episode refusal (bad arguments, collision, lock, resume identity)
        # writes no episode and no terminal record at all — exactly section 14's
        # "neither is a product terminal" — so the printed object carries no
        # `terminal` key rather than a fabricated or empty one.
        payload = {"contract_version": CONTRACT_VERSION, "error_code": error.code, "message": str(error)}
        print(json.dumps(payload))
        return error.exit_code
    except Exception as error:  # never let an unhandled fault look like anything but a failure
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        print(json.dumps(_system_failure_payload(str(error), code=type(error).__name__)))
        return SYSTEM_FAILURE_EXIT

    print(json.dumps(payload))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
````

</details>

## FILE: runtime/langgraph_factory/graph.py

SHA-256: `d74e86e3b954591f052a961a08d492de0559a0b79c16d6215541e26c56ff160f`

<details><summary>Exact content</summary>

````
"""The one production `StateGraph`: bindings, skeleton topology, and compilation.

This module owns registration, not node bodies. Every callable it registers is
resolved from N22's `node_registry()` or N23's `MODEL_NODE_ADAPTERS`; a binding
that is missing, placeholder, test-only, duplicated, or dangling fails the build
by stable ID rather than compiling into a graph that would look complete.

It also owns the two things no node body can own:

- the common node boundary (spec section 6.1), which injects `RuntimeContext`,
  records a graceful interrupt observed at the node's atomic boundary, and turns
  an unexpected exception into a classified `pending_failure` instead of letting
  an unproven state continue;
- the `RuntimeContext` factory itself (spec section 5.2), which opens the path
  guard, evidence writer, transport registry, source retriever, signal token and
  clock, and holds no model client and no routing authority.

Scope of this generation: the fixed skeleton only — `START -> D00 -> {D01 fresh
path, D00R resume path} -> D03 -> D04 -> {D05, D92}` plus the orphan-recovery
`D00 -> D96 -> D98 -> END` branch. The per-unit loop, the source/visual `Send`
map/reduce, and the workbook branch are registered by N30 and N32 into this same
builder; `DEFERRED_TOPOLOGY` names their owner for every node registered here
but not yet wired, so an undeclared unwired node still fails compilation.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langgraph.errors import GraphBubbleUp
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime

from . import acceptance, routing, transport as tp, unit_graph, workbook
from .artifacts import ArtifactStore
from .egress import EgressGuard, ReceiptLog, RetrievalPolicy, SourceRetriever
from .evidence import EvidenceStore
from .model_nodes import (
    MODEL_BOOKKEEPING_NODES,
    MODEL_NODE_ADAPTERS,
    build_model_node_context,
)
from .nodes import NODE_CATALOGUE, node_registry
from .persistence import InterruptToken, open_checkpoint_saver
from .state import (
    FACTORY_INPUT_FIELDS,
    FACTORY_OUTPUT_FIELDS,
    FACTORY_STATE_FIELDS,
    FIELD_REDUCER_CLASSES,
    FactoryInput,
    FactoryOutput,
    FactoryState,
    RuntimeContext,
)

__all__ = [
    "GRAPH_NAME",
    "GraphBindingError",
    "DEFERRED_TOPOLOGY",
    "SKELETON_NORMAL_EDGES",
    "SKELETON_BRANCHES",
    "build_runtime_context",
    "binding_inventory",
    "unit_repair_binding_inventory",
    "full_binding_inventory",
    "validate_bindings",
    "register_skeleton",
    "register_unit_repair_topology",
    "register_workbook_topology",
    "build_curriculum_factory_graph",
    "compiled_topology",
    "graph_digest",
    "contract_digests",
]

GRAPH_NAME = "plan26_curriculum_factory"


class GraphBindingError(RuntimeError):
    """A production binding or edge was rejected before compilation."""


# Only these modules may supply a production node body. A callable from anywhere
# else — a test module, a notebook, a locally defined lambda — is rejected by
# stable ID, so "the graph compiled" can never mean "the graph compiled against
# a stand-in".
PRODUCTION_BINDING_MODULES: tuple[str, ...] = (
    "runtime.langgraph_factory.nodes",
    "runtime.langgraph_factory.model_nodes",
    "runtime.langgraph_factory.workbook",
    "runtime.langgraph_factory.repair",
    "runtime.langgraph_factory.acceptance",
)

PLACEHOLDER_NAME_MARKERS: tuple[str, ...] = (
    "stub",
    "placeholder",
    "fake",
    "dummy",
    "mock",
    "sample",
    "example",
    "todo",
    "noop",
    "test",
)

PLACEHOLDER_SOURCE_MARKERS: tuple[str, ...] = (
    "raise NotImplementedError",
    "TODO: implement",
    "placeholder implementation",
)

# Registered here, wired by a later graph node. A node that is neither wired by
# the skeleton/unit-path tables `_validate_topology` inspects nor declared here
# fails the build: silence about an unwired node is how a topology gap becomes
# a silent halt at runtime.
#
# D16 and D17 need no row: once their bodies are members of `available`, they
# are reached as real *destinations* of already-wired `unit_graph.UNIT_BRANCHES`
# sources (D08/D09/D12/D14/D91 -> D17, M05 -> D16 -- the six rows `unit_graph
# .DEFERRED_EDGES` names), so `_validate_topology`'s own `wired` set already
# contains them. D18-D23 are reached only from *inside* the unit repair cycle
# itself (D17 -> D18 -> ... -> D21 -> D16, D22 -> D23 -> D05), which is wired by
# `acceptance.register_unit_repair_path` (via `register_unit_repair_topology`,
# called after `register_skeleton` returns) rather than by any table
# `_validate_topology` reads -- so they are declared deferred here for the same
# reason M06/M07/M08 are: really wired, by a registration step this function
# does not itself see.
#
# D24 needs no row either, for the same reason D16/D17 do not: it is
# `D05_SELECT_NEXT_UNIT`'s own `manifest_exhausted` destination, a row
# `unit_graph.DEFERRED_EDGES` already names, so once D24 is a member of
# `available` it is a real destination `unit_graph.branch_destinations`
# resolves and `_validate_topology`'s `wired` set already contains it. D30 is
# an N22-owned node already wired as a normal member of `unit_graph
# .UNIT_BRANCHES`, not part of this node's own D24-D32 engine at all. D25-D29,
# D31, D32 are reached only from *inside* the workbook branch itself, which is
# wired by `workbook.register_workbook_path` (via `register_workbook_topology`,
# called after `register_unit_repair_topology` returns) rather than by any
# table `_validate_topology` reads -- so they are declared deferred here for
# the same reason D18-D23 are.
DEFERRED_TOPOLOGY: Mapping[str, str] = {
    "D18_PLAN_TARGETED_UNIT_REPAIR": "N31_REPAIR_ACCEPTANCE",
    "D19_ROUTE_UNIT_REPAIR": "N31_REPAIR_ACCEPTANCE",
    "D20_ADMIT_UNIT_REPAIR": "N31_REPAIR_ACCEPTANCE",
    "D21_RETEST_REQUIRED_DESCENDANTS": "N31_REPAIR_ACCEPTANCE",
    "D22_ACCEPT_UNIT": "N31_REPAIR_ACCEPTANCE",
    "D23_CHECKPOINT_ACCEPTED_UNIT": "N31_REPAIR_ACCEPTANCE",
    "M06_REPAIR_NAMED_UNIT_ARTIFACT": "N31_REPAIR_ACCEPTANCE",
    "D25_ASSEMBLE_WORKBOOK": "N32_WORKBOOK_TERMINALS",
    "D26_RENDER_INVENTORY_INSPECT_WORKBOOK": "N32_WORKBOOK_TERMINALS",
    "D27_FREEZE_WORKBOOK_REVIEW_PACKET": "N32_WORKBOOK_TERMINALS",
    "D28_REDUCE_WORKBOOK_EVIDENCE": "N32_WORKBOOK_TERMINALS",
    "D29_CLASSIFY_AND_PLAN_WORKBOOK_REPAIR": "N32_WORKBOOK_TERMINALS",
    "D31_ADMIT_AND_RETEST_WORKBOOK_REPAIR": "N32_WORKBOOK_TERMINALS",
    "D32_RECOMPUTE_FINAL_RELEASE": "N32_WORKBOOK_TERMINALS",
    "M07_REVIEW_ACTUAL_WORKBOOK": "N32_WORKBOOK_TERMINALS",
    "M08_REPAIR_NAMED_WORKBOOK_DEFECT": "N32_WORKBOOK_TERMINALS",
}

SKELETON_NORMAL_EDGES: tuple[tuple[str, str], ...] = (
    (START, "D00_BOOTSTRAP_EPISODE"),
    ("D96_GRACEFUL_INTERRUPT_GATE", "D98_WRITE_TERMINAL"),
    ("D98_WRITE_TERMINAL", END),
)

SKELETON_BRANCHES: tuple[tuple[str, Callable[[Mapping[str, Any]], str]], ...] = (
    ("D00_BOOTSTRAP_EPISODE", routing.route_bootstrap),
    ("D01_VALIDATE_AND_FREEZE_INPUTS", routing.route_frozen_inputs),
    ("D02_COMPILE_EFFECTIVE_RUN", routing.route_effective_run),
    ("D00R_REVALIDATE_RESUME_IDENTITY", routing.route_resume_identity),
    ("D03_PROVE_CAPABILITIES", routing.route_capabilities),
    ("D04_INITIALIZE_OR_RESUME", routing.route_initialize_or_resume),
)


# --------------------------------------------------------------- runtime context


def _utc_clock() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_runtime_context(
    *,
    engine_root: Path | str,
    output_root: Path | str,
    run_id: str,
    curriculum_digest: str,
    authorization: Any = None,
    capability_proof: Mapping[str, Any] | None = None,
    retrieval_hosts: Sequence[str] = (),
    clock: Callable[[], Any] = _utc_clock,
    env_passthrough: Sequence[str] = (),
) -> RuntimeContext:
    """Open the services one invocation may reach (spec section 5.2).

    Constructed by the CLI after `prepare_episode_invocation` has fixed the run
    identity, and supplied to `invoke(context=...)`; it is deliberately not built
    inside the builder, because the transport and the authorization it enforces
    are bound to a run identity that does not exist at build time.
    """

    engine_root = Path(engine_root).resolve()
    output_root = Path(output_root).resolve()
    receipts = ReceiptLog(output_root / ".evidence" / "egress_receipts.jsonl")
    egress_guard = EgressGuard(receipts)
    return RuntimeContext(
        engine_root=engine_root,
        output_root=output_root,
        path_guard=ArtifactStore(output_root),
        evidence_service=EvidenceStore(output_root),
        transport_registry=tp.CliTransport(
            output_root=output_root,
            run_id=run_id,
            curriculum_digest=curriculum_digest,
            authorization=authorization,
            receipts=receipts,
            guard=egress_guard,
            ledger=tp.AttemptLedger(),
            capability_proof=capability_proof,
            env_passthrough=env_passthrough,
        ),
        source_retriever=SourceRetriever(
            guard=egress_guard,
            policy=RetrievalPolicy(allowed_hosts=frozenset(retrieval_hosts)),
        ),
        signal_token=InterruptToken(output_root),
        clock=clock,
    )


# ----------------------------------------------------------------- node boundary


def _mark_interrupt(update: Mapping[str, Any], node_id: str) -> dict[str, Any]:
    """Record a graceful signal on the guard record so routing stays pure."""

    marked = dict(update)
    guard = marked.get("pending_guard")
    guard = dict(guard) if isinstance(guard, Mapping) else {"node": node_id, "value": None}
    guard["interrupt_requested"] = True
    marked["pending_guard"] = guard
    return marked


def _boundary(node_id: str, body: Callable[..., Any], *, model_node: bool) -> Callable[..., Any]:
    """Wrap one node body in the common boundary of spec section 6.1.

    LangGraph injects `Runtime`, not the opened services, so the boundary is also
    the only place the `RuntimeContext` reaches a node body — N22's and N23's
    callables take it as an explicit argument precisely so they cannot fetch it
    themselves.
    """

    def node(state: Mapping[str, Any], runtime: Runtime[RuntimeContext]) -> dict[str, Any]:
        context = getattr(runtime, "context", None)
        try:
            if model_node:
                update = body(state, build_model_node_context(context))
            else:
                update = body(state, context)
        except GraphBubbleUp:
            # LangGraph's own control flow (interrupt/resume propagation) is not a
            # product failure and must reach the engine untouched.
            raise
        except Exception as error:  # the classified-failure contract of spec 6.1
            # A terminal_candidate is built here, not left for some later node to
            # supply: `_failure_destination` routes straight to D98_WRITE_TERMINAL
            # the moment `pending_failure` is truthy, with no dynamic-guard hop
            # through a classifier in between (unlike a model node's failure,
            # which D91 gets to classify first). Without one, D98's own
            # independent revalidation (nodes/terminal.py) always rejects a bare
            # `None` candidate as "not a JSON object" -- discarding the real
            # `error` message into an uninformative generic rejection. Shape
            # matches every other SYSTEM_FAILURE writer (model_nodes.py D91,
            # repair.py D17/D18, workbook.py D29) exactly: D98's validator is one
            # shared, independent re-derivation, not a per-writer contract.
            failure_state = state if isinstance(state, Mapping) else {}
            artifact_heads = failure_state.get("artifact_heads") or {}
            return {
                "pending_failure": {
                    "node": node_id,
                    "class": "system",
                    "cause": "unhandled",
                    "message": f"{type(error).__name__}: {error}",
                    "evidence": {"boundary": "node"},
                },
                "pending_guard": None,
                "terminal_candidate": {
                    "kind": "SYSTEM_FAILURE",
                    "failure": {"class": "system", "cause": "unhandled"},
                    "node": node_id,
                    "safe_heads": {
                        stream: head.get("hash")
                        for stream, head in sorted(artifact_heads.items())
                        if isinstance(head, dict)
                    },
                    "audit_high_water_mark": len(failure_state.get("evidence_index_entries") or []),
                },
            }
        token = getattr(context, "signal_token", None)
        if token is not None and bool(getattr(token, "is_set", lambda: False)()):
            return _mark_interrupt(update, node_id)
        return dict(update)

    node.__name__ = node_id
    node.__qualname__ = node_id
    node.__doc__ = getattr(body, "__doc__", None)
    node.plan26_binding = _binding_record(node_id, body)  # type: ignore[attr-defined]
    return node


def _underlying(body: Callable[..., Any]) -> Callable[..., Any]:
    """The authored function behind a decorated node, for identity and audit."""

    return getattr(body, "node_body", body)


def _binding_record(node_id: str, body: Callable[..., Any]) -> dict[str, Any]:
    target = _underlying(body)
    try:
        source = inspect.getsource(target)
    except (OSError, TypeError):  # pragma: no cover - a source-less callable is rejected
        source = ""
    return {
        "node_id": node_id,
        "module": getattr(target, "__module__", ""),
        "qualname": getattr(target, "__qualname__", ""),
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "source_lines": len(source.splitlines()),
    }


# ------------------------------------------------------------ binding validation


def binding_inventory() -> dict[str, Callable[..., Any]]:
    """Every node callable N20's own skeleton/unit-path tables resolve against.

    N31's unit-repair-cycle nodes (D16-D23) carry no `NODE_CATALOGUE` row and
    are deliberately absent from *this* function's return value even though
    they are real, wired members of the compiled production graph: several of
    N30's own tests in `test_plan26_unit_graph.py` independently recompute
    their expectation directly from this function's return value, so it stays
    exactly what it was before N31 (per N90 finding F1's own resolution --
    `full_binding_inventory()`/`unit_repair_binding_inventory()` below are the
    functions that widen it; this one never does). Use `unit_repair_binding_
    inventory()` for the actual widened set `build_curriculum_factory_graph`
    compiles against.

    N32's workbook engine (D24-D32, `workbook.WORKBOOK_NODE_BODIES`) is
    likewise absent from *this* function deliberately, not by oversight: D24
    is `D05_SELECT_NEXT_UNIT`'s own `manifest_exhausted` destination, and
    `unit_graph.DEFERRED_EDGES`/`unit_graph.UNIT_BRANCHES` (N30's frozen,
    already-verified tables) declare that edge deferred to N32 by name. If D24
    entered this function, `unit_graph.register_unit_path`'s *own*
    `available`-derived destination set for `D05_SELECT_NEXT_UNIT` would
    silently widen to include it -- correct for a production run, but it
    would falsify N30's own already-passing topology tests, which independently
    recompute their expectation from this exact function's return value.
    `register_workbook_topology` registers the workbook engine as an additive
    step over its own separate builder (N32 exercises it directly, not through
    `build_curriculum_factory_graph`), so the unit path's registered edges stay
    byte-identical to what they were before N32 and the workbook branch is
    still fully real -- just not reachable from `D05` in this generation,
    exactly as `unit_graph.DEFERRED_EDGES` documents.
    """

    bindings: dict[str, Callable[..., Any]] = dict(node_registry())
    for job_id, adapter in MODEL_NODE_ADAPTERS.items():
        bindings[job_id] = adapter
    bindings.update(MODEL_BOOKKEEPING_NODES)
    return bindings


def unit_repair_binding_inventory() -> dict[str, Callable[..., Any]]:
    """`binding_inventory()` plus this node's own D16-D23 unit-repair-cycle bodies.

    The set `build_curriculum_factory_graph` actually compiles the one
    production graph against (N90 finding F1): D16-D23 become real, reachable
    members of that graph, while D24-D32 (N32's still-deferred workbook
    engine) stay absent, exactly as `binding_inventory()`'s own docstring
    documents for that pair. Kept separate from `binding_inventory()` itself
    so N30's tests, which recompute their expectation directly from that
    function's return value, stay unaffected by this widening.
    """

    bindings = dict(binding_inventory())
    bindings.update(acceptance.UNIT_REPAIR_NODE_BODIES)
    return bindings


def full_binding_inventory() -> dict[str, Callable[..., Any]]:
    """`unit_repair_binding_inventory()` plus N32's workbook engine (D24-D32).

    The complete node set this generation's node bodies span. Kept separate
    from `binding_inventory()` itself for the reason documented there.
    """

    bindings = dict(unit_repair_binding_inventory())
    bindings.update(workbook.WORKBOOK_NODE_BODIES)
    return bindings


def _reject(code: str, node_id: str, detail: str) -> None:
    raise GraphBindingError(f"{code}:{node_id}: {detail}")


def validate_bindings(
    bindings: Mapping[str, Callable[..., Any]],
    *,
    required: Sequence[str],
) -> dict[str, dict[str, Any]]:
    """Reject a missing, placeholder, test-only, duplicate, or unusable binding."""

    for node_id in required:
        if node_id not in bindings:
            _reject("N20-BIND-MISSING", node_id, "no production callable is registered")

    seen: dict[tuple[str, str], str] = {}
    inventory: dict[str, dict[str, Any]] = {}
    for node_id in sorted(bindings):
        body = bindings[node_id]
        if not callable(body):
            _reject("N20-BIND-UNCALLABLE", node_id, f"binding is {type(body).__name__}")
        record = _binding_record(node_id, body)
        module = record["module"]
        if not any(
            module == allowed or module.startswith(f"{allowed}.")
            for allowed in PRODUCTION_BINDING_MODULES
        ):
            _reject("N20-BIND-PLACEHOLDER", node_id, f"module {module!r} is not a production node module")
        lowered = f"{module}.{record['qualname']}".lower()
        # Whole-word match, not substring: `D31_ADMIT_AND_RETEST_...` legitimately
        # contains "test" inside "retest", and a placeholder heuristic that
        # rejected every real "retest"/"latest"/"contest" binding would be a false
        # positive on the spec's own vocabulary, not a caught stand-in.
        marker = next(
            (m for m in PLACEHOLDER_NAME_MARKERS if re.search(rf"(?<![a-z]){re.escape(m)}(?![a-z])", lowered)),
            None,
        )
        if marker is not None:
            _reject("N20-BIND-PLACEHOLDER", node_id, f"binding name declares {marker!r}")
        if not record["source_sha256"] or record["source_lines"] == 0:
            _reject("N20-BIND-PLACEHOLDER", node_id, "binding has no readable source")
        source = inspect.getsource(_underlying(body))
        marker = next((m for m in PLACEHOLDER_SOURCE_MARKERS if m in source), None)
        if marker is not None:
            _reject("N20-BIND-PLACEHOLDER", node_id, f"binding body declares {marker!r}")
        identity = (module, record["qualname"])
        if identity in seen:
            _reject(
                "N20-BIND-DUPLICATE",
                node_id,
                f"shares callable {module}.{record['qualname']} with {seen[identity]}",
            )
        seen[identity] = node_id
        inventory[node_id] = record
    return inventory


def _validate_topology(registered: Sequence[str]) -> None:
    known = set(registered) | {START, END}
    wired: set[str] = set()
    for source, target in SKELETON_NORMAL_EDGES:
        for endpoint in (source, target):
            if endpoint not in known:
                _reject("N20-EDGE-DANGLING", endpoint, f"edge {source} -> {target} names an unregistered node")
        wired.update({source, target})
    for source, path in SKELETON_BRANCHES:
        if source not in known:
            _reject("N20-EDGE-DANGLING", source, "conditional edge source is not registered")
        wired.add(source)
        for target in routing.guard_destinations(source):
            if target not in known:
                _reject(
                    "N20-EDGE-DANGLING",
                    target,
                    f"{source} branch {path.__name__} names an unregistered destination",
                )
            wired.add(target)
    for source, target in unit_graph.UNIT_NORMAL_EDGES:
        wired.update({source, target})
    for source, _ in unit_graph.UNIT_BRANCHES:
        wired.add(source)
        wired.update(unit_graph.branch_destinations(source, registered))
    for node_id in registered:
        if node_id in wired:
            continue
        owner = DEFERRED_TOPOLOGY.get(node_id)
        if owner is None:
            _reject(
                "N20-NODE-UNDECLARED",
                node_id,
                "is registered but neither wired by the skeleton nor declared deferred",
            )


# ---------------------------------------------------------------- registration


def register_skeleton(
    builder: StateGraph,
    bindings: Mapping[str, Callable[..., Any]],
) -> dict[str, dict[str, Any]]:
    """Register every available node and the fixed skeleton edges.

    N30 and N32 extend the same builder by adding their own `add_node`-free
    `add_edge`/`add_conditional_edges` calls after this returns; nothing here is
    rewritten by them, so the skeleton stays the one place START, the recovery
    branch, and the single edge to END are decided.
    """

    routing.assert_guard_table_total(NODE_CATALOGUE)
    inventory = validate_bindings(bindings, required=_skeleton_required_nodes())
    _validate_topology(sorted(bindings))

    for node_id in sorted(bindings):
        model_node = node_id in MODEL_NODE_ADAPTERS
        builder.add_node(node_id, _boundary(node_id, bindings[node_id], model_node=model_node))

    for source, target in SKELETON_NORMAL_EDGES:
        builder.add_edge(source, target)

    for source, path in SKELETON_BRANCHES:
        destinations = routing.guard_destinations(source)
        builder.add_conditional_edges(source, path, {target: target for target in destinations})

    unit_graph.register_unit_path(builder, sorted(bindings))

    return inventory


def register_unit_repair_topology(builder: StateGraph, available: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Wire D16-D23's internal repair/acceptance cycle, additively over `register_skeleton`.

    Called from `build_curriculum_factory_graph` immediately after `register_
    skeleton` (which has already `add_node`-registered every member of
    `unit_repair_binding_inventory()`, D16-D23 included) and after `unit_graph
    .register_unit_path` (run inside `register_skeleton` itself). This closes
    N90 finding F1 for the six DEFERRED_EDGES rows N31 owns: those six edges
    are not added here -- they are `unit_graph.py`'s own rows, and resolve
    automatically the moment D16/D17 are members of the bindings `register_
    skeleton` receives -- this function adds only the loop internal to D16-D23
    itself, which no other module owns.
    """

    return acceptance.register_unit_repair_path(builder, available)


def register_workbook_topology(builder: StateGraph) -> dict[str, tuple[str, ...]]:
    """Register D24-D32 and wire the workbook branch, additively over `register_skeleton`.

    Not called by `build_curriculum_factory_graph`: this generation's single
    compile point is the N20-owned skeleton/unit-path catalogue only (spec
    section 8's D00-D23/M01-M06/D90/D91), and `binding_inventory()`'s own
    docstring documents why D24-D32 must stay absent from it. N32 owns wiring
    this function into whatever the production compile point becomes once the
    workbook branch is in scope; until then it is exercised directly, over its
    own builder, the way N32's own topology test already does.
    `register_skeleton` itself must never see these bindings; this function
    adds exactly the nodes `register_skeleton` did not, then wires them over
    the *full* merged node set so `workbook.register_workbook_path` can
    resolve `D90`/`D91`/`D98`/M07/M08 as real, already-registered targets.
    """

    workbook_bindings = dict(workbook.WORKBOOK_NODE_BODIES)
    validate_bindings(workbook_bindings, required=tuple(workbook_bindings))
    for node_id in sorted(workbook_bindings):
        if node_id in builder.nodes:
            # `build_curriculum_factory_graph` now compiles against `full_
            # binding_inventory()`, so `register_skeleton` has already added
            # these nodes; only N32's own direct-builder topology test still
            # calls this function before any `add_node` for D24-D32 exists.
            continue
        builder.add_node(node_id, _boundary(node_id, workbook_bindings[node_id], model_node=False))
    return workbook.register_workbook_path(builder, sorted(full_binding_inventory()))


def _skeleton_required_nodes() -> tuple[str, ...]:
    required = {source for source, _ in SKELETON_BRANCHES}
    for source, target in SKELETON_NORMAL_EDGES:
        required.update({source, target})
    for source, _ in SKELETON_BRANCHES:
        required.update(routing.guard_destinations(source))
    return tuple(sorted(required - {START, END}))


def build_curriculum_factory_graph(
    *, engine_root: Path, output_root: Path
) -> CompiledStateGraph:
    """Build and compile the one production graph (spec section 4).

    Compiles exactly once, over the output-root `SqliteSaver` N21 opens. The
    returned graph is invoked with `context=build_runtime_context(...)`; no
    services are captured at build time, so the compiled object carries no
    run identity and no authorization.

    Compiles against `full_binding_inventory()`, not `binding_inventory()` or
    `unit_repair_binding_inventory()`: D16-D23 (N31's unit repair/acceptance
    cycle) and D24-D32 (N32's workbook engine) are both real, wired members of
    the one compiled production graph (N90 findings F1 and F2). `register_
    unit_repair_topology` is called immediately after `register_skeleton` to
    wire the loop internal to D16-D23 that no other module owns; `register_
    workbook_topology` is called immediately after that to wire D24-D32's own
    internal loop additively over the same builder. Once D24-D32's bodies are
    members of the bindings `register_skeleton` passes to `unit_graph
    .register_unit_path`, the `(D05_SELECT_NEXT_UNIT, manifest_exhausted) ->
    D24_PROVE_EXACT_MANIFEST_COVERAGE` row in `unit_graph.DEFERRED_EDGES`
    resolves automatically, the same way N31's six rows did.
    """

    engine_root = Path(engine_root).resolve()
    output_root = Path(output_root).resolve()
    builder: StateGraph = StateGraph(
        FactoryState,
        context_schema=RuntimeContext,
        input_schema=FactoryInput,
        output_schema=FactoryOutput,
    )
    bindings = full_binding_inventory()
    register_skeleton(builder, bindings)
    register_unit_repair_topology(builder, sorted(bindings))
    register_workbook_topology(builder)
    saver, _connection = open_checkpoint_saver(output_root)
    return builder.compile(checkpointer=saver, name=GRAPH_NAME)


# ---------------------------------------------------------------------- digest


def _canonical_digest(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def compiled_topology(compiled: CompiledStateGraph) -> dict[str, Any]:
    """The node/edge structure of an actually compiled graph, not a declared one."""

    drawn = compiled.get_graph()
    return {
        "name": compiled.name,
        "nodes": sorted(drawn.nodes),
        "edges": sorted(
            [edge.source, edge.target, bool(edge.conditional)] for edge in drawn.edges
        ),
    }


def contract_digests() -> dict[str, str]:
    """File digests of every frozen model prompt and output schema.

    Folded into the graph digest so prompt or schema drift is visible as graph
    drift: the same topology over a changed prompt is not the same graph.
    """

    digests: dict[str, str] = {}
    registry = tp.load_job_registry()
    for job_id in sorted(registry):
        route = registry[job_id]
        for path in (tp.resolve_prompt_path(route), tp.resolve_schema_path(route)):
            path = Path(path)
            digests[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def graph_digest(compiled: CompiledStateGraph) -> str:
    """Canonical-JSON digest over topology, bindings, state schema, and contracts.

    Identical real bindings give an identical digest; a changed node body,
    reducer declaration, prompt, or schema changes it. Python object identity is
    deliberately not an input, so two builds in one process and two builds in two
    processes agree.
    """

    payload = {
        "topology": compiled_topology(compiled),
        "bindings": [
            _binding_record(node_id, body)
            for node_id, body in sorted(binding_inventory().items())
        ],
        "state": {
            "fields": [[field, FIELD_REDUCER_CLASSES[field]] for field in FACTORY_STATE_FIELDS],
            "input": list(FACTORY_INPUT_FIELDS),
            "output": list(FACTORY_OUTPUT_FIELDS),
        },
        "contracts": contract_digests(),
    }
    return _canonical_digest(payload)
````

</details>
