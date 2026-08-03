# Cross-Family Structured Judge

## Why this thread

The only check in this pipeline that reads output the way a human would never
ran. `acceptance.json` for all four units records
`"routing_divergence": "USER_AUTHORIZED_IN_SESSION_MODEL; cross-family judge
bypassed"`, and `routing/authoring.json` gives the rationale: "user authorized
the current in-session LLM as the model worker; no separate API."

`policy/checks.v1.yaml` defines `REV-JUDGE-SINGLE-CROSS-FAMILY` as requiring
"exactly one judge invocation per pass, from a different model family than the
generator, with an explicit rubric and a randomised presentation order," and
marks it `deferred: RT-5`. So this is a documented deferral rather than a
silent bug — but the practical effect is that the authoring model was the only
model that ever looked at its own output, across an entire four-unit run in
which every unit shipped unreadable.

## Findings

**Self-preference bias is near-universal and does not shrink as models get
better, which is why the *family* must differ rather than merely the
instance.** Jinming Yang et al., "Quantifying and Mitigating Self-Preference
Bias of LLM Judges" (arXiv:2604.22891), builds a gold-standard-free framework
from equal-quality response pairs and evaluates 20 mainstream LLMs. The full
text states: "Under this criterion, 17 of the 20 models reach significance;
the three near-zero models do not, confirming that their observed SPB values
are indistinguishable from sampling noise." The paper reports that advanced
capability is "often uncorrelated, or even negatively correlated, with low
SPB," identifies "Machiavellian Judges" that recognise quality yet still
favour their own output, and measures bias for $77.81 against an estimated
$5,000-7,500 for human annotation. Implication for this pipeline: asking the
in-session authoring model to also evaluate its output is the exact
configuration this paper measures as unreliable, and it is what the bypass
produced.

**Structured, per-dimension scoring is itself a bias mitigation, not just a
reporting convenience.** The same paper finds that forcing a structured
multi-dimensional evaluation strategy rather than one holistic score reduces
self-preference bias by 31.5% on average. Implication: the judge should emit a
verdict per dimension — rendering, readability band, vocabulary cap, domain
accuracy, safety-block completeness — rather than a single accept/reject, and
this is a measured improvement rather than a stylistic preference.

**Adding more judges is not a substitute for choosing judges well.** Ma,
Zhang, Zhao et al., "Judging with Many Minds: Do More Perspectives Mean Less
Prejudice? On Bias Amplifications and Resistance in Multi-Agent Based
LLM-as-Judge" (arXiv:2505.19477), studies multi-agent debate and critic
configurations and frames bias amplification and bias resistance as competing
outcomes that depend on panel composition and disagreement handling.
Implication: this supports the existing policy decision to run exactly one
well-chosen cross-family judge rather than restoring a large panel — the fix
for the bypass is to un-defer the single judge, not to add more.

**Judge bias can be reduced without any human-labelled calibration set.** Liu
et al., "Mitigating Judgment Preference Bias in Large Language Models through
Group-Based Polling" (arXiv:2510.08145), introduces Genii, an unsupervised
multi-agent collaborative framework that "outperforms supervised models
trained on annotated judgment data, while requiring no human-labeled
annotations," and holds up "even when weaker models act as server agents."
Implication: a project with no human-rated corpus — which is this one — still
has a route to a calibrated judge.

**Production practice measures the judge against humans instead of trusting
it.** Gupta, Rossell, Alcobaça et al. (Nubank), "Building Customer Support AI
Agents at 100M-User Scale: An Evaluation-Driven Framework" (arXiv:2606.08867),
describes deploying agents to 100M+ users with "rigorous LLM judge evaluation
with measured inter-rater agreement and GEPA optimization for consistency,"
and reports that "A central insight is that evaluation-pipeline quality
directly determines iteration velocity." Implication: the judge is itself an
artifact with a measurable error rate; before it becomes the gate that admits
lessons, its agreement with a human rater should be measured on a small
sample.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Jinming Yang et al., "Quantifying and Mitigating Self-Preference Bias of LLM
  Judges," arXiv:2604.22891 — https://arxiv.org/html/2604.22891v4
- Ma, Zhang, Zhao et al., "Judging with Many Minds: Do More Perspectives Mean
  Less Prejudice? On Bias Amplifications and Resistance in Multi-Agent Based
  LLM-as-Judge," arXiv:2505.19477 — https://arxiv.org/pdf/2505.19477
- Liu et al., "Mitigating Judgment Preference Bias in Large Language Models
  through Group-Based Polling" (Genii), arXiv:2510.08145 —
  https://arxiv.org/abs/2510.08145
- Gupta, Rossell, Alcobaça et al., "Building Customer Support AI Agents at
  100M-User Scale: An Evaluation-Driven Framework," arXiv:2606.08867 —
  https://arxiv.org/abs/2606.08867

## Discarded

- `https://zylos.ai/research/2026-04-10-llm-as-judge-production-agent-verification-2026/`
  — **cited by the previous scan; discarded in this refresh.** The page still
  resolves, so a link-liveness check would have passed it. It fails on the
  source-quality bar instead: an unsigned industry synthesis on a vendor
  domain with no named author and no original data. Checking its attributions
  directly showed the previous scan's headline statistic — "more than half of
  surveyed production agent teams now rely on judge LLMs at runtime" — traces
  to LangChain's *State of Agent Engineering* finding that 57% of respondents
  had agents **in production**, which is a different proposition. Its
  "Galileo Luna-2 (3B-8B) achieves 0.88-0.95 accuracy... 97% cost reduction"
  figure is relayed from a Galileo marketing page with no benchmark paper,
  sample size, or methodology. Both numbers are dropped rather than re-cited
  weakly; arXiv:2606.08867 replaces this source's role in the thread with a
  named production deployment.
- The previous scan attributed arXiv:2604.22891 to "Chen et al." The first
  author is Jinming Yang. The paper's content and its 17-of-20 and 31.5%
  figures verified correctly; only the attribution was wrong, and it is
  corrected above rather than the source being dropped.
