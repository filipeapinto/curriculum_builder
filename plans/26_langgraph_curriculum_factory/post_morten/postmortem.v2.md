# Run 26 LangGraph Curriculum Factory Postmortem v2

Status: **DRAFT — intended for iteration**

Date: 2026-08-13

Supersedes: `postmortem.v1.md` after independent QA review; v1 remains unchanged as the original draft.

Incident classification: **SPECIFICATION_DEFECT with requirements-lineage, implementation, harness, evidence, and audit-control failures**

## 1. Executive verdict

Run 26 must not be treated as production-ready and must not be unblocked by obtaining Gemini authentication.

The run implemented and extensively tested a substantial LangGraph curriculum factory, but its governing specification selected the wrong provider architecture. It required Codex authoring and Gemini review even though the repository's recorded user constraint requires subscription-only execution using Claude Code and ChatGPT/Codex, with no Gemini CLI or billed API key. The final verdict, `IMPLEMENTED_NOT_ACTIVATED`, was therefore correct only relative to a defective Plan 26 specification. It was not correct relative to the user's governing requirements.

The accurate disposition is:

> **SPECIFICATION_DEFECT — Plan 26's production provider topology contradicts governing user constraints. The activation verdict is invalid until the specification is corrected and independently re-reviewed.**

No Run 27 or implementation remediation should begin from this document. The first authorized action is specification correction. The verified LangGraph mechanics should be preserved where they remain compatible with the corrected specification.

## 2. Incident statement

The production LangGraph model-job configuration routes authoring, research, visual, repair, and workbook work to Codex, while routing actual unit and workbook review jobs `M05` and `M07` to the Gemini CLI using `gemini-3-pro-preview`:

- `runtime/langgraph_factory/config/model_jobs.v1.yaml`
- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md`

N60 could authenticate Codex through the user's ChatGPT subscription but could not authenticate Gemini. It consequently performed no live curriculum run. N90 then classified missing Gemini authentication as an external prerequisite and issued `IMPLEMENTED_NOT_ACTIVATED`.

That classification hid the real problem. Gemini was not an authorized external prerequisite. It was a specification error.

The repository's intended model-family split was already documented as:

```text
Claude Code / Anthropic subscription -> authoring and repair
Codex / OpenAI through ChatGPT subscription -> independent judgment
No billed API keys
No Gemini production route
```

Relevant authority evidence includes:

- `plans/11_provider_correction/provider_correction.plan.v1.md`
- `plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md`
- `plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml`
- `plans/22_graph_eng_evol_01/evolutionary_approach/evolution_graph_approach.v4.md`

## 3. Scope and evidence reviewed

This postmortem is based on a repository-wide textual inventory of 1,229 files and a focused review of 165 files containing Gemini, provider-family, cross-family, authentication, subscription, Plan 26, or related audit evidence. The review included:

- active and deprecated plans;
- repository prompts and meta-prompts;
- runtime and test code;
- Plan 26 specifications, QA criteria, graph contracts, patches, node results, receipts, evidence, and retained attempt logs;
- the 537-event Plan 26 audit stream;
- Git history for the relevant requirements and provider decisions; and
- repository-local Claude/Codex QA-gate instructions.

No `.agents` or `.codex` repository memory supplied a contrary provider instruction. `.claude` records documented tools and existing Gemini code but contained no user authorization selecting Gemini for this product.

### Reconstructed decision timeline

1. On 2026-08-01, the active meta-prompt recorded the general requirement for one different-family judge. It did not name Gemini.
2. On 2026-08-03, an agent implementation prompt selected Gemini after observing that its CLI was installed. The same implementation introduced the `gemini-3-pro-preview` default. No direct user instruction selecting Gemini was found.
3. The provider-correction work in Plan 11 already treated that provider path as retired rather than desired.
4. On 2026-08-10, Plans 20 and 21 explicitly documented the user's subscription-only constraint, rejected Gemini, and selected Claude authoring plus Codex judgment.
5. Plan 22 retained the subscription-only constraint and documented Claude-authored work with independent Codex review through the official plugin path.
6. Later on 2026-08-10, Plan 25 narrowed its predecessor observations to Plans 23 and 24, causing the provider correction to fall out of the immediate lineage.
7. On 2026-08-11, Plan 26 treated the stale Codex/Gemini runtime as an authoritative baseline, falsely attributed the split to Plan 25, and froze Gemini into the specification.
8. N00 verified that the Gemini executable existed but did not establish authorized usable access.
9. N60 finally made a real authentication probe, found Gemini unavailable, and executed no live curriculum proof.
10. N90 audited conformance to Plan 26, classified Gemini as an external prerequisite, and issued `IMPLEMENTED_NOT_ACTIVATED` without rechecking the higher-authority provider constraint.

## 4. What went wrong

Severity meanings:

- **Critical:** invalidates the governing specification, production architecture, or activation conclusion.
- **High:** defeats a required assurance property or allowed a major defect to survive until late audit.
- **Medium:** materially weakens reproducibility, auditability, or execution reliability.

QA consolidation applied in v2:

- v1 PM-05 (exact Gemini model), PM-09 (potential Google egress), and PM-10 (role inversion) are retained as sub-findings of Critical PM-01 rather than separately scored incidents.
- v1 PM-21 is merged into PM-22.
- PM-22 is reduced from Critical to High because its credential recommendation was not acted on and caused no transmission.
- The underlying facts, chronology, root-cause analysis, correction order, and acceptance criteria are unchanged.

### PM-01 — The Plan 26 provider architecture violated the explicit subscription-only requirement

Severity: **Critical**  
Status: **Open**

Plan 20 records that the user has Claude Code and ChatGPT Pro/Codex subscriptions and will never use a billed API key for this project. It explicitly states that the Gemini mechanism is broken and is not the fix. Plan 21 supersedes Plan 20 while preserving the same constraint: no production path may use a billed API key, raw model API, Gemini CLI, or hidden fallback.

Plan 26 nevertheless made Gemini a mandatory production dependency. This single root defect includes three derivative design choices that v1 listed separately:

- it froze the undocumented implementation default `gemini-3-pro-preview` even though no direct user or policy decision selected that model;
- it authorized Google to receive actual curriculum artifacts, PDFs, evidence, and rasterized pages if credentials became available—an unsupported but unrealized egress exposure; and
- it inverted the recorded role profile by assigning Codex to generation/repair and Gemini to judgment instead of Claude/Anthropic generation/repair and Codex/OpenAI judgment.

No evidence shows that any curriculum byte was transmitted to Google: Gemini authentication failed before a live curriculum run. The data-egress issue is therefore a hypothetical exposure created by the same unauthorized provider decision, not a separate incident.

Impact:

- The implementation cannot activate under the user's authorized access model.
- N60 was structurally destined to stop.
- The product was bound to an unapproved provider and exact model.
- The specification expanded the potential provider/data boundary without authorization, although no live Google transmission occurred.
- The proposed remedy of signing into Gemini or provisioning an API key contradicts the governing constraint.
- A naive Gemini-to-Codex substitution would still be wrong if Codex remained the generator, because generator and final judge must remain from different families.

Required correction:

- Require subscription-backed Claude/Anthropic for content-generating and repair roles and subscription-backed Codex/OpenAI for independent judgment.
- Reassign all eight model jobs coherently; do not perform a provider-name-only replacement.
- Prohibit Gemini commands, models, credentials, authorization fields, routes, transmission permissions, and fallbacks from the production contract.
- Re-derive and explicitly approve the Claude and Codex data boundaries.
- Prove model identity and entitlement only to the extent the actual subscription-backed drivers support.

### PM-02 — Plan 26 omitted controlling predecessor requirements from its authority set

Severity: **Critical**  
Status: **Open**

Plan 26 declared Plan 25 and the current runtime as its baseline. Its narrative considered Plans 23–25 but did not carry forward the provider-correction record in Plan 11 or the explicit provider constraints from Plans 20–22, even though those documents existed in the repository before Plan 26 was authored.

Plan 25's `previous_plan.obs.v1.md` only summarizes Plans 23 and 24. By inheriting that narrowed lineage, Plan 26 lost the subscription-only constraint and treated stale current runtime behavior as authority.

Impact:

- A lower-authority implementation artifact overrode a recorded user constraint.
- The specification had no complete requirements lineage.
- Subsequent traceability matrices were complete only against the already-defective Plan 26 document.

Required correction:

- Establish an explicit authority hierarchy: current user direction, subscription constraint, active meta-prompt, supersession chain, then implementation baseline.
- Include Plans 20–22 in the normative provenance and explicitly state what is retained or superseded.

### PM-03 — Plan 26 falsely attributed Gemini to Plan 25

Severity: **Critical**  
Status: **Open**

Plan 26 section 2.1 states that "The current Plan 25 prompts correctly separate Codex authoring/repair from Gemini review." The Plan 25 prompts and graph require different-family review but do not select Gemini. The Codex/Gemini split came from the then-current runtime, not from Plan 25.

Impact:

- The central provider decision was justified by a false provenance statement.
- Reviewers were led to treat Gemini as inherited policy instead of a new design choice.

Required correction:

- Remove the false attribution.
- Trace every model role to an actual governing source.
- Treat current code as an observed implementation state, never as proof of user authorization.

### PM-04 — “Different model family” was incorrectly converted into “Gemini”

Severity: **Critical**  
Status: **Open**

The active meta-prompt requires one judge from a different model family than the generator. It never says Gemini. Plan 26 section 20.1 claims Gemini was selected because of that cross-family requirement. This is a non sequitur: Claude/Anthropic authoring plus Codex/OpenAI judging satisfies the same rule using the authorized subscriptions.

Impact:

- A general independence constraint was mistaken for a provider mandate.
- An avoidable third provider and credential domain was introduced.

Required correction:

- State the invariant independently of vendor selection.
- Bind the current implementation profile to Anthropic generation and OpenAI/Codex judgment.

### PM-06 — Installed CLI presence was confused with provider authorization and feasibility

Severity: **High**  
Status: **Open**

The initial Gemini choice followed discovery that a `gemini` CLI binary was installed. N00 again recorded `which codex gemini` as a baseline fact. Binary presence does not establish user authorization, authentication, subscription entitlement, data-transmission permission, or product suitability.

Impact:

- The weakest possible capability signal was promoted into architectural authority.
- Feasibility was deferred until after implementation.

Required correction:

- Separate executable discovery, authentication, entitlement, authorization, and provider selection into distinct gates.
- Provider selection must precede implementation and be grounded in requirements, not PATH contents.

### PM-07 — Provider feasibility was tested too late

Severity: **High**  
Status: **Open**

Live provider authentication was not proven before the specification was frozen and implemented. N60, near the end of the run, was the first decisive live Gemini authentication gate.

Impact:

- Extensive implementation and test work accumulated behind an impossible activation dependency.
- The run paid the maximum possible cost before discovering a basic prerequisite failure.

Required correction:

- The corrected specification must place subscription identity, authentication, entitlement, and no-API-key checks before model-role implementation.
- Failure must block specification approval or implementation start, not merely activation.

### PM-08 — Preflight reported `ready: true` despite an unusable required model provider

Severity: **High**  
Status: **Open implementation/spec-conformance defect**

N60 records that the product's own preflight returned `ready: true` with all six capabilities passing, while a real Gemini call exited 41 because no credential existed. Plan 26 section 13 says missing Codex/Gemini credentials must make preflight report a failed capability and exit 3.

This is an implementation defect against Plan 26's own specification, not merely an environmental limitation. N90 nevertheless reported that no spec line lacked implementation evidence.

Impact:

- Operators received a false readiness signal.
- The final audit missed a direct spec-to-runtime contradiction.

Required correction:

- Define preflight semantics precisely and test real non-content authentication probes for every required model driver.
- `ready: true` must mean all required production providers can authenticate under the permitted subscription mode.

### PM-11 — The first implementation left the unit repair/acceptance topology unreachable

Severity: **High**  
Status: **Fixed during Run 26; retain as regression**

N90 found that D16–D23 were implemented and function-tested but never registered in `build_curriculum_factory_graph()`. N31's module deferred registration to N32 while N32 deferred it back. A real compiled run could not reach `D22_ACCEPT_UNIT` or `UNIT_ACCEPTED`.

Evidence:

- `plans/26_langgraph_curriculum_factory/patches/P-N31-001.patch.v1.yaml`

Impact:

- Function-level tests created false confidence about production reachability.
- Node ownership did not include responsibility for the integration seam.

Required prevention:

- Every model/deterministic subgraph owner must own or name exactly one integration owner.
- Acceptance must execute the production graph, not isolated node bodies.

### PM-12 — The first implementation left the workbook topology unreachable and claimed otherwise

Severity: **High**  
Status: **Fixed during Run 26; false-record issue remains historical**

D24–D32 and `register_workbook_topology()` existed, but the registration function was not called from the production graph builder. A real run could not reach workbook `COMPLETE`. The prior N32 result report incorrectly claimed the call was already present.

Evidence:

- `plans/26_langgraph_curriculum_factory/patches/P-N32-001.patch.v1.yaml`

Impact:

- A signed/receipted result contained a material false claim.
- Isolated topology tests did not prove production compilation.

Required prevention:

- Result claims must be mechanically re-derived from the exact receipted artifact.
- Production reachability tests must be mandatory before node admission.

### PM-13 — Frozen topology tests encoded stale implementation assumptions

Severity: **High**  
Status: **Fixed during Run 26; retain as regression/process lesson**

Correctly wiring D16–D32 broke tests whose hardcoded expectations predated the widened production topology. Patches P-N20-001, P-N20-002, P-N30-001, P-N31-003, and P-N32-002 were required to repair ownership and expectations.

Impact:

- Tests initially rewarded the incomplete graph.
- The write-set model prevented the responsible node from updating structurally affected tests.

Required prevention:

- Tests should derive expected production topology from the normative graph contract, not a predecessor's partial binding list.
- Shared integration tests need an explicit owner and invalidation rule.

### PM-14 — CLI cutover left stale Plan 25 tests outside the responsible node's write set

Severity: **High**  
Status: **Fixed during Run 26**

The Plan 26 CLI removed `parser_for` and legacy flags, but `tests/runtime/test_run_curriculum.py` still imported and tested the retired Plan 25 interface. N40 initially could not correct the test because it was outside N40's write set; P-N40-001 expanded ownership.

Impact:

- Downstream full-suite collection was blocked by an expected migration consequence.

Required prevention:

- Migration nodes must own the production interface and its direct compatibility/retirement tests as one atomic change.

### PM-15 — Descendant receipts were not invalidated after ancestor graph rework

Severity: **High**  
Status: **Open harness defect; N90 supplied compensating re-verification only**

N40, N50, and N60 receipts carried an older graph digest than the final graph after N20/N31/N32 rework. The manifest says descendants must be invalidated on ancestor rework, but the controller did not re-receipt them. N90 reran broad checks and treated the gap as non-blocking.

Impact:

- Receipt lineage does not fully prove that each descendant ran against the final ancestor state.
- A manual compensating audit replaced the controller's declared invalidation guarantee.

Required correction:

- The scheduler must automatically invalidate and rerun/re-receipt all digest-dependent descendants.
- Direct final-audit re-verification may supplement but must not erase the lineage defect.

### PM-16 — Required tests produced nondeterministic evidence and changed receipted files

Severity: **Medium**  
Status: **Open process/evidence defect**

Two N40 tests wrote fixed evidence files containing random temporary paths. Every full-suite rerun changed their bytes. N50 was instructed to capture and restore the old bytes; N90 treated the drift as informational under P-N90-001.

Impact:

- A required verification command could not reproduce its own receipted evidence.
- Later nodes needed a restoration workaround outside normal immutable-evidence semantics.

Required correction:

- Normalize volatile paths or write run-scoped evidence.
- Never require later nodes to restore stale evidence bytes merely to satisfy a hash gate.

### PM-17 — Harness status vocabulary and report formatting repeatedly caused false blocking

Severity: **Medium**  
Status: **Partly fixed; protocol defect remains**

The controller accepted only an exact bare `status: PASSED|NOT_AVAILABLE|BLOCKED` line, while node prompts and domain verdicts used richer forms such as bold Markdown, explanatory suffixes, or `ACTIVATED`/`IMPLEMENTED_NOT_ACTIVATED`. P-N31-002, P-N50-003, and P-N90-002 were needed to reconcile formatting.

The audit stream records nine `node_did_not_report_an_admissible_status` reasons.

Impact:

- Semantically valid work was repeatedly classified as blocked due to presentation syntax.
- The generic harness vocabulary and domain verdict vocabulary were conflated.

Required correction:

- Use a schema-bound machine-readable result record separate from human Markdown.
- Define an explicit mapping between node admission status and product verdict.

### PM-18 — Write-set and integration ownership were underspecified

Severity: **High**  
Status: **Partly repaired during Run 26; design issue remains**

The run required 14 immutable patches, several of which expanded write sets or moved responsibility because original node ownership excluded files necessarily affected by the node's own change. The N31/N32 mutual deferral is the clearest example, but N20, N30, N40, and N50 also required ownership correction.

Impact:

- Correct implementations were blocked from making necessary integration changes.
- Defects crossed node boundaries without a deterministic owner.

Required correction:

- Specify ownership for interfaces, call sites, integration tests, and shared outputs—not only module bodies.
- Add a pre-execution ownership-closure test.

### PM-19 — The execution controller was unstable and expensive to converge

Severity: **High**  
Status: **Historical; controller hardening required before reuse**

The 537-event audit stream contains:

- 41 attempt creations;
- 22 events with `status: BLOCKED`;
- 9 `controller_failed` events;
- 9 `claude_failed` reasons;
- 9 inadmissible-status reasons;
- 5 merge rollbacks;
- 3 write-set violations;
- graph-version and predecessor-checkpoint invalidations;
- repeated “predecessor not admissible” failures after completed work;
- one shared-output re-verification command exception;
- one concurrent-main-workspace conflict; and
- one merge completed after interruption.

The final handoff also disclosed that multiple controller subprocesses were killed by an outside mechanism and that completed work was later inspected and mechanically re-admitted.

Impact:

- Significant retry and judgment burden was moved onto the operator/agent.
- Merge-after-interruption and re-admission paths increased the risk of accepting artifacts not produced through the normal uninterrupted lifecycle.

Required correction:

- Make restart/recovery and shared-output admission first-class, deterministic controller operations.
- Record a machine-checkable reason and exact artifact binding for every re-admission.
- Eliminate result-format parsing as a source of retries.

### PM-20 — The final audit validated conformance to the wrong authority

Severity: **Critical**  
Status: **Open**

N90 performed a detailed spec-to-code and receipt audit but did not independently validate that the Plan 26 specification conformed to the user's governing requirements. Its traceability matrix began at Plan 26, so it could prove completeness while missing that Plan 26 itself was wrong.

Impact:

- A high-rigor audit produced a misleading top-level conclusion.
- “No implementation defect” was communicated despite the preflight contradiction and invalid provider requirement.

Required correction:

- Add a pre-implementation and final requirement-lineage audit performed by an independent model.
- The audit denominator must include explicit user constraints and predecessor supersession, not only the current spec.

### PM-22 — Final communication reframed a specification defect as missing user authentication

Severity: **High**  
Status: **Open record correction**

The formal Run 26 verdict was `IMPLEMENTED_NOT_ACTIVATED`, which correctly distinguished implementation status from activation. The defect was the explanation attached to that verdict: N60 and the final handoff described Gemini authentication as the remaining external prerequisite even though the recorded user constraint rejected Gemini as a production provider.

N60 acknowledged that only Claude Code and ChatGPT Pro/Codex subscriptions exist and no billed API key exists, yet suggested signing into Gemini or provisioning `GEMINI_API_KEY` as possible resolutions. The recommendation was never acted on, and no evidence shows that credentials were acquired or data transmitted. This is therefore a High-severity disposition and communication failure, not a separate Critical provider incident.

The 1,246 passing tests remain valid implementation evidence, but they do not cure this framing: N60 produced no curriculum artifact and ran neither the live one-unit nor full-release proof.

Impact:

- A requirements conflict was presented as a user credential task.
- “Built and verified, but awaiting Gemini authentication” directed the next step toward an explicitly rejected provider/billing model.
- Test volume could be read as stronger product evidence than the absent live proof justified.

Required correction:

- Supersede the result interpretation: the remaining blocker is specification selection, not missing user action.
- State implementation-test success, specification correctness, and product activation as three separate conclusions.
- Do not recommend credentials for a provider that the governing requirements do not authorize.

### PM-23 — “Independent Gemini review” overstated what provider diversity proves

Severity: **Medium**  
Status: **Open wording/assurance issue**

The repository research supports avoiding same-family self-review but also warns that cross-family judges can remain highly correlated. Plan 26 frequently treated a different provider as equivalent to independence.

Impact:

- Assurance language exceeded the evidence.

Required correction:

- Describe the control accurately as cross-family separation, not complete independence.
- Preserve deterministic checks and evidence denominators as primary safeguards.

### PM-24 — Historical evidence and active authority were not clearly separated

Severity: **High**  
Status: **Open**

Plan 26 relied on the current runtime's Codex/Gemini behavior while saying earlier plans remained historical. In practice, historical implementation state was promoted to active authority, while later corrective plans were omitted.

Impact:

- “Existing code” silently outweighed explicit corrective design decisions.

Required correction:

- Label every source as normative, superseded, historical evidence, or implementation observation.
- Require explicit approval for any new spec that reverses a normative provider constraint.

## 5. Root-cause analysis

### Primary root cause

Plan 26 lacked a requirements-authority gate. Its author treated the current Plan 25 runtime's provider split as a valid inherited requirement, then built a complete internal traceability system below that mistaken assumption.

### Contributing causes

1. Plan 25's predecessor observation chain omitted Plans 20–22.
2. The installed Gemini CLI created a false signal of availability.
3. The generic cross-family requirement was conflated with a Gemini mandate.
4. Provider authentication and subscription entitlement were deferred until N60.
5. Independent QA began from the Plan 26 spec instead of independently checking the spec's provenance.
6. Function-level and private-builder tests did not initially prove reachability through the production compile point.
7. Node write sets omitted integration seams and affected tests.
8. Human Markdown status parsing was used as a controller protocol.
9. Mutable/nondeterministic evidence interacted badly with hash-based receipts.
10. Final communication emphasized test volume and internal conformance over absent live product proof.

### Why the controls did not catch it earlier

The controls were strong below the specification boundary and weak above it. Hashing, receipts, topology checks, deterministic guards, and regression tests can prove that code faithfully implements a specification. They cannot prove that the specification represents the user's intent unless user constraints and supersession lineage are part of their denominator.

## 6. What remains valid and should be preserved

This incident does not show that all Run 26 work is unusable. Subject to the corrected specification and a fresh audit, the following appear reusable:

- the single compiled LangGraph production-path objective;
- typed state and code-owned reducers/guards;
- persistence, checkpoint, resume, immutable artifact, and terminal machinery;
- deterministic denominators and exact coverage checks;
- bounded targeted repair and invalidation/retest concepts;
- unit and workbook topology after the D16–D32 wiring corrections;
- isolation and schema-bound model-job concepts; and
- the broad regression/adversarial test corpus.

No prior receipt should be used to claim provider correctness or activation. Provider-dependent tests, preflight, transport configuration, authorization contracts, model-role assignments, and activation evidence must be re-derived after specification correction.

## 7. Required order of operations

1. Preserve Plan 26 v1, its receipts, patches, logs, and evidence as historical audit material.
2. Mark `IMPLEMENTED_NOT_ACTIVATED` as superseded by `SPECIFICATION_DEFECT` at the requirements level.
3. Produce a corrected specification version; do not start Run 27.
4. Have Claude author the correction under the GOAL/TEST/LOOP prompt in `prompts/`.
5. Have GPT/Codex independently test the corrected specification through the Claude-Codex plugin QA gate. Claude must not self-approve.
6. Iterate the specification until the independent gate passes or reports an honest terminal failure.
7. Present the corrected, independently verified specification for user approval.
8. Only after approval, decide the identifier and scope of an implementation remediation run.

## 8. Corrected-specification minimum acceptance criteria

The corrected specification is not acceptable unless all of the following are explicit and internally consistent:

1. It carries forward the subscription-only user constraint and cites its authority.
2. It contains no production Gemini CLI, Google/Gemini model, Gemini credential, Gemini data-transmission authorization, or silent fallback.
3. Claude/Anthropic performs content-generating and repair roles through an authenticated subscription-backed Claude Code mechanism.
4. Codex/OpenAI performs independent review/judgment through authenticated ChatGPT subscription access.
5. Generator and final judge remain from different provider/model families.
6. No billed API key or direct model HTTP API is permitted.
7. Preflight proves executable identity, authentication mode, subscription entitlement to the extent observable, prohibited API-key absence, required transport operation, and permitted data boundaries before content transmission.
8. Missing or unproven subscription access produces an honest non-success state without fallback.
9. All eight model jobs have a complete revised role/driver/model-policy mapping.
10. Every provider-specific statement, table, diagram, acceptance denominator, adversarial case, CLI contract, authorization rule, and resolved decision is updated consistently.
11. Existing LangGraph topology and deterministic product authority remain unchanged unless a documented incompatibility requires a separately approved change.
12. The spec distinguishes implementation proof from live product activation.
13. A real authorized one-unit and full-workbook proof remains required before activation.
14. The final audit begins from user requirements and supersession lineage, not merely the corrected spec.
15. The original v1 specification and Run 26 evidence remain immutable historical records.

## 9. Open corrective-action register

| ID | Action | Priority | Owner | State |
|---|---|---:|---|---|
| CA-01 | Author a corrected Plan 26 specification version with complete authority lineage | P0 | Claude | Not started |
| CA-02 | Independently review the corrected specification through GPT/Codex via the Claude-Codex plugin gate | P0 | Codex | Not started |
| CA-03 | Obtain user approval of the corrected specification before implementation | P0 | User | Not started |
| CA-04 | Replace the final Run 26 requirements-level disposition with `SPECIFICATION_DEFECT` | P0 | Specification owner | Not started |
| CA-05 | Define the later remediation-run scope only after spec approval | P1 | Planner | Blocked by CA-03 |
| CA-06 | Correct preflight semantics and tests in the later implementation run | P1 | Implementation owner | Blocked by CA-03 |
| CA-07 | Correct provider roles, transports, authorization, and model-job configuration in the later implementation run | P1 | Implementation owner | Blocked by CA-03 |
| CA-08 | Fix controller descendant invalidation and receipt regeneration | P1 | Harness owner | Not started |
| CA-09 | Make test evidence deterministic and run-scoped | P1 | Test/evidence owner | Not started |
| CA-10 | Replace Markdown status parsing with schema-bound controller results | P1 | Harness owner | Not started |
| CA-11 | Add production-compile reachability and integration-ownership gates | P1 | Graph/harness owner | Not started |
| CA-12 | Rerun authorized live unit/full-product proof only after implementation remediation | P0 for activation | Independent release owner | Blocked by CA-03 and remediation |

## 10. Evidence index

Primary requirements and lineage:

- `meta_prompt/curriculum.prompt.v1.md`
- `plans/05_simplification/research/conclusions.v1.md`
- `plans/05_simplification/research/verification.v1.md`
- `plans/05_simplification/prompt/implement_curriculum_runtime.prompt.v1.md`
- `plans/11_provider_correction/provider_correction.plan.v1.md`
- `plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md`
- `plans/21_graph_engineered_subscription_execution/graph_engineered_subscription_execution.plan.v1.yaml`
- `plans/22_graph_eng_evol_01/evolutionary_approach/evolution_graph_approach.v4.md`
- `plans/25_curriculum_factory_graph/previous_plan.obs.v1.md`

Plan 26 specification and implementation:

- `plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md`
- `plans/26_langgraph_curriculum_factory/qa_criteria.v3.md`
- `runtime/langgraph_factory/config/model_jobs.v1.yaml`
- `runtime/langgraph_factory/transport.py`
- `runtime/langgraph_factory/graph.py`
- `runtime/run_curriculum.py`

Run 26 result and process evidence:

- `plans/26_langgraph_curriculum_factory/results/N00_BASELINE_FREEZE.result.v1.md`
- `plans/26_langgraph_curriculum_factory/results/N60_LIVE_PRODUCT_PROOF.result.v1.md`
- `plans/26_langgraph_curriculum_factory/results/N90_FINAL_AUDIT.result.v1.md`
- `plans/26_langgraph_curriculum_factory/results/v3/audit/events.v1.jsonl`
- `plans/26_langgraph_curriculum_factory/patches/`
- `plans/26_langgraph_curriculum_factory/results/v3/logs/`

Relevant Git chronology:

- `c87dd8e` — active meta-prompt adds different-family judge rule; no Gemini mandate.
- `868337e` — runtime implementation introduces Gemini and `gemini-3-pro-preview`.
- `d65f196` — Plans 20/21 record subscription-only Claude-author/Codex-judge correction and reject Gemini.
- `0d6d9a2` — Plan 22 retains subscription-only constraints and Claude/Codex plugin review.
- `fc2ec5a` — Plan 25 narrows predecessor observations to Plans 23/24.
- `ac7ff3a` — Plan 26 freezes the Codex/Gemini topology and misattributes it to Plan 25/meta-prompt.

## 11. Revision notes

### v2 — 2026-08-13

- Incorporated independent QA feedback on severity and double-counting.
- Consolidated v1 PM-05, PM-09, and PM-10 into PM-01.
- Consolidated v1 PM-21 into PM-22 and reduced PM-22 from Critical to High.
- Preserved all underlying facts and the specification-first corrective sequence.
- Preserved v1 unchanged for audit.

### v1 — 2026-08-13

- Initial evidence-backed incident reconstruction.
- Records specification, provider, preflight, topology, harness, receipt, evidence, audit, and communication failures.
- Establishes that specification correction and independent review must precede any Run 27 decision.

