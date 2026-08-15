# Visual grounding — a reviewer that checks the picture shows the thing

## Why this thread

Every lesson ends with a Visuals section whose first entry is captioned
"Subject Identification":

```markdown
### Subject Identification

![subject_identification](assets/official_reference.jpg)
```

That file is byte-identical in all four lessons. Its sha256 is
`8f9ab6c86f259c4d8cc75066df4bba73ef895973bfd5e182316c2659cd964efc` in
`L01/document/assets/manifest.json`, and the same digest appears in the L02,
L03 and L04 manifests. One photograph is serving as the subject-identification
visual for four different subjects: a breadboard power-supply module, a
solderless breadboard, male-to-male jumper wires, and a digital multimeter.

The lessons are built almost entirely around looking at it. L01 instructs
"Find the battery and DC lead in the official kit photograph." L04 instructs
"Find the COM socket and note it always takes the black probe." A single kit
photograph cannot be the identification reference for all four.

`RECEIPT-HASH-RESOLVES: PASS` in every unit's `results/unit_checks.json`. That
check does exactly what its name says — it confirms the digest resolves to a
file that is present. `check_receipts` in `runtime/checks.py:46` compares
hashes. Nothing anywhere asks whether the image depicts the subject the caption
claims. This defect is not in the QA report; it was found by hashing the
assets.

## Findings

**Binary image-text alignment scoring is a solved-enough problem; localising
*what* disagrees is the open one — and localisation is what a reviewer must
emit to be actionable.**
Gordon, Bitton, Shafir, Garg, Chen, Lischinski, Cohen-Or and Szpektor,
"Mismatch Quest: Visual and Textual Feedback for Image-Text Misalignment"
(ECCV 2024, arXiv 2312.03766), state that "While existing image-text alignment
models reach high quality binary assessments, they fall short of pinpointing
the exact source of misalignment", and build a method producing "detailed
textual and visual explanation of detected misalignments". Implication for this
pipeline: a binary alignment score is already sufficient to have flagged our
defect — one photo against four different `identification.technical_name`
values would fail three of them outright. Localisation is the upgrade path, not
the entry price, so this agent is cheap to stand up.

**In educational diagram generation, correctness of labels is treated as a
separate property from the image existing, and is protected by anchoring to
deterministic structure.**
"CAGE" (arXiv 2604.09691) reports that diffusion models "catastrophically
garble text labels" and therefore anchors generation in executable code,
letting a refinement stage act only while "preserving label fidelity", measured
over 400 K-12 diagram prompts alongside a 2,000-item paired dataset,
EduDiagram-2K. Implication for this pipeline: our SVG assets (`path_map.svg`,
`evidence_card.svg`) *are* the deterministic code-anchored kind and do differ
per unit — the per-unit digests are distinct. The failure is isolated to the
one raster asset that was copied. That narrows the reviewer's job usefully: the
highest-risk asset is the one the pipeline did not generate.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Gordon, Bitton, Shafir, Garg, Chen, Lischinski, Cohen-Or, Szpektor, "Mismatch Quest: Visual and Textual Feedback for Image-Text Misalignment," ECCV 2024, arXiv 2312.03766 — https://arxiv.org/abs/2312.03766
- "CAGE: Bridging the Accuracy-Aesthetics Gap in Educational Diagrams via Code-Anchored Generative Enhancement," arXiv 2604.09691 — https://arxiv.org/abs/2604.09691

## Discarded

- https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07453.pdf — the ECCV proceedings PDF of Mismatch Quest. Fetched; returned undecodable compressed PDF streams with no extractable title, abstract or body. Per the retry ladder, retried once via the arXiv form (2312.03766), which returned clean text and is what this thread cites. Do not re-fetch the ecva.net PDF in a later scan.
- https://link.springer.com/chapter/10.1007/978-3-031-72998-0_18 — the same paper's Springer chapter page. Not fetched: the arXiv abstract had already verified the claim, and a publisher landing page would add nothing but a paywall risk.
