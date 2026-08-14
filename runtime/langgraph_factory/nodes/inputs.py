"""Episode bootstrap, identity freeze, effective run, capability, and resume nodes.

Owns D00, D00R, D01, D02, D03, D04, D92, and D96. These are the nodes that
decide what run this is, what it is allowed to build, and whether it may build
anything at all. None of them produces curriculum content.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from . import (
    PrerequisitePause,
    SystemFailure,
    canonical_digest,
    deterministic_node,
    guard,
    require,
)

__all__ = [
    "BOOTSTRAP_KINDS",
    "RESUMABLE_TERMINAL_KINDS",
    "RUN_MODES",
    "REQUIRED_CAPABILITIES",
    "MANDATORY_DRIVER_CLIS",
    "DRIVER_CAPABILITY_FIELDS",
    "EPISODE_INVOCATION_FIELDS",
    "compile_prerequisite_closure",
    "manifest_unit_records",
    "D00_BOOTSTRAP_EPISODE",
    "D00R_REVALIDATE_RESUME_IDENTITY",
    "D01_VALIDATE_AND_FREEZE_INPUTS",
    "D02_COMPILE_EFFECTIVE_RUN",
    "D03_PROVE_CAPABILITIES",
    "D04_INITIALIZE_OR_RESUME",
    "D92_REENTER_VALIDATED_FRONTIER",
    "D96_GRACEFUL_INTERRUPT_GATE",
]


BOOTSTRAP_KINDS: tuple[str, ...] = ("fresh", "resume", "recover_orphan")

# Spec section 14's `Resume` column: only these two terminals may legally be
# resumed. Everything else is a final episode outcome.
RESUMABLE_TERMINAL_KINDS: tuple[str, ...] = ("INTERRUPTED", "PAUSED_PREREQUISITE")

RUN_MODES: tuple[str, ...] = ("one", "all")

REQUIRED_CAPABILITIES: tuple[str, ...] = (
    "model_cli_identity",
    "retrieval",
    "renderer",
    "rasterizer",
    "persistence",
    "logger",
)

# The two model-CLI drivers spec 7.1/7.2 pin (`policy/routing/model_registry.v1.yaml`,
# `runtime/langgraph_factory/config/model_jobs.v1.yaml`); D03 requires a real,
# differentiated capability proof for each before any of the eight jobs may dispatch.
MANDATORY_DRIVER_CLIS: tuple[str, ...] = ("claude", "codex")

# The five differentiated proof classes spec 7.1 requires (no single undifferentiated
# ready flag): executable identity, permitted (subscription, never API-key) auth mode,
# observable subscription-backed usability, content-free probe operation, and the D03
# tool/MCP-closure check. `approved_data_boundary` is carried alongside them so the
# provider/data-class boundary N20's `egress.py` owns is proven read-only, never
# reimplemented locally.
DRIVER_CAPABILITY_FIELDS: tuple[str, ...] = (
    "executable_identity",
    "permitted_auth_mode",
    "observable_subscription_backed_usability",
    "content_free_operation",
    "tool_mcp_closure",
    "approved_data_boundary",
)

# The envelope the pre-invocation helper supplies as `FactoryInput["invocation"]`.
# D00 is the only node that reads it raw; every later node reads frozen state.
EPISODE_INVOCATION_FIELDS: tuple[str, ...] = (
    "kind",
    "contract_version",
    "engine_root",
    "curriculum_root",
    "output_root",
    "mode",
    "requested_unit_id",
    "authorization",
    "episode_ordinal",
    "prior_identity",
    "prior_terminal",
    "lease_open",
)

_MANIFEST_UNITS_KEY = "labs"
_UNIT_ID_KEY = "id"


def _record(value: Any, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), "schema_contract", f"{label} must be a JSON object")
    return dict(value)


def _text(value: Any, label: str) -> str:
    require(
        isinstance(value, str) and value.strip() != "",
        "schema_contract",
        f"{label} must be a non-empty string",
    )
    return value


def _canonical_path(value: Any, label: str) -> Path:
    """Canonicalize an absolute path, rejecting relative traversal segments.

    Symlinked parents are resolved rather than rejected (macOS `/var` is one),
    but a `..` segment is refused outright: it is the form a containment escape
    takes, and resolving it silently would hide where the run actually points.
    """

    path = Path(_text(value, label))
    require(path.is_absolute(), "invalid_input", f"{label} must be an absolute path", value=str(path))
    require(
        ".." not in path.parts,
        "invalid_input",
        f"{label} must not contain a relative traversal segment",
        value=str(path),
    )
    return path.resolve()


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _now(runtime_context: Any) -> str:
    clock = getattr(runtime_context, "clock", None)
    require(callable(clock), "capability", "runtime context exposes no clock")
    return str(clock())


# --------------------------------------------------------------------------
# D00
# --------------------------------------------------------------------------


@deterministic_node("D00_BOOTSTRAP_EPISODE")
def D00_BOOTSTRAP_EPISODE(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Classify this episode as fresh, legal resume, or orphan recovery."""

    invocation = projection["invocation"]
    require(invocation is not None, "invalid_input", "no episode invocation was supplied")
    envelope = _record(invocation, "invocation")

    unknown = sorted(set(envelope) - set(EPISODE_INVOCATION_FIELDS))
    require(
        not unknown,
        "schema_contract",
        "invocation envelope declares undeclared fields",
        unknown=unknown,
    )

    kind = envelope.get("kind")
    require(
        kind in BOOTSTRAP_KINDS,
        "invalid_input",
        f"invocation kind {kind!r} is not one of {list(BOOTSTRAP_KINDS)}",
    )

    prior_identity_present = bool(projection["run_id"]) or bool(envelope.get("prior_identity"))
    prior_terminal = envelope.get("prior_terminal") or projection["terminal"]
    lease_open = bool(envelope.get("lease_open"))

    if kind == "fresh":
        require(
            not prior_identity_present,
            "identity",
            "a fresh invocation cannot start against an existing run identity",
        )
        require(
            not lease_open,
            "identity",
            "a fresh invocation cannot start while a prior episode lease is open",
        )
        classification = "fresh"
    elif kind == "resume":
        require(
            prior_identity_present,
            "identity",
            "a resume invocation requires a prior immutable run identity",
        )
        require(
            isinstance(prior_terminal, dict),
            "identity",
            "a resume invocation requires a prior terminal record",
        )
        terminal_kind = prior_terminal.get("kind")
        require(
            terminal_kind in RESUMABLE_TERMINAL_KINDS,
            "identity",
            f"terminal {terminal_kind!r} is not legally resumable",
            resumable=list(RESUMABLE_TERMINAL_KINDS),
        )
        classification = "resume"
    else:
        require(
            prior_identity_present,
            "identity",
            "orphan recovery requires a prior immutable run identity",
        )
        require(
            lease_open and prior_terminal is None,
            "identity",
            "orphan recovery requires an open prior lease with no terminal",
            lease_open=lease_open,
            has_terminal=prior_terminal is not None,
        )
        classification = "recover_orphan"

    # The sanitized envelope is what every later node sees: the raw prior
    # terminal/lease summary is bootstrap-only evidence and is not carried
    # forward as if it were this episode's state.
    sanitized = {
        field: envelope.get(field)
        for field in EPISODE_INVOCATION_FIELDS
        if field not in ("prior_terminal", "lease_open")
    }
    sanitized["kind"] = classification

    return {
        "bootstrap_kind": classification,
        "invocation": sanitized,
        "pending_guard": guard("D00_BOOTSTRAP_EPISODE", classification),
    }


# --------------------------------------------------------------------------
# D00R
# --------------------------------------------------------------------------


@deterministic_node("D00R_REVALIDATE_RESUME_IDENTITY")
def D00R_REVALIDATE_RESUME_IDENTITY(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Prove the supplied resume identity equals the frozen prior identity exactly."""

    envelope = _record(projection["invocation"], "invocation")
    comparisons: list[dict[str, Any]] = []
    mismatched: list[str] = []

    supplied_by_field = {
        "contract_version": envelope.get("contract_version"),
        "engine_root": envelope.get("engine_root"),
        "curriculum_root": envelope.get("curriculum_root"),
        "output_root": envelope.get("output_root"),
        "mode": envelope.get("mode"),
        "requested_unit_id": envelope.get("requested_unit_id"),
    }
    for field, supplied in supplied_by_field.items():
        frozen = projection[field]
        equal = supplied == frozen
        comparisons.append({"field": field, "frozen": frozen, "supplied": supplied, "equal": equal})
        if not equal:
            mismatched.append(field)

    frozen_inputs = projection["frozen_inputs"]
    frozen_digest = projection["frozen_digest"]
    recomputed = canonical_digest(frozen_inputs)
    digest_equal = recomputed == frozen_digest
    comparisons.append(
        {
            "field": "frozen_digest",
            "frozen": frozen_digest,
            "supplied": recomputed,
            "equal": digest_equal,
        }
    )
    if not digest_equal:
        mismatched.append("frozen_digest")

    # Every frozen input must still hash to its recorded value: a resume that
    # re-reads changed engine bytes is a different run wearing the same identity.
    drifted: list[dict[str, str]] = []
    for entry in frozen_inputs:
        record = _record(entry, "frozen input")
        path = Path(_text(record.get("path"), "frozen input path"))
        expected = _text(record.get("sha256"), "frozen input sha256")
        if not path.is_file():
            drifted.append({"path": str(path), "expected": expected, "actual": "MISSING"})
            continue
        actual = _sha256_file(path)
        if actual != expected:
            drifted.append({"path": str(path), "expected": expected, "actual": actual})
    if drifted:
        mismatched.append("frozen_inputs")

    supplied_authorization = envelope.get("authorization")
    frozen_authorizations = projection["external_authorizations"]
    authorization_equal = canonical_digest(supplied_authorization) == canonical_digest(
        frozen_authorizations
    )
    comparisons.append(
        {
            "field": "external_authorizations",
            "frozen": canonical_digest(frozen_authorizations),
            "supplied": canonical_digest(supplied_authorization),
            "equal": authorization_equal,
        }
    )
    if not authorization_equal:
        mismatched.append("external_authorizations")

    history = projection["terminal_history"]
    last_terminal = history[-1] if history else None
    terminal_kind = last_terminal.get("kind") if isinstance(last_terminal, dict) else None
    terminal_legal = terminal_kind in RESUMABLE_TERMINAL_KINDS
    comparisons.append(
        {
            "field": "prior_terminal",
            "frozen": terminal_kind,
            "supplied": terminal_kind,
            "equal": terminal_legal,
        }
    )
    if not terminal_legal:
        mismatched.append("prior_terminal")

    require(
        not mismatched,
        "identity",
        "resume identity revalidation failed",
        mismatched=sorted(set(mismatched)),
        drifted_inputs=drifted,
    )

    receipt = {
        "kind": "resume_identity_comparison",
        "run_id": projection["run_id"],
        "comparisons": comparisons,
        "result": "PASS",
    }
    receipt["key"] = canonical_digest(receipt)

    validated = {
        "run_id": projection["run_id"],
        "contract_version": projection["contract_version"],
        "frozen_digest": frozen_digest,
        "mode": projection["mode"],
        "requested_unit_id": projection["requested_unit_id"],
        "engine_root": projection["engine_root"],
        "curriculum_root": projection["curriculum_root"],
        "active_manifest_path": projection["active_manifest_path"],
        "output_root": projection["output_root"],
        "prior_terminal_kind": terminal_kind,
        "comparison_key": receipt["key"],
    }

    return {
        "validated_recovery_envelope": validated,
        "evidence_index_entries": [receipt],
        "pending_guard": guard("D00R_REVALIDATE_RESUME_IDENTITY", "resume_identity_proven"),
    }


# --------------------------------------------------------------------------
# D01
# --------------------------------------------------------------------------


def _frozen_input_records(
    engine_root: Path, curriculum_root: Path, manifest_path: Path
) -> list[dict[str, str]]:
    """Hash every file whose bytes define what this run is allowed to build."""

    records: list[dict[str, str]] = [
        {"path": str(manifest_path), "sha256": _sha256_file(manifest_path), "role": "active_manifest"}
    ]
    for relative, role in (
        ("schemas", "engine_schema"),
        ("policy", "engine_policy"),
        ("meta_prompt", "engine_contract"),
    ):
        directory = engine_root / relative
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                records.append({"path": str(path), "sha256": _sha256_file(path), "role": role})
    for path in sorted(curriculum_root.rglob("*")):
        if path.is_file() and "deprecated" not in path.parts:
            records.append({"path": str(path), "sha256": _sha256_file(path), "role": "curriculum"})
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for record in records:
        if record["path"] in seen:
            continue
        seen.add(record["path"])
        unique.append(record)
    return sorted(unique, key=lambda item: item["path"])


def _resolve_active_manifest(curriculum_root: Path) -> Path:
    """Select the highest-versioned active manifest without naming a curriculum."""

    candidates = [
        path
        for path in curriculum_root.glob("*curriculum.v*.yaml")
        if "deprecated" not in path.parts
    ]
    require(
        bool(candidates),
        "invalid_input",
        "no active curriculum manifest under the curriculum root",
        curriculum_root=str(curriculum_root),
    )

    def version(path: Path) -> int:
        match = re.search(r"\.v(\d+)\.yaml$", path.name)
        return int(match.group(1)) if match else -1

    return max(candidates, key=lambda path: (version(path), path.name))


@deterministic_node("D01_VALIDATE_AND_FREEZE_INPUTS")
def D01_VALIDATE_AND_FREEZE_INPUTS(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Freeze the immutable run identity, input hashes, and authorization declaration."""

    envelope = _record(projection["invocation"], "invocation")

    engine_root = _canonical_path(envelope.get("engine_root"), "engine_root")
    curriculum_root = _canonical_path(envelope.get("curriculum_root"), "curriculum_root")
    output_root = _canonical_path(envelope.get("output_root"), "output_root")

    require(engine_root.is_dir(), "invalid_input", "engine root is not a directory")
    require(curriculum_root.is_dir(), "invalid_input", "curriculum root is not a directory")
    require(
        engine_root in curriculum_root.parents,
        "invalid_input",
        "curriculum root escapes the engine root",
        engine_root=str(engine_root),
        curriculum_root=str(curriculum_root),
    )
    require(
        output_root != engine_root and curriculum_root not in (output_root, *output_root.parents),
        "invalid_input",
        "output root must not be, or sit inside, the engine or curriculum roots",
        output_root=str(output_root),
    )

    mode = envelope.get("mode")
    require(mode in RUN_MODES, "invalid_input", f"mode {mode!r} is not one of {list(RUN_MODES)}")
    requested_unit_id = envelope.get("requested_unit_id")
    if mode == "one":
        require(
            isinstance(requested_unit_id, str) and requested_unit_id != "",
            "invalid_input",
            "mode 'one' requires a requested unit id",
        )
    else:
        require(
            requested_unit_id is None,
            "invalid_input",
            "mode 'all' must not name a requested unit id",
        )

    authorization = envelope.get("authorization")
    require(
        isinstance(authorization, dict) and bool(authorization),
        "authorization",
        "a run requires an explicit external-data authorization record",
    )

    manifest_path = _resolve_active_manifest(curriculum_root)
    frozen_inputs = _frozen_input_records(engine_root, curriculum_root, manifest_path)
    frozen_digest = canonical_digest(frozen_inputs)

    executables: list[dict[str, Any]] = []
    for declaration in authorization.get("executables", []) or []:
        record = _record(declaration, "executable declaration")
        name = _text(record.get("name"), "executable name")
        resolved = record.get("path")
        entry: dict[str, Any] = {"name": name, "path": resolved}
        if isinstance(resolved, str) and Path(resolved).is_file():
            entry["sha256"] = _sha256_file(Path(resolved))
        executables.append(entry)

    created_at = _now(runtime_context)
    identity_seed = {
        "contract_version": envelope.get("contract_version"),
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "output_root": str(output_root),
        "mode": mode,
        "requested_unit_id": requested_unit_id,
        "frozen_digest": frozen_digest,
        "created_at": created_at,
    }

    return {
        "contract_version": _text(envelope.get("contract_version"), "contract_version"),
        "run_id": canonical_digest(identity_seed),
        "created_at": created_at,
        "engine_root": str(engine_root),
        "curriculum_root": str(curriculum_root),
        "active_manifest_path": str(manifest_path),
        "output_root": str(output_root),
        "mode": mode,
        "requested_unit_id": requested_unit_id,
        "frozen_inputs": frozen_inputs,
        "frozen_digest": frozen_digest,
        "frozen_executable_identities": executables,
        "external_authorizations": [authorization],
        "pending_guard": guard("D01_VALIDATE_AND_FREEZE_INPUTS", "inputs_frozen"),
    }


# --------------------------------------------------------------------------
# D02
# --------------------------------------------------------------------------


def manifest_unit_records(manifest: Any) -> list[dict[str, Any]]:
    """Extract the ordered unit records of an arbitrary manifest.

    Manifest-neutral: the number of units, their identifiers, and their order all
    come from the document. Nothing here knows any curriculum.
    """

    require(isinstance(manifest, dict), "schema_contract", "manifest must be a mapping")
    units = manifest.get(_MANIFEST_UNITS_KEY)
    require(
        isinstance(units, list) and bool(units),
        "schema_contract",
        f"manifest {_MANIFEST_UNITS_KEY!r} must be a non-empty list",
    )
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, unit in enumerate(units):
        record = _record(unit, f"manifest unit at index {index}")
        unit_id = record.get(_UNIT_ID_KEY)
        require(
            isinstance(unit_id, str) and unit_id != "",
            "schema_contract",
            f"manifest unit at index {index} has no string {_UNIT_ID_KEY!r}",
        )
        require(
            unit_id not in seen,
            "schema_contract",
            f"manifest declares duplicate unit id {unit_id!r}",
        )
        seen.add(unit_id)
        records.append(record)
    return records


def _declared_prerequisites(unit: dict[str, Any]) -> list[str]:
    sequence = unit.get("sequence")
    if isinstance(sequence, dict) and "prerequisites" in sequence:
        declared = sequence["prerequisites"]
    else:
        declared = unit.get("prerequisites", [])
    if declared is None:
        return []
    require(
        isinstance(declared, list),
        "schema_contract",
        f"unit {unit.get(_UNIT_ID_KEY)!r} declares a non-list prerequisites value",
    )
    for value in declared:
        require(
            isinstance(value, str),
            "schema_contract",
            f"unit {unit.get(_UNIT_ID_KEY)!r} declares a non-string prerequisite",
        )
    return list(declared)


def compile_prerequisite_closure(
    unit_records: list[dict[str, Any]], target_unit_id: str
) -> list[str]:
    """Return the target's complete transitive prerequisite closure, in manifest order.

    Iterative rather than recursive so an arbitrarily deep chain cannot exhaust
    the interpreter stack, and cycle-detecting rather than depth-bounded so a
    malformed DAG is rejected by name instead of by timeout.
    """

    by_id = {unit[_UNIT_ID_KEY]: unit for unit in unit_records}
    require(
        target_unit_id in by_id,
        "invalid_input",
        f"requested unit {target_unit_id!r} is not in the manifest",
        known_unit_count=len(by_id),
    )

    required: set[str] = set()
    # Explicit DFS with an on-stack marker set: an edge back into the current
    # path is a cycle, an edge into an already-closed node is simple reuse.
    on_path: set[str] = set()
    stack: list[tuple[str, bool]] = [(target_unit_id, False)]
    while stack:
        unit_id, expanded = stack.pop()
        if expanded:
            on_path.discard(unit_id)
            required.add(unit_id)
            continue
        if unit_id in required:
            continue
        if unit_id in on_path:
            raise SystemFailure(
                "schema_contract",
                f"manifest prerequisite graph contains a cycle through {unit_id!r}",
                {"unit_id": unit_id, "path": sorted(on_path)},
            )
        on_path.add(unit_id)
        stack.append((unit_id, True))
        for prerequisite in _declared_prerequisites(by_id[unit_id]):
            if prerequisite not in by_id:
                raise SystemFailure(
                    "schema_contract",
                    f"unit {unit_id!r} declares unknown prerequisite {prerequisite!r}",
                    {"unit_id": unit_id, "prerequisite": prerequisite},
                )
            if prerequisite not in required:
                stack.append((prerequisite, False))

    return [unit[_UNIT_ID_KEY] for unit in unit_records if unit[_UNIT_ID_KEY] in required]


@deterministic_node("D02_COMPILE_EFFECTIVE_RUN")
def D02_COMPILE_EFFECTIVE_RUN(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Freeze the ordered unit list, target closure, and acceptance denominator."""

    manifest_path = Path(_text(projection["active_manifest_path"], "active_manifest_path"))
    frozen = {record["path"]: record["sha256"] for record in projection["frozen_inputs"]}
    require(
        str(manifest_path) in frozen,
        "integrity",
        "the active manifest is not in the frozen input set",
        manifest=str(manifest_path),
    )
    require(manifest_path.is_file(), "integrity", "the frozen active manifest is missing")
    actual = _sha256_file(manifest_path)
    require(
        actual == frozen[str(manifest_path)],
        "integrity",
        "the active manifest changed after it was frozen",
        expected=frozen[str(manifest_path)],
        actual=actual,
    )

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise SystemFailure(
            "schema_contract", f"active manifest is not parseable YAML: {error}"
        ) from error

    unit_records = manifest_unit_records(manifest)
    ordered_ids = [unit[_UNIT_ID_KEY] for unit in unit_records]

    # A declared prerequisite must exist even in `all` mode: an unresolvable
    # edge means the manifest's own ordering claim is unverifiable.
    known = set(ordered_ids)
    for unit in unit_records:
        for prerequisite in _declared_prerequisites(unit):
            require(
                prerequisite in known,
                "schema_contract",
                f"unit {unit[_UNIT_ID_KEY]!r} declares unknown prerequisite {prerequisite!r}",
            )

    mode = projection["mode"]
    requested_unit_id = projection["requested_unit_id"]
    if mode == "all":
        # `all` mode must still prove the whole graph is acyclic, which the
        # per-target closure does for every node at once.
        for unit_id in ordered_ids:
            compile_prerequisite_closure(unit_records, unit_id)
        target_closure = list(ordered_ids)
    else:
        require(
            isinstance(requested_unit_id, str) and requested_unit_id != "",
            "invalid_input",
            "mode 'one' requires a requested unit id",
        )
        target_closure = compile_prerequisite_closure(unit_records, requested_unit_id)

    # The curriculum's own domain contract. The engine's metaschema constrains the
    # shape of this file; the file constrains the domain a unit's artifacts assert.
    declared_domain = manifest.get("domain") if isinstance(manifest, dict) else None
    manifest_schema = (
        declared_domain.get("manifest_schema") if isinstance(declared_domain, dict) else None
    )

    effective_run = {
        "mode": mode,
        "requested_unit_id": requested_unit_id,
        "manifest_schema": manifest_schema,
        "ordered_unit_ids": ordered_ids,
        "unit_records": unit_records,
        "target_closure": target_closure,
        "manifest_path": str(manifest_path),
        "manifest_digest": actual,
    }
    effective_run["denominator_id"] = canonical_digest(
        {
            "manifest_digest": actual,
            "mode": mode,
            "target_closure": target_closure,
        }
    )

    return {
        "effective_run": effective_run,
        "pending_guard": guard("D02_COMPILE_EFFECTIVE_RUN", "effective_run_compiled"),
    }


# --------------------------------------------------------------------------
# D03
# --------------------------------------------------------------------------


@deterministic_node("D03_PROVE_CAPABILITIES")
def D03_PROVE_CAPABILITIES(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Prove every required capability and authorization before any transmission."""

    envelope = _record(projection["invocation"], "invocation")
    recovery = projection["validated_recovery_envelope"]
    frozen_digest = projection["frozen_digest"]
    if recovery is not None:
        require(
            recovery.get("frozen_digest") == frozen_digest,
            "identity",
            "the validated recovery envelope does not carry the frozen digest",
        )

    effective_run = projection["effective_run"]
    require(
        bool(effective_run) or recovery is not None,
        "invalid_input",
        "capability proof requires either a fresh effective run or a validated recovery envelope",
    )

    registry = getattr(runtime_context, "transport_registry", None)
    require(registry is not None, "capability", "runtime context exposes no transport registry")

    # The probe is a bounded local capability check, never a curriculum model job.
    prober = getattr(registry, "prove_capability", None)
    require(callable(prober), "capability", "transport registry exposes no capability prober")

    receipts: list[dict[str, Any]] = []
    missing: list[str] = []
    unavailable_facts: list[dict[str, Any]] = []
    for capability in REQUIRED_CAPABILITIES:
        try:
            proof = prober(capability)
        except FileNotFoundError as error:
            missing.append(capability)
            proof = {"result": "MISSING", "detail": str(error)}
        proof_record = _record(proof, f"{capability} capability proof")
        result = proof_record.get("result")
        if result == "UNAVAILABLE_EXTERNAL_FACT":
            unavailable_facts.append({"capability": capability, "detail": proof_record})
        elif result != "PASS":
            missing.append(capability)
        receipt = {
            "kind": "capability_receipt",
            "capability": capability,
            "run_id": projection["run_id"],
            "frozen_digest": frozen_digest,
            "proof": proof_record,
        }
        receipt["key"] = canonical_digest(receipt)
        receipts.append(receipt)

    # Spec 7.1's five differentiated driver-capability proof classes (executable
    # identity, permitted auth mode, observable subscription-backed usability,
    # content-free operation, and the D03 tool/MCP-closure check), plus the
    # egress-boundary check, live behind one more transport-registry field rather
    # than a single ready flag: `driver_capability_proof` is computed once, before
    # this episode's first transmission, by the production CLI
    # (`runtime.run_curriculum._prove_driver_capabilities`) against every mandatory
    # driver in `MANDATORY_DRIVER_CLIS`, using only N20-owned `transport.py`/
    # `egress.py` functions. D03 never re-executes a CLI itself (spec 6.2: a node
    # body never calls a model transport). The production CLI (`run_curriculum.py`)
    # already refuses -- before this episode's first transmission -- to invoke the
    # graph at all once this proof reports not-ready, exactly closing Run 26's false-
    # ready defect at the one real entry point; here, this attribute is read
    # best-effort, the same optional-duck-typing treatment `observe_executable`
    # already gets a few lines below, so a registry double built for an unrelated
    # topology/plumbing test (never wired to a driver-capability proof at all) is not
    # forced to fabricate one. When a registry *does* expose the attribute, every
    # field for every mandatory driver is validated in full and any one unproven
    # field still fails this node closed -- optional presence, never optional rigor.
    driver_proof = getattr(registry, "driver_capability_proof", None)
    not_ready_drivers: list[str] = []
    if driver_proof is not None:
        driver_proof_record = _record(driver_proof, "driver capability proof")
        drivers_record = driver_proof_record.get("drivers")
        require(
            isinstance(drivers_record, dict) and set(drivers_record) >= set(MANDATORY_DRIVER_CLIS),
            "capability",
            "driver capability proof does not cover every mandatory driver",
            mandatory=list(MANDATORY_DRIVER_CLIS),
            observed=sorted(drivers_record) if isinstance(drivers_record, dict) else None,
        )
        for driver_name in MANDATORY_DRIVER_CLIS:
            driver_detail = _record(drivers_record[driver_name], f"{driver_name} driver capability")
            driver_fields = driver_detail.get("fields")
            require(
                isinstance(driver_fields, dict) and set(driver_fields) >= set(DRIVER_CAPABILITY_FIELDS),
                "capability",
                f"{driver_name} driver capability proof is missing a required proof field",
                required=list(DRIVER_CAPABILITY_FIELDS),
                observed=sorted(driver_fields) if isinstance(driver_fields, dict) else None,
            )
            if not driver_detail.get("ready"):
                not_ready_drivers.append(driver_name)
        driver_receipt = {
            "kind": "driver_capability_receipt",
            "capability": "driver_capability_proof",
            "run_id": projection["run_id"],
            "frozen_digest": frozen_digest,
            "proof": driver_proof_record,
        }
        driver_receipt["key"] = canonical_digest(driver_receipt)
        receipts.append(driver_receipt)
        if not driver_proof_record.get("ready") or not_ready_drivers:
            missing.append("driver_capability_proof")

    frozen_executables = {entry["name"]: entry for entry in projection["frozen_executable_identities"]}
    observer = getattr(registry, "observe_executable", None)
    identity_mismatches: list[dict[str, Any]] = []
    if callable(observer):
        for name, frozen_entry in sorted(frozen_executables.items()):
            observed = observer(name)
            observed_record = _record(observed, f"{name} executable identity")
            for field in ("path", "sha256"):
                expected = frozen_entry.get(field)
                if expected is None:
                    continue
                if observed_record.get(field) != expected:
                    identity_mismatches.append(
                        {
                            "executable": name,
                            "field": field,
                            "frozen": expected,
                            "observed": observed_record.get(field),
                        }
                    )
            receipt = {
                "kind": "executable_identity_receipt",
                "capability": "model_cli_identity",
                "executable": name,
                "run_id": projection["run_id"],
                "frozen": frozen_entry,
                "observed": observed_record,
            }
            receipt["key"] = canonical_digest(receipt)
            receipts.append(receipt)

    require(
        not identity_mismatches,
        "identity",
        "a frozen executable identity does not match the installed executable",
        mismatches=identity_mismatches,
    )

    authorizations = projection["external_authorizations"]
    require(
        bool(authorizations),
        "authorization",
        "no external-data authorization record covers this run",
    )
    for authorization in authorizations:
        record = _record(authorization, "authorization record")
        require(
            record.get("curriculum_digest") == frozen_digest,
            "authorization",
            "the authorization record does not cover this run's frozen inputs",
            authorized=record.get("curriculum_digest"),
            frozen=frozen_digest,
        )
        require(
            record.get("output_root") in (None, projection["output_root"]),
            "authorization",
            "the authorization record is scoped to a different output root",
        )

    require(
        not missing,
        "capability",
        "required capabilities are unavailable",
        missing=sorted(missing),
        not_ready_drivers=not_ready_drivers,
    )

    if unavailable_facts:
        require(
            len(unavailable_facts) == 1,
            "capability",
            "more than one capability reported an unavailable external fact",
            facts=unavailable_facts,
        )
        raise PrerequisitePause(
            "required_external_fact_unavailable",
            "a named required external fact is unavailable at capability proof",
            {"facts": unavailable_facts, "receipts": [r["key"] for r in receipts]},
        )

    _ = envelope  # the envelope is proven against frozen state, not consumed further
    return {
        "capability_receipts": receipts,
        "pending_guard": guard("D03_PROVE_CAPABILITIES", "capabilities_proven"),
    }


# --------------------------------------------------------------------------
# D04
# --------------------------------------------------------------------------


@deterministic_node("D04_INITIALIZE_OR_RESUME")
def D04_INITIALIZE_OR_RESUME(projection: dict[str, Any], runtime_context: Any) -> dict[str, Any]:
    """Open a fresh episode, or import a prior episode's proven state byte-identically."""

    bootstrap_kind = projection["bootstrap_kind"]
    require(
        bootstrap_kind in BOOTSTRAP_KINDS,
        "invalid_input",
        f"unknown bootstrap kind {bootstrap_kind!r}",
    )
    require(
        bool(projection["capability_receipts"]),
        "capability",
        "an episode cannot be initialized without capability proof receipts",
    )

    envelope = _record(projection["invocation"], "invocation")
    ordinal = envelope.get("episode_ordinal")
    require(
        isinstance(ordinal, int) and not isinstance(ordinal, bool) and ordinal >= 0,
        "invalid_input",
        "invocation must carry a non-negative integer episode ordinal",
    )
    run_id = _text(projection["run_id"], "run_id")

    if bootstrap_kind == "recover_orphan":
        thread_id = f"{run_id}:recover:{ordinal}"
    else:
        thread_id = f"{run_id}:episode:{ordinal:06d}"
    episode_id = canonical_digest({"run_id": run_id, "thread_id": thread_id})

    update: dict[str, Any] = {
        "episode_id": episode_id,
        "checkpoint_thread_id": thread_id,
        "checkpoint_namespace": "",
    }

    if bootstrap_kind == "fresh":
        require(
            projection["validated_recovery_envelope"] is None,
            "invalid_input",
            "a fresh episode must not carry a validated recovery envelope",
        )
        update["resume_from"] = None
        update["pending_guard"] = guard("D04_INITIALIZE_OR_RESUME", "fresh_initialized")
        return update

    recovery = projection["validated_recovery_envelope"]
    require(
        isinstance(recovery, dict),
        "invalid_input",
        "a resume episode requires D00R's validated recovery envelope",
    )
    require(
        recovery.get("run_id") == run_id,
        "identity",
        "the validated recovery envelope names a different run",
    )
    require(
        recovery.get("frozen_digest") == projection["frozen_digest"],
        "identity",
        "the validated recovery envelope carries a different frozen digest",
    )

    history = projection["terminal_history"]
    prior = history[-1] if history else None
    require(
        isinstance(prior, dict) and prior.get("kind") in RESUMABLE_TERMINAL_KINDS,
        "identity",
        "resume requires a legally resumable prior terminal in the history ledger",
        prior_kind=prior.get("kind") if isinstance(prior, dict) else None,
    )

    # Accepted bytes are the one thing a resume may never rewrite: the import
    # re-presents the recorded heads unchanged and lets `advance_head` and
    # `accept_once` reject anything that is not byte-identical.
    accepted = projection["accepted_unit_receipts"]
    for unit_id, receipt in sorted(accepted.items()):
        record = _record(receipt, f"accepted receipt for {unit_id}")
        require(
            isinstance(record.get("receipt_hash"), str),
            "integrity",
            f"accepted receipt for {unit_id!r} has no receipt hash",
        )

    resume_from = {
        "prior_terminal_kind": prior["kind"],
        "comparison_key": recovery.get("comparison_key"),
        "imported_head_keys": sorted(projection["artifact_heads"]),
        "imported_counter_keys": sorted(projection["attempt_counters"]),
        "accepted_unit_ids": sorted(accepted),
    }

    update.update(
        {
            "resume_from": resume_from,
            "artifact_heads": dict(projection["artifact_heads"]),
            "attempt_counters": dict(projection["attempt_counters"]),
            "cursor": dict(projection["cursor"]),
            "unit_status": dict(projection["unit_status"]),
            "pending_guard": guard("D04_INITIALIZE_OR_RESUME", "resume_imported"),
        }
    )
    return update


# --------------------------------------------------------------------------
# D92
# --------------------------------------------------------------------------

# A stored frontier naming any of these is a resume that would re-enter a model
# without passing the attempt counter; it is a system failure, not a retry.
_MODEL_NODE_PREFIX = "M"


@deterministic_node("D92_REENTER_VALIDATED_FRONTIER")
def D92_REENTER_VALIDATED_FRONTIER(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Validate the persisted resume frontier and name one deterministic destination."""

    frontier = projection["resume_frontier"]
    require(
        isinstance(frontier, dict) and bool(frontier),
        "invalid_input",
        "resume re-entry requires a persisted deterministic frontier",
    )
    destination = frontier.get("destination")
    require(
        isinstance(destination, str) and destination != "",
        "invalid_input",
        "the stored frontier names no destination node",
    )
    require(
        not re.fullmatch(rf"{_MODEL_NODE_PREFIX}\d+_[A-Z0-9_]+", destination),
        "invalid_input",
        f"stored frontier destination {destination!r} is a model node",
        destination=destination,
    )

    # An activation with no matching execution receipt is an attempt whose
    # outcome nobody observed; re-entering deterministically would silently
    # abandon it.
    executed = {
        receipt.get("activation_id")
        for receipt in projection["model_execution_receipts"]
        if isinstance(receipt, dict)
    }
    unaccounted = sorted(
        activation.get("activation_id")
        for activation in projection["activation_receipts"]
        if isinstance(activation, dict)
        and activation.get("activation_id") not in executed
        and activation.get("activation_id") is not None
    )

    heads = projection["artifact_heads"]
    stale: list[dict[str, Any]] = []
    for key, expected_hash in sorted((frontier.get("parent_hashes") or {}).items()):
        current = heads.get(key)
        current_hash = current.get("hash") if isinstance(current, dict) else None
        if current_hash != expected_hash:
            stale.append({"stream": key, "expected": expected_hash, "current": current_hash})
    require(
        not stale,
        "integrity",
        "the stored frontier names parents that are no longer current heads",
        stale=stale,
    )

    receipt = {
        "kind": "frontier_validation",
        "destination": destination,
        "unaccounted_activations": unaccounted,
        "validated_parent_streams": sorted((frontier.get("parent_hashes") or {})),
        "counter_keys": sorted(projection["attempt_counters"]),
    }
    receipt["key"] = canonical_digest(receipt)

    if unaccounted:
        return {
            "evidence_index_entries": [receipt],
            "pending_guard": guard(
                "D92_REENTER_VALIDATED_FRONTIER",
                "incomplete_model_activation",
                activations=unaccounted,
            ),
        }

    require(
        bool(projection["capability_receipts"]),
        "capability",
        "re-entry requires current capability proof receipts",
    )
    require(
        bool(projection["external_authorizations"]),
        "authorization",
        "re-entry requires a current external-data authorization record",
    )

    return {
        "evidence_index_entries": [receipt],
        "pending_guard": guard(
            "D92_REENTER_VALIDATED_FRONTIER", "deterministic_reentry", destination=destination
        ),
    }


# --------------------------------------------------------------------------
# D96
# --------------------------------------------------------------------------


@deterministic_node("D96_GRACEFUL_INTERRUPT_GATE")
def D96_GRACEFUL_INTERRUPT_GATE(
    projection: dict[str, Any], runtime_context: Any
) -> dict[str, Any]:
    """Record an interrupted-episode candidate and the frontier it can resume from.

    This node reaches no transport, retrieval, or renderer: it runs when the
    episode is already stopping, and any external call here could block or fail
    on the way out and lose the frontier it exists to preserve.
    """

    recovery = projection["validated_recovery_envelope"]
    token = getattr(runtime_context, "signal_token", None)
    signal_set = bool(token is not None and getattr(token, "is_set", lambda: False)())

    if recovery is not None:
        classification = "crashed_episode"
    elif signal_set:
        classification = "graceful_signal"
    else:
        raise SystemFailure(
            "invalid_input",
            "the interrupt gate ran with neither a graceful signal nor a recovery envelope",
        )

    checkpoints = projection["checkpoint_metadata"]
    evidence = projection["evidence_index_entries"]
    frontier = projection["resume_frontier"] or {}

    high_water = {
        "checkpoint_records": len(checkpoints),
        "evidence_records": len(evidence),
        "last_checkpoint_id": (
            checkpoints[-1].get("checkpoint_id") if checkpoints else None
        ),
    }

    resume_frontier = {
        "destination": frontier.get("destination"),
        "parent_hashes": {
            stream: head.get("hash")
            for stream, head in sorted(projection["artifact_heads"].items())
            if isinstance(head, dict)
        },
        "selected_unit_id": projection["selected_unit_id"],
        "attempt_counters": dict(projection["attempt_counters"]),
        "classification": classification,
    }

    candidate = {
        "kind": "INTERRUPTED",
        "classification": classification,
        "episode_id": projection["episode_id"],
        "run_id": projection["run_id"],
        "resume_frontier": resume_frontier,
        "high_water_marks": high_water,
        "heads": resume_frontier["parent_hashes"],
    }

    return {
        "terminal_candidate": candidate,
        "resume_frontier": resume_frontier,
        "pending_guard": guard("D96_GRACEFUL_INTERRUPT_GATE", "interrupted"),
    }
