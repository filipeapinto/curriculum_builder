# Full protocol approval record

- Approval ID: `APR-FULL-20260819-02`
- Human statements: `i approve`; followed by `dude i approve = move!!!!!!!`
- Interpreted authority: execute the full approved research protocol, including bounded synthetic Claude benchmark calls, within plan v1 ceilings and fail-closed controls.
- Recorded: 2026-08-19 (America/New_York)
- Route: local first-party Claude Code subprocess, version 2.1.233.
- Authentication: existing first-party `claude.ai` subscription session; status inspected without reading credential material.
- Reviewer model: pinned `claude-sonnet-5` (official model ID; Sonnet 5).
- Official standard price at retrieval: US$2/MTok input and US$10/MTok output.
- Per-call ceiling: US$0.25; Claude cumulative ceiling remains US$125; total research ceiling remains US$250.
- Invocation policy: `--safe-mode`, `--tools ""`, `--disallowedTools "mcp__*"`, `--permission-mode dontAsk`, `--no-session-persistence`, JSON output, JSON Schema, isolated synthetic case directory, 15-minute controller timeout.
- Corpus/controller: must be created, digested, deterministically tested, and secret-scanned before the first live call.

Any failure to observe model identity, usage, structured output, timeout control, or tool suppression closes the route as `QA_ERROR`.
