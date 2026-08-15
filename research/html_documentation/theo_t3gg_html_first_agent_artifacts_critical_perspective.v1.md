# Critical practitioner perspective — HTML-first agent artifacts

## Source and status

- **Video:** [Stop letting your agents write Markdown.](https://www.youtube.com/watch?v=S9EGx6ik-18)
- **Creator:** [Theo — t3.gg](https://www.youtube.com/@t3dotgg)
- **Accessed:** 2026-08-15
- **Status:** practitioner critique and workflow guidance; not primary evidence for a universal format choice.

This video responds to Thariq Shihipar’s HTML-first workflow and argues that
HTML is a valuable additional surface for agent outputs, but not a general
replacement for Markdown. Its most useful contribution is identifying the
adoption constraints that an HTML-first argument can obscure.

## What it adds

1. **Avoid HTML maximalism.** Markdown remains useful for compact, plain-text,
   diff-friendly, long-lived notes and specifications. HTML is most persuasive
   when hierarchy, comparison, interaction, or visual explanation materially
   improves a human review task.
2. **HTML has genuine operating costs.** Generated HTML can become token-heavy,
   visually over-designed, hard to inspect in version-control diffs, and less
   portable than its author expects—especially on small screens. These costs
   should be accepted for a specific review benefit, not by default.
3. **The novelty effect is not proof of durable readability.** A polished HTML
   page may attract more attention today; that does not guarantee every future
   HTML report will be read. Document length and information design still
   matter.
4. **Assets and complex visual rendering remain unreliable.** Agents can
   hallucinate image URLs or produce weak SVG/layout output. An HTML artifact
   needs local, verified assets and rendered-page review, not faith in the
   markup alone.
5. **Learn with direct prompting before creating a skill.** Ask for a targeted
   HTML artifact, observe the recurring successes and failures, and only then
   codify stable requirements into a reusable skill. A generic “make HTML”
   skill risks recreating a repetitive visual style without solving the actual
   decision problem.
6. **Disposable interfaces can be valuable.** A one-off editor or playground
   can make a complex choice easier than a text box. It should have a clear
   import/export boundary—such as JSON, CSV, or a prompt—and need not be
   promoted into a persistent product.

## Application to this repository

The appropriate rule is **format by purpose**, not “HTML everywhere.”

| Purpose | Default form |
| --- | --- |
| Contracts, graph definitions, policies, schemas, receipts, and accepted evidence | Versioned structured data, code, or compact text; deterministic validation required |
| Reader-facing architecture explanation, option comparison, visual QA report, or interactive decision aid | Self-contained HTML when it makes review meaningfully better |
| Temporary exploration or data manipulation | Throwaway HTML tool with explicit import/export; do not add it to a durable workflow without a demonstrated recurring need |

For repository-owned HTML documentation, retain the safeguards already proposed:
semantic HTML, no hidden CDN/network dependency, accessible no-JavaScript
content, text alternatives for diagrams, locally resolving assets, and explicit
freshness/provenance. HTML must remain a derivative presentation of validated
runtime facts, never their substitute.

## Related material

- [`html_documentation_skills_assessment.v1.html`](html_documentation_skills_assessment.v1.html) — repository recommendation: use HTML for human-facing documentation while extracting/validating runtime facts deterministically.
- [`diy_smart_code_html_first_agent_artifacts_video_summary.v1.md`](diy_smart_code_html_first_agent_artifacts_video_summary.v1.md) — HTML-first practitioner framing and use cases.
- [`../rendering_gap_scan/rendered_page_visual_qa.md`](../rendering_gap_scan/rendered_page_visual_qa.md) — why merely rendering an artifact does not establish visual quality.
