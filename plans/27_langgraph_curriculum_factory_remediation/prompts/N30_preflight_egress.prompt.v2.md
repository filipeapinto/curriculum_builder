# GOAL

Make preflight, authentication, authorization, and the production CLI
truthful for the approved subscription-only production drivers, consuming
the `anthropic`/`openai`/`primary_source_hosts` egress boundary N20 now owns
and proves (moved from N30's v1 write set to N20's, per the v2 execution
package's correction of N20-F02 — see
`N20_provider_transport.prompt.v2.md`). Correct the exact Run 26 false-ready
condition before any curriculum content can be transmitted, and prove the
D03 tool/MCP-closure check v3 §7.1 class 5 requires.

This is the v2-package counterpart of `N30_preflight_egress.prompt.v1.md`.
That v1 prompt claimed N30 "owns only `egress.py`, the D03 input/capability
node, the production CLI, and the four exact tests declared in the graph" —
**this is no longer true.** `egress.py` and its direct test are N20-owned in
this graph; N30 consumes that boundary read-only, exactly as N30 already
consumed `routing.Selector`-style deterministic contracts in v1. Do not
recreate, shadow, or fork the egress module or its provider allowlist here;
if the boundary N20 shipped is wrong, that is an N20 defect to route back,
not something to patch locally.

# TEST

1. Define separate capability fields for executable identity, permitted auth
   mode, observable subscription-backed usability, required content-free
   operation, forbidden API-key absence, and approved data boundary — the
   first four proof classes of v3 §7.1.
2. Implement v3 §7.1 class 5 exactly as specified: D03 inspects the
   stream-json initialization event's tool and MCP-server lists directly and
   fails closed if any tool other than structured output, or any
   authenticated/invokable MCP-server tool, is present. A sandboxing flag
   (`--tools ""`, `--setting-sources ""`) is evidence of intent, never proof
   — do not accept flag presence as satisfying this class.
3. Require every mandatory field for every mandatory driver, across all five
   proof classes, before `ready: true`; one unknown or failed field makes
   readiness false and the CLI exit nonzero according to v3.
4. Reproduce the Run 26 defect: binaries present, one required provider
   unauthenticated. Assert preflight cannot return ready.
5. Reproduce N20-F06's live finding as a permanent regression case: an
   initialization event lists an MCP server under `--setting-sources ""`.
   Assert preflight still correctly evaluates tool-closure from the observed
   event (no tool granted) rather than either trusting the flag blindly or
   failing merely because a server is *listed*.
6. Cover executable spoofing, wrong auth mode, unavailable subscription,
   nonzero bounded probe, malformed output, model/driver mismatch, forbidden
   environment credential, unapproved endpoint, attempted fallback, and an
   exposed non-structured-output tool or an authenticated MCP-server tool.
7. Prove probes are content-free and transmit no curriculum artifacts, source
   text, PDFs, rendered pages, evidence, or user-owned files.
8. Prove the production CLI calls only N20-owned egress functions for
   authorization/transmission decisions — read-only consumption, no local
   reimplementation of the provider allowlist or data-class mapping.
9. Prove an unavailable approved driver produces an honest non-success state,
   never a fallback-provider recommendation or alternate-provider route.
10. Exercise the production CLI preflight path, not only helper functions.
11. Run focused preflight, CLI, capability-node, and adversarial tests and
    emit a schema-valid result.

N30 owns the D03 input/capability node, the production CLI, and its exact
tests declared in this graph — `egress.py` and its direct test are excluded
from N30's write set in this package. A provider-dispatch or egress-boundary
defect routes to N20; a graph-reachability defect routes to N40. Do not
rewrite their admitted outputs from this node. Remove every retired-provider
reference from N30-owned active tests and require the zero-occurrence test
scan (`check_forbidden_production_refs.py --node N30_PREFLIGHT_EGRESS`) to
remain green.

# LOOP

Classify each failure as capability semantics, production call-site wiring,
CLI status/exit mapping, or test fixture. If the failure traces to
`egress.py`'s own boundary rather than how N30 calls it, stop and route it to
N20 rather than patching it here. Repair the owning layer and rerun the
production-path negative case plus the full N30 slice. Never make readiness
easier to obtain to satisfy a test.
