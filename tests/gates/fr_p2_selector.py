"""Phase-2 gates — routing, the selector, and the three contracts they need.

**None of these claims execution of a selector: there is none.** Every gate here is
a static check over files. A `declaration` gate says a rule is *stated and
checkable*, never *enforced at runtime*; a `mapping` gate says an id is *owned*,
never *executed*.

Dependency order matters in this phase and is declared, not implied by ID.
``FR-P2-CONTRACT-VERSIONED`` and ``FR-P2-DEFERRED`` author what the other gates
read, so every gate that reads `decided_model`, `executed_model`, `action_kind`,
`decision_id` or an ``RT-`` id declares one of them as a dependency.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import common  # noqa: E402
import meta_prompt_source  # noqa: E402
from common import (  # noqa: E402
    Evidence,
    Fixture,
    GateFailure,
    REPO_ROOT,
    active_plan_path,
    gate_result,
    plan_section,
    read_named,
    rel,
)

FIXTURES = common.FIXTURES_DIR

META_PROMPT = meta_prompt_source.PROMPT
CHECKS = REPO_ROOT / "policy" / "checks.v1.yaml"
CONTROLLER = REPO_ROOT / "policy" / "controller.v1.yaml"
FAILURES = REPO_ROOT / "policy" / "failures.v1.yaml"
DEFERRED = REPO_ROOT / "policy" / "deferred.v1.yaml"
ROUTING_DIR = REPO_ROOT / "policy" / "routing"
MODEL_REGISTRY = ROUTING_DIR / "model_registry.v1.yaml"

DECISION_V1 = REPO_ROOT / "schemas" / "routing_decision.schema.v1.json"
DECISION_V2 = REPO_ROOT / "schemas" / "routing_decision.schema.v2.json"
LOG_V1 = REPO_ROOT / "schemas" / "execution_log.schema.v1.json"
LOG_V2 = REPO_ROOT / "schemas" / "execution_log.schema.v2.json"

V1_CONTRACTS = ["execution_log.schema.v1.json", "routing_decision.schema.v1.json"]

# The six entries FR-P2-BOUND (a) requires. Not a whitelist: the table legitimately
# carries other inputs, and a whitelist reading would delist them.
REQUIRED_AUTHORIZED = [
    "policy/routing/model_registry.v1.yaml",
    "policy/routing/task_taxonomy.v2.yaml",
    "policy/routing/routing_policy.v1.yaml",
    "policy/routing/quality_gates.v1.yaml",
    "schemas/routing_decision.schema.v2.json",
    "schemas/execution_log.schema.v2.json",
]

CLAIM_VOCABULARY = ("tree", "parse", "schema", "text", "mapping", "declaration", "execution")

RT_REFERENCE = re.compile(r"(?<![A-Za-z0-9])RT-[0-9]+")
SEL_REFERENCE = re.compile(r"(?<![A-Za-z0-9])SEL-[A-Z0-9\-]+")


# ---------------------------------------------------------------------------
# Prompt-section helpers. Every file composed here is a **named** file, opened by
# name and never globbed (rule 7): the prompt names its section assets in its own
# table, so the set is read from the contract rather than from the directory.


def contract_text(ev: Evidence | None = None) -> str:
    """The composed contract — the prompt plus its section assets.

    Since v6, `## Routing`, `## Inputs` and `## Proving it` live in assets the
    prompt binds. Slicing the short file alone would find none of them and report
    every section absent, so the subject of these gates is the composition.
    ``tests/meta_prompt_source.py`` owns how it is formed.
    """
    return meta_prompt_source.compose(ev.text_of if ev is not None else None)


def _slice(text: str, start: str, stop: str) -> str:
    begin = re.search(start, text, re.M)
    if not begin:
        return ""
    rest = text[begin.end():]
    end = re.search(stop, rest, re.M)
    return rest[: end.start()] if end else rest


def authorized_input_rows(prompt_text: str) -> list[str]:
    """The backticked entries of the authorized-input table."""
    section = _slice(prompt_text, r"^## Inputs\s*$", r"^###? ")
    return [cell for row in section.splitlines() if row.startswith("|")
            for cell in re.findall(r"`([^`]+)`", row.split("|")[1] if len(row.split("|")) > 1 else "")]


def retained_contracts_section(prompt_text: str) -> str:
    return _slice(prompt_text, r"^### Retained contracts\s*$", r"^## ")


def routing_section(prompt_text: str) -> str:
    return _slice(prompt_text, r"^## Routing\s*$", r"^## ")


def release_table_rows(prompt_text: str) -> list[list[str]]:
    section = _slice(prompt_text, r"^## Proving it\s*$", r"^## ")
    rows = []
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0] not in ("#", "") and not set(cells[0]) <= {"-"}:
            rows.append(cells)
    return rows


# ---------------------------------------------------------------------------
# FR-P2-CONTRACT-VERSIONED


def check_contract_versioned(ev: Evidence):
    problems: list[str] = []

    # (a) the decision contract
    for path in (DECISION_V2, LOG_V2):
        if not ev.exists(path):
            problems.append(f"missing-contract:{rel(path)}")
    if problems:
        return gate_result(False, "FR-P2-CONTRACT-VERSIONED FAIL — " + "; ".join(problems))

    for path in (DECISION_V2, LOG_V2):
        error = ev.schema_is_valid(path)
        if error:
            problems.append(f"invalid-schema:{rel(path)} {error}")

    d1 = ev.read_for_resolution(DECISION_V1)
    d2 = ev.read_for_resolution(DECISION_V2)
    expected = [f for f in d1["required"] if f != "selected_model"] + ["decided_model", "executed_model"]
    ev.resolve(
        "the nine required fields of routing_decision v1",
        rel(DECISION_V1),
        f"the ten required fields of {rel(DECISION_V2)}",
    )
    if set(d2["required"]) != set(expected) or len(d2["required"]) != 10:
        problems.append(
            f"decision-required-mismatch: v2 requires {sorted(d2['required'])}, expected {sorted(expected)}"
        )

    # (b) the log contract
    l1 = ev.read_for_resolution(LOG_V1)
    l2 = ev.read_for_resolution(LOG_V2)
    act1 = set(l1["$defs"]["act"]["required"])
    act2 = set(l2["$defs"]["act"]["required"])
    if act2 != act1 | {"action_kind"}:
        problems.append(
            f"act-required-mismatch: v2 requires {sorted(act2)}, expected {sorted(act1 | {'action_kind'})}"
        )
    kind = l2["$defs"]["act"]["properties"].get("action_kind", {})
    if "model_call" not in kind.get("enum", []):
        problems.append("action_kind is not a typed discriminator whose enum includes model_call")
    if "decision_id" not in l2["$defs"]["act"]["properties"]:
        problems.append("decision_id is not a property of the v2 act record")

    # (c) the conditional keys on the discriminator, never on free-text action
    conditionals = [
        clause for clause in l2["$defs"]["act"].get("allOf", [])
        if "decision_id" in clause.get("then", {}).get("required", [])
    ]
    if len(conditionals) != 1:
        problems.append("decision_id is not required by exactly one conditional clause")
    else:
        condition = conditionals[0].get("if", {}).get("properties", {})
        if condition.get("action_kind", {}).get("const") != "model_call":
            problems.append("the decision_id condition does not key on action_kind: model_call")
        if "action" in condition:
            problems.append("the decision_id condition keys on free-text action — a record could reword")

    # (d) both v1 files remain in schemas/, byte-unchanged from HEAD~
    for path in (LOG_V1, DECISION_V1):
        if not ev.exists(path):
            problems.append(f"retained-contract-missing:{rel(path)}")
            continue
        if ev.exists(REPO_ROOT / "schemas" / "deprecated" / path.name):
            problems.append(f"retained-contract-deprecated:{path.name}")
        error = v1_mutation(path, ev)
        if error:
            problems.append(error)

    # (e) shown by the positive fixtures below, and asserted here too
    # (f) every live manifest reference names v2
    problems += live_v1_references(ev)

    line = f"FR-P2-CONTRACT-VERSIONED {'PASS' if not problems else 'FAIL'} (v2 authored, v1 retained unchanged)"

    mutated = FIXTURES / "contract_v1_edited_in_place.reject.json"
    fixtures = [
        Fixture(
            name=rel(mutated),
            kind="reject",
            expected_error="v1-contract-mutated",
            detector=lambda: v1_mutation(mutated, None, compare_to="schemas/execution_log.schema.v1.json"),
        ),
        Fixture(
            name=rel(FIXTURES / "decision_v2_missing_executed.reject.json"),
            kind="reject",
            expected_error="'executed_model' is a required property",
            detector=lambda: common._validate_obj(
                common._deserialize(FIXTURES / "decision_v2_missing_executed.reject.json"),
                common._deserialize(DECISION_V2),
            ),
        ),
        Fixture(
            name=rel(FIXTURES / "act_model_call_wordplay.reject.json"),
            kind="reject",
            expected_error="'decision_id' is a required property",
            detector=lambda: common._validate_obj(
                common._deserialize(FIXTURES / "act_model_call_wordplay.reject.json"),
                _act_schema(LOG_V2),
            ),
        ),
        Fixture(
            name=rel(FIXTURES / "act_v1_shaped.accept.json"),
            kind="accept",
            detector=lambda: common._validate_obj(
                common._deserialize(FIXTURES / "act_v1_shaped.accept.json"), _act_schema(LOG_V1)
            ),
        ),
        Fixture(
            name=rel(FIXTURES / "decision_v2_valid.accept.json"),
            kind="accept",
            detector=lambda: common._validate_obj(
                common._deserialize(FIXTURES / "decision_v2_valid.accept.json"),
                common._deserialize(DECISION_V2),
            ),
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


def _act_schema(path: Path) -> dict:
    schema = common._deserialize(path)
    return {**schema["$defs"]["act"], "$defs": schema["$defs"]}


def v1_mutation(path: Path, ev: Evidence | None, compare_to: str | None = None) -> str | None:
    """A retained contract must be byte-identical to its state in the parent commit."""
    tracked = compare_to or rel(path)
    args = ["git", "show", f"HEAD~:{tracked}"]
    proc = ev.run(args) if ev is not None else __import__("subprocess").run(
        args, cwd=str(REPO_ROOT), capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        return f"v1-contract-unreadable:{tracked} {proc.stderr.strip()}"
    if proc.stdout != read_named(path):
        return f"v1-contract-mutated:{rel(path)} differs from HEAD~"
    return None


def live_v1_references(ev: Evidence | None = None) -> list[str]:
    """(f) The only surviving v1 references are the files themselves and the
    retained-contracts table; a live manifest reference must name v2."""
    problems = []
    retained = retained_contracts_section(
        contract_text(ev)
    )
    for path in common.production_files():
        if path.name in V1_CONTRACTS:
            continue  # the file itself
        try:
            text = ev.text_of(path) if ev is not None else read_named(path)
        except (OSError, UnicodeDecodeError):
            continue
        for name in V1_CONTRACTS:
            for line in text.splitlines():
                if name in line and line.strip() not in retained:
                    problems.append(f"live-v1-reference:{name} at {rel(path)}")
                    break
    return problems


# ---------------------------------------------------------------------------
# FR-P2-DEFERRED


def deferred_shape_violations(doc) -> list[str]:
    problems = []
    for entry in (doc or {}).get("deferred", []):
        rt = entry.get("id", "")
        if not re.fullmatch(r"RT-[0-9]+", rt):
            problems.append(f"deferred-id-malformed:{rt!r}")
            continue
        for field in ("obligation", "acceptance_criterion", "blocked_by"):
            if not entry.get(field):
                problems.append(f"deferred-field-missing:{rt}.{field}")
        if "promoted_id" in entry and "promotes_gate" not in entry:
            problems.append(f"deferred-promoted-without-gate:{rt}")
    return problems


def plan_deferred_table() -> dict[str, dict]:
    """Section 12's table, read from the active plan by name (rule 7)."""
    section = plan_section(read_named(active_plan_path()), 12)
    table = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            continue
        rt = cells[0].strip("*` ")
        if not re.fullmatch(r"RT-[0-9]+", rt):
            continue
        table[rt] = {
            "promotes_gate": cells[4].strip("*` ") if cells[4].strip("*` ") != "—" else "",
            "promoted_id": cells[5].strip("*` ") if cells[5].strip("*` ") != "—" else "",
        }
    return table


def dangling_rt_references(defined: set[str], scan_files) -> list[str]:
    problems = []
    for path in scan_files:
        try:
            text = read_named(path)
        except (OSError, UnicodeDecodeError):
            continue
        for found in sorted(set(RT_REFERENCE.findall(text))):
            if found not in defined:
                problems.append(f"deferred-id-unresolved:{found} at {rel(path)}")
    return problems


def check_deferred(ev: Evidence):
    doc = ev.parse(DEFERRED)
    problems = deferred_shape_violations(doc)
    defined = {e["id"] for e in doc.get("deferred", []) if "id" in e}

    ev.text_of(active_plan_path())
    mirror = plan_deferred_table()
    for rt in sorted(defined | set(mirror)):
        ev.resolve(rt, rel(DEFERRED), f"{rel(active_plan_path())} section 12's table")
    if defined != set(mirror):
        problems.append(
            f"deferred-mirror-mismatch: manifest {sorted(defined)} vs plan {sorted(mirror)}"
        )
    for entry in doc.get("deferred", []):
        row = mirror.get(entry.get("id", ""))
        if not row:
            continue
        if entry.get("promotes_gate", "") != row["promotes_gate"]:
            problems.append(f"deferred-mirror-mismatch:{entry['id']}.promotes_gate")
        if entry.get("promoted_id", "") != row["promoted_id"]:
            problems.append(f"deferred-mirror-mismatch:{entry['id']}.promoted_id")

    registry = ev.import_gate_module("registry")
    gate_ids = {g["id"] for g in registry.GATES}
    for entry in doc.get("deferred", []):
        gate = entry.get("promotes_gate")
        if gate and gate not in gate_ids:
            problems.append(f"promotes-gate-unresolved:{entry.get('id')} → {gate}")
        # promoted_id names a gate that does not exist yet and is never resolved.

    problems += dangling_rt_references(defined, common.production_files())

    mirrored = len(defined & set(mirror))
    dangling = sum(1 for p in problems if p.startswith("deferred-id-unresolved"))
    line = (
        f"FR-P2-DEFERRED {'PASS' if not problems else 'FAIL'} "
        f"({len(defined)} ids, {mirrored} mirrored, {dangling} dangling)"
    )

    reject = FIXTURES / "deferred_reference_dangling.reject.yaml"
    accept = FIXTURES / "deferred_no_promoted_id.accept.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="deferred-id-unresolved",
            detector=lambda: (dangling_rt_references(defined, [reject]) or [None])[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (
                deferred_shape_violations(common._deserialize(accept)) or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P2-BOUND


def bound_violations(prompt_text: str) -> list[str]:
    problems = []
    authorized = authorized_input_rows(prompt_text)
    for required in REQUIRED_AUTHORIZED:
        if not any(required in entry for entry in authorized):
            problems.append(f"unbound-input:{Path(required).name}")
    for name in V1_CONTRACTS:
        if any(name in entry for entry in authorized):
            problems.append(f"retired-version-authorized:{name}")
    retained = retained_contracts_section(prompt_text)
    for name in V1_CONTRACTS:
        if name not in retained:
            problems.append(f"retained-contract-untabled:{name}")
    if not re.search(r"already accepted|accepted under", retained, re.I):
        problems.append("retained-contract-untabled: the table does not restrict them to accepted work")
    if "RT-6" not in retained:
        problems.append("retained-contract-untabled: the table does not cite RT-6")
    return problems


def check_bound(ev: Evidence):
    text = contract_text(ev)
    for required in REQUIRED_AUTHORIZED:
        ev.resolve(required, "the authorized-input list section 9 fixes",
                   "a row of the composed contract's input table")
    problems = bound_violations(text)
    line = (
        f"FR-P2-BOUND {'PASS' if not problems else 'FAIL'} "
        f"({len(REQUIRED_AUTHORIZED)} required inputs bound, 2 contracts retained)"
    )
    fixtures = [
        Fixture(
            name=rel(FIXTURES / "prompt_missing_routing_input.reject.md"),
            kind="reject",
            expected_error="unbound-input:model_registry.v1.yaml",
            detector=lambda: (
                bound_violations(read_named(FIXTURES / "prompt_missing_routing_input.reject.md")) or [None]
            )[0],
        ),
        Fixture(
            name=rel(FIXTURES / "prompt_authorizes_v1_contract.reject.md"),
            kind="reject",
            expected_error="retired-version-authorized",
            detector=lambda: (
                bound_violations(read_named(FIXTURES / "prompt_authorizes_v1_contract.reject.md")) or [None]
            )[0],
        ),
        Fixture(
            name=rel(FIXTURES / "prompt_extra_authorized_input.accept.md"),
            kind="accept",
            detector=lambda: (
                bound_violations(read_named(FIXTURES / "prompt_extra_authorized_input.accept.md")) or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P2-NOVALUES


def routing_terms() -> tuple[dict[str, str], dict[str, dict]]:
    """Every model id, reasoning level and candidate-pool value the routing
    manifests own, and every declared prose_pattern, read from the manifests and
    never hard-coded here."""
    terms: dict[str, str] = {}
    patterns: dict[str, dict] = {}
    for path in sorted(ROUTING_DIR.glob("*.yaml")):
        doc = common._deserialize(path) or {}
        for name in (doc.get("models") or {}):
            terms[name] = "model_id"
        for spec in (doc.get("models") or {}).values():
            for effort in spec.get("reasoning_efforts", []):
                terms.setdefault(str(effort), "reasoning_effort")
        for rule in (doc.get("hard_rules") or {}).values():
            for name in rule.get("allowed_models", []):
                terms.setdefault(str(name), "candidate_pool")
            if "minimum_reasoning_effort" in rule:
                terms.setdefault(str(rule["minimum_reasoning_effort"]), "reasoning_effort")
        patterns.update(doc.get("prose_patterns") or {})
    return terms, patterns


def no_values_violations(prompt_text: str, terms: dict[str, str], patterns: dict[str, dict]) -> list[str]:
    problems = []
    for term in sorted(terms):
        spec = patterns.get(term)
        if not spec or not spec.get("prose_pattern"):
            problems.append(f"term-without-prose-pattern:{term}")
            continue
        if re.search(spec["prose_pattern"], prompt_text):
            problems.append(f"duplicated-value:{term}")
    return problems


def check_no_values(ev: Evidence):
    terms, patterns = routing_terms()
    for term in sorted(terms):
        ev.resolve(term, "policy/routing/*.yaml", "the prose_pattern the owning manifest declares")
    text = contract_text(ev)
    problems = no_values_violations(text, terms, patterns)
    line = (
        f"FR-P2-NOVALUES {'PASS' if not problems else 'FAIL'} "
        f"({len(terms)} terms, {len(patterns)} patterns, 0 inlined)"
    )
    fixtures = [
        Fixture(
            name=rel(FIXTURES / "prompt_inlines_model_id.reject.md"),
            kind="reject",
            expected_error="duplicated-value",
            detector=lambda: (
                no_values_violations(
                    read_named(FIXTURES / "prompt_inlines_model_id.reject.md"), terms, patterns
                ) or [None]
            )[0],
        ),
        Fixture(
            name=rel(FIXTURES / "prompt_incidental_effort_word.accept.md"),
            kind="accept",
            detector=lambda: (
                no_values_violations(
                    read_named(FIXTURES / "prompt_incidental_effort_word.accept.md"), terms, patterns
                ) or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P2-SEL-MAPPED


def sel_violations(checks_doc, gate_ids: set[str], deferred_ids: set[str],
                   ev: Evidence | None = None) -> tuple[list[str], list[str]]:
    """Each SEL-* id: an owner file that exists and names it, and a verification
    method from rule 6's vocabulary. Returns (problems, mapped_not_executed)."""
    problems, mapped = [], []
    for entry in (checks_doc or {}).get("selector", []):
        cid = entry.get("id", "")
        owner = entry.get("owner")
        if not owner:
            problems.append(f"advertised-without-owner:{cid}")
            continue
        owner_path = REPO_ROOT / owner
        present = ev.exists(owner_path) if ev is not None else owner_path.exists()
        if not present:
            problems.append(f"advertised-without-owner:{cid} — {owner} does not exist")
            continue
        owner_text = ev.text_of(owner_path) if ev is not None else read_named(owner_path)
        if cid not in owner_text:
            problems.append(f"advertised-without-owner:{cid} — {owner} does not name it")
        method = entry.get("method", "")
        if method not in CLAIM_VOCABULARY:
            problems.append(f"method-not-in-vocabulary:{cid} → {method!r}")
            continue
        if ev is not None:
            ev.resolve(cid, rel(CHECKS), f"{owner} and the artifact or gate that verifies it")
        if method in ("schema", "declaration"):
            artifact = entry.get("artifact")
            artifact_path = REPO_ROOT / artifact if artifact else None
            exists = (
                (ev.exists(artifact_path) if ev is not None else artifact_path.exists())
                if artifact_path else False
            )
            if not exists:
                problems.append(f"advertised-without-owner:{cid} — artifact {artifact!r} does not exist")
            if entry.get("verified_by") not in gate_ids:
                problems.append(f"advertised-without-owner:{cid} — no gate exercises it")
        elif method == "execution":
            rt = entry.get("deferred", "")
            if rt not in deferred_ids:
                problems.append(f"advertised-without-owner:{cid} — no resolving RT- reference")
            else:
                mapped.append(f"{cid} MAPPED, NOT EXECUTED ({rt})")
    return problems, mapped


def check_sel_mapped(ev: Evidence):
    checks_doc = ev.read_for_resolution(CHECKS)
    registry = ev.import_gate_module("registry")
    gate_ids = {g["id"] for g in registry.GATES}
    deferred_ids = {e["id"] for e in (ev.read_for_resolution(DEFERRED) or {}).get("deferred", [])}
    problems, mapped = sel_violations(checks_doc, gate_ids, deferred_ids, ev)

    # Reverse direction: an id stated anywhere in production but absent from the
    # manifest is as invisible as an id with no owner.
    declared = {e.get("id") for e in (checks_doc or {}).get("selector", [])}
    for path in common.production_files():
        if path == CHECKS:
            continue
        try:
            text = ev.text_of(path)
        except (OSError, UnicodeDecodeError):
            continue
        for found in sorted(set(SEL_REFERENCE.findall(text))):
            if found not in declared:
                problems.append(f"owner-without-id:{found} stated in {rel(path)}")

    line = (
        f"FR-P2-SEL-MAPPED {'PASS' if not problems else 'FAIL'} "
        f"({len(declared)} SEL ids, {len(mapped)} MAPPED, NOT EXECUTED: {'; '.join(mapped) or 'none'})"
    )
    reject = FIXTURES / "check_id_without_owner.reject.yaml"
    accept = FIXTURES / "sel_id_mapped_not_executed.accept.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="advertised-without-owner",
            detector=lambda: (
                sel_violations(common._deserialize(reject), gate_ids, deferred_ids)[0] or [None]
            )[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (
                sel_violations(common._deserialize(accept), gate_ids, deferred_ids)[0] or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P2-DECISION-VALID


def decided_model_resolves(record, registry_models: set[str]) -> str | None:
    model = record.get("decided_model")
    if model not in registry_models:
        return f"model-not-in-registry:{model!r}"
    return None


def check_decision(ev: Evidence):
    models = set((ev.read_for_resolution(MODEL_REGISTRY).get("models") or {}))
    wellformed = FIXTURES / "decision_wellformed.accept.json"
    problems = []
    error = ev.validate(wellformed, DECISION_V2)
    if error:
        problems.append(f"{rel(wellformed)}: {error}")
    ev.resolve("decided_model", rel(wellformed), rel(MODEL_REGISTRY) + " models")
    error = decided_model_resolves(common._deserialize(wellformed), models)
    if error:
        problems.append(f"{rel(wellformed)}: {error}")

    line = f"FR-P2-DECISION-VALID {'PASS' if not problems else 'FAIL'} (10 required fields, decided_model resolved)"
    missing = FIXTURES / "decision_missing_effort.reject.json"
    unknown = FIXTURES / "decision_model_not_in_registry.reject.json"
    fixtures = [
        Fixture(
            name=rel(missing),
            kind="reject",
            expected_error="'reasoning_effort' is a required property",
            detector=lambda: common._validate_obj(
                common._deserialize(missing), common._deserialize(DECISION_V2)
            ),
        ),
        Fixture(
            name=rel(unknown),
            kind="reject",
            expected_error="model-not-in-registry",
            detector=lambda: (
                common._validate_obj(common._deserialize(unknown), common._deserialize(DECISION_V2))
                or decided_model_resolves(common._deserialize(unknown), models)
            ),
        ),
        Fixture(
            name=rel(wellformed),
            kind="accept",
            detector=lambda: (
                common._validate_obj(common._deserialize(wellformed), common._deserialize(DECISION_V2))
                or decided_model_resolves(common._deserialize(wellformed), models)
            ),
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P2-BYPASS-DECLARED


def executed_differs(record) -> str | None:
    """(c) The comparison JSON Schema cannot express, performed here."""
    if record.get("decided_model") != record.get("executed_model"):
        return (
            f"executed-differs-from-decided:{record.get('decided_model')!r} decided, "
            f"{record.get('executed_model')!r} executed"
        )
    return None


def check_bypass_declared(ev: Evidence):
    ev.declaration()
    problems = []

    # (a) stated
    prompt = routing_section(contract_text(ev))
    if not re.search(r"--model[^.\n]*may not bypass the selector", prompt):
        problems.append("the § Routing section does not state that --model may not bypass the selector")
    controller = ev.text_of(CONTROLLER)
    if not re.search(r"may not bypass the selector", controller):
        problems.append("policy/controller.v1.yaml does not state the prohibition")
    if "SEL-NO-MODEL-BYPASS" not in ev.text_of(CHECKS):
        problems.append("SEL-NO-MODEL-BYPASS is not a check id in policy/checks.v1.yaml")

    # (b) representable
    for field in ("decided_model", "executed_model"):
        record = {k: v for k, v in common._deserialize(FIXTURES / "model_matches_decision.accept.json").items()
                  if k != field and not k.startswith("_")}
        if not ev.validate_obj(record, DECISION_V2):
            problems.append(f"routing_decision.schema.v2.json accepts a record without {field}")

    # (c) compared
    error = executed_differs(common._deserialize(FIXTURES / "model_matches_decision.accept.json"))
    if error:
        problems.append(f"the comparison rejects a conforming record: {error}")

    line = (
        f"FR-P2-BYPASS-DECLARED {'PASS' if not problems else 'FAIL'} "
        "(stated in prose, representable in the record, compared in gate code)"
    )
    bypass = FIXTURES / "model_override_bypass.reject.json"
    matches = FIXTURES / "model_matches_decision.accept.json"
    fixtures = [
        Fixture(
            name=rel(bypass),
            kind="reject",
            expected_error="executed-differs-from-decided",
            detector=lambda: (
                common._validate_obj(common._deserialize(bypass), common._deserialize(DECISION_V2))
                or executed_differs(common._deserialize(bypass))
            ),
        ),
        Fixture(
            name=rel(matches),
            kind="accept",
            detector=lambda: (
                common._validate_obj(common._deserialize(matches), common._deserialize(DECISION_V2))
                or executed_differs(common._deserialize(matches))
            ),
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P2-UNRECORDED-DECLARED


def check_unrecorded_declared(ev: Evidence):
    ev.declaration()
    problems = []

    # (a) a failure id whose outcome is META_SYSTEM_FAILURE, matched by its own
    #     declared prose_pattern rather than by prose the gate interprets.
    failures = common._deserialize(FAILURES)
    entries = [
        e for e in (failures.get("runtime_obligations") or [])
        if e.get("outcome") == "META_SYSTEM_FAILURE"
    ]
    if not entries:
        problems.append("policy/failures.v1.yaml carries no id whose outcome is META_SYSTEM_FAILURE")
        return gate_result(False, "FR-P2-UNRECORDED-DECLARED FAIL — " + "; ".join(problems))
    entry = entries[0]
    pattern = entry.get("prose_pattern")
    if not pattern:
        problems.append(f"condition-without-prose-pattern:{entry.get('id')}")
    elif not re.search(pattern, entry.get("condition", "")):
        problems.append(f"prose-pattern-does-not-match-condition:{entry.get('id')}")

    # (b) the controller maps that condition to that terminal state, and the meta
    #     prompt states the obligation. Resolving one manifest's condition id to
    #     another manifest's state is what `mapping` names.
    controller = ev.read_for_resolution(CONTROLLER)
    mapped = [
        c for c in (controller.get("terminal_conditions") or [])
        if c.get("condition_id") == entry.get("id")
    ]
    ev.resolve(
        str(entry.get("id")),
        rel(FAILURES) + " runtime_obligations",
        rel(CONTROLLER) + " terminal_conditions",
    )
    if not mapped:
        problems.append(f"controller-does-not-map:{entry.get('id')}")
    elif mapped[0].get("terminal_state") != "META_SYSTEM_FAILURE":
        problems.append(f"controller-maps-wrong-state:{entry.get('id')} → {mapped[0].get('terminal_state')}")
    if pattern and not re.search(pattern, contract_text(ev)):
        problems.append("the meta prompt does not state the obligation the failure entry declares")

    # (c) representable, and not over-broad
    call = FIXTURES / "call_without_decision.reject.json"
    write = FIXTURES / "act_file_write_no_decision.accept.json"
    if not ev.validate(call, LOG_V2):
        problems.append("execution_log.schema.v2.json accepts a model call with no decision_id")

    line = (
        f"FR-P2-UNRECORDED-DECLARED {'PASS' if not problems else 'FAIL'} "
        f"({entry.get('id')} → META_SYSTEM_FAILURE, representable, RT-4 for termination)"
    )
    fixtures = [
        Fixture(
            name=rel(call),
            kind="reject",
            expected_error="'decision_id' is a required property",
            detector=lambda: common._validate_obj(common._deserialize(call), _act_schema(LOG_V2)),
        ),
        Fixture(
            name=rel(write),
            kind="accept",
            detector=lambda: common._validate_obj(common._deserialize(write), _act_schema(LOG_V2)),
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P2-GATEITEMS


def _check_ids(checks_doc) -> set[str]:
    ids = set()
    for value in (checks_doc or {}).values():
        if isinstance(value, list):
            ids.update(e["id"] for e in value if isinstance(e, dict) and "id" in e)
    return ids


RELEASE_STAGES = {"logger", "static", "deterministic", "golden", "live-capability"}


def _staged_ids(checks_doc) -> set[str]:
    ids = set()
    for value in (checks_doc or {}).values():
        if isinstance(value, list):
            for entry in value:
                if isinstance(entry, dict) and entry.get("stage") in RELEASE_STAGES:
                    ids.add(entry["id"])
    return ids


def gate_item_violations(prompt_text: str, checks_doc) -> list[str]:
    """Both directions: every advertised gate item maps to a check id, and every
    check id the release table is responsible for appears in that table."""
    ids = _check_ids(checks_doc)
    problems, covered = [], set()
    for row in release_table_rows(prompt_text):
        gate_item, globs = row[1], row[2]
        patterns = re.findall(r"`([^`]+)`", globs)
        if not patterns:
            continue  # a row that advertises no check id claims no coverage
        for pattern in patterns:
            regex = re.compile("^" + re.escape(pattern).replace(r"\*", ".*") + "$")
            matched = {cid for cid in ids if regex.match(cid)}
            if not matched:
                problems.append(f"gate-item-unbacked:{gate_item.strip('*')} advertises {pattern}")
            covered |= matched
    for cid in sorted(_staged_ids(checks_doc) - covered):
        problems.append(f"check-id-unadvertised:{cid}")
    return problems


def check_gate_items(ev: Evidence):
    checks_doc = ev.read_for_resolution(CHECKS)
    text = contract_text(ev)
    for row in release_table_rows(text):
        ev.resolve(row[1].strip("*"), "the composed contract's release table",
                   f"the check ids in {rel(CHECKS)}")
    problems = gate_item_violations(text, checks_doc)
    line = (
        f"FR-P2-GATEITEMS {'PASS' if not problems else 'FAIL'} "
        f"({len(release_table_rows(text))} gate items, {len(_staged_ids(checks_doc))} staged check ids)"
    )
    reject = FIXTURES / "gate_item_without_check.reject.md"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="gate-item-unbacked",
            detector=lambda: (gate_item_violations(read_named(reject), checks_doc) or [None])[0],
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECK_TABLE = {
    "contract-versioned": check_contract_versioned,
    "deferred": check_deferred,
    "bound": check_bound,
    "no-values": check_no_values,
    "sel-mapped": check_sel_mapped,
    "decision": check_decision,
    "bypass-declared": check_bypass_declared,
    "unrecorded-declared": check_unrecorded_declared,
    "gate-items": check_gate_items,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, choices=sorted(CHECK_TABLE))
    args = parser.parse_args()
    ev = Evidence(gate_id=args.check)
    outcome = CHECK_TABLE[args.check](ev)
    print(outcome.detail)
    for record in outcome.fixtures:
        print(f"  fixture {record['fixture']}: {record['outcome']} ({record['matched_error']})")
    print(f"  mechanisms: {ev.claim() or '-'}")
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
