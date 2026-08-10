# Meta-Prompt Active Version Staleness Check Plan v1 — Focused QA (round 2)

## Verdict

**CHANGES REQUIRED — 0 Critical, 1 High.** I re-derived the plan's factual spine from the
repository rather than from the document, and it holds almost everywhere: `runtime/controller.py:29`
is the literal; `resolve_companions()` is at line 51 and is the first call in both
`static_preflight()` (line 139) and `session_bridge.prepare()` (line 69, strictly before
`require_internal_output` at 75, `output.mkdir()` at 78 and the logger gate at 81-82);
`simulate()` (161-234) genuinely never touches `self.prompt` or `resolve_companions()`;
`policy/checks.v1.yaml:327-336` is exactly the `PRECONDITION-ASSETS-RESOLVE` entry quoted, with
an `asserts` clause scoped to rows/banners/headings; all six named controller failure ids are
absent from `policy/checks.v1.yaml` and `grep -rn "PRECONDITION-" tests/gates/` returns nothing;
`main()`'s `parts` list at line 597 derives its score from `len(parts)`; the sole preflight-dict
consumer is `tests/runtime/test_controller.py:32-35`, which reads three keys and never compares
by equality; and both new step 3a and the new `sys.path` bullet are correct — I proved the
derived `SECTION_BANNER` byte-identical and proved the import-shadowing behaviour by experiment.
The one blocker is verification step 7: step 0 never captures a gate baseline record, the only
gate record the plan names is now six gates out of date, and the plan asserts as fact that
`FR-P0-CLEAN` and `FR-P0-NOSTALE` are the only expected failures when phase 5 currently reports
four FAIL and four BLOCKED.

## Findings

### 1. High — Verification step 7 diffs against a "baseline record" step 0 never captures, and the plan's stated pre-existing gate failures are wrong by six gates

**Evidence.** Step 0 enumerates the baseline explicitly and gates are not in it:

> Capture `git status --short` and `git stash list` … Capture the current output of
> `python3 tests/check_meta_prompt.py` … Capture the current output of
> `python3 -m unittest discover -s tests/runtime -t .` … **These three captures are the
> baseline.**

Step 7 then says "Run `python3 tests/gates/runner.py 5` and diff its result record against
**the baseline record**", and asserts "Both `FR-P0-CLEAN` and `FR-P0-NOSTALE` are expected to
remain FAIL … and neither is a regression." The only gate record the plan names anywhere is
`tests/results/gate_results.p5.20260803T133435.900879Z.json`, cited in step 0 as evidence of
worktree dirt.

That record and the current tree disagree by six gates. I ran the phase-5 runner read-only:

```
$ python3 tests/gates/runner.py 5
phase 5: 30 PASS, 4 FAIL, 4 BLOCKED, 0 SKIPPED of 38 registered
results: tests/results/gate_results.p5.20260803T153244.078373Z.json
```

Per-record comparison:

```
gate_results.p5.20260803T133435.900879Z.json  {'PASS': 36, 'FAIL': 2, 'BLOCKED': 0}
    ['FR-P0-NOSTALE', 'FR-P0-CLEAN']                      <- the record the plan cites
gate_results.p5.20260803T152642.390461Z.json  {'PASS': 35, 'FAIL': 3, 'BLOCKED': 0}
    [... , 'FR-P3-CAPS-OWNED']
gate_results.p5.20260803T153244.078373Z.json  {'PASS': 30, 'FAIL': 4, 'BLOCKED': 4}
    ['FR-P0-NOSTALE', 'FR-P0-CLEAN', 'FR-P2-DEFERRED', 'FR-P2-BOUND',
     'FR-P2-SEL-MAPPED', 'FR-P3-CAPS-OWNED', 'FR-P4-AGREEMENT', 'FR-P4-CHECK-MAPPING']
```

Neither extra failure is related to this plan, and neither is stable. `FR-P3-CAPS-OWNED` fails
on `docs/research/…`; `FR-P2-DEFERRED` fails on
`.claude/skills/plan-create-workspace/iteration-1/eval-gate-flakiness/…`. Both gates scan via
`tests/gates/common.py:75 production_files()`, which is an `os.walk` of `REPO_ROOT` excluding
only `{"tests", "plans", ".git"}` (`common.py:55-56`) — i.e. it reads **untracked** files under
`.claude/` and `docs/`. `FR-P0-NOSTALE`, by contrast, uses `git ls-files`
(`fr_p0_structure.py:278-292`). The phase-5 verdict therefore moved from 3 FAIL to 4 FAIL +
4 BLOCKED between 15:26 and 15:32 with no source edit at all.

`tests/results/*.json` is gitignored (`.gitignore:4`), so no gate record is under version
control and none of the ones on disk is pinned as authoritative.

**Impact.** An implementer following the plan literally has no baseline gate record to diff
against. The only one named shows 36 PASS / 2 FAIL / 0 BLOCKED; a post-change run today shows
30 / 4 / 4, so six gates appear to have moved PASS → FAIL or BLOCKED. Step 7's pass condition
("no gate moved from PASS to FAIL or BLOCKED") and the stop condition ("any gate moving from
PASS to FAIL") both fire on failures the change did not cause, halting a correct implementation.
The alternative reading — waving the extra failures away because the plan says only two are
expected — destroys the only mechanism that would have caught a genuine regression. The plan's
own instruction "Compare against the baseline record rather than against an assumed clean run"
is exactly right and is unexecutable as written.

**Minimal required remediation.** In step 0, add a fourth capture: run
`python3 tests/gates/runner.py 5` **before any edit** and record the emitted
`tests/results/gate_results.p5.<ts>.json` path and its per-gate status map as the gate baseline.
In step 7, replace "the baseline record" with that captured path, and replace the sentence
naming `FR-P0-CLEAN` and `FR-P0-NOSTALE` as the expected failures with "every gate the step-0
capture already records as FAIL or BLOCKED is pre-existing", noting that `FR-P2-DEFERRED` and
`FR-P3-CAPS-OWNED` scan untracked files outside `tests/` and `plans/` and so can move without
any repository edit.

## Prior-round remediation check

**Prior High 1 — third hardcoded version literal in `SECTION_BANNER`. Genuinely fixed.** The
plan now carries a dedicated step 3a rebuilding `SECTION_BANNER` (line 372) from
`re.escape(source.PROMPT.name)`, corrects "Architectural end state" item 1 to name **two**
offending files (`runtime/controller.py:29` and `tests/check_meta_prompt.py:373`), states why
the literal is functional rather than cosmetic (`banner_problems()`, lines 519-587), and adds
verification step 3 requiring byte-identity of the compiled pattern. I verified the derivation
is genuinely byte-identical rather than merely plausible — `re.escape` on this filename escapes
only the dots, and the non-ASCII `·` (U+00B7) and `[^-]*?` segments are outside the derived
part:

```
$ python3 -c "... print(repr(cur.pattern)); print(repr(new.pattern)); print(cur.pattern==new.pattern)"
'<!--\\s*section asset of curriculum\\.prompt\\.v1\\.md[^-]*?·\\s*owns:\\s*(.*?)\\s*-->'
'<!--\\s*section asset of curriculum\\.prompt\\.v1\\.md[^-]*?·\\s*owns:\\s*(.*?)\\s*-->'
IDENTICAL: True
```

The plan's supporting claim that step 3a changes no current output is also true: all three rows
in `tests/meta_prompt_source.py:64-80` are `COMPANION`, so `banner_problems()` never reaches the
banner-matching branch today.

**Prior High 2 — `import runtime.controller` shadowed by `tests/runtime/`. Genuinely fixed.**
Step 3 now carries a bolded, prescriptive bullet: insert `str(REPO)` at `sys.path[0]` on the
line **immediately after** the existing `sys.path.insert(0, …)` at line 77, never `append`,
never above line 77; it names `tests/runtime/__init__.py` as the shadowing package, explains
that the `try/except` converts the wrong order into a permanently-red part rather than a crash,
and requires asserting on `runtime.controller.__file__`. Verification step 2 repeats the
`__file__` requirement and explicitly rejects "the part reports PASS" as sufficient evidence,
and the stop conditions forbid falling back to regexing `controller.py`. I confirmed both halves
by experiment:

```
BAD-ORDER  (tests/ first): ModuleNotFoundError: No module named 'runtime.controller'
GOOD-ORDER (REPO first):   /Users/filipepinto/Projects/curriculum_builder/runtime/controller.py
                           prompt: .../meta_prompt/curriculum.prompt.v1.md True
```

`tests/runtime/__init__.py` exists, and `python3 tests/check_meta_prompt.py` puts `<REPO>/tests`
at `sys.path[0]` by script-directory default before line 77 even runs, so the prescribed
ordering is both necessary and sufficient.

## Observations (non-blocking)

- **Acceptance criterion slightly overstated.** "No meta-prompt version literal remains in
  `tests/check_meta_prompt.py`" will still be literally false after step 3a:
  `tests/check_meta_prompt.py:451` contains `curriculum.prompt.v1.md` inside a prose comment.
  It is inert, and the criterion's own colon-clause narrows the claim to `SECTION_BANNER`, so
  this is wording rather than a defect.

- **`policy/checks.v1.yaml` holds fourteen copies of the literal.** Fourteen `owner:
  meta_prompt/curriculum.prompt.v1.md` lines, plus one in `policy/deferred.v1.yaml:140`. The
  plan's item 1 ("**Two** files break that discipline today") is imprecise. It is not a blocker,
  because `tests/gates/fr_p4_policy_schemas.py:131-146` fails any entry whose `owner` path does
  not exist, so a version bump breaks those loudly rather than silently — which is the opposite
  of the failure class this plan exists to close.

- **Step 8's allowed-change list omits gate result records.** Running step 7 writes a new
  `tests/results/gate_results.p5.<ts>.json`. It is gitignored, so `git status --short` is
  unaffected and step 8 still passes as written; noting it only so the result file does not
  record it as an unexplained artifact.

- **Verification steps 1, 5 and 6 are executable exactly as written.** I ran the read-only
  ones: `python3 tests/check_meta_prompt.py` gives `EXECUTABLE (6/6 checks pass)` identically
  from the repository root and from `/tmp`; `python3 -m unittest discover -s tests/runtime -t .`
  gives `Ran 47 tests … OK` (with pre-existing subprocess argparse noise on
  `--phase-timeout-seconds` / `--max-run-seconds` that does not fail the suite);
  `python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --preflight` exits 0 and
  writes nothing. `runtime/io.py:35 sha256_file` returns a bare hexdigest matching
  `shasum -a 256`, so step 6's hash comparison is well formed. The numbered steps 1-8 have no
  duplicates or gaps, and the stop conditions reference step 2 (preflight dict), step 3 (the
  regex prohibition) and verification step 4 (the deliberate failure) correctly.

- **Step 4's "naming both paths" is satisfiable despite problem template 1 naming only one.**
  Pointing `self.prompt` at a nonexistent `…v2.md` fires both problem 1 (not a file) and problem
  2 (differs from `source.PROMPT`), so both paths appear across the reported problems and the
  part count is still `6/7`.
