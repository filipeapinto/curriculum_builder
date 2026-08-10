# GOAL

Bind every P5 deterministic check and isolated judge verdict to existing source
bytes and the compiled evaluator subtask denominator before acceptance.

# TEST

- Controller recomputation rejects missing, fabricated, symlinked, stale, or
  out-of-root evidence even when every digest is syntactically valid.
- The ledger must contain exactly generator, checks, isolated judges, reducer,
  repair loop, and evidence commit; a self-declared smaller set fails.
- Replayed verdicts and evidence from another run, prompt, policy, schema,
  route, contract, node, or attempt fail.

# LOOP

Repair only the failed artifact or evaluator owner and regenerate its evidence
source. Rerun the dependent join and byte admission; do not broadly regenerate
accepted siblings. Exhaustion routes to `SYSTEM_FAILURE`.
