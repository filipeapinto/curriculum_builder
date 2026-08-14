#!/usr/bin/env bash
# PreToolUse gate: blocks Write/Edit to *.prompt.md / *.prompt.v<N>.md files
# that delegate to general-purpose/Explore subagents without pinning a cheaper
# model. See .claude/governance/subagent_cost.md for the rule and rationale.
set -euo pipefail

input="$(cat)"

tool_name="$(jq -r '.tool_name // empty' <<<"$input")"
file_path="$(jq -r '.tool_input.file_path // empty' <<<"$input")"

if [[ "$tool_name" != "Write" && "$tool_name" != "Edit" ]]; then
  exit 0
fi

if [[ ! "$file_path" =~ \.prompt(\.v[0-9]+)?\.md$ ]]; then
  exit 0
fi

content="$(jq -r '.tool_input.content // .tool_input.new_string // empty' <<<"$input")"

violations="$(grep -n -iE 'subagent_type[^a-z]*(general-purpose|Explore)' <<<"$content" || true)"

if [[ -z "$violations" ]]; then
  exit 0
fi

blocked=0
while IFS= read -r line; do
  lineno="${line%%:*}"
  start=$(( lineno > 5 ? lineno - 5 : 1 ))
  end=$(( lineno + 5 ))
  window="$(sed -n "${start},${end}p" <<<"$content")"
  if ! grep -qiE '\bmodel\s*:' <<<"$window"; then
    blocked=1
    echo "Line $lineno delegates to general-purpose/Explore without a nearby model: override:" >&2
    echo "  $line" >&2
  fi
done <<<"$violations"

if [[ "$blocked" -eq 1 ]]; then
  echo "" >&2
  echo "Governance violation: .claude/governance/subagent_cost.md requires model: \"haiku\" (or explicit justification) on general-purpose/Explore subagent delegation in prompt files." >&2
  exit 2
fi

exit 0
