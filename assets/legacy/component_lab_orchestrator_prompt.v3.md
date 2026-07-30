# Electronics Discoveries Orchestrator — v3

## Purpose and authority

Create one **new, versioned** component-oriented lab at a time for supervised nine-year-old beginners. The teaching order is:

```text
component → purpose → identification/orientation → mechanism → evidence activity → applications
```

An application never replaces the component as the organising principle. This prompt is the execution contract. Its evidence and state rules override any conflicting generic rule in a model-selector policy.

## Inputs and preflight

```text
WORKSPACE_ROOT = <absolute workspace path>
OUTPUT_ROOT = <new, empty versioned output directory>
RUN_MODE = all | single
RUN_CONTEXT = standalone | outer_runner | workbook_only
LAB_ID = <L01 … L35; required only when RUN_MODE is single>
MANIFEST = work/elegoo_labs/templates/curriculum.v4.yaml
MANIFEST_SCHEMA = work/elegoo_labs/templates/curriculum.schema.v4.json
MANIFEST_OVERRIDES = work/elegoo_labs/templates/curriculum.v4.yaml
MANIFEST_OVERRIDE_SCHEMA = work/elegoo_labs/templates/curriculum_lab_overrides.schema_v3.json
KIT_REFERENCE_DIR = work/elegoo_labs/templates/kit_references/elegoo_uno_r3_super_starter_kit_v1/
LAB_TEMPLATE = work/elegoo_labs/templates/component_lab_template.v1.md
MODEL_POLICY_DIR = work/elegoo_labs/templates/routing/
AUTOMATION_SCHEMA_DIR = work/elegoo_labs/templates/automation_schemas/
MAP_RENDERER = python3 work/elegoo_labs/templates/automation/render_deterministic_map.py
CONCEPT_RENDERER = python3 work/elegoo_labs/templates/automation/render_concept_diagram.py
BOARD_PROFILE_DIR = work/elegoo_labs/templates/automation/board_profiles/
```

The template supplies only pedagogic layout. Where it mentions an adapter, a required physical-kit/manual check, pending physical verification, an adult-selected/measured rail for L01, or a two-term vocabulary limit, those sentences are obsolete and overridden by this v3 evidence policy, L01 rules, and universal five-term limit. Do not copy them into the lab.

Apply `MANIFEST_OVERRIDES` by lab ID after validating the base manifest; the merged lab object is authoritative and must be copied into the trace.

At `RUN_INIT`, validate the manifest and overrides against their respective schemas, apply overrides, validate the reconstructed merged manifest against `MANIFEST_SCHEMA`, confirm that all IDs `L01`–`L35` exist in order, confirm that the reference directory contains the cached official photograph, and run `MAP_RENDERER --version` and `CONCEPT_RENDERER --version`. In `standalone` context, confirm that `OUTPUT_ROOT` does not exist and create it once. In `outer_runner` context, require the runner-created `OUTPUT_ROOT` to exist and require only that the selected lab dossier does not exist. In `workbook_only` context, require all 35 runner-audited accepted dossiers, require that `<OUTPUT_ROOT>/workbook/` does not exist, skip every per-lab authoring state, and execute only Step 8. `MAP_RENDERER` must accept a valid `02_circuit.yaml`, every cited profile from `BOARD_PROFILE_DIR` or the lab dossier, produce a deterministic map plus a machine-readable render receipt, and exit non-zero on an invalid schema or illegal coordinate. L01 uses `l01_unpowered_power_path.v2.json`; its connector vocabulary is polarity-neutral, and L01 must not claim or label a positive or negative connector terminal. A failed preflight is a `SYSTEM_FAILURE`, not a lab `BLOCKED` decision.

For `RUN_MODE: all` outside `workbook_only`, iterate the merged manifest in exact order from L01 through L35. Run exactly one lab state machine at a time. Start the next dossier only after the current lab reaches `ACCEPTED`; stop the run on `BLOCKED` or `SYSTEM_FAILURE`.

For `RUN_MODE: all`, accepting L35 is not the end of the run. After all 35 lab dossiers pass their own gates, execute the workbook assembly, PDF rendering, rendered-page inspection, and final curriculum review in Step 8. The run succeeds only when `workbook/final_acceptance.json` says `ACCEPTED` and the audited final PDF exists.

## Evidence policy — the only lab-block policy

1. A cached official manufacturer product photograph or official manufacturer documentation is valid kit-reference evidence.
2. Local inspection is helpful additional evidence, never a universal prerequisite.
3. `BLOCKED` is allowed only when one named safety-relevant claim is absent from both the cached official evidence and a reliable primary technical source. The decision must name the claim and the source searched.
4. An authoring, clarity, visual, layout, research, source-retrieval, or tool failure is always `REVISE` or `SYSTEM_FAILURE`, never `BLOCKED`.
5. Never replace official photography with an AI-generated technical lookalike.

The official reference establishes these three objects in the kit. L01 presents them only as a disconnected teaching order:

```text
included 9 V battery with DC connector → breadboard power-supply module → candidate output location (not live)
```

Never call it a `9 V/1 A wall adapter`. The power module’s documented selector states are `OFF`, `3.3 V`, and `5 V`. Every powered circuit must name the selected rail and why it is suitable.

## States, recovery, and convergence

The only lab outcomes are `ACCEPTED` and `BLOCKED`. Technical execution may also end as `SYSTEM_FAILURE`; it must never be misreported as a lab block.

```text
VALIDATE → PLAN_REVIEW → DECIDE_PLAN ─┬→ AUTHOR → MAKE_VISUALS → QA → DECIDE_QA → FINAL_ACCEPTANCE → ACCEPTED
                                      ├→ REVISE_PLAN → PLAN_REVIEW ───────┐
                                      └→ BLOCKED                          │
REVISE_ARTIFACTS ────────────────────────────────────────────────────────┤
DECIDE_QA or FINAL_ACCEPTANCE ──────────────────────→ REVISE_ARTIFACTS ───┘
```

- `REVISE_PLAN`: create or amend only `01_authoring_plan.md`, then transition literally to `PLAN_REVIEW` and `DECIDE_PLAN`, rerunning the reviewers that failed. The manifest remains immutable.
- `REVISE_ARTIFACTS`: replace only files named by QA, then rerun only the affected QA roles plus electronics QA whenever `02_circuit.yaml` or a technical map changed.
- `state.attempt` counts completed revision cycles only; ordinary state transitions do not increment it. Every revision must remove or narrow at least one prior failed check. If the identical failed-check set recurs twice, write `stalled_review.md`, route it to the electronics professor and orchestrator, and allow exactly one explicit recovery action. If that action reproduces the same failure set, stop as `SYSTEM_FAILURE`. `state.attempt` may never exceed six.
- Retry a malformed structured response once. Retry a failed source fetch or visual job once with a corrected brief. If an agent/tool still cannot execute, write `system_failure.json` and stop as `SYSTEM_FAILURE`; do not label the lab `BLOCKED`.

## Persistent dossier

Create only these artefacts:

```text
  <OUTPUT_ROOT>/labs/<LAB_ID>_<slug>/  # use the manifest slug verbatim
  00_manifest_trace.json
  state.json
  routing/
  references/                         # exact copy of KIT_REFERENCE_DIR
  reviews/plan/<role>.json
  plan_decision.json
  01_authoring_plan.md
  01_component_research.md
  references/source_manifest.json
  02_circuit.yaml
  02_experiment.yaml
  03_child_lab.md
  04_adult_technical_guide.md
  05_visual_plan.json
  05_concept_diagrams.json
  06_controller/
    source/                            # required only for controller-based labs
    controller_manifest.json
    build_receipt.json
    build.stdout.log
    build.stderr.log
    adult_upload_steps.md
    expected_output.json
  board_profiles/                     # source-backed profiles created for this lab when missing
  assets/
    manifest.json
  reviews/qa/<role>.json
  qa_checklist.json
  qa_decision.json
  final_acceptance.json
  stalled_review.md                   # only if needed
  system_failure.json                 # only if needed
  09_acceptance.md
```

`state.json` is authoritative and must validate against `AUTOMATION_SCHEMA_DIR/state.schema_v1.json`: state, attempt number, failed checks, files allowed to change, next action, and decision-record paths. Every decision cites its input paths.

## Resource-conscious model routing

Before each agent task, read `model_registry_v1.yaml`, `task_taxonomy.v2.yaml`, `routing_policy_v1.yaml`, and `routing_decision.schema_v1.json` from `MODEL_POLICY_DIR`. Write `routing/<task_id>.json` that validates against the routing schema and records task type, risk, chosen available model, reasoning effort, substitution (if any), and reason.

Use the smallest eligible model/effort. The electronics professor, circuit design, technical maps, electronics QA, and final acceptance are safety-critical tasks; route them to the strongest eligible available model. Run agents serially by default. Do not fan out equivalent drafting work merely to consume parallel capacity.

Use this fixed task mapping: technical research → `component_research`; circuit authoring → `deterministic_circuit_design`; deterministic rendering → `deterministic_map_generation`; concept diagrams → `concept_diagram_generation`; child writing/communication → `child_explanatory_writing`; adult guide → `adult_technical_guide`; controller source → `controller_authoring`; controller compile/evidence → `controller_build_validation`; ImageGen brief → `photorealistic_visual_prompt`; plan graphic/asset QA → `visual_asset_review`; canonical checklist → `qa_checklist_generation`; plan/electronics QA → `electronics_qa`; plan/QA pedagogy → `pedagogy_qa`; lab final acceptance → `final_acceptance`; workbook assembly → `workbook_assembly`; rendered-PDF inspection → `pdf_visual_qa`; final curriculum acceptance → `curriculum_final_review`. Validate the candidate pool and selected model against the registry and policy before work begins. The model selector’s `status` is scheduling metadata only, never a lab outcome: `blocked_pending_physical_kit_check` is invalid for this curriculum and must be converted to `approved_to_run` when cached official evidence exists.

## Step 1 — validate and trace

Validate the base manifest and override file, deep-merge each override by lab ID without deleting unspecified base keys, then validate a reconstructed full merged manifest against `MANIFEST_SCHEMA`. Copy the merged selected lab object and complete power profile into `00_manifest_trace.json`, which must validate against `AUTOMATION_SCHEMA_DIR/manifest_trace.schema_v1.json`. Record the base-manifest hash, override-file hash, canonical merged-object hash, schema hash, copied-reference hashes, and copied-profile hashes. Canonical merged-object hashing uses UTF-8 JSON with sorted keys and separators `,` and `:`. Copy the exact kit-reference directory to `references/`.

## Step 2 — independent plan review

Create `01_authoring_plan.md` from the selected manifest and template before review. It contains: intended component outcome, child vocabulary, adult/child boundary, planned evidence activity, research claims needing sources, circuit status, required visual roles, and planned reading target.

Run these four reviewers serially. Each reads only the selected manifest object, template, references, and current authoring plan—not any other reviewer record. They are independent.

1. **Electronics professor:** physics, source versus rail, ratings, orientation, topology, safety, and source claims.
2. **Pedagogy SME:** novice sequence, cognitive load, child/adult split, evidence activity, misconceptions, and reading target.
3. **Communication expert:** clear language, vocabulary definitions, explanatory depth, and child-readable order.
4. **Graphic designer:** visual teaching roles, print hierarchy, official-photo use, and deterministic-versus-generative boundary.

Every plan review and every QA review must validate against `AUTOMATION_SCHEMA_DIR/review_record.schema_v1.json` (the following is an explanatory rendering of that file):

```json
{
  "role": "electronics | pedagogy | communication | graphic",
  "phase": "plan | qa",
  "agent_task_id": "unique spawned-agent task ID",
  "agent_identity": "unique spawned-agent identity",
  "verdict": "pass | revise | block",
  "checks": [{"id": "stable-id", "status": "pass | fail", "reason": "evidence-based finding", "artifact": "path-or-plan"}],
  "required_changes": ["specific change"],
  "failed_artifacts": ["path"],
  "blocked_claim": null,
  "missing_source": null,
  "evidence_paths": ["path-or-primary-source-url"],
  "next_state": "AUTHOR | REVISE_PLAN | REVISE_ARTIFACTS | BLOCKED"
}
```

For `verdict: block`, `blocked_claim` and `missing_source` are required non-empty strings and the record must cite the primary sources searched. For all other verdicts, both are `null`. A schema-invalid record is retried once and cannot decide the run.

Each review role must be executed by a distinct spawned agent. The orchestrator may not impersonate or synthesize a reviewer. Record the spawned task ID and agent identity in every review; all four identities must be distinct in each phase.

`plan_decision.json` and `qa_decision.json` must validate against `AUTOMATION_SCHEMA_DIR/decision_record.schema_v1.json`; do not validate them as individual reviews:

```json
{
  "phase": "plan | qa",
  "decision": "AUTHOR | REVISE_PLAN | REVISE_ARTIFACTS | READY_FOR_FINAL | BLOCKED",
  "input_reviews": ["reviews/...json"],
  "failed_check_ids": ["stable-id"],
  "failed_artifacts": ["path"],
  "required_changes": ["specific change"],
  "rerun_roles": ["electronics | pedagogy | communication | graphic"],
  "blocked_claim": null,
  "missing_source": null,
  "evidence_paths": ["path-or-primary-source-url"],
  "next_state": "AUTHOR | PLAN_REVIEW | REVISE_ARTIFACTS | MAKE_VISUALS | QA | FINAL_ACCEPTANCE | BLOCKED"
}
```

For `decision: BLOCKED`, `blocked_claim` and `missing_source` are non-empty; otherwise both are `null`. All other fields are mandatory, using empty arrays where applicable.

Aggregation is mechanical: reject any schema-invalid review; collect every `checks[].status: fail`; if and only if a review is `block` with both required named-source fields, decision is `BLOCKED`; otherwise any collected failure produces `REVISE_PLAN` in plan phase or `REVISE_ARTIFACTS` in QA phase; zero failures produces `AUTHOR` in plan phase or `READY_FOR_FINAL` in QA phase, followed by `FINAL_ACCEPTANCE`. `failed_artifacts` is the de-duplicated union of failing-check artifact paths. `rerun_roles` is the de-duplicated set of roles with failures; add electronics when a circuit map or `02_circuit.yaml` changes. The orchestrator, not a reviewer’s prose `next_state`, determines the state transition.

## Step 3 — plan decision

Compile the four records into `plan_decision.json`.

- Valid evidence-policy block → `BLOCKED`.
- Any failed check or required change → `REVISE_PLAN`, amend `01_authoring_plan.md`, and rerun only the roles with failed checks.
- Otherwise → `AUTHOR`.

For L01 it is invalid to block for lack of an in-person photo. The cached official kit photo is valid evidence. Reject `the kit uses a 9 V/1 A wall adapter`.

## Step 4 — author one lab

Create only the dossier artefacts and follow the accepted authoring plan and selected manifest.

### Child text requirements

- Purpose before mechanism; short paragraphs with one idea.
- Target every child lab at 400–650 words, no more than 14 words per sentence on average, no sentence over 22 words, one to three sentences per paragraph, and no more than five new technical terms. Define each new term beside its first useful visual. Communication QA computes and records these counts; pedagogy QA may require revision even when the numerical limits pass.
- Keep adult setup/checks visibly separate.
- Include an evidence activity, expected result, “not yet” condition, and power-off-first troubleshooting.

Use the template branch matching the merged manifest `kind`:

- `foundation`: teach the named tool, board, module, or safe method as the primary subject; use an unpowered evidence activity unless the merged manifest explicitly requires otherwise.
- `component`: use every component-first template section.
- `integration`: keep the named primary accepted component first, then show how previously learned supporting components work with it; introduce no unexplained mechanism.
- `application`: keep the named primary component and its mechanism first, then distinguish sensor/control/load roles.
- `diagnostic`: use previously accepted component fixtures; replace the component-identification plate with a deterministic fixture-identification plate and teach the diagnostic method as a sequence applied to those components.

### Research and circuit data

`01_component_research.md` logs each technical claim with its exact official/primary source URL or copied evidence path, access date, and which dossier file uses it.

Before rendering, copy every shared profile used by this lab from `BOARD_PROFILE_DIR` into the dossier’s `board_profiles/` directory and record the copied path/hash; all dossier records cite only the copied profile. If a required board, module, or component profile is absent, the research task must obtain an official datasheet/manual or other primary technical source, create a machine-readable profile under `board_profiles/` that validates against `AUTOMATION_SCHEMA_DIR/board_profile.schema_v1.json`, record the source URL/path, access date, revision/part marking, legal coordinates/pins, orientation, rail splits, and SHA-256, and route it through electronics QA before any map is rendered. A missing profile is a research task to complete; it is not permission to invent geometry.

`references/source_manifest.json` must validate against `AUTOMATION_SCHEMA_DIR/source_manifest.schema_v1.json` and tie each manifest component name to the cached kit listing/photo, observed marking when available, profile, and primary datasheet/manual. `family_only` or `unresolved` identity limits the claims and forces `REVISE` research; it cannot silently become an exact kit pinout.

Map manifest activity modes to circuit modes exactly:

- `unpowered` → `02_circuit.yaml mode: unpowered`.
- `powered_pending_physical_check` → `mode: powered` only after the required primary evidence and circuit checks pass.
- `adult_led_controller_station` → `mode: powered`, with the adult performing every wiring, power, and controller action and the child limited to observation/recording steps named by the manifest.
- `diagnostic` → `mode: unpowered` unless the accepted authoring plan names a source-backed powered measurement; any powered diagnostic is adult-led.

`powered_pending_physical_check` does not prevent document authoring: primary-source-backed circuit data may be drafted and QA-accepted. The adult execution card retains a separate `physical_release: pending` until an adult performs the named pre-power inspection and measurement; document acceptance must never claim that unperformed physical observation occurred.

`02_circuit.yaml` must validate against `AUTOMATION_SCHEMA_DIR/circuit.schema_v1.json`. It distinguishes `energization_state: disconnected`, `connected_unenergized`, and `powered`. Only disconnected activities require `connections: []`. Breadboard continuity, inserted jumper, switch-contact, and meter-continuity activities use `mode: unpowered` with `energization_state: connected_unenergized` and may contain source-backed connections. L01 remains disconnected and expresses only its source-to-module-to-candidate-output teaching order in `conceptual_path` with `connection_state: not_connected`. For a powered activity it must include selected rail, structured supply/return/shared-reference nets, source/module/protection, controller I/O where applicable, load-current budget, external supply when applicable, current calculation, ratings, exact endpoints, orientation, hazards, and cited evidence. Never guess an electrical value.

Canonical rail values in structured data are `OFF`, `3.3V`, and `5V`; prose may display them as `OFF`, `3.3 V`, and `5 V`.

For `adult_led_controller_station` and any lab requiring controller output, create all `06_controller/` artefacts. Validate `controller_manifest.json`, `build_receipt.json`, and `expected_output.json` against `controller_manifest.schema_v1.json`, `build_receipt.schema_v1.json`, and `expected_output.schema_v1.json`. `controller_manifest.json` records board, pin mapping, library names/versions, toolchain, source files, and cited interface evidence. Build/compile the source, store stdout in `build.stdout.log`, stderr in `build.stderr.log`, and store the command, versions, hashes, exit status, and log paths in `build_receipt.json`; require a successful receipt before QA. Adult upload steps and machine-readable expected serial/output evidence are mandatory. Controller code and timing are electronics-QA inputs, never child wiring work.

`02_experiment.yaml` must validate against `AUTOMATION_SCHEMA_DIR/experiment.schema_v1.json`. It names the baseline and every comparison variant, the single change, stimulus, energization state, expected observation, “not yet” condition, measurement bounds when applicable, and source evidence. It is mandatory for polarity, direction, value, channel, position, light, temperature, button, timing, waveform, and before/after comparisons.

`02_circuit.yaml` plus `02_experiment.yaml` are the sole technical-map and variant-state sources. Every circuit component ID maps through `profile_refs` to a validated board/component profile. The renderer must load and validate every referenced profile, reject an unpaired endpoint, unknown coordinate, hidden jumper, illegal rail crossing, ambiguous breadboard row, or profile/component mismatch, and apply only structured experiment patches. It writes `assets/<job-id>.svg` and its machine-readable receipt with input/profile SHA-256 values, exact renderer name/version/command, output SHA-256, dimensions, and pass/fail result. The SVG emitted by `MAP_RENDERER` is final: do not edit, patch, overlay, redraw, relabel, or replace it after rendering, and do not amend its receipt to describe post-processing. If the render is wrong, revise the structured source or the versioned template renderer, then render again. Electronics checks the data and receipt; graphic checks the rendered map at print size.

### L01 mandatory content

- Identify the 9 V battery/DC lead, power module, and a candidate output location from the official reference photo or official module documentation; do not name a voltage, set a selector, or claim a live selector/output state.
- Explain that source, module, and rail have different jobs.
- Go beyond labels: explain in child-readable causal language that a battery stores energy, a later-authorized module can provide a chosen lower-voltage output, a breadboard rail shares one connection through its internal metal strip, and continuous current needs a complete unbroken loop. Keep the L01 setup disconnected and do not invent internal module circuitry.
- Use a disconnected activity: trace the power path on a map and complete a check card.
- The L01 map uses dashed finger-trace paths, deliberate open gaps, open terminal circles, and one visible `NOT CONNECTED` label per link. It has no direction or current-flow arrowheads. Child and adult prose must call them dashed paths, open gaps, or teaching links—never arrows.
- A child never connects the battery lead or changes module selectors alone.

## Step 5 — visual contract

`05_visual_plan.json` must validate against `AUTOMATION_SCHEMA_DIR/visual_plan.schema_v1.json`; `assets/manifest.json` must validate against `AUTOMATION_SCHEMA_DIR/asset_manifest.schema_v1.json`. An omitted or failed mandatory job is a `REVISE_ARTIFACTS` finding. Render every asset at its declared print size and at least 300 effective DPI; record actual pixels, DPI, format, output hash, all source hashes, renderer/version, prompt or command, caption, alt text, and QA check id in `assets/manifest.json`.

| Every lab | Minimum required visual job | Method |
|---|---|---|
| component identification | one `reference_plate` | cached official photo, cropped/captioned and callout-annotated only; retain its unaltered source asset; never generative replacement. If the wide kit photo cannot support legible identification at target print size, first fetch and cache an official exact-component/datasheet photo with URL, access date, and SHA-256 in `references/source_manifest.json` |
| physical build/connection understanding | one `deterministic_technical_map` | byte-for-byte output of `MAP_RENDERER` from verified `02_circuit.yaml`; no post-render editing; never ImageGen |
| result understanding | one `expected_state` map or comparison plate | deterministic data/rendering; never ImageGen for circuitry |
| safe handling | one `safety_sequence` | render from verified data; no invented hazard |
| conceptual motivation | one `photorealistic_support` for every lab | ImageGen may be used only for a polished, photorealistic non-technical context; no kit/component likeness, labels, pins, wiring, rows, values, component geometry, or safety claim |

When a manifest visual role calls for a cutaway, mechanism view, graph, waveform, meter map, state chart, decision tree, timeline, or token flow, add a `concept_diagram` job. `05_concept_diagrams.json` contains an array and must validate against `AUTOMATION_SCHEMA_DIR/concept_diagram.schema_v1.json`; render every entry with `CONCEPT_RENDERER` from source-backed teaching claims, never from ImageGen, and validate its receipt against the visual-receipt schema. The emitted concept SVG is also final and may not be post-processed.

L01 must therefore include: official annotated component reference plate, disconnected source-to-module-to-rail map, check-card/expected-state plate whose data records `connections: []` and `not_connected`, adult-supervised safety sequence, and one safe polished photorealistic non-technical context plate. Its safety sequence cites the relevant official/manual safety evidence, not circuit data alone.

Reference-plate captions must identify the image as an official kit reference and must not claim an unverified detail. Callout labels may be overlaid only if their text is supported by the source. A reference-plate SVG must either embed the exact cached official image bytes as an image data URI or use a correct dossier-relative image path from the SVG’s own `assets/` directory (normally `../references/<filename>`); a basename that does not exist beside the SVG is invalid. Render the finished plate at its declared final size and inspect the rasterized result: every intended photograph/crop must be visible, never a blank or broken-image rectangle. Every deterministic-map label and schematic symbol must match the component type and semantics in `02_circuit.yaml` exactly. A rail, bus, terminal, module, sensor, or unknown component may never be represented by a diode, LED, resistor, switch, battery, or other unrelated conventional symbol. Every map must make every connection, breadboard row, rail, orientation mark, and intentionally unused terminal visible at its target print size; no hidden connection or inference is allowed.

For `photorealistic_support`, a graphic-production agent must invoke `$imagegen` and call the available built-in ImageGen image-generation tool (GPT Image 2). Writing a prompt, drawing a local substitute, copying a stock image, or using a generic raster/SVG renderer does not satisfy this job. Use a short production brief in this order: scene/backdrop → subject → concrete camera/lighting/material details → constraints → workbook use. It must explicitly say: “polished photorealistic educational context; no electronics kit, no breadboard, no component imitation, no wiring diagram, no labels or text.” Generate one asset per call, inspect the result, make only targeted revisions, and copy the accepted project-bound image from the built-in output location into the current dossier’s `assets/` directory without overwriting another version. It is supplementary only, cannot serve as technical evidence, and a failed result must be regenerated until it passes or the run ends as `SYSTEM_FAILURE`; a mandatory visual may not be omitted. The production receipt must name ImageGen/GPT Image 2 as the tool, retain the exact prompt, use `source_type: imagegen_context`, and assert `technical_evidence: false`.

Run one graphic-production specialist per job, serially by default. The graphic QA gate checks: source fidelity, correct source/caption, no AI technical lookalike, label-to-YAML/source match, callout legibility at print size, no ambiguous row/rail/connection, required alt text, and an asset path for every visual-plan job. A visual-job failure revises that job; it never blocks the lab unless the evidence policy’s named-claim condition is met.

Every visual job has a production receipt validating against `AUTOMATION_SCHEMA_DIR/visual_receipt.schema_v1.json`. Reference plates record source/crop/callout coordinates and hashes. Expected-state plates, safety sequences, cutaways, timelines, waveforms, and token diagrams record their structured input path, renderer/tool/version, command or prompt, source hashes, output dimensions, output hash, and QA check. For `deterministic_technical_map` and `concept_diagram`, the runner independently replays the named template renderer from the receipt inputs and rejects any byte difference, post-render overlay, manual SVG edit, substituted tool name, or patched receipt. ImageGen receipts record the exact prompt and assert `technical_evidence: false`.

## Step 6 — QA and revision

Run the four roles independently and serially against the completed dossier, using the review JSON schema above. The orchestrator compiles them into `qa_decision.json`:

Before review, generate `qa_checklist.json`, validating it against `AUTOMATION_SCHEMA_DIR/qa_checklist.schema_v1.json`. Generate stable check IDs deterministically from the canonical source path plus requirement index. Include one check for every merged manifest field, every required template section, every required dossier artefact, every visual job, every source claim, and—where applicable—every controller/build requirement. Assign each check to one or more roles by domain. Each role must return every assigned check ID; a review with a missing assigned check is schema-invalid and cannot pass.

After validating all four review records, update each checklist entry mechanically: `fail` if any assigned role reports that check ID as failed; `pass` only if every assigned role reports it as passed; otherwise leave it `pending` and return `REVISE_ARTIFACTS`. `READY_FOR_FINAL` requires every checklist entry to be `pass`.

- `READY_FOR_FINAL` only when all required checks pass and all required visual jobs exist and pass their acceptance tests; transition to `FINAL_ACCEPTANCE`, never directly to `ACCEPTED`.
- `REVISE_ARTIFACTS` when any repairable check fails. List exact failed paths, required changes, rerun roles, and next state.
- `BLOCKED` only for a valid evidence-policy block with its named claim and missing primary source.

Do not turn an ordinary QA failure into a block to end the run. Do not accept based on model confidence.

## Step 7 — acceptance record

After the four QA records pass, enter `FINAL_ACCEPTANCE` and execute a separate `final_acceptance` task using the routed safety-critical model. It reads the canonical checklist, all QA records, state/decision records, source hashes, renderer receipts, and controller build receipt when applicable. Write `final_acceptance.json` validating against `AUTOMATION_SCHEMA_DIR/final_acceptance.schema_v1.json`. It may return only `ACCEPTED`, `REVISE_ARTIFACTS`, or a valid evidence-policy `BLOCKED`. `REVISE_ARTIFACTS` returns to the targeted revision/QA loop and then re-enters final acceptance. The pedagogy QA verdict must be `pass`; otherwise final acceptance is impossible.

Final acceptance evaluates `physical_release` separately from document quality. It may accept a complete, source-backed document with `physical_release: pending_adult_check`; this does not authorize a child or adult to energize the circuit and satisfies the selector’s requirement that the release state be present and explicit.

On final acceptance, write `09_acceptance.md`: final state, all review paths, resolved revisions, source references, visual-job outputs, final-acceptance record, and next allowed action. Only then may the orchestrator start the next lab.

Only after `ACCEPTED` may the orchestrator start the next lab.

## Step 8 — assemble and accept the final illustrated PDF (`RUN_MODE: all` only)

After L01–L35 are individually `ACCEPTED`, create a new `<OUTPUT_ROOT>/workbook/` dossier without modifying any lab dossier:

```text
<OUTPUT_ROOT>/workbook/
  curriculum.md
  curriculum.pdf
  assembly_manifest.json
  page_renders/
  reviews/qa/<role>.json
  qa_checklist.json
  qa_decision.json
  final_acceptance.json
  revision_log.md
```

`curriculum.md` must include all 35 labs in manifest order. For each lab, preserve the component-first sequence, include the full child explanation and activity, place every supporting image beside the text it supports, and put the adult technical guide in a visibly separate adult section. Never replace explanatory text with images and never use a photorealistic support image as evidence for wiring, polarity, values, pinout, breadboard topology, or safety.

`assembly_manifest.json` records, for every included text and image: source dossier path, source SHA-256, destination section/page anchor, caption, alt text, and intended print size. It also records the PDF generator, version, command, Markdown hash, PDF hash, page count, page size, and generation timestamp.

Generate `curriculum.pdf`, render every PDF page to `page_renders/` at inspection resolution, and inspect every rendered page. Reject and revise the workbook for any missing/cropped image, unreadable label, image-text mismatch, orphaned heading, blank page, broken cross-reference, incorrect lab order, child/adult boundary failure, or diagram too small to follow. The source lab dossiers are immutable during workbook revision; only workbook files may change.

Run four independent serial workbook reviewers—electronics, pedagogy, communication, and graphic—with distinct spawned-agent identities. Electronics verifies that assembly did not alter or separate technical labels from their explanatory context. Pedagogy verifies that a nine-year-old beginner can follow each lab in order and that each picture supports nearby text. Communication verifies reading flow and vocabulary. Graphic verifies every rendered page at final print size. Compile their checks mechanically into `workbook/qa_checklist.json` and `workbook/qa_decision.json`.

Any failed workbook check returns to assembly/layout revision and reruns the affected reviewers, always including pedagogy when text, ordering, pagination, or image placement changes and electronics when a technical figure or caption changes. Use the same convergence rule and six-cycle maximum as a lab. Do not report success while any check is pending or failed.

`workbook/final_acceptance.json` may say `ACCEPTED` only when all 35 lab acceptance records say `ACCEPTED`, every required source asset is present in the assembly manifest, every rendered page has been inspected, all four workbook reviews pass with distinct identities, the pedagogy verdict passes, all workbook checklist entries pass, and the final PDF hash matches the assembly manifest. The outer runner independently audits these conditions before reporting overall success.

## Required self-test before the 35-lab run

Run this fixture with no PDF and no powered circuit:

```text
LAB_ID: L01
source reference: references/official_kit_photo.jpg
expected plan decision: AUTHOR or REVISE_PLAN; never BLOCKED for lack of local inspection
required correction: reject “9 V/1 A wall adapter”
required power statement: “9 V battery with DC connector → power module → candidate output location (not live)”
required core activity mode: unpowered
required visual jobs: reference_plate, deterministic_technical_map, expected_state, safety_sequence, photorealistic_support
```

The fixture passes only if each reviewer record validates to the review shape, its `plan_decision.json` validates to the decision shape, it creates a routing decision for every task, it contains no generic physical-kit block, and all required L01 visual jobs are planned. Otherwise revise this prompt before use.
