# GOAL

Make preflight, authentication, authorization, and egress truthful for the
approved subscription-only production drivers. Correct the exact Run 26
false-ready condition before any curriculum content can be transmitted.

# TEST

1. Define separate capability fields for executable identity, permitted auth
   mode, observable subscription-backed usability, required content-free
   operation, forbidden API-key absence, and approved data boundary.
2. Require every mandatory field for every mandatory driver before
   `ready: true`; one unknown or failed field makes readiness false and the CLI
   exit nonzero according to v2.
3. Reproduce the Run 26 defect: binaries present, one required provider
   unauthenticated. Assert preflight cannot return ready.
4. Cover executable spoofing, wrong auth mode, unavailable subscription,
   nonzero bounded probe, malformed output, model/driver mismatch, forbidden
   environment credential, unapproved endpoint, and attempted fallback.
5. Prove probes are content-free and transmit no curriculum artifacts, source
   text, PDFs, rendered pages, evidence, or user-owned files.
6. Prove runtime egress admits only approved source retrieval and registered
   sandboxed model-driver operations with least-privilege staged inputs.
7. Prove an unavailable approved driver produces an honest non-success state,
   never a Gemini/API-key recommendation or alternate-provider route.
8. Exercise the production CLI preflight path, not only helper functions.
9. Run focused preflight, CLI, capability-node, egress, and adversarial tests and
   emit a schema-valid result.

N30 owns only `egress.py`, the D03 input/capability node, the production CLI, and
the four exact tests declared in the graph. A provider-dispatch defect routes to
N20; a graph-reachability defect routes to N40. Do not rewrite their admitted
outputs from this node. Remove every retired-provider reference from N30-owned
active tests and require the zero-occurrence test scan to remain green.

# LOOP

Classify each failure as capability semantics, production call-site wiring,
egress boundary, CLI status/exit mapping, or test fixture. Repair the owning
layer and rerun the production-path negative case plus the full N30 slice.
Never make readiness easier to obtain to satisfy a test.
