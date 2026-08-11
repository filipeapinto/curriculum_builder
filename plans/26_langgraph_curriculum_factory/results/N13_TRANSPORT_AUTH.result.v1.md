# N13_TRANSPORT_AUTH result

status: PASSED
graph_digest: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N13_transport_authorization.prompt.v2.md (123d987b166da423f31d03b77f61b2be37ec175d3b90d6d3b091d0c9ac4e0f04)
generation: 2

## Inputs

- N00_BASELINE_FREEZE: c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5
- plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md: 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af
- plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md: 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0
- plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md: c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2
- plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md: d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad
- plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md: 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7
- plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md: edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b
- plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md (sections 6.3, 7.1-7.4, 9, 14): 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6
- plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml: 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8
- runtime/model_worker.py (read for the Plan 25 subprocess pattern only; not modified)

## Outputs

- runtime/langgraph_factory/transport.py: 338bf915823ad2ba23ae3fdf95e8030e249a5ee794f14a565ea397b30f5475b3
- runtime/langgraph_factory/egress.py: 837410dad45a7deb8ef761e3636700a7fbde9f45ff6d97d8b4ba7b5c96383f52
- runtime/langgraph_factory/config/model_jobs.v1.yaml: 7b5d168c106ad428dc59600765a7c2960f16e7dc53e735d0ac232b42096e8a96
- runtime/langgraph_factory/schemas/M01_research_unit_sources.schema.json: cb745d064f9a8d2575c718613ac8512985f79f99a0297d6bd376d6a9075fa6f9
- runtime/langgraph_factory/schemas/M02_create_unit_domain_data.schema.json: 311b48b3b85c4fcc2e549a2becfe7b3879a38ec4be59c2ff3e39a3522a5e2232
- runtime/langgraph_factory/schemas/M03_write_unit_content.schema.json: f5773a2c54271778abf71a15a7b2cd41440f010ab2bf8c7bdcfc11d64e7912eb
- runtime/langgraph_factory/schemas/M04_create_unit_visuals.schema.json: 6be7ad65b6ad2f9c1db7ac49cd80939e80b0c9a52c522e1a29a4d33aa534026e
- runtime/langgraph_factory/schemas/M05_review_actual_unit.schema.json: fe7618d77e94d09f6de7ecc5da64bd354032396a2ebe1a19895413e29f743b51
- runtime/langgraph_factory/schemas/M06_repair_named_unit_artifact.schema.json: 8ec0f76dff14cc09e87f618086c44d5e5da6f3858886f75e61c9b9e822ed9a49
- runtime/langgraph_factory/schemas/M07_review_actual_workbook.schema.json: 5bd32065f188659176b7558044547f58e5f7ac21884d4df14e17e0172c2e1b7c
- runtime/langgraph_factory/schemas/M08_repair_named_workbook_defect.schema.json: d43e442f8c41731cc3e0d32782eb2d34e4c259580a817a7cc126dbf4c8bedef6
- runtime/langgraph_factory/schemas/internal_authorization_receipt.schema.json: 99c08b818cd5268f7073ca9c38f215a433cb241985fadf6e0984e06a7f68fec1
- runtime/langgraph_factory/schemas/internal_capability_proof.schema.json: 9fa636cd87792ae3e9dcd68fc46b09c3ce3d73a5657a92762b1dabe439102640
- runtime/langgraph_factory/schemas/internal_egress_receipt.schema.json: fa75436422de72d7a7749dcc92741f87459e30b8f5245d7fb5fab6e93aece01d
- runtime/langgraph_factory/schemas/internal_execution_receipt.schema.json: c1f34b029f7a3c97ccd8980b6b1d0e342ada3920f946269fd610e83f245d2de5
- runtime/langgraph_factory/prompts/M01_research_unit_sources.prompt.md: cd34146c6888ca416438d38c0d4c8b519a98bc51baeff65ecb8d54dcaef123b5
- runtime/langgraph_factory/prompts/M02_create_unit_domain_data.prompt.md: 6c59088990aa03c2f76a90dd4568bbb4d2e40a25234d4530c1ac2a4a71f8dadd
- runtime/langgraph_factory/prompts/M03_write_unit_content.prompt.md: dfded39069111263b5cc9930c00d0362d900dd8731a2d8d013f6714d015c5d85
- runtime/langgraph_factory/prompts/M04_create_unit_visuals.prompt.md: 964a3d793ed7f98276ca6d8ad7818ad30a74643fc95367d5dcc0d8dba8ec0186
- runtime/langgraph_factory/prompts/M05_review_actual_unit.prompt.md: 013e1d5404311f642b799bc5ee6d71f8c1e7a82ed61ed7ee9532f0dafbd9766d
- runtime/langgraph_factory/prompts/M06_repair_named_unit_artifact.prompt.md: a02a21c9c63013e3007e49aabf0406fbbc6ab3e8624c309195c6bc2517c8517e
- runtime/langgraph_factory/prompts/M07_review_actual_workbook.prompt.md: 6c2c84591b8abd7a5dd6a037092ddc924048ee33ab927663a7a1d9663c8f34bd
- runtime/langgraph_factory/prompts/M08_repair_named_workbook_defect.prompt.md: d182c8d80e80f98b6fbb5deff8cb7da573ec452d9c93314881d202432b3213ab
- tests/runtime/test_plan26_transport.py: 8c67461bc0bc25134e61f1f237c23cd00283141ff9c6c53c0da8f493b316ff59
- tests/runtime/test_plan26_egress.py: e31bab0c2084a41928a0c5c9a96db9f87db18fc87a865e38723334658ac9bf1a

`runtime/langgraph_factory/__init__.py` was already present (N11's write) and was not
touched. No file outside this node's `writes` set was created or modified.

## Frozen job registry

`config/model_jobs.v1.yaml` declares `job_count: 8` and exactly eight entries; a
registry with any other count, or with a CLI/family disagreement, is rejected at load.

| Job | Job type | CLI | Family | Model | Task class | Reasoning |
|---|---|---|---|---|---|---|
| M01_RESEARCH_UNIT_SOURCES | research_unit_sources | codex | openai | gpt-5.6-sol | component_research | xhigh |
| M02_CREATE_UNIT_DOMAIN_DATA | create_unit_domain_data | codex | openai | gpt-5.6-sol | final_acceptance | max |
| M03_WRITE_UNIT_CONTENT | write_unit_content | codex | openai | gpt-5.6-sol | child_explanatory_writing | high |
| M04_CREATE_UNIT_VISUALS | create_unit_visuals | codex | openai | gpt-5.6-sol | photorealistic_visual_prompt | high |
| M05_REVIEW_ACTUAL_UNIT | review_actual_unit | gemini | google | gemini-3-pro-preview | (none) | cli_model_default |
| M06_REPAIR_NAMED_UNIT_ARTIFACT | repair_named_unit_artifact | codex | openai | gpt-5.6-sol | final_acceptance | max |
| M07_REVIEW_ACTUAL_WORKBOOK | review_actual_workbook | gemini | google | gemini-3-pro-preview | (none) | cli_model_default |
| M08_REPAIR_NAMED_WORKBOOK_DEFECT | repair_named_workbook_defect | codex | openai | gpt-5.6-sol | workbook_assembly | high |

M05/M07 carry `cli_model_default`, never Plan 25's asserted `max`: the inspected
`gemini 0.24.5` CLI exposes no effort argument, and `build_job_argv` rejects a Gemini
route that claims one.

No model schema declares a routing, retry, admission, acceptance, resume, join, or
terminal field. `assert_no_authoritative_fields` enforces this against a frozen banned
name set, applied to every schema at staging time and to every candidate at parse time,
and asserted for all eight schemas by test.

## Egress policy

`egress.py` owns one boundary for the whole Python process.

- `EgressGuard` patches `socket.socket.connect`, `socket.socket.connect_ex`, and
  `socket.create_connection`. Because the interception is on `socket.socket` itself,
  raw sockets, `http.client`, `urllib`, and any third-party client all reach the same
  check; there is no wrapper to route around. Every attempt is receipted before the
  denial is raised.
- Egress is permitted only inside an active `SourceRetriever` grant. The grant pins the
  hostname and the exact resolved addresses, so a connect to any other address during
  retrieval is denied as `dns_rebinding`, and any connect outside a retrieval is denied
  as `unauthorized_socket_no_active_retrieval`.
- `MODEL_API_HOSTS` (api.openai.com, chatgpt.com, api.anthropic.com,
  generativelanguage.googleapis.com, cloudcode-pa.googleapis.com, aiplatform hosts) is
  denied as `direct_model_endpoint` unconditionally — inside a grant, outside a grant,
  as an initial locator, and as a redirect target. The only route to a model is a child
  process of the pinned CLI.
- `SourceRetriever` additionally enforces scheme, host allowlist, globally-routable
  resolution, redirect-hop allowlisting, redirect count, HTTP status, size, and content
  type. A permitted retrieval receipts the locator, resolved host and addresses, final
  URL, redirect chain, status, TLS metadata, content type, byte count, `bytes_sha256`,
  data class, and the authorization receipt id.
- Spec 7.4 authorization is checked by `authorize_transmission` before any process or
  socket exists. Absent, expired, wrong-run, wrong-curriculum-digest, wrong-output-root,
  unauthorized-provider, and unauthorized-data-class all fail closed with a named reason
  and a receipt. `AuthorizationRecord` refuses to be constructed at all for an unknown
  provider or a data class that provider may not carry.

## Sandbox proof

Mechanism: macOS `sandbox-exec` (`/usr/bin/sandbox-exec`), profile generated per
activation by `render_sandbox_profile` as `(deny default)` + `(import "system.sb")`,
allowing read/write only under the activation workspace and a dedicated temporary home,
read-only on the CLI's installation prefix, and outbound network only on TCP 443/80 and
UDP 53.

Evidence, from tests that actually execute the sandbox on this host:

- `test_sandboxed_worker_cannot_read_repository_output_or_secrets` builds a workspace and
  probes four real forbidden paths — a repository source file, a sibling unit's accepted
  artifact under the output root, a parent-directory author-history file, and a
  credentials file. All four are unreadable; `readable_forbidden_paths == []`.
- `test_the_real_cli_starts_sandboxed_yet_cannot_read_outside_the_workspace` runs the
  actual installed `codex` (codex-cli 0.147.0) and `gemini` (0.24.5) binaries under the
  generated profile. Both start successfully (rc 0) while `/bin/cat` of the credentials
  file and of `runtime/model_worker.py` fails from inside the same profile.
- `build_sandboxed_argv` raises `CapabilityProofFailed` when no host sandbox exists, so a
  platform without one cannot silently launch a model CLI unsandboxed.
- `prove_transport_capabilities` records four facets. Three are required and proven on
  this host: `filesystem_isolation`, `python_process_egress_broker`,
  `identity_observation`. `require_capability_proof` refuses to proceed if any required
  facet is unproven.

Named limitation (recorded, not hidden): `subprocess_network_scope` is enforced only at
port granularity. `sandbox-exec` profile language cannot pin an outbound *hostname*, so
the model CLI subprocess is confined to TCP 443/80 and UDP 53 rather than to the
provider's hosts. It is recorded as a non-required facet with an explicit `limitation`
string. Host-level pinning of subprocess egress is not achievable on this platform with
this mechanism; the Python process itself is fully constrained, and the direct-model-HTTP
path is closed from Python.

## Identity observation

`decided_*` and `observed_*` are separate fields and the observation is extracted from
the CLI, never copied from the decision.

- Codex: `--json` is added to the pinned argv because the JSONL event stream is the only
  machine-readable identity channel codex-cli 0.147.0 offers. `observe_codex_identity`
  scans `session_configured`, `thread.started`, `turn.started`, and `model_reroute`
  events for a `model` field; a later `model_reroute` supersedes the session model, so a
  silent reroute becomes an `IdentityMismatch` rather than a false pass. A stream naming
  no model raises `IdentityUnobservable`.
- Gemini: `observe_gemini_identity` reads `stats.models` from the
  `--output-format json` envelope and requires exactly one model with
  `api.totalRequests > 0`. Verified against the installed CLI's own type definitions
  (`@google/gemini-cli-core` `JsonOutput.stats: SessionMetrics`,
  `SessionMetrics.models: Record<string, ModelMetrics>`).
- `assert_identity_matches` rejects a model or family disagreement, and rejects a review
  route executing in the authoring family. An identity mismatch is never retried.

## Negative network tests

Every one of these is self-contained: no test performs a real network call or a real
Codex/Gemini model invocation.

| Attempt | Result | Receipted reason |
|---|---|---|
| raw `socket.connect` outside a retrieval | denied | `unauthorized_socket_no_active_retrieval` |
| `socket.connect_ex` outside a retrieval | denied | `unauthorized_socket_no_active_retrieval` |
| `urllib.request.urlopen` | denied | `unauthorized_socket_no_active_retrieval` |
| `http.client.HTTPSConnection.connect` to api.openai.com | denied | `direct_model_endpoint` |
| `create_connection` to each of the 7 model API hosts | denied | `direct_model_endpoint` |
| locator pointing at api.openai.com | denied | `direct_model_endpoint` |
| redirect to an unapproved host | denied | `redirect_to_unapproved_host` |
| redirect to a model endpoint | denied | `redirect_to_model_endpoint` |
| connect to an address not pinned by the grant | denied | `dns_rebinding` |
| host resolving to 169.254.169.254 | denied | `non_global_address` |
| connect to the allowlisted host after the retrieval ends | denied | `unauthorized_socket_no_active_retrieval` |
| unauthorized retrieval (absent / wrong-provider receipt) | denied, opener never called | `authorization_absent`, `wrong_provider_authorization` |

## Commands

- `python3 -m pytest tests/runtime/test_plan26_transport.py tests/runtime/test_plan26_egress.py -q` — exit 0 — `plans/26_langgraph_curriculum_factory/results/evidence/N13_TRANSPORT_AUTH/node_tests.txt` — 112 passed
- `python3 -m pytest -q` — exit 0 — `plans/26_langgraph_curriculum_factory/results/evidence/N13_TRANSPORT_AUTH/full_suite.txt` — 377 passed, 2 skipped, 282 subtests passed
- `shasum -a 256 <all writes + inputs>` — exit 0 — hashes reproduced in the Hashes section
- `codex --version` — exit 0 — `codex-cli 0.147.0`
- `gemini --version` — exit 0 — `0.24.5`

Generation 2 (this rework):

- `python3 -m pytest tests/runtime/test_plan26_transport.py tests/runtime/test_plan26_egress.py -q` — exit 0 — `plans/26_langgraph_curriculum_factory/results/evidence/N13_TRANSPORT_AUTH/node_tests_gen2.txt` — 130 passed
- `python3 -m pytest -q` — exit 0 — `plans/26_langgraph_curriculum_factory/results/evidence/N13_TRANSPORT_AUTH/full_suite_gen2.txt` — 831 passed, 12 skipped, 282 subtests passed

The 12 skips are N10's two lock/API tests and the ten Plan 26 graph test modules, which
`pytest.importorskip` on `langgraph`; that package is not installed in this interpreter.
No N13 test skipped.

The two skips belong to N10 (`test_plan26_api_contract.py`, `test_plan26_lock_drift.py`)
and are unrelated to this node; no N13 test skipped.

## Tests

77 tests in `tests/runtime/test_plan26_transport.py` and 35 in
`tests/runtime/test_plan26_egress.py`, all PASS.

| TEST item | Backing tests | Verdict and assertion |
|---|---|---|
| 1. Exactly eight jobs; unknown job/family/model/schema/prompt fails before launch | `test_registry_freezes_exactly_the_eight_spec_routes`, `test_unknown_job_id_is_rejected`, `test_registry_with_the_wrong_job_count_is_rejected`, `test_registry_with_a_mismatched_family_is_rejected`, `test_unknown_schema_or_prompt_fails_before_launch`, `test_execute_rejects_an_unknown_job_without_launching`, `test_execute_rejects_undeclared_data_classes_without_launching` | PASS — `len(registry) == 8` and all six route fields match the frozen table for each job; unknown job/data class raises `RouteRejected` with `runner.calls == []` |
| 2. Prompts are package-relative; cwd/root substitution fails | `test_prompts_resolve_relative_to_the_package_not_the_cwd`, `test_prompt_path_substitution_is_rejected`, `test_every_route_has_a_package_prompt_and_schema` | PASS — with a decoy `prompts/` tree as cwd, all eight resolve to `tp.PROMPT_DIR` and none contains the decoy text; `../`, absolute, and nested names raise `RouteRejected` |
| 3. Missing/expired/wrong-run/provider/data authorization makes zero calls | `test_missing_or_mismatched_authorization_makes_zero_calls` (5 cases), `test_authorization_fails_closed_for_every_scope_mismatch` (7 cases), `test_subprocess_authorization_receipts_both_outcomes` | PASS — each case asserts `runner.calls == []` **and** `ledger.total_reserved == 0`, plus a `subprocess_transmission` denial receipt |
| 4. Worker cannot read repository/output/parent/sibling/history/secrets | `test_sandboxed_worker_cannot_read_repository_output_or_secrets`, `test_the_real_cli_starts_sandboxed_yet_cannot_read_outside_the_workspace` (codex + gemini), `test_workspace_contains_only_the_authorized_staging_set`, `test_staged_input_names_cannot_escape_or_shadow` | PASS — `readable_forbidden_paths == []` across four real forbidden paths; both real CLIs start rc 0 while `/bin/cat` of a secret and of a repo file fails; workspace inventory is exactly the four authorized names at mode 0700 |
| 5. Decided and observed executable/model/family identities match | `test_codex_identity_is_read_from_the_event_stream`, `test_codex_reroute_supersedes_the_initial_session_model`, `test_codex_stream_without_a_model_is_unobservable`, `test_gemini_identity_is_read_from_session_metrics`, `test_gemini_envelope_without_metrics_is_unobservable`, `test_review_route_must_not_execute_in_the_authoring_family`, `test_execute_fails_when_the_observed_model_differs_from_the_decision`, `test_execute_fails_when_identity_cannot_be_observed` | PASS — a stream naming `gpt-4o` raises `IdentityMismatch` even though the decision says `gpt-5.6-sol`, proving the value is read and not copied; an unobservable stream raises `IdentityUnobservable` |
| 6. Unauthorized socket/HTTP/model endpoint/redirect/DNS rebinding denied and receipted | `test_raw_socket_connect_is_denied_and_receipted`, `test_direct_model_endpoint_is_denied` (7 hosts), `test_urllib_and_http_client_cannot_route_around_the_broker`, `test_connect_ex_is_also_brokered`, `test_retrieval_denials_are_receipted` (7 cases), `test_dns_rebinding_to_an_unpinned_address_is_denied`, `test_grant_does_not_leak_past_the_retrieval` | PASS — each asserts both the raised `EgressDenied.reason` and the matching `receipts.denials[-1]["denial_reason"]` |
| 7. Only the source retriever can egress, with full metadata | `test_only_the_retriever_may_egress_to_an_allowlisted_host`, `test_authorized_retrieval_records_full_metadata`, `test_unauthorized_retrieval_makes_no_connection` | PASS — a real loopback connection succeeds inside the retriever and the identical connection is denied outside it; the allow receipt carries resolved host/addresses, final URL, status, TLS protocol/cipher/subject, byte count, `bytes_sha256`, data class, and authorization id |
| 8. Model CLI launch fails capability proof when the boundary is absent or bypassed | `test_unproven_capability_fails_closed`, `test_execute_refuses_to_launch_without_a_capability_proof`, `test_launch_is_refused_when_no_host_sandbox_exists`, `test_capability_proof_is_satisfied_on_this_host` | PASS — an unenforced facet gives `runner.calls == []` and `total_reserved == 0`; with `sandbox_mechanism()` returning `none`, `build_sandboxed_argv` raises and `prove_workspace_isolation` reports `enforced is False` |
| 9. Malformed/multiple/trailing/schema-invalid JSON gets only the explicit retry | `test_only_one_clean_json_document_is_accepted` (8 cases), `test_envelope_extractor_requires_a_response_string`, `test_m01_must_emit_exactly_one_phase`, `test_malformed_result_gets_exactly_one_retry_then_fails`, `test_schema_invalid_result_gets_exactly_one_retry`, `test_the_single_retry_can_succeed`, `test_identity_mismatch_is_never_retried`, `test_attempt_ledger_refuses_a_third_attempt` | PASS — empty/fenced/two-document/trailing/NaN/duplicate-key/non-object all raise a distinct `failure_class`; malformed gets exactly 2 runner calls and 2 reservations; identity mismatch gets exactly 1 |
| 10. Attempt reserved before launch; receipts contain all required evidence | `test_attempt_is_reserved_before_the_process_starts`, `test_receipt_carries_every_required_piece_of_evidence`, `test_timeout_is_classified_and_receipted`, `test_process_runner_kills_a_hung_process_group` | PASS — the runner observes `ledger.total_reserved == 1` at call time (`reserved_at_call == [1]`); the receipt validates against `internal_execution_receipt.schema.json` with no null required field; a real 30s process is terminated at a 1s timeout |
| 11. Fake transports are test-only, no product roots or success terminals | `test_fake_transport_refuses_a_product_root`, `test_fake_transport_cannot_emit_a_terminal`, `test_fake_transport_returns_only_schema_valid_candidates` | PASS — `sandbox_root` outside the system temp directory raises `TransportError`; a canned response carrying `terminal: UNIT_ACCEPTED` raises `jsonschema.ValidationError` against the closed job schema |

Supporting tests beyond the eleven items: pinned Codex and Gemini argv
(`test_codex_argv_is_pinned`, `test_gemini_argv_is_pinned`), the Gemini effort rejection,
closed control-free schemas for all eight jobs, staged-input hash validation, undeclared
worker-write rejection, allowlisted worker environment, workspace destruction, and
absence of every forbidden production import.

## Generation 2 rework (N30 findings B-10 and B-8)

Two unrelated defects reported by `results/N30_UNIT_GRAPH.result.v1.md`. Nothing outside
this node's write set was touched; `nodes/`, `model_nodes.py`, `graph.py`, `state.py`,
`persistence.py`, `unit_graph.py` and `tests/runtime/test_plan26_unit_graph.py` were read
only.

### B-10 (this node's half): M03 could not declare the visuals D10 reads

`schemas/M03_write_unit_content.schema.json` constrained `unit_content` to exactly
`{unit_id, sections, evidence_references}` under `additionalProperties: false`, while
`nodes/visuals.py:109` (D10) reads `body.get("visuals", [])` off the admitted content
head. A model could therefore never write the key the visual denominator is compiled
from, so every unit's denominator was empty by construction.

`unit_content` now permits one further property, `visuals`: an **optional** array (a unit
that needs no picture omits it, and an empty list is legal), each entry an object closed
at exactly the five fields D10 actually reads — `role` and `kind` required,
`permitted_facts`, `authoritative` and `requests_authoritative_facts` optional. The shape
was taken from `nodes/visuals.py` itself (`classify_visual_brief` reads `kind` and
`authoritative`; `D10_COMPILE_VISUAL_BRIEFS` reads `role`, `permitted_facts` and
`requests_authoritative_facts`), not from prose, and
`test_m03_may_declare_the_visual_brief_fields_d10_reads` asserts the two sets are equal so
they cannot drift apart again.

`additionalProperties: false` is retained at every level, including inside a visual entry:
the closed-schema safety property is widened by one legitimate key, not weakened.
`assert_no_authoritative_fields` still passes on the whole schema and on a candidate
carrying visuals, so none of the five field names is readable as a control-plane claim.
`prompts/M03_write_unit_content.prompt.md` gains the matching instruction, stating that a
declaration is a request rather than a picture and that an authoritative kind is drawn
deterministically from the accepted domain, never by a model.

This is the smaller half of B-10. The larger half — pointing `CURRICULUM_CONTRACTS[0]` at
a per-unit content contract that admits these four keys — is N22's and is not in this
node's write set. That contract landed concurrently as `schemas/unit_content.schema.v1.json`
and declares the same four properties and the same five visual fields, so the two are
compatible in the direction that matters: a candidate M03 may emit is a candidate D09
admits. Verified directly — the sample above validates against both documents.

### B-8: the production transport had no capability surface

`CliTransport` exposed only `executable` and `execute`, while D03, D11, D13 and D14 call
five further methods on `RuntimeContext.transport_registry` — which
`graph.build_runtime_context` installs `CliTransport` as. A production context therefore
failed D03 immediately. All five are now real, and are exercised against the real local
toolchain rather than a double.

| Method | Caller | What it now really does |
|---|---|---|
| `prove_capability` | D03 (`nodes/inputs.py`) | one bounded local probe per capability from `CAPABILITY_PROBES`, whose key set is asserted equal to D03's `REQUIRED_CAPABILITIES`. No probe can reach a model. `renderer`/`rasterizer` invoke `pandoc`/`typst` and the four poppler utilities for their real versions; `persistence` writes, reads back and deletes a probe file under the output root and round-trips a real SQLite write; `logger` proves the evidence root is appendable; `retrieval` proves the egress broker is installed; `model_cli_identity` resolves and hashes both model CLIs. |
| `observe_executable` | D03 | `probe_executable` — the identity-observation logic this node already owned — resolved through `PATH`, hashed, and version-probed. D03 compares `path` and `sha256` against the frozen identities. |
| `render_unit` | D13 (`nodes/render.py`) | resolves the admitted content body from the content-addressed `ArtifactStore` by the `content` parent hash, composes the deterministic layout source, and renders the unit PDF with Plan 25's own pinned invocation (`pandoc --pdf-engine=typst -V mainfont=Helvetica`). Returns real `layout_sha256`/`pdf_sha256` recomputed from the bytes on disk. |
| `inspect_pages` | D14 (`nodes/render.py`) | rasterizes every page with `pdftoppm`, cross-checks the count against `checks.pdf_page_count`, hashes each page image, and reports per-page problems: blank-ink detection at `checks.py`'s own threshold, plus undersized and clipped text measured per page from one `pdftotext -bbox-layout` pass using `pdf_inspect`'s calibrated ink-box ratio and `MIN_POINT_SIZE`. |
| `render_deterministic_visual` | D11 (`nodes/visuals.py`) | resolves the admitted domain body by the brief's `domain_hash` and draws through `runtime/visual_maps.py`. `DETERMINISTIC_VISUAL_RENDERERS`'s key set is asserted equal to `nodes/visuals.AUTHORITATIVE_VISUAL_KINDS`, so every kind D10 routes to D11 has a renderer. Topology kinds resolve through `visual_maps.render_map`, which dispatches on the *domain's* own `map_kind` — the brief's word for the picture never overrides the domain. |

Every fault path raises (`RenderFault`, `CapabilityProofFailed`, `VisualMapError`,
`CheckFailure`) rather than returning a degraded result, so D11/D13/D14's `except
Exception` boundaries classify it `class=system, cause=tool`. The one deliberate exception
is a blank or illegible page, which D14 owns as a *product* finding: `rasterize_pages`
therefore does not use `checks.rasterize_and_check_nonblank`, which aborts the whole
inspection on the first blank page, and the blank audit runs per page instead.

`prove_capability` classifies a probe that raises `UnavailableExternalFact` as
`UNAVAILABLE_EXTERNAL_FACT`, which is the only result that reaches D03's
`PrerequisitePause`; anything else that fails is `MISSING`, which is a system failure. The
path is asserted by `test_a_probe_may_report_an_unavailable_external_fact`. See the
`no-production-probe-classifies-an-unavailable-external-fact` finding below for what this
does and does not claim.

### Verified

- 130 tests in this node's two files, all PASS (18 new).
- The whole ambient suite: 831 passed, 12 skipped.
- A real unit PDF: `test_render_unit_produces_a_real_pdf_from_the_admitted_content_head`
  admits a content artifact, renders it, and asserts the file begins `%PDF` and hashes to
  the value returned. `test_inspect_pages_inventories_and_inspects_every_page_by_hash`
  then rasterizes that same PDF and asserts a positive contiguous inventory with a
  64-character hash and an existing image per page.
- A real deterministic visual:
  `test_render_deterministic_visual_draws_from_the_admitted_domain` asserts the SVG names
  a traced point that appears only in the admitted domain, so the picture is drawn from
  the domain rather than from the brief.
- A real blank page: `test_a_blank_page_is_a_finding_on_that_page_not_a_transport_fault`
  compiles a genuine two-page PDF whose first page is empty and asserts page 1 is
  `unreadable` with a problem while page 2 is clean and the call does not raise.

## Findings

- **subprocess-network-host-pinning-unavailable** — owner: N13 (this node), carried
  forward for N50/N60 review. Evidence key:
  `capability_proof.facets.subprocess_network_scope.limitation`. Fingerprint:
  `sandbox-exec:no-remote-host-filter:darwin`. `sandbox-exec` cannot restrict outbound
  traffic by hostname, so the model CLI subprocess is confined to TCP 443/80 and UDP 53
  rather than to the provider's endpoints. Recorded as a non-required facet with an
  explicit limitation string rather than claimed as enforced. The Python process itself
  is fully brokered and direct model HTTP from Python is closed, so this does not admit
  an unauthorized transmission path from the controller; it bounds what the CLI child
  could reach if the CLI itself were compromised.
- **codex-json-flag-added-to-pinned-argv** — owner: N13 (this node), for N90 audit
  confirmation. Evidence key: `config/model_jobs.v1.yaml:identity_observation.codex`.
  Fingerprint: `spec-7.2:argv:--json`. Spec 7.2's argv block does not list `--json`, but
  the same section requires the executed identity to be extracted from a machine-readable
  Codex event, and codex-cli 0.147.0 offers no other machine-readable channel. `--json`
  is therefore appended immediately before the instruction, pinned by
  `test_codex_argv_is_pinned`, and declared in frozen configuration under
  `identity_observation` rather than hidden in code.
- **live-identity-shape-unconfirmed** — owner: N60_LIVE_PRODUCT_PROOF. Evidence key:
  `transport.observe_codex_identity`. Fingerprint: `codex:session_configured:model`.
  The Codex identity extractor is proven against fixtures of the event shapes the
  installed binary declares (`session_configured`, `thread.started`, `turn.started`,
  `model_reroute` all appear in the 0.147.0 binary's event vocabulary), but no live
  invocation was made, since live model calls are out of scope until N60. The extractor
  fails closed on an unrecognized stream, so an unexpected live shape yields
  `IdentityUnobservable` and a D03 failure, never a fabricated identity.

Added at generation 2:

- **no-node-persists-an-admitted-artifact-body** (BLOCKING for production) — owner:
  N22_DETERMINISTIC_NODES, with N40_CLI_CUTOVER. Evidence key:
  `runtime/langgraph_factory/artifacts.py:admit_version` has no caller in
  `runtime/langgraph_factory/nodes/`. Fingerprint:
  `plan26/n13/artifact-bodies-never-reach-the-store`.
  `render_unit` and `render_deterministic_visual` receive only head *hashes* — D13 is
  handed `parents = {domain, content, visuals}` and D11 a brief carrying `domain_hash` —
  so the only way either can reach the bytes it must render is the content-addressed
  store under the output root. `ArtifactStore.admit_version` writes those blobs, and no
  deterministic node calls it: D08/D09/D12 advance heads in LangGraph state only. In a
  live episode both methods therefore raise `RenderFault` ("no admitted <channel>
  artifact for <unit> at <hash>"), which D11/D13 classify as `class=system, cause=tool`
  — a loud, correct failure, not a silent one. This node's tests admit the artifacts
  themselves and then render for real, so the adapters are proven; what remains is that
  an admission node must persist the body it admits. This is stated as a named gap, not
  as a resolved item.
- **d13-cannot-embed-a-visual-in-the-unit-pdf** — owner: N22_DETERMINISTIC_NODES.
  Evidence key: `nodes/render.py:78` (`renderer(unit_id, parents)`) against
  `nodes/visuals.py:481-488` (D12's admitted visual candidate carries `stream`,
  `version`, `parent_hash` and `hash` and no body). Fingerprint:
  `plan26/n13/visual-assets-are-unreachable-from-d13`.
  The visuals stream has no artifact body and D13 passes no asset map, so the renderer
  cannot resolve the `asset_path` D11 produced. The unit PDF this node renders is
  therefore prose-only: real, hash-correct, and page-inspectable, but carrying none of
  the unit's pictures. Nothing in this node's write set can fix it — D13's own contract
  has to carry the assets.
- **no-production-probe-classifies-an-unavailable-external-fact** — owner: N13 (this
  node), for N50/N60 review. Evidence key: `transport.CAPABILITY_PROBES`. Fingerprint:
  `plan26/n13/pause-path-mechanism-only`.
  D03 pauses only on `UNAVAILABLE_EXTERNAL_FACT`. The classification mechanism exists,
  is reached by any probe raising `UnavailableExternalFact`, and is tested. But all six
  capabilities D03 requires are decidable locally — an absent renderer, a dead sqlite, an
  unhashable CLI are each a *system* failure, not an unavailable external fact — so no
  production probe returns it today. Rather than invent an external fact to make the
  path look exercised in production, it is recorded here: the pause path is reachable by
  construction and unreached by the current six probes.
- **egress-guard-is-installed-by-no-production-path** — owner: N40_CLI_CUTOVER. Evidence
  key: `EgressGuard.install` has no caller outside tests. Fingerprint:
  `plan26/n13/guard-never-installed`. The `retrieval` probe requires `guard.installed`,
  exactly as the pre-existing `prove_transport_capabilities` facet does, so on a context
  whose guard was never opened the probe correctly reports `MISSING` and D03 fails
  closed. Opening the guard belongs to the CLI entry point, which does not exist yet.
- **lesson_render-is-not-reusable-for-a-plan-26-content-body** — owner: N13 (this node),
  for N90 audit confirmation. Evidence key: `runtime/lesson_render.py:455` against
  `schemas/M03_write_unit_content.schema.json`. Fingerprint:
  `plan26/n13/lesson-render-is-bound-to-lab-schema-v4`.
  Spec 2.3 lists `lesson_render.py` as reuse/adapt. Every one of its template functions
  is bound to a block of `schemas/lab.schema.v4.json` and it raises `RendererError` on a
  field with no branch, so a Plan 26 `unit_content` body — `{unit_id, sections,
  evidence_references, visuals}` — cannot be passed to it at all. The layout source is
  therefore composed in `compose_unit_markdown` while the parts that *are* shape-neutral
  are reused: Plan 25's pinned pandoc/typst invocation, `pdf_inspect`'s calibrated
  legibility constants, `checks.pdf_page_count`, and the whole of `visual_maps`.


## Invalidated descendants

Generation 1 invalidated nothing. Generation 2 inverts two of N30's own blocker probes,
both of which are written to invert and are N30's to update:

- `test_blocked_the_production_runtime_context_has_no_capability_surface`
  (`tests/runtime/test_plan26_unit_graph.py`) asserts all five capability methods are
  absent from `CliTransport`. All five now exist, so it fails by design — its docstring
  reads "Inverts when `CliTransport` (or the context builder) exposes them."
  `test_the_production_transport_exposes_the_capability_surface_the_nodes_call` in this
  node's own file now carries the positive claim.
- `test_blocked_a_real_m03_content_head_can_declare_no_visual` asserts
  `"visuals" not in unit_content["properties"]`. It now fails, likewise by design
  ("Inverts when `unit_content` may declare visuals").

Neither could be executed here: every Plan 26 graph test module `importorskip`s
`langgraph`, which is not installed in this interpreter, so all ten skip. The inversion
is read off the assertions, not claimed as an observed failure.

No predecessor or sibling artifact was modified. `nodes/`, `model_nodes.py`, `graph.py`,
`routing.py`, `state.py`, `reducers.py`, `persistence.py`, `unit_graph.py` and
`tests/runtime/test_plan26_unit_graph.py` are byte-identical.

## Hashes

| Path | sha256 |
|---|---|
| plans/26_langgraph_curriculum_factory/implementation.graph.v2.yaml | 96e1948fb28eb6fbb327939bc2764eb9bae625606ca668f384126bf10ca617e8 |
| plans/26_langgraph_curriculum_factory/prompts/N13_transport_authorization.prompt.v2.md | 123d987b166da423f31d03b77f61b2be37ec175d3b90d6d3b091d0c9ac4e0f04 |
| plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md | c861b67efcf89bc3258d3bfeafaffcb263cee4b1540e417bd6de645d5ced88d5 |
| plans/26_langgraph_curriculum_factory/contracts/baseline.v1.md | 896a58b086288093aaa7648ef495907bb9c397fb9b4487d6f5f7f12f13a118af |
| plans/26_langgraph_curriculum_factory/contracts/digest_algorithm.v1.md | 063bd87666472b9382eb04404ee85ead966d37541651d813b32d0f54239ff8d0 |
| plans/26_langgraph_curriculum_factory/contracts/node_ownership.v1.md | c35f29db99127050831137f65583a9fd96ea338daa3785cdbc2ea2df53a51fb2 |
| plans/26_langgraph_curriculum_factory/contracts/result_record_schema.v1.md | d7e17b0b9fd9f6228d77a440a20a596505cd6a8a3a34aebd23e41e9fb59e10ad |
| plans/26_langgraph_curriculum_factory/contracts/shared_names_and_paths.v1.md | 7b77a0775139c9a26ec0688ca8f437e5494ea161f3a4e8c5f3b92bcdb2261cc7 |
| plans/26_langgraph_curriculum_factory/contracts/traceability_matrix.v1.md | edfc93d1bd412959133d523538150280785de8e9c3d4b0a4425b52e32fde244b |
| plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md | 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 |
| runtime/langgraph_factory/transport.py | 338bf915823ad2ba23ae3fdf95e8030e249a5ee794f14a565ea397b30f5475b3 |
| runtime/langgraph_factory/egress.py | 837410dad45a7deb8ef761e3636700a7fbde9f45ff6d97d8b4ba7b5c96383f52 |
| runtime/langgraph_factory/config/model_jobs.v1.yaml | 7b5d168c106ad428dc59600765a7c2960f16e7dc53e735d0ac232b42096e8a96 |
| runtime/langgraph_factory/schemas/M01_research_unit_sources.schema.json | cb745d064f9a8d2575c718613ac8512985f79f99a0297d6bd376d6a9075fa6f9 |
| runtime/langgraph_factory/schemas/M02_create_unit_domain_data.schema.json | 311b48b3b85c4fcc2e549a2becfe7b3879a38ec4be59c2ff3e39a3522a5e2232 |
| runtime/langgraph_factory/schemas/M03_write_unit_content.schema.json | f5773a2c54271778abf71a15a7b2cd41440f010ab2bf8c7bdcfc11d64e7912eb |
| runtime/langgraph_factory/schemas/M04_create_unit_visuals.schema.json | 6be7ad65b6ad2f9c1db7ac49cd80939e80b0c9a52c522e1a29a4d33aa534026e |
| runtime/langgraph_factory/schemas/M05_review_actual_unit.schema.json | fe7618d77e94d09f6de7ecc5da64bd354032396a2ebe1a19895413e29f743b51 |
| runtime/langgraph_factory/schemas/M06_repair_named_unit_artifact.schema.json | 8ec0f76dff14cc09e87f618086c44d5e5da6f3858886f75e61c9b9e822ed9a49 |
| runtime/langgraph_factory/schemas/M07_review_actual_workbook.schema.json | 5bd32065f188659176b7558044547f58e5f7ac21884d4df14e17e0172c2e1b7c |
| runtime/langgraph_factory/schemas/M08_repair_named_workbook_defect.schema.json | d43e442f8c41731cc3e0d32782eb2d34e4c259580a817a7cc126dbf4c8bedef6 |
| runtime/langgraph_factory/schemas/internal_authorization_receipt.schema.json | 99c08b818cd5268f7073ca9c38f215a433cb241985fadf6e0984e06a7f68fec1 |
| runtime/langgraph_factory/schemas/internal_capability_proof.schema.json | 9fa636cd87792ae3e9dcd68fc46b09c3ce3d73a5657a92762b1dabe439102640 |
| runtime/langgraph_factory/schemas/internal_egress_receipt.schema.json | fa75436422de72d7a7749dcc92741f87459e30b8f5245d7fb5fab6e93aece01d |
| runtime/langgraph_factory/schemas/internal_execution_receipt.schema.json | c1f34b029f7a3c97ccd8980b6b1d0e342ada3920f946269fd610e83f245d2de5 |
| runtime/langgraph_factory/prompts/M01_research_unit_sources.prompt.md | cd34146c6888ca416438d38c0d4c8b519a98bc51baeff65ecb8d54dcaef123b5 |
| runtime/langgraph_factory/prompts/M02_create_unit_domain_data.prompt.md | 6c59088990aa03c2f76a90dd4568bbb4d2e40a25234d4530c1ac2a4a71f8dadd |
| runtime/langgraph_factory/prompts/M03_write_unit_content.prompt.md | dfded39069111263b5cc9930c00d0362d900dd8731a2d8d013f6714d015c5d85 |
| runtime/langgraph_factory/prompts/M04_create_unit_visuals.prompt.md | 964a3d793ed7f98276ca6d8ad7818ad30a74643fc95367d5dcc0d8dba8ec0186 |
| runtime/langgraph_factory/prompts/M05_review_actual_unit.prompt.md | 013e1d5404311f642b799bc5ee6d71f8c1e7a82ed61ed7ee9532f0dafbd9766d |
| runtime/langgraph_factory/prompts/M06_repair_named_unit_artifact.prompt.md | a02a21c9c63013e3007e49aabf0406fbbc6ab3e8624c309195c6bc2517c8517e |
| runtime/langgraph_factory/prompts/M07_review_actual_workbook.prompt.md | 6c2c84591b8abd7a5dd6a037092ddc924048ee33ab927663a7a1d9663c8f34bd |
| runtime/langgraph_factory/prompts/M08_repair_named_workbook_defect.prompt.md | d182c8d80e80f98b6fbb5deff8cb7da573ec452d9c93314881d202432b3213ab |
| tests/runtime/test_plan26_transport.py | 8c67461bc0bc25134e61f1f237c23cd00283141ff9c6c53c0da8f493b316ff59 |
| tests/runtime/test_plan26_egress.py | e31bab0c2084a41928a0c5c9a96db9f87db18fc87a865e38723334658ac9bf1a |
