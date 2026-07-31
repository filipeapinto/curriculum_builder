# Model routing manifests — folder index

A human's map of this directory. It is never an input to a run: the rules that bind
a run are stated in the meta prompt's `## Routing` section, and the data those rules
read is the four manifests below.

## Files

- `model_registry.v1.yaml` — model capabilities and availability, plus the anchored
  `prose_pattern` for every value the meta prompt must never inline.
- `task_taxonomy.v2.yaml` — task classes and risk profiles, including workbook and
  PDF assembly.
- `routing_policy.v1.yaml` — candidate-pool and escalation policy.
- `quality_gates.v1.yaml` — observable acceptance gates, never a model's own
  confidence.

## Elsewhere

- `schemas/routing_decision.schema.v2.json` — the decision-record format. Contracts
  live with the other contracts, because a validator reads them.
- `meta_prompt/assets/model_selector_prompt.v1.md` — the selector's own prompt. Prose a
  model reads lives with the other prose a model reads.
