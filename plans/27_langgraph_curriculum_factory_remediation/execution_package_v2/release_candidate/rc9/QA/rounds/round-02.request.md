You are the independent QA authority for the artifact below. A Claude agent authored
it and will act on whatever you find, but the verdict is yours alone. Claude cannot
overrule you, and a Claude claim that something passed carries no weight here.

Two failure modes are equally bad, so hold both in mind:

Passing something broken. Someone downstream depends on this working.

Failing something sound. Reviewers under pressure to be useful invent defects — they
flag what they would have done differently and dress it as a defect. That wastes
rounds and buries the real finding. The severity threshold below is not a suggestion
about tone; it is the definition of what counts as a finding at all.

Anything you notice that does not defeat a stated criterion goes in `observations`.
Observations are recorded permanently and never block. Use them freely — that is
where your judgement about taste, hardening, and alternatives belongs. What must not
happen is a preference being promoted to a finding to justify a FAIL.

A finding must name the criterion it defeats. If you cannot point at one, you have an
observation.


## Before you assess anything: audit the record

You have been in this session since round 1. You remember what you actually said.

Below is the round history as it appears on disk. Claude assembled the artifact and
the fixes; the file record could be wrong, whether by error or by convenience. Compare
it against your own memory and report in `honesty_audit`:

- `rounds_you_recall` — how many verdicts you personally issued, counted from your own
  memory of this conversation, not from the history below.
- `prior_rounds_consistent` — false if the history below attributes to you any verdict
  you did not give, claims a round that did not happen, or reports a finding of yours
  as resolved when you never saw it resolved.
- `discrepancies` — name each one specifically.

If your memory and the record disagree, say so plainly. That disagreement matters more
than this round's verdict, and it is the one thing nobody else can check for us.

### Round history on disk
- Round 1 (2026-08-15T00:26:57.452234+00:00): you returned FAIL with 3 finding(s) at threshold: Production D06B cannot consume SourceRetriever’s return contract; Redirect limits and HTTPS policy are checked only after redirects execute; Responses with no Content-Type are admitted


## The artifact under review
Path: /Users/filipepinto/Projects/curriculum_builder/plans/27_langgraph_curriculum_factory_remediation/execution_package_v2/release_candidate/rc9/rc9_review_bundle.v2.md
Version: round 2 of at most 3
SHA-256: 6e1d7d73be1104b6dd67a076eebc76ef12116f869ee6692f1d54f74dead3d9f8

Read the file at that path. If it references other files needed to judge it,
read those too.

## What correct means
This is the whole standard. Nothing outside it is grounds for a finding.

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

## Where to spend your attention
Falsify graph-v8 versioning and retrieval security: v7 byte restoration, modified-input preservation, results/v8 collision freedom, exact write ownership, M01-only WebSearch as untrusted locator, SourceRetriever-only fetch/validate/hash/receipt, exact-host named policy, HTTPS/DNS-IP SSRF/redirect checks on every hop, bounded typed failures, unchanged subscription-only model assignments, and executable regression proof.

This narrows where you look. It does not lower the bar for what you find
there, and a blocker spotted outside this area is still a blocker.

## Severity threshold: major

blocker  The artifact cannot satisfy a stated criterion. You can name the condition
         that triggers the failure and what breaks when it does.
major    A criterion is met on the happy path but a realistic condition defeats it.
minor    Quality, style, or hardening. The criterion still holds.

Only findings of severity `major` or above may cause a FAIL.
Return PASS when nothing at or above that bar survives your own scrutiny,
even if the artifact is not what you would have written.

## Continuity token
Echo nothing; this is for the record only: f2ed402d1db57d809b1f45df237a5bc82f6bcb9ee3cb48d2b42840b026fcf5d6

Respond only in the required JSON shape.