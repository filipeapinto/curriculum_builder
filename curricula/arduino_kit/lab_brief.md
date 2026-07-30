# Lab Author Brief

Write exactly one complete, standalone Markdown lab at the assigned path. The audience is an age-12-plus beginner with no prior electronics background. Do not use an Arduino, code, mains electricity, or unlisted components as required equipment. A regulated 5 V USB source through the kit's breadboard power module and a basic digital multimeter are the baseline. An optional USB logic analyzer or servo PWM tester may appear only in a clearly labelled optional verification section.

Use this exact order:

1. `# Lab NN - Title`
2. `## Big idea`
3. `## Learning goals`
4. `## Safety first`
5. `## What you need`
6. `## Infographic 1 - Identify` (a detailed description of a factual visual, component orientation and pin/terminal labels)
7. `## Predict` (include a one-sentence prediction prompt)
8. `## Infographic 2 - Build` (schematic and breadboard-plan description accurate enough to draw)
9. `## Build and test` (numbered, no skipped steps)
10. `## Infographic 3 - Observe` (measurement, signal, state, or energy-flow visual description)
11. `## Record what happened` (a small Markdown table with expected range/observation)
12. `## Explain it`
13. `## Common problems`
14. `## Check your understanding` (three short questions, then a `### Answers` section)
15. `## Optional deeper test` (only if a tool helps; otherwise a safe extension using kit items)

Use small, direct sentences. Name a common mistake before it can damage a component. All loads must stay low-voltage DC; relay contacts are never connected to mains. State measurement values as approximate and account for component variation. For a digital module that cannot be fully exercised manually, label the basic test honestly as `partial electrical check` and explain exactly which function needs pulse timing or data decoding.

Every `Safety first` section must explicitly say: `Never connect the breadboard or relay contacts to mains electricity.` Every lab must say a stated supply voltage (normally 5 V) or explicitly state that it is an unpowered resistance/continuity test.
