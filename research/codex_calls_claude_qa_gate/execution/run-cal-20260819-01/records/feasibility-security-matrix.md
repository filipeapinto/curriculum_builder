# Feasibility and security matrix

| Route | Support | Auth | Schema/usage | Isolation | Witness | Result |
|---|---|---|---|---|---|---|
| Claude CLI subprocess, safe mode | Official + locally tested | existing first-party Claude subscription | schema, session, tokens, estimated cost observed | separate process; no tools; no persistence; shared host | controller receipt + session/model/usage + input digest | **Feasible for constrained pilot** |
| Claude CLI subprocess, bare mode | Official | requires explicit API key/provider; subscription OAuth excluded | documented | strongest local prompt-loading suppression | same local limits | Defer unless dedicated API credential is provisioned |
| Claude Agent SDK / Messages API | Official | API/provider credential required | strongest programmatic semantics | application-defined | API request/response IDs possible | Candidate production architecture; not benchmarked here |
| Claude MCP/plugin route | Official MCP capability | configuration-dependent | integration-dependent | larger trust/config surface | implementation-dependent | No assurance advantage established; defer |
| Codex Sol ephemeral gate | Official + locally tested | ChatGPT subscription | schema and usage observed | fresh ephemeral read-only session | JSONL usage + digest-bound verdict | Feasible same-provider baseline |
| Codex Terra ephemeral gate | Official + locally tested | ChatGPT subscription | schema and usage observed | fresh ephemeral read-only session | JSONL usage + digest-bound verdict | Feasible independent-session comparator |

## Independence ratings

| Route | Process | Context | Model family | Vendor | Host integrity |
|---|---|---|---|---|---|
| Claude CLI | strong | strong under frozen safe-mode payload | distinct | distinct | weak/shared host |
| Codex Sol | strong | strong under ephemeral payload | producer-family baseline | same | weak/shared host |
| Codex Terra | strong | strong | related GPT-5.6 family, distinct variant | same | weak/shared host |

All unavailable, malformed, timed-out, over-budget, or digest-unbound results fail closed as `QA_ERROR`. No route is cryptographically independent on the shared host.
