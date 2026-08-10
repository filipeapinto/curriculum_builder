# Provider Correction — Execution Test Plan v1

## Purpose and boundary

Test `plans/provider_correction/provider_correction.plan.v1.md` without implementing it.
`RETIRED` is constructed at run time from ASCII `103, 101, 109, 105, 110, 105`; fixtures
must never contain the decoded identifier.

Evidence goes under `/private/tmp/provider-correction-test-<UTC>/`, never the repository.
Tests do not stage, stash, restore, reset, clean, or rewrite existing work. Runtime output
uses a fresh test-owned child of `outputs/`, removed only after its assertions complete.

## Availability stages

- **Runnable now, while the installed plugin is disabled:** `PC-T00` and `PC-T01` only.
  A conforming execution stops after `PC-T01`; no implementation edit is permitted.
- **Runnable after the plugin prerequisite passes:** `PC-T02` through `PC-T09` are the
  deterministic implementation and regression tests.
- **Live and blocked until the user enables the installed plugin:** `PC-T10`. Tests never
  enable it or mutate Claude Code settings.

## Ordered tests

### PC-T00 — Read-only baseline capture

Before invoking the implementation prompt, create the external test root and capture:

1. `claude plugin list`, plugin version, and enabled status.
2. `git status --porcelain=v2 -z --untracked-files=all`, `git diff --binary`, and
   `git diff --cached --binary` as raw files with SHA-256 hashes.
3. The index object id and working-tree SHA-256 for every inventoried or allowlisted path;
   for untracked paths, capture type, mode, size, and SHA-256.
4. A sorted, NUL-delimited manifest of every repository path except `.git/`, including
   hidden and ignored files, plus SHA-256 for every regular file and symlink-target bytes.
5. An encoded, case-insensitive full-tree inventory of matching path bytes and content
   bytes. Do not follow symlinks and do not decode the term into any persisted artifact.

This step is repository-read-only. Hash the bundle so it cannot be silently replaced.

### PC-T01 — Disabled-plugin fail-fast and zero mutation

When `PC-T00` records the plugin as disabled, invoke only phase 0 of the implementation
workflow. Require a non-success/blocked outcome naming the disabled prerequisite, with no
fallback CLI and no attempt to enable the plugin.

Repeat all `PC-T00` snapshots. Pass only when status, diffs, index objects, untracked-file
metadata/hashes, and full-tree manifest are byte-identical. No result, log append, cache
deletion, or timestamp touch is allowed. Keep the transcript externally. **Stop while the
plugin remains disabled.**

### PC-T02 — Enabled preflight and pre-edit behavioral baselines

After user enablement, repeat `PC-T00`, then make the one minimal read-only `worker`-route
call for a `high` review task at `xhigh`. Require plugin version, execution identity,
decided/executed model and effort, route identity, and bounded I/O; ambiguity stops edits.

Only after this preflight succeeds, capture pre-edit behavioral baselines:

- `./tests/run_gates.sh 4` and `./tests/run_gates.sh 5`, preserving their generated JSON,
  exit codes, per-gate states, and output digests in the external test root;
- `python3 tests/check_meta_prompt.py`;
- `python3 -m unittest discover -s tests/runtime -v`;
- `python3 runtime/run_curriculum.py --curriculum curricula/arduino_kit --test-static`;
- one `--test-simulated-all` run with a fresh explicit test-owned output root.

Record and remove only files those baseline commands create after copying their evidence.

### PC-T03 — Encoded full-tree path-and-byte regression test

Run `tests/runtime/test_provider_retirement.py` first. It must construct `RETIRED` from the
ASCII values, compare case-insensitively, not follow symlinks, exclude only `.git/`, scan
ignored/hidden/generated/binary files, and sort all path/content hits. Require zero hits.

Mutation-test the detector under a temporary scan root with four cases: matching regular
file content, a matching path name, hidden/ignored-style nesting, and binary bytes. Each
case must fail and identify every injected hit in sorted order; a control hit under
`.git/` must be ignored. No fixture may persist decoded bytes in the repository.

### PC-T04 — Contract activation and runtime ownership

Run the runtime unit suite and `tests/check_meta_prompt.py`. Add focused assertions that:

- v2 is the resolved active prompt and v1 is retained only under `meta_prompt/deprecated/`;
- Claude is recorded as orchestrator and author;
- the separate OpenAI-family verdict is accepted only through the plugin handoff over the
  existing `worker` route;
- no direct retired-provider executable, resolver, settings, credential, or fallback path
  is imported or invoked; and
- only deterministic Python emits terminal acceptance.

Mock the model boundary, not the validator. Both an author attempt to accept itself and a
plugin verdict that attempts to decide terminal acceptance must fail.

### PC-T05 — Exact request, verdict, and receipt contract

For exactly `OUTPUT_ROOT/plugin/judge_request.json`, `judge_verdict.json`, and
`judge_receipt.json`, test one valid triplet and a table of single-mutation negatives. The
validator must enforce the implementation's exact allowed key sets and types, then bind:
execution id; `worker` route id; plugin version; decided/executed model; `xhigh` effort;
authorized input and output path lists; and SHA-256 of request and verdict.

Negative cases must independently reject a missing field, extra field, wrong type,
execution-id mismatch, non-`worker` route, plugin-version mismatch, decided/executed model
mismatch, effort other than `xhigh`, reordered or altered authorization where order is
contractual, request-hash mismatch, verdict-hash mismatch, path traversal/absolute path,
an author-only input, a sibling-verdict input, an extra output, and any artifact outside
the three fixed paths. Assert the rejection occurs before aggregation or acceptance and
does not rewrite any of the three artifacts.

### PC-T06 — Dirty-worktree and delta protection

Compare the post-implementation repository to `PC-T02`'s pre-edit snapshot. Pass only if:

- the cached diff and every pre-existing index object are unchanged; execution staged
  nothing;
- pre-existing unstaged or untracked bytes outside the implementation allowlist are
  identical;
- in mixed target files, every baseline hunk without an overlapping encoded hit is
  preserved byte-for-byte, while only separable matching clauses/rows/hunks changed;
- every new or deleted path is explicitly authorized by the plan; and
- no unrelated status entry, mode, symlink target, or file hash changed.

An inseparable overlap is a stop, not a test waiver. Save the final binary cached/working
diff and a machine-readable allowlist comparison in the external test root.

### PC-T07 — Generated evidence and cache removal

Using `PC-T00`'s external manifest and hashes, require both named contaminated generated
run roots, every provider-specific proof/settings artifact beneath them, matching bytecode,
and the matching pytest-cache entry to be absent. Require no renamed or replacement copy
of those frozen receipts or input snapshots elsewhere in the repository.

The delta/action record must show whole-root deletion, not edited JSON evidence. Verify the
external pre-delete bundle hash and repeat the scan to prove bytes were not relocated.

### PC-T08 — Gate-baseline comparison

Run phases 4 and 5 again and compare by gate id with `PC-T02`, not merely by aggregate
counts. A baseline `PASS` may not become `FAIL` or `BLOCKED`; a baseline failure may not
worsen or block an additional gate; `SKIPPED` membership for the same requested phase must
not change unexpectedly. New gate ids, missing gate ids, crashes, and unrecorded outcomes
fail. Preserve exit codes and generated JSON, then remove only test-owned result files.

### PC-T09 — Static and simulated execution

Repeat the meta-prompt check, full runtime unit suite, static preflight, and simulated-all
command from `PC-T02`. Require no new failure, unchanged deterministic unit ordering and
coverage, terminal `ACCEPTED` only with `simulated-controller-only` coverage, complete log
audit, and no model or plugin call during static/simulated modes. Use a fresh output root;
verify existing-output refusal leaves a marker byte-identical, then remove only the fresh
test-owned output.

### PC-T10 — Enabled-plugin real smoke test (`high`/`xhigh`)

This only live test is blocked until user enablement. Through the corrected handoff, run
one isolated `high` review at `xhigh`; do not send safety-critical/`max`, add credentials,
or fall back to a direct CLI.

Validate the three exact artifacts with `PC-T05`, independently recompute both hashes,
confirm decided and executed model/effort agree, and prove the judge received only its
rubric and authorized candidate artifacts and wrote only its verdict. Then mutate a copy
of the authorization to include an author-only or sibling-verdict path and require
pre-call rejection with zero plugin invocation. The smoke passes only when Python validates
and aggregates the verdict; the plugin must not emit acceptance.

## Final audit and pass rule

After every repair, rerun `PC-T03`; after all tests, rerun it once more and repeat
`PC-T06`. Pass only when all applicable tests pass, the live test is evidenced rather than
simulated, both phase comparisons introduce no regression, and the final encoded scan has
zero path and content hits. If the plugin is disabled, report `PC-T00`/`PC-T01` as passed
and `PC-T02`–`PC-T10` as not run due to the explicit prerequisite; do not report overall
implementation acceptance.

Record test ids, commands, exit codes, artifact hashes, gate comparisons, blocked reason,
and the final verdict in `plans/provider_correction/provider_correction.result.v1.md` only
when implementation is authorized and has proceeded. Append the outcome to the shared log;
never edit prior entries.
