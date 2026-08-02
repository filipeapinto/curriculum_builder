# Layout archetypes

Read this when you have a claim to land and need the shape that carries it, or when
you need the exact signature of a helper in `assets/house.typ`.

Contents:
1. [Choosing the shape](#choosing-the-shape)
2. [The helpers](#the-helpers)
3. [Composing a page](#composing-a-page)
4. [Sizing that survives print](#sizing-that-survives-print)
5. [Worked skeleton](#worked-skeleton)

---

## Choosing the shape

The shape of a diagram is itself a claim. A reader infers from a ring that the thing
comes back around, from a timeline that the order is chronological and the gaps are
real, from a hierarchy that the lower boxes are *kinds of* the upper one. Picking the
shape by what looks nice puts a claim on the page you never checked.

| The relation you are explaining | Shape | Helper |
|---|---|---|
| A happens, then B, then C — one direction, an end state | linear flow | `flow` |
| Same, but the steps have long labels or there are more than six | vertical flow | `vflow` |
| It returns to its own beginning; doing it again is the point | cycle | `cycle-diagram` |
| One idea and the things that belong to it, no order between them | hub and spokes | `radial-map` |
| Events in time where *when* matters | timeline | `timeline` |
| Two ways of doing it, and the difference is the lesson | two columns | `grid` of `panel`s |
| Layers, where each rests on the one below | stacked bands | `panel`s stacked, or `vflow` |
| A whole and its parts, where the parts are simultaneous | labelled parts | `radial-map`, or hand-placed |
| A rule with conditions attached | flow plus `callout` | `flow` + `callout` |

If a candidate shape would tell the reader something you cannot defend — a circle for a
one-way process, a timeline for events whose order is contested — pick the plainer one.

**Sequence, and the thing a diagram is for.** A picture that just re-lists what the prose
already said is a decoration. The reason to draw is that some relation is hard to hold in
a sentence: something loops, something branches, two things run in parallel, one thing
gates another. Find that relation first and let it choose the shape.

---

## The helpers

All from `assets/house.typ`. Import as `#import "house.typ": *` and apply
`#show: page-setup` (or `page-setup-half` for a smaller sheet).

**Colours.** `ink`, `muted`, `rule-c`; five role pairs `primary`/`primary-bg`,
`support`/`support-bg`, `accent`/`accent-bg`, `caution`/`caution-bg`, `alert`/`alert-bg`.
Use a colour for a *kind of thing* and keep it consistent down the page — the reader will
assume two blue boxes are the same sort of object whether or not you meant it. Three
strands is usually the ceiling; past that the colour stops encoding anything.

```typst
#title-block("How a lever works", subtitle: "force, distance and the trade between them")

#panel([1 · THE PARTS], body, color: primary, bg: primary-bg)

#node("Fulcrum", detail: "the pivot", color: primary, bg: white, height: 24mm, size: 10pt)

#arrow(label: "and then")        // horizontal, label optional but usually worth it
#arrow-down(label: "if it fails")

#chip("misconception", color: alert)

#callout("Where learners go wrong", "You do not get work for free.", color: alert, bg: alert-bg)

#legend(((primary, "the lever"), (support, "the load"), (alert, "misconception")))

#footer-band("Conceptual diagram · illustrative, not to scale", right-text: "Year 7 · forces")
```

**`flow(steps, arrows: (), color:, bg:, height: 24mm, gap: 11mm)`**
`steps` is an array of `(title, detail)` pairs; `arrows` is one shorter and labels the
gaps. An unlabelled arrow says only "and then"; a labelled one says what actually happens
in between, which is usually the part the learner did not already know.

**`vflow(steps, arrows: (), color:, bg:, height: 17mm)`** — the same, stacked.

**`cycle-diagram(steps, size: 148mm, node-w: 48mm, node-h: 24mm, color:, bg:, center-label: none, center-detail: none, returns: (), return-color: caution)`**
Nodes evenly around a ring, clockwise from the top, with an arrow on the ring between
each pair. Put the name of the cycle in `center-label`. Give `size` at least `3 × node-w`
or the nodes will crowd the centre.

`returns` draws the paths *back* — an array of `(from-index, to-index, label)`,
zero-based — as dashed chords with arrowheads across the ring, labelled near the end they
start from. Reach for it whenever the loop is the reason you chose a ring: a cycle drawn
as five boxes and five forward arrows still reads as a checklist bent into a circle, and
the chords are what make it stop reading that way. Three or four chords is the ceiling
before the middle of the ring turns to noise, and with chords in play keep `center-detail`
short or drop it, since every chord passes near the centre.

```typst
#cycle-diagram(
  (("Engage", ".."), ("Explore", ".."), ("Explain", ".."), ("Elaborate", ".."), ("Evaluate", "..")),
  size: 150mm, node-w: 42mm, center-label: "5E",
  returns: (
    (2, 1, "the account exposes a gap"),
    (4, 2, "a misconception, not a grade"),
  ),
)
```

**`radial-map(center-label, spokes, size: 150mm, hub-w: 52mm, node-w: 46mm, node-h: 21mm, color:, bg:)`**
`spokes` is an array of `(title, detail)`. Give `size` at least `3.2 × node-w`, otherwise
the spoke lines disappear under the boxes and the hub reads as unconnected.

**`timeline(events, color:, height: 62mm, label-w: 46mm)`**
`events` is an array of `(when, what)` or `(when, what, detail)`. Labels alternate above
and below the axis so long ones do not collide. Ticks are evenly spaced — the axis shows
*order*, not duration, so do not use it where the size of the gaps is the point.

---

## Composing a page

A page usually reads as two to four horizontal bands, each a `panel` with a numbered
title. Numbering the bands (`1 · THE PARTS`) tells the reader where to start, which a
grid of equal boxes never does.

```typst
#title-block(..)
#v(4mm)
#panel([1 · ..], ..)
#v(4mm)
#grid(columns: (1fr, 1fr), column-gutter: 4mm, panel([2 · ..], ..), panel([3 · ..], ..))
#v(4mm)
#panel([4 · ..], ..)
#v(1fr)                       // pushes the footer to the bottom edge
#footer-band("..", right-text: "..")
```

`#v(1fr)` before the footer only works if everything above already fits; if the page
overflows, the build fails and tells you.

---

## Sizing that survives print

The default sheet is A3 landscape, which is 3307 × 2339 px at 200 ppi. It is generous —
about four bands. Signs you have the wrong amount of content:

- **Overflow to a second page.** The build refuses it. Cut a band; do not shrink the type
  below 7pt to make it fit, because the page's job is to be readable across a classroom.
- **Half the sheet empty.** Switch to `page-setup-half` (A4 landscape). Whitespace at that
  scale reads as something missing rather than as calm.

Type sizes that hold up: title 25pt, panel titles 11.5pt, node titles 9.5–11pt, detail
7.5–8.5pt, footer 7.6pt. Below 7pt nothing is legible in print, and the helpers already
sit near the floor.

Keep to Helvetica and skip emoji — an emoji falls back to whatever font the reading
machine has, which is how a diagram arrives as a row of empty boxes.

**Strings are not content.** `"a -- b"` and `"*bold*"` print literally, because typst only
applies smart punctuation and markup inside content brackets. Every helper accepts content,
so write `[a — b]` and `[*bold*]` rather than a quoted string wherever the text is prose a
reader will see. Quoted strings are fine for short labels with no punctuation.

**Mono printing.** The five washes are close in lightness, so `alert-bg` and `support-bg`
photocopy to nearly the same grey and any meaning carried only by hue is gone. Numbered
band titles, position and words survive; colour may reinforce them but must not be the
only carrier. If the user names a mono or school printer, drop to line art on white with
at most one or two washes, keep strokes dark, and check the result:

```bash
python3 -c "from PIL import Image; Image.open('out.png').convert('L').save('out_mono.png')"
```

Then look at `out_mono.png` and confirm nothing was lost. A `legend` of colour swatches is
the one element that cannot survive this — leave it out of a mono page rather than
printing four indistinguishable grey squares.

---

## Worked skeleton

```typst
#import "house.typ": *
#show: page-setup

#title-block(
  "How a lever multiplies force",
  subtitle: "A longer effort arm buys force by spending distance — the work is unchanged",
)
#v(4mm)

#panel([1 · THE FOUR PARTS], align(center)[
  #radial-map("Lever", (
    ("Fulcrum", "the fixed pivot"),
    ("Effort", "the force you apply"),
    ("Load", "the force you overcome"),
    ("Arms", "distance from pivot to each force"),
  ), size: 120mm, node-w: 34mm)
])
#v(4mm)

#panel([2 · THE TRADE], flow((
  ("Push further from the pivot", "longer effort arm"),
  ("Your force is multiplied", "effort arm ÷ load arm"),
  ("But your end travels further", "distance paid back"),
), arrows: ("so", "and so")), color: support, bg: support-bg)
#v(4mm)

#callout(
  "Where learners go wrong",
  "A lever does not create energy. The work you put in equals the work you get out, "
    + "minus friction — a lever only changes how that work is split between force and distance.",
  color: alert, bg: alert-bg,
)
#v(1fr)
#footer-band(
  "Conceptual diagram · illustrative, not to scale · no measurements asserted",
  right-text: "simple machines · forces",
)
```
