# Video summary — HTML-first artifacts for agent-assisted work

## Source and status

- **Video:** [Markdown vs HTML: Why Anthropic's Claude Code Team Chose Wrong First? Or Not?](https://www.youtube.com/watch?v=-iSLQe_imrE)
- **Creator:** [DIY Smart Code](https://www.youtube.com/@DIYSmartCode)
- **Accessed:** 2026-08-15
- **Status:** practitioner commentary; useful for workflow framing, not evidence that a format change improves this repository’s runtime correctness.

The video summarizes Thariq Shihipar’s argument that, when an agent creates a
document primarily for human review, self-contained HTML is often a more useful
surface than Markdown. The central claim is not that Markdown cannot represent
technical facts, but that HTML can present them with visual hierarchy,
navigation, diagrams, images, styles, and small interactions that make a person
more likely to inspect and challenge an agent’s work.

## Main claims presented

1. **HTML has a richer presentation vocabulary.** The video contrasts
   Markdown’s text-oriented headings, lists, and tables with HTML’s ability to
   include CSS, SVG, images, spatial layout, and JavaScript-driven controls in
   one portable file. A real SVG chart is offered as an alternative to an
   agent-generated ASCII chart.
2. **The goal is active human review.** A readable, navigable HTML plan may
   help a person compare options, follow a flow, and give feedback instead of
   skimming a long Markdown plan and delegating the decisions to the agent.
3. **The trade-off is token and generation cost.** The video estimates HTML
   output can cost roughly two to four times as many tokens as Markdown. It
   argues this cost is tolerable when the document will be read or reused.
4. **Candidate uses are visual specifications, code-review explainers, design
   prototypes, research/status reports, and one-off editing interfaces.** A
   disposable HTML tool can be appropriate when direct text editing is not a
   good way to express a decision.
5. **Context determines quality.** The video credits a coding agent’s access
   to the repository, Git history, connected tools, and browser context for
   making the resulting HTML informed rather than merely polished.

## Application to this repository

This supports the recommendation in
[`html_documentation_skills_assessment.v1.html`](html_documentation_skills_assessment.v1.html): use HTML directly for reader-facing architecture explainers,
graph documentation, reports, and review artifacts when visual structure or
interaction improves review.

It does **not** change the source-of-truth rule. Graph definitions, schemas,
route policy, run receipts, and checks must remain deterministic and verifiable
inputs. HTML is the review and communication layer built from, or checked
against, those inputs. A visually persuasive page must not be allowed to
substitute for executable evidence.

## Practical adoption rule

| Intended reader and task | Preferred artifact |
| --- | --- |
| Agent input, diff-friendly policy, compact durable notes | Markdown, JSON, YAML, or code as appropriate |
| Human comparison, architecture explanation, visual QA report, or interactive decision aid | Self-contained HTML with a readable no-JavaScript baseline |
| Runtime state, claims requiring proof, routing, or acceptance evidence | Validated structured data and receipts; render HTML only as a derivative |

For an HTML deliverable here, retain the assessment’s safeguards: semantic
HTML, no CDN dependency, accessible SVG/text alternatives, visible failure
paths, source links for claims, and an explicit freshness timestamp or
verification status.

## Related repository material

- [`html_documentation_skills_assessment.v1.html`](html_documentation_skills_assessment.v1.html) — recommended HTML-documentation pattern and quality constraints.
- [`../rendering_gap_scan/rendered_page_visual_qa.md`](../rendering_gap_scan/rendered_page_visual_qa.md) — why a rendered artifact needs meaningful visual QA rather than a superficial render check.
- [`../../how_it_works.md`](../../how_it_works.md) — an existing system narrative that is a strong candidate for an HTML explainer.
