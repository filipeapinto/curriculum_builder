# Meta-Prompt Activation — Implementation Plan v1

## Status and objective

Planning only; no implementation is authorized by this document's creation.

`runtime/controller.py:29` sets `self.prompt = self.engine / "meta_prompt/curriculum.prompt.v1.md"`.
That literal is never checked for existence, and it is the one copy of the active
meta-prompt path that nothing compares against anything else. Make the active version the
controller resolves a checked fact: it must exist, and it must be the same file
`tests/check_meta_prompt.py` reads as *the contract*.

## What is already checked, and what is not

There are four independent statements of the active meta-prompt path:

| # | Where | Currently protected by |
| - | ----- | ---------------------- |
| 1 | `tests/meta_prompt_source.py:PROMPT_REL` | it *is* the checker's subject; nothing above it |
| 2 | the prompt's own `PROMPT = ENGINE/meta_prompt/curriculum.prompt.v1.md` boundary line | `check_meta_prompt.creator_derivable`, which requires a boundary line equal to `ENGINE/<rel>` with `REPO/<rel> == PROMPT` |
| 3 | 14 `owner:` rows in `policy/checks.v1.yaml` | `FR-P4-CHECK-MAPPING`, which requires each `owner` file to exist |
| 4 | `runtime/controller.py:29` | **nothing** |

So (1)⇄(2) already agree by construction and (3) is at least required to resolve. (4) is
the hole. Its only consumer is `runtime/session_bridge.py:91`, which copies
`runtime.prompt` into `OUTPUT_ROOT/inputs/prompt.md` during input freeze. A stale literal
there fails late, mid-run, as a copy error inside an already-created evidence root — after
the logger gate, the manifest validation and the verifier fixtures have all passed. It can
also fail *silently* in the direction that matters more: a repository that has moved to a
v2 contract, with (1)–(3) all updated, would still freeze v1 into every run and every hash
in `input_freeze.json`, and all 31 gates plus 6/6 on the checker would still be green.

The defect class is therefore not "a missing file". It is **the runtime handing over a
different contract from the one the repository certifies.**

## Architectural end state

1. `CurriculumRuntime` resolves the active meta-prompt through one method,
   `resolve_prompt()`, that mirrors the existing `resolve_companions()`: it returns the
   path and raises `RuntimeFailure("PRECONDITION-PROMPT-RESOLVE", ...)` if the file is not
   there. Missing contract is a precondition failure at preflight, not an I/O error at
   freeze time.
2. `static_preflight()` reports the prompt with its SHA-256, exactly as it already reports
   each companion. A preflight that names every companion and omits the contract itself is
   an incomplete statement of what a run would read.
3. `tests/check_meta_prompt.py` gains a **seventh** check, `activation`, which asserts that
   the path the controller actually resolves at runtime is the file this checker composed.
   The checker's other six ask whether the contract can be started; this one asks whether
   the started contract is the one the runtime hands over.
4. No behaviour of the composed contract changes. No prompt text changes. No gate is added.

## Exact work

### 1. `runtime/controller.py` — one resolver, one failure id

- Keep the literal at line 29 assigning `self.prompt`; the constructor stays cheap and
  total, so constructing a `CurriculumRuntime` never fails on a missing prompt. Making
  `__init__` raise would break every existing `tests/runtime/` construction that never
  touches the prompt, and would make the new activation check die with a `RuntimeFailure`
  traceback instead of reporting a problem.
- Add `resolve_prompt(self) -> Path`: returns `self.prompt` if it `is_file()`, otherwise
  raises `RuntimeFailure("PRECONDITION-PROMPT-RESOLVE", f"missing active contract: {self.prompt}")`.
- Call it first in `static_preflight()`, before `resolve_companions()` — the contract
  outranks the companions it binds — and add `"prompt": {"path": ..., "sha256": ...}` to
  the returned dict.
- Call it at the top of `simulate()` as well, before `prepare_output`, so the failure
  precedes any evidence-root mutation. `simulate` never reads `self.prompt` today, so
  `--test-simulated-all` would otherwise walk every state, pass the final log audit and
  return `ACCEPTED` for an engine whose contract had been deleted. Both `--test-static` and
  `--test-simulated-all` are among the six commands in `runtime/finalize_evidence.py`;
  protecting only the first would leave the more frequently run path uncovered.
- Do not declare `PRECONDITION-PROMPT-RESOLVE` in `policy/checks.v1.yaml`. See §3 below;
  this is a deliberate decision, not an omission.

### 2. `runtime/session_bridge.py` — fail before the evidence root exists

- In `prepare()`, call `runtime.resolve_prompt()` on the line adjacent to the existing
  `runtime.resolve_companions()` call, i.e. before `require_internal_output` /
  `output.mkdir`. The freeze loop at line 91 then copies a path already proven present.
- Change nothing else in the freeze list. `_copy` keeps its current behaviour.

### 3. Why no new policy declaration

`policy/checks.v1.yaml` declares exactly two `PRECONDITION-*` ids
(`PRECONDITION-OUTPUT-ROOT-EXISTS`, `PRECONDITION-ASSETS-RESOLVE`), each with
`owner: meta_prompt/curriculum.prompt.v1.md`, `method: execution`, `deferred: RT-5`.
Eleven other `PRECONDITION-*` ids raised in `runtime/` are undeclared.

Declaring a twelfth would require `FR-P4-CHECK-MAPPING` to be satisfied: an existing
`owner` file plus either a `verified_by` naming a gate registered in
`tests/gates/registry.py`, or a `deferred:` entry in `policy/deferred.v1.yaml`. The first
would require registering a gate, which `FR-P0-REGISTRY` would then require to appear in
the owning family's plan catalogue — dragging a finished folder-refactoring plan into this
change. The second would attach a new deferral to a discharged RT id.

So: this plan adds an undeclared precondition id, consistent with the eleven that already
exist, and states that asymmetry here rather than half-resolving it. Generalising the
registry so a check like this can be declared is separate work and is named as such.

### 4. `tests/check_meta_prompt.py` — the `activation` check

Add `check_activation()` and register it as a seventh part in `main()`.

```
7. **activation**   the controller resolves this contract and no other. The path
                    `runtime.controller.CurriculumRuntime` hands to the input freeze
                    exists, and is the file composed above. A contract that passes
                    1-6 and is not the one a run reads is a contract certified in
                    place of another.
```

It must assert, in this order, and report every failure as a problem string:

1. `runtime.controller` imports and a `CurriculumRuntime` constructs. Add
   `sys.path.insert(0, str(REPO))` beside the existing insert of `tests/` at line 77:
   `runtime/controller.py` uses package-relative imports, so `import runtime.controller`
   resolves only with the repository root on the path, and today that holds only because
   both known invocations happen to run with the repository as cwd. **Any exception here is
   caught and reported as an `activation:` problem, never allowed to escape as a
   traceback.** The checker's five other parts read only stdlib and `meta_prompt_source`;
   `runtime.controller` pulls in `jsonschema`, `yaml`, `policy/controller.v1.yaml` and
   `policy/limits.v1.yaml`, and a checker whose subject is the meta-prompt must not die
   with an unrelated stack trace and no verdict.
2. `runtime.resolve_prompt()` returns without raising — i.e. the controller's active
   contract exists on disk. A `RuntimeFailure` here is reported with its `failure_id`.
3. `runtime.prompt == source.PROMPT`, compared as resolved paths, with both sides printed
   on mismatch. This is the check the user asked for.
4. `resolve_prompt` is called from `static_preflight`, from `simulate`, and from
   `session_bridge.prepare` — read with `inspect.getsource` of the three **function
   objects**, not by scanning the files, and requiring the literal call token in each. A
   file-level regex would match the name in a comment or an unreachable branch and would
   miss a call reached through a rename. The docstring must state the limit plainly: this
   proves the call is *written*, not that it *executes*. The behavioural half lives in
   `tests/runtime/` (§5); neither covers what the other does.
5. Every `owner:` value in `policy/checks.v1.yaml` of the form
   `meta_prompt/<name>.prompt.v<n>.md`, with no further path separator, names
   `source.PROMPT_REL`. Fourteen rows currently do. `FR-P4-CHECK-MAPPING` proves those
   files exist; it does not prove they are the *active* one, so a v2 activation that left
   the 14 rows pointing at a retained v1 would pass every gate. The pattern is anchored to
   the top level of `meta_prompt/` deliberately: `plans/contract_v2/prompt/contract_v2.prompt.v1.md:104`
   plans to retain the superseded prompt under `meta_prompt/deprecated/`, and an owner row
   naming retained history is not a stale activation. A check that forbade the migration it
   protects would be deleted the first time it fired.

Add the check to the module docstring's numbered list and to the "what 6/6 does not say"
paragraph, which must become 7/7. The docstring is the contract of this checker and a
seventh check that only the code knows about is the same defect one level up.

### 5. Tests

- `tests/runtime/test_controller.py` (stdlib `unittest`, matching every file in
  `tests/runtime/`): one test that `resolve_prompt()` returns the path for the real engine;
  one that `static_preflight()` output carries `prompt.sha256` equal to `sha256_file` of
  the real prompt; and, against a temporary engine copy under `ENGINE/outputs/` whose
  prompt is absent, three tests asserting `RuntimeFailure` with
  `failure_id == "PRECONDITION-PROMPT-RESOLVE"` out of `static_preflight`, `simulate`, and
  `session_bridge.prepare` — the behavioural counterpart to §4 item 4, which proves only
  that the calls are written. `simulate` must additionally be shown to raise **before**
  creating its output root.
- No fixture may create a second `meta_prompt/curriculum.prompt.v*.md` inside the
  repository proper: `check_assets` treats unowned files under `meta_prompt/assets/` as
  orphans, and a stray prompt sibling is exactly the ambiguity this plan exists to remove.
  Temporary engines live under `ENGINE/outputs/` per `require_internal_output`.

## Verification sequence

1. `python3 tests/check_meta_prompt.py` — expect `7/7`, `EXECUTABLE`.
2. Run it once from a directory that is not the repository root and require the same 7/7.
   The check imports the runtime, and it must not report the contract broken because of
   where it was invoked from.
3. Mutation-test the new check against the current tree, one mutation at a time, reverting
   between each: point `controller.py:29` at `meta_prompt/curriculum.prompt.v2.md` and
   require `FAIL activation` naming both paths; remove the call from `static_preflight`,
   then from `simulate`, then from `session_bridge.prepare`, requiring a failure naming the
   function each time; edit one `policy/checks.v1.yaml` owner row to a different version;
   and add an owner row under `meta_prompt/deprecated/` and require it to be **ignored**. A
   check that cannot be made to fail has not been shown to check anything, and one that
   cannot be made to stay quiet has not been shown to be scoped.
4. `python3 -m unittest discover -s tests/runtime -v` — no new failure.
5. `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5` — compare per gate id against the
   baseline captured before any edit; accept no new or worsened result.
6. `python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --test-static` and
   `--test-simulated-all` — same terminal behaviour and coverage as baseline, plus the new
   `prompt` field in the static preflight result.

## Acceptance criteria

- `check_meta_prompt.py` reports 7/7 and its docstring states all seven.
- The activation check fails, with a message naming both paths, when the controller literal
  and `meta_prompt_source.PROMPT_REL` disagree; when the controller's path does not exist;
  when `resolve_prompt` is no longer called from any of the three call sites; and when a
  top-level `meta_prompt/` owner row in `policy/checks.v1.yaml` names a non-active prompt
  version. It stays quiet for an owner row under `meta_prompt/deprecated/`.
- The checker returns 7/7 when invoked from outside the repository root, and never exits on
  an uncaught exception from importing the runtime.
- A missing contract fails as `PRECONDITION-PROMPT-RESOLVE` from `static_preflight`,
  `simulate` and `session_bridge.prepare`, in each case before any `OUTPUT_ROOT` is
  created, rather than as a copy error during input freeze or not at all.
- `static_preflight()` reports the contract's path and SHA-256 alongside the companions'.
- No gate added, no gate weakened, no registry or plan catalogue edited, no prompt text
  changed, phases 4 and 5 unchanged against baseline.

## Stop conditions and result

Stop on: a phase-4/5 gate regression that cannot be repaired inside the files named above;
a discovered requirement to register a gate or edit a plan catalogue (that is the registry
generalisation, and is out of scope); a collision with pre-existing staged user work in
`runtime/controller.py`, `runtime/session_bridge.py`, or `tests/` — the worktree is
currently dirty across all three, so classify hunks before editing and never stage, stash,
reset or restore.

Write `plans/meta_prompt_activation/meta_prompt_activation.result.v1.md` with the baseline,
changed paths, mutation-test evidence, per-gate comparison, and remaining failures. Append
the outcome to `plans/meta_prompt_activation/plans.log.md`.
