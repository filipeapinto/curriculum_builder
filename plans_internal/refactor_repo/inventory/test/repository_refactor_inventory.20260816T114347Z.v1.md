# Repository refactor inventory — human report

- inventory_version: `1.0`
- schema: `schemas/repository_refactor_inventory.schema.v1.json`
- generated_at_utc: `2026-08-16T11:43:47Z`
- repository_commit: `21f8c2755044a73c7bac91f15f591c80ede97d15`
- dirty: `True` (25 changed path(s))
- tool_versions: `{'python': '3.13.1', 'git': 'git version 2.48.1'}`
- command: `python3 tools/refactor_repo/inventory.py --repo-root <repo-root> --output-dir <output-dir>`
- complete: `True`

## Identities (spec v8 section 2)

| identity | current value(s) | target |
|---|---|---|
| Product name | Curriculum Builder | Curriculum Factory |
| Repository slug | curriculum_builder | curriculum_factory |
| Python distribution | (none found) | curriculum-factory |
| Python package | runtime | curriculum_factory |
| Source root | runtime/ | src/curriculum_factory/ |

## Directories

| path | tracked_state | lifecycle_class | disposition |
|---|---|---|---|
| .claude/ | tracked | repository_contract | Retain at repository root; out of the src/ production-code migration in spec v8 section 4, which onl |
| .github/ | tracked | repository_contract | Retain; .github/workflows/plan26-lock-drift.yml is a named direct CI reference spec v8 section 4 req |
| curricula/ | tracked | domain_input | Retain outside src/ (spec v8 section 4 explicitly keeps curricula/ outside src/); no P00 action. |
| docs/ | tracked | active_documentation | Retain outside src/ (spec v8 section 4); no P00 action. |
| failed_execution_evidence/ | tracked | retained_evidence | Retain as audit trail; these files document prior execution attempts and are useful for post-mortem  |
| governance/ | tracked | active_documentation | Retain; governance/governance.v3.html is the live document, governance/deprecated/ already holds sup |
| issues/ | tracked | active_documentation | Retain; issues/001..007 plus issues/README.md are the open defect register. |
| meta_prompt/ | tracked | repository_contract | Retain outside src/ (spec v8 section 4); no P00 action. |
| plans/ | mixed | active_documentation | Retain; large tracked tree (1947 tracked paths at collection time) including nested frozen QA/result |
| plans_internal/ | mixed | active_documentation | Retain; hosts this prompt, its schemas/checkpoints/execution log, and the QA gate session directorie |
| policy/ | tracked | repository_contract | Retain outside src/ (spec v8 section 4 explicitly keeps policy/ outside src/); no P00 action. |
| requirements/ | tracked | repository_contract | Retain; pinned dependency declaration (plan26.in) and hash-locked resolution (plan26.lock) consumed  |
| research/ | tracked | retained_evidence | Retain; SOTA/state-of-the-art scan evidence, including this refactor's own research/repository_refac |
| runtime/ | mixed | production_source | Move beneath src/curriculum_factory/ in the source-move phase (spec v8 section 4); out of scope for  |
| schemas/ | tracked | repository_contract | Retain outside src/ (spec v8 section 4); $id values under the https://example.invalid/curriculum_bui |
| tests/ | mixed | test_fixture | Coarse top-level classification only; the enum in schemas/repository_refactor_inventory.schema.v1.js |
| tools/ | untracked | repository_contract | Retain as refactor-support tooling outside src/curriculum_factory/; it is meta-tooling for this refa |

## Python surface

- runtime_imports: 163
- runtime_module_commands: 26
- entry_points: 4
- file_based_root_traversals: 95
- absolute_checkout_paths: 0

## Old identity references

- Product name: 9 occurrence(s)
- Python package: 399 occurrence(s)
- Repository slug: 84 occurrence(s)
- Source root: 1146 occurrence(s)

## Structured configuration

- pyproject.toml: present=False — Build backend, distribution metadata, package discovery (spec v8 section 4).
- setup.py: present=False — Legacy setuptools entry point.
- setup.cfg: present=False — Legacy setuptools configuration.
- MANIFEST.in: present=False — sdist inclusion rules.
- tox.ini: present=False — Multi-environment test runner configuration.
- pytest.ini: present=False — pytest discovery/configuration.
- conftest.py: present=False — pytest fixtures/collection hooks (not present at repo root).
- .pre-commit-config.yaml: present=False — Pre-commit hook configuration.
- requirements/plan26.in: present=True — Declared (unpinned) Plan 26 dependency set.
- requirements/plan26.lock: present=True — Hash-pinned resolved dependency set, verified in CI.
- .github/workflows/plan26-lock-drift.yml: present=True — CI: regenerates and diffs the dependency lock.

## outputs/ children: 0

outputs/ does not exist in this checkout at collection time (gitignored runtime write boundary; empty between runs).

## Test subtrees

- tests/fixtures/: no __init__.py — Shared accept/reject data fixtures consumed by tests/gates and tests/runtime.
- tests/gates/: no __init__.py — Repository quality-gate harness (FR-P* families: structure, retention, selector, calibration, policy schemas, engine, manifest, unit, verifier) run via tests/run_gates.sh, not pytest-collected directly.
- tests/refactor_repo/: no __init__.py — pytest suite for tools/refactor_repo/ (this P00 inventory tool itself), created by this prompt.
- tests/results/: no __init__.py — Generated per-run gate-result JSON (gitignored beyond a tracked .gitkeep); not durable evidence.
- tests/runtime/: importable (__init__.py present) — pytest unit/contract/adversarial tests for the runtime/ package, including the Plan 26/27 LangGraph curriculum factory test modules.
- tests/selftest/: no __init__.py — Currently empty except a tracked .gitkeep placeholder.

## Schema identifiers: 26 schema file(s)

## Environment

- python_version: 3.13.1
- platform: macOS-26.5.2-arm64-arm-64bit-Mach-O
- installed_packages: 60

## Stable item identifier appendix (machine-comparable)

Every row below is mechanically derived from the same `compute_stable_ids()` function applied to the JSON report generated in the same run; a comparison script must find the identical set of ids in both reports (test 4).

```
config:.github/workflows/plan26-lock-drift.yml	present
config:.pre-commit-config.yaml	absent
config:MANIFEST.in	absent
config:conftest.py	absent
config:pyproject.toml	absent
config:pytest.ini	absent
config:requirements/plan26.in	present
config:requirements/plan26.lock	present
config:setup.cfg	absent
config:setup.py	absent
config:tox.ini	absent
directory:.claude/	Retain at repository root; out of the src/ production-code migration in spec v8 section 4, which only moves the Python production package.
directory:.github/	Retain; .github/workflows/plan26-lock-drift.yml is a named direct CI reference spec v8 section 4 requires updating if tests/ moves.
directory:curricula/	Retain outside src/ (spec v8 section 4 explicitly keeps curricula/ outside src/); no P00 action.
directory:docs/	Retain outside src/ (spec v8 section 4); no P00 action.
directory:failed_execution_evidence/	Retain as audit trail; these files document prior execution attempts and are useful for post-mortem analysis. No live code or production functionality depends on them. May be archived or purged after successful P00 completion and sign-off.
directory:governance/	Retain; governance/governance.v3.html is the live document, governance/deprecated/ already holds superseded versions.
directory:issues/	Retain; issues/001..007 plus issues/README.md are the open defect register.
directory:meta_prompt/	Retain outside src/ (spec v8 section 4); no P00 action.
directory:plans/	Retain; large tracked tree (1947 tracked paths at collection time) including nested frozen QA/results evidence from prior, unrelated remediation plans; out of scope for this refactor's identity/source moves.
directory:plans_internal/	Retain; hosts this prompt, its schemas/checkpoints/execution log, and the QA gate session directories the qa-gate-codex-run skill writes.
directory:policy/	Retain outside src/ (spec v8 section 4 explicitly keeps policy/ outside src/); no P00 action.
directory:requirements/	Retain; pinned dependency declaration (plan26.in) and hash-locked resolution (plan26.lock) consumed directly by name in CI.
directory:research/	Retain; SOTA/state-of-the-art scan evidence, including this refactor's own research/repository_refactoring/repository_refactoring.sota.v1.md.
directory:runtime/	Move beneath src/curriculum_factory/ in the source-move phase (spec v8 section 4); out of scope for P00, which is read-only.
directory:schemas/	Retain outside src/ (spec v8 section 4); $id values under the https://example.invalid/curriculum_builder/ namespace are versioned contract identifiers per spec v8 section 3, not branding text — do not rewrite in place.
directory:tests/	Coarse top-level classification only; the enum in schemas/repository_refactor_inventory.schema.v1.json has no distinct 'test code' category, so the whole tree maps to test_fixture here while test_subtrees carries the real per-subdirectory decision spec v8 section 4's 'Test-tree decision' requires.
directory:tools/	Retain as refactor-support tooling outside src/curriculum_factory/; it is meta-tooling for this refactor, not shipped product source. Re-evaluate at the clean-room release phase whether it stays repo-only dev tooling or is retired once the refactor completes.
entrypoint:runtime/capability_cycle.py:module_main_guard:python3 -m runtime.capability_cycle	python3 -m runtime.capability_cycle
entrypoint:runtime/finalize_evidence.py:module_main_guard:python3 -m runtime.finalize_evidence	python3 -m runtime.finalize_evidence
entrypoint:runtime/run_curriculum.py:module_main_guard:python3 -m runtime.run_curriculum	python3 -m runtime.run_curriculum
entrypoint:runtime/session_bridge.py:module_main_guard:python3 -m runtime.session_bridge	python3 -m runtime.session_bridge
identity:Product name	Curriculum Factory
identity:Python distribution	curriculum-factory
identity:Python package	curriculum_factory
identity:Repository slug	curriculum_factory
identity:Source root	src/curriculum_factory/
import:runtime/langgraph_factory/evidence.py:20	from runtime.langgraph_factory.artifacts import (     ArtifactStore,     canonical_digest,     canonical_json_bytes,     file_digest,     resolve_within, )
import:runtime/langgraph_factory/persistence.py:38	from runtime.langgraph_factory.artifacts import (     bytes_digest,     canonical_digest,     canonical_json_bytes,     file_digest,     resolve_within, )
import:runtime/run_curriculum.py:42	from runtime.langgraph_factory import persistence as P
import:runtime/run_curriculum.py:43	from runtime.langgraph_factory import transport as tp
import:runtime/run_curriculum.py:44	from runtime.langgraph_factory.artifacts import canonical_digest
import:runtime/run_curriculum.py:45	from runtime.langgraph_factory.egress import (     PROVIDER_DATA_CLASSES,     PROVIDERS,     AuthorizationRecord,     EgressGuard,     ReceiptLog,     RetrievalHostProfileError,     load_retrieval_host_profile, )
import:runtime/run_curriculum.py:54	from runtime.langgraph_factory.graph import build_curriculum_factory_graph, build_runtime_context
import:runtime/run_curriculum.py:55	from runtime.langgraph_factory.nodes.inputs import (     DRIVER_CAPABILITY_FIELDS,     MANDATORY_DRIVER_CLIS,     REQUIRED_CAPABILITIES,     _frozen_input_records,     _resolve_active_manifest, )
import:tests/gates/fr_p5_unit.py:44	from runtime.readability import (GateBindings, bind_gate, bloom_flags,  # noqa: E402                                  check_bloom_verbs, check_readability, grade_level,                                  readability_violations, syllables)
import:tests/runtime/test_acceptance_gate.py:107	from runtime.lesson_render import RendererError
import:tests/runtime/test_acceptance_gate.py:131	from runtime import pdf_inspect
import:tests/runtime/test_acceptance_gate.py:170	import runtime.visual_maps as visual_maps
import:tests/runtime/test_acceptance_gate.py:171	from runtime import pdf_inspect
import:tests/runtime/test_acceptance_gate.py:18	from runtime.checks import CheckFailure, required_checks_for
import:tests/runtime/test_acceptance_gate.py:19	from runtime.logger import LogError
import:tests/runtime/test_acceptance_gate.py:20	from runtime.session_bridge import finalize
import:tests/runtime/test_acceptance_gate.py:227	from runtime.lesson_render import derived_records
import:tests/runtime/test_capabilities.py:10	from runtime.gemini import max_effort_settings, resolve_alias
import:tests/runtime/test_capabilities.py:8	from runtime.capabilities import (CapabilityError, remove_unavailable_route,                                   route_required_by_unit, validate_cross_family_proof)
import:tests/runtime/test_checks.py:11	from runtime.checks import (CheckFailure, check_derivation, check_receipts, pdf_page_count,                             rasterize_and_check_nonblank)
import:tests/runtime/test_claim_entailment.py:15	from runtime.checks import CheckFailure, check_claim_entailment
import:tests/runtime/test_controller.py:10	from runtime.controller import CurriculumRuntime, RuntimeFailure
import:tests/runtime/test_controller.py:11	from runtime.io import BoundaryError, sha256_file
import:tests/runtime/test_controller.py:9	from runtime.checkpoint import CheckpointError
import:tests/runtime/test_curriculum_factory_graph.py:11	from runtime.factory_state import FactoryStateError, FactoryStateStore
import:tests/runtime/test_curriculum_factory_graph.py:12	from runtime.io import sha256_file
import:tests/runtime/test_curriculum_factory_graph.py:9	from runtime.curriculum_factory_graph import (CurriculumFactoryGraph, FactoryGraphFailure,                                               NODE_IDS, PROMPT_FILES)
import:tests/runtime/test_gemini.py:11	from runtime.gemini import (GeminiSettingsError, audit_stream_events, max_effort_settings,                             resolve_alias, write_run_local_settings)
import:tests/runtime/test_lesson_render.py:15	from runtime.lesson_render import (HANDLED_FIELDS, RendererError, domain_fact_lines,                                    derived_records, render_adult_verification,                                    render_elaborate, render_engage, render_evaluate,                                    render_explain, render_explore, render_identification,                                    render_recording_block, render_troubleshooting,                                    render_unit)
import:tests/runtime/test_lesson_render.py:186	from runtime.lesson_render import render_cognitive_load
import:tests/runtime/test_lesson_render.py:21	from runtime.session_bridge import _markdown
import:tests/runtime/test_lesson_render.py:338	from runtime.checks import check_derivation
import:tests/runtime/test_lesson_render.py:372	from runtime.checks import check_derivation
import:tests/runtime/test_logger.py:11	from runtime.logger import ExecutionLogger, LogError
import:tests/runtime/test_plan26_adversarial.py:52	import runtime.run_curriculum as RC
import:tests/runtime/test_plan26_adversarial.py:53	from runtime.langgraph_factory import acceptance, repair, workbook
import:tests/runtime/test_plan26_adversarial.py:54	from runtime.langgraph_factory import graph as G
import:tests/runtime/test_plan26_adversarial.py:55	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_adversarial.py:56	from runtime.langgraph_factory import persistence as P
import:tests/runtime/test_plan26_adversarial.py:57	from runtime.langgraph_factory import routing as R
import:tests/runtime/test_plan26_adversarial.py:58	from runtime.langgraph_factory import transport as tp
import:tests/runtime/test_plan26_adversarial.py:59	from runtime.langgraph_factory import unit_graph as U
import:tests/runtime/test_plan26_adversarial.py:60	from runtime.langgraph_factory.artifacts import ArtifactStore
import:tests/runtime/test_plan26_adversarial.py:61	from runtime.langgraph_factory.egress import (     AuthorizationDenied,     AuthorizationRecord,     EgressDenied,     EgressGuard,     ReceiptLog,     authorize_transmission, )
import:tests/runtime/test_plan26_adversarial.py:69	from runtime.langgraph_factory.evidence import EvidenceStore
import:tests/runtime/test_plan26_adversarial.py:70	from runtime.langgraph_factory.nodes import (     NODE_CATALOGUE,     SystemFailure,     canonical_digest,     domain,     inputs,     sources,     stream_id,     visuals, )
import:tests/runtime/test_plan26_adversarial.py:80	from runtime.langgraph_factory.nodes.content import CONTENT_CHECK_IDS
import:tests/runtime/test_plan26_adversarial.py:81	from runtime.langgraph_factory.nodes.domain import DOMAIN_CHECK_IDS
import:tests/runtime/test_plan26_adversarial.py:82	from runtime.langgraph_factory.state import FIELD_REDUCERS, RuntimeContext
import:tests/runtime/test_plan26_cli.py:40	from runtime.langgraph_factory import persistence as P
import:tests/runtime/test_plan26_cli.py:41	from runtime.langgraph_factory import transport as tp
import:tests/runtime/test_plan26_cli.py:43	import runtime.run_curriculum as R
import:tests/runtime/test_plan26_cli.py:518	from runtime.langgraph_factory.artifacts import canonical_digest
import:tests/runtime/test_plan26_deterministic_nodes.py:1975	from runtime.langgraph_factory.reducers import TerminalConflict, write_episode_terminal_once
import:tests/runtime/test_plan26_deterministic_nodes.py:20	from runtime.langgraph_factory import nodes as node_pkg
import:tests/runtime/test_plan26_deterministic_nodes.py:21	from runtime.langgraph_factory.nodes import (     NODE_CATALOGUE,     ConvergenceExhausted,     PrerequisitePause,     SystemFailure,     canonical_digest,     content,     domain,     inputs,     node_registry,     project,     render,     review,     sources,     terminal,     visuals, )
import:tests/runtime/test_plan26_deterministic_nodes.py:3188	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3214	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3280	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3326	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3429	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3474	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3481	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3567	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3780	from runtime.langgraph_factory.nodes import candidate_field
import:tests/runtime/test_plan26_deterministic_nodes.py:38	from runtime.langgraph_factory.state import FIELD_REDUCER_CLASSES
import:tests/runtime/test_plan26_deterministic_nodes.py:3888	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_deterministic_nodes.py:3889	from runtime.langgraph_factory.nodes import mint_version
import:tests/runtime/test_plan26_deterministic_nodes.py:39	from runtime.langgraph_factory.egress import (     EgressGuard,     ReceiptLog,     RetrievalPolicy,     RetrievalResponse,     SourceRetriever, )
import:tests/runtime/test_plan26_egress.py:16	from runtime.langgraph_factory.egress import (     MODEL_API_HOSTS,     PROVIDER_DATA_CLASSES,     PROVIDERS,     AuthorizationDenied,     AuthorizationRecord,     EgressDenied,     EgressGuard,     ReceiptLog,     RetrievalHostProfileError,     RetrievalPolicy,     RetrievalResponse,     SourceRetriever,     _default_opener,     authorize_subprocess_transmission,     authorize_transmission,     load_retrieval_host_profile, )
import:tests/runtime/test_plan26_egress.py:513	from runtime.langgraph_factory.egress import DEFAULT_RETRIEVAL_HOSTS_PATH
import:tests/runtime/test_plan26_evidence.py:12	from runtime.langgraph_factory.artifacts import (     AcceptedImmutable,     ArtifactConflict,     ArtifactStore,     ArtifactStream,     HeadAdvanceError,     PathEscape,     VersionRecord,     bytes_digest,     canonical_json_bytes,     file_digest, )
import:tests/runtime/test_plan26_evidence.py:24	from runtime.langgraph_factory.evidence import (     GENESIS_HASH,     LOG_NAMES,     EvidenceCorrupt,     EvidenceError,     EvidenceLog,     EvidenceStore,     audit_log_file, )
import:tests/runtime/test_plan26_model_nodes.py:12	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_model_nodes.py:13	from runtime.langgraph_factory import transport as tp
import:tests/runtime/test_plan26_model_nodes.py:14	from runtime.langgraph_factory.nodes import terminal as nt
import:tests/runtime/test_plan26_model_nodes.py:1485	from runtime.langgraph_factory.nodes import sources
import:tests/runtime/test_plan26_model_nodes.py:15	from runtime.langgraph_factory.reducers import (     DuplicateConflict,     HeadAdvanceError,     advance_head,     append_unique,     monotonic_max,     union_disjoint, )
import:tests/runtime/test_plan26_model_nodes.py:1543	from runtime.langgraph_factory import routing
import:tests/runtime/test_plan26_model_nodes.py:1555	from runtime.langgraph_factory import routing
import:tests/runtime/test_plan26_model_nodes.py:1570	from runtime.langgraph_factory import routing
import:tests/runtime/test_plan26_model_nodes.py:1586	from runtime.langgraph_factory import routing
import:tests/runtime/test_plan26_model_nodes.py:1606	from runtime.langgraph_factory import routing
import:tests/runtime/test_plan26_model_nodes.py:1632	from runtime.langgraph_factory import repair, routing
import:tests/runtime/test_plan26_model_nodes.py:1703	from runtime.langgraph_factory import graph as G
import:tests/runtime/test_plan26_model_nodes.py:1712	from runtime.langgraph_factory.state import FactoryState
import:tests/runtime/test_plan26_model_nodes.py:23	from runtime.langgraph_factory.state import (     FACTORY_STATE_FIELDS,     FIELD_REDUCER_CLASSES,     RuntimeContext, )
import:tests/runtime/test_plan26_persistence.py:1245	from runtime.langgraph_factory.state import FACTORY_STATE_FIELDS
import:tests/runtime/test_plan26_persistence.py:42	from runtime.langgraph_factory import persistence as P
import:tests/runtime/test_plan26_persistence.py:43	from runtime.langgraph_factory.evidence import EvidenceStore
import:tests/runtime/test_plan26_persistence.py:44	from runtime.langgraph_factory.nodes import project as project_for_node
import:tests/runtime/test_plan26_persistence.py:45	from runtime.langgraph_factory.nodes import terminal as D98
import:tests/runtime/test_plan26_persistence.py:46	from runtime.langgraph_factory.state import RuntimeContext
import:tests/runtime/test_plan26_repair_acceptance.py:31	from runtime.langgraph_factory import acceptance, repair
import:tests/runtime/test_plan26_repair_acceptance.py:32	from runtime.langgraph_factory import graph as G
import:tests/runtime/test_plan26_repair_acceptance.py:33	from runtime.langgraph_factory import unit_graph as U
import:tests/runtime/test_plan26_repair_acceptance.py:34	from runtime.langgraph_factory.nodes import terminal
import:tests/runtime/test_plan26_repair_acceptance.py:35	from runtime.langgraph_factory.nodes import domain as domain_nodes
import:tests/runtime/test_plan26_repair_acceptance.py:36	from runtime.langgraph_factory.nodes import content as content_nodes
import:tests/runtime/test_plan26_repair_acceptance.py:37	from runtime.langgraph_factory.nodes.domain import DOMAIN_CHECK_IDS
import:tests/runtime/test_plan26_repair_acceptance.py:38	from runtime.langgraph_factory.nodes.content import CONTENT_CHECK_IDS
import:tests/runtime/test_plan26_repair_acceptance.py:39	from runtime.langgraph_factory.nodes import SystemFailure, canonical_digest, stream_id
import:tests/runtime/test_plan26_repair_acceptance.py:40	from runtime.langgraph_factory.state import FIELD_REDUCERS
import:tests/runtime/test_plan26_repair_acceptance.py:41	from runtime.langgraph_factory import reducers as red
import:tests/runtime/test_plan26_repair_acceptance.py:837	from runtime.langgraph_factory.nodes import project
import:tests/runtime/test_plan26_state_reducers.py:12	from runtime.langgraph_factory import reducers as R
import:tests/runtime/test_plan26_state_reducers.py:13	from runtime.langgraph_factory.state import (     FACTORY_INPUT_FIELDS,     FACTORY_OUTPUT_FIELDS,     FACTORY_STATE_FIELDS,     FIELD_REDUCER_CLASSES,     FIELD_REDUCERS,     FORBIDDEN_RUNTIME_CONTEXT_FIELDS,     RUNTIME_CONTEXT_FIELDS,     FactoryInput,     FactoryOutput,     FactoryState,     RuntimeContext,     RuntimeContextViolation,     StateInventoryError,     reducer_for,     validate_state_inventory, )
import:tests/runtime/test_plan26_topology.py:49	from runtime.langgraph_factory import graph as G
import:tests/runtime/test_plan26_topology.py:50	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_topology.py:51	from runtime.langgraph_factory import routing as R
import:tests/runtime/test_plan26_topology.py:52	from runtime.langgraph_factory import transport as tp
import:tests/runtime/test_plan26_topology.py:53	from runtime.langgraph_factory.nodes import NODE_CATALOGUE, node_registry
import:tests/runtime/test_plan26_topology.py:54	from runtime.langgraph_factory.state import (     FACTORY_STATE_FIELDS,     FactoryInput,     FactoryOutput,     FactoryState,     RuntimeContext, )
import:tests/runtime/test_plan26_topology.py:949	from runtime.langgraph_factory.nodes import terminal as nt
import:tests/runtime/test_plan26_topology.py:987	from runtime.langgraph_factory import nodes as node_pkg
import:tests/runtime/test_plan26_topology.py:988	from runtime.langgraph_factory.nodes import terminal as nt2
import:tests/runtime/test_plan26_transport.py:1614	from runtime.langgraph_factory.nodes.inputs import REQUIRED_CAPABILITIES
import:tests/runtime/test_plan26_transport.py:18	from runtime.langgraph_factory import transport as tp
import:tests/runtime/test_plan26_transport.py:19	from runtime.langgraph_factory.artifacts import (     UNIT_SCOPE,     ArtifactStore,     ArtifactStream,     canonical_json_bytes, )
import:tests/runtime/test_plan26_transport.py:2036	from runtime.langgraph_factory.nodes.visuals import AUTHORITATIVE_VISUAL_KINDS
import:tests/runtime/test_plan26_transport.py:25	from runtime.langgraph_factory.egress import (     PROVIDER_DATA_CLASSES,     AuthorizationDenied,     AuthorizationRecord,     EgressGuard,     ReceiptLog, )
import:tests/runtime/test_plan26_unit_graph.py:1284	from runtime.langgraph_factory.reducers import UnionConflict, union_disjoint
import:tests/runtime/test_plan26_unit_graph.py:2800	from runtime.langgraph_factory.artifacts import ArtifactStore, ArtifactStream, UNIT_SCOPE
import:tests/runtime/test_plan26_unit_graph.py:413	from runtime.langgraph_factory.artifacts import ArtifactStore
import:tests/runtime/test_plan26_unit_graph.py:414	from runtime.langgraph_factory.evidence import EvidenceStore
import:tests/runtime/test_plan26_unit_graph.py:58	from runtime.langgraph_factory import graph as G
import:tests/runtime/test_plan26_unit_graph.py:59	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_unit_graph.py:60	from runtime.langgraph_factory import persistence as P
import:tests/runtime/test_plan26_unit_graph.py:61	from runtime.langgraph_factory import routing as R
import:tests/runtime/test_plan26_unit_graph.py:62	from runtime.langgraph_factory import unit_graph as U
import:tests/runtime/test_plan26_unit_graph.py:63	from runtime.langgraph_factory.nodes import (     NODE_CATALOGUE,     canonical_digest,     domain,     inputs,     render,     review,     sources,     visuals, )
import:tests/runtime/test_plan26_unit_graph.py:73	from runtime.langgraph_factory.reducers import WriteOnceConflict, write_once
import:tests/runtime/test_plan26_unit_graph.py:74	from runtime.langgraph_factory.state import (     FACTORY_STATE_FIELDS,     FIELD_REDUCER_CLASSES,     FactoryState, )
import:tests/runtime/test_plan26_workbook.py:1010	from runtime.langgraph_factory.artifacts import ArtifactStore
import:tests/runtime/test_plan26_workbook.py:1011	from runtime.langgraph_factory.evidence import EvidenceStore
import:tests/runtime/test_plan26_workbook.py:32	from runtime.langgraph_factory import graph as G
import:tests/runtime/test_plan26_workbook.py:33	from runtime.langgraph_factory import model_nodes as mn
import:tests/runtime/test_plan26_workbook.py:34	from runtime.langgraph_factory import routing as R
import:tests/runtime/test_plan26_workbook.py:35	from runtime.langgraph_factory import unit_graph as U
import:tests/runtime/test_plan26_workbook.py:36	from runtime.langgraph_factory import workbook
import:tests/runtime/test_plan26_workbook.py:37	from runtime.langgraph_factory.nodes import SystemFailure, canonical_digest, stream_id, terminal
import:tests/runtime/test_plan26_workbook.py:38	from runtime.langgraph_factory.state import FIELD_REDUCERS
import:tests/runtime/test_plan26_workbook.py:543	from runtime.langgraph_factory.nodes import project
import:tests/runtime/test_plan26_workbook.py:775	from runtime.langgraph_factory.state import FactoryInput, FactoryOutput, FactoryState, RuntimeContext
import:tests/runtime/test_plan27_adversarial.py:109	from runtime.langgraph_factory import graph as G
import:tests/runtime/test_plan27_adversarial.py:20	from runtime.langgraph_factory import transport as tp
import:tests/runtime/test_retry.py:3	from runtime.retry import RetryLimit, RetryTracker
import:tests/runtime/test_routing.py:6	from runtime.routing import RoutingError, Selector
import:tests/runtime/test_run_curriculum.py:10	from runtime.controller import CurriculumRuntime
import:tests/runtime/test_run_curriculum.py:11	from runtime.langgraph_factory import egress as eg
import:tests/runtime/test_run_curriculum.py:12	from runtime.langgraph_factory import transport as tp
import:tests/runtime/test_run_curriculum.py:13	import runtime.run_curriculum as run_curriculum_module
import:tests/runtime/test_run_curriculum.py:14	import runtime.run_curriculum as R
import:tests/runtime/test_run_curriculum.py:45	from runtime.run_curriculum import parser_for
import:tests/runtime/test_run_state.py:15	from runtime import run_state, workbook
import:tests/runtime/test_run_state.py:16	from runtime.run_state import RunStateError
import:tests/runtime/test_run_state.py:168	from runtime.session_bridge import finalize
import:tests/runtime/test_run_state.py:17	from runtime.workbook import WorkbookError
import:tests/runtime/test_visual_maps.py:15	from runtime.visual_maps import (VisualMapError, classify_role, load_photo_regions,                                  match_photo_subject, regenerate_assets, render_breadboard,                                  render_enumeration, render_evidence_card, render_map,                                  render_parts_diagram, render_power_path, render_same_wire)
import:tests/runtime/test_visual_maps.py:206	from runtime.session_bridge import finalize
import:tests/runtime/unit_fixture.py:14	from runtime.io import atomic_json, sha256_file
import:tests/runtime/unit_fixture.py:15	from runtime.logger import ExecutionLogger
import:tests/runtime/unit_fixture.py:16	from runtime.visual_maps import regenerate_assets
modcmd:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:35	python3 -m runtime.run_curriculum
modcmd:plans/25_curriculum_factory_graph/qa_criteria.v1.md:159	python3 -m runtime.run_curriculum
modcmd:plans/25_curriculum_factory_graph/run_curriculum_factory.prompt.v1.md:50	python3 -m runtime.run_curriculum
modcmd:plans/25_curriculum_factory_graph/run_curriculum_factory.prompt.v1.md:59	python3 -m runtime.run_curriculum
modcmd:plans/25_curriculum_factory_graph/run_curriculum_factory.prompt.v1.md:68	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md:83	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/prompts/N40_cli_cutover.prompt.v1.md:3	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:720	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:724	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:731	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:739	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:747	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1475	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1479	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1486	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1494	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1502	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1592	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1596	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1603	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1611	python3 -m runtime.run_curriculum
modcmd:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1619	python3 -m runtime.run_curriculum
modcmd:plans/28_runtime_operations_docs/plans.log.md:32	python3 -m runtime.run_curriculum
modcmd:plans/28_runtime_operations_docs/qa/execution_test.plan.v1.md:112	python3 -m runtime.run_curriculum
modcmd:runtime/run_curriculum.py:2	python3 -m runtime.run_curriculum
modcmd:runtime/run_curriculum.py:65	python3 -m runtime.run_curriculum
oldref:.claude/skills/electronics-circuit-visualization/evals/evals.json:42:Repository slug	curriculum_builder
oldref:.claude/skills/electronics-circuit-visualization/evals/evals.json:44:Repository slug	curriculum_builder
oldref:.claude/skills/electronics-circuit-visualization/evals/evals.json:7:Repository slug	curriculum_builder
oldref:.claude/skills/electronics-circuit-visualization/evals/evals.json:9:Repository slug	curriculum_builder
oldref:.claude/skills/learning-agent-create/SKILL.md:6:Repository slug	curriculum_builder
oldref:.claude/skills/learning-agent-create/references/repo_conventions.md:1:Repository slug	curriculum_builder
oldref:.claude/skills/plan-create/evals/evals.json:22:Source root	runtime/controller.py
oldref:.claude/skills/plan-create/evals/evals.json:23:Source root	runtime/controller.py
oldref:.claude/skills/plan-create/evals/evals.json:39:Source root	runtime/checks.py
oldref:.claude/skills/plan-create/evals/evals.json:6:Source root	runtime/retry.py
oldref:.claude/skills/plan-create/evals/evals.json:7:Source root	runtime/retry.py
oldref:curricula/arduino_kit/checks.v1.yaml:136:Source root	runtime/session_bridge.py
oldref:curricula/arduino_kit/checks.v1.yaml:95:Source root	runtime/session_bridge.py
oldref:curricula/arduino_kit/domain.schema.v1.json:3:Repository slug	curriculum_builder
oldref:curricula/arduino_kit/manifest.domain.schema.v1.json:3:Repository slug	curriculum_builder
oldref:docs/images/prompts/curriculum_pipeline_infographic.v2.prompt.md:8:Repository slug	curriculum_builder
oldref:governance/governance.v3.html:235:Python package	runtime.logger
oldref:governance/governance.v3.html:268:Python package	runtime.logger.ExecutionLogger
oldref:governance/governance.v3.html:398:Python package	runtime.logger.ExecutionLogger
oldref:governance/governance.v3.html:5:Repository slug	curriculum_builder
oldref:governance/governance.v3.html:92:Repository slug	curriculum_builder
oldref:issues/001-renderer-emits-raw-json.md:18:Source root	runtime/session_bridge.py
oldref:issues/002-acceptance-bypasses-quality-gates.md:10:Source root	runtime/session_bridge.py
oldref:issues/002-acceptance-bypasses-quality-gates.md:11:Source root	runtime/session_bridge.py
oldref:issues/002-acceptance-bypasses-quality-gates.md:12:Source root	runtime/session_bridge.py
oldref:issues/002-acceptance-bypasses-quality-gates.md:9:Source root	runtime/session_bridge.py
oldref:issues/003-visual-pipeline-breaks-the-curriculum-contract.md:15:Source root	runtime/session_bridge.py
oldref:issues/003-visual-pipeline-breaks-the-curriculum-contract.md:9:Source root	runtime/session_bridge.py
oldref:issues/006-source-receipts-do-not-prove-claims.md:10:Source root	runtime/session_bridge.py
oldref:issues/006-source-receipts-do-not-prove-claims.md:9:Source root	runtime/checks.py
oldref:plans/03_folder_refactoring/folder_refactoring.plan.v6.md:145:Repository slug	curriculum_builder
oldref:plans/04_fix_meta_prompt/fix_meta_prompt.plan.v1.md:105:Repository slug	curriculum_builder
oldref:plans/04_fix_meta_prompt/fix_meta_prompt.plan.v1.md:86:Repository slug	curriculum_builder
oldref:plans/05_simplification/prompt/implement_curriculum_runtime.prompt.v1.md:102:Source root	runtime/run_curriculum.py
oldref:plans/05_simplification/prompt/implement_curriculum_runtime.prompt.v2.md:114:Source root	runtime/run_curriculum.py
oldref:plans/05_simplification/prompt/implement_curriculum_runtime.prompt.v3.md:172:Source root	runtime/run_curriculum.py
oldref:plans/05_simplification/prompt/implement_curriculum_runtime.prompt.v4.md:182:Source root	runtime/run_curriculum.py
oldref:plans/05_simplification/prompt/implement_curriculum_runtime.prompt.v5.md:191:Source root	runtime/run_curriculum.py
oldref:plans/05_simplification/prompt/implement_curriculum_runtime.prompt.v6.md:193:Source root	runtime/run_curriculum.py
oldref:plans/05_simplification/prompt/implement_curriculum_runtime.prompt.v6.md:74:Source root	runtime/io.py
oldref:plans/05_simplification/prompt/migrate_external_run_evidence.prompt.v1.md:129:Source root	runtime/io.py
oldref:plans/05_simplification/prompt/migrate_external_run_evidence.prompt.v1.md:39:Source root	runtime/io.py
oldref:plans/05_simplification/prompt/migrate_external_run_evidence.prompt.v1.md:5:Source root	runtime/io.py
oldref:plans/05_simplification/prompt/migrate_external_run_evidence.prompt.v2.md:148:Source root	runtime/io.py
oldref:plans/05_simplification/prompt/migrate_external_run_evidence.prompt.v2.md:21:Source root	runtime/io.py
oldref:plans/05_simplification/prompt/migrate_external_run_evidence.prompt.v2.md:30:Source root	runtime/controller.py
oldref:plans/05_simplification/prompt/migrate_external_run_evidence.prompt.v2.md:58:Source root	runtime/io.py
oldref:plans/05_simplification/simplification.handoff.v1.md:269:Repository slug	curriculum_builder
oldref:plans/05_simplification/simplification.handoff.v1.md:39:Repository slug	curriculum_builder
oldref:plans/05_simplification/simplification.handoff.v1.md:40:Repository slug	curriculum_builder
oldref:plans/05_simplification/simplification.handoff.v1.md:4:Repository slug	curriculum_builder
oldref:plans/06_schema_retirement/prompt/schema_retirement.prompt.v1.md:3:Repository slug	curriculum_builder
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:103:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:104:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:105:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:150:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:151:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:160:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:161:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:253:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:269:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:270:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:272:Source root	runtime/checkpoint.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:273:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:278:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:306:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:307:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:3:Repository slug	curriculum_builder
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v1.md:43:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:127:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:128:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:129:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:131:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:30:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:3:Repository slug	curriculum_builder
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:65:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:67:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/prompts/remove_time_limits.prompt.v2.md:87:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v1.md:106:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v1.md:121:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v1.md:124:Source root	runtime/checkpoint.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v1.md:154:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v1.md:173:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v1.md:174:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v1.md:176:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v1.md:73:Python package	runtime.run_curriculum.parser_for
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v2.md:106:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v2.md:39:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v2.md:65:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v2.md:74:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v3.md:67:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v3.md:83:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/qa/plan_qa.contracts.v3.md:84:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/qa/plan_qa.tests.v1.md:35:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/qa/plan_qa.tests.v1.md:36:Source root	runtime/controller.py
oldref:plans/09_remove_time_limits/qa/plan_qa.tests.v1.md:58:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/qa/plan_qa.tests.v1.md:69:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/qa/plan_qa.tests.v2.md:70:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:111:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:147:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:170:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:171:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:173:Source root	runtime/checkpoint.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:174:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:179:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:195:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:196:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:27:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:59:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:60:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:61:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:91:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v1.md:92:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v2.md:48:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v2.md:81:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/remove_time_limits.plan.v2.md:83:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v1.md:10:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v1.md:122:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v1.md:124:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v1.md:29:Source root	runtime/run_curriculum.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v1.md:67:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v2.md:100:Source root	runtime/session_bridge.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v2.md:101:Source root	runtime/capability_cycle.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v2.md:115:Source root	runtime/finalize_evidence.py
oldref:plans/09_remove_time_limits/remove_time_limits.result.v2.md:26:Source root	runtime/run_curriculum.py
oldref:plans/10_sota_agents_pipeline/prompt/phase1_sota_research.prompt.v1.md:4:Repository slug	curriculum_builder
oldref:plans/10_sota_agents_pipeline/prompt/phase1_sota_research.prompt.v2.md:4:Repository slug	curriculum_builder
oldref:plans/10_sota_agents_pipeline/prompt/phase2_skill_creation.prompt.v1.md:3:Repository slug	curriculum_builder
oldref:plans/10_sota_agents_pipeline/prompt/phase4_skill_creation.prompt.v1.md:3:Repository slug	curriculum_builder
oldref:plans/10_sota_agents_pipeline/prompt/phase4_skill_creation.prompt.v1.md:42:Source root	runtime/controller.py
oldref:plans/10_sota_agents_pipeline/prompt/phase4_skill_creation.prompt.v1.md:43:Source root	runtime/gemini.py
oldref:plans/10_sota_agents_pipeline/sota_agents_pipeline.plan.v1.md:30:Repository slug	curriculum_builder
oldref:plans/10_sota_agents_pipeline/sota_agents_pipeline.plan.v2.md:38:Repository slug	curriculum_builder
oldref:plans/11_provider_correction/provider_correction.plan.v1.md:65:Source root	runtime/controller.py
oldref:plans/11_provider_correction/provider_correction.plan.v1.md:76:Source root	runtime/capabilities.py
oldref:plans/11_provider_correction/provider_correction.plan.v1.md:79:Source root	runtime/capability_cycle.py
oldref:plans/11_provider_correction/provider_correction.plan.v1.md:82:Source root	runtime/session_bridge.py
oldref:plans/11_provider_correction/provider_correction.plan.v1.md:91:Source root	runtime/finalize_evidence.py
oldref:plans/11_provider_correction/provider_correction.plan.v1.md:92:Source root	runtime/run_curriculum.py
oldref:plans/11_provider_correction/qa/execution_test.plan.v1.md:63:Source root	runtime/run_curriculum.py
oldref:plans/11_provider_correction/qa/plan_qa.v1.md:55:Source root	runtime/session_bridge.py
oldref:plans/11_provider_correction/qa/plan_qa.v1.md:56:Source root	runtime/finalize_evidence.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:137:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:18:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:228:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:236:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:254:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:277:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:282:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:301:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:34:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:43:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:56:Source root	runtime/run_curriculum.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:57:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:66:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:75:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/_eval_rtd_ws.plan.v1.md:7:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/plans.log.md:26:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/plans.log.md:44:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/plans.log.md:54:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/plans.log.md:56:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/plans.log.md:74:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/plans.log.md:92:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/plans.log.md:9:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/prompts/_eval_rtd_ws.prompt.v1.md:112:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/prompts/_eval_rtd_ws.prompt.v1.md:14:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/prompts/_eval_rtd_ws.prompt.v1.md:26:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/prompts/_eval_rtd_ws.prompt.v1.md:7:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/prompts/_eval_rtd_ws.prompt.v1.md:86:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/prompts/_eval_rtd_ws.prompt.v1.md:88:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:100:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:113:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:13:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:191:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:198:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:220:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:22:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:267:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:30:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:51:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:61:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:77:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/execution_test.plan.v1.md:85:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/final_audit.v1.md:15:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/final_audit.v1.md:63:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/final_audit.v1.md:73:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/final_audit.v1.md:74:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/final_audit.v1.md:82:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/final_audit.v1.md:83:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v1.md:11:Repository slug	curriculum_builder
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v1.md:19:Repository slug	curriculum_builder
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v1.md:19:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v1.md:21:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v1.md:23:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v1.md:35:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v1.md:36:Repository slug	curriculum_builder
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v1.md:5:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:11:Repository slug	curriculum_builder
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:14:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:20:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:21:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:25:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:29:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:38:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:44:Repository slug	curriculum_builder
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v2.md:5:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v3.md:102:Source root	runtime/controller.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v3.md:12:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v3.md:14:Source root	runtime/controller.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v3.md:15:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v3.md:28:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v3.md:7:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:10:Repository slug	curriculum_builder
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:15:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:19:Repository slug	curriculum_builder
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:25:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:27:Source root	runtime/session_bridge.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:29:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:38:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:52:Source root	runtime/retry.py
oldref:plans/12__eval_rtd_ws/qa/plan_qa.v4.md:9:Repository slug	curriculum_builder
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:108:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:136:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:141:Python package	runtime.prompt
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:158:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:159:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:163:Python package	runtime.controller.__file__
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:191:Python package	runtime.prompt
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:210:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:224:Source root	runtime/run_curriculum.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:22:Source root	runtime/session_bridge.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:23:Python package	runtime.prompt
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:242:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:258:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:26:Source root	runtime/session_bridge.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:270:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:33:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:44:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:7:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/_eval_mps_ws.plan.v1.md:93:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/plans.log.md:24:Source root	runtime/session_bridge.py
oldref:plans/13__eval_mps_ws/plans.log.md:26:Python package	runtime.prompt
oldref:plans/13__eval_mps_ws/plans.log.md:30:Python package	runtime.controller.__file__.
oldref:plans/13__eval_mps_ws/plans.log.md:44:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/plans.log.md:9:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:100:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:101:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:129:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:145:Source root	runtime/session_bridge.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:17:Source root	runtime/finalize_evidence.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:19:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:22:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:43:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:53:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:6:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:76:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:79:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:82:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:94:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v1.md:95:Repository slug	curriculum_builder
oldref:plans/13__eval_mps_ws/qa/plan_qa.v2.md:114:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v2.md:119:Python package	runtime.controller.__file__
oldref:plans/13__eval_mps_ws/qa/plan_qa.v2.md:125:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v2.md:126:Repository slug	curriculum_builder
oldref:plans/13__eval_mps_ws/qa/plan_qa.v2.md:159:Source root	runtime/run_curriculum.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v2.md:160:Source root	runtime/io.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v2.md:6:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v2.md:96:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:102:Source root	runtime/run_curriculum.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:112:Source root	runtime/run_curriculum.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:132:Source root	runtime/run_curriculum.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:169:Python package	runtime.controller.__file__
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:223:Source root	runtime/controller.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:233:Source root	runtime/session_bridge.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:235:Source root	runtime/session_bridge.py
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:236:Python package	runtime.prompt
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:37:Repository slug	curriculum_builder
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:66:Python package	runtime.controller.__file__
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:70:Python package	runtime.controller
oldref:plans/13__eval_mps_ws/qa/plan_qa.v3.md:76:Source root	runtime/finalize_evidence.py
oldref:plans/14__eval_rtd_bl/plans.log.md:11:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/plans.log.md:28:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/plans.log.md:32:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/plans.log.md:34:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/plans.log.md:35:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/plans.log.md:38:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/plans.log.md:48:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/plans.log.md:8:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:14:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:26:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:30:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:37:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:46:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:47:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:52:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:64:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:68:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/prompts/retry_scope.prompt.v1.md:6:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/qa/execution_test.plan.v1.md:102:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/qa/execution_test.plan.v1.md:15:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/qa/execution_test.plan.v1.md:28:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/qa/execution_test.plan.v1.md:35:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/qa/execution_test.plan.v1.md:45:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/qa/execution_test.plan.v1.md:56:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/qa/final_audit.v1.md:21:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/qa/final_audit.v1.md:22:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/qa/final_audit.v1.md:25:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/qa/final_audit.v1.md:50:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:16:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:18:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:24:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:37:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:53:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:54:Python package	runtime.limit_policy
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:56:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:73:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/qa/plan_qa.v1.md:96:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:127:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:136:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:152:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:181:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:201:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:23:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:30:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:46:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:52:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:57:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:62:Source root	runtime/run_curriculum.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:63:Python package	runtime.limit_policy
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:64:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:68:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:7:Source root	runtime/retry.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:83:Source root	runtime/controller.py
oldref:plans/14__eval_rtd_bl/retry_scope.plan.v1.md:84:Source root	runtime/run_curriculum.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:106:Python package	runtime.controller.CurriculumRuntime
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:114:Python package	runtime.controller
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:116:Python package	runtime.controller
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:116:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:121:Python package	runtime.controller
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:124:Python package	runtime.resolve_prompt
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:126:Python package	runtime.prompt
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:182:Source root	runtime/run_curriculum.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:208:Source root	runtime/session_bridge.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:22:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:25:Source root	runtime/session_bridge.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:26:Python package	runtime.prompt
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:54:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:70:Source root	runtime/finalize_evidence.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:75:Source root	runtime/session_bridge.py
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:77:Python package	runtime.resolve_prompt
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:78:Python package	runtime.resolve_companions
oldref:plans/15__eval_mps_bl/meta_prompt_activation.plan.v1.md:7:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/plans.log.md:26:Source root	runtime/session_bridge.py
oldref:plans/15__eval_mps_bl/plans.log.md:28:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/plans.log.md:34:Source root	runtime/finalize_evidence.py
oldref:plans/15__eval_mps_bl/plans.log.md:9:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/prompts/meta_prompt_activation.prompt.v1.md:13:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/prompts/meta_prompt_activation.prompt.v1.md:19:Python package	runtime.resolve_prompt
oldref:plans/15__eval_mps_bl/prompts/meta_prompt_activation.prompt.v1.md:19:Source root	runtime/session_bridge.py
oldref:plans/15__eval_mps_bl/prompts/meta_prompt_activation.prompt.v1.md:20:Python package	runtime.resolve_companions
oldref:plans/15__eval_mps_bl/prompts/meta_prompt_activation.prompt.v1.md:28:Python package	runtime.controller
oldref:plans/15__eval_mps_bl/prompts/meta_prompt_activation.prompt.v1.md:35:Python package	runtime.prompt
oldref:plans/15__eval_mps_bl/prompts/meta_prompt_activation.prompt.v1.md:6:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/qa/execution_test.plan.v1.md:107:Repository slug	curriculum_builder
oldref:plans/15__eval_mps_bl/qa/execution_test.plan.v1.md:132:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/qa/execution_test.plan.v1.md:166:Source root	runtime/session_bridge.py
oldref:plans/15__eval_mps_bl/qa/execution_test.plan.v1.md:26:Source root	runtime/run_curriculum.py
oldref:plans/15__eval_mps_bl/qa/execution_test.plan.v1.md:27:Source root	runtime/run_curriculum.py
oldref:plans/15__eval_mps_bl/qa/execution_test.plan.v1.md:46:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/qa/execution_test.plan.v1.md:49:Source root	runtime/run_curriculum.py
oldref:plans/15__eval_mps_bl/qa/execution_test.plan.v1.md:51:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/qa/final_audit.v1.md:29:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/qa/final_audit.v1.md:33:Python package	runtime.prompt
oldref:plans/15__eval_mps_bl/qa/final_audit.v1.md:33:Source root	runtime/session_bridge.py
oldref:plans/15__eval_mps_bl/qa/plan_qa.v1.md:106:Source root	runtime/finalize_evidence.py
oldref:plans/15__eval_mps_bl/qa/plan_qa.v1.md:23:Source root	runtime/controller.py
oldref:plans/15__eval_mps_bl/qa/plan_qa.v1.md:24:Python package	runtime.controller
oldref:plans/15__eval_mps_bl/qa/plan_qa.v1.md:26:Source root	runtime/finalize_evidence.py
oldref:plans/15__eval_mps_bl/qa/plan_qa.v1.md:64:Source root	runtime/finalize_evidence.py
oldref:plans/15__eval_mps_bl/qa/plan_qa.v1.md:6:Source root	runtime/controller.py
oldref:plans/16__eval_gf_ws/_eval_gf_ws.plan.v1.md:212:Source root	runtime/session_bridge.py
oldref:plans/16__eval_gf_ws/qa/plan_qa.v1.md:221:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/plans.log.md:162:Source root	runtime/workbook.py
oldref:plans/18_runtime_integrity_remediation/plans.log.md:163:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/plans.log.md:26:Source root	runtime/checkpoint.py
oldref:plans/18_runtime_integrity_remediation/plans.log.md:32:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/plans.log.md:33:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/plans.log.md:9:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/prompts/runtime_integrity_remediation.prompt.v1.md:8:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/execution_test.plan.v1.md:219:Source root	runtime/readability.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:118:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:14:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:60:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:63:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:72:Python package	runtime.resolve_companions
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:73:Python package	runtime.run_verifier_fixtures
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:74:Python package	runtime._logger_gate
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:74:Source root	runtime/run_curriculum.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:7:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:88:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v1.md:89:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v2.md:130:Source root	runtime/readability.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v2.md:132:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v2.md:156:Source root	runtime/readability.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v2.md:32:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v2.md:37:Source root	runtime/logger.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v2.md:46:Python package	runtime.session_bridge.finalize
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v2.md:6:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v2.md:96:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v3.md:114:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v3.md:40:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v4.md:35:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v5.md:26:Source root	runtime/visual_maps.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v5.md:86:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v6.md:35:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v8.md:59:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/qa/plan_qa.v8.md:69:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:10:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:19:Source root	runtime/controller.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:208:Source root	runtime/visual_maps.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:283:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:329:Source root	runtime/readability.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:331:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:338:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:346:Source root	runtime/pdf_inspect.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:373:Source root	runtime/logger.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:547:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:591:Source root	runtime/run_state.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:609:Source root	runtime/workbook.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:62:Source root	runtime/lesson_render.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:64:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:694:Source root	runtime/readability.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.plan.v1.md:757:Source root	runtime/readability.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:297:Source root	runtime/pdf_inspect.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:302:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:314:Source root	runtime/readability.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:315:Python package	runtime.readability
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:461:Source root	runtime/lesson_render.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:463:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:467:Source root	runtime/visual_maps.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:472:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:476:Source root	runtime/pdf_inspect.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:478:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:480:Source root	runtime/session_bridge.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:504:Source root	runtime/checks.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:509:Source root	runtime/run_state.py
oldref:plans/18_runtime_integrity_remediation/runtime_integrity_remediation.result.v1.md:510:Source root	runtime/workbook.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:130:Python package	runtime.capability_cycle
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:155:Python package	runtime.controller.CurriculumRuntime.validated_manifest
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:182:Source root	runtime/workbook.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:183:Python package	runtime.workbook.assemble
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:190:Source root	runtime/run_state.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:191:Source root	runtime/controller.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:35:Python package	-m runtime
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:40:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:41:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:44:Source root	runtime/controller.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:45:Source root	runtime/session_bridge.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:47:Source root	runtime/capability_cycle.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:48:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:58:Source root	runtime/run_state.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:77:Source root	runtime/workbook.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P0_baseline_contract_freeze.prompt.v1.md:96:Source root	runtime/session_bridge.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:128:Source root	runtime/capability_cycle.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:129:Python package	runtime.capabilities.validate_cross_family_proof
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:131:Python package	runtime.test_capabilities
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:132:Python package	runtime.test_gemini
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:143:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:14:Source root	runtime/capability_cycle.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:17:Source root	runtime/routing.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:42:Source root	runtime/routing.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:47:Python package	runtime.capabilities.remove_unavailable_route
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:68:Python package	runtime.io.atomic_json
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:69:Python package	runtime.io.require_internal_output
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:87:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P1_live_capability_routing_closure.prompt.v1.md:9:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md:100:Source root	runtime/worker.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md:101:Source root	runtime/checkpoint.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md:106:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md:107:Source root	runtime/run_state.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md:12:Source root	runtime/session_bridge.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md:163:Source root	runtime/worker.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md:172:Source root	runtime/worker.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P2_schema_bound_worker_execution.prompt.v1.md:173:Python package	runtime.run_state
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:109:Source root	runtime/session_bridge.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:198:Source root	runtime/checks.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:55:Source root	runtime/controller.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:60:Source root	runtime/session_bridge.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:67:Source root	runtime/checks.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:71:Source root	runtime/visual_maps.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:72:Source root	runtime/lesson_render.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:73:Source root	runtime/run_state.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:74:Source root	runtime/logger.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:75:Source root	runtime/io.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P3_production_unit_state_machine.prompt.v1.md:76:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:215:Source root	runtime/run_state.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:216:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:24:Source root	runtime/run_curriculum.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:26:Source root	runtime/controller.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P4_full_manifest_orchestration.prompt.v1.md:31:Source root	runtime/run_state.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:58:Source root	runtime/workbook.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:61:Python package	runtime.checks.rasterize_and_check_nonblank
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:64:Source root	runtime/run_state.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:70:Source root	runtime/checks.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:72:Source root	runtime/pdf_inspect.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:75:Source root	runtime/visual_maps.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:76:Source root	runtime/readability.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:77:Source root	runtime/logger.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:78:Source root	runtime/controller.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P5_workbook_release_loop.prompt.v1.md:79:Source root	runtime/session_bridge.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P6_release_proof_debt_reconciliation.prompt.v1.md:169:Source root	runtime/readability.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P6_release_proof_debt_reconciliation.prompt.v1.md:71:Source root	runtime/io.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P6_release_proof_debt_reconciliation.prompt.v1.md:73:Source root	runtime/run_state.py
oldref:plans/19_curriculum_factory_production_loop_closure/prompts/P6_release_proof_debt_reconciliation.prompt.v1.md:91:Source root	runtime/run_curriculum.py
oldref:plans/20_subscription_only_execution_model/plans.log.md:26:Source root	runtime/finalize_evidence.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v1.md:134:Source root	runtime/finalize_evidence.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v1.md:139:Source root	runtime/gemini.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v1.md:140:Source root	runtime/finalize_evidence.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v1.md:25:Source root	runtime/session_bridge.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v1.md:48:Source root	runtime/session_bridge.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v1.md:55:Source root	runtime/session_bridge.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v2.md:112:Source root	runtime/session_bridge.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v2.md:113:Source root	runtime/worker.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v3.md:35:Source root	runtime/session_bridge.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v3.md:8:Source root	runtime/capabilities.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v3.md:93:Source root	runtime/session_bridge.py
oldref:plans/20_subscription_only_execution_model/qa/plan_qa.v3.md:9:Source root	runtime/capability_cycle.py
oldref:plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md:120:Source root	runtime/gemini.py
oldref:plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md:180:Source root	runtime/codex_gate.py
oldref:plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md:193:Source root	runtime/finalize_evidence.py
oldref:plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md:22:Source root	runtime/session_bridge.py
oldref:plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md:26:Source root	runtime/gemini.py
oldref:plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md:270:Source root	runtime/session_bridge.py
oldref:plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md:307:Source root	runtime/codex_gate.py
oldref:plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml:243:Source root	runtime/prompt_graph.py
oldref:plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml:278:Source root	runtime/subscription_worker.py
oldref:plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml:310:Source root	runtime/graph_runtime.py
oldref:plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml:311:Source root	runtime/graph_checkpoint.py
oldref:plans/21_graph_engineered_subscription_execution/prompts/P6_end_to_end_release_and_supersession.prompt.v1.md:33:Source root	runtime/readability.py
oldref:plans/21_graph_engineered_subscription_execution/qa/graph_runtime.review.v1.md:124:Source root	runtime/capability_cycle.py
oldref:plans/21_graph_engineered_subscription_execution/qa/graph_runtime.review.v1.md:125:Source root	runtime/gemini.py
oldref:plans/21_graph_engineered_subscription_execution/qa/graph_runtime.review.v1.md:39:Source root	runtime/prompt_graph.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.review.v1.md:16:Source root	runtime/graph_runtime.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.review.v1.md:24:Source root	runtime/prompt_graph.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.review.v2.md:16:Source root	runtime/graph_runtime.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.review.v2.md:19:Source root	runtime/readability.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.review.v2.md:47:Source root	runtime/readability.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.review.v3.closure.md:45:Source root	runtime/run_state.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.review.v3.md:21:Source root	runtime/readability.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.review.v3.md:57:Source root	runtime/workbook.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.v2.review.v1.md:45:Source root	runtime/session_bridge.py
oldref:plans/21_graph_engineered_subscription_execution/qa/historical_regressions.v2.review.v1.md:73:Source root	runtime/readability.py
oldref:plans/21_graph_engineered_subscription_execution/qa/prompt_subscription.review.v1.md:109:Source root	runtime/prompt_graph.py
oldref:plans/21_graph_engineered_subscription_execution/tools/validate_plan.py:581:Python package	runtime.yaml
oldref:plans/24_graph_engineered_curriculum_factory/previous_plan.obs.v1.md:18:Source root	runtime/run_curriculum.py
oldref:plans/25_curriculum_factory_graph/curriculum_factory.graph.v1.md:54:Source root	runtime/checks.py
oldref:plans/25_curriculum_factory_graph/curriculum_factory.graph.v1.md:55:Source root	runtime/lesson_render.py
oldref:plans/25_curriculum_factory_graph/curriculum_factory.graph.v1.md:56:Source root	runtime/workbook.py
oldref:plans/25_curriculum_factory_graph/qa_criteria.v1.md:159:Python package	-m runtime
oldref:plans/25_curriculum_factory_graph/run_curriculum_factory.prompt.v1.md:50:Python package	-m runtime
oldref:plans/25_curriculum_factory_graph/run_curriculum_factory.prompt.v1.md:59:Python package	-m runtime
oldref:plans/25_curriculum_factory_graph/run_curriculum_factory.prompt.v1.md:68:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/contracts/erratum_checkpoint_ns_rename.v1.md:11:Source root	runtime/langgraph_factory/state.py
oldref:plans/26_langgraph_curriculum_factory/contracts/erratum_checkpoint_ns_rename.v1.md:52:Source root	runtime/langgraph_factory/state.py
oldref:plans/26_langgraph_curriculum_factory/contracts/erratum_checkpoint_ns_rename.v1.md:53:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/26_langgraph_curriculum_factory/contracts/erratum_checkpoint_ns_rename.v1.md:55:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md:65:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md:73:Source root	runtime/langgraph_factory/repair.py
oldref:plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md:76:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md:79:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md:96:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md:47:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md:81:Python package	runtime.langgraph_factory.graph.build_curriculum_factory_graph
oldref:plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md:82:Python package	runtime.langgraph_factory.persistence.prepare_episode_invocation
oldref:plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md:83:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:117:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:126:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:134:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:143:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:151:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:65:Source root	runtime/langgraph_factory/reducers.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:73:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:81:Source root	runtime/langgraph_factory/egress.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:90:Source root	runtime/langgraph_factory/routing.py
oldref:plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml:99:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N20-001.patch.v1.yaml:20:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N20-001.patch.v1.yaml:72:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N20-001.patch.v1.yaml:85:Source root	runtime/langgraph_factory/routing.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N30-001.patch.v1.yaml:79:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N31-001.patch.v1.yaml:19:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N31-001.patch.v1.yaml:30:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N31-001.patch.v1.yaml:59:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N31-001.patch.v1.yaml:96:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N32-001.patch.v1.yaml:28:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N32-001.patch.v1.yaml:74:Source root	runtime/langgraph_factory/repair.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N40-001.patch.v1.yaml:26:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/patches/P-N40-001.patch.v1.yaml:33:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/patches/P-N40-001.patch.v1.yaml:39:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N40-001.patch.v1.yaml:41:Python package	runtime.session_bridge
oldref:plans/26_langgraph_curriculum_factory/patches/P-N40-001.patch.v1.yaml:43:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N40-001.patch.v1.yaml:46:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/patches/P-N40-001.patch.v1.yaml:50:Python package	runtime.controller.CurriculumRuntime
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N20-001.instructions.md:4:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N20-001.instructions.md:65:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N20-001.instructions.md:80:Source root	runtime/langgraph_factory/routing.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N30-001.instructions.md:73:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N31-001.instructions.md:102:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N31-001.instructions.md:20:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N31-001.instructions.md:54:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N31-001.instructions.md:5:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N32-001.instructions.md:16:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N32-001.instructions.md:83:Source root	runtime/langgraph_factory/repair.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N40-001.instructions.md:13:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N40-001.instructions.md:20:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N40-001.instructions.md:29:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N40-001.instructions.md:31:Python package	runtime.session_bridge
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N40-001.instructions.md:33:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N40-001.instructions.md:38:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/patches/sources/P-N40-001.instructions.md:43:Python package	runtime.controller.CurriculumRuntime
oldref:plans/26_langgraph_curriculum_factory/post_morten/deprecatde/postmortem.v1.md:626:Source root	runtime/langgraph_factory/transport.py
oldref:plans/26_langgraph_curriculum_factory/post_morten/deprecatde/postmortem.v1.md:627:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/post_morten/deprecatde/postmortem.v1.md:628:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/post_morten/postmortem.v2.md:586:Source root	runtime/langgraph_factory/transport.py
oldref:plans/26_langgraph_curriculum_factory/post_morten/postmortem.v2.md:587:Source root	runtime/langgraph_factory/graph.py
oldref:plans/26_langgraph_curriculum_factory/post_morten/postmortem.v2.md:588:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/prompts/N22_deterministic_nodes.prompt.v3.md:5:Source root	runtime/langgraph_factory/nodes/terminal.py
oldref:plans/26_langgraph_curriculum_factory/prompts/N40_cli_cutover.prompt.v1.md:3:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/prompts/repair_v3_sonnet_launcher.prompt.v1.md:14:Repository slug	curriculum_builder
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:163:Python package	runtime.langgraph_factory.graph.build_curriculum_factory_graph
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:168:Python package	runtime.run_curriculum.main
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:170:Python package	runtime.langgraph_factory.persistence.prepare_episode_invocation
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:178:Source root	runtime/langgraph_factory/state.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:310:Source root	runtime/langgraph_factory/transport.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:65:Source root	runtime/curriculum_factory_graph.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:69:Source root	runtime/model_worker.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:720:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:724:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:731:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:739:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:73:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:747:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:815:Source root	runtime/io.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:824:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md:871:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1475:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1479:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1486:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1494:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1502:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1609:Source root	runtime/io.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1617:Source root	runtime/gemini.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1621:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:1701:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:176:Source root	runtime/model_worker.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:186:Source root	runtime/capability_cycle.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:187:Source root	runtime/gemini.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:271:Source root	runtime/curriculum_factory_graph.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:283:Source root	runtime/model_worker.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:294:Source root	runtime/factory_state.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:296:Source root	runtime/checkpoint.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:298:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:454:Python package	runtime.langgraph_factory.graph.build_curriculum_factory_graph
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:461:Python package	runtime.run_curriculum.main
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:473:Python package	runtime.langgraph_factory.persistence.prepare_episode_invocation
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:495:Source root	runtime/langgraph_factory/state.py
oldref:plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md:673:Source root	runtime/langgraph_factory/transport.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1592:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1596:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1603:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1611:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1619:Python package	-m runtime
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1730:Source root	runtime/io.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1742:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:1824:Python package	runtime.run_curriculum
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:209:Source root	runtime/model_worker.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:306:Source root	runtime/curriculum_factory_graph.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:318:Source root	runtime/model_worker.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:329:Source root	runtime/factory_state.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:331:Source root	runtime/checkpoint.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:333:Source root	runtime/run_curriculum.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:491:Python package	runtime.langgraph_factory.graph.build_curriculum_factory_graph
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:498:Python package	runtime.run_curriculum.main
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:510:Python package	runtime.langgraph_factory.persistence.prepare_episode_invocation
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:532:Source root	runtime/langgraph_factory/state.py
oldref:plans/26_langgraph_curriculum_factory/spec/v3/langgraph_curriculum_factory.spec.v4.md:711:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022810122960Z-8bb675f7/attempt_record.json:10:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022810122960Z-8bb675f7/attempt_record.json:11:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022810122960Z-8bb675f7/attempt_record.json:14:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022909403208Z-5ea27456/attempt_record.json:10:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022909403208Z-5ea27456/attempt_record.json:11:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022909403208Z-5ea27456/attempt_record.json:14:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/attempt_record.json:10:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/attempt_record.json:11:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/attempt_record.json:14:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/pending_merge.json:18:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/pending_merge.json:19:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/pending_merge.json:210:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/pending_merge.json:211:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/pending_merge.json:214:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/pending_merge.json:22:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/pending_merge.json:37:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T022956865584Z-1ca24f00/pending_merge.json:42:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/attempt_record.json:10:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/attempt_record.json:11:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/attempt_record.json:14:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:16:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:17:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:208:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:209:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:20:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:212:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:299:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:300:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:303:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:318:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:323:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:35:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:40:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:423:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:513:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:514:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T031853853822Z-2cdec2b8/pending_merge.json:517:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/attempt_record.json:10:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/attempt_record.json:11:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/attempt_record.json:9:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/pending_merge.json:17:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/pending_merge.json:18:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/pending_merge.json:19:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/pending_merge.json:211:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/pending_merge.json:212:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/pending_merge.json:213:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T023042001279Z-f3803dc9/pending_merge.json:29:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/attempt_record.json:10:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/attempt_record.json:11:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/attempt_record.json:9:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:15:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:16:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:17:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:209:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:210:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:211:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:27:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:300:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:301:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:302:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:312:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:514:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:515:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T031938524426Z-4720b776/pending_merge.json:516:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/attempt_record.json:10:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/attempt_record.json:11:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/attempt_record.json:12:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/attempt_record.json:13:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/attempt_record.json:14:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/attempt_record.json:8:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/attempt_record.json:9:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:16:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:17:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:18:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:193:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:194:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:195:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:196:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:197:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:198:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:199:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:19:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:20:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:21:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T023136472551Z-6812be1e/pending_merge.json:22:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/attempt_record.json:10:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/attempt_record.json:11:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/attempt_record.json:12:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/attempt_record.json:13:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/attempt_record.json:14:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/attempt_record.json:8:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/attempt_record.json:9:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:14:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:15:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:16:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:17:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:18:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:191:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:192:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:193:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:194:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:195:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:196:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:197:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:19:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:20:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:286:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:287:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:288:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:289:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:290:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:291:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:292:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:481:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:482:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:483:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:484:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:485:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:486:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T032028418526Z-fa03e404/pending_merge.json:487:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/attempt_record.json:10:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/attempt_record.json:11:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/attempt_record.json:9:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/pending_merge.json:17:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/pending_merge.json:18:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/pending_merge.json:19:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/pending_merge.json:202:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/pending_merge.json:203:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T023202144538Z-8c9b84fa/pending_merge.json:204:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/attempt_record.json:10:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/attempt_record.json:11:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/attempt_record.json:9:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:15:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:16:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:17:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:200:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:201:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:202:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:301:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:302:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:303:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:528:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:529:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T032054456196Z-d2ce3f53/pending_merge.json:530:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:12:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:136:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:13:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:16:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:226:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:227:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:230:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:31:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:36:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:11:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:12:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:13:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:225:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:226:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:227:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:23:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:10:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:11:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:12:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:13:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:14:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:15:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:16:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:205:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:206:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:207:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:208:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:209:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:210:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:211:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:11:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:12:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:13:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:238:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:239:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:240:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N20_PROVIDER_TRANSPORT/7ab7a8fc087eff4f616b965e2513a599e75dd1b27da0dd5b3f4ae92789ad990c.json:12:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N20_PROVIDER_TRANSPORT/7ab7a8fc087eff4f616b965e2513a599e75dd1b27da0dd5b3f4ae92789ad990c.json:13:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N20_PROVIDER_TRANSPORT/7ab7a8fc087eff4f616b965e2513a599e75dd1b27da0dd5b3f4ae92789ad990c.json:16:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N20_PROVIDER_TRANSPORT/7ab7a8fc087eff4f616b965e2513a599e75dd1b27da0dd5b3f4ae92789ad990c.json:204:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N20_PROVIDER_TRANSPORT/7ab7a8fc087eff4f616b965e2513a599e75dd1b27da0dd5b3f4ae92789ad990c.json:205:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N20_PROVIDER_TRANSPORT/7ab7a8fc087eff4f616b965e2513a599e75dd1b27da0dd5b3f4ae92789ad990c.json:208:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N20_PROVIDER_TRANSPORT/7ab7a8fc087eff4f616b965e2513a599e75dd1b27da0dd5b3f4ae92789ad990c.json:31:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N20_PROVIDER_TRANSPORT/7ab7a8fc087eff4f616b965e2513a599e75dd1b27da0dd5b3f4ae92789ad990c.json:36:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N30_PREFLIGHT_EGRESS/d1e4bac143ff38ea2c80308079746540a4e12fb51c5ab4ca78d38104051d0603.json:11:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N30_PREFLIGHT_EGRESS/d1e4bac143ff38ea2c80308079746540a4e12fb51c5ab4ca78d38104051d0603.json:12:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N30_PREFLIGHT_EGRESS/d1e4bac143ff38ea2c80308079746540a4e12fb51c5ab4ca78d38104051d0603.json:13:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N30_PREFLIGHT_EGRESS/d1e4bac143ff38ea2c80308079746540a4e12fb51c5ab4ca78d38104051d0603.json:205:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N30_PREFLIGHT_EGRESS/d1e4bac143ff38ea2c80308079746540a4e12fb51c5ab4ca78d38104051d0603.json:206:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N30_PREFLIGHT_EGRESS/d1e4bac143ff38ea2c80308079746540a4e12fb51c5ab4ca78d38104051d0603.json:207:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N30_PREFLIGHT_EGRESS/d1e4bac143ff38ea2c80308079746540a4e12fb51c5ab4ca78d38104051d0603.json:23:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:10:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:11:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:12:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:13:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:14:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:15:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:16:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:187:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:188:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:189:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:190:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:191:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:192:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N40_INTEGRATION_OWNERSHIP/c1711eb6ea247a70119749a033384f174dfe5933315046886598624f0a1acd0b.json:193:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N50_EVIDENCE_AUDIT_CONTROLS/718c5032e29ca7f2dc38f9ae2e1b330dc406f30f93b062048032ea1fbb58bd99.json:11:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N50_EVIDENCE_AUDIT_CONTROLS/718c5032e29ca7f2dc38f9ae2e1b330dc406f30f93b062048032ea1fbb58bd99.json:12:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N50_EVIDENCE_AUDIT_CONTROLS/718c5032e29ca7f2dc38f9ae2e1b330dc406f30f93b062048032ea1fbb58bd99.json:13:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N50_EVIDENCE_AUDIT_CONTROLS/718c5032e29ca7f2dc38f9ae2e1b330dc406f30f93b062048032ea1fbb58bd99.json:196:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N50_EVIDENCE_AUDIT_CONTROLS/718c5032e29ca7f2dc38f9ae2e1b330dc406f30f93b062048032ea1fbb58bd99.json:197:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state/receipts/history/N50_EVIDENCE_AUDIT_CONTROLS/718c5032e29ca7f2dc38f9ae2e1b330dc406f30f93b062048032ea1fbb58bd99.json:198:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T101521764947Z-0c6137e6/attempt_record.json:10:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T101521764947Z-0c6137e6/attempt_record.json:11:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T101521764947Z-0c6137e6/attempt_record.json:15:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/attempt_record.json:10:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/attempt_record.json:11:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/attempt_record.json:15:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/pending_merge.json:103:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/pending_merge.json:18:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/pending_merge.json:19:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/pending_merge.json:23:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/pending_merge.json:98:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N20_PROVIDER_TRANSPORT/N20_PROVIDER_TRANSPORT-2026-08-15T102004834223Z-4230e27d/pending_merge.json:99:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/attempt_record.json:10:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/attempt_record.json:11:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/attempt_record.json:9:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/pending_merge.json:101:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/pending_merge.json:102:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/pending_merge.json:103:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/pending_merge.json:17:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/pending_merge.json:18:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N30_PREFLIGHT_EGRESS/N30_PREFLIGHT_EGRESS-2026-08-15T102305809197Z-9b0aa969/pending_merge.json:19:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:10:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:11:Source root	runtime/langgraph_factory/nodes/content.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:12:Source root	runtime/langgraph_factory/nodes/domain.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:13:Source root	runtime/langgraph_factory/nodes/visuals.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:14:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:15:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:16:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:17:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:8:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/attempt_record.json:9:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:108:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:109:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:110:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:111:Source root	runtime/langgraph_factory/nodes/content.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:112:Source root	runtime/langgraph_factory/nodes/domain.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:113:Source root	runtime/langgraph_factory/nodes/visuals.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:114:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:115:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:116:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:117:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:16:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:17:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:18:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:19:Source root	runtime/langgraph_factory/nodes/content.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:20:Source root	runtime/langgraph_factory/nodes/domain.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:21:Source root	runtime/langgraph_factory/nodes/visuals.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:22:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:23:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:24:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N40_INTEGRATION_OWNERSHIP/N40_INTEGRATION_OWNERSHIP-2026-08-15T102538472167Z-8d0a32f1/pending_merge.json:25:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/attempt_record.json:10:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/attempt_record.json:11:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/attempt_record.json:9:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/pending_merge.json:138:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/pending_merge.json:139:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/pending_merge.json:140:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/pending_merge.json:17:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/pending_merge.json:18:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N50_EVIDENCE_AUDIT_CONTROLS/N50_EVIDENCE_AUDIT_CONTROLS-2026-08-15T102814091389Z-2b0827df/pending_merge.json:19:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N70_LIVE_UNIT_PROOF/N70_LIVE_UNIT_PROOF-2026-08-15T104735440447Z-481062ca/pending_merge.json:40:Python package	runtime.run_curriculum
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N70_LIVE_UNIT_PROOF/N70_LIVE_UNIT_PROOF-2026-08-15T104735440447Z-481062ca/pending_merge.json:57:Python package	runtime.run_curriculum
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/attempts/N80_LIVE_WORKBOOK_PROOF/N80_LIVE_WORKBOOK_PROOF-2026-08-15T104943214298Z-444444e5/pending_merge.json:40:Python package	runtime.run_curriculum
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:12:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:13:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:17:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:92:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:93:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N20_PROVIDER_TRANSPORT.receipt.v1.json:97:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:11:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:12:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:13:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:95:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:96:Source root	runtime/langgraph_factory/nodes/sources.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N30_PREFLIGHT_EGRESS.receipt.v1.json:97:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:102:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:103:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:104:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:105:Source root	runtime/langgraph_factory/nodes/content.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:106:Source root	runtime/langgraph_factory/nodes/domain.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:107:Source root	runtime/langgraph_factory/nodes/visuals.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:108:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:109:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:10:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:110:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:111:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:11:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:12:Source root	runtime/langgraph_factory/nodes/__init__.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:13:Source root	runtime/langgraph_factory/nodes/content.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:14:Source root	runtime/langgraph_factory/nodes/domain.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:15:Source root	runtime/langgraph_factory/nodes/visuals.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:16:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:17:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:18:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N40_INTEGRATION_OWNERSHIP.receipt.v1.json:19:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:11:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:12:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:132:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:133:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:134:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N50_EVIDENCE_AUDIT_CONTROLS.receipt.v1.json:13:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N70_LIVE_UNIT_PROOF.receipt.v1.json:34:Python package	runtime.run_curriculum
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N70_LIVE_UNIT_PROOF.receipt.v1.json:51:Python package	runtime.run_curriculum
oldref:plans/27_langgraph_curriculum_factory_remediation/.run27_state_v9/receipts/N80_LIVE_WORKBOOK_PROOF.receipt.v1.json:34:Python package	runtime.run_curriculum
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/evidence_determinism.v1.yaml:22:Python package	runtime.langgraph_factory.evidence
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/evidence_determinism.v1.yaml:34:Python package	runtime.langgraph_factory.evidence
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:16:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:17:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:18:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:19:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:20:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:21:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:22:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:23:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:24:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:25:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:26:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:27:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:38:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:39:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:40:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:41:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:42:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:43:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:44:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:45:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:46:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:47:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:48:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:51:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:52:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:53:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:54:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:55:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:56:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:57:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:58:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:59:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:60:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:61:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:62:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:63:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:66:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:67:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:68:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:69:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:72:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:73:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:74:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:75:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:76:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:77:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:78:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:81:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:82:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:83:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:84:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:85:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:86:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:89:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:90:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:91:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:92:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:93:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:94:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:95:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:96:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:97:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/integration_ownership.v1.yaml:98:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml:38:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml:48:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml:49:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml:50:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml:58:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml:61:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml:62:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/contracts/requirements_lineage.v1.yaml:63:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py:37:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/execution_package_v2_qa_criteria.v1.md:40:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:100:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:128:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:129:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:130:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:148:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:149:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:150:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:151:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:152:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:153:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:172:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:173:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:174:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:25:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:46:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:47:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:50:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v1.yaml:99:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:143:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:144:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:148:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:174:Source root	runtime/langgraph_factory/nodes/inputs.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:175:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:182:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:194:Source root	runtime/langgraph_factory/graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:195:Source root	runtime/langgraph_factory/routing.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:196:Source root	runtime/langgraph_factory/unit_graph.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:197:Source root	runtime/langgraph_factory/repair.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:198:Source root	runtime/langgraph_factory/acceptance.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:199:Source root	runtime/langgraph_factory/workbook.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:218:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:219:Source root	runtime/langgraph_factory/artifacts.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:220:Source root	runtime/langgraph_factory/persistence.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:35:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:69:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:90:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:91:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/implementation.graph.v2.yaml:94:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/n20_recovery.plan.v1.md:52:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/n20_recovery.plan.v2.md:82:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/prompts/N20_provider_transport.prompt.v2.md:21:Source root	runtime/langgraph_factory/egress.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:108:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:121:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:122:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:183:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:184:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:213:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:217:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:235:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:249:Source root	runtime/langgraph_factory/model_nodes.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:261:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:272:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:282:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:299:Python package	runtime.gemini
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:354:Source root	runtime/a/b.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:356:Source root	runtime/a/b.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:372:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:373:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:394:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:416:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:423:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:77:Source root	runtime/langgraph_factory/transport.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:78:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py:774:Source root	runtime/run_curriculum.py
oldref:plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py:783:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/28_runtime_operations_docs.plan.v1.md:104:Source root	runtime/langgraph_factory/graph.py
oldref:plans/28_runtime_operations_docs/28_runtime_operations_docs.plan.v1.md:107:Source root	runtime/langgraph_factory/evidence.py
oldref:plans/28_runtime_operations_docs/28_runtime_operations_docs.plan.v1.md:12:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/28_runtime_operations_docs.plan.v1.md:132:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/28_runtime_operations_docs.plan.v1.md:13:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/plans.log.md:32:Python package	-m runtime
oldref:plans/28_runtime_operations_docs/plans.log.md:32:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/plans.log.md:9:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/prompts/28_runtime_operations_docs.prompt.v1.md:42:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/prompts/28_runtime_operations_docs.prompt.v1.md:6:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/qa/execution_test.plan.v1.md:111:Source root	runtime/run_curriculum.py
oldref:plans/28_runtime_operations_docs/qa/execution_test.plan.v1.md:112:Python package	-m runtime
oldref:plans_internal/create_system_doc/create_system_doc.prompt.v2.yaml:118:Python package	runtime.logger.ExecutionLogger
oldref:plans_internal/create_system_doc/create_system_doc.prompt.v2.yaml:20:Python package	runtime.logger.ExecutionLogger
oldref:plans_internal/refactor_repo/prompts/P00A_post_inventory_decomposition.prompt.v3.yaml:24:Python package	runtime.logger.ExecutionLogger
oldref:plans_internal/refactor_repo/prompts/P00_inventory_baseline.prompt.v3.yaml:29:Python package	runtime.logger.ExecutionLogger
oldref:plans_internal/refactor_repo/prompts/P01_packaging_skeleton.prompt.v3.yaml:25:Python package	runtime.logger.ExecutionLogger
oldref:plans_internal/refactor_repo/prompts/P02S_structured_data_codemod.prompt.v3.yaml:24:Python package	runtime.logger.ExecutionLogger
oldref:plans_internal/refactor_repo/prompts/P02_import_codemod.prompt.v3.yaml:24:Python package	runtime.logger.ExecutionLogger
oldref:plans_internal/refactor_repo/prompts/P06_schema_compatibility.prompt.v3.yaml:51:Repository slug	curriculum_builder
oldref:policy/checks.v1.yaml:113:Source root	runtime/lesson_render.py
oldref:policy/checks.v1.yaml:115:Source root	runtime/readability.py
oldref:policy/checks.v1.yaml:163:Source root	runtime/session_bridge.py
oldref:policy/checks.v1.yaml:164:Source root	runtime/checks.py
oldref:policy/checks.v1.yaml:173:Source root	runtime/session_bridge.py
oldref:policy/checks.v1.yaml:174:Source root	runtime/checks.py
oldref:policy/checks.v1.yaml:183:Source root	runtime/pdf_inspect.py
oldref:policy/checks.v1.yaml:184:Source root	runtime/session_bridge.py
oldref:policy/checks.v1.yaml:195:Source root	runtime/pdf_inspect.py
oldref:policy/checks.v1.yaml:196:Source root	runtime/session_bridge.py
oldref:policy/checks.v1.yaml:206:Source root	runtime/pdf_inspect.py
oldref:policy/checks.v1.yaml:207:Source root	runtime/session_bridge.py
oldref:policy/checks.v1.yaml:73:Source root	runtime/session_bridge.py
oldref:policy/retrieval_hosts.v1.yaml:3:Source root	runtime/langgraph_factory/egress.py
oldref:policy/routes.v1.yaml:123:Source root	runtime/langgraph_factory/transport.py
oldref:readme.md:1:Repository slug	curriculum_builder
oldref:research/agents_research/commercial_curriculum_platforms_qa.md:26:Repository slug	curriculum_builder
oldref:research/agents_research/commercial_curriculum_platforms_qa.md:52:Repository slug	curriculum_builder
oldref:research/agents_research/commercial_curriculum_platforms_qa.md:5:Repository slug	curriculum_builder
oldref:research/agents_research/domain_expert_factual_verification.md:14:Repository slug	curriculum_builder
oldref:research/agents_research/multi_agent_llm_judge_review.md:27:Repository slug	curriculum_builder
oldref:research/agents_research/multi_agent_llm_judge_review.md:51:Repository slug	curriculum_builder
oldref:research/agents_research/physical_safety_review_hands_on_stem.md:30:Repository slug	curriculum_builder
oldref:research/agents_research/physical_safety_review_hands_on_stem.md:46:Repository slug	curriculum_builder
oldref:research/agents_research/readability_vocabulary_control.md:27:Repository slug	curriculum_builder
oldref:research/agents_research/structured_output_rendering_qa.md:53:Repository slug	curriculum_builder
oldref:research/arduino_kit_domain_schema_drift/schema_contract_regression_testing.md:27:Source root	runtime/session_bridge.py
oldref:research/arduino_kit_domain_schema_drift/sota_agents.v1.json:17:Source root	runtime/session_bridge.py
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_builder_sota_capability_radar.v2.md:107:Product name	Curriculum Builder
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_builder_sota_capability_radar.v2.md:123:Product name	Curriculum Builder
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_builder_sota_capability_radar.v2.md:88:Product name	Curriculum Builder
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_builder_sota_capability_radar.v2.md:92:Product name	Curriculum Builder
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_factory_capability_radar.v1.md:14:Product name	Curriculum Builder
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_factory_capability_radar.v1.md:50:Product name	Curriculum Builder
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_factory_capability_radar.v1.md:55:Product name	Curriculum Builder
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_factory_capability_radar.v1.md:59:Product name	Curriculum Builder
oldref:research/curricula_gen_competitive_landscape/github_ai_curriculum_factory_capability_radar.v1.md:75:Product name	Curriculum Builder
oldref:research/plan_schemas/plan_schema_state_of_the_art.v1.md:106:Source root	runtime/langgraph_factory/graph.py
oldref:research/plan_schemas/plan_schema_state_of_the_art.v1.md:124:Source root	runtime/langgraph_factory/graph.py
oldref:research/plan_schemas/plan_schema_state_of_the_art.v1.md:38:Source root	runtime/langgraph_factory/graph.py
oldref:research/plan_schemas/plan_schema_state_of_the_art.v1.md:5:Repository slug	curriculum_builder
oldref:research/prompt_restart_strategies/prompt_restart_strategies.sota.v1.md:125:Source root	runtime/logger.py
oldref:research/prompt_restart_strategies/prompt_restart_strategies.sota.v1.md:12:Python package	runtime.logger.ExecutionLogger
oldref:research/prompt_restart_strategies/prompt_restart_strategies.sota.v1.md:99:Python package	runtime.logger.ExecutionLogger.start
oldref:research/prompt_schemas/prompt_schema_state_of_the_art.v1.md:5:Repository slug	curriculum_builder
oldref:research/rendering_gap_scan/rendered_page_visual_qa.md:9:Source root	runtime/checks.py
oldref:research/rendering_gap_scan/sota_agents.v1.json:4:Source root	runtime/session_bridge.py
oldref:research/rendering_gap_scan/sota_agents.v1.json:6:Source root	runtime/session_bridge.py
oldref:research/rendering_gap_scan/sota_agents.v1.json:7:Source root	runtime/session_bridge.py
oldref:research/rendering_gap_scan/structured_output_rendering_conformance.md:21:Source root	runtime/session_bridge.py
oldref:research/repository_refactoring/repository_refactoring.sota.v1.md:118:Repository slug	curriculum_builder
oldref:research/scan_test/commercial_platform_qa_practice.md:56:Source root	runtime/session_bridge.py
oldref:research/scan_test/curriculum_sequence_coherence.md:20:Source root	runtime/session_bridge.py
oldref:research/scan_test/multi_agent_llm_judge_review.md:59:Source root	runtime/session_bridge.py
oldref:research/scan_test/multimodal_asset_grounding_review.md:28:Source root	runtime/checks.py
oldref:research/scan_test/sota_agents.v1.json:39:Source root	runtime/checks.py
oldref:research/scan_test/sota_agents.v1.json:50:Source root	runtime/session_bridge.py
oldref:research/scan_test/sota_agents.v1.json:62:Source root	runtime/routing.py
oldref:research/scan_test/sota_agents.v1.json:6:Source root	runtime/session_bridge.py
oldref:research/scan_test/sota_agents.v1.json:7:Source root	runtime/session_bridge.py
oldref:research/scan_test/structured_output_rendering_conformance.md:11:Source root	runtime/session_bridge.py
oldref:research/scan_test/structured_output_rendering_conformance.md:29:Source root	runtime/checks.py
oldref:research/spec_schemas/spec_schema_state_of_the_art.v1.md:5:Repository slug	curriculum_builder
oldref:runtime/curriculum_factory_graph.py:1481:Python package	runtime.validated_manifest
oldref:runtime/curriculum_factory_graph.py:1514:Python package	runtime._logger_gate
oldref:runtime/curriculum_factory_graph.py:1518:Python package	runtime.static_preflight
oldref:runtime/curriculum_factory_graph.py:292:Python package	runtime.resolve_curriculum
oldref:runtime/curriculum_factory_graph.py:293:Python package	runtime.validated_manifest
oldref:runtime/curriculum_factory_graph.py:299:Python package	runtime.resolve_curriculum
oldref:runtime/curriculum_factory_graph.py:300:Python package	runtime.validated_manifest
oldref:runtime/curriculum_factory_graph.py:343:Python package	runtime.limit_policy
oldref:runtime/curriculum_factory_graph.py:443:Python package	runtime.selector.validate_decision
oldref:runtime/finalize_evidence.py:38:Source root	runtime/run_curriculum.py
oldref:runtime/finalize_evidence.py:39:Source root	runtime/run_curriculum.py
oldref:runtime/langgraph_factory/evidence.py:20:Python package	runtime.langgraph_factory.artifacts
oldref:runtime/langgraph_factory/graph.py:102:Python package	runtime.langgraph_factory.nodes
oldref:runtime/langgraph_factory/graph.py:103:Python package	runtime.langgraph_factory.model_nodes
oldref:runtime/langgraph_factory/graph.py:104:Python package	runtime.langgraph_factory.workbook
oldref:runtime/langgraph_factory/graph.py:105:Python package	runtime.langgraph_factory.repair
oldref:runtime/langgraph_factory/graph.py:106:Python package	runtime.langgraph_factory.acceptance
oldref:runtime/langgraph_factory/nodes/inputs.py:1193:Python package	runtime.run_curriculum._prove_driver_capabilities
oldref:runtime/langgraph_factory/persistence.py:38:Python package	runtime.langgraph_factory.artifacts
oldref:runtime/langgraph_factory/unit_graph.py:11:Python package	runtime.langgraph_factory
oldref:runtime/readability.py:142:Python package	runtime.readability
oldref:runtime/readability.py:5:Source root	runtime/checks.py
oldref:runtime/run_curriculum.py:16:Python package	runtime.langgraph_factory.nodes.inputs
oldref:runtime/run_curriculum.py:2:Python package	-m runtime
oldref:runtime/run_curriculum.py:315:Python package	runtime.langgraph_factory.transport
oldref:runtime/run_curriculum.py:42:Python package	runtime.langgraph_factory
oldref:runtime/run_curriculum.py:43:Python package	runtime.langgraph_factory
oldref:runtime/run_curriculum.py:44:Python package	runtime.langgraph_factory.artifacts
oldref:runtime/run_curriculum.py:45:Python package	runtime.langgraph_factory.egress
oldref:runtime/run_curriculum.py:54:Python package	runtime.langgraph_factory.graph
oldref:runtime/run_curriculum.py:55:Python package	runtime.langgraph_factory.nodes.inputs
oldref:runtime/run_curriculum.py:65:Python package	-m runtime
oldref:runtime/run_curriculum.py:7:Python package	runtime.langgraph_factory.graph.build_curriculum_factory_graph
oldref:runtime/session_bridge.py:55:Python package	runtime.resolve_curriculum
oldref:runtime/session_bridge.py:56:Python package	runtime.resolve_companions
oldref:runtime/session_bridge.py:57:Python package	runtime.validated_manifest
oldref:runtime/session_bridge.py:58:Python package	runtime.run_verifier_fixtures
oldref:runtime/session_bridge.py:68:Python package	runtime._logger_gate
oldref:runtime/session_bridge.py:78:Python package	runtime.prompt
oldref:schemas/calibration.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/checks.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/circuit_data.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/controller.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/curriculum.schema.v5.json:3:Repository slug	curriculum_builder
oldref:schemas/deferred.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/execution_log.schema.v2.json:3:Repository slug	curriculum_builder
oldref:schemas/failures.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/kit_calibration.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/lab.schema.v4.json:3:Repository slug	curriculum_builder
oldref:schemas/limits.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/manifest_domain.metaschema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/model_registry.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/plan.schema.v1.json:107:Source root	runtime/langgraph_factory/graph.py
oldref:schemas/plan.schema.v1.json:152:Python package	runtime.langgraph_factory.graph
oldref:schemas/plan.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/plan.schema.v1.json:5:Source root	runtime/langgraph_factory/graph.py
oldref:schemas/prompt.schema.v3.json:3:Repository slug	curriculum_builder
oldref:schemas/prompt.schema.v4.json:3:Repository slug	curriculum_builder
oldref:schemas/quality_gates.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/repository_refactor_inventory.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/routes.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/routing_decision.schema.v2.json:3:Repository slug	curriculum_builder
oldref:schemas/routing_policy.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/run_lifecycle.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/spec.schema.v1.json:3:Repository slug	curriculum_builder
oldref:schemas/task_taxonomy.schema.v2.json:3:Repository slug	curriculum_builder
oldref:schemas/unit_content.schema.v1.json:3:Repository slug	curriculum_builder
oldref:tests/fixtures/planref_stale_pair.reject/folder_refactoring.plan.v6.md:9:Repository slug	curriculum_builder
oldref:tests/gates/fr_p0_structure.py:68:Repository slug	curriculum_builder
oldref:tests/gates/fr_p5_unit.py:42:Source root	runtime/checks.py
oldref:tests/gates/fr_p5_unit.py:44:Python package	runtime.readability
oldref:tests/gates/gate_families.schema.v1.json:3:Repository slug	curriculum_builder
oldref:tests/runtime/test_acceptance_gate.py:107:Python package	runtime.lesson_render
oldref:tests/runtime/test_acceptance_gate.py:170:Python package	runtime.visual_maps
oldref:tests/runtime/test_acceptance_gate.py:18:Python package	runtime.checks
oldref:tests/runtime/test_acceptance_gate.py:19:Python package	runtime.logger
oldref:tests/runtime/test_acceptance_gate.py:20:Python package	runtime.session_bridge
oldref:tests/runtime/test_acceptance_gate.py:227:Python package	runtime.lesson_render
oldref:tests/runtime/test_capabilities.py:10:Python package	runtime.gemini
oldref:tests/runtime/test_capabilities.py:8:Python package	runtime.capabilities
oldref:tests/runtime/test_checks.py:11:Python package	runtime.checks
oldref:tests/runtime/test_claim_entailment.py:15:Python package	runtime.checks
oldref:tests/runtime/test_controller.py:100:Python package	runtime.run_verifier_fixtures
oldref:tests/runtime/test_controller.py:10:Python package	runtime.controller
oldref:tests/runtime/test_controller.py:113:Python package	runtime.simulate
oldref:tests/runtime/test_controller.py:11:Python package	runtime.io
oldref:tests/runtime/test_controller.py:21:Source root	runtime/io.py
oldref:tests/runtime/test_controller.py:33:Python package	runtime.static_preflight
oldref:tests/runtime/test_controller.py:44:Python package	runtime.simulate
oldref:tests/runtime/test_controller.py:51:Python package	runtime.prepare_output
oldref:tests/runtime/test_controller.py:55:Python package	runtime.prepare_output
oldref:tests/runtime/test_controller.py:59:Python package	runtime.prepare_output
oldref:tests/runtime/test_controller.py:64:Python package	runtime.simulate
oldref:tests/runtime/test_controller.py:70:Python package	runtime.legal_transition
oldref:tests/runtime/test_controller.py:71:Python package	runtime.legal_transition
oldref:tests/runtime/test_controller.py:72:Python package	runtime.legal_transition
oldref:tests/runtime/test_controller.py:76:Python package	runtime.simulate
oldref:tests/runtime/test_controller.py:80:Python package	runtime.simulate
oldref:tests/runtime/test_controller.py:86:Python package	runtime.simulate
oldref:tests/runtime/test_controller.py:89:Python package	runtime.simulate
oldref:tests/runtime/test_controller.py:93:Python package	runtime.simulate
oldref:tests/runtime/test_controller.py:97:Python package	runtime.validated_manifest
oldref:tests/runtime/test_controller.py:9:Python package	runtime.checkpoint
oldref:tests/runtime/test_curriculum_factory_graph.py:11:Python package	runtime.factory_state
oldref:tests/runtime/test_curriculum_factory_graph.py:12:Python package	runtime.io
oldref:tests/runtime/test_curriculum_factory_graph.py:139:Source root	runtime/curriculum_factory_graph.py
oldref:tests/runtime/test_curriculum_factory_graph.py:171:Python package	runtime.curriculum_factory_graph.readability_problems
oldref:tests/runtime/test_curriculum_factory_graph.py:195:Python package	runtime.curriculum_factory_graph.readability_problems
oldref:tests/runtime/test_curriculum_factory_graph.py:207:Python package	runtime.curriculum_factory_graph.readability_problems
oldref:tests/runtime/test_curriculum_factory_graph.py:225:Python package	runtime.validated_manifest
oldref:tests/runtime/test_curriculum_factory_graph.py:9:Python package	runtime.curriculum_factory_graph
oldref:tests/runtime/test_gemini.py:11:Python package	runtime.gemini
oldref:tests/runtime/test_lesson_render.py:15:Python package	runtime.lesson_render
oldref:tests/runtime/test_lesson_render.py:186:Python package	runtime.lesson_render
oldref:tests/runtime/test_lesson_render.py:21:Python package	runtime.session_bridge
oldref:tests/runtime/test_lesson_render.py:338:Python package	runtime.checks
oldref:tests/runtime/test_lesson_render.py:372:Python package	runtime.checks
oldref:tests/runtime/test_logger.py:11:Python package	runtime.logger
oldref:tests/runtime/test_plan26_adversarial.py:1580:Python package	runtime.model_worker
oldref:tests/runtime/test_plan26_adversarial.py:1581:Python package	runtime.capability_cycle
oldref:tests/runtime/test_plan26_adversarial.py:1585:Source root	runtime/run_curriculum.py
oldref:tests/runtime/test_plan26_adversarial.py:52:Python package	runtime.run_curriculum
oldref:tests/runtime/test_plan26_adversarial.py:53:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_adversarial.py:54:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_adversarial.py:55:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_adversarial.py:56:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_adversarial.py:57:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_adversarial.py:58:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_adversarial.py:59:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_adversarial.py:60:Python package	runtime.langgraph_factory.artifacts
oldref:tests/runtime/test_plan26_adversarial.py:61:Python package	runtime.langgraph_factory.egress
oldref:tests/runtime/test_plan26_adversarial.py:666:Python package	runtime.test_plan26_adversarial
oldref:tests/runtime/test_plan26_adversarial.py:669:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_adversarial.py:69:Python package	runtime.langgraph_factory.evidence
oldref:tests/runtime/test_plan26_adversarial.py:70:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_adversarial.py:80:Python package	runtime.langgraph_factory.nodes.content
oldref:tests/runtime/test_plan26_adversarial.py:81:Python package	runtime.langgraph_factory.nodes.domain
oldref:tests/runtime/test_plan26_adversarial.py:82:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_adversarial.py:981:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_cli.py:118:Python package	runtime.controller
oldref:tests/runtime/test_plan26_cli.py:119:Python package	runtime.curriculum_factory_graph
oldref:tests/runtime/test_plan26_cli.py:120:Python package	runtime.model_worker
oldref:tests/runtime/test_plan26_cli.py:121:Python package	runtime.session_bridge
oldref:tests/runtime/test_plan26_cli.py:122:Python package	runtime.checks
oldref:tests/runtime/test_plan26_cli.py:123:Python package	runtime.checkpoint
oldref:tests/runtime/test_plan26_cli.py:124:Python package	runtime.capability_cycle
oldref:tests/runtime/test_plan26_cli.py:156:Python package	runtime.langgraph_factory.graph
oldref:tests/runtime/test_plan26_cli.py:160:Python package	runtime.langgraph_factory.
oldref:tests/runtime/test_plan26_cli.py:1:Python package	runtime.run_curriculum
oldref:tests/runtime/test_plan26_cli.py:40:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_cli.py:41:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_cli.py:43:Python package	runtime.run_curriculum
oldref:tests/runtime/test_plan26_cli.py:518:Python package	runtime.langgraph_factory.artifacts
oldref:tests/runtime/test_plan26_cli.py:786:Source root	runtime/run_curriculum.py
oldref:tests/runtime/test_plan26_deterministic_nodes.py:1975:Python package	runtime.langgraph_factory.reducers
oldref:tests/runtime/test_plan26_deterministic_nodes.py:20:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:21:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_deterministic_nodes.py:236:Python package	runtime.langgraph_factory.nodes.
oldref:tests/runtime/test_plan26_deterministic_nodes.py:2533:Python package	runtime.run_curriculum._prove_live_capabilities
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3188:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3214:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3280:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3326:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3429:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3474:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3481:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3567:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3780:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3888:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_deterministic_nodes.py:3889:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_deterministic_nodes.py:38:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_deterministic_nodes.py:39:Python package	runtime.langgraph_factory.egress
oldref:tests/runtime/test_plan26_egress.py:16:Python package	runtime.langgraph_factory.egress
oldref:tests/runtime/test_plan26_egress.py:513:Python package	runtime.langgraph_factory.egress
oldref:tests/runtime/test_plan26_evidence.py:12:Python package	runtime.langgraph_factory.artifacts
oldref:tests/runtime/test_plan26_evidence.py:24:Python package	runtime.langgraph_factory.evidence
oldref:tests/runtime/test_plan26_model_nodes.py:12:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:13:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:1485:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_model_nodes.py:14:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_model_nodes.py:1543:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:1555:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:1570:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:1586:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:15:Python package	runtime.langgraph_factory.reducers
oldref:tests/runtime/test_plan26_model_nodes.py:1606:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:1632:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:1692:Python package	runtime.langgraph_factory.model_nodes
oldref:tests/runtime/test_plan26_model_nodes.py:1703:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_model_nodes.py:1708:Python package	runtime.langgraph_factory.model_nodes
oldref:tests/runtime/test_plan26_model_nodes.py:1712:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_model_nodes.py:23:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_persistence.py:108:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_persistence.py:1245:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_persistence.py:147:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_persistence.py:164:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_persistence.py:42:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_persistence.py:43:Python package	runtime.langgraph_factory.evidence
oldref:tests/runtime/test_plan26_persistence.py:44:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_persistence.py:45:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_persistence.py:46:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_persistence.py:966:Python package	runtime.langgraph_factory.transport
oldref:tests/runtime/test_plan26_persistence.py:967:Python package	runtime.langgraph_factory.egress
oldref:tests/runtime/test_plan26_persistence.py:968:Python package	runtime.langgraph_factory.model_nodes
oldref:tests/runtime/test_plan26_persistence.py:969:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_persistence.py:970:Python package	runtime.langgraph_factory.workbook
oldref:tests/runtime/test_plan26_repair_acceptance.py:31:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_repair_acceptance.py:32:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_repair_acceptance.py:33:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_repair_acceptance.py:34:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_repair_acceptance.py:35:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_repair_acceptance.py:36:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_repair_acceptance.py:37:Python package	runtime.langgraph_factory.nodes.domain
oldref:tests/runtime/test_plan26_repair_acceptance.py:38:Python package	runtime.langgraph_factory.nodes.content
oldref:tests/runtime/test_plan26_repair_acceptance.py:39:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_repair_acceptance.py:40:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_repair_acceptance.py:41:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_repair_acceptance.py:4:Python package	runtime.langgraph_factory.repair
oldref:tests/runtime/test_plan26_repair_acceptance.py:6:Python package	runtime.langgraph_factory.nodes.terminal.write_terminal
oldref:tests/runtime/test_plan26_repair_acceptance.py:837:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_repair_acceptance.py:856:Python package	runtime.langgraph_factory.nodes.terminal
oldref:tests/runtime/test_plan26_state_reducers.py:12:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_state_reducers.py:13:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_topology.py:208:Python package	runtime.langgraph_factory.
oldref:tests/runtime/test_plan26_topology.py:224:Python package	runtime.langgraph_factory.nodes.terminal
oldref:tests/runtime/test_plan26_topology.py:49:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_topology.py:50:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_topology.py:51:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_topology.py:52:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_topology.py:53:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_topology.py:54:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_topology.py:866:Python package	runtime.curriculum_factory_graph
oldref:tests/runtime/test_plan26_topology.py:869:Python package	runtime.session_bridge
oldref:tests/runtime/test_plan26_topology.py:949:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_topology.py:987:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_topology.py:988:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_transport.py:1614:Python package	runtime.langgraph_factory.nodes.inputs
oldref:tests/runtime/test_plan26_transport.py:18:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_transport.py:19:Python package	runtime.langgraph_factory.artifacts
oldref:tests/runtime/test_plan26_transport.py:2036:Python package	runtime.langgraph_factory.nodes.visuals
oldref:tests/runtime/test_plan26_transport.py:25:Python package	runtime.langgraph_factory.egress
oldref:tests/runtime/test_plan26_unit_graph.py:1284:Python package	runtime.langgraph_factory.reducers
oldref:tests/runtime/test_plan26_unit_graph.py:2258:Python package	runtime.langgraph_factory.model_nodes
oldref:tests/runtime/test_plan26_unit_graph.py:2800:Python package	runtime.langgraph_factory.artifacts
oldref:tests/runtime/test_plan26_unit_graph.py:413:Python package	runtime.langgraph_factory.artifacts
oldref:tests/runtime/test_plan26_unit_graph.py:414:Python package	runtime.langgraph_factory.evidence
oldref:tests/runtime/test_plan26_unit_graph.py:58:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_unit_graph.py:59:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_unit_graph.py:60:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_unit_graph.py:61:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_unit_graph.py:62:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_unit_graph.py:63:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_unit_graph.py:73:Python package	runtime.langgraph_factory.reducers
oldref:tests/runtime/test_plan26_unit_graph.py:74:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_unit_graph.py:957:Python package	runtime.langgraph_factory.unit_graph
oldref:tests/runtime/test_plan26_workbook.py:1010:Python package	runtime.langgraph_factory.artifacts
oldref:tests/runtime/test_plan26_workbook.py:1011:Python package	runtime.langgraph_factory.evidence
oldref:tests/runtime/test_plan26_workbook.py:32:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_workbook.py:33:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_workbook.py:34:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_workbook.py:35:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_workbook.py:36:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan26_workbook.py:37:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_workbook.py:38:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan26_workbook.py:543:Python package	runtime.langgraph_factory.nodes
oldref:tests/runtime/test_plan26_workbook.py:559:Python package	runtime.langgraph_factory.nodes.terminal
oldref:tests/runtime/test_plan26_workbook.py:5:Python package	runtime.langgraph_factory.workbook
oldref:tests/runtime/test_plan26_workbook.py:6:Python package	runtime.langgraph_factory.nodes.terminal.write_terminal
oldref:tests/runtime/test_plan26_workbook.py:775:Python package	runtime.langgraph_factory.state
oldref:tests/runtime/test_plan27_adversarial.py:109:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_plan27_adversarial.py:20:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_retry.py:3:Python package	runtime.retry
oldref:tests/runtime/test_routing.py:6:Python package	runtime.routing
oldref:tests/runtime/test_run_curriculum.py:104:Python package	runtime.states
oldref:tests/runtime/test_run_curriculum.py:106:Python package	runtime.controller.time.monotonic
oldref:tests/runtime/test_run_curriculum.py:107:Python package	runtime.simulate
oldref:tests/runtime/test_run_curriculum.py:10:Python package	runtime.controller
oldref:tests/runtime/test_run_curriculum.py:11:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_run_curriculum.py:12:Python package	runtime.langgraph_factory
oldref:tests/runtime/test_run_curriculum.py:13:Python package	runtime.run_curriculum
oldref:tests/runtime/test_run_curriculum.py:14:Python package	runtime.run_curriculum
oldref:tests/runtime/test_run_curriculum.py:45:Python package	runtime.run_curriculum
oldref:tests/runtime/test_run_curriculum.py:81:Python package	runtime.controller
oldref:tests/runtime/test_run_curriculum.py:82:Python package	runtime.session_bridge
oldref:tests/runtime/test_run_curriculum.py:83:Python package	runtime.curriculum_factory_graph
oldref:tests/runtime/test_run_curriculum.py:84:Python package	runtime.model_worker
oldref:tests/runtime/test_run_state.py:168:Python package	runtime.session_bridge
oldref:tests/runtime/test_run_state.py:16:Python package	runtime.run_state
oldref:tests/runtime/test_run_state.py:17:Python package	runtime.workbook
oldref:tests/runtime/test_visual_maps.py:15:Python package	runtime.visual_maps
oldref:tests/runtime/test_visual_maps.py:206:Python package	runtime.session_bridge
oldref:tests/runtime/unit_fixture.py:14:Python package	runtime.io
oldref:tests/runtime/unit_fixture.py:15:Python package	runtime.logger
oldref:tests/runtime/unit_fixture.py:16:Python package	runtime.visual_maps
schema:schemas/calibration.schema.v1.json	https://example.invalid/curriculum_builder/calibration.schema.v1.json
schema:schemas/checks.schema.v1.json	https://example.invalid/curriculum_builder/checks.schema.v1.json
schema:schemas/circuit_data.schema.v1.json	https://example.invalid/curriculum_builder/circuit_data.schema.v1.json
schema:schemas/controller.schema.v1.json	https://example.invalid/curriculum_builder/controller.schema.v1.json
schema:schemas/curriculum.schema.v5.json	https://example.invalid/curriculum_builder/curriculum.schema.v5.json
schema:schemas/curriculum_factory_production_loop_closure.schema.v1.json	curriculum_factory_production_loop_closure.schema.v1.json
schema:schemas/deferred.schema.v1.json	https://example.invalid/curriculum_builder/deferred.schema.v1.json
schema:schemas/execution_log.schema.v2.json	https://example.invalid/curriculum_builder/execution_log.schema.v2.json
schema:schemas/failures.schema.v1.json	https://example.invalid/curriculum_builder/failures.schema.v1.json
schema:schemas/kit_calibration.schema.v1.json	https://example.invalid/curriculum_builder/kit_calibration.schema.v1.json
schema:schemas/lab.schema.v4.json	https://example.invalid/curriculum_builder/lab.schema.v4.json
schema:schemas/limits.schema.v1.json	https://example.invalid/curriculum_builder/limits.schema.v1.json
schema:schemas/manifest_domain.metaschema.v1.json	https://example.invalid/curriculum_builder/manifest_domain.metaschema.v1.json
schema:schemas/model_registry.schema.v1.json	https://example.invalid/curriculum_builder/model_registry.schema.v1.json
schema:schemas/plan.schema.v1.json	https://example.invalid/curriculum_builder/plan.schema.v1.json
schema:schemas/prompt.schema.v3.json	https://example.invalid/curriculum_builder/prompt.schema.v3.json
schema:schemas/prompt.schema.v4.json	https://example.invalid/curriculum_builder/prompt.schema.v4.json
schema:schemas/quality_gates.schema.v1.json	https://example.invalid/curriculum_builder/quality_gates.schema.v1.json
schema:schemas/repository_refactor_inventory.schema.v1.json	https://example.invalid/curriculum_builder/repository_refactor_inventory.schema.v1.json
schema:schemas/routes.schema.v1.json	https://example.invalid/curriculum_builder/routes.schema.v1.json
schema:schemas/routing_decision.schema.v2.json	https://example.invalid/curriculum_builder/routing_decision.schema.v2.json
schema:schemas/routing_policy.schema.v1.json	https://example.invalid/curriculum_builder/routing_policy.schema.v1.json
schema:schemas/run_lifecycle.schema.v1.json	https://example.invalid/curriculum_builder/run_lifecycle.schema.v1.json
schema:schemas/spec.schema.v1.json	https://example.invalid/curriculum_builder/spec.schema.v1.json
schema:schemas/task_taxonomy.schema.v2.json	https://example.invalid/curriculum_builder/task_taxonomy.schema.v2.json
schema:schemas/unit_content.schema.v1.json	https://example.invalid/curriculum_builder/unit_content.schema.v1.json
testsubtree:tests/fixtures/	no __init__.py
testsubtree:tests/gates/	no __init__.py
testsubtree:tests/refactor_repo/	no __init__.py
testsubtree:tests/results/	no __init__.py
testsubtree:tests/runtime/	importable (__init__.py present)
testsubtree:tests/selftest/	no __init__.py
traversal:.claude/skills/curriculum-concept-visualization/scripts/build_diagram.py:56	canonical = Path(__file__).resolve().parent.parent / "assets" / "house.typ"
traversal:.claude/skills/electronics-circuit-visualization/scripts/verify_trace.py:24	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:.claude/skills/harness-graph-create/scripts/render_graph.py:606	f"  Resolve a new version instead — {Path(__file__).with_name('outpath.py').name} "
traversal:.claude/skills/harness-graph-create/scripts/render_graph.py:609	f"{Path(__file__).with_name('outpath.py')} <viz-dir> <name>)\"\n"
traversal:.claude/skills/qa-gate-codex-run/scripts/qa_gate.py:1247	original, SCHEMA_PATH = SCHEMA_PATH, Path(__file__).with_name("postmortem.schema.json")
traversal:.claude/skills/qa-gate-codex-run/scripts/qa_gate.py:49	SCHEMA_PATH = Path(__file__).with_name("verdict.schema.json")
traversal:.claude/skills/qa-gate-codex-run/scripts/qa_gate.py:50	BRIDGE_PATH = Path(__file__).with_name("codex_bridge.mjs")
traversal:.claude/skills/qa-gate-codex-run/scripts/test_verify_integrity.py:30	MODULE_PATH = Path(__file__).with_name("qa_gate.py")
traversal:curricula/arduino_kit/verify_domain.py:47	HERE = Path(__file__).resolve().parent
traversal:plans/01_legacy_v3/run_curriculum.v3.py:25	ROOT = Path(__file__).resolve().parents[4]
traversal:plans/21_graph_engineered_subscription_execution/tools/validate_plan.py:23	ROOT = Path(__file__).resolve().parents[1]
traversal:plans/21_graph_engineered_subscription_execution/tools/validate_plan_v2.py:23	ROOT = Path(__file__).resolve().parents[1]
traversal:plans/21_graph_engineered_subscription_execution/tools/validate_plan_v3.py:25	ROOT = Path(__file__).resolve().parents[1]
traversal:plans/26_langgraph_curriculum_factory/prompt_graph_controller.py:32	PLAN_DIR = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py:33	_HERE = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/controller/contracts.py:29	_HERE = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/controller/core.py:25	CONTROLLER_DIR = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/controller/run27_controller.py:20	_HERE = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/controller/scheduler.py:28	_HERE = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/controller/verify_evidence_determinism.py:12	_HERE = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/controller/verify_ownership.py:12	_HERE = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/controller/verify_requirements_lineage.py:12	_HERE = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/tests/test_forbidden_production_scan.py:21	TESTS_DIR = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/tests/test_node_result_protocol.py:23	TESTS_DIR = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_adversarial.py:26	_HERE = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/tests/test_run27_controller.py:20	TESTS_DIR = Path(__file__).resolve().parent
traversal:plans/27_langgraph_curriculum_factory_remediation/tools/validate_plan.py:15	PLAN_DIR = Path(__file__).resolve().parents[1]
traversal:plans/27_langgraph_curriculum_factory_remediation/tools/validate_result.py:17	PLAN_DIR = Path(__file__).resolve().parents[1]
traversal:runtime/capability_cycle.py:172	parser.add_argument("--engine", type=Path, default=Path(__file__).resolve().parents[1])
traversal:runtime/controller.py:28	self.engine = canonical(engine or Path(__file__).resolve().parents[1])
traversal:runtime/curriculum_factory_graph.py:268	self.engine = Path(engine or Path(__file__).resolve().parents[1]).resolve()
traversal:runtime/langgraph_factory/egress.py:27	SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"
traversal:runtime/langgraph_factory/egress.py:376	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:runtime/langgraph_factory/model_nodes.py:1774	tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
traversal:runtime/langgraph_factory/nodes/inputs.py:735	allowed_dunder_names = {"__doc__", "__file__", "__name__"}
traversal:runtime/langgraph_factory/transport.py:46	PACKAGE_ROOT = Path(__file__).resolve().parent
traversal:runtime/langgraph_factory/transport.py:774	raw_path = getattr(module, "__file__", None)
traversal:runtime/session_bridge.py:399	parser.add_argument("--engine", type=Path, default=Path(__file__).resolve().parents[1])
traversal:tests/check_meta_prompt.py:77	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/fixtures/registry_missing_gate.reject.py:14	sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "gates"))
traversal:tests/fixtures/registry_unowned_family.reject.py:22	sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "gates"))
traversal:tests/gates/common.py:35	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/gates/fr_p0_structure.py:26	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/fr_p1_retention.py:18	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/fr_p2_selector.py:21	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/fr_p2_selector.py:22	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
traversal:tests/gates/fr_p3_calibration.py:22	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/fr_p4_policy_schemas.py:21	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/fr_p5_engine.py:37	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/fr_p5_engine.py:38	sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
traversal:tests/gates/fr_p5_manifest.py:39	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/fr_p5_unit.py:33	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/fr_p5_verifier.py:36	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/runner.py:31	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/selftest.py:24	sys.path.insert(0, str(Path(__file__).resolve().parent))
traversal:tests/gates/selftest.py:36	sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
traversal:tests/meta_prompt_source.py:35	REPO = Path(__file__).resolve().parents[1]
traversal:tests/runtime/test_capabilities.py:13	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_checks.py:15	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_controller.py:14	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_curriculum_factory_graph.py:15	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_gemini.py:68	result = subprocess.run(["node", str(Path(__file__).resolve().parents[2] / "runtime/resolve_gemini_settings.mjs"),
traversal:tests/runtime/test_lesson_render.py:23	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_logger.py:14	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_adversarial.py:84	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_api_contract.py:39	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_cli.py:45	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_deterministic_nodes.py:1012	engine = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_deterministic_nodes.py:1588	source = "".join(Path(module.__file__).read_text(encoding="utf-8") for module in NODE_MODULES)
traversal:tests/runtime/test_plan26_deterministic_nodes.py:1989	source = Path(module.__file__).read_text(encoding="utf-8")
traversal:tests/runtime/test_plan26_deterministic_nodes.py:2007	tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
traversal:tests/runtime/test_plan26_deterministic_nodes.py:2021	body = ast.parse(Path(inputs.__file__).read_text(encoding="utf-8"))
traversal:tests/runtime/test_plan26_deterministic_nodes.py:2158	tree = ast.parse(Path(inputs.__file__).read_text(encoding="utf-8"))
traversal:tests/runtime/test_plan26_deterministic_nodes.py:225	tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
traversal:tests/runtime/test_plan26_deterministic_nodes.py:244	if path == Path(terminal.__file__) or "__pycache__" in path.parts:
traversal:tests/runtime/test_plan26_deterministic_nodes.py:281	tree = ast.parse(Path(terminal.__file__).read_text(encoding="utf-8"))
traversal:tests/runtime/test_plan26_deterministic_nodes.py:47	PACKAGE_ROOT = Path(node_pkg.__file__).resolve().parent
traversal:tests/runtime/test_plan26_lock_drift.py:22	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_model_nodes.py:1261	tree = ast.parse(Path(mn.__file__).read_text(encoding="utf-8"))
traversal:tests/runtime/test_plan26_model_nodes.py:1275	tree = ast.parse(Path(mn.__file__).read_text(encoding="utf-8"))
traversal:tests/runtime/test_plan26_model_nodes.py:1299	mn.build_test_model_node_context(sandbox_root=Path(__file__).parent, responses={})
traversal:tests/runtime/test_plan26_model_nodes.py:908	source = Path(mn.__file__).read_text(encoding="utf-8")
traversal:tests/runtime/test_plan26_persistence.py:48	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_prompt_graph_controller.py:12	ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_repair_acceptance.py:44	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_state_reducers.py:42	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_topology.py:62	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_transport.py:1672	engine_root = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_unit_graph.py:80	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan26_workbook.py:41	REPO_ROOT = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_plan27_adversarial.py:114	engine_root=Path(__file__).resolve().parents[2], output_root=output_root)
traversal:tests/runtime/test_routing.py:9	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/runtime/test_run_curriculum.py:17	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/runtime/unit_fixture.py:18	ENGINE = Path(__file__).resolve().parents[2]
traversal:tests/test_validate_instance.py:11	REPO_ROOT = Path(__file__).resolve().parents[1]
```
