---
name: sota-verify
description: Deterministically verify a completed SOTA research package against its approved plan. Use after synthesis and challenge to check required artifacts, identifiers, counts, citations, links, schemas, accessibility, rendering, integrity, budget reporting, and challenge dispositions.
---

# SOTA Verify

1. Read `../sota-plan-execute/references/sota-family-contract.md`. Run its non-waivable family checks against the plan and run package before deriving and running stricter plan-specific checks.
2. Verify required artifacts exist, are nonempty, and use required stable identifiers.
3. Reconcile search, screening, exclusion, inclusion, retry, and budget counts.
4. Check claim-to-source links, citations, local and external links where permitted, schemas, hashes, and paired terminal records.
5. Render and visually inspect required human-facing artifacts; verify diagram textual equivalents.
6. Confirm every challenge has a disposition and every limitation is disclosed.
7. Record each check as `PASS`, `FAIL`, `BLOCKED`, or `NOT_APPLICABLE` with evidence. An unavailable required check is `BLOCKED`, never `PASS`.

Return a deterministic verification report. A failed or unmeasurable required gate prevents acceptance; verification never grants human approval.
