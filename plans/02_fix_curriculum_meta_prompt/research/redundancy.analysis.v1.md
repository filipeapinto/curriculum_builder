# Redundancy and exclusivity analysis — `curriculum_creator/` support files

**Date:** 2026-07-29
**Goal:** every fact declared in exactly one file, zero contradictions between files.
**Method:** full read of every in-scope file, mechanical cross-checks (YAML/JSON parse,
regex sweeps for check ids, sha256 comparison, graph checks on the 35 lab entries),
then adversarial review by Codex (`gpt-5.6`, xhigh effort) until agreement.

**Scope.** In scope: `assets/*.yaml`, `assets/*.md`,
`assets/l01_unpowered_power_path.json`, `assets/fixtures/*`, `schema/*.json`,
`routing/*`, `prompts/component_lab_template.v1.md`, `readme.md`, `how_it_works.md`,
`pedagogy.md`. Out of scope for editing (changes needed there are reported in §5):
`prompts/meta_curriculum_prompt.prompt.v5.md`, `plans/*`, `assets/legacy/*`,
`how_it_works.typ`, `how_it_works.png`.

**Two decisions treated as deliberate, not defects** (per the task brief):
calibration outranks prose documents and its divergence from `lab_brief.md` /
`teacher_framework.md` is recorded on purpose; reviewer independence comes from what
a reviewer is given, not from enforced secrecy.

**Status: agreed.** Four Codex rounds. Round 4 verdict: *"I approve the proposal
unconditionally."* 95 facts inventoried, 25 contradictions, 33 proposed changes, three
items escalated to a human (§6). Nothing was edited — this is analysis and proposal
only.

**The one-line diagnosis.** Almost nothing in this folder is owned. Of 95 facts, 42
are stated in two or more files with no check keeping them equal, and 15 more are
described as derived with no mechanism deriving them. The contradictions in §2 are
not independent bugs; they are what happens to duplicated facts over time. That is
why the governance rule in §3 matters more than any individual fix: without rule 4,
this document describes a state the project will return to.

---

## 1. Fact inventory

Classification key — **CONTRA**: declared states differ. **DUP**: same fact stated
more than once, currently consistent (drift risk only). **DERIVED**: legitimately
computed from another declaration; the "sync" column says what keeps it true.

### 1.1 Learner and pedagogy

| # | Fact | Declared at | Class | Proposed owner |
|---|---|---|---|---|
| F01 | Learner age band | `calibration.v1.yaml:16` `9+`; `curriculum.v4.yaml:7` `9+`; `lab_brief.md:3` `12+`; `teacher_framework.md:5,292` `12+` | CONTRA (declared deliberate) | `calibration.v1.yaml` `learner.age_band` |
| F02 | Learner description sentence | `calibration.v1.yaml:17`; `curriculum.v4.yaml:7` (near-verbatim) | DUP | `calibration.v1.yaml` |
| F03 | "nine-year-old" as an inline literal | `lab.schema.v3.json:54,675`; `pedagogy.md:28`; `how_it_works.md:89,440` | DUP (5 hard-coded copies of an owned value) | `calibration.v1.yaml` |
| F04 | Supervision = adult required | `calibration.v1.yaml:18`; `component_lab_template.v1.md:160`; `teacher_framework.md:66` | DUP | `calibration.v1.yaml` `learner.supervision` |
| F05 | New terms per lab ≤ 2 | `calibration.v1.yaml:24`; `lab.schema.v3.json:186` (`maxItems:2`); `pedagogy.md:85-86`; `teacher_framework.md:126,290`; `component_lab_template.v1.md:44` | DERIVED (cal→schema, via `enforced_by`+`CAL-SCHEMA-AGREE`) + 3 unchecked prose copies | `calibration.v1.yaml` |
| F06 | Segments per lab 2–6 | `calibration.v1.yaml:25`; `lab.schema.v3.json:260-262`; `pedagogy.md:87` | DERIVED + 1 prose copy | `calibration.v1.yaml` |
| F07 | Bloom floor = understand | `calibration.v1.yaml:26`; `lab.schema.v3.json:108-120`; `pedagogy.md:99,105`; `how_it_works.md:123-125`; `readme.md:63`; `checks.v1.yaml:80-83`; `calibration.schema.v1.json:52` | DERIVED + 5 prose copies | `calibration.v1.yaml` |
| F08 | Objectives per lab 1–3 | `calibration.v1.yaml:27`; `lab.schema.v3.json:74-75` | DERIVED | `calibration.v1.yaml` |
| F09 | Success-criterion voice = first person | `calibration.v1.yaml:28`; `lab.schema.v3.json:103` **and** `:499`; `pedagogy.md:100-101` | DERIVED, but the pattern is declared **twice inside one schema** | `calibration.v1.yaml`; schema pattern defined once via `$defs` |
| F10 | Misconceptions ≥ 1 | `calibration.v1.yaml:29`; `lab.schema.v3.json:157`; `pedagogy.md:55` | DERIVED | `calibration.v1.yaml` |
| F11 | Concrete before abstract | `calibration.v1.yaml:30` (enum `required`); `lab.schema.v3.json:268-272` (free string); `pedagogy.md:88-89`; `component_lab_template.v1.md:154` | **CONTRA** — no `enforced_by` entry, and the schema field cannot express the enum | `calibration.v1.yaml` |
| F12 | `evaluate.success_criteria_checklist` mirrors `learning_objectives[].success_criterion` | `lab.schema.v3.json:494` (stated), `:499` (pattern only) | DERIVED, **unenforced** — nothing checks the mirroring | `lab.schema.v3.json` + a new check |
| F13 | Whole pedagogy-method rationale (5E, POE, conceptual change, retrieval, CLT, Bloom, scaffolding, dual coding) | `lab.schema.v3.json` field `description`s; `pedagogy.md` (entire file) | DUP by design (prose companion) — acceptable, but `pedagogy.md` also copies cap **values** | `lab.schema.v3.json` for constraints; `pedagogy.md` for rationale only |

### 1.2 Power, safety and the kit

| # | Fact | Declared at | Class | Proposed owner |
|---|---|---|---|---|
| F14 | Permitted power inputs (set of 2, one verified) | `calibration.v1.yaml:35-43`; `curriculum.v4.yaml:15-20`; `kit_evidence.md:13` | DUP (agreeing) | `calibration.v1.yaml` `power.permitted_inputs` |
| F15 | Which supply a lab may use | `calibration.v1.yaml:52-53` (verified only ⇒ 9 V battery); `lab_brief.md:3` (5 V USB, exclusive); `roster.md:3` (5 V USB); `teacher_audit.md:17` (L01 certified "5 V USB-only, no 9 V clip on rail") | **CONTRA** — `roster.md` and `teacher_audit.md` are *not* in the declared-divergence list at `meta prompt:86-88`. **Corrected in Codex R1:** `teacher_framework.md:176` is **not** part of this — it rejects the 9 V battery as a *direct breadboard source*, while `calibration.v1.yaml:37` has it *feeding the power module*. Compatible; my original reading was wrong | `calibration.v1.yaml` |
| F15b | Supply representations | `calibration.power.permitted_inputs` (ids); `curriculum.kit_power_profile` (no id field); `lab.safety.power_profile.source` (free text) | **Gap** — three parallel representations, no binding map (Codex R1) | `calibration.v1.yaml` |
| F16 | Rail set `{OFF, 3.3 V, 5 V}` | `calibration.v1.yaml:44-48`; `curriculum.v4.yaml:21-24`; `kit_evidence.md:15` | DUP | `calibration.v1.yaml` `power.rails` |
| F17 | Student circuit range 3–5 V | `calibration.v1.yaml:48`; `teacher_framework.md:61,174`; `lab_brief.md:25` ("normally 5 V") | DUP | `calibration.v1.yaml` |
| F18 | Rail colour is never an electrical identity | `calibration.v1.yaml:56-57`; `curriculum.v4.yaml:60-61` (L01 `required_explanation`); `component_lab_template.v1.md:91,161`; `lab.schema.v3.json:707` | DUP (4×) | `calibration.v1.yaml` `power.rules` |
| F19 | Child never touches the input side | `calibration.v1.yaml:54-55`; `component_lab_template.v1.md:160`; `curriculum.v4.yaml:76` | DUP | `calibration.v1.yaml` |
| F20 | Safety floor: power off before rewiring, troubleshooting starts power off, adult guide separate, stop if warm | `calibration.v1.yaml:61-65`; `teacher_framework.md:62,66,151,321`; `component_lab_template.v1.md:156,163-166`; `lab_brief.md:25` | DUP (4 files) | `calibration.v1.yaml` `safety_floor` |
| F21 | Stop threshold: **warm** vs **hot** | `calibration.v1.yaml:65` `stop_if_warm`; `component_lab_template.v1.md:166` "warm"; `teacher_framework.md:66` "hot" | **CONTRA** on a floor item `calibration.schema.v1.json:94-108` marks non-tunable | `calibration.v1.yaml` |
| F22 | Mains boundary sentence | `component_lab_template.v1.md:163`; `lab_brief.md:25`; `teacher_audit.md:11`; `teacher_framework.md:65`; `calibration.v1.yaml:58` (different wording) | DUP, 5 wordings | `calibration.v1.yaml` `power.rules` |
| F23 | `power_profile` field shape | `lab.schema.v3.json:1256-1293` (6 required, `additionalProperties:false`); `component_lab_template.v1.md:75-89` (9 different fields) | **CONTRA** — the template's block cannot validate | `lab.schema.v3.json` |
| F24 | A lab cites its supply *by id* | `checks.v1.yaml:22-27` `CAL-SOURCE-VERIFIED`; `calibration.v1.yaml:75` names `safety.power_profile.source` as the enforcer; `lab.schema.v3.json:1269-1272` is an unconstrained string | **CONTRA** — `enforced_by` claim is false | `lab.schema.v3.json` (needs the constraint) |
| F25 | Kit photo location | `calibration.v1.yaml:38` `assets/…`; `curriculum.v4.yaml:20`, `l01_unpowered_power_path.json:6`, `fixtures/l01_polarity_asserted.reject.json:6` all `work/elegoo_labs/templates/kit_references/…`; `kit_evidence.md:9` bare filename | **CONTRA** — 3 files cite a path outside CREATOR (verified byte-identical, sha256 `8f9ab6c8…`), against `readme.md:40-42` and `meta prompt:70-72` | `calibration.v1.yaml` |
| F26 | Kit listing URL | `kit_evidence.md:21`; `curriculum.v4.yaml:19`; `l01_unpowered_power_path.json:10`; `fixtures/…:10` | DUP (4×) | `kit_evidence.md` |
| F27 | `source_bundle_sha256` = the kit photo's sha256 | `l01_unpowered_power_path.json:40`; `fixtures/…:28` | DERIVED, **relationship undeclared anywhere** | `kit_evidence.md` (declare it) |
| F28 | Kit identity / inventory | `kit_evidence.md:5`; `roster.md:3`; `teacher_framework.md:5` | DUP | `kit_evidence.md` |

### 1.3 Lab structure and visuals

| # | Fact | Declared at | Class | Proposed owner |
|---|---|---|---|---|
| F29 | Number of lab-document blocks | `lab.schema.v3.json:8-16` = **7**; `lab.schema.v3.json:5` description = **"Five co-equal blocks"** | **CONTRA** inside one file | `lab.schema.v3.json` `required` |
| F30 | The mandatory lab section order | `lab_brief.md:5-21` (15 sections, "exact order"); `teacher_framework.md:27-168` (13, "may not omit a heading"); `component_lab_template.v1.md:17-137` (12, "Required lab structure"); `lab.schema.v3.json` (7 blocks + fixed 5E) | **CONTRA** — three prose structures each claiming exclusivity | `lab.schema.v3.json` + `component_lab_template.v1.md` |
| F31 | The word "visual role" | `lab.schema.v3.json:1591-1599` (7-value enum, output categories); `curriculum.schema.v4.json:280` + `curriculum.v4.yaml` (field named `visual_roles`, free text, 4/lab — in practice visual *briefs*); `checks.v1.yaml:48` (`CUR-VISUAL-ROLES`) | **CONTRA** — one term, two undeclared meanings across a contract boundary. **Narrowed from "six competing taxonomies" after Codex R1**, which is right that briefs and output categories are different things — but no file says so | `lab.schema.v3.json` `$defs/visual.role`; rename the manifest field |
| F32 | **Number of visuals per lab** | `lab.schema.v3.json:1378` `minItems:3`; `component_lab_template.v1.md:139-148` **five**; `teacher_audit.md:9,11` **exactly three**; `roster.md:61` **four** for L20, L22, L24–L27; `curriculum.v4.yaml` **four** for all 35; `teacher_framework.md:232` "at least three" | **CONTRA** — four different mandatory counts. *Raised by Codex R1; sharper than my original F31* | `lab.schema.v3.json` |
| F33 | Seven-role sufficiency matrix | asserted `how_it_works.md:257-260`, promised by `checks.v1.yaml:48-50`; `lab.schema.v3.json:1375-1381` allows any three records, repeated roles, and an optional `omission_finding` | **Unencoded claim** (Codex R1) | `lab.schema.v3.json` |
| F33b | ImageGen may not carry exact fact | `lab.schema.v3.json:1667-1680` (`if imagegen then carries_exact_electronic_fact const false`) — but the field is **optional** (`:1623`), so the rule never fires when absent; and no role/source-kind pairing blocks imagegen from `orientation_and_pins` or `connection_or_unpowered_path_map` | **Unenforced constraint** (Codex R1) | `lab.schema.v3.json` |
| F34 | ImageGen may never carry exact electronic fact | `lab.schema.v3.json:1602-1606,1667-1680`; `curriculum.v4.yaml:33-34`; `curriculum.schema.v4.json:122` (const); `component_lab_template.v1.md:60,149`; `how_it_works.md:262-275`; `routes.v1.yaml:83-84`; `kit_evidence.md:19` | DUP (7×) | `lab.schema.v3.json` |
| F35 | `design_rule` const string | `curriculum.schema.v4.json:41`; `curriculum.v4.yaml:10`; `lab.schema.v3.json:47`; `component_lab_template.v1.md:5`; `how_it_works.md:112` | DUP (5×) | `curriculum.schema.v4.json` (const) |

### 1.4 The curriculum itself

| # | Fact | Declared at | Class | Proposed owner |
|---|---|---|---|---|
| F36 | Lab count = 35 | `curriculum.v4.yaml` (35 entries; **no** `lab_count` field); hardcoded as "35" in `readme.md:7,36,88,97,102,107`, `how_it_works.md:75,364,369-378`, `kit_evidence.md:5`, `teacher_audit.md:4`; enumerated 35× in `roster.md` and `teacher_audit.md` | DERIVED, but `checks.v1.yaml:34-38` `CUR-COUNT-DERIVED` forbids a fixed count in "report text" | `curriculum.v4.yaml` |
| F37 | 35-lab ceiling in a regex | `curriculum.schema.v4.json:215,222` `^L(0[1-9]\|[12][0-9]\|3[0-5])$` | **CONTRA** with `:132` ("the schema does not fix a count") and with `CUR-COUNT-DERIVED` | `curriculum.schema.v4.json` (loosen) |
| F38 | Prerequisite id grammar | `curriculum.schema.v4.json:215` vs `lab.schema.v3.json:134-136` (`^L[0-9]{2,3}$`) | **CONTRA** — two grammars for one id type | one shared `$defs` |
| F39 | Lab titles / identities | `curriculum.v4.yaml` (35 titles); `roster.md:7-59` (35 different titles); `teacher_audit.md:17-51` (35 more) | **CONTRA-by-drift** — 1:1 by topic, **zero** title strings match across all three | `curriculum.v4.yaml` |
| F40 | `prepares_for` vs `prerequisites` | `curriculum.v4.yaml`, both fields on all 35 labs; `checks.v1.yaml:42` `CUR-PREREQS-RESOLVE` validates prerequisites **only** | **Ungoverned redundancy** (reclassified from CONTRA after Codex R1: no contract says they must be inverses). All references resolve; but only 38 edges are reciprocal — 23 `prepares_for` edges are not prerequisites of the target, and 31 prerequisite edges are absent from the source's `prepares_for` | `curriculum.v4.yaml` `prerequisites` only |
| F40b | Curriculum schema's enforcement claim | `curriculum.schema.v4.json:126,132` claims the schema requires labs "ascending, contiguous from L01, with unique ids"; it has only `minItems:1` and per-item patterns | **CONTRA** — the schema says more than it can express (Codex R1) | `checks.v1.yaml` (`CUR-IDS-CONTIGUOUS`) |
| F41 | Safety mode enum (4 values) | `curriculum.schema.v4.json:252-259`; `lab.schema.v3.json:1247-1255`; restated `how_it_works.md:94-95`, `readme.md:58-60` | DUP (identical) | one shared `$defs` |
| F42 | Circuit-status vocabulary | `curriculum.schema.v4.json:264-269` (`not_designed` \| `requires_verified_circuit_data`) vs `lab.schema.v3.json:690-694` (`not_designed` \| `designed_verified`) | **Missing mapping** (reclassified from CONTRA after Codex R1: these are plausibly lifecycle states — a spec says data is required, a finished dossier says it is verified. The defect is that no file declares the mapping and no check crosses the contract boundary) | declare the mapping + a cross-contract check |
| F43 | `CUR-ORIENTATIONS` target | `checks.v1.yaml:45-47`; `curriculum.schema.v4.json` has **no** orientation field; `lab.schema.v3.json:1160-1163` already requires `orientation_cue` | Unenforceable against the curriculum, redundant against the lab schema | `lab.schema.v3.json` |

### 1.5 Controller, checks, limits, routes

| # | Fact | Declared at | Class | Proposed owner |
|---|---|---|---|---|
| F44 | The 25 states | `controller.v1.yaml:25-50`; `how_it_works.md:152-183`; count restated `readme.md:45`, `how_it_works.md:149` | DUP + DERIVED count | `controller.v1.yaml` |
| F45 | Reviewer count per lab | `checks.v1.yaml:153-155` = **12**; `meta prompt:110,269` = 12; `how_it_works.md:244,355` = **8**; `readme.md:111-113` = **8** | **CONTRA**. Secondary: `controller.v1.yaml` has 4 plan + 4 QA + **1** `PDF_VISUAL_QA` state, so the 12 is not *derivable* from the controller contract — though as Codex R1 correctly notes, one state can fan out to four calls, so this is under-specification, not impossibility | `checks.v1.yaml` `REV-COUNT-TWELVE` |
| F46 | Review-aggregation rules | `controller.v1.yaml:91-95`; `how_it_works.md:218-223` | DUP | `controller.v1.yaml` |
| F47 | Targeted-revision meaning | `controller.v1.yaml:96-98`; `how_it_works.md:225-227` (cites `VIS-03`) | DUP + **orphan check id** | `controller.v1.yaml` |
| F48 | `VIS-03` | `how_it_works.md:225` only — not in `checks.v1.yaml` (41 ids) | **CONTRA** — reproduces the exact B3 defect (an advertised id with no assertion) | delete |
| F49 | BLOCKED eligibility | `controller.v1.yaml:104-116`; `how_it_works.md:234-238`; `meta prompt:144-145` | DUP | `controller.v1.yaml` |
| F50 | Checkpoint record fields | `controller.v1.yaml:71-79`; `how_it_works.md:185-187` | DUP | `controller.v1.yaml` |
| F51 | Resume semantics | `controller.v1.yaml:81-86`; `how_it_works.md:313-316`; `readme.md:112-114` | DUP | `controller.v1.yaml` |
| F52 | Full-run completion rule | `controller.v1.yaml:122-131`; `how_it_works.md:369-378` | DUP | `controller.v1.yaml` |
| F53 | Code-owns / model-owns split | `controller.v1.yaml:9-22`; `how_it_works.md:46-68`; `meta prompt:96-108` | DUP (3×) | `controller.v1.yaml` |
| F54 | Ordering rules (circuit→prose, consistency→QA, PDF→acceptance) | `controller.v1.yaml:54-69`; `how_it_works.md:194-209` | DUP | `controller.v1.yaml` |
| F55 | Terminal states (lab) | `controller.v1.yaml:52`; `how_it_works.md:182` | DUP | `controller.v1.yaml` |
| F56 | Terminal states (meta) | `readme.md:28`; `how_it_works.md:405-411`; `meta prompt:210-216` | DUP (3×) | `meta prompt` |
| F57 | Check-stage vocabulary | `checks.v1.yaml` uses `static, deterministic, golden, logger, live-capability`; `meta prompt:150-151` requires `logger, static, deterministic, simulated, live-capability, live-golden` | **CONTRA** — `golden`≠`live-golden`, and **no check has stage `simulated`**, so gate 3 has zero ids behind it | `checks.v1.yaml` |
| F58 | Checks with no stage | 8 of 41 (`DRIFT-*` ×7, `PRECONDITION-OUTPUT-ROOT-EXISTS`) | Gap — cannot be assigned to a gate | `checks.v1.yaml` |
| F58b | Where each check is enforced | `checks.v1.yaml:1` header promises "where it is enforced"; **none of the 41 ids names an implementation, worker or test owner** | **Gap — the single most load-bearing one.** This is why `VIS-03` could be invented and why B3 remains structurally possible (Codex R1) | `checks.v1.yaml` |
| F59 | The six proof gates | `meta prompt:153-160`; `readme.md:95-114`; `how_it_works.md:346-356` | DUP (3 wordings). **Corrected after Codex R1:** I originally listed `checks.v1.yaml` as a fourth copy. It is not — its `stage` values are check categories, not the gate sequence | `meta prompt` |
| F60 | Failure ledger A1–A10 / B1–B4 | `failures.v1.yaml`; restated `how_it_works.md:423-438`, `readme.md:116-130`, `how_it_works.md:250-252,277-281,326-340,357-361` | DUP | `failures.v1.yaml` |
| F61 | A6's definition | `failures.v1.yaml:30-32` (L01 self-contradiction) vs `how_it_works.md:84` (base/override merge) vs `how_it_works.md:430` (both fused) | **CONTRA** | `failures.v1.yaml` |
| F62 | Failure→correction mapping | `failures.v1.yaml` B1–B4 only (`correction`+`checks`); A1–A10 carry **no** correction/checks; the A-corrections live in `controller.v1.yaml:60,69,86,102` (5 of 10) and `how_it_works.md:423-438` (all 10) | **CONTRA with** `failures.v1.yaml:127-131` which demands every id map to a correction and a proving test | `failures.v1.yaml` |
| F63 | Route inventory | `routes.v1.yaml` = **4** (worker, pdf, rasterizer, imagegen); `how_it_works.md:304-307` = "the two declared routes"; `readme.md:26` PATH list omits `pdftoppm` | **CONTRA** | `routes.v1.yaml` |
| F64 | ImageGen route status | `routes.v1.yaml:73-77` `UNPROVEN`, `command: null`; `readme.md:110-112` and `how_it_works.md:354` list "real ImageGen" as proven by gate 4 | **CONTRA** — gate 4 cannot pass as documented | `routes.v1.yaml` |
| F65 | Preflight = real execution | `routes.v1.yaml:3-7,86-93`; `checks.v1.yaml:193-195`; `how_it_works.md:302-307`; `readme.md:109-110`; `meta prompt:159`; `failures.v1.yaml` A7 | DUP (6×) | `routes.v1.yaml` |
| F66 | Limits and their flags | `limits.v1.yaml`; `controller.v1.yaml:145` correctly delegates | **Correct single ownership** — the model to copy | `limits.v1.yaml` |
| F67 | Concurrency = 1 | `limits.v1.yaml:39-42`; `how_it_works.md:295` | DUP | `limits.v1.yaml` |
| F68 | `max_model_calls: 60` rationale | `limits.v1.yaml:14` "12 reviews + ~20 authoring calls" | DERIVED from F45, **unchecked** | `limits.v1.yaml` |
| F69 | `max_images: 12` rationale | `limits.v1.yaml:22` "seven visual roles plus revisions" | DERIVED from F31, **unchecked** | `limits.v1.yaml` |
| F70 | `--model` is fallback only | `controller.v1.yaml:146-148`; `how_it_works.md:300` | DUP | `controller.v1.yaml` |
| F71 | Startup precondition (V7 must not exist) | `checks.v1.yaml:186-192`; `meta prompt:39-43`; `readme.md:25-26` | DUP (3×) | `checks.v1.yaml` |
| F72 | Execution-log path | `execution_log.schema.v1.json:5`; `how_it_works.md:319`; `meta prompt:173` | DUP | `meta prompt` |
| F73 | Logger rules (never derive the closing id, monotonic, locked appends) | `failures.v1.yaml:71-75`; `execution_log.schema.v1.json:46,92`; `how_it_works.md:326-340`; `meta prompt:182-187` | DUP (4×) | `execution_log.schema.v1.json` |
| F74 | `unclosed_starts` must be empty | `execution_log.schema.v1.json:19-24` — but the property is **not in `required`** | Gap — a log omitting it passes `LOG-PAIRED` vacuously | `execution_log.schema.v1.json` |
| F74b | Log guarantees JSON Schema cannot express | `execution_log.schema.v1.json:5` claims monotonic ids, append-only order, exactly-one closure, resolvable `closes`, coverage. JSON Schema can express none of these. The `LOG-*` ids that do own them exist at `checks.v1.yaml:126-149` but the schema never names them | **Gap** (Codex R1) | `checks.v1.yaml` `LOG-*`, cross-referenced from the schema |
| F74c | ACT record semantics | `execution_log.schema.v1.json:32` — an ACT is appended at start **and** at completion; `meta prompt:289` — "`ACT` entries record completed actions" | **CONTRA** (Codex R1) | `execution_log.schema.v1.json` |
| F74d | "Validate every input against its schema" | `meta prompt:49,239` requires it; there are schemas for **4** files only (calibration, curriculum, lab, execution log). None exists for `routes/checks/controller/limits/failures.v1.yaml`, `routing/*.yaml`, or any `.md` | **CONTRA** — an unfulfillable precondition, not merely missing coverage (Codex R1) | `schema/` |

### 1.6 Routing

| # | Fact | Declared at | Class | Proposed owner |
|---|---|---|---|---|
| F75 | Model eligibility | `routing_policy.v1.yaml:13-30` (by risk tier) **and** `model_registry.v1.yaml` `allowed_for` (by capability label) | **CONTRA** — two mechanisms, disjoint vocabularies; only 1 of 8 `allowed_for` labels (`final_acceptance`) is also a task name. `child_explanatory_writing` is medium-risk (terra eligible by policy) but no `allowed_for` label matches | `routing_policy.v1.yaml` |
| F76 | The `low` risk tier | `routing_policy.v1.yaml:27-30` — **no task in `task_taxonomy.v2.yaml` has risk `low`** (8 high, 6 safety_critical, 3 medium) | Dead configuration | `task_taxonomy.v2.yaml` |
| F77 | `gpt-5.6-luna` | `model_registry.v1.yaml:28-36`, `allowed_for: [mechanical_processing]` — not a task in the taxonomy; unreachable | Dead configuration | `model_registry.v1.yaml` |
| F78 | Reasoning-effort vocabulary | `model_registry.v1.yaml:34` luna supports `low`; `routing_decision.schema.v1.json:12` enum has no `low` | **CONTRA** (minor) | `routing_decision.schema.v1.json` |
| F79 | Review domains | `controller.v1.yaml:27-30,42-45` = electronics, pedagogy, **communication**, **graphic**; `quality_gates.v1.yaml:2-14` = electronics, pedagogy, **visual**, release | **CONTRA** — no `communication` gate; `visual`≠`graphic` | `controller.v1.yaml` |
| F80 | Routing tier names | `routing_policy.v1.yaml` (safety_critical/high/medium/low) vs `how_it_works.md:288-292` ("no model / cheapest eligible / stronger / maximum reasoning") | DUP with disjoint vocabulary, no mapping | `routing_policy.v1.yaml` |
| F81 | Gate-token namespaces | `checks.v1.yaml` ids; `quality_gates.v1.yaml` `requires` tokens; `task_taxonomy.v2.yaml` `evidence_required` tokens; `routing_decision.schema.v1.json` free-string `quality_gate` | Three unlinked namespaces + one free-text field | `checks.v1.yaml` |

### 1.7 Provenance / project-status claims

| # | Fact | Declared at | Class | Proposed owner |
|---|---|---|---|---|
| F82 | Status of `teacher_audit.md` | `teacher_audit.md:4,11,15-51,59` asserts 35 labs audited, all PASS, sourced from a relative `labs/` that does not exist in CREATOR; shipped as a live input at `meta prompt:67`; no historical marker | **CONTRA — unprovenanced input.** *Reclassified after Codex R1*, which is right that a historical audit can coexist with "v3 never produced an accepted L01", so this is **not** an A5 violation. What survives: no declared status, a dangling source path, and two live contradictions it participates in (F15 supply, F32 visual count) | `assets/legacy/` |
| F83 | Folder inventory (file/folder counts, size) | `readme.md:34,36,38,40-43`. Verified actuals: 4 schema files, 14 files in `assets/`, 37 files excluding `plans/`, 1,567,723 bytes, **two** binaries with `how_it_works.png` the larger — against "2", "12", "3", "26 files, 852 KB", "the only binary" | **CONTRA** with the filesystem | `readme.md` (delete the counts) |
| F84 | Self-containment | `readme.md:40-42` "nothing outside this folder is required" | **CONTRA** on three counts: the `work/…` path (F25), the external binaries required at `readme.md:25`, and the two declared outside reads at `meta prompt:70-72` (Codex R1) | `meta prompt` |
| F85 | Historical v5 gate names | `failures.v1.yaml:57,79,92,107` (`DRIFT-LOG-NONMONOTONIC-OR-UNPAIRED`, `GOLDEN-REVIEWER-INDEPENDENCE`, `STATIC-CONTRACT-COVERAGE`, `GOLDEN-VISUAL-RECEIPT-CONSISTENCY`) share the `checks.v1.yaml` id namespace but are not in it | Ambiguity — historical vs live ids indistinguishable | `failures.v1.yaml` (mark historical) |
| F86 | **No Arduino / no controller** — the workbook's defining scope constraint | `roster.md:3`; `lab_brief.md:3`; `teacher_framework.md:5,251,275`; `teacher_audit.md:9,55`. Appears in **none** of `calibration.v1.yaml`, `curriculum.v4.yaml`, any `schema/*.json`, `readme.md`, `how_it_works.md`, `pedagogy.md`, `component_lab_template.v1.md` (verified by grep) | **CONTRA + ownerless** — `curriculum.v4.yaml` grants **14 of 35 labs** `core_activity.mode: adult_led_controller_station` (L16, L18, L20–L29, L32, L33), and the curriculum outranks all four files that forbid a controller | `calibration.v1.yaml` (new `scope` block) |
| F87 | Reject fixtures | `checks.v1.yaml` declares `fixture_expectation: reject` on 5 checks; only `L01-POLARITY-NEUTRAL:65` names a fixture file. `LAB-BLOOM-DEPTH:82`, `LAB-POE-ORDER:87`, `LAB-CURRENT-MARGIN:93`, `LAB-VALUE-SOURCED:100` declare the expectation with **no fixture** | **CONTRA** with `meta prompt:157,267` ("every fixture marked reject actually rejected") | `checks.v1.yaml` |
| F88 | `l01_unpowered_power_path.json` shape | the file itself; four `L01-*` checks read it | Gap — no schema in `schema/`, unlike every other data file | new `schema/l01_power_path.schema.v1.json` |
| F89 | Safety-floor enforcement | `calibration.v1.yaml:61-65` declares 4 floor items; `checks.v1.yaml:16-20` `CAL-SCHEMA-AGREE` covers **pedagogy caps only**; none of `power_off_before_rewiring`, `troubleshooting_starts_power_off`, `adult_guide_separate_from_child_text`, `stop_if_warm` maps to a schema constraint or a stable check | **Gap** — the safety floor is the least enforced part of the system (Codex R1) | `calibration.v1.yaml` `enforced_by` + `checks.v1.yaml` |

**Totals: 95 facts inventoried (88 + 7 added or split during Codex review).
25 CONTRADICTION, 42 DUPLICATE-AGREEING, 19 DERIVED (15 with no sync mechanism),
9 unenforced-claim gaps.** Two of my original contradictions (F15 teacher-framework
limb, F82 A5 framing) were withdrawn on Codex's evidence; three were reclassified
from contradiction to missing-mapping or ungoverned-redundancy (F40, F42, F82).

---

## 2. Contradictions, most severe first

Severity = what breaks if it is left. A contradiction that stops a release gate from
passing outranks one that merely misinforms a reader.

**1. The no-controller scope has no owner and the curriculum contradicts it (F86).**
"Without using the Arduino as a controller" is the workbook's defining promise. It
is stated only in `roster.md:3`, `lab_brief.md:3`, `teacher_framework.md:5,251,275`
and `teacher_audit.md:9,55` — four prose files, three of them already flagged as
divergent, all at the bottom of the precedence order. It appears in none of
`calibration.v1.yaml`, `curriculum.v4.yaml`, any schema, `readme.md`,
`how_it_works.md`, `pedagogy.md` or `component_lab_template.v1.md`. Meanwhile
`curriculum.v4.yaml` — which outranks all four — gives 14 of 35 labs
`core_activity.mode: adult_led_controller_station` (L16, L18, L20–L29, L32, L33),
lists `controller output` as a `component_set.supporting` item (`:759`), and mentions
a controller 49 times. Either the promise or a third of the curriculum is wrong, and
nothing in the system can tell which. **Needs a human decision** — see §3, P2.

**2. `teacher_audit.md` is an unprovenanced input that certifies contradicted facts
(F82, F15, F32).** Shipped in `assets/`, named as an input at `meta prompt:67`, no
declared status, sourcing a relative `labs/` that does not exist in CREATOR. It
certifies L01 as "5 V USB-only, no 9 V clip on rail" (`:17`) against a manifest whose
L01 traces battery → module → rail, and it asserts "exactly three infographic briefs"
for every lab (`:9,11`) against a manifest that gives every lab four.

**3. Gate 4 cannot pass as documented (F64, F63).** `routes.v1.yaml:9` states "Every
route in this file was proven"; `:73-77` marks `imagegen` `status: UNPROVEN,
command: null`. `readme.md:110-112` and `how_it_works.md:354` both list "real
ImageGen" among what gate 4 proves. `how_it_works.md:304-307` says two routes exist
where the file declares four, and `readme.md:26` omits `pdftoppm` from the PATH
preconditions although `ROUTE-PROVEN` demands a real call on it.

**4. Gate 3 has no checks behind it, and the stage vocabulary disagrees (F57, F58).**
`meta prompt:150-151` names six categories including `simulated`; `checks.v1.yaml`
uses five, calls the golden one `golden` rather than `live-golden`, and assigns
**no** check the stage `simulated`. Eight of the 41 ids have no stage at all. So the
release gate "every check in `checks.v1.yaml` executed" and the gate sequence cannot
both be satisfied as written.

**5. Three mutually exclusive mandatory lab structures (F30).** `lab_brief.md:5-21`
("use this exact order", 15 sections), `teacher_framework.md:27-168` ("may not omit a
heading", 13), `component_lab_template.v1.md:17-137` ("Required lab structure", 12).
None maps to another or to the schema's seven blocks. An author cannot satisfy all
three.

**6. Four different mandatory visual counts (F32).** Five
(`component_lab_template.v1.md:139-148`), exactly three (`teacher_audit.md:9`), four
for six named labs (`roster.md:61`), four for all 35 (`curriculum.v4.yaml`), at least
three (`lab.schema.v3.json:1378`).

**7. Reviewer count 12 vs 8 (F45).** `checks.v1.yaml:153-155` and `meta prompt:110,269`
say twelve; `how_it_works.md:244,355` and `readme.md:111-113` say eight. The word
"twelve" appears in neither document. `limits.v1.yaml:14` silently assumes twelve.

**8. The template defines a `power_profile` the schema rejects (F23).**
`component_lab_template.v1.md:75-89` gives a normative YAML block with nine fields;
`lab.schema.v3.json:1256-1293` requires six different ones with
`additionalProperties: false`. A lab following the template cannot validate.

**9. `CAL-SOURCE-VERIFIED` names an enforcer that cannot enforce it (F24).**
`calibration.v1.yaml:75` maps `power.permitted_inputs` to
`lab.schema → safety.power_profile.source`, which is `{"type":"string","minLength":5}`
— no enum, no pattern, no link to the calibration ids.

**10. A 35-lab ceiling inside a schema that says it has none (F37, F40b).**
`curriculum.schema.v4.json:132` says "the schema does not fix a count"; `:215,222`
constrain prerequisite references to `^L(0[1-9]|[12][0-9]|3[0-5])$`. `:126` also
claims to enforce ordering, contiguity, uniqueness and an L01 start that it cannot
express. Both violate `CUR-COUNT-DERIVED`.

**11. `lab.schema.v3.json` contradicts itself on block count (F29).** `:5` "Five
co-equal blocks"; `:8-16` seven required.

**12. A6 is misattributed twice (F61).** `failures.v1.yaml:30-32` defines it as L01
self-contradiction; `how_it_works.md:84` assigns it to the base/override merge and
`:430` fuses both.

**13. `VIS-03` does not exist (F48).** `how_it_works.md:225` cites it; it is not among
the 41 ids in `checks.v1.yaml`. The document explaining why advertising an unasserted
check is a drift stop does exactly that.

**14. Two model-eligibility mechanisms that disagree (F75–F78, F79).**
`routing_policy.v1.yaml` gates by risk tier; `model_registry.v1.yaml` gates by
`allowed_for` capability labels. Only 1 of 8 labels is also a task name, so
`child_explanatory_writing` is medium-risk (terra eligible by policy) with no matching
label (terra ineligible by registry). The `low` tier has no task; `gpt-5.6-luna` is
unreachable. `quality_gates.v1.yaml` has three domain gates against the controller's
four review domains, and calls one `visual` where the controller says `graphic`.

**15. `readme.md`'s inventory and self-containment claims are false (F83, F84, F25).**
Every count is wrong; "nothing outside this folder is required" is contradicted by the
`work/…` photo path in three files, by the external binaries at `:25`, and by the two
declared outside reads at `meta prompt:70-72`.

**16. Reject fixtures that do not exist (F87).** Four of five checks declare
`fixture_expectation: reject` with no fixture, making `meta prompt:157,267` vacuous.

**17. ACT semantics (F74c), `stop if warm` vs `hot` (F21), and the log's empty-set
guarantee (F74).** `meta prompt:289` says ACT records completed actions; the schema
requires one at start and one at completion. `teacher_framework.md:66` weakens a floor
item that `calibration.schema.v1.json:94-108` marks non-tunable. `unclosed_starts` is
described as mandatory-empty but is not in `required`, so `LOG-PAIRED` passes
vacuously on a log that omits it.

---

## 3. Proposed changes

Principles applied: one owner per fact; prefer DELETE over SYNC; a derivation is
permitted only if a named check keeps it true. "Round" is the Codex round in which
the change reached its approved form — R2 = approved or amended in round 2,
R3 = settled in round 3.

### Tier 1 — a gate cannot pass, or a shipped claim is false

| # | Change | Owner after | Round |
|---|---|---|---|
| **P1** | Remove `assets/teacher_audit.md` from the input set. Codex amended R2: a header alone is insufficient while it remains a meta-prompt input, and the `assets/legacy/` destination is itself out of scope — so this is **reported, not made** (see §5) | `assets/legacy/` | R2 amended |
| **P2** | Give the no-controller scope an owner: a `scope:` block in `calibration.v1.yaml`. Then either (a) delete the absolute exclusions at `roster.md:3`, `lab_brief.md:3`, `teacher_framework.md:5` — false against the manifest — or (b) remove `adult_led_controller_station` from both mode enums and re-mode 14 labs. **Escalated to a human**; Codex confirmed R2 this is a product decision, not cleanup | `calibration.v1.yaml` | R2 approved |
| **P3** | `controller.v1.yaml` owns reviewer topology (add `pdf_review_domains` beside `PDF_VISUAL_QA`, giving a complete 3×4). `REV-COUNT-TWELVE` asserts it **generically against controller data**, not as a literal 12 in two files. Fix `how_it_works.md:244,355` and `readme.md:111-113` | `controller.v1.yaml` | R2 amended |
| **P4** | `checks.v1.yaml` `stage` owns check **categories** only; the six-gate **sequence** moves to a dedicated gate manifest. Add missing stages, rename `golden`→`live-golden`. Codex amended R2: **do not invent `simulated` ids to populate a category** — each needs a real assertion | `checks.v1.yaml` + gate manifest | R2 amended |
| **P5** | Make `fixture_expectation` legal only when `fixture` is present, or add an explicit non-fixture negative-test indicator. Codex amended R2: my "vacuous" claim was too strong — tests may generate invalid cases dynamically | `checks.v1.yaml` | R2 amended |
| **P6** | `lab.schema.v3.json` `safety.power_profile.source` gains a form pattern; **`CAL-SOURCE-VERIFIED` owns the cross-file membership lookup** and `calibration.v1.yaml:75` stops claiming JSON Schema does it. Delete the rival YAML block at `component_lab_template.v1.md:75-89` | `checks.v1.yaml` + `lab.schema.v3.json` | R2 amended |
| **P7** | Docs: two routes → four; add `pdftoppm` to `readme.md:26`; narrow `routes.v1.yaml:9` to the three proven routes. Codex amended R2: **keep ImageGen as a gate-4 requirement** and state plainly that it is unproven so gate 4 cannot yet pass — making it optional is a product decision | `routes.v1.yaml` | R2 amended |
| **P8** | Same loose `^L[0-9]{2,3}$` in both schemas. Codex amended R2: a `$defs` in one schema is not shareable by the other; a genuinely shared definition needs a third schema or an external `$ref` | both schemas | R2 amended |
| **P9** | Delete `prepares_for` from `curriculum.schema.v4.json` and all 35 entries — **for lack of a declared semantic and any consumer**, not on a derivation claim. See §4 for the reasoning correction | `curriculum.v4.yaml` `prerequisites` | R3 settled |
| **P10** | Narrow `curriculum.schema.v4.json:126,132` to what the schema actually enforces; ordering and contiguity stay in `CUR-IDS-CONTIGUOUS` | `checks.v1.yaml` | R2 approved |

### Tier 2 — one fact, one owner

| # | Change | Owner after | Round |
|---|---|---|---|
| **P11** | `lab.schema.v3.json:5` "Five co-equal blocks" → seven, named | `lab.schema.v3.json` | R2 approved |
| **P12** | Add the missing `concrete_before_abstract` entry to `enforced_by`; replace `minProperties: 7` with an explicit `required` list of the seven cap names. Codex amended R2: **decide whether `recommended` is a supported calibration value before touching the lab schema** | `calibration.v1.yaml` | R2 amended |
| **P13** | Rename `curriculum.v4.yaml`'s per-lab `visual_roles` → `visual_briefs` (and `CUR-VISUAL-ROLES` with it), resolving the homonym; `lab.schema.v3.json $defs/visual.role` owns the enum. Settle the count in the schema and delete the rival counts and role lists. Codex amended R2: **do not delete `photorealistic_roles` merely because `source_kind` exists** — source kind says how an asset was made, not which brief must be photorealistic; migrate it to a validated owner or drop it deliberately | `lab.schema.v3.json` | R2 amended |
| **P14** | Encode the seven-role sufficiency matrix. Codex amended R2: `uniqueItems` cannot compare `role` inside object arrays, and `CUR-VISUAL-ROLES` validates the manifest, so it is the wrong owner — this needs a **named dossier-level coverage check** | new check | R2 amended |
| **P15** | Make `carries_exact_electronic_fact` required. Codex amended R2: **whitelist** the roles ImageGen may serve (purpose/application, mechanism, expected result) rather than blacklisting two — prohibited for identification, orientation/pins, connection maps, safety evidence | `lab.schema.v3.json` | R2 amended |
| **P16** | `lab.schema.v3.json` owns block structure; `component_lab_template.v1.md` keeps its 12 sections plus a mapping table to the schema blocks. Delete the rival structures at `lab_brief.md:5-21` and `teacher_framework.md:27-168`, keeping the framework content genuinely absent from the schema | `lab.schema.v3.json` | R2 approved |
| **P17** | Repoint the three `work/…` citations inside CREATOR. Codex amended R2: **`kit_evidence.md` owns evidence identity and hash**, and consumers reference a stable evidence id rather than duplicating a literal path — calibration should not own a reusable file path | `kit_evidence.md` | R2 amended |
| **P18** | Remove `VIS-03` from `how_it_works.md:225` **or** add it to the catalog. Codex amended R2: do not auto-substitute `PDF-VISUAL-REVIEW`; it is not necessarily the same assertion. Correct the A6 attribution at `:84,430` | `checks.v1.yaml` | R2 amended |
| **P19** | Give A1–A10 the `correction` and `checks` fields B1–B4 have; delete the duplicate mappings at `controller.v1.yaml:60,69,86,102` and `how_it_works.md:423-438`. Codex amended R2: **preserve the historical v5 gate labels as provenance**, only marking them historical | `failures.v1.yaml` | R2 amended |
| **P20** | Add a required `enforced_by` to each of the 41 check ids. Codex amended R2: this alone does not make B3 impossible — it needs **a schema for the check catalog plus a scanner meta-test** comparing every referenced stable id against the catalog | `checks.v1.yaml` | R2 amended |
| **P21** | Add `unclosed_starts` to `required`. Codex amended R2: keep cross-record guarantees in the `LOG-*` checks rather than restating them as pseudo-schema guarantees; P20 identifies their executors | `execution_log.schema.v1.json` + `checks.v1.yaml` | R2 amended |
| **P22** | `curriculum.schema.v4.json kit_power_profile` gains a required `input_id`. Codex amended R2: grammar alone is insufficient — add a cross-file check that the id exists in calibration and that its verification/evidence rules are satisfied | `calibration.v1.yaml` + a new check | R2 amended |
| **P23** | Map the four safety-floor items to enforcement. Codex amended R2: use **a separate safety-enforcement map**, not an overload of the pedagogy-only `enforced_by`. `teacher_framework.md:66` "hot" → "warm" | `calibration.v1.yaml` | R2 amended |
| **P24** | `CUR-ORIENTATIONS` has no manifest field to read. Retarget to dossiers only if it adds something beyond the already-required `orientation_cue`; otherwise delete | `lab.schema.v3.json` | R2 amended |
| **P25** | Add `schema/l01_power_path.schema.v1.json`, used by both the baseline and the reject fixture | new schema | R2 approved |
| **P29** | `routing_decision.schema.v1.json` is unenforceable as declared: **no `additionalProperties: false`** (verified), `task_class` unbound from the taxonomy, `selected_model` unbound from the registry and from `candidate_pool`, `reasoning_effort` unbound from the policy minimum for the recorded `risk`, and nothing requires `pro_mode`/independent QA for safety-critical work despite `routing_policy.v1.yaml:14-18`. Close the schema, add the expressible bindings, make the rest a named check | `routing/` | R3 raised by Codex |
| **P30** | No manifest→dossier linkage: nothing ties a dossier's `identity.lab_id`/`slug`/`kind` to its manifest entry, nothing asserts the two identical mode enums (F41) are equal, and nothing maps `requires_verified_circuit_data` → `designed_verified` (F42). One stable check owns the whole correspondence | new check | R3 raised by Codex |
| **P31** | `curriculum.schema.v4.json:134-138` permits a `lab_count` and says "the controller asserts this"; **no id in the 41-check catalog does, and the field is absent from the manifest** (both verified). Remove it — a declared count beside a countable list is exactly the redundancy this audit exists to remove | deleted | R3 raised by Codex |
| **P32** | Schemas for `checks`, `routes`, `controller`, `limits`, `failures` and `routing/*.yaml` — six declared contract inputs with no validating schema. Prerequisite for P20, and for `meta prompt:49` being satisfiable at all (F74d) | `schema/` | R3 raised by Codex |
| **P33** | P14 and P15 each get a stable check id, so neither is schema prose with no validation owner | `checks.v1.yaml` | R3 raised by Codex |

### Tier 3 — explanatory documents stop restating owned values

| # | Change | Round |
|---|---|---|
| **P26** | **My blanket-deletion list was rejected R2** and replaced: audit each statement in `how_it_works.md` / `readme.md` individually — keep explanatory summaries and the "why", delete only literal normative values and rules, and leave a pointer to the owner at each deletion | R2 rejected, replaced |
| **P27** | Delete the stale inventory counts at `readme.md:34,36,38,40`. Codex amended R2: **rewrite rather than delete** the dependency statement, distinguishing "no extra input assets" from required tools, declared external reads, and output locations | R2 amended |
| **P28** | `roster.md`'s 35-item list is removed, or becomes a generated and checked derivative of the manifest. `kit_evidence.md:5` "35-lab curriculum" → "the curriculum". The retained scope paragraph depends on P2 | R2 amended |

### The governance rule — replaced, not amended

My proposed 7-level total precedence order was **rejected in R2** on a point I accept:
calibration cannot outrank a schema that validates calibration itself, so a total
order is the wrong shape. Replaced with intersecting contracts, in a new in-scope
`assets/governance.v1.yaml` (the meta prompt is not editable in this task, so it
points at the file rather than owning the model):

- **domain facts** — `calibration.v1.yaml`, `curriculum.v4.yaml`
- **valid shapes** — `schema/*.json`
- **executable behaviour** — `controller`, `checks`, `routes`, `limits`, `failures`, `routing/*`
- **build and release** — the meta prompt
- **prose guidance** — `component_lab_template.v1.md`, only where contracts are silent
- **explanatory** — `readme.md`, `how_it_works.md`, `pedagogy.md`, `assets/*.md`

with four rules:

1. A schema validates its own domain-fact file; neither outranks the other, and a
   disagreement is a defect in one of the two, resolved by inspection.
2. A cross-contract conflict is a defect. Resolve it using the fact's named
   authoritative source and evidence; a validator may reject a mismatch but never
   settle the authority question. If no authoritative source is named, report an
   ownership defect. *(Codex R4. My draft said "the mechanically checkable one wins",
   which conflates enforcement with authority and would let a wrong schema `const`
   override calibrated evidence. The final clause matters here: several of the 42
   duplicate-agreeing facts have no named owner at all, and that absence is now
   itself reportable.)*
3. An explanatory document may not introduce a requirement. A rule stated only there
   and absent from every contract is a defect. *(This is what would have stopped
   `VIS-03`.)*
4. A fact declared in more than one contract must have a named check asserting the
   declarations agree, or one declaration is deleted. *(This is what stops the
   42 duplicate-agreeing facts in §1 from drifting back apart.)*

**P20 final form (R4):** each of the 41 check ids carries **both** `enforced_by`
(where the assertion runs) and `authoritative_source` (which file owns the fact being
asserted). These are different questions; the round-2 form collapsed them.
**P32 final form (R4):** `assets/governance.v1.yaml` is included in its own schema
coverage.

---

## 4. What Codex disputed, and how it resolved

Four rounds. Codex disputed nine claims; I conceded seven outright, narrowed two, and
won one. Codex raised eighteen findings I had missed.

### Conceded — Codex was right and I was wrong

**C5, the teacher-framework supply claim.** I wrote that
`teacher_framework.md:176` ("a rectangular 9 V battery is not a default breadboard
source") declares unsafe the one supply calibration marks `verified_official`. Codex
pointed out that `calibration.v1.yaml:37` describes the battery as *feeding the power
module*, while the framework rejects it as a *direct breadboard source*. Different
things. I checked both lines and withdrew the claim. What survives is narrower:
`roster.md:3` makes USB the standard source and is not in the declared-divergence
list.

**C1, `teacher_audit.md` as an A5 violation.** I framed it as "reporting static
coverage as live generation". Codex: a historical audit of manuscripts can coexist
with "v3 never produced an accepted L01"; the audit never claims live generation.
Withdrawn. Reclassified to what actually survives — an input with no declared status,
a dangling `labs/` source path, and two live contradictions it participates in.

**C3, the reviewer count.** My claim that the controller "cannot" produce twelve was
too strong: one `PDF_VISUAL_QA` state can fan out to four calls. Restated as
under-specification, not impossibility.

**C6, `CAL-SOURCE-VERIFIED`.** I claimed the check was unenforceable. Codex: it can be
a cross-file test; nothing says JSON Schema alone performs it. The defect is the false
`enforced_by` mapping, which is a smaller and more precise finding. This changed the
fix (P6) for the better.

**C9, the 35-lab ceiling.** Not a total ceiling — L36 validates as an `id`; the
ceiling is on the reference grammar.

**C15.** I asserted that `CAL-SCHEMA-AGREE` "silently skips" a cap. There is no
implementation, so I was asserting runtime behaviour I could not observe.

**D15.** A real error: I listed `checks.v1.yaml` as a fourth copy of the six-gate
sequence. Its `stage` values are check categories, not gates. This mattered — it
changed P4 from "align four copies" to "separate two different things".

**C16 and F40 reclassified.** `circuit_status` vs `circuit.status` are plausibly
lifecycle states, not a declared contradiction; `prepares_for` asymmetry is ungoverned
redundancy, since no contract says the two fields must be inverses.

### Narrowed — I accepted the correction but kept the finding

**N1, C4 visual roles.** Codex was right that "five incompatible taxonomies"
overcalled it: manifest strings are asset briefs, schema roles are output categories.
I held that the defect survives in narrower form — `curriculum.schema.v4.json:280`
names the field `visual_roles`, `checks.v1.yaml:48` names the check
`CUR-VISUAL-ROLES`, and `lab.schema.v3.json:1591` names the enum `role`: one word,
two meanings, no declaration. Codex agreed in R3 and it became the rename in P13.
Codex's own counter-finding — four different mandatory visual *counts* — was sharper
than my original and replaced it as F32.

**N2, `teacher_audit.md`.** Having withdrawn the A5 framing, I pointed out that Codex
had called the file "not evidence about current v7 output" while simultaneously citing
`teacher_audit.md:9` as the authority for the three-visual contradiction. It cannot be
both outside the evidence base and a party to a live conflict. Codex agreed in R3:
"I was distinguishing evidentiary validity from conflict status poorly."

### Where I pushed back and Codex conceded

**P9, `prepares_for`.** Codex rejected deletion on the ground that "current asymmetry
proves `prepares_for` is not derivable from `prerequisites`". That does not follow: an
inverse relation can be perfectly derivable while its stored values are wrong —
disagreement is evidence the two conflict, not evidence one carries information the
other cannot. Codex accepted this in R4 ("You are right on P9"). The action was
unchanged; the *reason* was, and the reason is what a future reader will rely on.

### Where Codex rejected my proposals outright

**P26, blanket deletion from `how_it_works.md`/`readme.md`.** My line-range list would
have removed genuine explanation along with restated values. Replaced with a per-
statement audit.

**The precedence rule.** I proposed a 7-level total order with calibration at the top.
Codex: calibration cannot outrank a schema that validates calibration itself, and
these are intersecting contracts, not a hierarchy. Correct, and it invalidated the
shape of my proposal, not just its content. Replaced with the governance model in §3.
Codex then rejected my *replacement's* second rule ("the mechanically checkable one
wins") on the same class of error — conflating enforcement with authority — and
supplied the wording now in §3.

### The eighteen findings Codex added

Adopted in full: the no-Arduino conflict (which I had also found independently before
reading the review); the four-way visual-count contradiction; the curriculum schema
claiming enforcement it cannot express; three unbound supply representations; the
safety floor being almost entirely unenforced; the seven-role sufficiency matrix being
asserted but not encoded; the ImageGen constraint never firing because its field is
optional; all 41 check ids lacking an executor; the execution-log schema's headline
guarantees being inexpressible in JSON Schema; the ACT-semantics conflict; the
unfulfillable "validate every input against its schema" precondition; the
`routing_decision` schema being unenforceable as declared; the missing manifest→
dossier linkage; the ungoverned `lab_count`; and the need for schemas across six
unschematized contract inputs.

---

## 5. Changes needed in out-of-scope files — reported, not made

### `prompts/meta_curriculum_prompt.prompt.v5.md`

| Line | Change | Because |
|---|---|---|
| `:49`, `:239` | "Validate each file against its schema before reading a value from it" is unfulfillable — schemas exist for 4 files only. Either narrow the sentence or add the missing schemas | F74d |
| `:67` | drop `assets/teacher_audit.md` (moving to `legacy/`) and `assets/roster.md` (35-item list deleted) from the input table | F82, F39 |
| `:70-72` | "Two reads reach outside `CREATOR`" is false while three files cite the `work/…` photo path — true again after the repoint | F25, F84 |
| `:76-83` | replace the 5-level precedence with a pointer to the single owned list; the current list does not rank `component_lab_template.v1.md`, `readme.md`, `how_it_works.md` or `pedagogy.md` | §3 precedence rule |
| `:86-88` | add `roster.md` to the named divergences, or resolve it | F15 |
| `:150-151` | stage vocabulary must match `checks.v1.yaml` after the rename | F57 |
| `:157`, `:267` | "every fixture marked reject actually rejected" is vacuous — 4 of 5 have no fixture | F87 |
| `:289` | "`ACT` entries record completed actions" contradicts `execution_log.schema.v1.json:32`, which requires an ACT at start *and* completion | F74c |
| `:110`, `:269` | correct as-is (twelve); the divergence is in `readme.md`/`how_it_works.md`, which are in scope | F45 |

### `assets/legacy/`

No changes. Receives `teacher_audit.md` under the proposal.

### `plans/`, `how_it_works.typ`, `how_it_works.png`

`how_it_works.typ` and `how_it_works.png` are the typeset form of `how_it_works.md`
and will carry every value deleted from it under P26. They must be regenerated from
the corrected Markdown, or they become a fourth copy of the facts being centralised.
No changes needed in `plans/`.

---

## 6. Still unagreed, and what needs a human

**Nothing remains unagreed between the analysis and Codex.** Round 4 verdict, verbatim:
"I approve the proposal unconditionally." Codex had earlier stated (R4): "I agree the
analysis is correct and complete, and I approve the proposal."

Three things are nevertheless *undecided*, and no amount of further review will settle
them, because they are product decisions rather than consistency questions. Both
reviewers agree they must go to a human.

**1. P2 — is `adult_led_controller_station` intended?** Fourteen of thirty-five labs
declare it. Four prose files promise the workbook uses no controller. One of the two
is wrong and the evidence cannot say which, because the constraint has never been
written into a contract. Deciding it (a) makes the promise false and requires editing
three prose files, or (b) makes a third of the curriculum wrong and requires re-moding
fourteen labs and removing an enum value from two schemas. This is the single most
consequential item in the analysis.

**2. P7 — is ImageGen optional?** `routes.v1.yaml` marks it `UNPROVEN` with a `null`
command while two documents list it among what gate 4 proves. The proposal states the
contradiction plainly rather than resolving it, because resolving it means deciding
whether a lab may ship without generated supporting visuals. Codex was explicit (R2):
do not remove it from a passing gate-4 requirement unless the product decides it is
optional.

**3. P12 — is `recommended` a supported calibration value?**
`calibration.schema.v1.json:61` permits `required | recommended` for
`concrete_before_abstract`, but a required free-text field in the lab schema can only
express `required`. Either the enum loses a value it cannot enforce, or the lab schema
gains a constraint. Codex asked (R2) that this be decided before touching the schema,
and I agree — changing the schema first would guess at a pedagogical intent nobody has
stated.

### Two limits of this analysis, stated plainly

- **No implementation exists.** Every check in `checks.v1.yaml` is an assertion in
  prose. Where the analysis says a check "does not cover" something, it means the
  specification does not cover it — not that a running test was observed to miss it.
  Codex corrected me on exactly this point at C15, and the correction applies
  throughout §1.
- **`assets/legacy/`, `plans/`, and the meta prompt were read but not audited for
  internal consistency**, per scope. Contradictions *between* them and the in-scope
  files are recorded in §5; contradictions *within* them are not.
