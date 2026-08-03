# The anatomy of a review agent in curriculum_builder

Contents:

1. [The six artifacts](#1-the-six-artifacts)
2. [Failure ledger entry](#2-failure-ledger-entry)
3. [Check inventory entry](#3-check-inventory-entry)
4. [Release advertisement](#4-release-advertisement)
5. [Fixture pair](#5-fixture-pair)
6. [Detector and gate](#6-detector-and-gate)
7. [Deferred obligation](#7-deferred-obligation)
8. [Dossier](#8-dossier)
9. [Worked example, end to end](#9-worked-example-end-to-end)
10. [Field mapping from the recommendation](#10-field-mapping-from-the-recommendation)

---

## 1. The six artifacts

| # | Artifact | Where | Why it exists |
|---|----------|-------|---------------|
| 1 | Failure entry | `policy/failures.v1.yaml` | states the rule, so the inventory has an `owner` that exists and says something |
| 2 | Inventory entry | `policy/checks.v1.yaml` or `curricula/<name>/checks.v1.yaml` | the id itself, its assertion, its stage, its execution status |
| 3 | Release row | the `release:` block of that same inventory | the surface that advertises the id; an unadvertised id has stopped being claimed |
| 4 | Fixture pair | `tests/fixtures/` | the executed evidence that the detector bites |
| 5 | Detector + gate, **or** deferred entry | `tests/gates/` + `tests/gates/registry.py`, **or** `policy/deferred.v1.yaml` | what actually runs, or the honest record of why nothing does |
| 6 | Dossier | `docs/agents/<CHECK-ID>.md` | provenance and the verdict-design reasoning |

Artifacts 1-3 and 5 are read by gates. Getting a field wrong is a gate
failure, not a style nit.

---

## 2. Failure ledger entry

`policy/failures.v1.yaml`, validated by `schemas/failures.schema.v1.json`.
Required: `id`, `correction` (≥20 chars), `verified_by` matching
`^(FR-[A-Z0-9-]+|RT-[0-9]+)$`. Everything else is permitted and used.

Pick the array that fits the defect's origin — `generator_defects` (A-series),
`v5_gate_failures` (B-series), `capability_failures`, `runtime_obligations`.
A defect observed in generated output is a generator defect.

```yaml
  - id: A14
    correction: >-
      Check the assembled document's shape before any semantic review reads it, so a
      section that is still structured data is caught at assembly rather than by a
      reviewer reading it as prose.
    verified_by: FR-P5-RENDER-SHAPE
    defect: the document renderer emitted raw JSON as the lesson body
    consequence: all four units shipped identically unreadable, past a check set that reported complete
    checks: [RENDER-NO-RAW-STRUCTURED]
    note: >-
      one templating bug reaching every unit, not four independent failures. No existing
      check inspected the shape of rendered output, only the upstream JSON's schema validity.
```

`checks: [<ID>]` is the link back — precedent is `A6`, which names
`DOC-DERIVED-FROM-SOURCE`. It is what makes this file the `owner` of your id
in more than name.

`verified_by` here follows the same rule as the inventory's: the gate that
proves the correction, or the `RT-` id that would. `A6` is worth studying —
its generic check *executes*, and its `verified_by` still says `RT-5`,
because the defect is about a generated lab and none exists. The check
running is not the correction being proven.

---

## 3. Check inventory entry

Validated by `schemas/checks.schema.v1.json`.

**Required:** `id`, `asserts` (≥10 chars), `owner`, `method`.
**Exactly one of:** `verified_by` (`^FR-[A-Z0-9-]+$`) or `deferred`
(`^RT-[0-9]+$`). Both, or neither, fails.

| Field | Rule |
|-------|------|
| `id` | `^[A-Z][A-Z0-9]*(-[A-Z0-9]+)+$`, never `FR-`-prefixed |
| `owner` | a path that exists; by contract it must also *name the id* |
| `method` | one of `tree`, `parse`, `schema`, `text`, `mapping`, `declaration`, `execution` |
| `artifact` | optional; the file carrying the verification |
| `stage` | `static`, `deterministic`, `golden`, `logger`, `live-capability` |
| `fixture` / `fixture_expectation` / `rejects` | optional, conventional, and worth writing |
| `note` | optional, free-form; where the reasoning goes |

Entries live under a lowercase category key (`unit:`, `reviewers:`,
`lab_document:`, `pdf:`, `log:`, `drift:`, …). Add to an existing category
when one fits; a new category is fine and needs no schema change.

```yaml
unit:
- id: RENDER-NO-RAW-STRUCTURED
  owner: policy/failures.v1.yaml
  method: parse
  artifact: tests/fixtures/unit_render_raw_json.reject.json
  verified_by: FR-P5-RENDER-SHAPE
  asserts: no child-facing section of an assembled unit parses as a JSON object or array.
    A section that round-trips through a JSON parser is structured data that was never
    rendered, whatever it validates against.
  stage: deterministic
  fixture: tests/fixtures/unit_render_raw_json.reject.json
  fixture_expectation: reject
  rejects: an Engage or Explore section whose whole body is a serialized object
  note: see docs/agents/RENDER-NO-RAW-STRUCTURED.md for provenance and verdict design
```

**Write `asserts` so it cannot be over-read.** It is quoted in reports. If
the check flags rather than blocks, say so there — `TEXT-BLOOM-VERBS` does:
*"This check FLAGS and NEVER BLOCKS … what is asserted is that the
disagreement was reported, never that the verdict is right."*

---

## 4. Release advertisement

Each inventory carries a `release:` block. Every row is `{stage, gate_item,
advertises: [patterns]}`, and patterns match `^[A-Z][A-Z0-9-]*\*?$` — a
trailing `*` is a prefix wildcard.

The gate checks **both directions**: every advertised pattern matches an id
at that stage, and every staged id is matched by a pattern at its own stage.
So a new id either falls under an existing wildcard (`LAB-*` covers
`LAB-ANYTHING-NEW`) or needs its own pattern added at its stage.

Check whether your id is already covered before adding a pattern; a pattern
matching nothing fails just as loudly as an id matching no pattern.

---

## 5. Fixture pair

`tests/fixtures/<slug>.reject.<ext>` and `<slug>.accept.<ext>`. Slugs are
lowercase, `_`-separated, and describe the condition rather than the check:
`unit_readability_above_band.reject.json`,
`unit_bloom_verb_matches_level.accept.json`. A directory works when the
fixture needs more than one file — `unit_receipt_resolves.accept/unit.json`.

**Build the reject fixture from `issues_resolved`.** If it says *"L04 used
mAVΩ, 10A socket, mode dial and fuse — four undefined terms against a cap of
two"*, the reject fixture is a unit carrying exactly those four terms against
a declared cap of two. A generic malformed file proves the detector rejects
malformed files, which was never in doubt.

The accept fixture is the same shape with the defect removed, and nothing
else changed. If accept and reject differ in two ways, a passing pair no
longer tells you which one the detector saw.

---

## 6. Detector and gate

Two pieces, deliberately separate. Detectors are pure and testable; gates
handle evidence, fixtures and reporting.

**The detector** takes parsed data and returns `list[str]`, each
`problem-code: human-readable message`. Empty list means clean. The code
before the colon is the contract — fixtures assert on it.

```python
def render_shape_violations(unit) -> list[str]:
    """A section that still parses as JSON was never rendered. Cheap and total:
    the check costs one parse and cannot be talked out of its verdict."""
    problems: list[str] = []
    for name, body in (unit.get("content") or {}).items():
        text = body if isinstance(body, str) else None
        if text is None:
            problems.append(f"render-section-not-text:{name} is not a string at all")
            continue
        try:
            parsed = json.loads(text.strip())
        except (ValueError, TypeError):
            continue
        if isinstance(parsed, (dict, list)):
            problems.append(
                f"render-raw-structured:{name} round-trips through a JSON parser, "
                f"so it is structured data that was never rendered to prose"
            )
    return problems
```

**The gate** is `check_<name>(ev: Evidence) -> GateOutcome`, in a module
under `tests/gates/`. The shape, from `tests/gates/common.py`:

```python
def check_render_shape(ev: Evidence):
    units = fr_p5_unit.unit_files(ev)
    ev.resolve("every child-facing section", "curricula/*/units/*.json content",
               "a JSON parser that must refuse it")
    problems = []
    for path in units:
        problems += [f"{p} ({rel(path)})"
                     for p in render_shape_violations(ev.read_for_resolution(path))]

    line = (f"FR-P5-RENDER-SHAPE {'PASS' if not problems else 'FAIL'} "
            f"({len(units)} units scanned; no generator exists, so the executed "
            f"assertion is the fixture pair — RT-7)")
    reject = FIXTURES / "unit_render_raw_json.reject.json"
    accept = FIXTURES / "unit_render_prose.accept.json"
    fixtures = [
        Fixture(name=rel(reject), kind="reject",
                expected_error="render-raw-structured",
                detector=lambda: (render_shape_violations(_load(reject)) or [None])[0]),
        Fixture(name=rel(accept), kind="accept",
                detector=lambda: (render_shape_violations(_load(accept)) or [None])[0]),
    ]
    detail = line if not problems else line + " — " + "; ".join(problems)
    return gate_result(not problems, detail, fixtures, stdout=line)
```

Three things in that summary line are load-bearing and easy to drop:

- **The count of real subjects scanned.** Today it is zero for anything whose
  subject is a generated unit. Reporting fixture coverage as coverage of
  generated work is failure `A5`, stated in the ledger by name.
- **`RT-7`**, the obligation that records why the count is zero.
- **`expected_error` on every reject fixture.** Without it the fixture proves
  only that something failed.

Where a detector produces several codes and you need the reject fixture to
trip more than one, `fr_p5_unit._codes()` joins the distinct codes with
`" + "` and the fixture asserts the joined string — so a fixture tripping
only one leg is a failure.

**Register the gate** in `tests/gates/registry.py`:

```python
{
    "id": "FR-P5-RENDER-SHAPE",
    "activation_phase": 5,
    "claim_class": "parse+execution",
    "depends_on": ["FR-P0-HARNESS"],
    "command": "python3 tests/gates/fr_p5_unit.py --check render-shape",
    "impl": "fr_p5_unit:check_render_shape",
},
```

…and add it to the CHECKS_TABLE of its module. The gate id's prefix must
belong to a family in `tests/gates/gate_families.v1.yaml`, and the gate must
also appear in that family's plan catalogue section — `FR-P0-REGISTRY`
compares each family against its own plan. Reusing an existing family
(`FR-P5-` → the simplification plan, catalogue section 9) means adding one
catalogue row. A genuinely new family is an entry in `gate_families.v1.yaml`,
a catalogue section in the owning plan, and the gates — and no code.

---

## 7. Deferred obligation

When nothing can execute the check yet, `policy/deferred.v1.yaml` gets an
entry and the inventory says `deferred: RT-N`:

```yaml
  - id: RT-11
    obligation: The rendered document is reviewed as a document
    acceptance_criterion: >-
      a rendered unit exists, produced by a real run, so RENDER-NO-RAW-STRUCTURED
      asserts over an assembled document rather than over its own fixtures alone
    blocked_by: >-
      nothing in this repository renders a unit
    promotes_gate: FR-P5-RENDER-SHAPE
```

`promotes_gate` names an **existing** gate id, resolved against the registry.
`promoted_id` — optional — names what that gate becomes once discharged, and
is deliberately *not* resolved, because it does not exist yet.

Pick the next free number, and read the comment above `RT-8` before you do:
one number is deliberately held open because a fixture cites it as its
canonical dangling reference. Defining it would make that fixture pass and
break the gate that depends on it failing.

`blocked_by` must be true. "No renderer exists" is a blocker; "not
implemented yet" is a restatement of `deferred`. When a blocker clears
partially, say which half — `RT-3` does exactly this.

---

## 8. Dossier

`docs/agents/<CHECK-ID>.md`, from `assets/agent_card.md`. It carries the
provenance (`what_makes_it_sota`, `sources`) and the verdict-design
reasoning, so the inventory `note` can stay one line.

Attribute the sources to the scan that verified them, with its date and
path. This skill does no research: a reader must be able to tell a citation
that was fetched and checked from one a factory pasted in.

---

## 9. Worked example, end to end

Recommendation 5 of `docs/research/sota_agents_research/sota_agents.v1.json`
("Structured-Output Rendering Conformance Gate") becomes:

| Step | Result |
|------|--------|
| Read the repo | no existing id inspects rendered shape; `LAB-SCHEMA-VALID` checks upstream JSON only |
| Reconcile | no conflict — the repo's own note says recovered judge budget goes to deterministic checks |
| Placement | engine (`policy/checks.v1.yaml`) — shape, not subject matter |
| Id | `RENDER-NO-RAW-STRUCTURED` |
| Verdict design | deterministic, blocking, `stage: deterministic`, executed against fixtures with `RT-11` for the missing subject |
| Failure entry | `A14`, `checks: [RENDER-NO-RAW-STRUCTURED]` |
| Inventory | entry above, `owner: policy/failures.v1.yaml`, `method: parse` |
| Release | falls under no existing pattern → add `RENDER-*` at `deterministic` |
| Fixtures | `unit_render_raw_json.reject.json` (Explore body is a serialized object, as L01-L04 shipped) / `unit_render_prose.accept.json` |
| Detector + gate | `render_shape_violations()` + `FR-P5-RENDER-SHAPE` |
| Dossier | `docs/agents/RENDER-NO-RAW-STRUCTURED.md` |

Note what the deterministic check buys: it catches the systemic root cause of
the failed run for one parse per section, and it transitively catches several
other recommendations' defects, because JSON does not score on a readability
band or read as prose to a judge. Build this class of agent first.

---

## 10. Field mapping from the recommendation

| Recommendation field | Becomes |
|---|---|
| `agent` | the dossier title; **not** the id — name the id for the assertion |
| `function` | the `asserts` string, rewritten as one falsifiable claim about a subject |
| `role_in_curriculum_builder` | a hypothesis to verify: inventory choice, `stage`, and where it runs |
| `issues_resolved` | the failure-ledger entry, and the reject fixture |
| `what_makes_it_sota` | dossier provenance; a one-line inventory `note` if it explains a design choice |
| `sources` | dossier provenance, verbatim, attributed to the scan — never re-verified, never added to |

Two of these are traps.

`function` usually describes an agent doing several things — the reference
scan's judge entry scores four dimensions *and* blocks on low agreement.
`asserts` is one falsifiable claim. Either narrow it, or split into two ids
that fail separately, which is what a reader of a failed report needs.

`role_in_curriculum_builder` is the scan's guess about a codebase it did not
read. Treat it as the thing Step 1 exists to check.
