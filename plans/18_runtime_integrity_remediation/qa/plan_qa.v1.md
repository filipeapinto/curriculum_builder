# Runtime Integrity Remediation Plan v1 — Focused QA

## Verdict

**CHANGES REQUIRED — 0 Critical, 2 High.** The plan's nine phases of concrete work
("Exact work" §1-§9) are, on mechanical verification against the actual repository
(`runtime/session_bridge.py`, `runtime/checks.py`, `schemas/lab.schema.v4.json`,
`curricula/arduino_kit/domain.schema.v1.json`, `curricula/arduino_kit/
arduino_kit_curriculum.v5.yaml`, `policy/checks.v1.yaml`, `outputs/arduino_kit_run_v2/**`)
accurate to a striking degree — every cited line number, field name, schema shape, and
current-behavior claim I checked in §1-§7 and §9 matched what the files actually contain.
The two defects found are both in the plan's account of its own scope boundary and of the
policy manifest it edits in §8: one materially misdescribes an existing, non-trivial file
(`runtime/controller.py`) to justify excluding it from scope, and the other's literal
instruction — deleting a note that documents an unmet obligation (`RT-7`) — risks
producing exactly the false-discharge claim the plan elsewhere promises never to make.
Neither finding blocks §1-§7/§9's technical work; both should be corrected before the
plan is treated as authoritative about what it leaves untouched.

## Findings

### 1. High — Phase 8's `policy/checks.v1.yaml` edit can overstate `RT-7`'s discharge, contradicting the plan's own boundary

**Evidence.** Phase 8 instructs: "for exactly the ids §3 and §6 wire into production
execution — `TEXT-READABILITY-BAND`, `TEXT-BLOOM-VERBS`, `DOC-DERIVED-FROM-SOURCE`,
`RECEIPT-HASH-RESOLVES` ... `PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW`
... remove the stale `note`/`deferred: RT-5` language that says 'zero generated units
exist to score today' / marks them as unexecuted, and add a `verified_by`-style pointer."

Reading `policy/checks.v1.yaml` directly: only the three PDF-family ids
(`PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW`, lines 159-177) actually
carry `deferred: RT-5`. The four unit-family ids already carry `verified_by` pointers to
existing gates (`FR-P5-READABILITY`, `FR-P5-BLOOM-VERBS`, `FR-P5-DERIVATION`,
`FR-P5-RECEIPT-HASH`) and no `deferred: RT-5` field at all. Only one of them —
`TEXT-READABILITY-BAND` (line 105-106) — carries the literal "zero generated units exist
to score today" note, and that note's actual subject is not `RT-5`: it ends "...and RT-7
is the coverage that is missing." `RT-7`'s acceptance criterion (`policy/deferred.v1.yaml`
lines 98-104) requires a unit under `curricula/<name>/units/`, a path the plan's own
"Architectural end state" item 6 explicitly says this plan does not produce ("RT-7 ...
is left untouched. This plan makes no claim about their discharge."). The units this plan
regenerates live at `outputs/arduino_kit_run_v2/L0N/`, not `curricula/arduino_kit/units/`.

**Impact.** If Phase 8 is executed as literally written — deleting the note that records
the `RT-7` gap for `TEXT-READABILITY-BAND` and replacing it with only a `verified_by`
pointer to the new production call site — a reader of `policy/checks.v1.yaml` after this
plan runs has no way to see that `RT-7`'s specific acceptance criterion (a unit under
`curricula/<name>/units/`) remains unmet. That is precisely the failure mode
`DRIFT-NO-MISREPORTING` (`policy/checks.v1.yaml` line 295-300) exists to catch: a check
reported as no longer missing its subject when the obligation naming that subject is
still open. It also directly contradicts the plan's own explicit promise, two pages
earlier in the same document, to make no discharge claim about `RT-7`.

**Minimal required remediation.** In Phase 8, restrict "remove the stale note/deferred:
RT-5 language" to the three ids that actually carry `deferred: RT-5` (the PDF family).
For the four unit-family ids, instead of deleting the RT-7 reference, update the note to
state plainly that the check now executes against real rendered content under
`outputs/<run>/L0N/` while `curricula/arduino_kit/units/` remains empty and `RT-7`'s own
path-specific criterion is still unmet — i.e., correct the note rather than remove it.

### 2. High — The plan's scope-boundary rationale misdescribes `runtime/controller.py` as a "16-line stub"

**Evidence.** "Status and objective" states the plan does not build the `policy/
controller.v1.yaml` state machine "because ... `runtime/controller.py` is a 16-line
stub." The actual file is 234 lines and defines a working `CurriculumRuntime` class —
`resolve_curriculum`, `resolve_companions`, `validated_manifest`, `run_verifier_fixtures`,
`_logger_gate`, `static_preflight`, and a `simulate()` method that walks every state in
`policy/controller.v1.yaml`, writing checkpoints, transitions, and a closing log audit
(labelled `"coverage": "simulated-controller-only"` / `"not generated-unit evidence"`, so
it correctly does not claim to satisfy `RT-1`). This class is not dead code: `runtime/
session_bridge.py`'s own `prepare()` — the function this plan modifies — imports and
calls it directly (`from .controller import CurriculumRuntime, RuntimeFailure`, then
`runtime.resolve_curriculum(...)`, `runtime.resolve_companions()`,
`runtime.validated_manifest(...)`, `runtime.run_verifier_fixtures(...)`,
`runtime._logger_gate(...)`), and `runtime/run_curriculum.py`'s CLI is built entirely
around it.

**Impact.** The "16-line stub" claim is the specific factual premise the plan offers for
why the controller/state-machine work is out of scope. It is false, and it is false in a
way that could mislead an implementer into believing there is no existing controller
infrastructure at all — when in fact substantial, already-integrated code (checkpointing,
logger-gate probing, manifest/verifier validation, a full simulated state walk) exists
and is a dependency of the exact function (`prepare()`) this plan edits. The plan's actual
scope exclusion (not building the *non-simulated*, `RT-1`-satisfying version of every
`policy/controller.v1.yaml` state) is still defensible on its own terms, but it is not
defensible on the stated grounds, and a reader who checks the citation — as this review
did — finds the plan's account of the repository contradicted by the repository.

**Minimal required remediation.** Replace "runtime/controller.py is a 16-line stub" with
an accurate description, e.g.: "`runtime/controller.py`'s `CurriculumRuntime.simulate()`
walks every `policy/controller.v1.yaml` state but only writes placeholder state files
labelled `simulated-controller-only`; no path produces real per-state artifacts, which is
what `RT-1` requires and this plan does not build." No other change to scope is needed —
the boundary itself does not depend on the false premise.

## Observations (non-blocking)

- The plan attributes the retrieval-prompt-before-Engage and misconception-beside-Explain
  placement rules to `meta_prompt/assets/unit_prose.v1.md`'s "required arc," but that
  file's "Required unit structure" list never names `retrieval_prompt`, `misconceptions`,
  `scaffolding`, or `vocabulary` at all — the fields' rationale (not their placement) is
  in `meta_prompt/assets/pedagogy.v1.md`. The placement choice itself is reasonable and
  consistent with the cited learning-science rationale; the citation to a specific
  document section as its source is not supported by that document's text.
- Phase 6 attributes the phrase "safety-critical and numeric claims require explicit
  technical entailment review" to `DOC-DERIVED-FROM-SOURCE`'s definition in
  `policy/checks.v1.yaml`; that exact requirement appears in `issues/006-source-
  receipts-do-not-prove-claims.md`'s acceptance criteria, not in the `checks.v1.yaml`
  entry's own `asserts` text. Wiring `check_claim_entailment` into the required check set
  is still correct; only the attribution is imprecise.
- The plan cites `arduino_kit_curriculum.v5.yaml:209` for language calling the meter "a
  basic digital multimeter"; line 209 is `subject_set:`, and `primary: Digital
  multimeter` is line 210. Off by one line; the substantive claim (no exact model named
  in the curriculum's own source documents) is correct.
- Reusing `readability_violations`/`bloom_flags` (to be extracted into `runtime/
  readability.py` per §3) against real rendered unit data requires an adapter:
  `readability_violations` expects `unit.get("child_facing_text")` as a list of strings,
  a fixture-only convention with no counterpart field in `lab.schema.v4.json`, so
  `runtime/checks.py` will need to wrap the rendered text into that shape before calling
  it. `bloom_flags` needs no such adapter — it already reads `pedagogy.learning_objectives`
  directly off the real `lab.json` shape. The plan does not mention this asymmetry, but it
  does not change what needs to be built.
- Phase 1 lists a test case for `next_lab_link` present/absent but the `render_evaluate`
  bullet describing what that function renders does not mention `next_lab_link` at all
  (it is optional in the schema, so omitting it does not trigger the "raise on unrendered
  required field" rule, but the render behavior for the optional field is unstated).
