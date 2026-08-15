# GitHub Landscape: Auditable AI Curriculum Factories

Version: **v1**  
Date: **2026-08-14**  
Status: **Research note; repository landscape, not an implementation decision**

## Research question

Does an open-source GitHub project already implement the same essential idea as
this repository: a curriculum-neutral AI production system that generates
complete instructional artifacts and subjects them to deterministic,
pedagogical, source-grounding, rendering, and independent-review gates before
it can honestly claim release?

## Executive finding

The search found meaningful prior art, but no reviewed project combines the
whole system.

Existing projects cluster into four separate categories:

1. educational-content generators;
2. stateful tutoring and lesson agents;
3. pedagogy or instructional-design knowledge libraries; and
4. lesson-plan evaluation tools.

The closest architectural analogue is `ai-lesson-agent`, because it uses a
stateful LangGraph workflow, checkpoints, human interrupts, deterministic
checks, bounded regeneration, and structural isolation between agent roles.
Oak National Academy's `oak-ai-autoeval-tools` is the closest dedicated
quality-evaluation analogue. `Educhain` is the closest reusable educational
content-generation library, while `education-agent-skills` is the strongest
reviewed pedagogy knowledge layer.

None of them, based on the reviewed repository documentation, provides the
same combination of:

- immutable curriculum and manifest contracts;
- curriculum-wide unit and workbook production;
- source-claim and artifact provenance receipts;
- deterministic plus independent cross-model review;
- rendered-document and visual QA;
- node-level write ownership and resumable evidence;
- fail-closed acceptance and honest run-level terminal states; and
- subscription-only provider routing with no billed-API fallback.

The differentiated position of this repository is therefore not merely “AI
course generation.” It is **curriculum production with software-release-grade
assurance**.

## Scope and method

This was a focused GitHub landscape scan, not an exhaustive census. Candidate
projects were discovered through searches combining curriculum, lesson,
course, LangGraph, multi-agent, evaluation, validation, evidence, and
educational-content terms. Claims below were checked against the projects'
GitHub repository pages and READMEs on 2026-08-14.

Projects were compared on the concerns that the local planning history treats
as essential:

- scope of generated instructional artifacts;
- curriculum or source grounding;
- graph-based, resumable orchestration;
- deterministic validation;
- model-based qualitative review;
- independence between author and judge;
- artifact rendering and learner-facing QA;
- retained intermediate evidence and provenance;
- explicit acceptance and terminal states; and
- provider and credential governance.

The local comparison baseline is:

- `plans/20_subscription_only_execution_model/subscription_only_execution_model.plan.v1.md`;
- `plans/26_langgraph_curriculum_factory/post_morten/postmortem.v2.md`;
- `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/implementation.graph.v7.yaml`;
- `plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/results/v7/N60_ADVERSARIAL_REGRESSION.result.v1.json`; and
- `issues/README.md`.

## Landscape map

| Project | Primary role | What is materially similar | What remains different |
|---|---|---|---|
| [ai-lesson-agent](https://github.com/harshithasompura/ai-lesson-agent) | Stateful interactive lesson agent | LangGraph orchestration, Postgres checkpoints, plan-approval interrupt, deterministic checks before model evaluation, bounded regeneration, prerequisite graph, and structural separation of planner, quiz, and tutor contexts | Converts one PDF into an interactive lesson rather than producing a manifest-defined curriculum and workbook. Review is self-evaluation rather than an independently governed cross-family release gate. It does not document curriculum-wide receipts, rendered-PDF QA, or a release terminal comparable to this repository's N90 audit. No explicit license file was visible in the reviewed repository root, so its code should not be reused without clarification. |
| [oak-ai-autoeval-tools](https://github.com/oaknational/oak-ai-autoeval-tools) | Lesson-plan evaluation workbench | Builds datasets of generated lesson plans, defines lesson-oriented tests, runs LLM-as-judge evaluations, and makes results inspectable. This is the closest analogue to a reusable qualitative curriculum-evaluation layer. | It evaluates uploaded lesson plans rather than orchestrating research, generation, repair, rendering, evidence, and release. It uses OpenAI API configuration and does not claim author/judge provider independence or hash-bound execution receipts. |
| [Educhain](https://github.com/satvik314/educhain) | Educational-content generation library | Python API for lesson plans, questions, flashcards, notes, multiple pedagogical approaches, and export to PDF, JSON, and CSV. Its modular engines are potentially useful as a reference for curriculum-neutral content APIs. | Generation is the product boundary. The README does not describe stateful production graphs, independent review, source-claim receipts, fail-closed acceptance, or final-artifact visual QA. Its provider model includes billed APIs, including OpenAI and Gemini. |
| [education-agent-skills](https://github.com/GarethManning/education-agent-skills) | Evidence-grounded pedagogy library | A large, agent-compatible collection of curriculum, assessment, and learning-science skills for Claude and Codex. It names supporting research, rates evidence strength, records exclusions, and explicitly distinguishes research-backed from original practitioner frameworks. | It is a knowledge and prompting layer, not a production control plane. It does not itself provide run persistence, artifact rendering, acceptance topology, receipts, or terminal-state governance. |
| [EduAgent](https://github.com/StudentTraineeCenter/edu-agent) | LangGraph/RAG learning platform | Uses LangGraph, document ingestion, RAG with source citations, adaptive study plans, quizzes, flashcards, mind maps, and persisted application data. It demonstrates a mature application shape around grounded educational generation. | It is learner-facing adaptive tutoring, not a teacher-facing curriculum publishing factory. Its documented stack relies on Azure OpenAI and other Azure services. The README does not expose curriculum release gates, independent model review, or artifact-level evidence chains. |
| [DeepTutor-local-app](https://github.com/therealtimex/DeepTutor-local-app) | Multi-agent learning and research application | Question planning, generation, validation reports, retained intermediate files, timestamped outputs, multi-agent learning plans, session persistence, and PDF/Markdown export. It is the closest reviewed example of keeping generation intermediates as inspectable artifacts. | Its validation is described as single-pass relevance analysis without rejection logic. It focuses on personalized learning, question generation, and research rather than curriculum-wide publishing and release assurance. It is AGPL-3.0, which matters if code reuse is considered. |
| [CodeSera](https://github.com/RylanHexx/CodeSera) | End-to-end code-course generator | A direct Planner → Researcher → Writer pipeline that produces multi-lesson HTML courses with exercises, quizzes, projects, navigation, and a reusable design system. | It is a lightweight generation application with a very small visible history at review time. It does not document independent QA, deterministic acceptance, evidence receipts, source-claim verification, or resumable release governance. |
| [ClassroomIO](https://github.com/classroomio/classroomio) | Full LMS with AI authoring | Generates course outlines, lesson content, and assignments inside a self-hostable LMS with course management, learner delivery, grading, and certificates. It demonstrates the downstream product experience a curriculum factory could feed. | AI authoring is enabled through provider API keys and is integrated into an LMS rather than governed as an auditable production run. The README does not describe comparable evidence preservation, cross-family review, or fail-closed artifact acceptance. It is AGPL-3.0. |

## Closest match: `ai-lesson-agent`

`ai-lesson-agent` is the most useful architectural comparison because it makes
several controls structural rather than leaving them as prompt instructions.
Its documented guarantees include:

- graph topology that prevents skipping the quiz;
- omission of the answer key from the tutor context rather than a prompt asking
  the tutor not to reveal it;
- a prerequisite graph used to order questions;
- deterministic checks before a four-criterion model evaluation;
- at most three regeneration attempts;
- a human approval interrupt after plan generation; and
- checkpointed pause and resume through LangGraph.

That philosophy closely matches this repository's preference for graph edges,
schemas, ownership rules, and terminal guards over behavioral promises.

The boundary is equally important. `ai-lesson-agent` is an interactive study
experience built from one source PDF. This repository is attempting a broader
production problem: convert a curriculum-owned manifest and domain contract
into a complete, publishable corpus while retaining evidence sufficient to
explain why every unit and the run as a whole were accepted. The former can
finish when a learner completes a lesson; the latter must prove that every
shipped artifact is safe, readable, grounded, complete, and consistently
rendered.

## Closest quality layer: Oak AutoEval

Oak National Academy's AutoEval project is the strongest direct evidence that
lesson-specific model evaluation is useful as its own subsystem. It supports:

- uploading lesson plans;
- constructing representative datasets;
- defining evaluation tests;
- running tests across a dataset; and
- viewing comparative results.

This suggests a useful separation for the local architecture: qualitative
lesson review criteria should be managed as versioned evaluation assets and
tested against a corpus, not exist only as prompts embedded in a production
graph.

The project also clarifies what AutoEval does not solve. A judge result does
not prove that the renderer emitted the reviewed content, that the supporting
source actually entails each claim, that every manifest unit was produced, or
that the final run reached a truthful terminal. Those remain deterministic and
provenance responsibilities of the production system.

## Strongest pedagogy layer: `education-agent-skills`

`education-agent-skills` is relevant because it treats educational knowledge
as modular agent capabilities rather than one large curriculum prompt. It also
does three things worth preserving in any future local pedagogy library:

1. names the research supporting a practice;
2. rates the strength of that evidence; and
3. records excluded or weakly supported practices explicitly.

This is more rigorous than merely naming a familiar framework such as Bloom's
taxonomy or learning styles. It could inform how this repository separates
curriculum-owned domain rules from reusable pedagogy rules, but the skills
would still require local schemas, tests, source verification, and
artifact-level acceptance before becoming production authority.

## What the landscape validates

### Stateful graphs are a credible foundation

`ai-lesson-agent` and EduAgent both use LangGraph for educational workflows.
The use of checkpoints, interrupts, and explicit graph stages supports this
repository's choice to model curriculum production as a resumable state
machine rather than a single prompt or script.

### Generation and evaluation should be separate subsystems

Educhain and CodeSera emphasize generation; Oak AutoEval emphasizes evaluation.
The separation visible across projects reinforces the local design choice to
make authoring and judging distinct jobs. The landscape does not, however,
show another reviewed educational repository enforcing the local requirement
that the final qualitative judge come from a different model family than the
generator.

### Intermediate artifacts are operationally valuable

DeepTutor retains background knowledge, question plans, individual results,
validation reports, and timestamped output directories. This supports the
local decision to preserve attempts and intermediate evidence. The local
design goes further by binding results to schemas, prompts, predecessors, and
digests.

### Structured educational outputs are already commoditized

Lesson-plan, quiz, flashcard, note, and course generation appear in multiple
open-source projects. These capabilities alone are not a defensible technical
identity. Reliability, provenance, safety, artifact quality, and honest
release semantics are the stronger differentiators.

## Gaps not covered by the reviewed projects

### Claim-level source support

Several candidates use RAG or citations, but the reviewed documentation does
not establish a receipt proving that a particular source passage supports a
particular instructional or safety claim. This distinction matters locally:
a hash can prove which bytes were retrieved without proving that those bytes
entail the claim made in a lesson.

### Final rendered-artifact review

Projects generate HTML or export PDF, but no reviewed candidate documents a
gate that evaluates the actual learner-facing rendered artifact and proves it
matches the accepted semantic content. The local Arduino audit demonstrates
why this matters: unit acceptance records can pass while shipped PDFs remain
unreadable or omit required content.

### Curriculum-wide completion semantics

The reviewed projects generally describe successful feature flows, not a
formal run state proving that every manifest item was produced and accepted.
This repository's distinction among `PASSED`, `BLOCKED`, `NOT_AVAILABLE`,
`ACTIVATED`, and `REMEDIATION_VERIFIED_NOT_ACTIVATED` is unusual and valuable.

### Versioned execution authority

No reviewed educational candidate documents the same combination of approved
specification digest, graph digest, prompt digest, predecessor receipts,
exclusive write ownership, immutable failed attempts, and terminal audit.
This is the clearest technical differentiator, although the local history also
shows its cost: without a canonical current-version pointer, rigorous version
preservation can make operational discovery harder.

### Subscription-only, no-fallback routing

Most reviewed applications are API-key oriented or support a menu of hosted
providers. They do not appear designed around authenticated consumer
subscriptions with an explicit prohibition on billed API fallback. The local
provider constraint is therefore both unusual and an integration limitation;
it should not be assumed that provider adapters from these projects can be
adopted directly.

## Practical implications for this repository

### Patterns worth studying

- From `ai-lesson-agent`: structural context isolation, human interrupts,
  bounded retry, and prerequisite-graph ordering.
- From Oak AutoEval: versioned evaluation datasets, test authoring, batch
  comparison, and inspectable judge results.
- From Educhain: a small, curriculum-neutral Python interface for educational
  content types and exports.
- From `education-agent-skills`: research citations, evidence-strength labels,
  explicit exclusions, and composable pedagogy capabilities.
- From DeepTutor: predictable, timestamped intermediate-artifact layouts.
- From ClassroomIO: downstream course-management and learner-delivery
  integration boundaries.

### Patterns that should not be imported uncritically

- self-evaluation by the same model family as the author;
- “citation present” as a substitute for claim-support verification;
- API-key fallback or provider menus that bypass the approved routing policy;
- one-pass validation without rejection or repair semantics;
- export success as proof of learner-facing render quality; and
- application success without a curriculum-wide completion denominator.

### Recommended positioning

Describe the project as:

> An auditable AI curriculum production system that treats instructional
> artifacts like release-engineered products: contract-bound inputs,
> source-grounded generation, independent review, deterministic and visual QA,
> retained evidence, resumable execution, and honest terminal states.

Avoid positioning it as simply an AI lesson-plan or course generator. That
category is crowded and understates the work already present in the plans and
runtime.

## Candidate integration strategy

The landscape supports selective borrowing of ideas, not wholesale adoption
of another project. A plausible conceptual stack is:

```text
education-agent-skills-like layer   reusable pedagogy knowledge
Educhain-like interface             curriculum-neutral content primitives
LangGraph runtime                   resumable production orchestration
Oak-AutoEval-like subsystem         corpus-based qualitative evaluation
local contracts and receipts        provenance, ownership, and release authority
local rendering gates               actual PDF/workbook/visual acceptance
```

The local contracts and receipt system remain the control plane. External
projects could inform individual layers only after license review, threat
modeling, dependency evaluation, and tests against the local acceptance
contract.

## Limitations

- The scan relied primarily on repository READMEs and exposed project
  documentation; it was not a line-by-line code audit of every candidate.
- GitHub search results favor projects with strong naming and documentation,
  so relevant but poorly indexed repositories may be absent.
- Repository activity, dependencies, provider support, and licensing can
  change after the access date.
- Feature claims are the projects' own unless this note explicitly labels a
  conclusion as comparative inference.
- Absence from a README is not proof that a capability does not exist in code;
  it means the capability was not established by this research pass.

## Sources

All source pages below were fetched and verified as real, on-topic GitHub
repositories on 2026-08-14.

- `harshithasompura/ai-lesson-agent`, “AI Learning Agent that transforms a PDF
  into an interactive lesson” — https://github.com/harshithasompura/ai-lesson-agent
- `oaknational/oak-ai-autoeval-tools`, “Oak National Academy's AI Auto Eval
  tools” — https://github.com/oaknational/oak-ai-autoeval-tools
- `satvik314/educhain`, “A Python package for generating educational content
  using Generative AI” — https://github.com/satvik314/educhain
- `GarethManning/education-agent-skills`, “Evidence-grounded AI skills for
  teachers, school leaders and EdTech builders” —
  https://github.com/GarethManning/education-agent-skills
- `StudentTraineeCenter/edu-agent`, “AI-powered educational platform” —
  https://github.com/StudentTraineeCenter/edu-agent
- `therealtimex/DeepTutor-local-app`, “DeepTutor: AI-Powered Personalized
  Learning Assistant” — https://github.com/therealtimex/DeepTutor-local-app
- `RylanHexx/CodeSera`, “AI-powered course generator” —
  https://github.com/RylanHexx/CodeSera
- `classroomio/classroomio`, “The Open Source Learning Management System for
  Companies” — https://github.com/classroomio/classroomio
- `langchain-ai/langgraph`, “Low-level orchestration framework for building
  stateful agents” — https://github.com/langchain-ai/langgraph

## Discarded or de-emphasized results

- Static curriculum repositories such as Microsoft's `AI-For-Beginners` were
  excluded because they publish curriculum but do not generate or govern it.
- General LMS projects without a substantive AI authoring path were excluded.
- Robotics “curriculum learning” repositories were excluded because
  curriculum means task scheduling for machine learning rather than human
  instructional content.
- GitHub topic pages and “awesome” lists were used only for discovery; claims
  in this note are tied to the candidate repositories themselves.
- Research prototypes described only in papers were de-emphasized because the
  user's question concerned comparable GitHub implementations.
