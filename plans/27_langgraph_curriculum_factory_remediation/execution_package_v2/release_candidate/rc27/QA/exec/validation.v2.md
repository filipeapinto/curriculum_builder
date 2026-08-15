# RC27 round-2 pre-QA validation

- Round 1 remains a formal `FAIL`; both RC27-B01 and RC27-B02 now have exact permanent
  adversarial regressions and architectural repairs.
- The verifier child is standard-library-only under `-I -S`; schema validation is
  trusted and schema-hash-bound; interpreter and runtime modules are receipted.
- Focused suites: 418 passed and 568 passed. Full runtime: 1369 passed, 2 skipped,
  419 subtests passed.
- Plan 26 N13 is freshly `PASSED` with no stale receipts.
- Authority hashes recompute; plan valid; ownership 75/75; complete-tree scan clean.

Only a terminal QA result whose chain independently verifies may approve RC27.
