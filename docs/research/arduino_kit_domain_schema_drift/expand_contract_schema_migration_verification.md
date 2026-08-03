# Expand/contract schema migration verification

## Why this thread

The commit that rewrote `domain.schema.v1.json` to require `electrical` +
`build_map` changed the contract but did not touch `l01_unpowered_power_path.json`,
the one content file that existed under the old contract at the time. There
was no intermediate period where both shapes were accepted, no tracked
follow-up to migrate `l01`, and no gate that would have stopped `l02`-`l04`
from being freshly authored against the now-stale shape afterward. This
thread asks what established software-engineering practice says about
carrying a breaking contract change through to every existing referent,
independent of the LLM-specific angle covered in the structured-output
thread.

## Findings

**The expand/contract (parallel change) pattern exists precisely to prevent a
breaking schema change from leaving some referents on the old shape
indefinitely.** The pattern splits a breaking change into an expand phase
(support both old and new shapes), a migrate phase (backfill/dual-write), and
a contract phase (remove the old shape only once every reader and writer uses
the new one) — and explicitly warns that teams should move through the phases
"as brisk a pace as their deployment schedule allows" rather than lingering in
a mixed state (Pete Hodgson, *Expand/Contract: making a breaking change
without a big bang*,
blog.thepete.net/blog/2023/12/05/expand/contract-making-a-breaking-change-without-a-big-bang/).
Implication for this pipeline: `domain.schema.v1.json` went straight to
"contract" (old shape rejected outright, `additionalProperties: false`) with
no expand phase and no tracked migration step for `l01`, and no equivalent
gate stopped `l02`-`l04` from being drafted against the abandoned old shape
afterward — the pattern this repo followed had the failure mode this
methodology names, not an edge case of it.

## Sources (all fetched and verified to resolve to real, on-topic content)

- Pete Hodgson, *Expand/Contract: making a breaking change without a big bang* — https://blog.thepete.net/blog/2023/12/05/expand/contract-making-a-breaking-change-without-a-big-bang/

## Discarded

- The bulk of the initial search results (Medium listicles, Xata/Prisma/
  vendor-product framing pages, systemdr/datasops/enolcasielles blog posts)
  restated the same three-phase description without adding a distinct,
  attributable claim beyond what Hodgson's article already supports; not
  fetched, to avoid padding this thread with redundant citations of the same
  well-known pattern.
- No source found made a specific claim about an *automated* gate that
  verifies migration completeness before the contract phase; the claim this
  thread makes is limited to the phased methodology and its stated urgency,
  not to a specific verification mechanism — that mechanism is this pipeline's
  own gap, not something borrowed from a cited source.
