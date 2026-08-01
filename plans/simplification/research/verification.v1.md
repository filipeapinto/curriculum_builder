# Verifying LLM-Generated Long Documents

## The checking layer: global consistency, factual grounding, and automated enforcement

Research compiled 2026-07-31. Evidence strength is labelled per claim.

**Evidence strength key**

- **[A] Strong** — peer-reviewed venue (ACL/EMNLP/NAACL/TACL/Nature Medicine), explicit numbers, method reproducible or repo public.
- **[B] Moderate** — arXiv preprint with explicit numbers and a stated method; single study, not independently replicated.
- **[C] Weak** — vendor blog, secondary reporting, or a claim without accessible numbers. Treat as a pointer, not a finding.

A general caveat: many of the strongest-looking 2026 preprints below were read via automated PDF/HTML extraction. Where a number is load-bearing for a design decision, re-read the table in the original. One paper (§2.1, *Lost in Stories*) contains an internal inconsistency I flag explicitly.

---

# 0. Headline findings

1. **Schema validation and semantic correctness are nearly uncorrelated.** One study measured 100% schema validity alongside **2.0% semantic success** on the same outputs. Schema validity is not a reliability metric. **[B]**
2. **LLM judge panels do not buy independence.** A 9-judge cross-family panel was measured at **2.18 effective independent votes** (24.2% of nominal). The best single judge beat every aggregation method on 3 of 4 datasets. **[B]**
3. **The best automatic attribution checkers sit around 74–80% balanced accuracy** — i.e. roughly a 1-in-5 error rate on the question "is this claim supported by this source." That is the ceiling on any "let a model check the citation" design. **[A]**
4. **Citation hallucination is not a solved problem and is not fixed by retrieval.** A 2.2M-citation study measured per-model fabrication rates from **14.23% to 94.93%**. **[B]**
5. **Citation *verifiers* have a base-rate problem that is worse than their recall problem.** At a realistic ~2% fabrication prevalence, verifier precision ranges from ~3% to ~18% — i.e. **5 to 39 false alarms per true catch**. **[B]**
6. **Programmatic verifiers beat LLM judges by 1.2×–7× where a deterministic check exists.** The design lesson is to convert as many checks as possible from judgment into computation. **[B]**
7. **There is exactly one clean published answer to "make an unsourceable value a hard stop": Proof-Carrying Numbers** — fail-closed verification in the *renderer*, not the model. It is a formal proposal with proved properties but **no empirical evaluation**. **[B, theory only]**

---

# 1. Question 1 — What schema validation catches, and what it structurally cannot

## 1.1 What constrained decoding actually guarantees

Constrained decoding (XGrammar, Outlines, llguidance, vendor "JSON mode") works by masking tokens during generation so the model *cannot* emit a string outside the grammar. XGrammar states the guarantee plainly: constrained decoding ensures **"100% structural correctness of the output"** and supports general context-free grammars — JSON, regex, custom CFGs. `https://github.com/mlc-ai/xgrammar` **[A — verifiable by inspecting the repo]**

The important architectural distinction, worth keeping straight:

| Layer | Tools | When it acts | What it guarantees |
|---|---|---|---|
| Constrained decoding | XGrammar, Outlines, llguidance (used by vLLM, SGLang) | *During* token generation | Output is in the grammar. Malformed output is physically unreachable. |
| Post-hoc validation + retry | Instructor (11K+ stars, 3M+ monthly downloads), Pydantic-AI, BAML | *After* generation | Output parses into the model; failures trigger a retry with validation feedback. |

Source: `https://techsy.io/en/blog/best-llm-structured-output-libraries` **[C]**, corroborated by the XGrammar and Instructor repos **[A]**.

So the catch list is: **malformed JSON, missing required fields, wrong primitive types, values outside enums, values outside declared numeric ranges, string pattern violations, and array cardinality violations.** With Pydantic custom validators (`@field_validator`, `@model_validator`) you additionally get **arbitrary intra-document Python checks** — cross-field consistency within one object, referential integrity within one payload, unit checks, checksum checks. That last category is underrated and is the boundary of what "schema validation" can be stretched to cover.

## 1.2 The measured gap between valid and correct

The sharpest available evidence is *When JSON Is Not Enough: Semantic Reliability of Schema-Constrained LLM Ordering Agents* (`https://arxiv.org/html/2607.18261v1`) **[B]**. It runs schema-constrained ordering agents and separates schema validity from semantic success:

| Model | Schema validity | Semantic success (prompt-only / JSON-schema) | Unsafe acceptances |
|---|---|---|---|
| GPT-OSS 120B-fast | 100% | 83.0% / 81.3% | — |
| Qwen3-30B-A3B | 100% | 31.3% / 30.7% | ~15% |
| Gemma-2-2B | 100% | — / **2.0%** | **41.7%** |

Aggregate across all cases: **16.1% unsafe acceptances and 16.2% catalog errors, at 100% schema validity.** The failures were: accepting orders that contradict a stated allergy, inventing modifiers not in the catalog, mis-distributing modifiers across items, and accepting non-vegan items where vegan was required.

The paper's conclusion is the one to carry forward:

> "Schema validity alone is not a sufficient reliability metric."
>
> "Structured output is a necessary interface layer, not a substitute for domain verification and fail-closed execution."

Note the direction of the JSON-schema effect: it is **flat to slightly negative** on semantics (83.0 → 81.3, 31.3 → 30.7). Constraining the form did not improve the content, and in the weakest model it coincided with catastrophic semantic collapse.

## 1.3 Constrained decoding can actively cost you reasoning quality

*Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models* (EMNLP 2024 Industry Track, Appier AI Research / NTU, `https://arxiv.org/abs/2408.02442`) **[A]** found a significant decline in reasoning ability under format restriction, with stricter constraints producing greater degradation. Strict JSON mode degrades reasoning tasks partly by forcing **output misordering** — the model must emit a conclusion field before it has "written" the reasoning that supports it.

The split is task-dependent: rigid formats **hurt** reasoning-heavy tasks (math, multi-hop QA) and **help** classification-shaped tasks (slot filling, intent detection).

Design consequence: if a document pipeline forces reasoning-bearing generation through a tight schema, it may be paying for structure with correctness. The mitigation is ordering — free-text reasoning field first, structured conclusions after — not abandoning schemas.

## 1.4 The three things schema validation structurally MISSES

This is the direct answer to the question asked.

### (a) Cross-document / cross-section derivation — MISSED, categorically

A JSON Schema validates one instance against one schema. It has no access to a second document, so it cannot express "field `X` in section 12 must equal field `X` in section 3", "this total must equal the sum of the line items in a *different* file", or "this claim must not contradict a claim made 40,000 tokens earlier."

This is not an implementation gap; it is what the formalism is. JSON Schema's `$ref`/`$id` resolve *schema* references, not *data* references across instances. Any cross-instance constraint has to live outside the schema layer — in a canonical fact store, a knowledge graph, or a validator with access to both documents (§2).

Empirically, this class of error is exactly where long-document systems fail. *Lost in Stories* (§2.1) finds contradiction rates rising with length; RefusalBench (§4.2) finds refusal accuracy collapsing from 73.0% single-document to 36.1% multi-document for the same model. Cross-document is where the difficulty lives, and it is precisely the region the schema layer does not see.

### (b) Truth of a cited source — MISSED, categorically

A schema can require `{"citation": {"doi": "...", "url": "..."}}` and enforce that the DOI matches `^10\.\d{4,9}/`. It cannot determine that the DOI resolves, that the resolved paper exists, that the paper says what the sentence claims, or that the paper is a primary rather than secondary source.

All four are separate verification problems, each with its own error rate (§3). The schema layer's contribution here is *shape only* — and shape is what makes a fabricated citation look legitimate. A well-formed fake DOI passes every syntactic check.

### (c) Binary asset provenance — MISSED, categorically

A schema can assert that a manifest entry has `{"path": "...", "sha256": "...", "type": "diagram"}`. It cannot assert that the file at `path` exists, that its hash matches, that it depicts what the caption says, or that it was derived from the data it claims to plot.

Only the first two of those are even mechanically checkable, and they need a filesystem walk plus a hash computation — a validator with I/O, not a schema. The last two (does this figure depict this claim; was this figure derived from this data) are open research problems. See §5 for the state of the art, which is genuinely weak.

**Additional classes worth naming that also fall outside the schema layer:** unit/dimensional errors that stay in range; plausible-but-wrong values inside a valid enum; omission (a schema with an optional field cannot detect that the field *should* have been populated); and semantic scope errors — the *Ordering Agents* paper's "scope splitting", where each field is individually valid but their combination means something different from what was requested.

---

# 2. Question 2 — State of the art for "was document A actually derived from data B?"

Short answer: **there is no general solution, and the field is split into four partial approaches that do not compose cleanly.** Ranked from most to least trustworthy:

## 2.0 The four approaches

| Approach | Mechanism | Strength | Where it breaks |
|---|---|---|---|
| **Cryptographic provenance** | Hash/sign the artifact chain (C2PA, W3C PROV) | Tamper-*evident*, deterministic | Proves *lineage*, not *correctness*. Stripped easily. |
| **Deterministic recomputation** | Recompute the derived value from source, compare | Sound, cheap, exact | Only works where derivation is a computable function |
| **Entailment / NLI checking** | Model checks "does B support claim in A" | Broad coverage, works on prose | ~74–80% balanced accuracy ceiling (§3.3) |
| **Trace/lineage logging** | Record what was retrieved and used at generation time | Explains *how*, enables audit | Self-reported by the generator; not adversarially sound |

### 2.0.1 Deterministic recomputation is the strongest and most under-used

*Aggregating LLM-Based Weak Verifiers for Spatial Layout Generation* (`https://arxiv.org/pdf/2606.05268`) reports that **programmatic weak verifiers outperform LLM judges by at least 1.2× and up to 7×** across aggregation methods, and that "LLM judges often incorrectly accept outputs that violate explicit requirements, while strong programmatic verifiers correctly identify these violations." **[B]**

The general principle from the deterministic-vs-LLM-evaluator literature: deterministic verification "returns the same verdict every time, names the exact rule that produced it, and is cheap and fast enough to run on every output", where LLM judges are probabilistic and give different verdicts on re-run. `https://cogniswitch.ai/guides/llm-as-a-judge-vs-deterministic-verification` **[C]**

Practical implication for a derivation check: **every derivation that can be expressed as a function should be re-executed rather than reviewed.** Sums, ratios, unit conversions, date arithmetic, lookups against a source table, count-of-items — all of these are recomputation problems being wastefully handed to judges.

### 2.0.2 Where recomputation is deployed commercially

Financial statement "tie-out" is the most mature commercial instance of exactly this problem — verifying that every number in a report matches its source. Workiva's Tie-Out Agent "automates consistency checks across financial documents, flags every discrepancy it finds, and generates AI-produced explanations for each variance" (reported 2026-07-31, `https://www.techtimes.com/articles/322387/20260731/workiva-embeds-ai-financial-close-agents-check-numbers-draft-esg-reports.htm`) **[C — vendor-sourced, no independent numbers]**. Suralink and DataSnipper ship comparable products. The framing is instructive: a single 10-K contains thousands of data points repeated across footnotes, tables and commentary, and tie-out is days of manual work per filing.

The evaluation methodology from *FinSheet-Bench* (`https://arxiv.org/html/2603.07316v1`) is worth stealing: a **three-tier cascading verification** — strict rule-based extraction first, then regex numeric extraction compared at **2.5% relative tolerance**, then LLM adjudication only for what survives. Cheap deterministic checks first, expensive judgment last, and only on the residue. **[B]**

### 2.0.3 Formal provenance models

W3C PROV-DM supplies the vocabulary — entities, activities, agents, and **derivation relations**. The survey *From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents* (`https://arxiv.org/html/2606.04990v3`) specialises PROV for LLM agents, adding retrieved chunks, tool arguments, memory writes, inter-agent messages, generated claims, and external state changes as first-class provenance objects. Its central claim: "provenance's relational structure is what allows it to support verification, attribution, debugging, safety enforcement, audit, and recovery." **[B]**

The honest limitation: PROV records *what the pipeline says it did*. It is an audit and debugging substrate, not a correctness proof. A generator that hallucinates while a correct chunk sits in its context produces a perfect provenance record for a wrong claim.

### 2.0.4 Requirements traceability — the closest mature analogue

Safety-critical engineering has done "document A must be traceable to artifact B" for decades via the Requirements Traceability Matrix, mandated for certification under **DO-178C** (FAA/EASA/Transport Canada airborne software) and **NASA-STD-8739.8**. **[A — standards documents]**

LLM-based automation of trace-link recovery is active: *Leveraging Graph-RAG and Prompt Engineering to Enhance LLM-Based Automated Requirement Traceability and Compliance Checks* (`https://arxiv.org/pdf/2412.08593`) and *Automated Trace Link Recovery Between Natural Language Requirements and Formal Specifications via LLMs* (Springer, `https://link.springer.com/chapter/10.1007/978-3-032-30693-7_1`) report LLM methods beating LSI, VSM, and Word2Vec on precision/recall/F1. **[B]**

Critically, **the deployed pattern is semi-automated**: the LLM proposes candidate links, a human validates, and validated links are stored in a graph database for version-aware navigation. Nobody in the certification world lets the model close the loop. That is the honest state of the art for derivation checking in a regulated setting.

## 2.1 Cross-section consistency: how systems stop chapter 12 contradicting chapter 3

### Named techniques, with measured effect

**Temporal knowledge graphs as canonical fact store.** DOME (*Generating Long-form Story Using Dynamic Hierarchical Outlining with Memory-Enhancement*, NAACL 2025, `https://aclanthology.org/2025.naacl-long.63.pdf`) stores generated content as quadruples `<subject, action, object, chapter_index>` and retrieves by entity plus LLM semantic filtering. **[A]**

Measured results:

- Conflict rate **4.52% → 0.56%** when the memory module is added — an **87.61% reduction** vs. the no-memory ablation.
- vs. prior SOTA (DOC): **0.56% vs 1.21%** conflict rate, ~54% better.
- Entropy-2 diversity 12.29 vs 11.55 (+6.3%) — consistency did not cost diversity.
- Cost: ~791 storage nodes and **16 extra LLM calls** per ~7,100-word story. Cheap.

That cost figure is the useful one. An explicit fact store bought a 8× conflict reduction for 16 calls.

**Time-aware validity intervals.** FACTTRACK (`https://arxiv.org/abs/2407.16347`) decomposes events into atomic facts, assigns each a **validity interval** so facts may legitimately change over time, detects contradictions against the interval-aware world state, and updates. **[B]**

Results: with LLaMA2-7B-Chat, FACTTRACK "substantially outperforms a fair baseline using LLaMA2-7B-Chat, and achieves performance comparable to a GPT-4 baseline"; with GPT-4 it "significantly outperforms the GPT-4 baseline." Structure substituted for scale — a 7B model with a world-state tracker matched a GPT-4 baseline without one. The paper reports comparative direction more than absolute numbers, which weakens it.

The validity-interval idea is the conceptually important one and generalises well beyond fiction. "Fact F was true as of section 3 and legitimately changed by section 12" is not a contradiction; naive fact-store checking flags it as one. Any real consistency checker over a document with versioning or staged content needs this.

**Narrative/world-state memory and KG-guided generation.** Related: *Narrative World Model* (`https://arxiv.org/pdf/2607.05577`), *Long Story Generation via Knowledge Graph and Literary Theory* (`https://arxiv.org/pdf/2508.03137`) with its narrative entity knowledge graph, and *Guiding Generative Storytelling with Knowledge Graphs* (Taylor & Francis, `https://www.tandfonline.com/doi/full/10.1080/10447318.2025.2603634`). Consistent direction of finding, thinner individual numbers. **[B]**

### How bad is the problem, measured

*Lost in Stories: Consistency Bugs in Long Story Generation by LLMs* (`https://arxiv.org/html/2603.05890v1`) **[B]** gives the best current taxonomy — **5 categories, 19 fine-grained subtypes**:

1. **Timeline & Plot Logic** (6): absolute time, duration, simultaneity, causeless effects, causal violations, abandoned elements
2. **Characterization** (4): memory, knowledge, skill fluctuation, forgotten abilities
3. **World-building & Setting** (3): core rule violations, social norms, geography
4. **Factual & Detail Consistency** (3): appearance mismatch, nomenclature confusion, **quantitative mismatch**
5. **Narrative & Style** (3): perspective confusion, tone, style shift

Measured error density (errors per 10,000 words):

| Model | Errors / 10K words |
|---|---|
| GPT-5-Reasoning | 0.113 |
| Gemini-2.5-Pro | 0.305 |
| Claude-Sonnet-4.5 | 0.520 |
| Qwen3-32B | 0.537 |
| MiniMax-M1-80k | 3.447 |

A **30× spread across models.** Model choice is a larger lever on consistency than most checking machinery.

**The detection result, with a caveat.** ConStory-Checker (their automated 5-dimension pipeline) reportedly achieves **Overall F1 = 0.678**, detecting **550 of 1,000 injected errors (55.0% recall)** vs. **171 (17.1% recall)** for two professional web-novel writers annotating the same material — a 3.2× improvement in discovery rate, with humans showing higher precision (0.660) and far lower recall (0.139).

Three caveats, and they matter:

- The paper is internally inconsistent: prose states human Overall F1 = 0.281 while Table 6 gives 0.229. **Verify before citing.**
- These are **injected** errors. Injected errors are systematically easier than naturally-occurring ones — they are discrete, local, and drawn from a known taxonomy. Recall on organic inconsistency will be lower.
- The human baseline is 2 annotators. "Beats human experts" on n=2 with 17% recall says more about how tedious the task is than about superhuman capability. The right reading is *humans are terrible at this*, not *machines are good at it*.

### Why long-context alone does not solve it

*Deep Research Bench II* (`https://arxiv.org/pdf/2601.08536`) attributes cross-section failures to **"attention dilution"** and the **"lost-in-the-middle"** phenomenon: models "fail to detect subtle contradictions or verify cross-sectional factual consistency" as context grows. Even the strongest agents pass **under 50% of rubrics**, with the largest deficits in Information Recall and Analysis. **[B]**

Its report-level metric **Factual & Logical Consistency (FLC)** — detect factual/logical contradictions, map issue count to a discrete score — is a reasonable off-the-shelf formulation.

Hard numbers on judge degradation with length, from the long-context QA literature: an LLM-judgment baseline **drops from 75% at 64K context to 61% at 262K** — a 14-point fall — while the gap versus a stronger method widens from +8pp at 6K to +21pp at 262K. `https://arxiv.org/pdf/2502.06329` **[B]**

**This is the central architectural finding of the section.** Feeding the whole document to a long-context model and asking "is this consistent?" degrades exactly where you need it. Structured extraction into a fact store, then pairwise checking, does not — DOME's approach costs 16 calls and does not care how long the document is.

### The theoretical ceiling on global consistency

*Foundations of Global Consistency Checking with Noisy LLM Oracles* (`https://arxiv.org/html/2601.13600`) **[B]** makes the point that most pipelines miss: checking each claim individually against sources does **not** give you a jointly coherent set. A set of individually-supported facts can still be mutually contradictory. Global consistency is **computationally intractable in general**; it becomes viable only when conflict sets are small or the structure is regular, formalised as querying a **noisy subset-consistency oracle** instantiated by an LLM judge.

Two consequences: (1) you cannot check all pairs at scale, so you need structure to prune, and (2) the oracle doing the pruning is itself noisy, at the rates in §4.

Complementary empirical work: *Contradiction Detection in RAG Systems* (`https://arxiv.org/abs/2504.00180`) on LLMs as context validators, and *Discovering Inconsistencies in Documents with Long-Context LLMs* (Springer, `https://link.springer.com/chapter/10.1007/978-3-031-94931-9_9`), which finds that **targeted structuring of document context improves recall** in inconsistency detection — again pointing at structure over raw context.

---

# 3. Factual grounding to primary sources

## 3.1 The AIS framework — the definitional foundation

**AIS (Attributable to Identified Sources)**, Rashkin et al., *Computational Linguistics* 49(4), 2023 — `https://aclanthology.org/2023.cl-4.2/`, data at `https://github.com/google-research-datasets/AIS`. **[A]**

Definition: NLG output pertaining to the external world must be verifiable against an independent, provided source. Empirically validated via human evaluation across three task types (two conversational QA sets, a summarisation set, a table-to-text set), with released annotations over CNN/DM, QReCC, Wizard of Wikipedia, and ToTTo.

**AutoAIS** is the automated estimator, typically an NLI model. This is the reference point everything else in this section is measured against.

## 3.2 How hard is automatic attribution? — AttributionBench

*AttributionBench: How Hard is Automatic Attribution Evaluation?* (Findings of ACL 2024, `https://aclanthology.org/2024.findings-acl.886.pdf`, arXiv `2402.15089`). **[A]**

The headline number is the one to internalise:

> "Even a fine-tuned GPT-3.5 only achieves around **80% macro-F1** under a binary classification formulation."

Binary. Supported vs. not supported. Fine-tuned. 80%.

Failure analysis: "a majority of failures stem from the model's inability to process nuanced information, and the discrepancy between the information the model has access to and that human annotators do."

That second clause is the underappreciated one — a large share of "errors" are the checker not having what the human had. In a document pipeline this maps directly to: the verifier sees a retrieved chunk, the human sees the whole paper.

## 3.3 The current ceiling — MiniCheck and LLM-AggreFact

*MiniCheck: Efficient Fact-Checking of LLMs on Grounding Documents* (EMNLP 2024, `https://aclanthology.org/2024.emnlp-main.499.pdf`, repo `https://github.com/Liyan06/MiniCheck`). **[A — repo inspectable]**

Task: given a claim and a grounding document, is the claim supported? Benchmark **LLM-AggreFact** aggregates 10 datasets across news, dialogue, science, healthcare.

Balanced accuracy on LLM-AggreFact:

| System | Params | Balanced acc. | Cost (13K checks) |
|---|---|---|---|
| GPT-4 | — | **75.3%** | $107 |
| **MiniCheck-FT5** | 770M | **74.7%** | **$0.24** |
| Claude-3 Opus | — | 74.1% | — |
| AlignScore | 355M | 70.4% | $0.20 |
| GPT-3.5 | — | 69.6% | — |
| DAE | — | 64.9% | — |
| SummaC-CV | — | 62.1% | — |
| T5-NLI-Mixed | — | 61.0% | — |

Per-dataset for MiniCheck-FT5: AggreFact 69.9, TofuEval 74.3, Wice 73.6, Reveal 77.3, ClaimVerify 72.2, FactCheck-GPT 86.2, ExpertQA 74.6, Lfqa 74.7.

Three things follow.

1. **~75% balanced accuracy is the state of the art for automated grounding checks.** Not 95%. A quarter of verdicts are wrong on a *binary* task with the source document supplied. Any pipeline that treats a grounding check as authoritative is building on a 25% error rate.
2. **A 770M model matches GPT-4 at 1/400th the cost.** This is the single most actionable engineering fact in this report — grounding checks should be run by a small specialist model on *every* claim, not by a frontier model on a sample.
3. **Atomic-fact decomposition is not necessary** for high performance, per the paper. That contradicts a common pipeline assumption and saves a decomposition stage.

Also notable: MiniCheck-FT5 was trained on **35K** synthetic examples vs. AlignScore's **4.7M** and still beat it by 4.3pp. Targeted synthetic data on realistic error modes outperformed volume.

## 3.4 Long-form factuality — SAFE

*Long-form factuality in large language models* (DeepMind, `https://arxiv.org/abs/2403.18802`). SAFE decomposes generated text into individual facts and resolves each via multi-step Google Search reasoning. Benchmark **LongFact**: thousands of fact-seeking prompts across 38 topics; 13 models across Gemini/GPT/Claude/PaLM-2. **[A]**

Numbers, and how to read them:

- SAFE matched human crowdworker ratings on **72%** of ~16,000 individual facts.
- On a sample of **100 disagreements**, SAFE was judged correct in **76%** of cases.
- **20× cheaper** than human annotation.

The "superhuman" framing in press coverage (`https://venturebeat.com/ai/google-deepmind-unveils-superhuman-ai-system-that-excels-in-fact-checking`) **[C]** overstates it. The comparison is against **crowdworkers**, not domain experts, and the 76% figure comes from adjudicating 100 disagreements. The defensible claim is: SAFE is cheaper than and roughly comparable to non-expert human annotation. It is not a substitute for expert review of safety-relevant content.

## 3.5 Citation fabrication rates — the numbers

Rates vary enormously by study, model, domain and prompt. Reported honestly, that variance *is* the finding.

**GhostCite** (`https://arxiv.org/html/2602.06718v1`) is the largest: **2.2M citations from 56,381 papers** across NeurIPS, ICML, IJCAI, AAAI, IEEE S&P, USENIX Security, CCS, NDSS (2020–2025), plus **375,440 generated citations** from 13 models across 40 CS domains. **[B]**

- **All models hallucinate.** Range **14.23% to 94.93%**.
- DeepSeek 14.23% (best), Claude-4 21.84%, Qwen-3 23.52%, GPT-5 50.92%, Hunyuan 94.93% (worst).
- Domain sensitivity spans **51.39 percentage points**: Computation and Language 28.80% → Digital Libraries 80.19%.
- Archival: **1.07% of published papers (604/56,381) contained invalid citations**, with an **80.9% surge in 2025** over the 2020–2024 average. One erroneous reference propagated into **16 separate papers**.
- Human process data: **41.5% of researchers copy-paste citations without checking; 76.7% of reviewers don't thoroughly verify references.**

Method: structured parsing → cascaded verification against local databases, academic indexes, and web search → similarity classification via **Levenshtein distance at a 0.9 threshold**.

Corroborating ranges from other studies **[B/C]**, showing the spread:

- 39.6% (GPT-3.5), 28.6% (GPT-4), 91.4% (Bard) for systematic-review references — `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11153973/` **[A — peer-reviewed]**
- 47% (GPT-4) to 77% (Llama 2 7B) for CS reference titles
- 11.4%–56.8% in a cross-model audit, "strongly shaped by model, domain, and prompt framing" — `https://arxiv.org/pdf/2603.03299`
- Mean 34% across 1,200 answers, range 12–68%

**The honest summary: order-of-magnitude 10–50% for frontier models on unaided citation generation, heavily domain-dependent, with pathological outliers above 90%.** Do not quote a single number.

## 3.6 Citation *verifiers* fail in three specific ways — HALLMARK

*HALLMARK: Diagnosing Three Failure Modes in LLM Citation Verifiers* (`https://arxiv.org/html/2607.18360`). **[B — but the most operationally useful paper in this report]**

**Failure mode 1 — agentic lookup inflates false positives.** Prompted models flag an entry as soon as *any single database* returns no match, rather than requiring consensus. Because CrossRef, OpenAlex and arXiv have non-overlapping coverage, **"single-source absence gets read as fabrication."**

- 5-call budget lifts detection rate to **0.97–0.99** vs. rule-based reference **0.87** —
- but inflates false-positive rate **~5×: 0.43–0.48 vs. 0.09**.
- GPT-5.1 + CrossRef/OpenAlex/arXiv: DR 0.967, FPR 0.478. Sonnet 4.6 + agentic bibtex-updater: DR 0.990, FPR 0.431.

**Failure mode 2 — the base-rate problem. This is the important one.** At venue-realistic **~2% fabrication prevalence**, precision, not recall, decides deployability:

- FPR spans **0.050 to 0.702** across verifiers — a ~7× gap.
- At 2% prevalence, PPV ranges from **1-in-6 to 1-in-39** flags being true positives.
- Low-FPR tools (Opus 4.7, Sonnet 4.6): PPV ~18%. High-FPR open-weight models: PPV ~3%.

> "The false-positive rate, not recall, decides whether a verifier is deployable."

A verifier at 3% PPV produces 32 false alarms per real catch. Reviewers stop reading it within a day. **Any hard-stop gate must be tuned on FPR at the true base rate, not on recall.**

**Failure mode 3 — post-cutoff calibration collapse.** On a 2024–2025 supplement (n=448), **8 of 12 models degrade sharply (FPR 0.59–0.89)**. GPT-5.1 (Jan 2025 cutoff) jumps to **FPR 0.693** on post-cutoff papers. Only latest-cutoff models hold: Sonnet 4.6 FPR 0.12, Opus 4.7 FPR 0.07. Mechanism: "flag everything unfamiliar." The paper honestly notes this is confounded with possible memorisation.

**Implication: a model's parametric knowledge must never be the citation oracle. Only external resolution counts.** And verifier choice must track training cutoff relative to the corpus being checked.

## 3.7 Inspectable citation-verification repos

All of these resolve references against external bibliographic databases — the correct architecture per §3.6. **[A — repos are public and inspectable]**

| Tool | URL | Sources checked |
|---|---|---|
| **RefChecker** (Mark Russinovich) | `https://github.com/markrussinovich/refchecker` | Semantic Scholar, OpenAlex, CrossRef, DBLP, ACL Anthology + LLM deep web search; single/bulk/whole-venue OpenReview scanning |
| **llm-citation-verifier** | `https://github.com/DWFlanagan/llm-citation-verifier` | Crossref DOI, real-time, flags fake DOIs; ships as an `llm` plugin |
| **hallucinator** | `https://github.com/gianlucasb/hallucinator` | Extracts refs from PDF, checks CrossRef/arXiv/DBLP/OpenAlex |
| **References-Validation / CheckIfExist** | `https://github.com/zabbonat/References-Validation` | PDF & DOCX batch; **exposed over MCP** — usable directly from Claude Desktop / VS Code |
| **CiteVerifier** | `https://github.com/NKU-AOSP-Lab/CiteVerifier` | Cascaded multi-source: local index → academic DBs → web search |
| **AutoCitation** | `https://github.com/sypsyp97/AutoCitation` | Agent that finds real citations for existing content |

Reported detector performance from the surrounding literature: CiteCheck **88.7 macro-F1 / 88.9% accuracy** (`https://arxiv.org/html/2605.27700v1`) **[B]**; CiteAudit 97% on generated benchmarks but **90% on real-world cases** **[B]**; general-purpose LLMs 48–91% detection with a pronounced recall–precision tradeoff. Read all of these against §3.6's base-rate warning — accuracy on a balanced benchmark tells you almost nothing about precision at 2% prevalence.

**The RefChecker + CheckIfExist(MCP) combination is the most directly usable thing in this report for a document pipeline.** Existence checking against 4–5 databases is cheap, deterministic, and catches the single largest error class.

---

# 4. Question 3 — How reliable is a model reviewing another model's output?

## 4.1 The optimistic baseline, and why it is misleading

The widely-cited figure is that strong models achieve **over 80% agreement with human preferences** on multi-turn conversation (MT-Bench/Chatbot Arena lineage) — comparable to human-human agreement. **[A]**

This number gets over-extended. It is for **subjective preference on conversational quality**. It does not transfer to factual verification, cross-section consistency, or technical correctness — where the measured numbers are much worse (§4.3, §4.5).

## 4.2 Bias taxonomy, quantified — CALM

*Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge* (`https://llm-judge-bias.github.io/`) **[B]**. 12 bias types — Position, Verbosity, Compassion-Fade, Bandwagon, Distraction, Fallacy-Oversight, Authority, Sentiment, Chain-of-Thought, Self-Enhancement, Refinement-Aware, Diversity — across ChatGPT, GPT-4-Turbo, GPT-4o, GLM-4, Claude-3.5, Qwen2.

Robustness rates (fact-related dataset): GPT-4o 0.977, Claude-3.5 0.952, GPT-4-Turbo 0.915, ChatGPT 0.900, GLM-4 0.887, Qwen2 0.884. Alignment dataset: Claude-3.5 0.985, GPT-4o 0.984, others 0.917–0.979.

**The weak spot is the one that matters for verification work:**

- **Fallacy-Oversight robustness: 0.566–0.832.** Models struggle to detect logical errors when the conclusion is correct.
- **Chain-of-Thought evaluation accuracy: 0.651–0.804.**

Read that carefully: **judges accept invalid reasoning that reaches a right answer.** For a document where a value must be *derived* correctly rather than merely *be* correct, this is the failure mode that a judge will systematically miss.

**Self-preference bias** is separately confirmed: GPT-4 "exhibits a significant degree of self-preference bias" measured via an Equal-Opportunity-style metric that controls for underlying completion quality using a third-party judge (`https://openreview.net/forum?id=Ns8zGZ0lmM`) **[B]**. Practical rule: **do not let the generating model family judge its own output.**

## 4.3 Panels do not fix it — the strongest single result here

Two papers pull in opposite directions. The pessimistic one has better methodology.

**The optimistic case — PoLL.** *Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models* (`https://arxiv.org/pdf/2404.18796`) **[B]**: a panel of smaller diverse models correlates better with human judgment than a single large judge across 3 judge settings and 6 datasets, at **>7× lower cost**, attributed to pooling across model families.

**The pessimistic case — and it is quantitative and specific.** *Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels* (`https://arxiv.org/html/2605.29800`) **[B]**.

9 judges across 7 families: GPT-4o (err 0.354), GPT-4o-mini (0.356), Claude Sonnet 4.5 (0.317), Gemini 2.5 Pro (0.324), Llama 4 Maverick (0.299), Llama 4 Scout (0.332), Qwen3-32B (0.282), Mistral Large 3 (0.338), DeepSeek-V3 (0.321).

**Effective independence:**

- **n_eff = 2.18** [95% CI 2.07–2.31] on MNLI. Independence ratio **24.2%** — **75.8% of nominal independence lost to correlated errors.**
- Mean pairwise φ̄ = **0.391** (σ 0.111). Eigenvalue cross-check n_eff = 2.16.
- Hard asymptote at **1/φ̄ ≈ 2.6**. No configuration of these models can exceed it.
- **First 5 judges deliver 90% of achievable independence (n_eff 1.96); judges 6–9 add only +0.22 effective votes.**

**Panels frequently lose to the best single judge:**

| Dataset | n_eff | Panel acc. | Best single judge | Panel lift |
|---|---|---|---|---|
| MNLI | 2.18 | 72.0% | 71.8% (Qwen3) | +0.2pp |
| SNLI | 2.35 | 77.7% | 84.2% (Claude) | **−6.5pp** |
| AlphaNLI | 2.48 | 88.7% | 91.2% | **−2.5pp** |

**Condorcet gap on MNLI: 22.0pp** [19.5–24.1] — actual 72% vs. 94% predicted under independence. Only 6.8% explained by shared item difficulty; ~93% is unexplained correlation. Permutation test **p < 10⁻⁴** (0 of 10,000).

**Correlated failure is visible in the error distribution:** 290 items (29%) correct by all 9 judges and **51 items (5.1%) wrong by all 9** — both vastly above the <<1% independence predicts. **"Over-prediction of contradiction accounts for 51% of all-wrong confusions."** Even on unanimous items, accuracy is 90.9% against the ~0.02% error rate independence would imply. **Unanimity is not evidence of correctness.**

**Aggregation cannot rescue it:** "even with oracle access to gold labels, the best stable method closes at most 11% of the gap across all four datasets." Majority vote 72.0%; Dawid-Skene EM 70.7% (worse); accuracy-weighted with oracle 72.2% (+0.2pp).

**Chain-of-thought makes it worse:** φ̄ rises to 0.456, n_eff falls to **1.94**. Shared reasoning amplifies shared errors.

**Humans are ~2× better:** human n_eff 4.0–5.8.

Recommended diagnostic: compute n_eff; **if n_eff/k < 0.5, treat results with caution.**

**Reconciling the two papers:** PoLL's claim is about *cost-efficiency and correlation with human preference*; Nine Judges is about *effective information content and accuracy on entailment*. Both can hold. The synthesis in the secondary literature — "adding multiple judges fixes bias, but only if they disagree on the right things" — is right, and Nine Judges shows that cross-family diversity does **not** deliver that (its three most-correlated pairs were all cross-family: Claude×Gemini φ=0.603, GPT-4o×Claude φ=0.588).

**Operational conclusion: budget for ~2 effective votes from any LLM panel, cap the panel at ~5, and never treat unanimity as verification.**

## 4.4 Judges are adversarially fragile

*LLMs Cannot Reliably Judge (Yet?)* (`https://arxiv.org/html/2506.09443`) **[B]**. 15 attacks across 12 judge models.

- Combined Attack (H6): **100% ASR** on Openchat-3.5, Qwen-2.5-7B, Mistral-7B. Fake Reasoning (H5) consistently **>80%**. Long-Suffix (H8) **100%** on Llama-3.3-70B.
- PAIR: 100% on Qwen-2.5-7B, 90% on Llama-3.1-8B. AdvEval 93.33% on Llama-3.3-70B.
- Average ASR: GPT-4o **71.26%** (strongest closed-source), JudgeLM-13B **69%** (lowest overall), Llama-3.3-70B 60.89%, DeepSeek-R1 **75.20%** despite reasoning specialisation.
- Machine translation: **all judges >90% ASR** under combined attack.
- Defences: re-tokenisation cuts ASR to 16.67% but degrades benign performance; LLM detectors reach 65.67% detection with overhead.

Adversarial framing matters less for a cooperative document pipeline — but "Fake Reasoning at >80% ASR" is *precisely* the non-adversarial failure a generator produces naturally when it writes confident, well-structured justification for a wrong value. The attack surface and the honest failure mode are the same surface.

## 4.5 Judges on technical and long content

- **Scientific comparative judgment: GPT-4o achieves 0.60 accuracy** — barely above chance on a binary task. From ReFACT (`https://arxiv.org/pdf/2509.25868`); the paper concludes "LLM-as-Judge paradigms may produce unreliable evaluations for factuality and reasoning tasks", particularly where domain expertise is required. **[B — I could not extract the full results tables; treat the 0.60 as needing confirmation]**
- **Length bias:** judges favour longer responses even when they contain errors, and "often fail to detect subtle factual inaccuracies, grading incorrect but fluent hallucinations as correct." **[B]**
- **Context-length degradation:** 75% → 61% from 64K to 262K (§2.1). **[B]**
- **Self-correction:** *When Can LLMs Actually Correct Their Own Mistakes?* (TACL, `https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00713/125177/`) and *Large Language Models Cannot Self-Correct Reasoning Yet* (`https://arxiv.org/abs/2310.01798`) **[A]**: intrinsic self-correction "does not improve or even degrades performance" on arithmetic reasoning, closed-book QA, code generation, plan generation and graph colouring. **Feedback generation is the bottleneck.** Self-correction works *only* when reliable external tools or knowledge supply the feedback.

## 4.6 Reliability summary table

| Verification task | Best measured performance | Source |
|---|---|---|
| Claim supported by given document | **74.7–75.3% bal. acc.** (MiniCheck-FT5 / GPT-4) | LLM-AggreFact **[A]** |
| Attribution, binary, fine-tuned | **~80% macro-F1** | AttributionBench **[A]** |
| Long-form fact checking vs. crowdworkers | **72% agreement**; 76% right on 100 disagreements | SAFE **[A]** |
| Injected story-consistency errors | **F1 0.678, 55% recall** | ConStory-Checker **[B]**, caveats §2.1 |
| Citation existence, 5-source agentic | **DR 0.97–0.99, FPR 0.43–0.48**; PPV ~3–18% @2% base rate | HALLMARK **[B]** |
| Detecting fallacious reasoning w/ correct conclusion | **0.566–0.832 robustness** | CALM **[B]** |
| Scientific comparative judgment | **~0.60 accuracy (near chance)** | ReFACT **[B]**, unconfirmed |
| Effective independent votes from 9 judges | **2.18** | Nine Judges **[B]** |
| Programmatic verifier vs. LLM judge | **1.2×–7× better** where computable | **[B]** |

**Headline: outside of deterministic recomputation, no automated verification method in the literature exceeds ~80% on a binary judgement. Design for a checking layer that is wrong 20–25% of the time.**

---

# 5. Question 4 — Systems that make an unsourceable fact a hard stop

Genuinely rare. Four categories, in descending order of rigour.

## 5.1 Proof-Carrying Numbers — the clean answer

*Proof-Carrying Numbers (PCN): A Protocol for Trustworthy Numeric Answers from LLMs via Claim Verification* (`https://arxiv.org/abs/2509.06902`, Sept 2025). **[B — formal, but explicitly no empirical evaluation]**

The mechanism, and its key architectural insight:

> "PCN places verification in the renderer, not the model: only claim-checked numbers are marked as verified, and all others **default to unverified**."

Numeric spans become **claim-bound tokens** verified against structured claims under explicit policies — exact equality, rounding, or tolerance ranges. Because verification happens at the **presentation layer**, the model cannot spoof it: a model that emits a "verified" marker does not thereby produce one.

Four proved properties:

1. **Soundness** — verified claims are trustworthy
2. **Completeness under honest tokens** — legitimate values pass
3. **Fail-closed behaviour** — unverified numbers render *without* verification marks
4. **Monotonicity under policy refinement** — stricter policies preserve verified status

The governing principle: **"trust is earned only by proof"**, and absence of marking itself communicates uncertainty — the *no unmarked defect* guarantee.

**Why this is the right shape for a hard stop.** PCN inverts the default. Standard pipelines are *fail-open*: output is assumed correct unless a checker objects, so a checker's false negative (at the 20–25% rates in §4) silently ships an error. PCN is *fail-closed*: a value is unverified unless proof exists, so a checker failure produces a **visible unverified marker**, not a silent falsehood. Given §4's error rates, fail-closed is the only defensible default.

**Evidence limitation, stated plainly:** the paper references evaluation contexts (World Bank data, medical sources) but the abstract and available text report **no empirical results**. This is a formal protocol proposal, not a validated system. The idea is sound and the guarantees are proved; the deployment evidence does not exist yet.

## 5.2 Citation-grounded / abstention architectures

The general pattern, from the applied literature **[C — practitioner sources, no controlled numbers]**: a citation-grounded system "enforces the link between every claim and a verifiable source, refuses to answer when the link cannot be made, and **treats unsupported claims as bugs**." Every claim carries a page/section/passage anchor; unsupported claims trigger refusal, not generation.

The research framing treats **abstention as a correct system action under insufficient evidence, rather than a generation failure** — with a final refusal boundary that stops related-but-insufficient evidence from being completed into unsupported claims.

**The structural obstacle, and it is a training-level one:** standard training "discourages abstention, as models are evaluated on accuracy metrics that reward correct answers and penalize wrong ones but do not distinguish between confident errors and acknowledged uncertainty, creating a training incentive toward confident guessing rather than honest abstention." You are fighting the objective function. This is why abstention must be enforced by *architecture* (a gate outside the model) rather than by *prompting*.

**RL for grounded abstention:** GRACE — *Reinforcement Learning for Grounded Response and Abstention under Contextual Evidence* (`https://arxiv.org/html/2601.04525v1`) trains the behaviour directly. **[B]**

## 5.3 How well does refusal actually work? — RefusalBench

*RefusalBench: Generative Evaluation of Selective Refusal in Grounded Language Models* (`https://arxiv.org/html/2510.10390v1`) **[B]**. This is the reality check on §5.2.

Taxonomy of informational uncertainty — 6 categories × 3 intensity levels × 176 perturbation strategies: **P-Ambiguity, P-Contradiction, P-MissingInfo, P-FalsePremise, P-GranularityMismatch, P-EpistemicMismatch**.

Results:

- Single-document (RefusalBench-NQ): best refusal accuracy **73.0%** (Claude-4-Sonnet).
- Multi-document (RefusalBench-GaRAGe): **"drops catastrophically."** Best is DeepSeek-R1 at **47.4%**. Claude-4-Sonnet falls **73.0% → 36.1%**.
- **"No frontier model achieves excellence (>80%) on both dimensions simultaneously"** (answering and refusing).
- **Scaling does not help:** "answer and refusal capabilities scale independently."
- **Reasoning does not help:** up to 4096 thinking tokens yields **<1pp** improvement in refusal accuracy.
- **Severe miscalibration:** ">73% of predictions occur at maximum confidence despite 40–69% accuracy." Models are maximally confident while being roughly coin-flip accurate.
- Models default to `REFUSE_INFO_MISSING` as a catch-all — 25% of all predictions on NQ.

The paper's constructive finding: refusal is "a trainable, alignment-sensitive capability" — improvable by targeted alignment, not by scale.

**Combined reading of §5.2 and §5.3: model-mediated abstention is unreliable — a 36–47% multi-document refusal accuracy is not a gate. A hard stop must be enforced by a deterministic gate outside the model (PCN's renderer-level check), not by asking the model to refuse.**

## 5.4 Safety-relevant technical domains

**Aerospace / space software.** DO-178C and NASA-STD-8739.8 mandate requirements traceability for certification. These are genuine hard stops — non-traceable requirements block certification — but they are **process controls with human sign-off**, predating and not currently delegated to LLMs. **[A]**

**Clinical.** The strongest activity is here.

- **TRIPOD-LLM** (*Nature Medicine*, `https://www.nature.com/articles/s41591-024-03425-5`) is the reporting guideline for LLM studies, and is positioned to inform regulatory compliance under the EU AI Act. Reporting standard, not an automated gate. **[A]**
- The gap is stated precisely in the T2D-Bench framing: RAG approaches "ground LLM outputs by retrieving guideline text, but **they do not consistently encode guideline logic as computable constraints that can verify whether an output satisfies required conditions or should be revised when support is missing**." **[B]** That sentence is the best single articulation of what is missing across this entire field: retrieval provides *material*, not *enforcement*.
- **T2D-Bench** (`https://arxiv.org/pdf/2606.24145`) is explicitly "Evidence-Gated Evaluation ... Using a Multi-Layer Clinical-Lifestyle Knowledge Graph", repo at `https://github.com/Saba-Farahani/t2d-bench-`. **I could not extract its operational gate definition or numbers** — the PDF resisted extraction. Flagged as the most promising unverified lead in this report. **[B, unconfirmed]**
- Grounding effect size, for scale: providing guideline text raised clinical information extraction accuracy from **45% → 81.9%** (Claude-2) and **36.1% → 82.0%** (GPT-4). **[B]** Large, but 82% is not a safety-grade number.

**Financial.** Tie-out automation (§2.0.2) is the closest thing to a deployed "every value must reconcile to source" system, but the products are vendor-reported without independent evaluation. **[C]**

**Verdict on the question as asked:** outside of regulated human-in-the-loop processes, **PCN is the only published protocol that makes an unsourceable value a structural hard stop, and it has no empirical validation.** T2D-Bench may be a second instance. This is a genuine gap in the literature, not an oversight in the search.

## 5.5 Binary asset provenance — the weakest area

Two disconnected literatures, neither of which solves the problem.

**Cryptographic lineage — C2PA / Content Credentials** (`https://spec.c2pa.org/specifications/specifications/2.4/explainer/Explainer.html`). **[A — public spec]** A C2PA manifest is a cryptographically signed record embedded in an asset declaring which model produced or modified it, what inputs were supplied, and the full edit chain, using hashes and signatures so alteration is detectable. Actions performed by an AI/ML system are identified via the `digitalSourceType` field. Adoption: OpenAI embeds C2PA in DALL·E 3 output; Samsung Galaxy S25 signs in the native camera app.

**Its limits are severe and well documented [C]:** metadata "can be stripped by users seeking to obscure provenance", and the signature becomes **invalid upon any image transformation** — resize, recompress, crop. In a document pipeline that processes or converts assets, C2PA breaks by default. Watermarking approaches (InvisMark, `https://arxiv.org/pdf/2411.07795`) and perceptual-hash hybrids (`https://arxiv.org/pdf/2503.11195`) address robustness. **[B]**

And the deeper limitation: **C2PA proves an asset's lineage, not its correctness.** A signed manifest attesting "this chart was generated by model M from file F" says nothing about whether the chart plots F correctly.

**Semantic asset verification — does the figure match the data?** Genuinely early. **[B]**

- **Visual Consistency Score (VCS)** — reference-free metric that has an LLM translate a caption into Python code, regenerate the chart, and compare the reconstruction against ground truth. Round-tripping through executable code is the most promising idea here because it converts a judgement into a computation.
- A verifier that "interprets numerical expressions within generated captions and cross-checks them against chart data, accounting for axis mappings, ratios, and relative trends" achieved **+22.2 percentage points absolute improvement in factual accuracy** over baseline LLM captioning — on **102 charts**. Small sample. `https://www.techrxiv.org/doi/pdf/10.36227/techrxiv.176070670.04768024/v1`
- **ChartAnchor** (`https://arxiv.org/html/2512.01017`) evaluates on four axes: functional validity (execution pass rate), visual rigor (chart type, colour, text, layout), semantic data fidelity (structured tuple matching), perceptual consistency.
- **ChartCap** (`https://arxiv.org/html/2508.03164`) targets dense chart-caption hallucination.

**Assessment: for binary assets, you can get cryptographic lineage (fragile) and code-round-trip semantic checking (early, small-sample). Neither is close to the maturity of text grounding checks, and text grounding checks only reach 75%.** For a manifest-driven document system, the defensible position today is: hash-and-verify existence deterministically, generate assets from declarative source (code/data) so the derivation is re-executable, and treat any semantic claim about an asset as unverified unless it is recomputed from the same source.

---

# 6. Synthesis — what the evidence supports

## 6.1 The layered picture

| Layer | Catches | Reliability | Cost |
|---|---|---|---|
| Constrained decoding | Malformed structure | ~100% | ~0 |
| Schema + Pydantic validators | Type/range/enum/intra-doc cross-field | ~100% *on what it expresses* | ~0 |
| Deterministic recomputation | Any computable derivation | Exact | Low |
| External resolution (DOI/DB) | Non-existent citations | High DR, **poor PPV at low base rate** | Low |
| Fact store / KG consistency | Cross-section contradiction | 8× conflict reduction (DOME) | ~16 calls/doc |
| Entailment checking (MiniCheck) | Claim-vs-source support | **~75%** | $0.24/13K |
| LLM judge | Everything else | **~60–80%, correlated, biased** | High |
| Human expert | Ground truth | 17% recall on injected consistency errors | Very high |

**The gradient is steep and monotonic.** Every step you can move a check *up* this table is worth far more than tuning the layer below. The highest-leverage engineering move available is converting judgement-shaped checks into computation-shaped checks.

## 6.2 Seven defensible design conclusions

1. **Never treat schema validity as a correctness signal.** 100% valid coexists with 2% correct.
2. **Invert the default to fail-closed (PCN).** Given 20–25% checker error, an unverified-by-default renderer is the only architecture where checker failure is visible rather than silent.
3. **Extract to a fact store; do not ask a long-context model to self-audit.** Judge accuracy falls 75%→61% from 64K to 262K. DOME's structured approach costs 16 calls and is length-independent.
4. **Use validity intervals, not flat fact stores** (FACTTRACK). Legitimate change over time is not contradiction; flat stores produce false positives on it.
5. **Resolve citations externally, never parametrically.** Post-cutoff FPR of 0.59–0.89 across 8 of 12 models. And **tune the gate on FPR at the true base rate** — at 2% prevalence a 0.43 FPR verifier yields ~3% precision and will be ignored within a day.
6. **Budget ~2 effective votes from any LLM panel; cap at 5; never treat unanimity as verification.** 5.1% of items were wrong by all 9 judges. CoT *increases* correlation.
7. **Do not ask the generating model family to judge its own output**, and do not rely on intrinsic self-correction — it degrades performance without external feedback (TACL **[A]**).

## 6.3 Where the evidence is genuinely thin

Stated explicitly so these are not over-read:

- **PCN has no empirical evaluation.** The formal properties are proved; deployment evidence does not exist.
- **T2D-Bench's evidence gate could not be extracted.** Best unverified lead; check `https://github.com/Saba-Farahani/t2d-bench-` directly.
- **ConStory-Checker's human baseline is n=2 annotators on injected errors, and the paper's prose and table disagree (0.281 vs 0.229).** Do not cite the "beats human experts" claim without re-reading Table 6.
- **ReFACT's 0.60 comparative-judgment figure could not be confirmed** from the source PDF.
- **PoLL and Nine Judges conflict** on whether panels help. I weight Nine Judges higher on methodology (n_eff, Condorcet gap, permutation test, oracle-aggregation ceiling) but this is a live disagreement, not a settled question.
- **Semantic binary-asset verification is genuinely immature** — the strongest result is +22.2pp on 102 charts.
- **No published system enforces "every value cites a primary source" end-to-end with measured results.** Financial tie-out comes closest and is vendor-reported. DO-178C comes closest in rigour and is human-executed.
- **Most 2026 preprints cited here are unreviewed and were read via extraction.** Re-read any table before it becomes load-bearing.

---

# Sources

**Structured output & schema limits**
- When JSON Is Not Enough — https://arxiv.org/html/2607.18261v1
- Let Me Speak Freely? (EMNLP 2024) — https://arxiv.org/abs/2408.02442
- XGrammar — https://github.com/mlc-ai/xgrammar
- Structured output library comparison — https://techsy.io/en/blog/best-llm-structured-output-libraries

**Global consistency & state tracking**
- DOME (NAACL 2025) — https://aclanthology.org/2025.naacl-long.63.pdf · https://arxiv.org/html/2412.13575v1
- FACTTRACK — https://arxiv.org/abs/2407.16347
- Lost in Stories / ConStory-Bench — https://arxiv.org/html/2603.05890v1
- Foundations of Global Consistency Checking with Noisy LLM Oracles — https://arxiv.org/html/2601.13600
- Contradiction Detection in RAG Systems — https://arxiv.org/abs/2504.00180
- Discovering Inconsistencies in Documents with Long-Context LLMs — https://link.springer.com/chapter/10.1007/978-3-031-94931-9_9
- Long Story Generation via Knowledge Graph and Literary Theory — https://arxiv.org/pdf/2508.03137
- Narrative World Model — https://arxiv.org/pdf/2607.05577
- Guiding Generative Storytelling with Knowledge Graphs — https://www.tandfonline.com/doi/full/10.1080/10447318.2025.2603634
- DeepResearch Bench II — https://arxiv.org/pdf/2601.08536
- FailSafe Long Context QA for Finance — https://arxiv.org/pdf/2502.06329

**Grounding & attribution**
- Measuring Attribution in NLG (AIS, CL 2023) — https://aclanthology.org/2023.cl-4.2/ · https://github.com/google-research-datasets/AIS
- AttributionBench (Findings ACL 2024) — https://aclanthology.org/2024.findings-acl.886.pdf · https://arxiv.org/abs/2402.15089
- MiniCheck (EMNLP 2024) — https://aclanthology.org/2024.emnlp-main.499.pdf · https://github.com/Liyan06/MiniCheck
- SAFE / LongFact — https://arxiv.org/abs/2403.18802
- CiteEval — https://arxiv.org/html/2506.01829
- A review of faithfulness metrics for hallucination assessment — https://arxiv.org/pdf/2501.00269

**Citation verification**
- HALLMARK — https://arxiv.org/html/2607.18360
- GhostCite — https://arxiv.org/html/2602.06718v1
- CiteCheck — https://arxiv.org/html/2605.27700v1
- Detecting & Correcting Reference Hallucinations in Commercial LLMs — https://arxiv.org/pdf/2604.03173
- Cross-Model Audit of Reference Fabrication — https://arxiv.org/pdf/2603.03299
- ChatGPT/Bard systematic review hallucination rates — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11153973/
- RefChecker — https://github.com/markrussinovich/refchecker
- llm-citation-verifier — https://github.com/DWFlanagan/llm-citation-verifier
- hallucinator — https://github.com/gianlucasb/hallucinator
- References-Validation (MCP) — https://github.com/zabbonat/References-Validation
- AutoCitation — https://github.com/sypsyp97/AutoCitation

**LLM-as-judge reliability**
- Nine Judges, Two Effective Votes — https://arxiv.org/html/2605.29800
- Justice or Prejudice? (CALM) — https://llm-judge-bias.github.io/
- Replacing Judges with Juries (PoLL) — https://arxiv.org/pdf/2404.18796
- LLMs Cannot Reliably Judge (Yet?) — https://arxiv.org/html/2506.09443
- Self-Preference Bias in LLM-as-a-Judge — https://openreview.net/forum?id=Ns8zGZ0lmM
- When Can LLMs Actually Correct Their Own Mistakes? (TACL) — https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00713/125177/
- LLMs Cannot Self-Correct Reasoning Yet — https://arxiv.org/abs/2310.01798
- ReFACT — https://arxiv.org/pdf/2509.25868
- A survey on LLM-as-a-judge — https://www.sciencedirect.com/science/article/pii/S2666675825004564

**Hard stops, abstention & provenance**
- Proof-Carrying Numbers — https://arxiv.org/abs/2509.06902
- RefusalBench — https://arxiv.org/html/2510.10390v1
- GRACE — https://arxiv.org/html/2601.04525v1
- T2D-Bench — https://arxiv.org/pdf/2606.24145 · https://github.com/Saba-Farahani/t2d-bench-
- TRIPOD-LLM (Nature Medicine) — https://www.nature.com/articles/s41591-024-03425-5
- From Agent Traces to Trust (PROV survey) — https://arxiv.org/html/2606.04990v3
- Graph-RAG requirement traceability — https://arxiv.org/pdf/2412.08593
- Trace Link Recovery via LLMs — https://link.springer.com/chapter/10.1007/978-3-032-30693-7_1
- DO-178C / NASA SWE-023 — https://swehb.nasa.gov/spaces/SWEHBVC/pages/50888880/SWE-023+-+Software+Safety-Critical+Requirements
- Aggregating LLM-Based Weak Verifiers — https://arxiv.org/pdf/2606.05268
- FinSheet-Bench — https://arxiv.org/html/2603.07316v1

**Binary asset provenance**
- C2PA Explainer — https://spec.c2pa.org/specifications/specifications/2.4/explainer/Explainer.html · https://c2pa.org/faqs/
- C2PA limits — https://truescreen.io/articles/c2pa-standard-history-limitations/
- InvisMark — https://arxiv.org/pdf/2411.07795
- Provenance Detection for AI-Generated Images — https://arxiv.org/pdf/2503.11195
- ChartAnchor — https://arxiv.org/html/2512.01017
- ChartCap — https://arxiv.org/html/2508.03164
- LLM-Powered Chart Captioning (VCS) — https://www.techrxiv.org/doi/pdf/10.36227/techrxiv.176070670.04768024/v1
