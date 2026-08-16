#!/usr/bin/env bash
# Generates the exact, machine-derived target list this prompt acts on.
# Re-run to regenerate; never hand-edit the .txt outputs.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

ASSETS="prompts/rebrand_system/assets"
EXCLUDES=(':!plans' ':!.plan26-run' ':!docs/deprecated' ':!docs/research'
          ':!meta_prompt/deprecated' ':!docs/specs/deprecated'
          ':!**/evals/**' ':!**/action_log.jsonl')

# 1) TARGETS — every live file containing the exact phrase "curriculum
#    builder" or "curriculum pipeline" as prose (repo-wide rebrand scope).
{
  echo "# generated $(date -u +%Y-%m-%dT%H:%M:%SZ) by find_old_name_references.sh — do not hand-edit"
  echo "# every file listed here gets its 'curriculum builder' / 'curriculum pipeline'"
  echo "# occurrences replaced with 'Curriculum Factory' by apply_rebrand.sh"
  echo
  git grep -il -i -E "curriculum builder|curriculum pipeline" -- . "${EXCLUDES[@]}" || true
} > "$ASSETS/targets.v1.txt"

# 2) readme.md-specific: self-description line + broken path references with
#    auto-discovered live replacement by basename.
LIVE_TREE=$(git ls-files -- . "${EXCLUDES[@]}")
{
  echo "# generated $(date -u +%Y-%m-%dT%H:%M:%SZ) by find_old_name_references.sh — do not hand-edit"
  echo
  echo "## readme.md lines matching self-description terms (pipeline|builder), word-boundary"
  grep -n -w -i -E "pipeline|builder" readme.md || echo "(none)"
  echo
  echo "## readme.md backtick paths: existence + auto-discovered live replacement by basename"
  grep -oE '`[^`]*/[^`]*`' readme.md | tr -d '`' | while read -r p; do
    if [ -e "$p" ]; then
      echo "OK      $p"
    else
      base=$(basename "$p")
      hit=$(printf '%s\n' "$LIVE_TREE" | grep -F "/$base" | grep -v '/deprecated/' || true)
      if [ -n "$hit" ]; then
        echo "MISSING $p -> candidate replacement(s):"
        printf '%s\n' "$hit" | sed 's/^/           /'
      else
        echo "MISSING $p -> no live replacement found in tracked tree"
      fi
    fi
  done
} > "$ASSETS/readme_targets.v1.txt"

# 3) CONTEXT ONLY — code identifiers / hyphenated forms, never edited by
#    apply_rebrand.sh (e.g. the User-Agent string tied to the repo name).
{
  echo "# generated $(date -u +%Y-%m-%dT%H:%M:%SZ) by find_old_name_references.sh — context only, do not edit"
  echo
  echo "## git grep -i -n 'curriculum-builder'"
  git grep -i -n "curriculum-builder" -- . "${EXCLUDES[@]}" || true
  echo
  echo "## git grep -i -n 'curriculum-pipeline'"
  git grep -i -n "curriculum-pipeline" -- . "${EXCLUDES[@]}" || true
} > "$ASSETS/repo_wide_context.v1.txt"

echo "wrote $ASSETS/targets.v1.txt"
echo "wrote $ASSETS/readme_targets.v1.txt"
echo "wrote $ASSETS/repo_wide_context.v1.txt"
