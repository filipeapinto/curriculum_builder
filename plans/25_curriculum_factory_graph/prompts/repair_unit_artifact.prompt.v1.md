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

Write one complete child artifact and one change response:

```text
{
  repair_id, owner, parent_version, parent_sha256,
  child_path,
  changed_locations[],
  finding_ids_addressed[],
  unchanged_dependency_sha256s,
  unresolved[]
}
```

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
- Write only the declared child and response targets.

Complete when the scoped child and change response are written. If a correction
requires scope expansion, record it as unresolved without making the expansion.
