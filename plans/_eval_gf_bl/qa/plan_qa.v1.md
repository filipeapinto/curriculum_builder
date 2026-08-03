# Gate Flakiness Plan v1 — Focused QA

Independent Critical/High review of `plans/_eval_gf_bl/gate_flakiness.plan.v1.md` as
first drafted, against the repository, the live gate run, and the harness's own stated
rules. Medium and Low observations are deliberately omitted.

## Verdict

**CHANGES REQUIRED — 1 Critical, 4 High.** The diagnosis is sound and unusually well
grounded: the author reproduced the runs before writing, and correctly concluded that the
harness is deterministic and the drift is ambient. The defect is in the remedy. As first
written the plan would narrow a normative scan set, cannot distinguish its own intended
verdict changes from regressions, proposes fixes for causes never observed to fire, and
sets an acceptance criterion that is unreachable and would pressure the implementer into
weakening the one gate that guards `APPROVED`.

## Findings

### 1. Critical — excluding by name silently disables detectors

**Evidence.** The first draft proposed adding `outputs/`, `.claude/`, and `.pytest_cache/`
to `PRODUCTION_EXCLUDED_TOP_LEVEL` (`tests/gates/common.py:55`). The comment immediately
above that frozenset (`common.py:53-56`) states the rule this violates verbatim: *"adding a
root here would narrow a normative scan set without declaring it, which is how a detector
stops seeing the file it exists to check."* The comment further identifies "a second
hand-maintained copy" as "the defect this plan keeps closing."

**Impact.** Four detectors take `production_files()` as their subject:
`FR-P2-SEL-MAPPED` (`fr_p2_selector.py:550`), `FR-P2-DEFERRED` (`fr_p2_selector.py:333`),
`FR-P2-NOVALUES` (`fr_p2_selector.py:234`), and `FR-P1-SCHEMA-RETENTION`
(`fr_p1_retention.py:165`). Narrowing their corpus makes every one of them quieter. The
result is a run that stops flaking because it stopped looking — the flake is "fixed" by
making the gates blind, and nothing in the harness would report that. This is strictly
worse than the reported symptom, because a flaky gate is visible and a blind gate is not.

**Minimal required remediation.** Derive the discriminator instead of listing it. Use git
tracking status, which the repository already treats as the authority for authored content
(`fr_p0_structure.py:278-292`). Declare the ambient category once, as data, distinct from
the rule-7 content category, and assert that every ambient member is already ignored or
generated so that a member becoming authored content fails loudly.

### 2. High — tracking status alone makes new authored files invisible

**Evidence.** The obvious form of the remediation for finding 1 — scan `git ls-files` —
excludes untracked files by construction. A source file that has been written but not yet
`git add`-ed is authored content under review.

**Impact.** The class of file most likely to contain a fresh defect is exactly the class the
fix would stop scanning. An author could add a `SEL-*` identifier or an `RT-<n>` reference
in a new file and no detector would see it until after it was committed — inverting the
purpose of the gates. This converts finding 1's fix into a subtler instance of finding 1.

**Minimal required remediation.** Resolve the scan set as
`tracked ∪ untracked-and-not-ignored`, via
`git ls-files -z --cached --others --exclude-standard`, minus the declared ambient set. An
untracked file that git would keep must stay in the scan set. Raise rather than fall back
to a filesystem walk if git fails, following `check_clean` (`fr_p0_structure.py:591-595`),
which already establishes that an empty result from a failed git is never a pass.

### 3. High — the plan cannot tell its own intended changes from regressions

**Evidence.** Steps 2, 3, and 4 all deliberately change what gates see, and therefore
deliberately change verdicts. The first draft's verification asked for "no new failures."
The live reproduction shows the run is already failing: phase 5 reports **35 PASS, 3 FAIL**,
with `FR-P0-CLEAN`, `FR-P0-NOSTALE`, and `FR-P3-CAPS-OWNED` failing, two of them on hits in
`.claude/` and `docs/research/**` that step 2 is specifically intended to remove.

**Impact.** Against a baseline that is already red, and with a change set designed to move
verdicts, "no new failures" is not a decidable criterion. An implementer cannot distinguish
"this gate went green because I stopped scanning agent scratch, as intended" from "this gate
went green because I broke it." Both look identical in the summary line.

**Minimal required remediation.** Freeze a baseline in step 0 as an explicit per-gate-id
record — status *and* detail line — captured with `FR_RESULTS_DIR` pointed outside the
repository, plus a pinned corpus fixture of scan-set paths and SHA-256s. Require every
individual gate whose verdict moves to be named and justified as an intended effect of a
specific step. Compare by gate id, never by aggregate count.

### 4. High — fixes are proposed for causes never demonstrated to fire

**Evidence.** The author's own reproduction found back-to-back runs byte-identical, and
phase-4/5 checks identical under seven `PYTHONHASHSEED` values. The first draft nonetheless
carried a flat list of repairs including lexicographic version resolution
(`fr_p5_verifier.py:62`), `errors[0]`-only reporting (`common.py:299-306`), the `[:5]`
error cap (`verify_domain.py:87-91`), and the duplicate merge implementations
(`common.py:438-453` versus `fr_p4_policy_schemas.py:177-182`).

**Impact.** These are real latent defects but none is the reported bug. Repairing them here
enlarges an unreviewed diff across `common.py` and four gate modules, and each edit is
itself a chance to move a verdict — in a task whose entire purpose is to stop verdicts from
moving unexpectedly. It also hides the actual fix inside unrelated churn.

**Minimal required remediation.** Add a hard rule that no cause is repaired until it has
been demonstrated to move a verdict, and land the diagnostic first so that demonstration is
possible: the result record does not currently capture what was scanned, so two differing
runs cannot be attributed even in principle. Move the undemonstrated items to an explicit
deferred section with file:line and a reason, and make "no deferred item was fixed
opportunistically" an acceptance criterion.

### 5. High — the acceptance criterion is unreachable and pressures the implementer

**Evidence.** The first draft required phases 4 and 5 to exit 0. `FR-P0-CLEAN`
(`fr_p0_structure.py:589-603`) fails on any non-empty `git status --porcelain`, runs at
every phase (`registry.py:104-111`, `activation_phase: 0`), and owns the exit code
(`runner.py:175`). The worktree is dirty now with 30+ entries of unrelated user work, and it
will necessarily be dirty with the implementer's own uncommitted edits throughout the task.

**Impact.** The criterion can never be met while the task is in progress. The only ways to
reach exit 0 are to weaken `FR-P0-CLEAN`, to move it to a later activation phase, or to
commit user work that this task must not touch. All three are worse than the bug, and the
first two damage the gate the harness relies on to guard `APPROVED`.

**Minimal required remediation.** Drop exit 0 as a criterion and replace it with per-gate
comparison against the frozen baseline. State explicitly that `FR-P0-CLEAN` failing on the
task's own uncommitted edits is correct behavior and is not to be repaired. Add "do not
weaken an assertion, add a waiver, or move a gate to a later activation phase" to the stop
conditions. Separately, constraining `FR-P0-CLEAN`'s subject to the step-2 scan set is a
legitimate narrowing of *which paths dirty it*, and is distinct from weakening *what it
asserts* about those paths.
