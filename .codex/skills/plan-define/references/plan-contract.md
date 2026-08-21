# Issue-remediation plan contract

A plan created by `plan-createe` must contain:

1. Identity: title, plan version, date, state, source issue path and state, predecessor, owner, and implementation-authority statement.
2. Executive intent: the problem being solved, target outcome, and why the proposed work addresses the documented root cause.
3. Source assessment: verified findings, assumptions, planning discoveries, report recommendations, risks, and unresolved decisions kept distinct.
4. Scope: included changes, exclusions, constraints, affected components, compatibility or migration boundary, and explicit non-goals.
5. Traceability: stable issue, correction, work-package, decision, risk, and acceptance identifiers with complete mappings among them.
6. Dependency-aware work packages: objective, inputs, targets, changes, dependencies, owner or capability, risks, verification, outputs, and done criteria.
7. Execution flow: ordered gates, permitted parallelism, stop conditions, rollback or recovery where relevant, and human authority points.
8. Verification: report-mandated acceptance tests, planner-added safeguards, regression checks, negative tests, integration checks, and required evidence.
9. Decision and risk registers: owner, timing or gate, recommendation or mitigation, effect, and blocking status.
10. Delivery: required artifacts, documentation, migration treatment, final handoff, and completion definition.
11. Version note and approval gate. Never claim approval without explicit human authorization.

Every version is immutable and standalone. It may cite evidence but cannot outsource operative instructions to the issue report or a predecessor.

## Repository placement

Unless an established repository convention or explicit user direction requires another location, place plans at `plans/<issue-slug>/<issue-slug>.solution_plan.vN.html`. Derive `<issue-slug>` from the source issue-report name by removing the extension and trailing `.issue_report.vN`. Do not place prospective solution plans inside `issues/`; issue reports are evidence, while plans are execution contracts.

## Machine-readable metadata

Embed one `<script type="application/json" id="plan-createe-contract">` object with:

- `schema`: `repo.plan-createe/v1`
- `plan_version`: positive integer
- `status`: `draft`, `awaiting approval`, `approved`, `superseded`, or `rejected`
- `source_issue`: repository-relative path or stable identifier
- `source_issue_status`: source report's stated review or decision state
- `predecessor`: path or `null`
- `implementation_authority`: `NONE` unless the human owner explicitly authorizes execution
- `work_packages`: array of unique work-package IDs
- `acceptance_tests`: array of unique acceptance-test IDs
- `open_decisions`: array of unique decision IDs

The visible document and metadata must agree.

## Minimal quality gates

- Every documented correction maps to at least one work package and acceptance test.
- Every work package maps to at least one finding, correction, risk, or planning discovery.
- Dependencies reference real work-package IDs and contain no cycle.
- Open scope or authority decisions gate the affected work.
- A pending issue decision is visible and cannot be mistaken for plan or implementation approval.
- Links and anchors resolve, HTML parses, identifiers are unique, and no template placeholders remain.
- The default output path is under `plans/<issue-slug>/`, and the source issue remains under its evidentiary location.
