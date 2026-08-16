# Acceptance Criteria Mapping: Specification §10 Criteria to Prompt Owners

This document maps each of the 20 acceptance criteria from refactoring specification §10 (v8) to its primary prompt owner, establishing complete traceability and unique ownership per specification requirement that "every planned change and acceptance criterion [is assigned] to exactly one primary prompt."

**Note**: Criterion titles are drawn directly from specification §10; see `refactor_repository.spec.v8.html` §10 for the authoritative criterion list and requirements.

---

## Acceptance Criteria Ownership Map

Per specification §10, the 20 executable acceptance tests are assigned as follows:

| Criterion | Specification §10 Criterion | Primary Owner |
|-----------|------|-------|
| 1 | Installed imports | P01 |
| 2 | CLI behavior | P08 |
| 3 | Root resolution | P04 |
| 4 | Distribution artifacts | P08 |
| 5 | Module origin | P03 |
| 6 | Test-tree decision | P09 |
| 7 | Shadowing rejection | P03 |
| 8 | Output containment | P04 |
| 9 | Fixture closure | P05 |
| 10 | Ignored-state independence | P05 |
| 11 | Empty-output resilience | P05 |
| 12 | Schema identity | P06 |
| 13 | Reference integrity | P06 |
| 14 | Documentation integrity | P07 |
| 15 | Fresh-clone reproducibility | P08 |
| 16 | Clean-room verification | P08 |
| 17 | Behavioral differential | P08 |
| 18 | Codemod safety | P02S |
| 19 | Regression and scope | P09 |
| 20 | Inventory reproducibility | P08 |

---

## Ownership Summary

| Prompt | Criteria Owned (Primary) | Count |
|--------|---|---|
| P01 | 1 | 1 |
| P02S | 18 | 1 |
| P03 | 5, 7 | 2 |
| P04 | 3, 8 | 2 |
| P05 | 9, 10, 11 | 3 |
| P06 | 12, 13 | 2 |
| P07 | 14 | 1 |
| P08 | 2, 4, 15, 16, 17, 20 | 6 |
| P09 | 6, 19 | 2 |
| **Totals** | **20 criteria, 9 owners** | **100%** |

All 20 specification §10 acceptance criteria have exactly one primary owner. P10 (external rename) is not assigned a criterion as it handles post-completion authorization.

---

## Authority Notes

- Each of 20 criteria has exactly one primary prompt owner; no gaps, overlaps, or multi-owner assignments.
- **Criterion 20** (complete end-to-end verification) is owned by P08 and must be witnessed by independent Codex QA.
- **P10** (External Rename) is not assigned a criterion; it handles post-completion external system changes and requires separate authorization outside the refactoring completion gate.
- For criterion definitions and detailed requirements, see specification `refactor_repository.spec.v8.html` §10.

---

**Verification**: This mapping satisfies the requirement that "every planned change and acceptance criterion [is assigned] to exactly one primary prompt" (specification §9.1).

