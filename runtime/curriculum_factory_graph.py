"""Executable Plan 25 curriculum-factory graph.

The graph consumes one supplied manifest and produces accepted unit/workbook artifacts.
Controller code owns every node activation, reducer, check, repair route, checkpoint,
acceptance decision, and terminal. Model transports only return bounded artifacts or
findings.
"""
from __future__ import annotations

from base64 import b64encode
from datetime import date
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Callable
from urllib.request import Request, urlopen

import jsonschema
import yaml

from . import pdf_inspect, run_state
from .checks import (CheckFailure, bloom_report, check_claim_entailment, check_derivation,
                     check_receipts, pdf_page_count, rasterize_and_check_nonblank,
                     readability_problems, required_checks_for, validate_unit)
from .checkpoint import Checkpoints
from .controller import CurriculumRuntime, RuntimeFailure
from .factory_state import FactoryStateStore, utc_now
from .io import atomic_json, canonical_hash, require_internal_output, sha256_file
from .lesson_render import child_facing_text, render_unit
from .logger import ExecutionLogger
from .model_worker import CodexWorker, GeminiReviewer, Worker, WorkerFailure
from .visual_maps import VisualMapError, regenerate_assets


GRAPH_PACKAGE = "plans/25_curriculum_factory_graph"
GRAPH_FILE = "curriculum_factory.graph.v1.md"
PROMPT_FILES = {
    "research_unit_sources": "research_unit_sources.prompt.v1.md",
    "create_unit_domain_data": "create_unit_domain_data.prompt.v1.md",
    "write_unit_content": "write_unit_content.prompt.v1.md",
    "create_unit_visuals": "create_unit_visuals.prompt.v1.md",
    "review_unit": "review_unit.prompt.v1.md",
    "repair_unit_artifact": "repair_unit_artifact.prompt.v1.md",
    "review_workbook": "review_workbook.prompt.v1.md",
    "repair_workbook": "repair_workbook.prompt.v1.md",
}

# These constants are executable node identities and make graph/code agreement testable.
NODE_IDS = (
    "D01_VALIDATE_AND_FREEZE_RUN", "D02_COMPILE_MANIFEST_RUN",
    "D03_PROVE_REQUIRED_CAPABILITIES", "D04_RESUME_OR_INITIALIZE",
    "D05_SELECT_NEXT_UNIT", "D06_COMPILE_AND_RETRIEVE_SOURCE_REQUESTS",
    "D07_ADMIT_SOURCE_JOIN", "D08_VALIDATE_DOMAIN", "D09_VALIDATE_UNIT_CONTENT",
    "D10_COMPILE_VISUAL_BRIEFS", "D11_RENDER_DETERMINISTIC_VISUALS",
    "D12_JOIN_AND_VERIFY_VISUALS", "D13_RENDER_UNIT", "D14_INSPECT_UNIT_PAGES",
    "D15_FREEZE_UNIT_REVIEW_PACKET", "D16_REDUCE_UNIT_EVIDENCE",
    "D17_CLASSIFY_UNIT_FINDINGS", "D18_PLAN_UNIT_REPAIR",
    "D19_ROUTE_UNIT_REPAIR", "D20_ADMIT_UNIT_REPAIR",
    "D21_RETEST_UNIT_DESCENDANTS", "D22_ACCEPT_UNIT",
    "D23_CHECKPOINT_ACCEPTED_UNIT", "D24_COMPUTE_MANIFEST_COVERAGE",
    "D25_ASSEMBLE_WORKBOOK", "D26_RENDER_AND_INSPECT_WORKBOOK_PAGES",
    "D27_FREEZE_WORKBOOK_REVIEW_PACKET", "D28_REDUCE_WORKBOOK_EVIDENCE",
    "D29_ROUTE_WORKBOOK_REPAIR", "D30_CLASSIFY_PREREQUISITE",
    "D31_ADMIT_WORKBOOK_REPAIR", "D32_FINAL_RELEASE_AUDIT",
    "M01_RESEARCH_UNIT_SOURCES", "M02_CREATE_UNIT_DOMAIN_DATA",
    "M03_WRITE_UNIT_CONTENT", "M04_CREATE_UNIT_VISUALS", "M05_REVIEW_UNIT",
    "M06_REPAIR_UNIT_ARTIFACT", "M07_REVIEW_WORKBOOK", "M08_REPAIR_WORKBOOK",
)


class FactoryGraphFailure(RuntimeError):
    def __init__(self, failure_id: str, message: str, *, terminal: str = "SYSTEM_FAILURE",
                 evidence: dict[str, Any] | None = None):
        super().__init__(message)
        self.failure_id = failure_id
        self.terminal = terminal
        self.evidence = evidence or {}


class PrerequisitePause(FactoryGraphFailure):
    def __init__(self, failure_id: str, message: str, evidence: dict[str, Any]):
        super().__init__(failure_id, message, terminal="PAUSED_PREREQUISITE", evidence=evidence)


class ConvergenceExhausted(FactoryGraphFailure):
    def __init__(self, message: str, evidence: dict[str, Any]):
        super().__init__("REPAIR-BOUND-EXHAUSTED", message,
                         terminal="CONVERGENCE_EXHAUSTED", evidence=evidence)


RESEARCH_DISCOVERY_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["sources"],
    "properties": {"sources": {"type": "array", "minItems": 1, "items": {
        "type": "object", "additionalProperties": False,
        "required": ["url", "publisher", "title", "claim_scope", "why_primary"],
        "properties": {
            "url": {"type": "string", "pattern": "^https?://"},
            "publisher": {"type": "string", "minLength": 2},
            "title": {"type": "string", "minLength": 2},
            "claim_scope": {"type": "string", "minLength": 5},
            "why_primary": {"type": "string", "minLength": 5},
        }}}}
}

RESEARCH_INTERPRET_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["sources", "unresolved"],
    "properties": {
        "sources": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["retrieval_result_id", "source_title", "publisher",
                         "exact_locator", "supported_facts", "claim_scope"],
            "properties": {
                "retrieval_result_id": {"type": "string"},
                "source_title": {"type": "string"}, "publisher": {"type": "string"},
                "exact_locator": {"type": "string", "minLength": 1},
                "supported_facts": {"type": "array", "minItems": 1,
                                    "items": {"type": "string", "minLength": 3}},
                "claim_scope": {"type": "string", "minLength": 3},
            }}},
        "unresolved": {"type": "array", "items": {"type": "string"}},
    }
}

VISUAL_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["filename", "svg", "role", "supports_section", "alt_text"],
    "properties": {
        "filename": {"type": "string", "pattern": "^[a-z0-9_-]+\\.svg$"},
        "svg": {"type": "string", "pattern": "<svg"},
        "role": {"enum": ["subject_identification", "purpose_or_application",
                            "orientation_and_parts", "mechanism", "expected_result",
                            "safety_or_troubleshooting"]},
        "supports_section": {"enum": ["engage", "explore", "explain", "elaborate",
                                       "evaluate", "identification", "troubleshooting"]},
        "alt_text": {"type": "string", "minLength": 10},
    }
}

REVIEW_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["findings", "page_results", "verdict"],
    "properties": {
        "findings": {"type": "array", "items": {"type": "object",
            "additionalProperties": False,
            "required": ["criterion_id", "severity", "artifact_owner", "exact_location",
                         "observed_defect", "required_correction"],
            "properties": {
                "criterion_id": {"type": "string"},
                "severity": {"enum": ["blocking", "advisory"]},
                "artifact_owner": {"enum": ["source_interpretation", "domain",
                                               "unit_content", "unit_visual", "unit_layout",
                                               "workbook"]},
                "exact_location": {"type": "string"},
                "observed_defect": {"type": "string"},
                "required_correction": {"type": "string"},
            }},
        },
        "page_results": {"type": "array", "items": {"type": "object",
            "additionalProperties": False, "required": ["page_number", "result", "notes"],
            "properties": {"page_number": {"type": "integer", "minimum": 1},
                           "result": {"enum": ["PASS", "FAIL"]},
                           "notes": {"type": "string"}}}},
        "verdict": {"enum": ["PASS", "REPAIR_REQUIRED"]},
    }
}

WORKBOOK_REPAIR_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["front_matter_markdown", "finding_ids_addressed"],
    "properties": {
        "front_matter_markdown": {"type": "string"},
        "finding_ids_addressed": {"type": "array", "items": {"type": "string"}},
    }
}

UNIT_LAYOUT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["margin_inches", "font_scale", "finding_ids_addressed"],
    "properties": {
        "margin_inches": {"type": "number", "minimum": 0.55, "maximum": 1.25},
        "font_scale": {"type": "number", "minimum": 0.9, "maximum": 1.15},
        "finding_ids_addressed": {"type": "array", "items": {"type": "string"}},
    },
}

CHECK_OWNER = {
    "LAB-SCHEMA-VALID": "unit_content",
    "TEXT-READABILITY-BAND": "unit_content",
    "TEXT-BLOOM-VERBS": "unit_content",
    "DOC-DERIVED-FROM-SOURCE": "unit_content",
    "RECEIPT-HASH-RESOLVES": "unit_visual",
    "VISUAL-ROLES-COMPLETE": "unit_visual",
    "PDF-ASSET-RESOLVES": "unit_visual",
    "PDF-PAGE-COUNT": "unit_layout",
    "PDF-PAGE-NONBLANK": "unit_layout",
    "PDF-TEXT-LEGIBLE": "unit_layout",
    "PDF-VISUAL-REVIEW": "unit_layout",
    "DOMAIN-VERIFIER": "domain",
}


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _default_fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "curriculum-factory/1.0"})
    with urlopen(request, timeout=60) as response:
        return response.read()


class LiveCapabilities:
    def __init__(self, author: Worker, reviewer: Worker,
                 fetcher: Callable[[str], bytes] = _default_fetch):
        self.author = author
        self.reviewer = reviewer
        self.fetcher = fetcher

    def prove(self, root: Path, *, full_run: bool) -> dict[str, Any]:
        required = ["codex", "pandoc", "pdftoppm", "pdfinfo", "pdftotext", "pdfimages"]
        if full_run:
            required.append("pdfunite")
        missing = [tool for tool in required if shutil.which(tool) is None]
        if missing:
            raise FactoryGraphFailure("CAPABILITY-TOOL-MISSING", f"required tools missing: {missing}")
        proof_root = root / "capabilities"
        proof_root.mkdir(parents=True, exist_ok=True)
        author = self.author.probe(proof_root)
        reviewer = self.reviewer.probe(proof_root)
        # Real render/raster proof against current binaries.
        source = proof_root / "probe.md"
        pdf = proof_root / "probe.pdf"
        source.write_text("# Capability proof\n\nVisible page.\n", encoding="utf-8")
        rendered = subprocess.run(["pandoc", str(source), "--pdf-engine=typst", "-V",
                                   "mainfont=Helvetica", "-o", str(pdf)],
                                  capture_output=True, text=True)
        if rendered.returncode != 0:
            raise FactoryGraphFailure("CAPABILITY-PDF-FAILED", rendered.stderr)
        pages = rasterize_and_check_nonblank(pdf, proof_root / "pages", dpi=200)
        try:
            payload = self.fetcher("https://example.com/")
        except Exception as error:
            raise FactoryGraphFailure("CAPABILITY-SOURCE-FAILED", str(error)) from error
        if not payload:
            raise FactoryGraphFailure("CAPABILITY-SOURCE-EMPTY", "source probe returned zero bytes")
        return {
            "status": "PASS", "author": author, "reviewer": reviewer,
            "pdf_sha256": sha256_file(pdf), "raster_pages": len(pages),
            "source_probe_sha256": hashlib.sha256(payload).hexdigest(),
        }


class CurriculumFactoryGraph:
    def __init__(self, engine: Path | None = None, *, author: Worker | None = None,
                 reviewer: Worker | None = None,
                 fetcher: Callable[[str], bytes] = _default_fetch,
                 capabilities: Any | None = None):
        self.engine = Path(engine or Path(__file__).resolve().parents[1]).resolve()
        self.runtime = CurriculumRuntime(self.engine)
        self.author = author or CodexWorker(self.engine)
        self.reviewer = reviewer or GeminiReviewer(self.engine)
        self.fetcher = fetcher
        self.capabilities = capabilities or LiveCapabilities(self.author, self.reviewer, fetcher)
        self.package = self.engine / GRAPH_PACKAGE
        self.graph_path = self.package / GRAPH_FILE
        self.prompts = {job: self.package / "prompts" / name
                        for job, name in PROMPT_FILES.items()}
        self.output: Path | None = None
        self.curriculum: Path | None = None
        self.manifest_path: Path | None = None
        self.manifest: dict[str, Any] | None = None
        self.store: FactoryStateStore | None = None
        self.logger: ExecutionLogger | None = None
        self.started_at = time.monotonic()

    def _resolve_curriculum_input(self, value: Path | str) -> tuple[Path, Path]:
        """Accept either a curriculum directory or its exact active manifest path."""
        supplied = Path(value)
        supplied = supplied if supplied.is_absolute() else self.engine / supplied
        supplied = supplied.resolve()
        if supplied.is_file():
            curriculum = self.runtime.resolve_curriculum(supplied.parent)
            manifest_path, _ = self.runtime.validated_manifest(curriculum)
            if supplied != manifest_path.resolve():
                raise RuntimeFailure(
                    "PRECONDITION-MANIFEST-NOT-ACTIVE",
                    f"supplied manifest is not the active validated manifest: {supplied}")
            return curriculum, supplied
        curriculum = self.runtime.resolve_curriculum(supplied)
        manifest_path, _ = self.runtime.validated_manifest(curriculum)
        return curriculum, manifest_path

    # -- controller infrastructure -------------------------------------------------

    def _require_package(self) -> dict[str, str]:
        required = {"graph": self.graph_path, **self.prompts}
        missing = [str(path) for path in required.values() if not path.is_file()]
        if missing:
            raise FactoryGraphFailure("FACTORY-PACKAGE-INCOMPLETE", f"missing: {missing}")
        graph_text = self.graph_path.read_text(encoding="utf-8")
        for job, filename in PROMPT_FILES.items():
            relative = f"prompts/{filename}"
            if relative not in graph_text:
                raise FactoryGraphFailure(
                    "FACTORY-PROMPT-UNBOUND", f"graph does not bind package-relative {relative}")
        return {name: sha256_file(path) for name, path in required.items()}

    def _active_inputs(self, curriculum: Path, manifest_path: Path) -> dict[str, str]:
        fixed = [
            "meta_prompt/curriculum.prompt.v1.md", "meta_prompt/assets/pedagogy.v1.md",
            "meta_prompt/assets/unit_prose.v1.md", "meta_prompt/assets/model_selector_prompt.v1.md",
            "policy/calibration.v1.yaml", "policy/checks.v1.yaml", "policy/controller.v1.yaml",
            "policy/failures.v1.yaml", "policy/limits.v1.yaml", "policy/routes.v1.yaml",
            "policy/deferred.v1.yaml", "policy/routing/model_registry.v1.yaml",
            "policy/routing/quality_gates.v1.yaml", "policy/routing/routing_policy.v1.yaml",
            "policy/routing/task_taxonomy.v2.yaml", "schemas/curriculum.schema.v5.json",
            "schemas/lab.schema.v4.json", "schemas/manifest_domain.metaschema.v1.json",
            "schemas/routing_decision.schema.v2.json", "schemas/execution_log.schema.v2.json",
            "schemas/run_lifecycle.schema.v1.json",
        ]
        paths = [self.engine / value for value in fixed]
        paths += sorted((self.engine / "runtime").glob("*.py"))
        paths += sorted(path for path in curriculum.rglob("*")
                        if path.is_file() and "deprecated" not in path.parts)
        paths += [self.graph_path, *self.prompts.values(), manifest_path]
        unique = sorted({path.resolve() for path in paths})
        missing = [str(path) for path in unique if not path.is_file()]
        if missing:
            raise FactoryGraphFailure("FROZEN-INPUT-MISSING", f"missing active inputs: {missing}")
        return {str(path.relative_to(self.engine)): sha256_file(path) for path in unique}

    def _limits(self, overrides: dict[str, int] | None) -> dict[str, Any]:
        limits = json.loads(json.dumps(self.runtime.limit_policy))
        for name, value in (overrides or {}).items():
            matched = False
            for group in limits.values():
                if not isinstance(group, dict):
                    continue
                for entry in group.values():
                    if isinstance(entry, dict) and entry.get("flag", "").lstrip("-").replace("-", "_") == name:
                        if value < 0:
                            raise FactoryGraphFailure("LIMIT-INVALID", f"negative limit: {name}")
                        entry["value"] = value
                        matched = True
            if not matched:
                raise FactoryGraphFailure("LIMIT-UNDECLARED", name)
        return limits

    def _run_identity(self, frozen: dict[str, str], output: Path, mode: str,
                      requested_unit: str | None, limits: dict[str, Any]) -> dict[str, Any]:
        payload = {"graph_version": 1, "frozen_inputs": frozen,
                   "output_root": str(output), "mode": mode,
                   "requested_unit": requested_unit, "effective_limits": limits}
        return {**payload, "run_id": canonical_hash(payload)}

    def _checkpoint(self, node: str) -> None:
        assert self.output and self.store and self.manifest_path
        ordinal = self.store.increment("checkpoint_ordinal", 100000)
        snapshot = self.output / "state_snapshots" / f"{ordinal:05d}_{node}.json"
        atomic_json(snapshot, self.store.read(), root=self.output)
        checkpoint = Checkpoints(self.output).write(
            ordinal=ordinal, state=node, next_state="GUARDED_EDGE",
            inputs=[self.manifest_path, self.graph_path], outputs=[snapshot],
            attempt=int(self.store.read()["counters"].get(f"node:{node}", 1)),
            started_at=self.started_at)
        self.store.append_unique("checkpoints", str(ordinal), {
            "node": node, "path": str(checkpoint.relative_to(self.output)),
            "sha256": sha256_file(checkpoint), "snapshot_sha256": sha256_file(snapshot)})

    def _activate(self, node: str, function: Callable[[], Any], *, checkpoint: bool = True) -> Any:
        assert self.output and self.store and self.logger
        if node not in NODE_IDS:
            raise FactoryGraphFailure("GRAPH-NODE-UNDECLARED", node)
        self.store.increment(f"node:{node}", 100000)
        start = self.logger.start(
            action=f"Activate curriculum factory graph node {node}", action_kind="state_transition",
            authorized_paths=[str(self.output)], trigger="declared guarded graph edge",
            expected=f"typed output for {node}", notes=node)
        self.store.append_event("NODE_STARTED", {"node": node})
        try:
            result = function()
        except KeyboardInterrupt:
            self.logger.fail(start, failure_type="other", what_failed=f"{node}: interrupted",
                             expected=f"typed output for {node}", notes="KeyboardInterrupt")
            self.store.append_event("NODE_INTERRUPTED", {"node": node})
            raise
        except Exception as error:
            self.logger.fail(start, failure_type="other", what_failed=f"{node}: {error}"[:2000],
                             expected=f"typed output for {node}", notes=type(error).__name__)
            self.store.append_event("NODE_FAILED", {"node": node, "error": str(error)})
            raise
        result_hash = canonical_hash(_json_safe(result))
        self.logger.complete(start, result=f"{node} completed",
                             notes=f"{node} result={result_hash}")
        self.store.append_event("NODE_COMPLETED", {"node": node, "result_hash": result_hash})
        if checkpoint:
            self._checkpoint(node)
        return result

    def _model(self, node: str, job: str, request: dict[str, Any], schema: dict[str, Any],
               *, reviewer: bool = False) -> dict[str, Any]:
        assert self.output and self.store and self.logger
        if node not in NODE_IDS or not node.startswith("M"):
            raise FactoryGraphFailure("GRAPH-MODEL-NODE-UNDECLARED", node)
        self.store.increment(f"node:{node}", 100000)
        self.store.append_event("NODE_STARTED", {"node": node, "job": job})
        worker = self.reviewer if reviewer else self.author
        unit_key = str(request.get("unit_id", "workbook"))
        retry_max = int(self.store.read()["effective_limits"]["retry"]
                        ["malformed_structured_output"]["value"]) + 1
        invocation = self.store.increment(f"model_invocations:{unit_key}", 100000)
        attempt_key = f"model_attempts:{unit_key}:{invocation}"
        last_error: Exception | None = None
        for _ in range(retry_max):
            if unit_key != "workbook":
                per_unit_max = int(self.store.read()["effective_limits"]["per_lab"]
                                   ["max_model_calls"]["value"])
                self.store.increment(f"model_calls:{unit_key}", per_unit_max)
            attempt = self.store.increment(attempt_key, retry_max)
            activation_id = f"{node}-{unit_key}-{invocation:03d}-{attempt:02d}"
            workspace = self.output / "model_activations" / activation_id
            start = self.logger.start(
                action=f"Execute bounded model job {job}", action_kind="model_call",
                decision_id=activation_id, authorized_paths=[str(workspace)],
                trigger=node, expected="one schema-valid bounded result")
            try:
                result, receipt = worker.run(
                    activation_id=activation_id, job=job, prompt_path=self.prompts[job],
                    request=request, output_schema=schema, workspace=workspace)
                decision = receipt.get("decision")
                if not isinstance(decision, dict):
                    raise WorkerFailure("model receipt has no routing decision")
                self.runtime.selector.validate_decision(decision)
                if decision["task_id"] != activation_id:
                    raise WorkerFailure("routing decision is correlated to another activation")
                if receipt.get("family") == getattr(self.author, "family", None) and reviewer:
                    raise WorkerFailure("reviewer family equals author family")
                self.store.append_unique("route_decisions", activation_id, decision)
                self.logger.complete(start, result=f"{job} produced a schema-valid result",
                                     notes=f"output={receipt.get('output_sha256')}")
                self.store.append_event("MODEL_RESULT", {
                    "node": node, "activation_id": activation_id,
                    "receipt_hash": canonical_hash(receipt)})
                self.store.append_event("NODE_COMPLETED", {
                    "node": node, "result_hash": canonical_hash(result)})
                self._checkpoint(node)
                return result
            except KeyboardInterrupt:
                self.logger.fail(start, failure_type="other", what_failed=f"{job}: interrupted",
                                 expected="one schema-valid bounded result",
                                 notes="external KeyboardInterrupt")
                self.store.append_event("NODE_INTERRUPTED", {"node": node, "job": job})
                raise
            except Exception as error:
                last_error = error
                self.logger.fail(start, failure_type="wrong-output", what_failed=str(error)[:2000],
                                 expected="one schema-valid bounded result")
                if not isinstance(error, (WorkerFailure, jsonschema.ValidationError)):
                    self.store.append_event("NODE_FAILED", {"node": node, "error": str(error)})
                    raise
        self.store.append_event("NODE_FAILED", {"node": node, "error": str(last_error)})
        raise FactoryGraphFailure("MODEL-OUTPUT-INVALID", str(last_error))

    def _artifact(self, unit_id: str, artifact_type: str, version: int, path: Path,
                  *, parent_version: int | None = None) -> dict[str, Any]:
        assert self.output and self.store
        record = {"unit_id": unit_id, "artifact_type": artifact_type, "version": version,
                  "parent_version": parent_version, "path": str(path.relative_to(self.output)),
                  "sha256": sha256_file(path), "recorded_utc": utc_now()}
        self.store.append_unique("unit_artifacts", f"{unit_id}:{artifact_type}:v{version}", record)
        current = self.store.read()["unit_heads"].get(f"{unit_id}:{artifact_type}")
        self.store.replace_current("unit_heads", f"{unit_id}:{artifact_type}", version,
                                   previous_version=current)
        return record

    # -- source/domain/content nodes ------------------------------------------------

    def _seed(self, unit_id: str) -> dict[str, Any] | None:
        assert self.curriculum
        candidates = sorted(path for path in self.curriculum.glob(f"{unit_id.lower()}*.json")
                            if "schema" not in path.name and "fixture" not in path.parts)
        return json.loads(candidates[0].read_text()) if len(candidates) == 1 else None

    def _source_request(self, unit: dict[str, Any]) -> dict[str, Any]:
        return {
            "unit_id": unit["id"],
            "question": (f"Find official primary sources supporting this unit's subject job, required "
                         f"explanations, activity and safety claims: {unit['subject_job']} | "
                         f"{' | '.join(unit['required_explanation'])}"),
            "required_claims": [unit["subject_job"], *unit["required_explanation"],
                                *unit["safety_focus"]],
            "authority": "official manufacturer, standards body, government, or original technical source",
        }

    def _research(self, unit: dict[str, Any], unit_root: Path) -> dict[str, Any]:
        assert self.store and self.output
        unit_id = unit["id"]
        inputs = unit_root / "inputs"
        inputs.mkdir(parents=True, exist_ok=True)
        projected = [self.manifest_path,
                     self.engine / self.manifest["domain"]["schema"],
                     self.engine / self.manifest["domain"]["manifest_schema"],
                     self.engine / "policy/calibration.v1.yaml"]
        for value in self.manifest["domain"]["config"].values():
            if isinstance(value, str):
                candidate = self.engine / value
                if candidate.is_file():
                    projected.append(candidate)
        for name in ("kit_calibration.v1.yaml", "circuit_library.v1.yaml", "checks.v1.yaml"):
            candidate = self.curriculum / name
            if candidate.is_file():
                projected.append(candidate)
        for source in sorted({path.resolve() for path in projected if path is not None}):
            target = inputs / source.name
            if target.exists() and sha256_file(target) != sha256_file(source):
                raise FactoryGraphFailure("UNIT-INPUT-NAME-COLLISION", source.name)
            if not target.exists():
                shutil.copy2(source, target)
        source_request = self._source_request(unit)
        self.store.append_unique("source_requests", f"{unit_id}:primary", source_request)
        seed = self._seed(unit_id)
        declared = list((seed or {}).get("primary_sources", []))
        if not declared:
            discovered = self._model(
                "M01_RESEARCH_UNIT_SOURCES", "research_unit_sources",
                {"mode": "DISCOVER", "unit_id": unit_id, "source_request": source_request,
                 "retrieval_capability": "web search restricted to primary authorities"},
                RESEARCH_DISCOVERY_SCHEMA)
            declared = discovered["sources"]
        retrievals = []
        source_dir = unit_root / "sources"
        source_dir.mkdir(parents=True, exist_ok=True)
        for index, declaration in enumerate(declared, 1):
            url = declaration.get("url_or_path") or declaration.get("url")
            if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                continue
            try:
                payload = self.fetcher(url)
            except Exception as error:
                raise PrerequisitePause(
                    "SOURCE-PRIMARY-UNAVAILABLE", f"required primary source unavailable: {url}",
                    {"unit_id": unit_id, "url": url, "error": str(error)}) from error
            target = source_dir / f"source_{index:02d}.html"
            target.write_bytes(payload)
            record = {
                "retrieval_result_id": f"{unit_id}-source-{index:02d}", "url": url,
                "path": str(target.relative_to(unit_root)), "sha256": sha256_file(target),
                "bytes": len(payload), "access_date": date.today().isoformat(),
                "declared": declaration,
                "text_excerpt": payload.decode("utf-8", errors="replace")[:50000],
            }
            retrievals.append(record)
            self.store.append_unique("retrieval_results", record["retrieval_result_id"],
                                     {key: value for key, value in record.items() if key != "text_excerpt"})
        if not retrievals:
            raise PrerequisitePause(
                "SOURCE-NO-PRIMARY-RESULT", f"no primary source could be retrieved for {unit_id}",
                {"unit_id": unit_id, "request": source_request})
        interpreted = self._model(
            "M01_RESEARCH_UNIT_SOURCES", "research_unit_sources",
            {"mode": "INTERPRET", "unit_id": unit_id, "source_request": source_request,
             "allowed_retrieval_results": retrievals}, RESEARCH_INTERPRET_SCHEMA)
        known = {item["retrieval_result_id"] for item in retrievals}
        if any(item["retrieval_result_id"] not in known for item in interpreted["sources"]):
            raise FactoryGraphFailure("SOURCE-JOIN-CORRELATION", "research cited an unknown retrieval result")
        if interpreted["unresolved"]:
            raise PrerequisitePause(
                "SOURCE-FACT-UNRESOLVED", f"required source facts unresolved for {unit_id}",
                {"unit_id": unit_id, "unresolved": interpreted["unresolved"]})
        atomic_json(source_dir / "source_manifest.json", {
            "sources": [{key: value for key, value in item.items() if key != "text_excerpt"}
                        for item in retrievals], "interpretation": interpreted}, root=unit_root)
        self.store.append_unique("source_results", f"{unit_id}:primary", interpreted)
        self.store.append_unique("admitted_sources", f"{unit_id}:v1", {
            "source_manifest": str((source_dir / "source_manifest.json").relative_to(self.output)),
            "sha256": sha256_file(source_dir / "source_manifest.json")})
        return {"seed": seed, "research": interpreted, "retrievals": retrievals}

    def _resume_research(self, unit: dict[str, Any], unit_root: Path) -> dict[str, Any] | None:
        assert self.store
        key = f"{unit['id']}:primary"
        path = unit_root / "sources/source_manifest.json"
        state = self.store.read()
        if key not in state["source_results"] or not path.is_file():
            return None
        manifest = json.loads(path.read_text())
        retrievals = []
        for record in manifest["sources"]:
            cached = unit_root / record["path"]
            if not cached.is_file() or sha256_file(cached) != record["sha256"]:
                raise FactoryGraphFailure("RESUME-SOURCE-HASH-MISMATCH", str(cached))
            retrievals.append({**record,
                               "text_excerpt": cached.read_text(errors="replace")[:50000]})
        return {"seed": self._seed(unit["id"]), "research": manifest["interpretation"],
                "retrievals": retrievals}

    def _resume_artifact(self, unit_id: str, artifact_type: str) -> dict[str, Any] | None:
        assert self.store and self.output
        state = self.store.read()
        version = state["unit_heads"].get(f"{unit_id}:{artifact_type}")
        if version is None:
            return None
        record = state["unit_artifacts"].get(f"{unit_id}:{artifact_type}:v{version}")
        if not record:
            raise FactoryGraphFailure("RESUME-ARTIFACT-HEAD-MISSING", f"{unit_id}:{artifact_type}:v{version}")
        path = self.output / record["path"]
        if not path.is_file() or sha256_file(path) != record["sha256"]:
            raise FactoryGraphFailure("RESUME-ARTIFACT-HASH-MISMATCH", str(path))
        value = json.loads(path.read_text())
        return {"path": path, "version": version,
                "domain" if artifact_type == "domain" else "lab": value}

    def _run_verifier(self, domain_path: Path) -> str:
        assert self.manifest and self.curriculum
        entry = self.engine / self.manifest["domain"]["verifier"]["entry_point"]
        proc = subprocess.run(["python3", str(entry), "--domain", str(domain_path)],
                              cwd=self.engine, capture_output=True, text=True)
        if proc.returncode != 0:
            raise CheckFailure((proc.stdout + proc.stderr)[-4000:])
        return proc.stdout.strip()

    def _create_domain(self, unit: dict[str, Any], research: dict[str, Any],
                       unit_root: Path) -> dict[str, Any]:
        assert self.manifest and self.store
        unit_id = unit["id"]
        schema = json.loads((self.engine / self.manifest["domain"]["schema"]).read_text())
        request = {
            "unit_id": unit_id, "manifest_unit": unit,
            "admitted_sources": research["research"],
            "retrieval_records": [{key: value for key, value in item.items()
                                   if key != "text_excerpt"} for item in research["retrievals"]],
            "domain_schema": schema, "domain_config": self.manifest["domain"]["config"],
            "curriculum_calibration": self._curriculum_calibration(),
            "existing_curriculum_domain_seed": research["seed"],
        }
        domain = self._model("M02_CREATE_UNIT_DOMAIN_DATA", "create_unit_domain_data", request, schema)
        current = self.store.read()["unit_heads"].get(f"{unit_id}:domain")
        version = int(current or 0) + 1
        parent_version = current
        repairs = 0
        maximum = int(self.store.read()["effective_limits"]["per_lab"]["max_revisions"]["value"])
        while True:
            path = unit_root / "artifacts" / "domain" / f"v{version}.json"
            atomic_json(path, domain, root=unit_root)
            try:
                jsonschema.Draft202012Validator(schema).validate(domain)
                verifier = self._run_verifier(path)
                self._artifact(unit_id, "domain", version, path,
                               parent_version=parent_version)
                return {"domain": domain, "path": path, "verifier": verifier,
                        "schema": schema, "version": version}
            except (jsonschema.ValidationError, CheckFailure) as error:
                if repairs >= maximum:
                    raise ConvergenceExhausted(
                        f"domain repair exhausted for {unit_id}",
                        {"unit_id": unit_id, "finding": str(error), "attempts": repairs})
                repair = self._model(
                    "M06_REPAIR_UNIT_ARTIFACT", "repair_unit_artifact",
                    {"unit_id": unit_id, "owner": "domain", "parent_version": version,
                     "parent_artifact": domain, "allowed_change_boundary": ["domain artifact"],
                     "named_findings": [str(error)], "required_retests": [
                         "domain schema", "curriculum verifier"]}, schema)
                self.store.append_unique("unit_repair_requests", f"{unit_id}:domain:{version}", {
                    "owner": "domain", "parent_version": version, "finding": str(error)})
                domain = repair
                parent_version = version
                version += 1
                repairs += 1

    def _curriculum_calibration(self) -> dict[str, Any] | None:
        assert self.curriculum
        candidates = sorted(self.curriculum.glob("*calibration*.yaml"))
        return yaml.safe_load(candidates[0].read_text()) if candidates else None

    def _write_content(self, unit: dict[str, Any], domain_record: dict[str, Any],
                       research: dict[str, Any], unit_root: Path) -> dict[str, Any]:
        assert self.store
        schema = json.loads((self.engine / "schemas/lab.schema.v4.json").read_text())
        unit_id = unit["id"]
        request = {
            "unit_id": unit_id, "manifest_unit": unit,
            "accepted_domain": domain_record["domain"],
            "accepted_domain_sha256": sha256_file(domain_record["path"]),
            "admitted_sources": research["research"], "lab_schema": schema,
            "engine_calibration": yaml.safe_load(
                (self.engine / "policy/calibration.v1.yaml").read_text()),
            "unit_prose": (self.engine / "meta_prompt/assets/unit_prose.v1.md").read_text(),
            "pedagogy": (self.engine / "meta_prompt/assets/pedagogy.v1.md").read_text(),
        }
        lab = self._model("M03_WRITE_UNIT_CONTENT", "write_unit_content", request, schema)
        current = self.store.read()["unit_heads"].get(f"{unit_id}:unit_content")
        version = int(current or 0) + 1
        parent_version = current
        repairs = 0
        maximum = int(self.store.read()["effective_limits"]["per_lab"]["max_revisions"]["value"])
        while True:
            path = unit_root / "artifacts" / "unit_content" / f"v{version}.json"
            atomic_json(path, lab, root=unit_root)
            try:
                validate_unit(lab, self.engine / "schemas/lab.schema.v4.json",
                              self.engine / self.manifest["domain"]["schema"])
                if lab["domain"] != domain_record["domain"]:
                    raise CheckFailure("unit domain differs from accepted domain artifact")
                check_derivation(lab)
                self._artifact(unit_id, "unit_content", version, path,
                               parent_version=parent_version)
                return {"lab": lab, "path": path, "schema": schema, "version": version}
            except (jsonschema.ValidationError, CheckFailure, KeyError, TypeError) as error:
                if repairs >= maximum:
                    raise ConvergenceExhausted(
                        f"unit-content repair exhausted for {unit_id}",
                        {"unit_id": unit_id, "finding": str(error), "attempts": repairs})
                lab = self._model(
                    "M06_REPAIR_UNIT_ARTIFACT", "repair_unit_artifact",
                    {"unit_id": unit_id, "owner": "unit_content", "parent_version": version,
                     "parent_artifact": lab, "immutable_domain": domain_record["domain"],
                     "allowed_change_boundary": ["unit content except domain"],
                     "named_findings": [str(error)],
                     "required_retests": ["lab schema", "domain equality", "derivation"]}, schema)
                parent_version = version
                version += 1
                repairs += 1

    # -- visual/render/review/accept ------------------------------------------------

    def _visuals(self, unit: dict[str, Any], content: dict[str, Any], unit_root: Path) -> dict[str, Any]:
        assert self.store
        lab = json.loads(json.dumps(content["lab"]))
        try:
            lab, unresolved = regenerate_assets(lab, self.curriculum, unit_root, unit_id=unit["id"])
        except VisualMapError as error:
            raise FactoryGraphFailure("VISUAL-DETERMINISTIC-RENDER", str(error)) from error
        for index, finding in enumerate(unresolved, 1):
            result = self._model(
                "M04_CREATE_UNIT_VISUALS", "create_unit_visuals",
                {"unit_id": unit["id"], "visual_id": f"model-{index:02d}",
                 "visual_brief": finding, "parent_facts": lab["domain"],
                 "constraints": ["non-authoritative", "no exact technical geometry",
                                 "legible and accessible at print size"]}, VISUAL_SCHEMA)
            target = unit_root / "assets" / result["filename"]
            target.write_text(result["svg"], encoding="utf-8")
            lab["visuals"].append({
                "role": result["role"], "source_kind": "imagegen",
                "supports_section": result["supports_section"],
                "carries_exact_domain_fact": False,
                "provenance": {"publisher": "Plan 25 bounded visual worker",
                               "item_or_family": finding["role"],
                               "access_date": date.today().isoformat(),
                               "file_hash": sha256_file(target),
                               "embedded_as": f"assets/{target.name}"},
                "omission_finding": "This supporting illustration carries no exact technical authority.",
            })
        lab["content"]["unresolved_visual_roles"] = []
        if len(lab["visuals"]) < len(unit["visual_roles"]):
            raise FactoryGraphFailure("VISUAL-DENOMINATOR-INCOMPLETE", unit["id"])
        image_max = int(self.store.read()["effective_limits"]["per_lab"]["max_images"]["value"])
        if len(lab["visuals"]) > image_max:
            raise ConvergenceExhausted(
                f"visual artifact limit reached for {unit['id']}",
                {"unit_id": unit["id"], "observed": len(lab["visuals"]), "limit": image_max})
        check_receipts({"visuals": {"receipts": [item["provenance"] for item in lab["visuals"]]}},
                        unit_root)
        version = content["version"] + 1
        path = unit_root / "artifacts" / "unit_content" / f"v{version}.json"
        atomic_json(path, lab, root=unit_root)
        self._artifact(unit["id"], "unit_content", version, path,
                       parent_version=content["version"])
        return {"lab": lab, "path": path, "version": version}

    def _render_and_check(self, unit: dict[str, Any], visual: dict[str, Any],
                          unit_root: Path, layout_spec: dict[str, Any] | None = None) -> dict[str, Any]:
        assert self.store
        lab = visual["lab"]
        document = unit_root / "document"
        if document.exists():
            shutil.rmtree(document)
        document.mkdir(parents=True)
        shutil.copytree(unit_root / "assets", document / "assets")
        markdown = document / f"{unit['id']}.md"
        body = render_unit(lab)
        markdown.write_text(body, encoding="utf-8")
        pdf = document / f"{unit['id']}.pdf"
        layout_spec = layout_spec or {"margin_inches": 0.8, "font_scale": 1.0}
        command = ["pandoc", str(markdown), "--resource-path", str(document),
                   "--pdf-engine=typst", "-V", "mainfont=Helvetica",
                   "-V", f"geometry:margin={layout_spec['margin_inches']}in",
                   "-V", f"fontsize={round(11 * layout_spec['font_scale'], 2)}pt",
                   "-o", str(pdf)]
        proc = subprocess.run(command,
                              cwd=unit_root, capture_output=True, text=True)
        if proc.returncode != 0:
            raise FactoryGraphFailure("PDF-RENDER-FAILED", proc.stderr)
        pages = rasterize_and_check_nonblank(pdf, document / "page_renders", dpi=200)
        checks: dict[str, dict[str, Any]] = {}

        def check(check_id: str, problems: list[Any] | None = None, evidence: Any = None) -> None:
            checks[check_id] = {"result": "PASS" if not problems else "FAIL",
                                "problems": problems or [], "evidence": evidence,
                                "subject_sha256": sha256_file(pdf)}

        try:
            validate_unit(lab, self.engine / "schemas/lab.schema.v4.json",
                          self.engine / self.manifest["domain"]["schema"])
            check("LAB-SCHEMA-VALID")
        except Exception as error:
            check("LAB-SCHEMA-VALID", [str(error)])
        try:
            derivation = check_derivation(lab)
            claims = check_claim_entailment(lab, unit_root)
            check("DOC-DERIVED-FROM-SOURCE", evidence={"derived": derivation, "claims": claims})
        except CheckFailure as error:
            check("DOC-DERIVED-FROM-SOURCE", [str(error)])
        try:
            receipts = check_receipts(
                {"visuals": {"receipts": [item["provenance"] for item in lab["visuals"]]}},
                unit_root)
            check("RECEIPT-HASH-RESOLVES", evidence=receipts)
        except CheckFailure as error:
            check("RECEIPT-HASH-RESOLVES", [str(error)])
        readability = readability_problems(child_facing_text(body),
                                            self.engine / "policy/calibration.v1.yaml")
        check("TEXT-READABILITY-BAND", readability)
        check("TEXT-BLOOM-VERBS", evidence=bloom_report(
            lab, self.engine / "policy/calibration.v1.yaml"))
        check("PDF-PAGE-COUNT", [] if pdf_page_count(pdf) == len(pages) else ["page count mismatch"])
        check("PDF-PAGE-NONBLANK")
        try:
            legible = pdf_inspect.text_legible(pdf)
            check("PDF-TEXT-LEGIBLE", legible["problems"], legible)
        except CheckFailure as error:
            check("PDF-TEXT-LEGIBLE", [str(error)])
        try:
            assets = pdf_inspect.assets_resolve(pdf, lab["visuals"], unit_root,
                                                unit_root / "results/pdf_images")
            check("PDF-ASSET-RESOLVES", assets["problems"], assets)
        except CheckFailure as error:
            check("PDF-ASSET-RESOLVES", [str(error)])
        check("VISUAL-ROLES-COMPLETE",
              [] if not lab["content"].get("unresolved_visual_roles") else
              lab["content"]["unresolved_visual_roles"])
        check("DOMAIN-VERIFIER")
        inventory = required_checks_for(self.engine, self.curriculum)
        required = inventory["required"]
        for check_id, metadata in required.items():
            if check_id not in checks:
                checks[check_id] = {"result": "NOT_RUN", "problems": ["required check not executed"],
                                    "subject_sha256": sha256_file(pdf),
                                    "blocking": metadata["blocking"]}
            else:
                checks[check_id]["blocking"] = metadata["blocking"]
        atomic_json(unit_root / "results/unit_checks.json", {
            "unit_id": unit["id"], "checks_version": inventory["checks_version"],
            "checks": checks}, root=unit_root)
        page_inventory = [{"page_number": index, "path": str(path.relative_to(unit_root)),
                           "sha256": sha256_file(path)} for index, path in enumerate(pages, 1)]
        atomic_json(unit_root / "results/page_inventory.json", {
            "pdf": str(pdf.relative_to(unit_root)), "pdf_sha256": sha256_file(pdf),
            "declared_page_count": len(pages), "pages": page_inventory}, root=unit_root)
        inventory_key = f"{unit['id']}:v{visual['version']}:{sha256_file(pdf)}"
        self.store.append_unique("unit_page_inventory", inventory_key, {
            "pdf_sha256": sha256_file(pdf), "pages": page_inventory})
        failures = sorted(check_id for check_id, result in checks.items()
                          if result.get("blocking", True) and result["result"] != "PASS")
        return {"lab": lab, "markdown": markdown, "pdf": pdf, "pages": pages,
                "page_inventory": page_inventory, "checks": checks, "failures": failures,
                "version": visual["version"]}

    def _review_unit(self, unit: dict[str, Any], rendered: dict[str, Any],
                     unit_root: Path) -> dict[str, Any]:
        pdf = rendered["pdf"]
        page_payloads = [{"page_number": index, "sha256": sha256_file(path),
                          "png_base64": b64encode(path.read_bytes()).decode("ascii")}
                         for index, path in enumerate(rendered["pages"], 1)]
        packet = {
            "unit_id": unit["id"], "unit_artifact": rendered["lab"],
            "unit_artifact_sha256": canonical_hash(rendered["lab"]),
            "pdf_sha256": sha256_file(pdf), "pages": page_payloads,
            "deterministic_results": rendered["checks"],
            "rubric": ["factual and source consistency", "domain-to-prose consistency",
                       "pedagogy and readability", "safety communication",
                       "visual truthfulness and relevance", "accessibility and print legibility",
                       "completeness and page coherence"],
            "randomized_presentation_seed": canonical_hash({"unit": unit["id"],
                                                              "pdf": sha256_file(pdf)}),
        }
        review_key = f"{unit['id']}:v{rendered['version']}:{sha256_file(pdf)}"
        self.store.append_unique("unit_review_packets", review_key, {
            "unit_id": unit["id"], "pdf_sha256": sha256_file(pdf),
            "page_count": len(page_payloads), "packet_sha256": canonical_hash(packet)})
        review = self._model("M05_REVIEW_UNIT", "review_unit", packet, REVIEW_SCHEMA, reviewer=True)
        expected = list(range(1, len(rendered["pages"]) + 1))
        observed = [item["page_number"] for item in review["page_results"]]
        if observed != expected or any(item["result"] != "PASS" for item in review["page_results"]):
            review["verdict"] = "REPAIR_REQUIRED"
        if any(item["severity"] == "blocking" for item in review["findings"]):
            review["verdict"] = "REPAIR_REQUIRED"
        visual_pass = (review["verdict"] == "PASS" and
                       len(review["page_results"]) == len(rendered["pages"]) and
                       all(item["result"] == "PASS" for item in review["page_results"]))
        rendered["checks"]["PDF-VISUAL-REVIEW"] = {
            "result": "PASS" if visual_pass else "FAIL",
            "problems": [] if visual_pass else ["independent review did not pass every rendered page"],
            "subject_sha256": sha256_file(pdf), "blocking": True,
            "evidence": {"reviewer_family": getattr(self.reviewer, "family", "unknown"),
                         "page_count": len(review["page_results"])},
        }
        rendered["failures"] = sorted(
            check_id for check_id, result in rendered["checks"].items()
            if result.get("blocking", True) and result["result"] != "PASS")
        inventory = required_checks_for(self.engine, self.curriculum)
        atomic_json(unit_root / "results/unit_checks.json", {
            "unit_id": unit["id"], "checks_version": inventory["checks_version"],
            "checks": rendered["checks"]}, root=unit_root)
        self.store.append_unique("unit_checks", review_key, {
            "path": str((unit_root / "results/unit_checks.json").relative_to(self.output)),
            "sha256": sha256_file(unit_root / "results/unit_checks.json"),
            "subject_sha256": sha256_file(pdf)})
        atomic_json(unit_root / "review/unit_review.json", review, root=unit_root)
        self.store.append_unique("unit_reviews", review_key, {
            "path": str((unit_root / "review/unit_review.json").relative_to(self.output)),
            "sha256": sha256_file(unit_root / "review/unit_review.json"),
            "verdict": review["verdict"]})
        return review

    def _repair_content(self, unit: dict[str, Any], visual: dict[str, Any],
                        findings: list[Any], unit_root: Path, attempt: int) -> dict[str, Any]:
        schema = json.loads((self.engine / "schemas/lab.schema.v4.json").read_text())
        lab = self._model(
            "M06_REPAIR_UNIT_ARTIFACT", "repair_unit_artifact",
            {"unit_id": unit["id"], "owner": "unit_content", "attempt": attempt,
             "parent_version": visual["version"], "parent_artifact": visual["lab"],
             "immutable_domain": visual["lab"]["domain"],
             "allowed_change_boundary": ["named content, pedagogy, safety, visual metadata locations"],
             "named_findings": findings,
             "required_retests": ["unit validation", "visual descendants", "render", "every page", "review"]},
            schema)
        if lab.get("domain") != visual["lab"].get("domain"):
            raise FactoryGraphFailure("REPAIR-DOMAIN-SCOPE-ESCAPE", unit["id"])
        path = unit_root / "artifacts" / "unit_content" / f"v{visual['version'] + 1}.json"
        atomic_json(path, lab, root=unit_root)
        self._artifact(unit["id"], "unit_content", visual["version"] + 1, path,
                       parent_version=visual["version"])
        return {"lab": lab, "path": path, "version": visual["version"] + 1}

    def _repair_sources(self, unit: dict[str, Any], research: dict[str, Any],
                        findings: list[Any], unit_root: Path, attempt: int) -> dict[str, Any]:
        assert self.store and self.output
        interpreted = self._model(
            "M06_REPAIR_UNIT_ARTIFACT", "repair_unit_artifact",
            {"unit_id": unit["id"], "owner": "source_interpretation", "attempt": attempt,
             "parent_version": attempt, "parent_artifact": research["research"],
             "allowed_change_boundary": ["source interpretation only; retrieval bytes immutable"],
             "named_findings": findings,
             "allowed_retrieval_results": research["retrievals"],
             "required_retests": ["source correlation", "source admission", "domain descendants"]},
            RESEARCH_INTERPRET_SCHEMA)
        known = {item["retrieval_result_id"] for item in research["retrievals"]}
        if interpreted["unresolved"] or any(
                item["retrieval_result_id"] not in known for item in interpreted["sources"]):
            raise FactoryGraphFailure("SOURCE-REPAIR-NOT-ADMISSIBLE", unit["id"])
        path = unit_root / "sources" / f"source_interpretation_v{attempt + 1}.json"
        atomic_json(path, interpreted, root=unit_root)
        self.store.append_unique("unit_repairs", f"{unit['id']}:source:{attempt}", {
            "owner": "source_interpretation", "attempt": attempt,
            "parent_sha256": canonical_hash(research["research"]),
            "child_sha256": sha256_file(path), "path": str(path.relative_to(self.output))})
        return {**research, "research": interpreted}

    def _repair_domain(self, unit: dict[str, Any], domain: dict[str, Any],
                       findings: list[Any], unit_root: Path, attempt: int) -> dict[str, Any]:
        schema = json.loads((self.engine / self.manifest["domain"]["schema"]).read_text())
        value = self._model(
            "M06_REPAIR_UNIT_ARTIFACT", "repair_unit_artifact",
            {"unit_id": unit["id"], "owner": "domain", "attempt": attempt,
             "parent_version": domain["version"], "parent_artifact": domain["domain"],
             "allowed_change_boundary": ["domain artifact only"],
             "named_findings": findings,
             "required_retests": ["domain schema", "curriculum verifier", "content descendants"]},
            schema)
        version = domain["version"] + 1
        path = unit_root / "artifacts" / "domain" / f"v{version}.json"
        atomic_json(path, value, root=unit_root)
        jsonschema.Draft202012Validator(schema).validate(value)
        verifier = self._run_verifier(path)
        self._artifact(unit["id"], "domain", version, path,
                       parent_version=domain["version"])
        return {"domain": value, "path": path, "version": version,
                "schema": schema, "verifier": verifier}

    def _repair_visual(self, unit: dict[str, Any], visual: dict[str, Any],
                       findings: list[Any], unit_root: Path, attempt: int) -> dict[str, Any]:
        schema = json.loads((self.engine / "schemas/lab.schema.v4.json").read_text())
        lab = self._model(
            "M06_REPAIR_UNIT_ARTIFACT", "repair_unit_artifact",
            {"unit_id": unit["id"], "owner": "unit_visual", "attempt": attempt,
             "parent_version": visual["version"], "parent_artifact": visual["lab"],
             "allowed_change_boundary": ["visuals", "content.unresolved_visual_roles"],
             "named_findings": findings,
             "required_retests": ["lab schema", "visual receipts", "render", "every page", "review"]},
            schema)
        immutable_parent = json.loads(json.dumps(visual["lab"]))
        immutable_child = json.loads(json.dumps(lab))
        for value in (immutable_parent, immutable_child):
            value.pop("visuals", None)
            value.get("content", {}).pop("unresolved_visual_roles", None)
        if immutable_parent != immutable_child:
            raise FactoryGraphFailure("REPAIR-VISUAL-SCOPE-ESCAPE", unit["id"])
        validate_unit(lab, self.engine / "schemas/lab.schema.v4.json",
                      self.engine / self.manifest["domain"]["schema"])
        version = visual["version"] + 1
        path = unit_root / "artifacts" / "unit_content" / f"v{version}.json"
        atomic_json(path, lab, root=unit_root)
        self._artifact(unit["id"], "unit_content", version, path,
                       parent_version=visual["version"])
        return {"lab": lab, "path": path, "version": version}

    def _repair_layout(self, unit: dict[str, Any], parent_spec: dict[str, Any],
                       findings: list[Any], attempt: int) -> dict[str, Any]:
        return self._model(
            "M06_REPAIR_UNIT_ARTIFACT", "repair_unit_artifact",
            {"unit_id": unit["id"], "owner": "unit_layout", "attempt": attempt,
             "parent_version": attempt, "parent_artifact": parent_spec,
             "allowed_change_boundary": ["unit render margin and font scale only"],
             "named_findings": findings,
             "required_retests": ["render", "page inventory", "all PDF checks", "review"]},
            UNIT_LAYOUT_SCHEMA)

    @staticmethod
    def _classify_unit_findings(check_failures: list[str], review: dict[str, Any]) -> tuple[str, list[Any]]:
        by_owner: dict[str, list[Any]] = {}
        for finding in review["findings"]:
            if finding["severity"] == "blocking":
                by_owner.setdefault(finding["artifact_owner"], []).append(finding)
        for check_id in check_failures:
            if check_id == "PDF-VISUAL-REVIEW" and by_owner:
                continue
            owner = CHECK_OWNER.get(check_id)
            if owner:
                by_owner.setdefault(owner, []).append(check_id)
        allowed = ["source_interpretation", "domain", "unit_content", "unit_visual", "unit_layout"]
        illegal = sorted(set(by_owner) - set(allowed))
        if illegal:
            raise FactoryGraphFailure("UNIT-FINDING-OWNER-ILLEGAL", str(illegal))
        for owner in allowed:
            if by_owner.get(owner):
                return owner, by_owner[owner]
        raise FactoryGraphFailure("UNIT-FAILURE-UNCLASSIFIED", str(check_failures))

    def _accept_unit(self, unit: dict[str, Any], rendered: dict[str, Any],
                     review: dict[str, Any], unit_root: Path, repair_history: list[Any]) -> dict[str, Any]:
        assert self.store and self.output
        blocking = sorted(check_id for check_id, result in rendered["checks"].items()
                          if result.get("blocking", True) and result["result"] != "PASS")
        if blocking or review["verdict"] != "PASS":
            raise FactoryGraphFailure("UNIT-ACCEPTANCE-DENIED",
                                      f"{unit['id']} blocking={blocking} review={review['verdict']}")
        if len(review["page_results"]) != len(rendered["pages"]):
            raise FactoryGraphFailure("UNIT-PAGE-DENOMINATOR", unit["id"])
        receipt = {
            "terminal_state": "ACCEPTED", "unit_id": unit["id"],
            "unit_sha256": canonical_hash(rendered["lab"]),
            "pdf": str(rendered["pdf"].relative_to(unit_root)),
            "pdf_sha256": sha256_file(rendered["pdf"]),
            "page_count": len(rendered["pages"]),
            "page_inventory_sha256": sha256_file(unit_root / "results/page_inventory.json"),
            "checks_sha256": sha256_file(unit_root / "results/unit_checks.json"),
            "review_sha256": sha256_file(unit_root / "review/unit_review.json"),
            "repair_history": repair_history, "accepted_utc": utc_now(),
        }
        receipt["receipt_sha256"] = canonical_hash(receipt)
        atomic_json(unit_root / "acceptance.json", receipt, root=unit_root)
        self.store.append_unique("accepted_units", unit["id"], receipt)
        self.store.update_unit_status(unit["id"], "ACCEPTED")
        run_state.record_unit_transition(self.output, unit["id"], "ACCEPTED")
        return receipt

    def _produce_unit(self, unit: dict[str, Any]) -> dict[str, Any]:
        assert self.output and self.store
        unit_id = unit["id"]
        unit_root = self.output / unit_id
        unit_root.mkdir(parents=True, exist_ok=True)
        for directory in ("results", "review", "artifacts"):
            (unit_root / directory).mkdir(parents=True, exist_ok=True)
        if self.store.read()["unit_status"].get(unit_id) != "ACTIVE":
            self.store.update_unit_status(unit_id, "ACTIVE")
        research = self._activate("D06_COMPILE_AND_RETRIEVE_SOURCE_REQUESTS",
                                  lambda: self._resume_research(unit, unit_root) or
                                  self._research(unit, unit_root))
        self._activate("D07_ADMIT_SOURCE_JOIN", lambda: {
            "unit_id": unit_id, "admitted": len(research["research"]["sources"])})
        domain = self._resume_artifact(unit_id, "domain")
        if domain is None:
            domain = self._create_domain(unit, research, unit_root)
        else:
            domain.update({"schema": json.loads(
                (self.engine / self.manifest["domain"]["schema"]).read_text()),
                           "verifier": self._run_verifier(domain["path"])})
        self._activate("D08_VALIDATE_DOMAIN", lambda: {
            "unit_id": unit_id, "sha256": sha256_file(domain["path"]),
            "verifier": domain["verifier"]})
        content = self._resume_artifact(unit_id, "unit_content")
        if content is None:
            content = self._write_content(unit, domain, research, unit_root)
        self._activate("D09_VALIDATE_UNIT_CONTENT", lambda: {
            "unit_id": unit_id, "sha256": sha256_file(content["path"])})
        maximum = int(self.store.read()["effective_limits"]["per_lab"]["max_revisions"]["value"])
        repeat_limit = int(self.store.read()["effective_limits"]["convergence"]
                           ["repeat_failure_threshold"]["value"])
        repair_history: list[dict[str, Any]] = []
        parent = content
        visual_override: dict[str, Any] | None = None
        layout_spec: dict[str, Any] = {"margin_inches": 0.8, "font_scale": 1.0,
                                      "finding_ids_addressed": []}
        failure_signatures: dict[str, int] = {}
        for attempt in range(maximum + 1):
            self._activate("D10_COMPILE_VISUAL_BRIEFS", lambda: {
                "unit_id": unit_id, "roles": unit["visual_roles"]})
            if visual_override is None:
                visual = self._activate("D11_RENDER_DETERMINISTIC_VISUALS",
                                        lambda: self._visuals(unit, parent, unit_root))
            else:
                visual = self._activate("D11_RENDER_DETERMINISTIC_VISUALS",
                                        lambda: visual_override)
                visual_override = None
            self._activate("D12_JOIN_AND_VERIFY_VISUALS", lambda: {
                "unit_id": unit_id, "visuals": len(visual["lab"]["visuals"])})
            rendered = self._activate("D13_RENDER_UNIT",
                                      lambda: self._render_and_check(
                                          unit, visual, unit_root, layout_spec))
            self._activate("D14_INSPECT_UNIT_PAGES", lambda: {
                "unit_id": unit_id, "pages": len(rendered["pages"]),
                "failures": rendered["failures"]})
            self._activate("D15_FREEZE_UNIT_REVIEW_PACKET", lambda: {
                "unit_id": unit_id, "pdf_sha256": sha256_file(rendered["pdf"]),
                "pages": len(rendered["pages"])})
            review = self._review_unit(unit, rendered, unit_root)
            failures = [*rendered["failures"],
                        *[finding for finding in review["findings"]
                          if finding["severity"] == "blocking"]]
            reduced = self._activate("D16_REDUCE_UNIT_EVIDENCE", lambda: {
                "unit_id": unit_id, "failures": failures,
                "review_verdict": review["verdict"]})
            if not failures and review["verdict"] == "PASS":
                unit_bytes = sum(path.stat().st_size for path in unit_root.rglob("*") if path.is_file())
                unit_limit = int(self.store.read()["effective_limits"]["per_lab"]
                                 ["max_storage_mb"]["value"]) * 1024 * 1024
                run_bytes = sum(path.stat().st_size for path in self.output.rglob("*") if path.is_file())
                run_limit = int(self.store.read()["effective_limits"]["per_run"]
                                ["max_storage_mb"]["value"]) * 1024 * 1024
                if unit_bytes > unit_limit or run_bytes > run_limit:
                    raise ConvergenceExhausted(
                        f"storage limit reached before accepting {unit_id}",
                        {"unit_id": unit_id, "unit_bytes": unit_bytes, "unit_limit": unit_limit,
                         "run_bytes": run_bytes, "run_limit": run_limit})
                log_audit = self.logger.audit()
                if (not log_audit["monotonic"] or log_audit["unclosed_starts"] or
                        log_audit["unknown_closes"] or log_audit["duplicate_closes"]):
                    raise FactoryGraphFailure("LOG-INTEGRITY", str(log_audit))
                receipt = self._activate("D22_ACCEPT_UNIT", lambda: self._accept_unit(
                    unit, rendered, review, unit_root, repair_history))
                self._activate("D23_CHECKPOINT_ACCEPTED_UNIT", lambda: receipt)
                return receipt
            if attempt >= maximum:
                raise ConvergenceExhausted(
                    f"unit repair bound exhausted for {unit_id}",
                    {"unit_id": unit_id, "attempts": attempt, "failures": failures})
            owner, named_findings = self._classify_unit_findings(
                rendered["failures"], review)
            signature = canonical_hash({"owner": owner, "findings": named_findings})
            failure_signatures[signature] = failure_signatures.get(signature, 0) + 1
            if failure_signatures[signature] >= repeat_limit:
                raise ConvergenceExhausted(
                    f"repeated failed-check set for {unit_id}",
                    {"unit_id": unit_id, "owner": owner, "signature": signature,
                     "repeats": failure_signatures[signature], "limit": repeat_limit})
            classification = self._activate("D17_CLASSIFY_UNIT_FINDINGS", lambda: {
                "unit_id": unit_id, "owner": owner, "findings": named_findings})
            invalidates = {
                "source_interpretation": ["domain", "unit content", "unit visuals", "unit render",
                                          "all page checks", "unit review"],
                "domain": ["unit content", "unit visuals", "unit render", "all page checks", "unit review"],
                "unit_content": ["unit visuals", "unit render", "all page checks", "unit review"],
                "unit_visual": ["unit render", "all page checks", "unit review"],
                "unit_layout": ["unit render", "all page checks", "unit review"],
            }[owner]
            plan = self._activate("D18_PLAN_UNIT_REPAIR", lambda: {
                **classification, "attempt": attempt + 1, "maximum": maximum,
                "immutable_parent_version": (domain["version"] if owner == "domain" else
                                             visual["version"]),
                "invalidates": invalidates})
            repair_key = f"{unit_id}:unit:{attempt + 1}"
            self.store.append_unique("unit_repair_requests", repair_key, plan)
            self.store.append_unique("invalidations", repair_key, {
                "owner": owner, "parent_version": plan["immutable_parent_version"],
                "descendants": invalidates, "required_retest_order": invalidates})
            self._activate("D19_ROUTE_UNIT_REPAIR", lambda: plan)
            if owner == "source_interpretation":
                research = self._repair_sources(unit, research, named_findings, unit_root, attempt + 1)
                domain = self._create_domain(unit, research, unit_root)
                repaired = self._write_content(unit, domain, research, unit_root)
                parent = repaired
            elif owner == "domain":
                domain = self._repair_domain(unit, domain, named_findings, unit_root, attempt + 1)
                repaired = self._write_content(unit, domain, research, unit_root)
                parent = repaired
            elif owner == "unit_content":
                repaired = self._repair_content(
                    unit, visual, named_findings, unit_root, attempt + 1)
                parent = repaired
            elif owner == "unit_visual":
                repaired = self._repair_visual(
                    unit, visual, named_findings, unit_root, attempt + 1)
                parent = repaired
                visual_override = repaired
            else:
                layout_spec = self._repair_layout(
                    unit, layout_spec, named_findings, attempt + 1)
                repaired = {"version": visual["version"], "path": visual["path"],
                            "layout_spec_sha256": canonical_hash(layout_spec)}
                visual_override = visual
            admission = {"unit_id": unit_id, "owner": owner,
                         "parent_version": plan["immutable_parent_version"],
                         "child_version": repaired["version"],
                         "sha256": (sha256_file(repaired["path"])
                                    if repaired.get("path") else repaired["layout_spec_sha256"])}
            self._activate("D20_ADMIT_UNIT_REPAIR", lambda: admission)
            self.store.append_unique("unit_repairs", repair_key, admission)
            self._activate("D21_RETEST_UNIT_DESCENDANTS", lambda: {
                "unit_id": unit_id, "order": plan["invalidates"]})
            repair_history.append({"attempt": attempt + 1, "owner": owner,
                                   "findings": named_findings,
                                   "parent_version": admission["parent_version"],
                                   "child_version": admission["child_version"],
                                   "invalidates": invalidates})
        raise AssertionError("bounded unit loop did not terminate")

    # -- workbook nodes -------------------------------------------------------------

    def _assemble_workbook(self, accepted: dict[str, Any], spec: dict[str, Any],
                           version: int) -> dict[str, Any]:
        assert self.output and self.manifest and self.store
        expected = [unit["id"] for unit in self.manifest["labs"]]
        if list(accepted) != expected:
            raise FactoryGraphFailure("WORKBOOK-COVERAGE-INEXACT",
                                      f"accepted {list(accepted)} != manifest {expected}")
        workbook = self.output / "workbook"
        workbook.mkdir(exist_ok=True)
        pdfs = [self.output / unit_id / accepted[unit_id]["pdf"] for unit_id in expected]
        if any(not pdf.is_file() or sha256_file(pdf) != accepted[unit_id]["pdf_sha256"]
               for unit_id, pdf in zip(expected, pdfs)):
            raise FactoryGraphFailure("WORKBOOK-UNIT-HASH-MISMATCH", "accepted unit PDF moved")
        inputs = list(pdfs)
        front = spec.get("front_matter_markdown", "").strip()
        if front:
            md = workbook / f"front_matter_v{version}.md"
            front_pdf = workbook / f"front_matter_v{version}.pdf"
            md.write_text(front, encoding="utf-8")
            proc = subprocess.run(["pandoc", str(md), "--pdf-engine=typst", "-V",
                                   "mainfont=Helvetica", "-o", str(front_pdf)],
                                  capture_output=True, text=True)
            if proc.returncode != 0:
                raise FactoryGraphFailure("WORKBOOK-FRONT-MATTER-RENDER", proc.stderr)
            inputs.insert(0, front_pdf)
        target = workbook / f"workbook_v{version}.pdf"
        proc = subprocess.run(["pdfunite", *[str(path) for path in inputs], str(target)],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise FactoryGraphFailure("WORKBOOK-ASSEMBLY-FAILED", proc.stderr)
        assembly = {"version": version, "expected_unit_ids": expected,
                    "included_unit_ids": expected,
                    "accepted_unit_hashes": {key: value["receipt_sha256"]
                                             for key, value in accepted.items()},
                    "source_pdfs": [{"path": str(path.relative_to(self.output)),
                                     "sha256": sha256_file(path)} for path in pdfs],
                    "workbook": str(target.relative_to(self.output)),
                    "workbook_sha256": sha256_file(target), "spec": spec}
        atomic_json(workbook / f"assembly_v{version}.json", assembly, root=self.output)
        self.store.append_unique("workbook_artifacts", f"workbook:v{version}", assembly)
        current = self.store.read()["workbook_heads"].get("workbook")
        self.store.replace_current("workbook_heads", "workbook", version,
                                   previous_version=current)
        return {"pdf": target, "assembly": assembly, "version": version}

    def _inspect_workbook(self, record: dict[str, Any]) -> dict[str, Any]:
        assert self.output and self.store
        pages = rasterize_and_check_nonblank(
            record["pdf"], self.output / "workbook" / f"page_renders_v{record['version']}", dpi=200)
        legible = pdf_inspect.text_legible(record["pdf"])
        checks = {
            "WORKBOOK-COVERAGE-EXACT": {"result": "PASS"},
            "WORKBOOK-PAGE-COUNT": {"result": "PASS" if pdf_page_count(record["pdf"]) == len(pages) else "FAIL"},
            "WORKBOOK-PAGE-NONBLANK": {"result": "PASS"},
            "WORKBOOK-TEXT-LEGIBLE": {"result": "PASS" if not legible["problems"] else "FAIL",
                                       "problems": legible["problems"]},
        }
        inventory = [{"page_number": index, "path": str(path.relative_to(self.output)),
                      "sha256": sha256_file(path)} for index, path in enumerate(pages, 1)]
        result = {**record, "pages": pages, "page_inventory": inventory, "checks": checks}
        atomic_json(self.output / "workbook" / f"checks_v{record['version']}.json",
                    {"checks": checks, "pages": inventory}, root=self.output)
        self.store.append_unique("workbook_checks", f"v{record['version']}", {
            "path": f"workbook/checks_v{record['version']}.json",
            "sha256": sha256_file(self.output / "workbook" / f"checks_v{record['version']}.json"),
            "workbook_sha256": sha256_file(record["pdf"])})
        self.store.append_unique("workbook_page_inventory", f"v{record['version']}", {
            "workbook_sha256": sha256_file(record["pdf"]), "pages": inventory})
        return result

    def _review_workbook(self, inspected: dict[str, Any]) -> dict[str, Any]:
        assert self.output and self.store
        packet = {
            "workbook_sha256": sha256_file(inspected["pdf"]),
            "assembly_manifest": inspected["assembly"],
            "pages": [{"page_number": index, "sha256": sha256_file(path),
                       "png_base64": b64encode(path.read_bytes()).decode("ascii")}
                      for index, path in enumerate(inspected["pages"], 1)],
            "deterministic_results": inspected["checks"],
            "rubric": ["exact coverage", "front matter and navigation", "pagination",
                       "cross-unit continuity", "visual and typographic consistency",
                       "accessibility and legibility", "no blank duplicate or stale pages"],
        }
        key = f"v{inspected['version']}"
        self.store.append_unique("workbook_review_packets", key, {
            "packet_sha256": canonical_hash(packet), "page_count": len(inspected["pages"])})
        review = self._model("M07_REVIEW_WORKBOOK", "review_workbook", packet,
                             REVIEW_SCHEMA, reviewer=True)
        expected = list(range(1, len(inspected["pages"]) + 1))
        if [item["page_number"] for item in review["page_results"]] != expected:
            review["verdict"] = "REPAIR_REQUIRED"
        if any(item["result"] != "PASS" for item in review["page_results"]):
            review["verdict"] = "REPAIR_REQUIRED"
        if any(item["severity"] == "blocking" for item in review["findings"]):
            review["verdict"] = "REPAIR_REQUIRED"
        path = self.output / "workbook" / f"review_v{inspected['version']}.json"
        atomic_json(path, review, root=self.output)
        self.store.append_unique("workbook_reviews", key, {
            "path": str(path.relative_to(self.output)), "sha256": sha256_file(path),
            "verdict": review["verdict"]})
        return review

    def _workbook(self) -> dict[str, Any]:
        assert self.store and self.manifest and self.output
        accepted = self.store.read()["accepted_units"]
        expected = [unit["id"] for unit in self.manifest["labs"]]
        accepted_ordered = {unit_id: accepted[unit_id] for unit_id in expected if unit_id in accepted}
        if list(accepted_ordered) != expected:
            raise FactoryGraphFailure("WORKBOOK-COVERAGE-INEXACT", "not every manifest unit is accepted")
        current = self.store.read()["workbook_heads"].get("workbook")
        spec = {"front_matter_markdown": ""}
        if current is not None:
            prior = self.store.read()["workbook_artifacts"].get(f"workbook:v{current}")
            if not prior:
                raise FactoryGraphFailure("RESUME-WORKBOOK-HEAD-MISSING", f"v{current}")
            spec = prior.get("spec", spec)
        maximum = int(self.store.read()["effective_limits"]["convergence"]
                      ["max_meta_revision_cycles"]["value"])
        repeat_limit = int(self.store.read()["effective_limits"]["convergence"]
                           ["repeat_failure_threshold"]["value"])
        failure_signatures: dict[str, int] = {}
        start_version = int(current or 0) + 1
        for version in range(start_version, maximum + 2):
            attempt = version - 1
            assembled = self._activate("D25_ASSEMBLE_WORKBOOK", lambda: self._assemble_workbook(
                accepted_ordered, spec, version))
            inspected = self._activate("D26_RENDER_AND_INSPECT_WORKBOOK_PAGES",
                                       lambda: self._inspect_workbook(assembled))
            self._activate("D27_FREEZE_WORKBOOK_REVIEW_PACKET", lambda: {
                "version": version, "pages": len(inspected["pages"]),
                "workbook_sha256": sha256_file(inspected["pdf"])})
            review = self._review_workbook(inspected)
            failures = [name for name, result in inspected["checks"].items()
                        if result["result"] != "PASS"] + [
                            item for item in review["findings"] if item["severity"] == "blocking"]
            reduced = self._activate("D28_REDUCE_WORKBOOK_EVIDENCE", lambda: {
                "version": version, "failures": failures, "review": review["verdict"]})
            if not failures and review["verdict"] == "PASS":
                return {**inspected, "review": review}
            if attempt >= maximum:
                raise ConvergenceExhausted("workbook repair bound exhausted", {
                    "attempts": attempt, "failures": failures})
            signature = canonical_hash(failures)
            failure_signatures[signature] = failure_signatures.get(signature, 0) + 1
            if failure_signatures[signature] >= repeat_limit:
                raise ConvergenceExhausted("workbook repeated failed-check set", {
                    "signature": signature, "repeats": failure_signatures[signature],
                    "limit": repeat_limit})
            plan = self._activate("D29_ROUTE_WORKBOOK_REPAIR", lambda: {
                "owner": "workbook", "attempt": attempt + 1,
                "accepted_unit_hashes": {key: value["receipt_sha256"]
                                         for key, value in accepted_ordered.items()},
                "findings": failures})
            repair_key = f"workbook:{attempt + 1}"
            self.store.append_unique("workbook_repair_requests", repair_key, plan)
            self.store.append_unique("invalidations", repair_key, {
                "owner": "workbook", "parent_version": version,
                "descendants": ["workbook assembly", "workbook render", "all workbook pages",
                                "workbook review", "final release audit"],
                "required_retest_order": ["assemble", "render", "inspect all pages",
                                          "review", "release audit"]})
            repaired = self._model(
                "M08_REPAIR_WORKBOOK", "repair_workbook",
                {"parent_spec": spec, **plan, "allowed_change_boundary": ["front matter only"]},
                WORKBOOK_REPAIR_SCHEMA)
            before = {key: value["receipt_sha256"] for key, value in accepted_ordered.items()}
            after = {key: value["receipt_sha256"] for key, value in self.store.read()["accepted_units"].items()}
            if before != after:
                raise FactoryGraphFailure("WORKBOOK-REPAIR-UNIT-MUTATION", "accepted unit hashes changed")
            spec = repaired
            self._activate("D31_ADMIT_WORKBOOK_REPAIR", lambda: {
                "attempt": attempt + 1, "spec_sha256": canonical_hash(spec),
                "accepted_unit_hashes": before})
            self.store.append_unique("workbook_repairs", repair_key, {
                "attempt": attempt + 1, "parent_version": version,
                "child_spec_sha256": canonical_hash(spec), "accepted_unit_hashes": before})
        raise AssertionError("bounded workbook loop did not terminate")

    def _release_audit(self, workbook: dict[str, Any], log: dict[str, Any]) -> dict[str, Any]:
        assert self.store and self.manifest and self.output
        state = self.store.read()
        expected = [unit["id"] for unit in self.manifest["labs"]]
        accepted = state["accepted_units"]
        problems = []
        if list(accepted) != expected:
            problems.append("accepted-unit coverage differs from manifest")
        for unit_id in expected:
            receipt = accepted.get(unit_id)
            if not receipt:
                continue
            unit_root = self.output / unit_id
            pdf = unit_root / receipt["pdf"]
            if not pdf.is_file() or sha256_file(pdf) != receipt["pdf_sha256"]:
                problems.append(f"{unit_id} accepted PDF hash mismatch")
            checks = json.loads((unit_root / "results/unit_checks.json").read_text())["checks"]
            if any(result.get("blocking", True) and result["result"] != "PASS"
                   for result in checks.values()):
                problems.append(f"{unit_id} has a nonpassing blocking check")
            review = json.loads((unit_root / "review/unit_review.json").read_text())
            if review["verdict"] != "PASS":
                problems.append(f"{unit_id} review is not PASS")
        if workbook["review"]["verdict"] != "PASS":
            problems.append("workbook review is not PASS")
        if any(result["result"] != "PASS" for result in workbook["checks"].values()):
            problems.append("workbook deterministic check failed")
        if sha256_file(workbook["pdf"]) != workbook["assembly"]["workbook_sha256"]:
            problems.append("workbook hash mismatch")
        events = self.store.events()
        if [event["ordinal"] for event in events] != list(range(1, len(events) + 1)):
            problems.append("event ordinals not contiguous")
        if (not log["monotonic"] or log["unclosed_starts"] or log["unknown_closes"] or
                log["duplicate_closes"]):
            problems.append(f"execution log integrity failed: {log}")
        if problems:
            raise FactoryGraphFailure("FINAL-RELEASE-AUDIT", "; ".join(problems))
        audit = {"status": "PASS", "run_id": state["identity"]["run_id"],
                 "manifest_unit_ids": expected,
                 "accepted_unit_hashes": {key: value["receipt_sha256"] for key, value in accepted.items()},
                 "workbook_sha256": sha256_file(workbook["pdf"]),
                 "workbook_pages": len(workbook["pages"]),
                 "event_count": len(events), "audited_utc": utc_now()}
        atomic_json(self.output / "workbook/final_release_audit.json", audit, root=self.output)
        return audit

    # -- public execution -----------------------------------------------------------

    def run(self, *, curriculum: Path | str, output_root: Path | str,
            lab_id: str | None = None, all_units: bool = False, resume: bool = False,
            limit_overrides: dict[str, int] | None = None) -> dict[str, Any]:
        output = require_internal_output(Path(output_root), self.engine)
        self.output = output
        self.curriculum, self.manifest_path = self._resolve_curriculum_input(curriculum)
        _, self.manifest = self.runtime.validated_manifest(self.curriculum)
        package_hashes = self._require_package()
        limits = self._limits(limit_overrides)
        mode = "ALL_UNITS" if all_units else "ONE_UNIT"
        if not resume and not all_units and not lab_id:
            raise RuntimeFailure("PRECONDITION-RUN-MODE", "production requires --lab-id or --all")
        frozen = self._active_inputs(self.curriculum, self.manifest_path)
        identity = self._run_identity(frozen, output, mode, lab_id, limits)

        try:
            if resume:
                if not output.is_dir():
                    raise FactoryGraphFailure("RESUME-ROOT-MISSING", str(output))
                self.store = FactoryStateStore(output)
                stored = self.store.read()
                # Resume uses the original mode/target; callers may repeat them but cannot change them.
                original = stored["identity"]
                mode, lab_id = original["mode"], original.get("requested_unit")
                identity = self._run_identity(frozen, output, mode, lab_id, stored["effective_limits"])
                self.store.validate_identity(identity["run_id"])
                self.store.events()
                Checkpoints(output).valid_prefix()
                self.store.resume_interrupted()
            else:
                if output.exists():
                    raise FactoryGraphFailure("PRECONDITION-OUTPUT-ROOT-EXISTS", str(output))
                output.mkdir(parents=True)
                (output / "results").mkdir()
                self.store = FactoryStateStore(output)
                self.store.initialize(identity, frozen, limits)
            self.logger = ExecutionLogger(output, self.engine / "schemas/execution_log.schema.v2.json")

            if not resume:
                gate = self.runtime._logger_gate(self.logger, output)
                atomic_json(output / "results/gate_0_logger.json", gate, root=output)
                self._activate("D01_VALIDATE_AND_FREEZE_RUN", lambda: {
                    "identity": identity, "package_hashes": package_hashes}, checkpoint=True)
                preflight = self.runtime.static_preflight(self.curriculum)
                units = self.manifest["labs"]
                ids = [unit["id"] for unit in units]
                if lab_id and lab_id not in ids:
                    raise FactoryGraphFailure("PRECONDITION-UNKNOWN-UNIT", lab_id)
                if mode == "ALL_UNITS":
                    selected_ids = ids
                else:
                    required: set[str] = set()

                    def add_prerequisites(unit_id: str) -> None:
                        if unit_id in required:
                            return
                        record = next(item for item in units if item["id"] == unit_id)
                        for prerequisite in record["sequence"]["prerequisites"]:
                            add_prerequisites(prerequisite)
                        required.add(unit_id)

                    add_prerequisites(lab_id)
                    selected_ids = [unit_id for unit_id in ids if unit_id in required]
                effective = {"mode": mode, "requested_unit": lab_id,
                             "ordered_manifest_unit_ids": ids,
                             "selected_unit_ids": selected_ids,
                             "manifest_sha256": sha256_file(self.manifest_path),
                             "graph_sha256": sha256_file(self.graph_path)}
                self.store.write_once("effective_run", effective)
                atomic_json(output / "results/gate_1_static_preflight.json", preflight, root=output)
                atomic_json(output / "results/effective_run.json", effective, root=output)
                atomic_json(output / "meta_execution_state.json", {
                    "authorized_roots": {"engine": str(self.engine),
                                         "curriculum": str(self.curriculum),
                                         "output_root": str(output)},
                    "manifest_sha256": sha256_file(self.manifest_path),
                    "prompt_sha256": sha256_file(self.graph_path), "run_id": identity["run_id"]},
                    root=output)
                self._activate("D02_COMPILE_MANIFEST_RUN", lambda: effective)
                capability = self._activate("D03_PROVE_REQUIRED_CAPABILITIES", lambda: self.capabilities.prove(
                    output, full_run=mode == "ALL_UNITS"))
                self.store.append_unique("capability_receipts", "D03", capability)
                self._activate("D04_RESUME_OR_INITIALIZE", lambda: {"resume": False, "cursor": 0})
                self.store.set_status("ACTIVE")
            else:
                self._activate("D04_RESUME_OR_INITIALIZE", lambda: {"resume": True,
                    "cursor": self.store.read()["cursor"]})

            effective = self.store.read()["effective_run"]
            unit_by_id = {unit["id"]: unit for unit in self.manifest["labs"]}
            accepted = self.store.read()["accepted_units"]
            for unit_id in effective["selected_unit_ids"]:
                if unit_id in accepted:
                    continue
                unit = unit_by_id[unit_id]
                missing_prereqs = [value for value in unit["sequence"]["prerequisites"]
                                   if value not in self.store.read()["accepted_units"]]
                if missing_prereqs:
                    raise FactoryGraphFailure(
                        "MANIFEST-PREREQUISITE-ORDER-VIOLATION",
                        f"{unit_id} selected before prerequisites {missing_prereqs}",
                        evidence={"unit_id": unit_id, "missing_prerequisites": missing_prereqs})
                selection = self._activate("D05_SELECT_NEXT_UNIT", lambda: {
                    "unit_id": unit_id, "manifest_ordinal": effective["ordered_manifest_unit_ids"].index(unit_id)})
                ordinal = selection["manifest_ordinal"]
                if str(ordinal) not in self.store.read()["unit_selections"]:
                    self.store.append_unique("unit_selections", str(ordinal), selection)
                self._produce_unit(unit)
                self.store.set_cursor(self.store.read()["cursor"] + 1)
                coverage = self._activate("D24_COMPUTE_MANIFEST_COVERAGE", lambda: {
                    "accepted": list(self.store.read()["accepted_units"]),
                    "expected": effective["selected_unit_ids"]})

            if mode == "ONE_UNIT":
                unit_id = effective["requested_unit"]
                receipt = self.store.read()["accepted_units"].get(unit_id)
                if not receipt:
                    raise FactoryGraphFailure("UNIT-PRODUCT-MISSING", unit_id)
                terminal = self._write_terminal("UNIT_ACCEPTED", {
                    "unit_id": unit_id, "receipt_sha256": receipt["receipt_sha256"]})
                return {**terminal, "output_root": str(output), "unit": receipt}

            self.store.set_status("ASSEMBLING")
            workbook = self._workbook()
            pre_release_log = self.logger.audit()
            audit = self._activate("D32_FINAL_RELEASE_AUDIT",
                                   lambda: self._release_audit(workbook, pre_release_log),
                                   checkpoint=False)
            # D32 has now closed; terminal decision is separately logged and then audited.
            terminal = self._write_terminal("COMPLETE", {
                "audit_sha256": sha256_file(output / "workbook/final_release_audit.json"),
                "workbook_sha256": audit["workbook_sha256"]})
            lifecycle = run_state._recompute(output, run_state.read(output))
            lifecycle.update({"run_status": "COMPLETE", "workbook_assembled": True,
                              "workbook_coverage": {"expected": len(self.manifest["labs"]),
                                                    "included": len(self.manifest["labs"])},
                              "closed_at": utc_now()})
            lifecycle.pop("terminal_reason", None)
            run_state._write(output, lifecycle)
            return {**terminal, "output_root": str(output),
                    "workbook": str(workbook["pdf"]), "audit": audit}
        except KeyboardInterrupt:
            return self._write_terminal("INTERRUPTED", {"reason": "external interrupt",
                                                         "resume": True})
        except PrerequisitePause as error:
            classified = self._activate("D30_CLASSIFY_PREREQUISITE", lambda: {
                "failure_id": error.failure_id, "classification": "external_curriculum_fact",
                "system_causes_excluded": True, "evidence": error.evidence})
            return self._write_terminal("PAUSED_PREREQUISITE", {
                "failure_id": error.failure_id, "message": str(error),
                "classification": classified, "evidence": error.evidence})
        except FactoryGraphFailure as error:
            return self._write_terminal(error.terminal, {
                "failure_id": error.failure_id, "message": str(error), "evidence": error.evidence})
        except Exception as error:
            return self._write_terminal("SYSTEM_FAILURE", {
                "failure_id": type(error).__name__, "message": str(error)})

    def _write_terminal(self, terminal: str, guard: dict[str, Any]) -> dict[str, Any]:
        assert self.store and self.logger and self.output
        start = self.logger.start(
            action=f"Write truthful factory terminal {terminal}", action_kind="terminal_decision",
            authorized_paths=[str(self.output)], trigger="terminal guard",
            expected=f"one controller-owned {terminal} record")
        record = self.store.write_terminal(terminal, guard)
        self.logger.complete(start, result=f"terminal {terminal} committed")
        audit = self.logger.audit()
        atomic_json(self.output / "final_log_audit.json", audit, root=self.output)
        return {**record, "log_audit": audit}
