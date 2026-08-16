"""Contained live model transports for Plan 25 model-worker nodes."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any, Protocol

import jsonschema

from .gemini import write_run_local_settings
from .io import atomic_json, sha256_file
from .routing import Selector


class WorkerFailure(RuntimeError):
    pass


class Worker(Protocol):
    family: str

    def probe(self, workspace: Path) -> dict[str, Any]: ...

    def run(self, *, activation_id: str, job: str, prompt_path: Path,
            request: dict[str, Any], output_schema: dict[str, Any],
            workspace: Path) -> tuple[dict[str, Any], dict[str, Any]]: ...


TASK_CLASS = {
    "research_unit_sources": "component_research",
    "create_unit_domain_data": "final_acceptance",
    "write_unit_content": "child_explanatory_writing",
    "create_unit_visuals": "photorealistic_visual_prompt",
    "repair_unit_artifact": "final_acceptance",
    "repair_workbook": "workbook_assembly",
}


def _extract_json(text: str) -> dict[str, Any]:
    value = text.strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value)
        value = re.sub(r"\s*```$", "", value)
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise WorkerFailure(f"worker final response is not JSON: {error}: {value[:300]}") from error
    if not isinstance(parsed, dict):
        raise WorkerFailure("worker response must be a JSON object")
    return parsed


class CodexWorker:
    """Run bounded author/research/repair jobs through the policy selector and Codex CLI."""

    family = "openai"

    def __init__(self, engine: Path, *, fallback_model: str | None = None,
                 timeout_seconds: int = 900):
        self.engine = Path(engine).resolve()
        self.selector = Selector(self.engine)
        self.fallback_model = fallback_model
        self.timeout_seconds = timeout_seconds

    def _decision(self, activation_id: str, job: str) -> dict[str, Any]:
        task_class = TASK_CLASS.get(job)
        if not task_class:
            raise WorkerFailure(f"no model task class for {job}")
        return self.selector.select(activation_id, task_class, fallback_model=self.fallback_model)

    def probe(self, workspace: Path) -> dict[str, Any]:
        schema = {"type": "object", "additionalProperties": False,
                  "required": ["status"], "properties": {"status": {"const": "ROUTE_OK"}}}
        probe_prompt = workspace / "probe.prompt.md"
        probe_prompt.write_text("Return exactly the JSON object required by the supplied schema.\n")
        result, receipt = self.run(
            activation_id="D03-worker-probe", job="write_unit_content",
            prompt_path=probe_prompt, request={"probe": True}, output_schema=schema,
            workspace=workspace / "worker_probe")
        if result != {"status": "ROUTE_OK"}:
            raise WorkerFailure(f"worker probe returned {result}")
        return receipt

    def run(self, *, activation_id: str, job: str, prompt_path: Path,
            request: dict[str, Any], output_schema: dict[str, Any],
            workspace: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        if not prompt_path.is_file():
            raise WorkerFailure(f"model prompt does not resolve: {prompt_path}")
        workspace = Path(workspace).resolve()
        workspace.mkdir(parents=True, exist_ok=False)
        decision = self._decision(activation_id, job)
        instruction = (
            prompt_path.read_text(encoding="utf-8")
            + "\n\nThe controller staged your only authorized input at authorized_input.json. "
              "Read it, perform exactly this job, and return only the JSON object required by "
              "output.schema.json. Do not inspect parent directories. Do not decide graph state."
        )
        with tempfile.TemporaryDirectory(prefix="curriculum-factory-model-") as isolated_name:
            isolated = Path(isolated_name).resolve()
            request_path = isolated / "authorized_input.json"
            schema_path = isolated / "output.schema.json"
            result_path = isolated / "result.json"
            atomic_json(request_path, request, root=isolated)
            atomic_json(schema_path, output_schema, root=isolated)
            command = [
                "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
                "-s", "read-only", "--skip-git-repo-check", "-C", str(isolated),
                "-m", decision["decided_model"],
                "-c", f'model_reasoning_effort="{decision["reasoning_effort"]}"',
                "--output-schema", str(schema_path), "-o", str(result_path), instruction,
            ]
            started = datetime.now(timezone.utc)
            proc = subprocess.run(command, cwd=isolated, capture_output=True, text=True,
                                  timeout=self.timeout_seconds)
            ended = datetime.now(timezone.utc)
            if proc.returncode != 0 or not result_path.is_file():
                shutil.copy2(request_path, workspace / request_path.name)
                shutil.copy2(schema_path, workspace / schema_path.name)
                raise WorkerFailure(
                    f"{job} failed with exit {proc.returncode}: {(proc.stderr or proc.stdout)[-2000:]}")
            result = _extract_json(result_path.read_text(encoding="utf-8"))
            for path in (request_path, schema_path, result_path):
                shutil.copy2(path, workspace / path.name)
        jsonschema.Draft202012Validator(output_schema).validate(result)
        request_path = workspace / "authorized_input.json"
        result_path = workspace / "result.json"
        receipt = {
            "activation_id": activation_id, "job": job, "family": self.family,
            "decision": decision, "command": command, "returncode": proc.returncode,
            "started_utc": started.isoformat(), "ended_utc": ended.isoformat(),
            "elapsed_seconds": (ended - started).total_seconds(),
            "prompt_sha256": sha256_file(prompt_path),
            "input_sha256": sha256_file(request_path),
            "output_sha256": sha256_file(result_path),
            "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:],
        }
        return result, receipt


class GeminiReviewer:
    """Independent, no-tools, cross-family transport for actual product reviews."""

    family = "google"

    def __init__(self, engine: Path, *, model: str = "gemini-3-pro-preview",
                 timeout_seconds: int = 900):
        self.engine = Path(engine).resolve()
        self.model = model
        self.timeout_seconds = timeout_seconds

    def probe(self, workspace: Path) -> dict[str, Any]:
        schema = {"type": "object", "additionalProperties": False,
                  "required": ["status"], "properties": {"status": {"const": "ROUTE_OK"}}}
        prompt = workspace / "review-probe.prompt.md"
        prompt.write_text("Return only {\"status\":\"ROUTE_OK\"}.\n")
        result, receipt = self.run(
            activation_id="D03-review-probe", job="review_unit", prompt_path=prompt,
            request={"probe": True}, output_schema=schema,
            workspace=workspace / "reviewer_probe")
        if result != {"status": "ROUTE_OK"}:
            raise WorkerFailure(f"reviewer probe returned {result}")
        return receipt

    def run(self, *, activation_id: str, job: str, prompt_path: Path,
            request: dict[str, Any], output_schema: dict[str, Any],
            workspace: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        if job not in {"review_unit", "review_workbook"}:
            raise WorkerFailure(f"independent reviewer cannot perform {job}")
        workspace = Path(workspace).resolve()
        workspace.mkdir(parents=True, exist_ok=False)
        instruction = (
            prompt_path.read_text(encoding="utf-8")
            + "\n\nReview only authorized_input.json. Return only one JSON object conforming "
              "exactly to output.schema.json, without a Markdown fence. Do not use tools."
        )
        with tempfile.TemporaryDirectory(prefix="curriculum-factory-review-") as isolated_name:
            isolated = Path(isolated_name).resolve()
            request_path = isolated / "authorized_input.json"
            schema_path = isolated / "output.schema.json"
            atomic_json(request_path, request, root=isolated)
            atomic_json(schema_path, output_schema, root=isolated)
            settings_path, settings_hash = write_run_local_settings(isolated, self.model)
            environment = dict(os.environ)
            environment["GEMINI_CLI_SYSTEM_SETTINGS_PATH"] = str(settings_path)
            command = ["gemini", "-m", self.model, "-s", "--approval-mode", "default",
                       "--output-format", "json", instruction]
            started = datetime.now(timezone.utc)
            proc = subprocess.run(command, cwd=isolated, env=environment,
                                  capture_output=True, text=True, timeout=self.timeout_seconds)
            ended = datetime.now(timezone.utc)
            if proc.returncode != 0:
                raise WorkerFailure(f"{job} reviewer failed: {(proc.stderr or proc.stdout)[-2000:]}")
            outer = json.loads(proc.stdout)
            response = outer.get("response") if isinstance(outer, dict) else None
            result = _extract_json(response if isinstance(response, str) else proc.stdout)
            for path in (request_path, schema_path, settings_path):
                target = workspace / ("gemini_system_settings.json" if path == settings_path else path.name)
                shutil.copy2(path, target)
        jsonschema.Draft202012Validator(output_schema).validate(result)
        result_path = workspace / "result.json"
        atomic_json(result_path, result, root=workspace)
        request_path = workspace / "authorized_input.json"
        decision = {
            "task_id": activation_id, "task_class": (
                "pedagogy_qa" if job == "review_unit" else "curriculum_final_review"),
            "risk": "safety_critical", "candidate_pool": [self.model],
            "decided_model": self.model, "executed_model": self.model,
            "reasoning_effort": "max", "pro_mode": True,
            "quality_gate": ["actual_artifact", "every_rendered_page", "frozen_rubric"],
            "decision_rationale": "required independent cross-family product review",
            "evidence_inputs": ["authorized_input.json"], "escalate_when": [],
            "substitution": None, "status": "approved_to_run",
        }
        receipt = {
            "activation_id": activation_id, "job": job, "family": self.family,
            "decision": decision, "command": command, "returncode": proc.returncode,
            "started_utc": started.isoformat(), "ended_utc": ended.isoformat(),
            "elapsed_seconds": (ended - started).total_seconds(),
            "settings_sha256": settings_hash, "prompt_sha256": sha256_file(prompt_path),
            "input_sha256": sha256_file(request_path), "output_sha256": sha256_file(result_path),
            "stderr": proc.stderr[-4000:],
        }
        return result, receipt
