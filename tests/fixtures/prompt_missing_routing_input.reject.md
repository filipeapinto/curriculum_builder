# Negative fixture for FR-P2-BOUND (a)

The routing package is orphaned: the model registry is never named as an authorized
input, so one bare row stands in for a file nothing binds.

## Inputs

| Input | Role |
|---|---|
| `policy/calibration.v1.yaml` | the premises |
| `policy/routing/task_taxonomy.v2.yaml` | task classes and their risk profiles |
| `policy/routing/routing_policy.v1.yaml` | candidate-pool and escalation policy |
| `policy/routing/quality_gates.v1.yaml` | observable acceptance gates |
| `schemas/routing_decision.schema.v2.json` | the routing-decision record format |
| `schemas/execution_log.schema.v2.json` | the execution-log record format |

### Retained contracts

Not authorized inputs. Each validates work already accepted under it, and nothing
else. Both are retirable under `RT-6`.

| Retained contract | Readable only to |
|---|---|
| `schemas/execution_log.schema.v1.json` | validate execution logs already accepted under v1 |
| `schemas/routing_decision.schema.v1.json` | validate routing decisions already accepted under v1 |

## Routing

Synthetic. Never executed.
