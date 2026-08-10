# RetryTracker Per-Unit State Reset Planning Log

Append-only record for the planning, QA, test-planning, and implementation-prompt
workflow. Existing entries must not be edited or removed; later corrections are
new entries.

## Objective

Fix the defect in runtime/retry.py where RetryTracker's per-unit revision state (self.failures, and the associated per-unit counters) is never reset at unit boundaries, so a fresh curriculum unit inherits the repeat-failure history of earlier units and can be permanently blocked by RetryLimit on unrelated content.

## Entry template

```text
### <UTC timestamp> — <agent/task>
- Action: <work performed>
- Paths touched: <paths, or none>
- Evidence/decision: <verification or decision rationale>
- Issues: <critical/high findings, blockers, or none>
```

## Entries

### 2026-08-03T15:18:32Z — plan_author
- Action: Authored implementation plan v1: add an explicit begin_unit(unit_id) boundary to RetryTracker that resets self.failures, self.revisions and self.used, plus six unit tests covering reset, idempotence and config preservation.
- Paths touched: plans/_eval_rtd_ws/_eval_rtd_ws.plan.v1.md
- Evidence/decision: Read runtime/retry.py (self.failures/revisions/used set only in __init__, never cleared); tests/runtime/test_retry.py (3 existing tests); repo-wide grep shows no production instantiation of RetryTracker outside runtime/retry.py and its test; policy/limits.v1.yaml declares max_revisions under per_lab and budgets retries inside per_lab.max_model_calls; baseline 'python3 -m unittest discover -s tests/runtime -t .' reports Ran 47 tests OK.
- Issues: None pending critical/high QA. Noted in-plan: repeat_failure_threshold sits under convergence rather than per_lab in policy, treated as per-unit by assumption and recorded as such.

### 2026-08-03T15:23:49Z — plan_qa_round1
- Action: Independent focused QA of plan v1 by a fresh subagent with no prior context. Verdict: CHANGES REQUIRED — 0 Critical, 3 High.
- Paths touched: plans/_eval_rtd_ws/qa/plan_qa.v1.md
- Evidence/decision: Reviewer verified claims against the repository and applied the proposed begin_unit to a scratch copy at /tmp/rtqa. Confirmed sound: 47-test OK baseline, no production RetryTracker call site, verbatim policy quotes, and that begin_unit works as written. Findings: (1) test 3.1 threshold arithmetic off by one, fails against the FIXED source; (2) git-cleanliness acceptance criteria unsatisfiable — baseline worktree already dirty in 6 paths including two the plan calls untouched, inviting destruction of uncommitted work; (3) verification step 7 compares gates to a baseline no step captures, and FR-P0-NOSTALE/FR-P0-CLEAN are already red.
- Issues: 3 High open, blocking. Plan must be revised before the execution test plan or prompt is written.

### 2026-08-03T15:25:15Z — plan_author
- Action: Revised plan v1 in place against QA round 1. Finding 1: rewrote step 3.1 to assert the repeat counter RESTARTS (repeat_threshold-1 successes then a raise) and added an explicit warning against the off-by-one phrasing. Finding 2: added step 0.4 capturing a verbatim git status --porcelain baseline snapshot, converted verification step 6 and the acceptance criteria from absolute-clean to delta-against-snapshot, and added an explicit prohibition on checkout/restore/stash/reset/clean plus a stop condition. Finding 3: added step 0.5 capturing a pre-change ./tests/run_gates.sh 5 baseline naming FR-P0-NOSTALE and FR-P0-CLEAN as known-red, dropped the 'if they were green at baseline' conditional in 4.2, and made verification step 7 a no-PASS-to-FAIL diff. Also tightened verification step 4, which QA recorded as a non-blocking observation, because it was provably vacuous as written.
- Paths touched: plans/_eval_rtd_ws/_eval_rtd_ws.plan.v1.md
- Evidence/decision: Confirmed the reviewer's counts independently: revision() raises when failures[key] >= repeat_threshold, so the threshold-th call raises; the baseline worktree is dirty in six paths including policy/limits.v1.yaml and schemas/limits.schema.v1.json; no step 0 substep captured a gate baseline. Revised in place per the skill's Step 4, no version bump, no scope expansion beyond the three findings plus the vacuous-verification tightening.
- Issues: None known. Pending QA round 2.

### 2026-08-03T15:29:52Z — plan_qa_round2
- Action: Independent focused QA round 2 of the revised plan v1 by a second fresh subagent. Verdict: CHANGES REQUIRED — 0 Critical, 2 High.
- Paths touched: plans/_eval_rtd_ws/qa/plan_qa.v2.md
- Evidence/decision: Reviewer re-verified all factual claims and applied step 2.2's begin_unit plus all six step-3 tests to a scratch copy at /tmp/rtqa2 (six pass patched, five error AttributeError unmodified, confirming 47+6=53). Round-1 findings 1 and 3 confirmed remediated; round-1 finding 2 only partially — the destruction risk is closed but the unsatisfiability recurred in a new form. New High 1: runtime/retry.py and tests/runtime/test_retry.py are already staged additions ('A ') in the baseline git status --porcelain, so verification step 1 fails at baseline and editing them yields 'AM', a status change the plan itself defines as disturbed work rather than an addition. New High 2: verification step 4(b) requires all step-3 tests to error with AttributeError pre-change, but test 3.6 never calls begin_unit and passes by design, making step 4 unpassable and its mandated result-file record false. I independently confirmed finding 1 by running git status --porcelain on both paths.
- Issues: 2 High open after the second and final permitted QA round.

### 2026-08-03T15:30:02Z — pipeline_controller
- Action: STOPPED the pipeline at Step 4 per SKILL.md's bound of at most two QA passes. Steps 5-7 (execution test plan, implementation prompt, final audit) were NOT performed and their artifacts do not exist. This package is incomplete by design, not by omission.
- Paths touched: none
- Evidence/decision: SKILL.md Step 4: 'Allow at most two QA passes. If the plan still isn't clean after two rounds, stop the whole pipeline here, report the outstanding findings to the user, and do not proceed to Steps 5-7 — a test plan and prompt built on a plan with open Critical/High findings inherit those defects.' Two rounds were run by two separate fresh subagents; round 2 returned CHANGES REQUIRED — 0 Critical, 2 High. Both open findings are verification-layer defects in the plan, not defects in the proposed fix, which both reviewers independently confirmed correct on scratch copies.
- Issues: 2 High open, both documented in plans/_eval_rtd_ws/qa/plan_qa.v2.md with minimal remediations: (1) rewrite the step 0.4 snapshot expectation and verification steps 1 and 6 in terms of the porcelain code transition 'A ' -> 'AM' for the two target files, which are already staged additions; (2) scope verification step 4(b) to tests 3.1-3.5 only, since 3.6 never calls begin_unit and passes against the unmodified source by design. A third repository gate, FR-P3-CAPS-OWNED, went red after the plan was authored and is out of scope. Resuming this package means applying those two remediations and re-entering at Step 3.

### 2026-08-03T15:57:27Z — plan_author
- Action: Revised plan v1 in place against QA round 2, after SKILL.md Step 4 was corrected to allow continuing past two rounds while the Critical+High count strictly decreases (ceiling five). Round 1 had 3 High, round 2 had 2 High — a strict decrease — so this package is entitled to a round 3. Finding 1: step 0.4 now states verbatim that runtime/retry.py and tests/runtime/test_retry.py are already staged additions ('A ') in the baseline snapshot and that the permitted delta is the 'A ' -> 'AM' transition on exactly those two paths; verification step 1's pass condition is now 'both appear as A ' with failure defined as either already carrying a worktree modification; verification step 6 and the matching acceptance criterion now assert the 'A ' -> 'AM' transition instead of 'addition of two paths'. Finding 2: verification step 4(b) is scoped to tests 3.1-3.5 and states explicitly that test 3.6 passes against the unmodified source by design, expecting five errors and one pass; the result-file mandate now records that shape instead of a blanket AttributeError claim.
- Paths touched: plans/_eval_rtd_ws/_eval_rtd_ws.plan.v1.md
- Evidence/decision: Independently re-confirmed finding 1 by running 'git status --porcelain -- runtime/retry.py tests/runtime/test_retry.py', which returns exactly 'A  runtime/retry.py' and 'A  tests/runtime/test_retry.py'. Finding 2 follows from the plan's own text: step 3.6 specifies a test that never calls begin_unit, so it cannot raise AttributeError, which the round-2 reviewer also confirmed empirically at /tmp/rtqa2. Revised in place per Step 4, no version bump, no scope expansion beyond the two findings.
- Issues: None known. Pending QA round 3.

### 2026-08-03T16:05:45Z — plan_qa_round3
- Action: Independent focused QA round 3 of the revised plan v1 by a third fresh subagent with no prior context. Verdict: CHANGES REQUIRED — 0 Critical, 1 High. Round-over-round Critical+High count: 3, 2, 1 — strictly decreasing, so SKILL.md Step 4 permits continuing.
- Paths touched: plans/_eval_rtd_ws/qa/plan_qa.v3.md
- Evidence/decision: Reviewer executed rather than read: applied step 2.2 and tests 3.1-3.6 verbatim at /tmp/rtqa3 (five AttributeErrors plus 3.6 passing against unmodified source, all nine passing patched), reproduced cross-unit carryover for verification 4(a), and applied the change to a full repository copy at /tmp/rtqa3repo confirming Ran 53 tests OK, a porcelain diff of exactly two lines ('A ' -> 'AM' on the two target files), and byte-identical pre/post gate verdicts. Both round-2 findings confirmed remediated. New High: step 0.5 declared only FR-P0-NOSTALE and FR-P0-CLEAN red at baseline when phase 5 actually reports 30 PASS, 4 FAIL, 4 BLOCKED of 38 — FR-P2-DEFERRED and FR-P3-CAPS-OWNED also FAIL and four gates are BLOCKED — and that wrong list propagated into step 4.2, verification step 7 and the mandated result-file record, while the pass criterion covered PASS-to-FAIL only and ignored PASS-to-BLOCKED entirely. I independently reran ./tests/run_gates.sh 5 and confirmed the four FAIL and four BLOCKED gates exactly as reported.
- Issues: 1 High open at round 3, addressed in the next entry.

### 2026-08-03T16:05:56Z — plan_author
- Action: Revised plan v1 in place against QA round 3 finding 1 (gate baseline enumeration wrong and pass criterion blind to BLOCKED). Rewrote step 0.5 to make the verdicts it captures at implementation time the sole authority for every gate assertion, and demoted the in-plan enumeration to an explicitly informational 'observed while writing' block now listing all four FAIL (FR-P0-CLEAN, FR-P0-NOSTALE, FR-P2-DEFERRED, FR-P3-CAPS-OWNED) and all four BLOCKED (FR-P2-BOUND, FR-P2-SEL-MAPPED, FR-P4-CHECK-MAPPING, FR-P4-AGREEMENT) gates, with a note that gate state here drifts with untracked work and that a difference from the block is not a finding. Extended the pass criterion in step 4.2, verification step 7 and the acceptance criteria from 'no gate moved from PASS to FAIL' to 'no gate moved from PASS to FAIL or to BLOCKED', with the reason stated (a gate can be knocked out by a newly failing dependency without itself turning red), and widened the matching stop condition the same way. Changed the result-file mandate from naming two known-red gates to naming every gate the step-0.5 capture recorded as FAIL or BLOCKED. Also recorded, from the reviewer's non-blocking observation, that run_gates.sh exits non-zero whenever any gate is red, so verification step 7 is judged on the per-gate diff and never on exit status.
- Paths touched: plans/_eval_rtd_ws/_eval_rtd_ws.plan.v1.md
- Evidence/decision: Independently reran ./tests/run_gates.sh 5 against the untouched repository before editing: summary 'phase 5: 30 PASS, 4 FAIL, 4 BLOCKED, 0 SKIPPED of 38 registered', with the four FAIL and four BLOCKED gates exactly as the reviewer reported. Revised in place per Step 4, no version bump; scope limited to the one finding plus the exit-status clarification it directly implicates.
- Issues: None known. Pending QA round 4.

### 2026-08-03T16:11:05Z — plan_qa_round4
- Action: Independent focused QA round 4 of the revised plan v1 by a fourth fresh subagent with no prior context. Verdict: APPROVED — 0 Critical, 0 High. The QA loop converges and closes here: round-over-round Critical+High counts were 3, 2, 1, 0, strictly decreasing at every step and within SKILL.md Step 4's five-round ceiling. Steps 5-7 are now unblocked.
- Paths touched: plans/_eval_rtd_ws/qa/plan_qa.v4.md
- Evidence/decision: Reviewer verified by execution rather than reading: baseline 'Ran 47 tests' OK; no production RetryTracker call site (15 grep hits, 13 of them planning/eval material); all three policy/limits.v1.yaml quotes verbatim; porcelain code 'A ' on both target files and the six git diff paths as claimed; applied step 2.2 plus tests 3.1-3.6 verbatim at /tmp/rtqa4 producing exactly the predicted five AttributeErrors plus one pass against the unmodified source and 'Ran 9 tests' OK patched, confirming the 53 total; reproduced the 4(a) cross-unit carryover on the unmodified class; ./tests/run_gates.sh 5 returned the exact 30 PASS, 4 FAIL, 4 BLOCKED state the revised step 0.5 describes, with no PASS gate reading runtime/retry.py content; and porcelain is byte-identical across test and gate runs, so verification step 6's delta assertion is satisfiable.
- Issues: None. 0 Critical, 0 High.

### 2026-08-03T16:12:33Z — test_planner
- Action: Authored the execution test plan v1: fourteen ordered tests RTD-T00 through RTD-T13 covering, in sequence, the read-only baseline capture (tests, porcelain snapshot, complete per-gate verdicts), the two fail-fast preconditions from plan step 0, the scratch defect reproduction and the method-absence check, one test per implementation phase (step 2 code shape including a byte-for-byte diff of retry() and revision(), step 3 test authorship, the post-change 53-test suite), the behavioural acceptance checks, the no-begin_unit regression case, the porcelain delta, the gate diff, scope containment, and result-file completeness — closing with a final audit and pass rule.
- Paths touched: plans/_eval_rtd_ws/qa/execution_test.plan.v1.md
- Evidence/decision: Test ids and pass conditions derive directly from the QA-approved plan v1: RTD-T00 from steps 0.3-0.5, RTD-T01/T02 from the step 0.1/0.2 stop conditions, RTD-T03/T04 from verification step 4(a)/4(b) with 4(b) scoped to tests 3.1-3.5 plus 3.6 passing, RTD-T07 from verification step 5, RTD-T10 from the 'A ' -> 'AM' delta in verification step 6, RTD-T11 from verification step 7 including the PASS-to-BLOCKED regression rule, and RTD-T13 from the plan's result-file mandate. No Availability stages section: the plan has no external prerequisite, only internal fail-fast preconditions, so every test id can run now.
- Issues: None.

### 2026-08-03T16:13:15Z — prompt_author
- Action: Authored the GOAL/TEST/LOOP implementation prompt v1. GOAL cites plans/_eval_rtd_ws/_eval_rtd_ws.plan.v1.md by path, defers to it on any disagreement, states the two-file scope and the explicit non-goals, front-loads the step-0 fail-fast checks and the never-run-git-checkout/restore/stash/reset/clean constraint. TEST enumerates RTD-T00 through RTD-T13 in the same order as the execution test plan, citing plans/_eval_rtd_ws/qa/execution_test.plan.v1.md by path, one line each on what the test proves. LOOP states the repair-and-rerun discipline with explicit downstream-invalidation rules, warns against the two failure modes the plan forecloses (loosening revision() to satisfy a mis-specified test, and misattributing a pre-existing red gate), restates all eight stop conditions, and names the exact result file and the append-only log.
- Paths touched: plans/_eval_rtd_ws/prompts/_eval_rtd_ws.prompt.v1.md
- Evidence/decision: TEST section ids and order were taken directly from the ordered tests in the execution test plan, RTD-T00 through RTD-T13 with no additions or omissions, which is what the Step 8 validator checks mechanically. Stop conditions were copied from the plan's own 'Stop conditions and result' section, with the gate condition widened to FAIL-or-BLOCKED to match the QA round 3 remediation.
- Issues: None.

### 2026-08-03T16:17:04Z — final_auditor
- Action: Independent final audit of the whole package by a fresh subagent with no prior context. Verdict: PASS — 0 Critical, 0 High remaining.
- Paths touched: plans/_eval_rtd_ws/qa/final_audit.v1.md
- Evidence/decision: Auditor confirmed all eleven stages have log entries with monotonic timestamps and that the log is genuinely append-only — the superseded pipeline_controller STOP entry was corrected by a later entry rather than edited away. All six Critical/High findings across rounds 1-3 (3, then 2, then 1; round 4 clean) were verified present in the plan's current text rather than taken on the log's word: the 3.1 threshold arithmetic, the porcelain-delta reframing, the step-0.5 gate baseline, the 'A ' -> 'AM' transition, 4(b) scoped to tests 3.1-3.5, and the full four-FAIL/four-BLOCKED enumeration with the 'or to BLOCKED' criterion mirrored in all four required places. The prompt's TEST section lists RTD-T00 through RTD-T13 in the same ids and same order as the execution test plan with no orphans either way, and GOAL, plan scope and test-plan coverage agree on the two-file scope and the four non-goals. No application source was touched: runtime/retry.py and tests/runtime/test_retry.py remain 'A ' with an empty git diff and no begin_unit method. The auditor independently re-derived the package's facts (47 tests OK, no production call site, gates at 30 PASS / 4 FAIL / 4 BLOCKED).
- Issues: None. No remaining blocker. Disclosed by the auditor, not as a finding: .claude/skills/plan-create/SKILL.md was corrected mid-run to permit continuing past two QA rounds while the Critical+High count strictly decreases, which is what authorized rounds 3 and 4; the log records this and the current skill text supports it.

### 2026-08-03T16:17:18Z — package_validator
- Action: Ran the mechanical package validator, Step 8. Output: 'OK — plans/_eval_rtd_ws v1 package is structurally valid', exit 0. The package is complete: plan, four QA rounds, execution test plan, prompt, final audit, and this log.
- Paths touched: none
- Evidence/decision: python3 .claude/skills/plan-create/scripts/validate_plan_package.py plans/_eval_rtd_ws — confirms all six artifacts exist at the latest version, required sections are present in each, both verdict lines are well-formed, the APPROVED and PASS verdicts genuinely carry 0 Critical and 0 High, and every RTD test id in the prompt's TEST section has a matching entry in the execution test plan with no orphans on either side.
- Issues: None. The package is ready to hand off. Running plans/_eval_rtd_ws/prompts/_eval_rtd_ws.prompt.v1.md is a separate, later action that this planning work does not authorize.
