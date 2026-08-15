# RC29 pre-QA validation

- Source bytes equal locally validated RC28; RC28 QA is invalidated by verified
  process-integrity failure, not by an artifact finding.
- Committed regression set 12 passed; focused suites 419 and 569 passed; complete
  runtime 1370 passed, 2 skipped, 419 subtests passed.
- Plan 26 N13 is current `PASSED` with no stale receipts.
- Authority hashes recompute; plan valid; ownership 75/75; scan 67/zero.

Review is limited to ordinary software correctness: run committed regression tests
and inspect implementation boundaries. Do not construct or execute new payloads.
Only qa-gate `verify` may approve RC29.
