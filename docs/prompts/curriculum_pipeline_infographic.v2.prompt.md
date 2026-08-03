# ImageGen prompt — curriculum pipeline infographic v2

Use case: infographic-diagram

Asset type: polished repository architecture infographic, 16:9 landscape PNG

Primary request: Create a highly polished, immediately understandable left-to-right
systems diagram for the `curriculum_builder` repository. The reader must see exactly
which files enter, which master prompt runs, which companion skills and code participate,
and which output files and results emerge. This is an engineering architecture plate,
not a generic process poster.

Audience: software engineers and curriculum-system reviewers who have not seen the
repository before.

Scene/backdrop: warm white canvas with a very faint technical grid. Four large numbered
columns connected by one strong horizontal flow arrow. Use generous whitespace and
strict alignment.

Style/medium: premium editorial vector-like infographic; crisp sans-serif typography;
precise orthogonal connectors; restrained navy, cyan, emerald, and amber palette; subtle
flat color panels; no 3D, no clip art, no decorative illustration, no gradients, no drop
shadows, no watermark.

Composition/framing:

1. Left column, header `1  INPUT FILES`, divided into three stacked cards:
   - `ENGINE POLICY` with `calibration · controller · limits · routes · checks · failures · deferred`
   - `LIVE SCHEMAS` with `curriculum v5 · lab v4 · routing decision v2 · execution log v2`
   - `CURRICULUM` with `manifest v5 · domain schema · calibration · checks · evidence · fixtures`
   A small input chip below reads `RUN ARGS  --curriculum  --output-root`.

2. Center-left column, header `2  MASTER PROMPT + SKILLS`, with one dominant card:
   `meta_prompt/curriculum.prompt.v1.md`
   Subtitle: `reads one supplied curriculum · writes only to OUTPUT_ROOT`
   Directly beneath, three smaller companion-skill cards:
   - `UNIT PROSE` / `unit_prose.v1.md`
   - `PEDAGOGY` / `pedagogy.v1.md`
   - `MODEL ROUTING` / `model_selector_prompt.v1.md`
   Show these three feeding upward into the master prompt.

3. Center-right column, header `3  CODE + EXECUTION`, as a clean vertical six-step rail:
   `VALIDATE INPUTS`
   `RETRIEVE PRIMARY SOURCES`
   `ASSEMBLE DOMAIN BLOCK`
   `RUN DOMAIN VERIFIER  verify_domain.py`
   `GENERATE + CHECK UNIT  Python + model workers`
   `RENDER + AUDIT  deterministic code`
   Add a slim side rail labeled `LOGGER · ROUTING DECISIONS · HASHED CHECKPOINTS` running
   beside all six steps. Add a small badge: `CODE DECIDES · MODELS WRITE`.

4. Right column, header `4  OUTPUT FILES + RESULTS`, divided into two stacked cards:
   - `EACH UNIT` with `unit data · child text · adult guide · visuals · receipts · PDF`
   - `RUN RESULTS` with `execution log · routing records · gate report · resume hashes · final product · terminal report`
   Finish with a clear terminal pill: `ACCEPTED  |  SYSTEM FAILURE  |  DRIFT STOP`.

Use one unbroken visual flow:
`INPUT FILES  →  MASTER PROMPT + SKILLS  →  CODE + EXECUTION  →  OUTPUT FILES + RESULTS`.

Bottom status strip, visually secondary but readable:
`CURRENT STATE · contracts and repository gates exist · runtime not implemented · 0 generated units (RT-5 / RT-7)`

Title text, verbatim: `CURRICULUM BUILDER · FILES TO VERIFIED OUTPUT`

Subtitle text, verbatim: `One supplied curriculum. One generic prompt. Explicit code, skills, evidence, and results.`

Constraints: render all quoted labels verbatim; preserve file-version numbers; make
filenames readable at normal desktop size; keep arrows directional and unambiguous;
every output must visibly originate from the execution column; no extra stages or
invented filenames; no circuit imagery; no school-themed decoration; no logos; no
watermark; no tiny footnotes.
