# Plan: make the curriculum creator executable unattended, and reusable for a second curriculum — v2

Supersedes `remediation.plan.v1.md`, which Codex judged **PLAN INSUFFICIENT**: 3 findings
fully covered, 11 partially, 2 not at all, one internal contradiction, and nine success
criteria of which none could distinguish a fix from its absence. v1 is retained as
evidence. Every change below is traceable to a v1 defect.

## 1. Goal — WHY

Take `curriculum_creator` to a state where `prompts/meta_curriculum_prompt.prompt.v5.md`
can be started by a human and left alone until it reaches a terminal state, and where a
second curriculum in a different domain reuses the machinery without editing it.

## 2. Success criteria — WHY

Every criterion below is a command whose output distinguishes a fix from its absence.
v1 failed this: its criterion 3 was `grep -rn "3[0-5]\]" schema/`, which passes today with
both defects present — the `\]` made it a regex matching nothing. Each criterion here was
run against the current tree and **must fail now**; a criterion that already passes is not
a criterion.

| # | Command | Must be, now | Must be, when done |
|---|---|---|---|
| 1 | `rg -F '3[0-5]' schema/` | 2 hits | 0 hits |
| 2 | `python3 tools/check_inputs_have_schemas.py` | fails | passes — every entry in the prompt's Inputs table maps to a validator that ran, not merely a file that exists |
| 3 | `python3 tools/check_external_paths.py` | fails — `curriculum.v4.yaml:19` and both L01 files cite outside paths | passes — every outside reference is either repointed or listed in an explicit `declared_external_reads` allowlist with a reason |
| 4 | `python3 -m pytest tests/test_log_pairing.py` | no such test | passes 6 cases: unknown `closes`, duplicate `closes`, completion citing unknown ACT, out-of-order close, duplicate id, start never closed |
| 5 | `python3 tools/check_isolation.py` | fails | passes — proves no verdict file exists on disk at any point during a review pass |
| 6 | `python3 tools/check_checks_executed.py` | fails | passes — every id in `checks.v1.yaml` is executed by a named test; `stage: v7-runtime` requires a corresponding assertion in the v7 test suite, not a label |
| 7 | `python3 tools/check_domain_dispatch.py` | fails | passes — a full lab fixture validates against core **and** the domain schema its `domain_id` selects, and a lab whose `domain_id` names an unregistered domain is rejected |
| 8 | `python3 tools/check_docs_match.py` | fails | passes — counts, reviewer cardinality and file inventories in `readme.md`, `how_it_works.md`, `infographic.prompt.v1.md` match the repository |
| 9 | `python3 tools/check_no_competing_authority.py` | fails — `kit_power_profile` in the manifest and `power:` in calibration both define supplies | passes — exactly one authority per fact |

Codex's GREEN LIGHT is **not** a criterion. v1 listed it as criterion 1; a reviewer's
conclusion is an outcome, not evidence. It is the exit condition of Step 8, nothing more.

## 3. Scope & non-goals — WHY

**In scope**
- The twelve blockers and four non-blocking concerns from Codex review 2.
- The five findings from Codex's review of v1: the calibration contradiction, incomplete
  migration of the runtime contract, cross-artifact rules misattributed to JSON Schema,
  domain-dispatch theatre, and the undeclared engine dependency.
- The `tools/` validators the criteria above depend on. These are part of the work, not
  assumed to exist.

**Non-goals**
- Running the meta prompt.
- Building the second curriculum. Step 5 proves the split with a real fixture; it does not
  author a second domain's content.
- Rewriting `lab_brief.md` / `teacher_framework.md` to match calibration. Their divergence
  is recorded deliberately; a reviewer asking for it to be silenced is escalated (§8).

## 4. Context & assumptions — WHY

**Established by execution, not assumption**

| Fact | Evidence |
|---|---|
| `-C` does not contain a worker | A worker given `-C <its own dir>` **and** `-s read-only` read a sibling's verdict by absolute path, 0 ms, first attempt. Scratch directories cannot enforce isolation. |
| `codex exec` needs `--skip-git-repo-check` | `ROOT` is not a git repo; without it the call fails before any model call |
| stdin must be closed | without `< /dev/null` the process blocks forever on stdin, burning no CPU, looking alive |
| Only typst renders PDF; only `pdftoppm` rasterizes | no TeX engine, no Python PDF library importable |
| ImageGen has no proven invocation | never established in this environment |

**Assumptions**
- The architecture is sound. Thirty-plus findings across three reviews; none said the
  design is wrong.
- Learner age band is 9+; the pedagogy caps derive from it.
- A reviewer cannot read a file that has not been written. This is the only containment
  primitive available without a container or a second OS user, and it is sufficient
  (Step 4).

## 5. Steps — HOW

### Step 1: Build the validators first
- **Does:** Writes the nine `tools/check_*.py` scripts and `tests/test_log_pairing.py` that
  §2 depends on. Each must **fail against the current tree** before any fix is made — a
  validator that passes on a known defect is a false instrument, which is exactly what v1's
  criterion 3 was.
- **Produces:** `tools/`, `tests/`, and a recorded baseline showing all nine failing.
- **Depends on:** none. **Parallel?** yes. **Owner:** this session.
- **Why first:** v1 wrote fixes then claimed verification. This inverts it.

### Step 2: Resolve competing authorities — **DECISION REQUIRED**
- **Does:** Fixes the contradiction Codex found in v1. Three files currently define
  supplies: `calibration.v1.yaml → power`, `curriculum.v4.yaml → kit_power_profile`, and
  the proposed domain profile. Chooses one and deletes the others' claim.
- **Recommendation:** the domain profile owns supplies; calibration keeps `learner`,
  `pedagogy_caps`, `safety_floor`; `kit_power_profile` is removed from the manifest with
  its evidence URL migrated. Calibration's schema changes accordingly — v1 wrongly said it
  was unchanged while Step 3 removed a section from it.
- **Blocks:** Steps 5 and 6. **Owner:** user, then this session.

### Step 3: Mechanical corrections
- **Does:** Two lab-id regexes in `curriculum.schema.v4.json`; repoint the L01 files **and**
  `curriculum.v4.yaml:19` at `assets/official_kit_photo.jpg`; 8→12 reviewers in
  `how_it_works.md` and `infographic.prompt.v1.md`; refresh `readme.md`; state the naming
  convention canonically and verify it repository-wide; add `uniqueItems` on power-input
  ids and a min≤max constraint on calibration ranges (v1 covered neither).
- **Verified by:** criteria 1, 3, 8. **Owner:** this session.

### Step 4: Isolation by non-existence — the structural fix
- **Does:** Resolves the blocker that made v1 insufficient. Since no sandbox flag contains
  a worker, isolation comes from **what exists**, not what is forbidden: during a review
  pass the controller holds every verdict in process memory and writes **nothing** to disk
  until all four reviewers in that pass have returned. A reviewer cannot read a sibling
  verdict because no sibling verdict exists anywhere on the filesystem while it runs.
- **Enforced by:** `tools/check_isolation.py` — runs a real four-reviewer pass with a
  filesystem watch over the entire output root, and fails if any verdict artifact appears
  before the barrier. Also fails if a worker's structured output is read from a file rather
  than captured from its stdout.
- **Why this and not a container:** it needs no new dependency, it is testable with the
  tools present, and it makes the guarantee *structural* — the file's absence is the
  boundary. Docker or a second OS user would also work and are recorded as alternatives if
  this proves insufficient.
- **Verified by:** criterion 5. **Owner:** this session.

### Step 5: Domain split with real dispatch
- **Does:** Splits `lab.schema.v3.json` into `lab.core.schema.v1.json` (identity, pedagogy,
  sequence, visual machinery; `domain` opaque but requiring `domain_id`) and
  `schema/domain/electronics.schema.v1.json`. Adds `schema/domain/registry.v1.json` mapping
  `domain_id` → schema path + version, so dispatch is data rather than convention. Requires
  all seven visual roles or a validated omission waiver (v1 covered neither; the schema
  still says `minItems: 3`).
- **Guards against the theatre Codex named:** the criterion is not "two schemas exist" but
  "a full lab fixture passes both layers, and an unregistered `domain_id` is rejected".
- **Verified by:** criterion 7. **Depends on:** Step 2. **Owner:** this session.

### Step 6: Schemas and cross-artifact validators
- **Does:** Writes schemas for `limits`, `routes`, `checks`, `failures`, `pipeline`. Then —
  the part v1 got wrong — implements as **code** the rules JSON Schema cannot express: that
  a fixture named by a check exists; that a route marked `UNPROVEN` is not cited by any
  gate; that a lab's declared supply id exists in the selected domain profile and is
  `verified_official`; that `unclosed_starts` is computed rather than authored. v1
  attributed all of these to schemas.
- **Verified by:** criteria 2, 4, 6. **Depends on:** Steps 2, 5. **Owner:** this session.

### Step 7: Migrate the runtime contract, completely
- **Does:** Codex's point that adding files is not migrating. The prompt still names
  `assets/controller.v1.yaml` as authoritative and sends workers to `lab.schema.v3.json`.
  This step updates the prompt, `checks.v1.yaml`, the precedence list, the release gates and
  the documentation in one pass, and retires the superseded artifacts. Also resolves:
  bootstrap log root and its migration semantics; deterministic model selection including
  availability, substitution and ties; imagegen proven or removed with the visual contract
  revised; PDF acceptance given a defined pixel metric, fixtures and failure semantics; the
  pipeline encoding four PDF-review invocations.
- **If Step 2's engine option is taken:** `engine/` is added to the prompt's input
  inventory with a hash and a compatibility rule — Codex noted it would otherwise be an
  undeclared runtime dependency inside immutable `CREATOR`.
- **Verified by:** criteria 6, 8, 9. **Owner:** this session.

### Step 8: Re-review
- **Does:** Submits to Codex. Independently verifies each finding before accepting it — of
  the last two reviews, every claim checked held, but checking is the rule regardless.
- **Owner:** Codex, then this session.

## 6. Artifacts & output format — HOW

```text
curriculum_creator/
  tools/check_*.py                     NEW  the nine validators §2 depends on
  tests/test_log_pairing.py            NEW  six pairing failure modes
  schema/
    lab.core.schema.v1.json            NEW
    domain/registry.v1.json            NEW  domain_id -> schema + version
    domain/electronics.schema.v1.json  NEW
    limits|routes|checks|failures|pipeline .schema.v1.json   NEW
    lab.schema.v3.json                 RETIRED in Step 7, not merely superseded
  assets/
    domain/electronics.v1.yaml         NEW  supplies, rails — sole authority
    calibration.v1.yaml                power removed; schema updated to match
    curriculum.v4.yaml                 kit_power_profile removed; photo path repointed
  plans/remediation.plan.v1.md         retained as evidence
```

## 7. Verification — HOW

The nine commands in §2 are the verification. Two disciplines govern them:

**Every validator must fail before it passes.** Step 1 records a baseline of all nine
failing against the current tree. A validator that cannot demonstrate the defect it
detects is not evidence.

**No criterion is a conclusion.** Not "Codex approves", not "the schema exists", not "the
documentation says twelve". Each names a command and the output that distinguishes fixed
from broken.

## 8. Risks, failure handling & escalation — HOW

**Per-step failure policy.** Step 1 failing to fail is itself a defect — investigate the
validator, not the tree. Steps 3–7 are corrections: fix, re-run the criterion, re-verify.
Step 2 blocks downstream work and never proceeds on assumption. Step 8 returning findings
is the expected case.

**Risks**

| Risk | Why it matters | Mitigation |
|---|---|---|
| A validator that passes on a defect | v1's criterion 3 did exactly this, in a plan whose risk table named the failure mode | Step 1 requires a recorded failing baseline before any fix |
| Isolation by non-existence has a hole | If any worker writes its verdict directly rather than returning it, the barrier is gone | `check_isolation.py` fails if output is read from a file rather than captured from stdout |
| Domain split becomes theatre | An opaque block proves only that opacity is permitted | Criterion 7 requires a full lab through both layers plus rejection of an unregistered domain |
| Partial fixes reported complete | Demonstrated three times today: one of three regexes; a photo copied but not repointed; a validation rule asserted while creating five unschema'd assets | Every criterion is a command, run and shown, never a claim |
| Reporting a background job as working | Demonstrated twice today: a dead process whose status field still said running; a process blocked on stdin at 0.02s CPU | Check process liveness and output growth, never a status field |

**Escalate to a human when**
- Step 2's authority decision is needed.
- ImageGen cannot be proven and the visual sufficiency matrix must change as a result.
- Isolation by non-existence proves insufficient and a container or second OS user becomes
  necessary — that is a new dependency, not an implementation detail.
- A review finding contradicts a decision recorded here on purpose, such as the
  calibration/prose divergence.
