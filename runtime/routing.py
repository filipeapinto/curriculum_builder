from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
import yaml


class RoutingError(RuntimeError):
    pass


EFFORTS = ["medium", "high", "xhigh", "max"]
DETERMINISTIC_TASKS = {"merge", "validation", "hashing", "rendering", "aggregation", "audit", "logging"}


class Selector:
    def __init__(self, engine: Path):
        self.engine = engine.resolve()
        self.registry = yaml.safe_load((engine / "policy/routing/model_registry.v1.yaml").read_text())
        self.taxonomy = yaml.safe_load((engine / "policy/routing/task_taxonomy.v2.yaml").read_text())
        self.policy = yaml.safe_load((engine / "policy/routing/routing_policy.v1.yaml").read_text())
        self.schema = json.loads((engine / "schemas/routing_decision.schema.v2.json").read_text())

    def select(self, task_id: str, task_class: str, *, fallback_model: str | None = None,
               executed_model: str | None = None, force_effort: str | None = None) -> dict[str, Any]:
        if task_class in DETERMINISTIC_TASKS:
            raise RoutingError(f"deterministic work cannot be routed to a model: {task_class}")
        tasks = {name: value for name, value in self.taxonomy["tasks"].items()}
        if task_class not in tasks:
            raise RoutingError(f"task class is not declared: {task_class}")
        risk = tasks[task_class]["risk"]
        rule = self.policy["hard_rules"][risk]
        registered = self.registry["models"]
        candidate_pool = [model for model in rule["allowed_models"] if model in registered]
        if not candidate_pool:
            raise RoutingError(f"no registered eligible model for {task_class}")
        decided = candidate_pool[0]
        if fallback_model is not None:
            if decided in registered:
                if fallback_model != decided:
                    raise RoutingError("--model fallback may not bypass an available selector decision")
            elif fallback_model in candidate_pool:
                decided = fallback_model
            else:
                raise RoutingError("fallback model is not eligible")
        effort = force_effort or rule["minimum_reasoning_effort"]
        allowed_efforts = registered[decided]["reasoning_efforts"]
        if effort not in allowed_efforts:
            raise RoutingError(f"{decided} does not support policy effort {effort}")
        executed = executed_model or decided
        decision = {
            "task_id": task_id, "task_class": task_class, "risk": risk,
            "candidate_pool": candidate_pool, "decided_model": decided,
            "executed_model": executed, "reasoning_effort": effort,
            "pro_mode": bool(rule.get("pro_mode_for_final_judgment", False)),
            "quality_gate": tasks[task_class]["evidence_required"],
            "decision_rationale": "smallest eligible candidate pool under hard safety rules",
            "evidence_inputs": tasks[task_class]["evidence_required"],
            "escalate_when": [item["condition"] for item in self.policy.get("escalation_rules", [])],
            "substitution": None, "status": "approved_to_run",
        }
        jsonschema.Draft202012Validator(self.schema).validate(decision)
        if executed != decided:
            raise RoutingError(f"executed model {executed} differs from decided model {decided}")
        return decision

    def validate_decision(self, decision: dict[str, Any]) -> None:
        jsonschema.Draft202012Validator(self.schema).validate(decision)
        if decision["decided_model"] != decision["executed_model"]:
            raise RoutingError("executed_model must equal decided_model")
