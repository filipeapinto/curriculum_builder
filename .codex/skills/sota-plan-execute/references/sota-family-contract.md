# Normative SOTA family contract v1

This contract is mandatory for every new SOTA plan and run. Plans may add stricter controls but must not remove, rename, weaken, relabel, or contradict these rules. Family checks run before plan-specific checks; an unavailable mandatory check is `BLOCKED`, never `PASS`.

## Compact package

```text
research/<sota-slug>/
├── plan/<sota-slug>.plan.vN.html
└── runs/<run-id>/
    ├── report.html
    ├── execution-log.json
    └── evidence/              # optional and plan-justified
```

The versioned plan is the sole prospective execution contract. `execution-log.json` is the append-only record of actual activities. `report.html` is the human-facing method, evidence, findings, limitations, challenge dispositions, verification, and state record. Optional evidence must be indexed from the report and attributable from the log.

## Universal plan contents

Every plan states its stable study and plan IDs, version, predecessor, status, question, intended decision, owner, scope, exclusions, evidence boundary, method, role assignments, dependencies, model/tool/human allocation, budgets and measurement, gates, retry and stopping rules, outputs, family plus plan-specific tests, and human approval state. Study-specific searches, appraisal instruments, experiments, incident reconstruction, or other methods are conditional.

## Execution and provenance

Use `schemas/execution_log.schema.v2.json` as the canonical log envelope. Each material activity has paired start and terminal records and stable activity ID. Model/skill activities additionally record, in required structured run evidence referenced by the log, the installed skill identity/version or explicit `unknown`, actual model/tool/version, effort, inputs, outputs, time, usage, and routing decision. Missing historical provenance remains unknown.

Stable study, plan, run, activity, source, finding, challenge, verification, artifact, and decision IDs are required where applicable. Retries state the failure and materially changed approach. Deviations are approved and recorded before affected work.

## Challenge and verification

Independent challenge receives frozen inputs without intended defenses. Every challenge has a stable ID, severity, evidence, affected finding, required action, and disposition. Unresolved Critical or High challenges block completion.

Verification order is fixed: validate the plan against this family baseline; validate the run package against this baseline; then run stricter plan-specific checks. Required checks record `PASS`, `FAIL`, `BLOCKED`, or `NOT_APPLICABLE` with evidence. Verification cannot waive controls, accept research, or grant implementation authority.

## Terminal state envelope

Every report separately records exactly one value for each dimension:

- research support: `SUPPORTED`, `PARTIALLY_SUPPORTED`, `NOT_SUPPORTED`, `INCONCLUSIVE`, `BLOCKED`;
- execution: `NOT_STARTED`, `RUNNING`, `BLOCKED`, `FAILED`, `COMPLETE`;
- verification: `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`;
- human acceptance: `PENDING`, `ACCEPTED`, `REJECTED`, `REVISION_REQUESTED`;
- implementation authority: `NONE`, `LIMITED`, `GRANTED`, `REVOKED`.

Verification `PASS` with acceptance `PENDING` remains unaccepted; acceptance never implies implementation authority. Only the human owner may set acceptance or authority.

## Failure and compatibility

Missing required files, invalid log structure, unpaired activities, omitted states, weakened family rules, unresolved mandatory challenge, or unavailable required verification blocks acceptance. Material scope, method, budget, output, or authority changes return to versioned planning.

Historical packages are assessed read-only with the same applicable baseline. Absence remains absence; no migration, repair, or fabricated provenance is permitted without separate authority.
