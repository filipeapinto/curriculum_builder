# GOAL

Implement `N13_TRANSPORT_AUTH` after N00. Create the package-relative prompts,
schemas, exact eight-job registry, CLI transports, capability proofs, structural
workspace isolation, external-data authorization, and enforceable runtime egress
policy required by spec sections 3.1, 7.2, and 7.4.

M01/M02/M03/M04/M06/M08 use `codex exec`; M05/M07 use `gemini`. Use no
LangChain wrapper, provider SDK, or direct model HTTP API. All Python-process
network operations must pass a code-owned egress broker: only the deterministic
source retriever may open HTTP(S), and only for the run-authorized locator/data
class. Model CLIs launch through a proved host sandbox/profile that denies
undeclared filesystem access and constrains egress to the required CLI provider
operation. If the host cannot enforce or observe this boundary, D03 fails.

# TEST

1. Exactly eight jobs; unknown job/family/model/schema/prompt fails before launch.
2. Prompts are package-relative; cwd/root prompt substitution fails.
3. Missing/expired/wrong-run/provider/data authorization makes zero calls.
4. Worker cannot read repository/output/parent/sibling/history/secrets.
5. Decided and observed executable/model/family identities match.
6. Unauthorized Python socket/HTTP use, direct model endpoint access, redirect to
   an unapproved host, and DNS rebinding attempt are denied and receipted.
7. Only the authorized source retriever can egress; allowlisted retrieval records
   resolved destination, status/TLS metadata, bytes hash, and authorization.
8. Model CLI launch fails capability proof when the required runtime sandbox/
   egress boundary is absent or bypassed.
9. Malformed/multiple/trailing/schema-invalid JSON gets only the explicit retry.
10. Attempt is reserved before launch; receipts contain all required evidence.
11. Fake transports are test-only and cannot use product roots/success terminals.

Write `results/N13_TRANSPORT_AUTH.result.v1.md` with registry, egress policy,
sandbox proof, negative network tests, commands, and hashes.

# LOOP

Patch one registry, authorization, egress broker, sandbox profile, workspace,
subprocess, parser, identity proof, or receipt owner. Rerun zero-egress and
bypass tests after every change. Stop if authorization can follow transmission,
direct model HTTP remains possible, or runtime isolation cannot be proved.

