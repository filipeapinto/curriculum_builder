# GOAL

Implement `plans/_eval_gf_bl/gate_flakiness.plan.v1.md` exactly, using
`plans/_eval_gf_bl/qa/execution_test.plan.v1.md` as the acceptance procedure.

Eliminate the class of defect in which a phase 4 or phase 5 gate run returns a different
verdict than an immediately preceding run with no change to repository source.

Start from the plan's finding, which is already reproduced and must not be re-litigated:
**the harness is deterministic; the drift is ambient.** Gate order is fixed
(`runner.py:52-71`), there is no randomness, threading, or network call under
`tests/gates/`, and back-to-back runs are byte-identical. What moves between runs is the
*subject* several gates take: the git worktree, the git index, agent scratch under
`.claude/`, generated output under `outputs/`, build caches, and OS files. Live
enumeration puts 448 of 645 "production" scan files under `outputs/` and 53 under
`.claude/`. Fix the subject, not the scheduler.

The change is confined to `tests/gates/**` and `tests/run_gates.sh`. Work in this order and
do not reorder it:

1. **Freeze the baseline and corpus** before touching anything. Per-gate-id status and
   detail for phases 4, 5, and the full 0–5 sweep, with `FR_RESULTS_DIR` pointed outside
   the repository. Plus a pinned list of scan-set paths with SHA-256.
2. **Land the diagnostic first.** Extend the result record (`runner.py:155-166`) with
   `run_environment`; add `tests/gates/run_diff.py`; add a twin-run determinism self-test
   to `tests/gates/selftest.py`. Until this exists, a verdict change cannot be attributed
   to a cause, and no fix may be claimed to work.
3. **Separate ambient artifacts from repository content.** Resolve `production_files()`
   (`common.py:75-101`) as `(tracked ∪ untracked-and-not-ignored) − ambient`, from
   `git ls-files -z --cached --others --exclude-standard`. Declare the ambient set once as
   data, distinct from the rule-7 content set, and assert every member is already ignored
   or generated. Raise if git fails; never fall back to a filesystem walk.
4. **Correct the two gates whose subject is the developer's machine.** Constrain
   `FR-P0-CLEAN` (`fr_p0_structure.py:589-603`) to paths in the new scan set. Route
   `FR-P0-NOSTALE` (`fr_p0_structure.py:278-292`) through it so the git **index** stops
   being an input.
5. **Remove the retroactive class-drift flip.** Make `fr_p5_verifier.py:151-153` record
   `execution` and `fr_p5_manifest.py:140-144` record `schema` on every path including the
   early return. Keep `_class_drift_sweep` (`runner.py:196-231`) intact — the defect is the
   conditional recording, not the sweep.
6. **Pin the environment.** One interpreter for `run_gates.sh:14-15` and `common.py:274-282`;
   explicit minimal `env=` for `ev.run`; `PYTHONHASHSEED=0` and `LC_ALL=C.UTF-8`; all four
   `FR_*` overrides recorded; `check_registry` takes the phase from `RUN_STATE` and fails
   explicitly rather than reading `FR_PHASE` (`fr_p0_structure.py:756`).

Two rules override any local judgment about what would be nice to fix:

**No cause is repaired until it has been demonstrated to move a verdict.** If GF-T01 cannot
make an injection change a gate, the corresponding step has no demonstrated cause and moves
to the deferred list.

**The reviewed corpus may not shrink except by declared ambient membership.** A fix that
stops a gate flaking by making it stop looking is worse than the bug. `common.py:53-56`
states this rule and it is binding. An untracked, non-ignored, newly authored source file
must still be scanned.

Do not touch the plan's step-6 deferred items: `fr_p5_verifier.py:62`, `common.py:299-306`,
`verify_domain.py:87-91`, `common.py:438-453`, `fr_p4_policy_schemas.py:177-182`,
`fr_p5_unit.py:206`. They are real, they are latent, and they are not this bug.

The worktree carries unrelated user work. Never stage, stash, reset, restore, or clean.
Never write into `tests/results/`; always redirect `FR_RESULTS_DIR` outside the repository.

# TEST

Run GF-T00 through GF-T09 from the execution test plan strictly in order, without skipping
ahead. Each test's evidence goes to `/private/tmp/gate-flakiness-test-<UTC>/`.

1. **GF-T00** — freeze baseline, twin runs per phase, full 0–5 sweep, corpus fixture,
   environment capture. If the twin runs differ, stop and report: the plan's diagnosis is
   incomplete and must be revised before any edit.
2. **GF-T01** — reproduce ambient drift in an external copy, one injection at a time:
   `RT-9` under `.claude/` must FAIL `FR-P2-DEFERRED` and BLOCK both phase-4 dependants;
   a `SEL-*` under `outputs/` must FAIL `FR-P2-SEL-MAPPED`; a `.DS_Store` must be read as
   text; `git add` must change `FR-P0-NOSTALE`'s subject.
3. **GF-T02** — diagnostic is observation-only (per-gate map equals GF-T00), `run_diff.py`
   attributes a transition to the injected file, and the determinism self-test is proven to
   fail on a deliberately time-dependent gate.
4. **GF-T03** — scan-set correctness in **both** directions. Ambient additions inert; and a
   tracked file, an untracked non-ignored new file, a file in a new directory, and an
   ambient-lookalike tracked file all still scanned and still caught. Every removal from the
   frozen corpus must be a declared ambient member. Git failure raises.
5. **GF-T04** — `FR-P0-CLEAN` ignores dirt outside the scan set, still FAILs on dirty
   tracked source, still raises when git fails, and did not move `activation_phase`.
   `FR-P0-NOSTALE` unchanged across all four index states.
6. **GF-T05** — the two phase-5 gates record their mechanisms on every path,
   `FR-P0-REGISTRY` no longer flips retroactively, and the sweep still fires on a genuine
   mismatch.
7. **GF-T06** — one interpreter; polluted `PYTHONPATH` reports an environment error rather
   than `verifier-fixture-accepted`; identical maps across four `PYTHONHASHSEED` and three
   `LC_ALL` values; all `FR_*` recorded; standalone `FR-P0-REGISTRY` fails explicitly on a
   wrong `FR_PHASE`.
8. **GF-T07** — full 0–5 sweep compared per gate id, with a table mapping every changed
   verdict to the plan step that intended it. Unexplained changes fail.
9. **GF-T08** — no deferred item touched, no path outside the allowed set changed, no
   assertion weakened, no waiver added, no `activation_phase` changed.
10. **GF-T09** — worktree byte-identical to GF-T00; `tests/results/` gained no files.

Exit code 0 is **not** an acceptance criterion and must not be pursued. `FR-P0-CLEAN` will
fail for as long as this task's own edits are uncommitted; that is correct. Compare by gate
id against the frozen baseline, never by aggregate count and never by exit code.

# LOOP

Execute each test in order. On failure, record the test id, command, exit code, evidence
hashes, and the narrow root cause; revise only the in-scope failed artifact; re-run the
GF-T02 determinism self-test immediately; then re-run the failed test and every later test
whose evidence may have changed. Continue until GF-T00 through GF-T09 all pass.

Do not waive, reorder, weaken, or replace a test.

Stop without claiming success on: a collision with pre-existing user work; a required repair
outside `tests/gates/**` and `tests/run_gates.sh`; a baseline `PASS` becoming `FAIL` that
cannot be explained as an intended effect; or the discovery that a proposed exclusion would
hide authored content.

Never respond to a failing gate by weakening its assertion, adding a waiver, moving it to a
later activation phase, excluding the path that triggered it, committing or discarding user
work, or fixing a deferred item to make a symptom go away. If a gate fails because it is
correctly reporting a real defect, say so and stop; that is not flakiness.

When implementation has proceeded, write
`plans/_eval_gf_bl/gate_flakiness.result.v1.md` with the frozen baseline, the GF-T01
demonstrated-cause list, the per-gate comparison table with justifications, the deferred
list carried forward untouched, remaining failures, and the final verdict. Append — never
rewrite — the outcome to `plans/_eval_gf_bl/plans.log.md`.

Claim completion only when every test has passed, every verdict change is justified, and
the reviewed corpus is provably no smaller than at GF-T00 except by declared ambient
membership.
