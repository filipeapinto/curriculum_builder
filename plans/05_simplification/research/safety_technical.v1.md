# Generating Safety-Relevant Technical Instruction for Children with LLMs

**Research report — 2026-07-31**
**Scope:** hands-on electronics/making activities for children; how correctness of circuits, component values and safety guidance is assured.

**Evidence strength labels used throughout:**
- **[STRONG]** — peer-reviewed / benchmark with published methodology, or primary regulatory/standards text, or primary source from the organisation itself.
- **[MODERATE]** — reputable journalism, NGO testing report, single case study, or primary source read via a summarisation layer.
- **[WEAK]** — vendor marketing claim, forum anecdote, or search-engine summary I could not independently verify.

---

## 0. Bottom line up front

**Question asked: is there ANY precedent for autonomously generating safety-relevant hands-on technical instruction for children, and can it be done without expert human review?**

**Answer: No precedent, and the evidence says no — not at present, not for the circuit-correctness half of the problem.**

Three findings carry most of the weight:

1. **The closest measurable proxy task — board-level schematic design from datasheets — has a top-model pass rate of 8.15%.** (HWE-Bench, arXiv 2603.18102). This is not "needs a bit of polish." This is the task failing more than nine times in ten. **[STRONG]**
2. **Every organisation that actually ships AI-assisted electronics design keeps a qualified human engineer as the terminal gate**, and says so explicitly — including the ones whose commercial interest is to claim otherwise (Diode Computers: *"Engineers still sign off every design"*). **[STRONG]**
3. **Every human-authored children's electronics curriculum found is authored and reviewed by domain experts and physically built and tested before publication**, and is usually additionally constrained by a hardware layer (kit, standards compliance, ≤24 V, magnet-polarised connectors) that removes most of the hazard *before* the instructions are written. The instructions are not the primary safety control. **[STRONG]**

The last point is the one most likely to be missed. In professionally produced children's electronics, **safety is achieved mostly in hardware and product certification, not in prose.** A generated curriculum that produces only prose inherits none of that protection.

There is a real, defensible middle position, developed in §7.

---

## 1. What a professionally produced children's electronics lab actually contains

### 1.1 Is there a published template or standard?

**There is no single published standard for an electronics lab document.** There are three overlapping layers that in practice function as one:

| Layer | Source | Status |
|---|---|---|
| Pedagogical structure | 5E model (Engage/Explore/Explain/Elaborate/Evaluate), NGSS three-dimensional learning | De facto standard in US science education; widely published templates **[STRONG]** |
| Physical-computing pedagogy | Raspberry Pi Foundation's 12 principles of computing pedagogy; three-level model (curriculum → teaching approaches → learning materials) | Published, organisation-specific **[STRONG]** |
| Publisher house template | Adafruit Learning System guide spec; SparkFun SIK/experiment-guide format | Published but proprietary house style **[MODERATE]** |

NGSS/5E lesson templates typically require: grade level, topic, **performance expectations**, learning outcomes, **prior student knowledge**, science & engineering practices, disciplinary core ideas, crosscutting concepts, **anticipated misconceptions**, the five 5E phases, and **materials list with sources**.
https://aae.lewiscenter.org/documents/AAE/Science/NGSS/5E%20NGSS%20Lesson%20Planning%20Template.doc
https://lessondraft.com/blog/science-lesson-plan-guide

Note what is *absent* from the generic template: **there is no mandatory safety field.** Safety enters through the science-education duty-of-care regime (§2.3), not through the lesson template. **[MODERATE — inference from the templates surveyed]**

### 1.2 Adafruit Learning System — the closest thing to a published spec

Adafruit publishes an explicit authoring guide with a required structure and a **two-stage moderation workflow** (initial moderation → final moderation → publication approval), with checks on page settings, featured products, and guide body.

Required structural elements include: cover + metadata, linked table of contents, overview, **parts list** (with a hard rule: `Product` element for ≤5 parts, `Add Parts` element for ≥6 or non-Adafruit parts), **Fritzing wiring diagram**, code with commenting and SPDX author/licence headers, image licensing attribution.
https://cdn-learn.adafruit.com/downloads/pdf/creating-great-guides-for-the-adafruit-learning-system.pdf
**[STRONG — primary source]**

Two things stand out:

- **The parts list is a first-class, format-constrained artefact**, not prose. Adafruit binds each part to a product SKU. That is the mechanism by which component identity is grounded — a specific purchasable part, not a description.
- **The published guide contains no explicit safety-protocol section.** Safety is not handled editorially at the guide level; it is handled by the products being Adafruit-designed low-voltage hardware and by the moderation gate. **[STRONG for the observation; MODERATE for the interpretation]**

The Adafruit Learning System GitHub repo is explicitly **closed to unreviewed contribution**: it is "only for Adafruit approved Learning System Guides," with outside authors redirected to Adafruit Playground. Code must compile against the current Arduino IDE.
https://github.com/adafruit/Adafruit_Learning_System_Guides
**[STRONG]**

That is the review model: *gated authorship + build-and-compile verification + two moderation passes*, not post-hoc fact-checking.

### 1.3 SparkFun

SparkFun's Inventor's Kit (SIK) v4.1 experiment guide is a 16-circuit / 5-project progression. Per circuit the guide provides: step-by-step build instructions, **circuit diagram**, **hookup table** (an explicit pin-to-pin mapping table — a machine-checkable artefact), full example code, concepts explained at point of use, and **a troubleshooting section per circuit**.
https://learn.sparkfun.com/tutorials/sparkfun-inventors-kit-experiment-guide---v41/all
https://media.digikey.com/pdf/Data%20Sheets/Sparkfun%20PDFs/BOK-15478_Web.pdf
**[STRONG]**

SparkFun additionally publishes a separate **Teacher's Guide to the Circuits** with learning objectives per circuit, i.e. the pedagogical layer is a *separate document* from the build layer.
https://cdn.sparkfun.com/assets/f/c/a/2/f/SparkFunInventorsKitSIKTeacherGuide.pdf
**[MODERATE — PDF was binary-encoded and could not be fully parsed; structure inferred from metadata and secondary description]**

SparkFun maintains a dedicated Department of Education producing the curriculum, and documents every original product with hookup guide + datasheet + schematic.
https://www.sparkfun.com/documentation

**The recurring per-activity primitive across Adafruit and SparkFun is: parts list (SKU-bound) → wiring diagram → hookup table → code → troubleshooting.** Troubleshooting is not optional garnish; it is where the failure modes the author encountered while physically building the thing get recorded. **A generator that has not built the circuit cannot author this section from evidence.**

### 1.4 micro:bit Foundation

Aimed at ages 8–14, grounded in constructivist learning theory. Lessons mapped to CSTA standards. Deployed in ~90% of UK primary schools (>21,000).
https://microbit.org/teach/lessons/
https://microbit.org/about/impact/research/
**[STRONG]**

Safety guidance is published as a **separate product-level document**, not per lesson:
- Max current from the 3V edge-connector pin to an external circuit: **100 mA**
- Only the supplied battery pack and USB lead
- **Explicit prohibition on portable battery chargers / USB charging ports**
- Zinc or alkaline only; **no rechargeables**; do not charge non-rechargeables; correct polarity; remove spent cells
- **"Do not leave your BBC micro:bit within reach of children under 8 years of age."**
- Handle by edges (ESD); no metal on the board (short/fire); away from water; store in anti-static bag
- Peripherals "should comply with the relevant standards and should be marked accordingly"
https://microbit.org/get-started/user-guide/electrical-product-guidance/
https://microbit.org/get-started/user-guide/safety/
**[STRONG — primary]**

This is the pattern to internalise: **the safety envelope is a small set of hard numeric constraints attached to the hardware (100 mA, ≥8 years, alkaline only), published once, and inherited by every lesson.** It is not re-derived per activity, and it is not something a lesson author is expected to invent.

### 1.5 Kit vendors and toy-form kits

- **Snap Circuits** (ages 5–9 for Beginner, 8+ for Pro): components are moulded snap-together blocks that look like real parts; no soldering, no loose wires. Marketed with a "circuit safe" safety device.
- **littleBits** (8+): magnetic connectors that **enforce correct polarity — it is physically impossible to connect a bit backwards.**
https://stemeducationguide.com/snap-circuits-vs-littlebits/
https://www.fractuslearning.com/best-snap-circuits-electronics-kits/
**[MODERATE — vendor/reviewer sources]**

This is the single most important structural observation in this section: **the dominant safety strategy in children's electronics is to make the dangerous configuration mechanically unbuildable.** littleBits' polarity magnets and Snap Circuits' fixed-footprint blocks mean a wrong instruction cannot produce a hazardous circuit. Breadboard + jumper wires + loose components — which is what a generated curriculum will most naturally target — deliberately removes that protection in exchange for authenticity.

- **ELEGOO / Freenove** manuals (35+ lessons, code, photos of assembled circuits) are the low-cost end. Documented quality complaints: hand-written resistor labels that are hard to read; a Freenove chapter that connects 5V/GND to a PCF8574 without clarifying resistor usage; example sketches that error in the IDE.
https://forums.raspberrypi.com/viewtopic.php?t=319412
https://www.manualslib.com/manual/4058976/Elegoo-Mega-2560.html
**[WEAK — forum anecdote, but directionally consistent]**

Useful calibration: **human-authored kit manuals at the budget end already contain the exact class of error a generator would produce.** The bar is not perfection. But those manuals ship with the physical components and a support channel, and the vendor carries product liability.

### 1.6 Tinkercad Circuits — the verification asset

Autodesk Tinkercad Circuits is a free browser-based **simulator for Arduino + breadboard circuits**, explicitly positioned so students "simulate ideas in a safe virtual space before wiring up," eliminating risk of damaging physical components.
https://www.tinkercad.com/teachers/electronics
https://tryengineering.org/news/tinkercad-circuits-simulate-electronics/
**[STRONG for existence and positioning]**

This matters more than its section length suggests: it is a **free, executable oracle for exactly the class of circuit a children's curriculum would use.** It is the most obvious candidate for closing the generate→verify loop (§7). I found no evidence of anyone using it programmatically as a verification backend for generated content. **[Absence of evidence, searched]**

### 1.7 Other structures worth knowing

- **Exploratorium Science Snacks**: "hands-on, **teacher-tested** activities," inexpensive easily-available materials, detailed instructions and images, clear explanations. The Tinkering Studio operates as an on-floor R&D lab with an open-source dissemination model.
https://www.exploratorium.edu/snacks
https://www.exploratorium.edu/tinkering
**[STRONG]** — note "teacher-tested" is a stated editorial claim, i.e. physical trial is part of their definition of done.
- **IEEE TryEngineering**: 130+ lesson plans, standards-aligned, sections include Background Concepts, Engineering Design Process, Design Challenge with criteria/constraints, Materials, Real World Applications, Digging Deeper.
https://tryengineering.org/lesson-plans/critical-load
**[MODERATE]**
- **Arduino Education Curriculum Grid** explicitly lists **Electronic Safety as the first item** in the Electronics Skills strand, before breadboarding and soldering.
https://content.arduino.cc/assets/Arduino%20Curriculum%20Grid_Student_Kit.pdf
**[STRONG]**
- **Raspberry Pi Foundation** digital making curriculum + 12 pedagogy principles.
https://www.raspberrypi.org/teach/pedagogy
https://static.raspberrypi.org/files/education/DigitalMakingCurriculum.pdf
**[STRONG]**

---

## 2. Safety standards and review practice

### 2.1 The hard regulatory numbers

**EN IEC 62115 (Electric toys — Safety)** — the European adaptation of IEC 62115:2017, for children under 14:
- **Supply voltage shall not exceed 24 V**, and internal voltages above 24 V must not pose a hazard.
- Insulation protection for live parts; withstand-voltage testing.
- Compliance with EN IEC 62115 requires *also* meeting **EN 71-1** (mechanical/physical), **EN 71-2** (flammability), **EN 71-3** (migration of certain elements).
https://blog.qima.com/lab-testing/guide-to-en-iec-62115-standard
https://www.compliancegate.com/toy-safety-standards-european-union/
https://webstore.ansi.org/preview-pages/bsi/preview_30420288.pdf
**[STRONG]**

**EN 71-1** requires that toys be accompanied by instructions for use/assembly/maintenance where appropriate, and mandates **warnings, age labels and user instructions for safe use *and foreseeable misuse***, applied visibly on toy, packaging or instructions. CEN/TR 15071 governs national translations of those warnings.
https://law.resource.org/pub/eu/toys/en.71.1.2014.html
https://www.intertek.com/toys-childrens-products/eu-toy-directive/
**[STRONG]**

**This is the sharpest legal point in the report: in the EU, the instructional text of a children's electronics product is itself a regulated safety artefact.** Warnings and instructions are a compliance deliverable under EN 71-1, not editorial content. Autonomously generating that text places generated output inside a conformity-assessment boundary.

**ASTM F963-23 (US)** — applies to all toys for children under 14. Since **20 April 2024**, toys must be tested by a **CPSC-accepted third-party laboratory**, and the responsible company must issue a **Children's Product Certificate (CPC) per batch**. F963-23 added enhanced measures for battery-operated toys addressing electrical risks.
https://www.eurofins.com/toys-hardlines/resources/articles/astm-f963-23-compliance-navigating-us-toy-safety-standards/
https://www.qima.com/consumer-products/lab-testing/us-standards-astm-f963
**[STRONG]**

**Reese's Law / 16 CFR 1263 (button & coin cells)** — CPSC adopted **ANSI/UL 4200A-2023** as the mandatory standard on 11 Sept 2023; mandatory for products manufactured or imported after **19 March 2024**. Requires **child-resistant battery compartments** (tool required, or two independent simultaneous motions) and specific ingestion-hazard warning labels. Named for Reese Hamsmith, 18 months old, died Dec 2020 after swallowing a coin cell.
https://www.federalregister.gov/documents/2023/09/21/2023-20334/safety-standard-for-button-cell-or-coin-batteries-and-consumer-products-containing-such-batteries
https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery
**[STRONG]**

Direct implication: **any generated activity that specifies a CR2032 (extremely common in children's electronics — LED throwies, micro:bit accessories, wearables) is touching a regime with a named child fatality behind it.** A coin-cell holder specified without a child-resistant compartment is a documented lethal hazard class, not a theoretical one.

### 2.2 Precedent that children's electronics kits do injure children

**School Specialty Publishing recall, 2006** — ~43,000 "Ideal" and "Brighter Child" science kits recalled including **"All About Electricity"** and **"The Science Search Lab: Electricity."** Failure mode: **the battery case overheats — thermal burn hazard.** One reported incident: a young boy with minor burns to his fingers. Sold July 2004 – May 2006, $16–$24.
https://www.cpsc.gov/Recalls/2006/school-specialty-publishing-recalls-childrens-science-kits-for-thermal-burn-hazard
**[STRONG — primary CPSC]**

The realistic hazard in low-voltage children's electronics is **not electric shock. It is thermal — overheated batteries, shorted cells, hot components — plus ingestion (coin cells) and burns (soldering).** A safety review that only checks "is the voltage low?" checks the wrong thing. A shorted AA alkaline pack at 4.5 V is entirely capable of the hazard that triggered a 43,000-unit recall.

### 2.3 School-side review practice

**UK — CLEAPSS.** Advisory service for a consortium of local authorities; publishes **model (general) risk assessments** and **Supplementary Risk Assessments (SRAs)** for particular-risk activities, plus **Student Safety Sheets**. Critically: schools use the model assessment, but **teachers must adapt it to their own circumstances** — building, equipment, proximity of other students.
https://science.cleapss.org.uk/resource-info/ps090-making-and-recording-risk-assessments-in-school-science.aspx
https://science.cleapss.org.uk/Resource/SSS096a-Risk-assessment.pdf
**[STRONG]**

This is the correct model for generated content: **generated guidance can at best be a model risk assessment. The adaptation step is legally the teacher's and cannot be generated away.**

**US — NSTA duty of care.** Teachers have a legal **duty of care**: provide safety instruction and appropriate supervision during *every* lab activity. Safety practices must be captured in a **safety acknowledgement form signed by student and parent/guardian**, kept on file, and **"no student should be permitted to participate in a laboratory activity without this document being on file."** NSTA publishes elementary/middle/high school versions. NSTA also advises districts to review insurance policies for adequate liability coverage for lab-based instruction.
https://www.nsta.org/nstas-official-positions/liability-science-educators-laboratory-safety
https://www.nsta.org/blog/acknowledgment-form-safer-contract
https://static.nsta.org/pdfs/LegalImplicationsOfDutyOfCareForScienceInstruction.pdf
**[STRONG]**

**Insurer/district requirements**: I found the NSTA recommendation that districts verify liability coverage for lab instruction, and generic school liability/student-accident coverage products. **I found no evidence of an insurer-mandated curriculum sign-off process specific to STEM content.** The gate is duty-of-care and district policy, not insurance underwriting.
https://www.berryinsurance.com/blog/guide-for-insuring-schools
**[MODERATE — including the negative finding]**

**Makerspace/soldering.** Soldering-iron tips run ~400 °F (up to 900 °F depending on application); flux fumes are the dominant respiratory hazard (not lead vapour); **lead-free solder can emit more toxic fumes than leaded** because fluxes are often PVC/chlorinated. Guidance calls for well-ventilated space, PPE, and with young people a zero-tolerance behaviour policy.
https://makezine.com/article/education/safety-in-school-makerspaces/
https://www.futurelearn.com/info/courses/build-a-makerspace/0/steps/39468
https://drs.illinois.edu/Page/SafetyLibrary/SolderingSafety
**[MODERATE]**

Note the counter-intuitive fact — *lead-free is not automatically the safer choice for fumes* — as an example of the kind of domain nuance a plausible-sounding generator gets backwards.

**Low-voltage classroom guidance** is informal but consistent: LED-lighting activities are appropriate from ages ~5–6 with adult help; motors and circuit design from ~10–12; and students should **never** experiment with wall outlets or car batteries.
https://des.sc.gov/sites/des/files/Library/battery_lesson.pdf
**[MODERATE]**

### 2.4 Summary of the safety envelope a generator would have to respect

| Constraint | Value | Source strength |
|---|---|---|
| Max toy supply voltage (EU) | **24 V** | STRONG |
| micro:bit external current from 3V pin | **100 mA** | STRONG |
| Toy age scope | **under 14** (EN 71 / ASTM F963) | STRONG |
| micro:bit minimum age | **8** | STRONG |
| Coin cells | child-resistant compartment + warning label mandatory (US, post-19 Mar 2024) | STRONG |
| Third-party lab test + CPC | mandatory for US toys post-20 Apr 2024 | STRONG |
| Dominant real hazard | **thermal / battery overheating**, ingestion, soldering burns — not shock | STRONG |
| Instructions & warnings | **themselves regulated** under EN 71-1 | STRONG |

---

## 3. Can LLMs get circuits right? The benchmark evidence

This is the section that should determine the design.

### 3.1 The decisive result: HWE-Bench

**HWE-Bench** — 300 board-level design tasks across 8 application domains, paired with **2,914 real IC datasheets**. Models generate schematics from functional requirements plus component documentation, then face **static electrical verification and dynamic circuit simulation**.

> **"the top-performing model achieved an overall pass rate of 8.15%."**

The authors conclude models show "initial engineering usability and documentation understanding" but **"lack physical intuition."**
https://arxiv.org/abs/2603.18102
**[STRONG]**

**Why this is the right benchmark to weight most heavily:** board-level design from datasheets — discrete parts, real components, real pinouts, verified by simulation — is structurally the same task as "specify a working breadboard circuit for a child." It is *not* IC/analog transistor-level design, which is harder than anything a curriculum needs. HWE-Bench is the closest published proxy, and the number is 8.15%.

### 3.2 Corroborating benchmarks

**CIRCUIT** (510 QA pairs, analog circuit reasoning):
- **GPT-4o: 48.04% accuracy on the final numerical answer**
- **GPT-4o: 27.45% pass rate on "unit tests"** (grouped question sets testing a coherent circuit)
- Conclusion: *"the most advanced LLMs still struggle with understanding circuits, which requires multi-level reasoning, particularly when involving circuit topologies."*
https://arxiv.org/abs/2502.07980
**[STRONG]**

The 48% → 27% collapse is the important shape: **models get isolated questions right about twice as often as they get a coherent multi-step circuit right.** A curriculum activity is a coherent multi-step circuit, not an isolated question. Spot-checking individual claims in a generated lab will systematically overestimate whether the lab works.

Documented error types include **approximation errors in division/exponent/log, and unit errors** — e.g. the benchmark records a model computing `R_out = 1/(250 × 10⁻³ S) = 1/0.25 kΩ = 4 kΩ`. That is a unit-scaling slip producing a confidently stated, wrong resistance. **[MODERATE — quoted via search summary of the paper]**

This is precisely the failure mode that matters for children's electronics, where nearly every activity turns on one arithmetic step: the LED current-limiting resistor.

**CircuitLM** (schematic generation from natural language). Documented baseline LLM failure modes, verbatim: models *"frequently hallucinate components, violate strict physical constraints, and produce non-machine-readable outputs."* Specifically catalogued:
- **component hallucination**
- **pin hallucination** (wrong pin names/numbers)
- **omission of essential supporting components — pull-ups, decoupling capacitors, current-limiting resistors, I²C multiplexers**

Zero-shot baselines: **ERC Pass@1 77–85%, but LLM-as-Judge Pass@1 only 21–51%.** The authors call this the "evaluation gap": baseline models generate **structurally valid but functionally flawed** circuits. Even with the full multi-agent + curated-component-database pipeline, ERC only reaches 83–88%, and major errors remain the primary residual failure mode.
https://arxiv.org/html/2601.04505v2
**[STRONG]**

**"Omission of current-limiting resistors" is a named, benchmark-documented LLM failure mode.** And omitting a current-limiting resistor is the canonical beginner LED-circuit error: the LED behaves as a constant-voltage device up to the point of self-destruction and depends entirely on external circuitry to limit current; at 9 V or 12 V it "will glow briefly and die almost instantly."
https://resources.altium.com/p/should-you-omit-a-current-limiting-resistor-for-led-if-youre-using-a-matching-voltage-power-supply
https://www.oemstock.com/blog/common-led-resistor-mistakes-and-how-to-fix-them
**[STRONG]**

So the highest-frequency LLM circuit failure and the highest-frequency children's-electronics circuit failure **are the same failure.** For a child on 3 V this destroys a component; on a 9 V battery it produces a hot, failing part in a child's hands. That is the thermal hazard class from §2.2.

**MMCircuitEval** — 3,614 multimodal QA pairs across digital and analog circuits and EDA stages. GPT-4v: **69.4% overall, 48.2% on back-end design.** InstructBLIP and BLIP2 score **<20%**. Significant performance gaps concentrated in back-end design and complex computation.
https://arxiv.org/abs/2507.19525
**[STRONG]**

**AMSbench** — ~8,000 questions, 8 models including Qwen2.5-VL and Gemini 2.5 Pro; "significant limitations… particularly in complex multi-modal reasoning and sophisticated circuit design."
https://arxiv.org/abs/2505.24138
**[STRONG]**

**Masala-CHAI** — 7,500 captioned SPICE netlists from 10 textbooks; fine-tuning yields ~46% relative improvement in Pass@1 within agentic frameworks, reaching **>40% Pass@1** on challenging generation tasks. Read the right way: **state-of-the-art *after* domain fine-tuning on a purpose-built corpus is ~40%.**
https://arxiv.org/abs/2411.14299
**[STRONG]**

**Practitioner test of LLMs as *verifiers*** (AutoCuro, ChatGPT + Gemini on two STM32 boards). Worked: component-placement review with heavily labelled diagrams, power-network analysis when explicitly annotated, generic checklist generation. **Failed completely: spatial reasoning, trace-width verification, top/bottom layer routing.** Testing on the 336-component board was abandoned. Verdict: LLMs are *"talking textbooks"* for design discussion, not verification. No numeric accuracy rates published.
https://autocuro.com/blog/can-llms-verify-pcb-designs
**[MODERATE — practitioner blog, methodology described but not peer-reviewed]**

**Do not plan to have an LLM check its own circuit.** That is the one role the evidence specifically rules out.

### 3.3 Component/datasheet lookup accuracy

A vendor (GerberGPT) claims **10,000 part-lookup queries across 47 datasheet families; ChatGPT-5 answered confidently on every question; only 37.2% correct** against authoritative manufacturer specs. Cited example: hallucinating PA9 as USART2 on an STM32F407VGT6.
https://www.gerbergpt.com/
**[WEAK — vendor marketing for a competing product; methodology not published; site was unreachable for direct verification. Treat the number as unusable and the direction as consistent with CircuitLM's peer-reviewed pin-hallucination finding.]**

Practising engineers' consensus, for what it is worth: an LLM has *"the distinct disadvantage of being untrustworthy to the point of just making stuff up in very convincing ways."*
https://forum.allaboutcircuits.com/threads/can-gpt-4-revolutionize-pcb-design-exploring-the-possibility-of-automating-footprints-and-schematics-creation-from-datasheets.192572/
**[WEAK — forum]**

### 3.4 Code generation, and the one study on novices

Arduino/embedded code is the other half of a physical-computing activity.

A controlled study of **novice Arduino programmers** compared self-programming vs ChatGPT-3.5-assisted. No significant difference in rubric scores or interest, but the **self-programming group scored significantly higher on posttest and on programming self-efficacy**, and **the ChatGPT group made significantly more program punctuation errors.**
https://digitalscholarship.unlv.edu/jrtc/vol8/iss1/1/
**[STRONG — controlled study, though small domain]**

This is the only direct evidence found on LLM-generated technical content and *children/novices learning electronics*, and it is mildly negative on learning outcomes, independent of correctness.

General code-generation error rates: GPT-3.5 ~18% error / GPT-4 ~12.5% error on Python tasks; GPT-3.5 answers to Stack-Overflow-style questions incorrect **52%** of the time. Typical errors: missing edge cases, **incorrect API usage especially for less common libraries**, control-flow logic errors.
https://arxiv.org/pdf/2504.18858
**[MODERATE]**

"Incorrect API usage for less common libraries" maps directly onto the sensor/display driver libraries a children's electronics curriculum lives on.

### 3.5 General scientific reliability and self-consistency

Washington State University (Cicek et al.), *Rutgers Business Review*, March 2026: >700 hypotheses from post-2021 journal papers, each posed 10 times.
- Surface accuracy **76.5% (2024, GPT-3.5) / 80% (2025, GPT-5 mini)**
- **~60% above chance after adjusting for guessing**
- **False-statement identification: 16.4%**
- **Answers matched only 73% of the time across identical repeated prompts**
https://www.sciencedaily.com/releases/2026/03/260317064452.htm
**[MODERATE — reported via ScienceDaily; the venue is a business review, and the domain is business hypotheses, so transfer to electronics is indirect]**

Two transferable points: **models are far worse at identifying that something is false than at confirming something true (16.4%)**, and **the same prompt gives different answers 27% of the time.** Both are hostile to a review strategy built on asking a model to check work.

**LLM-as-judge** is separately documented as **overconfident**: judges "tend to overestimate human agreement," with a calibration gap between stated confidence and actual accuracy; agreement is decent on objective tasks and poor on open-ended reasoning (~47%).
https://arxiv.org/html/2508.06225v2
https://proceedings.iclr.cc/paper_files/paper/2025/file/08dabd5345b37fffcbe335bd578b15a0-Paper-Conference.pdf
**[STRONG]**

---

## 4. Datasheet-grounded generation — what exists

This is the most encouraging section, and the most directly actionable.

**Yes, people are enforcing datasheet grounding, and it demonstrably helps — but it does not close the gap.**

**D2S-FLOW** — automated parameter extraction from datasheets for SPICE model generation. Three mechanisms: Attention-Guided Document Focusing, **Hierarchical Document-Enhanced Retrieval**, Heterogeneous Named Entity Normalization (handling inconsistent naming across manufacturers). Results: **EM 0.86, F1 0.92, Entity Coverage 0.96**, beating the strongest baseline by 19.4% / 5.7% / 13.1%.
https://arxiv.org/abs/2502.16540
**[STRONG]**

Read carefully: **extracting a parameter from a datasheet is a largely solved problem (F1 0.92).** *Designing a correct circuit with it* is the 8.15% problem. Grounding fixes the retrieval half, not the reasoning half.

**CircuitLM** grounds generation in a curated, embedding-powered **component knowledge base**, in five stages: component identification → **canonical pinout retrieval** → chain-of-thought reasoning → JSON schematic synthesis → visualisation. Explicitly "addresses LLM pin hallucinations by sourcing exact pin names and numbers from the curated database," and adds **a custom deterministic ERC engine** parsing CircuitJSON as a topological graph: galvanic short-circuit detection, passive component verification, **inductive load protection**, **logic-level voltage matching**, floating-input detection.
Result: **fatal errors nearly eliminated (μ≈0.0); major errors reduced but still the primary residual failure mode (μ=0.1–0.3); ERC Pass@1 only 83–88%.**
https://arxiv.org/html/2601.04505v2
**[STRONG]**

The transferable architecture: **a curated component database with canonical pinouts, plus a deterministic rule-checking engine that is not an LLM.** That combination is what eliminated *fatal* errors. Note it did not eliminate *major* errors.

**Diode Computers** (commercial, Anthropic partnership) — the most relevant industrial precedent:
- Claude works in **Zener**, a domain-specific language, so schematics are backed by Python-like code an LLM can reason over and diff.
- **Datasheets supplied in machine-readable form** alongside DSL docs and a small set of high-quality examples; model drafts reference modules per part.
- Composition over creation: model **searches a Registry and imports vetted building blocks** rather than inventing topologies.
- Stated failure mode: *"Models can sound confident about circuits that would never work. The only way to close that gap is to give them access to ground truth: simulation results that don't lie."*
- **"Engineers still sign off every design."** "Layout integration and human design review remain the final stages before fabrication."
https://blog.diode.computer/anthropic-partnership
**[STRONG — primary, company blog]**

That is a company commercially motivated to claim autonomy, describing: DSL + machine-readable datasheets + vetted component registry + simulation ground truth + **mandatory human engineer sign-off**. A separate third-party summary confirms **"Every Diode design is reviewed by experienced electrical engineers to ensure safety, compliance, and manufacturability before production."**
https://www.cofactr.com/case-studies/how-diode-computers-connected-pcb-design-directly-to-sourcing-with-cofactr
**[MODERATE]**

**pcbGPT** and **TypedSchematics** (block-based PCB tool with real-time detection of common connection errors) are further points in the same design space; the recurring theme in the literature is that **automated circuit generation "requires designs to correspond to real, library-available components with correct pin assignments,"** grounding decisions in datasheets, component libraries and structured knowledge representations.
https://arxiv.org/pdf/2606.01188
https://arxiv.org/pdf/2509.14576
**[MODERATE]**

**Broader safety-critical practice.** Across DO-178C (avionics), ISO 26262 (automotive), IEC 62304 (medical device software), the settled position is that LLMs are **drafting aids, not autonomous generators**: output is "rough and human review is mandatory"; "a qualified human must build and sign off on the actual assurance argument"; treat LLM output as **draft material only**; AI-generated content must **link back to traceable, re-runnable evidence.**
https://www.parasoft.com/blog/addressing-nasa-concerns-llm-safety-critical-development/
https://aurahealth.ch/llms-in-samd-regulatory-documentation/
**[MODERATE — vendor/consultancy blogs, but describing regulatory requirements that are themselves STRONG]**

---

## 5. Documented incidents: AI-generated instructional content causing or risking harm

### 5.1 The closest analogue — AI toys giving children physical instructions

**FoloToy "Kumma" teddy bear, November 2025.** PIRG *Trouble in Toyland 2025* found the GPT-4o-backed toy would tell children **where to find matches, knives, pills and plastic bags**, and would escalate into graphic sexual content. Outcome: **OpenAI suspended the developer for policy violations; FoloToy suspended sales of all products and announced a company-wide end-to-end safety audit.** (Sales resumed later in November after recall.)
https://pirg.org/edfund/resources/trouble-in-toyland-2025-a-i-bots-and-toxics-represent-hidden-dangers/
https://www.cnn.com/2025/11/19/tech/folotoy-kumma-ai-bear-scli-intl
https://gizmodo.com/ai-powered-teddy-bear-caught-talking-about-sexual-fetishes-and-instructing-kids-how-to-find-knives-2000687140
**[STRONG — NGO testing report + multiple independent outlets. Note: PIRG's own page returned 403 to direct fetch; details are via CNN/Gizmodo/UPI reporting of it.]**

**This is the single most on-point precedent in the entire report: an LLM autonomously generating hands-on physical instructions to children, deployed commercially, and it produced instructions to obtain fire and blades.** It was caught by an external consumer-advocacy organisation, not by the vendor, not by the model provider, and not by any toy-safety certification.

**Common Sense Media** rates Gemini "Under 13" and "Gemini with teen protections" both **High Risk**, citing fundamental design flaws and lack of age-appropriate safety measures; found Grok not safe for teens; and recommends **no AI chatbot use for children 5 and under, and ages 6–12 only under adult supervision.**
https://www.commonsensemedia.org/ai-ratings/ai-risk-assessments
https://www.commonsensemedia.org/press-releases/googles-gemini-platforms-for-kids-and-teens-pose-risks-despite-added-filters-common-sense-media-reports
**[STRONG]**

Note the age overlap: **the recommended supervision band (6–12) is exactly the target band for children's electronics activities.**

### 5.2 AI-generated instructional books — the foraging precedent

AI-generated mushroom foraging guides proliferated on Amazon (2023). Field mycologists identified specific dangerous errors, notably **encouraging identification by smell and taste.** Four excerpts scored 100% on AI-detection tools. Authors were largely non-existent. The New York Mycological Society warned the proliferation could "mean life or death."
https://www.404media.co/ai-generated-mushroom-foraging-books-amazon/
https://civileats.com/2023/10/10/ai-is-writing-books-about-foraging-what-could-go-wrong/
**[STRONG — original 404 Media reporting + expert bodies]**

The structural parallel is exact: **a genre of instructional non-fiction where the text looks authoritative, the reader is a beginner who cannot detect the error, and the error is only revealed by physical consequence.** Children's electronics is the same genre with a lower ceiling on harm.

### 5.3 Other documented instructional-harm incidents

- **Pak'nSave "Savey Meal-bot"** (NZ, Aug 2023, GPT-3.5): generated an "aromatic water mix" that **produces chlorine gas**, described as "the perfect nonalcoholic beverage," **with no hazard disclaimer.** AI Incident Database #594.
https://incidentdatabase.ai/cite/594/
https://www.forbes.com/sites/mattnovak/2023/08/12/supermarket-ai-gives-horrifying-recipes-for-poison-sandwiches-and-deadly-chlorine-gas/
**[STRONG]**
The mechanism is worth naming: **the model was competent at the format and blind to the chemistry.** A generator competent at lesson-plan format and blind to circuit physics fails identically.

- **Google AI Overviews** (May 2024): glue on pizza (sourced from an 11-year-old Reddit comment), eat one rock per day (sourced from The Onion). Google restricted the feature and retrained to downrank humour/forum sources.
https://www.forbes.com/sites/roberthart/2024/05/31/google-restricts-ai-search-tool-after-nonsensical-answers-told-people-to-eat-rocks-and-put-glue-on-pizza/
**[STRONG]**

- **Hiking/navigation.** July 2026: two Lithuanian hikers stranded on climbing terrain below Niebieska Turnia in the Polish Tatras after consulting ChatGPT about a shortcut — **helicopter rescue.** 2025: two hikers rescued on Unnecessary Mountain, BC after following a ChatGPT-planned route. The **OECD AI monitor** documents travellers misled to non-existent destinations (the fabricated "Sacred Canyon of Humantay," Peru) and warns of physical-harm risk. BC search-and-rescue reported a concerning increase in AI-related incidents across 1,960 SAR activations in 2024.
https://cybernews.com/ai-news/hikers-rescued-chatgpt/
https://www.nationalobserver.com/2025/06/17/news/alltrails-ai-tool-search-rescue-members
https://futurism.com/artificial-intelligence/ai-hallucination-landmarks-tourists
**[MODERATE→STRONG — multiple independent incidents, OECD cited]**

- **Reddit Answers** flagged by moderators for dangerous medical advice they could not disable or hide.
https://www.yahoo.com/news/article/moderators-call-ai-controls-reddit-230749897.html
**[MODERATE]**

### 5.4 AI-generated *educational* content specifically

**PLOS ONE (Powell & Courchesne)** — exploratory case study, ChatGPT generating a **first-grade science lesson on heredity** across nine refinement prompts. Findings:
- **Hallucinated resource**: recommended *"Why Do Tigers Have Stripes? And Other Questions About Evolution"* by Mary Kay Carson. The author is real and writes similar books; **the book does not exist.** Not findable on Amazon or in library databases.
- **Safety-relevant error**: suggested **using live animals (dogs or cats) in the classroom**, which many US schools prohibit on health and safety grounds.
- **Missing details**: no structure for observation activities, no discussion prompts, undefined vocabulary timing.
- **Age-inappropriateness**: homework for first-graders without age-appropriateness guidance.
- Conclusion: teachers **must** read over and revise; outputs are starting points requiring critical expert examination.
https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0305337
**[STRONG — peer-reviewed, though n=1 case study]**

**This is the closest published study to the task at hand, and in a single elementary science lesson it produced both a hallucinated resource and a school-safety violation.** The hallucinated book is instructive: plausible author, plausible title, plausible subject, non-existent object. The component-and-part-number analogue is obvious.

Corroborating: **>40%** of students in a Discrete Mathematics course and **>50%** in Programming Language Principles reported encountering incorrect information in AI-generated materials 1–3 times; **53% of errors classified as hallucinations**; AI-generated learning objectives "often superficial," requiring extensive edits.
https://arxiv.org/pdf/2507.11543
**[MODERATE]**

**Commercial AI lesson-planning tools** (MagicSchool, Khanmigo, Diffit, Brisk, Curipod, Eduaide, Education Copilot) universally position output as **a first draft requiring teacher customisation** — "most teachers treat it as a first draft that needs 10-15 minutes of customization rather than a finished product." Compliance emphasis is FERPA/COPPA/SOC 2 — i.e. **data protection, not content correctness.** None claims autonomous production of validated hands-on lab content.
https://www.forasoft.com/blog/article/automated-lesson-plan-generation-software
**[MODERATE]**

**Curriculum-publishing practitioners** are blunter: *"No AI model is trained to optimize for adoption review criteria, developmental benchmarks by grade band, equity and representation standards, accessibility compliance, or cross-program editorial coherence,"* each requiring a qualified human K-12 reviewer **throughout the workflow, not just as a final check.** AI-generated K-12 content "can pass a read and fail adoption review."
https://www.sixredmarbles.com/insights/k-12-ai-content-quality-review/
**[MODERATE — industry vendor, but a curriculum publisher describing its own gates]**

**Policy layer.** UNESCO's *Guidance for Generative AI in Education and Research* proposes a **human-agent, age-appropriate approach to ethical validation and pedagogical design**, stressing validation of GenAI systems for pedagogical appropriateness; it notes institutions are **largely unprepared to validate the tools.** OECD promotes human judgement, feedback and oversight at the centre.
https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research
https://www.oecd.org/content/dam/oecd/en/publications/reports/2026/01/oecd-digital-education-outlook-2026_940e0dd8/062a7394-en.pdf
**[STRONG]**

Recent work on agentic educational content generation converges on **"a principled division of labor"**: agentic AI as *scalable first-line quality control*, humans essential for pedagogical depth and instructional validity — with the specific warning that **automated validation was prone to approving items that were technically correct but instructionally shallow.**
https://arxiv.org/pdf/2604.03926
**[MODERATE]**

---

## 6. Direct answer to the question posed

### 6.1 Is there ANY precedent for autonomously generating safety-relevant hands-on technical instruction for children?

**One, and it is a cautionary tale, not a template.**

The **FoloToy Kumma** bear is the only found instance of an LLM autonomously producing hands-on physical guidance to children at scale in a commercial product. It told children where to find matches and knives. It was withdrawn after external NGO testing, and OpenAI cut off the developer. (§5.1) **[STRONG]**

Everything else in the adjacent space is **assistive with a mandatory human gate**:
- AI lesson-planning tools → explicit first-draft framing, teacher customisation assumed. (§5.4)
- AI circuit/PCB design → Diode Computers, the most advanced commercial case, with DSL + machine-readable datasheets + vetted registry + simulation, still: **"Engineers still sign off every design."** (§4)
- Safety-critical technical documentation in avionics/medical → LLM output is draft material; qualified human sign-off is a regulatory requirement. (§4)

**Nobody is doing this autonomously. The people best equipped to do it, with the strongest commercial incentive to claim they do, explicitly say they do not.** **[STRONG]**

### 6.2 Can it be done without expert human review?

**Not for circuit correctness and component values. The benchmark numbers do not support it.**

- 8.15% top pass rate on datasheet-grounded board-level schematic design (HWE-Bench)
- 27.45% GPT-4o pass rate on grouped circuit unit tests (CIRCUIT)
- 21–51% functional Pass@1 for zero-shot schematic generation, against 77–85% *structural* validity — the "evaluation gap": circuits that look right and do not work (CircuitLM)
- Omission of current-limiting resistors is a **named, catalogued** LLM failure mode — and is simultaneously the canonical way a children's LED circuit destroys a component and gets hot
- Pin/component hallucination is a **named, catalogued** LLM failure mode
- Models identify false statements at **16.4%** and give inconsistent answers to identical prompts **27%** of the time
- LLM-as-judge is **overconfident and mis-calibrated** — so self-review does not rescue this
- The one direct practitioner test of LLMs *verifying* hardware designs concluded "talking textbooks, not verification"

**Three claims I want to make precise, because they are where a plan is most likely to go wrong:**

**(a) The safety envelope is the easy part; the circuit is the hard part.** The safety constraints are a small, stable, citable set of numbers (§2.4): ≤24 V, ≤100 mA on a micro:bit 3V pin, ages 8+/under-14, coin-cell rules, no mains, adult supervision, ventilation for soldering. An LLM can reliably reproduce a short constraint list it is given. It cannot reliably produce a working circuit. **Do not let good performance on the safety boilerplate be read as competence at the engineering.** The Savey Meal-bot was fluent at recipe format and blind to chemistry.

**(b) Low voltage does not mean low hazard.** The one documented children's-electronics recall in this report is a **battery-case thermal burn** at toy voltages (§2.2), and the CPSC coin-cell regime exists because of a **child fatality** (§2.1). "It's only 3 volts" is not a safety argument. Short-circuit, reverse polarity, over-current and battery-chemistry errors are the live hazards, and all four are things a wrong instruction can cause.

**(c) In the EU the instructions are themselves regulated.** EN 71-1 makes warnings and instructions for safe use *and foreseeable misuse* a compliance deliverable (§2.1). Generated instructional text for a children's electronics product is not merely editorial content; it sits inside a conformity-assessment boundary.

### 6.3 What CAN be generated without expert review

Being fair to the technology — the following are supported by the evidence as low-risk to generate:

- **Pedagogical scaffolding**: 5E phase structure, learning objectives, standards mapping, vocabulary, discussion prompts, extension activities, assessment questions. (Caveat: objectives are documented as often "superficial," and automated validation approves items that are "technically correct but instructionally shallow" — a quality problem, not a safety problem.)
- **Narrative, framing, real-world context, differentiation.**
- **Restating a supplied safety envelope** — the constraint list, not its derivation.
- **First-draft structure** for a human expert to fill and correct.
- **Retrieval and extraction from datasheets** — genuinely strong (D2S-FLOW F1 0.92), *provided the datasheet is retrieved by exact part number rather than recalled from weights.*

---

## 7. The defensible architecture, if this is being built anyway

Synthesised from what actually works in CircuitLM, Diode, Adafruit, littleBits and CLEAPSS. Ordered by how much risk each removes.

1. **Constrain the hardware, not the prose.** This is the highest-leverage control and the one the human curricula rely on most. A closed, pre-vetted component library (specific SKUs, like Adafruit's product-bound parts list) with canonical pinouts; ideally a kit that is already EN 62115 / ASTM F963 certified. littleBits made the wrong circuit *unbuildable*; a fixed component set with fixed roles approximates that in software. **Generation composes vetted blocks; it does not invent topologies.** (Diode's "composition over creation.")

2. **Hard-code the safety envelope as non-generated constants.** ≤24 V; supply-specific current limits; age floor; coin-cell rules; no mains, no rechargeable-charging, no unattended battery packs; soldering only with stated ventilation/PPE/age. Cite the standard next to each number. These must be *asserted*, never inferred, never re-derived per activity.

3. **Deterministic rule checking that is not an LLM.** CircuitLM's ERC engine is the model: shorts, current-limit presence, voltage-level matching, floating inputs, polarity, inductive-load protection. This is what eliminated *fatal* errors. It is ordinary code over a structured circuit representation, not a prompt.

4. **Simulation as ground truth.** Diode: *"simulation results that don't lie."* Tinkercad Circuits simulates precisely the Arduino/breadboard circuits a children's curriculum uses, free, and I found no evidence of anyone using it as a verification backend for generated content — a genuine gap. A circuit that has not been simulated or built should not ship.

5. **Emit structured circuits, not prose.** Netlist / hookup table / component list as the primary artefact, with prose rendered *from* it. Prose cannot be checked; a hookup table can. This also matches how Adafruit and SparkFun already structure their guides.

6. **Every numeric value traced to a retrieved datasheet**, by exact part number, retrieved not recalled. No unsourced component value should survive to output. This is the one thing the literature says is reliably achievable.

7. **A named human expert sign-off gate before any child touches it**, recorded. Every serious actor in this space has one. It is also what the NSTA duty-of-care and CLEAPSS regimes assume exists.

8. **Frame generated safety guidance as a model risk assessment requiring local adaptation** — CLEAPSS's explicit position. Do not let it read as a completed risk assessment.

**What not to do:** do not use an LLM to check the LLM's circuit. Overconfident judges (§3.5), 16.4% false-statement detection, 27% self-inconsistency, and the one practitioner test of LLM hardware verification concluding "talking textbooks, not verification" all point the same way. A second model agreeing is not evidence.

---

## 8. Evidence gaps and honest caveats

- **Adafruit's and SparkFun's internal technical-accuracy review processes are not publicly documented** beyond the moderation workflow and the closed-contribution repo policy. I searched specifically and found no published editorial standard for technical correctness. Their real process is likely "engineers who designed the board write the guide and build the circuit," but that is inference. **[Absence of evidence, searched]**
- **No published incident of AI-generated *electronics* instruction injuring a child was found.** The evidence is by analogy (foraging, recipes, hiking, AI toys) plus benchmark failure rates. That analogy is strong but it is an analogy — say so rather than overstating.
- **The GerberGPT 37.2% figure is vendor marketing and should not be cited as a number.** Its direction agrees with peer-reviewed pin-hallucination findings; that is all it establishes.
- **Some 2026 arXiv results (HWE-Bench, CircuitLM) are recent and may be pre-peer-review.** I fetched both directly and read their reported numbers; HWE-Bench's 8.15% is doing heavy lifting in this report and is worth re-verifying at publication.
- **PIRG's primary report page returned HTTP 403**; the Kumma findings here come from CNN, Gizmodo, UPI and Fox Business reporting on it, which are consistent with each other.
- **The Common Sense Media AI Toys risk assessment PDF and the SparkFun Teacher's Guide PDF could not be parsed** (binary-encoded); their contents are represented via secondary description.
- **The Cicek et al. accuracy study is in business-hypothesis territory**, reported via ScienceDaily, in a business review venue. The 16.4%-false-detection and 73%-consistency figures are striking and directionally useful, but transfer to electronics is indirect.
- **No insurer-mandated STEM-curriculum sign-off process was found** — the operative gate in schools is duty of care and district policy, not underwriting. This is a negative finding from a targeted search, not an exhaustive one.
- **No evidence found of anyone using a circuit simulator as an automated verification backend for LLM-generated educational content.** If that is the intended design, it appears to be novel — which cuts both ways.

---

## Source list

**Curricula and publishers**
- https://microbit.org/get-started/user-guide/electrical-product-guidance/
- https://microbit.org/get-started/user-guide/safety/
- https://microbit.org/teach/lessons/
- https://microbit.org/about/impact/research/
- https://cdn-learn.adafruit.com/downloads/pdf/creating-great-guides-for-the-adafruit-learning-system.pdf
- https://github.com/adafruit/Adafruit_Learning_System_Guides
- https://learn.sparkfun.com/tutorials/sparkfun-inventors-kit-experiment-guide---v41/all
- https://media.digikey.com/pdf/Data%20Sheets/Sparkfun%20PDFs/BOK-15478_Web.pdf
- https://cdn.sparkfun.com/assets/f/c/a/2/f/SparkFunInventorsKitSIKTeacherGuide.pdf
- https://www.sparkfun.com/documentation
- https://content.arduino.cc/assets/Arduino%20Curriculum%20Grid_Student_Kit.pdf
- https://www.arduino.cc/education
- https://www.raspberrypi.org/teach/pedagogy
- https://static.raspberrypi.org/files/education/DigitalMakingCurriculum.pdf
- https://www.exploratorium.edu/snacks
- https://www.exploratorium.edu/tinkering
- https://tryengineering.org/lesson-plans/critical-load
- https://www.tinkercad.com/teachers/electronics
- https://tryengineering.org/news/tinkercad-circuits-simulate-electronics/
- https://stemeducationguide.com/snap-circuits-vs-littlebits/
- https://www.fractuslearning.com/best-snap-circuits-electronics-kits/
- https://aae.lewiscenter.org/documents/AAE/Science/NGSS/5E%20NGSS%20Lesson%20Planning%20Template.doc
- https://lessondraft.com/blog/science-lesson-plan-guide

**Standards, safety and school practice**
- https://blog.qima.com/lab-testing/guide-to-en-iec-62115-standard
- https://www.compliancegate.com/toy-safety-standards-european-union/
- https://webstore.ansi.org/preview-pages/bsi/preview_30420288.pdf
- https://law.resource.org/pub/eu/toys/en.71.1.2014.html
- https://www.intertek.com/toys-childrens-products/eu-toy-directive/
- https://www.eurofins.com/toys-hardlines/resources/articles/astm-f963-23-compliance-navigating-us-toy-safety-standards/
- https://www.qima.com/consumer-products/lab-testing/us-standards-astm-f963
- https://www.federalregister.gov/documents/2023/09/21/2023-20334/safety-standard-for-button-cell-or-coin-batteries-and-consumer-products-containing-such-batteries
- https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery
- https://www.cpsc.gov/Recalls/2006/school-specialty-publishing-recalls-childrens-science-kits-for-thermal-burn-hazard
- https://science.cleapss.org.uk/resource-info/ps090-making-and-recording-risk-assessments-in-school-science.aspx
- https://science.cleapss.org.uk/Resource/SSS096a-Risk-assessment.pdf
- https://www.nsta.org/nstas-official-positions/liability-science-educators-laboratory-safety
- https://www.nsta.org/blog/acknowledgment-form-safer-contract
- https://static.nsta.org/pdfs/LegalImplicationsOfDutyOfCareForScienceInstruction.pdf
- https://makezine.com/article/education/safety-in-school-makerspaces/
- https://drs.illinois.edu/Page/SafetyLibrary/SolderingSafety
- https://www.futurelearn.com/info/courses/build-a-makerspace/0/steps/39468
- https://des.sc.gov/sites/des/files/Library/battery_lesson.pdf
- https://www.berryinsurance.com/blog/guide-for-insuring-schools

**LLM circuit/EDA benchmarks and grounding**
- https://arxiv.org/abs/2603.18102 (HWE-Bench — 8.15%)
- https://arxiv.org/abs/2502.07980 (CIRCUIT — 48.04% / 27.45%)
- https://arxiv.org/html/2601.04505v2 (CircuitLM)
- https://arxiv.org/abs/2507.19525 (MMCircuitEval)
- https://arxiv.org/abs/2505.24138 (AMSbench)
- https://arxiv.org/abs/2411.14299 (Masala-CHAI)
- https://arxiv.org/abs/2502.16540 (D2S-FLOW)
- https://arxiv.org/pdf/2606.01188 (pcbGPT)
- https://arxiv.org/pdf/2509.14576 (TypedSchematics)
- https://blog.diode.computer/anthropic-partnership
- https://www.cofactr.com/case-studies/how-diode-computers-connected-pcb-design-directly-to-sourcing-with-cofactr
- https://autocuro.com/blog/can-llms-verify-pcb-designs
- https://www.gerbergpt.com/ (WEAK — vendor claim)
- https://forum.allaboutcircuits.com/threads/can-gpt-4-revolutionize-pcb-design-exploring-the-possibility-of-automating-footprints-and-schematics-creation-from-datasheets.192572/
- https://resources.altium.com/p/should-you-omit-a-current-limiting-resistor-for-led-if-youre-using-a-matching-voltage-power-supply
- https://www.oemstock.com/blog/common-led-resistor-mistakes-and-how-to-fix-them

**LLM reliability, education content, and incidents**
- https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0305337
- https://digitalscholarship.unlv.edu/jrtc/vol8/iss1/1/
- https://arxiv.org/pdf/2507.11543
- https://arxiv.org/pdf/2504.18858
- https://www.sciencedaily.com/releases/2026/03/260317064452.htm
- https://arxiv.org/html/2508.06225v2
- https://proceedings.iclr.cc/paper_files/paper/2025/file/08dabd5345b37fffcbe335bd578b15a0-Paper-Conference.pdf
- https://arxiv.org/pdf/2604.03926
- https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research
- https://www.oecd.org/content/dam/oecd/en/publications/reports/2026/01/oecd-digital-education-outlook-2026_940e0dd8/062a7394-en.pdf
- https://www.sixredmarbles.com/insights/k-12-ai-content-quality-review/
- https://www.forasoft.com/blog/article/automated-lesson-plan-generation-software
- https://pirg.org/edfund/resources/trouble-in-toyland-2025-a-i-bots-and-toxics-represent-hidden-dangers/
- https://www.cnn.com/2025/11/19/tech/folotoy-kumma-ai-bear-scli-intl
- https://gizmodo.com/ai-powered-teddy-bear-caught-talking-about-sexual-fetishes-and-instructing-kids-how-to-find-knives-2000687140
- https://www.commonsensemedia.org/ai-ratings/ai-risk-assessments
- https://www.commonsensemedia.org/press-releases/googles-gemini-platforms-for-kids-and-teens-pose-risks-despite-added-filters-common-sense-media-reports
- https://www.404media.co/ai-generated-mushroom-foraging-books-amazon/
- https://civileats.com/2023/10/10/ai-is-writing-books-about-foraging-what-could-go-wrong/
- https://incidentdatabase.ai/cite/594/
- https://www.forbes.com/sites/mattnovak/2023/08/12/supermarket-ai-gives-horrifying-recipes-for-poison-sandwiches-and-deadly-chlorine-gas/
- https://www.forbes.com/sites/roberthart/2024/05/31/google-restricts-ai-search-tool-after-nonsensical-answers-told-people-to-eat-rocks-and-put-glue-on-pizza/
- https://cybernews.com/ai-news/hikers-rescued-chatgpt/
- https://www.nationalobserver.com/2025/06/17/news/alltrails-ai-tool-search-rescue-members
- https://futurism.com/artificial-intelligence/ai-hallucination-landmarks-tourists
- https://www.parasoft.com/blog/addressing-nasa-concerns-llm-safety-critical-development/
- https://aurahealth.ch/llms-in-samd-regulatory-documentation/
