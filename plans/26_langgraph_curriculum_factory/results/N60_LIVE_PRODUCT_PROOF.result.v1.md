# N60_LIVE_PRODUCT_PROOF result

status: NOT_AVAILABLE
node_prompt: plans/26_langgraph_curriculum_factory/prompts/N60_live_product_proof.prompt.v1.md (ee8ea92eef6ed8610c4ac273bbe7f0e263ac2f1ce2381d745751b7b48ca54588)

## Inputs
- N50_ADVERSARIAL_REGRESSION: 796e197370e486990f5d47636c8c714bbf62b5422de1bbad03cec72d546cfe7d
- plans/26_langgraph_curriculum_factory/spec/langgraph_curriculum_factory.spec.v1.md: 44e63e6271cae25f14f0bc970c598d1c15da41b67ae3cdf811bbb2f2303536e6 (sections 6.3, 7.3, 8.1, 12, 16 — Codex/Gemini transport, observed-identity requirement, live-preconditions checklist)
- runtime/run_curriculum.py: 76da9110121ede62a64f29585b840ac934828b41a6376831a355fa95519ec170 (production CLI entry, `--preflight`)

## Outputs
- plans/26_langgraph_curriculum_factory/results/N60_LIVE_PRODUCT_PROOF.result.v1.md: (this file; hashed externally by a later node)
- plans/26_langgraph_curriculum_factory/results/evidence/N60_LIVE_PRODUCT_PROOF: directory of 8 evidence files, see Commands

## Commands

1. `which codex gemini` / `codex --version` / `gemini --version`
   exit 0 — both executables resolved; identity captured in `evidence/cli_identity.txt` (`codex-cli 0.147.0`, `gemini 0.24.5`).

2. Inspect `~/.codex/auth.json` and environment
   exit 0 — `evidence/codex_auth_mode.txt`: `auth_mode: "chatgpt"`, `OPENAI_API_KEY: None`. Codex is authenticated via the user's ChatGPT subscription; no billed API key involved.

3. `cat ~/.gemini/settings.json`, `cat ~/.gemini/google_accounts.json`, env check
   exit 0 — `evidence/gemini_config.txt`: `selectedType: "gemini-api-key"`; `google_accounts.json.active: null` (no OAuth account signed in); `GEMINI_API_KEY` and `GOOGLE_API_KEY` unset in the shell environment.

4. `gemini -p "reply with the single word: PONG" </dev/null`
   **exit 41** — `evidence/gemini_auth_probe.txt`: `"When using Gemini API, you must specify the GEMINI_API_KEY environment variable."` This is a local capability probe only (per spec 8.1's "one local probe per capability, no curriculum model job"); no curriculum content was constructed or transmitted before this call, and the call carried none.

5. `curl -s -o /dev/null -w "http_code=%{http_code}" --max-time 5 https://api.openai.com` and `...generativelanguage.googleapis.com`
   exit 0 — `evidence/network_probe.txt`: `http_code=421` and `http_code=404` respectively — both endpoints are network-reachable, ruling out network egress as the blocker; the failure is authentication-only.

6. `/tmp/plan26_n30_verify/bin/python -m runtime.run_curriculum --engine-root <repo> --curriculum <repo>/curricula/arduino_kit --output-root /tmp/n60_live_proof_output_root --preflight`
   exit 0 — `evidence/preflight_stdout.json` / `evidence/preflight_stderr.txt` / `evidence/preflight_exit.txt`. The product's own D03 preflight reports `"ready": true` with all six capabilities (`model_cli_identity`, `retrieval`, `renderer`, `rasterizer`, `persistence`, `logger`) PASS — because that probe only proves executable identity/hash/version (spec 8.1's "executable identity mismatch, missing capability/authorization = system"), not live model-provider authentication. It does not invoke either CLI's model backend, so it cannot and does not detect the credential gap found in command 4. This node's own additional live-credential probe (command 4) is what surfaces the actual blocker.

## Tests

1. **Authorization and capabilities pass before any curriculum transmission.** — **FAIL**. Codex is authenticated (chatgpt subscription) and network egress to both providers is reachable, but Gemini — required by spec 6.3/7.3 for the M05/M07 cross-family review jobs, with no substitute permitted — cannot authenticate: `gemini-api-key` is the configured auth mode, no `GEMINI_API_KEY`/`GOOGLE_API_KEY` is set, and no Google OAuth account is signed in (`google_accounts.json.active: null`). A real, non-simulated Gemini invocation exits 41 before producing any output. This is a genuine external prerequisite absence, not an implementation defect: the runtime, transport, and preflight code built in N00-N50 are unaffected and the product's own `--preflight` reports `ready: true` (it does not probe live authentication). Per GOAL, this node performs **no partial transmission** and stops here.
2. One-unit run justifies actual `UNIT_ACCEPTED` — **NOT ATTEMPTED**. Blocked by Test 1; running `--unit` would place review work on the Gemini-required M05 edge, which cannot execute.
3. Resume/interruption preserves accepted bytes — **NOT ATTEMPTED**. No episode was created; there are no accepted bytes to preserve.
4. Full run justifies actual `COMPLETE` — **NOT ATTEMPTED**. Blocked by Test 1.
5. Independent recomputation matches terminal/checkpoint/evidence/artifact hashes — **NOT ATTEMPTED**. No terminal state exists to recompute.
6. No simulated/fake/prewritten/manual artifact appears in product evidence — **PASS**. No curriculum artifact was produced by this node; only real CLI/config probes (commands 1-6 above) are recorded, and every reported result is the literal output of a real command, not a substitute.

## Findings

- **Blocking cause (external prerequisite, not implementation)**: Gemini CLI (`/opt/homebrew/bin/gemini`, v0.24.5) has no usable credential in this environment. `~/.gemini/settings.json` selects `gemini-api-key` auth; `GEMINI_API_KEY`/`GOOGLE_API_KEY` are unset; no Google account is signed in for OAuth. Spec 6.3/7.3 hard-require live Gemini execution for M05/M07 review with no wrapper/API/simulated substitute permitted (spec line 865). This matches the project's standing constraint (no billed API keys exist for this user; only Claude Code and ChatGPT Pro/Codex subscriptions) — resolving it requires the user to either sign into the `gemini` CLI with an eligible Google/Gemini subscription account or provision a `GEMINI_API_KEY`, both outside this node's authorization per LOOP ("Do not broaden authorization, expose credentials"). Owner: none in this manifest — this is a live external-account precondition, tracked here for the user, not routed through `rework_edges.live_product_proof` (that edge is for implementation defects in the N60 proof harness itself, which none were found).
- **Re-verification**: this determination reproduces, unchanged, the same blocker found in the prior N60 attempt at this environment (identical executable hashes, identical auth state, identical preflight `ready: true` result). No drift in `runtime/run_curriculum.py` or the spec since that attempt (hashes match). The blocker is a stable environmental fact, not a transient probe failure.

## Invalidated descendants

None. This node reached no product terminal, so no downstream artifact depends on a claim this node did not make.
