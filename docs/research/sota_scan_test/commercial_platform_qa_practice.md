# Commercial practice — what shipping platforms actually gate on

## Why this thread

The other six threads ask what a reviewer *could* be. This one asks what
survived contact with real learners, because the pipeline's failure was not a
missing idea — `prompt.md` already names `TEXT-READABILITY-BAND`,
`TEXT-BLOOM-VERBS` and `REV-JUDGE-SINGLE-CROSS-FAMILY` as mandatory — it was
that every one of them was absent or inert while four lessons shipped anyway.
The QA report's root-cause line: "schema validity was the only thing measured."

So the question here is what production platforms put between a generated
lesson and a child, and specifically whether they rely on a per-artifact review
gate at all.

## Findings

**The most widely repeated claim about Duolingo's review workflow is not
supported by Duolingo's own description of it.**
Secondary write-ups assert that every AI-generated exercise is reviewed and
approved by a qualified linguist before publication, with automated quality
checks first. Duolingo's own page, "At Duolingo, humans and AI work together to
create a high-quality learning experience", describes something different: human
experts own the earlier stages — curriculum design and authoring the raw
content — and AI generates exercises from that raw content downstream, with
AI-powered tooling helping content developers work faster. The page describes
no post-generation human review gate and no automated post-generation quality
check. Implication for this pipeline: the leading commercial example places its
human expertise *upstream as constraints*, not downstream as inspection. That
is worth knowing before copying an inspection-heavy design — but note our run
had neither, since its upstream constraints (grade band, term cap) were
declared and then never enforced at either end.

**A large education platform's public governance gates capabilities on named
review bodies and adversarial testing, not on artifact validity.**
Khan Academy's "Framework for Responsible AI in Education" requires "a
monitoring & evaluation plan to determine the impact expected through the use
of AI and verify that the AI is performing as intended" and "the means to
determine AI's trustworthiness, and in areas where the AI is not trustworthy,
there is an action plan to address improvement." It describes deliberate
red-teaming to "find flaws in the AI to uncover potential vulnerabilities", and
a standing "Responsible AI Extended Working Group" that "evaluates upcoming
capabilities against the framework and monitors launched features." It does not
publish a per-artifact content vetting protocol. Implication for this pipeline:
the closest production analogue to our situation is not a missing check but a
missing *body that notices a check is inert*. Our run's judge was bypassed with
a recorded rationale and shipped anyway; a monitoring plan of the kind
described here is what converts "documented as deferred RT-5" into "blocked".

**Published multi-agent instructional-design systems still terminate in human
review, even in their most autonomous mode.**
"Instructional Agents" (arXiv 2508.19611) evaluates across five university
courses and describes output "reviewed and refined by teaching faculty prior to
use." Implication for this pipeline: the `*Draft pending downstream human
review.*` banner hard-coded into every shipped document at
`runtime/session_bridge.py:203` asserts a stage that has no implementation.
Either the stage exists and should be a gate with a recorded verdict, or the
banner is a claim the pipeline cannot support and should stop making.

## Sources (all fetched and verified to resolve to real, on-topic content)

- "At Duolingo, humans and AI work together to create a high-quality learning experience," Duolingo blog — https://blog.duolingo.com/how-duolingo-experts-work-with-ai/
- "Khan Academy's Framework for Responsible AI in Education," Khan Academy blog — https://blog.khanacademy.org/khan-academys-framework-for-responsible-ai-in-education/
- "Instructional Agents: Reducing Teaching Faculty Workload through Multi-Agent Instructional Design," ECAL'26, arXiv 2508.19611 — https://arxiv.org/abs/2508.19611

## Discarded

- https://support.khanacademy.org/hc/en-us/articles/13965308352781-What-is-Khan-Academy-s-approach-to-responsible-AI-development and https://support.khanacademy.org/hc/en-us/articles/14394814244365-What-safety-features-does-Khanmigo-have — both returned HTTP 403. The second was the retry; the whole support.khanacademy.org subdomain blocks this fetcher. No claim was lost, because the blog.khanacademy.org framework page covers the same ground and verified cleanly.
- Entire first Khanmigo result set — mamasmiles.com, kidsaitools.com, aitoolsbakery.com, myengineeringbuddy.com, aiflowreview.com. Rejected without fetching under the source-quality bar: affiliate review sites recycling each other's claims about content filters and Common Sense Media ratings, with no primary source.
- Entire first Duolingo result set — drphilippahardman.substack.com, sridhar-ai.ch, zenml.io LLMOps database, frugaltesting.com, buildmvpfast.com. Rejected without fetching, and this rejection turned out to matter: these are the origin of the "qualified linguist approves every AI exercise" claim that the primary Duolingo page does not support. Citing any of them would have put a false workflow into the recommendation.
