---
name: plan-createe
description: Create or revise a versioned, implementation-ready solution plan from an issue report. Use when Codex must translate documented findings, causes, corrections, risks, and acceptance tests into a bounded remediation plan; do not use to investigate an unverified issue or execute the resulting plan.
---

# Plan Createe

Turn an issue report into a self-contained plan that another agent or team can implement after the required human approval. Preserve every issued plan version and keep planning separate from implementation.

## Required resources

1. Read [references/plan-contract.md](references/plan-contract.md).
2. Use [assets/solution-plan.template.html](assets/solution-plan.template.html) as the minimum HTML structure. Adapt sections to the issue; do not retain placeholder text.
3. Use `scripts/next_plan_version.py <plan-directory> <plan-stem> <extension>` to select the next unused output path.
4. Run `scripts/validate_plan.py <plan-path> [issue-report-path]` before delivery.

If a required resource is missing, stop and report the missing dependency.

## Workflow

1. Read the entire issue report and resolve repository-relative links when they materially support the plan. Record the source path, version or digest if available, review state, findings, root causes, recommended corrections, acceptance tests, risks, open decisions, and authority boundary.
2. Confirm that the input is an issue report with enough evidence and remediation direction to plan. Do not silently investigate uncertain claims. Classify unsupported or pending claims as assumptions or prerequisites.
3. Choose the repository's existing plan location and naming convention. Otherwise derive an issue slug by removing the issue report extension plus trailing `.issue_report.vN`, create or reuse `plans/<issue-slug>/`, and write `<issue-slug>.solution_plan.vN.html` there. Discover all versions in that plan subfolder and create exactly the next unused version; never overwrite, rename, move, or delete an issued version.
4. Define the intended outcome, in-scope changes, exclusions, constraints, and traceability from each verified issue or correction to plan work and acceptance evidence. Do not broaden remediation beyond the report without labeling the addition as a planning discovery and making its approval explicit.
5. Decompose the solution into bounded work packages. For each package state its inputs, target files or components when known, concrete changes, dependencies, owner or required capability, risks, verification, outputs, and done criteria. Order packages by dependency and identify work that can run in parallel.
6. Add preflight, implementation, integration, migration or compatibility, documentation, and final verification activities only when the issue requires them. Preserve historical evidence; never propose fabricating missing provenance.
7. Convert report acceptance tests into executable or inspectable verification. Add necessary regression and negative tests, but distinguish report-mandated acceptance from planner-added safeguards.
8. Resolve ordinary implementation details from repository evidence. Put genuinely scope-changing choices in a decision register with owner, gate, options, recommendation, and effect. Do not leave implementation to guess.
9. Make the plan self-contained: restate all operative scope, work, dependencies, decisions, controls, outputs, and acceptance rules. A predecessor or issue-report link is provenance, not required runtime context.
10. Set the plan state according to authority: `draft` when material decisions remain, `awaiting approval` when ready for authorization, or `approved` only when the human owner explicitly approves this plan. Issue approval and plan approval are distinct; planning never authorizes implementation.
11. Validate structure, source linkage, versioning, internal anchors, traceability, dependency integrity, acceptance coverage, and approval language. Fix failures and rerun validation.
12. Report the new plan path, source issue, predecessor, status, material planning discoveries, unresolved decisions, and validation result. Do not execute the plan unless separately asked and authorized.

## Revision rules

- Treat feedback as input to a new `vN+1`, not permission to edit an issued plan.
- Carry forward the complete current plan; never use “unchanged,” a diff, or a predecessor as operative content.
- If planning exposes a material defect, correction, risk, or acceptance requirement absent from the issue report, identify it as a planning discovery. Require issue-owner confirmation before implementation when it changes scope or authority.
- If the report is rejected, superseded, or too incomplete to support remediation, do not invent a solution plan. Return the blocking evidence and required next decision.

## Skill-family boundary

`plan-createe` is the planning member of an issue-remediation skill family. Its output is the prospective execution contract. Future execution and verification members may consume an approved plan, but they must not infer implementation authority from the plan's existence or from approval of the source issue alone.

## Output contract

Default to one accessible, self-contained HTML plan at `plans/<issue-slug>/<issue-slug>.solution_plan.vN.html`. Keep evidentiary issue artifacts under `issues/` and prospective implementation contracts under `plans/`. The plan must identify its source issue and predecessor, remain usable without opening either, and include the machine-readable metadata required by the plan contract. Use another format only when the user or repository convention requires it.
