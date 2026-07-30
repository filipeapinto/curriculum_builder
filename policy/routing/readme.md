# Model Selector — v1

This package separates task classification, model selection, and quality escalation from the lab orchestrator.

The selector does not author a lab. It reads the task, applicable quality gates, available model registry, and prior evaluation evidence; it then produces a recorded routing decision. The orchestrator must use that decision or record why it could not.

## Files

- `model_registry.v1.yaml` — current model capabilities and availability.
- `task_taxonomy.v2.yaml` — current task classes and risk profiles, including workbook/PDF assembly.
- `routing_policy.v1.yaml` — candidate-pool and escalation policy.
- `quality_gates.v1.yaml` — observable acceptance gates, not model self-confidence.
- `routing_decision.schema.v1.json` — required decision-record format.
- `model_selector_prompt.v1.md` — prompt for the selector.

## Design rule

Hard safety rules constrain the eligible model pool. Task classification chooses among the eligible models. QA outcomes determine acceptance, retry, or escalation. No model may approve its own unsupported technical claim.
