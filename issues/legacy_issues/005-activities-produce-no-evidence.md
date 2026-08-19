# P1 - Make Predict-Observe-Explain activities produce an actual observation

## Problem

The units contain the labels of a Predict-Observe-Explain sequence, but the learner generally points at objects or traces the runtime's diagram. The activity does not generate evidence capable of confirming or confronting the prediction.

Examples:

- L02 asks which breadboard holes share a hidden clip, but the learner only looks at a physical board and the defective map (`L02/document/L02.md:24-76`). No cutaway, verified board-specific topology, or adult-led continuity check establishes which holes are electrically joined. The lesson later asserts the observation anyway (`:73,83-85`).
- L03 teaches that a wire joins two endpoints, while requiring every wire to remain out of the board and showing both endpoints as `NOT CONNECTED`. The learner does not observe a connection or distinguish a wire route from a component connection.
- L04's learner outcome is to distinguish voltage, continuity, and current modes, but the activity only points at sockets/dial labels on a powered-off meter. There is no verified dial/jack map, probe plan, or safe demonstration that yields evidence about the difference between those measurement modes.
- The generated “evidence cards” do not record the unit-specific prediction or outcome; they repeat three generic identification statements.

This violates the project's own pedagogy: exploration must precede explanation, observations must be distinct from mechanisms, and a prediction must be confronted by evidence from the activity.

## Expected behavior

Each unit needs a safe, age-appropriate observation whose result can support or disconfirm the prediction. Fully unpowered does not mean evidence-free: a verified transparent/cutaway visual, board-specific connectivity map, safe adult-led continuity demonstration, physical sorting task, or other curriculum-approved observation can supply evidence.

## Acceptance criteria

- For every prediction option, the activity defines what observable result would support or disconfirm it.
- `observe.what_to_observe`, numbered steps, expected observation, evidence fields, explanation, and visuals refer to the same event/data.
- The learner records the prediction before observing and records the result afterward in a usable evidence area.
- “What you saw” cannot assert a result that the steps and shipped visuals never exposed.
- L02 has verified board-specific topology or a safe test; L03 exposes the two-endpoint relationship without contradicting it visually; L04 has an exact, safe socket/mode planning task.
- A semantic integration test rejects POE blocks where the observation is only “look at the answer map” or where no evidence field captures the outcome.
