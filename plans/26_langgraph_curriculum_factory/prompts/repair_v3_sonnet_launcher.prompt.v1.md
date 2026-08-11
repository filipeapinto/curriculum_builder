# GOAL

Repair the Plan 26 prompt-graph launcher so a non-interactive Claude Sonnet node
can run its explicitly authorized pytest command without enabling unrestricted
shell access. Prove the launcher with a cheap preflight, preserve verified work,
then resume at `N30_UNIT_GRAPH` exactly once.

This repairs only the implementation harness. It must not replace, weaken, or
modify the production LangGraph architecture required by
`plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md`.

# CURRENT STATE

- Repository: `/Users/filipepinto/Projects/curriculum_builder`.
- Active implementation graph: `plans/26_langgraph_curriculum_factory/implementation.graph.v3.yaml`.
- Controller: `plans/26_langgraph_curriculum_factory/prompt_graph_controller.py`.
- Compact state: `plans/26_langgraph_curriculum_factory/results/v3/`.
- Nine nodes are verified `PASSED`: N00, N10, N11, N12, N13, N20, N21, N22, N23.
- `N30_UNIT_GRAPH` is the sole `READY` frontier. It is not passed.
- The interrupted v2 implementation and evidence are the baseline; do not reset,
  revert, delete, or overwrite unrelated dirty work.
- Two N30 launcher attempts were rejected before useful implementation work:
  1. `--permission-mode acceptEdits` did not authorize Bash in non-interactive mode.
  2. The scoped allow rule authorized
     `/tmp/plan26_n30_verify/bin/python -m pytest *`, but Sonnet invoked
     `python3 -m pytest`, so Bash was denied again.
- Neither failed attempt produced an admissible N30 receipt.

# NON-NEGOTIABLE SAFETY

1. Do not use `--permission-mode bypassPermissions`,
   `--dangerously-skip-permissions`, or a wildcard `Bash(*)` rule.
2. Keep `acceptEdits` and authorize only ordinary read/edit tools plus pytest
   through the controller-resolved Plan 26 interpreter.
3. Do not hardcode a temporary interpreter path in a node prompt or controller
   preamble. Resolve it from `PLAN26_PYTHON` or `execution.python_candidates`.
4. The exact same resolved path must be used in:
   - Claude's allowed Bash pattern;
   - the node prompt packet's test instruction;
   - the controller's independent verification command;
   - the launcher preflight.
5. A permission failure must fail fast before N30 is launched and must not consume
   a node attempt or write a node receipt.
6. Do not rerun Claude for any already-passed node. If a harness change makes old
   receipts require revalidation, validate their schema, recorded zero exits,
   current output hashes, and predecessor fingerprints mechanically. Focused
   verification may be rerun only where mechanical revalidation is insufficient.
7. Do not run the complete runtime suite before N50.
8. If the graph or schema changes, create the next version and move the superseded
   version under `plans/26_langgraph_curriculum_factory/deprecated/`. Update all
   active references. Do not silently mutate a frozen version contract.

# IMPLEMENTATION

1. Inspect current processes and the current graph/controller/status. Confirm no
   prior N30 controller process is still active before editing.
2. Add one controller-level command-expansion function that resolves the Plan 26
   interpreter once and replaces `{python}` anywhere inside every
   `execution.claude_command` argument, including inside
   `Bash({python} -m pytest *)`.
3. Build the Sonnet command from structured manifest arguments. The active policy
   must be equivalent to:
   - `--permission-mode acceptEdits`;
   - allowed tools `Read`, `Edit`, `Write`, `Glob`, `Grep`;
   - exactly `Bash(<resolved-python> -m pytest *)` for shell execution.
4. Inject the resolved interpreter into the generated prompt packet:
   `Run every pytest command as <resolved-python> -m pytest ...; never use
   python3, python, or plain pytest.`
5. Add a `preflight` controller subcommand. It must use the same isolated-workspace
   creation and the same resolved Sonnet command/tool policy as a real node, but
   send only a minimal prompt requiring exactly:
   `<resolved-python> -m pytest --version`.
   It passes only if the nested Claude command exits zero, actually invokes the
   authorized Bash command, and returns an explicit success marker. It may not edit
   repository files or create a node receipt.
6. Persist the preflight log outside the isolated workspace under the v3/vNext
   scheduler log directory. Include command, exit, and log hash in its JSON result.
7. Keep implementation-result cache identity separate from launcher plumbing:
   node correctness depends on node definition, prompt, spec, predecessor receipts,
   pinned environment, and current output hashes. Record the harness/controller
   digest for audit and revalidate receipts with it, but do not rerun successful
   implementation nodes merely because permission-launcher code changed.
8. Add or update focused controller tests for placeholder expansion, exact tool
   scope, preflight success/failure, no receipt on preflight failure, cache
   preservation, and N30 remaining the only frontier.

# TEST

Run, in order:

1. Controller unit tests only.
2. Graph/schema validation.
3. Controller status. It must show the nine listed nodes `PASSED`, N30 `READY`,
   and no other ready node.
4. The new launcher preflight. Do not launch N30 unless it passes.
5. Dry-run selecting only N30.
6. Run exactly one N30 generation.

Acceptance requires:

- no unrestricted permission flag or broad Bash wildcard;
- the resolved interpreter is identical in allowlist, prompt, preflight, and
  independent verification;
- preflight proves nested Sonnet can execute pytest non-interactively;
- passed-node receipts remain admitted without rerunning their Claude prompts;
- N30 tests use the hash-locked interpreter;
- N30 changes merge only when its reported status is `PASSED`, its focused tests
  return zero, its result record is admissible, and every changed path is inside
  N30's declared write set;
- no full-suite execution occurs during this repair or N30 run.

# LOOP

If a launcher/controller test or preflight fails, fix the launcher and repeat only
the controller tests, validation, status, and preflight. Do not spend another N30
attempt until preflight is green.

After one preflight-proven N30 run:

- if N30 passes, report its receipt hash, focused-test count, changed paths, elapsed
  time, and the next frontier; then continue the graph one generation at a time;
- if N30 exposes an implementation defect, stop permission work and report the exact
  failing assertion and owning rework node;
- if N30 is blocked for any launcher/permission reason, stop and report the precise
  command/tool mismatch. Do not apply another speculative permission patch.
