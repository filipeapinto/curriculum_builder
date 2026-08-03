# Output contracts

Three artifacts, all in one output directory (default
`docs/research/<scan-name>/`).

## 1. Thread files — `<thread-name>.md`

One per research thread, snake_case name describing the reviewer archetype
(e.g. `multi_agent_llm_judge_review.md`,
`physical_safety_review_hands_on_stem.md`). Use
`assets/thread_template.md`.

Four sections, in order:

- **Why this thread** — the specific observed defect that motivated it, with
  the concrete evidence (quote the QA report, name the check that was inert,
  cite the file). This is what separates a grounded scan from a literature
  review.
- **Findings** — bolded one-line claim, then the evidence and the named
  source, then an explicit "implication for this pipeline" line. Attribute
  every claim to a source by name and identifier inline; a paragraph with no
  attribution reads as your opinion and will be treated as such.
- **Sources** — full citations with URLs, under a heading that states these
  were all fetched and verified.
- **Discarded** — every source rejected during this thread and why. If
  nothing was discarded, say so; an empty discard section on every thread is a
  signal that verification was not actually performed.

## 2. Recommendation array — `sota_agents.v<N>.json`

A JSON array. Pick the next unused `N` in the output directory rather than
overwriting a previous scan — comparing scans over time is a large part of why
this is re-runnable.

Every element has exactly these six keys, all strings except `sources`:

```json
[
  {
    "agent": "Name of the recommended reviewer agent",
    "function": "What it actually does: what it reads, what it checks, what it emits, and what it blocks on. Concrete enough to implement from.",
    "what_makes_it_sota": "Why this reflects current best practice, citing the specific findings and identifiers from the thread files that support it.",
    "role_in_curriculum_builder": "Where it plugs into this pipeline: which gate, before/after which existing check, on which input.",
    "issues_resolved": "The specific defect in the reviewed output or QA report this addresses. Quote it.",
    "sources": ["https://... (every URL logged as kept in action_log.jsonl)"]
  }
]
```

Field-by-field expectations:

- `agent` — a role name, not a feature name. If it does not read like
  something you could staff, it is probably a check rather than an agent.
- `function` — must distinguish this agent from its neighbours. If two
  entries' `function` fields are interchangeable, merge them.
- `what_makes_it_sota` — cite identifiers (arXiv numbers, vendor names). "Best
  practice suggests" with no attribution is not an answer to this field.
- `role_in_curriculum_builder` — must name a real insertion point in the
  pipeline you read. If you do not know the pipeline's gate structure, read it
  before filling this in; a guessed integration point makes the whole
  recommendation unusable.
- `issues_resolved` — must quote or precisely reference an observed defect.
  If you cannot, this agent is speculative and should be dropped or clearly
  marked as such.
- `sources` — non-empty, and every URL must appear in `action_log.jsonl` in
  an entry whose decision is to keep it. The validator enforces this.

## 3. Action log — `action_log.jsonl`

One JSON object per line, appended in the order actions were taken. Every
entry has `ts` (ISO 8601, UTC) and `action`. Other keys vary by action type.

Action types used by this methodology:

| `action` | Typical keys |
|---|---|
| `read_file` | `path`, `purpose` |
| `bash` | `command`, `purpose` |
| `web_search` | `query`, `purpose`, `result_count`, optional `note` |
| `web_fetch_verify` | `url`, `claim`, `result`, `decision` |
| `analysis` | `note`, plus whatever structured fields the judgement produced (e.g. `research_threads_planned`) |
| `write_file` | `path`, `purpose`, optional `sources_cited`, `sources_discarded_in_file` |
| `final_check` | `note`, `sources_verified_kept`, `sources_discarded` |

`web_fetch_verify` entries are load-bearing: `result` carries the verdict
(see `references/source_verification.md`) and `decision` carries keep or
discard. The validator reads `decision` to determine whether a citation was
earned, so write decisions that begin with `keep` or `DISCARD` rather than
freeform prose.

Use `scripts/log_action.py` to append entries; it timestamps them and
guarantees each line is valid JSON.
