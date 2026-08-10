# Subscription-Only Model Execution Architecture Planning Log

Append-only record for the planning, QA, test-planning, and implementation-prompt
workflow. Existing entries must not be edited or removed; later corrections are
new entries.

## Objective

Replace the curriculum factory's live-model execution design — currently built around subprocess calls to a gemini CLI for worker execution and cross-family judging — with an architecture where content-generation prompts execute directly in Claude Code and QA/gate/judge steps execute via the installed Codex plugin, since the user has only Claude and ChatGPT Pro subscriptions and no billed API key exists or will exist for this project.

## Entry template

```text
### <UTC timestamp> — <agent/task>
- Action: <work performed>
- Paths touched: <paths, or none>
- Evidence/decision: <verification or decision rationale>
- Issues: <critical/high findings, blockers, or none>
```

## Entries

### 2026-08-09T20:20:48Z — plan_author
- Action: Authored implementation plan v1: retire the gemini-CLI subprocess mechanism (capability_cycle.py, gemini.py, resolve_gemini_settings.mjs) and correct session_bridge.py so worker execution is honestly attributed to the in-session Claude agent while the cross-family judge step becomes a real codex exec/review subprocess call under the user's ChatGPT Pro subscription, replacing the current silent ACCEPTED_PENDING_REVIEW bypass.
- Paths touched: plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md
- Evidence/decision: Read runtime/session_bridge.py, runtime/capability_cycle.py, runtime/capabilities.py, runtime/finalize_evidence.py, policy/routing/routing_policy.v1.yaml, plans/19_curriculum_factory_production_loop_closure/prompts/P0 and P1 in full; confirmed codex CLI installed and authenticated via chatgpt auth_mode (~/.codex/auth.json); confirmed codex exec/review non-interactive subcommands exist; grepped repo for all gemini references.
- Issues: None pending independent QA.

### 2026-08-09T20:31:02Z — plan_qa_round1
- Action: Independent QA round 1: CHANGES REQUIRED — 1 Critical, 2 High. Critical: plan's worker-is-Claude premise silently contradicted already-proven, already-approved policy/routes.v1.yaml worker route (codex exec) and plan 19 P1-T04/P2-T18/P3, which commit to codex exec as the authoring mechanism and charter retiring session_bridge.py. High: codex exec vs codex review named as interchangeable when only codex exec supports structured --output-schema/--output-last-message output. High: finalize_evidence.py's Gemini-shaped receipt field assumptions described as a path swap, not the schema rewrite they require.
- Paths touched: plans/20_subscription_only_execution_model/qa/plan_qa.v1.md
- Evidence/decision: Fresh subagent with repo access; live-verified codex --version, ~/.codex/auth.json auth_mode, a real codex exec --json --output-schema --output-last-message call, and codex review --help's lack of structured output support.
- Issues: 1 Critical, 2 High — plan revised in place to address all three before round 2.

### 2026-08-09T20:31:02Z — plan_author
- Action: Revised plan v1 in place: widened scope to explicitly and disclosedly supersede policy/routes.v1.yaml's worker route, policy/routing/model_registry.v1.yaml's OpenAI-only registry, and plan 19's P1-T04/P2-T18/P3 worker-adapter and session-bridge-disposition commitments (previously omitted from scope). Named codex exec --json --output-schema --output-last-message specifically as the QA-gate mechanism, dropped codex review as an option. Specified the exact receipt field contract finalize_evidence.py requires and added a verification step exercising it end-to-end.
- Paths touched: plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md
- Evidence/decision: Read policy/routes.v1.yaml and policy/routing/model_registry.v1.yaml in full to ground the widened scope precisely; incorporated QA round 1's live-verified codex exec flag behavior.
- Issues: None pending round 2 QA.

### 2026-08-09T20:40:12Z — plan_qa_round2
- Action: Independent QA round 2: CHANGES REQUIRED — 2 Critical, 0 High (1 High reclassified non-blocking observation). Critical: schemas/routes.schema.v1.json's status enum only allows UNPROVEN, so marking the required worker route unproven would trigger the file's own preflight rule to stop as META_SYSTEM_FAILURE every time -- the plan's fix was unimplementable as stated. Critical: reconciliation still missed plan 19 P2's Hard Constraint #1 (one invocation interface for all four roles, explicitly forbidding a separate code path for authoring) and P3's 25-state handler registry requirement, both of which directly conflict with the corrected architecture.
- Paths touched: plans/20_subscription_only_execution_model/qa/plan_qa.v2.md
- Evidence/decision: Fresh subagent with repo access; read schemas/routes.schema.v1.json and schemas/model_registry.schema.v1.json directly, confirmed the UNPROVEN-only enum; read plan 19 P2 and P3 prompt text in full for Hard Constraint #1 and the state-handler registry requirement.
- Issues: 2 Critical -- plan revised in place: added an IN_SESSION status to routes.schema.v1.json as explicit in-scope work (not a stop condition), pre-checked it doesn't affect capabilities.remove_unavailable_route, explicitly superseded P2 Hard Constraint #1 with a named two-interface model, and selected P3's migrate-into-controller-path disposition explicitly rather than leaving it open. Also tightened the non-blocking item.type observation.

### 2026-08-09T20:40:13Z — plan_author
- Action: Revised plan v1 in place, round 2: added explicit schemas/routes.schema.v1.json change (new IN_SESSION status) to step 2's scope with a pre-check against capabilities.remove_unavailable_route; added a required qa_gate route carrying the existing proven codex exec transcript; explicitly superseded P2's Hard Constraint #1 with a named two-interface model (in-session Claude for authoring, codex exec for research/review/revision/QA-gate) and named which test id needs retargeting; explicitly selected P3's 'migrate into the controller path' disposition over 'reduce to an internal adapter,' stating session_bridge.py's corrected logic becomes the per-state-handler implementation, not a standalone manual CLI; enumerated real Codex item.type values as an explicit requirement instead of a substring guess.
- Paths touched: plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md
- Evidence/decision: Read schemas/routes.schema.v1.json and schemas/model_registry.schema.v1.json in full; grepped repo for all UNPROVEN references to pre-check the schema change's blast radius; read plan 19 P2 and P3 prompt text in full to ground the two-interface and disposition-selection language precisely.
- Issues: None pending round 3 QA.

### 2026-08-09T20:45:59Z — plan_qa_round3
- Action: Independent QA round 3: CHANGES REQUIRED -- 2 Critical, 1 High (3 total). Round 2's two Criticals confirmed genuinely fixed. But round 2's own P2/P3 reconciliation fixes introduced two new/deepened Criticals: (1) the in-session interface's satisfaction of P2 hard constraints 2-5 is asserted 'in spirit' without stating the disposition of P2's adversarial containment tests, which structurally cannot pass against a no-subprocess interface; (2) step 4 says preserve session_bridge.finalize() exactly as-is while step 5 claims that same monolithic logic becomes the per-state-handler implementation P3 requires -- directly contradictory, and finalize() as written cannot satisfy P3's per-state checkpointing/revision requirements without a bigger redesign than scoped. Also: Claude model_registry entry's supports_pro_mode as 'not applicable' text is schema-invalid (field is strict boolean).
- Paths touched: plans/20_subscription_only_execution_model/qa/plan_qa.v3.md
- Evidence/decision: Fresh subagent; confirmed round 2 fixes hold (schema edit and remove_unavailable_route non-impact verified against real files); found new contradictions in the P2/P3 reconciliation text introduced during round 2's revision.
- Issues: STOP -- round-by-round Critical+High count: round 1 = 3, round 2 = 2, round 3 = 3. Per skill's convergence rule, a round that does not strictly decrease from the previous round halts the pipeline; round 3 regressed instead of converging. Halting before round 4; reporting to user rather than continuing to revise.
