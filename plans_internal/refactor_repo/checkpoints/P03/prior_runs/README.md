# Superseded intermediate test runs

These directories are retained for traceability only. **They are not this checkpoint's
Test 7 evidence** — that is `../t5_final_tree/`, produced against the checkpoint tree
actually under review.

- `t1/` — first post-codemod full-suite run of the original P03 execution, before the
  operator-authorized compatibility correction.
- `t2_post_compatibility_correction/` — full-suite run after that correction, still
  during the original execution.
- `t4_recovery/` — full-suite run made during the first recovery pass, against the
  reconstructed tree `db6f611dbee4cc80ab4d85425c318338dd37a994`. Its results are
  identical to `t5_final_tree/` (109 failed, 1370 passed, 2 skipped, 9 errors; 29 new
  vs t0; 0 fixed since t0; exact match against `p04_handoff_allowlist`), but it was run
  in a virtual environment whose package set was not pinned deliberately, and against a
  tree that predates the re-executed move. `t5_final_tree/` supersedes it and records
  its exact environment freeze at `../evidence/verification/test_environment_freeze.txt`.
