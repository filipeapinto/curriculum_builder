---
name: sota-plan-create
description: Create or revise versioned, self-contained state-of-the-art research plans from the skill's reusable HTML asset. Use when Codex must design, clarify, review, or iterate a research plan; preserve every prior version; produce the next vN+1 artifact; or prepare an approved plan for handoff to sota-plan-execute.
---

# SOTA Plan Create

Create a rigorous, reviewable research plan. Iterate until its question, method, evidence flow, controls, outputs, and approval gate are clear. Never overwrite a plan version.

## Required references

1. Read `../sota-plan-execute/references/sota-family-contract.md` and use `assets/sota-plan.template.html` as the normative reusable structure and visual system. The asset is derived from the proven structure of `research/llm_failure_analysis/plan/sota_research.plan.v5.html`, but is self-contained and replaces that repository artifact as the drafting source. Do not copy study-specific content from the example.
2. Read `references/plan-contract.md` before creating or revising a plan.
3. Read `references/research-model-allocation-policy.v1.yaml` as planning input. Embed the selected allocation and controls in the plan so execution does not depend on the policy file.

If a referenced repository file is missing, stop and report the missing dependency.

## Workflow

1. Identify the research directory, primary question, intended decision, owner, evidence boundary, and originating issue or accepted report from the request and repository context.
2. Discover all existing plan versions. Use `scripts/next_plan_version.py <plan-directory> <plan-stem> <extension>` to select the next unused version.
3. For a new plan, create `v1`. For an iteration, read the latest version and create exactly `vN+1`.
4. Preserve the previous plan unchanged. Never rename, replace, edit, or delete it.
5. Before drafting the plan, compare the intended remediation scope with the originating issue and accepted report. If planning has introduced or materially changed a proposed skill, artifact, method, control, risk, acceptance criterion, or authority boundary, create the next preserved version of the issue or issue-confirmation report first. The updated issue must be self-contained, distinguish verified issue evidence from planning discoveries, and identify the plan versions that exposed the new scope. Do not silently broaden the plan beyond the issue record.
6. Copy and adapt `assets/sota-plan.template.html` into the new version. Replace every `{{PLACEHOLDER}}`, remove genuinely inapplicable conditional blocks only after recording why they are not applicable, and preserve the asset's accessible, responsive, and print-ready visual system unless the user or repository convention requires another presentation. A plan may strengthen but never remove, rename, weaken, relabel, or contradict family requirements.
7. Estimate execution cost from the proposed workload. For every ceiling, state its derivation, confidence, measurement mechanism, warning threshold, hard stop, and unavailable-measure behavior.
8. Separate deterministic operations, model judgment, and human authority. Apply the shared model-allocation policy, embed the selected allocation, and document justified deviations.
9. Assign every non-human research-team function to an installed role skill: `$sota-method-lead`, `$sota-evidence-review`, `$sota-synthesize`, `$sota-independent-challenge`, or `$sota-verify`. Embed each role's inputs, outputs, responsibility, and authority boundary in the plan.
10. Make the plan self-contained: it must hold every instruction, role assignment, allocation, budget, control, output, and acceptance rule needed for execution. A reader must not need the predecessor to understand or execute it. Never replace operative content with “unchanged,” “as before,” a diff, or a predecessor reference. Supporting evidence may be cited but must not become a second governing contract.
11. Verify that no `{{PLACEHOLDER}}` remains, then verify internal links, required sections, version labels, textual equivalents for meaningful diagrams, references, issue synchronization, responsive/print rendering, and standalone completeness.
12. Mark the result `awaiting approval` unless the human owner explicitly approves it. Planning does not authorize execution.
13. Report the new plan path, synchronized issue/report path when applicable, predecessor, material changes, validation results, and approval state.

## Iteration rules

- Treat feedback as input to a new version, not permission to modify an old version.
- Carry forward all operative content. Make requested changes traceable in a short version note that is not needed to interpret or execute the plan.
- Treat the predecessor as provenance, never as required context. Recompute and restate the complete current question, scope, method, roles, allocation, budget, controls, outputs, and acceptance rules.
- Synchronize the originating issue before the plan whenever planning discovers material scope not already recorded there. Preserve the previous issue/report version and do not present a proposed planning choice as a verified defect.
- Resolve contradictions and missing decisions in the plan itself; do not leave execution to guess them.
- Ask the human owner only when a decision materially changes scope, authority, budget, eligibility, or acceptance.
- Do not execute the research. Hand an approved plan to `$sota-plan-execute`.

## Output contract

Default to one self-contained HTML plan named `<stem>.vN.html` in the research effort's `plan/` directory. Use another format only when the user or repository convention requires it. The approved plan is the sole execution contract; do not require separate project budget, protocol, allocation, or control files. The plan must name its predecessor for provenance, but it must remain complete if every predecessor is unavailable. It must state whether it is draft, awaiting approval, approved, superseded, or rejected.
