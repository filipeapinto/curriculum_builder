// "How the curriculum generator works" — one-page landscape infographic.
// Built with typst; Helvetica only (system font, no network fetch).

#set page(width: 420mm, height: 348mm, margin: (x: 10mm, top: 9mm, bottom: 9mm), fill: white)
#set text(font: "Helvetica", size: 9pt, fill: rgb("#1a1a1a"))
#set par(leading: 0.55em, justify: false)

// ---------- palette ----------
#let ink        = rgb("#1a1a1a")
#let grey       = rgb("#5a5a5a")
#let grey-lt    = rgb("#8f8f8f")
#let rule-c     = rgb("#c9c9c9")
#let bg-faint   = rgb("#f7f7f7")

#let build-c    = rgb("#1f4e8c")
#let build-lt   = rgb("#e8eef8")
#let gen-c      = rgb("#1f6b4a")
#let gen-lt     = rgb("#e7f2ec")
#let gate-c     = rgb("#8a5a00")
#let gate-lt    = rgb("#faf1de")
#let fail-c     = rgb("#a5382b")
#let lane-c     = rgb("#6b6b6b")

#let CW = 400mm  // content width available inside every band container

// ---------- primitive helpers ----------

// filled / stroked box with content, absolutely placed
#let nbox(x, y, w, h, body, fill: white, stroke-c: ink, sw: 1pt, radius: 1.6pt) = {
  place(top+left, dx: x, dy: y, box(width: w, height: h, fill: fill, stroke: sw + stroke-c, radius: radius, inset: 0pt)[
    #align(center+horizon)[#body]
  ])
}

// plain text placed at a point, box auto-sized (no clipping)
#let ntext(x, y, w, body, align-h: center) = {
  place(top+left, dx: x, dy: y, box(width: w)[#align(align-h)[#body]])
}

// horizontal line segment, no head, from (x,y) length w to the right
#let seg-h(x, y, w, color: ink, dashed: false, sw: 1.1pt) = {
  place(top+left, dx: x, dy: y, line(length: w, stroke: (paint: color, thickness: sw, dash: if dashed { "dashed" } else { none })))
}
// vertical line segment, from (x,y) length h downward (negative h = upward)
#let seg-v(x, y, h, color: ink, dashed: false, sw: 1.1pt) = {
  place(top+left, dx: x, dy: y, line(length: calc.abs(h), angle: 90deg, stroke: (paint: color, thickness: sw, dash: if dashed { "dashed" } else { none })))
  // note: for negative h, caller must pass y already at the top and h positive downward only;
}

#let AH = 2.6mm // arrowhead length
#let HH = 1.5mm // arrowhead half-height

#let head-right(x, y, color: ink) = {
  place(top+left, dx: x - AH, dy: y - HH, polygon(fill: color, (0mm,0mm), (0mm, 2*HH), (AH, HH)))
}
#let head-left(x, y, color: ink) = {
  place(top+left, dx: x, dy: y - HH, polygon(fill: color, (AH,0mm), (AH, 2*HH), (0mm, HH)))
}
#let head-down(x, y, color: ink) = {
  place(top+left, dx: x - HH, dy: y - AH, polygon(fill: color, (0mm,0mm), (2*HH,0mm), (HH, AH)))
}
#let head-up(x, y, color: ink) = {
  place(top+left, dx: x - HH, dy: y, polygon(fill: color, (0mm,AH), (2*HH,AH), (HH, 0mm)))
}

// full arrow: horizontal, tip lands exactly at x+w
#let harrow(x, y, w, color: ink, dashed: false, sw: 1.1pt) = {
  seg-h(x, y, w - AH, color: color, dashed: dashed, sw: sw)
  head-right(x + w, y, color: color)
}
#let harrow-left(x, y, w, color: ink, dashed: false, sw: 1.1pt) = {
  seg-h(x + AH, y, w - AH, color: color, dashed: dashed, sw: sw)
  head-left(x, y, color: color)
}
#let varrow-down(x, y, h, color: ink, dashed: false, sw: 1.1pt) = {
  place(top+left, dx: x, dy: y, line(length: h - AH, angle: 90deg, stroke: (paint: color, thickness: sw, dash: if dashed { "dashed" } else { none })))
  head-down(x, y + h, color: color)
}
#let varrow-up(x, y, h, color: ink, dashed: false, sw: 1.1pt) = {
  place(top+left, dx: x, dy: y - h + AH, line(length: h - AH, angle: 90deg, stroke: (paint: color, thickness: sw, dash: if dashed { "dashed" } else { none })))
  head-up(x, y - h, color: color)
}

// small diamond "decide" marker, centered at (cx,cy)
#let decide(cx, cy, size: 8mm, color: gate-c, fill: gate-lt) = {
  place(top+left, dx: cx - size/2, dy: cy - size/2,
    rotate(45deg, reflow: true,
      rect(width: size/1.414, height: size/1.414, fill: fill, stroke: 1.1pt + color)))
}

#let dot(cx, cy, r: 1mm, color: ink) = {
  place(top+left, dx: cx - r, dy: cy - r, circle(radius: r, fill: color, stroke: none))
}

// ============================================================
// MASTHEAD
// ============================================================
#box(width: CW, height: 18mm)[
  #align(center)[
    #text(size: 24pt, weight: "bold")[How the Curriculum Generator Works]
    #v(1.2mm)
    #text(size: 11.5pt, style: "italic", fill: grey)[
      One prompt builds the generator. The generator builds every lab the curriculum names. Nobody watches.
    ]
  ]
]
#v(0.5mm)
#line(length: CW, stroke: 0.7pt + rule-c)
#v(3mm)

// ============================================================
// BAND 1 — BUILD
// ============================================================
#let B1H = 58mm
#box(width: CW, height: B1H)[
  // header
  #place(top+left, rect(width: CW, height: 7mm, fill: build-c, stroke: none))
  #ntext(0mm, 1.3mm, CW, text(fill: white, weight: "bold", size: 12.5pt)[BUILD  ·  runs once, a human starts it])

  // clear-label banner
  #place(top+left, dy: 7mm, rect(width: CW, height: 6.4mm, fill: build-lt, stroke: none))
  #ntext(0mm, 8.4mm, CW, text(fill: build-c, weight: "bold", size: 10.5pt)[
    THE META-PROMPT WRITES THE GENERATOR, NOT THE CURRICULUM.
  ])

  // main 3-column diagram
  #let ry = 16mm
  #let col1x = 2mm
  #let col1w = 92mm
  #let col2x = 118mm
  #let col2w = 160mm
  #let col3x = 302mm
  #let col3w = 96mm
  #let boxtop = ry + 6mm
  #let colh = 23mm     // col1 / col3 list boxes
  #let col2h = 34mm    // meta-prompt hero box (taller — more content)

  // column headers
  #ntext(col1x, ry, col1w, text(weight: "bold", size: 9.5pt, fill: grey)[INPUTS])
  #ntext(col2x, ry, col2w, text(weight: "bold", size: 9.5pt, fill: build-c)[META-PROMPT])
  #ntext(col3x, ry, col3w, text(weight: "bold", size: 9.5pt, fill: grey)[OUTPUT])

  // col1 box — inputs list
  #nbox(col1x, boxtop, col1w, colh, [
    #box(width: col1w - 6mm)[
      #set text(size: 8.3pt)
      #set par(leading: 0.62em)
      #box(width: 100%)[• curriculum.v4.yaml — which labs, how many]  \
      #box(width: 100%)[• lab.schema.v3.json]  \
      #box(width: 100%)[• component\_lab\_template]  \
      #box(width: 100%)[• routing/ — model policy]  \
      #box(width: 100%)[• legacy v3 generator — evidence]
    ]
  ], fill: bg-faint, stroke-c: rule-c, sw: 0.9pt)

  // callout — the manifest, not the generator, decides the lab count
  #nbox(col1x, boxtop + colh + 2mm, col1w, 9mm, [
    #box(width: col1w - 6mm)[
      #text(size: 7pt, style: "italic", fill: build-c)[
        the manifest decides how many labs exist — nothing downstream hardcodes a count
      ]
    ]
  ], fill: build-lt, stroke-c: build-c, sw: 0.9pt)

  // arrow 1
  #harrow(col1x + col1w + 2mm, boxtop + colh/2, col2x - (col1x + col1w) - 4mm, color: build-c)

  // col2 box — meta-prompt (hero)
  #nbox(col2x, boxtop, col2w, col2h, [
    #box(width: col2w - 14mm)[
      #align(center)[
        #text(weight: "bold", size: 11.5pt, fill: build-c)[meta\_curriculum\_builder.prompt.v6.md + assets/]
        #v(2mm)
        #text(size: 9.5pt, style: "italic", fill: build-c)["builds the factory, never the product"]
        #v(2mm)
        #text(size: 8pt, fill: grey)[produces exactly one finished lab (L01) as proof]
      ]
    ]
  ], fill: build-lt, stroke-c: build-c, sw: 1.4pt)

  // arrow 2
  #harrow(col2x + col2w + 2mm, boxtop + colh/2, col3x - (col2x + col2w) - 4mm, color: build-c)

  // col3 box — outputs list
  #nbox(col3x, boxtop, col3w, colh, [
    #box(width: col3w - 6mm)[
      #set text(size: 8.3pt)
      #set par(leading: 0.62em)
      #box(width: 100%)[• templates\_v7/]  \
      #box(width: 100%)[• controller (python)]  \
      #box(width: 100%)[• worker prompts]  \
      #box(width: 100%)[• schemas]  \
      #box(width: 100%)[• tests]  \
      #box(width: 100%)[• golden L01]
    ]
  ], fill: bg-faint, stroke-c: rule-c, sw: 0.9pt)
]

#v(2mm)

// ============================================================
// BAND 2 — PROVE
// ============================================================
#let B2H = 48mm
#box(width: CW, height: B2H)[
  #place(top+left, rect(width: CW, height: 7mm, fill: gate-c, stroke: none))
  #ntext(0mm, 1.3mm, CW, text(fill: white, weight: "bold", size: 12.5pt)[PROVE  ·  six gates, in order — all must pass before the full run])

  #let gy = 11mm
  #let gh = 22mm
  #let ngates = 6
  #let ggap = 6mm
  #let barrierw = 30mm
  #let gw = (CW - barrierw - 10mm - (ngates - 1) * ggap) / ngates

  #let gates = (
    ("0", "Logger", "append-only · IDs monotonic · every start paired — built and proven before anything else exists"),
    ("1", "Static (every lab)", "every advertised check actually asserted, not just named"),
    ("2", "Deterministic", "state machine · checkpoints · hashes · resource limits"),
    ("3", "Simulated (every lab)", "revision · retry · block · failure · interrupt/resume — with fake workers"),
    ("4", "Live capability", "real worker call · real image job · real PDF render"),
    ("5", "Golden L01", "one complete lab — reviewed, rendered, page-inspected, accepted"),
  )

  #for (i, g) in gates.enumerate() {
    let gx = i * (gw + ggap)
    nbox(gx, gy, gw, gh, [
      #box(width: gw - 5mm)[
        #align(center)[
          #text(weight: "bold", size: 9.5pt, fill: gate-c)[Gate #g.at(0) · #g.at(1)]
          #v(1.5mm)
          #text(size: 7.6pt, fill: grey)[#g.at(2)]
        ]
      ]
    ], fill: gate-lt, stroke-c: gate-c, sw: 1.1pt)
    if i < ngates - 1 {
      harrow(gx + gw + 0.6mm, gy + gh/2, ggap - 1.2mm, color: gate-c)
    }
  }

  // barrier / release gate after gate 5
  #let bx = ngates * gw + (ngates - 1) * ggap + 8mm
  #harrow(ngates * gw + (ngates - 1) * ggap + 0.6mm, gy + gh/2, 6.4mm, color: gate-c)
  #nbox(bx, gy, barrierw, gh, [
    #box(width: barrierw - 5mm)[
      #align(center)[
        #text(weight: "bold", size: 8.6pt, fill: white)[RELEASE GATE]
        #v(1mm)
        #line(length: 70%, stroke: 1.4pt + white)
        #v(1mm)
        #text(size: 7.6pt, fill: white)[full-run command runs only when all six pass]
      ]
    ]
  ], fill: gate-c, stroke-c: gate-c, sw: 1.1pt)

  // failure loop: dashed return line beneath the gate row
  #let fy = gy + gh + 6mm
  #seg-v(2mm, gy + gh, 6mm - AH, color: fail-c, dashed: true, sw: 1pt)
  #head-down(2mm, fy, color: fail-c)
  #for i in range(ngates) {
    let gx = i * (gw + ggap)
    let cx = gx + gw/2
    seg-v(cx, fy - 5mm, 5mm, color: fail-c, dashed: true, sw: 0.9pt)
  }
  #seg-h(2mm, fy, ngates * gw + (ngates - 1) * ggap - 2mm, color: fail-c, dashed: true, sw: 1pt)
  #harrow-left(2mm, fy, 0mm, color: fail-c) // endpoint cap (zero-length, head only via left arrow at start not needed)
  #head-left(2mm, fy, color: fail-c)
  #ntext(6mm, fy + 1.6mm, ngates * gw + (ngates - 1) * ggap - 10mm,
    text(size: 7.8pt, fill: fail-c, style: "italic")[
      any gate fails  →  revise  →  re-run affected gates  ·  capped at 6 revision cycles
    ]
  )
]

#v(2mm)

// ============================================================
// BAND 3 — GENERATE
// ============================================================
#let B3H = 80mm
#box(width: CW, height: B3H)[
  #place(top+left, rect(width: CW, height: 7mm, fill: gen-c, stroke: none))
  #ntext(0mm, 1.3mm, CW, text(fill: white, weight: "bold", size: 12.5pt)[GENERATE  ·  repeats once per lab, unattended])

  #let ry = 10mm
  #let rowh = 62mm
  #let midy = ry + rowh/2 - 3mm

  // cluster geometry — C1/C4/C5 all carry a 4-lane review pass, so they share a width
  #let c1x = 0mm
  #let c1w = 84mm
  #let c2x = 92mm
  #let c2w = 56mm
  #let c3x = 156mm
  #let c3w = 60mm
  #let c4x = 224mm
  #let c4w = 84mm
  #let c5x = 316mm
  #let c5w = 84mm

  // ---- C1: PLAN + 4 isolated plan reviews + decide ----
  #nbox(c1x, ry, c1w, rowh, [], fill: white, stroke-c: rule-c, sw: 0.7pt)
  #ntext(c1x, ry + 2mm, c1w, text(weight: "bold", size: 10pt, fill: gen-c)[PLAN])
  #nbox(c1x + 4mm, ry + 8mm, c1w - 8mm, 8mm, text(size: 8pt)[write lab plan (5E sequence)], fill: gen-lt, stroke-c: gen-c, sw: 1pt)
  #varrow-down(c1x + c1w/2, ry + 16mm, 5mm, color: gen-c)
  // 4 sealed lanes
  #let lanelabels = ("A","B","C","D")
  #let laney = ry + 22mm
  #let laneh = 15mm
  #let lanew = (c1w - 8mm - 3*1.6mm) / 4
  #for (i, lab) in lanelabels.enumerate() {
    let lx = c1x + 4mm + i * (lanew + 1.6mm)
    nbox(lx, laney, lanew, laneh, [
      #align(center)[
        #text(size: 7.2pt, fill: lane-c, weight: "bold")[Review #lab]
        #v(0.8mm)
        #text(size: 6.2pt, fill: grey)[sealed lane]
      ]
    ], fill: white, stroke-c: lane-c, sw: (0.9pt))
  }
  #ntext(c1x + 4mm, laney + laneh + 1mm, c1w - 8mm, text(size: 6.4pt, fill: lane-c, style: "italic")[isolated — none reads another's verdict])
  #varrow-down(c1x + c1w/2, laney + laneh + 5.5mm, 5mm, color: gen-c)
  #decide(c1x + c1w/2, laney + laneh + 14mm, size: 8mm)
  #ntext(c1x + c1w/2 + 5mm, laney + laneh + 11.5mm, c1w/2 - 6mm, text(size: 6.6pt, fill: gate-c)[decide])
  #ntext(c1x, laney + laneh + 19mm, c1w, text(size: 6.6pt, fill: grey)[advance · block · revise])

  // connector C1 -> C2
  #harrow(c1x + c1w + 2mm, ry + 17mm, (c2x - (c1x+c1w)) - 4mm, color: gen-c)

  // ---- C2: RESEARCH · CIRCUIT · EXPERIMENT ----
  #nbox(c2x, ry, c2w, 34mm, [
    #box(width: c2w - 8mm)[
      #align(center)[
        #text(weight: "bold", size: 9pt, fill: gen-c)[RESEARCH]
        #v(1mm) #text(size: 8pt, fill: grey)[↓]  #v(1mm)
        #text(weight: "bold", size: 9pt, fill: gen-c)[CIRCUIT]
        #v(1mm) #text(size: 8pt, fill: grey)[↓]  #v(1mm)
        #text(weight: "bold", size: 9pt, fill: gen-c)[EXPERIMENT]
      ]
    ]
  ], fill: gen-lt, stroke-c: gen-c, sw: 1.1pt)
  #ntext(c2x, ry + 36mm, c2w, text(size: 7pt, fill: grey, style: "italic")[→ machine-readable circuit data])

  // connector C2 -> C3
  #harrow(c2x + c2w + 2mm, ry + 17mm, (c3x - (c2x+c2w)) - 4mm, color: gen-c)

  // ---- C3: CHILD TEXT · ADULT GUIDE · VISUALS ----
  #nbox(c3x, ry, c3w, 34mm, [
    #box(width: c3w - 8mm)[
      #align(center)[
        #text(weight: "bold", size: 9pt, fill: gen-c)[CHILD TEXT]
        #v(1mm) #text(size: 8pt, fill: grey)[+]  #v(1mm)
        #text(weight: "bold", size: 9pt, fill: gen-c)[ADULT GUIDE]
        #v(1mm) #text(size: 8pt, fill: grey)[+]  #v(1mm)
        #text(weight: "bold", size: 9pt, fill: gen-c)[VISUALS]
      ]
    ]
  ], fill: gen-lt, stroke-c: gen-c, sw: 1.1pt)
  #ntext(c3x, ry + 36mm, c3w, text(size: 7pt, fill: grey, style: "italic")[all generated from that same data])

  // connector C3 -> C4
  #harrow(c3x + c3w + 2mm, ry + 17mm, (c4x - (c3x+c3w)) - 4mm, color: gen-c)

  // ---- C4: 4 isolated QA reviews + decide ----
  #nbox(c4x, ry, c4w, rowh, [], fill: white, stroke-c: rule-c, sw: 0.7pt)
  #ntext(c4x, ry + 2mm, c4w, text(weight: "bold", size: 10pt, fill: gen-c)[QA REVIEW])
  #let laney4 = ry + 9mm
  #let lanew4 = (c4w - 8mm - 3*1.6mm) / 4
  #for (i, lab) in lanelabels.enumerate() {
    let lx = c4x + 4mm + i * (lanew4 + 1.6mm)
    nbox(lx, laney4, lanew4, laneh, [
      #align(center)[
        #text(size: 7.2pt, fill: lane-c, weight: "bold")[Reviewer #lab]
        #v(0.8mm)
        #text(size: 6.2pt, fill: grey)[sealed lane]
      ]
    ], fill: white, stroke-c: lane-c, sw: 0.9pt)
  }
  #ntext(c4x + 4mm, laney4 + laneh + 1mm, c4w - 8mm, text(size: 6.4pt, fill: lane-c, style: "italic")[isolated — none reads another's verdict])
  #varrow-down(c4x + c4w/2, laney4 + laneh + 5.5mm, 5mm, color: gen-c)
  #decide(c4x + c4w/2, laney4 + laneh + 14mm, size: 8mm)
  #ntext(c4x + c4w/2 + 5mm, laney4 + laneh + 11.5mm, c4w/2 - 6mm, text(size: 6.6pt, fill: gate-c)[decide])
  #ntext(c4x, laney4 + laneh + 19mm, c4w, text(size: 6.6pt, fill: grey)[advance · block · revise])

  // connector C4 -> C5
  #harrow(c4x + c4w + 2mm, ry + 17mm, (c5x - (c4x+c4w)) - 4mm, color: gen-c)

  // ---- C5: rasterize + 4 isolated PDF reviews -> ACCEPT ----
  #nbox(c5x, ry, c5w, rowh, [], fill: white, stroke-c: rule-c, sw: 0.7pt)
  #ntext(c5x, ry + 2mm, c5w, text(weight: "bold", size: 10pt, fill: gen-c)[PDF REVIEW])
  #nbox(c5x + 4mm, ry + 8mm, c5w - 8mm, 9mm, [
    #align(center)[#text(size: 7pt)[rasterize 200 dpi · every page — inspect the #text(style: "italic")[shipped] PDF]]
  ], fill: gen-lt, stroke-c: gen-c, sw: 1pt)
  #varrow-down(c5x + c5w/2, ry + 17mm, 4mm, color: gen-c)
  #let laney5 = ry + 22mm
  #let lanew5 = (c5w - 8mm - 3*1.6mm) / 4
  #let pdflabels = ("A","B","C","D")
  #for (i, lab) in pdflabels.enumerate() {
    let lx = c5x + 4mm + i * (lanew5 + 1.6mm)
    nbox(lx, laney5, lanew5, laneh, [
      #align(center)[
        #text(size: 7.2pt, fill: lane-c, weight: "bold")[PDF #lab]
        #v(0.8mm)
        #text(size: 6.2pt, fill: grey)[sealed lane]
      ]
    ], fill: white, stroke-c: lane-c, sw: 0.9pt)
  }
  #ntext(c5x + 4mm, laney5 + laneh + 1mm, c5w - 8mm, text(size: 6.4pt, fill: lane-c, style: "italic")[isolated — none reads another's verdict])
  #varrow-down(c5x + c5w/2, laney5 + laneh + 5.5mm, 5mm, color: gen-c)
  #nbox(c5x + 4mm, laney5 + laneh + 12mm, c5w - 8mm, 10mm, text(size: 9pt, weight: "bold", fill: white)[✓ ACCEPT], fill: gen-c, stroke-c: gen-c, sw: 1.2pt)

  // loop back: accept -> advance to next lab (L01 ... LN), routed under the whole row
  #let loopy = ry + rowh + 7mm
  #varrow-down(c5x + c5w/2, ry + rowh - 1mm, loopy - (ry + rowh - 1mm) - AH + AH, color: gen-c, sw: 1.1pt)
  #seg-h(c1x + c1w/2, loopy, c5x + c5w/2 - (c1x + c1w/2), color: gen-c, sw: 1.1pt)
  #varrow-up(c1x + c1w/2, ry + rowh - 1mm, (ry + rowh - 1mm) - loopy, color: gen-c, sw: 1.1pt)
  #ntext(c1x + c1w/2 + 4mm, loopy - 3.6mm, c5x - c1x - c1w/2 - 4mm,
    text(size: 8pt, fill: gen-c, weight: "bold")[accept → advance to next lab  ·  L01 … LN   —   never advance without acceptance])

]

#v(3mm)
#line(length: CW, stroke: 0.7pt + rule-c)
#v(1.5mm)
#box(width: CW, height: 9mm)[
  #ntext(0mm, 0mm, CW * 0.56, align-h: left, text(size: 8.6pt)[
    #text(weight: "bold", fill: gen-c)[After the last lab:]  assemble workbook  →  4 workbook reviews  →  final PDF  →  #text(weight: "bold")[done]
  ])
  #ntext(CW * 0.56, 0.6mm, CW * 0.44, align-h: right, text(size: 7.6pt, fill: grey)[
    every lab validates against #text(style: "italic")[lab.schema.v3.json] — seven blocks: identity · pedagogy · sequence (5E) · electronics · content · safety · visuals
  ])
]
#v(2mm)

// ============================================================
// FOOTER — why it can run unattended
// ============================================================
#line(length: CW, stroke: 0.7pt + rule-c)
#v(2mm)
#box(width: CW, height: 6mm)[
  #ntext(0mm, 0mm, CW, align-h: left, text(weight: "bold", size: 11pt)[Why it can run unattended])
]
#v(2mm)

#let items = (
  ("Checkpoint after every step", "hashes recorded; resume restarts at the first invalid checkpoint and never rebuilds accepted work."),
  ("Bounded retries", "malformed output once, transient failure once, then stop."),
  ("Targeted revision", "only the named failed artifact is regenerated, never the whole lab."),
  ("Code decides, models write", "Python owns state, routing, aggregation and every acceptance decision; no model ever advances a state."),
  ("Every action logged", [#text()[ACT] records start and completion in pairs; #text()[EXEC] records failures and always carries `Closes: ACT-NNN`. Zero unpaired starts is a release gate.]),
  ("It stops itself", "drift detection halts the run on scope creep, weakened tests, misreported evidence, or two cycles without progress."),
)

#let fcols = 6
#let fgap = 4mm
#let fw = (CW - (fcols - 1) * fgap) / fcols
#box(width: CW, height: 24mm)[
  #for (i, it) in items.enumerate() {
    let fx = i * (fw + fgap)
    nbox(fx, 0mm, fw, 24mm, [
      #box(width: fw - 6mm)[
        #text(size: 8.4pt, weight: "bold", fill: ink)[#it.at(0)]
        #v(1mm)
        #text(size: 7.4pt, fill: grey)[#it.at(1)]
      ]
    ], fill: bg-faint, stroke-c: rule-c, sw: 0.8pt)
  }
]

#v(3mm)
#align(center)[
  #box(stroke: 1pt + ink, radius: 2pt, inset: (x: 4mm, y: 2mm))[
    #text(size: 9.5pt, weight: "bold")[
      META\_ACCEPTED    ·    META\_SYSTEM\_FAILURE    ·    META\_DRIFT\_STOP
    ]
  ]
  #v(1mm)
  #text(size: 7.6pt, fill: grey, style: "italic")[the only three ways a run can end]
]

#v(6mm)
#align(right)[
  #text(size: 7.2pt, fill: grey-lt)[curriculum\_creator  ·  meta prompt v5  ·  lab schema v3]
]
