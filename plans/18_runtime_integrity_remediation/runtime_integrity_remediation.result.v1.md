# Runtime Integrity Remediation — Execution Result v1

Executed `prompts/runtime_integrity_remediation.prompt.v1.md` against
`runtime_integrity_remediation.plan.v1.md`, with the ordered tests in
`qa/execution_test.plan.v1.md`, on 2026-08-08.

**Outcome: all fourteen tests (`RIR-T00`-`RIR-T13`) PASS.** No Stop condition was hit:
`official_kit_photo.jpg` is croppable to two of the three subjects `RIR-T01` asks about, so
the sequence continued into §9 as the plan provides for. Two units reached
`ACCEPTED_PENDING_REVIEW` and two are `BLOCKED` on a photographic role no photograph this
curriculum owns can satisfy — the honest outcome, not a failure of the implementation.

---

## RIR-T00 — Baseline (captured before any change)

- `git rev-parse HEAD`: `37920a60c33b3995f6f1be117ec3e9acbdfce5a5`
- `git status --porcelain` at start (all pre-existing, none this plan's):
  `M .claude/settings.json`, `?? .DS_Store`, `?? docs/.DS_Store`, `?? issues/`,
  `?? plans/runtime_integrity_remediation/`
- SHA-256 of all 166 files under `outputs/arduino_kit_run_v2/L01`-`L04` captured to
  `/tmp/rir_t00_hashes.txt`; `policy/deferred.v1.yaml`, `tests/gates/registry.py` and
  `tests/gates/gate_families.v1.yaml` copied aside for byte comparison. The asset hashes
  `RIR-T10` diffs against are listed in that file. **`outputs/` is gitignored**
  (`.gitignore:` "Run output ... never committed history"), so `git diff` cannot serve as
  the before/after record for `RIR-T10` or `RIR-T12`; the captured hash file is used
  instead, and this is noted again under `RIR-T12`.
- `python3 -m pytest tests/runtime/ -v`: **0 tests ran — 8 collection errors.** Every module
  failed with `ModuleNotFoundError: No module named 'runtime.<x>'`. Cause: `tests/runtime/`
  carries an `__init__.py`, so pytest inserts `tests/` at `sys.path[0]` and the test package
  `tests.runtime` shadows the production package `runtime`. Plain `import runtime` outside
  pytest resolves correctly, so this was invisible except under the test runner. This
  pre-existing breakage made the plan's Verification-sequence step 1 unrunnable and is the
  one out-of-plan fix this execution made (see "Deviations").
- `bash tests/run_gates.sh 2`: `FR-P2-GATEITEMS PASS (6 gate items in the engine's release
  table plus 2 declared by curricula, **42 staged check ids**)`; phase totals
  `14 PASS, 4 FAIL, 3 BLOCKED, 17 SKIPPED of 38`.
- `bash tests/run_gates.sh 5`: `FR-P4-ALL-VALIDATE PASS (12 manifest→schema pairs resolved
  from the manifests themselves)`; phase totals `28 PASS, 5 FAIL, 5 BLOCKED, 0 SKIPPED of 38`.
  The five baseline FAILs are `FR-P0-CLEAN` (untracked files), `FR-P0-NOSTALE`,
  `FR-P1-GITKEEP`, `FR-P2-DEFERRED`, `FR-P3-CAPS-OWNED` — all pre-existing and all still
  failing for the same pre-existing reasons afterwards.

Both gate baselines reproduce round-10 QA's independently recorded figures exactly.

**PASS** — every capture completed; running the capture modified nothing.

---

## RIR-T01 — Photography locatability (§2, §9 step 0)

By direct visual inspection of `curricula/arduino_kit/official_kit_photo.jpg` (1500×1500),
read whole and then as four 750×750 quadrants each upscaled to 1100×1100:

| Unit-role | Outcome |
| --- | --- |
| **L02 — breadboard** | `locatable-and-croppable`. Full-size solderless breadboard at pixels (0, 640)–(1045, 985). Both power rails with their `+`/`−` markings, the centre trench, numbered columns 1–60 and lettered rows a–e / f–j are all legible in the crop. |
| **L03 — wire/jumper detail** | `locatable-and-croppable`. Pixels (0, 1225)–(735, 1500) contain both wire types the unit teaches: the male-male jumper bundle with bare pin ends visible at both ends of each wire, and the male-female Dupont ribbon with its black housings. |
| **L04 — multimeter** | **`BLOCKED (needs verified photograph)`**. No multimeter, meter probe or meter dial appears anywhere in the image. The complete visible inventory is: power supply module, joystick, HC-SR04, relay, DHT11, RGB LED module, fan blade and DC motor, UNO R3, ULN2003 stepper driver, disc, prototype shield with mini breadboard, LEDs, transistors, photoresistors, electrolytic capacitor, active and passive buzzers, tactile buttons, one- and four-digit seven-segment displays, breadboard, 9 V battery with barrel lead, DIP ICs, USB cable, IR remote, resistor array, 10 K potentiometer, LCD1602, jumper wires, SG90 servo, 28BYJ-48 stepper and mounting hardware. This confirms issue 004's claim. |

**Additional finding, not asked for but forced by applying §2's resolver rule to L01's own
declared roles.** L01's manifest declares *two* photographic roles. `verified photorealistic
kit-identification photograph` resolves — the subject of that role is the kit itself, so the
uncropped inventory flat-lay *is* the subject. `safe disconnected setup photograph` does
**not**: the image is an inventory flat-lay, not a photograph of an assembled-but-disconnected
L01 setup, and no region shows the source lead end, the module DC input and the candidate
output location together. Reusing the whole frame for that role would be exactly the
oversized-unrelated-asset substitution issue 003 records, so it is recorded
`BLOCKED (needs verified photograph)` too. This is why L01's terminal state is `BLOCKED`.

Not the Stop condition: two of the three subjects `RIR-T01` asks about are croppable, and a
third (the kit itself) resolves for L01, so the sequence continued.

Every outcome is recorded machine-readably in the new
`curricula/arduino_kit/verified_photo_regions.v1.json`, including the two absent subjects and
the finding behind each.

**PASS** — an explicit, recorded outcome exists for all three unit-roles.

---

## RIR-T02 — Renderer (§1, issue 001)

`python3 -m pytest tests/runtime/test_lesson_render.py -v` → **28 passed**.

- One test per render function per field shape: all four `record_method` values, empty vs
  populated `options`, `worked_example` present/absent, `next_lab_link` present/absent,
  `orientation_cue` present/absent, `signoff_required` true/false.
- `test_assembled_markdown_has_no_serialized_object_syntax_or_field_names` renders a fixture
  unit through the assembled `_markdown()` path and asserts zero `{`, zero `}`, zero `":`,
  and zero occurrences of *every* schema field name containing an underscore (derived by
  walking `lab.schema.v4.json`, not by a hand-written list). Zero matches.
- `test_unrenderable_required_field_raises_renderer_error` adds a populated field with no
  template branch and confirms `RendererError`, naming the field. A field present but empty
  is not treated as unrendered.
- `test_every_handled_field_set_matches_the_schema` asserts `HANDLED_FIELDS` covers *exactly*
  the schema's properties at each location, so the renderer cannot drift from the contract.
- Independently confirmed against real output: `outputs/arduino_kit_run_v2/L02/document/L02.md`
  contains 0 occurrences of `{` or `}`.

**PASS.**

---

## RIR-T03 — Visual pipeline (§2, issue 003)

`python3 -m pytest tests/runtime/test_visual_maps.py -v` → **32 passed**, covering every case
the test plan names:

- `power_path` — directed sequence with per-edge labels read from `domain.electrical`
  (`not yet connected — you are only tracing` when the circuit is `not_designed`,
  `carries current` when `designed_verified`); the blanket `NOT CONNECTED` is gone.
- `connectivity` + `same_wire` **with the three-item `traced_path` matching L03's real shape**
  — items 0/1 render as the connected dashed pair (exactly one `stroke-dasharray`), item 2
  renders as its own unconnected labelled point under "Also find, on its own — not joined to
  the wire", neither dropped nor joined to the pair.
- `connectivity` + `enumeration` — every item its own labelled point, asserted by
  `"<line" not in svg`: no connecting line is drawn at all.
- `breadboard` — five-hole clip groups, the centre trench, the rail break and the safety inset.
- Unrecognized `map_kind` and a `connectivity` map with no `relationship` both raise
  `VisualMapError` rather than falling back to the generic chain.
- Evidence card reflects the fixture's own `child_records`, and the three hardcoded generic
  lines are asserted absent.
- All sixteen `visual_roles` strings L01-L04 declare classify to a renderer; an unknown role
  string fails closed.
- An unresolvable role writes a `BLOCKED` `acceptance.json` naming the role rather than
  raising, and ships no photograph at all rather than substituting one.

**PASS.**

---

## RIR-T04 — Fail-closed acceptance (§3, issue 002)

`python3 -m pytest tests/runtime/test_acceptance_gate.py -v` → **16 passed**. Fixtures:

| Test-plan fixture | Result |
| --- | --- |
| (a) raw-JSON body rejected | A populated field with no template branch is rejected at the gate (by `RendererError` or by schema validation, whichever fires first), and the shipped document is separately asserted free of serialized object syntax and of five literal field names. |
| (b) irrelevant image rejected by `PDF-ASSET-RESOLVES` | An asset swapped after the PDF shipped, with its receipt updated to the new bytes, produces `no image in the shipped PDF matches the receipted picture`. A receipt that stops resolving against the bytes on disk is separately confirmed to be a hard abort that writes no `acceptance.json` at all — the behaviour §2 explicitly preserves. |
| (c) undersized text rejected by `PDF-TEXT-LEGIBLE` | Regenerating L02's visuals with 12 px labels produces `text below 9.0pt` and a non-`ACCEPTED` terminal state. |
| (d) a check that cannot reach its subject | `PDF-VISUAL-REVIEW` records `NOT_RUN_BLOCKED` (never `PASS`) while the reviewer verdict is unfilled, and appears in `blocking_failures`. A filled verdict makes it `PASS`; a failed criterion makes it `FAIL` and the unit `BLOCKED`. |
| (e) cross-family bypass | With every blocking check passing, `terminal_state` is `ACCEPTED_PENDING_REVIEW`, never `ACCEPTED`. The disclosure string no longer co-exists with `ACCEPTED`. |
| (f) re-entry is opt-in | `finalize()` twice with `reentry_reason` on the second call succeeds; twice **without** it still raises `LogError`. The original `ACT` is closed exactly once, ever, and re-entry opens its own `action_kind: resume` record. |

Separately: `curricula/arduino_kit/checks.v1.yaml` validates against
`schemas/checks.schema.v1.json` with **0 errors**; `DOMAIN-VERIFIER` and
`VISUAL-ROLES-COMPLETE` are both present, both `stage: deterministic`, both advertised in the
**deterministic** row and in neither `static` row; `DOMAIN-VERIFIER` carries
`verified_by: FR-P5-VERIFIER-REQUIRED` and no `deferred`; `VISUAL-ROLES-COMPLETE` carries
`deferred: RT-5` and no `verified_by` — the exact wording rounds 8-10 converged on.

An id required of every unit but absent from its catalogue is a hard `CheckFailure`, tested.

**PASS.**

---

## RIR-T05 — L04 correction (§4, issue 004)

- `curricula/arduino_kit/arduino_kit_curriculum.v5.yaml:227` reads
  `- Current mode is never placed directly across a supply.`
- That sentence now appears **verbatim** in L04's rendered document at line 147 (child-facing,
  "In one sentence", from `domain.electrical.behaviour.child_level`), line 173 (child-facing,
  the misconception's `confronted_by`), and line 228 (adult-facing, inside
  `## Adult verification (adult only)` which starts at line 219). It is also in
  `safety.adult_verification.endpoint_check` and in the rewritten
  `curricula/arduino_kit/l04_multimeter_evidence.v1.json`'s `orientation`.
- Both removed universal claims are gone. Grep counts across
  `L04/workers/lab.json`, `L04/workers/domain.json`, `L04/document/L04.md` and
  `curricula/arduino_kit/l04_multimeter_evidence.v1.json`: `200 mA`/`200mA` = 0 except one
  meta-textual occurrence inside `content.sourced_claims[2].evidence_scope`, whose whole job
  is to record *why* the figure was removed; `10A socket`/`10 A socket` = 0;
  `shares one ... fuse` = 0. `ratings_and_limits` now carries three model-agnostic entries,
  none of which states a number, and socket selection is framed throughout as reading the
  meter's own labels and manual.
- The deterministic current-mode red-X visual resolves:
  `assets/current_mode_red_x.svg`, `role: safety_or_troubleshooting`,
  `supports_section: troubleshooting`, rendered from
  `domain.electrical.failure_modes[0]` ("Put the meter in current mode and place its two
  probes straight across a supply, one on each terminal."). Verified by eye on page 8 of the
  rasterized PDF: two boxes, the connection between them, and a heavy red X across it.
- `PDF-VISUAL-REVIEW` for L04 is recorded `PASS` with a filled verdict whose findings cover
  both required points explicitly: the statement is present and correctly worded, and no
  jack or threshold claim exceeding a cited source remains.

**PASS.**

---

## RIR-T06 — POE semantics (§5, issue 005)

`python3 -m pytest tests/runtime/test_poe_semantics.py -v` → **17 passed**.

- For each of L02/L03/L04, `observe.what_to_observe`, `evidence_fields`,
  `expected_observation`, `explain.what_you_saw` and the visuals' `supports_section` all name
  the same event (L02: clip + trench; L03: wire + expansion; L04: socket + dial).
- L02's `map_kind` is now `breadboard`; `what_to_observe` names the cutaway diagram; the
  evidence card records the five holes and the trench.
- L03's `relationship` is `same_wire` over a three-item `traced_path`; `what_to_observe`
  covers both the wire pair and the separately-located expansion row; `what_you_saw` no
  longer contains "not connected".
- L04's `relationship` is `enumeration`; the observation is reading the jack-and-dial diagram
  with the meter off; no live measurement.
- `test_no_explanation_asserts_a_result_the_steps_never_exposed` stems every content word in
  `what_you_saw` and requires it to appear in the steps, evidence fields, observation,
  expected observation, evidence-card records or named parts. This caught two real
  over-claims (L02's "unpowered", L03's "one piece of wire") which were corrected.
- The rejecting fixture — only the assembly map referenced, no `evidence_fields` — is
  rejected with both `poe-answer-map-only` and `poe-no-evidence-fields`. An uncommitted
  prediction is also rejected.

**PASS.**

---

## RIR-T07 — Source-claim entailment (§6, issue 006)

`python3 -m pytest tests/runtime/test_claim_entailment.py -v` → **13 passed**.

The four regression fixtures under `tests/fixtures/` resolve to their expected outcomes
through `checks.check_claim_entailment`:

| Fixture | Outcome |
| --- | --- |
| `unit_claim_wrong_device.reject.json` | rejected `claim-wrong-device` |
| `unit_claim_unsupported_number.reject.json` | rejected `claim-unsupported-number` |
| `unit_claim_out_of_scope_source.reject.json` | rejected `claim-locator-text-absent` |
| `unit_claim_valid_exact_model.accept.json` | accepted |

Their shared cached source lives at `tests/fixtures/unit_claim_source/sources/source_01.html`.
Adding the missing `derivation.premises` to the unsupported-number fixture flips it to
accepted, proving the derivation rule is what carries it.

Both L03 miscitations are resolved, checked by grepping the shipped worker JSON directly:

- **`absolute_max: 1 A` jumper rating.** Kept as a deliberately conservative planning limit
  and explicitly marked as derived: the rating's own `source` field now reads "Derived, not
  sourced… No cited source states a jumper-wire rating", and the matching `sourced_claims`
  entry carries four `derivation.premises` and an `evidence_scope` stating the cited text
  establishes only the 20 AWG gauge limit. The 1 A figure is no longer attributed to the 2 A
  source.
- **"expansion board is in the kit".** Scope-corrected. The string
  `breadboard expansion board` no longer appears anywhere the unit *asserts* something (it
  survives only inside the `sourced_claims` entry that records the correction). The item is
  now named as the kit's prototype shield and its expansion rows, visible in the kit
  photograph; the cited generic guide is used only for what a grouped row of holes does
  electrically, with `evidence_scope` stating it supports "nothing about which board ships in
  any particular kit".

Every shipped unit L01-L04 entails its own numeric claims against its own cached sources.

**PASS.**

---

## RIR-T08 — Run-level lifecycle (§7, issue 007)

`python3 -m pytest tests/runtime/test_run_state.py -v` → **13 passed**.

- A fixture reproducing the real shape (35-unit manifest, 4 attempted) reports `run_status`
  `IN_PROGRESS` — never `COMPLETE`/`ACCEPTED` — with exactly 31 `remaining_unit_ids` and
  `next_unit: L05`.
- A `BLOCKED` unit counts as attempted, not completed, and not remaining.
- `close_run` requires a stated reason and refuses `COMPLETE`; the schema independently
  refuses a stated stop with no `terminal_reason`, and refuses `COMPLETE` without workbook
  assembly or with units remaining.
- `assemble()` refuses `COMPLETE` at 4-of-35 coverage, writes the coverage receipt anyway,
  and leaves `run_status` unchanged; it also refuses when a completed unit has no shipped PDF.
- `assert_resumable` rejects a manifest-hash mismatch, a prompt-hash mismatch, a unit out of
  order, a run with no lifecycle record, and refuses to overwrite a unit already recording
  `ACCEPTED` *or* `ACCEPTED_PENDING_REVIEW`.
- §3's wiring is proven: `finalize()` alone updates `run_state.json`, with no separate call.

The real `outputs/arduino_kit_run_v2/run_state.json` now reads: `run_status: PARTIAL`,
`manifest_unit_count: 35`, `completed_unit_ids: [L02, L03]`, `blocked_unit_ids: [L01, L04]`,
31 `remaining_unit_ids`, `next_unit: L05`, `workbook_assembled: false`, a
`resumable_checkpoint` at L03, and a stated `terminal_reason`. It validates against
`schemas/run_lifecycle.schema.v1.json`.

**PASS.**

---

## RIR-T09 — Policy/curriculum check-inventory reconciliation (§8)

- `jsonschema` against `schemas/checks.schema.v1.json`: **0 errors** on `policy/checks.v1.yaml`
  and **0 errors** on `curricula/arduino_kit/checks.v1.yaml`.
- `tests/gates/fr_p4_policy_schemas.mapping_violations()` run directly over the merged
  inventory with the real `registry.py::GATES` and `policy/deferred.v1.yaml`: **0 problems**.
  `DOMAIN-VERIFIER` reports VERIFIED HERE; `LAB-SCHEMA-VALID`, `PDF-PAGE-COUNT`,
  `PDF-PAGE-NONBLANK`, `PDF-ASSET-RESOLVES`, `PDF-TEXT-LEGIBLE`, `PDF-VISUAL-REVIEW` and
  `VISUAL-ROLES-COMPLETE` all report MAPPED via `RT-5` — all six §8 ids keep
  `deferred: RT-5`; none was removed and no `verified_by` pointer to a call site was invented.
- Each of those six now carries a `note` naming its real production call site
  (`session_bridge.py`'s `finalize()` for the schema and page checks;
  `runtime/pdf_inspect.py::text_legible` / `assets_resolve` / `visual_review_template` for the
  three §3 newly wires in), each stating that `deferred: RT-5` stays because no registered
  gate verifies that call site.
- `TEXT-READABILITY-BAND`'s note is **corrected, not deleted**: it now states the check
  executes against real rendered child-facing text under `outputs/<run>/L0N/` via
  `runtime/checks.py::readability_problems`, *and* that `RT-7` remains unmet because its
  acceptance criterion names `curricula/<name>/units/`, which is still empty.
- `bash tests/run_gates.sh 2` → `FR-P2-GATEITEMS PASS (… 44 staged check ids)`, exactly the
  two ids this plan adds above the baseline's 42; phase totals unchanged at
  `14 PASS, 4 FAIL, 3 BLOCKED, 17 SKIPPED`.
- `bash tests/run_gates.sh 5` → `FR-P4-ALL-VALIDATE PASS (12 manifest→schema pairs)`; phase
  totals unchanged at `28 PASS, 5 FAIL, 5 BLOCKED, 0 SKIPPED`, with the identical five
  pre-existing FAILs. Nothing newly fails.
- `tests/gates/registry.py` and `tests/gates/gate_families.v1.yaml` are **byte-identical** to
  the `RIR-T00` copies (`diff -q`, and `git diff --stat` reports nothing).
- `tests/gates/fr_p5_unit.py` now *imports* all six of `syllables`, `grade_level`,
  `readability_violations`, `check_readability`, `bloom_flags`, `check_bloom_verbs` from
  `runtime/readability.py` and defines none of them locally (confirmed via
  `fr_p5_unit.<name>.__module__ == 'runtime.readability'` for all six). The gate bodies take
  their harness dependencies through `bind_gate`, so `runtime/` gains no dependency on
  `tests/`. All five of its own checks still pass unchanged: `FR-P5-READABILITY PASS`,
  `FR-P5-BLOOM-VERBS PASS`, `FR-P5-DERIVATION PASS`, `FR-P5-RECEIPT-HASH PASS`,
  `FR-P5-UNIT-CONTRACT PASS`, each with the same fixture verdicts as at baseline.

**PASS.**

---

## RIR-T10 — Regenerate and re-accept L01-L04 (§9)

Asset SHA-256 diffed against `RIR-T00`'s captured bytes — **all six changed**, so
`regenerate_assets()` genuinely ran:

| Asset | Before → after |
| --- | --- |
| `L02/assets/path_map.svg` | `2e5d5dc54206` → `196c13928608` |
| `L02/assets/evidence_card.svg` | `904413d26c72` → `1d94c55818dd` |
| `L03/assets/path_map.svg` | `52bf8477b207` → `3f3f763d885a` |
| `L03/assets/evidence_card.svg` | `4d12a6e8099e` → `91e5b56aa3c3` |
| `L04/assets/path_map.svg` | `b4579fa09fcf` → `1f93bcc74ef5` |
| `L04/assets/evidence_card.svg` | `507a27f66c76` → `ed24474f071a` |

The shipped asset set is now role-driven rather than a single reused inventory shot:

- L01 — `photo_kit_inventory.jpg`, `path_map.svg`, `evidence_card.svg`
- L02 — `photo_breadboard.jpg`, `cutaway_clip_illustration.svg`, `path_map.svg`,
  `rail_break_warning.svg`, `evidence_card.svg`
- L03 — `photo_jumper_wires.jpg`, `connection_endpoint_diagram.svg`, `path_map.svg`,
  `loose_wire_hazard.svg`, `evidence_card.svg`
- L04 — `probe_placement_diagram.svg`, `path_map.svg`, `current_mode_red_x.svg`,
  `evidence_card.svg` (and **no** photograph: the meter role is unresolved)

`official_reference.jpg` — the whole-kit shot previously substituted into every unit — is
gone from L02, L03 and L04.

Each `results/unit_checks.json` lists **all ten** required check ids with an explicit
`PASS`/`FAIL`/`NOT_RUN_BLOCKED` and a reason, plus both `checks_version` values
(`{engine: "1.0", curriculum: "1.0"}`). The hardcoded four-key dict is gone, and the invented
`DOMAIN-SCHEMA-VALID` id it contained is not reintroduced.

`run_state.record_unit_transition` fired inside `finalize()` for each unit; no separate call
was made.

### Terminal states — matching what `RIR-T01` actually found

| Unit | `terminal_state` | Why |
| --- | --- | --- |
| **L01** | `BLOCKED` | `VISUAL-ROLES-COMPLETE` FAIL — `safe disconnected setup photograph` unresolved, exactly as `RIR-T01` recorded. Also `TEXT-READABILITY-BAND` FAIL (below). |
| **L02** | `ACCEPTED_PENDING_REVIEW` | Every blocking check passed — `RIR-T01` found the breadboard croppable, so its photographic role resolved — and the cross-family judge bypass forbids `ACCEPTED`. |
| **L03** | `ACCEPTED_PENDING_REVIEW` | Same: `RIR-T01` found the wire detail croppable, all blocking checks pass, bypass forbids `ACCEPTED`. |
| **L04** | `BLOCKED` | `VISUAL-ROLES-COMPLETE` FAIL — `photorealistic meter` unresolved, exactly as `RIR-T01` recorded. |

No unit reports `ACCEPTED`: the cross-family bypass is present on all four, so `ACCEPTED` is
unreachable for this run by design.

### Direct visual inspection of the rasterized PDFs

Every page of all four units was inspected at 200 dpi (L01: 8 pages; L02, L03, L04: 9 pages
each). All four read as prose with subject-appropriate visuals placed beside the sections
they support. L04 states the current-mode safety rule directly to both audiences. Two real
rendering defects were found by eye and fixed before the final pass:

1. **Missing-glyph tick boxes.** Pandoc rewrote a leading `- [ ]` into a task-list glyph the
   shipped Helvetica has no character for, so every checkbox printed as a tofu box. Escaping
   the brackets does not help — pandoc strips the escapes and converts anyway. Fixed by
   rendering `[_]`, which pandoc leaves alone and which prints cleanly.
2. **Overlapping labels in the breadboard cutaway.** The "power rail", "top half" and
   "bottom half" labels collided with the hole rows. Fixed by giving each its own baseline.

A third issue was found and fixed while inspecting: L03's "map to follow" prose listed the
three traced points flatly, while the map drew the first two as one wire. `domain_fact_lines`
now renders the `same_wire` relationship in the prose too, so prose and map cannot disagree
(`unit_prose.v1.md:55`).

The recorded `PDF-VISUAL-REVIEW` verdicts under each unit's `review/visual_review.json` carry
one answered line item per page and per visual, the reviewer's identity, an explicit note
that this is a recorded human-equivalent verdict rather than automated computer vision, and
per-unit findings.

**PASS** — asset hashes changed; every `unit_checks.json` entry is explicit; every
`terminal_state` matches what `RIR-T01` actually found; the rasterized PDFs pass direct
inspection.

---

## RIR-T11 — Full verification-sequence replay

1. `python3 -m pytest tests/runtime/ -v` → **166 passed, 14 subtests passed**. Every new
   suite (`test_lesson_render.py` 28, `test_visual_maps.py` 32, `test_acceptance_gate.py` 16,
   `test_poe_semantics.py` 17, `test_claim_entailment.py` 13, `test_run_state.py` 13) and
   every pre-existing suite (`test_checks.py`, `test_controller.py`, `test_capabilities.py`,
   `test_gemini.py`, `test_logger.py`, `test_retry.py`, `test_routing.py`,
   `test_run_curriculum.py`) passes. Against the `RIR-T00` baseline of 0 passing this is a
   strict improvement in every direction.
2. `bash tests/run_gates.sh 2` and `bash tests/run_gates.sh 5` (the plan's own text names
   `tests/gates/run_gates.sh`, which does not exist; the real runner was used) — see
   `RIR-T09`. The fixture-gate suite still passes after the `readability`/`bloom` extraction.
3. The L01-L04 inspection from `RIR-T10` — done.
4. `run_state.json` inspection from `RIR-T08` — done.
5. The L04 diff from `RIR-T05` — done.

**PASS.**

---

## RIR-T12 — Regression: scope boundary held

- **No path outside L01-L04 and run-level state changed.** `outputs/` is gitignored, so this
  was checked by re-hashing every file under `outputs/arduino_kit_run_v2/` and comparing to
  `RIR-T00`'s capture: the only run-root change is the new `run_state.json` (mtime 2026-08-08).
  `execution_log.jsonl`, `meta_execution_state.json`, `results/gate_0_logger.json`,
  `results/gate_1_static_preflight.json`, `QA/arduino_kit_run_v2.qa_report.v1.md` and the two
  logger dotfiles all retain their original 2026-08-02/03 mtimes and contents. `L05`-`L35`
  were never generated and no directory for them exists.
- **No schema-validation regression for a unit this plan does not regenerate.** There is no
  such unit: `curricula/arduino_kit/units/` is empty and `outputs/arduino_kit_run_v2/`
  contains only L01-L04. All four regenerated units validate against both amended schemas
  with 0 errors, and the copied verifier accepts all four domains. The Stop condition on
  schema breakage was therefore never triggered.
- **`policy/deferred.v1.yaml` is byte-identical** to the `RIR-T00` copy.
- `tests/gates/registry.py` and `tests/gates/gate_families.v1.yaml` byte-identical.

**PASS.**

---

## RIR-T13 — Result file and log entry

This file exists and records the `RIR-T00` baseline, every changed/created/deleted path per
phase, the `RIR-T01` disposition for L02/L03/L04 (and L01), full test results for every suite
in the Verification sequence, and the remaining failures with their causes. The execution
outcome was appended to `plans/runtime_integrity_remediation/plans.log.md` as a new entry,
below the round-10 QA and final-audit entries, with no existing entry edited or removed.

**PASS.**

---

## Changed, created and deleted paths, by phase

Nothing was deleted. `git add`/`git commit` were not run; everything is an inspectable
working-tree diff.

**§1 renderer (issue 001)**
- created `runtime/lesson_render.py`
- created `tests/runtime/test_lesson_render.py`
- modified `runtime/session_bridge.py` — `_markdown()` delegates to `render_unit`; the
  `json.dumps` block and the `_svg` generic renderer are gone

**§2 visual pipeline (issue 003)**
- created `runtime/visual_maps.py`
- created `curricula/arduino_kit/verified_photo_regions.v1.json`
- created `tests/runtime/test_visual_maps.py`
- modified `curricula/arduino_kit/domain.schema.v1.json` — `relationship` enum on
  `unpowered_path_map`, required when `map_kind: connectivity`
- modified `runtime/session_bridge.py` — `prepare()` calls `regenerate_assets()` instead of
  globbing for a photo and stacking rows into an SVG

**§3 fail-closed acceptance (issue 002)**
- created `runtime/readability.py`, `runtime/pdf_inspect.py`
- created `tests/runtime/test_acceptance_gate.py`, `tests/runtime/unit_fixture.py`
- modified `runtime/checks.py` — `required_checks_for`, `readability_problems`,
  `bloom_report`; `check_derivation` reads `content.derived`
- modified `runtime/session_bridge.py` — `finalize(..., reentry_reason=, curriculum=)`, the
  computed check set, the bypass rule, the `BLOCKED` rule, the `run_state` wiring, the
  `document/` clear-and-recreate
- modified `curricula/arduino_kit/checks.v1.yaml` — `DOMAIN-VERIFIER`,
  `VISUAL-ROLES-COMPLETE`, and both added to the deterministic `release.advertises` row
- modified `schemas/lab.schema.v4.json` — `content.derived[]`,
  `content.unresolved_visual_roles[]`
- modified `tests/gates/fr_p5_unit.py` — imports the six shared functions

**§4 L04 correction (issue 004)**
- modified `curricula/arduino_kit/l04_multimeter_evidence.v1.json`
- modified `outputs/arduino_kit_run_v2/L04/workers/{lab,domain}.json`

**§5 POE (issue 005)**
- created `tests/runtime/test_poe_semantics.py`
- modified `curricula/arduino_kit/domain.schema.v1.json` — `evidence_card` on
  `breadboard_build_map`
- modified `outputs/arduino_kit_run_v2/L02,L03,L04/workers/{lab,domain}.json`

**§6 source-claim entailment (issue 006)**
- created `tests/fixtures/unit_claim_wrong_device.reject.json`,
  `unit_claim_unsupported_number.reject.json`, `unit_claim_out_of_scope_source.reject.json`,
  `unit_claim_valid_exact_model.accept.json`, `tests/fixtures/unit_claim_source/`
- created `tests/runtime/test_claim_entailment.py`
- modified `runtime/checks.py` — `check_claim_entailment`
- modified `schemas/lab.schema.v4.json` — `content.sourced_claims[]`
- modified `outputs/arduino_kit_run_v2/L01,L02,L03,L04/workers/lab.json`

**§7 run-level state (issue 007)**
- created `schemas/run_lifecycle.schema.v1.json`, `runtime/run_state.py`,
  `runtime/workbook.py`, `tests/runtime/test_run_state.py`
- created `outputs/arduino_kit_run_v2/run_state.json`

**§8 inventory reconciliation**
- modified `policy/checks.v1.yaml` — notes on six ids, corrected `RT-7` note
- modified `tests/gates/fr_p5_unit.py`

**§9 regeneration**
- modified, for each of L01-L04: `inputs/*` (re-frozen), `input_freeze.json`,
  `interrupt_receipt.json`, `workers/{lab,domain}.json`, `assets/*`, `document/*`,
  `results/unit_checks.json`, `acceptance.json`, `execution_log.jsonl`
- created, for each of L01-L04: `review/visual_review.json`, `results/pdf_images/`

**Out-of-plan (see Deviations)**
- created `tests/__init__.py`

---

## Deviations from the plan, and why

1. **`tests/__init__.py` (new, one line).** `RIR-T00` found the entire `tests/runtime/` suite
   uncollectable: `tests/runtime/__init__.py` makes `tests.runtime` importable as `runtime`
   once pytest inserts `tests/` at `sys.path[0]`, shadowing the production package. Without a
   fix, the plan's Verification-sequence step 1 and tests `RIR-T02`-`RIR-T08` and `RIR-T11`
   could not run at all. Three candidate fixes were tried in a `/tmp` scratch copy;
   `--import-mode=importlib` does not help and deleting `tests/runtime/__init__.py` is
   destructive, so the additive one-file fix was taken. It changes no gate outcome.
2. **`curricula/arduino_kit/verified_photo_regions.v1.json` (new).** §2 requires the resolver
   to find "a verified asset whose provenance already names the exact subject", and §9 step 0
   requires a recorded human verification. Something machine-readable had to hold the outcome
   of `RIR-T01` so the resolver could act on it and so the crops stay reproducible. This file
   is that record. It is a curriculum data file, not a schema, catalogue or gate.
3. **`content.derived[]` and `content.unresolved_visual_roles[]` sit under `content`, not at
   the top level.** They were first added top-level, which flipped the real, registered
   `FR-P5-UNIT-CONTRACT` gate from PASS to FAIL: that gate asserts the unit contract's
   top-level block set is *exactly* the six engine blocks plus `domain`, and a seventh
   top-level block is the `G1` defect it exists to catch. Moving both under `content`
   restores it to PASS. `check_derivation` accepts either location so the gate's own
   pre-existing top-level fixtures keep working.
4. **`PDF-TEXT-LEGIBLE` measures the nominal size, not the raw ink box.**
   `pdftotext -bbox-layout` reports each line's ink extent, which is smaller than the type
   size. The ratio was measured against this repository's own pandoc/typst/Helvetica
   toolchain at 8, 9, 11 and 14 pt and is a constant 0.92, recorded as `_INK_BOX_RATIO`. This
   is a measurement, not an assumption.
5. **`check_claim_entailment` requires a sourced claim for numeric strings, not for all
   prose.** The plan says "every numeric or safety-critical string in
   `safety.adult_verification.limits`/`endpoint_check` and in `domain` electrical ratings".
   Coverage is scoped to strings that actually state a number, in both locations. Prose with
   no number is the unit's own instruction to a learner, and demanding a citation for it
   would make the check a formality. Every claim entry is still fully validated for locator
   resolution, subject scope and derivation regardless of numbers.

---

## Remaining failures, with their exact cause

Two checks remain non-`PASS`, and both are honest findings rather than incomplete work.

1. **`VISUAL-ROLES-COMPLETE: FAIL` on L01 and L04.** This is the plan's own expected outcome
   and `RIR-T01`'s recorded finding. `official_kit_photo.jpg` contains no multimeter (L04's
   `photorealistic meter`) and is an inventory flat-lay rather than a photograph of an
   assembled disconnected setup (L01's `safe disconnected setup photograph`). Both units are
   `BLOCKED` and say so on their own last page. **Clearing this needs a human with the
   physical kit to take two photographs.** The plan explicitly forbids acquiring them, and
   none was acquired.
2. **`TEXT-READABILITY-BAND: FAIL` on L01** — the rendered child-facing text scores 6.74
   Flesch-Kincaid against the band `[2, 6]` declared in `policy/calibration.v1.yaml`. This is
   pre-existing L01 prose that this plan does not authorize rewriting (§9: "regenerating
   net-new pedagogical content beyond fixing the named defects is out of scope"), surfaced
   for the first time because this plan is what made the check execute against real generated
   text. L02 scores 5.43, L03 5.34 and L04 5.90, all inside the band. L01 is `BLOCKED`
   independently on its photographic role, so this does not change its terminal state.
   Clearing it means simplifying L01's prose, which is a content task for a later pass.

One non-reproducible observation, recorded rather than hidden: during a batch in which a
concurrent `pytest` invocation was killed by a command timeout (exit 143), a single run of
`tests/runtime/` reported one failure and one error in `test_acceptance_gate.py`. Six
subsequent runs — three of that file alone and three of the full suite — all passed, the
renderer was confirmed deterministic for the same input, and the shipped `L02.md` contains
zero brace characters. The most probable cause is the killed concurrent process. It is
recorded here because the alternative, silently re-running until green, is the behaviour this
plan exists to end.
