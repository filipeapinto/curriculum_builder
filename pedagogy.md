# The teaching methods behind the lab schema

Every pedagogical field in `schema/lab.schema.v3.json` implements a named,
evidence-based method. This file says which, and why it is in the schema rather
than in a style guide.

The reason it is in the schema: a rule in prose is advice, and a generator under
pressure drops advice. A rule in the schema is a validation failure.

---

## The spine: 5E instructional model

Bybee / BSCS. The most widely used sequence in primary science teaching, and the
one the workbook's own `component → purpose → identification → mechanism →
evidence → applications` chain already approximates.

| 5E phase | Schema field | What it does |
|---|---|---|
| **Engage** | `sequence.engage` | surfaces curiosity and *elicits the child's existing idea*, including a wrong one |
| **Explore** | `sequence.explore` | hands-on work before explanation |
| **Explain** | `sequence.explain` | mechanism, once there is evidence to attach it to |
| **Elaborate** | `sequence.elaborate` | transfer, near and far |
| **Evaluate** | `sequence.evaluate` | the child judges their own success |

The order matters more than the labels. Explanation comes *after* exploration —
telling a nine-year-old how a diode works before they have seen one refuse current
produces recitation, not understanding.

---

## Inside Explore: Predict–Observe–Explain

White & Gunstone. The child commits a prediction **before** observing.

```
predict.recorded_before_observing: const true
```

A `const` because a prediction recorded afterwards is not a prediction, and this is
the single most common way POE gets hollowed out in practice. If the child never
commits, a surprising result produces no conflict, and no conceptual change
follows.

---

## Misconceptions: conceptual change

Posner, Strike, Hewson & Gertzog. Wrong ideas are not absent — they are already
there, and a clear explanation delivered alongside an untouched misconception
leaves the misconception intact.

`pedagogy.misconceptions` requires at least one per lab, each with:

- the misconception itself
- **why it is common** — forces it to be a real alternative conception, not a
  strawman
- **what confronts it** — the specific observation in *this* lab that makes it
  untenable

Electronics is full of these: current being "used up" as it goes round, wire colour
determining electrical identity, a battery storing electrons rather than energy,
voltage being something that flows.

---

## Prior knowledge and retrieval practice

Roediger & Karpicke. Recalling from memory strengthens learning far more than
re-reading it.

`prior_knowledge.retrieval_prompt` requires a *recall*, not a recap — the child
answers from memory before new material arrives. `assumed_ideas` requires every
assumption to be stated; undeclared prior knowledge is what makes a lab silently
fail for a child who missed something three labs ago.

---

## Vocabulary and cognitive load

Sweller; Mayer.

- `vocabulary` is capped at **two** new terms per lab (`maxItems: 2`), each defined
  at first use.
- `cognitive_load.segments` is capped at **six** — beyond that, working memory in
  this age band is the binding constraint, not motivation.
- `cognitive_load.concrete_before_abstract` enforces the CRA sequence: the physical
  object and action come before any schematic symbol or abstract term.
- `worked_example` is optional but available — the worked-example effect is
  strongest exactly where this workbook operates, with novices in a new domain.

---

## Objectives and success criteria

Bloom's revised taxonomy for the objective; Black & Wiliam for the criterion.

```
learning_objectives[].bloom_level      one must be "understand" or higher
learning_objectives[].success_criterion  must match ^I can .+
evaluate.success_criteria_checklist      the same criteria, child-tickable
```

The `contains` constraint blocks a lab whose objectives are all `remember` —
identification alone is not a lab. The `^I can` pattern forces the criterion into
the child's voice, because a success criterion the child cannot apply to their own
work is a teacher's note, not formative assessment.

`evaluate.hinge_question` is one question whose answer reveals whether the key idea
landed or the misconception survived.

---

## Scaffolding and fading

Wood, Bruner & Ross; Vygotsky.

`scaffolding` splits `adult_does` from `child_does`, and requires a `fading_note`
naming something the child now does alone that an adult did in an earlier lab.
Without the fading requirement, scaffolding silently becomes permanent dependence —
lab 30 looking exactly like lab 3.

---

## Dual coding

Paivio; Mayer's multimedia principles.

`visuals[].supports_section` ties every image to the section it explains. Words and
pictures presented together are processed in complementary channels; the same
image floating three paragraphs away competes for attention instead
(spatial contiguity). `placement_steps` matching the written steps one-to-one
serves the same principle — the child never holds two orderings in mind at once.

---

## Where pedagogy meets safety

Two schema rules are pedagogical as much as they are safety rules:

**`not_yet_outcome` is required.** Every lab must define a safe "not yet" result
and its first check. A workbook where only success is described teaches that not
working means you failed. Framing it as a normal, expected branch — with
troubleshooting starting power-off — is both safer and better teaching.

**Observation is distinguished from mechanism.** `explain.what_you_saw` and
`explain.why_it_happened` are separate required fields. Collapsing them lets a lab
assert a mechanism the child never had evidence for, which is how "the electricity
gets used up" survives an otherwise good lesson.

---

## What the schema deliberately does not encode

Tone, warmth, sentence rhythm, when a metaphor helps, whether a particular hook
will land with a particular child. Those stay in
`prompts/component_lab_template.v1.md` and in the reviewers' judgement. The
schema fixes the structure that makes good teaching possible; it does not attempt
to specify good teaching.
