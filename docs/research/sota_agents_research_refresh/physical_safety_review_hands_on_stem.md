# Hands-On Physical-Safety Dry-Run Reviewer

## Why this thread

Every lesson in this run carries an `Adult safety verification` block that a
supervising adult is expected to read and sign against. In L01 that block
specifies `"hazard_mode": "fully disconnected low-voltage identification"`,
limits of "No energized work, no connector insertion, no selector movement,
and no measurement in this lab," and an `endpoint_check` requiring the adult
to point to all three path locations and confirm every connection is open.

It shipped as a raw JSON dump, like everything else. The one block whose whole
function is to be read and acted on by a human before a child touches
hardware was rendered unreadable in all four lessons.

Beyond legibility, nothing verifies that the block is *behaviourally
consistent* with the steps above it. `L04`'s limits say "no fuse replacement
in this lab" while the Explain section teaches fuse-sharing behaviour; L01's
`endpoint_check` names "all three path locations" and the numbered steps
happen to contain three, but no check compares them. The executed check set
(`DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID`,
`RECEIPT-HASH-RESOLVES`) confirms the fields are present and well-shaped, and
stops there.

## Findings

**The professional standard for hands-on science safety is a rehearsal, not a
document review.** Kenneth Roy's "Science Activity Safety Checklist" (NSTA,
2 March 2018) lists as item 12: perform the activity yourself before using it
with students. The checklist also requires documenting physical-hazard
precautions (trip hazards, projectiles), hand/power-tool precautions, and a
written safety-precautions statement for both teacher and students, and closes
with "Always make note of safety actions in your lesson plans and keep copies
of the check list." Implication for this pipeline: the reviewer that matches
this standard walks the numbered Explore steps as if performing them and
checks that the safety block describes what those steps actually ask a child
to do — it does not merely assert that the safety fields exist. This is also
the strongest-grade source in the scan: professional-body guidance that
predates the LLM framing and is what practitioners are actually held to.

**Named-dimension safety scoring with a regeneration loop is already
implemented in a K-12 generation pipeline.** arXiv:2604.04728's Safeguard
Agent scores generated content against five criteria — age-appropriateness,
accuracy, safety, bias, educational value — and on failure "the pipeline
re-enters the generation stage, using safeguard feedback to guide the next
attempt." Implication: a hands-on-hardware safety dimension is a direct
transfer of this pattern; the difference is that the hazard here is physical
rather than representational, which raises the cost of a miss rather than
changing the architecture.

**Treating oversight as its own adversarial layer is an active 2026
direction.** Sadhu & Dhor, "Hierarchical Pedagogical Oversight: A Multi-Agent
Adversarial Framework for Reliable AI Tutoring" (arXiv:2512.22496), proposes
hierarchical oversight in which some agents generate educational content while
others critically evaluate it, with adversarial checking at different
organisational levels. Implication: physical safety should be its own review
layer with authority to block, distinct from the pedagogy and domain-fact
reviewers — an adult signing an unreadable block is a failure the general
quality judge has no particular reason to prioritise, and a dedicated layer
does.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Kenneth Roy, "Science Activity Safety Checklist," NSTA, 2018-03-02 —
  https://www.nsta.org/blog/science-activity-safety-checklist
- "A Multi-Agent Framework for Democratizing XR Content Creation in K-12
  Classrooms," arXiv:2604.04728 — https://arxiv.org/html/2604.04728
- Sadhu & Dhor, "Hierarchical Pedagogical Oversight: A Multi-Agent Adversarial
  Framework for Reliable AI Tutoring," arXiv:2512.22496 —
  https://www.arxiv.org/pdf/2512.22496

## Discarded

- Nothing was discarded in this thread; all three sources the previous scan
  cited here re-verified cleanly and are retained. Worth recording for the
  next scan: the NSTA page is the most durable citation in the whole set — it
  has been stable since 2018, is professional-body guidance rather than
  vendor or preprint material, and was the only source in this refresh that
  required no caveat, no correction, and no alternate URL form.
