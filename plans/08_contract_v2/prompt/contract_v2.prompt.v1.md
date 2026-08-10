# Author the Curriculum Contract v2 — Prompt v1

## Objective

Produce `meta_prompt/curriculum.prompt.v2.md`: a complete successor to
`meta_prompt/curriculum.prompt.v1.md` that states two things v1 leaves implicit or wrong —
the contract is executed from Claude Code, and the required second model family is reached
through the installed `openai-codex` Claude Code plugin.

This is an authoring task. Do not implement runtime code, do not run a curriculum, and do
not generate a unit.

## Read first, completely

1. `meta_prompt/curriculum.prompt.v1.md` — the document being superseded. Read every line.
2. `meta_prompt/assets/unit_prose.v1.md`, `pedagogy.v1.md`, `model_selector_prompt.v1.md`.
3. `policy/routes.v1.yaml`, `policy/controller.v1.yaml`, `policy/routing/` (all four files),
   `policy/checks.v1.yaml`, `policy/deferred.v1.yaml`, `policy/limits.v1.yaml`,
   `policy/calibration.v1.yaml`, `policy/failures.v1.yaml`.
4. `schemas/routing_decision.schema.v2.json` — note `reasoning_effort` is required with
   enum `medium | high | xhigh | max`.
5. `runtime/` — the controller, logger and selector that now exist, and
   `tests/runtime/` — 42 passing tests. v2 must describe the system that exists.
6. `tests/check_meta_prompt.py` and `tests/meta_prompt_source.py` — these bind the
   contract's filename and mission block.

Do not read `meta_prompt/deprecated/`.

## The two substantive changes

### 1. Claude Code is the execution environment

v1 never says who reads it. It is addressed to a model — it has a §Final response section
and instructs the reader not to ask the user ordinary implementation questions — but it
never names the environment, which is how a Python-controller reading and an agent reading
both looked defensible.

v2 states plainly: this contract is read and executed by Claude Code, which is the
orchestrator. Reconcile that with v1 §Acceptance's "Code decides, models write" without
weakening it: the orchestrator invokes deterministic code in `runtime/` for unit order,
state transitions, routing, retries, checkpoints, revision targeting, audits and every
acceptance decision. The orchestrator does not make those decisions itself. State the
boundary explicitly enough that a reader cannot conclude the agent may adjudicate a gate.

### 2. The second model family comes from the openai-codex plugin

v1 §Review requires "one judge per pass, from a different model family than the
generator." It names no provider, and it must not start naming one loosely.

v2 states: the orchestrating family is Anthropic (Claude Code); the second family is
OpenAI, reached through the installed `openai-codex` Claude Code plugin, whose underlying
capability is the already-proven `worker` route in `policy/routes.v1.yaml`
(`codex exec -s workspace-write --skip-git-repo-check -m <decided_model>
-c model_reasoning_effort=<decided_effort>`).

Constraints v2 must carry:

- **No new credential.** Both families are already authenticated on this machine. v2 must
  not introduce, assume, or reference an API key, token or secret. v1 references none, and
  v2 must reference none. Verify by search before you finish.
- **Effort must remain recordable.** Every model call emits a routing decision with
  `reasoning_effort` from the enum above. `codex exec` carries it via
  `-c model_reasoning_effort=`; `claude -p --model <id> --effort <level>` accepts
  `low, medium, high, xhigh, max`. Neither family requires a mapping layer. Say so, and
  forbid inventing one.
- **Resolve the plugin-versus-route question explicitly.** `policy/routes.v1.yaml` requires
  each capability to be a preflight-provable invocation with a recorded command. A plugin
  invoked inside an interactive session is not that. v2 must state which of these holds and
  why: the plugin is a convenience wrapper over the recorded `worker` route and the route
  remains the proven capability; or the plugin itself needs a route entry. Do not leave it
  ambiguous. Do not edit `policy/routes.v1.yaml` in this task — state the requirement, and
  record any needed route work as a new obligation in the deferred inventory's style
  without editing `policy/deferred.v1.yaml` either.
- **Structural isolation survives.** §Review requires "isolation is structural, not
  instructed," and §Acceptance forbids a model aggregating its own verdict. If the
  orchestrating Claude is also a reviewer, that is instructed isolation and v2 must forbid
  it: the judge runs as a separate invocation with its own authorized input and output
  paths, and the controller aggregates.

## What must not change

v2 is a revision, not a rewrite. Preserve v1's structure, section order, voice and every
rule not touched by the two changes above. Specifically preserve, in substance and in
strength:

- `ENGINE` derived from the file's own location, never written down.
- The §Precedence ranking, its stated reason, and the rule that every read source is ranked.
- Never hardcode a unit count, curriculum name, subject, or any domain word.
- One parent for every fact; the domain block as sole parent.
- Grounding: every domain value carries a primary source retrieved during the run.
- The domain verifier requirement and "never use a model to check a model's domain work."
- The six gates, their order, their check ids, and the `simulated` label rule.
- The hash of this file recorded in the run's state.
- The three claims in §Final response that are never merged.
- The measured figures and their citations — do not round, drop or restate them.

Do not soften a rule to make the new material fit. If the two changes genuinely conflict
with an existing rule, state the conflict in the run report rather than resolving it
silently.

## Mechanical obligations

1. Write `meta_prompt/curriculum.prompt.v2.md`.
2. Move `meta_prompt/curriculum.prompt.v1.md` to `meta_prompt/deprecated/` with `git mv`,
   preserving history. §Precedence requires superseded contracts to be retained there and
   never read.
3. Update the mission block's `PROMPT =` line to the v2 path, and update
   `tests/check_meta_prompt.py` and `tests/meta_prompt_source.py` wherever they bind the v1
   filename. These are the only two test files in scope.
4. Find and update every other live reference to `curriculum.prompt.v1.md` outside
   `meta_prompt/deprecated/` and `plans/`. Search the whole repository.
5. Do not edit `policy/`, `schemas/`, `curricula/`, `runtime/`, `tests/runtime/`, the
   companions in `meta_prompt/assets/`, or any gate.

## Verification

Baseline before you start — record it:

```text
./tests/run_gates.sh 4      → 28 PASS, 2 FAIL, 8 SKIPPED of 38
./tests/run_gates.sh 5      → 36 PASS, 2 FAIL of 38
python3 tests/check_meta_prompt.py → 6/6 PASS
```

The two failures are pre-existing: `FR-P0-CLEAN` (dirty worktree) and `FR-P0-NOSTALE`
(three `assets/` hits under `.claude/skills/curriculum-concept-visualization/`). Neither is
yours to fix.

After the change, all three commands must report the same results — same two failures, no
third, `FR-P0-NOSTALE` still at exactly three hits, `check_meta_prompt.py` still 6/6. A
`FR-P1` retention or `FR-P0` history failure means the `git mv` was done wrong.

Then verify by search that v2 contains no API key, token, credential or secret reference,
and no provider name in a position where v1 would have said "family."

## Final response

Lead with the outcome. Report:

- The v2 path, its line count, and the deprecated v1 path.
- How each of the two substantive changes is stated, quoting the sentences that carry them.
- The plugin-versus-route position taken, and why.
- Every rule from "What must not change" confirmed present, or named as changed with the
  reason.
- Any conflict found between the new material and an existing rule, unresolved and stated.
- Files changed outside `meta_prompt/`, with justification for each.
- All three verification commands with their before and after results.
- Confirmation that no credential reference exists in v2.

Never claim v2 is proven by this task. It is an authored contract; nothing has executed it.
