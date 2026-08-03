// Current curriculum pipeline — synchronized with meta_prompt/curriculum.prompt.v1.md.
#set page(width: 420mm, height: 297mm, margin: 11mm, fill: white)
#set text(font: "Helvetica", size: 9pt, fill: rgb("#17202a"))
#set par(leading: 0.62em)

#let ink = rgb("#17202a")
#let muted = rgb("#5f6b76")
#let line-c = rgb("#c8d0d7")
#let engine = rgb("#174a7e")
#let engine-bg = rgb("#eaf2f9")
#let domain = rgb("#146447")
#let domain-bg = rgb("#e9f5ef")
#let gate = rgb("#875b00")
#let gate-bg = rgb("#fbf3df")
#let warn = rgb("#9b352d")
#let warn-bg = rgb("#faecea")

#let panel(title, body, color: engine, bg: engine-bg) = box(
  width: 100%,
  fill: bg,
  stroke: 1pt + color,
  radius: 3pt,
  inset: 4mm,
)[
  #text(size: 11pt, weight: "bold", fill: color)[#title]
  #v(2mm)
  #body
]

#let node(title, detail, color: ink, bg: white) = box(
  width: 100%,
  height: 25mm,
  fill: bg,
  stroke: 0.8pt + color,
  radius: 2pt,
  inset: 2.5mm,
)[
  #align(center+horizon)[
    #text(size: 9.2pt, weight: "bold", fill: color)[#title]
    #v(1.1mm)
    #text(size: 7.4pt, fill: muted)[#detail]
  ]
]

#let arrow = align(center+horizon)[#text(size: 17pt, weight: "bold", fill: muted)[→]]

#align(center)[
  #text(size: 24pt, weight: "bold")[How the Curriculum Pipeline Works]
  #v(1.5mm)
  #text(size: 11pt, style: "italic", fill: muted)[
    One generic prompt runs a supplied curriculum. The curriculum owns its domain. Evidence stays honest.
  ]
]
#v(4mm)

#panel([1 · BOUNDARIES], [
  #grid(
    columns: (1fr, 8mm, 1fr, 8mm, 1fr, 10mm, 1.45fr),
    column-gutter: 2mm,
    node([ENGINE], [derived from prompt location · immutable], color: engine, bg: white),
    arrow,
    node([CURRICULUM], [required path · manifest, domain schema, verifier · immutable], color: domain, bg: white),
    arrow,
    node([OUTPUT_ROOT], [required path · only write target · must be empty], color: gate, bg: white),
    arrow,
    node([curriculum.prompt.v1.md], [runs the supplied curriculum directly · no subject or unit count hardcoded], color: engine, bg: white),
  )
  #v(2.5mm)
  #align(center)[#text(size: 8.5pt, weight: "bold", fill: engine)[
    The active prompt no longer builds a curriculum-specific generator.
  ]]
], color: engine, bg: engine-bg)

#v(4mm)

#panel([2 · ONE DECLARED UNIT], [
  #grid(
    columns: (1fr, 5mm, 1fr, 5mm, 1fr, 5mm, 1fr, 5mm, 1fr, 5mm, 1fr),
    column-gutter: 1mm,
    node([Manifest], [read the next declared unit], color: engine, bg: white),
    arrow,
    node([Retrieve], [primary sources, exact identifiers], color: domain, bg: white),
    arrow,
    node([Domain], [assemble the subject facts], color: domain, bg: domain-bg),
    arrow,
    node([Verify], [curriculum-owned deterministic verifier], color: domain, bg: white),
    arrow,
    node([Generate + check], [six engine blocks · generic checks], color: engine, bg: white),
    arrow,
    node([Judge + checkpoint], [one cross-family judge · code decides], color: gate, bg: white),
  )
  #v(3mm)
  #grid(
    columns: (1.2fr, 1fr, 1fr),
    column-gutter: 4mm,
    box(fill: white, stroke: 0.8pt + engine, radius: 2pt, inset: 3mm)[
      #text(weight: "bold", fill: engine)[Six engine blocks]
      #v(1mm)
      #text(size: 8pt)[identity · pedagogy · sequence · content · safety · visuals]
    ],
    box(fill: white, stroke: 0.8pt + domain, radius: 2pt, inset: 3mm)[
      #text(weight: "bold", fill: domain)[One curriculum block]
      #v(1mm)
      #text(size: 8pt)[domain · its schema, verifier, fixtures, and evidence]
    ],
    box(fill: white, stroke: 0.8pt + gate, radius: 2pt, inset: 3mm)[
      #text(weight: "bold", fill: gate)[One-parent rule]
      #v(1mm)
      #text(size: 8pt)[every rendered subject fact points to its value in domain]
    ],
  )
], color: domain, bg: domain-bg)

#v(4mm)

#panel([3 · PROVE, THEN SCALE], [
  #let gates = (
    ("0", "Logger", "append-only · paired"),
    ("1", "Static", "inventories agree"),
    ("2", "Deterministic", "checks + fixtures"),
    ("3", "Simulated", "failure + resume"),
    ("4", "Live capability", "real routes"),
    ("5", "Golden unit", "render + inspect"),
  )
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    column-gutter: 3mm,
    ..gates.map(g => box(height: 23mm, fill: white, stroke: 0.9pt + gate, radius: 2pt, inset: 2mm)[
      #align(center+horizon)[
        #text(weight: "bold", fill: gate)[#g.at(0) · #g.at(1)]
        #v(1mm)
        #text(size: 7.3pt, fill: muted)[#g.at(2)]
      ]
    ]),
  )
  #v(2.5mm)
  #align(center)[
    #text(weight: "bold", fill: gate)[all six pass → remaining declared units → assembled product → render → page inspection → audited result]
  ]
], color: gate, bg: gate-bg)

#v(4mm)

#panel([CURRENT REPOSITORY STATE · 2026-08-02], [
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    column-gutter: 4mm,
    [#text(weight: "bold")[Phase 4]  #text(fill: warn)[30 gates pass]],
    [#text(weight: "bold")[Phase 5]  #text(fill: warn)[38 gates pass]],
    [#text(weight: "bold")[RT-5]  no runtime controller, logger, renderer, source run, or live route],
    [#text(weight: "bold")[RT-7]  zero generated units],
  )
  #v(2mm)
  #align(center)[#text(size: 8.7pt, weight: "bold", fill: warn)[
    Repository and fixture coverage is not generated-unit coverage. Produced units remain drafts pending downstream human review.
  ]]
], color: warn, bg: warn-bg)

#v(4mm)
#line(length: 100%, stroke: 0.7pt + line-c)
#v(2mm)
#align(right)[
  #text(size: 7.8pt, fill: muted)[curriculum\_builder · curriculum prompt v1 · curriculum schema v5 · lab schema v4]
]
