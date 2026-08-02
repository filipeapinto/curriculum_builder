---
name: curriculum-concept-visualization
description: Compose conceptual, explanatory diagrams for teaching any subject — process and flow diagrams, cycles, concept maps, timelines, comparisons, layered structures, pedagogy-sequence graphics — producing a typst source file and a compiled landscape PNG that stays legible in print. Use this skill WHENEVER someone wants an idea made visual for a learner or a colleague: "draw me a diagram explaining how a lever works", "make a one-page explainer on photosynthesis", "visualise the 5E instructional model", "concept map for this unit", "timeline of the Industrial Revolution", "diagram the water cycle", "illustrate the steps of long division", "show the difference between mitosis and meiosis", "I need a picture for this lesson handout", or whenever a curriculum unit needs a graphic that explains rather than specifies. Also use it proactively when someone is about to have an image model draw an explanatory diagram — text inside generated images comes out garbled and unprintable, which is exactly what a teaching diagram cannot afford. SCOPE BOUNDARY: this skill draws ideas, not exact physical facts. If the picture has to be *correct about a real circuit* — wiring, breadboard hole positions, which pin joins which net, ratings a learner would build from — that belongs to `electronics-circuit-visualization`, which renders it deterministically from structured circuit data; route there rather than freehanding it here. Plans, runbooks and migration docs go to `plan-infographic`.
---

# Curriculum concept visualization

A teaching diagram earns its place by making a *relation* visible — something loops,
something branches, two things run in parallel, one thing gates another. Relations like
that are expensive to hold in a sentence and cheap to see in a picture. A diagram that
merely re-lists what the prose already said is decoration, and the reader learns to skip it.

So the first question is never "what shape should this be" but **what is the one thing a
reader should be able to say after looking at it that they could not say before.** Write
that sentence down. It becomes the subtitle, it decides the shape, and anything on the
page that does not serve it is competing with it.

## What this skill will and will not draw

Here you compose the typst yourself. That is the right arrangement for illustrative
content and would be the wrong one for a wiring diagram, and the difference is worth
being precise about: nothing on a concept page is a checkable assertion about a specific
physical object. "A lever trades force for distance" is a claim about the world that a
reader evaluates with their own knowledge. "The resistor sits between pin 13 and the
anode" is a claim about *this* build that a child will act on with a hand and a wire, and
being wrong about it is not a misunderstanding, it is a broken part.

So: **the moment a picture would assert an exact fact about a real physical system —
which pin, which hole, which terminal, which measured value — stop.** For circuits that
is `electronics-circuit-visualization`, which renders from structured data and audits
every string on the page back to a field in it. Say so and route the user there rather
than drawing an approximation; an approximate wiring diagram is worse than none, because
it looks authoritative.

Common shapes that stay inside this skill's boundary: how a process works, why a rule
holds, what the parts of an idea are and how they relate, the order things happened in,
how two approaches differ, how a lesson or curriculum is structured. Mixed asks are
normal — "explain the lesson *and* show the build" splits into a concept page here and a
build map there.

## Workflow

1. **Find the claim.** One sentence, in the user's subject, that the page must land. If
   the request is vague ("something on photosynthesis"), draft the sentence and say what
   you have chosen — it is faster to correct a sentence than a rendered page. If the
   content comes from a file (a unit, a lesson, a manifest), read it and take the
   substance from there rather than from memory.

2. **Pick the shape from the relation**, not from taste. A ring tells the reader the thing
   returns to its start; a timeline tells them the order is chronological. Choosing the
   shape carelessly puts a claim on the page you never checked.
   `references/layouts.md` has the table of relations to shapes, the exact signatures of
   every helper, and a worked skeleton — read it before composing.

3. **Compose the typst** in the output directory, importing the house style:

   ```typst
   #import "house.typ": *
   #show: page-setup
   ```

   `assets/house.typ` carries the page setup (A3 landscape, white, Helvetica, 200 ppi),
   a five-role colour palette, and the primitives — `title-block`, `panel`, `node`,
   `arrow`, `flow`, `vflow`, `cycle-diagram`, `radial-map`, `timeline`, `callout`,
   `chip`, `legend`, `footer-band`. Use them rather than rebuilding page geometry; they
   exist so your attention goes to the explanation instead of to millimetres.

4. **Build.** The script copies the house style next to your source (typst resolves
   imports relative to its own root, and the copy is also what lets the `.typ` still
   compile on someone else's machine):

   ```bash
   python3 scripts/build_diagram.py <dir>/<name>.typ
   ```

   It writes `<name>.png` beside the source and refuses the failures that are invisible
   in source and glaring in print: a page that silently split in two, a portrait sheet, a
   font nobody else has, a networked asset, a page that came out blank. Deliver the
   `.typ` and the `.png` together — the source is what makes the diagram editable next
   term instead of disposable.

5. **Open the PNG and read it.** This step is not optional and nothing can do it for you.
   The build checks the format; it cannot see two labels sitting on top of each other, a
   box that clipped its own text, an arrow pointing the wrong way round, or an
   explanation that simply does not land. Look at it as a reader who does not already
   know the answer, and fix what you find before handing it over. Three things worth
   checking deliberately, because they are easy to miss in your own work:
   - **Is the claim carried by the drawing or only by the prose?** See below.
   - **Is a band of the sheet empty?** Dead white space at A3 reads as something
     missing. Either the page wants another band or it wants `page-setup-half`.
   - **Would it survive the printer it is destined for?** If the user mentioned mono or
     a school printer, check that removing colour removes nothing.

## Conventions that keep a teaching page honest

These are small and they matter, because a printed page carries more authority than the
conversation that produced it.

- **Draw the relation; do not caption it.** The strongest temptation on a diagram is to
  put the interesting part in a paragraph beside the picture — "the model also loops
  back", "these two run in parallel" — and let the drawing stay tidy. Readers believe the
  drawing. If a relation is worth stating, it should be a mark on the page: a return
  chord on the ring (`returns:` on `cycle-diagram`), a second arrow, a struck-through
  version of the wrong shape next to the right one. A prose panel explaining what the
  diagram would have shown is the most common way a good page falls short of its subject.
- **Say what the page is.** `footer-band` exists for this: *"Conceptual diagram ·
  illustrative, not to scale"*. A diagram that does not admit it is conceptual invites
  someone to measure off it.
- **Never let colour be the only carrier.** Tints photocopy to near-identical greys, and
  a lot of teaching material is printed in mono on a tired school machine. Every
  distinction the page makes should also be readable from position, a label, a line
  style, or a numbered band title. When the user mentions black and white, go further:
  keep to line art and one or two very light washes, and check the render in greyscale
  before delivering.
- **Do not imply precision you are not asserting.** Evenly spaced timeline ticks show
  order, not duration. Box sizes are layout, not magnitude. If a proportion is the point,
  say the number in words rather than encoding it in geometry you did not compute.
- **Name the misconception.** The most valuable box on a teaching page is often the
  `callout` that says where learners go wrong — it is the part that is genuinely hard to
  get from the textbook, and it is why a teacher keeps the handout.
- **Label the arrows.** An unlabelled arrow says "and then". A verb on it says what
  happens in between, which is usually the thing being taught.
- **Spend colour on meaning.** Readers assume two boxes of the same colour are the same
  kind of thing. Three strands is usually the ceiling; past that, colour stops encoding
  anything and becomes noise.
- **No emoji, no downloaded assets.** Emoji fall back to whatever font the reading machine
  has, which is how a handout arrives as a row of empty boxes; a networked image is a
  diagram with an expiry date.

## When the subject is not yours to invent

If the diagram would need facts you do not have — dates you are unsure of, a mechanism
you would be guessing at, the structure of a unit you have not read — get them from the
source or ask. This skill has no audit trail to catch an invented fact, which is exactly
why the material has to be right on the way in. Being wrong in a confident, printable,
classroom-ready format is the failure mode worth avoiding here.
