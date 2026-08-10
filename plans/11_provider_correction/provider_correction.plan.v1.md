# Provider Correction — Implementation Plan v1

## Status and objective

Planning only; no implementation is authorized by this document's creation.

Remove the retired provider integration completely, including case-insensitive text,
path names, generated evidence, caches, runtime code, tests, and historical planning
references. Restore the intended design: Claude Code executes the curriculum contract,
deterministic Python owns state and acceptance, and Claude obtains isolated OpenAI-family
input through the installed `openai-codex` Claude Code plugin.

To avoid recreating the forbidden identifier in this plan, `RETIRED` means the lowercase
ASCII sequence `103, 101, 109, 105, 110, 105`. Checks must construct it from those bytes;
no new artifact may spell it literally.

## Architectural end state

1. Claude Code is the sole orchestrator and primary authoring environment.
2. Python remains the authority for manifests, ordering, transitions, retries, hashes,
   deterministic checks, isolation, and acceptance. Neither Claude nor the plugin decides
   whether a unit passes.
3. Independent model input comes from OpenAI through the installed `openai-codex` Claude
   Code plugin. The plugin is the in-session interface over the already proven `worker`
   route in `policy/routes.v1.yaml`; it is not a second route and requires no new
   credential, API client, provider settings file, or direct alternate-provider CLI.
4. The OpenAI judge receives only its rubric and authorized candidate artifacts, writes
   only its verdict, and cannot read sibling verdicts. Claude cannot review its own work.
   The controller validates and aggregates the verdict. This input is a `high` review
   task at `xhigh`, which the installed plugin exposes; it is not the `safety_critical`
   `final_acceptance` task and never substitutes `xhigh` for unsupported `max`.
5. Every model action retains a routing decision and execution receipt binding role,
   decided/executed model, effort, authorized inputs/outputs, and route id.

`plans/contract_v2/prompt/contract_v2.prompt.v1.md` is the authoritative statement of this
boundary. Implementation must activate that contract rather than invent another design.

## Exact work

### 0. Fail-fast plugin prerequisite

- Before any repository edit or deletion, record `claude plugin list`, the installed
  `codex@openai-codex` version, and enabled status. It is currently installed but disabled;
  execution stops here until the user enables it outside this plan.
- Once enabled, make one minimal read-only plugin call at `xhigh` and record its actual
  execution/result semantics. Stop if model, effort, route identity, or isolation cannot be
  evidenced. This plan does not enable plugins, mutate external settings, invent an effort
  mapping, or fall back to a direct CLI.

### 1. Protect the dirty worktree and freeze the inventory

- Capture plain and NUL-delimited Git status plus cached and working-tree diffs for every
  path the task will touch. Never stage, stash, reset, restore, clean, or overwrite user
  work.
- Construct `RETIRED` from its ASCII bytes and inventory both case-insensitive path-name
  hits and byte-content hits under the repository, excluding only `.git/`.
- Bind the implementation allowlist to that inventory plus the contract/runtime/test
  files named below. A newly discovered hit joins the same narrow class; it does not
  authorize unrelated cleanup.

### 2. Activate the Claude Code contract

- Execute the already-authored contract-v2 instructions: create
  `meta_prompt/curriculum.prompt.v2.md`, retain v1 under `meta_prompt/deprecated/`, and
  update `runtime/controller.py`, `tests/check_meta_prompt.py`, and
  `tests/meta_prompt_source.py` to resolve v2.
- State the five architectural rules above in v2 without weakening its existing
  precedence, grounding, verifier, isolation, routing, or deterministic-acceptance rules.
- Update only live documentation references needed to identify v2 as current. Do not
  redesign the curriculum contract or routing policy.

### 3. Remove the mistaken provider-specific runtime

- Delete `runtime/${RETIRED}.py`, `runtime/resolve_${RETIRED}_settings.mjs`, and
  `tests/runtime/test_${RETIRED}.py`.
- Remove their imports and provider-settings logic from `runtime/capabilities.py` and
  `tests/runtime/test_capabilities.py`. Retain provider-neutral route availability and
  real-receipt validation.
- Remove the direct alternate-provider CLI cycle from `runtime/capability_cycle.py`.
  Replace it with a provider-neutral validator for the Claude-orchestrated plugin handoff,
  or delete the module if no live caller needs it; do not leave a dead compatibility shim.
- Update `runtime/session_bridge.py` so it records Claude as orchestrator/author and accepts
  one structurally isolated plugin verdict. Remove the hardcoded OpenAI author identity and
  the inaccurate “current in-session model” substitution record.
- Use exactly `OUTPUT_ROOT/plugin/judge_request.json`, `judge_verdict.json`, and
  `judge_receipt.json`. The receipt must bind an execution id, `worker` route id, plugin
  version, decided/executed model, `xhigh` effort, authorized input/output path lists, and
  request/verdict hashes. Deterministically reject absent, extra, or mismatched fields and
  any author-only or sibling-verdict path. If the phase-0 call cannot support these claims,
  stop rather than fabricate a receipt.
- Update `runtime/finalize_evidence.py` to consume the plugin verdict/receipt and report the
  real author, judge, route, and isolation result. Update `runtime/run_curriculum.py` only
  where its live-capability behavior must reflect this handoff.
- Add focused runtime tests proving: no direct retired-provider executable/config path is
  used; Claude authors; the plugin supplies the separate OpenAI verdict; decided and
  executed model/effort agree; unauthorized inputs or outputs fail; and Python alone emits
  acceptance.

### 4. Remove residual text, names, and invalid evidence

- In `plans/simplification/`, classify the staged and unstaged hunks in the six
  `implement_curriculum_runtime.prompt.v1.md` through `.v6.md` files. Delete a file only if
  it is wholly the faulty, task-owned instruction and contains no separable user work;
  otherwise preserve nonmatching content and replace only the faulty route sections with a
  short supersession pointer to this plan and the contract-v2 prompt. Apply the same
  surgical rule to the phase-6 result and handoff.
- In the five `plans/simplification/research/*.v1.md` files with inventory hits, remove only
  the affected comparison row, clause, or source. Do not rename a model in a citation or
  attribute its result to another model. If the identifier is inseparable from a claim or
  URL, remove that claim and citation cleanly.
- Delete the two contaminated generated run roots, `outputs/runtime_task_v6/` and
  `outputs/arduino_kit_run_v2/`, as generated artifacts. Do not rewrite frozen receipts or
  input snapshots in place. Record a pre-delete file manifest and hashes in temporary task
  evidence; do not persist the forbidden bytes elsewhere in the repository.
- Delete matching `__pycache__` bytecode and clear the matching `.pytest_cache` record.
  Caches are regenerated only from the corrected source.
- Rename or delete every remaining path whose name contains `RETIRED`; edit every remaining
  text/byte hit. Planning artifacts produced by this workflow are part of the scan.

### 5. Add one permanent regression test

Add `tests/runtime/test_provider_retirement.py`. It must build the forbidden byte sequence
from the six ASCII values, walk the repository without following symlinks, exclude only
`.git/`, and fail with the complete sorted list of matching path names or file contents.
It must scan ignored, hidden, generated, and binary files so caches and output snapshots
cannot reintroduce the dependency. No fixture may contain the literal identifier.

## Verification sequence

1. Run the new retirement test first and require zero path/content hits.
2. Run all runtime unit tests and the contract checks.
3. Run phase 4 and phase 5 gates and compare every result with the captured baseline;
   accept no new or worsened failure.
4. Run static and simulated curriculum execution and require the same deterministic
   coverage and terminal behavior as baseline.
5. Repeat the phase-0 isolated `xhigh` plugin call through the corrected handoff and
   validate its exact request, verdict, and receipt artifacts. Do not fall back to a direct
   provider CLI or add credentials if the plugin is unavailable.
6. Repeat the encoded full-tree path/content scan after every repair and once after all
   tests, then audit the final Git delta against the baseline and allowlist.

## Acceptance criteria

- The encoded full-tree scan reports zero matching path names and zero matching bytes.
- Claude Code is explicitly the orchestrator and authoring environment in the active v2
  contract and runtime evidence.
- Independent input is obtained only through the installed `openai-codex` Claude Code
  plugin over the existing `worker` route; no alternate-provider runtime, settings,
  resolver, proof directory, credential instruction, or direct CLI call remains.
- The plugin is enabled before edits begin. One real isolated `high`/`xhigh` plugin smoke
  call has a valid routing decision and receipt; model and effort match, and unauthorized
  path access is rejected. No safety-critical `max` decision is sent through an interface
  that cannot express it.
- Python, not either model, validates the verdict and decides acceptance.
- Provider-neutral runtime behavior, static/simulated runs, contract checks, and phase
  gates introduce no regression beyond captured baseline failures.
- Contaminated generated runs and caches are removed rather than falsified by editing.
- The final delta contains only inventoried references, the narrow architecture correction,
  the v2 activation, the regression test, and this planning workflow's artifacts.

## Stop conditions and result

Stop on a collision with pre-existing user work, an unavailable required plugin, ambiguous
receipt semantics, a required repair outside the allowlist, or a new/worsened gate failure
that cannot be repaired within scope. An overlapping hunk is a collision; separable staged
or unstaged content is preserved and is not a blocker. Do not substitute another provider
or direct CLI.

Write `plans/provider_correction/provider_correction.result.v1.md` with the baseline,
changed/deleted paths, test results, plugin receipt summary, encoded zero-hit result, and
remaining failures. Append the execution outcome to `plans/provider_correction/plans.log.md`.
