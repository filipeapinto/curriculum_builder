# P0 - Render structured unit data as a learner lesson, not raw JSON

## Problem

Every shipped lesson serializes the `engage`, `explore`, `explain`, `elaborate`, `evaluate`, identification, troubleshooting, and safety objects directly into the Markdown/PDF body. The result is a schema dump with braces, quoted keys, underscores, booleans, and nested arrays rather than prose for a supervised beginner aged 9+.

Examples:

- `outputs/arduino_kit_run_v2/L01/document/L01.md:13-18` renders the Engage object literally.
- `outputs/arduino_kit_run_v2/L01/document/L01.md:20-82` renders the entire Explore object literally.
- The identical defect appears in L02, L03, and L04.
- Rasterized page 1 of each PDF visibly contains dense JSON; this is not merely a Markdown-source defect.

The renderer also drops whole teaching blocks present in `workers/lab.json`, including prior-knowledge retrieval, misconception confrontation, vocabulary definitions, scaffolding/adult-versus-child roles, and cognitive-load segmentation. In L01, for example, the word `rail` is declared with a child definition in `workers/lab.json`, but that definition never reaches the document.

## Root cause

`runtime/session_bridge.py:201-220` is not a lesson renderer. `_markdown()` calls `json.dumps(...)` for every structured block (`:207-214`) and never maps several required schema fields into the unit structure mandated by `meta_prompt/assets/unit_prose.v1.md`.

## Expected behavior

The deterministic renderer should transform the validated unit object into the required learner document structure: short learner-facing paragraphs, numbered actions, usable prediction choices, an evidence-recording area, definitions beside first use, a calm troubleshooting table, and a visibly separate adult-verification section.

## Acceptance criteria

- No learner-facing section contains serialized object syntax or schema keys such as `recorded_before_observing`, `what_you_saw`, or `safe_first_check`.
- Every required unit-prose block is represented, including retrieval, vocabulary definitions, misconception confrontation, scaffolding, evidence recording, and adult verification.
- Structured values are rendered by field-aware templates (lists, numbered steps, tables, prompts, checkboxes), not a generic recursive dump.
- Renderer tests cover each supported field shape and fail on unknown/unrendered required fields.
- A PDF regression fixture is inspected from the shipped raster and is readable without consulting `workers/lab.json`.
- L01-L04 are regenerated; patching the current PDFs by hand is not accepted.
