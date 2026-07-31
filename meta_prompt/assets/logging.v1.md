<!-- section asset of meta_curriculum_builder.prompt.v6.md · read whole -->

## The action log

`V7/test_results/prompt_execution_log.md`, append-only, validating against
`schemas/execution_log.schema.v2.json`. Every record carries a typed `action_kind`,
and an act whose `action_kind` is `model_call` must carry the `decision_id` of the
routing decision it was made under — the condition keys on the type, never on the
wording of `action`.

Every controller action appends one record before it starts and one when it ends:
a completion `ACT` citing the started id, or an `EXEC` whose mandatory `Closes`
field names it. So the pairing gate is computable — collect every started id,
subtract every id cited by a completion or a `Closes`, and the remainder must be
empty.

The logger takes the closing id as an argument and never derives one; its counter
is monotonic by construction, never recovered by counting text in the file it is
writing; appends hold an exclusive lock and never rewrite what is on disk; and if
an id cannot be allocated or an append cannot be proven, the run stops as
`META_SYSTEM_FAILURE`. That is failure B1, which recorded an entire previous run
through a logger nobody had tested.

`V7/test_results/meta_execution_state.json` records the log path and hash, completed action count,
failure count, unpaired-start ids, last action id and last completion id.

## Convergence and drift

Keep `V7/test_results/meta_execution_state.json` current and atomic: goal hash,
prompt hash, authorized roots, phase, revision cycle, gates passed and failing,
stable failure ids, artifacts authorized to change, resource totals, last
measurable improvement, drift result, next action, terminal state, log totals.

The prompt hash covers this contract whole — `meta_prompt/meta_curriculum_builder.prompt.v6.md`
and every `section` asset it names, hashed in the order the asset table gives. A
hash over the short file alone would let a rule change under a run that reports
itself unchanged.

```text
run gate → record failures → authorize affected artifacts
→ revise → rerun affected and dependent gates
→ record measurable improvement → repeat
```

Stop as `META_DRIFT_STOP` on any `DRIFT-*` condition in `policy/checks.v1.yaml`, or
on exceeding any limit in `policy/limits.v1.yaml`. A defective test may change only
where it contradicts this contract; record both hashes, the contradiction, the
correction and the regression evidence.

Three terminal states, no others:

- `META_ACCEPTED` — every release gate and drift audit passes; golden L01 accepted.
- `META_SYSTEM_FAILURE` — a required capability stays unavailable after bounded
  retry, with evidence; or the log cannot be written; or a startup precondition
  needs a human decision.
- `META_DRIFT_STOP` — scope drift or bounded non-convergence.

Implementation, prompt, schema, test, renderer, visual and layout defects require
revision. They are not external failures — do not classify your own bug as an act
of God.
