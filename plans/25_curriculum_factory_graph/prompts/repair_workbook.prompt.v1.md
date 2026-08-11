# Repair a named workbook defect

## Job

Create one new version of a workbook-owned artifact for the supplied named defects.
Accepted unit packages are immutable inputs and may not be changed.

## Authorized inputs

- activation envelope and validated routing decision;
- `repair_id`, attempt, maximum, named workbook finding set, and required retest
  order;
- one current workbook-owned parent artifact/version/hash;
- ordered immutable accepted-unit IDs, paths, and hashes;
- exact allowed workbook paths or fields; and
- one child-version output target and response contract.

Unit source/content/domain/visual write access, unit author history, sibling verdicts,
acceptance records as writable data, counters, and terminal state are excluded.

## Output

Write one complete workbook-owned child artifact and change response:

```text
{
  repair_id, owner: WORKBOOK,
  parent_version, parent_sha256, child_path,
  accepted_unit_hashes_before,
  changed_locations[], finding_ids_addressed[], unresolved[]
}
```

Permitted examples are front matter, TOC/navigation, pagination, workbook styling,
and assembly metadata within the supplied boundary. The ordered unit inputs must be
referenced exactly once and byte-unchanged.

## Bounds

- Never edit, regenerate, truncate, reorder, or replace accepted unit content or PDFs.
- Never edit the parent in place or expand the allowed boundary.
- Never write checks, reviews, coverage verdicts, release state, or terminal state.
- Do not assert that the defect passed. The controller reassembles, rerenders every
  page, rereviews, and audits.
- Write only the declared child and response targets.

Complete when the scoped child and change response are written. If the requested
correction would require a unit change, leave it unresolved and make no such change.
