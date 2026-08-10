# Migrate External Run Evidence Into ENGINE/outputs — Prompt v2

## Changes from v1

v1's §3 step 6 scope check (`git status --short | grep -vE '^\?\? outputs/|^ M
...v6\.md$'`) was verified against the actual repository state before execution and
found broken: nothing in this repository is committed yet for this feature line, so
`git status --short` already shows far more dirty/untracked paths than v1's tolerance
list named, and — critically — `implement_curriculum_runtime.prompt.v6.md` itself is
currently **untracked** (`??`), not tracked-and-modified (`M`). v1's pattern only
excluded the `M` form, so editing v6.md the way §2 requires would still show as
`?? plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md`, never
match the exclude, and fail `SCOPE_OK` on every attempt — including a correct one —
burning all five retries into a false `MIGRATION_INCOMPLETE`.

Everything else below is unchanged from v1. Only §3 step 6 (and its explanatory
parenthetical) differs.

## Context, for a session with no memory of how this arose

`runtime/io.py` used to require every `--output-root` to resolve **outside** `ENGINE`
(`require_external_output`), which meant no run of this repository could complete
without an operator provisioning a durable external sibling directory. That function
was replaced by `require_internal_output`, which requires the opposite: every
`--output-root` must now resolve **beneath `ENGINE/outputs/`**, and a path outside it
raises `BoundaryError` before any artifact or model call.
`meta_prompt/curriculum.prompt.v1.md`'s Mission section and `.gitignore` were already
updated to match (`ENGINE/outputs/` is gitignored, so run evidence there is never
committed). `ENGINE` itself is not a literal directory in this repository — it is the
runtime's name for the repository root (`runtime/controller.py`'s `self.engine`
defaults to `Path(__file__).resolve().parents[1]`), so `ENGINE/outputs/` on disk is
just this repo's top-level `outputs/`.

Two things were left behind by that fix and are this prompt's job:

1. One real run's evidence, `runtime_task_v6`, is still sitting at the old external
   location, `parent(ENGINE)/curriculum_builder_runs/runtime_task_v6` (~11MB). It needs
   to move to `ENGINE/outputs/runtime_task_v6`.
2. `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md` — the prompt
   that produced that run — still states the **old, now-false** rule in five places: it
   defines `EVIDENCE_PARENT` as a sibling outside `ENGINE`, explicitly forbids using the
   repository's `outputs/` directory, and instructs the sandbox to authorize an
   *additional* writable root for it. Left uncorrected, the next person who runs that
   prompt gets an instruction that contradicts the actual runtime and either fails or
   silently drifts back to the old convention.

`implement_curriculum_runtime.prompt.v4.md` and `v5.md` contain the identical stale
block. **Do not touch them.** They are superseded drafts of the same iterative prompt;
this repository's convention throughout is that a superseded version is retained
byte-unchanged as history, never edited to match a later fix. Only `v6`, the current
version, is corrected here.

## Goal

1. Move `runtime_task_v6`'s evidence into `ENGINE/outputs/`, byte-identical, with the
   old location gone.
2. Correct `implement_curriculum_runtime.prompt.v6.md` so it states the rule
   `runtime/io.py` actually enforces.
3. Prove neither change broke anything already passing.

## Authorized paths — nothing else may be touched

- `parent(ENGINE)/curriculum_builder_runs/` (read, then delete once step 1's proof
  passes)
- `ENGINE/outputs/` (write)
- `plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md` (edit, per
  the exact blocks in §2 below — no other line in this file)

Do not touch `docs/how_it_works.md`, `docs/how_it_works.png`, `docs/how_it_works.typ`,
`docs/infographic.prompt.v1.md`, `readme.md`, or anything under `docs/`, `plans/`
(other than the one file named above), or `runtime/`/`tests/` — these either already
carry unrelated in-progress changes or are out of this task's scope. If `git status
--short` shows any of them newly modified when this prompt ends, that is a scope
failure, not a side effect to report and keep.

## 1. Move the run evidence

```sh
SRC=$(cd .. && pwd)/curriculum_builder_runs/runtime_task_v6
DST=outputs/runtime_task_v6
```

`runtime_task_v6` is a **terminal** run: three attempts recorded `"terminal_state":
"FAILED"` (preserved as evidence) and one recorded `"terminal_state":
"ACCEPTED_BY_RUNTIME_AS_DRAFT"`, per its own `final_audit.json`. Nothing will ever
call `--resume` on it again, so this is a plain relocation, never a content edit —
`mv`, not `cp` followed by hand-editing.

Steps:
1. Confirm `$SRC` exists and `$DST` does not.
2. `mkdir -p outputs` (idempotent; it may already exist).
3. `cp -R "$SRC" "$DST"` (copy, not move yet — the source stays until verified).
4. Verify byte-for-byte parity: same file count, and every file's sha256 identical
   between `$SRC` and `$DST` (e.g. `diff -r "$SRC" "$DST"` exits 0).
5. Only after parity is confirmed: `rm -rf "$SRC"`.
6. If `parent(ENGINE)/curriculum_builder_runs/` is now empty, remove it too.

Several JSON records inside the run (`final_audit.json`, `task_ledger.json`,
checkpoints, execution logs) embed the *old* absolute path as a string field (e.g.
`"path": ".../curriculum_builder_runs/runtime_task_v6/attempt_v1"`). **Do not edit
these strings.** They are historical audit trail, not a live pointer anything
re-resolves — rewriting them would be editing evidence after the fact, which this
repository's whole discipline (`§Acceptance`, `§Grounding` equivalents) treats as
worse than leaving a stale field. Leave them as-is; note the staleness in this task's
own report, don't silently fix it into the record.

## 2. Correct implement_curriculum_runtime.prompt.v6.md

Five edits, all in that one file, each exact:

**a. Line 31** — `outside \`ENGINE\`` → beneath `ENGINE/outputs/`:
```
- old: 3. Start L01 from a new, empty output root outside `ENGINE` and preserve the attempt as
- new: 3. Start L01 from a new, empty output root beneath `ENGINE/outputs/` and preserve the attempt as
```

**b. Line 36** — same substitution:
```
- old:    permit another attempt, select a new empty external output root and rerun L01 from
- new:    permit another attempt, select a new empty output root beneath `ENGINE/outputs/` and rerun L01 from
```

**c. Lines 66-67** — `EVIDENCE_PARENT` derivation:
```
- old: EVIDENCE_PARENT      = derive as parent(ENGINE)/curriculum_builder_runs
- old: TASK_ROOT            = EVIDENCE_PARENT/runtime_task_v6
- new: EVIDENCE_PARENT      = ENGINE/outputs
- new: TASK_ROOT            = EVIDENCE_PARENT/runtime_task_v6
```
(`TASK_ROOT`'s own line is unchanged — only what `EVIDENCE_PARENT` resolves to moves.)

**d. Lines 73-82** — the durability/sandbox paragraph, replace the full two paragraphs:
```
- old:
Canonicalize `ENGINE`, `EVIDENCE_PARENT`, and each proposed `OUTPUT_ROOT` before writing.
Require `EVIDENCE_PARENT` to be a durable, writable sibling outside `ENGINE`. Never use
`/tmp`, `/private/tmp`, `$TMPDIR`, a cache directory, or the repository's `outputs/`
directory for task evidence. If durable external write access cannot be established,
return `DURABLE_EVIDENCE_ROOT_UNAVAILABLE` before repository edits or live calls; do not
fall back to volatile storage.

The invoking sandbox must authorize `EVIDENCE_PARENT` as an additional writable root
(for the Codex CLI, use its scoped `--add-dir` mechanism). This grants only the durable
evidence sibling; it does not widen writes elsewhere.

- new:
Canonicalize `ENGINE` and each proposed `OUTPUT_ROOT` before writing. `EVIDENCE_PARENT`
is fixed at `ENGINE/outputs` — `runtime/io.py`'s `require_internal_output` refuses any
output root that does not resolve beneath it, raising `BoundaryError` before any
artifact or model call. Never use `/tmp`, `/private/tmp`, `$TMPDIR`, or a cache
directory for task evidence, and never pass an output root outside `ENGINE/outputs/`.

`ENGINE/outputs/` is gitignored, so run evidence needs no separate durable root and no
sandbox `--add-dir` grant: it is already inside whatever root the sandbox authorizes
for this repository. If `ENGINE/outputs/` itself cannot be created or written to (for
example, a read-only checkout), return `DURABLE_EVIDENCE_ROOT_UNAVAILABLE` before
repository edits or live calls; do not fall back to volatile storage.
```

**e. Line 84** — the boundary the outer loop enforces between attempts:
```
- old: Reject any output root equal to or nested beneath `ENGINE`. Before each outer-loop attempt, the
- new: Reject any output root that does not resolve beneath `ENGINE/outputs/`. Before each outer-loop attempt, the
```

Leave `DURABLE_EVIDENCE_ROOT_UNAVAILABLE`'s outcome-enum entry (around lines 508-525)
as a named status — it is now the rarer case of `ENGINE/outputs/` itself being
unwritable rather than an external sibling being unwritable, and edit 2d's new
paragraph already states that condition; no further line there needs to change.

## 3. Test — the loop's success condition

All of these must pass, in this order, before the loop may stop:

```sh
# 1. Move proof: old location gone, new location present, nothing else in outputs/ disturbed
test ! -e "$(cd .. && pwd)/curriculum_builder_runs/runtime_task_v6" \
  && test -d outputs/runtime_task_v6 \
  && echo "MOVE_OK"

# 2. v6 prompt no longer states the old rule anywhere
! grep -n "curriculum_builder_runs\|outside \`ENGINE\`\|external output root\|additional writable root" \
  plans/simplification/prompt/implement_curriculum_runtime.prompt.v6.md \
  && echo "V6_TEXT_OK"

# 3. v4 and v5 are untouched — confirms the "don't touch superseded versions" rule held
git diff --stat -- plans/simplification/prompt/implement_curriculum_runtime.prompt.v4.md \
                   plans/simplification/prompt/implement_curriculum_runtime.prompt.v5.md \
  | (! grep .) && echo "V4_V5_UNTOUCHED"

# 4. Static contract check still green
python3 tests/check_meta_prompt.py

# 5. Full runtime unit-test suite still green (run via the package path — plain
#    `pytest tests/runtime/test_X.py` or `unittest discover -s tests` both collide
#    with a pre-existing, unrelated sys.path issue where tests/runtime/'s own
#    __init__.py shadows the top-level runtime/ package; this invocation avoids it)
python3 -m unittest discover -s tests/runtime -v

# 6. Scope check: nothing outside the authorized paths changed. Nothing in this
#    repository is committed yet for this feature line, so git status --short is
#    already dirty with unrelated pre-existing work; the pattern below excludes
#    exactly that pre-existing state plus the two paths this task is authorized to
#    change (outputs/runtime_task_v6, which is gitignored and so already invisible
#    to git status, and implement_curriculum_runtime.prompt.v6.md, which is
#    currently UNTRACKED — it will show as "??", never "M" — so the exclude below
#    matches "??", not "M").
git status --short | grep -vE \
  '^ M \.gitignore$|^ M docs/how_it_works\.md$|^ M docs/how_it_works\.png$|^ M docs/how_it_works\.typ$|^ M docs/infographic\.prompt\.v1\.md$|^ M meta_prompt/curriculum\.prompt\.v1\.md$|^ M readme\.md$|^\?\? docs/deprecated/$|^\?\? docs/png/$|^\?\? docs/prompts/$|^\?\? plans/contract_v2/$|^\?\? plans/simplification/prompt/implement_curriculum_runtime\.prompt\.v[1-5]\.md$|^\?\? plans/simplification/prompt/implement_curriculum_runtime\.prompt\.v6\.md$|^\?\? plans/simplification/prompt/migrate_external_run_evidence\.prompt\.v[12]\.md$|^\?\? plans/skill_conversion/$|^\?\? runtime/$|^\?\? tests/runtime/$|^\?\? outputs/' \
  | (! grep .) && echo "SCOPE_OK"
```

If this prompt is ever re-run after some of the above pre-existing dirty paths have
been committed or removed, re-derive the exclude list from a fresh `git status
--short` taken before §1 rather than trusting this literal list — its job is to
tolerate whatever was already dirty coming in, not to hardcode these exact files
forever.

## 4. The loop

1. Perform §1 (move) and §2 (five edits), in that order.
2. Run every command in §3.
3. If every one prints its `_OK` marker (or, for 4 and 5, exits 0 with no failures),
   stop. Report `ACCEPTED`, listing the old and new paths and the two changed files.
4. If any command fails: diagnose from its actual output — do not guess. Common
   failure modes and their fix are already fully specified above (a missed edit
   site, a typo in the replacement text, a file this task is not authorized to
   touch having changed). Fix precisely that, then restart from step 2 — the full
   §3 battery, not just the check that failed, since an edit made to satisfy one
   check must not silently break another already passing.
5. Bounded retry: five full passes through step 4. If the fifth still fails, stop
   and report `MIGRATION_INCOMPLETE` with the exact failing command, its output,
   and the state left on disk. Never force a pass by weakening a §3 check, and
   never leave the repository with `runtime_task_v6` duplicated in both locations
   or with `implement_curriculum_runtime.prompt.v6.md` half-edited — either
   complete both §1 and §2 together or roll back to the state this prompt started
   from and report the bounded failure honestly.
