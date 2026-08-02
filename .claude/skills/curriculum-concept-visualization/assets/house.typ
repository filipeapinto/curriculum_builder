// House style for curriculum concept diagrams.
// Import with:  #import "house.typ": *   then  #show: page-setup
// Everything here is layout only. What the page *says* is yours to compose.

// ---------------------------------------------------------------- palette
// Five roles, each with an ink colour and a wash. Use role by meaning, not
// by taste: a reader who sees the same colour twice will assume the two
// things are the same kind of thing, so spending a colour on decoration
// costs you the ability to mean something with it later.
#let ink = rgb("#17202a") // body text
#let muted = rgb("#5f6b76") // captions, secondary detail
#let rule-c = rgb("#c8d0d7") // hairlines, axes

#let primary = rgb("#174a7e") // the main chain of the explanation
#let primary-bg = rgb("#eaf2f9")
#let support = rgb("#146447") // the secondary or contrasting strand
#let support-bg = rgb("#e9f5ef")
#let accent = rgb("#6b3fa0") // a third strand, used sparingly
#let accent-bg = rgb("#f1ecf8")
#let caution = rgb("#875b00") // conditions, gates, "only if"
#let caution-bg = rgb("#fbf3df")
#let alert = rgb("#9b352d") // failure, misconception, stop
#let alert-bg = rgb("#faecea")

// ------------------------------------------------------------------ page
// A3 landscape at 200 ppi -> 3307 x 2339 px. White, Helvetica, no network.
#let page-setup(doc) = {
  set page(width: 420mm, height: 297mm, margin: 11mm, fill: white)
  set text(font: "Helvetica", size: 9.5pt, fill: ink)
  set par(leading: 0.62em)
  doc
}

// A half-size sheet for a single simple idea. A page with four boxes on it
// should not be A3; the whitespace reads as something missing.
#let page-setup-half(doc) = {
  set page(width: 297mm, height: 210mm, margin: 9mm, fill: white)
  set text(font: "Helvetica", size: 9.5pt, fill: ink)
  set par(leading: 0.62em)
  doc
}

// --------------------------------------------------------------- heading
#let title-block(title, subtitle: none) = align(center)[
  #text(size: 25pt, weight: "bold")[#title]
  #if subtitle != none [
    #v(1.8mm)
    #text(size: 11.5pt, style: "italic", fill: muted)[#subtitle]
  ]
]

// ---------------------------------------------------------------- pieces
#let panel(title, body, color: primary, bg: primary-bg) = box(
  width: 100%,
  fill: bg,
  stroke: 1pt + color,
  radius: 3pt,
  inset: 4.5mm,
)[
  #text(size: 11.5pt, weight: "bold", fill: color)[#title]
  #v(2.2mm)
  #body
]

#let node(title, detail: none, color: ink, bg: white, height: 24mm, size: 10pt) = box(
  width: 100%,
  height: height,
  fill: bg,
  stroke: 0.9pt + color,
  radius: 2pt,
  inset: 2.8mm,
)[
  #align(center + horizon)[
    #text(size: size, weight: "bold", fill: color)[#title]
    #if detail != none [
      #v(1.2mm)
      #text(size: 7.6pt, fill: muted)[#detail]
    ]
  ]
]

// An arrow with nothing written on it says "and then". An arrow with a verb
// on it says what actually happens between the two boxes, which is usually
// the part the learner did not already know.
#let arrow(label: none, color: muted) = align(center + horizon)[
  #box[
    #text(size: 17pt, weight: "bold", fill: color)[→]
    #if label != none {
      place(center + horizon, dy: -4mm, box(width: 22mm)[
        #align(center)[#text(size: 7pt, fill: color)[#label]]
      ])
    }
  ]
]

#let arrow-down(label: none, color: muted) = align(center)[
  #text(size: 16pt, weight: "bold", fill: color)[↓]
  #if label != none [
    #h(2mm)
    #text(size: 7pt, fill: color)[#label]
  ]
]

#let chip(body, color: primary, bg: white) = box(
  fill: bg,
  stroke: 0.7pt + color,
  radius: 8pt,
  inset: (x: 2.6mm, y: 1.2mm),
)[#text(size: 8pt, weight: "bold", fill: color)[#body]]

#let callout(title, body, color: caution, bg: caution-bg) = box(
  width: 100%,
  fill: bg,
  stroke: (left: 2.4pt + color, rest: 0.7pt + color),
  radius: 2pt,
  inset: 3.2mm,
)[
  #text(size: 9pt, weight: "bold", fill: color)[#title]
  #v(1.2mm)
  #text(size: 8.4pt)[#body]
]

#let legend(entries) = {
  // entries: array of (colour, label)
  set text(size: 8pt, fill: muted)
  grid(
    columns: entries.map(_ => auto),
    column-gutter: 6mm,
    ..entries.map(e => [
      #box(width: 3.2mm, height: 3.2mm, fill: e.at(0), radius: 1pt)
      #h(1.4mm) #e.at(1)
    ]),
  )
}

// The footer is where the page admits what it is. A conceptual diagram that
// does not say it is conceptual invites a reader to build from it.
#let footer-band(left-text, right-text: none) = {
  line(length: 100%, stroke: 0.6pt + rule-c)
  v(1.6mm)
  grid(
    columns: (1fr, auto),
    text(size: 7.6pt, fill: muted)[#left-text],
    if right-text != none { text(size: 7.6pt, fill: muted)[#right-text] } else { [] },
  )
}

// ------------------------------------------------------------ archetypes
// steps: array of (title, detail). arrows: array of labels, one shorter.
#let flow(steps, arrows: (), color: primary, bg: white, height: 24mm, gap: 11mm) = {
  let cols = ()
  let cells = ()
  for (i, s) in steps.enumerate() {
    cols.push(1fr)
    cells.push(node(s.at(0), detail: s.at(1), color: color, bg: bg, height: height))
    if i < steps.len() - 1 {
      cols.push(gap)
      cells.push(arrow(label: if i < arrows.len() { arrows.at(i) } else { none }, color: color))
    }
  }
  grid(columns: cols, column-gutter: 2mm, ..cells)
}

#let vflow(steps, arrows: (), color: primary, bg: white, height: 17mm) = {
  for (i, s) in steps.enumerate() {
    node(s.at(0), detail: s.at(1), color: color, bg: bg, height: height)
    if i < steps.len() - 1 {
      v(1.2mm)
      arrow-down(label: if i < arrows.len() { arrows.at(i) } else { none }, color: color)
      v(1.2mm)
    }
  }
}

// A ring for anything that returns to its own start: instructional cycles,
// feedback loops, iteration. Reserve it for genuine loops — drawing a
// one-way process as a circle tells the reader something untrue about it.
// `returns` draws the paths back: an array of (from-index, to-index, label),
// zero-based, as dashed chords across the ring. If a loop is the reason you chose
// a ring, draw it -- a return path described in a side panel is a claim the picture
// itself is not making, and the reader believes the picture.
#let cycle-diagram(
  steps,
  size: 148mm,
  node-w: 48mm,
  node-h: 24mm,
  color: primary,
  bg: white,
  center-label: none,
  center-detail: none,
  returns: (),
  return-color: caution,
) = {
  let n = steps.len()
  let r = size / 2 - node-h / 2 - 1mm
  block(width: size, height: size)[
    // The ring itself. Without it the "cycle" is a scatter of boxes with small
    // arrows between them, and the shape stops making its own argument.
    #place(center + horizon, circle(radius: r, stroke: 1pt + rule-c, fill: none))
    #{
      let inner = r.mm() - node-h.mm() / 2 - 3
      for ret in returns {
        let ai = -90deg + 360deg * ret.at(0) / n
        let aj = -90deg + 360deg * ret.at(1) / n
        let px = inner * calc.cos(ai)
        let py = inner * calc.sin(ai)
        let dx = inner * calc.cos(aj) - px
        let dy = inner * calc.sin(aj) - py
        let d = calc.sqrt(dx * dx + dy * dy)
        let ang = calc.atan2(dx, dy)
        place(left + horizon, dx: size / 2 + px * 1mm, dy: py * 1mm,
          rotate(ang, origin: left + horizon,
            line(length: d * 0.9 * 1mm, stroke: (paint: return-color, thickness: 0.9pt, dash: "dashed"))))
        // the head sits at the end of the dashes, not partway along them
        place(center + horizon, dx: (px + dx * 0.955) * 1mm, dy: (py + dy * 0.955) * 1mm,
          rotate(ang, text(size: 12pt, weight: "bold", fill: return-color)[→]))
        if ret.len() > 2 and ret.at(2) != none {
          // sits near the source end: every chord passes through the middle of the
          // ring, so labels stacked at the midpoint would pile on each other and on
          // the centre label.
          place(center + horizon, dx: (px + dx * 0.26) * 1mm, dy: (py + dy * 0.26) * 1mm,
            box(fill: white, inset: (x: 1.4mm, y: 0.7mm), width: 30mm)[
              #align(center)[#text(size: 7pt, fill: return-color)[#ret.at(2)]]
            ])
        }
      }
    }
    #for (i, s) in steps.enumerate() {
      let a = -90deg + 360deg * i / n
      place(
        center + horizon,
        dx: r * calc.cos(a),
        dy: r * calc.sin(a),
        box(width: node-w)[#node(
            s.at(0),
            detail: s.at(1),
            color: color,
            bg: bg,
            height: node-h,
          )],
      )
      // arrow sitting on the ring itself, between this node and the next
      let m = a + 360deg / n / 2
      place(
        center + horizon,
        dx: r * calc.cos(m),
        dy: r * calc.sin(m),
        rotate(m + 90deg, text(size: 16pt, weight: "bold", fill: color)[→]),
      )
    }
    #if center-label != none {
      place(center + horizon, box(width: size - 2 * node-w - 6mm)[
        #align(center)[
          #text(size: 12pt, weight: "bold", fill: color)[#center-label]
          #if center-detail != none [
            #v(1.4mm)
            #text(size: 8pt, fill: muted)[#center-detail]
          ]
        ]
      ])
    }
  ]
}

// A hub with spokes: the usual honest shape of a "concept map" ask.
#let radial-map(center-label, spokes, size: 150mm, hub-w: 52mm, node-w: 46mm, node-h: 21mm, color: primary, bg: white) = {
  let n = spokes.len()
  let r = size / 2 - node-h / 2 - 1mm
  block(width: size, height: size)[
    #for (i, s) in spokes.enumerate() {
      let a = -90deg + 360deg * i / n
      place(left + horizon, dx: size / 2,
        rotate(a, origin: left + horizon, line(length: r, stroke: 0.9pt + rule-c)))
      place(center + horizon, dx: r * calc.cos(a), dy: r * calc.sin(a),
        box(width: node-w)[#node(s.at(0), detail: s.at(1), color: color, bg: bg, height: node-h, size: 9pt)])
    }
    #place(center + horizon, box(width: hub-w)[#node(center-label, color: color, bg: bg.lighten(0%), height: 22mm, size: 11pt)])
  ]
}

// events: array of (when, what, detail). Alternates above/below the axis so
// long labels do not collide.
#let timeline(events, color: primary, height: 62mm, label-w: 46mm) = {
  let n = events.len()
  block(width: 100%, height: height)[
    #place(left + horizon, line(length: 100%, stroke: 1.2pt + color))
    #for (i, e) in events.enumerate() {
      let x = 100% * (i + 0.5) / n
      place(left + horizon, dx: x - 1.4mm, circle(radius: 1.4mm, fill: color, stroke: none))
      let above = calc.even(i)
      let label = box(width: label-w)[
        #align(center)[
          #text(size: 9.4pt, weight: "bold", fill: color)[#e.at(0)]
          #v(0.8mm)
          #text(size: 8.6pt)[#e.at(1)]
          #if e.len() > 2 [
            #v(0.8mm)
            #text(size: 7.4pt, fill: muted)[#e.at(2)]
          ]
        ]
      ]
      if above {
        place(left + bottom, dx: x - label-w / 2, dy: -height / 2 - 7mm, label)
      } else {
        place(left + top, dx: x - label-w / 2, dy: height / 2 + 7mm, label)
      }
      place(left + horizon, dx: x - 0.3pt, dy: if above { -3.5mm } else { 3.5mm },
        line(length: 7mm, angle: 90deg, stroke: 0.8pt + rule-c))
    }
  ]
}
