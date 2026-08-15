# Rebrand Product Naming to "Curriculum Factory" — Prompt v1

Work in `/Users/filipepinto/Projects/curriculum_builder`.

Run `prompts/rebrand_system/assets/find_old_name_references.sh` first. It
regenerates:

- `assets/targets.v1.txt` — every live file with the exact phrase
  "curriculum builder" or "curriculum pipeline" (repo-wide, minus historical
  and code-identifier exclusions baked into the script).
- `assets/readme_targets.v1.txt` — `readme.md`'s self-description line plus
  its backtick path references, each checked for existence with an
  auto-discovered live replacement where one exists.
- `assets/repo_wide_context.v1.txt` — hyphenated/code-identifier hits
  (e.g. the `curriculum-builder/1.0` User-Agent string). Informational only,
  never edited.

Then run `prompts/rebrand_system/assets/run_rebrand_with_log.py`. This is
the single entrypoint — it runs `apply_rebrand.sh` (case-preserving phrase
substitution `curriculum builder` / `curriculum pipeline` → `Curriculum
Factory` in every file `targets.v1.txt` names, plus the exact known fix to
`readme.md`'s three broken path references), then runs all five TESTS
itself, and logs every step as a schema-conformant record via
`runtime.logger.ExecutionLogger` — the same logger the curriculum runtime
uses — validated against `schemas/execution_log.schema.v2.json`, written to
`prompts/rebrand_system/execution/execution_log.jsonl`. It exits 0 only if
every step completed and the log has zero unclosed starts.

Do not hand-edit any file yourself. Do not grep or search for anything
yourself, and do not hand-write log entries — the scripts already do all of
it. If a script's output looks wrong, stop and report `STALE_SCRIPT_OUTPUT`;
do not improvise a fix by hand.

## GOAL

After running both scripts: every live, non-historical reference to
"curriculum builder" or "curriculum pipeline" as the product's own name
reads "Curriculum Factory" instead. The repo/directory name
`curriculum_builder`, the git remote, and every code identifier (e.g. the
`User-Agent` string in `runtime/langgraph_factory/egress.py`) are untouched.
`readme.md` has zero orphan path references. No file outside what the
scripts touched is modified.

## TESTS

`run_rebrand_with_log.py` runs and logs all five as ACT/EXEC records:

1. Only files named by `targets.v1.txt` or `readme.md` (plus files under
   `assets/`/`execution/`) changed — compared against a `git status`
   baseline taken before step 1, so pre-existing unrelated dirty state is
   not mistaken for a stray edit.
2. Re-running the finder afterward finds zero remaining live targets
   (`targets.v1.txt` has zero non-comment lines).
3. `readme.md` contains "Curriculum Factory", no longer contains the old
   self-description string, and every backtick path resolves (directory-only
   mentions like `` `deprecated/` `` are not treated as paths).
4. `runtime/langgraph_factory/egress.py` and its test have no diff (code
   identifier untouched).
5. `git remote -v` and `readme.md`'s first line still say
   `curriculum_builder` (repo identity untouched).

Additionally, the script's own exit code requires every ACT it started to be
closed (`audit()["unclosed_starts"] == []`) and every record to validate
against `schemas/execution_log.schema.v2.json`.

## LOOP

1. Run `./prompts/rebrand_system/assets/find_old_name_references.sh`.
2. Run `python3 ./prompts/rebrand_system/assets/run_rebrand_with_log.py`.
   It applies the rebrand, runs all five TESTS, and writes
   `execution/execution_log.jsonl`.
3. If it exits non-zero, read `execution_log.jsonl` for the `EXEC` record(s)
   that explain what failed. Fix only within `readme.md` or the files named
   in `targets.v1.txt`, by re-running step 2 (both scripts are idempotent).
   Do not hand-edit prose and do not touch any file the scripts did not
   name.
4. Repeat until `run_rebrand_with_log.py` exits 0.
5. Stop. Do not commit.

Completion = `run_rebrand_with_log.py` exits 0, meaning every TEST passed
and `execution/execution_log.jsonl` validates against
`schemas/execution_log.schema.v2.json` with zero unclosed starts.
