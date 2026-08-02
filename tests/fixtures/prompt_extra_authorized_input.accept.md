# Positive fixture for FR-P2-BOUND (a)

A table carrying all six required entries **plus** `policy/calibration.v1.yaml`,
which must pass. (a) is not a whitelist: the authorized-input table legitimately
carries other inputs, and a whitelist reading would delist them.

## Inputs

| Input | Role |
|---|---|
| `policy/calibration.v1.yaml` | the premises |
| `policy/routing/model_registry.v1.yaml` | model capabilities and availability |
| `policy/routing/task_taxonomy.v2.yaml` | task classes and their risk profiles |
| `policy/routing/routing_policy.v1.yaml` | candidate-pool and escalation policy |
| `policy/routing/quality_gates.v1.yaml` | observable acceptance gates |
| `schemas/routing_decision.schema.v2.json` | the routing-decision record format |
| `schemas/execution_log.schema.v2.json` | the execution-log record format |

## Routing

Synthetic. Never executed.
