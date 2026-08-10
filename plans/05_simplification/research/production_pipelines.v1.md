# Production Pipelines for Long-Form Structured Content with LLMs

Research date: 2026-07-31. Scope: named systems that generate books, textbooks, courses, surveys, reports or technical documentation at scale using orchestrator/worker or plan-then-write architectures.

## Evidence labels used throughout

- **(A) Engineering-documented** — peer-reviewed paper, published system card, or first-party engineering blog with mechanism-level detail and numbers.
- **(B) Inspectable open source** — repository you can read; architecture verifiable from code.
- **(C) Vendor marketing** — claims exist, mechanism does not. Explicitly called out.

A system can be both A and B. Where I could not verify a claim, I say so rather than filling the gap.

---

## Summary table

| System | Owner | Label | Architecture | State between sections | "Done" decided by | Cross-section consistency mechanism |
|---|---|---|---|---|---|---|
| STORM / Co-STORM | Stanford OVAL | A + B | 4 stages: knowledge curation → outline → **parallel** section writing → polish | Shared `InformationTable` (retrieved snippets) on disk; sections do **not** see each other | Code (pipeline stages), no critic loop | Post-hoc dedup pass only. No contradiction detection |
| AutoSurvey | NeurIPS 2024 | A + B | Outline consolidation → **parallel** subsection drafting → refinement → LLM-jury eval | Retrieved papers per subsection; refinement injects **neighbouring** subsections | Multi-LLM-as-judge (GPT-4 + Claude + Gemini) | Refinement pass sees previous + following subsection |
| SurveyForge | ACL 2025 | A + B | Outline heuristics → memory-driven retrieval agent (SANA) → **parallel** sections → refinement | Three memory modules (sub-query, retrieval, temporal rerank) | Code + SurveyBench metrics | Refinement over concatenated sections to remove repetition |
| AgentWrite / LongWriter | THUDM, ICLR 2025 | A + B | Plan (outline + per-paragraph word budget) → **sequential** write | Each subtask receives all *n−1* previously generated sections verbatim | Word-count schema + trained model | Sequentiality itself. Parallel variant measured and rejected |
| Re3 | Berkeley/Meta, EMNLP 2022 | A + B | Plan → Draft → Rewrite (rerank) → Edit | Structured plan + rolling summaries + NER-built character attribute dictionary | Trained discriminative rerankers | Entailment model flags contradictions against attribute dictionary — **measured as near-useless** |
| WriteHERE | arXiv 2503.08275 | A + B | Recursive, heterogeneous task decomposition (retrieval / reasoning / composition) interleaved with execution | Dynamic task graph, not a fixed outline | Recursive planner | Decomposition adapts mid-write instead of committing to an outline |
| Open Deep Research | LangChain | A + B | Scope → Research (supervisor + parallel sub-agents) → **Write in one LLM call** | Research brief + cleaned sub-agent notes in LangGraph state | Supervisor decides research sufficiency; writing is single-shot | **Abandoned parallel section writing**; one writer sees everything |
| Claude Research | Anthropic | A | Lead agent (Opus) + 3–5 parallel subagents (Sonnet) + separate CitationAgent | Lead agent's plan persisted to Memory (context truncates at 200k) | Lead agent self-assessment against rubric | Single synthesising agent; citations added in separate pass |
| Magentic-One | Microsoft | A + B | Orchestrator with **Task Ledger** (facts, guesses, plan) + **Progress Ledger** (per-step reflection) | Two explicit ledgers, rewritten on stall | Orchestrator self-reflection; stall counter triggers replan | Not a long-form writer; ledger pattern is the transferable part |
| The AI Scientist | Sakana | A + B | Idea → experiment → **sequential** section-by-section LaTeX fill via Aider → reflection → reviewer | LaTeX template as the artifact; notes/plots passed forward | Automated LLM reviewer | Weak. Independent eval found duplicate/misplaced sections in 57% of papers |
| GPT-Researcher (multi_agents) | Assaf Elovic | A + B | Chief Editor → Editor (outline) → parallel Researchers → Reviewer ⇄ Reviser → Writer → Publisher | LangGraph `ResearchState` + nested `DraftState` subgraph per section | Reviewer returns `None` to accept; loop otherwise | Subgraph isolation to avoid race conditions; writer only touches finalised content |
| Instructional Agents | arXiv 2508.19611 | A | ADDIE-framework multi-agent: syllabus → slides → scripts → assessments | Prior artifacts passed forward | Four modes from Autonomous to Full Co-Pilot; humans rate | Sequential artifact chaining; humans rated more collaboration = higher quality |
| Learn Your Way | Google Research | A | Personalisation pipeline (re-level + interest swap) then multi-representation generation from **an existing source chapter** | Source PDF is ground truth for every representation | 3 pedagogy experts, rating ≥0.85; RCT with 60 students | Everything derives from one fixed source — consistency by construction |
| LongPage / book-writing model | arXiv 2605.17064 | A | **Not agentic.** Single long-context model trained on multi-resolution scaffolds (scene → chapter → book → prompt) | Scaffold is generated in-context before prose | Model | Consistency learned, not orchestrated |
| Cosmopedia | Hugging Face | A + B | Massively parallel independent generations from clustered seed prompts | None — no cross-document state by design | Code + dedup filters | Not applicable; diversity engineered via audience × style prompt matrix |
| Elicit / Ought | Elicit | A (partial) | "Factored cognition": task-graph execution framework, dependency-scheduled | Task graph; every stage auditable and exportable | Per-block validation, PRISMA-aligned audit trail | Each block validated independently, then composed |
| LibriScribe | OSS | B | Concept → Outline → Characters → World → Chapter writer → Editor → Format | **Files on disk**: `project_data.json`, `outline.md`, `characters.json`, `world.json`, `chapter_N.md` | Explicit human approval gates per stage | Every agent reads the shared outline/characters/world files |
| Sudowrite | Sudowrite | C (docs, not engineering) | Story Bible (Braindump → Synopsis → Style → Characters → World → Outline → Scenes) + Chapter Continuity | Story Bible; up to 25 linked docs / 20,000 words of prior narrative | Human | Context stuffing. Documented as *reference*, not enforcement |
| Novelcrafter | Novelcrafter | C | Typed Codex (character/location/object/lore/subplot/other), selectively injected | Codex database | Human | Selective prompt injection |
| Writer.com / Jasper / Notion AI / Gamma | vendors | **C — no engineering substance** | Claimed knowledge-graph grounding / brand layers | unstated | unstated | unstated |
| Pearson / McGraw-Hill / O'Reilly | publishers | **C — policy statements, not pipelines** | n/a | n/a | Human editorial | n/a |
| Khan Academy | Khan Academy | C (honest, but no architecture) | LLM drafts paragraphs from a human outline; drafts extra question variants | n/a | 20-person human content team | Human review of every output |

---

## 1. Peer-reviewed and engineering-documented systems (A)

### STORM — Stanford OVAL (NAACL 2024) — also (B)

The most-copied architecture in this space, and the details matter because most later systems inherit its weaknesses.

Four modules, per the repo README: knowledge curation, outline generation, article generation, article polishing. "The system first conducts Internet-based research to collect references and generates an outline," then "uses the outline and references to generate the full-length article with citations."

The load-bearing detail is in `knowledge_storm/storm_wiki/modules/article_generation.py`. **Sections are written in parallel**:

> `with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_thread_num) as executor:`

And each section writer sees **only its own subtree of the outline plus its own retrieved documents** — not the other sections, not their drafts. Retrieval is per-section: `information_table.retrieve_information(queries=section_query, search_top_k=self.retrieve_top_k)`. Results are collected via `as_completed` and merged by `article.update_section(...)`.

The only cross-section mechanism is the polish module, and it is explicitly **deduplication, not consistency**. Its `PolishPage` signature reads: "You are a faithful text editor that is good at finding repeated information in the article and deleting them to make sure there is no repetition." There is no contradiction detection anywhere in the pipeline.

Reported limits, verbatim from the paper and README: "The system cannot produce publication-ready articles that often require a significant number of edits." The paper names two emergent failure modes: "source bias transfer and over-association of unrelated facts."

Co-STORM adds a `DiscourseManager` with turn policy, an LLM moderator, and a persistent "mind map" that organises collected information "into a hierarchical concept structure" — i.e. Stanford's own answer to STORM's missing shared state was to add an explicit external knowledge structure.

- https://arxiv.org/abs/2402.14207
- https://github.com/stanford-oval/storm

### AutoSurvey — NeurIPS 2024 — also (B)

Closest published analogue to a "generate a whole structured book" pipeline, and it publishes the numbers.

Outline: papers are "randomly divided according to the LLM's context window size, resulting in the creation of multiple outlines. The model then consolidates these outlines to form the final comprehensive outline." Map-reduce over the outline itself.

Drafting: parallel per subsection, each retrieving its own references: "the sub-outline Oi of that subsection will be used to retrieve the necessary relevant reference papers Psec."

The consistency mechanism is the one worth stealing — **a refinement pass with a sliding local window**:

> "During the refinement process, the model needs to polish each subsection based on the local context (considering the previous and following subsections) to improve readability, eliminate redundancies, and enhance coherency."

Done is decided by a multi-LLM jury (GPT-4, Claude-3-Haiku, Gemini-1.5-Pro), correlating with human judgement at Spearman ρ = 0.5429 — *moderate*, which is itself a finding: the judge is not a reliable oracle.

Failure modes with numbers:
- Without retrieval, citation recall collapses from **83.48% → 60.11%**.
- **Reflection barely mattered: 4.57 vs 4.56 average score.** A critic loop bought essentially nothing.
- Error analysis: "overgeneralization accounts for the largest proportion (51%)" — the model falls back on parametric knowledge rather than the retrieved sources.

- https://arxiv.org/abs/2406.10252
- https://proceedings.neurips.cc/paper_files/paper/2024/file/d07a9fc7da2e2ec0574c38d5f504d105-Paper-Conference.pdf

### SurveyForge — ACL 2025 main — also (B)

Same shape as AutoSurvey, but replaces ad-hoc retrieval with an explicit memory architecture (SANA):

- **Memory for Sub-query** — uses already-retrieved literature as memory to decompose queries, instead of naive prompting.
- **Memory for Retrieval** — holds "the literature 𝒫R related to the entire outline as memory M" so a subsection retrieves against the whole document's frame, not just its own title.
- **Temporal-aware Reranking Engine** — "integrates textual relevance, citation impact, and publication recency."

Confirms the dominant pattern: "The content of each section is generated in parallel to reduce the generation time," followed by a refinement stage "aimed at refining the raw survey obtained by concatenating the contents of each section generated in parallel."

Stated limitation, and it is the honest one for this whole field: the system struggles with "establishing profound connections across multiple publications," defaulting to "mechanical reference listing" rather than synthesis.

- https://arxiv.org/abs/2503.04629
- https://github.com/InternScience/SurveyForge

### AgentWrite / LongWriter — THUDM, ICLR 2025 — also (B)

**The single most decision-relevant measurement I found.**

Two steps. Plan: "using LLM to generate a writing outline given a writing instruction, which includes the main content and word count requirements for each paragraph." Write: "call the LLM serially to complete each subtask, generating the writing content section by section."

Crucially, when writing paragraph *n*, the model receives "the previously generated n−1 sections, allowing the model to continue writing the next section based on the existing writing history."

They ablated exactly the question every orchestrator design faces:

> "+Parallel slightly improves the model's output length score, it impairs the output quality of AgentWrite, especially in terms of Coherence (−6%)."

Parallel section generation is faster and measurably less coherent. This is the direct empirical counterpart to LangChain's qualitative finding below.

- https://arxiv.org/abs/2408.07055
- https://github.com/THUDM/LongWriter

### Re3 — EMNLP 2022 — also (B)

Oldest system here and still the most sophisticated attempt at *enforced* cross-section consistency. Four modules:

- **Plan** — "augment a given premise with a setting, characters, and outline," generated by sequential prompting with rejection sampling.
- **Draft** — reconstructs the prompt at every step: "we include 'Previous Sections' Outlines' as a very high-level summary of previous larger story sections, followed by a 'Recent Story Summary'... At the end we repeat verbatim the immediately preceding passage as 'Autoregressive Context.'" A three-tier context hierarchy: coarse global, medium recent, verbatim local.
- **Rewrite** — two *trained discriminative* rerankers (coherence with prior story; relevance to the current outline point) plus rule-based heuristic filters.
- **Edit** — maintains "an 'Attribute Dictionary' for each character," extracted by prompting for a numbered list of facts, then uses "an entailment model to flag contradictions between new and old values for the same key."

**And they report that it didn't work.** The Edit module "contributes negligibly to primary metrics," and "there remain many continuity issues in re3's final stories which are not resolved by our Edit module" — because many errors are "non-character-based inconsistencies, such as in the setting or current scene." Their listed unsolved long-range problems: "overall theme; scenes and world setting; pace and tempo of storylines; and foreshadowing before major events."

This is the most valuable negative result in the corpus: a structured, entity-keyed contradiction detector with a trained entailment model still failed to fix global consistency.

- https://aclanthology.org/2022.emnlp-main.296/
- https://github.com/yangkevin2/emnlp22-re3-story-generation

### Open Deep Research — LangChain — also (B)

First-party engineering blog documenting an architecture they *reversed*.

> "the reports were disjoint because the section-writing agents were not well coordinated"

They abandoned parallel section writing. Current architecture is three phases: **Scope** (clarification loop → research brief), **Research** (supervisor delegates to parallel sub-agents on subtopics), **Write** (a *single LLM call* producing the whole report from the brief plus all research findings).

Context engineering: chat history is compressed into a brief; "our sub-agent cleans up its findings and returns them to the supervisor," pruning irrelevant tokens before they hit the supervisor's context.

The key architectural claim: **multi-agent is used for research (parallelisable, low-coupling) and deliberately not for writing (high-coupling)**.

Open questions they name: how to handle token-heavy tool responses, whether evals should run during execution, whether long-term memory should cache expensive research.

- https://www.langchain.com/blog/open-deep-research
- https://github.com/langchain-ai/open_deep_research

### Claude Research — Anthropic

Orchestrator-worker: "a lead agent coordinates the process while delegating to specialized subagents that operate in parallel." The lead "analyzes it, develops a strategy, and spawns subagents to explore different aspects simultaneously," then synthesises and hands off to a dedicated CitationAgent.

Delegation contract, verbatim — this is the most portable single sentence in the whole corpus:

> "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries."

Persistence: the lead agent saves "its plan to Memory to persist the context, since if the context window exceeds 200,000 tokens it will be truncated and it is important to retain the plan."

Evaluation rubric: "factual accuracy (do claims match sources?), citation accuracy (do the cited sources match the claims?), completeness (are all requested aspects covered?), source quality (did it use primary sources over lower-quality secondary sources?), and tool efficiency."

Cost: "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats," and "token usage by itself explains 80% of the variance" in performance.

Failure modes, verbatim and unusually candid:
- "spawning 50 subagents for simple queries, scouring the web endlessly for nonexistent sources, and distracting each other with excessive updates"
- subagents "duplicate work, leave gaps, or fail to find necessary information" without detailed instructions
- agents "consistently chose SEO-optimized content farms over authoritative but less highly-ranked sources like academic PDFs or personal blogs"

Explicit anti-recommendation:
> "some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems today"

- https://www.anthropic.com/engineering/multi-agent-research-system

### Magentic-One — Microsoft — also (B)

Not a content generator, but its state design is the cleanest published version of "orchestrator memory". Two ledgers: a **Task Ledger** holding facts, educated guesses and the plan; a **Progress Ledger** where the orchestrator "self-reflects on task progress and checks whether the task is completed" at each step. Outer loop rewrites the Task Ledger and replans when "progress is not being made for enough steps" — an explicit stall counter rather than an open-ended loop.

- https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/

### The AI Scientist — Sakana — also (B)

Write-up is **sequential section-by-section into a fixed LaTeX template** via Aider, "proceeding in order of introduction, background, methods, experimental setup, results, and conclusion," with Semantic Scholar used "to autonomously find relevant papers to cite."

Sakana's own stated failure modes: no vision capabilities so "generated plots are sometimes unreadable"; "can incorrectly implement its ideas or make unfair comparisons to baselines"; and it "struggles to compare the magnitude of two numbers."

Independent evaluation (arXiv 2502.14297) supplies harder numbers:
- "five out of twelve proposed experiments (42%) failed due to coding errors"
- four of seven manuscripts (57%) contained hallucinated or incorrect numerical results
- structural defects in 57% of papers: "missing or misplaced figures, incomplete sections (e.g., 'Conclusions Here' placeholder), duplicates, or repeated figures"
- literature review "relying on simplistic keyword searches rather than profound synthesis," "median of just five citations per paper — most of which were outdated"
- cost: "$42 USD — an average of $6 per manuscript"

The 57% structural-defect rate is what happens when a template slot is the only definition of "section done".

- https://sakana.ai/ai-scientist/
- https://arxiv.org/abs/2502.14297

### Learn Your Way — Google Research

The only system here with a randomised controlled trial. Pipeline: personalisation layer (re-level to grade "while maintaining the scope of its content," then "strategic replacement of generic examples with ones that are personalized to the learner's reported interests"), then generation of five representations — immersive text with embedded questions, section-level quizzes, slides + narration, audio lessons, mind maps.

Stack: "a powerful base model, multi-step agentic workflows, and fine-tuned components," including a model fine-tuned specifically for educational illustrations, on top of LearnLM inside Gemini 2.5 Pro.

Quality gate: three pedagogical subject-matter experts rating "accuracy, coverage, and the LearnLM learning science principles," achieving "an average expert rating of 0.85 or higher across all pedagogical criteria."

Outcome: RCT, 60 students aged 15–18, +11 percentage points on a retention test 3–5 days later versus a standard digital reader.

Architecturally the critical choice: **it transforms a fixed source chapter rather than generating from nothing**, so global consistency is inherited from the source rather than enforced across agents.

- https://research.google/blog/learn-your-way-reimagining-textbooks-with-generative-ai/

### LongPage / "Towards Human-Level Book-Writing Capability" (arXiv 2605.17064)

The dissenting architecture: **no orchestrator at all**. A long-context model is trained on ~6,000 Project Gutenberg books (649.1M Llama-3 tokens; 60.43% book text, 39.35% planning scaffold, 0.23% synthetic prompt) to expand a prompt through a four-level scaffold — scene, chapter, book, prompt/metadata — and then into prose, single-pass with "regex-guided constrained decoding." Notable trick: an "Early First Chapter" stage that "generates the first chapter text early for quality control and continuity establishment, before full-book chapter planning."

Caveat: the paper's own evaluation is weak — "several training components are evaluated jointly, suggesting future ablation studies are needed."

- https://arxiv.org/abs/2605.17064

### Instructional Agents (arXiv 2508.19611) — closest published analogue to a curriculum builder

Multi-agent system following the ADDIE instructional-design framework "to generate syllabi, slides, scripts, and assessments," evaluated across five university-level CS courses.

Four operation modes — **Autonomous** (no human input), **Catalog-Guided** (institutional data and prior feedback), **Feedback-Guided** (instructors review outputs), **Full Co-Pilot** (pauses at each step for real-time feedback). Six artifact types evaluated: Learning Objectives, Syllabus, Assessments, Final Slides, Slide Scripts, Instructional Package.

Headline result: **"Human reviewers found that greater collaboration leads to higher quality."** Autonomy traded against quality, monotonically.

⚠️ Verification note: an automated read of the PDF returned a *different* set of four mode names and a Dean/Instructional-Designer/Teaching-Assistant agent roster. The project homepage contradicts it. I am reporting only the homepage-verified version; treat the agent roster as unverified.

- https://arxiv.org/abs/2508.19611
- https://hyan-yao.github.io/instructional_agents_homepage/

### Cosmopedia — Hugging Face — also (B)

Not orchestrated long-form, but the best-documented account of *content diversity at scale*: 25B tokens, 30M+ files, >10k H100 GPU hours, Mixtral-8x7B, open pipeline.

The mechanism worth borrowing is prompt-space engineering. They clustered "millions of web samples... into 145 clusters," kept 112 topics after filtering, then multiplied coverage deliberately: "four different audiences (young children, high school students, college students, researchers) and leveraging three generation styles (textbooks, blog posts, wikiHow articles), we can get up to 12 times the number of prompts." They also "condition the prompts on the topic only 50% of the time."

Result: "less than 1% duplicate content" across 30 million prompts, and "less than 4 contaminated samples for MMLU" by 10-gram overlap.

- https://github.com/huggingface/blog/blob/main/cosmopedia.md

### Elicit / Ought — partial (A)

The "factored cognition" lineage. Ought built "a task graph execution framework for efficiently running compositions of language model tasks... Elicit engineers only need to specify how tasks depend on other tasks (e.g. claim extraction depends on ranking), and the scheduling and execution across compute nodes happen automatically." The framework "runs the graph of tasks in parallel as efficiently as allowed by the dependency structure."

Their stated philosophy is the important bit: "we're generally not training machine learning models end-to-end using outcome data, but building Elicit compositionally and inspired by human processes."

The current product side is thinner on mechanism but strong on the *governance* pattern: search → abstract screening → full-text screening → extraction → report, "with each stage exportable to CSV or XLSX and each decision recorded for end-to-end auditability," each block validated independently (PRISMA 2020 aligned).

- https://ought.org/updates/2022-04-08-elicit-plan
- https://elicit.com/blog/systematic-review-for-prisma-2020

---

## 2. Inspectable open source (B)

### GPT-Researcher `multi_agents` — also (A) via its blog

Agent roster: Chief Editor (orchestrator, LangGraph), Editor (plans outline), Researcher, Reviewer, Reviser, Writer, Publisher. "the writer only touches finalized content."

Real state schema, verbatim:

```python
class ResearchState(TypedDict):
    task: dict
    initial_research: str
    sections: List[str]
    research_data: List[dict]
    title: str
    headers: dict
    date: str
    table_of_contents: str
    introduction: str
    conclusion: str
    sources: List[str]
    report: str
```

Parallelism is handled by a **nested subgraph with its own state** — the explicitly stated reason being to avoid "race conditions and inconsistencies in the final data report":

```python
class DraftState(TypedDict):
    task: dict
    topic: str
    draft: dict
    review: str
    revision_notes: str
```

Stopping condition is a code-level predicate, not a model judgement call:

```python
workflow.add_conditional_edges('reviewer',
    (lambda draft: "accept" if draft['review'] is None else "revise"),
    {"accept": END, "revise": "reviser"})
```

- https://docs.gptr.dev/blog/gptr-langgraph

### LibriScribe

Cleanest example of **filesystem-as-state** for book generation. Agents run in order: Concept Generator → Outliner → Character Generator → Worldbuilder → Chapter Writer → Editor → Formatting. Project layout, verbatim:

```
your_project/
├── project_data.json
├── .libriscribe_status.json
├── outline.md
├── characters.json
├── world.json
├── chapter_1.md
```

`.libriscribe_status.json` is described as "lightweight stage/checkpoint recovery state" — resumability as a first-class concern. Explicit human gates at concept approval and outline review.

- https://github.com/guerra2fernando/libriscribe

### WriteHERE (arXiv 2503.08275)

The architectural dissent within the research literature. Argues that outline-first pipelines "rely on predefined workflows and rigid thinking patterns to generate outlines before writing, resulting in constrained adaptability during writing." Instead: three primitive task types — "retrieval, reasoning, and composition" — combined by "a planning mechanism that interleaves recursive task decomposition and execution, eliminating artificial restrictions on writing workflow." Claims to outperform SOTA on all automatic metrics for both fiction and technical report generation. No limitations section surfaced in the abstract.

### StoryWriter (arXiv 2506.16445, CIKM 2025)

Three modules, verbatim from the abstract: "(1) outline agent, which generates event-based outlines containing rich event plots, character, and event-event relationships. (2) planning agent, which further details events and plans which events should be written in each chapter to maintain an interwoven and engaging story. (3) writing agent, which **dynamically compresses the story history based on the current event** to generate and reflect new plots, ensuring the coherence of the generated story."

The compression-of-history mechanism is the notable part: state is neither full context nor a static summary, but a summary *conditioned on what is being written now*.

⚠️ A PDF read of this paper returned a plausible but unverifiable "consistency agent" that does not appear in the abstract's three-module list. Discount it.

### Other OSS book generators (low engineering value)

SimonWaldherr/AI-Book-Generator, wesleyscholl/book-generator, fangfufu/LLM-book-generator, raestrada/storycraftr, adamwlarson/ai-book-writer (AutoGen-based), takimdigital/AI-StorySmith. All follow the same title → concept → outline → sequential chapters shape. None publishes evaluation or failure analysis. Useful only as evidence of convergence on one naive pattern.

---

## 3. Vendor marketing with no engineering substance (C)

State this plainly: **no commercial long-form content vendor has published a mechanism-level account of its pipeline.**

- **Writer.com** — "grounded in business context via Writer's Knowledge Graph," agents "composable building blocks in Agent Builder." No architecture, no evaluation, no failure modes. Marketing.
- **Jasper** — "Jasper IQ, a proprietary intelligence layer that ingests your brand voice guidelines, style guides, product information." Claims "long-form consistency"; publishes nothing about how. Marketing.
- **Gamma** — "writes the body copy, places callouts and charts, and lays out the document." Product description only.
- **Notion AI** — third-party comparisons describe it as an assistant, "not as powerful as Jasper for generating full-length articles." No first-party engineering content.
- **Sudowrite** — better than the rest because the *documentation* is specific: Story Bible built in a fixed order (Braindump → Synopsis → Genre/Style → Characters → Worldbuilding → Outline → Scenes), Chapter Continuity linking "up to 25 linked documents," "up to 20,000 words of prior content" per generation, series-level Story Bible shared across books. But the honest reading is context-stuffing: the Story Bible "is included in the AI's context when generating new text, but the tool does not actively enforce consistency against it." No architecture, no measurements.
- **Novelcrafter** — six typed Codex categories (character, location, object, lore, subplot, other) "selectively injected" into prompts. Typed state is a genuine design choice; there is no published retrieval or validation detail.
- **Pearson, McGraw-Hill, O'Reilly** — I found **no production content pipeline** from any of them. Pearson's announcements concern AI *study tools* and certification content volume; McGraw-Hill's are a student-facing "AI Reader"; O'Reilly's public position is a **disclosure policy**, not a pipeline: authors must "track their use of GenAI and share this information with their editors." Any claim that major publishers run orchestrated LLM book-generation pipelines is unsupported by public evidence.
- **Khan Academy** — honest and correspondingly unglamorous. AI is used to draft paragraphs from a *human-written outline* and to generate additional question variants after a human writes the first of each type. A 20-person content team reviews every output. This is assisted authoring, not a generation pipeline.
- **Technical documentation (Stripe, Twilio, Google)** — searched specifically; found **the opposite of what the brief hypothesised**. Their published AI work is about making docs *consumable* by LLMs (Twilio's MCP server over 1,500+ endpoints, prompt libraries; Stripe/Google integration docs), not about generating docs with LLMs. The one genuinely transferable pattern in this space comes from docs-as-code tooling like Fern: generated code examples are **compiled or executed in CI before publication**, and CI blocks merges when docs contradict specs. That is the only "section is done" gate in this entire report that is decided by an executable oracle rather than a model or a human.

Independent-sounding comparisons deserve the same scrutiny: the widely-linked "We Tested 4 AI Novel Tools for 25 Chapters. Only 1 Survived" is **vendor marketing for Novarrium**. Despite the headline it publishes no methodology, no raw data, and attributes its contradiction examples to forum complaints rather than its own test. Do not cite it.

---

## What actually generalises

Ten findings that survived cross-checking. The first four are the ones that should change a design.

**1. Parallel section writing is measurably worse, and two independent groups reversed on it.**
LongWriter ablated it: parallel generation improved length but cost **−6% Coherence**. LangChain shipped it, then removed it: "the reports were disjoint because the section-writing agents were not well coordinated." Their resolution was to keep multi-agent for *research* and write the document in a single LLM call. STORM, AutoSurvey and SurveyForge all still parallelise — and all three need a post-hoc pass to clean up what parallelism broke. The split is not orchestrator-vs-monolith; it is **parallelise retrieval and analysis, serialise composition.**

**2. Nobody has a working contradiction detector. The best-engineered attempt was measured and failed.**
Re3 built the strongest version anyone has published — per-character attribute dictionaries extracted by NER, an entailment model flagging conflicting values for the same key — and reported it "contributes negligibly," because real inconsistencies are "non-character-based... such as in the setting or current scene." Every other system in this report handles cross-section conflict by **deduplication**, which is a different problem. STORM's polish prompt is literally about "finding repeated information... and deleting them." If your design needs global non-contradiction, the published state of the art will not give it to you; the working alternatives are (a) serialise so contradictions can't form, or (b) derive everything from one fixed source, as Learn Your Way does.

**3. Local-window refinement is the cheapest real coherence mechanism.**
AutoSurvey's refinement stage polishes "each subsection based on the local context (considering the previous and following subsections)." SurveyForge does the same over the concatenated draft. Re3's Draft module generalises it into a three-tier context — coarse outlines of all prior sections, a rolling recent summary, then the immediately preceding passage verbatim. That tiering is more useful than either "give it everything" or "give it nothing."

**4. Global critic loops buy less than everyone assumes; retrieval buys a lot.**
AutoSurvey's own ablation: removing reflection moved the score from 4.57 to 4.56. Removing retrieval collapsed citation recall from 83.48% to 60.11%. Spend the budget on grounding, not on a reviewer agent. Corroborating: their dominant residual error, at 51%, is "overgeneralization" — the model ignoring sources in favour of parametric knowledge, which no critic loop reliably catches.

**5. State lives on disk or in a typed graph state, essentially never in context alone.**
LibriScribe: `outline.md` + `characters.json` + `world.json` + per-chapter markdown + a checkpoint file. GPT-Researcher: a `ResearchState` TypedDict with a nested `DraftState` subgraph *specifically* to prevent race conditions. Anthropic: the lead agent writes its plan to Memory because "if the context window exceeds 200,000 tokens it will be truncated." Magentic-One: an explicit Task Ledger and Progress Ledger. Externalised, typed, resumable state is the one architectural choice on which every serious system agrees.

**6. "Done" is decided by code far more often than by a model.**
GPT-Researcher's gate is a lambda: accept if `review is None`. STORM's is pipeline-stage completion. Fern's is whether the code example compiles in CI. Model-judged completion is used where cheap and unreliable — AutoSurvey's LLM jury correlates with humans at ρ≈0.54, and Sakana's automated reviewer waved through papers that an independent evaluation found had hallucinated numbers in 57% of cases. **A schema, a word budget, or an executable check is a better oracle than a critic agent.**

**7. Sub-agent briefs need a fixed four-part contract.**
Anthropic, from production: "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries." Their documented failure without it — subagents "duplicate work, leave gaps, or fail to find necessary information" — is exactly the failure mode a fan-out curriculum builder would hit.

**8. Sub-agents must compress before returning.**
LangChain: "our sub-agent cleans up its findings and returns them to the supervisor," pruning irrelevant tokens. StoryWriter's writing agent "dynamically compresses the story history based on the current event." Anthropic's subagents "feed the most essential discoveries back." Raw tool output returned to an orchestrator is the standard way these systems die of context exhaustion.

**9. Cost is dominated by the fan-out, and it is knowable in advance.**
"Multi-agent systems use about 15× more tokens than chats," and "token usage by itself explains 80% of the variance" in performance. Sakana's counterpoint: $6 per manuscript — cheap enough that a 42% experiment failure rate and 57% structural-defect rate are economically tolerable if a human is reviewing anyway. Both numbers should inform whether fan-out is worth it for a given artifact.

**10. In education specifically, autonomy and quality trade off monotonically, and grounding beats generation.**
Instructional Agents, across five real university courses and four autonomy levels: "greater collaboration leads to higher quality." Khan Academy — the largest actual deployment — uses the LLM only to draft from a human outline and to clone question types, with every output reviewed by a 20-person team. And the only system with a randomised trial and a measured learning outcome, Learn Your Way (+11 points on delayed retention), does not generate a curriculum at all: it **transforms an existing authored chapter**, which is why its consistency problem largely disappears.

### Diversity, if generating many parallel artifacts

Cosmopedia is the reference implementation: topic clustering (145 → 112 topics), an explicit audience × style matrix producing 12× the prompts, seeding on topic only 50% of the time, and n-gram dedup/contamination checks — yielding "less than 1% duplicate content" across 30M generations. If a curriculum builder generates many lessons from one topic tree, this is the published recipe for keeping them from collapsing into each other.

### Two honest gaps

- **No published system solves global consistency for generated-from-scratch long-form content.** The field's revealed preference is to avoid the problem (serialise, or ground in a source) rather than solve it.
- **No commercial vendor has published a pipeline.** Every claim of "long-form consistency" from Writer, Jasper, Gamma, Notion, Sudowrite or Novelcrafter is unaccompanied by architecture or measurement. The engineering signal in this domain is almost entirely academic and open-source.

---

## Sources

- https://arxiv.org/abs/2402.14207 — STORM (NAACL 2024)
- https://github.com/stanford-oval/storm — STORM / Co-STORM code
- https://arxiv.org/abs/2406.10252 — AutoSurvey (NeurIPS 2024)
- https://proceedings.neurips.cc/paper_files/paper/2024/file/d07a9fc7da2e2ec0574c38d5f504d105-Paper-Conference.pdf
- https://arxiv.org/abs/2503.04629 — SurveyForge (ACL 2025)
- https://github.com/InternScience/SurveyForge
- https://arxiv.org/abs/2408.07055 — LongWriter / AgentWrite (ICLR 2025)
- https://github.com/THUDM/LongWriter
- https://aclanthology.org/2022.emnlp-main.296/ — Re3 (EMNLP 2022)
- https://github.com/yangkevin2/emnlp22-re3-story-generation
- https://arxiv.org/abs/2503.08275 — WriteHERE
- https://arxiv.org/abs/2506.16445 — StoryWriter
- https://arxiv.org/abs/2410.06203 — Integrating Planning into Single-Turn Long-Form Text Generation (Google)
- https://www.langchain.com/blog/open-deep-research
- https://github.com/langchain-ai/open_deep_research
- https://docs.gptr.dev/blog/gptr-langgraph — GPT-Researcher multi-agent
- https://github.com/assafelovic/gpt-researcher
- https://www.anthropic.com/engineering/multi-agent-research-system
- https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/
- https://sakana.ai/ai-scientist/
- https://arxiv.org/abs/2502.14297 — independent evaluation of the AI Scientist
- https://research.google/blog/learn-your-way-reimagining-textbooks-with-generative-ai/
- https://arxiv.org/abs/2605.17064 — LongPage / book-writing model
- https://arxiv.org/abs/2508.19611 — Instructional Agents
- https://hyan-yao.github.io/instructional_agents_homepage/
- https://github.com/huggingface/blog/blob/main/cosmopedia.md
- https://ought.org/updates/2022-04-08-elicit-plan
- https://elicit.com/blog/systematic-review-for-prisma-2020
- https://github.com/guerra2fernando/libriscribe
- https://docs.sudowrite.com/using-sudowrite/1ow1qkGqof9rtcyGnrWUBS/chapter-continuity/4KL8gFeLZQ6GSBjDWtSbV6
- https://www.novelcrafter.com/features/codex
- https://support.khanacademy.org/hc/en-us/articles/20349258135181-How-does-Khan-Academy-use-AI-in-our-content-development-process
- https://www.oreilly.com/about/oreilly-approach-to-generative-ai.html
- https://buildwithfern.com/post/how-to-write-llm-friendly-documentation
- https://writer.com/blog/writer-ai-hq-press-release/ — marketing, no mechanism
