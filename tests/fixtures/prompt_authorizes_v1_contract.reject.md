# Negative fixture for FR-P2-BOUND (b)

Every required entry is present, and the table also lists a **retained** contract as
an authorized input. A retained version is readable by a validator checking old
records and by nothing else; a new run may never be validated against a superseded
contract, which is exactly what versioning them additively was meant to prevent.

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

### Retained contracts

Not authorized inputs. Each validates work already accepted under it, and nothing
else. Both are retirable under `RT-6`.

| Retained contract | Readable only to |
|---|---|
| `schemas/execution_log.schema.v1.json` | validate execution logs already accepted under v1 |
| `schemas/routing_decision.schema.v1.json` | validate routing decisions already accepted under v1 |

## Routing

Synthetic. Never executed.
