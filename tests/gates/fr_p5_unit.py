"""Phase-5 gates — the four generic checks every unit owes, in any domain.

``plans/simplification/plan/simplification.plan.v3.md`` §6 phase 4 names four checks
the engine owes every curriculum: readability against a band, Bloom verbs against the
declared level, cross-document derivation, and hash resolution. §7 sequences this
phase first among the substantive work for one reason — these operate on a unit file,
so a hand-written fixture exercises them with no generator in existence.

**What these gates cover today, stated so it cannot be over-read.** A unit is a file
under ``curricula/<name>/units/``. There are none: nothing in this repository
generates one. The production relation is therefore reported as a **count of units
scanned**, and today that count is zero. The executed assertion is the fixture pair
below, and that is the whole of the coverage. Real coverage over generated work is
``RT-7``. A gate that reported this as generated-lab coverage would be failure A5.

**No domain word appears here.** The readability band and the Bloom verb table are
read from ``policy/calibration.v1.yaml``, which binds every run regardless of
curriculum; the derivation check resolves pointers into whatever a unit's ``domain``
block holds without knowing what is in it; and the receipt check hashes bytes.
``TEXT-BLOOM-VERBS`` **flags and never blocks**: human raters agree with each other on
Bloom level only 46.58% of the time, so this gate asserts that a disagreement is
raised and recorded, never that a Bloom verdict is correct.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import Evidence, Fixture, REPO_ROOT, gate_result, rel  # noqa: E402

FIXTURES = common.FIXTURES_DIR

CALIBRATION = REPO_ROOT / "policy" / "calibration.v1.yaml"
CURRICULA_DIR = REPO_ROOT / "curricula"
RETIRED = "deprecated"

# Where a generated unit lands. Named by convention rather than by curriculum, and
# resolved at run time: the engine may know that units exist and must not know whose.
UNITS_SUBDIR = "units"


# ---------------------------------------------------------------------------
# The production subject


def unit_files(ev: Evidence | None = None) -> list[Path]:
    """Every generated unit, in every curriculum. Zero today, and reported as zero."""
    found: list[Path] = []
    entries = (
        ev.listdir(CURRICULA_DIR) if ev is not None
        else (sorted(CURRICULA_DIR.iterdir()) if CURRICULA_DIR.is_dir() else [])
    )
    for entry in entries:
        if not entry.is_dir() or entry.name == RETIRED:
            continue
        found += sorted((entry / UNITS_SUBDIR).glob("*.json"))
    return found


def _load(path: Path):
    return common._deserialize(path)


def _pointer(node, dotted: str):
    """Follow a dotted path through parsed data. Returns ``(value, found)``.

    Strict: each segment is a mapping key or a list index and nothing else. A fuzzy
    walk would let a wrong pointer resolve to a coincidentally-named neighbour, which
    is the drift this check exists to catch.
    """
    for key in dotted.split("."):
        if isinstance(node, dict) and key in node:
            node = node[key]
        elif isinstance(node, list) and key.isdigit() and int(key) < len(node):
            node = node[int(key)]
        else:
            return None, False
    return node, True


# ---------------------------------------------------------------------------
# Readability — TEXT-READABILITY-BAND


_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_SENTENCE = re.compile(r"[.!?]+(?:\s|$)")
_VOWEL_RUN = re.compile(r"[aeiouy]+")


def syllables(word: str) -> int:
    """Vowel runs, with a silent trailing ``e`` removed and a floor of one.

    A published syllabifier would be a dependency this repository does not have, and
    the band is what carries the judgement — the metric only has to be the same
    metric every time it is applied.
    """
    lowered = word.lower().strip("'’-")
    if not lowered:
        return 0
    if len(lowered) > 2 and lowered.endswith("e") and not lowered.endswith(("le", "ee", "ye")):
        lowered = lowered[:-1]
    return max(1, len(_VOWEL_RUN.findall(lowered)))


def grade_level(text: str) -> float | None:
    """Flesch-Kincaid grade level, or ``None`` when there is nothing to score."""
    words = _WORD.findall(text)
    sentences = max(1, len(_SENTENCE.findall(text)))
    if not words:
        return None
    total = sum(syllables(w) for w in words)
    return round(0.39 * (len(words) / sentences) + 11.8 * (total / len(words)) - 15.59, 2)


def readability_violations(unit, band, metric: str) -> list[str]:
    problems: list[str] = []
    text = unit.get("child_facing_text") if isinstance(unit, dict) else None
    if not isinstance(text, list) or not [t for t in text if str(t).strip()]:
        return ["readability-no-subject: the unit declares no child_facing_text to score"]
    if metric != "flesch_kincaid_grade":
        return [f"readability-metric-unknown:{metric!r} is not a metric this gate computes"]
    score = grade_level("\n".join(str(t) for t in text))
    if score is None:
        return ["readability-no-subject: child_facing_text carries no words"]
    low, high = band
    if not low <= score <= high:
        problems.append(
            f"readability-out-of-band: the unit scores {score} and the band is [{low}, {high}]"
        )
    return problems


def check_readability(ev: Evidence):
    calibration = ev.read_for_resolution(CALIBRATION)
    ev.resolve("readability.band", rel(CALIBRATION), "the units under curricula/*/units/")
    declared = (calibration or {}).get("readability") or {}
    band, metric = declared.get("band"), str(declared.get("metric", ""))
    problems: list[str] = []
    if not (isinstance(band, list) and len(band) == 2):
        problems.append(
            f"readability-band-missing: {rel(CALIBRATION)} declares no two-element "
            "readability band, so the check has no premise to apply"
        )
        band = [0, 0]

    units = unit_files(ev)
    for path in units:
        unit = ev.read_for_resolution(path)
        for problem in readability_violations(unit, band, metric):
            problems.append(f"{problem} ({rel(path)})")

    line = (
        f"FR-P5-READABILITY {'PASS' if not problems else 'FAIL'} "
        f"({len(units)} units scanned, band {band}, metric {metric or 'none'}; "
        f"no generator exists, so the executed assertion is the fixture pair — RT-7)"
    )
    reject = FIXTURES / "unit_readability_above_band.reject.json"
    accept = FIXTURES / "unit_readability_in_band.accept.json"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="readability-out-of-band",
            detector=lambda: (readability_violations(_load(reject), band, metric) or [None])[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (readability_violations(_load(accept), band, metric) or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# Bloom verbs — TEXT-BLOOM-VERBS, which flags and never blocks


def bloom_flags(unit, table: dict) -> list[str]:
    """Every disagreement between a declared level and the verb that opens the
    objective. A **flag**, never a verdict: the level a verb implies is a reading, and
    human raters agree with each other on it only 46.58% of the time."""
    order = list(table)
    flags: list[str] = []
    objectives = ((unit or {}).get("pedagogy") or {}).get("learning_objectives") or []
    for index, objective in enumerate(objectives):
        declared = (objective or {}).get("bloom_level")
        statement = str((objective or {}).get("statement", "")).strip()
        opening = re.split(r"[^A-Za-z]+", statement, maxsplit=1)[0].lower()
        found = [level for level in order if opening in [v.lower() for v in table[level]]]
        if not found:
            flags.append(
                f"bloom-verb-unclassified: objective {index} opens with {opening!r}, "
                f"which no level's verb list claims"
            )
            continue
        if declared not in order:
            flags.append(
                f"bloom-verb-level-undeclared: objective {index} declares {declared!r}, "
                "which is not a level the table names"
            )
            continue
        implied = min(order.index(level) for level in found)
        if implied < order.index(declared):
            flags.append(
                f"bloom-verb-below-declared-level: objective {index} declares "
                f"{declared!r} and opens with {opening!r}, a {order[implied]!r} verb"
            )
        elif implied > order.index(declared):
            flags.append(
                f"bloom-verb-above-declared-level: objective {index} declares "
                f"{declared!r} and opens with {opening!r}, a {order[implied]!r} verb"
            )
    return flags


def check_bloom_verbs(ev: Evidence):
    calibration = ev.read_for_resolution(CALIBRATION)
    ev.resolve("bloom_verbs", rel(CALIBRATION), "each unit's declared bloom_level")
    table = (calibration or {}).get("bloom_verbs") or {}

    # What fails this gate is the flagging machinery being absent or unusable — never
    # a flag. A blocking Bloom check would be a 46.58%-reliable rule with the force of
    # a schema.
    problems: list[str] = []
    if not isinstance(table, dict) or len(table) < 2:
        problems.append(
            f"bloom-table-missing: {rel(CALIBRATION)} declares no ordered bloom_verbs "
            "table, so no verb can be classified at all"
        )
    for level, verbs in (table or {}).items():
        if not isinstance(verbs, list) or not verbs:
            problems.append(f"bloom-table-incomplete:{level} lists no verbs")

    units = unit_files(ev)
    flags: list[str] = []
    for path in units:
        flags += [
            f"{flag} ({rel(path)})"
            for flag in bloom_flags(ev.read_for_resolution(path), table)
        ]

    line = (
        f"FR-P5-BLOOM-VERBS {'PASS' if not problems else 'FAIL'} "
        f"({len(units)} units scanned, {len(table)} levels, {len(flags)} flags raised — "
        f"flags are recorded and never block; no generator exists, so the executed "
        f"assertion is the fixture pair — RT-7)"
    )
    for flag in flags:
        ev.note(f"bloom-flag: {flag}")
    reject = FIXTURES / "unit_bloom_verb_below_level.reject.json"
    accept = FIXTURES / "unit_bloom_verb_matches_level.accept.json"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="bloom-verb-below-declared-level",
            detector=lambda: (bloom_flags(_load(reject), table) or [None])[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (bloom_flags(_load(accept), table) or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    if flags:
        detail += " | flags: " + "; ".join(flags)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# Cross-document derivation — DOC-DERIVED-FROM-SOURCE


def derivation_violations(unit) -> list[str]:
    """One parent: every rendered fact names the pointer into ``domain`` it came from,
    and equals what is there. Prose that derives from nothing has a second author."""
    problems: list[str] = []
    domain = (unit or {}).get("domain")
    derived = (unit or {}).get("derived")
    if not isinstance(derived, list) or not derived:
        return ["derivation-absent: the unit renders no fact from its domain data"]
    if not isinstance(domain, dict):
        return ["derivation-absent: the unit declares no domain block to derive from"]
    for index, entry in enumerate(derived):
        if not isinstance(entry, dict):
            problems.append(f"derivation-pointer-unresolved: entry {index} is not a mapping")
            continue
        pointer = str(entry.get("from", ""))
        target = entry.get("target", index)
        if not pointer.startswith("domain."):
            problems.append(
                f"derivation-pointer-unresolved:{target} cites {pointer!r}, which does "
                "not start at the domain block"
            )
            continue
        value, found = _pointer(domain, pointer[len("domain."):])
        if not found:
            problems.append(f"derivation-pointer-unresolved:{target} cites {pointer!r}")
            continue
        if str(entry.get("rendered")) != str(value):
            problems.append(
                f"derivation-value-mismatch:{target} renders {entry.get('rendered')!r} "
                f"and {pointer} holds {value!r}"
            )
    return problems


def check_derivation(ev: Evidence):
    units = unit_files(ev)
    # Recorded once, before the loop, so the claim class is the same whether or not a
    # unit exists. A gate whose declared class drifts with the contents of the
    # repository fails FR-P0-REGISTRY (d) the day the first unit lands.
    ev.resolve(
        "every rendered fact",
        "curricula/*/units/*.json derived[]",
        "that unit's own domain block",
    )
    problems: list[str] = []
    for path in units:
        unit = ev.read_for_resolution(path)
        problems += [f"{p} ({rel(path)})" for p in derivation_violations(unit)]

    line = (
        f"FR-P5-DERIVATION {'PASS' if not problems else 'FAIL'} "
        f"({len(units)} units scanned; no generator exists, so the executed assertion "
        f"is the fixture pair — RT-7)"
    )
    reject = FIXTURES / "unit_derivation_unparented.reject.json"
    accept = FIXTURES / "unit_derivation_one_parent.accept.json"
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="derivation-value-mismatch",
            detector=lambda: (derivation_violations(_load(reject)) or [None])[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (derivation_violations(_load(accept)) or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------
# Receipt hashes — RECEIPT-HASH-RESOLVES


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_violations(unit_path: Path) -> list[str]:
    """B4, generalised: a receipt that does not resolve to the artifact actually
    shipped proves nothing. The hash is recomputed from the bytes, never trusted."""
    unit = _load(unit_path)
    problems: list[str] = []
    visuals = (unit or {}).get("visuals")
    if not isinstance(visuals, list) or not visuals:
        return ["receipt-absent: the unit ships no visual carrying a receipt"]
    root = unit_path.parent / str((unit or {}).get("artifact_root", "."))
    for index, visual in enumerate(visuals):
        provenance = (visual or {}).get("provenance") or {}
        embedded = provenance.get("embedded_as")
        recorded = str(provenance.get("file_hash", ""))
        label = (visual or {}).get("role", index)
        if not embedded or not recorded:
            problems.append(f"receipt-absent:{label} records no hash or names no artifact")
            continue
        asset = root / str(embedded)
        if not asset.is_file():
            problems.append(f"receipt-asset-missing:{label} names {embedded}, which is not shipped")
            continue
        actual = _sha256(asset)
        if actual != recorded:
            problems.append(
                f"receipt-hash-mismatch:{label} records {recorded[:12]}… and {embedded} "
                f"hashes to {actual[:12]}…"
            )
    return problems


def check_receipt_hash(ev: Evidence):
    units = unit_files(ev)
    ev.resolve(
        "every visual receipt hash",
        "curricula/*/units/*.json visuals[].provenance",
        "the bytes of the artifact each names",
    )
    problems: list[str] = []
    for path in units:
        problems += [f"{p} ({rel(path)})" for p in receipt_violations(path)]

    reject = FIXTURES / "unit_receipt_unresolved.reject" / "unit.json"
    accept = FIXTURES / "unit_receipt_resolves.accept" / "unit.json"
    line = (
        f"FR-P5-RECEIPT-HASH {'PASS' if not problems else 'FAIL'} "
        f"({len(units)} units scanned; no generator exists, so the executed assertion "
        f"is the fixture pair — RT-7)"
    )
    fixtures = [
        Fixture(
            name=rel(reject),
            kind="reject",
            expected_error="receipt-hash-mismatch",
            detector=lambda: (receipt_violations(reject) or [None])[0],
        ),
        Fixture(
            name=rel(accept),
            kind="accept",
            detector=lambda: (receipt_violations(accept) or [None])[0],
        ),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)


# ---------------------------------------------------------------------------

CHECKS_TABLE = {
    "readability": check_readability,
    "bloom-verbs": check_bloom_verbs,
    "derivation": check_derivation,
    "receipt-hash": check_receipt_hash,
}


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
