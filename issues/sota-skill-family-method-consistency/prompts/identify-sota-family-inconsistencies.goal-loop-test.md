# Prompt - Identify SOTA skill-family method and output inconsistencies

## Goal

Audit the complete installed SOTA skill family and determine why executions governed by the same family can produce incompatible directory structures, evidence formats, lifecycle records, verification meanings, and terminal research answers.

Use these two runs as the primary comparative cases:

- `research/codex_calls_claude_qa_gate/`
- `research/codex_same_model_qa_gate/`

Treat `issues/sota-skill-family-method-consistency/sota-skill-family-method-output-contract-inconsistency.issue.html` as the issue statement, not as proof. Verify every assertion directly.

Do not modify skills, plans, research artifacts, or either run during this task. Produce an evidence-based inconsistency report and a proposed canonical family contract for later human review.

The audit must distinguish:

- legitimate variation caused by different research questions;
- plan-specific parameters and extensions;
- prohibited variation in the shared method;
- implementation drift between skill definitions and actual runs;
- historical/version drift that cannot be reconstructed; and
- claims that cannot be established from available provenance.

The desired invariant is not identical substantive conclusions. It is a comparable research-answer contract: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `NOT_SUPPORTED`, `INCONCLUSIVE`, or `BLOCKED`, accompanied by separate execution, verification, human-acceptance, and implementation-authority states.

## Loop

Repeat the following loop until the stopping tests below pass.

### 1. Inventory

Read every current `sota-*` `SKILL.md` and every directly required reference, schema, script, or template. Inventory each skill's trigger, inputs, outputs, authority boundary, handoffs, required records, failure routes, and terminal states.

Inventory both case-study directories completely. Record paths, formats, schemas, IDs, timestamps, approvals, execution events, budgets, source records, analysis artifacts, synthesis products, challenges, verification reports, and final reports.

### 2. Normalize

Map both runs onto one neutral lifecycle:

```text
plan → approval → start gate → calibration → protocol approval → collection
→ screening/appraisal/extraction → incident/local analysis → evaluation
→ synthesis → independent challenge → correction → verification
→ human acceptance → terminal research answer
```

For each lifecycle stage, record `present`, `absent`, `not applicable`, `blocked`, or `not evidenced`. Do not infer completion from the existence of downstream files.

Map equivalent artifacts across the two runs. Identify where equivalent concepts use different paths, formats, schemas, IDs, or meanings.

### 3. Compare

Build at least these matrices:

1. Skill-to-skill contract and handoff matrix.
2. Run-to-run directory and artifact crosswalk.
3. Lifecycle-stage coverage matrix.
4. Required-record/schema comparison.
5. Verification-check and severity comparison.
6. Terminal-state and research-answer semantics comparison.
7. Plan-controlled versus family-controlled responsibility matrix.

For every inconsistency, assign a stable ID and classify it as:

- `METHOD_INVARIANT_MISSING`
- `STRUCTURE_DRIFT`
- `SCHEMA_DRIFT`
- `LIFECYCLE_DRIFT`
- `VERIFICATION_DRIFT`
- `TERMINAL_SEMANTIC_DRIFT`
- `AUTHORITY_DRIFT`
- `DOCUMENTATION_DRIFT`
- `LEGITIMATE_PLAN_VARIATION`
- `UNKNOWN_PROVENANCE`

### 4. Trace causes

Trace each inconsistency to the exact skill instruction, plan clause, missing family rule, run record, or unverifiable historical assumption that permits it. Separate direct evidence from inference.

Determine specifically:

- why one project has `execution/<run-id>/` and the other does not;
- why one relies heavily on Markdown/CSV while the other uses versioned JSON records;
- whether the plans were allowed to redefine mandatory family method;
- whether `sota-plan-execute` defines an enforceable canonical run package;
- whether role-skill output contracts are sufficiently precise;
- whether `sota-verify` has a non-waivable family baseline;
- whether equivalent missing evidence produces equivalent outcomes;
- whether “pass with limitations” and “blocked/not accepted” are consistently defined; and
- whether either run can prove which skill versions and agent assignments produced it.

### 5. Propose the canonical contract

Propose, but do not implement, a canonical contract containing:

- directory tree rooted at `execution/<run-id>/`;
- required and optional artifact classes;
- canonical machine-readable schemas and stable identifiers;
- lifecycle and gate state machine;
- normalized research-answer vocabulary;
- separate execution, verification, acceptance, and implementation states;
- family-level verification baseline;
- plan extension and strengthening rules;
- fail-closed rules;
- migration strategy for both case-study runs; and
- deterministic conformance tests.

For each proposed rule, cite the inconsistency IDs it resolves and identify which skill owns the rule.

### 6. Challenge

Run an independent challenge of the audit. The challenger must test whether the proposed uniformity would incorrectly constrain legitimate research-method differences, conceal domain-specific evidence, or confuse canonical records with human-facing presentation.

Disposition every challenge explicitly as accepted, corrected, rejected with evidence, or unresolved.

### 7. Correct and re-test

Correct the audit and proposed contract based on accepted challenges. Re-run all deterministic tests and preserve the before/after disposition trail.

## Test

The task is complete only when all of the following tests pass:

### Coverage tests

- Every installed `sota-*` skill and directly required family reference is inventoried.
- Every file in both case-study directories is classified or explicitly excluded with a reason.
- Every neutral lifecycle stage has a status for both runs.
- Every required family handoff has an identified producer, consumer, artifact, and failure route.

### Evidence tests

- Every reported inconsistency cites exact repository paths and, where practical, line numbers or record IDs.
- Facts, attributed claims, inferences, and unknowns are labeled separately.
- No claim that a skill was invoked relies only on output resemblance.
- Skill-version provenance is reported as unknown unless durable evidence establishes it.

### Consistency tests

- The proposed contract clearly separates invariant method from legitimate plan variation.
- Both runs can be deterministically evaluated against the same baseline.
- Equivalent defects map to equivalent verification outcomes.
- Research support status is independent from execution completion, verification conformance, human acceptance, and implementation authority.
- A plan can strengthen but cannot weaken the family baseline.

### Structural tests

- The proposed canonical directory tree assigns exactly one authoritative location to every required artifact class.
- Required records have proposed schema names, versions, stable ID rules, and producer/consumer ownership.
- Optional human-readable reports are explicitly distinguished from canonical machine records.
- Resume and terminal-state discovery do not depend on directory inference.

### Challenge tests

- An independent challenge register exists.
- Every challenge has a disposition.
- Unresolved material challenges prevent a final “ready to implement” recommendation.

### Deliverable tests

Produce one audit package containing:

1. Executive finding and severity.
2. Verified inconsistency register.
3. All comparison matrices.
4. Root-cause analysis by skill and contract layer.
5. Proposed canonical family contract.
6. Migration mapping for both case-study runs.
7. Deterministic conformance-test specification.
8. Independent challenge register and dispositions.
9. Unknowns and required human decisions.
10. A final disposition: `READY_FOR_SKILL_REDESIGN`, `PARTIALLY_READY`, or `BLOCKED`.

## Stop rules

Stop and report `BLOCKED` rather than guessing if a required skill or referenced family dependency is missing, the case-study evidence cannot be read, or provenance is necessary for a conclusion but unavailable.

Stop collection when every installed family component and both complete run trees have been accounted for and two consecutive comparison passes reveal no new inconsistency class. Do not begin editing the skill family until the human owner approves the audit and canonical contract.
