#!/usr/bin/env python3
"""Bridge an in-session model worker to the deterministic runtime.

The controller prepares a bounded request and opens a logged model operation. The
calling model writes only the two authorized JSON outputs, then the controller resumes,
validates, renders, audits, and closes the operation. No external model API is assumed.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any
from urllib.request import Request, urlopen

import jsonschema
import yaml

from .checks import check_receipts, pdf_page_count, rasterize_and_check_nonblank
from .checkpoint import Checkpoints
from .controller import CurriculumRuntime, RuntimeFailure
from .io import atomic_json, require_internal_output, sha256_file
from .logger import ExecutionLogger


MODEL_ID = "gpt-5.6-sol"


def _copy(source: Path, destination: Path) -> dict[str, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return {"source": str(source), "copied": str(destination), "sha256": sha256_file(destination)}


def _find_seed(curriculum: Path, lab_id: str) -> Path:
    candidates = sorted(path for path in curriculum.glob(f"{lab_id.lower()}*.json")
                        if "schema" not in path.name and "fixture" not in path.parts)
    if len(candidates) != 1:
        raise RuntimeFailure("PRECONDITION-DOMAIN-SEED", f"expected one unit seed, found {candidates}")
    return candidates[0]


def _svg(path: Path, title: str, rows: list[str], *, root: Path) -> None:
    escaped = [html.escape(str(row)) for row in rows]
    height = 150 + 70 * len(escaped)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{height}" viewBox="0 0 1400 {height}">',
             '<rect width="1400" height="100%" fill="white"/>',
             f'<text x="70" y="70" font-family="Helvetica" font-size="40" font-weight="bold">{html.escape(title)}</text>']
    for index, row in enumerate(escaped):
        y = 140 + index * 70
        parts.append(f'<circle cx="100" cy="{y}" r="16" fill="white" stroke="#17365D" stroke-width="5"/>')
        parts.append(f'<text x="145" y="{y + 12}" font-family="Helvetica" font-size="30">{row}</text>')
        if index + 1 < len(escaped):
            parts.append(f'<line x1="100" y1="{y + 20}" x2="100" y2="{y + 50}" stroke="#C9472F" stroke-width="5" stroke-dasharray="12 12"/>')
            parts.append(f'<text x="125" y="{y + 48}" font-family="Helvetica" font-size="19" fill="#C9472F">NOT CONNECTED</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def prepare(engine: Path, curriculum_value: Path, lab_id: str, output: Path) -> dict[str, Any]:
    runtime = CurriculumRuntime(engine)
    curriculum = runtime.resolve_curriculum(curriculum_value)
    runtime.resolve_companions()
    manifest_path, manifest = runtime.validated_manifest(curriculum)
    runtime.run_verifier_fixtures(manifest)
    unit = next((item for item in manifest["labs"] if item["id"] == lab_id), None)
    if unit is None:
        raise RuntimeFailure("PRECONDITION-UNKNOWN-UNIT", lab_id)
    output = require_internal_output(output, engine)
    if output.exists():
        raise RuntimeFailure("PRECONDITION-OUTPUT-ROOT-EXISTS", str(output))
    output.mkdir(parents=True)
    (output / "results").mkdir()
    logger = ExecutionLogger(output, engine / "schemas/execution_log.schema.v2.json")
    logger_gate = runtime._logger_gate(logger, output)
    atomic_json(output / "results/gate_0_logger.json", logger_gate, root=output)

    freeze_start = logger.start(action="Freeze copied and hashed acceptance inputs", action_kind="initialization",
                                authorized_paths=[str(output)], trigger="session bridge prepare",
                                expected="immutable run-local input bundle")
    inputs = output / "inputs"
    seed = _find_seed(curriculum, lab_id)
    copies = []
    for source, relative in [
        (runtime.prompt, "prompt.md"), (manifest_path, "manifest.yaml"),
        (engine / manifest["domain"]["schema"], "domain.schema.json"),
        (engine / manifest["domain"]["schema"], Path(manifest["domain"]["schema"]).name),
        (engine / "schemas/lab.schema.v4.json", "lab.schema.json"),
        (engine / "policy/calibration.v1.yaml", "calibration.yaml"),
        (seed, "domain_seed.json"),
        (engine / manifest["domain"]["verifier"]["entry_point"], "verify_domain.py"),
    ]:
        copies.append(_copy(source, inputs / relative))
    # A copied verifier is an executable input and must retain its local data
    # dependencies. Keep their original basenames so its run-local imports resolve.
    for dependency_name in ("kit_calibration.v1.yaml", "circuit_library.v1.yaml"):
        dependency = curriculum / dependency_name
        if dependency.is_file():
            copies.append(_copy(dependency, inputs / dependency_name))
    for name in ("unit_prose.v1.md", "pedagogy.v1.md"):
        copies.append(_copy(engine / "meta_prompt/assets" / name, inputs / name))
    photo_candidates = sorted(curriculum.glob("*.jpg"))
    if photo_candidates:
        copies.append(_copy(photo_candidates[0], output / "assets/official_reference.jpg"))
    atomic_json(output / "input_freeze.json", {"files": copies, "unit": unit,
                "runtime_hashes": [{"path": str(path), "sha256": sha256_file(path)}
                                   for path in sorted((engine / "runtime").glob("*.py"))]}, root=output)
    logger.complete(freeze_start, result=f"froze {len(copies)} copied inputs")

    seed_data = json.loads((inputs / "domain_seed.json").read_text())
    sources = output / "sources"
    sources.mkdir()
    source_receipts = []
    for index, source in enumerate(seed_data.get("primary_sources", []), 1):
        url = source.get("url_or_path")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            continue
        action = logger.start(action="Fetch declared primary-source bytes for selected unit",
                              action_kind="source_request", authorized_paths=[str(output)],
                              trigger=url, expected="cached primary-source bytes and resolving hash")
        target = sources / f"source_{index:02d}.html"
        try:
            request = Request(url, headers={"User-Agent": "curriculum-runtime/1.0"})
            with urlopen(request, timeout=45) as response:
                payload = response.read()
            target.write_bytes(payload)
            receipt = {"url": url, "access_date": date.today().isoformat(),
                       "claim_scope": source.get("claim_scope"), "path": str(target.relative_to(output)),
                       "sha256": sha256_file(target), "bytes": len(payload)}
            source_receipts.append(receipt)
            logger.complete(action, result=f"cached {len(payload)} bytes as {target.name}")
        except Exception as error:
            logger.fail(action, failure_type="tool-error", what_failed=f"primary-source fetch failed: {error}",
                        expected="retrievable official primary source")
            raise RuntimeFailure("SOURCE-FETCH-FAILED", str(error)) from error
    atomic_json(output / "sources/source_manifest.json", {"sources": source_receipts}, root=output)

    assets = output / "assets"
    assets.mkdir(exist_ok=True)
    path_rows = [item.get("name", item.get("coordinate", "point")) for item in seed_data.get("terminals", [])]
    if not path_rows:
        path_rows = [str(item) for item in seed_data.get("legal_coordinates", [])]
    _svg(assets / "path_map.svg", f"{lab_id} disconnected teaching path", path_rows, root=output)
    _svg(assets / "evidence_card.svg", f"{lab_id} evidence card", ["Trace each dashed teaching link", "Tick each place you can identify", "Keep every connection open"], root=output)
    asset_records = []
    for asset in sorted(assets.iterdir()):
        if asset.is_file():
            asset_records.append({"embedded_as": str(asset.relative_to(output)), "sha256": sha256_file(asset)})
    atomic_json(output / "assets/manifest.json", {"assets": asset_records}, root=output)

    decision = {
        "task_id": f"{lab_id}-in-session-authoring", "task_class": "final_acceptance",
        "risk": "safety_critical", "candidate_pool": [MODEL_ID],
        "decided_model": MODEL_ID, "executed_model": MODEL_ID, "reasoning_effort": "max",
        "pro_mode": True, "quality_gate": ["schema_validation", "domain_verifier", "receipt_hashes"],
        "decision_rationale": "user authorized the current in-session LLM as the model worker; no separate API",
        "evidence_inputs": ["inputs", "sources/source_manifest.json", "assets/manifest.json"],
        "escalate_when": [], "substitution": "USER_AUTHORIZED_IN_SESSION_MODEL_DIVERGENCE",
        "status": "approved_to_run",
    }
    jsonschema.Draft202012Validator(json.loads((engine / "schemas/routing_decision.schema.v2.json").read_text())).validate(decision)
    (output / "routing").mkdir()
    atomic_json(output / "routing/authoring.json", decision, root=output)
    model_start = logger.start(action="Generate bounded unit domain and document with in-session model",
                               action_kind="model_call", decision_id=decision["task_id"],
                               authorized_paths=[str(output / "workers/domain.json"), str(output / "workers/lab.json")],
                               trigger="user-authorized in-session model bridge",
                               expected="schema-valid domain.json and lab.json")
    (output / "workers").mkdir()
    request = {
        "role": "bounded unit author",
        "stable_check_ids": ["LAB-SCHEMA-VALID", "LAB-BLOOM-DEPTH", "LAB-POE-ORDER",
                             "TEXT-READABILITY-BAND", "DOC-DERIVED-FROM-SOURCE", "RECEIPT-HASH-RESOLVES"],
        "authorized_inputs": ["inputs", "sources/source_manifest.json", "assets/manifest.json"],
        "authorized_outputs": ["workers/domain.json", "workers/lab.json"],
        "output_schemas": ["inputs/domain.schema.json", "inputs/lab.schema.json"],
        "unit": unit, "model_start_id": model_start,
        "constraints": ["fully disconnected and unpowered", "no connector polarity", "no live measurement",
                        "derive prose from domain.json", "use only shipped assets and exact recorded hashes",
                        "output is a draft pending downstream human review"],
    }
    atomic_json(output / "worker_request.json", request, root=output)
    checkpoint = Checkpoints(output).write(ordinal=1, state="VALIDATE", next_state="PLAN",
                                           inputs=[output / "input_freeze.json"],
                                           outputs=[output / "worker_request.json"], attempt=0,
                                           started_at=time.monotonic(), worker_identity="controller")
    atomic_json(output / "interrupt_receipt.json", {"forced_interrupt": True,
                "checkpoint": str(checkpoint), "checkpoint_sha256": sha256_file(checkpoint),
                "preserved_hashes": {"input_freeze": sha256_file(output / "input_freeze.json"),
                                     "worker_request": sha256_file(output / "worker_request.json")}}, root=output)
    return {"terminal_state": "INTERRUPTED", "next_action": "in-session model writes authorized outputs",
            "output_root": str(output), "model_start_id": model_start}


def _markdown(lab: dict[str, Any]) -> str:
    identity, pedagogy, sequence = lab["identity"], lab["pedagogy"], lab["sequence"]
    lines = [f"# {identity['unit_id']} — {identity['title']}", "", "*Draft pending downstream human review.*", "",
             identity["subject_job_sentence"], "", "## What I will learn", ""]
    for objective in pedagogy["learning_objectives"]:
        lines.append(f"- {objective['success_criterion']}")
    labels = [("Engage", sequence["engage"]), ("Explore", sequence["explore"]),
              ("Explain", sequence["explain"]), ("Elaborate", sequence["elaborate"]),
              ("Evaluate", sequence["evaluate"])]
    for title, value in labels:
        lines.extend(["", f"## {title}", "", json.dumps(value, ensure_ascii=False, indent=2)])
    lines.extend(["", "## Identification", "", json.dumps(lab["content"]["identification"], ensure_ascii=False, indent=2),
                  "", "## Troubleshooting", "", json.dumps(lab["content"]["troubleshooting"], ensure_ascii=False, indent=2),
                  "", "## Adult safety verification", "", json.dumps(lab["safety"], ensure_ascii=False, indent=2),
                  "", "## Visuals", ""])
    for visual in lab["visuals"]:
        embedded_name = Path(visual["provenance"]["embedded_as"]).name
        lines.extend([f"### {visual['role'].replace('_', ' ').title()}", "",
                      f"![{visual['role']}](assets/{embedded_name})", ""])
    return "\n".join(lines) + "\n"


def finalize(engine: Path, output: Path) -> dict[str, Any]:
    output = output.resolve()
    logger = ExecutionLogger(output, engine / "schemas/execution_log.schema.v2.json")
    pending = json.loads((output / "worker_request.json").read_text())
    start_id = pending["model_start_id"]
    domain_path, lab_path = output / "workers/domain.json", output / "workers/lab.json"
    if not domain_path.is_file() or not lab_path.is_file():
        raise RuntimeFailure("MODEL-OUTPUT-MISSING", "authorized model outputs are missing")
    before = json.loads((output / "interrupt_receipt.json").read_text())["preserved_hashes"]
    after = {"input_freeze": sha256_file(output / "input_freeze.json"),
             "worker_request": sha256_file(output / "worker_request.json")}
    if before != after:
        raise RuntimeFailure("RESUME-HASH-MISMATCH", f"{before} != {after}")
    domain = json.loads(domain_path.read_text())
    lab = json.loads(lab_path.read_text())
    jsonschema.Draft202012Validator(json.loads((output / "inputs/domain.schema.json").read_text())).validate(domain)
    jsonschema.Draft202012Validator(json.loads((output / "inputs/lab.schema.json").read_text())).validate(lab)
    if lab["domain"] != domain:
        raise RuntimeFailure("DOC-DERIVED-FROM-SOURCE", "lab domain is not byte-equivalent to model domain output")
    logger.complete(start_id, result="in-session model outputs received and schema-valid",
                    notes=f"domain={sha256_file(domain_path)} lab={sha256_file(lab_path)}")
    verifier_start = logger.start(action="Execute copied deterministic domain verifier",
                                  action_kind="command", authorized_paths=[str(output)],
                                  trigger="schema-valid unit domain",
                                  expected="copied verifier exits zero")
    verifier = subprocess.run(["python3", str(output / "inputs/verify_domain.py"), "--domain", str(domain_path)],
                              cwd=output, capture_output=True, text=True)
    if verifier.returncode != 0:
        logger.fail(verifier_start, failure_type="tool-error",
                    what_failed=(verifier.stdout + verifier.stderr)[-4000:],
                    expected="copied verifier exits zero")
        raise RuntimeFailure("DOMAIN-VERIFIER-FAILED", verifier.stdout + verifier.stderr)
    logger.complete(verifier_start, result=verifier.stdout.strip())
    receipt_result = check_receipts({"visuals": {"receipts": [item["provenance"] for item in lab["visuals"]]}}, output)
    result_dir = output / "results"
    atomic_json(result_dir / "unit_checks.json", {"LAB-SCHEMA-VALID": "PASS",
                "DOMAIN-SCHEMA-VALID": "PASS", "DOMAIN-VERIFIER": "PASS",
                "RECEIPT-HASH-RESOLVES": "PASS", "receipt_results": receipt_result,
                "forced_resume_hashes_before": before, "forced_resume_hashes_after": after}, root=output)
    render_start = logger.start(action="Render selected unit draft to shipped PDF", action_kind="render",
                                authorized_paths=[str(output)], trigger="validated model unit",
                                expected="Pandoc Typst PDF")
    document = output / "document"
    document.mkdir()
    shutil.copytree(output / "assets", document / "assets")
    markdown = document / f"{lab['identity']['unit_id']}.md"
    markdown.write_text(_markdown(lab), encoding="utf-8")
    pdf = document / f"{lab['identity']['unit_id']}.pdf"
    render = subprocess.run(["pandoc", str(markdown), "--resource-path", str(document),
                             "--pdf-engine=typst", "-V", "mainfont=Helvetica",
                             "-o", str(pdf)], cwd=output, capture_output=True, text=True)
    if render.returncode != 0:
        logger.fail(render_start, failure_type="tool-error", what_failed=f"PDF render failed: {render.stderr}",
                    expected="valid shipped PDF")
        raise RuntimeFailure("PDF-RENDER-FAILED", render.stderr)
    pages = rasterize_and_check_nonblank(pdf, output / "document/page_renders", dpi=200)
    logger.complete(render_start, result=f"rendered {len(pages)} nonblank PDF pages")
    terminal_start = logger.start(action="Record controller terminal decision for selected unit",
                                  action_kind="terminal_decision", authorized_paths=[str(output)],
                                  trigger="all executed blocking checks passed",
                                  expected="ACCEPTED draft with divergence disclosure")
    summary = {"terminal_state": "ACCEPTED", "unit_id": lab["identity"]["unit_id"],
               "claim": "every executed automated check passed",
               "draft_status": "pending downstream human review", "pdf": str(pdf),
               "pdf_sha256": sha256_file(pdf), "page_count": pdf_page_count(pdf),
               "page_renders": [{"path": str(page), "sha256": sha256_file(page)} for page in pages],
               "routing_divergence": "USER_AUTHORIZED_IN_SESSION_MODEL; cross-family judge bypassed",
               "resume_hashes_preserved": before == after}
    atomic_json(output / "acceptance.json", summary, root=output)
    logger.complete(terminal_start, result="selected unit accepted as draft under user-authorized divergence")
    audit = logger.audit()
    summary["execution_log_audit"] = audit
    atomic_json(output / "acceptance.json", summary, root=output)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "finalize"])
    parser.add_argument("--engine", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--curriculum", type=Path, default=Path("curricula/arduino_kit"))
    parser.add_argument("--lab-id", default="L01")
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    engine = args.engine.resolve()
    curriculum = args.curriculum if args.curriculum.is_absolute() else engine / args.curriculum
    value = prepare(engine, curriculum, args.lab_id, args.output_root) if args.action == "prepare" else finalize(engine, args.output_root)
    print(json.dumps(value, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
