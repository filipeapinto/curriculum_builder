# RetryTracker Per-Unit State Reset Plan v1 — Focused QA (Round 3)

## Verdict

**CHANGES REQUIRED — 0 Critical, 1 High.**

I executed the plan rather than reading it. Every source claim checks out: `runtime/retry.py`
matches the described baseline exactly (`self.used`, `self.revisions`, `self.failures` set only
in `__init__`, never cleared, no unit-boundary method); `tests/runtime/test_retry.py` holds
exactly the three named tests; the three quoted `policy/limits.v1.yaml` entries and their
rationales are verbatim correct; `python3 -m unittest discover -s tests/runtime -t .` reports
`Ran 47 tests` / `OK`; a repo-wide `RetryTracker` search finds only `runtime/retry.py`,
`tests/runtime/test_retry.py` and planning material — the production repeat-failure path is
`runtime/controller.py:183-202`, which keeps its own local `failures_seen` and never imports
`RetryTracker`; `git status --porcelain` carries `A  runtime/retry.py` and
`A  tests/runtime/test_retry.py`, and `git diff --name-only` lists exactly the six paths the
plan describes.

I then reproduced the whole sequence outside the repository. In `/tmp/rtqa3` I applied step 2.2
verbatim and wrote tests 3.1–3.6 exactly as specified: against the unmodified source the suite
gives `Ran 9 tests ... FAILED (errors=5)` — five `AttributeError: 'RetryTracker' object has no
attribute 'begin_unit'` plus test 3.6 passing, precisely the shape verification step 4(b)
predicts — and the 4(a) scratch reproduction shows unit 2's first `revision({"A","B"},
{"A","B"})` raising `RetryLimit("repeated failure set did not narrow")` off unit 1's inherited
`failures` entry. Against the patched source all nine pass. In a full copy of the repository at
`/tmp/rtqa3repo` (`cp -a`, including `.git` and every untracked path) I applied the same change:
`Ran 53 tests` / `OK`, the porcelain diff against the real repository's baseline is exactly two
lines — `A ` → `AM` on `runtime/retry.py` and `tests/runtime/test_retry.py`, nothing added,
removed or otherwise changed — and `./tests/run_gates.sh 5` produces a byte-identical per-gate
verdict list before and after (`diff` exit 0). Verification steps 1–7 and the acceptance criteria
are therefore satisfiable as written, and step 3.1's threshold arithmetic is correct: it passes
against the fixed source. The result file and the log entry land inside the already-collapsed
`?? plans/_eval_rtd_ws/` untracked entry, so writing them adds no porcelain line either.

The one blocker is factual, and it is in the gate baseline the plan declares.

## Findings

### 1. High — The declared baseline gate state is wrong: four gates FAIL, not two, and four more are BLOCKED

**Evidence.** Step 0.5 states: "At the time of writing, `FR-P0-NOSTALE` (stale-path hits) and
`FR-P0-CLEAN` (dirty worktree) were already FAILing", and follows with "If any gate other than
those two is red at baseline, record it and report it" — a phrasing that treats those two as the
complete red set. I ran `./tests/run_gates.sh 5` against the untouched repository. The summary
line is `phase 5: 30 PASS, 4 FAIL, 4 BLOCKED, 0 SKIPPED of 38 registered`. The red set is:

```
FR-P0-CLEAN            FAIL
FR-P0-NOSTALE          FAIL
FR-P2-DEFERRED         FAIL   (9 ids, 9 mirrored, 9 dangling — RT-9/RT-11 unresolved in .claude/skills/…)
FR-P3-CAPS-OWNED       FAIL   (unowned-cap-copy in docs/research/…)
FR-P2-BOUND            BLOCKED (dependency FR-P2-DEFERRED failed)
FR-P2-SEL-MAPPED       BLOCKED (dependency FR-P2-DEFERRED failed)
FR-P4-CHECK-MAPPING    BLOCKED (dependency FR-P2-DEFERRED failed)
FR-P4-AGREEMENT        BLOCKED (dependency FR-P4-CHECK-MAPPING blocked)
```

The plan carries this same two-gate framing into step 4.2 ("`FR-P0-NOSTALE` and `FR-P0-CLEAN`
remaining red is the expected, already-recorded baseline state"), into verification step 7, and
— most consequentially — into the mandated result-file contents: "the post-change per-gate
verdicts diffed against the step-0.5 baseline (naming `FR-P0-NOSTALE` and `FR-P0-CLEAN` as
known-red at baseline)".

**Impact.** Two separate harms. (a) False record: an implementer who follows the result-file
instruction as written records a baseline whose known-red set is two gates when it is four, with
four further gates BLOCKED and unmentioned anywhere in the plan; the resulting artifact reads as
"phase 5 is otherwise green, and this change kept it that way", which is not the state of the
repository either before or after the change. (b) Misattribution risk: an implementer who trusts
the plan's enumeration rather than re-deriving it, then sees `FR-P2-DEFERRED` or
`FR-P3-CAPS-OWNED` FAIL after the change, has been primed to read those as regressions caused by
this work and to trigger the stop condition "A gate that was PASS at the step-0.5 baseline is
FAIL afterwards". I verified they are not regressions: the pre- and post-change verdict lists are
identical. Separately, the pass criterion at 4.2/step 7 is stated only as "no gate moved from
PASS to FAIL", which does not cover the four BLOCKED gates at all — a PASS → BLOCKED move would
pass every check in this plan.

**Minimal required remediation.** In step 0.5, replace the two-gate enumeration with the actual
baseline — four FAIL (`FR-P0-CLEAN`, `FR-P0-NOSTALE`, `FR-P2-DEFERRED`, `FR-P3-CAPS-OWNED`) and
four BLOCKED (`FR-P2-BOUND`, `FR-P2-SEL-MAPPED`, `FR-P4-CHECK-MAPPING`, `FR-P4-AGREEMENT`), all
pre-existing and all out of scope — and mirror that list in step 4.2, verification step 7 and the
result-file instruction, which should say "naming every gate red or blocked at baseline" rather
than naming two. Extend the pass criterion to "no gate moved from PASS to FAIL **or to
BLOCKED**". Alternatively, delete the enumerations entirely and make every gate statement a pure
delta against the verdicts captured at 0.5; do not leave a hard-coded list that no longer matches
the repository.

## Observations (non-blocking)

- Test 3.6 as specified is a line-for-line duplicate of the pre-existing `test_repeat_failure_limit`
  (same `repeat_threshold=2`, same three `revision` calls, same `assertRaises`), which the plan
  also requires to stay unmodified. It adds a test to the count and no coverage. Its role in
  verification 4(b) is correctly handled, so this is cosmetic.
- Step 3.1's parenthetical "exactly the shape the pre-existing `test_repeat_failure_limit` asserts
  for a fresh tracker" is a loose analogy: that test's first call (`revision({"A"}, {"A","B"})`)
  is narrowing and records nothing, so its shape is narrow-then-repeat-then-raise, not
  succeed-then-raise. The arithmetic the step actually prescribes is right and the test passes.
- Step 1.2 concludes `self.used` is per-unit state, but the `retry:` limits it derives from
  (`malformed_structured_output`, `transient_worker_source_or_image_failure`) sit at the top level
  of `policy/limits.v1.yaml`, not under `per_lab` — the same structural gap step 1.3 honestly
  flags for `convergence.repeat_failure_threshold`. The conclusion is the sane one; only the
  ambiguity disclosure is one entry short.
- `begin_unit` ships as dead code. `runtime/controller.py:183` maintains its own
  `failures_seen: dict[tuple[str, ...], int]` local to `simulate()` and raises
  `RuntimeFailure("REPEAT-FAILURE", …)` from `limit_policy` directly; nothing constructs
  `RetryTracker`. The plan discloses this and step 0.2 stops if a call site appears, so it is
  recorded here only — but no production behaviour changes as a result of this work.
- `./tests/run_gates.sh 5` exits non-zero (1) at baseline because gates are red. No step in the
  plan depends on its exit status, so this is informational.
