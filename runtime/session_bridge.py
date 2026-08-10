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
import json
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any
from urllib.request import Request, urlopen

import jsonschema
import yaml

from . import pdf_inspect, run_state
from .checks import (CheckFailure, bloom_report, check_claim_entailment, check_derivation,
                     check_receipts, pdf_page_count, rasterize_and_check_nonblank,
                     readability_problems, required_checks_for)
from .checkpoint import Checkpoints
from .controller import CurriculumRuntime, RuntimeFailure
from .io import atomic_json, require_internal_output, sha256_file
from .lesson_render import child_facing_text, render_unit
from .logger import ExecutionLogger
from .visual_maps import regenerate_assets


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

    _, unresolved_roles = regenerate_assets(unit, curriculum, output, unit_id=lab_id, seed=seed_data)

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
        "unresolved_visual_roles": unresolved_roles,
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
    return render_unit(lab)


CROSS_FAMILY_BYPASS = "USER_AUTHORIZED_IN_SESSION_MODEL; cross-family judge bypassed"
VISUAL_REVIEW_FILE = "review/visual_review.json"


def _resolve_curriculum(engine: Path, output: Path, curriculum: Path | None) -> Path:
    if curriculum is not None:
        return Path(curriculum)
    meta = output.parent / "meta_execution_state.json"
    if not meta.is_file():
        raise RuntimeFailure("PRECONDITION-CURRICULUM-UNRESOLVED",
                             f"no curriculum given and no {meta} to read one from")
    return Path(json.loads(meta.read_text())["authorized_roots"]["curriculum"])


def finalize(engine: Path, output: Path, *, reentry_reason: str | None = None,
             curriculum: Path | None = None) -> dict[str, Any]:
    """Validate, render and score one unit against the real required check set.

    Fail-closed: every id in `checks.required_checks_for` gets one explicit
    `PASS`/`FAIL`/`NOT_RUN_BLOCKED` entry, and anything other than `PASS` on a blocking
    check keeps the unit out of `ACCEPTED`. `reentry_reason` makes a second finalization
    of an already-finalized root legal — it opens a new logger `ACT` rather than reusing
    the original run's closed one, and clears `document/` rather than assuming it is absent.
    """
    output = output.resolve()
    engine = Path(engine).resolve()
    curriculum = _resolve_curriculum(engine, output, curriculum)
    logger = ExecutionLogger(output, engine / "schemas/execution_log.schema.v2.json")
    pending = json.loads((output / "worker_request.json").read_text())
    if reentry_reason:
        # A new ACT, never the original run's already-closed model_start_id.
        start_id = logger.start(action="Re-finalize an already-finalized unit against corrected inputs",
                                action_kind="resume",
                                authorized_paths=[str(output / "workers/domain.json"),
                                                  str(output / "workers/lab.json")],
                                trigger=reentry_reason,
                                expected="schema-valid domain.json and lab.json")
    else:
        start_id = pending["model_start_id"]

    domain_path, lab_path = output / "workers/domain.json", output / "workers/lab.json"
    if not domain_path.is_file() or not lab_path.is_file():
        raise RuntimeFailure("MODEL-OUTPUT-MISSING", "authorized model outputs are missing")
    before = json.loads((output / "interrupt_receipt.json").read_text())["preserved_hashes"]
    after = {"input_freeze": sha256_file(output / "input_freeze.json"),
             "worker_request": sha256_file(output / "worker_request.json")}
    if before != after:
        raise RuntimeFailure("RESUME-HASH-MISMATCH", f"{before} != {after}")

    inventory = required_checks_for(engine, curriculum)
    results: dict[str, dict[str, Any]] = {
        check_id: {"result": "NOT_RUN_BLOCKED", "reason": "the check did not reach its subject",
                   "blocking": meta["blocking"], "source": meta["source"]}
        for check_id, meta in inventory["required"].items()}

    def record(check_id: str, result: str, reason: str = "", **extra: Any) -> None:
        results[check_id].update({"result": result, "reason": reason, **extra})

    domain = json.loads(domain_path.read_text())
    lab = json.loads(lab_path.read_text())
    jsonschema.Draft202012Validator(json.loads((output / "inputs/domain.schema.json").read_text())).validate(domain)
    jsonschema.Draft202012Validator(json.loads((output / "inputs/lab.schema.json").read_text())).validate(lab)
    record("LAB-SCHEMA-VALID", "PASS",
           "the unit validates against lab.schema.v4.json and its domain block against "
           "this curriculum's own domain schema")
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
    record("DOMAIN-VERIFIER", "PASS", verifier.stdout.strip()[:400])

    receipt_result = check_receipts({"visuals": {"receipts": [item["provenance"] for item in lab["visuals"]]}}, output)
    record("RECEIPT-HASH-RESOLVES", "PASS",
           f"{len(receipt_result)} receipts recomputed from the bytes they name")

    unresolved = (lab.get("content") or {}).get("unresolved_visual_roles") or []
    if unresolved:
        record("VISUAL-ROLES-COMPLETE", "FAIL",
               "unresolved visual role(s): " + "; ".join(entry["role"] for entry in unresolved),
               unresolved_visual_roles=unresolved)
    else:
        record("VISUAL-ROLES-COMPLETE", "PASS",
               "every visual role the manifest declares resolved to a shipped, receipted asset")

    try:
        derived = check_derivation(lab)
        entailed = check_claim_entailment(lab, output)
        record("DOC-DERIVED-FROM-SOURCE", "PASS",
               f"{len(derived)} rendered facts resolve to a domain pointer; "
               f"{len(entailed)} sourced claims resolve to text that supports them")
    except CheckFailure as error:
        record("DOC-DERIVED-FROM-SOURCE", "FAIL", str(error)[:800])

    render_start = logger.start(action="Render selected unit draft to shipped PDF", action_kind="render",
                                authorized_paths=[str(output)], trigger="validated model unit",
                                expected="Pandoc Typst PDF")
    document = output / "document"
    if reentry_reason:
        shutil.rmtree(document, ignore_errors=True)
    document.mkdir()
    shutil.copytree(output / "assets", document / "assets")
    markdown = document / f"{lab['identity']['unit_id']}.md"
    body = _markdown(lab)
    markdown.write_text(body, encoding="utf-8")
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

    child_text = child_facing_text(body)
    readability = readability_problems(child_text, engine / "policy/calibration.v1.yaml")
    record("TEXT-READABILITY-BAND", "PASS" if not readability else "FAIL",
           "; ".join(readability) or f"{len(child_text.split())} words of rendered child-facing "
                                     "text score inside the declared band")
    flags = bloom_report(lab, engine / "policy/calibration.v1.yaml")
    record("TEXT-BLOOM-VERBS", "PASS",
           f"{len(flags)} disagreement(s) recorded; this check flags and never blocks",
           flags=flags)

    try:
        legible = pdf_inspect.text_legible(pdf)
        record("PDF-TEXT-LEGIBLE", "PASS" if not legible["problems"] else "FAIL",
               "; ".join(legible["problems"]) or
               f"smallest rendered line box is {legible['smallest']}pt and no line is clipped")
    except CheckFailure as error:
        record("PDF-TEXT-LEGIBLE", "NOT_RUN_BLOCKED", str(error)[:400])
    try:
        assets = pdf_inspect.assets_resolve(pdf, lab["visuals"], output,
                                            output / "results/pdf_images")
        record("PDF-ASSET-RESOLVES", "PASS" if not assets["problems"] else "FAIL",
               "; ".join(assets["problems"]) or
               f"{len(assets['declared'])} receipted visuals resolve against the shipped PDF")
    except CheckFailure as error:
        record("PDF-ASSET-RESOLVES", "NOT_RUN_BLOCKED", str(error)[:400])

    review_path = output / VISUAL_REVIEW_FILE
    review_path.parent.mkdir(parents=True, exist_ok=True)
    if not review_path.is_file():
        review_path.write_text(json.dumps(
            pdf_inspect.visual_review_template(len(pages), lab["visuals"]), indent=2) + "\n",
            encoding="utf-8")
    verdict = json.loads(review_path.read_text())
    review_problems = pdf_inspect.visual_review_problems(verdict)
    record("PDF-VISUAL-REVIEW",
           "PASS" if not review_problems else ("FAIL" if verdict.get("reviewed") else "NOT_RUN_BLOCKED"),
           "; ".join(review_problems)[:800] or
           f"reviewer {verdict.get('reviewer')} answered every criterion for {len(pages)} pages "
           f"and {len(lab['visuals'])} visuals", verdict_path=VISUAL_REVIEW_FILE)

    atomic_json(output / "results/unit_checks.json", {
        "unit_id": lab["identity"]["unit_id"],
        "checks_version": inventory["checks_version"],
        "checks": results,
        "receipt_results": receipt_result,
        "forced_resume_hashes_before": before, "forced_resume_hashes_after": after}, root=output)

    blocking_failures = sorted(check_id for check_id, entry in results.items()
                               if entry["blocking"] and entry["result"] != "PASS")
    bypassed = CROSS_FAMILY_BYPASS in pending.get("routing_divergence", CROSS_FAMILY_BYPASS)

    if results["VISUAL-ROLES-COMPLETE"]["result"] != "PASS":
        terminal_state = "BLOCKED"
        claim = ("a visual role the curriculum's manifest requires has no verified asset: "
                 + "; ".join(f"{entry['role']} — {entry['reason']}" for entry in unresolved))
    elif blocking_failures:
        terminal_state = "BLOCKED"
        claim = "blocking checks did not pass: " + ", ".join(blocking_failures)
    elif bypassed:
        terminal_state = "ACCEPTED_PENDING_REVIEW"
        claim = ("every blocking check passed, but a cross-family judge was bypassed; "
                 "a downstream human step must resolve this before the unit is accepted")
    else:
        terminal_state = "ACCEPTED"
        claim = "every required check passed"

    terminal_start = logger.start(action="Record controller terminal decision for selected unit",
                                  action_kind="terminal_decision", authorized_paths=[str(output)],
                                  trigger=f"{len(results)} required checks scored",
                                  expected="a terminal state matching what the checks recorded")
    summary = {"terminal_state": terminal_state, "unit_id": lab["identity"]["unit_id"],
               "claim": claim,
               "draft_status": "pending downstream human review", "pdf": str(pdf),
               "pdf_sha256": sha256_file(pdf), "page_count": pdf_page_count(pdf),
               "page_renders": [{"path": str(page), "sha256": sha256_file(page)} for page in pages],
               "routing_divergence": CROSS_FAMILY_BYPASS,
               "checks": {check_id: entry["result"] for check_id, entry in results.items()},
               "blocking_failures": blocking_failures,
               "unresolved_visual_roles": unresolved,
               "visual_review": {"path": VISUAL_REVIEW_FILE, "problems": review_problems},
               "reentry_reason": reentry_reason,
               "resume_hashes_preserved": before == after}
    atomic_json(output / "acceptance.json", summary, root=output)
    logger.complete(terminal_start, result=f"unit recorded {terminal_state}")
    audit = logger.audit()
    summary["execution_log_audit"] = audit
    atomic_json(output / "acceptance.json", summary, root=output)
    run_state.record_unit_transition(output.parent, summary["unit_id"], terminal_state)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "finalize"])
    parser.add_argument("--engine", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--curriculum", type=Path, default=Path("curricula/arduino_kit"))
    parser.add_argument("--lab-id", default="L01")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--reentry-reason", default=None,
                        help="re-finalize an already-finalized unit, stating why")
    args = parser.parse_args()
    engine = args.engine.resolve()
    curriculum = args.curriculum if args.curriculum.is_absolute() else engine / args.curriculum
    value = (prepare(engine, curriculum, args.lab_id, args.output_root) if args.action == "prepare"
             else finalize(engine, args.output_root, reentry_reason=args.reentry_reason,
                           curriculum=curriculum))
    print(json.dumps(value, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
