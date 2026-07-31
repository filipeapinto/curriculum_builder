<!-- section asset of meta_curriculum_builder.prompt.v6.md · read whole -->

## Routing

Which model serves which task is data, and this section is what binds that data. It
names the authorized routing inputs and states the invariants no data file can
express. It **never inlines a value**: no model id, no reasoning level, no candidate
pool appears here. The prompt binds; the data obeys. A routing fact with two owners
is the defect this separation exists to stop.

`policy/routes.v1.yaml` and `policy/routing/` are different things and are never
merged: the first is the set of external capabilities proven by a real preflight
call, the second is which model serves which task.

**The invariants.**

- The selector runs first and code applies its result. A model never chooses its own
  route.
- `--model` is a fallback only and **may not bypass the selector** in
  `policy/routing/`, promoted here from `policy/controller.v1.yaml`. Check id
  `SEL-NO-MODEL-BYPASS`.
- No model at all for merging, validating, hashing, rendering, aggregating,
  auditing or logging — those are deterministic work. Check id
  `SEL-NO-MODEL-FOR-DETERMINISTIC`.
- The cheapest eligible route serves bounded drafting; a stronger route serves
  electronics design and QA; maximum reasoning is reached only through a failed
  safety escalation, and never as a default. Check id `SEL-ESCALATION-BOUNDED`.
- No redundant drafts. Runs are serial by default.
- No model approves its own unsupported technical claim, promoted here from
  `policy/routing/readme.md`.

**The obligation.** Every model call emits a schema-valid routing decision before
the call is made, validating against `schemas/routing_decision.schema.v2.json`
(`SEL-DECISION-VALID`), and the decision records the route **actually executed** in
`executed_model` beside the route decided in `decided_model`
(`SEL-EXECUTED-MATCHES-DECIDED`). The execution log's act for that call carries the
decision's id in `decision_id`, required by `action_kind: model_call` in
`schemas/execution_log.schema.v2.json`.

**What this section does and does not achieve.** It makes these rules stated, owned
and representable in records a validator can check. It does not make them enforced,
because nothing in this repository executes a model, applies a routing decision or
refuses a call. Prose states the rule, JSON Schema proves both fields exist, and a
gate compares them; only a controller could refuse to act on the difference.
`RT-3`, `RT-4` and `RT-5` in `policy/deferred.v1.yaml` name that work, and until
each is discharged no document or report may state that the selector is enforced.
