# Gate Flakiness Planning Workflow — Final QA Audit v1

Standing audit of the corrected plan, the focused QA, the execution test plan, the
implementation prompt, the shared log, and workflow scope.

## Verdict

**PASS — 0 Critical, 0 High remaining.** The package is internally aligned, the one
Critical and four High findings are materially remediated, and the plan is grounded in a
reproduction performed before it was written rather than in inference from reading code.

## Evidence

- **Diagnosis is empirical, not assumed.** The reproduction ran phase 4 and phase 5 twice
  each with `FR_RESULTS_DIR` redirected outside the repository and found output
  byte-identical apart from the results filename, plus identical phase-4/5 output across
  seven `PYTHONHASHSEED` values. This falsified the intuitive "the harness is nondeterministic"
  hypothesis and redirected the plan to ambient state drift. The plan states the falsified
  hypothesis explicitly rather than quietly dropping it, and `GF-T00` re-runs the twin-run
  check so a future implementer discovers it if the conclusion ever stops holding.

- **Critical remediated.** The first draft added `outputs/`, `.claude/`, and
  `.pytest_cache/` to `PRODUCTION_EXCLUDED_TOP_LEVEL` (`common.py:55`), directly against the
  binding rule at `common.py:53-56`. The corrected plan derives the scan set from git
  tracking status instead of extending a hand-maintained name list, declares the ambient
  category separately from the content category, and asserts ambient members are already
  ignored or generated. `GF-T03` tests removals against the frozen corpus and fails any
  removal outside the declared ambient set.

- **Four High remediated.** (2) The scan set is `tracked ∪ untracked-not-ignored`, and
  `GF-T03`'s "must be included" direction tests the newly authored untracked file
  specifically. (3) `GF-T00` freezes a per-gate-id baseline with detail lines and a corpus
  fixture, and `GF-T07` requires a justification table mapping each changed verdict to the
  step that intended it. (4) The plan carries a hard "no cause is repaired until
  demonstrated" rule, `GF-T01` is the demonstration, and six undemonstrated defects are
  listed with file:line in step 6 and audited as untouched by `GF-T08`. (5) Exit 0 is
  removed as a criterion in the plan, the test plan, and the prompt; all three state that
  `FR-P0-CLEAN` failing on the task's own uncommitted edits is correct.

- **The remedy cannot silently disable a detector.** This is the failure mode most likely to
  make the symptom disappear while making the harness worse, and it is now closed at three
  independent points: the design principle in the plan, the bidirectional `GF-T03`, and the
  prompt's standing rule that the reviewed corpus may not shrink except by declared ambient
  membership. The prompt additionally forbids "excluding the path that triggered it" as a
  response to a failing gate.

- **Ordering is load-bearing and enforced.** The diagnostic lands before any fix, because
  the result record does not currently capture what was scanned and two differing runs
  therefore cannot be attributed even in principle. `GF-T02` requires the diagnostic to be
  observation-only and requires the new self-test to be *seen to fail* on a deliberately
  time-dependent gate, so it is not accepted on the strength of never having failed.

- **Scope is bounded and audited.** The implementation-allowed set is `tests/gates/**` and
  `tests/run_gates.sh`. `GF-T08` audits the six deferred file:line targets as untouched;
  `GF-T09` audits worktree integrity; every gate invocation redirects `FR_RESULTS_DIR`
  outside the repository, so `tests/results/` — 274 accumulated files, never truncated
  (`runner.py:78-86`) — gains nothing.

- **User work is protected throughout.** The worktree carries 30+ entries of unrelated
  in-flight changes. No artifact stages, stashes, resets, restores, or cleans; `GF-T09`
  requires byte-identical index objects and untracked bytes; a collision is a stop
  condition in the plan and in the prompt's LOOP.

- **Prompt alignment.** GOAL restates the ambient-drift diagnosis, the six ordered steps,
  and the two overriding rules. TEST covers GF-T00 through GF-T09 in order with the same
  stop and pass semantics. LOOP re-runs the determinism self-test after every repair and
  enumerates the specific evasions — weakening an assertion, adding a waiver, moving an
  activation phase, excluding the triggering path, committing user work — that would make
  the symptom vanish without fixing the defect.

- **Honest residual.** The plan does not claim the six deferred defects are harmless. It
  states each with file:line and a reason it is latent rather than live, so the next task
  inherits them as known work rather than rediscovering them.

## Remaining blocker

None. Implementation may proceed under the prompt. The first gate is `GF-T00`; if its twin
runs are not identical, the diagnosis is incomplete and the plan must be revised before any
edit — that branch is specified rather than left to the implementer.
