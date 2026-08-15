# Physical/child-safety review for hands-on hardware instructions

## Why this thread

Every one of L01-L04 is built around a heavy, explicit safety scaffold: each
lesson declares a `hazard_mode` (e.g. "fully disconnected low-voltage
identification"), an `## Adult safety verification` block with
`verified_configuration`, `limits`, `endpoint_check`, and
`signoff_required: true`, and Explore steps that repeatedly instruct
"Check with the adult that the battery lead is physically disconnected"
before any handling. This is clearly a safety-first design. But the QA
report shows the entire document — including this safety block — rendered
as raw, unparsed JSON to whoever (a parent/adult) would actually read it
before signing off. Nothing in the current check set
(`DOMAIN-SCHEMA-VALID`, `DOMAIN-VERIFIER`, `LAB-SCHEMA-VALID`,
`RECEIPT-HASH-RESOLVES`) verifies that the safety block *reads clearly and
consistently* to the adult who has to act on it — schema validity only
confirms the fields exist, not that a human can use them safely.

## Findings

**Classroom science-safety practice treats a live trial run, not a
checklist read-through, as the pre-release safety gate.** NSTA's "Science
Activity Safety Checklist" (Science Safety Advisory Board) requires, among
other steps: complete a hazard analysis and review of relevant safety data,
apply appropriate control measures, document precautions for physical
hazards (e.g. trip/fall, projectiles) and tool use — and, most relevant
here, "the teacher performs [the] lab, activity, or demonstration prior to
its use with students," i.e. a dry-run rehearsal, not just a document
review. This maps directly onto a `curriculum_builder` safety-reviewer agent
that should *walk through* the generated Explore/steps sequence and the
Adult-safety-verification block as if performing them, checking internal
consistency (does every step referenced in `endpoint_check` actually appear
in the numbered steps above it? does the stated `hazard_mode` match what the
steps actually ask the child to do?) rather than only checking that the
JSON fields are present.

**A concrete, verified architecture for automated safety review with a
revision loop already exists for K-12 generated content.** The same
Safeguard Agent described in "A Multi-Agent Framework for Democratizing XR
Content Creation in K-12 Classrooms" (arXiv:2604.04728) scores generated
content on "age-appropriateness... absence of violent or disturbing
imagery... educational alignment" alongside factual accuracy, and triggers
regeneration on failure rather than a bare reject. The same pattern (score
on named safety dimensions, feed failures back into regeneration) applies
directly to a hands-on-hardware safety reviewer for `curriculum_builder`,
scoring dimensions like "hazard_mode consistency," "adult-verification-block
completeness," and "no step implies contact with an energized/connected
part."

**Layered/adversarial oversight for reliability is an active 2026 direction
worth tracking as this check matures.** "Hierarchical Pedagogical
Oversight: A Multi-Agent Adversarial Framework for Reliable AI Tutoring"
(arXiv:2512.22496) — cited here only for its general architectural pattern
of complementary, layered review agents (verified via metadata/topic only,
full text not extractable) — supports treating physical-safety review as
its own oversight layer distinct from pedagogy or domain-fact review, each
catching different failure classes.

## Sources (fetched and verified)

- NSTA, "Science Activity Safety Checklist" —
  https://www.nsta.org/blog/science-activity-safety-checklist
- "A Multi-Agent Framework for Democratizing XR Content Creation in K-12
  Classrooms," arXiv:2604.04728 — https://arxiv.org/html/2604.04728
- Sadhu & Dhor, "Hierarchical Pedagogical Oversight: A Multi-Agent
  Adversarial Framework for Reliable AI Tutoring," arXiv:2512.22496 —
  https://www.arxiv.org/pdf/2512.22496 (metadata/topic verified only; cite
  conservatively)
