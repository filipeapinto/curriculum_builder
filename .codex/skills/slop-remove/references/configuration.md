# Configuration

Use configuration to change style preferences, not factual or contractual preservation.

## Sources and precedence

Resolve settings in this order, highest first:

1. Binding repository and artifact contracts. These are not style configuration and cannot be overridden here.
2. Explicit preferences in the current user request, within those contracts.
3. A configuration file at the exact path supplied by the user.
4. `<repo-root>/policy/slop-remove.yaml`, when it exists.
5. `default-policy.yaml` in this directory.

Do not search home directories or unrelated repositories for implicit configuration. Report which non-default source was applied.

Merge mappings recursively. Replace scalar values. Replace lists rather than appending them, except `exempt_terms`, which is the ordered union of defaults and overrides with duplicates removed. Reject unknown top-level keys and invalid value types; do not guess.

## Supported configuration

```yaml
version: 1

default:
  mode: review                 # review | rewrite
  voice: restrained            # neutral | restrained | warm | natural
  preserve_structure: true     # true | false, unless a contract fixes structure
  first_person: false          # true | false
  opinions: false              # true | false
  sentence_complexity: short   # short | contextual | unrestricted

patterns:
  filler: remove               # remove | review | allow
  vague_attribution: require_named_source
  passive_voice: contextual

punctuation:
  em_dash: contextual          # avoid | contextual | allow
  heading_case: preserve_contract

artifact_profiles:
  learner_prose: learner_prose

exempt_terms:
  - domain-specific term
```

All named pattern entries accept `remove`, `review`, or `allow` unless the default file demonstrates a more specific value such as `require_named_source`, `prefer_evidence`, `contextual`, or `allow_if_defined_or_exact`.

An artifact-profile value names a section in `artifact-profiles.md`. Do not accept an unknown profile name. Inline user instructions may adjust a profile for the current task without changing the stored configuration.

## Non-configurable rules

Configuration cannot authorize changes to facts, numbers, units, dates, negations, modal force, scope, citations, evidence boundaries, provenance, identifiers, schema values, controlled status values, safety instructions, acceptance criteria, or immutable history. It also cannot grant permission to edit files or create a new artifact version.

If a requested preference conflicts with this floor, preserve the protected content and disclose the skipped preference.
