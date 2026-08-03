# Meta-Prompt Active Version Staleness Check — Implementation Plan v1

## Status and objective

Planning only; no implementation is authorized by this document's creation.

`runtime/controller.py:29` sets `self.prompt = self.engine / "meta_prompt/curriculum.prompt.v1.md"`.
That version literal is never checked for existence, and it is duplicated
independently at `tests/meta_prompt_source.py:37` (`PROMPT_REL`) and a third time,
regex-escaped, at `tests/check_meta_prompt.py:373` inside `SECTION_BANNER`. Nothing
in the repository asserts that any of the three agree or that any of them resolves.

This plan adds two narrow things: a fail-fast precondition in the controller so a
missing active meta-prompt stops a run before it mutates anything, and a seventh
part in `tests/check_meta_prompt.py` that asserts the path the controller
*actually resolves* is the same file the contract checker checks. It does not
redesign version resolution, does not introduce a policy manifest for the prompt
version, does not add an FR- gate, and does not change the contract's own text.

### Why this is a real defect and not a hypothetical

The consequence is not a clean error. `runtime/session_bridge.py:91` copies
`runtime.prompt` into the frozen input bundle. By the time that line runs,
`prepare()` has already passed `require_internal_output`, called `output.mkdir()`,
built the `ExecutionLogger`, run the logger gate, and written
`results/gate_0_logger.json` (`runtime/session_bridge.py:76-82`). A prompt whose
version has moved therefore fails *after* an OUTPUT_ROOT exists and holds
evidence — and `PRECONDITION-OUTPUT-ROOT-EXISTS` means that root can never be
reused, so the half-written run has to be removed by hand before a retry.

The divergence is reachable by an ordinary edit. `plans/contract_v2/prompt/contract_v2.prompt.v1.md`
instructs an implementer to create `meta_prompt/curriculum.prompt.v2.md` and update
`runtime/controller.py`, `tests/check_meta_prompt.py` and `tests/meta_prompt_source.py`
to resolve v2 — three separate files, no mechanism that notices if one is missed.
Update the test side alone and `tests/check_meta_prompt.py` reports
`meta prompt: EXECUTABLE (6/6 checks pass)` against v2 while the controller still
hands v1 — or nothing — to the run. That is the silent staleness this plan closes.

## Architectural end state

1. `tests/meta_prompt_source.py` remains the single declared owner of the meta-prompt
   version. `tests/gates/fr_p5_engine.py:25` already states that it holds "no version
   literal for the meta prompt" and defers to that module. **Two** files break that
   discipline *silently*, not one: `runtime/controller.py:29` and
   `tests/check_meta_prompt.py:373`, where the literal is regex-escaped inside
   `SECTION_BANNER` and so does not match a plain search for `curriculum.prompt.v`.
   This plan leaves neither in place unaddressed. The fourteen `owner:` copies in
   `policy/checks.v1.yaml` and the one in `policy/deferred.v1.yaml:140` are out of scope
   and deliberately so: `tests/gates/fr_p4_policy_schemas.py:131-146` fails any entry whose
   `owner` path does not exist, so those copies break loudly on a version bump — the
   opposite of the silent-staleness class this plan closes.
2. `runtime/` never imports from `tests/`. The controller keeps its own literal; the
   agreement between the controller's literal and the owner becomes a *checked* claim
   rather than a hoped-for one. The checker's own literal is not checked but
   **derived**, because it lives in the same file as the check and a check that
   validates its own copy of a value proves nothing.
3. On the two paths that resolve companions — `static_preflight()` and
   `session_bridge.prepare()` — the active meta-prompt is proved to resolve **before**
   an OUTPUT_ROOT is created, a log record is written, or a model is called.
   `simulate()` (line 161) is out of scope: it never reads `self.prompt` and never
   calls `resolve_companions()`, so it neither gains nor needs this guarantee.
4. The resolved prompt path and its hash appear in static preflight evidence, so a run
   records which contract version it actually resolved rather than leaving it implicit.

## Exact work

### 0. Baseline capture and worktree protection (fail-fast)

- The worktree is heavily dirty with pre-existing staged user work (`git status --short`
  currently lists dozens of staged additions unrelated to this plan, and
  `tests/results/gate_results.p5.20260803T133435.900879Z.json` records `FR-P0-CLEAN FAIL`
  citing exactly that dirt). Capture `git status --short` and `git stash list` before any
  edit and again at the end. Never stage, stash, reset, restore, clean, or commit.
- Capture the current output of `python3 tests/check_meta_prompt.py` verbatim, including
  its final `meta prompt: … (N/N checks pass)` line.
- Capture the current output of `python3 -m unittest discover -s tests/runtime -t .`.
- Capture the gate baseline **before any edit**: run `python3 tests/gates/runner.py 5`,
  record the path of the `tests/results/gate_results.p5.<ts>.json` it emits, and record
  that record's per-gate status map. This captured path is *the baseline record* referred
  to in verification step 7. No gate record in the repository is authoritative for this
  purpose — `tests/results/*.json` is gitignored (`.gitignore:4`), so every record on disk
  is a leftover from some earlier run, including
  `tests/results/gate_results.p5.20260803T133435.900879Z.json`, which is cited above only
  as evidence that `FR-P0-CLEAN` fails on pre-existing dirt and must not be used as the
  diff target.
- These four captures are the baseline. A gate or test already failing before the edit
  is not this plan's to fix and must not be counted as a regression; a *new or worsened*
  failure is a stop condition. Do not run `tests/run_gates.sh` expecting a clean result —
  `FR-P0-CLEAN` fails on the pre-existing dirt by design.

### 1. Add the controller-side fail-fast

- In `runtime/controller.py`, extend `resolve_companions()` (line 51) so it also proves
  `self.prompt.is_file()` before returning, raising
  `RuntimeFailure("PRECONDITION-PROMPT-MISSING", f"active meta prompt missing: {self.prompt}")`.
  Check the prompt **before** the companion loop, so the failure names the contract root
  rather than three assets that are beside the point when the contract itself is gone.
- `resolve_companions()` is the correct single insertion point: `static_preflight()`
  (line 139) calls it first, and `session_bridge.prepare()` calls it at line 69 — before
  `require_internal_output`, `output.mkdir()` and the logger gate. One edit covers both
  entry points at a position that already precedes every mutation.
- Use a **distinct** failure id. Do not reuse `PRECONDITION-ASSETS-RESOLVE`: that id is
  registered in `policy/checks.v1.yaml:327-336` with an `asserts` clause scoped to the
  asset table's rows, banners and headings. Raising it for a missing prompt file would
  make a registered inventory entry describe something it does not assert, which this
  repository treats as evidence misreporting (failure class B3), not a shortcut.
- No policy edit is required for the new id, and this must be verified rather than
  assumed. `runtime/controller.py` already raises six ids absent from
  `policy/checks.v1.yaml` (`PRECONDITION-CURRICULUM-OUTSIDE-ENGINE`,
  `PRECONDITION-CURRICULUM-MISSING`, `PRECONDITION-MANIFEST-MISSING`,
  `PRECONDITION-VERIFIER-MISSING`, `PRECONDITION-UNKNOWN-UNIT`,
  `PRECONDITION-RESUME-ROOT-MISSING`), and no file under `tests/gates/` matches
  `PRECONDITION-`. Re-run both greps at implementation time; if either has changed, stop
  and re-scope rather than editing `policy/checks.v1.yaml` under this plan.

### 2. Record the resolved prompt in preflight evidence

- In `static_preflight()` (line 138), add a `"prompt"` entry to the returned dict holding
  the resolved path and `sha256_file(self.prompt)`, in the same shape already used for
  `"companions"`.
- Before making this change, grep the repository for consumers that assert on the exact
  key set of the preflight dict (`tests/runtime/test_run_curriculum.py`,
  `tests/runtime/test_controller.py`, and any gate reading a preflight record). If any
  consumer compares the dict by equality rather than by key, add the key and update that
  single assertion; if that would cascade beyond one assertion, drop this step — it is the
  lowest-value part of the plan and is not worth widening the change.

### 3. Add the seventh part to `tests/check_meta_prompt.py`

- Add a `check_resolution()` function and register it in `main()`'s `parts` list
  (line 597) as `("resolution", check_resolution())`, placed **last** so the existing six
  parts keep their order and any reader diffing output sees an addition rather than a
  reshuffle. `main()` derives its score from `len(parts)`, so the printed
  `(N/N checks pass)` line updates itself; no count is hardcoded there.
- `check_resolution()` must **observe** the resolution, not re-derive it: import
  `runtime.controller`, instantiate `CurriculumRuntime(REPO)`, and read `.prompt` off the
  instance. A regex over `controller.py`'s source would be a second implementation of the
  resolution rule and would pass while the real one was broken.
- It reports three problems, each with the two paths named in the message:
  1. `resolution: the controller resolves <path>, which does not exist` when
     `runtime.prompt` is not a file.
  2. `resolution: the controller resolves <a> and this checker checks <b>` when the two
     differ. Compare `Path(...).resolve()` on **both** sides: `self.engine` is passed
     through `canonical()` but the joined prompt path is not, so an unresolved symlink
     anywhere above the repo would otherwise produce a false failure.
  3. `resolution: <path> does not exist` when `source.PROMPT` itself is missing.
- Wrap the import and instantiation in `try/except Exception` and convert a failure into a
  single `resolution:` problem naming the exception. `CurriculumRuntime.__init__` reads
  `policy/controller.v1.yaml` and `policy/limits.v1.yaml` and constructs a `Selector`;
  without this, an unrelated broken policy file would abort the whole checker and the
  other six parts would stop reporting. The checker must degrade to one honest failure,
  not to no output.
- **The `sys.path` order is load-bearing.** Insert `str(REPO)` at `sys.path[0]` on the
  line immediately **after** the existing `sys.path.insert(0, …)` at line 77, so the
  repository root precedes `tests/`. Never use `sys.path.append`, and never insert above
  line 77. `tests/runtime/` is itself an importable package named `runtime`
  (`tests/runtime/__init__.py` exists), so with `tests/` first on the path
  `import runtime.controller` resolves to the test package and raises
  `ModuleNotFoundError: No module named 'runtime.controller'`. Combined with the
  `try/except` below, the wrong order does not crash — it produces a permanently-red
  seventh part reporting an import error, which reads like the new check working. Verify
  the import resolves to `<REPO>/runtime/controller.py` by asserting on
  `runtime.controller.__file__`, running the checker from both the repository root and
  from another directory.
- Update the module docstring: it says "in six parts" and "What `6/6` means is narrow".
  Both become seven and `7/7`, and the new part gets its own numbered entry describing
  what it does and does not prove — it proves the controller and the checker name the same
  existing file; it does not prove that file is the *intended* version, which remains git
  history and review.

### 3a. Derive the banner regex instead of leaving a third literal

- In the same file, rebuild `SECTION_BANNER` (line 372) so the filename comes from
  `re.escape(source.PROMPT.name)` rather than the inline `curriculum\.prompt\.v1\.md`.
  The composed pattern must be character-for-character what it is today for the current
  version — confirm by comparing `SECTION_BANNER.pattern` before and after the edit.
- This is not tidying. `banner_problems()` (lines 519-587) is what makes flipping a table
  cell from `section` to `companion` a failure instead of a quieter contract. On a version
  bump the stale regex stops matching a correct `section asset of curriculum.prompt.v2.md`
  banner, so a section asset reads as `banner = None`: the flipped-cell attack goes
  undetected and a correctly bannered asset is reported as "declared section but carries no
  section banner" — a false failure in the opposite direction. `check_resolution()` cannot
  see either case, because it only compares resolved paths.
- No asset carries a section banner today (all three rows in
  `tests/meta_prompt_source.py:64-80` are `companion`), so this edit is expected to change
  no current output. Confirm that by diffing the checker's output against the step-0
  baseline; a changed line here means the derivation is wrong, not that a defect was found.

### 4. Add one regression test

- Add a test to `tests/runtime/test_controller.py` that sets `self.runtime.prompt` to a
  path under the test's temp directory that does not exist, calls `resolve_companions()`,
  and asserts a `RuntimeFailure` whose `failure_id` is `PRECONDITION-PROMPT-MISSING`.
  Mutating the attribute on the instance is sufficient and avoids building a throwaway
  engine tree — `CurriculumRuntime.__init__` reads two policy files from `engine`, so a
  bare temp directory cannot be constructed as an engine.
- Add a second test asserting the happy path is unchanged: `resolve_companions()` on the
  real engine returns the three companion paths and does not raise.
- Do not add a test that asserts the controller's literal equals a literal spelled again
  in the test. That is a third copy of the version and would itself go stale; the
  agreement is `check_resolution()`'s job, and it reads both sides.

## Verification sequence

1. Run `python3 tests/check_meta_prompt.py`, from the repository root and again from
   another directory. Pass means seven `PASS` lines and
   `meta prompt: EXECUTABLE (7/7 checks pass)` both times, with the six pre-existing parts
   reporting exactly what the step-0 baseline recorded — the banner derivation in step 3a
   must move no line of that output.
2. Prove the import is not shadowed. Assert that the `runtime.controller` module imported
   by the checker has `__file__` equal to `<REPO>/runtime/controller.py`, not
   `<REPO>/tests/runtime/…`. A `resolution` part that passes is not sufficient evidence
   here, because the `try/except` converts a shadowed import into a reported problem rather
   than a crash, and a reader skimming for `PASS` would not distinguish the two.
3. Prove the derived banner pattern is unchanged for the current version: print
   `SECTION_BANNER.pattern` and require it to equal the pre-edit pattern byte for byte.
4. Prove the new part can fail, then restore. Temporarily point `self.prompt` at
   `meta_prompt/curriculum.prompt.v2.md` (which does not exist), re-run, and require
   `FAIL resolution` naming both paths and `NOT EXECUTABLE (6/7 checks pass)`. Revert the
   edit and re-run to confirm step 1's result returns. A check that has never been
   observed failing has not been shown to check anything.
5. Run `python3 -m unittest discover -s tests/runtime -t .`. Pass means the two new tests
   pass and no previously passing test now fails.
6. Run `python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --preflight`
   and require exit 0, a `"prompt"` entry whose sha256 matches
   `shasum -a 256 meta_prompt/curriculum.prompt.v1.md`, and every other key unchanged
   against the step-0 baseline.
7. Run `python3 tests/gates/runner.py 5` and diff its result record against the gate
   baseline record captured in step 0, by path. Pass means no gate moved from PASS to FAIL
   or BLOCKED relative to *that* record. Every gate the step-0 capture already records as
   FAIL or BLOCKED is pre-existing and is not a regression — do not use a fixed list of
   expected failures, because the set is not stable: `FR-P2-DEFERRED` and
   `FR-P3-CAPS-OWNED` scan via `tests/gates/common.py:75 production_files()`, an `os.walk`
   of the repository root excluding only `{"tests", "plans", ".git"}`, so they read
   untracked files under `.claude/` and `docs/` and can move without any repository edit.
   If a gate outside this plan's edit set moves PASS → FAIL or BLOCKED, first re-run the
   step-0 capture command to establish whether the move is reproducible from an untracked
   file rather than from the change; only a move that survives that re-check is a
   regression. Compare against the captured baseline record rather than against an assumed
   clean run.
8. Re-run `git status --short`. Pass means the only changes beyond the step-0 baseline are
   `runtime/controller.py`, `tests/check_meta_prompt.py`, `tests/runtime/test_controller.py`,
   this plan package under `plans/_eval_mps_ws/`, and regenerated `__pycache__`.

## Acceptance criteria

- `resolve_companions()` raises `PRECONDITION-PROMPT-MISSING` when the active meta prompt
  is absent, and does so before any OUTPUT_ROOT is created, any log record is written, or
  any model is called, on both the `static_preflight()` and `session_bridge.prepare()`
  paths.
- `tests/check_meta_prompt.py` reports seven parts and fails as `resolution` — naming both
  paths — when the controller's resolved prompt and `tests/meta_prompt_source.PROMPT`
  disagree or do not exist. This has been observed failing, not merely asserted.
- No *functional* meta-prompt version literal remains in `tests/check_meta_prompt.py`:
  `SECTION_BANNER` is derived from `source.PROMPT.name`, and its compiled pattern is
  byte-identical to the pre-edit pattern for the current version. The inert mention inside
  the prose comment at `tests/check_meta_prompt.py:451` is out of scope and stays.
- The `runtime.controller` the checker imports resolves to `<REPO>/runtime/controller.py`,
  proved by `__file__` and not merely by the part reporting `PASS`.
- The new failure id is distinct from `PRECONDITION-ASSETS-RESOLVE`, and
  `policy/checks.v1.yaml` is unmodified.
- `runtime/` gains no import from `tests/`.
- Static preflight evidence records the resolved prompt path and hash.
- No gate regresses against the step-0 gate baseline record; pre-existing FAIL/BLOCKED
  gates are reported as pre-existing, citing that record by path.
- The meta prompt's own text, the asset table, and `policy/` are unchanged.

## Stop conditions and result

Stop on any of: a required edit outside `runtime/controller.py`,
`tests/check_meta_prompt.py`, `tests/runtime/test_controller.py` and this plan package; a
collision with pre-existing staged or unstaged user work in those files; discovering that
`policy/checks.v1.yaml` or a gate does enumerate controller failure ids after all, which
would make the new id a policy change rather than a code change; a preflight-dict consumer
that cannot absorb step 2 in a single assertion; or any gate moving from PASS to FAIL or
BLOCKED against the step-0 gate baseline record and still doing so on the re-check
described in verification step 7.
Stop rather than working around: do not delete a run root, do not weaken an existing
check, do not silence a pre-existing failure to make the diff look clean, and do not
resolve a stop condition by broadening scope. In particular, if the seventh part reports
an import error, fix the `sys.path` order — do not fall back to regexing `controller.py`,
which step 3 forbids for the reason given there.

`plans/contract_v2/prompt/contract_v2.prompt.v1.md:122,130` pin
`check_meta_prompt.py → 6/6` as a baseline and an acceptance criterion. That prompt has
never been executed and is already drifted on other numbers, and it is outside this plan's
edit set, so it is deliberately left untouched; record it in the result file as known-stale
documentation rather than editing it or treating the 6/6 disagreement as a regression.

Write `plans/_eval_mps_ws/_eval_mps_ws.result.v1.md` recording the step-0 baseline verbatim,
the changed paths, the output of each verification step including the deliberate
step-4 failure and its restoration, the gate diff against baseline, and any remaining
failure with evidence that it pre-existed. Append the execution outcome to
`plans/_eval_mps_ws/plans.log.md`.
