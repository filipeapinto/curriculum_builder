# GOAL

Amend P0 for Plan 21 v2 without changing the frozen v1 prompt. Produce the
baseline-assurance addendum that binds actual sandbox profile, engine, root
resolution evidence, and operator-authority public-key bytes. Preserve the live
unit vocabulary including `ACCEPTED_PENDING_REVIEW` and `SYSTEM_FAILURE`.

# TEST

- Every named profile, binary, root-evidence, and public-key file exists as a
  regular file; the controller recomputes its size, SHA-256, owner, and mode.
- The exact observed unit vocabulary is `ACCEPTED`,
  `ACCEPTED_PENDING_REVIEW`, `BLOCKED`, `SYSTEM_FAILURE`; P4 owns migration.
- Missing files, symlinks, fabricated hashes, contradictory roots, and a model-
  writable authorization root fail before P1.

# LOOP

Repair only the assurance inventory or its source files, then rerun every byte,
owner, mode, root, and vocabulary check. Stop to `SYSTEM_FAILURE` after two
identical failures. Submit the compiled P0 test/artifact denominator and source
manifest; never let the addendum nominate its own denominator.
