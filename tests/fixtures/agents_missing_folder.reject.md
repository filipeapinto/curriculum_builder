# Negative fixture for FR-P1-DOC

A retention table that answers every top-level folder except `docs/`. The gate must
report `retention-unanswered:docs` rather than inferring an answer — leaving a
folder's retention to inference is how three conventions accumulated in the first
place.

## Retention

| Folder | Keeps a `deprecated/`? | Why |
|---|---|---|
| `policy/` | yes | manifests are superseded in place and the prior version is history |
| `curricula/` | yes | a retired curriculum is evidence, not a live input |
| `schemas/` | yes — gated | a schema may enter only when nothing references it |
| `meta_prompt/` | yes | a superseded prompt is read by nobody but explains a decision |
| `tests/` | no | a gate that no longer applies is deleted with the rule it proved |
| `plans/` | yes | plan and prompt pairs below the active version live there |
