# Repository refactor rollback map

Each phase is independently revertible with `git revert <phase-commit>`, followed by
the verification named below. History must not be reset or rewritten.

| Phase | Reversal validation |
|---|---|
| Inventory and planning | Inventory schema validation and read-only dirty-state check |
| Packaging skeleton | Packaging tests; confirm the pre-refactor import contract |
| Import codemods | Codemod fixture suite and idempotence checks |
| Source move | Full suite from the predecessor checkout |
| Resource/root repair | Root, egress, CLI, and output-containment tests |
| Output/fixture disposition | Fixture-closure tests; no restore is needed because no output child was deleted |
| Schema decisions | Schema identity/ref-resolution tests |
| Identity documentation | Reference-integrity tests and documented command smoke checks |
| Release proof | Remove only this harness/report checkpoint and rerun predecessor tests |
| Test tree | Revert the path map/decision together, then compare collected test IDs |

The remote repository and local checkout rename are not part of these Git phases. If
later authorized, their rollback is to restore the prior GitHub name, `origin` URL, and
checkout name, then verify clone, fetch, and push separately.
