# Run 27 N20 recovery plan v1

## Objective

Recover Run 27 from the valid `N20_PROVIDER_TRANSPORT` `BLOCKED` result without
weakening the zero-retired-provider requirement, crossing node write boundaries,
rewriting evidence, or inventing a production transport.

## Authority and preservation

1. Preserve the current Run 27 v1 graph, N00–N20 results, and all evidence as an
   immutable failed attempt. Do not edit them in place.
2. Preserve Plan 26 historical artifacts. They are evidence, not active production
   authority and are excluded from the active-tree zero-occurrence scan.
3. Create only versioned correction artifacts. The corrected specification, execution
   graph, prompts, approval schema, approval contract, results, and evidence must not
   reuse v1 paths that already carry evidence.

## Correction design

### 1. Correct the specification

Create Plan 26 specification v3 from the independently verified v2, with these bounded
changes only:

- Active specification text contains zero literal retired-provider or retired-family
  identifiers. Historical v1/v2 remain untouched.
- Claude receives the exact canonical authorized-input projection in the prompt sent
  over stdin. It receives no filesystem tools; `--tools ""` remains mandatory.
- Claude structured output uses a deterministic CLI-schema projection passed as inline
  JSON to `--json-schema`. The projection removes unsupported dialect metadata and
  rejects external references. The unmodified canonical schema remains the admission
  authority and is applied again after execution.
- Receipts bind the canonical input digest, canonical schema digest, CLI-schema
  projection digest, exact argv policy, requested identity, and observed identity.
- The invocation uses machine-readable stream events and extracts executed identity
  from the top-level assistant turn, not from an aggregate usage map.
- Empty tools plus strict empty MCP configuration are checked from the initialization
  event. Any exposed model-accessible tool other than structured output fails closed.

No graph topology, reducer, retry, denominator, persistence, repair, or terminal rule
may change in the specification correction.

### 2. Correct the Run 27 execution package

Create a v2 execution package bound to specification v3:

- Use a new result/evidence root so the v1 N00–N20 attempt remains byte-for-byte intact.
- Extend the forbidden-reference checker with `--node <NODE_ID>`. Node mode derives its
  scan set from that node's declared active production/test writes. N20–N50 use node
  mode. N60 alone runs the complete active-tree scan.
- Move `runtime/langgraph_factory/egress.py` and
  `tests/runtime/test_plan26_egress.py` from N30 ownership to N20 ownership. N20 owns the
  atomic provider registry, transport authorization classes, model endpoint denial,
  authorization receipt schema, transport, model-job configuration, and their direct
  tests. N30 consumes that boundary read-only and owns capability/preflight/CLI wiring.
- Make every active file belong to exactly one write set. Structural validation must
  reject overlap or an unowned required change.
- N20 verification runs its focused suites plus `--node N20_PROVIDER_TRANSPORT`.
  N30–N50 do likewise for their node IDs. N60 runs both full test denominators and the
  complete active-tree zero-occurrence scan.
- N00 v2 binds the exact specification-v3 digest, execution-graph-v2 digest, both
  independent QA verification digests, the model/effort decision already supplied by
  the user, and explicit user approval.

### 3. Validate before implementation

Before any production edit:

1. Validate the v2 execution graph, schemas, paths, ownership, dependencies, and
   verification commands.
2. Prove the node-scoped scanner fails on an owned seeded violation, ignores a
   later-node file during an earlier node, and the N60 scan detects both.
3. Prove the CLI-schema projection is deterministic and that all eight projected
   schemas are accepted by the installed Claude CLI using content-free probes.
4. Prove stdin input works with empty tools and that no filesystem or MCP tool is
   model-accessible.
5. Run independent Codex QA on specification v3 and the v2 execution package using the
   default app-server transport.
6. Stop and return the exact passing digests to the user. Do not self-approve.

## Restart and execution

After explicit user approval of the exact passing digests:

1. Start the v2 run at its new N00 approval gate.
2. Execute nodes sequentially. N20 performs the atomic provider/authorization migration.
3. Advance only on schema-valid admitted results; preserve every attempt.
4. N60 proves zero retired-provider identifiers across the complete active tree and runs
   the full regression denominators.
5. N70/N80 may report `NOT_AVAILABLE` when subscription-backed live proof is unavailable;
   they must never simulate activation.
6. Only N90 may issue the terminal result.

## Required stop conditions

Stop without production edits if the corrected specification or v2 execution package
fails independent QA, if user approval does not bind the exact passing digests, or if a
new cross-node ownership conflict appears. During implementation, emit an honest blocked
result rather than widening scope or weakening a check.
