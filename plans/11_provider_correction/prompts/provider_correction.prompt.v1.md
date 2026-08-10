# GOAL

Implement `plans/provider_correction/provider_correction.plan.v1.md` exactly, using
`plans/provider_correction/qa/execution_test.plan.v1.md` as the acceptance procedure.
Run this workflow in Claude Code. Claude is the orchestrator and author; obtain the one
independent OpenAI-family review only through the installed `openai-codex` Claude Code
plugin over the existing `worker` route. Deterministic Python alone validates evidence,
aggregates the verdict, and decides acceptance.

`RETIRED` means the lowercase ASCII sequence `103, 101, 109, 105, 110, 105`. Construct it
from those bytes for every scan; never persist or print the decoded identifier in a new
artifact.

Phase 0 is mandatory and occurs before every repository mutation. Externally capture the
PC-T00 baseline and inspect `claude plugin list`, the installed plugin version, and enabled
status. If the plugin is disabled, run PC-T01, report the workflow blocked in the external
transcript, and stop with zero repository mutations—including no result file, log append,
cache deletion, or timestamp touch. Do not enable a plugin, alter external settings, add
credentials, invoke a direct provider CLI, or substitute another route. If enabled, make
the specified minimal read-only `high` review call at `xhigh`; stop before edits unless its
model, effort, route, execution identity, bounded I/O, and isolation are evidenced.

After that prerequisite passes, preserve the dirty worktree exactly as the plan requires:
never stage, stash, reset, restore, clean, overwrite, or delete pre-existing user work.
Freeze the encoded full-tree inventory and constrain changes to its hits plus the plan's
explicit contract/runtime/test/output/cache/log/result allowlist. Treat an overlapping
user hunk, ambiguous handoff semantics, or required out-of-allowlist repair as a stop.

Implement only the listed correction: activate contract v2; remove the mistaken
provider-specific runtime, tests, paths, residual references, contaminated generated run
roots, and matching caches; preserve separable nonmatching work; and add
`tests/runtime/test_provider_retirement.py`. Do not rewrite frozen generated receipts or
snapshots, relocate their bytes, redesign the curriculum contract, or broaden routing.

The handoff contract has exactly these paths:

- `OUTPUT_ROOT/plugin/judge_request.json`
- `OUTPUT_ROOT/plugin/judge_verdict.json`
- `OUTPUT_ROOT/plugin/judge_receipt.json`

The receipt must use an exact validated schema that binds execution id, `worker` route id,
plugin version, decided and executed model, `xhigh` effort, authorized input and output
path lists, and SHA-256 hashes of the request and verdict. Reject absent, extra, mistyped,
or mismatched fields; paths outside the three fixed artifacts; traversal or absolute
paths; author-only or sibling-verdict inputs; and extra outputs before aggregation. The
judge receives only its rubric and authorized candidate artifacts, writes only its
verdict, and never decides terminal acceptance.

# TEST

Use the external evidence root and exact preservation rules in the execution test plan.
Run PC-T00 through PC-T10 strictly in order, without skipping ahead:

1. PC-T00: capture and hash the repository-read-only baseline.
2. PC-T01: prove disabled-plugin fail-fast and byte-identical zero mutation; stop here if
   disabled.
3. PC-T02: after user enablement, prove the live read-only preflight, then capture gate,
   prompt, unit, static, and simulated baselines before edits.
4. PC-T03: require the encoded repository scan and detector mutation tests to pass with
   zero path/content hits, excluding only `.git/` and never following symlinks.
5. PC-T04: prove contract-v2 activation, Claude ownership, plugin-only separate review,
   absence of direct retired-provider behavior, and Python-only acceptance.
6. PC-T05: prove the exact three-artifact schema and every listed single-mutation negative
   case, with rejection before aggregation and no artifact rewrite.
7. PC-T06: prove index, dirty-worktree, mixed-hunk, allowlist, mode, symlink, and unrelated
   file preservation against PC-T02.
8. PC-T07: prove whole-root generated-evidence and cache removal against the immutable
   external manifest, with no edited, renamed, or relocated copy.
9. PC-T08: compare phase 4 and 5 gates by gate id against baseline; accept no new or
   worsened result.
10. PC-T09: repeat prompt, runtime, static, and simulated checks; preserve deterministic
    ordering/coverage, forbid model calls in test modes, and verify output refusal.
11. PC-T10: run the real isolated plugin smoke test at `high`/`xhigh`, validate and
    recompute the three artifacts, prove bounded I/O and pre-call authorization rejection,
    and require Python validation/aggregation.

PC-T10 must be run and evidenced for implementation acceptance. A disabled plugin permits
only the explicit PC-T00/PC-T01 blocked result; it never permits a success claim. Simulated
or fabricated plugin evidence cannot satisfy PC-T02 or PC-T10.

# LOOP

After the enabled preflight and authorized edits begin, execute each applicable test in
order. On failure, record the test id, command, exit code, evidence hashes, and narrow root
cause; revise only the in-scope failed artifact; rerun PC-T03 immediately; then rerun the
failed test and every later test whose evidence may have changed. Continue until PC-T00
through PC-T10 all pass, including the real live smoke test, both gate comparisons, the
final PC-T06 audit, and a final encoded zero-hit scan.

Do not waive, reorder, weaken, or replace a test. Stop without claiming success on a
plugin becoming unavailable, ambiguous receipt semantics, collision with user work,
required work outside the allowlist, or a new/worsened gate failure that cannot be repaired
within scope. Never respond to a failure by enabling plugins, changing external settings,
adding credentials, using a direct provider CLI, fabricating evidence, or editing frozen
generated evidence.

When implementation has actually proceeded, write
`plans/provider_correction/provider_correction.result.v1.md` with the captured baseline,
changed/deleted paths, test ids and commands, exit codes, artifact hashes, per-gate
comparisons, plugin receipt summary, encoded zero-hit result, remaining failures, and final
verdict. Append—never rewrite—the execution outcome to
`plans/provider_correction/plans.log.md`. Claim completion only when every applicable test,
including PC-T10, has passed and the final delta matches the allowlist.
