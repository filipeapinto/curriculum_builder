# Gate Flakiness Planning Log

Append-only record for the planning, QA, test-planning, and implementation-prompt workflow.
Existing entries must not be edited or removed; later corrections are new entries.

## Objective

Diagnose and eliminate the reported class of defect in which a phase 4 or phase 5 gate
returns a different verdict on a rerun with no change to repository source between runs,
then produce an implementation plan, an independent Critical/High QA pass, an ordered
execution test plan, and a GOAL/TEST/LOOP implementation prompt.

## Entry template

```text
### <UTC timestamp> — <agent/task>
- Action: <work performed>
- Paths touched: <paths, or none>
- Evidence/decision: <verification or decision rationale>
- Issues: <critical/high findings, blockers, or none>
```

## Entries

### 2026-08-03T15:24:00Z — /root
- Action: Read `plans/provider_correction/` end to end to establish the artifact set and
  sequence this workflow is asked to reproduce, then inspected the live gate machinery:
  `tests/run_gates.sh`, `tests/gates/runner.py`, `registry.py`, `common.py`, the phase-4 and
  phase-5 gate modules, and `curricula/arduino_kit/verify_domain.py`.
- Paths touched: None.
- Evidence/decision: The reference workflow is six artifacts — an append-only log, an
  implementation plan revised in place after QA, a focused Critical/High QA report, an
  ordered execution test plan, a GOAL/TEST/LOOP prompt, and a final standing audit. Its
  defining property is that QA is an independent pass that gates the plan, not a
  self-review; on provider correction it caught four High findings the plan's own author
  missed. This workflow reproduces that structure and that sequence.
- Issues: None.

### 2026-08-03T15:26:00Z — /root
- Action: Ran a read-only reproduction before writing any plan. Phase 4 and phase 5 were
  each executed twice with `FR_RESULTS_DIR` redirected to a temporary directory outside the
  repository; phase-4 and phase-5 checks were additionally executed under `PYTHONHASHSEED`
  ∈ {0,1,2,7,999,12345,424242}. `common.production_files()` was enumerated live.
- Paths touched: None. No repository file was written; all gate results went to
  `/var/folders/.../tmp.5679sVfI9t/`.
- Evidence/decision: Back-to-back runs were byte-identical apart from the results filename;
  all seven hash seeds produced identical output. The intuitive hypothesis — that the
  harness is internally nondeterministic — is therefore **false**, and the plan's direction
  changed accordingly. Live enumeration showed the "production" scan set is 645 files, of
  which 448 are under `outputs/`, 53 under `.claude/`, 5 under `.pytest_cache/`, and 1 is a
  `.DS_Store`. Phase 5 reported 35 PASS, 3 FAIL, 0 BLOCKED of 38, with `FR-P0-CLEAN` failing
  on the dirty worktree, `FR-P0-NOSTALE` failing on hits including three inside
  `.claude/skills/curriculum-concept-visualization/` — an agent-authored directory added in
  the most recent commit — and `FR-P3-CAPS-OWNED` failing on two `docs/research/**` prose
  files. The mechanism is ambient state drift between runs, not scheduling or seeding.
- Issues: None. The reproduction is the finding.

### 2026-08-03T15:31:00Z — /root
- Action: Authored implementation plan v1 from the reproduction: freeze a baseline and
  corpus, land a diagnostic before any fix, separate ambient artifacts from repository
  content, correct the two gates whose subject is the developer's machine, remove the
  retroactive class-drift flip, and pin the execution environment.
- Paths touched: `plans/_eval_gf_bl/gate_flakiness.plan.v1.md`,
  `plans/_eval_gf_bl/plans.log.md`.
- Evidence/decision: Blast radius was traced through the declared dependency chain
  `FR-P2-DEFERRED` → `FR-P4-CHECK-MAPPING` → `FR-P4-AGREEMENT` (`registry.py:276`,
  `registry.py:260`), which is how drift in an agent scratch file reaches phase 4. A second,
  independent mechanism was found in `_class_drift_sweep` (`runner.py:196-231`), which
  rewrites an already-reported `PASS` to `FAIL` based on mechanism sets that several phase-5
  gates record conditionally on data (`fr_p5_verifier.py:151-153`,
  `fr_p5_manifest.py:140-144`).
- Issues: None pending Critical/High QA.

### 2026-08-03T15:36:00Z — /root/plan_qa
- Action: Completed independent focused Critical/High QA of plan v1 against the repository,
  the live gate run, and the harness's own stated rules.
- Paths touched: `plans/_eval_gf_bl/qa/plan_qa.v1.md`, `plans/_eval_gf_bl/plans.log.md`.
- Evidence/decision: Verdict CHANGES REQUIRED with **1 Critical and 4 High**. The diagnosis
  was accepted; the remedy was not. The Critical finding is that the draft's proposed
  exclusions would have violated the binding rule stated at `common.py:53-56` and made four
  detectors quieter — fixing the flake by making the gates blind, which is strictly worse
  than the symptom because a flaky gate is visible and a blind gate is not.
- Issues: Critical — name-list exclusion silently disables detectors. High — tracking status
  alone makes newly authored untracked files invisible; the plan cannot distinguish its own
  intended verdict changes from regressions against an already-red baseline; fixes were
  proposed for six causes never demonstrated to fire; and the exit-0 acceptance criterion is
  unreachable and would pressure the implementer into weakening `FR-P0-CLEAN`, the gate that
  guards `APPROVED`.

### 2026-08-03T15:40:00Z — /root
- Action: Incorporated all five QA remediations into plan v1 in place, without expanding the
  objective.
- Paths touched: `plans/_eval_gf_bl/gate_flakiness.plan.v1.md`,
  `plans/_eval_gf_bl/plans.log.md`.
- Evidence/decision: Replaced the name-list exclusion with a scan set derived from git as
  `(tracked ∪ untracked-and-not-ignored) − declared ambient`, with an assertion that ambient
  members are already ignored or generated and a hard failure if git errors. Added the
  frozen baseline and corpus fixture as step 0 and required per-gate justification. Added
  the standing rule that no cause is repaired until demonstrated to move a verdict, and
  moved six undemonstrated defects to an explicit deferred section with file:line and
  reasons. Replaced the exit-0 criterion with per-gate comparison and stated that
  `FR-P0-CLEAN` failing on the task's own uncommitted edits is correct behavior.
- Issues: None. Six latent defects are carried forward as declared deferred work.

### 2026-08-03T15:44:00Z — /root/qa_test_plan
- Action: Authored the ordered execution test plan, GF-T00 through GF-T09.
- Paths touched: `plans/_eval_gf_bl/qa/execution_test.plan.v1.md`,
  `plans/_eval_gf_bl/plans.log.md`.
- Evidence/decision: The plan opens with a baseline freeze that re-runs the twin-run check,
  so a future implementer discovers it if the "harness is deterministic" conclusion ever
  stops holding, and specifies that branch rather than leaving it to judgment. GF-T01
  reproduces the bug before any fix exists, so a step with no demonstrated cause is deferred
  by the plan's own rule. GF-T03 tests the scan set in both directions, because the
  must-be-included direction is the one that catches a fix which works by making detectors
  blind. GF-T02 requires the new determinism self-test to be seen to fail on a deliberately
  time-dependent gate, so it is not accepted merely for never having failed. Every gate
  invocation redirects `FR_RESULTS_DIR` outside the repository.
- Issues: None.

### 2026-08-03T15:48:00Z — /root/prompt_writer
- Action: Authored the Claude Code implementation prompt with explicit GOAL, TEST, and LOOP
  sections from the corrected plan and the execution test plan.
- Paths touched: `plans/_eval_gf_bl/prompts/gate_flakiness.prompt.v1.md`,
  `plans/_eval_gf_bl/plans.log.md`.
- Evidence/decision: GOAL states the reproduced diagnosis as settled so the implementer does
  not re-derive it, fixes the six-step order, and carries the two overriding rules. LOOP
  enumerates the specific evasions that would make the symptom vanish without fixing the
  defect — weakening an assertion, adding a waiver, moving an activation phase, excluding
  the triggering path, committing user work, fixing a deferred item — and requires the
  implementer to stop and say so when a gate is correctly reporting a real defect.
- Issues: None.

### 2026-08-03T15:52:00Z — /root/qa_log_auditor
- Action: Completed the final standing audit of the corrected plan, focused QA, execution
  test plan, implementation prompt, shared log, artifact hygiene, and workflow scope.
- Paths touched: `plans/_eval_gf_bl/qa/final_audit.v1.md`, `plans/_eval_gf_bl/plans.log.md`.
- Evidence/decision: PASS with 0 Critical and 0 High remaining. All five findings are
  materially remediated; the detector-blinding failure mode is closed at three independent
  points (design principle, bidirectional GF-T03, and the prompt's standing corpus rule);
  every participant is logged; and no repository source file was modified by this planning
  workflow.
- Issues: None. Implementation may proceed under the prompt, beginning at GF-T00.
