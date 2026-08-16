# Execute the complete Curriculum Factory repository refactor

You are the sole implementation agent. Finish the complete repository refactor defined
by `plans_internal/refactor_repo/refactor_repository.spec.v8.html`.

## Authority and source of truth

The HTML specification above is the authoritative requirements document. Read it in
full before changing anything. Implement every applicable requirement and satisfy all
20 executable acceptance tests in section 10.

The existing P00–P10 prompts, RUN controller, orchestration ledger, checkpoint reports,
QA sessions, journals, and prior agent claims are not execution instructions for this
run. They may be inspected only as historical evidence. Do not invoke them, resume
them, repair them, generate replacements for them, or use their completion status as
proof that the specification is satisfied.

Do not delegate work to sub-agents. Do not spawn agents. Do not run an agent inside an
agent. Perform the implementation and verification yourself in this session.

## Required outcome

Deliver a genuinely complete, clean, installable repository in which:

- the human-facing product name is `Curriculum Factory`;
- the repository identity is `curriculum_factory` where repository identity is meant;
- the Python distribution is `curriculum-factory`;
- the Python package is `curriculum_factory`;
- all production Python code is under `src/curriculum_factory/`;
- no production `runtime` package remains or resolves;
- package-owned resources ship in wheel and sdist and load without assuming a normal
  filesystem path;
- repository-owned policy, schemas, curricula, and outputs use an explicit data or
  repository root rather than `Path(__file__).parents[...]` inference;
- outputs are constrained beneath the selected repository's `outputs/` boundary before
  any artifact is created;
- ignored output state is disposable and no test or active evidence depends on it;
- every required retained run-derived fixture is tracked, minimal by consumer closure,
  SHA-256-manifested, and referenced by an active consumer;
- existing schema `$id` values are preserved or versioned according to section 3, with
  complete decision and reference-resolution coverage;
- live code, automation, configuration, documentation, commands, and paths use the
  correct identity, with every intentional legacy occurrence recorded precisely;
- the selected test-tree layout is evidence-supported and cannot shadow the installed
  production package;
- installation, imports, CLIs, tests, gates, artifact builds, documentation commands,
  and clean-room verification work from a fresh clone without ignored or untracked
  material.

Do not perform the external GitHub repository rename, local checkout rename, or changes
to integrations unless the user separately authorizes those exact external operations.
Record them as pending when authorization is absent. Their absence does not excuse any
repository-local acceptance failure.

## Execution method

1. Inspect the current Git worktrees, branches, commits, staged changes, unstaged
   changes, untracked files, ignored files, and remote relationship. Identify the most
   advanced legitimate implementation state. Preserve unrelated user work.
2. Read specification v8 completely and build a concise requirement-to-evidence
   checklist covering every requirement and all 20 acceptance tests. This checklist is
   for execution tracking, not a replacement planning bureaucracy.
3. Inspect all existing refactor commits and working-tree changes. Reuse correct code,
   repair incomplete code, and discard no evidence or user change merely because a
   prior attempt was messy. Do not trust checkpoint labels or prior QA verdicts without
   reproducing the underlying behavior.
4. Run the current tests before further mutation and capture actual failures. Detect
   environment contamination, especially editable installs or imports resolving from a
   different worktree. All meaningful verification must use the intended checkout and
   installed artifact.
5. Implement every missing repository-local requirement directly. Keep changes scoped
   to the refactor; do not introduce an unrelated subsystem redesign or formatting
   sweep.
6. Migrate every active consumer of ignored output data before treating `outputs/` as
   empty. Do not weaken, skip, deselect, or delete tests to manufacture empty-output
   success. Preserve exact historical bytes only when an assertion genuinely requires
   them; otherwise generate test-local data.
7. Review identity and path occurrences semantically. Do not blindly replace schema
   identifiers, historical records, external URLs, or deprecated material. Every
   retained legacy occurrence must have exact location, consumer, rationale, and a
   testable removal condition.
8. Build wheel and sdist, inspect both file lists and metadata, install only the wheel
   into a fresh environment, and run import, origin, CLI, module-command, package
   resource, explicit-root, and containment checks from outside the checkout.
9. Run the complete test suite and repository gates with `outputs/` empty. Then create
   unrelated ignored output state and prove it does not affect selection or results.
10. Reproduce the inventory from a clean checkout and prove it is read-only,
    schema-valid, complete, and nonzero on seeded collection failure.
11. Run clean-room verification from a clean checkout containing no ignored or
    untracked local material and using only documented dependencies. Test Python and
    structured-data codemods for fixtures, dry-run behavior, determinism, idempotence,
    unsafe diagnostics, and residual-reference postconditions.
12. Fix every failure attributable to the refactor and repeat the relevant checks.
    Continue until the entire acceptance matrix passes. Do not stop merely because a
    focused subset passes.
13. Review the complete final diff for scope, accidental evidence churn, secrets,
    generated build artifacts, stale paths, and test weakening. Ensure the intended
    worktree is clean after committing the final repository-local result.

## Mandatory acceptance matrix

You must execute and retain evidence for every specification section 10 criterion:

1. installed imports;
2. CLI behavior;
3. root resolution;
4. wheel and sdist contents, metadata, installation, and resource loading;
5. installed module origin;
6. evidence-backed test-tree decision;
7. package-shadowing rejection from repository root, test directories, and an external
   directory;
8. output containment, including absolute, traversal, symlink, and alternate-spelling
   escapes rejected before mutation;
9. bidirectional fixture closure and digest accuracy;
10. ignored-state independence;
11. full-suite empty-output resilience;
12. schema identity decisions and `$ref` resolution;
13. live reference integrity with enumerated exceptions;
14. documented path and command integrity;
15. fresh-clone reproducibility;
16. clean-room verification;
17. behavioral differential against the recorded baseline using only predeclared
    normalization;
18. Python, TOML, JSON, and YAML codemod safety;
19. full regression and final-delta scope review without weakened tests;
20. reproducible, read-only, fail-closed inventory.

For each criterion, record the exact command, exit code, and essential result. A skipped,
interrupted, timed-out, environment-contaminated, or partially observed command is not a
pass. Existing failures must be distinguished from new failures with reproducible
evidence; they cannot be silently ignored.

## Completion rules

Do not say “finished,” “complete,” or equivalent unless all of the following are true:

- every repository-local requirement in specification v8 is implemented;
- all 20 acceptance criteria have current, reproducible passing evidence;
- the complete test suite and repository gates pass with empty `outputs/`;
- clean wheel and sdist build and inspection pass;
- a fresh wheel install passes from outside the checkout;
- clean-room verification passes without ignored or untracked dependencies;
- no production import resolves from the checkout, another worktree, or a test tree;
- no active test or evidence consumer reads durable data from ignored `outputs/`;
- the final diff contains no unrelated changes, generated build artifacts, secrets, or
  weakened tests;
- the implementation worktree is clean and the exact final commit is identified.

If any item is not satisfied, continue working. If genuinely blocked by missing external
authorization or unavailable external state, report the exact unsatisfied criterion,
the commands and evidence proving the block, the last verified commit, and the smallest
user action required. Do not present a partial implementation as completion.

## Final response

Report:

- the branch, worktree, and final commit;
- a concise summary of implemented changes;
- a 20-row acceptance table with PASS/BLOCKED, exact commands, and evidence locations;
- complete test/gate totals;
- wheel/sdist and fresh-install results;
- clean-room result;
- remaining intentional exceptions;
- pending external rename operations;
- confirmation that no sub-agent or P00–P10/RUN orchestration was used.

Do not push, force-push, open a pull request, rename the GitHub repository, rename the
checkout, publish artifacts, or modify external integrations unless the user explicitly
authorizes that exact action.
