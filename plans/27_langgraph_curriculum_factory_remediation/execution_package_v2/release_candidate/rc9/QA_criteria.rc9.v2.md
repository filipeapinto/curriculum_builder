# QA criteria — Run 27 execution package v2 recovery rc9, correction round 2

The reviewed artifact is `rc9_review_bundle.v2.md`. It supersedes the failed
`rc9_review_bundle.v1.md` without modifying that artifact or its round-1 QA
record. Review v2 as the complete graph-v8 recovery candidate. Use the
repository only for read-only recomputation of hashes and commands named in the
bundle. Do not treat any earlier QA verdict as a verdict on v2.

Round 1 returned three findings that v2 must close at the production boundary:

- `RC9-QA-001`: D06B must consume SourceRetriever's real `(body, receipt)`
  contract, verify the receipt digest, persist the retrieved bytes, and stage
  those exact hash-bound bytes for M01 interpretation.
- `RC9-QA-002`: redirect scheme, exact host/port, DNS/IP, rebinding, and count
  checks must run before every redirected request is followed, including HTTPS
  downgrade attempts and the first redirect beyond the configured bound.
- `RC9-QA-003`: a missing Content-Type must fail closed rather than being
  admitted as an allowed response.

Numbered acceptance criteria:

1. **RC9-T01 — v7 restoration and recovery preservation.** The live
   `implementation.graph.v7.yaml` hashes exactly to
   `b7e52ae7f2c8d1eb3984fcea014063a3be29eb88cf7cc5980bdb9ef503728c22`.
   The improperly modified bytes remain separately preserved at SHA-256
   `b6c17e81c6e32f32b86183d4577fe9a18894c0657504eca832e36d7daa17865e`.
   Existing `results/v7/` artifacts remain immutable and graph v7 is not an
   admission target.
2. **RC9-T02 — true v8 versioning.** Graph v8, schema v5, contract v5, all v8
   prompts, scanner, validators, and tests bind to graph v8 and `results/v8/`.
   No v8 result/evidence path collides with legacy results.
3. **RC9-T03 — topology and authority unchanged.** Node order is exactly
   N00→N10→N20→N30→N40→N50→N60→N70→N80→N90. Edges, legal terminals, source
   specification, witnessed approval, model/effort assignments, and
   subscription-CLI-only execution are carried forward.
4. **RC9-T04 — complete, non-overlapping ownership.** N20 owns `egress.py` and
   its direct tests. N30 owns `nodes/sources.py`, `runtime/run_curriculum.py`,
   the retrieval policy, curriculum schema/manifest, and direct N30 tests. N40
   owns `nodes/__init__.py`. Every changed production-facing path is in exactly
   one v8 write set.
5. **RC9-T05 — locator-only M01 WebSearch.** Only M01 DISCOVER receives Claude
   WebSearch; its output is an untrusted locator. No locator becomes evidence
   without deterministic SourceRetriever fetch, validation, hashing, receipt,
   byte persistence, and hash-bound staging for M01 INTERPRET.
6. **RC9-T06 — named exact-host policy.** Curricula select a named profile and
   cannot supply hosts. The electronics profile contains exactly
   `learn.sparkfun.com`, `docs.arduino.cc`, `www.arduino.cc`,
   `learn.adafruit.com`, `support.microbit.org`, `www.cpsc.gov`, and
   `www.allaboutcircuits.com`. Wildcards, URLs, mixed-case or duplicate hosts,
   unknown profiles, and model-driven expansion fail closed.
7. **RC9-T07 — per-hop pre-follow enforcement.** SourceRetriever is the only
   fetch path. It enforces authorization/data class, HTTPS, exact pinned
   host/port, DNS resolution, public-IP and rebinding checks before the initial
   request and before every redirect request. It denies the first hop beyond
   the redirect limit without requesting it, validates the final URL again,
   bounds the read, requires status 200 and an explicit allowed Content-Type,
   hashes the body, and appends a schema-valid receipt. Model endpoints,
   downgrade redirects, cross-host redirects, and private/link-local/loopback
   addresses fail closed.
8. **RC9-T08 — tuple contract and byte identity.** The production D06B call
   consumes exactly `(body: bytes, receipt: mapping)`, requires
   `bytes_sha256`, `http_status`, and `content_type`, verifies that the body
   matches `bytes_sha256`, persists bytes under a content-addressed path, and
   supplies a staged-input record with that same path and digest. Contract
   drift is a typed system failure; missing required facts remain bounded
   prerequisite failures.
9. **RC9-T09 — policy binding and no billed path.** The selected profile,
   resolved ordered hosts, and policy digest are evidence-bound. No billed API
   key, provider SDK, direct model HTTP call, custom endpoint, alternate
   provider, wildcard authority, or unrestricted worker environment can
   activate a production model route.
10. **RC9-T10 — positive and negative executable proof.** Tests compose the
    actual SourceRetriever and D06B implementations, exercise callback-based
    pre-follow redirect validation, denial before an excess-hop request,
    HTTPS-downgrade denial, absent Content-Type denial, tuple/hash-bound byte
    staging, exact-host loading, SSRF/DNS-rebinding denial, M01-only WebSearch,
    policy binding, and graph/result versioning. Fixtures may not bypass the
    production return contract.
11. **RC9-T11 — baseline exception is proved, not waived.** The sole legacy
    N10 changed-file mismatch is reproduced against unmodified `HEAD`; the live
    and `git show HEAD` bytes have the stated identical hash and differ from
    the old historical result. No v8 admission inherits the mismatch.
12. **RC9-T12 — preservation and executable plan.** rc1–rc8, earlier graphs,
    schemas, contracts, prompts, QA sessions, v7 results/evidence, failed live
    attempts, the failed rc9 v1 artifact, and its round-1 record remain readable
    and unmodified. The active plan validator returns `valid:true`, the package
    and runtime suites pass, scanners report zero violations, and v8 has a
    collision-free executable route through N90.

Falsify these claims where possible. In particular, inspect the actual opener's
redirect handler rather than only canned response metadata; verify that a
redirect is checked before urllib follows it; compose the real D06B call with
the real SourceRetriever return shape; confirm persisted bytes match the
receipt; and ensure missing Content-Type cannot be normalized into acceptance.
