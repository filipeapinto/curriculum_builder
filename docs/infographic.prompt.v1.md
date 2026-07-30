# Infographic build prompt — "How the curriculum generator works"

Produce one polished landscape PNG explaining how a single meta-prompt builds a
generator, and how that generator then produces every lab in the curriculum and a workbook
without a human watching.

## Deliverable

- Path: `docs/how_it_works.png`, with its typst source beside it as
  `docs/how_it_works.typ` — in `docs/`, next to `how_it_works.md`, **not** in
  `policy/`. `policy/` holds declared run inputs that the meta prompt treats as
  immutable; this diagram is documentation about the system, authored before a run
  and never written by one.
- Landscape, at least **2400 × 1600 px**, white background, print-legible at A3.
- Self-contained. Only system fonts — use **Helvetica** (it is present; a missing
  font is a hard failure in typst). No network fetches, no external images.
- Build it with `typst` (installed at `/opt/homebrew/bin/typst`):
  `typst compile <file>.typ <out>.png --format png --ppi 200`.
- Nothing else in the repository may be modified.

## The story, in three bands

The reader must finish able to answer: *what runs once, what repeats per lab, and why
can I walk away?*

### Band 1 — BUILD (runs once, a human starts it)

```
INPUTS                          META-PROMPT                    OUTPUT
curriculum manifest ← defines WHICH labs and HOW MANY                                   templates_v7/
lab.schema.v3.json         →    meta_curriculum_prompt    →      controller (python)
component_lab_template            .prompt.v5.md                  worker prompts
policy/routing/ (model policy)                                   schemas
legacy v3 generator (evidence)   "builds the factory,             tests
                                  never the product"              golden L01
```

Label this band clearly: **the meta-prompt writes the generator, not the
curriculum.** It produces exactly one finished lab (L01) as proof.

### Band 2 — PROVE (six gates, in order, all must pass)

A left-to-right chain of six gates. Each gate is a box with its name and a one-line
"what it proves". A padlock or barrier sits after gate 6: **only when all six pass
is the full-run command released.**

| Gate | Proves |
|---|---|
| 0 · Logger | append-only, IDs monotonic, every start paired — built and proven *before anything else exists* |
| 1 · Static (every lab) | every advertised check actually asserted, not just named |
| 2 · Deterministic | state machine, checkpoints, hashes, resource limits |
| 3 · Simulated (every lab) | revision, retry, block, failure, interrupt/resume — with fake workers |
| 4 · Live capability | real worker call, real image job, real PDF render |
| 5 · Golden L01 | one complete lab, reviewed, rendered, page-inspected, accepted |

Show a failure arrow from any gate looping back to *revise → re-run affected gates*,
capped at **6 revision cycles**.

### Band 3 — GENERATE (repeats once per lab, unattended)

The per-lab pipeline, as a loop. Show it compactly — five clusters, not 25 boxes:

```
PLAN → 4 isolated plan reviews → decide
     → RESEARCH · CIRCUIT · EXPERIMENT        (machine-readable circuit data)
     → CHILD TEXT · ADULT GUIDE · VISUALS     (all generated from that same data)
     → 4 isolated QA reviews → decide
     → PDF render → page inspection → ACCEPT
```

Then: **accept → advance to the next lab. Never advance without acceptance.**
After the last lab: assemble workbook → 4 workbook reviews → final PDF → done.

Draw the loop as **L01 … LN** or **lab 1 … lab N**, never as a fixed 35. Add a small
callout on the curriculum input: *"the manifest decides how many labs exist —
nothing downstream hardcodes a count."* Today it holds 35; that is data, not
architecture.

Mark two properties visually inside this band:
- **Reviewers are isolated** — 8 per lab, none can read another's verdict; show it
  as separate sealed lanes, not a committee.
- **Every lab must validate against `lab.schema.v3.json`** — seven blocks: identity,
  pedagogy, sequence (5E), electronics, content, safety, visuals.

## Side panel — "Why it can run unattended"

A distinct column or footer strip. Six short items, each one line:

- **Checkpoint after every step** — hashes recorded; resume restarts at the first
  invalid checkpoint and never rebuilds accepted work.
- **Bounded retries** — malformed output once, transient failure once, then stop.
- **Targeted revision** — only the named failed artifact is regenerated, never the
  whole lab.
- **Code decides, models write** — Python owns state, routing, aggregation and every
  acceptance decision; no model ever advances a state.
- **Every action logged** — `ACT` records start and completion in pairs; `EXCE`
  records failures. Zero unpaired starts is a release gate.
- **It stops itself** — drift detection halts the run on scope creep, weakened
  tests, misreported evidence, or two cycles without progress.

Correct that last bullet's typo when you draw it: the failure record prefix is
**`EXEC`**, not `EXCE`.

Close the panel with the three, and only three, ways a run can end:

`META_ACCEPTED` · `META_SYSTEM_FAILURE` · `META_DRIFT_STOP`

## Design direction

- Calm, technical, editorial — closer to a well-set engineering diagram than a
  marketing graphic. No clip art, no gradients-for-decoration, no drop shadows.
- One restrained accent colour for the BUILD band, a second for GENERATE, neutral
  greys for structure. Gates in a third colour that reads as "checkpoint".
- Strong typographic hierarchy: band titles large, node labels medium, annotations
  small. Generous white space; let the three bands breathe.
- Arrows must be unambiguous about direction and about which are *failure* paths
  (dashed or coloured differently, labelled).
- Include a one-line subtitle under the main title: *"One prompt builds the
  generator. The generator builds every lab the curriculum names. Nobody watches."*
- Bottom-right, small: `curriculum_creator · meta prompt v5 · lab schema v3`

## Acceptance

The PNG is done when a reader who has never seen this project can, in under a
minute, state the difference between the meta-prompt and the generator, name what
must pass before the full run is allowed, and give two reasons the run is safe
to leave alone.
