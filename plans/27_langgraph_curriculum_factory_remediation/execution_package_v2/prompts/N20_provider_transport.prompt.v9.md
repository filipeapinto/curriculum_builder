# GOAL

Recovery authority: the controlling Run 27 prompt requires repair and cascade after a genuine live descendant exposes a defect. Graph v8 at SHA-256 `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1` and all of its results remain historical. All fresh admissions use graph v9 and `results/v9/`.

This generation additionally owns the deterministic curriculum-verifier transport used by D08. Execute the exact frozen argv without a shell, re-hash the entry point and every accept/reject fixture, run the full fixture suite and candidate under a no-network sandbox, and bind the receipt to the candidate hash. M02 receives hash-verified staged schema/calibration/fixture text but has no authority to declare a verifier verdict.

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
--graph execution_package_v2/implementation.graph.v9.yaml`**, explicitly
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
result and evidence at their shared path. `implementation.graph.v9.yaml`
fixes this at the graph level: `result_pattern`, and every node's own
result-write and evidence-root entries in `writes` — including N20's own —
move under `execution_package_v2/results/v9/` instead of
`execution_package_v2/results/`. This node's own write set below already
reflects that move. N20's write set, the two egress paths, and the
N20V2-F01 scan-scope fix (`retired_provider_test_scan.scan_roots` as the
explicit migration-owned union) are otherwise unchanged in substance from
v6. This prompt's own `--graph` values now name
`implementation.graph.v9.yaml` instead of `implementation.graph.v6.yaml`,
the same rename `implementation.graph.v9.yaml`'s own header applies to the
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
   `python3 plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/controller/scan_node.py --node N20_PROVIDER_TRANSPORT --graph plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v9.yaml`
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
