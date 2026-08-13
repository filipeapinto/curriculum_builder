# GOAL

Correct the Plan 26 LangGraph Curriculum Factory specification before any new implementation run begins.

Claude is the specification author and repairer. GPT/Codex, reached only through the repository's `qa-gate-codex-run` Claude-Codex plugin workflow using its default app-server transport, is the independent tester and sole QA verdict authority. Claude must not issue its own pass verdict or substitute direct self-review for the plugin gate.

Start by reading these files completely:

1. `PSIM/19QMM26N0033/phase_2_conops/deliverables/final_assembly/run-010-visualization-improvement-03/postmortem.v1.md`
2. `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md`
3. `meta_prompt/curriculum.prompt.v1.md`
4. `plans/11_provider_correction/provider_correction.plan.v1.md`
5. `plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md`
6. `plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml`
7. `plans/22_graph_eng_evol_01/evolutionary_approach/evolution_graph_approach.v4.md`
8. `plans/25_curriculum_factory_graph/previous_plan.obs.v1.md`
9. `plans/25_curriculum_factory_graph/curriculum_factory.graph.v1.md`
10. `plans/26_langgraph_curriculum_factory/results/N60_LIVE_PRODUCT_PROOF.result.v1.md`
11. `plans/26_langgraph_curriculum_factory/results/N90_FINAL_AUDIT.result.v1.md`
12. `.claude/skills/qa-gate-codex-run/SKILL.md`

Create a new corrected specification at:

`plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v2.md`

Preserve `langgraph_curriculum_factory.spec.v1.md` byte-for-byte as historical Run 26 evidence. Do not edit, move, deprecate, or delete the v1 specification, Plan 26 receipts, patches, results, logs, runtime code, tests, policies, schemas, model-job configuration, or implementation graph during this task.

This is a specification-correction task only. Do not start, name, scaffold, or execute Run 27. Do not implement the provider migration. Do not obtain credentials. Do not change production code.

The v2 specification must:

- identify v1's Gemini selection as a specification defect and state exactly which v1 decisions v2 supersedes;
- establish an explicit authority hierarchy and complete lineage through Plans 20–22, Plan 25, the active meta-prompt, and current user direction;
- retain the compiled LangGraph factory, deterministic control authority, state, reducer, evidence, repair, persistence, unit/workbook, and terminal requirements unless a provider correction makes a specific textual adjustment necessary;
- replace the production provider profile consistently with subscription-backed Claude Code/Anthropic authoring and repair plus subscription-backed Codex/OpenAI independent judgment;
- keep generator and final judge in different model/provider families;
- prohibit Gemini CLI, Google/Gemini models, Gemini credentials, Gemini data transmission, billed API keys, raw model HTTP APIs, and hidden provider fallbacks;
- distinguish the Claude-Codex plugin used to independently QA this specification from the production runtime transport selected by the specification;
- define production subscription transports and observed/requested identity claims honestly, using only evidence the installed drivers can actually provide;
- revise all eight model-job assignments coherently rather than replacing isolated provider names;
- update every affected narrative section, table, diagram, provider authorization, staged-input rule, preflight rule, CLI contract, acceptance denominator, adversarial test, resolved decision, prerequisite, traceability entry, and checklist item;
- make preflight fail before curriculum transmission unless every required production driver proves executable identity, permitted authentication mode, usable subscription-backed access, required operation, and permitted data boundary;
- prohibit `ready: true` when any mandatory provider cannot authenticate;
- state that missing or unproven Claude/Codex subscription access is a truthful non-success state and never authorizes fallback;
- preserve the requirement for a real authorized one-unit proof and real full-workbook proof before activation;
- distinguish implementation conformance from product activation and from specification correctness;
- require the final audit to validate requirements lineage before spec-to-code conformance; and
- preserve all v1/Run 26 artifacts as historical evidence.

Do not silently invent product requirements. Where the repository's controlling sources genuinely conflict or cannot resolve a production transport detail, mark a precise `USER_DECISION_REQUIRED` item in v2 and stop that decision from flowing into implementation. Do not resolve uncertainty by copying the current runtime.

# TEST

Run these tests in order. Record exact evidence for every test. A test passes only on observable evidence; prose confidence is not evidence.

1. **SPEC-T00 — Historical immutability.** Prove the SHA-256 of `langgraph_curriculum_factory.spec.v1.md` is unchanged from the value recorded by N60/N90 (`44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6`). Prove no forbidden runtime, test, plan-result, receipt, patch, log, policy, schema, model-job, or implementation-graph file changed.
2. **SPEC-T01 — Authority and supersession.** Verify v2 explicitly orders governing user constraints, active meta-prompt requirements, Plans 20–22, Plan 25 product requirements, Plan 26 retained mechanics, and observed current code. Every retained or superseded provider decision must cite its source and disposition.
3. **SPEC-T02 — Gemini elimination.** Search the complete v2 document case-insensitively for `gemini`, `google`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and `gemini-3-pro-preview`. The only allowed occurrences are historical defect statements or explicit prohibitions. No occurrence may define a production job, provider, credential, authorization, endpoint, prerequisite, fallback, or activation remedy.
4. **SPEC-T03 — Subscription-only invariant.** Verify v2 prohibits billed API keys, raw model HTTP APIs, custom provider endpoints, and hidden fallbacks, and requires Claude Code and Codex to operate through the user's subscription-backed authentication.
5. **SPEC-T04 — Cross-family role mapping.** Verify all eight model jobs have one explicit role, provider family, subscription driver, input boundary, output schema, identity claim, and failure disposition. Content-generating/mutating roles must be Claude/Anthropic; independent judgment roles must be Codex/OpenAI. Any intentional exception must be separately justified and must preserve different-family final judgment.
6. **SPEC-T05 — Complete consistency.** Mechanically enumerate every provider/model/transport/authentication occurrence in v2 and inspect each one. Tables, prose, diagrams, acceptance denominators, adversarial cases, authorizations, prerequisites, resolved decisions, and checklists must agree with the same corrected profile.
7. **SPEC-T06 — Preflight truthfulness.** Verify v2 makes `ready: true` impossible when a mandatory model driver cannot authenticate or demonstrate permitted subscription-backed operation. Confirm the exact N60 false-ready condition is an explicit negative regression case.
8. **SPEC-T07 — Data-boundary correction.** Verify no Google/Gemini transmission authorization survives and that Claude/Codex staged inputs are explicit, least-privilege, content-aware, and approved before transmission.
9. **SPEC-T08 — LangGraph preservation.** Compare v1 and v2 structurally. Confirm provider correction does not silently redesign the compiled graph, deterministic routing/acceptance, reducers, checkpoint/resume, repair bounds, artifact immutability, unit/workbook denominators, or terminal authority.
10. **SPEC-T09 — Honest lifecycle.** Verify v2 states that specification approval precedes implementation remediation, implementation tests do not equal activation, and activation requires real authorized unit and workbook product proofs. Verify it does not start or authorize Run 27.
11. **SPEC-T10 — Historical regressions.** Verify v2 contains explicit controls for: Plan 25 false attribution; installed-CLI/authorization confusion; late provider feasibility; N60's false-ready preflight; unauthorized provider egress; production-topology reachability; descendant receipt invalidation; deterministic evidence; machine-readable status; and requirements-level final audit.
12. **SPEC-T11 — Independent GPT/Codex gate.** Invoke the repository's `qa-gate-codex-run` skill against the new versioned specification using the default app-server transport through the openai-codex/Claude-Codex plugin. Use `major` as the severity threshold, at most five rounds, and allow read-only grounding in every source named in GOAL plus the postmortem. The criteria are SPEC-T00 through SPEC-T10. Do not use Claude self-review, a Claude subagent, `/codex:transfer`, or an unstructured direct Codex call as the verdict.
13. **SPEC-T12 — Gate integrity verification.** After Codex returns `QA_PASSED`, run the gate's `verify` operation and require a witnessed, hash-chain-valid `QA_PASSED`. If the gate returns `QA_ERROR`, report the specification as `UNVERIFIED`; if it returns terminal `QA_FAILED`, run the gate's postmortem and report the diagnosis. Neither state is a pass.
14. **SPEC-T13 — Final change audit.** Prove the only intended repository changes are the new versioned specification, the specified correction-result record, and QA-gate-owned evidence/version artifacts. Report any pre-existing or unrelated dirty files without modifying them.

Codex's independent review must specifically attempt to falsify these claims:

- v2 fully removes Gemini as a production dependency rather than hiding it behind generic provider wording;
- v2 does not accidentally assign both generation and final judgment to OpenAI/Codex;
- v2 does not confuse the specification-review plugin with the production model transport;
- v2 does not claim subscription entitlement or executed-model identity that the drivers cannot prove;
- v2 does not weaken cross-family review, actual-page review, evidence denominators, or real-product activation requirements;
- v2 does not use the current implementation as authority to override user constraints; and
- v2 is sufficiently complete to govern a later remediation plan without inventing provider decisions.

# LOOP

1. Capture the clean/read-only baseline and run SPEC-T00 before writing v2. If v1's hash does not match the recorded value or protected files already overlap the intended write, stop with `BASELINE_MISMATCH`; do not repair history.
2. Draft v2 by copying the complete v1 structure and making a coherent specification-level correction. Do not perform a blind global provider-name replacement.
3. Run SPEC-T01 through SPEC-T10. On failure, edit only the new v2 specification and rerun the failed test plus every downstream test.
4. Start the independent `qa-gate-codex-run` session only after deterministic tests pass. The QA script owns its `QA/` directory; Claude must never write or edit files inside it.
5. If Codex returns `ROUND_OPEN`, address every criterion-defeating finding in a new higher-numbered specification version, then invoke the gate's `round` operation. Preserve version lineage; never edit a version already judged.
6. If a Codex finding is demonstrably outside the stated criteria, rebut it through the gate using source evidence. Do not lower the severity threshold or weaken a criterion to obtain a pass.
7. Continue for at most five Codex rounds. Stop immediately on `QA_ERROR`, integrity failure, unchanged-finding non-convergence, baseline drift, protected-file mutation, an unresolved provider decision, or exhausted rounds.
8. Only a successful gate `verify` result permits the final status `SPECIFICATION_CORRECTED_AND_INDEPENDENTLY_VERIFIED`. Claude may report that status but may not originate it.
9. Write a concise result next to the passing specification named `langgraph_curriculum_factory.spec_correction.result.v1.md`. It must include the final spec path and hash, predecessor v1 hash, deterministic test results, Codex session/round/turn identifiers, plugin transport/version evidence, gate verification output, remaining observations, exact changed files, and the explicit statement: `No Run 27 or implementation work was started.`
10. Stop after the corrected specification, independent QA evidence, and result record exist. Do not modify runtime code or begin implementation.
