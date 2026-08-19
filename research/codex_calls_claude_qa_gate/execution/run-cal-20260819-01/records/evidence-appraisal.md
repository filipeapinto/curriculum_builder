# Evidence appraisal and extraction

Full-review screening retained 22 of 24 calibration candidates; `SRC-018` was irrelevant and `SRC-022` inaccessible. No inclusion target was forced. Mechanism coverage converged across CLI, API/SDK, structured output, permissions, usage/cost, controller sandboxing, evaluator bias, and provenance.

| Evidence group | IDs | Appraisal | Extracted decision-relevant claims |
|---|---|---|---|
| Claude CLI/SDK automation | `SRC-001`–`SRC-004` | High authority/current official docs; locally corroborated at CLI 2.1.233 | `-p` supports non-interactive use; JSON/schema/session/usage and cost-estimate fields exist; bare mode avoids ambient customizations but requires API-key/provider auth. |
| Claude permissions/security | `SRC-005`–`SRC-008` | High authority; controls are client-enforced and version-sensitive | Safe mode disables project/user customizations while preserving auth; tool deny/removal and permission modes can bound agency; non-interactive trust behavior requires explicit hardening. |
| Anthropic API controls | `SRC-009`–`SRC-012` | High authority/current official API docs | Direct Messages/SDK route, structured outputs, token counting, and rate-limit evidence support a future service implementation; they do not by themselves create reviewer independence. |
| Codex controller/comparator | `SRC-013`–`SRC-016` | High authority/current official OpenAI docs; locally corroborated at CLI 0.147.0 | `codex exec` supports ephemeral scripted calls, read-only sandbox, JSONL usage, and output schema; MCP is available but adds configuration surface. |
| Judge reliability | `SRC-017`, `SRC-019`, `SRC-020` | Original empirical preprints; relevant but tasks differ from repository QA | MT-Bench reports useful human agreement alongside position/verbosity/self-enhancement biases. PoLL reports diverse panels outperforming one judge in its settings. Self-preference work reports measurable preference for familiar/lower-perplexity text. Generalization to code/document QA remains limited. |
| Provenance/security/implementation | `SRC-021`, `SRC-023`, `SRC-024` | Primary specification/guidance and official implementation | Artifact provenance concepts support digest-bound inputs and receipts; prompt injection and excessive agency are explicit threat classes; official SDK code is an inspectable alternative to CLI subprocess integration. |

## Claim links

- `CLM-001`: Claude Code officially documents programmatic non-interactive execution and schema-bound JSON. Evidence: [`SRC-002`](https://code.claude.com/docs/en/headless), [`SRC-001`](https://code.claude.com/docs/en/cli-reference).
- `CLM-002`: Safe automation must suppress ambient prompt/config loading and tools. Evidence: [`SRC-002`](https://code.claude.com/docs/en/headless), [`SRC-005`](https://code.claude.com/docs/en/permissions).
- `CLM-003`: Claude Sonnet 5 is pinned as `claude-sonnet-5` and listed at $2/MTok input, $10/MTok output at retrieval. Evidence: [Anthropic models overview](https://platform.claude.com/docs/en/about-claude/models/overview), [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- `CLM-004`: Codex supports non-interactive ephemeral/read-only/schema-bound comparison runs. Evidence: [`SRC-013`](https://learn.chatgpt.com/docs/developer-commands), [`SRC-014`](https://learn.chatgpt.com/docs/non-interactive-mode).
- `CLM-005`: LLM judging has known bias and a diverse panel may reduce intramodel bias, but vendor diversity is not proof of correctness. Evidence: [`SRC-017`](https://arxiv.org/abs/2306.05685), [`SRC-019`](https://arxiv.org/abs/2404.18796), [`SRC-020`](https://arxiv.org/abs/2410.21819).
- `CLM-006`: Digest-bound provenance and prompt-injection/agency controls are relevant assurance mechanisms. Evidence: [`SRC-021`](https://slsa.dev/spec/v1.2/provenance), [`SRC-023`](https://owasp.org/www-project-top-10-for-large-language-model-applications/).

## Contradictions and limits

Official feature availability establishes supported mechanisms, not empirical reliability. Research supporting panels/diversity is compatible with, but does not guarantee, improved repository QA. The benchmark found Claude less restrained than both Codex conditions on this small synthetic corpus, contrary to any presumption that cross-vendor review is inherently better. Client-reported Claude cost is an estimate; Codex ChatGPT-auth calls report tokens but no incremental per-call spend.
