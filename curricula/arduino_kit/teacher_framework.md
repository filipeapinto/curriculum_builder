# Teacher Framework — Discovering Electronics Without Programming

## Purpose and promise

This workbook is for an absolute beginner, approximately age 12 and above, using the ELEGOO UNO R3 Super Starter Kit **without using the Arduino as a controller or writing code**. Its aim is not to make students memorise parts. Each investigation should help them make, test, explain, and revise a claim about how electricity behaves.

The workbook uses low-voltage, battery/USB-powered activities only. A student must never connect a breadboard circuit to wall power, a mains adapter with bare wires, or an unknown power supply.

The central learning cycle is:

> **Notice → Predict → Build → Measure/observe → Explain → Improve → Reflect**

Every lab must use that cycle in the same order. The student should be able to open any chapter and know where to find the safety rule, the wiring plan, the evidence table, and the explanation.

## Course-wide learning outcomes

By the end, a student should be able to:

1. Identify common passive components, switches, indicators, transducers, and modules from their package/markings and schematic symbols.
2. Read a breadboard: connected rows, centre gap, power rails, and the fact that rail breaks are common.
3. Use a digital multimeter (DMM) safely to measure voltage, resistance, continuity, diode behaviour, and—only when explicitly taught—current.
4. Distinguish voltage (electrical push), current (rate of charge flow), resistance (opposition to current), power (rate of energy transfer), and polarity (a required direction).
5. Predict and verify simple series and parallel circuits, including a current-limiting resistor with every ordinary LED.
6. Use data and observations rather than appearance alone to identify faults: open circuit, short circuit, reversed polarity, wrong breadboard row, depleted battery/source, and incorrect DMM setting.
7. Explain that some kit devices need a controller or a timed/protocol signal to demonstrate their intended operation. They can still be inspected or partly characterised honestly, but not claimed to be fully tested.

## Required lab template

Each lab must use the headings below, in this order. A lab writer may add a short extension, but may not omit a heading. Keep one normal lab to 2–4 student-facing pages, excluding optional teacher notes.

### 1. Lab number and title

Use a short, action-oriented title, e.g., **Lab 05 — Resistor: Controlling Current**. Add a one-line *big idea* in plain language.

### 2. Component card

Include at a glance:

| Field | Required content |
| --- | --- |
| What it is | One beginner-friendly sentence. |
| How to recognise it | Photograph/illustration, package features, markings, pin count, and schematic symbol where relevant. |
| What it does in a circuit | One precise sentence without metaphor-only explanation. |
| Polarity / orientation | `Polarised`, `not polarised`, or `orientation matters for this setup`; show the physical cue. |
| What can be tested here | `Full functional test`, `Basic electrical test`, or `Partial characterisation`; explain the limit. |

Never identify a part solely by colour, because kit revisions can vary.

### 3. Aim

One observable learning target beginning with **“I can…”**. It must name both a practical and conceptual outcome.

*Example:* “I can use a DMM to measure a resistor and explain why an LED needs one in series.”

### 4. Safety check

Show the standard safety box plus any lab-specific hazards. Students should tick each item before building. Use direct verbs and avoid alarmist language.

Standard wording:

- Use only the specified low-voltage power source (normally 3–5 V DC).
- Disconnect power before moving wires or changing the circuit.
- Check for a direct wire path between `+` and `–` before applying power.
- Never put a DMM set to **current** directly across a supply.
- Do not connect the breadboard to household/mains electricity.
- Stop if a component, wire, or battery becomes hot; disconnect power and ask an adult/teacher.
- LEDs, diodes, electrolytic capacitors, transistors, and integrated circuits have orientations; check their markings first.

If a coin cell is used, add: keep it away from young children and never short it. If a piezo/buzzer is used, add a hearing-comfort note. If a motor/servo is considered, add: keep fingers, hair, and loose clothing away from moving parts.

### 5. Materials and equipment

Specify exact quantities, expected values/ranges, and alternate names. Separate **from the kit**, **shared equipment**, and **optional extension**. Include a DMM setting where it prevents mistakes. Do not quietly assume a bench power supply, Arduino, or oscilloscope.

### 6. Before you build: prediction

Provide one question that can be answered before wiring, with a sentence stem:

> “I predict that ___ will happen because ___.”

Predictions are hypotheses, not scored as right or wrong. Later, require students to compare their prediction with evidence.

### 7. Setup and circuit map

Use a compact, labelled breadboard infographic plus a schematic for every powered circuit. The diagram must show:

- supply `+` and `–` clearly, with voltage stated;
- breadboard row/column placement sufficient to reproduce the circuit;
- every resistor value, LED/diode orientation, transistor pin label, and polarised capacitor marking;
- the DMM leads and mode when a measurement is part of the setup;
- a **power-off wiring check** before a power-on step.

Use conventional schematic flow left-to-right where practical: source at left/top, ground at bottom, signal direction left-to-right. Do not use colour as the only way to distinguish polarity; label `+`, `–`, `A` (anode), `K` (cathode), `C/B/E`, or pin names.

### 8. Build and test steps

Number steps one action at a time. A beginner should not need to infer a missing connection. Use this rhythm:

1. Identify the component and verify its orientation/value with a power-off check.
2. Build the circuit with power disconnected.
3. Conduct a visual short-circuit and breadboard-row check.
4. Apply the stated low voltage.
5. Observe or measure one named variable.
6. Change **one** variable only, if the lab includes a comparison.
7. Disconnect power before reconfiguration.

Place a brief **Check** after 2–4 actions, such as “The LED should be off until the switch closes.” Never prescribe an uncertain outcome as proof that the part is good; use conditional phrasing and troubleshooting.

### 9. Evidence: observation and measurement table

Every lab needs a small preformatted table. Include units in headers and at least three data rows when a variable changes. Leave space for *observed*, *measured*, and *unexpected result* where relevant.

Minimum patterns:

| Trial | What changed | Prediction | Observation | Measurement (unit) |
| --- | --- | --- | --- | --- |

For a DMM reading, name the mode in the table or caption: `V DC`, `Ω`, `continuity`, or `diode`. Use `OL`/open loop as a valid result when appropriate; teach that it normally means the meter sees a resistance beyond its range or no conductive path.

### 10. Make sense of it

Use three layers, each short:

1. **What happened?** State the evidence pattern in ordinary language.
2. **Why?** Give a correct causal explanation using no more than two new technical terms; define each in a callout.
3. **Connect it.** Relate the result to a circuit they will meet later.

Use analogies only after the physical explanation and label them as analogies. Avoid saying current is “used up”; components transfer electrical energy to light, heat, sound, motion, or stored electric/magnetic energy while charge continues around a complete circuit.

When calculations are appropriate, show substitution with units, then answer with sensible rounding:

`I = V / R`, `V = I × R`, `P = V × I`.

Do not require a calculation before the student has observed the phenomenon.

### 11. Reflection

End with 2–3 prompts:

- “My prediction was supported/not supported because…”
- “One piece of evidence was…”
- “If the circuit did not work, I would check…”
- “Where might this component be useful?”

One prompt must require a claim supported by a measurement or observation—not a definition recalled from memory.

### 12. Troubleshooting ladder

Use a calm, ordered fault-finding list. Begin with the least risky checks.

1. Disconnect power.
2. Compare every lead to the diagram; confirm the correct breadboard rows and rail continuity.
3. Check source voltage with the DMM in `V DC` mode.
4. Check component value/orientation with power off.
5. Check continuity of wires/switch contacts where suitable.
6. Rebuild one section at a time; do not randomly move several wires at once.

Include component-specific likely causes and a *never do this* warning if a fault could tempt a student into a short circuit, an LED without a resistor, or unsafe DMM use.

### 13. Quick assessment and extension

Every lab closes with:

- **Check for understanding:** two questions: one explain/predict and one interpret/diagnose.
- **Success criteria:** a three-item student checklist (build, evidence, explanation).
- **Optional extension:** a safe, one-variable challenge clearly marked as optional.

Provide concise answer guidance in a teacher-only note or answer key, not mixed into student instructions.

## Non-negotiable electrical facts and safety standards

### Power limits and source rules

- Standard student circuits use a regulated **3–5 V DC** source. State the actual voltage chosen in every diagram.
- Use a USB power bank, a breadboard power module fed by USB, or other regulated low-voltage classroom source. Do not expose students to mains wiring.
- A rectangular 9 V battery is not a default breadboard source. Its internal resistance makes results unreliable and it can damage low-voltage parts if misused.
- Disconnect power before any rewiring. It is acceptable to power a circuit only long enough to make the stated observation.
- Treat unexplained heat, smell, swelling, smoke, or leaking as a stop condition. Do not reuse a damaged component.

### Component protection rules

- **LEDs:** use a series current-limiting resistor. For a 5 V supply, use **220 Ω to 1 kΩ** unless the lab specifies otherwise. Begin with 1 kΩ for a safe visible result.
- **Ordinary diodes:** observe anode/cathode; the band normally marks the cathode. Do not claim all diodes have the same forward voltage.
- **Electrolytic capacitors:** polarity matters; connect only to the stated low voltage and never reverse it. Discharge safely through an appropriate resistor before handling a charged setup.
- **Transistors:** pin order varies by device and package. Require the learner to read the marking and use the kit’s labelled reference or a component-card pinout—never assume the flat face gives a universal pin order.
- **Integrated circuits/modules:** align any notch/dot/pin 1 mark, never force pins, and use only the documented supply voltage.
- **Motors/servos:** a motor can draw more current than LEDs and may produce voltage spikes; no direct DMM-current measurement unless the lab explicitly directs it. Never claim a servo can be positioned without a suitable pulse signal.

### DMM rules

The DMM is a measurement device, not a power source. Put a dedicated meter icon beside every measurement.

| DMM mode | Use | Connection rule | Never do |
| --- | --- | --- | --- |
| `V DC` | Measure potential difference | Put probes **in parallel** across the two points | Do not break the circuit to insert it. |
| `Ω` / continuity | Measure resistance or path | Power **off**, preferably isolate one component lead | Do not measure a powered circuit. |
| diode test | Compare a diode’s one-way behaviour | Power off, identify polarity | Do not expect every LED to light strongly. |
| `A` / `mA` | Measure current | Break circuit and put meter **in series**, correct jack/range | Never place it across a supply or leave lead in the current jack afterward. |

Default to voltage, resistance, continuity, and diode test. Current measurement should appear only after a dedicated DMM lesson, with a large warning illustration.

### Breadboard truth

- On a typical half-size breadboard, five holes in each numbered row on one side of the centre trench are connected; the two sides are not connected across the trench.
- Power rails often have a break in the middle. Test or bridge the break deliberately; never assume a coloured line means continuity.
- Different brands vary. The first lab must have students use continuity mode (or a supplied breadboard map) to verify their board.
- A component’s two leads must not be placed in the same connected strip when the intent is to put it in the circuit.

## Shared vocabulary and writing standards

Introduce new terms only when the activity makes them useful. Put first-use terms in a highlighted “word card” with pronunciation if it is non-obvious.

| Preferred term | Student-ready definition | Avoid / clarify |
| --- | --- | --- |
| circuit | a complete path that allows charge to move | “electricity goes to the part and disappears” |
| voltage | energy difference that can push charge through a circuit; measured in volts (V) | “voltage is current” |
| current | rate of electric charge flow; measured in amperes (A) | “current is stored in a resistor” |
| resistance | opposition to current; measured in ohms (Ω) | “resistance stops all electricity” |
| polarity | a direction/terminal requirement | “positive electricity” as a substance |
| conductor | material/path that lets charge move easily | “wire makes power” |
| insulator | material that strongly resists charge movement | “no charge exists” |
| series | one route, component after component | “shares voltage equally” without evidence/conditions |
| parallel | more than one route between the same two nodes | “current is always equal in branches” |
| ground / 0 V | the chosen reference point in a circuit, usually supply negative here | Earth/ground unless actually connected to protective earth |
| sensor | device that changes/communicates a signal in response to a condition | not necessarily usable without a controller |
| actuator/output | device that makes light, sound, motion, or another effect | not necessarily independently testable |

Use “higher/lower voltage,” “more/less current,” and explicit units. Label conventions: `V`, `mA`, `Ω`, `kΩ`, `µF`, `Hz`, and `s`. A lower-case `m` means milli (one thousandth); `M` means mega (one million)—do not conflate them.

## Infographic and accessibility conventions

Each lab should include **at least three purposeful visuals**, selected from the list below. They must teach, not decorate.

1. **Component ID card:** realistic outline/photo-style drawing plus physical clues, symbol, pins, and orientation mark.
2. **Concept graphic:** one causal relationship, e.g., “more resistance → less current (with the same voltage)” or a capacitor charge/discharge timeline.
3. **Breadboard build map:** a clear reproducible layout, labelled pins/nodes, rail breaks, and polarity.
4. **Measurement graphic:** where the black/red probes go and DMM dial/mode.
5. **Evidence visual:** a small graph, comparison strip, or before/after diagram derived from the lab data.

Conventions across the book:

- Red is conventionally `+`; black/blue is `–`/0 V. Every colour meaning must also have a text label and line style, for colour-blind accessibility.
- Use gold/yellow with a `!` for a caution; use red with a stop symbol only for “do not” actions; use green/blue check marks for verified safe checks.
- Draw electron movement only when necessary and distinguish it from conventional current direction; default to conventional current arrows (`+` to `–`) and say so once in the foundations chapter.
- Make diagrams high contrast, use minimum 11–12 pt text in the PDF, avoid tiny breadboard labels, and add a caption which says what the student should notice.
- Do not use a component photograph alone as wiring instructions. Pair it with a simplified drawing/schematic.
- Give every visual a descriptive title and meaningful alt text in the source document, e.g., “DMM voltage probes placed across the two LED terminals, not in series.”

## Scope labels: full test, basic electrical test, and partial characterisation

The no-Arduino constraint is important. A device may be real, present, and not fully demonstrable without a programmed controller, a pulse generator, serial/I²C/SPI source, or an appropriate driver. Honesty is part of the lesson.

Place one of these labels at the top of every component card:

| Label | Meaning | Appropriate evidence |
| --- | --- | --- |
| **Full functional test** | The lab demonstrates the component’s intended primary behaviour using only permitted low-voltage, non-programmed equipment. | Visible/audible/measurable response and explanation. |
| **Basic electrical test** | The lab verifies a fundamental electrical property, but not every intended use. | Resistance, diode test, continuity, passive response, or simple switch/indicator action. |
| **Partial characterisation — controller/signal required for full operation** | The lab can identify pins, verify supply/continuity or a limited property, but cannot prove the module carries out its intended digital/timed function. | Clearly state what was and was not proven. |

Mandatory wording for the third label:

> “This investigation checks **[specific property]**. It does not prove that the module can **[intended behaviour]**, because that needs **[a controller / timed pulse / communication protocol / suitable driver]**. Do not apply power or signals beyond the module’s documented limits.”

Examples likely to need partial-characterisation labels in a UNO starter kit (exact contents/revision must be checked):

- **DHT11 temperature/humidity module:** may be identified and supplied only if kit documentation permits; a microcontroller-timed single-wire exchange is needed to read humidity/temperature data.
- **HC-SR04 ultrasonic module:** needs trigger pulses and timing of the echo pulse; a standalone DMM cannot measure distance operation.
- **LCD1602 display:** needs a compatible controller and command/data protocol to display text; contrast/backlight may be separately considered only with correct documented connections.
- **SG90 servo:** needs repetitive control pulses for position; direct DC power is not a position test and must not be represented as one.
- **IR receiver, joystick module, relay module, 74HC595, sound sensor, RFID, matrix/keypad modules (if present):** confirm the interface and driver/protocol needs; test only safe, meaningful subproperties.

Some items should have **one shared systems chapter** rather than artificial independent “functional” labs if a no-controller setting makes a separate test unsafe or scientifically empty. That chapter may still give each component a component card and a clearly bounded, useful observation. A lab count can equal or exceed the number of component types without pretending every module fully operates.

No lab may power a 5 V logic module from an arbitrary supply, inject a signal from the DMM, or infer functional health from a single resistance reading across a multi-pin module.

## Recommended progression and cognitive load

Build knowledge in this order; lab authors should declare prerequisites rather than reteach everything.

1. Safety, breadboard map, source polarity, DMM basics.
2. Conductors/insulators, resistance, series/parallel, switch.
3. LED, diode, current limiting, voltage measurement.
4. Variable resistor, photoresistor, thermistor, button/switch, passive sensors.
5. Capacitor and timing/energy-storage concepts.
6. Transistor as a controlled switch; buzzer/motor outputs with safe limits.
7. Complex modules: identify interfaces and conduct honest partial characterisation.
8. Capstone diagnosis/design challenge using familiar parts.

Introduce at most two new technical words and one new tool operation per ordinary lab. Reinforce rather than repeat long explanations. Use “you will observe” only when a correct build reasonably gives a detectable result; otherwise say “record what you observe.”

## Support for diverse learners and learners aged 12+

- Begin each lab with a picture, a one-sentence aim, and a 3–5 minute build estimate. Use short numbered steps, one action per line.
- Pair visual information with a spoken/printed plain-language version; do not rely on colour, fine motor precision, or rapid reading alone.
- Provide pre-bent wire kits or a partner role split: **builder**, **safety checker**, **meter reader**, **recorder**. Rotate roles.
- Offer a partially completed evidence table and formula card for students who benefit from scaffolding; offer an extension measurement/graph for faster learners.
- Give an alternative to fine colour-band reading: measure resistor values with a DMM or use labelled parts trays. Explain colour bands without making them a gatekeeper.
- State approximate outcomes/ranges rather than rigid “correct” readings. Kit tolerances, LED colours, source voltage, ambient light, and component variation are legitimate evidence to discuss.
- Use no prerequisite algebra beyond substitution. Make unit conversions optional or guided.
- Avoid idioms, gendered assumptions, and shaming language such as “obvious” or “easy.” Frame mistakes as data for fault-finding.

## Teacher quality checklist for every submitted lab

Before release, the teacher/editor verifies:

- [ ] The exact kit part is correctly identified; any uncertainty is labelled and does not drive an unsafe step.
- [ ] The aim, prediction, evidence, explanation, reflection, and assessment align with one observable idea.
- [ ] Source voltage and all component values/orientations are shown in words and diagrams.
- [ ] A safe current-limiting resistor protects each ordinary LED.
- [ ] DMM steps use the correct mode, jacks, and series/parallel placement; no powered resistance measurement is requested.
- [ ] Breadboard connections have been checked for same-strip mistakes and rail breaks.
- [ ] The lab contains three or more educational visuals with high-contrast, label-plus-colour accessibility.
- [ ] Student directions are age-appropriate and avoid unsupported claims.
- [ ] Any controller/protocol/timing-dependent component carries the correct scope label and explicit limitation.
- [ ] Troubleshooting begins with power off and does not encourage random rewiring.
- [ ] Assessment asks for evidence-based reasoning, not only vocabulary recall.

## Standard teacher-note format

Place teacher notes after student content, visibly marked **Teacher note — not required for the student**. Include anticipated results/ranges, common misconceptions, solution answers, setup preparation, timing, and whether an observation is optional/variable. Do not hide a critical safety instruction only in teacher notes; students must see it before the relevant build step.

## Tone and visual voice

Write with respectful curiosity: “Let’s test the claim,” “Your result may differ; record it,” and “A circuit that does not work is a chance to diagnose.” Do not anthropomorphise components as “wanting” current, and do not imply students caused a fault through carelessness. The book should make careful measurement feel like the core activity, with the circuit as the instrument for asking a question.
