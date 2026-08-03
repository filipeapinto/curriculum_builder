# Meta-Prompt Active Version Staleness Check Planning Log

Append-only record for the planning, QA, test-planning, and implementation-prompt
workflow. Existing entries must not be edited or removed; later corrections are
new entries.

## Objective

runtime/controller.py resolves the active meta-prompt as a bare path literal (meta_prompt/curriculum.prompt.v1.md) that is never checked for existence and is duplicated independently in tests/meta_prompt_source.py. Add a check that proves the version the controller actually resolves exists on disk and is the same file tests/check_meta_prompt.py checks, so the contract cannot silently go stale relative to the runtime that hands it over.

## Entry template

```text
### <UTC timestamp> — <agent/task>
- Action: <work performed>
- Paths touched: <paths, or none>
- Evidence/decision: <verification or decision rationale>
- Issues: <critical/high findings, blockers, or none>
```

## Entries

### 2026-08-03T15:19:57Z — plan_author
- Action: Inspected runtime/controller.py, runtime/session_bridge.py, tests/check_meta_prompt.py, tests/meta_prompt_source.py, policy/checks.v1.yaml and the gate tree; authored implementation plan v1 adding a controller fail-fast plus a seventh 'resolution' part to the contract checker.
- Paths touched: plans/_eval_mps_ws/_eval_mps_ws.plan.v1.md, plans/_eval_mps_ws/plans.log.md
- Evidence/decision: controller.py:29 and meta_prompt_source.py:37 hold independent copies of the version literal with no existence check; session_bridge.py:91 copies runtime.prompt only after OUTPUT_ROOT is created and gate_0_logger.json is written, so staleness surfaces after mutation. fr_p5_engine.py:25 already declares meta_prompt_source the sole owner of the version, which the controller breaks. Six controller PRECONDITION ids are already absent from policy/checks.v1.yaml and no gate greps for them, so a new id needs no policy edit.
- Issues: None pending critical/high QA.

### 2026-08-03T15:28:53Z — plan_author
- Action: Revised plan v1 in place for both High findings from plan_qa.v1.md. Finding 1: added step 3a deriving SECTION_BANNER from source.PROMPT.name, and corrected Architectural end state items 1-2 to name tests/check_meta_prompt.py:373 as the second file holding a version literal. Finding 2: replaced the sys.path bullet with an explicit ordering requirement plus the reason, and added verification step 2 asserting runtime.controller.__file__.
- Paths touched: plans/_eval_mps_ws/_eval_mps_ws.plan.v1.md, plans/_eval_mps_ws/plans.log.md
- Evidence/decision: QA proved the third literal is regex-escaped at tests/check_meta_prompt.py:373 so plain greps missed it, and reproduced ModuleNotFoundError when tests/ precedes the repo root on sys.path because tests/runtime/ is an importable package named runtime. Also tightened end-state item 3 to the two paths that call resolve_companions (simulate() never does) and added FR-P0-NOSTALE to the expected pre-existing gate failures, per the two non-blocking observations.
- Issues: Two High findings remediated without scope expansion; no edit to policy/ or to the meta prompt. Pending second QA pass.

### 2026-08-03T15:36:46Z — plan_qa
- Action: Completed round-1 focused Critical/High QA of plan v1 against the repository.
- Paths touched: plans/_eval_mps_ws/qa/plan_qa.v1.md
- Evidence/decision: Verified line numbers, the pre-mutation ordering of resolve_companions() on both paths, the PRECONDITION-ASSETS-RESOLVE policy entry, the six unregistered failure ids, and that no gate enumerates PRECONDITION- ids or pins check_meta_prompt.py's shape.
- Issues: CHANGES REQUIRED — 0 Critical, 2 High: a third regex-escaped version literal at tests/check_meta_prompt.py:373, and sys.path shadowing of runtime by the tests/runtime package.

### 2026-08-03T15:36:46Z — plan_qa
- Action: Completed round-2 focused QA with a fresh reviewer, including verification that both round-1 High findings were genuinely remediated rather than merely acknowledged.
- Paths touched: plans/_eval_mps_ws/qa/plan_qa.v2.md
- Evidence/decision: Both prior High findings confirmed fixed by experiment: the derived SECTION_BANNER pattern is byte-identical to the current one, and the prescribed sys.path order resolves runtime.controller to the engine module while the reverse order raises ModuleNotFoundError. One new High found: step 0 captures no gate baseline record while verification step 7 diffs against one.
- Issues: CHANGES REQUIRED — 0 Critical, 1 High. Verification step 7 is unexecutable as written and the plan's named pre-existing gate failures are six gates out of date; two gates scan untracked files and move without any repository edit.

### 2026-08-03T15:36:46Z — plan_author
- Action: STOPPED the pipeline after the second QA pass without authoring the execution test plan, implementation prompt, or final audit.
- Paths touched: none
- Evidence/decision: SKILL.md step 4 allows at most two QA passes and directs that if the plan is not clean after two rounds the pipeline stops before steps 5-7, because a test plan and prompt built on a plan with open Critical/High findings inherit those defects. Round 2 returned CHANGES REQUIRED with 1 High. Revising a third time and proceeding would make the fix self-approved, which is the exact failure mode the independent-QA structure exists to prevent.
- Issues: OPEN High from plan_qa.v2.md finding 1: no gate baseline is captured in step 0, so verification step 7 and the related acceptance criterion and stop condition are unexecutable. Remediation is known and narrow (add a pre-edit gate-runner capture to step 0 and rewrite step 7 to diff against it) but requires a third QA pass the skill does not authorize.

### 2026-08-03T15:57:34Z — plan_author
- Action: Resumed the pipeline under the corrected SKILL.md step 4 (continue while Critical+High strictly decreases, ceiling 5 rounds; round 1 = 2 High, round 2 = 1 High is a strict decrease). Revised plan v1 in place for plan_qa.v2 High finding 1.
- Paths touched: plans/_eval_mps_ws/_eval_mps_ws.plan.v1.md, plans/_eval_mps_ws/plans.log.md
- Evidence/decision: Step 0 gained a fourth capture running tests/gates/runner.py 5 before any edit and recording the emitted gate_results.p5.<ts>.json path plus its per-gate status map as THE baseline record, with an explicit note that no on-disk record is authoritative because tests/results/*.json is gitignored. Verification step 7 now diffs against that captured path, drops the fixed FR-P0-CLEAN/FR-P0-NOSTALE expected-failure list in favour of 'every gate the step-0 capture records as FAIL or BLOCKED is pre-existing', names FR-P2-DEFERRED and FR-P3-CAPS-OWNED as gates that move on untracked files via common.py:75 production_files(), and adds a re-check before calling a move a regression. The stop condition and the gate acceptance criterion were aligned to the same captured record. Two non-blocking wording observations also tightened: the SECTION_BANNER acceptance criterion now excludes the inert comment at check_meta_prompt.py:451, and end-state item 1 now says 'silently' and explains why the fifteen policy/ owner copies are out of scope.
- Issues: One High remediated without scope expansion; no edit to runtime/, tests/ or policy/. Pending round-3 QA.

### 2026-08-03T16:06:28Z — plan_qa
- Action: Completed round-3 focused QA with a fresh independent reviewer that implemented the plan end-to-end on two scratch copies (/tmp/mpsqa/base pristine, /tmp/mpsqa/repo modified) rather than reading it.
- Paths touched: plans/_eval_mps_ws/qa/plan_qa.v3.md
- Evidence/decision: The implemented change reached 7/7 from two working directories, 6/7 under the step-4 deliberate break, 'Ran 49 tests ... OK', a matching preflight sha256, and byte-identical phase-4 and phase-5 gate status maps against the pristine copy with zero gates moved. All three prior High findings were re-checked by experiment: the derived SECTION_BANNER and the step-0 gate baseline are genuinely fixed; the sys.path shadowing is fixed in diagnosis but its prescribed insertion point is itself defective.
- Issues: CHANGES REQUIRED — 0 Critical, 2 High. (1) Step 3 prescribes inserting str(REPO) at line 78 of tests/check_meta_prompt.py, but REPO is not bound until line 81; run verbatim this raises a module-level NameError that kills the whole checker, a symptom the stop conditions' import-error guidance does not cover. (2) Verification step 6 diffs the preflight dict against 'the step-0 baseline' but step 0's four enumerated captures contain no preflight capture — the same uncaptured-baseline defect class round 2 raised for step 7, in a step round 2 did not re-check.

### 2026-08-03T16:06:36Z — plan_author
- Action: STOPPED the pipeline after the third QA pass. Did not author the execution test plan, the implementation prompt, or the final audit.
- Paths touched: none
- Evidence/decision: SKILL.md step 4 continues the QA loop only while each round's Critical+High count is strictly lower than the previous round's, to a ceiling of five rounds, and directs an immediate stop short of the ceiling when a round's count does not decrease. Round-by-round count: round 1 = 2 (0C/2H), round 2 = 1 (0C/1H), round 3 = 2 (0C/2H). Round 3 did not decrease on round 2, so the loop stops at three rounds rather than continuing to five. The plan is not clean, so steps 5-7 are skipped: a test plan and prompt built on a plan with open High findings inherit those defects.
- Issues: Two OPEN High findings from plan_qa.v3.md. Finding 1: step 3's sys.path insertion point is line-ordered wrong — str(REPO) is prescribed for line 78 but REPO is not bound until line 81, producing a module-level NameError rather than the import error the stop conditions anticipate. Finding 2: verification step 6 diffs the preflight dict against a step-0 baseline that step 0 never captures. Both remediations are described as one-line plan edits, but applying them would make the third revision self-approved without an independent pass, which is the failure mode the independent-QA structure exists to prevent.
