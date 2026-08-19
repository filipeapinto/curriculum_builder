# Local capability inventory

Observation timestamp: 2026-08-19 05:22–05:25 EDT. Collection was read-only and did not invoke a model or inspect authentication/session contents.

## Observed executables

| ID | Path | Version | SHA-256 |
|---|---|---|---|
| `TOOL-CLAUDE-01` | `/opt/homebrew/bin/claude` | Claude Code 2.1.233 | `bc466b6cde63edafc773f471a1fb98787fabb31f52240c8616ce7e1f587b212d` |
| `TOOL-CODEX-01` | `/opt/homebrew/bin/codex` | codex-cli 0.147.0 | `19c4f144c5226a9f17c58e6f0fa854843b0f77a6eb420f40e2745a12f10f5d37` |

## Help-advertised Claude route

Claude advertises non-interactive `-p/--print`, `json` and `stream-json` output, `--json-schema`, `--max-budget-usd`, model selection, session IDs, no-session-persistence, permission modes, tool allow/deny controls, MCP configuration, strict MCP mode, safe mode, and bare mode. Bare mode states that it skips hooks, plugins, MCP discovery, auto-memory, keychain reads, and project instruction discovery, but still requires explicitly supplied API/provider credentials. Help also warns that non-interactive mode skips the workspace trust dialog.

This supports a *candidate subprocess architecture*. It does not establish working authentication, license/subscription suitability, actual cost bounding, runtime reliability, or reviewer independence.

## Help-advertised Codex route

Codex advertises `exec` and `review` non-interactive commands, read-only/workspace-write/danger-full-access sandboxes, approval policies, ephemeral sessions, ignored user config/rules, JSONL events, final-output schemas, explicit output files, and external MCP management. `codex sandbox` exposes readable-root and network-disable controls. Current official OpenAI documentation confirms `codex exec` defaults to a read-only sandbox and supports JSONL and output-schema operation.

## Repository precedent

The repository contains `.claude/skills/qa-gate-codex-run/`, a Claude→Codex protocol with versioned artifacts, schema-validated verdicts, PASS/FAIL/ERROR separation, hashes, session witnesses, bounded iterations, isolated execution copies, and postmortems. Its recorded digests are:

- skill: `6a61b15379dda535bdeac44486c28a7ab993f998380900ac65061f1b2f169bf1`
- protocol: `7366b6fc211b0c2871a1ac5887d3d8fbdf8c0e69fc0e64a7f3993fd086aa67f2`

It is useful protocol precedent only. Its Claude-specific plugin bridge does not prove the reverse Codex→Claude route.

## Unavailable or deliberately untested

- Authentication status and credential stores: excluded from calibration inspection.
- Live Claude/Codex inference: not authorized.
- Provider usage/cost fields: documented, not empirically verified.
- CLI exit/failure behavior under missing auth, timeout, malformed schema, or prompt injection: reserved for the second-gate benchmark.
- Host-level independence: unavailable because both CLIs would execute under the same user/host unless a later protocol selects remote isolation.
