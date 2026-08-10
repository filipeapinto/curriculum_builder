# RetryTracker Per-Unit State Reset Plan v1 — Focused QA (Round 4)

## Verdict

**APPROVED — 0 Critical, 0 High.**

Every factual claim the plan makes about this repository checks out against the actual
files, and every predicted observable was reproduced rather than reasoned about. I read
`/Users/filipepinto/Projects/curriculum_builder/runtime/retry.py` and
`/Users/filipepinto/Projects/curriculum_builder/tests/runtime/test_retry.py` in full and
confirmed the described baseline (`self.used`, `self.revisions`, `self.failures` assigned
only in `__init__`, never cleared; three existing tests; no `begin_unit`). I ran
`python3 -m unittest discover -s tests/runtime -t .` and got `Ran 47 tests` / `OK`. A
repo-wide `RetryTracker` grep (excluding `.git/`, `node_modules/`, `__pycache__/`) returns
15 files: `runtime/retry.py`, `tests/runtime/test_retry.py`, and 13 planning/eval documents
(`plans/_eval_rtd_bl/*`, `plans/_eval_rtd_ws/*`, `.claude/skills/plan-create/evals/evals.json`,
`.claude/skills/plan-create-workspace/.../eval_metadata.json`) — no production
instantiation, exactly as step 0.2 asserts. The three quoted
`/Users/filipepinto/Projects/curriculum_builder/policy/limits.v1.yaml` entries are verbatim
correct: `per_lab.max_model_calls` value 60 with rationale "12 reviews + ~20 authoring calls
+ bounded retries, with headroom" (lines 17-20), `per_lab.max_revisions` value 3 with
rationale "a fourth attempt on the same failed-check set is the repeat-failure signal"
(lines 21-24), `convergence.repeat_failure_threshold` value 2 with rationale "the same
failed-check set twice without narrowing ends the loop" (lines 49-52). `git status
--porcelain` carries `A  runtime/retry.py` and `A  tests/runtime/test_retry.py`, and
`git diff --name-only` lists exactly six paths including the five the plan names, with
`AM runtime/run_curriculum.py` and `AM runtime/session_bridge.py` present as described.

I did not stop at reading. I copied `runtime/retry.py` and `tests/runtime/test_retry.py` to
`/tmp/rtqa4/`, wrote tests 3.1–3.6 exactly as step 3 specifies, and ran them both ways.
Against the **unmodified** source: `Ran 9 tests ... FAILED (errors=5)` — five
`AttributeError: 'RetryTracker' object has no attribute 'begin_unit'` from tests 3.1–3.5 and
test 3.6 passing, precisely the "five errors and one pass" verification step 4(b) predicts.
I then applied the step-2.2 `begin_unit` verbatim (plus the 2.1 attribute and the 2.3
`{kind: 0 for kind in self.limits}` rebuild): `Ran 9 tests` / `OK`. Test 3.1's arithmetic is
right — after the reset, one non-narrowing resubmission succeeds (`failures[key] == 1 < 2`)
and the second raises (`>= 2`), and the default `revision_limit=3` does not fire first.
47 + 6 = 53 is correct, and no file outside `runtime/retry.py` imports `RetryTracker`, so
nothing else in the suite can move.

I reproduced verification step 4(a) against the unmodified class: one tracker,
`revision({"A","B"}, {"A","B"})` in unit 1 leaves `failures={('A','B'): 1}`, and unit 2's
*first* attempt raises `RetryLimit("repeated failure set did not narrow")`. The defect is
real and the plan's stop condition on this reproduction will not fire.

I ran `./tests/run_gates.sh 5` and got `30 PASS, 4 FAIL, 4 BLOCKED, 0 SKIPPED of 38
registered` with exactly the eight red gates the plan's orientation block names — the block
is accurate, and the plan correctly demotes it to informational in favour of the step-0.5
capture. I then checked whether this change can move a PASS gate: `FR-P5-ENGINE-GENERIC`'s
`ENGINE_ROOTS` is `("policy", "schemas")` (`tests/gates/fr_p5_engine.py:51`), `FR-P2-NOVALUES`
scans the meta prompt against routing-manifest terms, and `FR-P0-PLANREF` globs only
`folder_refactoring.*.v*.md`. Nothing reads `runtime/retry.py` for content. I also confirmed
`git status --porcelain` is byte-identical before and after a full gate run and a full test
run, so verification step 6's "no path may be added" is satisfiable: `tests/results/*.json`
and `__pycache__/` are gitignored, and `plans/_eval_rtd_ws/` appears as a single collapsed
`?? ` entry, so the step-4.3 result file and log append add no porcelain line.

## Findings

None. No Critical or High findings.

## Observations (non-blocking)

- `begin_unit` ships as dead code: no `runtime/` module constructs a `RetryTracker`
  (verified by the 15-file grep above). The plan discloses this in its scope section and
  step 0.2 stops if a call site appears, so it is recorded here only.
- The `retry:` limits in `policy/limits.v1.yaml` (lines 65-73) sit at top level, not under
  `per_lab`, the same structural situation step 1.3 flags for `repeat_failure_threshold`.
  The plan resolves `self.used` to per-unit on the strength of the `max_model_calls`
  rationale ("bounded retries") without flagging it as a second assumption. Resetting
  per-unit is defensible — the rationale "one retry distinguishes a blip from a defect" is
  clearly per-occurrence, not per-run — so this is a completeness note on step 1.3, not a
  correctness problem.
- The baseline `python3 -m unittest discover -s tests/runtime -t .` prints an argparse usage
  error to stderr (`unrecognized arguments: --max-run-seconds 1`) from a subprocess-based
  test in the untracked `tests/runtime/test_run_curriculum.py`, while still reporting
  `Ran 47 tests` / `OK`. An implementer should not misread that noise as a red baseline and
  trip the step-0.3 stop condition.
- Part of the 47-test baseline comes from `tests/runtime/test_run_curriculum.py`, which is
  untracked user work. If it changes between step 0.3 and verification step 5, the
  hard-coded `Ran 53 tests` will not match even though the change is correct. Judging step 5
  as "step-0.3 count + 6" would be more robust than the literal 53, though 53 is correct
  as of this review.
- `.DS_Store` is untracked at the repository root and under `docs/`. macOS Finder activity
  can add or remove such entries independently of this work, which is the one plausible way
  verification step 6's strict "no other entry may appear" could trip on something the plan
  did not cause.
