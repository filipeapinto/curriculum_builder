---
name: sota-plan-create
description: Create or revise versioned state-of-the-art research plans modeled on research/llm_failure_analysis/plan/sota_research.plan.v5.html. Use when Codex must design, clarify, review, or iterate a research plan; preserve every prior version; produce the next vN+1 artifact; or prepare an approved plan for handoff to sota-plan-execute.
---

# SOTA Plan Create

Create a rigorous, reviewable research plan. Iterate until its question, method, evidence flow, controls, outputs, and approval gate are clear. Never overwrite a plan version.

## Required references

1. Inspect `research/llm_failure_analysis/plan/sota_research.plan.v5.html` as the structural reference.
2. Read `references/plan-contract.md` before creating or revising a plan.
3. Read `references/research-model-allocation-policy.v1.yaml` as planning input. Embed the selected allocation and controls in the plan so execution does not depend on the policy file.

If a referenced repository file is missing, stop and report the missing dependency.

## Workflow

1. Identify the research directory, primary question, intended decision, owner, and evidence boundary from the request and repository context.
2. Discover all existing plan versions. Use `scripts/next_plan_version.py <plan-directory> <plan-stem> <extension>` to select the next unused version.
3. For a new plan, create `v1`. For an iteration, read the latest version and create exactly `vN+1`.
4. Preserve the previous plan unchanged. Never rename, replace, edit, or delete it.
5. Build the new plan using the contract. Keep it technology-neutral unless the research question requires a named implementation.
6. Estimate execution cost from the proposed workload. For every ceiling, state its derivation, confidence, measurement mechanism, warning threshold, hard stop, and unavailable-measure behavior.
7. Separate deterministic operations, model judgment, and human authority. Apply the shared model-allocation policy, embed the selected allocation, and document justified deviations.
8. Assign every non-human research-team function to an installed role skill: `$sota-method-lead`, `$sota-evidence-review`, `$sota-incident-analyze`, `$sota-synthesize`, `$sota-independent-challenge`, or `$sota-verify`. Embed each role's inputs, outputs, responsibility, and authority boundary in the plan.
9. Make the plan self-contained: it must hold every instruction, role assignment, allocation, budget, control, output, and acceptance rule needed for execution. Supporting evidence may be cited but must not become a second governing contract.
10. Verify internal links, required sections, version labels, textual equivalents for meaningful diagrams, and references.
11. Mark the result `awaiting approval` unless the human owner explicitly approves it. Planning does not authorize execution.
12. Report the new plan path, predecessor, material changes, validation results, and approval state.

## Iteration rules

- Treat feedback as input to a new version, not permission to modify an old version.
- Carry forward accepted content and make requested changes traceable in the new version.
- Resolve contradictions and missing decisions in the plan itself; do not leave execution to guess them.
- Ask the human owner only when a decision materially changes scope, authority, budget, eligibility, or acceptance.
- Do not execute the research. Hand an approved plan to `$sota-plan-execute`.

## Output contract

Default to one self-contained HTML plan named `<stem>.vN.html` in the research effort's `plan/` directory. Use another format only when the user or repository convention requires it. The approved plan is the sole execution contract; do not require separate project budget, protocol, allocation, or control files. The plan must name its predecessor and state whether it is draft, awaiting approval, approved, superseded, or rejected.
