# QA criteria — Run 27 execution package v2 recovery rc9

The reviewed artifact is `rc9_review_bundle.v1.md`. Review it as the complete
versioned graph-v8 recovery candidate. Use the repository only for read-only
recomputation of hashes and commands named in the bundle. Do not treat earlier QA
verdicts as a verdict on rc9.

Report findings at severity `major` only when a realistic condition defeats a
numbered criterion. Put style or optional hardening in observations.

1. **RC9-T01 — v7 restoration and recovery preservation.** The live
   `implementation.graph.v7.yaml` hashes exactly to
   `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22`.
   The improperly modified bytes remain separately preserved at SHA-256
   `b6c17e81c6e32f32b86183d4577fe9a18894c0657504eca832e36d7daa17865e`.
   Every existing `results/v7/` artifact is preserved and graph v7 is not an
   admission target.
2. **RC9-T02 — true v8 versioning.** Graph v8, schema v5, contract v5, the
   three v8 prompts, scanner, validators, and tests all bind to graph v8 and
   `results/v8/`. No v8 result/evidence path collides with the legacy flat
   results root or `results/v7/`. Validator graph/schema/contract/result
   bindings are explicit and internally consistent.
3. **RC9-T03 — topology and authority unchanged.** Node order is exactly
   N00→N10→N20→N30→N40→N50→N60→N70→N80→N90; edges and legal terminals are
   unchanged. The approved source specification, its witnessed QA record, rc3
   package-structure approval, and all eight model/effort assignments are
   carried forward exactly. Execution remains subscription CLI-only.
4. **RC9-T04 — recovered ownership is complete and non-overlapping.** N30 owns
   `nodes/sources.py`, `runtime/run_curriculum.py`,
   `policy/retrieval_hosts.v1.yaml`, `schemas/curriculum.schema.v5.json`,
   the selected arduino manifest, and direct N30 tests. N40 owns
   `nodes/__init__.py`. N20 retains sole ownership of `egress.py` and its
   direct tests; N30 consumes it read-only. No write path has two owners.
5. **RC9-T05 — WebSearch is locator-only and M01-only.** Only M01 DISCOVER may
   receive Claude WebSearch. Its output is an untrusted locator candidate.
   It cannot become admitted evidence without deterministic SourceRetriever
   fetch, validation, content hashing, and receipt creation. No other worker
   receives WebSearch or unrestricted tooling.
6. **RC9-T06 — named exact-host policy.** Curricula select a named profile and
   cannot supply hosts. The electronics profile contains exactly:
   `learn.sparkfun.com`, `docs.arduino.cc`, `www.arduino.cc`,
   `learn.adafruit.com`, `support.microbit.org`, `www.cpsc.gov`, and
   `www.allaboutcircuits.com`. Wildcards, URLs, mixed-case hosts, duplicate
   hosts, unknown profiles, and model-driven expansion fail closed.
7. **RC9-T07 — per-hop retrieval enforcement.** SourceRetriever remains the
   only fetch path and enforces HTTPS, exact host, DNS resolution, public-IP
   and rebinding checks, redirects at every hop, redirect bounds, response
   size/type/status limits, authorization/data-class matching, content hash,
   and receipt append. Model endpoints and private/link-local/loopback
   addresses fail closed.
8. **RC9-T08 — policy binding and bounded failure.** The selected profile,
   resolved ordered hosts, and policy-file digest are bound into authorization
   and execution evidence. Missing/unknown policy or an unavailable verified
   source yields a typed bounded failure, never a fabricated URL, fake receipt,
   vacuous success, alternate-provider fallback, or `NOT_AVAILABLE`
   substitution for a repairable subscription path.
9. **RC9-T09 — billed model paths remain impossible.** No billed API key,
   provider SDK, direct model HTTP call, custom endpoint, alternate provider,
   wildcard authority, or unrestricted worker environment can activate a
   production model route. Claude and Codex subscription CLIs retain their
   approved model/effort identities.
10. **RC9-T10 — positive and negative automated proof.** The package suite and
    N20/N30 runtime suites genuinely exercise the exact-host loader,
    unknown/wildcard/URL rejection, source fetch authorization, HTTPS/SSRF/DNS
    rebinding/redirect denial, M01-only WebSearch grant, untrusted-locator
    validation, policy binding, and versioned graph/result invariants. The
    deterministic validation record must match executable repository behavior,
    not merely narrative.
11. **RC9-T11 — baseline exception is proved, not waived.** The only permitted
    legacy N10 mismatch is reproduced against unmodified `HEAD`; the live and
    `git show HEAD` bytes have the same stated hash and differ from the older
    hash in the admitted historical result. No v8 result may inherit that
    mismatch.
12. **RC9-T12 — historical preservation and executable plan.** rc1–rc8, their
    QA sessions, all earlier graphs/schemas/contracts/prompts, v7 results and
    evidence, and failed live attempts remain readable and unmodified. The
    active plan validator returns `valid:true`, the package suite passes, and
    the v8 graph has a collision-free executable route through N90.

Falsify the bundle's claims where possible. Pay particular attention to a host
being checked only before the first request but not after redirects/DNS changes;
WebSearch data bypassing SourceRetriever; graph-v8 write ownership omitting a
live-modified file; stale v7 paths hidden in v8 prompts/validators; a structured
contract digest disagreeing with live bytes; and tests whose fixture bypasses the
production call site.
