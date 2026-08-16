# Refactor repository identity and layout — Prompt v2

Work from the Git repository root. This is a repository refactor, not merely a
product-name search-and-replace.

## Intent

Make the repository consistently represent **Curriculum Factory** at all four
identity layers:

1. Human-facing product name: `Curriculum Factory`.
2. Repository/checkout slug: use one approved filesystem- and Git-safe slug
   consistently (the default proposal is `curriculum_factory`).
3. Python source layout: importable production code belongs below `src/`.
   Prefer the standard `src/<python_package>/...` form; do not assume that
   changing `runtime/` to `src/` without a package directory is sufficient.
4. Internal identifiers and paths: package imports, CLI entry points, schema
   identifiers, User-Agent values, tests, docs, scripts, and configuration must
   intentionally use either the display name, repo slug, or Python package name
   according to their role.

Also classify folders whose purpose or lifecycle is unclear, including
`outputs/`, and identify any other names or placements that conflict with the
repository's own conventions or normal Python project practice.

## Safety and decisions

- Read the complete repository guidance and inspect the dirty worktree first.
  Preserve all unrelated changes.
- Run `prompts/refactor_repo/assets/audit_repository_layout.sh` before proposing
  or making moves.
- Do not infer that an old-looking folder is obsolete from its name. Prove its
  producers, consumers, Git tracking/ignore state, and documentary references.
- Do not delete historical or generated material during this refactor. Classify
  it as live source, generated runtime data, cache/scratch, test artifact,
  retained evidence, or deprecated history; then keep, move, archive, or ignore
  it according to that classification.
- Renaming the remote GitHub repository, changing its URL, or renaming the local
  checkout requires explicit user authorization immediately before that external
  or parent-directory operation. Prepare and validate the in-repository changes
  independently so those operations can be performed last.
- Use `git mv` for tracked moves. Never hide broken references with compatibility
  shims unless a shim is an explicit, temporary migration decision with a removal
  condition.
- Do not commit unless asked.

## Required discovery report

Before implementation, write a concise migration inventory that records:

- the current and proposed display name, repo slug, checkout directory, Python
  distribution name (if packaging exists), and import package name;
- every top-level directory, its owner/reader, whether it is tracked or ignored,
  and its lifecycle classification;
- all production imports and executable entry points rooted in `runtime`;
- all code deriving the repository root from `__file__` (a move below `src/`
  changes parent depth and can silently redirect policy/schema/output paths);
- references to `runtime/`, `outputs/`, `curriculum_builder`, hyphenated variants,
  old product phrases, and absolute checkout paths;
- packaging/build configuration that exists and what is missing for a reliable
  `src` layout; and
- an explicit disposition for every questionable directory. `UNKNOWN` is an
  acceptable interim classification only when accompanied by the evidence still
  needed.

The current repository gives `outputs/` a live architectural role: `.gitignore`
marks it as generated run output and `runtime/io.py` constrains `--output-root`
below it. Retain that top-level runtime boundary, but do not use it as permanent
fixture or evidence storage. The intended end state is an empty, ignored
`outputs/` between runs, optionally represented in Git by only `.gitkeep` and a
short README explaining that its children are disposable generated artifacts.

Classify and migrate the existing children as follows, rechecking references at
execution time:

- `arduino_kit_run_v2` is durable test and research evidence. Move only the
  required, immutable material to a purpose-named tracked location such as
  `tests/fixtures/runs/arduino_kit_run_v2/`; update tests, skills, issues,
  research, and governance references. Minimize the fixture where consumers do
  not need the entire run, but preserve evidence cited by active findings.
- `run27` is referenced by transport tests and research. Determine whether each
  consumer needs existing bytes, a smaller checked-in fixture, or a run-local
  directory created by the test. Prefer generated test scratch data where exact
  historical contents are not the subject of the test.
- `arduino_kit_run_v1` has weak historical/research use. Preserve only cited
  evidence in an archive or fixture location if the citation remains valuable.
- `arduino_kit_plan25_l01_20260811`,
  `remove-time-limits-v2-acceptance`, and `runtime_task_v6` had no live
  non-historical consumers during the initial audit. Treat them as removal
  candidates, not proven-safe deletions; re-run the dependency scan and confirm
  they are reproducible or unneeded before removing them.

No durable test, research, audit, or issue artifact may depend on ignored local
state after the migration. A fresh clone must either contain the required
fixture/evidence or be able to generate it through a documented command.

## Implementation requirements

After the inventory is reviewable and no material naming decision is unresolved:

1. Define one identity map with separate values for display name, repo slug,
   distribution name, import package, and User-Agent. Apply each value only in
   the contexts it owns.
2. Establish a conventional Python source layout. The default target is
   `src/curriculum_factory/` for the code currently under `runtime/`, but verify
   whether preserving `runtime` as the import package is a compatibility
   requirement before choosing. Add the minimal packaging/test configuration
   required to make imports work without ad-hoc `sys.path` mutation.
3. Update imports, module execution commands, CLI/script paths, `__file__`-based
   root discovery, mocks, fixtures, policy references, documentation, and tests
   atomically with the source move.
4. Update human-facing branding and machine identifiers using the identity map.
   Schema `$id` values and network identifiers are API-like values: assess
   compatibility before changing them and document intentional exceptions.
5. Normalize other directories only when the inventory proves a better name or
   placement. Prefer lifecycle-based names (`archive`, `fixtures`, `generated`,
   `reports`) only when they accurately describe ownership and retention.
6. Migrate durable material out of `outputs/`, update all consumers, then remove
   obsolete run children. Keep the `outputs/` boundary and its ignore rule. Do
   not retain duplicate fixture and output copies after equivalence and consumer
   tests are proven.
7. Update the README so it describes the real current system, source layout,
   output lifecycle, installation/test commands, and any remaining migration
   step for the local checkout or remote repository.

## Verification

The refactor is complete only when all applicable checks pass:

1. The full existing test suite and repository gate harness pass from a clean
   environment using the documented command.
2. The package imports and CLI entry points work using the installed/src-layout
   configuration, not because the repository root happens to be on `sys.path`.
3. A representative run accepts a run-named directory below `outputs/` and
   rejects an output path outside the authorized root.
4. No live reference remains to the old source path, old checkout path, or old
   identity except entries listed in a reviewed exceptions file with a reason
   (historical documents and compatibility-stable identifiers may qualify).
5. Every README backtick path and documented command resolves or executes.
6. Ignored generated/cache directories remain ignored; required fixtures and
   retained evidence are tracked outside `outputs/` and remain available to
   their consumers in a fresh clone.
7. `git status` contains only the intended refactor plus the user's pre-existing
   changes. Rename detection is reviewed so large moves did not become accidental
   delete-and-recreate edits.
8. `outputs/` contains no retained test fixture or historical evidence after
   cleanup; a smoke run can populate it and its generated children can be removed
   without breaking the test suite.

Return a summary containing the identity map, directory disposition table,
changes made, checks run with results, intentional exceptions, and any external
rename still awaiting authorization.
