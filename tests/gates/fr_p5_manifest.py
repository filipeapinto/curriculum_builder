"""Phase-5 gate — a curriculum constrains its own manifest surfaces, or it does not run.

`G5` took `kit_power_profile` and `visual_system` out of the engine's manifest contract,
because they are one subject's words in a contract that must hold for any subject. That
move is only half done when the constraint is removed. `schemas/curriculum.schema.v5.json`
as first written let `domain.config` be **any nonempty object** and `mode` and
`domain_state` be **any string** — v4 validated all four, v5 validated none of them, and
the manifest got looser rather than more general. Relaxing an acceptance criterion to make
a repository pass is the one move this plan forbids.

So the shape lives somewhere else now, and the engine's job is to require that somewhere
exists:

    the engine never knows what a curriculum's configuration contains or what its
    hazard classes are called. It knows the curriculum must **say**, in a contract
    of its own, and that the saying must actually constrain.

Three things are checked, in that order:

(a) every curriculum declares `domain.manifest_schema`, a real JSON Schema **under its own
    directory** — an engine-held one is `G5` again wearing a different name;
(b) that contract validates against `schemas/manifest_domain.metaschema.v1.json`: a closed
    `$defs/config` with at least one required key, and a closed `$defs/core_activity`
    requiring and *enumerating* `mode` and `domain_state`. The metaschema names no subject
    term; it requires the shape of constraining and reads none of the values;
(c) the manifest's own content is then validated against that contract — `domain.config`
    against `$defs/config`, and every lab's `core_activity` against `$defs/core_activity`.

A curriculum whose contract accepts anything fails (b) and never reaches (c). That is the
difference between moving a constraint and dropping one.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import Evidence, Fixture, REPO_ROOT, gate_result, rel  # noqa: E402
from fr_p5_verifier import curriculum_manifests  # noqa: E402

FIXTURES = common.FIXTURES_DIR

# What the engine requires of a curriculum-supplied manifest contract. Engine-owned and
# subject-free: it constrains the constraining, never the subject.
METASCHEMA = REPO_ROOT / "schemas" / "manifest_domain.metaschema.v1.json"

CONFIG_REF = "#/$defs/config"
ACTIVITY_REF = "#/$defs/core_activity"


def _at(contract: dict, ref: str) -> dict:
    """The contract, entered at one of its two declared definitions.

    `$defs` travels with the schema so that a definition may reference its siblings;
    only the entry point changes.
    """
    entered = dict(contract)
    entered.pop("$ref", None)
    entered["$ref"] = ref
    return entered


def contract_violations(contract, label: str) -> list[str]:
    """What is wrong with the contract itself, before any content is validated."""
    if not isinstance(contract, dict):
        return [f"domain-unconstrained:{label} is not a JSON Schema object"]
    error = common._validate_obj(contract, common._deserialize(METASCHEMA))
    if error:
        return [
            f"domain-unconstrained:{label} does not constrain what the engine stopped "
            f"constraining — {error}"
        ]
    return []


def content_violations(doc, contract, label: str) -> list[str]:
    """What is wrong with the manifest, read against the contract it declared."""
    problems: list[str] = []
    domain = (doc or {}).get("domain") or {}
    error = common._validate_obj(domain.get("config"), _at(contract, CONFIG_REF))
    if error:
        problems.append(f"domain-config-invalid:{label} domain.config — {error}")
    activity = _at(contract, ACTIVITY_REF)
    for lab in (doc or {}).get("labs") or []:
        error = common._validate_obj(lab.get("core_activity"), activity)
        if error:
            problems.append(
                f"core-activity-invalid:{label} {lab.get('id')} core_activity — {error}"
            )
    return problems


def declared_contract(doc, label: str) -> tuple[Path | None, list[str]]:
    """Resolve `domain.manifest_schema` to a file under the curriculum's own directory."""
    domain = (doc or {}).get("domain") or {}
    declared = domain.get("manifest_schema")
    if not declared:
        return None, [
            f"manifest-schema-undeclared:{label} declares no manifest_schema, so nothing "
            "states what its configuration or its hazard classes may be"
        ]
    path = REPO_ROOT / declared
    if not path.is_file():
        return None, [
            f"manifest-schema-undeclared:{label} names manifest_schema {declared!r}, "
            "which is not a file"
        ]
    owner = f"curricula/{Path(label).parent.name}/"
    if not str(declared).startswith(owner):
        return None, [
            f"manifest-schema-undeclared:{label} names manifest_schema {declared!r}, "
            f"which is not under its own directory {owner} — an engine-held domain "
            "contract is the leak again"
        ]
    return path, []


def check_domain_constrained(ev: Evidence):
    manifests = curriculum_manifests(ev)
    problems: list[str] = []
    if not manifests:
        problems.append(
            "manifest-schema-undeclared: no curriculum manifest was found at all, so the "
            "requirement is unmeasurable and is reported as such rather than as a pass"
        )

    enumerated = 0
    for path in manifests:
        doc = ev.parse(path)
        label = rel(path)
        ev.resolve(
            "the manifest domain contract",
            label + " domain.manifest_schema",
            "the curriculum's own directory and the engine metaschema",
        )
        contract_path, found = declared_contract(doc, label)
        problems += found
        if contract_path is None:
            continue
        error = ev.validate(contract_path, METASCHEMA)
        contract = common._deserialize(contract_path)
        if error:
            problems.append(
                f"domain-unconstrained:{rel(contract_path)} does not constrain what the "
                f"engine stopped constraining — {error}"
            )
            continue
        problems += content_violations(doc, contract, label)
        activity = ((contract.get("$defs") or {}).get("core_activity") or {}).get("properties") or {}
        enumerated += len((activity.get("mode") or {}).get("enum") or [])
        enumerated += len((activity.get("domain_state") or {}).get("enum") or [])

    labs = sum(len((ev.parse(p) or {}).get("labs") or []) for p in manifests)
    line = (
        f"FR-P5-DOMAIN-CONSTRAINED {'PASS' if not problems else 'FAIL'} "
        f"({len(manifests)} curricula, each declaring a constraining manifest contract; "
        f"{enumerated} curriculum-declared terms enumerated, {labs} core_activity blocks "
        "validated against them)"
    )

    shrugging = FIXTURES / "manifest_domain_unconstrained.reject.json"
    constraining = FIXTURES / "manifest_domain_constrained.accept.json"
    undeclared_mode = FIXTURES / "core_activity_mode_undeclared.reject.json"
    fixtures = [
        Fixture(
            name=rel(shrugging),
            kind="reject",
            expected_error="domain-unconstrained",
            detector=lambda: (
                contract_violations(common._deserialize(shrugging), rel(shrugging)) or [None]
            )[0],
        ),
        Fixture(
            name=rel(constraining),
            kind="accept",
            detector=lambda: (
                contract_violations(common._deserialize(constraining), rel(constraining))
                or [None]
            )[0],
        ),
        Fixture(
            name=rel(undeclared_mode),
            kind="reject",
            expected_error="core-activity-invalid",
            detector=lambda: (
                content_violations(
                    common._deserialize(undeclared_mode),
                    common._deserialize(constraining),
                    rel(undeclared_mode),
                )
                or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECKS_TABLE = {"domain-constrained": check_domain_constrained}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, choices=sorted(CHECKS_TABLE))
    args = parser.parse_args()
    ev = Evidence(gate_id=args.check)
    outcome = CHECKS_TABLE[args.check](ev)
    print(outcome.detail)
    for record in outcome.fixtures:
        print(f"  fixture {record['fixture']}: {record['outcome']} ({record['matched_error']})")
    print(f"  mechanisms: {ev.claim() or '-'}")
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
