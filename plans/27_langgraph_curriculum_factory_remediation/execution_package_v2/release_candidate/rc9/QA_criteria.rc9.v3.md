# QA criteria — Run 27 rc9 correction round 3

The reviewed artifact is `rc9_review_bundle.v3.md`. This is the final
correction successor to failed v1 and v2 artifacts; both artifacts and both
prior QA rounds remain immutable. The complete round-2 criteria are incorporated
by reference from `QA_criteria.rc9.v2.md` at SHA-256
`9bd7a6be133b45c231786b9d7b58b4cbb7372b9ca934b637a22ab64c866da92f`
and are embedded immediately after this addendum.

Round 2 confirmed the production fixes for `RC9-QA-001`, `RC9-QA-002`, and
`RC9-QA-003`, but retained `RC9-QA-002` solely because tests did not execute
the nested urllib handler in the production `_default_opener`. V3 adds a direct
regression with this exact obligation:

1. Import and call production `_default_opener`, not a SourceRetriever opener
   stub.
2. Make the production nested `_Tracker.redirect_request` receive a redirect.
3. Instrument the stdlib superclass `HTTPRedirectHandler.redirect_request` so
   construction of the follow-up request is observable.
4. Have the real production callback deny the redirect.
5. Prove the only observed event is validation: neither superclass request
   construction nor a would-follow event may occur.
6. The test must fail if the production callback is removed or moved below
   `super().redirect_request`.

All twelve criteria in v2 remain mandatory, including exact v7 preservation,
true v8 namespace/version binding, unchanged topology/provider architecture,
non-overlapping ownership, M01 locator-only search, exact-host policy,
pre-follow per-hop enforcement, the real D06B `(body, receipt)` contract and
hash-bound bytes, no billed model path, positive/negative executable proof,
the proved legacy baseline exception, and complete historical preservation.

Falsify the new direct test by inspecting its exact production call path and,
if useful, by reasoning through removal or relocation of the callback. A canned
opener that merely imitates callback order does not satisfy this addendum.
