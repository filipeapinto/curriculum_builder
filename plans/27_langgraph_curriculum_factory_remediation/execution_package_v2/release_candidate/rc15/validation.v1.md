# RC15 pre-QA validation

- Graph v8 SHA-256: `c2d79ac0387c935977385138d2d891cf1539041f1a4532acf94fc8dc687bf6b1`.
- Graph v9 SHA-256: `5236bf6b13a2c5171ad11ab80f1147e20b6b59f46708090d25ec16c5a7574379`.
- Approval schema v6 SHA-256: `5ecc63dd64377b9bac39facb30f147cad1ab07f3d1ad137bbc9254b39dd58bf0`.
- Approval contract v6 SHA-256: `f4e609d1d93f1303c651e6cbe58233ec35b7bb7eab86a9ef393fc002b5229b70`.
- Governing specification SHA-256: `e14df5a36ce12d700fe9fc4aa4aea466771bc89f31bc6e9d49f812c147b1bb3c`.
- `validate_plan_v2.py`: valid; order N00 through N90.
- Integration-ownership verifier: 75 claims passed, zero failures.
- Execution-package tests: 176 passed.
- Focused runtime/repair tests: 797 passed.
- Combined focused/package tests: 973 passed.
- Full runtime tests: 1350 passed, 2 skipped, 419 subtests passed.
- Plan 26 N13 receipt refreshed through its real host-level verification; its
  controller reports no stale receipts.
- Python compilation and `git diff --check`: passed.

Independent QA has not yet supplied a verdict; only the QA gate may do so.
