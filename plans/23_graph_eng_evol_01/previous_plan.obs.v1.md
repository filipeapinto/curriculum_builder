# Observations carried from Plan 22

1. The evolutionary workflow must remain a cyclic computational graph rather
   than a filename-ordered prompt sequence.
2. Prompt genes and topology genes require separate mutation operators.
3. Population evaluation requires candidate-bound parallel joins and complete
   denominators before scoring.
4. Immutable candidates, append-only evidence, Pareto selection, and bounded
   generation loops remain useful and are retained.
5. Plan 22's two bespoke external-review prompts duplicated a QA mechanism that
   already exists in the repository.
6. Plan 23 standardizes decisive external QA on
   `.claude/skills/qa-gate-codex-run` and removes those bespoke review prompts.
7. The QA gate's `ROUND_OPEN` state is evolutionary feedback, not permission to
   edit a candidate in place.
8. `QA_PASSED` is insufficient until the gate's own `verify` command confirms
   the record against the witnessed Codex session.
9. `QA_ERROR` is inconclusive, `QA_FAILED` is terminal, and neither may be
   converted into promotion.
10. Plan authoring stays small: one approach, one run prompt, one criteria file,
    one observations file, and a flat prompt folder. No local orchestration,
    optimization, manifest, policy, or tools folders are introduced.

