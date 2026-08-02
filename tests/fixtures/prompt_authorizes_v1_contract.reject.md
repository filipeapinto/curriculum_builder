# Negative fixture for FR-P2-BOUND (b)

Every required entry is present, and the table also lists a **retired** contract as
an authorized input. A retired version is never an authorized input to a new run; a
new run may never be validated against a superseded contract, which is exactly what
versioning them additively was meant to prevent.

## Inputs

| Input | Role |
|---|---|
| `policy/routing/model_registry.v1.yaml` | model capabilities and availability |
| `policy/routing/task_taxonomy.v2.yaml` | task classes and their risk profiles |
| `policy/routing/routing_policy.v1.yaml` | candidate-pool and escalation policy |
| `policy/routing/quality_gates.v1.yaml` | observable acceptance gates |
| `schemas/routing_decision.schema.v2.json` | the routing-decision record format |
| `schemas/execution_log.schema.v2.json` | the execution-log record format |
| `schemas/routing_decision.schema.v1.json` | the routing-decision record format, previous version |

## Routing

Synthetic. Never executed.
