# GOAL

Implement `N13_TRANSPORT_AUTH` after N00. Create the package-relative prompts,
schemas, frozen eight-job registry, CLI transports, capability proofs, structural
workspace isolation, and external-data authorization contract in spec section 7.

M01/M02/M03/M04/M06/M08 use `codex exec`; M05/M07 use `gemini`. Use no
LangChain chat wrapper, provider SDK, or direct model HTTP API. Observe executed
model/family/executable identity rather than asserting it. Stage only the exact
authorized projection and artifacts in a disposable isolated workspace.

# TEST

1. Exactly eight registered jobs; unknown job/family/model/schema/prompt fails.
2. Prompts resolve from `runtime/langgraph_factory/prompts/`, never cwd/root prompts.
3. Missing/expired/wrong-run/provider/data-class authorization makes zero calls.
4. Worker cannot read repository, output root, parent, sibling, history, or secrets.
5. Decided and observed executable/model/family identities must match.
6. Malformed/multiple/trailing/schema-invalid JSON is rejected with the one
   explicit policy retry only.
7. Attempt is reserved before launch; crash/timeout cannot create an uncounted call.
8. Receipts contain all specified hashes, bounded streams, timing, status, and authorization.
9. Fake transports are test-only and cannot use product roots or success terminals.

Write `results/N13_TRANSPORT_AUTH.result.v1.md` with registry, route/projection
tables, isolation/authorization evidence, commands, and hashes.

# LOOP

Patch one registry, prompt/schema, authorization, workspace, subprocess, parser,
identity proof, or receipt owner. Rerun tests 1–5 after every change. Stop if
identity/isolation cannot be proven or transmission can precede authorization.

