# Meta-Prompt Active Version Staleness Check Plan v1 — Focused QA (round 3)

## Verdict

**CHANGES REQUIRED — 0 Critical, 2 High.**

I did not review this on paper. I copied the repository twice into `/tmp/mpsqa/`
(`base/` pristine, `repo/` modified) and executed the plan end-to-end on the copy:
the controller fail-fast, the preflight `"prompt"` key, `check_resolution()`, the
derived `SECTION_BANNER`, the `sys.path` insertion, and the two regression tests.
The plan's factual spine holds — every line number, failure id, gate claim and
consumer claim I checked is accurate, and the implemented change produces
`EXECUTABLE (7/7 checks pass)` from both the repository root and `/tmp`, a correct
`FAIL resolution … (6/7 checks pass)` under the step-4 deliberate break, `Ran 49
tests … OK` (up from 47), a preflight `"prompt"` sha256 matching
`shasum -a 256`, and **byte-identical phase-4 and phase-5 gate status maps against
the pristine copy** (zero gate moved). Two things block. First, the bolded,
prescriptive `sys.path` bullet in step 3 is literally unexecutable: it instructs
inserting `str(REPO)` at line 78, and `REPO` is not bound until line 81 — I ran it
and got `NameError: name 'REPO' is not defined`, which kills the whole checker, not
just the seventh part. Second, verification step 6 diffs the preflight dict "against
the step-0 baseline", and step 0's four enumerated captures do not include a
preflight capture — the same defect class round 2 flagged as High for step 7, in a
step round 2 did not re-check.

## Findings

### 1. High — The prescribed `sys.path` insertion point raises `NameError` and crashes the checker; `REPO` is not defined until three lines later

**Evidence.** Step 3 is prescriptive and bolded about the exact line:

> **The `sys.path` order is load-bearing.** Insert `str(REPO)` at `sys.path[0]` on the
> line immediately **after** the existing `sys.path.insert(0, …)` at line 77, so the
> repository root precedes `tests/`. Never use `sys.path.append`, and never insert above
> line 77.

The module header of `/Users/filipepinto/Projects/curriculum_builder/tests/check_meta_prompt.py`
binds `REPO` two statements *later*:

```
77  sys.path.insert(0, str(Path(__file__).resolve().parent))
78
79  import meta_prompt_source as source  # noqa: E402
80
81  REPO = source.REPO
```

I applied the instruction verbatim on the scratch copy and ran it:

```
$ sed -n '77,78p' /tmp/mpsqa/repo/tests/check_meta_prompt.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO))

$ python3 tests/check_meta_prompt.py
Traceback (most recent call last):
  File "/private/tmp/mpsqa/repo/tests/check_meta_prompt.py", line 78, in <module>
    sys.path.insert(0, str(REPO))
                           ^^^^
NameError: name 'REPO' is not defined
```

Moving the same statement to immediately after line 81 preserves the ordering property
the plan is protecting and works: I re-ran the fully implemented checker and got
`EXECUTABLE (7/7 checks pass)` from the repository root and from `/tmp`, with
`runtime.controller.__file__ == /private/tmp/mpsqa/repo/runtime/controller.py`.
The plan's underlying *diagnosis* is correct and I re-proved it independently:

```
BAD-ORDER  (tests/ at index 0): ModuleNotFoundError: No module named 'runtime.controller'
GOOD-ORDER (REPO at index 0):   /tmp/mpsqa/repo/runtime/controller.py
```

**Impact.** An implementer following the bullet literally gets a module-level
`NameError` on *every* invocation of `tests/check_meta_prompt.py` — all seven parts
stop reporting, `runtime/finalize_evidence.py:37` (which shells out to this checker)
records a traceback, and verification steps 1-4 all fail at once. The plan's own
recovery guidance does not cover this: the stop conditions say "if the seventh part
reports an import error, fix the `sys.path` order", but a `NameError` at import time
means there is no seventh part and no output at all, so the symptom does not match the
prescription. The prohibition "never insert above line 77" is correct and must be kept —
inserting above line 77 lets line 77 push `tests/` back to index 0 and re-creates the
shadowing — so the implementer cannot resolve this by moving the line up.

**Minimal required remediation.** In step 3, change "on the line immediately **after**
the existing `sys.path.insert(0, …)` at line 77" to "on the line immediately **after**
`REPO = source.REPO` at line 81 (`REPO` is not bound before then), which still leaves
the repository root ahead of `tests/`". Keep the "never `append`, never above line 77"
prohibitions unchanged.

### 2. High — Verification step 6 diffs the preflight dict against a "step-0 baseline" that step 0 never captures

**Evidence.** Step 0 enumerates its captures and closes the set explicitly:

> Capture `git status --short` and `git stash list` … Capture the current output of
> `python3 tests/check_meta_prompt.py` verbatim … Capture the current output of
> `python3 -m unittest discover -s tests/runtime -t .`. … Capture the gate baseline
> **before any edit** … **These four captures are the baseline.**

Step 6 then requires a fifth comparison the four captures cannot support:

> Run `python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --preflight`
> and require exit 0, a `"prompt"` entry whose sha256 matches … and **every other key
> unchanged against the step-0 baseline**.

Every other verification step maps onto a capture: step 1 → capture 2, step 5 →
capture 3, step 7 → capture 4, step 8 → capture 1. Step 6 alone has no antecedent.
The comparison is also not reconstructible after the fact, because step 2 edits
`static_preflight()` itself. On the scratch copy the post-change output is:

```
$ python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --preflight | \
    python3 -c "import json,sys;d=json.load(sys.stdin);print(list(d.keys()))"
['status', 'manifest', 'manifest_sha256', 'unit_count', 'unit_ids', 'prompt', 'companions', 'verifier_fixtures']
```

— the new key is inserted *between* `unit_ids` and `companions`, so the raw JSON also
reorders. Without a pre-edit capture there is nothing to establish that `manifest`,
`manifest_sha256`, `unit_count`, `unit_ids`, `companions` and `verifier_fixtures` are
unchanged rather than merely present.

**Impact.** Step 6's stated pass condition cannot be discharged, and the closing
instruction — "Write `plans/_eval_mps_ws/_eval_mps_ws.result.v1.md` recording the step-0
baseline verbatim, … the output of each verification step" — mandates recording evidence
the plan never told the implementer to collect. This is the identical defect the round-2
QA raised as High for step 7 and that step 0 was amended to close for gates; the same
amendment was not extended to preflight. The likely outcome is that the implementer
silently downgrades step 6 to "the `prompt` key is present and its hash matches", which
is the weaker check the plan explicitly rejected elsewhere.

**Minimal required remediation.** Add a fifth bullet to step 0: "Capture the current
output of `python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit
--preflight` verbatim", and change "These four captures are the baseline" to "These five
captures are the baseline".

## Prior-round remediation check

**Prior High (a) — third regex-escaped version literal in `SECTION_BANNER` at
`tests/check_meta_prompt.py:373`. Genuinely fixed, and the line numbers are right.**
`SECTION_BANNER = re.compile(` is at line 372 and the escaped literal
`curriculum\.prompt\.v1\.md` is at line 373, exactly as the plan's intro (373) and
step 3a (372) each state. I confirmed the plan's supporting claim that the literal is
invisible to a naive search:

```
$ grep -n "curriculum.prompt.v" tests/check_meta_prompt.py
451:    # `curriculum.prompt.v1.md` is. What made the *old* zero-section state a defect was
```

— line 373 does not appear, because the on-disk text is backslash-escaped. I then applied
step 3a's derivation on the scratch copy and compared compiled patterns rather than
trusting the plan:

```
$ python3 -c "<load edited check_meta_prompt.py>; print(repr(m.SECTION_BANNER.pattern)); ..."
'<!--\\s*section asset of curriculum\\.prompt\\.v1\\.md[^-]*?·\\s*owns:\\s*(.*?)\\s*-->'
IDENTICAL: True
```

The claim that the edit changes no current output also holds: all three `EXPECTED` rows in
`tests/meta_prompt_source.py:64-80` are `COMPANION`, so `banner_problems()` (line 519)
never reaches the banner-matching branch, and the checker's six pre-existing `PASS` lines
were byte-identical before and after in my run.

**Prior High (b) — `sys.path` shadowing of the `runtime` package by `tests/runtime/`.
Diagnosis fixed, prescription broken.** The plan now names `tests/runtime/__init__.py`
as the shadowing package, explains that the `try/except` converts a wrong order into a
permanently-red part rather than a crash, requires asserting on
`runtime.controller.__file__`, repeats that in verification step 2, and forbids the
regex fallback in the stop conditions — all of which I re-proved by experiment (both
orders reproduced above; `tests/runtime/__init__.py` exists; running
`python3 tests/check_meta_prompt.py` puts `<REPO>/tests` at `sys.path[0]` by script-directory
default before line 77 even executes). What is **not** fixed is the concrete insertion
point the remediation introduced — see Finding 1. The remediation for a shadowing bug
introduced a `NameError`; it needs one more line-number correction to be genuinely closed.

**Prior High (c) — verification step 7 diffing against an uncaptured gate baseline.
Genuinely fixed.** Step 0 now carries the fourth capture ("run `python3
tests/gates/runner.py 5`, record the path of the `tests/results/gate_results.p5.<ts>.json`
it emits, and record that record's per-gate status map … This captured path is *the
baseline record* referred to in verification step 7"), explicitly disqualifies every
on-disk record as authoritative via `.gitignore:4` (confirmed: line 4 is
`tests/results/*.json`), and step 7 now says "diff its result record against the gate
baseline record captured in step 0, **by path**" with the fixed
`FR-P0-CLEAN`/`FR-P0-NOSTALE` expected-failure list replaced by "every gate the step-0
capture already records as FAIL or BLOCKED is pre-existing". The `production_files()`
rationale is accurate (`tests/gates/common.py:75`, `os.walk` excluding only
`{"tests", "plans", ".git"}`), and the cited
`tests/results/gate_results.p5.20260803T133435.900879Z.json` does record exactly
`{'FR-P0-NOSTALE': 'FAIL', 'FR-P0-CLEAN': 'FAIL'}`. I also verified the underlying
premise the step exists to protect — that this change moves no gate — by running both
phases on the pristine and modified copies:

```
base: /tmp/mpsqa/base/tests/results/gate_results.p5.…json
mod : /tmp/mpsqa/repo/tests/results/gate_results.p5.…json
DIFFS: {}
base non-PASS: {'FR-P0-NOSTALE': 'FAIL', 'FR-P0-CLEAN': 'FAIL', 'FR-P2-DEFERRED': 'FAIL',
  'FR-P2-BOUND': 'BLOCKED', 'FR-P2-SEL-MAPPED': 'BLOCKED', 'FR-P3-CAPS-OWNED': 'FAIL',
  'FR-P4-AGREEMENT': 'BLOCKED', 'FR-P4-CHECK-MAPPING': 'BLOCKED'}
phase 4 base: 22 PASS, 4 FAIL, 4 BLOCKED, 8 SKIPPED   phase 4 mod: identical
```

## Observations (non-blocking)

- **`check_resolution()` problem 3 is unreachable dead code.** Step 3 requires
  "`resolution: <path> does not exist` when `source.PROMPT` itself is missing". `main()`
  calls `text = source.compose()` (line 595) *before* building `parts`, and
  `compose()` → `sources()` → `PROMPT.read_text()` raises `FileNotFoundError` first, so the
  checker dies before the seventh part runs. Harmless, but it can never fire and cannot be
  demonstrated failing.

- **Step 2 is optional but its output is an unconditional acceptance criterion.** Step 2
  says "if that would cascade beyond one assertion, drop this step", while the acceptance
  criteria state unconditionally "Static preflight evidence records the resolved prompt path
  and hash" and step 6 unconditionally requires the `"prompt"` entry. I confirmed the drop
  branch is unreachable in this tree — the only `static_preflight` consumer is
  `tests/runtime/test_controller.py:32-35`, which reads three keys and never compares by
  equality; `tests/runtime/test_run_curriculum.py` never mentions preflight; and no gate,
  schema or policy file reads `gate_1_static_preflight` (`grep -rn gate_1_static_preflight
  tests/ runtime/ policy/ schemas/` → nothing). So the contradiction is latent, not live.

- **"six ids absent from `policy/checks.v1.yaml`" is an undercount.** `runtime/controller.py`
  also raises `PRECONDITION-MANIFEST-INVALID`, `PRECONDITION-DOMAIN-CONTRACT-ESCAPES`,
  `PRECONDITION-DOMAIN-MANIFEST-INVALID`, `PRECONDITION-VERIFIER-UNPROVEN` and
  `PRECONDITION-VERIFIER-FIXTURE`, none of which are in `policy/checks.v1.yaml` either (the
  file contains only `PRECONDITION-OUTPUT-ROOT-EXISTS` at line 319 and
  `PRECONDITION-ASSETS-RESOLVE` at line 327). The direction of the claim — no policy edit is
  required — is correct and I re-verified both greps: `grep -rn "PRECONDITION-" tests/gates/`
  returns nothing, and `policy/failures.v1.yaml` is a failure-*class* taxonomy (`A1`…`C1`),
  not a runtime failure-id registry.

- **`runtime/session_bridge.py:76-82` is off by one at the low end.** `require_internal_output`
  is at line 75, not 76; `output.mkdir()` is at 78 and the logger gate plus
  `results/gate_0_logger.json` at 81-82. The argument is unaffected. `runtime/session_bridge.py:91`
  is exactly `(runtime.prompt, "prompt.md")`, as claimed.

- **The "fourteen `owner:` copies" claim is exact.**
  `grep -c "meta_prompt/curriculum.prompt.v1.md" policy/checks.v1.yaml` → `14`, and
  `policy/deferred.v1.yaml:140` carries the fifteenth. `tests/gates/fr_p4_policy_schemas.py`
  does fail an entry whose `owner` path does not exist
  (`advertised-without-owner:{cid} — owner {owner} does not exist`), though note that the
  gate carrying that check, `FR-P4-CHECK-MAPPING`, is currently BLOCKED in this tree, so the
  "breaks loudly" guarantee is not presently executing.

- **Everything else in the verification sequence executed as written on the copy.**
  `EXECUTABLE (7/7 checks pass)` from repo root and from `/tmp`; step 4's deliberate break
  (pointing line 29 at `curriculum.prompt.v2.md`) produced `FAIL resolution` with both paths
  named across two problems and `NOT EXECUTABLE (6/7 checks pass)`; `python3 -m unittest
  discover -s tests/runtime -t .` gave `Ran 49 tests … OK` (47 before, +2), with the same
  pre-existing `--max-run-seconds` argparse noise the round-2 QA recorded; preflight exited 0
  with `sha256 46fc2670…` matching `shasum -a 256 meta_prompt/curriculum.prompt.v1.md`. The
  only version literal left in `tests/check_meta_prompt.py` after step 3a is the prose comment
  at line 451, which the acceptance criteria already scope out.
