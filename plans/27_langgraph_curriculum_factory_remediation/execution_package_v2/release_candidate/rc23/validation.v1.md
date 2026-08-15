# RC23 pre-QA validation

- RC22 remains a preserved FAIL with RC22-QA-001 and RC22-QA-002.
- Exact D02 reviewer probes now pass: active Arduino admitted; indirect eval,
  dynamic native import, fork, and dependency-indirect-eval rejected before entry.
- Exact guard probes pass for chdir, utime, and mkfifo existing-to-renamed paths.
- Package/focused combined: 986 passed.
- Full runtime: 1363 passed, 2 skipped, 419 subtests passed.
- Plan 26 N13: PASSED, no stale receipts.
- Graph/spec/schema/contract hashes remain those recorded in the RC23 bundle.

Only a terminal verified QA chain may approve RC23.
