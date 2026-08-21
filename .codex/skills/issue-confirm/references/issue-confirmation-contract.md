# Issue-confirmation contract

The confirmation report is an evidence record between an issue and any later solution plan.

## Required properties

- The supplied issue text and issue file are provenance, not proof.
- Each material conclusion cites a repository path, stable record identifier, command result, or external source sufficient for another reviewer to inspect.
- Facts, attributed claims, inferences, competing explanations, and unknowns remain distinguishable.
- The overall result is exactly one of `VERIFIED`, `PARTIALLY_VERIFIED`, `CONTRADICTED`, or `UNRESOLVED`.
- Root-cause language cannot be stronger than its evidence.
- Recommended corrections trace to findings and include observable acceptance tests.
- Risks state effect, owner or `unassigned`, and whether they block the requested decision.
- Human decision remains pending unless an authorized human explicitly decides.
- Confirmation grants no implementation authority.

## Versioning and naming

Issued reports are immutable. Create exactly the next unused version and never overwrite, rename, move, or delete an earlier version.

Unless repository convention says otherwise, place the report beside the issue and name it:

`<issue-stem>.issue_report.vN.html`

The report must be standalone. Its predecessor and evidence links provide provenance but cannot carry content required to understand the current findings.

## Template fidelity

Use the highest numeric, non-deprecated `templates/issue-report.template.vN.html`. Preserve every section marked `data-required-section="true"` and the JSON template contract. Replace all double-brace placeholders. Repeated table rows may be expanded to represent all findings.

The report must contain:

1. A one-paragraph executive summary.
2. Trigger provenance and investigation boundary.
3. Verification functions, actual execution evidence, result locations, and findings.
4. Evidence-linked root-cause analysis or an explicit unresolved result.
5. Bounded corrections and acceptance tests.
6. Risks and open items.
7. Human decision state, requested decision, reviewer authority, report version, digest, and predecessor.
