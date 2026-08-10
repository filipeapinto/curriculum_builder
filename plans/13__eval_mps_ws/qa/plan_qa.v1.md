# Meta-Prompt Active Version Staleness Check Plan v1 — Focused QA

## Verdict

**CHANGES REQUIRED — 0 Critical, 2 High.** The plan's factual spine holds up under
independent verification: `runtime/controller.py:29` is the literal, `resolve_companions()`
is at line 51 and is genuinely called first on both mutation paths (`static_preflight()`
line 139, `session_bridge.prepare()` line 69, both strictly before `require_internal_output`
at line 75 and `output.mkdir()` at line 78); `policy/checks.v1.yaml:327-336` is exactly the
`PRECONDITION-ASSETS-RESOLVE` entry the plan quotes; all six named controller failure ids
are confirmed absent from `policy/checks.v1.yaml`; `grep -rn "PRECONDITION-" tests/gates/`
returns nothing; `main()`'s `parts` list at lines 597-604 derives its score from `len(parts)`
with no hardcoded count; the only consumer of the preflight dict is
`tests/runtime/test_controller.py:32-35`, which reads three keys and never compares by
equality; `tests/results/*.json` and `outputs/` are both gitignored so verification step 6
is satisfiable; `--preflight` and `python3 tests/gates/runner.py 5` both exist and work; and
nothing executable reads `check_meta_prompt.py`'s output shape (`runtime/finalize_evidence.py:37`
records stdout/returncode without parsing). Two things block it. First, the plan's central
architectural claim — that `runtime/controller.py` is "the remaining file that breaks the
discipline" — is false: `tests/check_meta_prompt.py:373` hardcodes the same version literal
inside a live regex, in the very file the plan edits, and the plan leaves it stale. Second,
`import runtime.controller` from `tests/check_meta_prompt.py` is not the trivial sys.path
addition the plan describes, because `tests/runtime/` is itself an importable package named
`runtime` that shadows the real one.

## Findings

### 1. High — A third hardcoded meta-prompt version literal survives, inside the file the plan edits

**Evidence.** `tests/check_meta_prompt.py:372-374`:

```python
SECTION_BANNER = re.compile(
    r"<!--\s*section asset of curriculum\.prompt\.v1\.md"
    r"[^-]*?·\s*owns:\s*(.*?)\s*-->", re.S)
```

The plan's greps missed it because the literal is regex-escaped (`curriculum\.prompt\.v1\.md`),
so a search for `curriculum.prompt.v` does not match it:

```
$ grep -rn 'curriculum\.prompt\.v' --include="*.py" . | grep -v plans
runtime/controller.py:29
tests/meta_prompt_source.py:5,37,65
tests/check_meta_prompt.py:451        # a comment, not the regex

$ grep -rn 'curriculum\\\.prompt' --exclude-dir=.git .
tests/check_meta_prompt.py:373:    r"<!--\s*section asset of curriculum\.prompt\.v1\.md"
```

This directly falsifies two load-bearing plan statements. "Architectural end state" item 1-2:
*"`tests/meta_prompt_source.py` remains the single declared owner of the meta-prompt version …
`runtime/controller.py` is the remaining file that breaks the discipline."* It is not the
remaining file. It also falsifies the claim `tests/gates/fr_p5_engine.py:25-27` relies on
(*"`tests/meta_prompt_source.py` is, per readme.md, the only definition of 'the meta prompt'
any checker uses"*).

This literal is functional, not prose. `banner_problems()` (lines 519-587) is the check whose
own docstring says it exists so that *"flip a row from `section` to `companion` and that file
leaves the composition … and every other check still reports a full pass"* becomes a failure.
On a v1→v2 bump, `SECTION_BANNER` still matches only `…v1.md`, so a companion carrying a
correct `section asset of curriculum.prompt.v2.md` banner reads as `banner = None` and the
flipped-cell attack the check was written to stop goes undetected; symmetrically, a correctly
bannered v2 *section* asset is reported as *"declared section but carries no section banner"* —
a false failure. The plan's new `check_resolution()` cannot see either, because it only
compares the controller's resolved path against `source.PROMPT`.

**Impact.** The plan ships claiming the version literal is now owned in one place and checked,
while a second functional copy remains in the file it just edited. Part 6 (`assets`) silently
weakens on the next version bump — exactly the "reports a full pass on a gutted contract"
failure class the checker's own docstring cites as B3 misreporting.

**Minimal required remediation.** In step 3, add one bullet: rebuild `SECTION_BANNER` from
`re.escape(source.PROMPT.name)` instead of the inline `curriculum\.prompt\.v1\.md`, and correct
"Architectural end state" items 1-2 to name `tests/check_meta_prompt.py:373` as the second
offender rather than asserting `runtime/controller.py` is the only one. No new files, no scope
widening — the change is inside a file already in the plan's edit set.

### 2. High — `import runtime.controller` is shadowed by `tests/runtime/`; the sys.path insertion order is load-bearing and unstated

**Evidence.** The plan says (step 3): *"`sys.path` already contains `tests/` (line 77); add the
repository root the same way so `import runtime.controller` resolves when the file is run as
`python3 tests/check_meta_prompt.py` from any directory."* It treats this as a one-line
formality.

But `tests/runtime/` is a real package — `tests/runtime/__init__.py` exists
(`"""Focused tests for the reusable curriculum runtime."""`) — and `tests/` is already
`sys.path[0]` via line 77. So `runtime` is ambiguous, and only one ordering works:

```
$ python3 -c "import sys; from pathlib import Path;
sys.path.insert(0, str(Path('tests').resolve()));
sys.path.insert(0, str(Path('.').resolve()));
import runtime.controller as c; print('OK', c.__file__)"
OK /Users/filipepinto/Projects/curriculum_builder/runtime/controller.py

$ python3 -c "import sys; from pathlib import Path;
sys.path.insert(0, str(Path('.').resolve()));
sys.path.insert(0, str(Path('tests').resolve()));
import runtime.controller"
ModuleNotFoundError: No module named 'runtime.controller'
```

The second ordering is what you get from `sys.path.append(REPO)` — the most common idiom — or
from inserting the new line *above* line 77 rather than below it. The plan's own step-3
instruction to *"wrap the import and instantiation in `try/except Exception` and convert a
failure into a single `resolution:` problem"* means the wrong ordering does not crash loudly;
it produces a permanently-red seventh part reporting `ModuleNotFoundError`, which reads as the
new check working rather than as a wiring mistake.

I verified the correct wiring end-to-end (prototype at `/tmp/proto_check.py`, run from both the
repo root and `/tmp`): with the repo root inserted after line 77, `CurriculumRuntime(REPO).prompt`
resolves and `check_resolution()` returns `[]`. So the design is sound — only its stated
justification is.

**Impact.** A coin-flip between a working check and a check that always fails for a reason
unrelated to the thing it checks. In the failing case the plan's step-3 prohibition on regexing
`controller.py` makes the obvious "fix" the forbidden one.

**Minimal required remediation.** Replace the sys.path bullet with the explicit requirement:
insert `str(REPO)` at `sys.path[0]` on the line **immediately after** the existing line 77
(never `append`), and state why — `tests/runtime/` is an importable package named `runtime`
that shadows the engine's, so the repository root must precede `tests/` on `sys.path`.

## Observations (non-blocking)

- "Architectural end state" item 3 claims the prompt is proved to resolve *"before any run
  creates an OUTPUT_ROOT, writes a log record, or calls a model."* `CurriculumRuntime.simulate()`
  (`runtime/controller.py:161-234`) creates the output root at line 164 and writes log records
  without ever calling `resolve_companions()`. The Acceptance criteria correctly scope the claim
  to the `static_preflight()` and `prepare()` paths, and `simulate()` never reads `self.prompt`,
  so there is no functional defect — only an overclaim in the end-state section.

- `plans/contract_v2/prompt/contract_v2.prompt.v1.md:122` and `:130` pin
  `python3 tests/check_meta_prompt.py → 6/6 PASS` and *"`check_meta_prompt.py` still 6/6"* as
  baseline and acceptance criteria. The plan cites this file as its motivating scenario but does
  not note that a seventh part invalidates those two lines, and its stop conditions forbid
  editing them. That prompt has not been executed and is already drifted on another number
  (it says `FR-P0-NOSTALE` has "exactly three hits"; the current record
  `tests/results/gate_results.p5.20260803T141136.834494Z.json` shows 8), so this is stale
  documentation rather than a blocker.

- Baseline note for step 0: the current phase-5 record shows **two** pre-existing failures,
  `FR-P0-CLEAN` **and** `FR-P0-NOSTALE` (8 `assets/` hits, four of them in
  `runtime/session_bridge.py` and `.claude/skills/`). The plan's step 0 and verification step 5
  name only `FR-P0-CLEAN`. The diff-against-baseline method the plan prescribes handles this
  correctly, so no change is required.
