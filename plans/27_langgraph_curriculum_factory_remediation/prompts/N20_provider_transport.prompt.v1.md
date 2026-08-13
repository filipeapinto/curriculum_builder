# GOAL

Implement the corrected specification's complete provider-role and transport
profile across all eight production model jobs.

The corrected v2 specification is the authority. Do not perform a blind
Gemini-to-Codex string replacement and do not preserve Codex as generator if v2
assigns generation and repair to Claude/Anthropic. The specification-review QA
plugin is not automatically the production transport.

# TEST

1. Build a table from v2 for M01–M08 containing role, mutability, provider
   family, subscription driver, input boundary, output schema, identity claim,
   and failure disposition. Fail before editing if any field is unresolved.
2. Update transport, configuration, prompts, schemas, model nodes, policy, and
   direct tests consistently with that table.
3. Mechanically search production code/config/policy for Gemini/Google commands,
   models, credentials, authorization, transmission, endpoints, and fallback.
   Historical fixtures may remain only when clearly isolated and never imported
   or dispatched by production.
4. Prove no billed API-key environment variable, provider SDK, direct HTTP model
   call, or custom endpoint can activate a production model route.
5. Prove generating/mutating jobs use Claude/Anthropic and independent judgment
   jobs use Codex/OpenAI, with a different-family final judge.
6. Prove every job validates staged inputs before transmission and validates its
   schema-bound output before admission.
7. Prove missing, failed, or identity-mismatched drivers fail closed without
   reassignment or fallback.
8. Record requested versus observed identity honestly. Do not claim executed
   model identity or subscription entitlement beyond what the driver exposes.
9. Run focused transport, authorization, model-node, and policy tests.
10. Emit the schema-valid node result and an eight-job conformance report.

N20 owns only the exact transport/model/config/prompt/schema, route/registry,
and test paths declared in the graph. Egress, preflight, CLI, topology, evidence,
and their tests belong to later nodes. Route a defect there rather than widening
this node's write set.

N20 also owns retirement or complete correction of every predecessor test file
named in its write set. No active test may name, import, invoke, probe, configure,
simulate, authorize, or expect the retired provider path. Delete a test file when
its entire subject is retired; rewrite only genuinely provider-neutral product
assertions against the approved production architecture. The zero-occurrence
active-test scan must pass. N60's full `tests/runtime` denominator must collect
without the retired modules or CLI.

# LOOP

On a failure, identify whether the owner is the job contract, driver, staged
boundary, output schema, identity receipt, or policy/config call site. Repair
that owner and every affected direct test in the same attempt. Rerun all N20
tests because an eight-job mapping is atomic. Stop with `BLOCKED` rather than
inventing an unapproved production transport detail.
