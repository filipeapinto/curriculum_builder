# Repair a named unit artifact

## Job

Create one new version of exactly one unit-owned artifact to correct the supplied
named findings. Preserve the immutable parent and all content outside the allowed
change boundary.

## Authorized inputs

- activation envelope and validated routing decision;
- `repair_id`, attempt, maximum, named failed-check set, and required retest order;
- exactly one owned parent artifact with type, version, bytes, and hash;
- immutable dependency projections and hashes;
- exact allowed paths or JSON pointers;
- named findings with evidence locations and required corrections; and
- one new-version output target and response contract.

Unrelated artifacts, sibling units, broad author context, hidden tests, prior reviewer
conversation beyond the named findings, counters, acceptance state, and terminal
state are excluded.

## Output

Return exactly one complete child artifact conforming to the controller-staged
`output.schema.json`. The schema is owner-specific: source interpretation, curriculum
domain, complete unit content/visual metadata, or bounded unit-layout settings. It is
the only legal response shape for this activation. Controller code computes parent
and child hashes, writes the versioned artifact, checks the allowed diff, and records
changed locations.

The child must remain complete; it may differ from the parent only at allowed
locations. Use immutable dependencies as facts, not material to rewrite.

## Bounds

- Do not edit the parent in place.
- Do not change another artifact owner, accepted prerequisite, source bytes, domain
  facts outside scope, check result, review, receipt, counter, route, or state.
- Do not broaden the repair, regenerate the whole unit for a local defect, or choose
  which tests run.
- Do not report that a finding passed. The controller admits the child and reruns the
  declared invalidated descendants.
- Do not write files; return only the schema-valid child JSON for the controller's
  preallocated target.

Complete when the scoped child and change response are written. If a correction
requires scope expansion, record it as unresolved without making the expansion.
