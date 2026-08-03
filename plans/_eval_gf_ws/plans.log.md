# Gate Rerun Flakiness (Phases 4-5) Planning Log

Append-only record for the planning, QA, test-planning, and implementation-prompt
workflow. Existing entries must not be edited or removed; later corrections are
new entries.

## Objective

Identify and eliminate the causes of gate verdicts that change between reruns of ./tests/run_gates.sh at phases 4 and 5 with no intervening code change, so that a gate verdict is a function of committed repository state alone and every remaining FAIL is a real defect rather than an artifact of machine state, run history, or concurrent execution.

## Entry template

```text
### <UTC timestamp> — <agent/task>
- Action: <work performed>
- Paths touched: <paths, or none>
- Evidence/decision: <verification or decision rationale>
- Issues: <critical/high findings, blockers, or none>
```

## Entries

### 2026-08-03T15:30:07Z — plan_author
- Action: Authored implementation plan v1: an investigation-and-fix plan for gate verdict flakiness across reruns at phases 4-5. Six phases: A build a read-only rerun differ, B retry+mark transient external I/O, C remove generated/untracked state from the verdict path, D stop phase-4/5 gates rewriting FR-P0-REGISTRY, E lock concurrent runs, F re-measure.
- Paths touched: plans/_eval_gf_ws/_eval_gf_ws.plan.v1.md
- Evidence/decision: Grounded in the real harness (tests/run_gates.sh, tests/gates/runner.py, common.py, selftest.py, fr_p4_policy_schemas.py, fr_p5_*.py, registry.py) and in 274 recorded runs under tests/results/. Measured: 88 runs contain an 'Operation timed out' external failure; FR-P0-CLEAN flips 85 times, FR-P0-REGISTRY 51, FR-P0-NOSTALE 46, FR-P2-DEFERRED and FR-P4-AGREEMENT 19 each. A PASS/FAIL pair 148ms apart on FR-P0-CLEAN is the direct proof of rerun nondeterminism. Root cause was derived from evidence, not assumed.
- Issues: None pending critical/high QA. Filesystem confirmed local APFS at 93% capacity, so the I/O timeouts are load/concurrency-driven rather than a network mount; prerequisite 0c stops the run if that does not hold on the implementer's machine.

### 2026-08-03T15:44:59Z — plan_qa_round_1
- Action: Independent focused QA of plan v1 by a fresh subagent with repository access. Verdict: CHANGES REQUIRED - 3 Critical, 4 High.
- Paths touched: plans/_eval_gf_ws/qa/plan_qa.v1.md
- Evidence/decision: Reviewer reproduced the plan's counts against tests/results/ (88 timeout runs, per-gate tallies, 51/46/85 flips, the 148ms pair, the untracked load-bearing fixture, every confirmed non-cause) and found the arithmetic sound but the causal attribution wrong in three places.
- Issues: C1 the cited RT-9 cascade record names policy/deferred.v1.yaml, a tracked file mid-edit, not outputs/. C2 extending PRODUCTION_EXCLUDED_TOP_LEVEL also narrows FR-P0-NOSTALE via fr_p0_structure.py:287 and would silence 3 real hits on committed .claude/ content. C3 Phase D's three target sites account for 0, 0 and 1 of 83 recorded drift events. H4 retry applied to common.py:121, which none of the recorded failures reach. H5 rule-7 statement of record pointers wrong. H6 silent except OSError swallow flakes toward PASS, unaddressed. H7 a .json lockfile name would break self-tests (c) and (e) inside the root gate.

### 2026-08-03T15:44:59Z — plan_author
- Action: Revised plan v1 in place against all seven QA findings, without expanding scope.
- Paths touched: plans/_eval_gf_ws/_eval_gf_ws.plan.v1.md
- Evidence/decision: Every finding independently re-verified before revising: fr_p0_structure.py:287 does use PRODUCTION_EXCLUDED_TOP_LEVEL; folder_refactoring.plan.v6.md:502-506 is the real rule-7 enumeration; common.py:291 is _deserialize's read; the 020605 record does read 'at policy/deferred.v1.yaml'; class_drift tallies confirmed as NOSTALE 50, GITKEEP 19, FR-P1-DOC 7, SCHEMA-RETENTION 2, with 53 of 62 drift runs containing a timeout. Two further facts found during re-verification and folded in: FR-P1-DOC no longer exists in registry.py, and FR-P1-SCHEMA-RETENTION's declaration was already corrected to tree+text at registry.py:125, so the content-caused drift QA pointed at is already resolved and the last drift-bearing run is 2026-08-02.
- Issues: F1 cascade reclassified as worktree-changed-mid-run; Phase A step 4 added to detect it. F2 exclusion approach replaced: production_files() is intersected with git ls-files, PRODUCTION_EXCLUDED_TOP_LEVEL left untouched, plus a mandatory before/after tracked-hit diff as invariant 3. F3 Phase D withdrawn in full and re-derived: aborted gates no longer feed the drift sweep. F4 retry extended to common.py:291 and selftest.py:117. F5 rule-7 pointer corrected, grep instruction dropped. F6 the three silent-swallow sites must re-raise after retry. F7 lockfile named tests/results/.run.lock with its own gitignore line. Observations 1-4 folded into invariants 1 and 2 and the Phase B tally. None pending round-2 QA.

### 2026-08-03T15:53:36Z — plan_qa_round_2
- Action: Second independent focused QA of the revised plan v1 by a fresh subagent. Verdict: CHANGES REQUIRED - 1 Critical, 2 High.
- Paths touched: plans/_eval_gf_ws/qa/plan_qa.v2.md
- Evidence/decision: Reviewer confirmed 6 of 7 round-1 findings fully remediated and 1 partially. It independently reproduced the re-derived Phase D in every particular: the class_drift tally, FR-P1-DOC absent from registry.py, FR-P1-SCHEMA-RETENTION declared tree+text at registry.py:125, the last drift-bearing run, and that 81 of 83 drift events belong to gates that terminated by raising - so the proposed aborted-skip targets the right population and conceals nothing. It also verified tests/results/.run.lock is safe against every glob over that directory, and read all 661 files returned by production_files() through read_named to confirm none raises today.
- Issues: C1 Phase C step 1's git ls-files intersection cannot be both retried and mechanism-neutral: through Evidence.run it stamps execution onto four gates whose claim_class lacks it, failing FR-P0-REGISTRY deterministically on every run, and Phase D step 3 forbids the only escape; around Evidence.run the Phase B retry does not apply and an unretried git call lands inside the root gate's self-test at selftest.py:241. H2 Phase B step 5's unconditional re-raise fires inside FR-P0-HARNESS self-test (f) at selftest.py:240-245, converting one transient read into a whole-run BLOCKED, and buys nothing there. H3 the silent-swallow census is 3 of 6 sites; fr_p1_retention.py:109, fr_p2_selector.py:555 and fr_p5_engine.py:183 are omitted and fr_p1_retention.py:109 is armed, so Phase F's 'no file silently dropped' criterion is unmeetable as written.

### 2026-08-03T15:53:36Z — plan_author
- Action: STOPPED the pipeline after two QA rounds without a clean verdict, per SKILL.md Step 4. Steps 5-7 (execution test plan, implementation prompt, final audit) were deliberately NOT produced.
- Paths touched: none
- Evidence/decision: SKILL.md Step 4: 'Allow at most two QA passes. If the plan still isn't clean after two rounds, stop the whole pipeline here, report the outstanding findings to the user, and do not proceed to Steps 5-7 - a test plan and prompt built on a plan with open Critical/High findings inherit those defects.' Round 1 returned 3 Critical / 4 High and round 2 returned 1 Critical / 2 High, so the bound is reached with findings open.
- Issues: Open and unremediated: C1 (Phase C git ls-files intersection unimplementable as written), H2 (Phase B re-raise blast radius through the root gate), H3 (incomplete silent-swallow census). All three are concentrated in the Phase B/C remediation mechanics; Phases A, D, E and the whole evidence base passed round 2. The package is deliberately incomplete: no execution test plan, no implementation prompt, no final audit. Implementation is not authorized.

### 2026-08-03T16:00:09Z — plan_author
- Action: Resumed the pipeline under the corrected SKILL.md Step 4 (continue while Critical+High strictly decreases, ceiling 5 rounds; round 1 = 7, round 2 = 3, so the run is entitled to continue). Revised plan v1 in place against all three round-2 findings, without expanding scope.
- Paths touched: plans/_eval_gf_ws/_eval_gf_ws.plan.v1.md
- Evidence/decision: Each finding independently re-verified before revising: production_files() at common.py:75 takes no Evidence and its five call sites (fr_p1_retention.py:165, fr_p2_selector.py:234,333,550, selftest.py:241) have none to pass; Evidence.run records execution unconditionally at common.py:275; selftest.py:238-245 does call production_files() and scan_for_stale with no Evidence; the three omitted swallow sites are real and reached from gate bodies (fr_p1_retention.py:109 via :165-166, fr_p2_selector.py:555 via :550, fr_p5_engine.py:183 via :256), all three using ev.text_of; git ls-files | grep -c '^"' = 0 confirms the quotePath hole is latent; production_files() returns 671 files today with 448 under outputs/ and 79 under .claude/ (12 tracked), confirming the .claude count is volatile.
- Issues: R2-1 remediated: the bounded retry is factored into a module-level _run_retryable in common.py that records no mechanism; production_files() calls it directly with -z and core.quotePath=false; Evidence.run keeps its single _record('execution'); failure after retries raises rather than falling back to an untracked walk; Phase C step 3 added to prove mechanisms_used and class_drift are unchanged. R2-2 remediated: an explicit strict parameter replaces the unconditional re-raise, strict=True from production gate bodies and strict=False (with a note naming the skipped path) from selftest.py:244 and every Fixture detector, with the root-gate caller stated in the plan and in the code comment. R2-3 remediated: the census is now the full six sites in a table, with fr_p3_calibration.py:145,376 recorded as excluded by evidence, and Phase F step 3(b) enumerates per site. Phase C steps renumbered 4-7 after the insertion. None pending round-3 QA.

### 2026-08-03T16:12:26Z — plan_qa_round_3
- Action: Third independent focused QA of the revised plan v1 by a fresh subagent with repository access and no sight of the prior rounds or the log. Verdict: CHANGES REQUIRED - 0 Critical, 3 High.
- Paths touched: plans/_eval_gf_ws/qa/plan_qa.v3.md
- Evidence/decision: Reviewer re-derived the whole corpus independently (88 timeout runs, the per-gate transient counts, 62 drift runs of which 53 carry a timeout, 85 FR-P0-CLEAN flips, 61 of 64 FR-P0-REGISTRY FAILs class-drift), confirmed every file:line citation including the full six-site swallow census plus the two evidence-excluded fr_p3_calibration sites, and applied the Phase C tracked-content scan-root change live in a scratch copy: production_files() 671 -> 110 paths, dangling_rt_references to 0, FR-P0-NOSTALE's 8 hits intact, no tracked-path hit lost. The round-2 Critical (retry vs mechanism neutrality) is confirmed resolved by the _run_retryable factoring.
- Issues: H1 the new strict=False 'append a note naming the skipped path' requirement has no note channel - all six exempt call sites pass no Evidence, and passing ev at selftest.py:244 makes FR-P0-HARNESS report execution+mapping+text against its declared execution+mapping, permanently failing FR-P0-REGISTRY through the drift sweep (verified by execution). H2 the Phase B retry allowlist (git ls-files, git status, git log, git rev-list) does not match the exact argv Phase C mandates (git -c core.quotePath=false ls-files -z), so the raising git call Phase C places inside root-gate self-test (f) would ship unretried, voiding the plan's own bound on that exposure. H3 invariant 2 is unmeetable as stated: check_caps rglobs its own CAP_SCAN_ROOTS = (meta_prompt, docs, policy) at fr_p3_calibration.py:52,410-414, which no phase of this plan touches, and FR-P3-CAPS-OWNED is failing right now on two untracked docs/research/** files, flipping PASS->FAIL across today's ten phase-5 runs.

### 2026-08-03T16:12:36Z — plan_author
- Action: STOPPED the pipeline after QA round 3 on the convergence rule, not the round ceiling. Steps 5-7 (execution test plan, implementation prompt, final audit) were deliberately NOT produced.
- Paths touched: none
- Evidence/decision: SKILL.md Step 4 continues a run only while each round's Critical+High count is strictly lower than the previous round's, to a ceiling of five rounds, and stops immediately short of the ceiling when a round's count does not decrease. Round-over-round: round 1 = 3 Critical + 4 High = 7; round 2 = 1 Critical + 2 High = 3 (strict decrease, which is why round 3 was entitled to run); round 3 = 0 Critical + 3 High = 3 (no decrease). 3 is not lower than 3, so the plateau condition fires at round 3 and the loop ends two rounds short of the ceiling. Note for the record that the severity composition did improve (the last Critical is gone, and the round-3 reviewer independently confirmed both round-2 mechanisms are resolved), but the rule keys on the Critical+High sum, and by that measure this revision did not converge.
- Issues: Open and unremediated: H1 (strict=False notes have no Evidence-free channel; the obvious fix permanently fails FR-P0-REGISTRY), H2 (retry allowlist does not cover the exact git argv Phase C mandates, leaving the root-gate git call unretried), H3 (invariant 2 unmeetable - FR-P3-CAPS-OWNED reads untracked docs/research/** through CAP_SCAN_ROOTS, a scan root no phase of this plan touches, and is flipping on it today). H1 and H2 are both consequences of the round-2 remediations themselves; H3 is a scope gap in invariant 2 that all three rounds missed until now. The package is deliberately incomplete: no execution test plan, no implementation prompt, no final audit, and no Step 8 validation. Implementation is not authorized.
