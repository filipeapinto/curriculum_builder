# Plan QA — contracts, schema, runtime, prompts, and gates

## Gate verdict

**FAIL** — 0 Critical, 3 High, 3 Medium, 0 Low findings.

The plan correctly identifies the three canonical policy entries, the schema's
duration-only `per_phase` group, and the hard-coded parser group that would fail after
that group is deleted. It is not implementation-ready because it misses a second active
prompt instruction, prescribes two test commands that execute no gates, and does not
specify regression coverage for the CLI contract it requires.

## Findings

### High — H1: the active-prompt inventory is incomplete

**Evidence.** The plan names only
`plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md:122`, the
`36,000 seconds` outer-task limit. The same active prompt also says at lines 139–141:
“The active per-lab, **per-state**, retry, and convergence limits remain binding inside
each attempt.” In the active limits manifest, the only `per_phase`/per-state entry is
`policy/limits.v1.yaml:38–42`'s 900-second timeout. Deleting `per_phase` while retaining
that sentence leaves an active instruction that says a now-removed duration-limit class
is binding. The repository itself establishes v6 as current and v4/v5 as superseded
history at `plans/simplification/prompt/migrate_external_run_evidence.prompt.v2.md:39–51`.

The plan's searches at lines 22 and 62 also do not match the actual comma-formatted
`36,000`, and exact key/value searches cannot find the descriptive `per-state ...
limits remain binding` instruction. Historical v3, v4, and v5 also contain `36,000`
but are superseded drafts; they should be classified, not edited.

**Required remediation.** Add v6 lines 139–141 to the mandatory prompt edit: remove
`per-state` and leave the still-valid per-lab non-time, retry, and convergence limits.
Expand the inventory/verification search to cover comma-formatted values and descriptive
time-limit wording (`wall time`, `per-state`, seconds/minutes/hours), then explicitly
classify v1–v5 as superseded prompt history and v6 as current.

### High — H2: both prescribed gate commands are non-executing

**Evidence.** `tests/gates/fr_p4_policy_schemas.py:374–384` is a CLI program requiring
`--check`; it contains no pytest tests. `tests/run_gates.sh:1–14` is the repository's
registered-gate runner, and `tests/gates/registry.py:249–271` registers the phase-4
policy/schema checks. Executing the plan's exact commands produced:

- `python3 -m pytest -p no:cacheprovider tests/gates/fr_p4_policy_schemas.py` →
  **0 collected**, exit 5.
- `python3 -m pytest -p no:cacheprovider tests/gates` → **0 collected**, exit 5.

By contrast, the actual focused commands
`python3 tests/gates/fr_p4_policy_schemas.py --check validate` and `--check agreement`
both passed on the pre-change tree and exercised their rejection fixtures.

**Required remediation.** Replace the two pytest commands with the supported commands:

```sh
python3 tests/gates/fr_p4_policy_schemas.py --check validate
python3 tests/gates/fr_p4_policy_schemas.py --check agreement
./tests/run_gates.sh 4
./tests/run_gates.sh 5
python3 -m unittest discover -s tests/runtime -v
python3 tests/check_meta_prompt.py
```

Retain the plan's dirty-tree caveat for `FR-P0-CLEAN`, but do not describe a zero-test
pytest invocation as a focused or broad pass.

### High — H3: the absence contract has no biting fixture or runtime CLI regression test

**Evidence.** `tests/gates/fr_p4_policy_schemas.py:237–252` only checks that every
remaining limit has a numeric value and a `--` flag. Its sole limit fixture at
`tests/fixtures/limit_without_number.reject.yaml` proves only the missing-number case
(`fr_p4_policy_schemas.py:318–325`). No existing runtime test imports
`runtime.run_curriculum.parser_for`, checks help/options, or rejects removed flags;
`tests/runtime/test_controller.py:1–118` tests controller behavior only. The current
CLI accepts `--max-run-seconds 1 --preflight` with exit 0 because parsed limit
overrides are not consumed by `main`; therefore an acceptance check based only on a
successful run cannot prove flag removal.

The plan asks for a “focused assertion” but does not name a negative fixture, does not
add a parser-focused runtime test target, and omits both from its final diff command.
The phase-4 gate could be implemented incorrectly and still have no fixture that bites
on a forbidden time entry, while the gate suite could pass even if a removed CLI alias
were manually retained.

**Required remediation.** Make the edit inventory explicit:

- Update `tests/gates/fr_p4_policy_schemas.py` with a detector for the three forbidden
  paths and flags while preserving the numeric/flag checks for remaining limits.
- Add a rejection fixture such as
  `tests/fixtures/time_limit_present.reject.yaml` and wire it to that detector.
- Add `tests/runtime/test_run_curriculum.py` to prove parser construction succeeds
  with no `per_phase`, all three removed options are absent/rejected, and representative
  non-time options remain present with policy defaults.
- Include both new files in verification/diff scope and run the runtime unittest suite.

### Medium — M1: conditional edit targets are not resolved to an exact scope

**Evidence.** Plan lines 16, 18, and 38–40 say to edit
`policy/controller.v1.yaml` and `meta_prompt/curriculum.prompt.v1.md` only “if” or
“if necessary,” and `policy/checks.v1.yaml` only after possible drift. Repository
inspection resolves those questions now:

- `policy/controller.v1.yaml:18` says code owns generic “timeouts” but names no
  duration, default, or flag.
- `policy/controller.v1.yaml:83`, `policy/routes.v1.yaml:128`,
  `runtime/checkpoint.py:21–34`, and `runtime/finalize_evidence.py:20,93` are elapsed-time
  telemetry.
- `policy/controller.v1.yaml:151`, `meta_prompt/curriculum.prompt.v1.md:56,96–97,
  283,377–379`, and `policy/checks.v1.yaml:266–268,308–312` remain valid for non-time
  limit and convergence contracts.

**Required remediation.** State the disposition rather than deferring it:
`policy/controller.v1.yaml`, `policy/checks.v1.yaml`, and
`meta_prompt/curriculum.prompt.v1.md` do **not** require edits for this change; retain
and verify them. If product intent is instead to ban the word/concept “timeouts” from
the controller contract, explicitly add controller line 18 as a required edit. Do not
leave the implementer to redefine scope after starting.

### Medium — M2: the representative-run acceptance is not executable as written

**Evidence.** `runtime/run_curriculum.py:45–47` always rejects
`--test-live-capabilities`, and lines 52–64 support simulated/golden simulation or
refuse live generation. The only currently runnable representative execution is a
simulation. Telemetry is concrete in `runtime/checkpoint.py:28`, but the plan gives no
command or assertion for it and cannot practically demonstrate a run exceeding the old
90-minute/10-hour thresholds.

**Required remediation.** Define the proof as (1) parser/source inspection establishing
that no duration policy is loaded or accepted, plus (2) an exact supported simulated
run command that reaches `ACCEPTED`, and (3) inspection/assertion that generated
checkpoints still contain numeric `elapsed_seconds`. Do not label this live generated-
curriculum coverage.

### Medium — M3: the plan conflates two different 36,000-second contracts

**Evidence.** `policy/limits.v1.yaml:49–52` is `per_run.max_seconds` for the meta run.
The v6 prompt explicitly says at lines 117–122 that its 36,000-second envelope covers
“the complete outer development task, not each individual L01 run.” The plan calls the
prompt text another run-cap instruction without recording this distinction.

**Required remediation.** Keep the v6 edit in scope if the intended outcome is to
remove time governance from the whole curriculum-generation workflow, but describe it
as the outer implementation-task wall-time envelope, not as another implementation of
`per_run.max_seconds`. Verify the policy cap and prompt envelope independently.

## Verified contract inventory

### Existing files that must be edited

1. `policy/limits.v1.yaml` — delete `per_lab.max_seconds`, all of `per_phase`, and
   `per_run.max_seconds`; retain all non-time entries and generic limit behavior.
2. `schemas/limits.schema.v1.json` — remove `per_phase` from `required` and remove the
   `per_phase` property. `per_lab` and `per_run` are generic entry maps and remain.
3. `runtime/run_curriculum.py` — stop indexing the deleted `per_phase` group; iterate
   actual supported groups/present mappings so the remaining policy-backed flags stay.
4. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md` — remove
   the outer 36,000-second bullet and the stale per-state-binding phrase.
5. `tests/gates/fr_p4_policy_schemas.py` — enforce the semantic absence contract and
   attach a biting rejection fixture.

### New test files required

1. `tests/fixtures/time_limit_present.reject.yaml` (name may vary) — forbidden-duration
   negative fixture for the phase-4 agreement detector.
2. `tests/runtime/test_run_curriculum.py` (name may vary) — parser/help/rejection and
   remaining-non-time-option regression coverage.

### Inspected files that should remain unchanged

- `policy/controller.v1.yaml`, `policy/checks.v1.yaml`, and
  `meta_prompt/curriculum.prompt.v1.md`: generic non-time limit/convergence ownership
  and elapsed telemetry remain valid.
- `runtime/session_bridge.py:130`: 45-second HTTP request safety timeout.
- `runtime/capability_cycle.py:134`: 300-second external subprocess safety timeout;
  line 146 is telemetry.
- `runtime/checkpoint.py` and `runtime/finalize_evidence.py`: elapsed-time telemetry.
- `policy/routes.v1.yaml:128`: elapsed-time reporting.
- `curricula/arduino_kit/teacher_framework.md`: learner-facing activity duration.
- `plans/simplification/prompt/implement_curriculum_runtime.prompt.v1.md` through
  `v5.md`: superseded prompt history; v3–v5 retain historical 36,000-second text.
- `plans/legacy_v3/run_curriculum.v3.py`: historical executable artifact, not imported
  by the active runtime; its 60-second transport timeout remains history.

## Agent-log entry for `plans.log.md`

- `/root/plan_qa_contracts` (plan QA reviewer A) performed a read-only contract audit
  of the remove-time-limits plan against active policy/schema/runtime/prompt/gate code,
  fixtures, runtime tests, prompt-version provenance, and repository runners. Commands
  included broad `rg` inventories, line-numbered file inspection, current CLI help and
  flag probes, direct phase-4 `validate`/`agreement` checks, both prescribed pytest
  probes (each collected 0 and exited 5), and the supported runtime unittest suite
  (43 passed). Result: **FAIL** with 0 Critical, 3 High, and 3 Medium findings; no
  production/source/test/plan file was modified by this reviewer.
