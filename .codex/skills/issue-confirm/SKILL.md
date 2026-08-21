---
name: issue-confirm
description: Investigate a reported repository issue from supplied text and an issue-file path, determine what is verified, contradicted, or unresolved, and create the next immutable HTML issue-report version from the repository's canonical issue-report template. Use before remediation planning; do not implement fixes.
---

# Issue Confirm

Confirm or challenge an issue against repository evidence, then issue a reviewable report. Treat the supplied text and issue file as claims to investigate, not as established facts.

## Required inputs

Require both:

1. Issue text describing the reported behavior, concern, or invariant violation.
2. A repository-relative or absolute path to the issue file.

Resolve a discoverable missing value from the conversation or repository context. If either input remains ambiguous, stop and request it. Never guess the issue target.

## Required resources

1. Read the entire issue file.
2. Read [references/issue-confirmation-contract.md](references/issue-confirmation-contract.md).
3. Discover `templates/issue-report.template.vN.html` files outside `templates/deprecated/`. Use the highest numeric version as the canonical template. If none exists, stop and report the missing dependency.
4. Read repository instructions governing the issue's scope and every material file inspected.

## Workflow

1. Establish the reported claims, expected invariant, affected scope, operational consequence, and requested decision from the issue text and issue file. Preserve disagreements between those inputs.
2. Determine the output directory from repository convention. Otherwise write beside the issue file.
3. Derive the report stem from the issue filename by removing its final extension and any trailing `.vN`, then appending `.issue_report`. Run `scripts/next_issue_report_version.py <output-directory> <report-stem>` to select exactly the next unused version.
4. Inspect the smallest sufficient set of primary repository evidence. Prefer exact files, schemas, logs, tests, generated artifacts, and version history over summaries. Use external evidence only when the issue requires an externally verifiable claim.
5. For every material claim, record one status:
   - `VERIFIED`: directly supported by cited evidence.
   - `PARTIALLY_VERIFIED`: only a bounded portion is supported.
   - `CONTRADICTED`: reliable evidence conflicts with the claim.
   - `UNRESOLVED`: available evidence cannot decide it.
6. Reproduce or test the behavior when a safe, read-only or non-destructive check can materially increase confidence. Do not implement a correction.
7. Separate observation, inference, attributed statement, and unknown. Do not convert missing evidence into proof of absence.
8. Identify root cause only to the depth supported by evidence. Label competing explanations and confidence. If no root cause is established, say so explicitly.
9. Recommend bounded corrections and acceptance tests, but grant no implementation authority. Distinguish corrections supported by verified findings from optional improvements.
10. Copy the canonical template into `<report-stem>.vN.html`; preserve its required sections, embedded contract, responsive styling, and print behavior. Replace every placeholder, add rows when needed, and remove no required section.
11. Set lifecycle state to `awaiting human decision` unless the authorized reviewer explicitly supplies a decision. Never infer approval from the request to investigate.
12. Preserve every earlier issue and report version unchanged. A later report must be standalone and name its predecessor.
13. Run `scripts/validate_issue_report.py <report-path> <template-path>` and resolve every failure before delivery.

## Boundaries

- Confirming an issue authorizes investigation and report creation only.
- Do not modify the issue file, implementation, tests, policy, configuration, or prior reports.
- Do not silently broaden the issue. Record newly discovered adjacent problems as risks or open items unless the user authorizes a separate issue.
- If evidence access is unavailable, produce a report only when the template can truthfully record an `UNRESOLVED` result; otherwise report the blocker without fabricating a confirmation.
- Do not invoke SOTA research skills merely because the template contains an independent-verification table. Name the expected skill only when a governing workflow actually required it, and state missing invocation evidence as unknown.

## Delivery

Report the new issue-report path, source issue path, template version, predecessor, overall verification result, decisive evidence, unresolved items, validation results, and lifecycle state.
