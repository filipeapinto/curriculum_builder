# Making the page worth reading

A system guide fails in two directions. The familiar one is thinness — the
document that skips deployment and recovery. The other one is a wall: thirteen
identical sections of grey prose and eight-column tables, technically complete,
which the reader abandons on section three and reconstructs from the repo
instead. Depth that nobody reads bought nothing.

HTML is here for the second failure. Read this when a page is coming out
uniform, when you are deciding whether a diagram earns its place, or when you
are about to invent a layout the template does not have.

## Contents

- [The reader you are designing for](#the-reader-you-are-designing-for)
- [Page rhythm](#page-rhythm)
- [Choosing a diagram](#choosing-a-diagram)
- [Making a diagram carry evidence](#making-a-diagram-carry-evidence)
- [Engagement that is not decoration](#engagement-that-is-not-decoration)
- [Static-first, and why](#static-first-and-why)
- [Accessibility as accuracy](#accessibility-as-accuracy)
- [Anti-patterns](#anti-patterns)

## The reader you are designing for

Three people open this file, and the page has to serve all of them without
three versions of itself.

| Reader | Arrives | Needs in the first 15 seconds |
|---|---|---|
| On-call operator | Mid-incident, phone or laptop, possibly no network | What healthy looks like, what they may restart, what they must not touch |
| Maintainer | About to change a node or a route | The graph, the contracts around the thing they are changing, what state survives |
| Reviewer | Deciding whether to approve or trust | The boundary, the trust surfaces, and which claims were actually verified |

This is why the template opens with at-a-glance cards, a stop-and-escalate box,
and the evidence legend before any prose: each of the three finds their footing
above the fold, and none of them has to scroll to section 12 to discover the
thing that would have stopped them making it worse.

## Page rhythm

Vary the texture deliberately. A reader skimming a page navigates by shape
before they navigate by heading, so if every section has the same shape they
have nothing to steer by.

- **Open with orientation, not throat-clearing.** The lede is one or two
  sentences the reader could repeat back to a colleague.
- **Alternate the form.** Diagram → contract table → prose consequence →
  callout. Three tables in a row are a signal you are transcribing evidence
  rather than explaining it.
- **Put the sharp thing in a callout.** Stop conditions, verified gaps, blind
  spots and prohibited actions each get a box because a reader must not be able
  to skim past them. Use them for the four or five genuinely sharp facts; a page
  where everything is boxed has nothing emphasised.
- **Hide reference bulk behind `<details>`, never findings.** A 90-row source
  register collapses. A verified gap does not.
- **Let sections be uneven.** The system's real complexity lives in two or three
  places. Sections that match that shape read as written; thirteen equal
  sections read as filled in.

## Choosing a diagram

The test is not "is there a graph" — it is "does a relationship here cost the
reader more in prose than in pixels". Three archetypes cover almost everything a
system guide needs, and `scripts/diagram_svg.py` renders each from a small JSON
spec (`--print-schema` shows the format).

| Reader question | Archetype | Where it usually goes |
|---|---|---|
| What runs, in what order, and where does it go wrong? | `flow` | Graph behavior |
| What are the parts, and which side of a boundary is each on? | `stack` | Architecture, deployment, trust boundaries |
| Who does what to whom, in what order? | `sequence` | Operations and recovery, external handoffs |

Two or three diagrams in a guide is usually right. Each additional one costs a
maintenance burden forever, so it has to answer a question the others do not:
four pictures of the same pipeline is four things to update and one thing
understood.

**Draw the failure paths.** A flow diagram showing only the happy path is worse
than no diagram — it tells a reader in an incident that they are off the map.
Repair and failure edges are their own edge kinds, and the renderer routes
back-edges through a gutter beneath the flow precisely so the loops stay
legible instead of scribbling across the forward path.

## Making a diagram carry evidence

A diagram is read as verified fact unless it says otherwise, which is why the
figure caption carries scope, source and evidence status, and why the renderer
puts them there automatically.

- The diagram renders the evidence. It may not add a node, an edge, a control,
  a bound or a confidence level that the sources do not state. An arrow you
  drew because it "must" be there is an inference — label it as one.
- Mixed evidence in one picture is fine and common: nodes read from a graph
  definition are `declared`; the path a trace actually exercised is `observed`.
  Per-node evidence badges exist for exactly this.
- Every figure ships a text equivalent listing the same nodes and edges. It is
  what a screen reader announces, what survives a greyscale print, and what a
  reviewer diffs when the graph changes.
- If the renderer reports overlap, clipping or an orphan node, that is a finding
  about the spec, not a nuisance. An orphan node in particular usually means an
  edge exists in the system that you have not found in the evidence.

## Engagement that is not decoration

Engagement here means the page rewards attention, not that it moves.

- **Answer the question in the caption.** "Run path" is a title. "Validation can
  send a draft back to drafting twice, then the run terminates" is a takeaway,
  and it is what the reader will remember.
- **Make the numbers concrete.** "Bounded retries" is furniture. "Max 2, then
  `terminal_failed`" is information.
- **Use colour as reinforcement, never as the message.** Every distinction the
  page makes — evidence state, node kind, edge kind — also carries a word, a
  border style or a shape. Print it in greyscale before you believe it.
- **Write the consequence, not just the mechanism.** "Checkpoints are written
  after each node" is the mechanism; "a crash mid-node replays that node from
  the last checkpoint, so a node with side effects runs twice" is why anyone
  cares.

## Static-first, and why

One self-contained file. No CDN, no remote font, no remote image, no analytics.
The guide is read during the incident it documents, on a laptop that may have no
route out, and a stylesheet that fails to load takes the page's structure with
it.

JavaScript may enhance; it may not carry content. `<details>` gives collapsing,
`position:sticky` gives the nav, CSS `@media print` gives the printable copy —
none of it needs a script. If you add one, the page must still be complete and
navigable with it off, and the print stylesheet must expand what the reader
would otherwise print collapsed.

Diagrams go inline as SVG rather than linked files: one file that can be
emailed, dropped in a ticket, or opened from a USB stick during an outage.

## Accessibility as accuracy

These are the same requirement. A guide whose meaning lives in colour, in
unlabelled images, or in a diagram with no text equivalent is a guide that is
*inaccurate for some readers* — it asserts less than it appears to.

Minimums the verifier enforces: `lang` on `<html>`, a viewport meta, a real
`<title>`, alt text on every image, `role="img"` plus a `<title>` on inline SVG,
every visual inside a `<figure>` with a `<figcaption>` and a text equivalent.
Beyond that, keep contrast comfortable in both colour schemes, keep the heading
levels sequential, and keep tables to the columns a reader actually needs — a
14-column table is inaccessible to everybody, sighted or not.

## Anti-patterns

- **The template, filled in.** Placeholders left in, sections padded to look
  even, `<!-- FILL -->` shipped. The verifier fails on the last one; the first
  two need you.
- **Decorative diagram.** A picture that repeats the table above it. Delete one.
- **Colour-coded severity with no legend.** Red means whatever the reader
  assumes it means.
- **The tour.** Sections ordered by how you explored the repo instead of by what
  the reader needs first.
- **Confident prose over a gap.** The most expensive failure in this whole
  skill: smooth writing where evidence ran out. An empty section labelled
  `unknown` is worth more than a full one that was imagined.
