from __future__ import annotations

import json
from pathlib import Path
import subprocess
import threading
import time
from typing import Any, Callable

import jsonschema
import yaml

from .checkpoint import CheckpointError, Checkpoints
from .io import atomic_json, canonical, canonical_hash, require_internal_output, require_within, sha256_file
from .logger import ExecutionLogger, LogError
from .routing import Selector


class RuntimeFailure(RuntimeError):
    def __init__(self, failure_id: str, message: str, terminal_state: str = "SYSTEM_FAILURE"):
        super().__init__(message)
        self.failure_id = failure_id
        self.terminal_state = terminal_state


class CurriculumRuntime:
    def __init__(self, engine: Path | None = None):
        self.engine = canonical(engine or Path(__file__).resolve().parents[1])
        self.prompt = self.engine / "meta_prompt/curriculum.prompt.v1.md"
        self.controller_policy = yaml.safe_load((self.engine / "policy/controller.v1.yaml").read_text())
        self.limit_policy = yaml.safe_load((self.engine / "policy/limits.v1.yaml").read_text())
        self.states = list(self.controller_policy["states"])
        self.selector = Selector(self.engine)

    def legal_transition(self, current: str, following: str) -> bool:
        if current not in self.states:
            return False
        index = self.states.index(current)
        expected = self.states[index + 1] if index + 1 < len(self.states) else "ACCEPTED"
        return following == expected

    def resolve_curriculum(self, value: str | Path) -> Path:
        curriculum = canonical(Path(value) if Path(value).is_absolute() else self.engine / value)
        curricula_root = canonical(self.engine / "curricula")
        if curricula_root not in curriculum.parents:
            raise RuntimeFailure("PRECONDITION-CURRICULUM-OUTSIDE-ENGINE", f"curriculum escapes curricula root: {curriculum}")
        if not curriculum.is_dir():
            raise RuntimeFailure("PRECONDITION-CURRICULUM-MISSING", f"curriculum directory missing: {curriculum}")
        return curriculum

    def resolve_companions(self) -> list[Path]:
        names = ["unit_prose.v1.md", "pedagogy.v1.md", "model_selector_prompt.v1.md"]
        paths = [self.engine / "meta_prompt/assets" / name for name in names]
        missing = [str(path) for path in paths if not path.is_file()]
        if missing:
            raise RuntimeFailure("PRECONDITION-ASSETS-RESOLVE", f"missing companions: {missing}")
        return paths

    def manifest_path(self, curriculum: Path) -> Path:
        manifests = sorted(curriculum.glob("*curriculum.v*.yaml"))
        if not manifests:
            raise RuntimeFailure("PRECONDITION-MANIFEST-MISSING", f"no active manifest under {curriculum}")
        def version(path: Path) -> int:
            import re
            match = re.search(r"\.v(\d+)\.yaml$", path.name)
            return int(match.group(1)) if match else -1
        return max(manifests, key=version)

    def validated_manifest(self, curriculum: Path) -> tuple[Path, dict[str, Any]]:
        path = self.manifest_path(curriculum)
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            schema = json.loads((self.engine / "schemas/curriculum.schema.v5.json").read_text())
            jsonschema.Draft202012Validator(schema).validate(raw)
        except (yaml.YAMLError, json.JSONDecodeError, jsonschema.ValidationError) as error:
            raise RuntimeFailure("PRECONDITION-MANIFEST-INVALID", f"manifest invalid before value consumption: {error}") from error
        domain_contract = canonical(self.engine / raw["domain"]["manifest_schema"])
        if curriculum not in domain_contract.parents:
            raise RuntimeFailure("PRECONDITION-DOMAIN-CONTRACT-ESCAPES", str(domain_contract))
        contract = json.loads(domain_contract.read_text(encoding="utf-8"))
        try:
            jsonschema.Draft202012Validator(contract["$defs"]["config"]).validate(raw["domain"]["config"])
            validator = jsonschema.Draft202012Validator(contract["$defs"]["core_activity"])
            for lab in raw["labs"]:
                validator.validate(lab["core_activity"])
        except jsonschema.ValidationError as error:
            raise RuntimeFailure("PRECONDITION-DOMAIN-MANIFEST-INVALID", str(error)) from error
        ids = [lab["id"] for lab in raw["labs"]]
        if len(ids) != len(set(ids)):
            raise RuntimeFailure("CUR-IDS-NOT-UNIQUE", f"duplicate ids: {ids}")
        return path, raw

    def run_verifier_fixtures(self, manifest: dict[str, Any]) -> list[dict[str, Any]]:
        declaration = manifest.get("domain", {}).get("verifier")
        if not declaration or declaration.get("proven", {}).get("result") != "all_fixtures_behaved":
            raise RuntimeFailure("PRECONDITION-VERIFIER-UNPROVEN", "domain verifier missing or unproven")
        entry = canonical(self.engine / declaration["entry_point"])
        if not entry.is_file() or self.engine not in entry.parents:
            raise RuntimeFailure("PRECONDITION-VERIFIER-MISSING", str(entry))
        results = []
        for item in declaration["must_reject"]:
            fixture = canonical(self.engine / item["fixture"])
            proc = subprocess.run(["python3", str(entry), "--domain", str(fixture)], cwd=self.engine,
                                  capture_output=True, text=True)
            combined = proc.stdout + proc.stderr
            if proc.returncode == 0 or item["expected_code"] not in combined:
                raise RuntimeFailure("PRECONDITION-VERIFIER-FIXTURE", f"reject fixture behaved incorrectly: {fixture}: {combined}")
            results.append({"fixture": str(fixture), "expected": "reject", "code": item["expected_code"]})
        for value in declaration["must_accept"]:
            fixture = canonical(self.engine / value)
            proc = subprocess.run(["python3", str(entry), "--domain", str(fixture)], cwd=self.engine,
                                  capture_output=True, text=True)
            if proc.returncode != 0:
                raise RuntimeFailure("PRECONDITION-VERIFIER-FIXTURE", f"accept fixture refused: {fixture}: {proc.stdout}{proc.stderr}")
            results.append({"fixture": str(fixture), "expected": "accept"})
        return results

    def _logger_gate(self, logger: ExecutionLogger, output: Path) -> dict[str, Any]:
        opened: list[str] = []
        guard = threading.Lock()
        def append_pair(index: int) -> None:
            start = logger.start(action=f"Concurrent logger probe operation {index}", action_kind="test",
                                 authorized_paths=[str(output)], trigger="logger gate zero",
                                 expected="paired concurrent append")
            logger.complete(start, result=f"probe {index} completed")
            with guard:
                opened.append(start)
        threads = [threading.Thread(target=append_pair, args=(index,)) for index in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        audit = logger.audit()
        if not audit["monotonic"] or audit["unclosed_starts"] or audit["duplicate_closes"] or len(opened) != 4:
            raise RuntimeFailure("LOG-GATE-FAILED", str(audit))
        return audit

    def static_preflight(self, curriculum: Path) -> dict[str, Any]:
        companions = self.resolve_companions()
        manifest_path, manifest = self.validated_manifest(curriculum)
        fixtures = self.run_verifier_fixtures(manifest)
        return {
            "status": "PASS", "manifest": str(manifest_path), "manifest_sha256": sha256_file(manifest_path),
            "unit_count": len(manifest["labs"]), "unit_ids": [lab["id"] for lab in manifest["labs"]],
            "companions": [{"path": str(path), "sha256": sha256_file(path)} for path in companions],
            "verifier_fixtures": fixtures,
        }

    def prepare_output(self, output_root: Path, *, resume: bool) -> Path:
        output = require_internal_output(output_root, self.engine)
        if resume:
            if not output.is_dir():
                raise RuntimeFailure("PRECONDITION-RESUME-ROOT-MISSING", str(output))
        else:
            if output.exists():
                raise RuntimeFailure("PRECONDITION-OUTPUT-ROOT-EXISTS", str(output))
            output.mkdir(parents=True)
            (output / "results").mkdir()
        return output

    def simulate(self, curriculum: Path, output_root: Path, *, lab_id: str | None = None,
                 resume: bool = False, interrupt_after: str | None = None,
                 failure_injector: Callable[[str], str | None] | None = None) -> dict[str, Any]:
        output = self.prepare_output(output_root, resume=resume)
        logger = ExecutionLogger(output, self.engine / "schemas/execution_log.schema.v2.json")
        started_at = time.monotonic()
        required_checkpoints: set[str] = set()
        required_transitions: set[str] = set()
        if not resume:
            gate = self._logger_gate(logger, output)
            atomic_json(output / "results/gate_0_logger.json", gate, root=output)
        manifest_path, manifest = self.validated_manifest(curriculum)
        self.run_verifier_fixtures(manifest)
        units = manifest["labs"]
        if lab_id:
            units = [unit for unit in units if unit["id"] == lab_id]
            if not units:
                raise RuntimeFailure("PRECONDITION-UNKNOWN-UNIT", lab_id)
        checkpoints = Checkpoints(output)
        prefix = checkpoints.valid_prefix() if resume else []
        start_index = len(prefix)
        attempts = 0
        failures_seen: dict[tuple[str, ...], int] = {}
        state_outputs: list[Path] = []
        for ordinal, state in enumerate(self.states, 1):
            if ordinal <= start_index:
                continue
            next_state = self.states[ordinal] if ordinal < len(self.states) else "ACCEPTED"
            transition_id = f"TRANSITION-{ordinal:03d}-{state}"
            required_transitions.add(transition_id)
            start = logger.start(action=f"Execute simulated controller state {state}", action_kind="state_transition",
                                 authorized_paths=[str(output)], trigger=f"state machine {state}",
                                 expected=f"legal transition to {next_state}", notes=transition_id)
            injected = failure_injector(state) if failure_injector else None
            if injected:
                failed_set = (injected,)
                failures_seen[failed_set] = failures_seen.get(failed_set, 0) + 1
                attempts += 1
                logger.fail(start, failure_type="wrong-output", what_failed=f"simulated failed check {injected}",
                            expected="affected artifact passes targeted rerun")
                if failures_seen[failed_set] >= self.limit_policy["convergence"]["repeat_failure_threshold"]["value"]:
                    raise RuntimeFailure("REPEAT-FAILURE", injected)
                continue
            state_path = output / "simulated" / "states" / f"{ordinal:03d}_{state}.json"
            atomic_json(state_path, {"state": state, "units": [unit["id"] for unit in units],
                                    "simulated": True, "next_state": next_state}, root=output)
            state_outputs.append(state_path)
            logger.complete(start, result=f"state {state} completed", notes=transition_id)
            checkpoint_id = f"CHECKPOINT-{ordinal:03d}-{state}"
            checkpoint_start = logger.start(action=f"Write atomic checkpoint after state {state}", action_kind="file_write",
                                            authorized_paths=[str(output)], trigger=f"completed {state}",
                                            expected="hashed atomic checkpoint", notes=checkpoint_id)
            checkpoint = checkpoints.write(ordinal=ordinal, state=state, next_state=next_state,
                                           inputs=[manifest_path], outputs=[state_path], attempt=attempts,
                                           started_at=started_at)
            logger.complete(checkpoint_start, result=f"checkpoint {checkpoint.name} committed", notes=checkpoint_id)
            required_checkpoints.add(checkpoint_id)
            if interrupt_after == state:
                atomic_json(output / "interrupt_receipt.json", {"after_state": state,
                            "checkpoint": str(checkpoint), "checkpoint_sha256": sha256_file(checkpoint)}, root=output)
                return {"terminal_state": "INTERRUPTED", "next_state": next_state, "output_root": str(output)}
        terminal = logger.start(action="Record simulated terminal acceptance decision", action_kind="terminal_decision",
                                authorized_paths=[str(output)], trigger="zero blocking simulated checks",
                                expected="ACCEPTED simulation only")
        logger.complete(terminal, result="simulated controller accepted; not generated-unit evidence")
        audit = logger.audit(required_checkpoint_ids=required_checkpoints,
                             required_transition_ids=required_transitions)
        if audit["unclosed_starts"] or audit["duplicate_closes"] or audit["missing_checkpoints"] or audit["missing_transitions"]:
            raise RuntimeFailure("FINAL-LOG-AUDIT", str(audit))
        summary = {"terminal_state": "ACCEPTED", "coverage": "simulated-controller-only",
                   "unit_count": len(units), "unit_ids": [unit["id"] for unit in units],
                   "attempt": attempts, "log_audit": audit, "output_root": str(output)}
        atomic_json(output / "simulated_acceptance.json", summary, root=output)
        return summary
