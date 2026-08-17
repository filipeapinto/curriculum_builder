# Research trigger: loss of control in recursively revised LLM specifications

Version: 1  
Triggered: 2026-08-17  
Owner: repository owner  
Target: `plans_internal/create_system_doc/create_system_doc.spec.v11.html`

## Trigger

After many iterations in which Codex and Claude generated, criticized, and repaired successive versions of a specification, the owner no longer has a confident mental model of the resulting artifact. Executing it may consume substantial time and money while faithfully producing a system that is no longer the one originally intended.

The first research pass responded with conventional requirements-management controls. The owner rejected that framing because LLM-driven work changes the operating environment: generation and revision are cheap and fast; specifications are active context and executable control surfaces; agents can recursively transform their own evaluation criteria; context is compressed; reviewers share model priors; and plausible agreement can mask correlated drift.

This rejection triggers a second, AI-native research pass.

## Research decision to support

Determine which control architecture can preserve meaningful human steering when LLM agents repeatedly revise specifications and review one another, and decide whether `create_system_doc.spec.v11.html` should be executed, re-anchored, experimentally probed, or replaced.

## Primary questions

1. What is materially different about intent preservation in LLM-driven work?
2. Why can reciprocal Codex/Claude review converge while still drifting from the owner's intent?
3. Which AI-native approaches have emerged: executable intent, context engineering, trace/eval systems, heterogeneous judges, debate protocols, agent harnesses, spec-driven development, uncertainty/escalation mechanisms, and reversible experiments?
4. Which approaches merely reproduce old process in new terminology?
5. What control loop fits this repository and the observed v1→v11 evolution?
6. What is the cheapest high-information action before committing to implementation?

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

## Required output

Create one engaging, self-contained HTML research report at `research_results.v1.html`. It must:

- link claims directly to sources;
- distinguish findings, inference, and recommendation;
- visualize the uncontrolled and controlled loops;
- analyze the local v1→v11 trajectory;
- compare candidate control architectures;
- recommend a concrete pre-execution experiment;
- state an explicit execution verdict;
- remain readable offline except for following source links;
- use no external scripts, fonts, or assets.

## Completion condition

Research is complete when the owner can use the report to choose among:

1. execute v11 unchanged;
2. re-anchor v11 and run a bounded probe;
3. reconstruct a replacement candidate from independent evidence;
4. abandon the specification family.

The report must not confuse a more elaborate process with restored control.
