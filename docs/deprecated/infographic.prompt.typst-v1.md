# Infographic build prompt — current curriculum pipeline

Produce a polished landscape PNG that explains the active contract in
`meta_prompt/curriculum.prompt.v1.md` and distinguishes required runtime behavior from
what the repository currently implements.

## Deliverable

- `docs/how_it_works.png`, with `docs/how_it_works.typ` beside it.
- Landscape, at least 2400 × 1600 px, white background, print-legible at A3.
- Helvetica only; no network assets.
- Build with Typst at 200 ppi.
- Preserve superseded versions in `docs/deprecated/`; never delete them.

## Story

### Band 1 — BOUNDARIES

Show three inputs flowing into the active prompt:

```text
ENGINE (immutable) + CURRICULUM (immutable) + OUTPUT_ROOT (only write target)
                              ↓
                 curriculum.prompt.v1.md
```

State clearly: **the prompt runs the supplied curriculum directly; it no longer builds
a curriculum-specific generator.** The prompt derives `ENGINE`, requires the other two
paths, never names a subject, and never hardcodes a unit count.

### Band 2 — ONE UNIT

Show this flow:

```text
manifest unit → retrieve primary sources → assemble domain block
→ curriculum verifier → generate six engine blocks
→ generic deterministic checks → one cross-family judge → checkpoint
```

Show the seven-block unit split: six engine blocks (`identity`, `pedagogy`, `sequence`,
`content`, `safety`, `visuals`) plus the curriculum-owned `domain` block.

Call out:

- every rendered subject fact points back to one value in `domain`;
- the curriculum supplies its domain schema, deterministic verifier, and fixtures;
- code decides and models write;
- outputs are drafts pending downstream human review.

### Band 3 — PROVE, THEN SCALE

Show the six runtime gates in order: Logger, Static, Deterministic, Simulated, Live
capability, Golden unit. Only after all six pass may the full-run command be written.
Then show: remaining declared units → assembled product → render → page inspection →
audited result.

Add a prominent current-state panel:

**TODAY: contracts and repository gates exist; runtime does not.**

- phase 4: 30 repository gates pass;
- phase 5: 38 repository gates pass;
- no controller, logger, renderer, source-fetching run, or live route exists (`RT-5`);
- zero generated units exist (`RT-7`);
- static and fixture coverage must not be described as generated-unit coverage.

## Footer

Use: `curriculum_builder · curriculum prompt v1 · curriculum schema v5 · lab schema v4`

## Acceptance

A new reader should understand the read/write boundary, the engine/domain split, the
per-unit flow, the six proof gates, and the difference between repository readiness and
an executed curriculum run.
