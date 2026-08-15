# RC22 pre-QA validation

- Graph v8/v9, schema v6, contract v6, and governing-spec hashes match the review bundle.
- Package 176; focused runtime/repair 804; combined exact denominator 980.
- Full runtime 1357 passed, 2 skipped, 419 subtests passed.
- Exact RC21 regressions pass: active Arduino D01→D02; malicious Python dependency
  refusal; `os.chdir` existing-to-renamed undeclared-directory normalization.
- Plan 26 N13 is current and reports no stale receipts.
- Python compilation and whitespace checks pass.

RC21 remains a preserved FAIL. Only a successfully verified fresh RC22 QA chain may
approve entry into graph v9.
