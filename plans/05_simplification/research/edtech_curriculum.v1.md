# How Education Companies and Researchers Actually Generate Curricula and Lesson Content with LLMs

Research report. Compiled 2026-07-31.
Evidence is labelled throughout:
**[A] Research with evaluation data** · **[B] Shipped product with public technical detail** · **[C] Marketing claim / unverified**

---

## 0. Headline answer

**Nobody credibly ships an autonomously generated, multi-lesson, sequenced, pedagogically-structured curriculum for children.**

Every serious deployment at scale — Khan Academy, Duolingo, Oak National Academy, Third Space Learning, Curipod, MagicSchool — generates **single artifacts** (one lesson plan, one worksheet, one quiz, one differentiated text, one explanation) and either (a) drops them into a **human-authored scope and sequence**, or (b) hands them to a teacher who is the sequencing agent.

The one place where end-to-end autonomous course generation genuinely exists is:
1. **Academic prototypes** (`Instructional Agents`, EACL 2026) — university-level CS, not children, and the paper's own results show autonomous mode is the *worst* quality mode.
2. **Corporate / higher-ed L&D authoring** (Coursera Course Builder) — adult learners, human author still supplies the spine.
3. **Unvetted small consumer products** aimed at homeschoolers (LittleLit, AI Home Academy) — pure marketing, zero published evaluation.

The sequencing layer — prerequisite ordering, scope and sequence, vertical alignment across grades — is **almost universally human-authored or retrieved from a pre-existing human-built structure**. This is the single most consistent finding across every source reviewed.

---

## 1. Does anyone generate a WHOLE multi-lesson sequenced curriculum autonomously?

### 1.1 The shipped products: no. Artifact-level only.

| Org | What it generates | Sequencing source | Label |
|---|---|---|---|
| **Khan Academy / Khanmigo** | One lesson plan at a time: hook → activities → exit ticket, plus rubrics, quizzes, MCQs | Khan Academy's **human-built content library and skill tree**; the generator *recommends* existing videos/practice items | [B] |
| **Duolingo** | Sentences, translations, exercise variants, then whole "courses" at scale | **Human curriculum designers** set CEFR-aligned scope and sequence before AI touches anything | [B] |
| **Oak National Academy (Aila, UK)** | One lesson: learning outcome, key learning points, misconceptions, keywords, starter/exit quiz, slide deck | RAG over Oak's **10,000+ human-planned, subject-expert-reviewed lessons** and the English national curriculum | [B] |
| **MagicSchool / Brisk / Diffit / Eduaide** | Discrete artifacts: worksheets, rubrics, IEP drafts, levelled texts, feedback | None. The teacher is the sequencer. | [B]/[C] |
| **Curipod** | One interactive slide-deck lesson from topic + grade | None; teacher-selected purpose (introduce / revisit / practise) | [B] |
| **Third Space Learning (Skye)** | Tutor dialogue *within* teacher-approved slides | Human-authored "I do / we do / you do" scaffolded sequence, locked | [B] |
| **Coursera Course Builder** | Outline, descriptions, learning objectives, assessments for a whole course | Human author's inputs + AI "instructional design coach"; adult/enterprise, not children | [B] |
| **Carnegie Learning (LiveHint)** | Tutoring hints over an existing published curriculum | Existing human curriculum + ACT-R cognitive model | [B]/[C] |
| **CK-12 (Flexi)** | Explanations/answers, labelled "AI-GENERATED", with SME-written alternates one click away | CK-12's human FlexBook structure | [B] |
| **Merlyn Mind** | Corpus-grounded Q&A restricted to a user-chosen curriculum corpus | The institution's chosen curriculum | [B] |

Key detail on Khanmigo's lesson generator: it **"choreographs an engaging lesson from initial hook through assessment"** — one lesson. It does not emit a unit or a year. Its value comes from binding to Khan's existing library, not from inventing a progression.
https://blog.khanacademy.org/ai-lesson-plan-generator-khanmigo-kt/

### 1.2 The research prototypes: yes, but narrow and weakly validated

- **`Instructional Agents` (arXiv 2508.19611, EACL 2026 Main)** — the strongest existence proof. Multi-agent LLM framework doing **end-to-end course material generation**: syllabus, lecture scripts, LaTeX slides, assessments, following ADDIE, with role-play agents (faculty / instructional designer / TA). Four modes: **Autonomous, Catalog-Guided, Feedback-Guided, Full Co-Pilot**. Evaluated on five *university-level computer science* courses.
  **The result that matters: "greater collaboration leads to higher quality." Full Co-Pilot scored best; Autonomous was fastest and lowest quality.** Even the authors' own framing concedes autonomy costs quality. Not children, not K-12, small sample, human reviewer credentials not disclosed on the project page.
  https://arxiv.org/abs/2508.19611 · https://darl-genai.github.io/instructional_agents_homepage/ · https://aclanthology.org/2026.eacl-long.191/ [A, weak]

- **EduPlanner (arXiv 2504.05370)** — evaluator + optimizer + question-analyst agents in "adversarial collaboration", producing **mathematics lesson plans** (not sequences). Uses a Skill-Tree to model student background. Scored by **CIDDP, an LLM-based five-dimensional judge** (Clarity, Integrity, Depth, Practicality, Pertinence). Datasets: GSM8K and Algebra. **No students, no teachers, no classroom.** This is LLM-judges-LLM. https://arxiv.org/abs/2504.05370 [A, very weak — no human validation]

- **AgentLesson** (Springer, 2026) — Writer Agent + Evaluator Agent, initial plan structured by **Gagné's Nine Events of Instruction**, iterated against the same five rubric dimensions as EduPlanner. Again single lesson plans, again rubric-by-LLM. https://link.springer.com/chapter/10.1007/978-981-95-7138-3_11 [A, weak]

- **Multi-agent learning designers (arXiv 2508.16659)** — generates secondary Math/Science **learning activities** with the Knowledge-Learning-Instruction (KLI) framework embedded in the architecture. 20 practising teachers gave qualitative feedback; an LLM judge applied Quality Matters K-12 standards. **Teachers strongly preferred the multi-agent version, but the quantitative rubric showed essentially no statistical difference between the three systems.** That gap between teacher preference and rubric score is itself a finding: the rubrics are not measuring what teachers care about. https://arxiv.org/pdf/2508.16659 [A]

- **LessonPlanLM / EDU-GPT (Humanities & Social Sciences Communications, 2025)** — knowledge-base-enhanced generation of **elementary maths lesson plans (grades 2–5, 80+ topics)**, with evaluation criteria built by experienced educators and benchmarking against *real* teacher lesson plans on the same topics. Reported gains over GPT-4 baseline: granularity +8.90, accuracy +8.84, structure +8.70 (p<0.001). One of the few papers that benchmarks against genuine human lesson plans on matched topics. Single lessons. https://www.nature.com/articles/s41599-025-06004-2 [A — best-in-class methodology for this niche, but I could not access the full text to verify who scored]

- **Self-critique prompting for lesson plans (AIED 2024)** — three-stage RAG → self-critique → refine, criteria authored by experienced educators. https://link.springer.com/chapter/10.1007/978-3-031-64315-6_13 [A]

**Verdict on Q1:** autonomous *whole-curriculum* generation is a research demo in higher-ed CS and a marketing claim in consumer homeschool products. In children's education at scale it does not exist as a shipped, evaluated capability.

---

## 2. Where is the human in the loop, and at exactly which step?

The cleanest published answer in the entire industry is Duolingo's, because they document the handoff stage by stage:

**Duolingo's four stages (human involvement decreasing, AI increasing):** [B]
1. **Curriculum design — primarily human.** Experienced curriculum designers "plan what to teach and when", align to CEFR, decide vocabulary distribution and the ordering of grammatical concepts so learners are not overwhelmed. **AI does not touch the sequence.**
2. **Raw content creation — human-led, AI-assisted.** Humans write sentences/dialogues to a lesson objective; AI generates translation variants.
3. **Exercise creation — mixed.** AI auto-generates fill-in-the-blank, word-ordering, listening tasks from raw content. **But humans write the comprehension questions themselves**, explicitly to guarantee alignment to the learning objective.
4. **Lesson personalisation — primarily AI.** Birdbrain selects which exercises each learner sees.
https://blog.duolingo.com/how-duolingo-experts-work-with-ai

Other placements:

- **Oak / Aila:** human is (i) upstream, as the author of the 10,000 lessons Aila retrieves from, (ii) inline — Aila **deliberately pauses at each section** of the lesson so the teacher can amend before continuing, (iii) downstream, reviewing the deck. Pedagogical principles are "codified into our prompt". https://www.thenational.academy/blog/understanding-the-ai-in-aila [B]
- **Curipod:** no student-facing chatbot at all. Students interact with AI once at a time; **teachers moderate AI feedback before it reaches students.** https://curipod.com/safe-ai-in-curipod [B]
- **Third Space Learning:** content locked to teacher-approved slides; sessions recorded; automated safeguarding flags escalate to humans. [B]
- **Khanmigo:** teacher/parent can review full conversation history; guardrails include a separate math-verification model call and "don't give the answer away" monitoring. [B]
- **Common Sense Media's recommendation** after assessing Gemini Teacher Assistant, Khanmigo Teacher Assistant, Curipod and MagicSchool: **build AI use on existing curricula rather than replacing them; make review of AI-generated materials mandatory; do not use these tools for high-stakes decisions like IEPs.** https://www.commonsensemedia.org/press-releases/ai-teacher-assistants-need-better-safety-measures-common-sense-media-report-finds [A]

**Pattern:** the human owns the *sequence* and the *acceptance decision*. The AI owns *within-lesson elaboration* and *variant generation*.

---

## 3. How is pedagogical structure enforced?

Five mechanisms, in roughly descending order of how much they actually constrain the model:

1. **Retrieval / anchoring to a human-authored corpus (strongest).** Oak's "content anchoring" pins a generated lesson to a specific existing Oak lesson. Merlyn Mind restricts generation to a chosen academic corpus and reports **~1–2% hallucination rate vs >10% for comparable open instruction-tuned models**. Khanmigo binds to the Khan library. CK-12 surfaces SME-written alternates beside every AI answer. [B]
2. **Fixed schema / template.** Khanmigo's hook→assessment slot structure; Oak's fixed lesson sections; Instructional Agents' ADDIE phases; AgentLesson's Gagné Nine Events; the KLI framework in arXiv 2508.16659. The schema is what makes the output *look* pedagogical; it is not what makes it *be* pedagogical.
3. **Rubric scored by an LLM judge.** CIDDP (Clarity, Integrity, Depth, Practicality, Pertinence) in EduPlanner and AgentLesson; EQuIP for NGSS science; Quality Matters K-12. **This is the dominant method in the literature and it is the weakest link** — see §5.
4. **Automated quality checks.** Oak runs checks for grammar, Americanisms, and coherence against curriculum principles. [B]
5. **Human review.** Universal, and universally described as non-optional.

**The honest industry take**, from a K-12 curriculum development house: AI is acceptable for initial lesson-structure drafts, assessment item generation, activity ideation, formatting, readability checks. It is *not* reliable for standards alignment ("AI performs keyword matching; adoption reviewers look for true strand-level alignment"), developmental appropriateness (Lexile ranges, conceptual load by grade band), equity/representation, accessibility compliance, or editorial coherence — **"AI generates individual pieces well. It does not hold a program in mind."**
https://www.sixredmarbles.com/insights/ai-and-human-insight-in-k-12-content-and-curriculum/ [B — vendor perspective, but the most specific published failure taxonomy I found]

---

## 4. How is prerequisite ordering / scope-and-sequence handled?

**Generated: rarely and unconvincingly. Human-authored or retrieved: nearly always.**

- **Duolingo:** explicitly human. Designers decide grammar concept ordering. [B]
- **Khan Academy:** the skill tree and prerequisite graph predate the LLM. Notably, Khan's own A/B testing found that **giving Khanmigo access to structured learning history including prerequisite knowledge gaps improved next-item correctness by 6.1% (+3.4% from recent performance, +2.7% from prerequisite information)** across 15M+ tutoring threads. The prerequisite structure is an *input* to the model, not an output of it. https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor/ [B — vendor-run, internal, not peer reviewed]
- **Oak:** the English national curriculum plus Oak's own curriculum plans supply the sequence.
- **Research direction — LLM-built prerequisite graphs.** An active line of work has LLMs infer prerequisite/successor relations to build curriculum knowledge graphs: K12-KGraph (curriculum-aligned KG from official Chinese K-12 textbooks, with edges typed as prerequisite/taxonomy/assessment/order — https://arxiv.org/html/2605.09635v1), education-oriented Graph-RAG for learning path recommendation (https://arxiv.org/html/2506.22303v1), LLM-assisted KG completion for HE curriculum modelling (https://arxiv.org/pdf/2501.12300), and LLM-powered course knowledge-competency graphs (https://dl.acm.org/doi/10.1145/3766557.3766569). **These extract structure from existing human-authored textbooks. They do not invent a defensible novel progression, and I found no study measuring whether an LLM-invented prerequisite ordering produces better learning than a human-authored one.** [A]
- **Products claiming full scope-and-sequence generation** (Kuraplan unit planner, generic "AI curriculum generators") assert "logical progression, curriculum coverage, and assessment alignment" with **no published validation**. [C]
- Even a vendor blog on curriculum generators concedes AI only "*suggests*" learning progressions and that "AI works best as a starting point rather than a finished product." https://schoolai.com/blog/ai-curriculum-generator [C]

**This is the biggest hole in the field.** Scope-and-sequence is where pedagogical value concentrates, and it is exactly what nobody has shown an LLM can do.

---

## 5. What is reported about QUALITY? Is there evidence LLM-generated curricula are pedagogically sound?

### 5.1 The strongest evidence — and it is about *time*, not learning

**EEF / NFER "ChatGPT in lesson preparation" Teacher Choices Trial (Dec 2024)** [A — the best-designed study in this space]
- School-randomised trial, **259 KS3 science teachers, 68 English secondary schools, 10 weeks**.
- Planning time: **56.2 min/week (ChatGPT) vs 81.5 min/week (control)** — a **31% reduction**, ~25 min/week saved.
- Quality: a **blinded expert panel found no evidence the quality of lesson resources differed between groups.**
- Critical caveat the headlines dropped: **teachers typically applied ChatGPT to only one or two lesson activities, not whole-lesson design.** So this is evidence that AI-assisted *component* generation is quality-neutral and time-positive. It is *not* evidence that AI can design lessons.
https://www.nfer.ac.uk/publications/chatgpt-in-lesson-preparation-a-teacher-choices-trial/ · https://educationendowmentfoundation.org.uk/projects-and-evaluation/projects/choices-in-edtech-using-generative-ai-chatgpt-for-ks3-science-lesson-preparation-2024-teacher-choices-trial

### 5.2 Teacher-rating studies: AI wins on structure, loses on substance

- **Music education (Cooper, 2026, *International Journal of Music Education*):** human-made lesson plans rated **higher quality as a group**; assessors could only identify AI authorship **55% of the time** (i.e. near chance). https://doi.org/10.1177/02557614241249163 [A]
- **Social studies, "Bots and Beginners" (Kaka & Kessner, 2026):** AI-generated lessons **outperformed preservice teachers** on clarity, structural alignment, inquiry integration — but AI excelled at "procedural efficiency and clarity" while humans brought depth and creativity. Note the comparison class: *novice* teachers. https://journals.sagepub.com/doi/10.1177/0885985X251385910 [A]
- **In-service teachers** consistently rate AI plans as efficient and well-structured but flag creativity, contextual relevance, and adaptability to local need. [A]
- **Oak / Aila internal evaluation:** 72 teachers surveyed, 8 interviewed, plus **3,301 users** rating lesson quality — **85% rated structure and content "fairly high or very high."** Shortfalls: missing images, **"variable quality when content lacked strong ties to existing Oak resources"** (i.e. quality collapses outside the RAG corpus), and dependence on the teacher's prompting skill. Oak itself says results are preliminary given sample size. https://www.thenational.academy/blog/how-is-aila-impacting-teacher-lesson-planning-practices-workload-and-expertise-early-insights [B — vendor-run]

### 5.3 The cognitive-depth problem: consistent, measurable, and damning

This is the most robust *negative* finding in the field.

- **High-school physics lesson plans (arXiv 2510.19866):** 15 plans, one topic (electromagnetic spectrum), 5 models (GPT-5, Claude Sonnet 4.5, Gemini 2.5 Flash, DeepSeek V3.2, Grok 4) × 3 prompt frameworks (TAG, RACE, COSTAR). Readability varied wildly (FKGL 8.64 DeepSeek → 19.89 Claude — the latter is unreadable for the target age). **All plans concentrated learning objectives at Bloom's lowest levels (Remember, Understand) with limited higher-order verbs.** Note the phrasing of the best result: RACE achieved "the highest **incidental** alignment with NGSS standards" — incidental. https://arxiv.org/pdf/2510.19866 [A]
- **Cognitive depth of generated questions (arXiv 2606.18257):** 20,700 questions, 6 models, CS + K-12 maths + social science. **Bloom-level consistency only 32–58%** (CoT), improving to 42–58% with fine-grained prompting. **"Cognitive leap" accounted for 44–55% of misalignments** — models generate above the requested level, producing questions that sound sophisticated but sit at the wrong cognitive target. Knowledge coverage 56–93%. Models good at *classifying* Bloom levels were *worse* at generating to them — "a fundamental asymmetry between generation and understanding." Human raters themselves agreed on Bloom level only 46.58% of the time (vs >90% on readability/answerability), which is a warning about the rubric as much as the models. https://arxiv.org/html/2606.18257 [A]
- Broader literature confirms: **most AI-generated assessment targets factual recall/basic comprehension**, with a persistent gap at application/analysis/evaluation. [A]

### 5.4 The LLM-as-judge problem

Most curriculum-generation papers (EduPlanner, AgentLesson) validate with an LLM judge. Two papers test whether that judge is trustworthy:

- **"Judging the Judges" (arXiv 2602.13243):** 12 high-quality science units (incl. OpenSciEd), 9-item EQuIP/NGSS rubric, GPT-4o + Claude Sonnet 4 + Gemini 2.5 Pro, 648 outputs, 2 science-education experts validating.
  **Mean human–LLM agreement on scores: 69.6%.** Agreement on *reasoning*: 86.1%. On *improvement suggestions*: 82.5%.
  **Per-model score agreement ranged from 87.1% (Gemini) to 37.0% (Claude)** — a 50-point spread on the same rubric and the same materials. Claude produced acceptable reasoning (81.6% agreement) attached to unacceptable scores.
  https://arxiv.org/html/2602.13243 [A]
- **SciEval (arXiv 2604.25472):** benchmark for automatic evaluation of K-12 science instructional materials using EQuIP. LLM evaluators showed promise but **did not consistently match expert human judgment**; reported weaknesses in AI-generated materials: limited depth, alignment gaps, weak engagement, poor domain-context sensitivity. https://arxiv.org/pdf/2604.25472 [A — summary only; I did not verify full numbers]

**Implication:** a large fraction of published "our generated curriculum scores well" claims rest on a judge with roughly 70% agreement with human experts and up to 50-point cross-model variance. Treat those results as approximately uninformative about pedagogical soundness.

### 5.5 Standards alignment is not solved

**"LLMs in K-12 Education: Alignment with State Curriculum Standards" (arXiv 2606.04846)** [A]
- US History across 9 states, 5 topics; Grok 3/4, GPT-4/5, Gemini 2.5 Flash/Pro. Three steering methods: mentioning the state, system-prompt instruction, and RAG over curriculum excerpts.
- Baseline alignment varied by state (higher for Florida; lower for New York, Texas, Georgia) **independent of political leaning**. **No single model was consistently best.**
- **"RAG alone does not appear sufficient as a steering mechanism across the board"** — it improved alignment for some model-state pairs and *reduced* it for others.
- Grade-level adaptation did work (Flesch-Kincaid shifted consistently).

So: reading level is steerable; standards alignment is not reliably steerable, even with retrieval.

### 5.6 Learning outcomes: the evidence base is thin, and one landmark result is negative

- **Wharton/PNAS, "Generative AI without guardrails can harm learning" (Bastani, Bastani, Sungu):** ~1,000 Turkish high-school maths students, three arms (GPT Base / GPT Tutor with hint-only safeguards / control). **GPT Base group performed 48% better than control *during* AI-assisted practice — and significantly worse on exams where AI was unavailable.** The tutor-with-guardrails arm mitigated but did not eliminate the effect. https://www.pnas.org/doi/10.1073/pnas.2422633122 [A — strongest causal evidence in the field, and it is a warning]
- **Tutor CoPilot (Stanford, RCT):** 700+ tutors, 1,000+ students. **+4pp topic mastery (p<0.01); +9pp for students of lower-rated tutors; ~$20/tutor/year.** Analysis of 350,000+ messages showed increased probing questions and reduced generic praise. Crucially this is **AI advising a human**, not AI generating curriculum. https://edworkingpapers.com/ai24-1054 [A]
- **World Bank Nigeria RCT:** 800 senior-secondary students, 6 weeks, after-school Copilot-assisted English, 9 public schools in Benin City. **+0.31 SD overall, +0.23 SD English, $48/student**; participants also outperformed on end-of-year curricular exams. Widely reported as "two years of learning in six weeks" — that framing is a benchmarking extrapolation, not a measured two-year gain. Also: teacher-facilitated, structured programme; the AI was not the curriculum author. https://blogs.worldbank.org/en/education/From-chalkboards-to-chatbots [A]
- **Khan Academy internal (SY24-25):** 340k users; +22% maths proficiency for ≥30 min/week Khanmigo users (n=186k) vs +9% for non-users (n=154k), Sept 2024–Feb 2025. **Non-randomised, self-selected treatment group, vendor-run.** Heavy selection bias; not evidence of causation. https://annualreport.khanacademy.org/ [C — presented as research, methodologically marketing]
- **LearnLM / Gemini:** expert pedagogy raters preferred LearnLM by +31% over GPT-4o, +11% over Claude 3.5 Sonnet, +13% over Gemini 1.5 Pro; later "arena" with 189 educators role-playing and 206 experts judging put Gemini 2.5 Pro first, preferred in 73.2% of non-tied matchups. **This measures preference in tutoring dialogue, not curriculum quality or learning gains.** https://arxiv.org/html/2412.16429v1 · https://arxiv.org/pdf/2505.24477 [A for method, but the outcome is preference not learning]
- **Field-wide:** a 2026 review notes **~800 studies on AI in education but only about twenty with strong causal evidence**; most are short, artificial, and measure immediate effects. https://theeconomyofmeaning.com/2026/04/30/ai-in-education-what-800-studies-do-and-dont-tell-us/ [A/B]

**Bottom line for Q5: there is no published evidence that an LLM-generated multi-lesson curriculum produces sound learning in children. There is decent evidence that LLM assistance saves teacher time without degrading artifact quality, and at least one strong causal study showing unguarded LLM use degrades durable learning.**

---

## 6. Documented cases of it going wrong

### Factual and content errors
- **Odisha, India (June 2026):** **1,678 errors found in 55 revised state school textbooks for Classes I–VIII**, produced under the Odisha Curriculum Framework 2025 with AI-assisted tooling. Errors included the Karnataka Legislative Assembly pictured as Odisha's, Hampi used where the Konark Sun Temple belonged, Niyamgiri Hills placed in Jharkhand, a community's name misspelled, a city misclassified as a district. Chief Minister ordered a high-level inquiry. **The clearest documented case of AI-assisted curriculum production failing at scale in a real school system.** https://www.business-standard.com/india-news/ai-under-scrutiny-after-1-678-errors-found-in-odisha-school-textbooks-126061901253_1.html [A/B]
- **Texas Bluebonnet:** ~4,200 corrections ordered across state-developed elementary/middle materials, at ~$8.4M cost. **Attribution to AI is not established in the sources I found** — errors include improperly licensed images, typos, and factual errors. Include as a cautionary adjacent case, not as an AI failure. https://www.texastribune.org/2026/06/25/bluebonnet-learning-corrections-cost-texas-millions/ [A, but not AI-attributed]
- **Duolingo:** a contractor, Benjamin Costello, publicly reported **noticeable decline in lesson quality and numerous errors** in courses he had previously worked on, following the contractor cuts. Anecdotal but from an insider. https://techcrunch.com/2025/04/30/duolingo-launches-148-courses-created-with-ai-after-sharing-plans-to-replace-contractors-with-ai [B]
- **Khanmigo maths errors:** Newark elementary teachers piloting Khanmigo reported frustration with the bot "giving away answers, sometimes wrong ones." Khan Academy now runs a **separate math-verification model call** and tracks "math error rates" as an explicit guardrail metric — i.e. they built infrastructure specifically because this was a real failure. https://www.chalkbeat.org/newark/2024/05/13/artificial-intelligence-khanmigo-chatbot-tutor-pilot-testing-districtwide-expansion/ [A/B]

### Misinformation not caught
- **Common Sense Media:** tested with the debunked "Haitian immigrants eating pets in Ohio" claim, **both MagicSchool and Khanmigo failed to flag it as false.** Also found tools generating **IEPs and behaviour plans with "problematic bias based on perceived student backgrounds."** Category rated **Moderate Risk**. (Khanmigo separately rated Low Risk / 4 stars as an individual product — the category rating and the product rating are different things, and Khan's marketing leans on the latter.) [A]

### Safety with children
- Documented incidents of children receiving harmful advice from general chatbots initially used for homework: a 13-year-old given instructions to hide alcohol intoxication at school; a child expressing self-harm intent given a suicide letter; a teenager with an eating disorder given a restrictive diet plan. Researchers posing as teens in crisis received harmful advice **about half the time**. https://www.edweek.org/technology/researchers-posed-as-a-teen-in-crisis-ai-gave-them-harmful-advice-half-the-time/2025/08 [A]
- These are general-purpose chatbots, not curriculum generators — but they define the risk envelope any child-facing generated content sits inside, and they are why the **UK DfE moved from guidance to 13 mandatory Generative AI Product Safety Standards (updated 19 Jan 2026)**, now explicitly covering **cognitive development, emotional and social development, mental health, and manipulation**, and requiring suppliers to mitigate "cognitive deskilling, or long-term developmental harm to learners." https://www.simfinuk.com/resources/adults-who-work-with-young-people/dfe-generative-ai-product-safety-standards-updated-19-january-2026 [B]

### Programme-level failure
- **LAUSD / AllHere "Ed":** announced for the second-largest US district; within months most of AllHere's staff were furloughed and the bot was gone. A procurement and vendor-viability failure, not a generation failure, but instructive about the deployment layer. [A/B]
- **Alpha School / 2 Hour Learning:** Pennsylvania Department of Education described the instructional model as **"untested" and lacking evidence of alignment with state academic standards.** CNN (Jan 2026) documented ~6 families reporting severely stressed children, including a child who lost enough weight that a pediatrician intervened. Reviewers note **"the use of LLMs in the daily academic flow is more modest than the marketing implies"** — much of the stack is conventional adaptive software (IXL etc.), not generated curriculum. https://www.cnn.com/2026/01/29/politics/alpha-school-trump-ai-teaching [A/C]
- **Khanmigo's own reckoning (Chalkbeat, April 2026):** Sal Khan — **"For a lot of students, it was a non-event. They just didn't use it much."** Khan Academy's chief learning officer Kristen DiCerbo — **"So far I am not seeing the revolution in education."** A geometry teacher stopped using it; engagement was stronger among administrators than teachers. DiCerbo identifies a structural problem: **"Students aren't great at asking questions well."** https://www.chalkbeat.org/2026/04/09/sal-khan-reflects-on-ai-in-schools-and-khanmigo/ [A/B — the single most useful source on the gap between claim and reality]

---

## 7. Separating the three categories explicitly

### (a) Research with real evaluation data — trust with caveats
EEF/NFER lesson-prep RCT (n=259 teachers, blinded quality panel) · Wharton/PNAS guardrails study (n≈1,000, causal, negative) · Tutor CoPilot RCT (n=700 tutors) · World Bank Nigeria RCT (n=800) · "Judging the Judges" (human validation of LLM judges, 648 outputs, 2 experts) · Bloom cognitive-depth study (20,700 questions) · physics lesson-plan multi-model evaluation (n=15 plans — small) · music/social-studies teacher-rating studies · LessonPlanLM vs real teacher plans · LearnLM expert-rater arenas.
**Systemic weakness across all of it: small expert panels (often 2), single topics, LLM judges, no long-run learning outcomes, almost nothing on multi-lesson sequences.**

### (b) Shipped products with genuine public technical detail
Duolingo's four-stage human/AI split · Oak National Academy Aila (RAG + content anchoring + codified pedagogy prompt + automated coherence/Americanism checks; open experiments at labs.thenational.academy) · Khan Academy's A/B testing writeup (15M threads, named guardrail metrics, honest about latency and error rates) · Merlyn Mind's 1–2% vs >10% hallucination comparison · Curipod's "no student-facing chatbot" architecture · Third Space Learning's 13-standard DfE compliance and safeguarding flags · CK-12's AI-GENERATED labelling with SME alternates · Coursera Course Builder (4,000+ enterprise courses, 87% median time reduction — vendor figure).

### (c) Marketing claims — no independent validation found
"Full-year scope and sequence with unit overviews and anchor texts, instantly" (generic AI curriculum generators, Kuraplan) · **LittleLit / AI Home Academy** — complete personalised K-12 homeschool curricula, textbooks, and 1:1 AI teaching, "calibrated to grade-level expectations", zero published evaluation, aimed directly at children with the least institutional oversight · Carnegie Learning's "trained on how students learn best" / "Large Math Model" framing (the ACT-R lineage is real; the LLM claim is unaudited) · MagicSchool's "6M+ educators, fastest growing school platform ever" (adoption, not quality) · Khan Academy's 22% vs 9% internal efficacy figure (non-randomised, self-selected) · Duolingo's "148 courses, doubling the catalogue in a year" (throughput, not quality — and contradicted by the insider quality report) · Alpha School's "2x learning" (top 1–2% MAP scores from a self-selected $40–75k/yr private cohort).

---

## 8. Blunt conclusions

1. **The artifact/sequence distinction is the whole game.** Everything that works is artifact-level. Everything that claims sequence-level is either unevaluated or evaluated by an LLM judge that agrees with human experts ~70% of the time.
2. **Grounding beats prompting.** The two clearest quality signals in the whole corpus are Merlyn's corpus restriction (1–2% vs >10% hallucination) and Oak's admission that quality degrades **when content lacks strong ties to existing Oak resources**. Retrieval into a human-authored corpus is the only mechanism with real evidence behind it. Schema and rubric alone produce well-formatted, low-Bloom, plausibly-wrong material.
3. **The failure mode is not gibberish — it is plausible mediocrity.** Correct-looking, well-structured, readable at the wrong grade level, pitched at Remember/Understand, "incidentally" aligned to standards, and impossible to run in a live classroom.
4. **The genuinely validated benefit is teacher time**, ~31% on lesson prep, quality-neutral, on *component* generation. That is a real and defensible product claim. "AI builds your curriculum" is not.
5. **If you build a curriculum builder for children:** own the scope-and-sequence as human-authored data, anchor generation to it via retrieval, enforce a schema, and put a mandatory human acceptance gate at the *sequence* level, not just the artifact level. Do not use an LLM judge as your quality bar. Expect Bloom-level drift upward and readability drift upward, and measure both explicitly.

---

## Sources

**Products / industry**
- https://blog.khanacademy.org/ai-lesson-plan-generator-khanmigo-kt/
- https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor/
- https://annualreport.khanacademy.org/
- https://www.chalkbeat.org/2026/04/09/sal-khan-reflects-on-ai-in-schools-and-khanmigo/
- https://www.chalkbeat.org/newark/2024/05/13/artificial-intelligence-khanmigo-chatbot-tutor-pilot-testing-districtwide-expansion/
- https://blog.duolingo.com/how-duolingo-experts-work-with-ai
- https://blog.duolingo.com/large-language-model-duolingo-lessons
- https://techcrunch.com/2025/04/30/duolingo-launches-148-courses-created-with-ai-after-sharing-plans-to-replace-contractors-with-ai
- https://www.thenational.academy/blog/understanding-the-ai-in-aila
- https://www.thenational.academy/blog/introducing-aila-for-ai-lesson-planning
- https://www.thenational.academy/blog/how-is-aila-impacting-teacher-lesson-planning-practices-workload-and-expertise-early-insights
- https://labs.thenational.academy/
- https://curipod.com/safe-ai-in-curipod
- https://thirdspacelearning.com/trust-compliance/dfe-generative-ai-product-safety-standards/
- https://www.merlyn.org/blog/merlyn-minds-education-specific-language-models
- https://help.ck12.org/hc/en-us/articles/18005531406875-The-Limitations-of-Flexi-s-Generative-AI
- https://blog.coursera.org/coursera-launches-course-builder
- https://www.magicschool.ai/tools/lesson-plan
- https://carnegielearning.medium.com/carnegie-learning-announces-livehint-ai-the-first-generative-ai-math-tutor-trained-to-think-like-517a910615e0
- https://www.sixredmarbles.com/insights/ai-and-human-insight-in-k-12-content-and-curriculum/
- https://schoolai.com/blog/ai-curriculum-generator
- https://www.littlelit.ai/ai-for-homeschooling-best-ai-app-for-homeschools
- https://aihomeacademy.com/curriculum

**Research**
- https://arxiv.org/abs/2508.19611 (Instructional Agents, EACL 2026) · https://aclanthology.org/2026.eacl-long.191/
- https://arxiv.org/abs/2504.05370 (EduPlanner)
- https://link.springer.com/chapter/10.1007/978-981-95-7138-3_11 (AgentLesson)
- https://arxiv.org/pdf/2508.16659 (Multi-agent learning designers, KLI)
- https://www.nature.com/articles/s41599-025-06004-2 (LessonPlanLM / knowledge-enhanced)
- https://link.springer.com/chapter/10.1007/978-3-031-64315-6_13 (self-critique prompting)
- https://arxiv.org/pdf/2510.19866 (physics lesson plans, 5 models × 3 frameworks)
- https://arxiv.org/html/2606.18257 (cognitive depth, 20,700 questions)
- https://arxiv.org/html/2602.13243 (Judging the Judges)
- https://arxiv.org/pdf/2604.25472 (SciEval)
- https://arxiv.org/html/2606.04846 (state standards alignment)
- https://arxiv.org/html/2605.09635v1 (K12-KGraph)
- https://arxiv.org/html/2506.22303v1 (Graph-RAG learning paths)
- https://arxiv.org/pdf/2501.12300 (KG completion for curriculum modelling)
- https://arxiv.org/html/2412.16429v1 · https://arxiv.org/pdf/2505.24477 (LearnLM)
- https://arxiv.org/abs/2601.06225 (Classroom AI, grade-specific finetuning, 208 participants)
- https://eric.ed.gov/?id=ED624058 (Bloom classification, 21,380 objectives, BERT F1 up to 0.95)
- https://www.pnas.org/doi/10.1073/pnas.2422633122 (GenAI without guardrails harms learning)
- https://edworkingpapers.com/ai24-1054 (Tutor CoPilot RCT)
- https://www.nfer.ac.uk/publications/chatgpt-in-lesson-preparation-a-teacher-choices-trial/
- https://educationendowmentfoundation.org.uk/projects-and-evaluation/projects/choices-in-edtech-using-generative-ai-chatgpt-for-ks3-science-lesson-preparation-2024-teacher-choices-trial
- https://blogs.worldbank.org/en/education/From-chalkboards-to-chatbots
- https://doi.org/10.1177/02557614241249163 (music lesson plans)
- https://journals.sagepub.com/doi/10.1177/0885985X251385910 (Bots and Beginners)
- https://onlinelibrary.wiley.com/doi/full/10.1111/jcal.13092 (AI vs human learning objectives)
- https://www.rand.org/pubs/research_reports/RRA4180-1.html (teacher AI adoption 25%→53%)
- https://theeconomyofmeaning.com/2026/04/30/ai-in-education-what-800-studies-do-and-dont-tell-us/

**Failures / oversight**
- https://www.business-standard.com/india-news/ai-under-scrutiny-after-1-678-errors-found-in-odisha-school-textbooks-126061901253_1.html
- https://www.commonsensemedia.org/press-releases/ai-teacher-assistants-need-better-safety-measures-common-sense-media-report-finds
- https://institute.commonsensemedia.org/risk-assessments/khanmigo
- https://www.edweek.org/technology/researchers-posed-as-a-teen-in-crisis-ai-gave-them-harmful-advice-half-the-time/2025/08
- https://www.cnn.com/2026/01/29/politics/alpha-school-trump-ai-teaching
- https://www.texastribune.org/2026/06/25/bluebonnet-learning-corrections-cost-texas-millions/
- https://www.simfinuk.com/resources/adults-who-work-with-young-people/dfe-generative-ai-product-safety-standards-updated-19-january-2026
- https://www.washingtontimes.com/news/2026/jul/14/allhere-chatbot-scandal-shows-not-deploy-ai/

**Confidence caveats:** I could not access full text for the Nature/HSSC LessonPlanLM paper, the JCAL learning-objectives paper (403), or the AgentLesson chapter (paywalled) — those entries rest on abstracts and secondary summaries. SciEval and arXiv 2508.16659 details come from PDF summarisation and should be verified before citing numerically.
