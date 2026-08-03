# <CHECK-ID> — <Agent name from the recommendation>

**Inventory** `<policy/checks.v1.yaml | curricula/<name>/checks.v1.yaml>`, category `<key>`
**Owner** `<path that states the rule>`
**Method** `<tree|parse|schema|text|mapping|declaration|execution>` · **Stage** `<stage>`
**Execution** `<verified_by: FR-… | deferred: RT-…>`
**Verdict** `<blocks | flags and never blocks | flags and escalates to a named human>`

## What it asserts

<One falsifiable claim about a named subject — the same claim as the
inventory's `asserts`, in full. If it flags rather than blocks, say so here
too, so this file cannot be read as claiming more authority than the check has.>

## The defect it exists to catch

<From the recommendation's `issues_resolved`: what actually shipped wrong,
how systemic it was, and which existing check was supposed to catch it.
Name the failure-ledger id and the reject fixture that reproduces it.>

- Failure ledger: `<A-id / B-id>` in `policy/failures.v1.yaml`
- Reject fixture: `tests/fixtures/<slug>.reject.<ext>`
- Accept fixture: `tests/fixtures/<slug>.accept.<ext>`

## Verdict design

<Why deterministic or judged; why it blocks or flags; why this stage; why
executed or deferred. Someone will later ask why this agent does not block —
answer it here rather than making them re-derive it. If a model call is
involved, state where it fits in `policy/limits.v1.yaml`.>

## Reconciliation with existing decisions

<Only when the recommendation argues against something this repo already
decided and recorded. State what the recommendation argues, what the repo
decided and where that is written, which evidence won, and why. Delete this
section when there is no conflict — an empty "no conflicts found" heading
reads as if the question was never asked.>

## Provenance

Carried verbatim from `<docs/research/<scan>/sota_agents.v<N>.json>`,
recommendation "<agent name>", produced by the `learning-agent-research` scan of
`<date>`. **These sources were fetched and verified by that scan and have not
been re-checked here** — this factory does no research. Re-verification, if
the claims start to matter, is a re-run of that skill.

### Why this is state of the art

<`what_makes_it_sota`, verbatim.>

### Sources

- <url>
- <url>

## Change log

- `<YYYY-MM-DD>` created from recommendation "<agent name>".
