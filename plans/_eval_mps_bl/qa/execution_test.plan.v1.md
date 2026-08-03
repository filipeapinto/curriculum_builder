# Meta-Prompt Activation — Execution Test Plan v1

Ordered acceptance procedure for
`plans/meta_prompt_activation/meta_prompt_activation.plan.v1.md`. Run MP-T00 through MP-T07
strictly in order. A later test may not be run to explain an earlier failure.

Evidence root: an external scratch directory outside the repository, referred to as
`EVIDENCE`. Nothing in this procedure writes to the repository except the implementation's
own authorized edits. Temporary engine copies live under `ENGINE/outputs/`, which
`require_internal_output` already constrains.

The worktree is dirty across `runtime/` and `tests/` (staged additions, some with unstaged
modifications). No test may stage, stash, reset, restore or clean.

---

## MP-T00 — Baseline, before any edit

**Command.**
```
git status --porcelain=v1 --untracked-files=all
python3 tests/check_meta_prompt.py
python3 -m unittest discover -s tests/runtime -v
./tests/run_gates.sh 4
./tests/run_gates.sh 5
python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --test-static
python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --test-simulated-all
```

**Pass.** All captured to `EVIDENCE/baseline/` with exit codes and SHA-256 of each output.
`check_meta_prompt.py` must report `EXECUTABLE (6/6)`; if it does not, the pre-existing
failure is recorded and carried forward as the comparison point, and the implementation may
not claim to have fixed it.

**Why first.** Every later comparison is against this. Phase 4 and 5 gate results are
recorded per gate id, not as a single verdict, because "no new or worsened result" cannot be
evaluated from a rolled-up pass count.

---

## MP-T01 — The defect is real and currently unguarded

Run before any edit, and revert every mutation immediately.

**Procedure.**
1. Point `runtime/controller.py:29` at `meta_prompt/curriculum.prompt.v2.md`.
2. `python3 tests/check_meta_prompt.py` → must still report `6/6 EXECUTABLE`.
3. `./tests/run_gates.sh 4` and `5` → must match MP-T00 exactly.
4. `python3 runtime/run_curriculum.py ... --test-simulated-all` → must still reach
   `ACCEPTED`.
5. Revert; confirm `git diff` on `runtime/controller.py` is empty against MP-T00.

**Pass.** Steps 2-4 all green with the controller pointing at a file that does not exist.

**Why.** This is the plan's premise, executed rather than asserted. If any existing check
already fails here, the plan's scope is wrong and implementation stops for re-planning
rather than adding a redundant check.

---

## MP-T02 — `resolve_prompt` behaviour at the three call sites

Run after the `runtime/` edits and before touching `tests/check_meta_prompt.py`.

**Procedure.** Build a temporary engine under `ENGINE/outputs/mp_activation_tmp/` — a copy
of the engine's `policy/`, `schemas/`, `curricula/`, `meta_prompt/assets/` and `runtime/`
with `meta_prompt/curriculum.prompt.v1.md` absent. Then:

| # | Call | Expect |
| - | ---- | ------ |
| 1 | `CurriculumRuntime(tmp)` | constructs, raises nothing |
| 2 | `CurriculumRuntime(tmp).resolve_prompt()` | `RuntimeFailure`, `failure_id == "PRECONDITION-PROMPT-RESOLVE"` |
| 3 | `.static_preflight(curriculum)` | same failure id |
| 4 | `.simulate(curriculum, out)` | same failure id, **and `out` does not exist afterwards** |
| 5 | `session_bridge.prepare(tmp, ...)` | same failure id, and no `OUTPUT_ROOT` created |
| 6 | `CurriculumRuntime().static_preflight(...)` on the real engine | `prompt.sha256` equals `sha256_file(meta_prompt/curriculum.prompt.v1.md)` |

**Pass.** All six. Row 1 is not incidental: a constructor that raises would break existing
`tests/runtime/` cases and the activation check's own import.

**Fail action.** If row 4 leaves an output root behind, the call is in the wrong position in
`simulate`; move it above `prepare_output` rather than deleting the created directory.

**Cleanup.** Remove `ENGINE/outputs/mp_activation_tmp/` and confirm `git status` matches
MP-T00 plus only the authorized source edits.

---

## MP-T03 — The activation check passes on the honest tree

**Command.** `python3 tests/check_meta_prompt.py`

**Pass.** `PASS activation` and `meta prompt: EXECUTABLE (7/7 checks pass)`. The other six
parts still `PASS` with unchanged text.

**Also required.** The module docstring lists seven parts, its "what 6/6 means" paragraph
now reads 7/7, and the docstring states that this part imports the runtime and that its
call-site assertion proves the call is written, not that it executes. A seventh check the
docstring does not mention is the same silent divergence this plan exists to close.

---

## MP-T04 — Invocation independence

**Command.** From a directory outside the repository:
```
python3 /abs/path/to/curriculum_builder/tests/check_meta_prompt.py
```

**Pass.** `7/7 EXECUTABLE`, identical output to MP-T03.

**Why.** `tests/check_meta_prompt.py:77` only puts `tests/` on `sys.path`; the runtime's
package-relative imports need the repository root. Without the added insert this reports the
contract broken because of the caller's working directory.

---

## MP-T05 — Mutation tests: the check can fail, and knows when not to

One mutation at a time, reverted before the next. After the last revert, `git diff` must be
empty against the MP-T03 state.

| Mutation | Required output |
| -------- | --------------- |
| `controller.py:29` → `curriculum.prompt.v2.md` | `FAIL activation`, message naming both the controller's path and the composed contract's |
| `controller.py:29` → an existing but different real file under `meta_prompt/assets/` | `FAIL activation` on the equality assertion, not on existence |
| remove the `resolve_prompt` call from `static_preflight` | `FAIL activation` naming `static_preflight` |
| remove it from `simulate` | `FAIL activation` naming `simulate` |
| remove it from `session_bridge.prepare` | `FAIL activation` naming `prepare` |
| edit one `policy/checks.v1.yaml` `owner:` row to `meta_prompt/curriculum.prompt.v9.md` | `FAIL activation` naming the row |
| add an `owner:` row `meta_prompt/deprecated/curriculum.prompt.v1.md` | **`PASS activation`** — retained history is not a stale activation |
| make `runtime/controller.py` unimportable (syntax error) | `FAIL activation` with a one-line message; **no traceback, and the checker still returns a verdict for the other six parts** |

**Pass.** Every row. The last two are the ones that decide whether this check is scoped and
survivable; a check that fires on retained history or dies on an unrelated import error will
be weakened the first time it fires.

---

## MP-T06 — No regression

**Command.** Re-run every command from MP-T00 except `git status`.

**Pass.**
- `unittest discover` — the three new `PRECONDITION-PROMPT-RESOLVE` tests and the preflight
  hash test pass; no previously passing test fails.
- Phase 4 and phase 5, compared **per gate id** against `EVIDENCE/baseline/`: no new or
  worsened result. Particular attention to `FR-P0-REGISTRY` (no gate added, so the registry
  must be untouched) and `FR-P4-CHECK-MAPPING` (no new check id declared, so the mapping
  must be unchanged).
- `--test-static` returns the same terminal behaviour plus the new `prompt` field.
- `--test-simulated-all` returns the same coverage, unit ids and terminal state.

**Fail action.** A gate regression is repaired inside the four files this plan authorizes.
If it cannot be, stop — do not weaken a gate, edit `tests/gates/registry.py`, or touch a
plan catalogue.

---

## MP-T07 — Delta audit

**Command.** `git status --porcelain=v1 --untracked-files=all` and `git diff` against
MP-T00.

**Pass.** Changed paths are exactly:
`runtime/controller.py`, `runtime/session_bridge.py`, `tests/check_meta_prompt.py`,
`tests/runtime/test_controller.py`, plus this plan's own artifacts under
`plans/meta_prompt_activation/`.

No change to `meta_prompt/`, `policy/`, `schemas/`, `tests/gates/`, `tests/meta_prompt_source.py`,
or any other plan directory. Pre-existing staged and unstaged hunks in the touched files are
byte-identical to MP-T00 except where an authorized edit sits. No leftover directory under
`ENGINE/outputs/`.

**Why last.** MP-T05 mutates four files repeatedly. A clean final delta is the only proof
that every mutation was reverted rather than left behind under a passing test.
