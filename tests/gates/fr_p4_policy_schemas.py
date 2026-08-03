"""Phase-4 gates — a contract per manifest, and the mapping that says who owns what.

A file code depends on can be malformed without anything noticing, unless something
validates it. These gates give every manifest under ``policy/`` a schema, resolve
the pairing from the manifest's **own** pointer rather than from a list kept here,
and then prove the two internal agreements a schema cannot express.

``FR-P4-CHECK-MAPPING`` is where this plan closes gate **B3** in the form it can:
an id advertised with no owner and no stated way of ever being verified. The
stronger form — an id with an owner that nothing executes — is reported as a
**count with an identifier**, never hidden as a pass.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import Evidence, Fixture, REPO_ROOT, gate_result, read_named, rel  # noqa: E402

FIXTURES = common.FIXTURES_DIR

POLICY = REPO_ROOT / "policy"
CHECKS = POLICY / "checks.v1.yaml"
LIMITS = POLICY / "limits.v1.yaml"
FAILURES = POLICY / "failures.v1.yaml"
DEFERRED = POLICY / "deferred.v1.yaml"

CIRCUIT_SCHEMA = REPO_ROOT / "schemas" / "circuit_data.schema.v1.json"
POLARITY_FIXTURE = (
    REPO_ROOT / "curricula" / "arduino_kit" / "fixtures" / "l01_polarity_asserted.reject.json"
)
# Rule 3's accepting case. A detector that only ever sees violations proves nothing
# about what it accepts: without this, a schema that rejected every circuit would
# pass FR-P4-FIXTURE-BITES. This is the real L01 path, not a synthetic one.
POLARITY_ACCEPT = REPO_ROOT / "curricula" / "arduino_kit" / "l01_unpowered_power_path.json"
TIME_LIMIT_FIXTURE = FIXTURES / "time_limit_present.reject.yaml"

# Rule 1: a refactor gate never appears in the check inventory, and a curriculum
# check never lives in tests/gates/. The prefixes are what keeps the two apart.
# A check id is matched whole. Without excluding a leading `-`, the tail of a gate
# id reads as a curriculum check id and the gate invents an undeclared check out of
# its own registry — which is why the scan below anchors on a non-hyphen boundary.
FR_ID = re.compile(r"^FR-[A-Z0-9-]+$")
RT_ID = re.compile(r"^RT-[0-9]+$")


def policy_manifests() -> list[Path]:
    """Every manifest that names its own contract.

    gate_impl_fix, `simplification.plan.v3.md` §6 phase 3: the check inventory split in
    two, and the half that moved is a manifest like any other. Both halves validate
    against the same schema — only the owner changes — and a gate that validated one of
    them would be validating half an inventory. Curriculum inventories are reached by
    name under a directory read at run time, never by a glob over `curricula/**`: the
    other files there declare no contract pointer and are not manifests of this kind.
    """
    return sorted(POLICY.rglob("*.yaml")) + [
        p for p in common.check_inventories() if p != common.CHECKS_MANIFEST
    ]


def check_entries(doc) -> list[dict]:
    return [
        entry
        for value in (doc or {}).values()
        if isinstance(value, list)
        for entry in value
        if isinstance(entry, dict) and "id" in entry
    ]


# ---------------------------------------------------------------------------
# FR-P4-ALL-VALIDATE


def pairing_violations(manifests, ev: Evidence | None = None) -> tuple[list[str], list[str]]:
    """Every manifest names its own contract, and validates against it."""
    problems, pairs = [], []
    for path in manifests:
        doc = common._deserialize(path)
        pointer = (doc or {}).get("schema")
        if not pointer:
            problems.append(f"no-schema-for-manifest:{rel(path)}")
            continue
        schema_path = REPO_ROOT / pointer
        if not schema_path.exists():
            problems.append(f"no-schema-for-manifest:{rel(path)} names {pointer}, which does not exist")
            continue
        if ev is not None:
            ev.resolve(f"the contract for {rel(path)}", f"{rel(path)}'s own schema pointer", pointer)
            error = ev.validate(path, schema_path)
        else:
            error = common._validate_obj(doc, common._deserialize(schema_path))
        if error:
            problems.append(f"{rel(path)}: {error}")
        pairs.append(f"{rel(path)} → {pointer}")
    return problems, pairs


def check_validate(ev: Evidence):
    manifests = ev.select(policy_manifests())
    problems, pairs = pairing_violations(manifests, ev)
    line = (
        f"FR-P4-ALL-VALIDATE {'PASS' if not problems else 'FAIL'} "
        f"({len(pairs)} manifest→schema pairs resolved from the manifests themselves)"
    )
    reject = FIXTURES / "policy_manifest_unschemaed.reject.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="no-schema-for-manifest",
            detector=lambda: (pairing_violations([reject])[0] or [None])[0],
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail + "\n  " + "\n  ".join(pairs), fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P4-CHECK-MAPPING


def mapping_violations(doc, gate_ids: set[str], deferred_ids: set[str]) -> tuple[list[str], list[str], list[str]]:
    """(a) an owner that exists, (b) a method and the artifact carrying it.

    Returns (problems, verified_here, mapped_not_executed)."""
    problems, verified, mapped = [], [], []
    for entry in check_entries(doc):
        cid = entry["id"]
        if FR_ID.match(cid):
            problems.append(f"refactor-gate-in-check-inventory:{cid}")
            continue
        owner = entry.get("owner")
        if not owner:
            problems.append(f"advertised-without-owner:{cid} names no owner")
            continue
        if not (REPO_ROOT / owner).exists():
            problems.append(f"advertised-without-owner:{cid} — owner {owner} does not exist")
            continue
        method = entry.get("method")
        if method not in common.MECHANISM_ORDER:
            problems.append(f"advertised-without-owner:{cid} — {method!r} is not a verification method")
            continue
        gate, rt = entry.get("verified_by"), entry.get("deferred")
        if gate and rt:
            problems.append(f"advertised-without-owner:{cid} is both verified here and deferred")
        elif gate:
            if gate not in gate_ids:
                problems.append(f"advertised-without-owner:{cid} — {gate} is not a gate in the registry")
            else:
                verified.append(cid)
        elif rt:
            if rt not in deferred_ids:
                problems.append(f"advertised-without-owner:{cid} — {rt} is not a deferred id")
            else:
                mapped.append(f"{cid} ({rt})")
        else:
            problems.append(
                f"advertised-without-owner:{cid} — no gate executes it and no RT- id records why not"
            )
    return problems, verified, mapped


def check_mapping(ev: Evidence):
    # gate_impl_fix, §6 phase 3: the inventory is the engine's file and each
    # curriculum's own, read as one. Reading only the engine's half would report every
    # id the split moved as undeclared, and would report the harness naming those ids as
    # naming undeclared checks — a wrong scan root, not a weakened criterion. Nothing
    # was dropped rather than moved, and this is what proves it in both directions.
    doc = ev.read_for_resolution(CHECKS)
    for path in common.check_inventories():
        if path != CHECKS:
            doc = {**doc, **{k: doc.get(k, []) + v
                             for k, v in (ev.read_for_resolution(path) or {}).items()
                             if isinstance(v, list)}}
    registry = ev.import_gate_module("registry")
    gate_ids = {g["id"] for g in registry.GATES}
    deferred_ids = {
        e["id"] for e in (ev.read_for_resolution(DEFERRED) or {}).get("deferred", []) if "id" in e
    }
    declared = {e["id"] for e in check_entries(doc)}
    for entry in check_entries(doc):
        ev.exists(REPO_ROOT / entry.get("owner", ""))
        ev.resolve(entry["id"], rel(CHECKS), f"{entry.get('owner')} and its verification artifact")
    problems, verified, mapped = mapping_violations(doc, gate_ids, deferred_ids)

    # Rule 1, the other direction: every curriculum check id this harness names must
    # be declared in the inventory. The gate modules are read **by name**, which rule
    # 7's named-file clause allows; nothing here globs tests/**.
    #
    # "No FR-* id appears there" means no refactor gate is listed *as a check* — that
    # is the per-entry test above. It cannot mean the string may never occur, because
    # (b) explicitly offers "a gate id in tests/gates/registry.py" as the artifact
    # that carries a check's verification, and seven ids take it.
    ev.text_of(CHECKS)
    prefixes = sorted({cid.split("-")[0] for cid in declared})
    named = re.compile(r"(?<![A-Za-z0-9-])(" + "|".join(prefixes) + r")-[A-Z0-9-]+")
    for gate in registry.GATES:
        module = common.GATES_DIR / f"{gate['impl'].split(':')[0]}.py"
        if not module.exists():
            continue
        source = ev.text_of(module)
        for match in sorted({m.group(0) for m in named.finditer(source)}):
            if match not in declared:
                problems.append(f"harness-names-undeclared-check:{match} in {rel(module)}")

    line = (
        f"FR-P4-CHECK-MAPPING {'PASS' if not problems else 'FAIL'} "
        f"({len(declared)} ids: {len(verified)} VERIFIED HERE, "
        f"{len(mapped)} MAPPED, NOT EXECUTED — {', '.join(mapped) or 'none'})"
    )
    reject = FIXTURES / "orphan_check_id.reject.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="advertised-without-owner",
            detector=lambda: (
                mapping_violations(common._deserialize(reject), gate_ids, deferred_ids)[0] or [None]
            )[0],
        )
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P4-AGREEMENT


def names_duration_governance(value: str) -> bool:
    """Recognize duration semantics even when a cap is renamed."""
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    tokens = [token for token in re.split(r"[^a-z0-9]+", camel_split.lower()) if token]
    token_set = set(tokens)
    if token_set & {
        "second", "seconds", "sec", "secs", "millisecond", "milliseconds",
        "minute", "minutes", "min", "mins", "hour", "hours", "hr", "hrs",
        "timeout", "deadline", "duration", "ttl",
    }:
        return True
    pairs = set(zip(tokens, tokens[1:]))
    if pairs & {("wall", "clock"), ("wall", "time")}:
        return True
    return bool(
        token_set & {"limit", "cap", "budget", "maximum", "max"}
        and token_set & {"time", "runtime", "elapsed"}
    )


def forbidden_time_limit_violations(doc) -> list[str]:
    """Reject duration-governing keys or flags without constraining telemetry prose."""
    problems = []
    for group, entries in (doc or {}).items():
        if not isinstance(entries, dict) or group == "schema":
            continue
        for name, spec in entries.items():
            if not isinstance(spec, dict):
                continue
            flag = str(spec.get("flag", ""))
            if names_duration_governance(str(name)) or names_duration_governance(flag):
                problems.append(f"forbidden-time-limit:{group}.{name} ({flag or 'no flag'})")
    return problems


def limit_violations(doc) -> list[str]:
    """(a) Every limits entry is numeric/flagged and is not duration governance."""
    problems = []
    for group, entries in (doc or {}).items():
        if not isinstance(entries, dict) or group == "schema":
            continue
        for name, spec in entries.items():
            where = f"{group}.{name}"
            if not isinstance(spec, dict):
                problems.append(f"limit-missing-value:{where} is a bare value with no flag")
                continue
            if not isinstance(spec.get("value"), (int, float)):
                problems.append(f"limit-missing-value:{where} states no number")
            if not str(spec.get("flag", "")).startswith("--"):
                problems.append(f"limit-missing-value:{where} names no flag")
    problems += forbidden_time_limit_violations(doc)
    return problems


def failure_violations(doc, gate_ids: set[str], deferred_ids: set[str]) -> tuple[list[str], dict]:
    """(b) Every failures id names a correction and a verification owner, recorded
    as which of the two kinds it is."""
    problems, owners = [], {"gate": [], "deferred": []}

    def walk(node):
        if isinstance(node, dict):
            if "id" in node and isinstance(node.get("id"), str):
                yield node
            for value in node.values():
                yield from walk(value)
        elif isinstance(node, list):
            for value in node:
                yield from walk(value)

    for entry in walk(doc or {}):
        fid = entry["id"]
        if not entry.get("correction"):
            problems.append(f"failure-without-correction:{fid}")
        owner = entry.get("verified_by")
        if not owner:
            problems.append(f"failure-without-verification-owner:{fid}")
        elif owner in gate_ids:
            owners["gate"].append(f"{fid}→{owner}")
        elif RT_ID.match(owner) and owner in deferred_ids:
            owners["deferred"].append(f"{fid}→{owner}")
        else:
            problems.append(f"failure-without-verification-owner:{fid} names {owner!r}, which resolves to nothing")
    return problems, owners


def check_agreement(ev: Evidence):
    registry = ev.import_gate_module("registry")
    gate_ids = {g["id"] for g in registry.GATES}
    deferred_ids = {
        e["id"] for e in (ev.read_for_resolution(DEFERRED) or {}).get("deferred", []) if "id" in e
    }

    problems = limit_violations(ev.parse(LIMITS))

    failures_doc = ev.parse(FAILURES)
    failure_problems, owners = failure_violations(failures_doc, gate_ids, deferred_ids)
    problems += failure_problems
    for kind, entries in owners.items():
        for entry in entries:
            fid, owner = entry.split("→")
            ev.resolve(fid, rel(FAILURES), f"{owner} ({'a gate here' if kind == 'gate' else 'a deferred obligation'})")

    # (c) the check-inventory mapping relation, asserted from the manifest side.
    # Both halves, for the reason FR-P4-CHECK-MAPPING states.
    ev.parse(CHECKS)
    checks_doc = common.merged_check_inventory()
    mapping_problems, verified, mapped = mapping_violations(checks_doc, gate_ids, deferred_ids)
    problems += mapping_problems

    line = (
        f"FR-P4-AGREEMENT {'PASS' if not problems else 'FAIL'} "
        f"(limits: every entry numbered and flagged, with no duration governors; failures: "
        f"{len(owners['gate'])} proven here, {len(owners['deferred'])} deferred; "
        f"checks: {len(verified)} VERIFIED HERE, {len(mapped)} MAPPED, NOT EXECUTED). "
        f"Out of scope by design: controller states vs implemented states (RT-1) and "
        f"routes vs recorded proof (RT-2) — both compare a manifest to a running system."
    )
    reject = FIXTURES / "limit_without_number.reject.yaml"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="limit-missing-value",
            detector=lambda: (limit_violations(common._deserialize(reject)) or [None])[0],
        ),
        Fixture(
            name=rel(TIME_LIMIT_FIXTURE),
            kind="reject",
            expected_error="forbidden-time-limit",
            detector=lambda: (
                forbidden_time_limit_violations(common._deserialize(TIME_LIMIT_FIXTURE)) or [None]
            )[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# FR-P4-FIXTURE-BITES


def check_fixture_bites(ev: Evidence):
    """Both paths are literals here, so no cross-file resolution occurs and the
    class is ``schema`` alone."""
    error = ev.validate(POLARITY_FIXTURE, CIRCUIT_SCHEMA)
    inert = error is None
    line = (
        f"FR-P4-FIXTURE-BITES {'PASS' if not inert else 'FAIL'} "
        f"(the polarity fixture is rejected by circuit_data.schema.v1.json)"
    )
    fixtures = [
        Fixture(
            name=rel(POLARITY_FIXTURE),
            kind="reject",
            expected_error="'kit,battery,dc_lead,positive_terminal' should not be valid under",
            detector=lambda: common._validate_obj(
                common._deserialize(POLARITY_FIXTURE), common._deserialize(CIRCUIT_SCHEMA)
            ),
        ),
        Fixture(
            name=rel(POLARITY_ACCEPT),
            kind="accept",
            detector=lambda: common._validate_obj(
                common._deserialize(POLARITY_ACCEPT), common._deserialize(CIRCUIT_SCHEMA)
            ),
        ),
    ]
    detail = line if not inert else line + " — the schema accepted a circuit that asserts polarity on an unpowered path"
    return gate_result(not inert, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECK_TABLE = {
    "validate": check_validate,
    "agreement": check_agreement,
    "fixture-bites": check_fixture_bites,
    "mapping": check_mapping,
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
