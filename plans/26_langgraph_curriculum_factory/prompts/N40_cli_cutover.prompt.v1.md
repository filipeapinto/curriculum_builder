# GOAL

Implement `N40_CLI_CUTOVER` after N32. Make `python3 -m runtime.run_curriculum`
the sole production entry to the compiled Plan 26 LangGraph factory.

The CLI may parse/validate syntax, canonicalize paths, acquire the output lock,
prepare the episode invocation, build the graph once, invoke it, cross-check its
structured output against terminal/evidence ledgers, print one JSON object, and
map exit codes. It may not run product steps, inspect results to invent routing,
infer acceptance, or fall back to Plan 25/custom FSM/simulation/session bridge.

Implement exact preflight, one, all, and resume commands/collision rules from
spec section 16. Historical modules may remain only when unreachable from the
production import/call graph.

# TEST

1. Static and runtime call-graph proof shows one production graph builder/path.
2. CLI help exposes no legacy simulation/session-bridge/custom-controller path.
3. Mode mutual exclusions, arguments, canonical paths, collision/resume rules,
   stdout JSON, stderr diagnostics, and exit codes match the spec.
4. Preflight is read-only and cannot emit product success.
5. CLI code contains no product nodes, guards, joins, acceptance, or frontier selection.
6. Missing authorization/capability fails before transmission and never simulates.
7. Existing Plan 25 roots are readable history but refused for Plan 26 resume.
8. Production import audit rejects LangChain wrappers/provider SDKs/direct model HTTP.

Write `results/N40_CLI_CUTOVER.result.v1.md` with CLI/call-graph proof,
migration disposition, commands, and hashes.

# LOOP

Patch one parser, invocation helper, graph builder wiring, output verifier,
exit mapping, reachability test, or documentation owner. Do not delete user
history to pass scans. Stop if a second production path remains reachable.

