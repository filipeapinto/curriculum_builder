# GOAL

Implement `plans/meta_prompt_activation/meta_prompt_activation.plan.v1.md` exactly, using
`plans/meta_prompt_activation/qa/execution_test.plan.v1.md` as the acceptance procedure.

`runtime/controller.py:29` hardcodes the active meta-prompt path and nothing checks it. It
is one of four statements of that path; the other three already agree with each other by
construction or by gate. Close the hole so the contract the runtime hands to a run cannot
silently differ from the contract `tests/check_meta_prompt.py` certifies.

Change exactly four files:

- `runtime/controller.py` — add `resolve_prompt()`, mirroring `resolve_companions()`:
  return `self.prompt` if it `is_file()`, else raise
  `RuntimeFailure("PRECONDITION-PROMPT-RESOLVE", f"missing active contract: {self.prompt}")`.
  Call it first in `static_preflight()` and at the top of `simulate()` **before**
  `prepare_output`. Add `"prompt": {"path": ..., "sha256": ...}` to the `static_preflight`
  result. Leave `__init__` total — it must not raise on a missing prompt.
- `runtime/session_bridge.py` — call `runtime.resolve_prompt()` in `prepare()` beside the
  existing `runtime.resolve_companions()` call, before `require_internal_output` and
  `output.mkdir`. Change nothing else.
- `tests/check_meta_prompt.py` — add a seventh check, `activation`, described below.
- `tests/runtime/test_controller.py` — stdlib `unittest`, matching the existing style
  (`self.assertRaises(RuntimeFailure)` then `assertEqual(caught.exception.failure_id, ...)`).

The `activation` check asserts, in order, reporting each failure as a problem string:

1. `runtime.controller` imports and `CurriculumRuntime()` constructs. Add
   `sys.path.insert(0, str(REPO))` beside the existing `tests/` insert at line 77 — the
   runtime uses package-relative imports and today resolves only by cwd accident. Catch
   every exception and report it as one `activation:` line; never let a traceback escape,
   and never let this part stop the other six from reporting.
2. `resolve_prompt()` returns without raising; a `RuntimeFailure` is reported with its
   `failure_id`.
3. `runtime.prompt == source.PROMPT` as resolved paths, printing both on mismatch.
4. `resolve_prompt` is called from `static_preflight`, `simulate` and
   `session_bridge.prepare` — read with `inspect.getsource` of the three **function
   objects**, not by scanning file text, requiring the literal call token in each, and
   naming the offending function on failure.
5. Every `policy/checks.v1.yaml` `owner:` value of the form
   `meta_prompt/<name>.prompt.v<n>.md` **with no further path separator** equals
   `source.PROMPT_REL`. An owner row under `meta_prompt/deprecated/` is out of scope and
   must not fire.

Update the module docstring: seven numbered parts, "6/6" becomes "7/7", and state plainly
that this part imports the runtime and that item 4 proves the call is *written*, not that it
*executes*.

Do not add a gate. Do not edit `tests/gates/registry.py`, any plan catalogue,
`policy/checks.v1.yaml`, `tests/meta_prompt_source.py`, or any file under `meta_prompt/`.
Do not declare `PRECONDITION-PROMPT-RESOLVE` in `policy/checks.v1.yaml`: `FR-P4-CHECK-MAPPING`
would then require a `verified_by` gate id, and `FR-P0-REGISTRY` would require that gate in
a finished plan's §8 catalogue. Eleven runtime precondition ids are already undeclared; this
is the twelfth, stated openly in the plan.

The worktree is dirty across `runtime/` and `tests/`. Never stage, stash, reset, restore,
clean, or overwrite pre-existing user work. Classify hunks before editing; an overlapping
hunk that cannot be separated is a stop.

# TEST

Run MP-T00 through MP-T07 from the execution test plan strictly in order. Do not skip ahead,
and do not run a later test to explain an earlier failure.

1. **MP-T00** — capture the full baseline to an evidence directory outside the repository:
   `git status`, `check_meta_prompt.py`, `unittest discover -s tests/runtime`,
   `run_gates.sh 4`, `run_gates.sh 5`, `--test-static`, `--test-simulated-all`, each with
   exit code and output hash. Phase results recorded **per gate id**.
2. **MP-T01** — before any edit, prove the defect: point `controller.py:29` at a
   nonexistent v2, confirm the checker still reports 6/6, both gate phases match baseline,
   and `--test-simulated-all` still reaches `ACCEPTED`. Revert and confirm a clean diff. If
   anything already fails here, stop and re-plan; the scope would be wrong.
3. **MP-T02** — after the `runtime/` edits only, against a temporary engine under
   `ENGINE/outputs/` with the prompt absent: constructor does not raise; `resolve_prompt`,
   `static_preflight`, `simulate` and `session_bridge.prepare` each raise
   `PRECONDITION-PROMPT-RESOLVE`; `simulate` leaves **no output root behind**; and on the
   real engine `static_preflight` reports the prompt's true SHA-256.
4. **MP-T03** — `7/7 EXECUTABLE`, other six parts unchanged, docstring updated.
5. **MP-T04** — same 7/7 when invoked by absolute path from outside the repository.
6. **MP-T05** — the eight mutations in the test plan's table, one at a time, each reverted:
   six must produce a specific `FAIL activation` message; the `meta_prompt/deprecated/`
   owner row must **PASS**; an unimportable controller must yield one line and still let the
   other six parts report.
7. **MP-T06** — re-run every MP-T00 command. No new or worsened result per gate id.
   `FR-P0-REGISTRY` and `FR-P4-CHECK-MAPPING` in particular must be unchanged, because
   nothing was registered or declared.
8. **MP-T07** — final delta is exactly the four source files plus this plan's artifacts;
   pre-existing hunks byte-identical to MP-T00; no leftover under `ENGINE/outputs/`.

MP-T01 and MP-T05 are not optional. A check that has never been observed to fail has not
been shown to check anything, and a check that has never been observed to stay quiet has not
been shown to be scoped.

# LOOP

Execute each test in order. On failure, record the test id, command, exit code, output hash
and the narrow root cause; fix only the in-scope file that caused it; re-run that test and
every later test whose evidence could have changed.

Specific loops:

- MP-T02 row 4 leaves an output root → the call sits below `prepare_output` in `simulate`;
  move it above. Do not delete the directory and re-run.
- MP-T04 fails → the `REPO` `sys.path` insert is missing or ordered after the import.
- MP-T05 deprecated-row mutation fires → the owner pattern is crossing `/`; anchor it to the
  top level of `meta_prompt/`.
- MP-T06 gate regression → repair inside the four authorized files. If it cannot be
  repaired there, stop.

Never respond to a failure by weakening or deleting a check, adding a gate, editing
`tests/gates/registry.py` or a plan catalogue, relaxing the mutation table, declaring the new
check id to satisfy a mapping gate, or leaving an MP-T05 mutation in place. Never resolve a
dirty-worktree collision with `git checkout`, `restore`, `reset`, `stash`, or `clean`.

When every test passes, write
`plans/meta_prompt_activation/meta_prompt_activation.result.v1.md` with the MP-T00 baseline,
changed paths, per-test commands and exit codes, the full MP-T05 mutation table with the
observed message for each row, the per-gate comparison, and any remaining failure. Append —
never rewrite — the outcome to `plans/meta_prompt_activation/plans.log.md`.

Claim completion only when MP-T00 through MP-T07 have all passed, including every row of the
MP-T05 table and a clean MP-T07 delta.
