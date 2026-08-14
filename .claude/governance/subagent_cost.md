# Governance: subagent model selection in prompt files

Applies to any `*.prompt.md` or `*.prompt.v<N>.md` file (plan implementation
prompts under `plans/**/prompts/`, `plans/**/execution_package*/**/prompts/`, etc).

## Rule

If the prompt instructs Claude Code to spawn subagents via the `Agent` tool
with `subagent_type: general-purpose` (or `Explore`) for search, lookup, or
mechanical multi-file scanning work, the prompt MUST pin a cheaper model on
that call:

- `model: "haiku"` for pure search/lookup/grep-style delegation.
- `model: "sonnet"` (or omit, inheriting parent) only when the subagent task
  requires non-trivial reasoning, synthesis, or judgment calls that a smaller
  model would get wrong.

## Why

Subagent calls run under their own context and are billed independently.
Historical sessions showed general-purpose subagents alone accounting for a
disproportionate share (34%) of total usage — mostly on tasks that were
mechanical search/scan work, not reasoning work.

## Enforcement

A `PreToolUse` hook on `Write`/`Edit` (`.claude/hooks/check_prompt_governance.sh`)
blocks writes to matching prompt files if they reference `general-purpose` or
`Explore` subagent delegation without a `model:` override nearby. This is a
heuristic text check, not a parser — false positives are possible; the hook
prints the matched line so the author can fix or override.
