# Bloom's-Level and Cognitive-Demand Reviewer

## Why this thread

`TEXT-BLOOM-VERBS` is defined in `policy/checks.v1.yaml` to assert that "every
disagreement between an objective's declared bloom_level and the verb that
opens its statement is raised and recorded against the ordered bloom_verbs
table," and it is explicit that the check "FLAGS and NEVER BLOCKS — human
raters agree with each other on Bloom level only 46.58% of the time." Like
`TEXT-READABILITY-BAND`, it does not appear in `results/unit_checks.json` for
any of L01-L04. It did not run.

Reading the four documents directly surfaces what it would have flagged. All
twelve "What I will learn" objectives across L01-L04 open with the same three
verbs — *point to*, *explain*, *trace*:

- L01: "I can point to the three places..." / "I can explain why..." / "I can
  trace the teaching path..."
- L02: "I can point to a five-hole group..." / "I can explain why two holes..."
  / "I can trace the connectivity map..."
- L03: "I can write down endpoint A and endpoint B..." / "I can explain why..."
  / "I can trace the connection plan..."
- L04: "I can point to all four locations..." / "I can say which socket..." /
  "I can trace the socket-and-mode map..."

That is four consecutive labs at an essentially flat remember/understand
demand, with no progression. `LAB-BLOOM-DEPTH` checks the *declared* field
against a floor; nothing read the sentence beneath it, which is precisely the
distinction the policy note draws between the two checks.

## Findings

**LLMs can hit targeted cognitive levels when prompted well, but automated
evaluation of whether they did is not equivalent to human judgement.** Scaria,
Chenna & Subramani, "Automated Educational Question Generation at Different
Bloom's Skill Levels using Large Language Models: Strategies and Evaluation"
(arXiv:2408.04394), tests five state-of-the-art LLMs with advanced prompting
and both expert and automated evaluation, concluding that LLMs "can generate
relevant and high-quality educational questions of different cognitive levels
when prompted with adequate information" while stating plainly that
"automated evaluation is not on par with human evaluation." Implication for
this pipeline: this is direct external support for the flag-never-block
posture already written into `TEXT-BLOOM-VERBS`. The right fix is to make the
check actually execute, not to promote it to a blocking gate.

**On rubric-scoring instructional materials, general-purpose models measure
weak, which bounds how much this agent should be trusted.** SciEval
(arXiv:2604.25472) evaluates K-12 science instructional materials "across 13
criteria (N=3549) using the EQuIP rubric" with expert annotations achieving
high inter-rater reliability, and finds that of the mainstream LLMs tested
"none achieve strong performance," with domain-aligned fine-tuning yielding
"up to 11 percent performance gains." Implication: the verb-table comparison
is deterministic and cheap and should run on every unit; anything requiring
pedagogical judgement should be surfaced to the human reviewer the documents
already anticipate ("Draft pending downstream human review"), not auto-scored.

**Separating pedagogy review from content generation is the prevailing agent
architecture, rather than one generic reviewer.** Chu et al., "LLM Agents for
Education: Advances and Applications" (arXiv:2503.11733), surveys educational
LLM agents across tutoring, content generation, assessment and error
detection, treating these as distinct specialised roles rather than
capabilities of a single agent. Cited here for that architectural point only —
it is a survey, not an empirical result. Implication: the Bloom/cognitive-
demand reviewer is its own agent with its own input (the rendered objectives
and hinge questions) and its own verdict, separate from the readability
checker even though both read the same file.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Scaria, Chenna & Subramani, "Automated Educational Question Generation at
  Different Bloom's Skill Levels using Large Language Models: Strategies and
  Evaluation," arXiv:2408.04394 — https://arxiv.org/abs/2408.04394
- "SciEval: A Benchmark for Automatic Evaluation of K-12 Science Instructional
  Materials," arXiv:2604.25472 — https://arxiv.org/abs/2604.25472
- Chu et al., "LLM Agents for Education: Advances and Applications,"
  arXiv:2503.11733 — https://arxiv.org/pdf/2503.11733

## Discarded

- Nothing was discarded in this thread — all three candidate sources fetched
  cleanly and supported the claims made of them. Two carry stated limits
  rather than discards: arXiv:2503.11733 is a survey and is cited only for
  role separation, never for a measured result; and the previous scan's
  citations in this thread (arXiv:2408.04394, arXiv:2503.11733) were
  re-verified in this refresh and both still hold, with the quoted line
  "automated evaluation is not on par with human evaluation" confirmed
  verbatim.
