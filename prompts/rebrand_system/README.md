# rebrand_system

One-off GOAL/TEST/LOOP prompt that replaces every live reference to
"Curriculum Builder" and "Curriculum Pipeline" with "Curriculum Factory".
Every step — finding references, applying the rebrand, testing the result,
and logging — is done by code, not by the agent's judgment.

## Files

- `rebrand_curriculum_factory.prompt.v1.md` — the prompt. Run this with
  Claude Code.
- `assets/find_old_name_references.sh` — generates the exact target lists.
  Re-run to regenerate; never hand-edit its outputs.
- `assets/apply_rebrand.sh` — applies the rebrand mechanically: case-
  preserving phrase substitution in every file `targets.v1.txt` names, plus
  the known fix to `readme.md`'s broken path references. Idempotent.
- `assets/run_rebrand_with_log.py` — the entrypoint. Runs both scripts
  above, runs all five acceptance tests, and logs every step through
  `runtime.logger.ExecutionLogger` (the same logger the curriculum runtime
  uses), validated against `schemas/execution_log.schema.v2.json`. Exits 0
  only if every test passed and the log has zero unclosed starts.
- `assets/targets.v1.txt` — generated. Every live file containing
  "curriculum builder" or "curriculum pipeline" as prose.
- `assets/readme_targets.v1.txt` — generated. `readme.md`'s self-description
  line and its backtick path references, each checked for existence with an
  auto-discovered live replacement where one exists.
- `assets/repo_wide_context.v1.txt` — generated. Hyphenated/code-identifier
  hits (e.g. the `curriculum-builder/1.0` User-Agent string). Informational
  only, never edited.
- `execution/execution_log.jsonl` — the standard-schema run log: one
  `act`/`exec` record per step, schema-conformant, append-only.

## Usage

```sh
./prompts/rebrand_system/assets/find_old_name_references.sh
python3 ./prompts/rebrand_system/assets/run_rebrand_with_log.py
```

or just run `rebrand_curriculum_factory.prompt.v1.md`, which does the same
two calls and stops on the script's exit code.
