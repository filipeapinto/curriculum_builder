# Research trigger: loss of control in recursively revised LLM specifications

Version: 1  
Triggered: 2026-08-17  
Owner: repository owner  
Target: `plans_internal/create_system_doc/create_system_doc.spec.v11.html`

## Trigger

After many iterations in which Codex and Claude generated, criticized, and repaired successive versions of a specification, the owner no longer has a confident mental model of the resulting artifact. Executing it may consume substantial time and money while faithfully producing a system that is no longer the one originally intended.

The first research pass responded with conventional requirements-management controls. The owner rejected that framing because LLM-driven work changes the operating environment: generation and revision are cheap and fast; specifications are active context and executable control surfaces; agents can recursively transform their own evaluation criteria; context is compressed; reviewers share model priors; and plausible agreement can mask correlated drift.

This rejection triggers a second, AI-native research pass.

## Research need

Establish a reusable, trigger-independent body of evidence about control and intent preservation when LLM agents repeatedly revise artifacts and review one another. After the SME research is complete, a separate general-purpose analysis may apply it to the target that caused this trigger.

## Primary questions

1. What is materially different about intent preservation in LLM-driven work?
2. Why can reciprocal Codex/Claude review converge while still drifting from the owner's intent?
3. Which AI-native approaches have emerged: executable intent, context engineering, trace/eval systems, heterogeneous judges, debate protocols, agent harnesses, spec-driven development, uncertainty/escalation mechanisms, and reversible experiments?
4. Which approaches merely reproduce old process in new terminology?
5. Which mechanisms and control patterns generalize across domains and agent platforms?
6. What are the evidence limits and unresolved research questions?

## Evidence boundary

- Prefer 2024–2026 primary research, official platform engineering material, active specifications, and current tool documentation.
- Older sources may be used only where they define a still-relevant mechanism; they must not drive the proposed operating model.
- Treat vendor claims as evidence of available patterns, not independent proof of effectiveness.
- Treat agreement among LLMs as correlated evidence, not truth.
- Separate repository observations from external claims.
- Hyperlink every externally supported claim in the results.

## Required AI-native failure modes

The research must explicitly examine:

- recursive semantic drift across full rewrites;
- lossy compaction and context pollution;
- preference leakage and same-family/self-preference in LLM judges;
- evaluator/spec co-adaptation and Goodhart-like optimization;
- correlated blind spots in multi-agent debate;
- authority laundering, where agent-generated text later appears as an accepted requirement;
- verification capture, where tests generated from the mutated spec prove only self-consistency;
- escalating token/tool cost and autonomous surface-area growth;
- human review overload and plausible-text rubber stamping;
- irreversible actions taken before uncertainty is surfaced.

## Required separation of outputs

The research process has two epistemically distinct outputs:

1. `research_results.v2.html` — a trigger-agnostic synthesis produced from independent SME research. It may contain general evidence-backed findings, evidence limitations, reusable mechanisms, and clearly labeled design proposals. It must not mention or assess the triggering repository artifact.
2. `research_application.v1.html` — a separate general-agent application of the completed research to the trigger. It owns all repository observations, mappings, inferences, recommendations, and execution verdicts.

Both outputs must hyperlink externally supported claims to their sources, remain readable offline except for following source links, and use no external scripts, fonts, or assets.

## Completion condition

Research is complete when the reusable SME synthesis is valid without knowledge of this trigger. Application is complete when a separate agent transparently maps that synthesis to the triggering evidence and exposes its reasoning without altering the research layer.
