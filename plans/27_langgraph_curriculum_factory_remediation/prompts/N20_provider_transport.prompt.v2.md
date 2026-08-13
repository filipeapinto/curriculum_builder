# GOAL

Implement the corrected v3 specification's complete provider-role and
transport profile across all eight production model jobs, using the exact
mechanics v3 proves live against the installed CLIs: an inline CLI-schema
projection (never a schema file path), stdin delivery of the canonical
authorized-input projection (never a staged-file read, since `--tools ""`
leaves no read tool), `--output-format stream-json --verbose` per-turn
identity extraction (never the aggregate `modelUsage` map), and an observed
tool/MCP-closure proof from the initialization event (never inferred from
`--tools`/`--setting-sources` alone).

This is the v2-package counterpart of `N20_provider_transport.prompt.v1.md`,
which reached `BLOCKED` (findings N20-F01 through N20-F09,
`plans/27_langgraph_curriculum_factory_remediation/results/N20_PROVIDER_TRANSPORT.result.v1.json`).
That v1 attempt's result and evidence are historical and untouched. This
prompt exists because the v1 attempt's blocking findings required both a
specification correction (now v3, §7) and an execution-package correction
(this graph): N20-F02 found that the frozen `anthropic`/`openai` authorization
classes v3 requires cannot be expressed while `egress.py`'s provider allowlist
is owned by a later node, so **this graph moves `runtime/langgraph_factory/egress.py`
and `tests/runtime/test_plan26_egress.py` into N20's write set**; N20-F01
found the bare whole-tree forbidden-reference scan unsatisfiable for any node
before the last one to touch a migration-affected test, so **this node's
verification uses `check_forbidden_production_refs.py --node N20_PROVIDER_TRANSPORT`**
instead of the bare whole-tree form N60 alone still runs.

The corrected v3 specification is the authority. Do not perform a blind
Gemini-to-Codex string replacement and do not preserve Codex as generator if
v3 assigns generation and repair to Claude/Anthropic. The specification-review
QA plugin is not automatically the production transport.

# TEST

1. Build a table from v3 for M01–M08 containing role, mutability, provider
   family, subscription driver, input boundary, output schema, identity
   claim, and failure disposition. Fail before editing if any field is
   unresolved.
2. Update transport, configuration, prompts, schemas, model nodes, policy,
   and direct tests consistently with that table.
3. Implement the four v3-corrected Claude transport mechanics as distinct,
   independently testable units in `transport.py`:
   a. a deterministic CLI-schema projection builder that strips `$schema` and
      rejects (never silently drops) an external `$ref`, computed once per
      canonical schema and proven byte-identical across repeated builds;
   b. stdin delivery of the JSON-encoded `{instruction, authorized_input_projection}`
      document to the `claude --print` subprocess, with no positional
      instruction argument and no reliance on the worker reading
      `authorized_input.json` from `--add-dir`;
   c. executed-identity extraction from `--output-format stream-json --verbose`
      per-turn assistant events' `message.model` (`parent_tool_use_id` null),
      never from the final envelope's `modelUsage` map; and
   d. a D03 capability check that inspects the stream-json initialization
      event's tool and MCP-server lists directly and fails closed if any tool
      other than structured output, or any authenticated/invokable MCP-server
      tool, is present — independent of what `--tools`/`--setting-sources`
      claim.
4. Move `egress.py`'s provider allowlist and `PROVIDER_DATA_CLASSES` to the
   `anthropic`/`openai`/`primary_source_hosts` classes v3 §7.4 requires,
   dropping the retired third-party class and its model-API hosts entirely.
   Update `internal_authorization_receipt.schema.json`'s provider enum in the
   same atomic step so no transport test can construct an authorization
   record `egress.py` would then reject. Update
   `tests/runtime/test_plan26_egress.py` to prove the new allowlist and to
   prove the dropped class is actually unreachable, not merely renamed.
5. Mechanically search production code/config/policy for the retired
   provider's commands, models, credentials, authorization, transmission,
   endpoints, and fallback, using
   `python3 plans/27_langgraph_curriculum_factory_remediation/controller/check_forbidden_production_refs.py --node N20_PROVIDER_TRANSPORT`
   — the node-scoped scan proves N20's own write set clean without depending
   on N30–N50's not-yet-migrated files. Historical fixtures outside this
   node's write set may remain until their owning node retires them; do not
   widen this node's write set to reach them.
6. Prove no billed API-key environment variable, provider SDK, direct HTTP
   model call, or custom endpoint can activate a production model route.
7. Prove generating/mutating jobs use Claude/Anthropic and independent
   judgment jobs use Codex/OpenAI, with a different-family final judge.
8. Prove every job validates staged inputs before transmission and validates
   its schema-bound output — using the unmodified canonical schema, not the
   CLI-schema projection — before admission.
9. Prove missing, failed, or identity-mismatched drivers fail closed without
   reassignment or fallback.
10. Record requested versus observed identity honestly. Do not claim executed
    model identity or subscription entitlement beyond what the driver
    exposes.
11. Run focused transport, authorization, egress, model-node, and policy
    tests.
12. Emit the schema-valid node result and an eight-job conformance report.

N20 owns the exact transport/model/config/prompt/schema, route/registry,
egress/authorization, and test paths declared in this graph — a superset of
v1's N20 write set, extended by exactly the two egress paths named above.
Preflight orchestration, the production CLI, topology/integration, evidence,
and their other tests belong to later nodes. Route a defect there rather than
widening this node's write set further.

N20 also owns retirement or complete correction of every predecessor test
file named in its write set. No active test may name, import, invoke, probe,
configure, simulate, authorize, or expect the retired provider path. Delete a
test file when its entire subject is retired; rewrite only genuinely
provider-neutral product assertions against the approved production
architecture.

# LOOP

On a failure, identify whether the owner is the job contract, driver, egress
allowlist, staged boundary, output schema, identity receipt, or policy/config
call site. Repair that owner and every affected direct test in the same
attempt. Rerun all N20 tests because an eight-job mapping and the
egress/authorization boundary are each atomic. Stop with `BLOCKED` rather than
inventing an unapproved production transport detail.
